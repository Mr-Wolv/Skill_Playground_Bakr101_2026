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


def _read(path: Path) -> tuple[str | None, str | None]:
    """Read text safely. Returns (text, None) on success or (None, error_msg)
    if the file is missing/unreadable. Keeps validate() crash-free so any
    drift (corrupt/missing doc) is REPORTED, never thrown."""
    try:
        return path.read_text(encoding="utf-8"), None
    except FileNotFoundError:
        try:
            rel = path.relative_to(ROOT)
        except ValueError:
            rel = path
        return None, f"{rel}: missing required file"
    except OSError as e:
        return None, f"{path}: unreadable ({e})"


def _load_json(path: Path) -> tuple[dict, str | None]:
    """Load JSON safely. Returns (data, None) or ({}, error_msg)."""
    text, err = _read(path)
    if err:
        return {}, err
    try:
        return json.loads(text), None
    except json.JSONDecodeError as e:
        return {}, f"{path.name}: invalid JSON ({e})"


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
        text, err = _read(file)
        if err:
            fail(err)
            continue
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
        name = name_match.group(1).strip().strip('"').strip("'")
        skill_names.append(name)

    fs_skills = sorted(set(skill_names))
    fs_count = len(fs_skills)

    catalog_text, err = _read(root / "SKILL-CATALOG.md")
    if err:
        fail(err)
        catalog_text = ""
    domain_text, err = _read(root / "SKILL-CATALOG-DOMAIN.md")
    if err:
        fail(err)
        domain_text = ""
    cheatsheet_text, err = _read(root / "SDLC-PHRASE-CHEATSHEET.md")
    if err:
        fail(err)
        cheatsheet_text = ""
    readme_text, err = _read(root / "README.md")
    if err:
        fail(err)
        readme_text = ""
    skill_md_text, err = _read(root / "SKILL.md")
    if err:
        fail(err)
        skill_md_text = ""

    # README only lists skills inside its category table rows (`| ... | ... |`);
    # scanning the whole file would false-positive on command/fence code-spans
    # (uv, pytest, make, ...). Restrict to table-row lines.
    readme_rows = "\n".join(
        ln for ln in readme_text.splitlines() if ln.strip().startswith("|")
    )
    readme_skills = sorted(set(re.findall(r"`([a-z][a-z0-9_-]+)`", readme_rows)))

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

    for skill in readme_skills:
        if skill not in fs_skills:
            fail(f"README.md references missing skill: {skill}")

    # SKILL.md "Skill Categories" table lists representative skills in plain-text
    # cells (comma-separated). They must all be real on-disk skills.
    skill_md_repr = set()
    for ln in skill_md_text.splitlines():
        if not ln.strip().startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        # representative column is the 2nd cell; skip header/separator rows
        if len(cells) < 2 or cells[0].startswith("Category"):
            continue
        for tok in re.split(r",\s*", cells[1]):
            tok = tok.strip().strip("`")
            if re.fullmatch(r"[a-z][a-z0-9_-]+", tok):
                skill_md_repr.add(tok)
    for skill in skill_md_repr:
        if skill not in fs_skills:
            fail(f"SKILL.md references missing skill: {skill}")

    # Orphan check: every skill directory must be documented somewhere — either
    # named in skills.json (custom categories or community list) or referenced
    # by backtick in one of the catalog/overview docs. A skill present on disk
    # but absent from both is silently undocumented.
    _jdata, err = _load_json(skills_json)
    if err:
        fail(err)
        # cannot proceed without the manifest; remaining checks are meaningless
        return errors
    _json_names = {
        s for arr in _jdata.get("categories", {}).values() for s in arr
    } | set(_jdata.get("community_skill_names", []))
    mentioned = set(_json_names)
    for doc in (catalog_text, domain_text, cheatsheet_text, readme_text, skill_md_text):
        mentioned |= set(re.findall(r"`([a-z][a-z0-9_-]+)`", doc))
    for skill in fs_skills:
        if skill not in mentioned:
            fail(f"orphan skill (on disk, documented nowhere): {skill}")

    data, err = _load_json(skills_json)
    if err:
        return errors
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

    # community_skill_names must enumerate exactly the non-custom skills on disk
    # (filesystem minus the custom set), with no overlap and length == community_skills.
    # This closes the gap where community skills were only a count, so docs that
    # reference individual community skills (e.g. SKILL-CATALOG-DOMAIN.md) could not
    # be reconciled by name.
    community_list = data.get("community_skill_names")
    if not isinstance(community_list, list):
        fail("skills.json missing 'community_skill_names' list")
    else:
        community_set = set(community_list)
        custom_set = {s for arr in data.get("categories", {}).values() for s in arr}
        expected_community = set(fs_skills) - custom_set
        if len(community_list) != data.get("community_skills"):
            fail(
                f"skills.json community_skill_names={len(community_list)} "
                f"but community_skills={data.get('community_skills')}"
            )
        if community_set & custom_set:
            fail(
                "skills.json community_skill_names overlaps custom set: "
                f"{sorted(community_set & custom_set)}"
            )
        if community_set != expected_community:
            extra = sorted(community_set - expected_community)
            missing = sorted(expected_community - community_set)
            if extra:
                fail(f"skills.json community_skill_names lists non-community: {extra}")
            if missing:
                fail(f"skills.json community_skill_names missing: {missing}")

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
        text, err = _read(doc_files[label])
        if err:
            fail(err)
            continue
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
    _summary, _err = _load_json(root / "skills.json")
    custom_count = len(
        {s for arr in _summary.get("categories", {}).values() for s in arr}
    ) if not _err else 0
    print("VALIDATION PASSED")
    print(f"- filesystem skills: {fs_count}")
    print(f"- custom skills (documented): {custom_count}")
    print("- catalogs and docs are structurally consistent")
