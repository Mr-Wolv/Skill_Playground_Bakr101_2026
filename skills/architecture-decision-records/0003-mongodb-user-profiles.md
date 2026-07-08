# 0003: MongoDB for User Profiles

- Status: Deprecated
- Date: 2023-06-15
- Superseded by: [0020-deprecate-mongodb.md](0020-deprecate-mongodb.md)

## Context

User profiles were originally stored in MongoDB for flexible, schema-less
documents.

## Decision (historical)

Store user profiles in MongoDB.

## Consequences

- This decision was later reversed. MongoDB added operational surface area
  without delivering enough schema flexibility to justify it, and the team
  preferred a single primary datastore.
- See [0020](0020-deprecate-mongodb.md) for the deprecation and migration plan.
