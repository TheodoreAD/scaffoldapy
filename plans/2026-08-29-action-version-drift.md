---
status: idea
updated: 2026-08-29
---

# GitHub Action versions have drifted, and nothing in this family watches them

## Context

Every CI run in this family now emits a deprecation annotation:

```
Node.js 20 is deprecated. The following actions target Node.js 20 but are being forced to run on
Node.js 24: actions/checkout@v4
```

Noticed 2026-08-29 on two green `ingesta` runs, whose workflow is a byte-identical copy of this
repo's `template/.github/workflows/ci.yml`. So it is not that repo's annotation — it is this
template's, reproduced in every repo generated from it, on every run.

Measured across the six personal repos cloned on this machine: **14 `actions/checkout@v4`
occurrences**, in `ci.yml`, `docs.yml`, `devcontainer.yml`, `docker-release.yml`,
`publish_on_push.yml` and `publish.yml`. Thirteen are ref pins; one, in the release workflow holding
`id-token: write`, is hash-pinned by hand, which is the single deliberate exception the family's
`zizmor.yml` describes.

Checked against the upstream release feeds rather than assumed:

| action               | pinned here | current   | notes                                    |
| -------------------- | ----------- | --------- | ---------------------------------------- |
| `actions/checkout`   | `v4`        | `v7.0.1`  | v4 → node20; v5, v6 and v7 all → node24  |
| `astral-sh/setup-uv` | `v9.0.0`    | `v10.0.1` | one major behind; no deprecation warning |

Two things worth stating because the obvious guess is wrong. **The fix is not "bump to v5"** — that
was the first assumption and it is two majors stale. And `actions/checkout` shipped v4.4.0, v5.1.0,
v6.1.0 and v7.0.1 within half an hour of each other on 2026-07-20, so upstream is actively
maintaining four majors in parallel; being on an older one is a supported position, not neglect.

## Why it has no owner today

This is the cost side of a trade this family took on purpose. The canonical `zizmor.yml` sets a
`ref-pin` policy rather than zizmor's blanket hash-pin default, and its own comment gives the
reason: pinning everywhere without dependabot means pins that silently rot, and dependabot means a
standing PR stream on repos that are pushed to directly.

That reasoning is sound and this plan does not reopen it. What it observes is the half that was
implied and never built: having declined the bot, nothing at all watches these versions, so the
first signal is a deprecation annotation on a green run — which is exactly the kind of output nobody
reads, because the run passed.

## Open questions

[NEEDS CLARIFICATION: which major to land on. `v7` is current and shares the node24 runtime with
`v5` and `v6`, so the deprecation is answered identically by any of the three and the choice is
about how often the family wants to move. Worth reading v5→v6 and v6→v7 release notes for breaking
changes before picking — a checkout major has changed default behaviour before, and this template's
copy is inherited unreviewed by every generated repo.]

[NEEDS CLARIFICATION: whether `setup-uv` moves in the same pass. It emits no warning, so it is not
urgent, but leaving it a major behind reproduces the same drift with no trigger to catch it later.
Against bundling: two version bumps in one change makes a CI regression ambiguous.]

[NEEDS CLARIFICATION: what replaces dependabot, given the family declined it. Options seen so far,
none evaluated: a periodic task in `repo-tasks`' quality namespace that compares each `uses:` pin
against the upstream latest and reports rather than edits; a scheduled workflow doing the same; or
accepting manual review and giving it a trigger, e.g. a line in this repo's release checklist. The
reporting shape fits the family's stated objection better than the PR-stream shape does, since the
objection was to standing PRs rather than to knowing.]

[NEEDS CLARIFICATION: how the bump reaches already-generated repos. `ci.yml` claims byte-identity
with this template, so a template change makes every existing copy diverge until each is pulled
forward by hand — `ingesta` re-established that identity on 2026-08-29 and would break it again the
moment this lands. Whether that is a `copier update` per repo, or a one-line manual edit each, is
the same unanswered question the byte-identity claim always carried.]

## Recommended direction

Rough, and the ordering matters more than the choices.

1. Settle the target major, and change `template/.github/workflows/` plus this repo's own
   `.github/workflows/ci.yml` in one commit, so the template and its own dogfooding stay in step.
2. Only then sweep the sibling repos, one commit each, so a regression is attributable.
3. Treat the third open question as the real deliverable. Bumping fourteen pins once and adding no
   trigger schedules this same plan for whenever the next runtime is deprecated.
