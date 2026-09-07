---
status: idea
updated: 2026-09-05
source_repo: github.com-personal/repo-tasks
source_session: bb66cbe5-7369-4f49-a8e7-7949db5ff99a.jsonl
source_moment: 2026-09-04T21:47:43Z
---

# Does a generated repo's test suite assert literals derived from its own mutable state?

## Context

`repo-tasks` hit this once and settled it 2026-09-05 as a convention rather than a mechanism, in
`contributing/test-tiers.md`, "Unit tier: mocked `c.run`": 11 unit tests asserted version strings
derived from the repo's real `pyproject.toml` and went red the moment the first real release moved
the version. The fix there is an autouse `pinned_version` fixture in `tests/unit/conftest.py`, and
the rule is that a value read from the repo's own `pyproject.toml` is pinned by a fixture, never
asserted literally.

A generated repo inherits the convention but not that conftest, and its own version moves on the
same release path, so the same exposure exists in principle. Whether it exists in practice, and
whether the generated `AGENTS.md` or `tests/README.md` should state the rule, is this repo's
question. `repo-tasks` deliberately did not decide it: writing into a generated repo's instructions
is `scaffoldapy`'s half of the split.

## Evidence

- The one observed instance and its fix are in `repo-tasks`' `contributing/test-tiers.md`, under the
  pitfall beginning "the same blind spot hides a test's own dependence on mutable repo state".
- Filed from the `repo-tasks` session named in the frontmatter, while retiring that repo's
  `plans/2026-09-04-tests-asserting-mutable-repo-state.md`. The distinctive phrase to search that
  transcript for is the user answering "1, then 3, then 2." when asked which plan to take next.

## Open questions

[NEEDS CLARIFICATION: does the template's own test tree, or any e2e-rendered combination, assert a
literal that comes from the generated project's `pyproject.toml` — version, name, `requires-python`,
dependency groups? One grep of the template's tests for values that also appear in the rendered
`pyproject.toml` answers it. If nothing does, the exposure is hypothetical here too and the honest
answer is a sentence in the generated `tests/README.md`, or nothing.]

[NEEDS CLARIFICATION: if the rule is worth stating for generated repos, where — the generated
`AGENTS.md`, the generated `tests/README.md`, or a stamped `pinned_version`-style fixture in the
generated `tests/unit/conftest.py`? A stamped fixture is the only one of the three that enforces
anything, and also the only one that ships code every generated repo carries whether or not it needs
it.]

## Recommended direction

Grep first. If no generated test asserts such a literal, state the rule in one sentence where the
generated test conventions already live and stop; a stamped fixture is the speculative-need shape
unless a generated repo has actually been bitten.
