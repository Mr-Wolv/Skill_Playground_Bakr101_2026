---
name: document-reviewer
description: Review documents for clarity, structure, completeness, and consistency
---

# Document Reviewer

Reviews technical documents for quality, clarity, and completeness.

## When to use

- A document is ready for review before publishing
- An existing document needs improvement
- You're establishing documentation standards for a project

## Instructions

1. **Read the document** and assess:
   - **Clarity** — is the purpose clear? Are terms defined? Is the language precise?
   - **Structure** — is there a logical flow? Are sections well-organized? Is the navigation clear?
   - **Completeness** — are all relevant topics covered? Are there gaps?
   - **Consistency** — does it match the project's tone, terminology, and formatting?
2. **Provide actionable feedback** — point to specific sections with concrete suggestions
3. **Check technical accuracy** — verify code examples, commands, and configuration snippets
4. **Review for audience** — is the level appropriate (beginner vs. expert)?

## What to flag

- Missing table of contents for documents > 500 words
- Broken links or references to non-existent sections
- Too much jargon without explanation
- Assumptions about reader knowledge that aren't justified
- Contradictory statements
- Missing examples for complex concepts

## Review format

```markdown
## Review: [Document Title]

### Strengths
- ...

### Issues
1. **Section X, paragraph Y**: [issue description]
   **Suggestion**: [concrete fix]

### Overall
[Summary assessment with go/no-go recommendation]
```
