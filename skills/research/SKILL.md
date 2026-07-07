---
name: research
description: Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated to a background agent.
---

# Research

## Boundary

Use this skill when the job is to answer a substantive question by investigating primary sources and capturing the findings in a durable Markdown artifact inside the repo.

Do not use this skill when the main need is guidance on how to evaluate sources, analyze standards, or synthesize evidence without necessarily producing a repo research note. For that, use `research-methodology`.

Do not use this skill for failure investigation or root-cause workflows after incidents. For that, use `failure-analysis`, `root-cause-analysis`, `five-whys-analysis`, or `postmortem` depending on depth and purpose.

Spin up a **background agent** to do the research, so you keep working while it reads.

Its job:

1. Investigate the question against **primary sources** — official docs, source code, specs, first-party APIs — not a secondary write-up of them. Follow every claim back to the source that owns it.
2. Write the findings to a single Markdown file, citing each claim's source.
3. Save it where the repo already keeps such notes; match the existing convention, and if there is none, put it somewhere sensible and say where.
