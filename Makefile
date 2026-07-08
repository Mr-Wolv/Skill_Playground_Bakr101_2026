# Convenience targets. uv is the only dependency (no global install needed).
# Run `make verify` for the full regression gate used in CI.

PYTHON := python
UV := uv

.PHONY: verify test validate parity sync shortcut clean

# Full regression suite (catalog + sync/parity + import.allow parser).
verify test:
	$(UV) run --with pytest pytest

# Catalog coherence gate (the part CI also runs standalone).
validate:
	$(PYTHON) scripts/validate_catalog.py

parity:
	$(PYTHON) scripts/check_skill_mirror_parity.py

# End-to-end dry-run shortcut (no writes unless --apply).
shortcut:
	$(PYTHON) scripts/sync_and_validate.py

# Apply downstream sync from global source of truth into this repo.
sync:
	$(PYTHON) scripts/sync_global_to_repo.py --apply

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
