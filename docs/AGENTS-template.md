# AGENTS Template

Use this template when you want a repository to preserve the same governance model used in `Skill-Playground`.

Adapt the paths, source-of-truth rules, and validation commands to the target repository.

```md
# AGENTS.md

## Mission

Treat this repository as a living engineering system rather than a loose collection of files.

Optimize for long-term coherence, maintainability, and engineering quality rather than local convenience.

When working in this repo:

- optimize for high cohesion and low coupling
- avoid duplication, drift, and unnecessary capability inflation
- prefer reusable concepts over narrow one-off additions
- keep code, documentation, and automation consistent with the current repository state

## Default Working Rules

Before creating or modifying substantial artifacts:

1. inspect the existing structure for overlap or drift
2. determine whether the need is best solved by:
   - enhancing an existing artifact
   - simplifying or splitting an overloaded artifact
   - merging overlapping artifacts
   - creating something new only if it adds clear value
3. update all affected documentation and indexes in the same change

## Consistency Requirements

Whenever the repository structure or public behavior changes, keep these aligned as needed:

- source directories
- README
- entry-point documentation
- catalogs or indexes
- machine-readable manifests
- governance docs
- automation and validation scripts

If exact counts are mentioned anywhere, verify them from the filesystem or other real source of truth instead of copying old numbers.

## Source of Truth

Define the primary source of truth explicitly.

Example:

- workspace source of truth: `<repo>/<source-dir>`
- mirrored external location: `<external-mirror-path>`

If documents disagree with the source of truth, update the documents.

## Sync Model

If the repository mirrors content elsewhere, define parity precisely.

Example:

- parity means full folder contents, not only matching folder names
- changes should preserve parity unless a task explicitly says otherwise

After sync-affecting work, run the appropriate maintenance commands.

Example:

1. `<sync-command>`
2. `<validate-command>`
3. `<parity-check-command>`

Or provide a convenience wrapper:

- `<combined-command>`

## Documentation Style

- prefer clear operational language over marketing language
- be explicit about scope, source of truth, and maintenance rules
- do not leave stale counts or unsupported claims in docs
- when uncertain, state the verified fact and note what still needs verification

## Change Heuristics

Before adding new structure, ask:

- does this already exist?
- is it partially covered already?
- should the current artifact be expanded instead?
- would a separate artifact improve modularity or only add noise?
- does the change improve reuse, discoverability, maintainability, or engineering quality?

Only add new structure when the answer is materially yes.

## Validation

For any meaningful change:

- run the most specific validation available first
- then run broader repository checks if they exist
- do not claim validation passed unless it was actually run
- if validation cannot be run, state why
```

## Notes for Adaptation

Replace the placeholders with repo-specific facts:

- source directories
- mirrored directories
- validation commands
- catalogs or manifests
- any architecture charter such as `To-do.md`, `docs/governance.md`, or ADRs

## Suggested Usage

This template is most useful for repositories that have one or more of the following:

- mirrored local/global content stores
- generated catalogs or indexes
- skill or prompt ecosystems
- policy-heavy engineering repositories
- documentation that can drift from the filesystem
