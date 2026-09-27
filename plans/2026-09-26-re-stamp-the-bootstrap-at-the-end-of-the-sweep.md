---
status: idea
updated: 2026-09-26
source_repo: github.com-personal/repo-tasks
source_session:
source_moment: 2026-09-26
source_plan: plans/2026-08-25-consumer-transitions.md
---

# The v0.3.0 sweep gains a last step: re-stamp `bootstrap-repo-tasks.sh`

## Context

Filed from a `repo-tasks` session on 2026-09-26. Nothing was written to this tree; everything below
is read-only measurement taken from outside it.

**An amendment to `2026-09-08-sweep-to-repo-tasks-v0-3-0.md`, filed for this repo on 2026-09-08 and
still unabsorbed, rather than new work beside it.** That plan's four measured items are still
exactly what `inv consumers.diff` reports today — `ruff.toml`, `dprint.json`, `pytest.ini` behind,
and `hadolint-py` declared without the manifest's `!=2.15.1.2`. What it cannot know is that
`repo-tasks` decided on 2026-09-26 that **a sweep ends by re-stamping the consumer's bootstrap**,
and that the reporter now prints a fifth line for this repo: `bootstrap unpinned`.

## Evidence

`bootstrap-repo-tasks.sh:14` carries the unpinned form —
`'repo-tasks @ git+https://github.com/TheodoreAD/repo-tasks'`, no `@vX.Y.Z` — and `ci.yml:25` runs
`./bootstrap-repo-tasks.sh`. So this repo's CI installs `repo-tasks` `main` at run time, while a
developer here is on `v0.3.0`, the latest tag, which `inv repo-tasks.update` installs.

The premise the old wording rested on has expired: "unpinned until a `vX.Y.Z` tag exists" stopped
being the reason on 2026-09-04, when `v0.2.0` was cut. A tag existing does nothing until `stamp` is
re-run in this repo.

## What pinning does to this repo specifically

This is the one consumer where pinning changes more than CI, and the reason it was safe to decide:

- **Until now, this repo's own CI was the family's only post-push check of what `repo-tasks` does to
  a generated repo** — it installed `main`, then ran the e2e tier. Pinned, it tests the tag it was
  stamped at and says nothing about unreleased `repo-tasks`.
- **`repo-tasks`' `canary.yml` covers that instead**, since 2026-09-13: it checks out this repo's
  default branch, installs the `repo-tasks` checkout being pushed as the global tool, and runs
  `inv test.integration`. Its header and `repo-tasks`' `contributing/quality-gate.md` were rewritten
  on 2026-09-26 to describe both states, so nothing there needs changing when the pin lands here.
- **Task-code fixes stop arriving for free.** `repo-tasks`' own plan records that this repo "was
  never behind" on two link-check fixes because the global tool moved. After pinning, the tool on a
  developer machine still moves, but CI does not until the next tag plus a re-stamp.

## Recommended direction

Absorb into `2026-09-08-sweep-to-repo-tasks-v0-3-0.md`, adding one step after the gate and
`inv test.integration` both pass: `inv repo-tasks.stamp` in this checkout, committing the
regenerated `bootstrap-repo-tasks.sh`.

- **After the gate, not before**, since `stamp` pins the version _active in the process running it_
  — what this repo was verified against — rather than the newest tag. It needs the network.
- **Not `inv configure`**, which calls `stamp` but also re-runs dev-env setup and `configs.pull` out
  of the sweep's order.
- **Whether the template's generated `bootstrap-repo-tasks.sh` should start pinned** is a separate,
  larger question for this repo — a generated repo is stamped by `inv configure` at generation, so
  it probably already is. Not measured from the filing side.
