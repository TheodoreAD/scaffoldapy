"""Shared render machinery for the template test suite. Every render lands in pytest's own
tmp_path sandbox, so checking a combination — in a test or a one-off investigation — is a single
fixture call, never a throwaway render script in /tmp.

COMBINATIONS is the single parametrization source for the whole suite, including the real
end-to-end quality gate — see AGENTS.md: never exclude a combination to make a test pass."""

import os
import subprocess
from pathlib import Path
from typing import Protocol

import copier
import pytest

TEMPLATE_DIR = Path(__file__).parent.parent

BASE_ANSWERS: dict[str, object] = {
    "package_name": "example_pkg",
    "description": "An example project.",
    "github_repo": "TheodoreAD/example-pkg",
}

COMBINATIONS: dict[str, dict[str, object]] = {
    "mcp_server-http-single-source": {
        "interface": "mcp_server",
        "fetch_strategy": "http",
        "multi_source": False,
        "source_key": "olx",
    },
    "mcp_server-http-multi-source": {
        "interface": "mcp_server",
        "fetch_strategy": "http",
        "multi_source": True,
        "source_key": "olx",
    },
    "mcp_server-browser-session": {
        "interface": "mcp_server",
        "fetch_strategy": "browser_session",
        "multi_source": False,
        "source_key": "temu",
    },
    # Covering each axis value once is not the same as covering their crossings: browser_session
    # and multi_source were each green above while their intersection generated code that couldn't
    # import (sources/base.py hardcoded the http fetcher, 2026-08-23).
    "mcp_server-browser-multi-source": {
        "interface": "mcp_server",
        "fetch_strategy": "browser_session",
        "multi_source": True,
        "source_key": "temu",
    },
    "cli-no-fetch": {
        "interface": "cli",
        "fetch_strategy": "none",
    },
    "web_service-no-fetch": {
        "interface": "web_service",
        "fetch_strategy": "none",
    },
    "skill": {
        "interface": "skill",
    },
    "library": {
        "interface": "library",
    },
}


def package_name_of(answers: dict[str, object]) -> str:
    """The package_name a combination actually renders with (its own override, or the base one)."""
    return str({**BASE_ANSWERS, **answers}["package_name"])


class Render(Protocol):
    def __call__(self, answers: dict[str, object], *, run_tasks: bool = False) -> Path: ...


@pytest.fixture
def render(tmp_path: Path) -> Render:
    """Factory rendering the template into this test's own tmp_path sandbox.

    run_tasks=False (default): file-tree/config checks only — copier.yml's _tasks (uv sync,
    inv configure) need real network/uv and are skipped.
    run_tasks=True: the real end-to-end render — _tasks run, producing a generated repo with its
    own .venv whose quality gate can be exercised via run_in_generated_repo.
    """

    def _render(answers: dict[str, object], *, run_tasks: bool = False) -> Path:
        dst = tmp_path / "generated"
        _ = copier.run_copy(
            str(TEMPLATE_DIR),
            str(dst),
            data={**BASE_ANSWERS, **answers},
            defaults=True,
            overwrite=True,
            unsafe=run_tasks,
            vcs_ref="HEAD",
            skip_tasks=not run_tasks,
        )
        return dst

    return _render


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
    """
    return subprocess.run(
        list(args),
        cwd=dst,
        env={**os.environ, "PATH": f"{dst / '.venv' / 'bin'}:{os.environ['PATH']}"},
        capture_output=True,
        text=True,
        check=False,
    )
