---
status: idea
updated: 2026-08-31
---

# Generated repos should call the family's security workflow

## Context

Filed from `repo-tasks` on 2026-08-31, the day the dependency audit landed there as its own GitHub
Actions workflow. Nothing in this repo was touched.

`repo-tasks` now hosts a **reusable** workflow, `.github/workflows/security-reusable.yml`, which
runs `uv audit --locked` and nothing else. Each repo in the family is meant to carry a small caller
that invokes it, so the audit has exactly one definition and no per-repo drift — the drift being the
whole reason it was built that way. `repo-tasks` itself is done; every other repo needs its caller,
and this repo is the highest-leverage of them because its template hands the file to every project
generated from here on.

Verified working, `repo-tasks` commit `9933e2a`, run `33339113208`: `CI` and `Security` report as
two independent runs against the same commit, the reusable call resolves as `audit / audit`, and the
whole job takes 9s.

## What a caller looks like

`.github/workflows/security.yml`, and this is essentially the whole file:

```yaml
name: Security

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  audit:
    uses: TheodoreAD/repo-tasks/.github/workflows/security-reusable.yml@d17c60715e2a7fd63cf22874255c6923277b7859 # 2026-08-31
```

`repo-tasks` itself uses the local `./.github/workflows/security-reusable.yml` form because it hosts
the file; every other repo uses the `TheodoreAD/…@main` form above.

## Why it is shaped this way

The reasoning lives in `repo-tasks`' `contributing/quality-gate.md`, section "The dependency audit
runs as its own workflow", and in its `plans/2026-08-30-deps-audit-in-ci.md`. The three points that
matter for a caller in this repo:

- **The job installs nothing.** `uv audit --locked` reads `uv.lock` and queries OSV; it needs no
  venv, so there is no `bootstrap.sh` step, nothing to cache, and nothing about a generated repo's
  interface or dependency set that changes the caller. The same six lines work for `cli`,
  `web_service`, `mcp_server`, `skill` and `library` alike.
- **A separate workflow is the point.** GitHub gives every workflow its own check run, name and
  badge, so a green `CI` beside a red `Security` reads as "the code is fine, the dependencies are
  not". Folding the audit into the generated `ci.yml` would lose that and put a network call inside
  the workflow whose whole point is running offline.
- **A pinned SHA, not `@main`** — the user's call 2026-09-04, on stability. A moving ref would
  change a generated repo's audit the moment `repo-tasks`' `main` moved, in repos nobody is
  touching. The SHA above is the commit that introduced the reusable workflow; bump it when that
  file changes, which so far it has not. `ci.check-actions` parses this shape already — job-level
  `uses:`, 40-hex SHA, trailing comment as the readable version — so a template that emits it stays
  legible to the tooling.

[PITFALL: the pin is not yet watched by anything. `ci.check-actions` resolves currency through
`gh api repos/<owner>/<repo>/releases/latest`, and `repo-tasks` publishes no releases and carries no
tags, so its own reusable workflow is skipped as "nobody's release to track". A generated repo will
therefore sit on whatever SHA the template baked in until someone looks. If this repo is going to
emit the pin into every future project, that is worth knowing before the first dozen exist.]

[PITFALL: the reusable workflow is hosted in `repo-tasks` specifically **because that repo is
public**. On Free, Pro and Team plans a reusable workflow must live in the same repository or a
public one — so a public host is callable from a private generated repo, while hosting it in a
private repo would need Enterprise. A generated repo is frequently private, so this is the property
that makes the caller work at all, and it is not obvious from looking at either file.]

## Open questions

[NEEDS CLARIFICATION: does the caller go in unconditionally, or behind a copier question? The
template's `.github/workflows/` already conditions `docs.yml` on `with_docs`, so there is precedent
for optional workflows. Against a question: the audit is not a feature, it costs nothing, and every
generated repo has a `uv.lock` — an option here would mostly produce repos differing for no reason,
which is the exact problem this design removes. Probably unconditional, but this repo's own
convention on when a file earns a question should decide it.]

[NEEDS CLARIFICATION: does `COMBINATIONS` need to grow for this? The end-to-end test renders each
combination and runs its quality gate; a new always-present workflow file would be covered by the
existing combinations rather than needing new ones, but the generated workflow set is exactly the
kind of thing `test_template.py` asserts on, so an assertion probably wants adding rather than a
combination.]

[NEEDS CLARIFICATION: should the generated repo's `AGENTS.md` mention it? A generated repo's own
agent instructions describe how to develop and test it. "A red `Security` check means a dependency
advisory, not broken code, and there is no suppression list" is arguably a thing a future agent in
that repo needs told, since the natural reaction to a red check is to look for a code defect.]

## Recommended direction

Add the caller unconditionally to `template/.github/workflows/security.yml`, with an assertion in
`test_template.py` that it lands, and leave the copier question alone unless this repo's convention
says otherwise. It is six lines that never vary by interface.

Note this only covers **future** generated repos. The seven existing repos in the family
(`power-user-linux-setup`, `agent-skills`, `invoke-stubs`, `ingesta`, and the `*-polite-mcp` ones)
each still need the same file added by hand, which is tracked as a `DEFERRED` in `repo-tasks`'
`plans/2026-08-30-deps-audit-in-ci.md` rather than here.
