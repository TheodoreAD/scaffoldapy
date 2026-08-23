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
- `pytest` — the whole suite runs in under a minute. Don't reach for a throwaway render script to
  check template output: `tests/conftest.py`'s `render` fixture sandboxes any combination into
  `tmp_path` in one call, and the suite already renders every `COMBINATIONS` entry.

## Two file trees, and only one of them is the template

`template/` is what gets copied into a generated repo (`_subdirectory: template` in `copier.yml`).
Everything at this repo's root — `pyproject.toml`, `tasks.py`, `ruff.toml`, `tests/` — is
`scaffoldapy`'s _own_ dev tooling and is never copied anywhere. Editing the root copy when the
template copy was meant is the easiest mistake to make here.

Some files deliberately exist in both places. `LICENSE`, `.envrc`, `tasks.py` and
`.github/workflows/ci.yml` are byte-identical, and `tests/test_repo_sync.py` fails if they ever stop
being — hand-syncing is not a plan on its own, which is how `ci.yml` sat on the pre-`repo-tasks` CI
recipe at the root while the template's copy had moved on. `.gitignore` is the deliberate exception:
the template's copy is a superset (a generated repo can have `site/` and `.cache/`; this one can't),
so the guard checks containment rather than equality.

Others deliberately exist only at the root and must **not** be added to `template/` — `ruff.toml`,
`pyrightconfig.json`, `dprint.json`, `pytest.ini`, `.editorconfig` are pulled from `repo-tasks`'
canonical copies by `copier.yml`'s `_tasks` at generation time instead, and `tests/test_template.py`
asserts they're absent from a freshly rendered repo.

Interface-conditional template files encode the condition in the _filename_, e.g.
`template/tests/{% if interface == "cli" %}test_cli.py{% endif %}.jinja` — an empty rendered name
means copier drops the file entirely.

## Never exclude a combination from the e2e test to make it pass

`test_generated_repo_passes_quality_check_out_of_the_box` renders for real (`_tasks` included:
network, `uv`) and asserts a generated repo's own `inv quality.check` exits 0. It is the only test
that catches template _content_ bugs — bad Jinja whitespace, unformatted output, broken generated
code — and it only catches them for combinations it actually runs.

Every entry in `COMBINATIONS` stays parametrized into it. If one fails, the template is wrong: fix
the template. Confirmed twice: the `skill` interface's `orchestrator.py` bug survived while only
`cli-no-fetch` was covered, and an empty `dependencies = []` formatting bug survived while `library`
was excluded — each surfaced the moment its combination was added back.

Adding a new `interface` choice therefore means adding a `COMBINATIONS` entry _and_ seeding at least
one test file for it, so `pytest` inside the generated repo has something to collect.

## Plans

Work-in-progress designs and ideas live in `plans/YYYY-MM-DD-topic.md` — see the `plan-docs` skill
for the status lifecycle and when to retire one.
