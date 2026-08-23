---
status: landed
updated: 2026-08-23
---

# Two real template bugs found while verifying the dependency/CI redesign

## Context

Surfaced 2026-08-23 while verifying `power-user-linux-setup`'s
`plans/2026-08-20-runtime-dev-venv-split.md` scaffoldapy convergence — running a real generated
project's `inv quality.check` for the first time (previously never exercised at generation time,
since `copier.yml`'s `_tasks` only ran `configure`, never `quality.check`). Both are pre-existing,
unrelated to the dependency/CI work that surfaced them — not caused by it, just never visible before.

## Bug 1: dprint reflow on the template's own README.md/SKILL.md markdown

`dprint check` fails on the rendered `README.md` and `.agents/skills/<name>/SKILL.md` — their prose
line-wrapping doesn't match dprint's markdown formatting rules. Affects every generated project
(not interface-specific). Fix: run `dprint fmt` against the template's own `README.md.jinja`/
`SKILL.md.jinja` sources (or the rendered output) and reflow to match, then re-verify.

## Bug 2: `contextlib.suppress` used with `async with` in the `skill` interface's `orchestrator.py`

Real runtime bug, not just a lint finding — confirmed via `TypeError` at actual test run time, and
also a basedpyright `reportGeneralTypeIssues` error (not just a warning):

```
async with semaphore, contextlib.suppress(SourceQueryError):
```

`contextlib.suppress` is a sync context manager only (`__enter__`/`__exit__`, not
`__aenter__`/`__aexit__`) — using it inside an `async with` fails at runtime. Only affects the
`skill` interface's generated `orchestrator.py` (the `_bounded_query` helper). Fix: either wrap it
in `contextlib.AsyncExitStack`, or use a plain sequential `with contextlib.suppress(...):` nested
inside the `async with semaphore:` block instead of combining both in one `async with`.

## Next step

Not yet scoped or fixed — pick one, fix it, verify against a fresh `copier copy` + real
`inv quality.check` run (not just template inspection), same way the dependency/CI work was verified.

## Resolution

Both fixed 2026-08-23. Bug 2: `orchestrator.py.jinja`'s `_bounded_query` now nests a plain
`with contextlib.suppress(...)` inside `async with semaphore:` instead of combining both in one
`async with`. Bug 1: reflowed `README.md.jinja` and `SKILL.md.jinja` prose to match dprint's
markdown wrapping (`textWrap: always`, 100-col) — derived by running `dprint fmt` against real
rendered output and translating the wrap points back through the jinja placeholders. Verified with
fresh `copier copy` renders across all six `interface` combinations (`dprint check` on the rendered
markdown, real `pytest` run, and a full `inv quality.check` on a generated `skill`-interface
project) plus the existing repo test suite (17 passed).

## Migrated to

Nothing — pure code changes, self-explanatory from the diff/commit history. No docs/contributing
content needed.
