---
status: idea
updated: 2026-09-07
source_repo: github.com-personal/repo-tasks
source_session: 52905ee0-50ff-4376-bd19-5ab4d9ca0a24.jsonl
source_moment: 2026-09-07T11:15:05Z
---

## Context

This repo's `uv.lock` pins `invoke-stubs` at `ad052ca` — the distribution's first commit, 0.1.0.
0.2.0 declared every module `invoke/__init__.py` re-exports from plus `util` — 16 in all — and fixed
three annotations invoke has wrong rather than missing; **0.3.0 (`f70ff01`, on `main`) is the one to
take**, adding a generic `Lexicon` and the parser subpackage's attributes on top.

`repo-tasks` took it 2026-09-07 with a green gate, which was the verification `invoke-stubs`' own
plan listed as owed before any consumer bumped. Filed from that session; nothing here was touched.

The entry appears in this repo's own `pyproject.toml` only — no template file names it — so a
generated project picks the stubs up through `repo-tasks-quality` at generation time and there is
nothing templated to keep in step.

## Evidence

Session transcript `52905ee0-50ff-4376-bd19-5ab4d9ca0a24.jsonl` under
`~/.claude/projects/-home-tdumitrescu-projects-github-com-personal-repo-tasks/`, 2026-09-07, from
"we just finished upgrading the invoke stubs".

The one cost that session paid, and why 0.3.0 rather than 0.2.0 is the target: 0.2.0 declared
`Lexicon(dict[str, Any])`, so `Collection.collections["x"]` became honestly `Any` where 0.1.0's
fall-through to invoke's untyped vendored `Lexicon` had been `Unknown | None` — silenced by the
tests tier, where `reportAny` is not. 37 errors in one file, closed with `cast(Collection, ...)`.
0.3.0's generic `Lexicon` typed those lookups at the source and all 16 casts came back out, named by
`reportUnnecessaryCast`. Going straight to 0.3.0 skips both halves.

Measured for this repo before filing: **no file here indexes `.collections[`**, and 6 lines carry a
`pyright: ignore`.

## Open questions

[NEEDS CLARIFICATION: does a freshly generated project's first `inv quality.precommit` now resolve
0.2.0 by itself? The dependency is an unpinned `@ git+` spec in the manifest `repo-tasks` splices,
so a new project's first lock should take whatever `main` holds — worth confirming once against a
real generation rather than assuming, since that is the path most consumers arrive on.]

## Recommended direction

`inv deps.lock --package invoke-stubs`, `inv venv.sync`, `inv quality.precommit`, commit the lock
bump. Then generate one throwaway project and check its lock names `13bcc9e` or later, which is the
half this repo actually owns.
