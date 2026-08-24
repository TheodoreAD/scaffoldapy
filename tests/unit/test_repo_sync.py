"""Guards the files that deliberately exist twice — once as this repo's own dev tooling at the
root, once inside template/ — against the drift that hand-syncing invites. AGENTS.md claimed all
four such files were byte-identical for a while when only LICENSE actually was: .github/workflows/
ci.yml had been left behind on the pre-repo-tasks CI recipe, and nothing anywhere would have said
so. These tests are that "nothing anywhere"."""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
TEMPLATE_ROOT = REPO_ROOT / "template"

# Byte-identical in both places, by design. Not repo-tasks' concern (it owns ruff.toml and the
# other four canonical configs instead, pulled at generation time), and not parametrizable per
# generated repo either — so a plain duplicate is the honest shape, as long as something checks it.
IDENTICAL_FILES = [
    "LICENSE",
    ".envrc",
    ".github/workflows/ci.yml",
    "tasks.py",
]


@pytest.mark.parametrize("relpath", IDENTICAL_FILES)
def test_root_and_template_copies_stay_identical(relpath: str) -> None:
    root_copy = REPO_ROOT / relpath
    template_copy = TEMPLATE_ROOT / relpath
    assert root_copy.exists(), f"{relpath} missing at the repo root"
    assert template_copy.exists(), f"{relpath} missing under template/"
    assert root_copy.read_text() == template_copy.read_text(), (
        f"{relpath} has drifted between the repo root and template/ — they are meant to stay "
        "byte-identical (see AGENTS.md, 'Two file trees')"
    )


def test_template_gitignore_is_a_superset_of_the_root_one() -> None:
    """.gitignore is the one duplicate that legitimately differs: a generated repo can build a
    docs site (site/) and run an http fetcher's disk cache (.cache/), neither of which this repo
    does. Everything the root ignores still has to be ignored there too."""
    root_entries = {line.strip() for line in (REPO_ROOT / ".gitignore").read_text().splitlines() if line.strip()}
    template_entries = {
        line.strip() for line in (TEMPLATE_ROOT / ".gitignore").read_text().splitlines() if line.strip()
    }
    assert root_entries <= template_entries, (
        f"template/.gitignore is missing entries the root one has: {sorted(root_entries - template_entries)}"
    )
