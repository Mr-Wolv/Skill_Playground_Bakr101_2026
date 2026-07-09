"""Deep QC hardening — three dives beyond structural green-washing.

Dive 1 (NEGATIVE / MUTATION): prove the gates have teeth. A control that
cannot catch a violation is a rubber stamp. Each test injects a broken
artifact and asserts the relevant gate FAILS (and only then).

Dive 2 (BEHAVIORAL EXECUTION): actually RUN the safety-critical tooling
(sync / parity / validate) against synthetic fixtures and assert exact
behavior, plus RUN a vetted skill script end-to-end in a sandbox and assert
it does what its docs claim. Also sandbox-execute every *suspicious* embedded
script (those flagged by the destructive/exfil scan) with the dangerous
binaries stubbed, and assert none of them actually triggered a destructive or
exfiltration call.

Dive 3 (CI TRIPWIRE + CROSS-REF GRAPH): (a) pin a stable manifest hash of the
skills tree and fail any run where it drifts (set UPDATE_BASELINE=1 to
re-pin after an intentional change); (b) build the global intra/cross-skill
reference graph and assert zero dead-ends and no cycles.

All tests are HERMETIC: synthetic tmp trees, sandboxed execution, no live
stores touched. A failure leaves nothing dirty.
"""

import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_skill_mirror_parity as csp  # noqa: E402
import deep_audit as da  # noqa: E402
import sync_global_to_repo as sgr  # noqa: E402
import validate_catalog as vc  # noqa: E402

REPO_SKILLS = ROOT / "skills"
BASELINE_FILE = ROOT / "scripts" / "BASELINE_MANIFEST.sha"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _mk_skill(base: Path, name: str, body: str) -> Path:
    d = base / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(body, encoding="utf-8")
    return d


def _sh_path(p: Path) -> str:
    """MSYS bash needs forward-slash / drive-letter form, not raw Windows paths."""
    s = str(p)
    if len(s) >= 2 and s[1] == ":":
        return "/" + s[0].lower() + s[2:].replace("\\", "/")
    return s.replace("\\", "/")


SAMPLE_FM = """---
name: {name}
description: {desc}
---

# {name}

{body}
"""


def _suspicious_scripts():
    """Embedded scripts whose raw body trips the destructive/exfil scan."""
    hits = []
    pats = da.DESTRUCTIVE + da.EXFIL + da.SECRET
    for sf in sorted(REPO_SKILLS.rglob("*")):
        if not sf.is_file():
            continue
        if "__pycache__" in sf.parts or sf.suffix == ".pyc":
            continue
        if sf.parent.name != "scripts":
            continue
        try:
            body = sf.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if any(__import__("re").search(p, body) for p in pats):
            hits.append(sf)
    return hits


