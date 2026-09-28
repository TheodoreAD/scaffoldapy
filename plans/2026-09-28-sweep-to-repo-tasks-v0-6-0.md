---
status: idea
updated: 2026-09-28
source_repo: github.com-personal/repo-tasks
source_session: 44be2918-1669-4d16-9f77-56535cc6ddeb.jsonl
source_moment: 2026-09-28T11:15:00Z
source_plan:
---

# Sweep to repo-tasks v0.6.0

## Context

repo-tasks v0.6.0 was released 2026-09-28 (tag on `a2d9cf5`, CI/Security/Canary green; Canary runs
this repo's e2e tier against it). This machine's global tool is already at v0.6.0. What it carries
for a consumer:

- **Shipped configs:** `pyrightconfig.json` drops `allowedUntypedLibraries: ["invoke"]`, redundant
  since invoke-stubs 0.2.0. `zizmor.yml` disables zizmor 1.30's `self-repository` audit, because
  actionlint and act both reject its `uses: $/` fix.
- **`deps.check-currency`:** an excluded latest release reads as excluded, not BEHIND.
- **Colour:** uv and gh output is forced plain wherever repo-tasks parses it.
- **gitflow PR mode:** finished branches are deleted, and a stale base is refused. That matters only
  to a repo using `gitflow.*`.

The sequence is repo-tasks' `contributing/consumer-sweep.md`, "The sweep".

## This repo's drift

`inv consumers.diff` from repo-tasks, 2026-09-28: **config files behind: `pyrightconfig.json`,
`zizmor.yml`.** Nothing else was flagged.

**The template matters more than this repo's own copies.** Every generated project starts from
whatever `template/` ships. Check whether the template carries its own copy of either config, or
pulls them at generation time. If it carries a copy, update it in the same pass. The already-filed
`2026-09-28-template-ci-records-the-ubuntu-26-04-measurement.md` touches the template's `ci.yml` and
fits the same sweep.

## Recommended direction

Run the sweep per the doc, and look at `template/` in the same pass. Canary on repo-tasks already
showed v0.6.0 green against this repo's e2e tier, so a red gate here after `configs.pull` would be a
this-repo difference worth reading, not an expected break.
