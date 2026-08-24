"""The one real end-to-end check: renders every COMBINATIONS entry for real — copier.yml's _tasks
included — and asserts the generated repo's own `inv quality.check` genuinely exits 0.

Its prerequisites are what put it in the integration tier rather than the unit one: real network,
`uv`, and the globally `uv tool install`ed repo-tasks. It is not in `inv quality.check`'s gate;
`inv test.integration` runs it, and `.github/workflows/ci.yml` calls that on every push — see
AGENTS.md, which also carries the standing rule that a combination is never excluded to make this
pass."""

import os
import subprocess
from pathlib import Path

import pytest
from support import COMBINATIONS, Render


def run_in_generated_repo(dst: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run a command inside a generated repo, sandboxed to its own toolchain.

    Bare `inv`, not `uv run inv` — repo-tasks/invoke are deliberately never project dependencies
    of a generated repo (see pyproject.toml.jinja), only the globally `uv tool install`ed
    repo-tasks on this machine, the same assumption copier.yml's own _tasks and the generated
    .github/workflows/ci.yml both make. `dst/.venv/bin` is prepended ahead of whatever's already
    on PATH so the generated repo's own ruff/pytest/basedpyright/... always win over this suite's
    own dev venv (this suite's dependencies have no reason to match a given combination's —
    confirmed live: a bare inherited PATH resolved `pytest` to *this* repo's venv instead of the
    generated one, and the generated repo's `typer` dependency was invisible there).

    Lives here rather than in a conftest deliberately: it shells out into a generated repo, which
    is precisely the capability no unit-tier test should be able to reach by accident.
    """
    return subprocess.run(
        list(args),
        cwd=dst,
        env={**os.environ, "PATH": f"{dst / '.venv' / 'bin'}:{os.environ['PATH']}"},
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize("combo_name", COMBINATIONS)
def test_generated_repo_passes_quality_check_out_of_the_box(
    render: Render, isolated_home: Path, combo_name: str
) -> None:
    """Real end-to-end: renders without skip_tasks (copier.yml's _tasks — `uv sync`, then
    `uv run inv configure` — actually runs, hitting the network and pulling repo-tasks'
    canonical configs for real), then runs the generated repo's own `inv quality.check` and
    asserts it genuinely exits 0. Parametrized over every `COMBINATIONS` entry. Full interface
    coverage matters here specifically: `orchestrator.py`'s `contextlib.suppress`/`async with` bug
    (fixed 2026-08-23) only existed in the `skill` interface's own template, invisible to a version
    of this test that only ever rendered `cli-no-fetch`.

    Deliberately `quality.check`, not `quality.precommit` — the generated repo's actual CI
    (`.github/workflows/ci.yml`) runs check-only, with no auto-fix step first. `precommit` runs
    `fix` (ruff format, dprint fmt, ...) before checking, which would silently mask exactly the
    kind of formatting bug this test exists to catch (confirmed live 2026-08-23: a dprint
    markdown-wrapping bug in the generated README.md/SKILL.md passed a `precommit`-based version
    of this test while failing every generated repo's real CI).
    """
    dst = render(COMBINATIONS[combo_name], run_tasks=True)
    assert (dst / "pyrightconfig.json").exists()  # _tasks ran for real, configs.pull included
    # `inv configure`'s user-wide writes landed in the sandboxed HOME, not the dev machine's — the
    # positive half of the isolated_home fixture's promise, checked where it is cheapest.
    assert any((isolated_home / ".local" / "share" / "direnv" / "allow").iterdir())
    assert any((isolated_home / ".cache" / "claude-code").iterdir())

    result = run_in_generated_repo(dst, "inv", "quality.check")
    assert result.returncode == 0, result.stdout + result.stderr
