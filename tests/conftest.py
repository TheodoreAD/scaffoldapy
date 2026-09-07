"""Shared render machinery for the template test suite, reachable from both tiers. Every render
lands in pytest's own tmp_path sandbox, so checking a combination — in a test or a one-off
investigation — is a single fixture call, never a throwaway render script in /tmp.

Fixtures only. The importable constants live in support.py, next door — see its docstring for why
`from conftest import ...` is not safe to rely on here."""

import warnings
from pathlib import Path

import copier
import pytest
from copier.errors import DirtyLocalWarning, ShallowCloneWarning

from tests.support import BASE_ANSWERS, TEMPLATE_DIR, Render


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
        # `vcs_ref="HEAD"` is what makes the template testable as it stands, and copier warns about
        # the clone it makes to do that — never about the render, which succeeds either way. Both
        # warnings it can raise here are that, and the shipped pytest.ini's `filterwarnings = error`
        # turns either into 21 failures:
        #
        #   DirtyLocalWarning   locally, the moment anyone edits template/ — i.e. exactly when the
        #                       suite is worth running.
        #   ShallowCloneWarning in CI, where actions/checkout clones at depth 1. A full clone would
        #                       silence it, but ci.yml is byte-identical to the template's copy by
        #                       design (test_repo_sync.py enforces it) and a generated repo has no
        #                       copier in its tests, so the fix belongs here rather than there.
        #
        # The pair is why a green local run did not predict CI: locally the tree is full but dirty,
        # in CI it is clean but shallow, and each raises only its own half.
        #
        # Scoped to this call rather than added to the shared pytest.ini, which ships to consumers
        # that have never heard of copier.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DirtyLocalWarning)
            warnings.simplefilter("ignore", ShallowCloneWarning)
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
