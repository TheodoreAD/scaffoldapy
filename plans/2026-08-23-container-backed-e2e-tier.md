---
status: idea
updated: 2026-08-24
---

## Context

Deferred from the retired e2e-coverage-holes plan (landed 2026-08-23). The e2e suite
(`tests/integration/test_e2e.py`) renders into pytest's `tmp_path` on this machine with copier.yml's
`_tasks` running for real, so generation depends on the global `repo-tasks` install, `direnv`, and
an inherited `PATH` and `HOME`.

[DECISION: harden the existing `tmp_path`-based e2e first, rather than moving generation into a
container — chosen 2026-08-23. The temp-dir tests already catch real template bugs and needed no new
infrastructure; every coverage hole found that day was closable with parametrization.]

### What the revisit trigger turned out to be (2026-08-24)

The original parking condition was "a bug class the temp-dir tier structurally cannot catch". None
has appeared. What did appear is a side-effect class: the tier **mutates the dev machine's real
`$HOME` on every run**, because a generated repo's `inv configure` (`dev-env.setup` →
`direnv.allow` + `agents.wire-claude-hook`) writes user-wide state, and `run_in_generated_repo` /
copier's `_tasks` inherit the real environment. Measured 2026-08-24:

- 292 entries in `~/.local/share/direnv/allow/` whose `.envrc` path is a
  `pytest-of-tdumitrescu/…/generated` directory that no longer exists.
- 292 empty `~/.cache/claude-code/tmp-pytest-of-…-generated-direnv-env` files, same origin.

Both are exactly the kind of user-wide effect `repo-tasks`' clean-OS tier exists to keep off a dev
machine (`repo-tasks/contributing/test-tiers.md`, "Clean-OS tier: testing user-wide effects").
Harmless individually, but unbounded growth, and evidence that the tier is not sandboxed the way
`tests/conftest.py`'s docstring ("every render lands in pytest's own tmp_path sandbox") implies.

[PITFALL: `~/.cache/claude-code/` also holds ~366 `tmp-pytest-…-test_claude_hook_*-direnv-env` files
from `repo-tasks`' own **unit** tests (`tests/unit/test_agents.py` calls `wire_claude_hook` against
`tmp_path` without overriding `HOME`, and `agents.py` derives the cache dir from `Path.home()`).
That is `repo-tasks`' leak, not this repo's — it belongs in a `repo-tasks` plan, noted here only so
the two are not confused when cleaning up.]

### What the sibling repo actually has now

The retired plan's pointer to `repo-tasks`' fixtures predates several changes there; the current
shape, from `repo-tasks/tests/integration/` and `contributing/test-tiers.md`:

- `testcontainers` lives in the single `dev` dependency group — there is no separate opt-in
  `integration` group any more, and no `pyrightconfig.json`/`pytest.ini` exclude for the tier.
  `pytest.ini`'s `testpaths = tests/unit` is what keeps Docker out of `quality.check`.
- `clean-os.Dockerfile` (`debian:bookworm-slim` + `ca-certificates curl git direnv`, non-root
  `tester`, `uv` under `~/.local/bin`) lives under `tests/integration/`, deliberately not at the
  repo root.
- `clean_os_container` is module-scoped; source is mounted read-only and `tar`-copied in (excluding
  `.venv` and caches); mutating tests share one container under a disjoint-paths rule.
- The image is built through `repo_tasks.docker`'s own tasks (dogfooding), explicitly **not**
  `testcontainers`' `DockerImage`, because docker-py's `images.build()` eagerly resolves credentials
  for every registry in `~/.docker/config.json` and a stale entry fails the build. This repo has no
  dogfooding reason to use the docker tasks, so a plain `subprocess.run(["docker", "build", ...])`
  is the equivalent that avoids the same trap.
- `repo-tasks`' CI does **not** run its integration tier (Docker is opt-in there); this repo's
  `ci.yml` runs `inv test.integration` on every push. A Docker-backed test here would therefore run
  in GitHub Actions too (`ubuntu-latest` ships a daemon), adding image build and cold-cache
  `uv sync` minutes to every push.

### What CI already covers

`.github/workflows/ci.yml` runs the e2e on a fresh `ubuntu-latest` runner after
`./bootstrap-repo-tasks.sh` — a clean machine, no pre-existing `$HOME` state, the pinned
`repo-tasks` version. The "real CI runner" property the original deferral wanted is already
exercised on every push. What a container would add is that property **locally**, plus the ability
to test against a `repo-tasks` version other than the one globally installed on this machine.

### `$HOME` isolation landed in the existing tier (2026-08-24)

`tests/integration/conftest.py`'s autouse `isolated_home` fixture points `HOME` at a `tmp_path`
directory, drops the `XDG_*` overrides, and pins `UV_CACHE_DIR`/`UV_PYTHON_INSTALL_DIR` back to the
real machine's (resolved via `uv cache dir`/`uv python dir`). The e2e now also asserts the direnv
allow entry and the claude-code env file landed inside the fake HOME. Verified: the full tier passes
with the two real directories' counts unchanged, and the 293+293 stale entries were purged.

[PITFALL: `monkeypatch.setenv` alone does not reach copier's `_tasks`. copier runs them with
plumbum's `local.env` (`copier/_main.py`, `subprocess.run(..., env=dict(local.env))`), a snapshot of
`os.environ` taken when plumbum is first imported — so with only `os.environ` patched, the generated
repo's configure step still wrote to the real HOME while the plain-subprocess
`run_in_generated_repo` saw the fake one. Both mappings have to be patched; the fixture does it from
one loop. Confirmed live, both leaks intact on the first attempt.]

## Open questions

- [NEEDS CLARIFICATION: if the container tier is built, does it replace the `tmp_path` e2e or sit
  beside it? Beside means two renders of every `COMBINATIONS` entry per `inv test.integration` — the
  slow tier roughly doubles, and in CI the container one is redundant with the runner itself.
  Replace means losing the warm-cache ~50s local loop unless the host uv cache is bind-mounted in.]
- [NEEDS CLARIFICATION: what does the container install `repo-tasks` from? `bootstrap-repo-tasks.sh`
  (the stamped version, matching CI) is the honest default; a bind-mounted local `repo-tasks`
  checkout is the cross-repo-development case the `tmp_path` tier can never offer, and may be the
  one thing that justifies the container at all.]

## Recommended direction

The side-effect finding is answered by the `$HOME` isolation above, at no new dependency and no
speed cost. That leaves the container question exactly where the original decision put it.

[DEFERRED: a container-backed e2e tier — `tests/integration/clean-os.Dockerfile` copied from
`repo-tasks`' shape, `testcontainers` added to `dev`, a module-scoped container that runs
`bootstrap-repo-tasks.sh` then `copier copy --trust` per combination and asserts
`inv quality.check`. Worth building only for what `$HOME` isolation cannot give: a truly clean OS
with no pre-installed `repo-tasks` (proving the bootstrap script + generation from zero, locally),
and generating against a `repo-tasks` version other than this machine's global install. Revisit
trigger: the first time a `repo-tasks` change needs to be tested against this template before it is
released, or a generated-repo failure reproduces in CI but not locally. Both halves fired on
2026-08-25 without a container being the fix: two `repo-tasks` `main` changes broke every generated
repo and were only visible once the global tool was updated (`inv repo-tasks.update`, the
AGENTS.md-sanctioned workaround), and the e2e's own direnv assertion passed locally and failed on a
runner with no `direnv`. Neither needed a container, but each cost a full CI round trip to learn
what a local clean-OS run would have shown in a minute — the tally to weigh against the build cost.]
