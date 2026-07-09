# Convenience targets. uv is the only dependency (no global install needed).
# Run `make verify` for the full regression gate used in CI.

PYTHON := python
UV := uv

.PHONY: verify test validate parity sync shortcut clean qcaudit qcaudit-baseline gate install-hook

# Full regression suite (catalog + sync/parity + import.allow parser + QC dives).
verify test:
	$(UV) run --with pytest pytest

# Catalog coherence gate (the part CI also runs standalone).
validate:
	$(PYTHON) scripts/validate_catalog.py

parity:
	$(PYTHON) scripts/check_skill_mirror_parity.py

# Compositional deep-audit climb (L3->L8) — the standing QC gate.
qcaudit:
	$(PYTHON) scripts/deep_audit.py climb

# Pin/re-pin the manifest tripwire baseline after an intentional change:
#   make qcaudit-baseline
qcaudit-baseline:
	UPDATE_BASELINE=1 $(UV) run --with pytest pytest tests/test_deep_qc.py::TestManifestTripwire

# Single mechanical gate used by CI AND the pre-commit hook (same toolchain,
# so local commits cannot bypass what CI enforces).
gate:
	$(PYTHON) scripts/gate.py

# Install the local pre-commit hook so every commit is gated automatically.
install-hook:
	$(PYTHON) -c "import shutil,pathlib;p=pathlib.Path('.git/hooks/pre-commit');shutil.copy('scripts/pre-commit.hook',p);p.chmod(0o755);print('pre-commit hook installed at',p)"

# End-to-end dry-run shortcut (no writes unless --apply).
shortcut:
	$(PYTHON) scripts/sync_and_validate.py

# Apply downstream sync from global source of truth into this repo.
sync:
	$(PYTHON) scripts/sync_global_to_repo.py --apply

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
