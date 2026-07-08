import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
SKILLS_JSON = ROOT / "skills.json"

# Doc paths are derived per-root inside validate() so the check is testable
# against a synthetic repo, not silently pinned to the module-level ROOT.


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate(root: Path = ROOT) -> list[str]:
    """Return a list of validation errors (empty == PASS).

    All paths are derived from `root` so the check is testable against a
    synthetic repo as well as the real one.
    """
    errors: list[str] = []

    def fail(msg: str) -> None:
        errors.append(msg)

    skills_dir = root / "skills"
    skills_json = root / "skills.json"

    skill_files = sorted(skills_dir.glob("*/SKILL.md"))
    skill_names: list[str] = []
    for file in skill_files:
        text = read_text(file)
        if not text.startswith("---\n"):
            fail(f"{file.relative_to(root)}: missing opening frontmatter delimiter")
            continue
        name_match = re.search(r"^name:\s*(.+)$", text, re.MULTILINE)
        desc_match = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
        if not name_match:
            fail(f"{file.relative_to(root)}: missing name in frontmatter")
            continue
        if not desc_match:
            fail(f"{file.relative_to(root)}: missing description in frontmatter")
        skill_names.append(name_match.group(1).strip())

    fs_skills = sorted(set(skill_names))
    fs_count = len(fs_skills)

    catalog_text = read_text(root / "SKILL-CATALOG.md")
    domain_text = read_text(root / "SKILL-CATALOG-DOMAIN.md")
    cheatsheet_text = read_text(root / "SDLC-PHRASE-CHEATSHEET.md")

    catalog_skills = sorted(set(re.findall(r"`([a-z][a-z0-9_-]+)`", catalog_text)))
    domain_skills = sorted(set(re.findall(r"`([a-z][a-z0-9_-]+)`", domain_text)))
    cheatsheet_skills = sorted(set(re.findall(r"`([a-z][a-z0-9_-]+)`", cheatsheet_text)))

    for skill in catalog_skills:
        if skill not in fs_skills:
            fail(f"SKILL-CATALOG.md references missing skill: {skill}")

    for skill in domain_skills:
        if skill not in fs_skills:
            fail(f"SKILL-CATALOG-DOMAIN.md references missing skill: {skill}")

    for skill in cheatsheet_skills:
        if skill not in fs_skills:
            fail(f"SDLC-PHRASE-CHEATSHEET.md references missing skill: {skill}")

    data = json.loads(read_text(skills_json))
    # custom count is DERIVED from the manifest (not hardcoded) so union sync that
    # adds skills under the "imported" bucket keeps the gate green automatically.
    custom_count = len(
        {skill for arr in data.get("categories", {}).values() for skill in arr}
    )
    if data.get("total_skills") != fs_count:
        fail(
            f"skills.json total_skills={data.get('total_skills')} but filesystem has {fs_count}"
        )
    if data.get("custom_skills") != custom_count:
        fail(
            f"skills.json custom_skills={data.get('custom_skills')} but expected {custom_count}"
        )

    json_skills = sorted(
        {skill for arr in data.get("categories", {}).values() for skill in arr}
    )
    for skill in json_skills:
        if skill not in fs_skills:
            fail(f"skills.json references missing skill: {skill}")

    # Per-row source labels in SKILL-CATALOG.md must match the canonical custom set.
    # The aggregate count check above does NOT catch a row that is labeled wrong
    # (e.g. a custom skill tagged `community` or vice versa) as long as the totals
    # happen to balance, so we verify the exact labeled set here.
    custom_catalog_rows = set(
        re.findall(
            r"^\|\s*`([a-z][a-z0-9_-]+)`\s*\|\s*(?:\*\*custom\*\*|custom)\s*\|",
            catalog_text,
            re.MULTILINE,
        )
    )
    custom_set = set(json_skills)  # every skill in the manifest categories is "custom"
    for skill in custom_catalog_rows - custom_set:
        fail(f"SKILL-CATALOG.md labels `{skill}` custom but it is not in the custom set")
    for skill in custom_set - custom_catalog_rows:
        fail(f"SKILL-CATALOG.md missing custom label for `{skill}` (or labeled community)")

    # SKILL-CATALOG-DOMAIN.md claims to list the custom skills by domain. The
    # domain tables (excluding the meta-skills block) must enumerate exactly the
    # canonical custom set and nothing else.
    domain_meta = re.search(r"## .*Meta-Skills(.*?)## Summary", domain_text, re.S)
    domain_meta_skills = (
        set(re.findall(r"`([a-z][a-z0-9_-]+)`", domain_meta.group(1)))
        if domain_meta
        else set()
    )
    domain_listed = set(re.findall(r"`([a-z][a-z0-9_-]+)`", domain_text)) - domain_meta_skills
    for skill in domain_listed - custom_set:
        fail(f"SKILL-CATALOG-DOMAIN.md lists `{skill}` in domain tables but it is not custom")
    for skill in custom_set - domain_listed:
        fail(f"SKILL-CATALOG-DOMAIN.md missing custom skill `{skill}` from domain tables")

    expected_snippets = {
        "README.md": [
            f"{fs_count} skills",
            "repository-archaeology",
            "architecture-review",
        ],
        "SKILL.md": [f"{fs_count} skills", "repository-archaeology", "design-review"],
        "SKILL-CATALOG.md": [f"# SDLC Skills Catalog — {fs_count} Skills"],
        "SKILL-CATALOG-DOMAIN.md": [
            f"{custom_count} custom skills",
            f"{fs_count} verified skills",
        ],
        "docs/index.md": [f"{fs_count} verified skills", f"{custom_count} custom skills"],
        "docs/catalog-governance.md": [
            f"Repository skill directories: **{fs_count}**",
            f"Global skill directories: **{fs_count}**",
        ],
    }

    doc_files = {
        "README.md": root / "README.md",
        "SKILL.md": root / "SKILL.md",
        "SKILL-CATALOG.md": root / "SKILL-CATALOG.md",
        "SKILL-CATALOG-DOMAIN.md": root / "SKILL-CATALOG-DOMAIN.md",
        "docs/index.md": root / "docs" / "index.md",
        "docs/catalog-governance.md": root / "docs" / "catalog-governance.md",
    }

    for label, snippets in expected_snippets.items():
        text = read_text(doc_files[label])
        for snippet in snippets:
            if snippet not in text:
                fail(f"{label} missing expected text: {snippet}")

    return errors


if __name__ == "__main__":
    root = ROOT
    if len(sys.argv) > 1:
        root = Path(sys.argv[1]).resolve()
    errors = validate(root)
    if errors:
        print("VALIDATION FAILED")
        for err in errors:
            print(f"- {err}")
        sys.exit(1)

    # Recompute counts for the human-readable summary without re-running checks.
    fs_count = len(
        sorted({p.name for p in (root / "skills").glob("*/") if (p / "SKILL.md").exists()})
    )
    data = json.loads(read_text(root / "skills.json"))
    custom_count = len(
        {s for arr in data.get("categories", {}).values() for s in arr}
    )
    print("VALIDATION PASSED")
    print(f"- filesystem skills: {fs_count}")
    print(f"- custom skills (documented): {custom_count}")
    print("- catalogs and docs are structurally consistent")
