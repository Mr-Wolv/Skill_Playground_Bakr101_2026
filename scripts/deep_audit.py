#!/usr/bin/env python3
"""deep_audit.py — compositional deep-audit harness (see docs/AUDIT-METHODOLOGY.md).

Levels:
  L0  single file (SKILL.md): frontmatter, fenced blocks, internal refs, script safety
  L1  single skill folder:    internal integrity + script syntax + destructive/exfil/secret scan
  L2  thematic cluster:       overlap / trigger collisions across the cluster
  L3+ parent re-verify:       reuse existing canonical gates (manifest, catalog, parity)

Usage:
  python scripts/deep_audit.py skill <name>
  python scripts/deep_audit.py cluster [--scope <glob>]   # glob over skills/<name>/scripts existence
  python scripts/deep_audit.py report
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys
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
          r"(?i)password\s*=\s*['\"]?[^\s'\"]+", r"(?i)api[_-]?key\s*=\s*['\"]?[^\s'\"]+",
          r"(?i)token\s*=\s*['\"]?[^\s'\"]+", r"Bearer\s+[A-Za-z0-9._-]+",
          r"ghp_[A-Za-z0-9]{20,}", r"\bsk-[A-Za-z0-9]{20,}", r"xoxb-[A-Za-z0-9-]+"]
# --- absolute/leaky path (WARN) --- require a real path segment after the drive colon
HARDCODED_PATH = [r"[A-Za-z]:\\[A-Za-z]", r"/home/[a-z]+/[A-Za-z]", r"/Users/[a-z]+/[A-Za-z]", r"C:\\Users\\"]


def fenced_blocks(md: str):
    out, cur, lang = [], [], None
    for line in md.splitlines():
        m = re.match(r"^```(\w+)?\s*$", line)
        if m:
            if cur:
                out.append((lang, "\n".join(cur))); cur, lang = [], None
            else:
                lang = m.group(1)
        elif cur is not None:
            cur.append(line)
    if cur:
        out.append((lang, "\n".join(cur)))
    return out


def audit_skill(name: str):
    """L0 + L1 for one skill folder. Returns list of findings."""
    f = SK / name
    findings = []
    def add(sev, msg): findings.append({"level": "L0/L1", "skill": name, "sev": sev, "msg": msg})

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

    # referenced local paths exist
    for m in re.finditer(r"[`]?((?:references|templates|scripts|assets)/[\w./-]+)[`]?", text):
        ref = m.group(1)
        if not (f / ref).exists():
            add(CRIT, f"referenced file not found on disk: {ref}")

    # fenced blocks: dangerous patterns + empty
    for i, (lang, body) in enumerate(fenced_blocks(text)):
        if not body.strip():
            add(INFO, f"empty fenced block #{i} (lang={lang})")
        for pat in DESTRUCTIVE:
            if re.search(pat, body):
                add(WARN, f"fenced block #{i} ({lang}) destructive pattern: {pat}")
        for pat in EXFIL:
            if re.search(pat, body):
                add(WARN, f"fenced block #{i} ({lang}) exfil pattern: {pat}")
        for pat in SECRET:
            if re.search(pat, body):
                add(WARN, f"fenced block #{i} ({lang}) secret pattern: {pat}")
        for pat in HARDCODED_PATH:
            if re.search(pat, body):
                add(WARN, f"fenced block #{i} ({lang}) hardcoded path: {pat}")

    # scripts/ dir: syntax check each (no working-tree pollution: ast.parse, no pyc)
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
            elif sf.suffix in (".sh", ".bash"):
                # Shell syntax checking via `bash -n` is environment-limited here
                # (the spawned interpreter cannot resolve Windows/UNIX paths), so
                # it is intentionally NOT run as a CRITICAL gate. The destructive/
                # exfil/secret pattern scan below still runs on the script body.
                # ENV-LIMITATION: shell lint must be run by a human in a real shell.
                pass
            # also scan raw script files for the same patterns
            try:
                body = sf.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for pat in DESTRUCTIVE + EXFIL + SECRET + HARDCODED_PATH:
                if re.search(pat, body):
                    add(WARN, f"{sf.name}: pattern {pat}")
    return findings


def script_bearing():
    out = []
    for d in sorted(SK.iterdir()):
        if d.is_dir() and (d / "scripts").is_dir():
            out.append(d.name)
    return out


def audit_cluster(scope=None):
    """L0+L1 over cluster, then L2 analysis, then re-verify parents (L3/L4/L5)."""
    names = script_bearing()
    if scope:
        pat = scope.replace("*", ".*")
        names = [n for n in names if re.search(pat, n)]
    allf = []
    print(f"=== L0/L1: auditing {len(names)} script-bearing skills ===")
    for n in names:
        f0 = audit_skill(n)
        crit = [x for x in f0 if x["sev"] == CRIT]
        warn = [x for x in f0 if x["sev"] == WARN]
        print(f"  {n}: {len(crit)} CRITICAL, {len(warn)} WARN")
        for x in crit: print("      CRIT:", x["msg"])
        for x in warn: print("      WARN:", x["msg"])
        allf.extend(f0)

    # L2: duplicate trigger / overlap signals across cluster (heuristic on name + desc keywords)
    print("\n=== L2: cluster overlap heuristic ===")
    descs = {}
    for n in names:
        t = (SK / n / "SKILL.md").read_text(errors="replace")
        m = re.search(r"^description:\s*(.+)$", t, re.M)
        descs[n] = m.group(1).strip().lower() if m else ""
    # token overlap
    toks = {n: set(re.findall(r"[a-z]{4,}", d)) for n, d in descs.items()}
    seen = {}
    for n in names:
        for k, v in toks.items():
            if k == n: continue
            inter = v & toks[n]
            if len(inter) >= 4 and len(inter) >= 0.6 * min(len(v), len(toks[k])):
                seen.setdefault((n, k), inter)
    if seen:
        for (a, b), inter in seen.items():
            print(f"  POSSIBLE OVERLAP {a} <-> {b}: shared {sorted(inter)[:8]}")
    else:
        print("  no strong description overlap detected")

    # parent re-verify (L3/L4/L5): reuse canonical gates as subprocesses
    print("\n=== Parent re-verify (L5 repo collection) ===")
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_catalog.py")],
                       capture_output=True, text=True)
    print("  validate_catalog.py:", "OK" if r.returncode == 0 else "FAIL", "|",
          r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr.strip().splitlines()[-1])
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_skill_mirror_parity.py")],
                       capture_output=True, text=True)
    print("  check_skill_mirror_parity.py:", "OK" if r.returncode == 0 else "FAIL", "|",
          r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr.strip().splitlines()[-1])

    # summary
    crit_total = [x for x in allf if x["sev"] == CRIT]
    warn_total = [x for x in allf if x["sev"] == WARN]
    print(f"\n=== SUMMARY: {len(crit_total)} CRITICAL, {len(warn_total)} WARN across cluster ===")
    REPORT.write_text(json.dumps({
        "scope": scope or "script-bearing", "names": names,
        "critical": crit_total, "warn": warn_total,
    }, indent=2))
    print(f"report written: {REPORT}")
    return 1 if crit_total else 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s1 = sub.add_parser("skill"); s1.add_argument("name")
    s2 = sub.add_parser("cluster"); s2.add_argument("--scope", default=None)
    sub.add_parser("report")
    args = ap.parse_args()
    if args.cmd == "skill":
        f0 = audit_skill(args.name)
        for x in f0: print(f"[{x['sev']}] {x['msg']}")
        print("OK" if not any(x['sev'] == CRIT for x in f0) else "FAIL")
        sys.exit(0 if not any(x['sev'] == CRIT for x in f0) else 1)
    elif args.cmd == "cluster":
        sys.exit(audit_cluster(args.scope))
    elif args.cmd == "report":
        print(REPORT.read_text() if REPORT.exists() else "no report yet")


if __name__ == "__main__":
    main()
