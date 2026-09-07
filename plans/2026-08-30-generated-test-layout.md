---
status: idea
updated: 2026-08-30
---

# The tier split and the socket guard should be generated together

Filed from a `repo-tasks` session, 2026-08-30, where it had been sitting as
`plans/2026-08-27-generated-test-layout.md` since 2026-08-27. It was written there because that is
where the shipped half lives, but every question in it is about what **this** repo generates, so it
belongs here. Nothing was decided in the meantime; the content below is the 08-27 plan plus one
update noted inline.

## Context

`repo-tasks` ships both halves a two-tier test tree needs — `pytest-socket` and `pytest-cov` are in
the `repo-tasks-quality` manifest, so every consumer has them installed — but nothing generates the
tree that uses them. That repo's own `tests/unit/conftest.py` holds the autouse `no_network` fixture
and is explicitly "exemplary by being read, not distributed" (its `contributing/test-tiers.md`).
Generated projects are `scaffoldapy`'s half, and today it generates:

- `tests/conftest.py` and `tests/unit/test_<something>.py`, per interface,
- **no** `tests/integration/`,
- **no** socket guard,
- **no** question about the layout at all.

So a generated repo lands on a half-split shape: `tests/unit/` exists because the shipped
`pytest.ini` says `testpaths = tests/unit`, but the second tier the split exists _for_ is absent,
and the unit tier's central promise — "no Docker, no network, nothing outside tmp_path" — is
enforced only in the repo that wrote it down.

The user's framing, 2026-08-27: the split and the guard "would be nice to have together, and created
by default, but if the user prefers a simple `tests/` don't force the pytest socket restriction."

Two facts make that shape cheap to build:

- **The plugins are already everywhere.** Standardising them means a generated tree opts in with a
  fixture, never with a dependency edit.
- **A flat `tests/` is a supported layout**, as of `repo-tasks`' `14a91f3`. It was not, for a day:
  `filterwarnings = error` promoted the `testpaths` fallback's own notice to a hard exit-1 crash, so
  a repo with a plain `tests/` could not run `pytest` at all. That is fixed and covered by a real
  subprocess test, which is what makes "offer the flat layout as a genuine choice" an honest offer
  rather than a second-class path.

## Open questions

[NEEDS CLARIFICATION: whether the layout is a copier **question** or a consequence of an existing
one. A standalone `tests_layout: split | flat` is the obvious shape, but it may be derivable — a
`library` or `skill` interface with `fetch_strategy = none` has nothing to integration-test, while
`web_service` and any `fetch_strategy != none` project does. Deriving it means one fewer prompt;
asking means the generator does not quietly decide something the developer cares about.
`~/AGENTS.md`'s generator guidance — independent combinable axes over a top-level enum, and minimal
necessary prompts — cuts both ways here and does not settle it.]

[NEEDS CLARIFICATION: what a generated `tests/integration/` should actually contain. An empty
directory does not survive git. A placeholder test is the shape `test_politeness.py` and friends
already use, but an integration seed needs something real to integrate with, and the natural
candidate differs per interface (a `TestClient` round trip for `web_service`, a live fetch for
`fetch_strategy != none`, nothing obvious for `library`). The fallback is a `README.md` in the
directory explaining what the tier is for, which costs nothing and keeps the directory tracked.]

[NEEDS CLARIFICATION: whether the flat layout should get the socket guard as an **opt-in comment**
rather than nothing at all. The user's instruction is not to force it; a commented-out fixture with
one line saying what uncommenting buys is not forcing, and it puts the option in front of the person
who would want it. Against: a generated repo full of commented-out code is its own smell.]

[NEEDS CLARIFICATION: whether `test.untested-modules` and the `_integration` suffix need saying in
the generated `AGENTS.md`. Both are gate-visible rules a generated repo inherits without being told.
The third item this question used to carry — the basename-uniqueness rule — is answered, see below.]

**The wait on `repo-tasks` is over, 2026-09-04, and the answer is "packaged".** That repo took the
option its 2026-08-30 measurement had rejected on too narrow a framing: `tests/`, `tests/unit/` and
`tests/integration/` each carry an `__init__.py`, the shipped `pyrightconfig.json` carries
`extraPaths: ["."]`, and the shipped `ruff.toml` carries a `flake8-tidy-imports` `banned-api` entry
for `src` as the guard that pays for it. The deciding criterion was that packaging is pytest's own
documented shape for the `prepend` import mode this family uses, rather than a workaround.
`--import-mode=importlib` was ruled out: it removes the basename rule too, but pytest documents that
it makes utility modules under `tests/` not importable at all. The reasoning, the three-way
comparison and the community survey are in that repo's `contributing/type-checking.md`, "Why
`tests/` is a package"; the plan that decided it has since been retired, and
`plans.py archive --file 2026-08-30-tests-import-layout.md` reads it back.

Two consequences for this plan, both now decidable:

- **The generated `AGENTS.md` should not document a basename rule**, because the generated tree will
  not have one. What it documents instead is that `tests/` is a package and why — one line, pointing
  at the shipped config rather than restating it.
- **The generated tree needs the three `__init__.py` files**, in both the split and flat layouts, or
  it ships a tree the configs it also ships now assume. That is a change to the template, not just
  to its docs, and it wants covering in the e2e tier the same way direction 3 below asks.

Filed from a `repo-tasks` session; the work is this repo's.

## Recommended direction

Rough, and deliberately not settled — the questions above come first.

1. **Split by default, flat on request.** The split is the shape worth defaulting to: two tiers with
   different prerequisites is what the shipped `pytest.ini` and `test.integration` are built around,
   and a project that discovers it wants an integration tier later should find the seam already cut.
2. **The guard ships with the split, never with the config.** `tests/unit/conftest.py` gets the
   autouse `no_network` fixture (and, worth considering alongside, `isolated_home` — the same
   `Path.home()` trap `repo-tasks` hit costs a generated project the same stale files). The flat
   layout gets neither, and the shipped `pytest.ini` gains no `--disable-socket`: `addopts` reaches
   every consumer, and the guard is a promise the unit tier makes rather than one the shared config
   may impose on a layout that never made it.
3. **Cover it in the e2e tier.** `test_e2e.py` renders every combination and runs the generated
   repo's own gate — that is where "the generated split actually passes its own `quality.check`"
   gets proved, and where a flat-layout combination would prove the fallback works end to end rather
   than only in `repo-tasks`' subprocess test.

[DEFERRED: this supersedes a narrower item from `repo-tasks`' now-retired quality-gate sweep plan,
which assumed seeding the fixture would be what moved `pytest-socket` into the exported manifest.
The manifest move happened first and on its own merits, so what is left is only the generated tree.]
