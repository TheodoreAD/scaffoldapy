"""Fixtures for the integration tier — the one tier whose renders run copier.yml's _tasks for real
and therefore shell out (`uv sync`, `inv configure`, the generated repo's own quality gate). Same
split as repo-tasks' tests/integration/conftest.py: whatever lets a test reach outside tmp_path
lives here, where no unit test can pick it up by accident. Fixtures only — importable constants
stay in tests/support.py (see its docstring for why `from conftest import` is unsafe here)."""

import os
import subprocess
from collections.abc import MutableMapping
from pathlib import Path
from typing import cast

import pytest
from plumbum.machines import local

# plumbum's LocalEnv has the mapping methods monkeypatch.setitem/delitem need without declaring
# the Mapping ABC — hence the cast, via `object` because basedpyright flags a direct one as
# non-overlapping.
_plumbum_env = cast(MutableMapping[str, str], cast(object, local.env))


def _uv_dir(kind: str) -> str:
    """The real machine's `uv cache dir` / `uv python dir`, resolved before HOME is faked.

    `--color never` because uv honours `FORCE_COLOR` even into a pipe, and Claude Code exports it:
    the path came back wrapped in ANSI escapes, which made it relative, so every render built a
    cold cache inside the generated repo and its `ruff check .` then linted the whole cache —
    31,442 findings, and a gate that ran into pytest's timeout instead of failing (2026-09-28).
    The absolute-path check is what turns the next such surprise into an error here."""
    out = subprocess.run(
        ["uv", "--color", "never", kind, "dir"], capture_output=True, text=True, check=True
    ).stdout.strip()
    if not Path(out).is_absolute():
        raise RuntimeError(f"`uv {kind} dir` returned a non-absolute path: {out!r}")
    return out


@pytest.fixture(autouse=True)
def isolated_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A fresh, empty HOME for every test in this tier, yielded as a Path.

    A generated repo's `inv configure` writes user-wide state — `direnv allow` records the .envrc
    under ~/.local/share/direnv/allow, `agents.wire-claude-hook` drops an env cache file under
    ~/.cache/claude-code — and both copier's _tasks and run_in_generated_repo inherit this process's
    environment. Before this fixture every real render left one of each behind on the dev machine
    (292 of each measured 2026-08-24, all pointing at long-deleted pytest-of-* directories). Autouse,
    same reasoning as repo-tasks' `tmp_cwd`: taking a fixture is something you can't forget, where a
    `monkeypatch.setenv` first line is.

    Only the two uv directories are pinned back to the real machine: the cache (a cold cache per
    render would cost the whole tier's budget again in downloads) and the managed-Python dir (so a
    render never re-downloads an interpreter into the throwaway HOME). Both resolved via uv itself
    rather than assumed under ~/.cache — UV_CACHE_DIR or a uv.toml can relocate either. The XDG
    overrides are dropped rather than repointed so `direnv` and anything else XDG-aware falls back
    to the fake HOME too. `UV_PYTHON` is dropped for the reason given at the removals list.
    """
    home = tmp_path / "home"
    home.mkdir()
    overrides = {
        "HOME": str(home),
        "UV_CACHE_DIR": _uv_dir("cache"),
        "UV_PYTHON_INSTALL_DIR": _uv_dir("python"),
    }
    # UV_PYTHON outranks a generated repo's .python-version, so a shell still carrying one (this
    # machine exported 3.14 until 2026-09-28) would build every venv at that version and hide the
    # floor this tier checks.
    removals = ("XDG_CACHE_HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "UV_PYTHON")
    # Two environments, not one: copier runs _tasks with plumbum's `local.env`, a snapshot of
    # os.environ taken when plumbum was first imported, so a monkeypatched os.environ alone leaves
    # `inv configure` writing to the real HOME while run_in_generated_repo (plain subprocess) sees
    # the fake one — confirmed live 2026-08-24, both leaks intact with only os.environ patched.
    for env in (os.environ, _plumbum_env):
        for name, value in overrides.items():
            monkeypatch.setitem(env, name, value)
        for name in removals:
            if name in env:
                monkeypatch.delitem(env, name)
    return home
