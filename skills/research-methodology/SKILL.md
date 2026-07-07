---
name: research-methodology
description: Source hierarchy, CRAAP test, RFC analysis, literature review, knowledge synthesis
---

# Research Methodology

Structured approach to technical research and knowledge synthesis.

## When to use

- Evaluating whether a library or approach is production-ready
- Investigating a technical topic you're unfamiliar with
- Analyzing RFCs, standards, or specification documents
- Synthesizing information from multiple sources

## Boundary

Use this skill for the method of research: source hierarchy, credibility evaluation, RFC reading, literature review, and synthesis discipline.

Do not use this skill when the user primarily wants the actual research carried out and written into the repository as a note or findings document. For that, use `research`.

Do not use this skill as a post-incident causal analysis workflow. For that, use `failure-analysis`, `root-cause-analysis`, `five-whys-analysis`, or `postmortem`.

## Instructions

1. **Define the research question** — what specifically do you need to know?
2. **Gather sources** — prioritize by the source hierarchy:
   - **Primary**: official documentation, RFCs, source code, research papers
   - **Secondary**: authoritative blog posts, technical talks, official guides
   - **Tertiary**: Stack Overflow, community forums, blog summaries
3. **Apply the CRAAP test** to each source:
   - **C**urrency — how recent is this?
   - **R**elevance — does it address your question?
   - **A**uthority — is the source reputable?
   - **A**ccuracy — is the information correct? Cross-reference.
   - **P**urpose — why was this written? Is there bias?
4. **Analyze RFCs** — identify the problem statement, proposed solution, alternatives, and adoption status
5. **Synthesize** — summarize findings, identify consensus and disagreements, and make a recommendation

## Output format

```markdown
## Research: [Topic]

### Key sources
- Official docs: [link] (authoritative)
- RFC #1234: [link] (standards track)

### Findings
1. [Finding with source attribution]

### Recommendation
[Clear recommendation based on evidence]
```

## Anti-patterns

- Citing tertiary sources as gospel (Stack Overflow answers can be wrong)
- Cherry-picking sources that support a predetermined conclusion
- Ignoring recency (a 5-year-old article may be obsolete)
