---
status: idea
updated: 2026-08-25
depends_on: [repo-tasks]
---

## Context

`template/pyproject.toml.jinja` carries a comment above `[dependency-groups]` explaining why the
empty `dev` group cannot take the `dev = []` shape dprint prefers (and that `dependencies = []`
already uses): `repo-tasks configs.ensure-deps` spliced its entries in right after the `[`, which
on a one-line empty array produced `dev = [  "basedpyright...",` — rejected by dprint, failing the
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

[NEEDS CLARIFICATION: is the pinned `repo-tasks` version already past `2f79b4b`, or does this wait
on a release/`inv repo-tasks.update` first? Check the bootstrap stamp before starting.]
