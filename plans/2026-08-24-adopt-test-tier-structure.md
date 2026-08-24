---
status: in-progress
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

This repo has a stronger case for the split than its sibling: `test_template.py` renders real
`copier` templates, which is exactly the slow, prerequisite-carrying shape the integration tier
exists for, while `test_repo_sync.py` is ordinary unit work.

### What the suite actually costs

Measured 2026-08-24, warm caches, 37 tests, `pytest --durations=25`: **55.9s total**, of which the
10 `test_generated_repo_passes_quality_check_out_of_the_box` parametrizations are ~49.8s (2.9s–7.4s
each). Everything else totals ~6s; the next slowest single test is `test_copier_update_round_trip`
at 1.0s.

The fast/slow split is therefore not file-level but test-level inside `test_template.py`: one test
function (ten parametrizations) is 89% of the runtime, and it is the only one needing network, `uv`,
and the global `repo-tasks` install.

### The dependency has not shipped to this machine yet

[PITFALL: the globally installed `repo-tasks` is still pre-tier — it publishes `quality.test` /
`quality.test-integration`, not the `test` namespace, and its canonical `pytest.ini` still says
`testpaths = tests`. `inv configs.diff` here reports "up to date" for exactly that reason. The tier
work exists only in the `repo-tasks` working tree; verified 2026-08-24 that the repo has no `v*`
tags at all and that local `main` sat 2 commits ahead of `origin/main`.]

Consequences for sequencing:

- `inv test.unit` does not exist on this machine yet, so nothing here can call it.
- `inv configs.pull` today would pull the **old** `pytest.ini`, not the tiered one.
- Splitting this repo's own tests right now would change nothing behaviourally: `testpaths = tests`
  still collects both tier directories, so the 50s e2e would stay in `quality.check` regardless.

The template half is not blocked, and is compatible both ways: `testpaths = tests` collects
`tests/unit/` recursively, and the tiered `testpaths = tests/unit` names it directly. It therefore
lands first, on its own.

## Design

### 1. `template/tests/` → `template/tests/unit/` (unblocked; lands first)

Every seeded test file moves down one level, keeping its Jinja-conditional filename verbatim.
`template/tests/conftest.py` stays at the shared level, matching `repo-tasks`' three-conftest shape,
so a generated repo's first integration test can reach it.

[DECISION: no `tests/integration/` is seeded. `test.integration` no-ops cleanly when the directory
is absent, and an empty tier holding nothing but a conftest is noise in a fresh repo.]

A generated repo then matches the shipped `pytest.ini` from its first commit instead of tripping
pytest's "No files were found in testpaths ... Searching recursively from the current directory
instead" fallback, and has the family layout in place before its first test is written.

### 2. `tests/combinations.py` — the shared fixture module, renamed off `conftest`

[DECISION: the shared non-fixture content must not live in `conftest.py`. Verified live 2026-08-24
in a scratch repo: with a `tests/conftest.py` **and** a `tests/integration/conftest.py` present,
`from conftest import X` resolves differently per tier — it finds `tests/conftest.py` from
`tests/unit/test_*.py` (works) but the tier-local `tests/integration/conftest.py` from
`tests/integration/test_*.py` (`ImportError: cannot import name X from 'conftest'`). The failure is
silent and direction-dependent, which is worse than a plain break. A distinctly-named
`tests/combinations.py` imports identically from both tiers — verified in the same scratch repo.
`pytest.ini`'s `pythonpath` is not an alternative: it is a pulled canonical config and cannot be
hand-edited here.]

Moves into `tests/combinations.py`: `TEMPLATE_DIR`, `BASE_ANSWERS`, `COMBINATIONS`,
`package_name_of`. These are module-level constants feeding `@pytest.mark.parametrize`, so they
cannot be fixtures.

### 3. `tests/unit/` + `tests/integration/`

- `tests/conftest.py` — the `render` fixture and the `Render` protocol. Both tiers need it.

  [DECISION: `render`'s `run_tasks=True` branch stays in the shared fixture rather than being split
  out. It defaults to `False`, its docstring already states the cost, and splitting the factory in
  two to enforce what the default already encourages is not worth the indirection.]

- `tests/unit/` — `test_repo_sync.py` and `test_template.py` minus the e2e (~27 tests, ~6s).
- `tests/integration/conftest.py` — `run_in_generated_repo`, and nothing else. This is the one
  helper a unit test must not reach by accident: it shells out into a generated repo.
- `tests/integration/test_e2e.py` — `test_generated_repo_passes_quality_check_out_of_the_box`, its
  ten parametrizations, and its full existing docstring.

[DECISION: no `smoke`/`regression` marking. The integration tier is ten parametrizations of a single
test function, so there is no fast-happy-path slice to separate from a slow remainder. The marker
ships in the pulled `pytest.ini` either way; nothing here gets marked.]

### 4. `ci.yml` gains `- run: inv test.integration`

[DECISION: the e2e moves to the integration tier and CI keeps running it, rather than either (a)
leaving a 50s network-dependent test inside a tier whose contract reads "no network, nothing outside
tmp_path", or (b) following `repo-tasks`' own precedent of an opt-in tier absent from CI. Option (b)
was rejected because this repo's integration prerequisites — network, `uv`, the global `repo-tasks`
install — are all things its CI already provides, unlike `repo-tasks`' Docker daemon, and because
the e2e is the only test that catches template _content_ bugs. Chosen 2026-08-24.]

The step is added to **both** copies of `ci.yml`, keeping them byte-identical so
`test_repo_sync.py`'s guard needs no change. It is meaningful here and a clean no-op in a generated
repo (`test.integration` prints "no tests/integration directory — nothing to do" and returns).

The residual cost is that local `inv quality.precommit` stops covering template content bugs.
Mitigated in `AGENTS.md`, not by a hook: a `template/` change is verified with `inv test.all`.

### 5. `inv configs.pull` for the tiered `pytest.ini`

Its own standalone commit, per the regeneration rule in `~/AGENTS.md` — never folded into the split
commit, and never rerun as a side effect of routine work.

## Files touched

Step 1 (now):

- `template/tests/**` → `template/tests/unit/**` (git mv; `conftest.py` stays put)
- `tests/test_template.py` — `test_library_seeds_a_smoke_test`'s asserted path
- `template/AGENTS.md`, `template/README.md.jinja` — the "tests live in `tests/`" lines

Step 2 (after `repo-tasks` ships and `inv repo-tasks.update` lands it here):

- `pytest.ini` — via `inv configs.pull`, standalone commit
- `tests/combinations.py` (new), `tests/conftest.py`, `tests/unit/**`, `tests/integration/**`
- `.github/workflows/ci.yml` and `template/.github/workflows/ci.yml` — identical new step
- `AGENTS.md` — the `inv test.all` rule for `template/` changes, and the tier layout

## Verification

- Step 1: the existing suite, unchanged. `test_library_seeds_a_smoke_test` pins the new seeded path,
  and all ten e2e parametrizations render and run a generated repo's real `inv quality.check`, so a
  layout that breaks collection inside a generated repo fails loudly.
- Step 2: `inv test.unit` collects 27 tests and no e2e; `inv test.integration` collects exactly the
  ten; `inv test.all` totals 37, matching today's count. `pytest tests/integration` must pass **on
  its own** — that is the invocation that exposes the `conftest` name collision in §2.
- `inv quality.precommit` before each commit.

## Open questions

None.
