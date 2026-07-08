import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
DOC_FILES = {
    "README.md": ROOT / "README.md",
    "SKILL.md": ROOT / "SKILL.md",
    "SKILL-CATALOG.md": ROOT / "SKILL-CATALOG.md",
    "SKILL-CATALOG-DOMAIN.md": ROOT / "SKILL-CATALOG-DOMAIN.md",
    "docs/index.md": ROOT / "docs" / "index.md",
    "docs/catalog-governance.md": ROOT / "docs" / "catalog-governance.md",
}
SKILLS_JSON = ROOT / "skills.json"

errors = []


def fail(msg: str):
    errors.append(msg)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


skill_files = sorted(SKILLS_DIR.glob("*/SKILL.md"))
skill_names = []
for file in skill_files:
    text = read_text(file)
    if not text.startswith("---\n"):
        fail(f"{file.relative_to(ROOT)}: missing opening frontmatter delimiter")
        continue
    name_match = re.search(r"^name:\s*(.+)$", text, re.MULTILINE)
    desc_match = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
    if not name_match:
        fail(f"{file.relative_to(ROOT)}: missing name in frontmatter")
        continue
    if not desc_match:
        fail(f"{file.relative_to(ROOT)}: missing description in frontmatter")
    skill_names.append(name_match.group(1).strip())

fs_skills = sorted(set(skill_names))
fs_count = len(fs_skills)

catalog_text = read_text(ROOT / "SKILL-CATALOG.md")
domain_text = read_text(ROOT / "SKILL-CATALOG-DOMAIN.md")
cheatsheet_text = read_text(ROOT / "SDLC-PHRASE-CHEATSHEET.md")

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

skills_json = json.loads(read_text(SKILLS_JSON))
# custom count is DERIVED from the manifest (not hardcoded) so union sync that
# adds skills under the "imported" bucket keeps the gate green automatically.
custom_count = len(
    {skill for arr in skills_json.get("categories", {}).values() for skill in arr}
)
if skills_json.get("total_skills") != fs_count:
    fail(
        f"skills.json total_skills={skills_json.get('total_skills')} but filesystem has {fs_count}"
    )
if skills_json.get("custom_skills") != custom_count:
    fail(
        f"skills.json custom_skills={skills_json.get('custom_skills')} but expected {custom_count}"
    )

json_skills = sorted(
    {skill for arr in skills_json.get("categories", {}).values() for skill in arr}
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

for label, snippets in expected_snippets.items():
    text = read_text(DOC_FILES[label])
    for snippet in snippets:
        if snippet not in text:
            fail(f"{label} missing expected text: {snippet}")

if errors:
    print("VALIDATION FAILED")
    for err in errors:
        print(f"- {err}")
    sys.exit(1)

print("VALIDATION PASSED")
print(f"- filesystem skills: {fs_count}")
print(f"- custom skills (documented): {custom_count}")
print("- catalogs and docs are structurally consistent")
