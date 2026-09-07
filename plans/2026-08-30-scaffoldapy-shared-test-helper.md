---
status: idea
updated: 2026-08-30
---

# `tests/support.py` is the family's only bare-import test helper

## Context

Filed from `repo-tasks` on 2026-08-30 while answering the open question in that repo's
`plans/2026-08-30-tests-import-layout.md` — "is the shared-helper use case real for this family, or
was it one consumer once?". Answering it meant surveying every personal repo with a `tests/` tree,
and `scaffoldapy` came out of that survey as the one case with a latent problem. Nothing in this
repo was touched.

**The measurement.** Nine personal repos have tests. Two express a shared test world, and they do it
differently:

| repo          | how                                                                                                |
| ------------- | -------------------------------------------------------------------------------------------------- |
| `scaffoldapy` | `tests/support.py`, imported by four files across `tests/`, `tests/unit/` and `tests/integration/` |
| `ingesta`     | a 159-line `tests/conftest.py` of session-scoped fixtures                                          |

The other seven have no helper module at all. So the need is real and recurring — but it is a
minority shape, and the two repos that have it answered it in ways that have very different
properties.

[PITFALL: `tests/conftest.py` does a bare `from support import BASE_ANSWERS, TEMPLATE_DIR, Render`.
That resolves only because pytest's default `prepend` import mode puts `tests/` at the **front** of
`sys.path` for the session, which means a top-level module named `support` shadows anything else by
that name — for the test run, for every import underneath it. `support` is close to the most
collidable module name available. It works today and there is no evidence of a collision; the point
is that it works by shadowing rather than by namespacing, and the failure mode when it does break is
an import resolving to the wrong module rather than an error.]

The irony worth recording, because it is what makes the decision non-obvious: this is the repo that
would gain most from a packaged `tests/` (a real `tests.support` import, no shadowing), and it is
also the repo leaning hardest on the very `sys.path` property that packaging removes.

## Why this is filed here rather than decided in `repo-tasks`

`repo-tasks` was weighing a **family-wide** change — `__init__.py` in every `tests/` tree,
`extraPaths: ["."]` in the shipped `pyrightconfig.json`, and a ruff `banned-api` guard to close the
second import route that `extraPaths` opens. Measured there, that combination costs nothing
mechanically (pytest, ruff, basedpyright and coverage all unchanged).

But the survey undercut the case for it: the need is in two of nine repos, and neither is currently
blocked. That makes a family-wide config change a large answer to a small, local question — and the
local question is this repo's.

This also bears on this repo's own `plans/2026-08-30-generated-test-layout.md`, which explicitly
waits on the `repo-tasks` plan before writing anything about basenames into the generated
`AGENTS.md`. That wait can now end: the family-wide decision is no longer the blocker it looked
like, because the honest recommendation is per-repo.

## Open questions

**The conftest route is already closed, and this plan's first draft got that wrong.** It proposed
moving `support.py`'s contents into `tests/conftest.py` as fixtures — the `ingesta` shape — on the
strength of a survey that had read the module's imports but not its docstring. The module documents
that exact move as rejected, for two failure modes it records as confirmed live:

- A tier-local `tests/integration/conftest.py` shadows `tests/conftest.py` for that tier only, which
  surfaces as a silent, direction-dependent `ImportError`.
- This repo has a **second** `tests/conftest.py`, under `template/`, which wins outright whenever
  pytest falls back to searching from the working directory — precisely what the shipped
  `testpaths = tests/unit` triggers in a repo that has not split its tests yet.

[DECISION: `from conftest import X` is ambiguous in this repo in two independent ways, so a distinct
module name is the fix, not the problem. Whatever happens to the import mechanism, the _contents_
stay in a module of their own. That leaves renaming and packaging as the only live options.]

Worth stating what the module actually carries, because it raises the stakes on getting the import
right: `COMBINATIONS` is the single parametrization source for the entire suite including the real
end-to-end quality gate, and two of its entries exist only because of specific past bugs (a
`browser_session × multi_source` crossing that generated non-importable code, and two `-long-name`
entries pinning where dprint's 100-column reflow wraps interpolated `package_name`). An import that
silently resolved to the wrong module would not fail loudly — it would run a different, smaller
matrix.

[NEEDS CLARIFICATION: or package `tests/` in this repo alone — add `__init__.py`, import
`from tests.support import …`, and take `extraPaths: ["."]` in this repo's `pyrightconfig.json`
only? That is the pytest-recommended arrangement for `prepend` mode and it fixes the shadowing
properly. But `pyrightconfig.json` is pulled from `repo-tasks` by `configs.pull`, so a local
`extraPaths` is per-repo drift in a file whose whole design is that it does not drift — which is
exactly the coupling that sent this question to `repo-tasks` in the first place.]

[NEEDS CLARIFICATION: or leave it. Nothing is broken, the collision is hypothetical, and a rename
from `support.py` to something unlikely to collide (`_scaffoldapy_test_support.py`) buys most of the
safety for one `git mv` and four import lines. Cheapest of the three, and it neither adopts nor
forecloses the others.]

## Superseded 2026-09-04: the family decided, and it decided packaging

The rename recommended below is no longer the move. `repo-tasks` settled the family-wide question on
2026-09-04, by the user: **`tests/` is a package**, following pytest's own recommendation for the
`prepend` import mode. Landed there in commit `a8bfebc`:

- `__init__.py` in `tests/` and each tier.
- `extraPaths: ["."]` in the **shipped** `pyrightconfig.json`.
- A `flake8-tidy-imports` `banned-api` entry for `src` in the **shipped** `ruff.toml`, guarding the
  second import route `extraPaths` opens. It names no package, so it is inert rather than wrong in a
  flat-layout consumer.

That removes the objection this plan raised against packaging here — that a local `extraPaths` would
be per-repo drift in a file designed not to drift. It is no longer local: it arrives through
`configs.pull` like everything else in that file.

So the fix for `tests/support.py` is now the proper one rather than the mitigation: **package
`tests/` and import `from tests.support import ...`**, which resolves by namespace instead of by
`sys.path` position and removes the shadowing mechanism outright rather than making a collision
unlikely.

[DECISION: the rename to `_scaffoldapy_test_support.py` is dropped, not deferred. It existed only as
a cheap stopgap while the family question was open; the question is closed, and doing both would
mean renaming a module twice.]

## Recommended direction

1. `inv configs.pull` to take the new `pyrightconfig.json` and `ruff.toml`.
2. Add `__init__.py` to `tests/`, `tests/unit/` and `tests/integration/`.
3. Change the three bare `from support import ...` sites to `from tests.support import ...`
   (`tests/conftest.py`, `tests/unit/test_template.py`, `tests/integration/test_e2e.py`).
4. Run this repo's gate, and specifically confirm the end-to-end test still renders and gates every
   entry in `COMBINATIONS` — that is the assertion most likely to notice an import that moved.

[PITFALL: this repo has a **second** `tests/conftest.py` under `template/`, and the packaging change
is about the real one. Do not add `__init__.py` under `template/` as part of this — what the
template generates is a separate question, owned by this repo's own
`plans/2026-08-30-generated-test-layout.md`, which was waiting on the family decision and can now
proceed. Two trees, two changes, and conflating them is how the template acquires a file nobody
chose.]

Whichever way it goes, `plans/2026-08-30-generated-test-layout.md` can stop waiting on `repo-tasks`:
the family-wide change is not happening on the strength of this evidence, so the generated
`AGENTS.md` should document the basename rule as the property of the default import mode that it
actually is.
