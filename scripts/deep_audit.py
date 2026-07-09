#!/usr/bin/env python3
"""deep_audit.py — compositional deep-audit harness (see docs/AUDIT-METHODOLOGY.md).

The ecosystem is audited compositionally: coherence is re-proven at every
level AS YOU ASCEND, and each level runs unit (isolated) -> e2e (collective)
-> re-verify against the already-passing parent before ascending.

  L0  single file (SKILL.md): frontmatter, fenced blocks, internal refs, script safety
  L1  single skill folder:    internal integrity + script syntax + destructive/exfil/secret scan
  L2  thematic cluster:       overlap / trigger collisions across the cluster
  L3  category grouping:      every skills.json category member is a real disk skill; keys sane
  L4  full skills/ (238):     ocean-deep L0/L1 over EVERY skill (not just script-bearing)
  L5  repo collection:        reused canonical gates (validate_catalog + parity)  [done in prior turn]
  L6  repo <-> B:             one-way mirror integrity (check_skill_mirror_parity)
  L7  B <-> C:                derived-copy parity (runtime is rebuilt from B)
  L8  four-store topology:    boundary + no-leakage (private excluded; no machine paths in shared)

Commands:
  python scripts/deep_audit.py skill <name>     # L0/L1 one skill
  python scripts/deep_audit.py cluster [--scope <glob>]
  python scripts/deep_audit.py categories        # L3
  python scripts/deep_audit.py all               # L4 (all 238)
  python scripts/deep_audit.py topology          # L6 + L7 + L8
  python scripts/deep_audit.py climb             # run L3,L4,L6,L7,L8 in order (unit->e2e->reverify)
  python scripts/deep_audit.py report
"""
from __future__ import annotations
import argparse, importlib.util, json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SK = ROOT / "skills"
REPORT = ROOT / ".deep_audit_report.json"

# --- severity ---
CRIT, WARN, INFO = "CRITICAL", "WARN", "INFO"

# --- script safety patterns (WARN; context decides) ---
DESTRUCTIVE = [
    r"rm\s+-rf?\s", r"rm\s+-fr?\s", r":\(\)\s*\{", r"\bmkfs\b", r"dd\s+if=",
    r">\s*/dev/sd", r"chmod\s+0{3}\b", r"git\s+push\s+--force", r"git\s+reset\s+--hard",
    r"truncate\s+-s\s+0", r"\bshutdown\b", r"curl\b[^\n]*\|\s*(sh|bash)",
    r"wget\b[^\n]*\|\s*(sh|bash)", r"\beval\b",
]
EXFIL = [r"curl\s+-X\s+POST", r"\bscp\s+", r"\brsync\b[^\n]*(ssh|remote)",
         r"\bnc\b\s", r"tar\b[^\n]*\|\s*ssh", r"base64\b"]
SECRET = [r"AKIA[0-9A-Z]{16}", r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
          r"(?i)password\s*=\s*['\"]?[^\\s'\"]+", r"(?i)api[_-]?key\s*=\s*['\"]?[^\\s'\"]+",
          r"(?i)token\s*=\s*['\"]?[^\\s'\"]+", r"Bearer\s+[A-Za-z0-9._-]+",
          r"ghp_[A-Za-z0-9]{20,}", r"\bsk-[A-Za-z0-9]{20,}", r"xoxb-[A-Za-z0-9-]+"]
# --- absolute/leaky path (WARN) --- require a real path segment after the drive colon
HARDCODED_PATH = [r"[A-Za-z]:\\[A-Za-z]", r"/home/[a-z]+/[A-Za-z]", r"/Users/[a-z]+/[A-Za-z]", r"C:\\Users\\"]

# Tagged pattern catalogue: each regex source mapped to a stable category so a
# WARN finding can be matched against a reviewed allowlist by (skill, cat, rel).
PATTERN_CATS = [
    ("destructive", DESTRUCTIVE),
    ("exfil", EXFIL),
    ("secret", SECRET),
    ("hardcoded-path", HARDCODED_PATH),
]
WARN_CAT_DEFAULT = "other"

