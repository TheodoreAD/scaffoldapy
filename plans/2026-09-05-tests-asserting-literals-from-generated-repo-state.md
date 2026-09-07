---
status: landed
updated: 2026-09-08
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

## Answered 2026-09-08: nothing asserts one, in either tree

~~Does the template's own test tree, or any e2e-rendered combination, assert a literal from the
generated project's `pyproject.toml`?~~ **No.** Grepped both `tests/` and `template/tests/` for
`version`, a literal `0.1.0`, `requires-python` and `__version__`: four hits, all prose — three
docstrings and one comment, no assertion among them. The seeded tests are per-interface entry-point
checks (a `TestClient` round trip, a CLI invocation, an import smoke test) and assert nothing about
the project's own metadata. The one place this repo's suite reads a generated `pyproject.toml` at
all, `test_generates_valid_pyproject_and_config`, compares the project name against the answer set
that rendered it — derived from the render, not a literal, so it moves with the input rather than
with a release.

~~If the rule is worth stating for generated repos, where?~~ **Nowhere, and that is the finding
rather than a deferral.** The exposure needs a test that reads the repo's _own_ `pyproject.toml`,
which a generated repo acquires only when someone writes one. Stamping a `pinned_version` fixture
into every generated `tests/unit/conftest.py` would ship a fixture for a test nobody has written, in
a repo whose version has never moved — the speculative-need shape this plan's own direction warned
against. A sentence in the generated `AGENTS.md` was the cheap alternative and is rejected for a
related reason: that file is deliberately short, and spending a reader's attention on a trap no
generated repo is near is how it stops being read.

**What changes the answer**: a generated repo growing a test that asserts on its own metadata. The
rule to apply then is `repo-tasks`' — pin such a value in a fixture, never assert it literally —
already written down in that repo's `contributing/test-tiers.md` under "Unit tier: mocked `c.run`",
which is a better home than a copy of it here.
