---
status: idea
updated: 2026-09-26
source_repo: github.com-personal/repo-tasks
source_session: bcf810d6-38c7-48d3-adfe-2ff30399d4c9.jsonl
source_moment: 2026-09-26
source_plan: plans/2026-08-27-pytest-plugin-survey.md (retired the same day)
---

# Which pytest plugins a generated repo gets per interface

## Context

`repo-tasks` ships three pytest plugins family-wide through the `repo-tasks-quality` manifest:
`pytest-cov`, `pytest-socket` and `pytest-timeout`, each chosen because it does nothing until asked.
Its plugin survey ran 2026-08-30 over twenty-four candidates, and the result lives in that repo's
`contributing/test-tiers.md`, "Pytest plugins: what ships, what is recommended, what was rejected".

That survey could not answer one question, because it belongs here: **which plugins a generated
project should get because of the interface it was generated for**, not because every repo in the
family needs them. The user settled on 2026-09-26 that this is scaffoldapy's decision, and retired
the survey plan in `repo-tasks` with this filed in its place.

## Evidence

The two concrete candidates, from the survey's recommend table:

- **`syrupy`** (snapshot assertions): recommended, not shipped, "precisely because that repo, not
  this one, has the snapshot concern". scaffoldapy renders templates and currently asserts on them
  by hand.
- **An async test plugin for `web_service`/`mcp_server`**: `pytest-asyncio` was rejected for the
  shared manifest because `anyio` already fills the slot family-wide, and `repo-tasks` derives
  `anyio_mode` into each consumer's `pytest.ini`. Whether a generated async interface needs anything
  beyond that is the open part.

This sits beside scaffoldapy's own `plans/2026-08-30-generated-test-layout.md`, which works out the
same split for the test tree itself.

## Open questions

[NEEDS CLARIFICATION: does `syrupy` belong in scaffoldapy's own dev group, for its template tests,
or in a generated project's, or both?]

[NEEDS CLARIFICATION: does any generated interface need an async plugin beyond the `anyio` mode
`repo-tasks` already derives? If not, say so in the generated-test-layout plan and close this.]

## Recommended direction

Decide it alongside `generated-test-layout`, since both are "what the generated test tree looks like
per interface". Anything chosen goes in the template's dependency selection, not in `repo-tasks`'
shared manifest.
