---
name: skills-browser
description: Interactive skill browser and reference — list, search, and describe available skills
---

# Skills Browser

Interactive browser for exploring available skills in the Skill Playground collection.

## When to use

- You want to know what skills are available
- You're looking for a skill to accomplish a specific task
- You need a quick reference on what a particular skill does

## Instructions

1. **Read `skills.json`** to get the canonical list of skills organized by category
2. **List all skills** — show the full catalog organized by category from `skills.json`
3. **Search by keyword** — find skills matching a specific term (e.g., "Docker", "tests", "Spring")
4. **Describe a skill** — read `skills/<name>/SKILL.md` and show the name, description, and key instructions
5. **Suggest skills** — given a task description, recommend which skill(s) to use

## Example output

```markdown
Available skills (from skills.json):

🧪 Testing (5): unit-test-writer, integration-test-writer, test-fixture-generator, ...
🏗️ Architecture (5): clean-architecture-principles, clean-code-principles, ...
... (categories and counts from skills.json)
```

The JSON manifest at `skills.json` is the source of truth for category membership and skill counts. Refer to it directly rather than using hardcoded lists.
