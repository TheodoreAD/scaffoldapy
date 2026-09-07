# Agent instructions

Cross-tool instructions for AI coding agents working in this repo. Universal conventions (sudo/ssh
askpass, Bash/allowlist discipline, cross-session memory policy) live in `~/AGENTS.md` — no need to
repeat them here, only what's specific to this repo.

## Build & test

- Needs the shared `repo-tasks` uv tool on `PATH` — `power-user-linux-setup`'s `bootstrap.sh`
  installs it, and `./bootstrap-repo-tasks.sh` here does the same thing (it's what CI runs). Neither
  `repo-tasks` nor `invoke` is a dependency of this repo, same as every repo it generates.
- `inv dev-env.setup` once after cloning, then plain `pytest`/`inv` — no `uv run` prefix.
- `inv quality.precommit` before considering a change done.
- **Anything under `template/` also needs `inv test.all`.** `precommit` runs the unit tier only
  (~6s); the e2e that catches template _content_ bugs lives in the integration tier (~50s) and does
  not run there. CI runs both, but finding it locally is the point.
- The e2e verdict is only as current as the **global** `repo-tasks` install it renders with, not the
  `repo-tasks` checkout next door. A template change that leans on a `repo-tasks` fix (the
  empty-`dev`-group shape did, 2026-08-25) needs that fix pushed to `repo-tasks` `main` and then
  `inv repo-tasks.update` here first — otherwise `inv test.all` fails against the stale tool and
  looks like a template bug. `./bootstrap-repo-tasks.sh` is unpinned until `repo-tasks` tags a
  release, so CI installs `main` and never has this lag.
- Don't reach for a throwaway render script to check template output: `tests/conftest.py`'s `render`
  fixture sandboxes any combination into `tmp_path` in one call, and the suite already renders every
  `COMBINATIONS` entry.

### Test tiers

Following `repo-tasks/contributing/test-tiers.md`, which is also where the shipped
`testpaths = tests/unit` comes from:

- `tests/unit/` — `inv test.unit`, and the only tier in `quality.check`/`precommit`. Renders with
  copier.yml's `_tasks` skipped, so it needs nothing beyond the dev dependency group.
- `tests/integration/` — `inv test.integration`. One module, `test_e2e.py`, rendering every
  `COMBINATIONS` entry for real: network, `uv`, and the global `repo-tasks` install. `ci.yml` runs
  it on every push, so it is not opt-in the way `repo-tasks`' own Docker tier is. Its own
  `conftest.py` holds the autouse `isolated_home` fixture: a real render's `inv configure` writes
  user-wide state (`direnv allow`, `~/.cache/claude-code`), and this fixture is what keeps that
  inside `tmp_path` — patching both `os.environ` and plumbum's `local.env`, because copier runs
  `_tasks` from the latter, a snapshot taken at import that `monkeypatch.setenv` never reaches.
- `tests/support.py` — `COMBINATIONS` and friends, imported by both tiers as `tests.support`.
  Deliberately **not** `conftest.py`: `from conftest import ...` resolves to a different file per
  tier once a tier-local conftest exists, and `template/tests/conftest.py` shadows the real one
  outright whenever pytest falls back to searching from the working directory. Both confirmed live,
  both silent.
- `tests/` is a **package** — an `__init__.py` in it and in each tier — so that import resolves by
  namespace rather than by `sys.path` position. Do not add one under `template/tests/`: what the
  template generates is a separate decision.

Why the tree is shaped this way, and what was rejected, is in
[`contributing/test-suite.md`](contributing/test-suite.md).

## Two file trees, and only one of them is the template

`template/` is what gets copied into a generated repo (`_subdirectory: template` in `copier.yml`).
Everything at this repo's root — `pyproject.toml`, `tasks.py`, `ruff.toml`, `tests/` — is
`scaffoldapy`'s _own_ dev tooling and is never copied anywhere. Editing the root copy when the
template copy was meant is the easiest mistake to make here.

Some files deliberately exist in both places. `LICENSE`, `.envrc`, `tasks.py`,
`.github/workflows/ci.yml` and `.github/workflows/security.yml` are byte-identical, and
`tests/unit/test_repo_sync.py` fails if they ever stop being — hand-syncing is not a plan on its
own, which is how `ci.yml` sat on the pre-`repo-tasks` CI recipe at the root while the template's
copy had moved on. `.gitignore` is the deliberate exception: the template's copy is a superset (a
generated repo can have `site/` and `.cache/`; this one can't), so the guard checks containment
rather than equality.

Others deliberately exist only at the root and must **not** be added to `template/` — `ruff.toml`,
`pyrightconfig.json`, `dprint.json`, `pytest.ini`, `.editorconfig` are pulled from `repo-tasks`'
canonical copies by `copier.yml`'s `_tasks` at generation time instead, and
`tests/unit/test_template.py` asserts they're absent from a freshly rendered repo.

Interface-conditional template files encode the condition in the _filename_, e.g.
`template/tests/unit/{% if interface == "cli" %}test_cli.py{% endif %}.jinja` — an empty rendered
name means copier drops the file entirely. A conditional **workflow** file pays for that with a
blind spot: `inv ci.check-actions --path template/.github/workflows` reads only names ending `.yml`,
so the docs workflow's action pins have to be checked by hand. See
[`contributing/generated-workflows.md`](contributing/generated-workflows.md), which also carries why
the security audit is a pinned call rather than a copy.

A generated repo's seeded tests live under `template/tests/unit/` — the tier that `repo-tasks`'
canonical `pytest.ini` names in `testpaths`, so a fresh repo matches it from its first commit
instead of relying on pytest's search-from-cwd fallback. `template/tests/conftest.py` stays at the
shared level, above the tier, so a repo that later adds `tests/integration/` can reach it.

## Never exclude a combination from the e2e test to make it pass

`tests/integration/test_e2e.py`'s `test_generated_repo_passes_quality_check_out_of_the_box` renders
for real (`_tasks` included: network, `uv`) and asserts a generated repo's own `inv quality.check`
exits 0. It is the only test that catches template _content_ bugs — bad Jinja whitespace,
unformatted output, broken generated code — and it only catches them for combinations it actually
runs. It is also the reason a `template/` change needs `inv test.all`, not just `precommit`.

Every entry in `COMBINATIONS` stays parametrized into it. If one fails, the template is wrong: fix
the template. Confirmed twice: the `skill` interface's `orchestrator.py` bug survived while only
`cli-no-fetch` was covered, and an empty `dependencies = []` formatting bug survived while `library`
was excluded — each surfaced the moment its combination was added back.

Adding a new `interface` choice therefore means adding a `COMBINATIONS` entry _and_ seeding at least
one test file for it, so `pytest` inside the generated repo has something to collect. Covering each
axis value once is not the same as covering their crossings — `browser_session` and `multi_source`
were each green on their own while their intersection generated code that couldn't import
(2026-08-23); when two axes' template files reference each other, add the crossing entry too.

## Keep `{{ package_name }}` out of mid-line wrapped prose in templated markdown

dprint reflows generated markdown at 100 columns and a generated repo's `quality.check` enforces it,
so template prose that interpolates `{{ package_name }}` mid-paragraph is only dprint-clean near the
name length it was written against — a longer name shifts the wrap and fails the generated repo's
first CI run. Put an interpolated path/command on its own line (a fenced code block), or drop the
interpolation where prose works without it ("this package"). The `*-long-name` `COMBINATIONS`
entries render with the family's longest real package name to catch this class.

## Plans

Work-in-progress designs and ideas live in `plans/YYYY-MM-DD-topic.md` — see the `plan-docs` skill
for the status lifecycle and when to retire one.
