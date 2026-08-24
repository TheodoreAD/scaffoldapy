"""Shared render machinery for the template test suite, reachable from both tiers. Every render
lands in pytest's own tmp_path sandbox, so checking a combination — in a test or a one-off
investigation — is a single fixture call, never a throwaway render script in /tmp.

Fixtures only. The importable constants live in support.py, next door — see its docstring for why
`from conftest import ...` is not safe to rely on here."""

from pathlib import Path

import copier
import pytest
from support import BASE_ANSWERS, TEMPLATE_DIR, Render


@pytest.fixture
def render(tmp_path: Path) -> Render:
    """Factory rendering the template into this test's own tmp_path sandbox.

    run_tasks=False (default): file-tree/config checks only — copier.yml's _tasks (uv sync,
    inv configure) need real network/uv and are skipped. This is the unit tier's mode.
    run_tasks=True: the real end-to-end render — _tasks run, producing a generated repo with its
    own .venv whose quality gate can be exercised. Integration tier only; it is what makes that
    tier slow and network-dependent.
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
