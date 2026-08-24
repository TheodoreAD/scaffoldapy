---
status: idea
updated: 2026-08-25
depends_on: [repo-tasks]
---

# CI fails with `actionlint: command not found` since the gate grew `workflow-check`

## Context

Found 2026-08-25 from `power-user-linux-setup`, during a CI-failure sweep for an unrelated plan
(`power-user-linux-setup/plans/2026-08-23-git-hooks-for-quality-gate.md`). This repo's `CI` run
32769297205 (commit `77d06bb`, 2026-08-24 19:38Z) fails `inv quality.check` with exit 127:

```
bash: line 1: actionlint: command not found
actionlint .github/workflows/ci.yml
##[error]Process completed with exit code 127.
```

The next run (`c1beaa3`, 22:45Z) fails earlier on `dprint check` (exit 20), so it never reaches the
step — the 127 is still there underneath it.

Cause, verified against `repo-tasks` history: `afe1bcf` (2026-08-24 21:26 +0300,
"quality.workflow-check: lint GitHub Actions workflows in the gate") added an `actionlint` step to
`quality.check`, and its sibling `5c5ab92` added `actionlint-py` (and `act-bin`) to `repo-tasks`'
own `dependency-groups` — the list `repo-tasks configs.ensure-deps` copies into consumers. This
repo's `pyproject.toml` `dev` group predates that: it has `shellcheck-py`/`shfmt-py` but no
`actionlint-py`, so CI's `inv dev-env.setup` (`uv sync`) never installs the binary the gate now
calls. Locally the same gate passes only because `power-user-linux-setup` installs `actionlint-py`
user-wide (`uv-tool`), which is exactly the "user-wide install is for the human, the group is what
CI resolves" split `~/AGENTS.md` warns about under "Installing a tool on this machine".

The bootstrap script pins no version (`repo-tasks @ git+https://github.com/TheodoreAD/repo-tasks`),
so CI picked up the new gate step the moment `repo-tasks` pushed it, while this repo's declared
tools stayed where `ensure-deps` last left them. Any consumer in the family whose `dev` group was
populated before `5c5ab92` has the same gap; `power-user-linux-setup` already carries
`actionlint-py` (its CI is green on this step).

## Recommended direction

1. Re-run `repo-tasks configs.ensure-deps` here, then `inv deps.lock` (or the repo's equivalent) so
   `uv.lock` picks up `actionlint-py`; commit both. That is the designed refresh path, not a
   hand-edit of the `dev` group — the `pyproject.toml` comment already says the group is
   `ensure-deps`-owned.
2. Generated repos are unaffected going forward: `copier.yml` runs `repo-tasks configs.ensure-deps`
   at generation time, so a fresh render already gets the current list. Confirm with one e2e render
   that `actionlint-py` lands in the output's `dev` group.
3. Run `inv quality.check` locally with `actionlint` removed from `PATH` (or in the container tier)
   to prove the group, not the user-wide tool, satisfies the step — the local green that hid this is
   the thing to stop trusting.

[NEEDS CLARIFICATION: is a consumer's `dev` group drifting behind `repo-tasks`' tool list something
`configs.diff`/`configs.status` should report, the way they already report drifted config files? A
gate step that depends on a tool the consumer never declared is the same shape as a pulled
`pytest.ini` naming a directory the consumer never created — the shared side moved and the consumer
found out from CI. That belongs to `repo-tasks`, not here; noting it so it isn't lost.]
