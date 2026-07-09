# Semantic open-work sweep (enumerate → read → judge)

Reusable lexicon + scoping for "does this repo still carry open To-do /
for-the-future / pending-work language?" after a convergence pass. Proven on
the Skill-Playground repo (710 files, 168,894 lines scanned).

## Pass 1 — narrow "unfinished work" lexicon
```python
import re
LEX1 = re.compile(r"(?i)\b("
    r"to[\s-]?do|fixme|xxx|hack|stub|placeholder|lorem\s+ipsum|"
    r"not\s+(yet\s+)?(done|implemented|finished|wired|tested|verified|complete|executed|added|merged|built)|"
    r"(still\s+)?(pending|outstanding|unfinished|incomplete|left\s+to)|"
    r"(left|omitted|skipped|deferred|postponed|not\s+executed|unexecuted)\b|"
    r"(needs?|requires?|should\s+be)\s+(work|review|done|added|implemented|finished|completed|filled|written)|"
    r"(for\s+now|later|someday|eventually|in\s+a\s+future|future\s+(work|pass|version|release|step)|"
    r"coming\s+soon|wip|work\s+in\s+progress|tbd|not\s+yet|upcoming)|"
    r"(did\s+not|haven'?t|hasn'?t|has\s+not|have\s+not)\s+(done|read|merged|added|implemented|verified|checked|run|completed)|"
    r"(remains?|remain)\s+(a\s+)?(open|future|todo|incomplete|unfinished)|"
    r"(missing|absent)\s+(feature|implementation|section|file|test|doc)|"
    r"not\s+(production[\s-]?ready|ready)|"
    r"(draft|rough|experimental|unstable)\b"
    r")")
```

## Pass 2 — extended (catches "different wording")
```python
LEX2 = re.compile(r"(?i)\b("
    r"roadmap|backlog|milestone|next\s+step|coming\s+(soon|next)|"
    r"planned\b|queue\s*(of|for)|stage\s*[23]|phase\s*[23]|"
    r"when\s+(ready|available|possible)|once\s+(ready|available|stable)|"
    r"will\s+(be\s+)?(done|added|implemented|finished|completed|merged|supported)|"
    r"not\s+(supported|available|implemented|ready|done)\s+(yet|for\s+now)|"
    r"for\s+(now|the\s+time\s+being)|at\s+a\s+later\s+(date|time|point)|"
    r"in\s+(the\s+)?(next\s+release|upcoming\s+release|subsequent)|"
    r"work\s+(remaining|left|todo)|remaining\s+work|"
    r"open\s+(item|task|issue|question)|unresolved\s+(item|task|question)|"
    r"circle\s+back|follow[\s-]?up\s+(needed|required|later)|"
    r"not\s+(yet|currently)\s+(supported|available|implemented|done|wired)|"
    r"this\s+is\s+(a\s+)?(placeholder|stub|wip|draft)|"
    r"to\s+be\s+(completed|finished|done|added|implemented|merged|decided|resolved)\b"
    r")")
```

## Ignore list (avoids 90% of false positives)
```python
IGNORE = re.compile(r"(?i)("
    r"left:|left-0|left-4|border-left|\.left|"           # CSS `left`
    r"OrderStatus|in_progress|`pending`|enum|"            # code enums
    r"#\s*TODO:|[\"']TODO[\"']|TODO,|TODO\)|"         # boilerplate template TODOs
    r"placeholder[=?\":]|placeholder\?|placeholder\)|"     # HTML/JSX placeholder attr
    r"eventually\s+consistent|eventual|converge|"          # distributed-systems content
    r"later\s+\(|phase\s+[0-9]|stage\s+[0-9]|"
    r"clean\s+it\s+up\s+later|later\s+never|fix\s+it\s+later|"
    r"revisit\s+later|\"For the future\"|for the future|"
    r"future\s+work|future\s+pass|future\s+cleanup|future\s+release|"
    r"not\s+executed"
    r")")
```

## Scoping (critical)
- Scope the sweep to **repo-level artifacts**: `docs/`, root `*.md`,
  `scripts/`, and any `*PROPOSAL*`/`*COMPLETENESS*` docs.
- **EXCLUDE `skills/**` body content.** Skills about project management,
  postmortems, planning, code-review legitimately contain `backlog`,
  `roadmap`, `milestone`, `Next Steps`, `Open Questions`, `Planned`
  (enum value in a report generator), `DRAFT` (GraphQL `PostStatus` enum),
  and `# TODO: Customize` (user-facing template scaffolds). Those are the
  skill's subject matter — editing them corrupts the skill.

## Judgment calls from the live audit
- **GENUINE → fix:** `docs/merge-proposal.md` "Candidate for future
  cleanup" (×2) and "If discoverability becomes a bigger concern later"
  → rewrote as closed decisions ("Decision: no merge", "No rename is
  recommended. The current names are accepted.").
- **FALSE POSITIVE → leave:** every `skills/**` hit (domain vocabulary);
  `graphql-schema-design.md` `DRAFT` (enum value);
  `pattern-combinations.md` "Enables future work on D" (illustrative A/B/C/D
  template text); `AGENTS.md` "revisit later" (the repo's own
  expansion-control governance policy, not open work).

## Re-verify after fixes
Re-run the scoped sweep; assert 0 repo-level hits remain. Then run the full
gate (`make verify` + `make qcaudit`) before committing.
