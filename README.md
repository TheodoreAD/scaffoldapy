# scaffoldapy

Copier template for scaffolding repos in this personal Python agent-tooling family — MCP servers,
CLIs, web services, Agent Skills, and plain libraries — with the family's structural conventions
([`repo-tasks`](https://github.com/TheodoreAD/repo-tasks), `src/` layout, dedicated per-tool config
files) already wired in.

Built around **composable axes**, not fixed shapes: `interface` (what the repo ships — MCP server,
CLI, web service, skill, or library), `fetch_strategy` (none, plain polite HTTP, or a CDP-driven
browser session), and `multi_source` (a single upstream vs. a pluggable per-source adapter). Each
answer gates a small, independent module of files rather than branching into separate monolithic
trees — a CLI or web service that fetches gets the exact same `core/` polite-fetch primitives an MCP
server does.

## Usage

```shell
copier copy gh:TheodoreAD/scaffoldapy /path/to/new-repo
```

or, to pick up template improvements in an already-generated repo later:

```shell
copier update
```

(run from inside the generated repo, which keeps its own `.copier-answers.yml`).

## Template structure

Template content lives under `template/` (`_subdirectory: template` in `copier.yml`) — everything
else at this repo's root (`pyproject.toml`, `tasks.py`, `ruff.toml`, ...) is `scaffoldapy`'s own dev
tooling, dogfooding `repo-tasks` like every other repo in the family, and is never copied into a
generated project. `ruff.toml`/`pyrightconfig.json`/`dprint.json`/`pytest.ini`/`.editorconfig` are
**not** stamped into the template at all — `copier.yml`'s `_tasks` (`uv sync`, then
`uv run inv configure`) pulls them from `repo-tasks`' canonical copies automatically right after
generation, same mechanism every other consumer uses (see
[`contributing/repo-family-architecture.md`](https://github.com/TheodoreAD/power-user-linux-setup/blob/master/contributing/repo-family-architecture.md)
in `power-user-linux-setup`). `LICENSE`, `tasks.py`, `.gitignore`, `.github/workflows/ci.yml` are
still deliberately duplicated in both places with identical content — kept in sync by hand, since
those aren't `repo-tasks`' concern.

## Dev loop

- `uv sync` + `direnv allow` once, then plain `pytest`/`inv` (no `uv run` wrapper needed).
- `inv quality.precommit` before considering a change done — `tasks.py` is
  `from repo_tasks import
  ns`, `repo-tasks`' own ready-made root Collection with `quality` (and
  future modules) already nested under their own names, so no local `add_collection` wiring needed
  here either.
- `pytest` — most of `tests/test_template.py` renders a representative spread of `copier.yml` answer
  combinations into a temp dir with `skip_tasks=True` (fast, offline — `_tasks` needs real
  `uv`/network) and asserts the resulting file tree/config is well-formed.
  `test_generated_repo_passes_quality_precommit_out_of_the_box` is the one real end-to-end check —
  renders for real (`_tasks` included), then asserts the generated repo's own
  `inv quality.precommit` genuinely exits 0. Uses the `cli` interface, not `library` — `library`
  generates zero test files, which makes pytest itself exit nonzero (no tests collected) for a
  reason unrelated to what that test checks; a real gap in the `library` interface specifically, not
  yet fixed.
