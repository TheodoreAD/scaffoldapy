---
status: idea
updated: 2026-08-24
depends_on: [repo-tasks]
---

# Adopt `repo-tasks`' unit/integration test structure

## Context

`repo-tasks` landed a two-tier test layout on 2026-08-24 and ships the config half of it to every
consumer: `tests/unit/` and `tests/integration/`, `pytest.ini`'s `testpaths = tests/unit`, a
registered `smoke` marker, and a `test` namespace (`inv test.unit` / `test.integration` /
`test.smoke` / `test.regression` / `test.all`) replacing `quality.test`. Only the unit tier runs in
`quality.check`/`precommit`. Rationale and measurements: `repo-tasks/contributing/test-tiers.md`.

This repo has `tests/conftest.py`, `tests/test_template.py`, `tests/test_repo_sync.py`, and
`testpaths = tests`.

The next `inv configs.pull` here overwrites `pytest.ini` with the shipped one, whose `testpaths`
names `tests/unit`. That is not an error — pytest warns and falls back to searching recursively from
the working directory — but the fallback is broader than `tests/` and pytest does not respect
`.gitignore`.

**This repo has a stronger case for the split than its sibling.** `test_template.py` renders real
`copier` templates, which is exactly the slow, prerequisite-carrying shape the integration tier
exists for, while `test_repo_sync.py` looks like ordinary unit work. A split here would separate
things that genuinely differ, rather than being adopted for conformity.

## Open questions

[NEEDS CLARIFICATION: does `test_template.py` belong in the integration tier? It renders with
`copier` — a real dependency doing real filesystem work — but needs no Docker, no network and no
service, which is what the tier's prerequisites are actually about. If it stays in the unit tier,
this repo's split is cosmetic and the simpler `tests/unit/`-only shape applies; if it moves, this
repo gets the first genuine two-tier layout outside `repo-tasks` and the shared `testpaths` fits
without further thought.]

[NEEDS CLARIFICATION: the existing `tests/conftest.py` — does its content belong at `tests/` (shared
by both tiers) or in `tests/unit/`? `repo-tasks` uses three conftests deliberately: shared at
`tests/`, tier-specific below, so a unit test cannot reach an integration fixture by accident. Needs
a read of what is actually in this one.]

[NEEDS CLARIFICATION: does this repo want the `smoke`/`regression` marker split at all? It ships to
every generated project through the shared `pytest.ini` whether this repo uses it or not, so the
question is only whether anything here gets marked — not whether the marker exists.]

## Recommended direction

Read `tests/conftest.py` and `test_template.py` first; both open questions turn on what is actually
in them. If `test_template.py` is genuinely the slow half, take the full split — this repo is the
better pilot for it than `power-user-linux-setup`, whose tier would be empty.

Worth doing alongside the sibling plan
(`power-user-linux-setup/plans/2026-08-24-adopt-test-tier-structure.md`) rather than separately: the
two repos should not diverge on this, and the decision here informs that one.

[NEEDS CLARIFICATION: this repo also generates _other_ repos. Does the template's own scaffolded
`tests/` directory adopt the tier layout too, so a freshly generated project starts with
`tests/unit/` and matches the shared `pytest.ini` from its first commit? That is arguably more
important than what this repo does with its own tests, and is not covered by either sibling plan.]
