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
    "docs/final-audit-2026-07-08.md": ROOT / "docs" / "final-audit-2026-07-08.md",
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
custom_count = 46

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
    "docs/final-audit-2026-07-08.md": [
        f"Repository skills: **{fs_count}**",
        f"Global mirrored skills: **{fs_count}**",
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
