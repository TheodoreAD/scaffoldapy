---
status: landed
updated: 2026-09-08
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
the file; every other repo uses the `TheodoreAD/…@<sha>` form above. That repo's own `security.yml`
comment still describes the other repos as calling it `@main` — written before the pinning call of
2026-09-04, and not what this template emits.

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

## Questions, as answered

~~Unconditional, or behind a copier question?~~ **Unconditional.** The precedent that looked
relevant — `docs.yml` conditioned on `with_docs` — cuts the other way once stated: a docs site is a
feature a project either wants or does not, while the audit is a check that costs nothing and every
generated repo has a `uv.lock` for. A question here would produce repos differing for no reason,
which is the drift the single shared definition exists to remove.

~~Does `COMBINATIONS` need to grow?~~ **No, an assertion instead**, exactly as the question guessed.
The file never varies by interface, so a new combination would render the same six lines a tenth
time. Two assertions went into `test_template.py`: the file lands in every combination, and its
`uses:` is a 40-hex SHA with a trailing date comment. The second is the one worth having — it
asserts the pin's _shape_ rather than a commit, so bumping the pin is free and replacing it with
`@main` is caught.

~~Should the generated `AGENTS.md` mention it?~~ **Yes**, and it says the thing the question named:
a red `Security` is an advisory against `uv.lock`, not a defect in the code, the fix is a version
bump, and there is no suppression list. The push trigger is stated with it, because an advisory
landing in a quiet week is invisible until the next push and that is the property that makes the
check's silence weaker than it looks.

## Landed 2026-09-08

`template/.github/workflows/security.yml`, and this repo's own byte-identical copy alongside it —
added to `test_repo_sync.py`'s `IDENTICAL_FILES` on the same argument as `ci.yml`: this repo should
run what it ships. It is the family's **first** caller; `repo-tasks` hosts the reusable workflow and
calls its own copy by path, and no other repo had one yet, so the pin form was this repo's to set.

Pinned to `d17c607`, re-resolved against the remote rather than copied from this plan, and confirmed
to be the only commit that has ever touched `security-reusable.yml` — so the pin is both current and
the file's whole history. It was born after the family's action bump, so the pinned copy already
runs `checkout@v7` and `setup-uv@v10.0.1`: pinning does not reintroduce the Node 20 deprecation that
the same session removed from this repo's own workflows.

Verified through the e2e tier: every rendered repo creates the file, and each one's own
`inv quality.check` — actionlint and zizmor included — passes on it.

## Recommended direction

Add the caller unconditionally to `template/.github/workflows/security.yml`, with an assertion in
`test_template.py` that it lands, and leave the copier question alone unless this repo's convention
says otherwise. It is six lines that never vary by interface.

Note this only covers **future** generated repos. The seven existing repos in the family
(`power-user-linux-setup`, `agent-skills`, `invoke-stubs`, `ingesta`, and the `*-polite-mcp` ones)
each still need the same file added by hand, which is tracked as a `DEFERRED` in `repo-tasks`'
`plans/2026-08-30-deps-audit-in-ci.md` rather than here.

## Migrated to

- [`contributing/generated-workflows.md`](../contributing/generated-workflows.md) — why the audit is
  a separate workflow, why it is called rather than copied, the public-host requirement that makes
  it work from a private repo, the SHA-pin decision, and the pitfall that nothing watches that pin
  because the host publishes no releases.
- `template/.github/workflows/security.yml` itself, which carries the short version in comments, and
  the generated `AGENTS.md`, which tells that repo how to read a red check.

Deliberately not migrated: the verification of the reusable workflow in its own repo (commit and run
ids), which belongs to that repo, and the note that the other family repos still need a caller by
hand — tracked as a DEFERRED in `repo-tasks`' `plans/2026-08-30-deps-audit-in-ci.md`, which is where
the sweep is owned.
