---
status: planned
updated: 2026-09-27
source_repo: github.com-personal/repo-tasks
source_session: bcf810d6-38c7-48d3-adfe-2ff30399d4c9.jsonl
source_moment: 2026-09-27
source_plan: plans/2026-09-05-pyright-include-coverage.md (retired 2026-09-26, into contributing/file-discovery.md)
---

# Sweep to repo-tasks v0.5.0

## Context

`repo-tasks` `v0.5.0` was released 2026-09-27 and this machine's global tool is on it. Run the sweep
as `repo-tasks`' `contributing/consumer-sweep.md`, "The sweep", describes it. The two store plans
already filed here, `2026-09-08-sweep-to-repo-tasks-v0-3-0.md` and
`2026-09-26-re-stamp-the-bootstrap-at-the-end-of-the-sweep.md`, are earlier releases' and may fold
into this one.

What `v0.5.0` adds that this sweep uses:

- `inv deps.check-currency`, run after `inv deps.lock`: which `repo-tasks-quality` entries the lock
  holds behind their latest release. A plain lock keeps old pins, so take each with
  `inv deps.lock --package <name>`.
- `inv configs.check-include` plus `repo-tasks.toml`'s `[pyright] extra-include` and
  `[pyright] unchecked`. This repo is the case that motivated them.
- Also new: `inv dist.check-isolated`, the pin-comment check in `inv ci.check-actions`,
  `inv repo-tasks.status --latest`, `docker.logout`/`helm.logout`, `venv.sync --extra/--group`.

## Evidence

Measured 2026-09-27 from `repo-tasks`' session, read-only in this tree (`git status` clean after),
with the installed `v0.5.0` tool.

**`inv configs.check-include`: `template/` holds 2 tracked `.py` files, never checked** —
`template/tasks.py` and `template/tests/conftest.py`, literal Python rather than Jinja. Proved on a
clone of `main` on 2026-09-26: a `repo-tasks.toml` holding

```toml
[pyright]
extra-include = ["template*"]
```

then `inv configs.pull` changed exactly the `include` line, `configs.check-include` went clean, and
`basedpyright` over the whole tree against this repo's own `.venv` reported 0 errors, 0 warnings.
This repo has no `repo-tasks.toml` today, so the file is new.

**`inv deps.check-currency`: 6 of 14 manifest entries behind.** `basedpyright` 1.39.10 (latest
1.40.1), `ruff` 0.16.3 (0.16.9), `shfmt-py` 4.0.0 (4.2.0), `dprint-py` 0.56.1.0 (0.57.4.0),
`actionlint-py` 1.7.12.24 (1.7.12.25), `zizmor` 1.29.0 (1.30.1). `invoke-stubs` is current.

## Open questions

[NEEDS CLARIFICATION: should the generated project's own `repo-tasks.toml` template carry anything
here? A generated repo gets the shipped `include` and no `template/`, so probably not, but the e2e
tier is what would show it.]

## Recommended direction

Run the sweep as documented. Add `repo-tasks.toml` with `extra-include = ["template*"]` and pull,
which puts `template/` under the gate for the first time. Take the six lags with
`inv deps.lock --package <name>`. Run the e2e tier (`inv test.integration`) since this repo's output
has its own gate, then stamp last.
