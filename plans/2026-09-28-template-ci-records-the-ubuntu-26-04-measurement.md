---
status: idea
updated: 2026-09-28
source_repo: github.com-personal/repo-tasks
source_session: 44be2918-1669-4d16-9f77-56535cc6ddeb.jsonl
source_moment: 2026-09-28T00:20:00Z
source_plan: plans/2026-09-28-ubuntu-latest-moves-to-26-04-from-2026-10-19.md
---

# The template's `ci.yml` should say `ubuntu-latest` floats on purpose, measured on 26.04

## Context

GitHub moves `ubuntu-latest` from Ubuntu 24.04 to 26.04 from 2026-10-19
(actions/runner-images#14748). repo-tasks measured the move before deciding. CI, Canary and the
shared Security audit ran on `ubuntu-24.04` and `ubuntu-26.04` side by side. Every job passed on
both, and no annotation appeared beyond GitHub's own migration notice. The user chose to **keep
floating `ubuntu-latest`**. The decision and the evidence are in repo-tasks'
`contributing/quality-gate.md`, "Workflow hardening".

Canary's job is scaffoldapy's `inv test.integration`: ten real renders of the template, each running
its generated repo's full `inv quality.check`. So the template's generated CI shape is covered by
that measurement.

The plan that decided this said to "say so in the template's `ci.yml` comment, so the next
announcement is not re-litigated". The template is here, so the edit is this repo's to make.

## Evidence

Decided in repo-tasks session `44be2918-1669-4d16-9f77-56535cc6ddeb`, by the user's answer to
"Measurement is all green. Keep floating ubuntu-latest?" choosing "Float, record and land
(Recommended)". The measured runs: repo-tasks CI `36360757263`, Canary `36360757240`, Security
`36360757585`, all on the since-deleted branch `measure/ubuntu-26-04`.

## Open questions

None. This is a comment, not a behaviour change.

## Recommended direction

Next to `runs-on: ubuntu-latest` in `template/.github/workflows/ci.yml`, and in this repo's own
`ci.yml` if it floats too, add a short comment. It should say the label floats deliberately, that
the 24.04 to 26.04 move was measured green on 2026-09-28, and where the reasoning lives.

One trap: don't pin `ubuntu-26.04` anywhere to "test ahead". actionlint does not know that label
yet, and the gate fails on `[runner-label]`.
