---
status: landed
updated: 2026-08-25
depends_on: [repo-tasks]
---

## Context

`template/pyproject.toml.jinja` carries a comment above `[dependency-groups]` explaining why the
empty `dev` group cannot take the `dev = []` shape dprint prefers (and that `dependencies = []`
already uses): `repo-tasks configs.ensure-deps` spliced its entries in right after the `[`, which on
a one-line empty array produced `dev = [  "basedpyright...",` — rejected by dprint, failing the
generated repo's first `inv quality.check`. Confirmed live 2026-08-23, 6 of 7 e2e combinations.

That defect is fixed upstream as of repo-tasks commit `2f79b4b` (2026-08-25): `ensure_deps` now
rebuilds a blank `dev = []` or `dev = [\n]` as the one multi-line shape dprint accepts, with a unit
test pinning the exact output and an integration test running the real `dprint check` over it. The
workaround here has outlived the bug.

## Recommended direction

Once this repo's pinned `repo-tasks` includes that commit:

1. Delete the template comment and collapse the empty group to `dev = []`, matching `dependencies`.
   Keep the `web_service` branch that adds `"httpx"` — that one is never empty, so it takes the
   multi-line shape on its own.
2. Re-run the e2e matrix; the 6 previously-failing combinations are the regression check.

## Landed 2026-08-25

Step 1 in `8362c92`. Step 2: the global tool was moved to `main` (`09321ae`, well past `2f79b4b`)
with `inv repo-tasks.update`, and the full e2e matrix passed 10/10 — the six previously-failing
combinations included. The bootstrap stamp stays unpinned (no release tag exists), so CI has always
installed `main` and never needed the wait.

## Migrated to

Nothing — the template comment is gone, the `[]` shape is in `template/pyproject.toml.jinja`, and
the e2e is the regression check. The upstream fix's own record is repo-tasks' unit and integration
tests around `ensure_deps`.
