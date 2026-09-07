# This repo's own test suite: the decisions behind its shape

`AGENTS.md` says how to run the tiers and what each one costs. This file says why the tree is
arranged the way it is, and what was rejected — the parts that are expensive to re-derive and
invisible from the code.

## `tests/` is a package, and `support.py` is imported by name

`tests/`, `tests/unit/` and `tests/integration/` each carry an `__init__.py`, and the three import
sites say `from tests.support import ...`. Two independent reasons, and neither is style.

**A bare `from support import ...` resolves by shadowing, not by namespacing.** pytest's default
`prepend` import mode puts `tests/` at the front of `sys.path` for the session, so a top-level
module named `support` — close to the most collidable name available — wins over anything else by
that name for every import underneath it. It worked and there was never a collision; the failure
mode if there had been one is an import quietly resolving to the wrong module rather than an error.
That matters more here than in most repos, because `tests/support.py` holds `COMBINATIONS`, the
single parametrization source for the whole suite including the real end-to-end gate. A wrong
resolution would not fail — it would run a smaller matrix, silently.

**The contents cannot move into a `conftest.py`.** `from conftest import X` is ambiguous here in two
separate ways, both confirmed live: a tier-local `tests/integration/conftest.py` shadows
`tests/conftest.py` for that tier only, surfacing as a silent direction-dependent `ImportError`; and
this repo has a **second** `tests/conftest.py`, under `template/`, which wins outright whenever
pytest falls back to searching from the working directory — exactly what the shipped
`testpaths = tests/unit` triggers in a repo that has not split its tests yet. A distinct module name
has neither problem, so whatever happens to the import mechanism, the contents stay in a module of
their own.

Packaging is pytest's own documented recommendation for `prepend` mode, and it is a family-wide
decision rather than a local one: the shipped `pyrightconfig.json` carries `extraPaths: ["."]` so
basedpyright resolves `tests.support`, and the shipped `ruff.toml` carries a `flake8-tidy-imports`
`banned-api` entry for `src` to close the second import route `extraPaths` opens. Both arrive
through `configs.pull`, so none of it is per-repo drift. The reasoning for the family-wide half, and
why `--import-mode=importlib` was ruled out, is in `repo-tasks`' `contributing/type-checking.md`
under "Why `tests/` is a package".

**Rejected: renaming `support.py` to something uncollidable.** It was the cheap mitigation while the
family question was open — one `git mv` and three import lines, most of the safety, neither adopting
nor foreclosing packaging. Dropped rather than deferred once the family settled, because doing both
would rename the module twice, and because a name chosen to be unlikely is not the same as a
mechanism that cannot collide.

**Rejected: moving the helpers into session-scoped fixtures**, the shape the one other repo in the
family with a shared test world uses. It is the `conftest` route above under another name, and it
runs into both shadowing mechanisms.

The survey behind that comparison, from 2026-08-30: nine personal repos have tests, two express a
shared test world, seven have no helper module at all. The need is real and recurring but a minority
shape — which is why the answer stayed per-repo for a while before the family-wide config change
made packaging free.

## What the template's own tests do not do

The generated `tests/` tree is a **different question** from this one, owned by its own plan. Two
things follow that are easy to get wrong when working on both trees in one session:

- Do not add `__init__.py` under `template/tests/` as part of a change to this repo's suite. Two
  trees, two decisions; conflating them is how the template acquires a file nobody chose.
- The generated `AGENTS.md` should not document a globally-unique-test-basename rule. That
  requirement is a property of the unpackaged layout, and the family has taken packaging — so what a
  generated repo eventually needs told is that `tests/` is a package and why, not a rule it does not
  have.

## No speculative fixtures in what we generate

`repo-tasks` was bitten by unit tests asserting version strings read from the repo's own
`pyproject.toml`: the first real release moved the version and eleven tests went red at once. Its
answer is an autouse `pinned_version` fixture and a convention — a value read from the repo's own
metadata is pinned by a fixture, never asserted literally.

A generated repo inherits the convention but not the fixture, so the question was whether to stamp
one in. Checked 2026-09-08: **no test in either tree asserts such a literal.** The seeded tests are
per-interface entry-point checks — a `TestClient` round trip, a CLI invocation, an import smoke test
— and assert nothing about the project's own metadata; the one place this repo's suite reads a
generated `pyproject.toml` compares the project name against the answer set that rendered it, which
is derived from the render rather than a literal.

So nothing is stamped. A fixture for a test nobody has written, in a repo whose version has never
moved, is a speculative need — and the cheap alternative, a sentence in the generated `AGENTS.md`,
was rejected for a related reason: that file is deliberately short, and spending a reader's
attention on a trap no generated repo is near is how it stops being read. What changes the answer is
a generated repo growing a test that asserts on its own metadata; the rule to apply then is already
written down in `repo-tasks`' `contributing/test-tiers.md`.

## The end-to-end tier is the only thing that tests template content

Everything else here renders with copier's `_tasks` skipped, so it checks the file tree and nothing
about whether the result works. `tests/integration/test_e2e.py` renders every `COMBINATIONS` entry
for real and asserts the generated repo's own `inv quality.check` exits 0 — which is why `AGENTS.md`
carries the standing rule that a combination is never excluded to make it pass, and why a
`template/` change needs `inv test.all` rather than `precommit`.

It is also where an import that moved gets caught: it is the one test whose collection spans all
three tiers of this repo's tree.
