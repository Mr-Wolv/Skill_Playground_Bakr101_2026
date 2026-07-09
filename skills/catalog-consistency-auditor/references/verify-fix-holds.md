# Verify a fix holds — the "taste, don't promise" recipe

A single green `gate.py` run is not proof a convergence/stores fix is durable.
Run this three-step taste test before declaring a fix complete. Replace
`catalog-consistency-auditor` with the shared skill under test.

## 1. Idempotency under reload (run twice)

```bash
cd /path/to/Skill-Playground
python scripts/sync_runtime_to_mirror.py --apply   # reload-mimic #1
python - <<'PY'
import sys, importlib.util
sys.path.insert(0, "scripts")
spec = importlib.util.spec_from_file_location("csp", "scripts/check_skill_mirror_parity.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
import skill_paths
B, C = skill_paths.global_skills_dir(), skill_paths.runtime_skills_dir()
m, e, d = mod.check_parity(B, C)
print("AFTER SYNC #1 -> missing-in-B:", m, "| shared-skill diffs:", d)
PY
# run the sync AGAIN (a second boot) and assert the same clean result
python scripts/sync_runtime_to_mirror.py --apply   # reload-mimic #2
# ...assert missing-in-B: [] and shared-skill diffs: [] again
```

If B==C stays clean across both runs, the derived store is idempotent.

## 2. Adversarial injection (prove the guard fires)

```bash
SK="$LOCALAPPDATA/hermes/skills/catalog-consistency-auditor/SKILL.md"
printf '\n<!-- OSCILLATION TEST JUNK -->\n' >> "$SK"
python scripts/gate.py > /tmp/gate_adv.log 2>&1
echo "GATE EXIT=$?"          # expect non-zero
grep -c "\[CRITICAL\]" /tmp/gate_adv.log   # expect >= 1
grep -i "L7 runtime diff\|content-mismatch" /tmp/gate_adv.log | head -2
```

Expected: `gate.py` exits non-zero with an `[CRITICAL] L7 runtime diff vs B:
content-mismatch`. If the gate stays green here, the safety net is broken — stop
and fix the check, not the symptom.

## 3. Restore + confirm green

```bash
cp ~/.agents/skills/catalog-consistency-auditor/SKILL.md "$SK"
python scripts/gate.py > /tmp/gate_restore.log 2>&1
echo "GATE EXIT=$?"         # expect 0
tail -3 /tmp/gate_restore.log   # expect "ALL GATES PASS"
grep -c "\[CRITICAL\]" /tmp/gate_restore.log   # expect 0
```

Expected: `ALL GATES PASS, 0 CRITICAL`.

## Why this matters

The cost of a false "fixed" claim is a later reload that breaks the gate and
forces whack-a-mole. Three cheap checks up front convert a promise into evidence.
This discipline is mandatory for any L7 runtime<->global drift fix.