# Reviewed WARN allowlist: a finding is "accepted" when its (skill, cat, rel)
# triple appears in scripts/warn_allowlist.json. `rel` is the regex source that
# triggered it, so the allowlist is specific to the exact risky token, not a
# whole skill. New (un-allowlisted) WARNs mean an unreviewed risk -> fail in
# --strict. Allowlist entries with no matching finding are STALE -> prune.
ALLOWLIST = ROOT / "scripts" / "warn_allowlist.json"


def load_allowlist():
    if not ALLOWLIST.exists():
        return set()
    try:
        data = json.loads(ALLOWLIST.read_text(encoding="utf-8"))
    except Exception:
        return set()
    return {tuple(e) for e in data.get("allow", [])}


def finding_key(skill, cat, rel):
    return (skill, cat or WARN_CAT_DEFAULT, rel or "")


def apply_allowlist(findings):
    """Split WARN findings into (allowed, new_unmatched, stale_entries)."""
    allow = load_allowlist()
    allowed, new_unmatched = [], []
    seen_keys = set()
    for f in findings:
        if f["sev"] != WARN:
            continue
        key = finding_key(f["skill"], f.get("cat"), f.get("rel"))
        seen_keys.add(key)
        if key in allow:
            allowed.append(f)
        else:
            new_unmatched.append(f)
    stale = sorted(allow - seen_keys)
    return allowed, new_unmatched, stale


# machine username (resolved at runtime; repo is public -> must never appear in shared stores)
USERNAME = os.environ.get("USERNAME") or os.environ.get("USER") or ""


def fenced_blocks(md: str):
    """Yield (lang, body) for each ``` fenced block.

    State machine: cur is None while OUTSIDE a fence, a list while INSIDE.
    Opening a fence starts a new list; closing flushes it. Prose before the
    first fence is correctly ignored (cur is None).
    """
    out, cur, lang = [], None, None
    for line in md.splitlines():
        m = re.match(r"^```(\w+)?\s*$", line)
        if m:
            if cur is None:
                cur, lang = [], m.group(1)       # start of a block
            else:
                out.append((lang, "\n".join(cur)))  # end of a block
                cur, lang = None, None
        elif cur is not None:
            cur.append(line)
    if cur is not None:
        out.append((lang, "\n".join(cur)))       # unterminated final block
    return out


