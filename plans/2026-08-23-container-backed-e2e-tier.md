---
status: idea
updated: 2026-08-23
---

## Context

Deferred from the retired e2e-coverage-holes plan (landed 2026-08-23). The e2e suite renders into
pytest's `tmp_path` on this machine, so generation still depends on the global `repo-tasks` install,
`direnv`, and an inherited `PATH` — not quite what a generated repo's real CI runner sees.

[DECISION: harden the existing `tmp_path`-based e2e first, rather than moving generation into a
container — chosen 2026-08-23. The temp-dir tests already catch real template bugs and needed no new
infrastructure; every coverage hole found that day was closable with parametrization.]

## Open questions

- [NEEDS CLARIFICATION: what bug class, if any, ever slips through that the temp-dir tier
  structurally could not have caught? This plan stays parked until one does — that's the revisit
  trigger, not a schedule.]

## Recommended direction

[DEFERRED: a container-backed e2e tier, so generation no longer depends on this machine's global
`repo-tasks` install, `direnv`, or an inherited `PATH`. `repo-tasks`' own `tests/integration/` plus
`pytest.ini`'s `--ignore` is the shape to copy if it happens.]