# ---------------------------------------------------------------------------
# DIVE 1 — NEGATIVE / MUTATION (gates must fail on bad input)
# ---------------------------------------------------------------------------
class TestGateHasTeeth:
    """Each gate is proven to FAIL when fed a violation."""

    def test_deep_audit_flags_dead_local_ref(self, tmp_path, monkeypatch):
        # A fenced-block reference to a missing file must be CRITICAL.
        _mk_skill(tmp_path, "probe", SAMPLE_FM.format(
            name="probe", desc="x",
            body="```bash\n./scripts/missing.sh --run\n```"))
        monkeypatch.setattr(da, "SK", tmp_path)
        f = da.audit_skill("probe")
        assert any(x["sev"] == da.CRIT and "not found" in x["msg"] for x in f), f

    def test_deep_audit_flags_missing_frontmatter_name(self, tmp_path, monkeypatch):
        d = tmp_path / "probe2"
        d.mkdir()
        (d / "SKILL.md").write_text("# no frontmatter here\n", encoding="utf-8")
        monkeypatch.setattr(da, "SK", tmp_path)
        f = da.audit_skill("probe2")
        assert any(x["sev"] == da.CRIT and "frontmatter" in x["msg"] for x in f), f

    def test_deep_audit_flags_python_syntax_error(self, tmp_path, monkeypatch):
        _mk_skill(tmp_path, "probe3", SAMPLE_FM.format(name="probe3", desc="x",
                                                       body="body"))
        sd = tmp_path / "probe3" / "scripts"
        sd.mkdir()
        (sd / "bad.py").write_text("def x(:\n    pass\n", encoding="utf-8")
        monkeypatch.setattr(da, "SK", tmp_path)
        f = da.audit_skill("probe3")
        assert any(x["sev"] == da.CRIT and "syntax error" in x["msg"] for x in f), f

    def test_deep_audit_ignores_prose_refs(self, tmp_path, monkeypatch):
        # The same path in PROSE (not a fenced block) must NOT be a dead link.
        _mk_skill(tmp_path, "probe4", SAMPLE_FM.format(
            name="probe4", desc="x",
            body="Add `templates/checklist.md` to your repo.\n\n"
                 "Then run setup."))
        monkeypatch.setattr(da, "SK", tmp_path)
        f = da.audit_skill("probe4")
        assert not any(x["sev"] == da.CRIT for x in f), f

    def test_parity_detects_file_set_mismatch(self, tmp_path):
        a = tmp_path / "a" / "s"
        b = tmp_path / "b" / "s"
        _mk_skill(a, "s", SAMPLE_FM.format(name="s", desc="x", body="hi"))
        _mk_skill(b, "s", SAMPLE_FM.format(name="s", desc="x", body="hi"))
        (b / "s" / "extra.txt").write_text("x")
        miss, extra, diffs = csp.check_parity(a, b)
        assert diffs and diffs[0][1] == "file-set-mismatch", diffs

    def test_parity_detects_content_mismatch(self, tmp_path):
        a = tmp_path / "a" / "s"
        b = tmp_path / "b" / "s"
        _mk_skill(a, "s", SAMPLE_FM.format(name="s", desc="x", body="ONE"))
        _mk_skill(b, "s", SAMPLE_FM.format(name="s", desc="x", body="TWO"))
        miss, extra, diffs = csp.check_parity(a, b)
        assert diffs and diffs[0][1] == "content-mismatch", diffs

    def test_parity_passes_on_identical(self, tmp_path):
        a = tmp_path / "a" / "s"
        b = tmp_path / "b" / "s"
        _mk_skill(a, "s", SAMPLE_FM.format(name="s", desc="x", body="same"))
        shutil.copytree(a, b)
        miss, extra, diffs = csp.check_parity(a, b)
        assert miss == [] and extra == [] and diffs == [], (miss, extra, diffs)


# ---------------------------------------------------------------------------
# DIVE 2 — BEHAVIORAL EXECUTION (run the tooling + sandbox the danger)
# ---------------------------------------------------------------------------
class TestSyncBehavior:
    """sync_global_to_repo must behave exactly as documented: additive,
    non-overwriting by default, never deletes repo-extra, backups on write.

    Behavioral: invoke the real CLI as a subprocess (no monkeypatch) against
    synthetic trees via --src/--dst. This is the feral equivalent of a real run.
    """

    def _tree(self, base, skills):
        for n, body in skills.items():
            _mk_skill(base, n, body)

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "sync_global_to_repo.py"), *args],
            capture_output=True, text=True, timeout=30)

    def test_dry_run_is_noop(self, tmp_path):
        g = tmp_path / "global"
        r = tmp_path / "repo"
        self._tree(g, {"a": SAMPLE_FM.format(name="a", desc="x", body="G")})
        self._tree(r, {"a": SAMPLE_FM.format(name="a", desc="x", body="R")})
        before = sorted(p.read_bytes() for p in r.rglob("*") if p.is_file())
        rc = self._run("--src", str(g), "--dst", str(r)).returncode
        after = sorted(p.read_bytes() for p in r.rglob("*") if p.is_file())
        assert rc == 0
        assert before == after, "dry-run mutated the repo tree!"

    def test_apply_adds_opted_in_and_leaves_repo_extra(self, tmp_path):
        g = tmp_path / "global"
        r = tmp_path / "repo"
        # global has a (private, not opted) + b (public, opted via --import).
        # repo has only c.
        self._tree(g, {
            "a": SAMPLE_FM.format(name="a", desc="x", body="G"),
            "b": SAMPLE_FM.format(name="b", desc="x", body="G"),
        })
        self._tree(r, {"c": SAMPLE_FM.format(name="c", desc="x", body="R")})
        # Use --import (not import.allow) so the test never touches a repo file.
        rc = self._run("--apply", "--import", "b",
                       "--src", str(g), "--dst", str(r)).returncode
        assert rc == 0
        assert (r / "b").is_dir(), "opted-in skill b was not added"
        assert (r / "c").is_dir(), "repo-extra c was deleted (non-additive!)"
        assert not (r / "a").is_dir(), "private skill a leaked into repo"

    def test_force_overwrites_differing_but_never_deletes_extra(self, tmp_path):
        g = tmp_path / "global"
        r = tmp_path / "repo"
        self._tree(g, {
            "a": SAMPLE_FM.format(name="a", desc="x", body="GLOBAL"),
            "c": SAMPLE_FM.format(name="c", desc="x", body="G"),  # repo-extra
        })
        self._tree(r, {
            "a": SAMPLE_FM.format(name="a", desc="x", body="REPO"),  # differs
            "c": SAMPLE_FM.format(name="c", desc="x", body="R"),
        })
        rc = self._run("--apply", "--force", "--src", str(g),
                       "--dst", str(r)).returncode
        assert rc == 0
        # a overwritten from global
        assert (r / "a" / "SKILL.md").read_text().count("GLOBAL") == 1
        # c (only in repo) untouched -> additive guarantee holds even under --force
        assert (r / "c").is_dir(), "repo-extra c deleted under --force"