def audit_skill(name: str):
    """L0 + L1 for one skill folder. Returns list of findings."""
    f = SK / name
    findings = []
    def add(sev, msg, cat=None, rel=None):
        findings.append({"level": "L0/L1", "skill": name, "sev": sev, "msg": msg,
                         "cat": cat, "rel": rel})

    if not f.is_dir():
        add(CRIT, f"skill folder missing: {f}"); return findings

    skill_md = f / "SKILL.md"
    if not skill_md.is_file():
        add(CRIT, "missing SKILL.md"); return findings

    text = skill_md.read_text(encoding="utf-8", errors="replace")
    # frontmatter
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not fm:
        add(CRIT, "no YAML frontmatter block"); return findings
    fmtext = fm.group(1)
    fm_name = re.search(r"^name:\s*(.+)$", fmtext, re.M)
    fm_desc = re.search(r"^description:\s*(.+)$", fmtext, re.M)
    if not fm_name:
        add(CRIT, "frontmatter missing `name:`")
    else:
        n = fm_name.group(1).strip().strip('"').strip("'")
        if n != name:
            add(CRIT, f"frontmatter name `{n}` != folder `{name}`")
    if not fm_desc:
        add(CRIT, "frontmatter missing `description:`")
    else:
        if not fm_desc.group(1).strip():
            add(CRIT, "frontmatter `description:` empty")

    # referenced LOCAL paths that must exist — only inside fenced code blocks,
    # to avoid flagging prose/instructive text (e.g. "- add templates/checklists"
    # or external pointers like "Allium references/test-generation"). A genuine
    # dead link is a command/include inside a code fence that points to a
    # missing file within this skill tree.
    for lang, body in fenced_blocks(text):
        for m in re.finditer(r"(\.{0,2}/)?((?:references|templates|scripts|assets)/[\w./-]+)", body):
            ref = m.group(2)
            target = (f / ref)
            # resolve; if it escapes the skills root it is cross-skill/external -> skip
            try:
                target.resolve().relative_to(SK)
            except Exception:
                continue
            if not target.exists():
                add(CRIT, f"referenced file not found on disk: {ref}")

    # fenced blocks: dangerous patterns + empty
    for i, (lang, body) in enumerate(fenced_blocks(text)):
        if not body.strip():
            add(INFO, f"empty fenced block #{i} (lang={lang})")
        for cat, pats in PATTERN_CATS:
            for pat in pats:
                if re.search(pat, body):
                    add(WARN, f"fenced block #{i} ({lang}) pattern: {pat}", cat=cat, rel=pat)
        if USERNAME and re.search(re.escape(USERNAME), body):
            add(WARN, f"fenced block #{i} ({lang}) contains machine username `{USERNAME}`",
                cat="username", rel=USERNAME)

    # scripts/ dir: syntax check each (no working-tree pollution: compile, no pyc)
    sd = f / "scripts"
    if sd.is_dir():
        for sf in sorted(sd.iterdir()):
            if sf.name == "__pycache__" or sf.name.startswith("."):
                continue
            if sf.suffix == ".py":
                try:
                    compile(sf.read_text(encoding="utf-8", errors="replace"), sf.name, "exec")
                except SyntaxError as e:
                    add(CRIT, f"python syntax error in {sf.name}: {e}")
            # scan raw script files for the same patterns
            try:
                body = sf.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for cat, pats in PATTERN_CATS:
                for pat in pats:
                    if re.search(pat, body):
                        add(WARN, f"{sf.name}: pattern {pat}", cat=cat, rel=pat)
            if USERNAME and re.search(re.escape(USERNAME), body):
                add(WARN, f"{sf.name}: contains machine username `{USERNAME}`",
                    cat="username", rel=USERNAME)
    return findings


def script_bearing():
    return [d.name for d in sorted(SK.iterdir()) if d.is_dir() and (d / "scripts").is_dir()]


def all_skills():
    return [d.name for d in sorted(SK.iterdir()) if d.is_dir() and (d / "SKILL.md").is_file()]


# ---------------------------------------------------------------------------
# L3 — category grouping integrity
# ---------------------------------------------------------------------------
def audit_categories():
    sj = json.loads((ROOT / "skills.json").read_text())
    cats = sj.get("categories", {})
    disk = set(all_skills())
    findings = []
    known_domains = set(sj.get("domains", [])) if "domains" in sj else set()
    for cat, members in cats.items():
        if known_domains and cat not in known_domains:
            # category key not a declared domain — flag for review (WARN, not CRIT)
            findings.append({"level": "L3", "skill": cat, "sev": WARN,
                             "msg": f"category key `{cat}` not in skills.json domains"})
        for m in members:
            if m not in disk:
                findings.append({"level": "L3", "skill": cat, "sev": CRIT,
                                 "msg": f"category `{cat}` lists unknown skill `{m}` (not on disk)"})
    # every disk skill that is custom should appear somewhere? Not required.
    return findings


