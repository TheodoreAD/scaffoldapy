---
status: landed
updated: 2026-09-08
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

## Questions, as answered

~~Does a freshly generated project resolve the current stubs by itself?~~ **Yes**, and it needed no
throwaway generation to find out: this session's end-to-end tier renders ten real projects, and
every one installed `invoke-stubs==0.3.0 (from git+…@f70ff01e)`. The unpinned `@ git+` spec in the
manifest `repo-tasks` splices does what it looked like it would do — a new project's first lock
takes whatever `main` holds. Nothing here is owed on the generated side.

## Landed 2026-09-08

`inv deps.lock --package invoke-stubs` took `ad052ca` (0.1.0) straight to `f70ff01` (0.3.0),
skipping 0.2.0 and both halves of the cost `repo-tasks` paid for it. `inv quality.precommit` green
with **no source change at all** — the measurement filed with this plan held: no file here indexes
`.collections[`, so the `Any` that 0.2.0 made honest never surfaces, and there were no casts to add
under 0.2.0 or remove under 0.3.0.

The six `pyright: ignore` lines this repo carries were unaffected;
`reportUnnecessaryTypeIgnoreComment` is on, so a stub bump that made one redundant would have failed
the gate rather than gone unnoticed.