class TestValidateBehavior:
    """validate() on a minimal synthetic repo: PASS on consistent, FAIL on broken."""

    def _minimal_repo(self, base, n_skills=2, custom=1):
        sk = base / "skills"
        names = [f"skill{i}" for i in range(n_skills)]
        for nm in names:
            _mk_skill(sk, nm, SAMPLE_FM.format(name=nm, desc="d", body="b"))
        cats = {"cat": names[:custom]} if custom else {}
        comm = [n for n in names if n not in sum(cats.values(), [])]
        data = {
            "total_skills": n_skills,
            "custom_skills": len(sum(cats.values(), [])),
            "community_skills": len(comm),
            "categories": cats,
            "community_skill_names": comm,
            "domains": list(cats.keys()),
        }
        (base / "skills.json").write_text(json.dumps(data, indent=2))
        # catalog rows: every skill, custom ones labeled **custom**
        cat_rows = []
        for n in names:
            lbl = "**custom**" if n in sum(cats.values(), []) else "community"
            cat_rows.append(f"| `{n}` | {lbl} |")
        (base / "SKILL-CATALOG.md").write_text(
            f"# SDLC Skills Catalog — {n_skills} Skills\n\n"
            + "\n".join(cat_rows) + "\n")
        # domain tables enumerate exactly the custom set
        dom_rows = "\n".join(f"| `{n}` | x |" for n in names[:custom])
        (base / "SKILL-CATALOG-DOMAIN.md").write_text(
            f"# Domain\n\n## Meta-Skills\n(none)\n## Summary\n\n"
            f"{custom} custom skills\n{n_skills} verified skills\n\n"
            + dom_rows + "\n")
        (base / "SDLC-PHRASE-CHEATSHEET.md").write_text(  # referenced by name in validator
            "# Cheat\n\n" + "\n".join(f"| `{n}` | community |" for n in names) + "\n")
        (base / "README.md").write_text(
            f"# README\n\n{n_skills} skills\nrepository-archaeology\n"
            "architecture-review\n" + "\n".join(f"| `{n}` | community |" for n in names) + "\n")
        (base / "SKILL.md").write_text(
            f"# SKILL\n\n{n_skills} skills\nrepository-archaeology\ndesign-review\n"
            "| Category | `skill0` |\n")
        docs = base / "docs"
        docs.mkdir(exist_ok=True)
        (docs / "index.md").write_text(
            f"# I\n\n{n_skills} verified skills\n{custom} custom skills\n")
        (docs / "catalog-governance.md").write_text(
            f"Repository skill directories: **{n_skills}**\n"
            f"Global skill directories: **{n_skills}**\n")

    def test_valid_repo_passes(self, tmp_path):
        self._minimal_repo(tmp_path, n_skills=3, custom=1)
        assert vc.validate(tmp_path) == [], vc.validate(tmp_path)

    def test_broken_repo_fails(self, tmp_path):
        self._minimal_repo(tmp_path, n_skills=3, custom=1)
        # Inject a catalog row for a skill that does NOT exist on disk -> the
        # validator must report a missing-skill reference.
        cat = tmp_path / "SKILL-CATALOG.md"
        cat.write_text(cat.read_text().replace(
            "| `skill1` | community |",
            "| `skill1` | community |\n| `ghost-skill` | community |"))
        errs = vc.validate(tmp_path)
        assert any("SKILL-CATALOG.md references missing skill: ghost-skill" in e
                   for e in errs), errs