# ---------------------------------------------------------------------------
# L6 / L7 — store parity (reuse check_skill_mirror_parity.check_parity)
# ---------------------------------------------------------------------------
def load_parity():
    spec = importlib.util.spec_from_file_location(
        "csp", ROOT / "scripts" / "check_skill_mirror_parity.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def store_parity(a: Path, b: Path):
    mod = load_parity()
    return mod.check_parity(a, b)


# ---------------------------------------------------------------------------
# L8 — four-store topology boundary + no-leakage
# ---------------------------------------------------------------------------
def load_paths():
    spec = importlib.util.spec_from_file_location(
        "sp", ROOT / "scripts" / "skill_paths.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_paths():
    spec = importlib.util.spec_from_file_location(
        "sp", ROOT / "scripts" / "skill_paths.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def audit_topology():
    """L6 + L7 + L8. Returns findings list."""
    findings = []
    sp = load_paths()
    B = sp.global_skills_dir()
    C = sp.runtime_skills_dir()
    private = sp.local_skills_dir()
    user = sp.user_skills_dir()

    # L6: repo <-> B (one-way mirror: repo must be subset of B; parity expected)
    miss_b, extra_b, diffs_b = store_parity(SK, B)
    if miss_b or extra_b or diffs_b:
        for n in miss_b:
            findings.append({"level": "L6", "skill": n, "sev": CRIT, "msg": "in repo but missing from B (source of truth)"})
        for n in extra_b:
            findings.append({"level": "L6", "skill": n, "sev": WARN, "msg": f"in B but not in repo: {n}"})
        for d in diffs_b[:50]:
            findings.append({"level": "L6", "skill": d[0], "sev": CRIT, "msg": f"parity diff vs B: {d[1]}"})

    # L7: B <-> C (runtime is a derived copy of B). C is ADDITIVE by design:
    # skills present in C but absent from B are the agent's private/extra skills
    # and must NEVER be deleted, so extra_in_C is expected (INFO, not CRIT).
    # A genuine defect is when B has a skill C lacks (runtime fell behind) or a
    # content mismatch in a shared skill.
    miss_c, extra_c, diffs_c = store_parity(B, C)
    if miss_c or diffs_c:
        for n in miss_c:
            findings.append({"level": "L7", "skill": n, "sev": CRIT, "msg": "in B but missing from runtime C (runtime fell behind)"})
        for d in diffs_c[:50]:
            findings.append({"level": "L7", "skill": d[0], "sev": CRIT, "msg": f"runtime diff vs B: {d[1]}"})
    for n in extra_c:
        findings.append({"level": "L7", "skill": n, "sev": INFO, "msg": f"in runtime C but not in B (private/extra skill, additive — expected)"})

    # L8: boundary + leakage
    # (a) The PRIVATE store must NOT be nested inside a shared store. This only
    # fires when private is a DISTINCT directory physically under B/C/repo.
    # (On a default Windows install runtime C == private path, so the two are
    # the same dir — that is NOT a leak; skip when paths are identical.)
    for store_name, store in [("B", B), ("C", C), ("repo", SK)]:
        if not store.exists():
            continue
        for other_name, other in [("private", private), ("user", user)]:
            if not other.exists():
                continue
            if other == store:
                continue  # same dir by design -> not a containment leak
            if other in store.parents or store in other.parents:
                for p in other.rglob("SKILL.md"):
                    findings.append({"level": "L8", "skill": p.parent.name, "sev": CRIT,
                                     "msg": f"private store `{other_name}` is nested under shared `{store_name}`"})
    # (b) no machine username / C:\Users paths in SHARED stores (privacy + portability).
    # Tightened: only flag a *real* Windows-user path or the resolved username,
    # not the generic `[A-Za-z]:\` drive pattern (it false-positives on f-string
    # "text:\n{var}" newlines).
    USER_PATH = re.compile(r"C:\\Users\\" + re.escape(USERNAME) if USERNAME else r"(?!x)x")
    for store_name, store in [("repo", SK), ("B", B), ("C", C)]:
        for p in store.rglob("*"):
            if not p.is_file() or "__pycache__" in p.parts or p.suffix == ".pyc":
                continue
            try:
                t = p.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            if USERNAME and re.search(re.escape(USERNAME), t):
                findings.append({"level": "L8", "skill": f"{store_name}/{p.relative_to(store)}",
                                 "sev": WARN, "msg": f"contains machine username `{USERNAME}`"})
            if USERNAME and USER_PATH.search(t):
                findings.append({"level": "L8", "skill": f"{store_name}/{p.relative_to(store)}",
                                 "sev": CRIT, "msg": f"hardcoded C:\\Users\\{USERNAME} path"})
    return findings


# ---------------------------------------------------------------------------
# CLI entrypoints
# ---------------------------------------------------------------------------
def run_cluster(scope=None):
    names = script_bearing()
    if scope:
        pat = scope.replace("*", ".*")
        names = [n for n in names if re.search(pat, n)]
    return run_unit_e2e(names, "cluster")


def run_all():
    return run_unit_e2e(all_skills(), "all-238")


def run_unit_e2e(names, label):
    allf = []
    print(f"=== L0/L1: auditing {len(names)} skills ({label}) ===")
    for n in names:
        f0 = audit_skill(n)
        crit = [x for x in f0 if x["sev"] == CRIT]
        warn = [x for x in f0 if x["sev"] == WARN]
        if crit or warn:
            print(f"  {n}: {len(crit)} CRITICAL, {len(warn)} WARN")
            for x in crit: print("      CRIT:", x["msg"])
            for x in warn: print("      WARN:", x["msg"])
        allf.extend(f0)
    # L2 overlap (only meaningful for a real cluster; run cheaply for all too)
    print("\n=== L2: cluster overlap heuristic ===")
    descs = {}
    for n in names:
        t = (SK / n / "SKILL.md").read_text(errors="replace")
        m = re.search(r"^description:\s*(.+)$", t, re.M)
        descs[n] = m.group(1).strip().lower() if m else ""
    toks = {n: set(re.findall(r"[a-z]{4,}", d)) for n, d in descs.items()}
    seen = {}
    for n in names:
        for k, v in toks.items():
            if k == n: continue
            inter = v & toks[n]
            if len(inter) >= 5 and len(inter) >= 0.7 * min(len(v), len(toks[k])):
                seen.setdefault((n, k), inter)
    if seen:
        for (a, b), inter in seen.items():
            print(f"  POSSIBLE OVERLAP {a} <-> {b}: shared {sorted(inter)[:8]}")
    else:
        print("  no strong description overlap detected")
    crit_total = [x for x in allf if x["sev"] == CRIT]
    warn_total = [x for x in allf if x["sev"] == WARN]
    print(f"\n=== SUMMARY ({label}): {len(crit_total)} CRITICAL, {len(warn_total)} WARN ===")
    return crit_total, warn_total, allf


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s1 = sub.add_parser("skill"); s1.add_argument("name")
    s2 = sub.add_parser("cluster"); s2.add_argument("--scope", default=None)
    sub.add_parser("categories")
    sub.add_parser("all")
    sub.add_parser("topology")
    s_climb = sub.add_parser("climb")
    s_climb.add_argument("--strict", action="store_true",
                         help="treat new (un-allowlisted) WARNs and stale allowlist "
                              "entries as failures -> enforces 0/0 across climb")
    s_allow = sub.add_parser("allowlist",
                             help="(re)generate scripts/warn_allowlist.json from "
                                  "current WARN findings (review-then-commit)")
    s_allow.add_argument("--write", action="store_true",
                         help="write the allowlist file (default: print only)")
    sub.add_parser("report")
    args = ap.parse_args()

    if args.cmd == "skill":
        f0 = audit_skill(args.name)
        for x in f0: print(f"[{x['sev']}] {x['msg']}")
        sys.exit(0 if not any(x["sev"] == CRIT for x in f0) else 1)

    elif args.cmd == "cluster":
        crit, warn, _ = run_cluster(args.scope)
        sys.exit(1 if crit else 0)

    elif args.cmd == "all":
        crit, warn, _ = run_all()
        sys.exit(1 if crit else 0)

    elif args.cmd == "categories":
        f = audit_categories()
        for x in f: print(f"[{x['sev']}] {x['msg']}")
        print(f"=== L3 SUMMARY: {sum(x['sev']==CRIT for x in f)} CRITICAL, "
              f"{sum(x['sev']==WARN for x in f)} WARN ===")
        sys.exit(1 if any(x["sev"] == CRIT for x in f) else 0)

    elif args.cmd == "topology":
        f = audit_topology()
        for x in f: print(f"[{x['sev']}] {x['level']} {x['msg']}")
        print(f"=== L6/L7/L8 SUMMARY: {sum(x['sev']==CRIT for x in f)} CRITICAL, "
              f"{sum(x['sev']==WARN for x in f)} WARN ===")
        sys.exit(1 if any(x["sev"] == CRIT for x in f) else 0)

    elif args.cmd == "climb":
        total_crit = total_warn = 0
        print("############ COMPOSITIONAL DEEP-AUDIT CLIMB ############")
        for label, fn in [("L3 categories", lambda: audit_categories()),
                          ("L4 all-238", lambda: run_all()[2]),
                          ("L6/L7/L8 topology", lambda: audit_topology())]:
            print(f"\n############ {label} ############")
            f = fn()
            c = sum(x["sev"] == CRIT for x in f)
            w = sum(x["sev"] == WARN for x in f)
            total_crit += c; total_warn += w
            for x in f: print(f"[{x['sev']}] {x.get('level','?')} {x['msg']}")
            # parent re-verify (L5 canonical gates) after each level
            print("  -- parent re-verify (L5) --")
            r = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_catalog.py")],
                               capture_output=True, text=True)
            print("   validate_catalog.py:", "OK" if r.returncode == 0 else "FAIL")
            r = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_skill_mirror_parity.py")],
                               capture_output=True, text=True)
            print("   check_skill_mirror_parity.py:", "OK" if r.returncode == 0 else "FAIL")
        # WARN allowlist enforcement (mechanical coherence): only WARNs that are
        # explicitly reviewed are tolerated. --strict turns any new/un-allowed
        # WARN and any stale allowlist entry into a failure -> climb is 0/0.
        allowed, new_unmatched, stale = apply_allowlist(
            audit_categories() + run_all()[2] + audit_topology())
        if new_unmatched:
            print(f"\n!!! {len(new_unmatched)} NEW (un-reviewed) WARN(s) not in allowlist:")
            for x in new_unmatched:
                print(f"    {x['skill']} [{x.get('cat')}] {x['msg']}")
        if stale:
            print(f"\n!!! {len(stale)} STALE allowlist entr(y/ies) — no matching finding:")
            for e in stale:
                print(f"    {e}")
        print(f"\n=== CLIMB COMPLETE: {total_crit} CRITICAL, {total_warn} WARN "
              f"({len(allowed)} allowed, {len(new_unmatched)} new) ===")
        failed = total_crit > 0 or (args.strict and (new_unmatched or stale))
        if new_unmatched or stale:
            print("WARN allowlist drift detected"
                  + (" (strict -> FAIL)" if args.strict else " (non-strict: tolerated)"))
        sys.exit(1 if failed else 0)

    elif args.cmd == "allowlist":
        findings = audit_categories() + run_all()[2] + audit_topology()
        warns = [f for f in findings if f["sev"] == WARN]
        entries = sorted({finding_key(f["skill"], f.get("cat"), f.get("rel"))
                          for f in warns})
        payload = {
            "_comment": "Reviewed WARN allowlist (mechanical coherence). Each entry is "
                        "(skill, category, regex-source). A new WARN not listed here is an "
                        "UNREVIEWED risk and fails `climb --strict`. An entry with no "
                        "matching finding is STALE and should be pruned. Regenerate with "
                        "`python scripts/deep_audit.py allowlist --write` AFTER reviewing.",
            "allow": [list(e) for e in entries],
        }
        text_out = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
        if args.write:
            ALLOWLIST.write_text(text_out, encoding="utf-8")
            print(f"wrote {ALLOWLIST} ({len(entries)} entries)")
        else:
            print(text_out)
        sys.exit(0)


if __name__ == "__main__":
    main()
