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
generated project. A few files are deliberately duplicated in both places with identical content
(`LICENSE`, `.editorconfig`, `pytest.ini`, `dprint.json`, `tasks.py`, `.gitignore`,
`.github/workflows/ci.yml`) — kept in sync by hand, same convention `repo-tasks`' own `ruff.toml`
comment already documents for the family at large.

## Dev loop

- `uv sync` + `direnv allow` once, then plain `pytest`/`inv` (no `uv run` wrapper needed).
- `inv quality.precommit` before considering a change done — `tasks.py` is `from repo_tasks import
  ns`, `repo-tasks`' own ready-made root Collection with `quality` (and future modules) already
  nested under their own names, so no local `add_collection` wiring needed here either.
- `pytest` — `tests/test_template.py` renders a representative spread of `copier.yml` answer
  combinations into a temp dir and asserts the resulting file tree/config is well-formed.
- Manual end-to-end check after a real template change: `copier copy . /tmp/scaffold-check --data
  ...`, then `uv sync && inv quality.check` inside the generated dir — must pass clean out of the box.