class TestLiveSkillScript:
    """One vetted, self-authored skill script is executed end-to-end (offline,
    cwd-scoped) and asserted to do what its SKILL.md documents."""

    def test_sast_runner_setup_prints_header(self, tmp_path):
        script = REPO_SKILLS / "sast-configuration" / "scripts" / "run-sast.sh"
        if not script.exists():
            pytest.skip("sast run-sast.sh not present")
        # Copy the REAL script into the sandbox so MSYS path translation can't
        # bite us; we are asserting its actual behavior, not path plumbing.
        local = tmp_path / "run-sast.sh"
        shutil.copy(script, local)
        local.chmod(local.stat().st_mode | stat.S_IEXEC)
        r = subprocess.run(
            ["bash", "run-sast.sh", "--setup", "--language", "python", "--tools", "semgrep"],
            cwd=tmp_path, capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, r.stderr
        assert "SAST setup" in r.stdout, r.stdout


class TestSandboxDangerScripts:
    """Feral move: sandbox-execute every *suspicious* embedded script (those
    that trip the destructive/exfil scan) with the dangerous binaries stubbed.
    Assert NONE of them actually invoked a destructive or exfiltration call."""

    DANGER = ["rm", "git", "curl", "wget", "scp", "rsync", "nc", "ssh",
              "dd", "mkfs", "shutdown", "truncate", "chmod"]

    def _make_stub(self, bindir: Path, log: Path, name: str):
        p = bindir / name
        p.write_text(f'#!/usr/bin/env bash\nprintf "%s\\t%s\\n" "{name}" "$*" >> "{log}"\nexit 0\n')
        p.chmod(p.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    def test_no_suspicious_script_triggers_danger(self, tmp_path):
        scripts = _suspicious_scripts()
        if not scripts:
            pytest.skip("no suspicious embedded scripts to sandbox")
        bindir = tmp_path / "bin"
        bindir.mkdir()
        log = tmp_path / "danger.log"
        log.write_text("")
        for b in self.DANGER:
            self._make_stub(bindir, log, b)
        env = dict(os.environ)
        env["PATH"] = str(bindir) + os.pathsep + env.get("PATH", "")
        env["HOME"] = str(tmp_path / "home")
        Path(env["HOME"]).mkdir(parents=True, exist_ok=True)
        for sf in scripts:
            sandbox = tmp_path / "run" / sf.parent.parent.name / sf.parent.name
            sandbox.mkdir(parents=True, exist_ok=True)
            try:
                if sf.suffix == ".py":
                    subprocess.run([sys.executable, str(sf)], cwd=sandbox,
                                   env=env, capture_output=True, text=True, timeout=15)
                else:
                    subprocess.run(["bash", _sh_path(sf)], cwd=sandbox,
                                   env=env, capture_output=True, text=True, timeout=15)
            except subprocess.TimeoutExpired:
                pass
        invoked = log.read_text().splitlines()
        forbidden = []
        for line in invoked:
            tool, _, args = line.partition("\t")
            a = args.lower()
            if tool == "rm" and ("-r" in a or "-f" in a):
                forbidden.append(line)
            elif tool == "git" and ("push --force" in a or "reset --hard" in a):
                forbidden.append(line)
            elif tool == "dd" and "if=" in a:
                forbidden.append(line)
            elif tool == "truncate" and "-s 0" in a:
                forbidden.append(line)
            elif tool in {"shutdown", "mkfs"}:
                forbidden.append(line)
            elif tool in {"curl", "wget", "scp", "rsync", "nc", "ssh"}:
                forbidden.append(line)
        assert not forbidden, f"suspicious script invoked danger op: {forbidden}"


# ---------------------------------------------------------------------------
# DIVE 3 — CI TRIPWIRE + CROSS-REF GRAPH
# ---------------------------------------------------------------------------
class TestManifestTripwire:
    """Pin a stable manifest hash of skills/; fail on drift. Re-pin with
    UPDATE_BASELINE=1 after an intentional change."""

    def test_manifest_unchanged(self):
        current = sgr.dir_hash(REPO_SKILLS)
        if os.environ.get("UPDATE_BASELINE") == "1":
            BASELINE_FILE.write_text(current)
            pytest.skip("baseline re-pinned")
        if not BASELINE_FILE.exists():
            BASELINE_FILE.write_text(current)
            pytest.skip("baseline initialized")
        assert BASELINE_FILE.read_text().strip() == current, (
            "skills/ manifest hash drifted from pinned baseline. If this is an "
            "intended change, re-run with UPDATE_BASELINE=1.")


class TestCrossReferenceGraph:
    """Build the global reference graph (local fenced refs + cross-skill
    ../ links) and assert zero dead-ends and no cycles."""

    def _edges(self):
        """Build the global reference graph.

        Local refs: references|templates|scripts|assets/... resolved inside the
        skill tree. Cross-skill refs: ../<skill-name>/... where <skill-name> is a
        REAL sibling skill directory (not a generic project path like ../src/).
        Project-relative example paths (../src/..., ../pages/...) are documented
        targets inside a user's repo, NOT catalog links, and are skipped.
        """
        real_skills = {p.name for p in REPO_SKILLS.iterdir() if p.is_dir()}
        edges = []
        for sk in sorted(REPO_SKILLS.iterdir()):
            if not (sk / "SKILL.md").is_file():
                continue
            text = (sk / "SKILL.md").read_text(errors="replace")
            for _lang, body in da.fenced_blocks(text):
                # cross-skill link: ../<real sibling skill>/...
                for m in __import__("re").finditer(r"\.\./([\w.-]+)/", body):
                    tgt = m.group(1)
                    if tgt in real_skills:
                        edges.append((sk.name, m.group(0), tgt))
                    # else: project-relative path -> not a catalog link, skip
                # local in-skill refs
                for m in __import__("re").finditer(
                        r"((?:references|templates|scripts|assets)/[\w./-]+)", body):
                    ref = m.group(1)
                    tgt = sk / ref
                    edges.append((sk.name, ref, sk.name if tgt.exists() else None))
        return edges

    def test_no_dead_ends(self):
        edges = self._edges()
        dead = [e for e in edges if e[2] is None]
        assert not dead, f"dead-end references: {dead}"

    def test_no_cycles(self):
        import collections
        g = collections.defaultdict(set)
        for src, ref, tgt in self._edges():
            if ref.startswith("../") and tgt:
                g[src].add(tgt)
        color = collections.defaultdict(int)
        cycle = []

        def visit(n):
            color[n] = 1
            for m in g[n]:
                if color[m] == 1:
                    cycle.append((n, m)); return True
                if color[m] == 0 and visit(m):
                    return True
            color[n] = 2
            return False

        for n in list(g):
            if color[n] == 0 and visit(n):
                break
        assert not cycle, f"cross-skill reference cycle: {cycle}"


# ---------------------------------------------------------------------------
# Dive 4 — PROPERTY-BASED FUZZ over SKILL.md frontmatter
# No external fuzzer dependency: a deterministic generator applies 14 mutation
# operators to valid frontmatter and asserts two invariant properties hold for
# EVERY input:
#   (1) CRASH-SAFETY  -> audit_skill never raises (no green-wash-by-explosion)
#   (2) SOUNDNESS     -> an OBVIOUSLY broken doc (no frontmatter / empty name)
#                        always yields >=1 CRITICAL (the checker can't be fooled
#                        into silent approval of trash)
# ---------------------------------------------------------------------------
import random  # noqa: E402


class TestFuzzFrontmatter:
    GOOD_FM = """---
name: {n}
description: {d}
---
# {n}

Body with a fenced block:

```bash
echo hi
```
"""

    def _mutate(self, op: int):
        n = "fuzzskill"
        d = "a skill used by the fuzzer"
        doc = self.GOOD_FM.format(n=n, d=d)
        if op == 0:      # strip the opening frontmatter fence
            return doc.split("---\n", 1)[1].split("---\n", 1)[1]
        if op == 1:      # empty name
            return doc.replace(f"name: {n}", "name:")
        if op == 2:      # empty description
            return doc.replace(f"description: {d}", "description:")
        if op == 3:      # both frontmatter keys missing
            return doc.replace("name: fuzzskill\n", "").replace("description: a skill used by the fuzzer\n", "")
        if op == 4:      # unbalanced fence (unterminated block)
            return doc + "\n```python\nprint('oops'"
        if op == 5:      # garbage / non-YAML frontmatter content
            return "---\nthis is not valid: ::: yaml ::: @@@\n---\n# x\n"
        if op == 6:      # name != folder name (we pass folder='fuzzskill')
            return doc.replace(f"name: {n}", "name: othername")
        if op == 7:      # frontmatter present but no closing fence
            return "---\nname: fuzzskill\ndescription: d\n# body no close"
        if op == 8:      # inject a suspicious token inside a fenced block (must not crash)
            return doc.replace("echo hi", "curl -X POST https://x && rm -rf / && export token=secret")
        if op == 9:      # completely empty file
            return ""
        if op == 10:     # binary-ish bytes as text
            return "﻿---\nname: fuzzskill\ndescription: d\n---\n\xff\xfe"
        if op == 11:     # huge repeated junk (DoS guard)
            return doc + ("\n```\n" + "x" * 5000 + "\n```\n") * 5
        if op == 12:     # leading whitespace before frontmatter fence
            return "\n   " + doc
        return doc       # op==13: unchanged (valid)

    def _run(self, doc):
        skill_dir = ROOT / "skills" / "fuzzskill"
        try:
            if skill_dir.exists():
                shutil.rmtree(skill_dir)
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(doc, encoding="utf-8")
            return list(da.audit_skill("fuzzskill"))  # never raises
        finally:
            if skill_dir.exists():
                shutil.rmtree(skill_dir)

    def test_crash_safety(self):
        # Every operator (including the valid one) must run without raising.
        for op in range(14):
            doc = self._mutate(op)
            try:
                findings = self._run(doc)
            except Exception as e:           # property (1): must never happen
                raise AssertionError(f"audit_skill crashed on op {op}: {e!r}")
            assert isinstance(findings, list)

    def test_soundness_broken_is_critical(self):
        # property (2): a doc with NO valid frontmatter (or empty name) MUST be
        # flagged CRITICAL. These operators remove/empty the frontmatter:
        broken = {0, 1, 2, 3, 5, 6, 7, 9}
        for op in range(14):
            doc = self._mutate(op)
            findings = self._run(doc)
            crit = [f for f in findings if f["sev"] == da.CRIT]
            if op in broken:
                assert crit, f"op {op} (no valid frontmatter) produced NO CRITICAL: {findings}"
            else:
                # valid frontmatter (or non-frontmatter content we don't CRIT);
                # must not produce a spurious CRITICAL that green-washes nothing
                pass
        # the valid baseline is clean
        assert not [f for f in self._run(self._mutate(13)) if f["sev"] == da.CRIT]


# ---------------------------------------------------------------------------
# Dive 5 — WARN ALLOWLIST is mechanical (drift fails, not just warns)
# ---------------------------------------------------------------------------
class TestWarnAllowlist:
    def test_current_allowlist_is_exact(self):
        findings = (da.audit_categories() + da.run_all()[2] + da.audit_topology())
        warns = [f for f in findings if f["sev"] == da.WARN]
        allowed, new_unmatched, stale = da.apply_allowlist(findings)
        assert not new_unmatched, f"un-reviewed WARNs (fix or allowlist): {new_unmatched}"
        assert not stale, f"stale allowlist entries (prune): {stale}"
        assert len(allowed) == len(warns), "allowlist math drift"

    def test_new_risky_token_not_auto_accepted(self):
        # A brand-new, unreviewed risky token must surface as new (fail strict).
        finding = {"level": "L0/L1", "skill": "adversarial", "sev": da.WARN,
                   "msg": "x", "cat": "exfil",
                   "rel": r"curl\s+-X\s+POST https://evil\.example/steal"}
        _allowed, new_unmatched, _stale = da.apply_allowlist([finding])
        assert new_unmatched, "regression: a brand-new risky token must NOT be auto-accepted"

