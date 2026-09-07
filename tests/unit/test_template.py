"""Renders a representative spread of copier.yml answer combinations and asserts the resulting file
tree/config is well-formed. Every render here skips copier.yml's _tasks, so the whole module needs
nothing beyond the dev dependency group — that is what keeps it in the unit tier.

The one check that renders for real, _tasks and all, is
test_generated_repo_passes_quality_check_out_of_the_box in tests/integration/test_e2e.py."""

import shutil
import subprocess
import tomllib
from pathlib import Path
from typing import cast

import copier
import pytest
import yaml

from tests.support import BASE_ANSWERS, COMBINATIONS, TEMPLATE_DIR, Render, package_name_of


@pytest.mark.parametrize("answers", COMBINATIONS.values(), ids=COMBINATIONS.keys())
def test_generates_valid_pyproject_and_config(render: Render, answers: dict[str, object]) -> None:
    dst = render(answers)
    pkg = package_name_of(answers)

    pyproject = dst / "pyproject.toml"
    assert pyproject.exists()
    parsed = tomllib.loads(pyproject.read_text())
    assert parsed["project"]["name"] == pkg.replace("_", "-")

    # ruff.toml/pyrightconfig.json/dprint.json/pytest.ini/.editorconfig are deliberately NOT
    # stamped into the template at all — copier.yml's _tasks pulls them from repo-tasks'
    # canonical copies at generation time (skipped here, see the render fixture — exercised for
    # real in test_generated_repo_passes_quality_check_out_of_the_box below).
    for name in ("ruff.toml", "pyrightconfig.json", "dprint.json", "pytest.ini", ".editorconfig"):
        assert not (dst / name).exists()

    assert (dst / "README.md").exists()
    assert (dst / "LICENSE").exists()
    assert (dst / ".github" / "workflows" / "ci.yml").exists()

    # PEP 561 marker: without it a consumer installing this package (`uv add git+...`) sees it as
    # untyped, however fully annotated its source actually is.
    assert (dst / "src" / pkg / "py.typed").exists()

    # core/cache.py's ResponseCache writes under .cache/<package_name> by default, so a generated
    # repo that fetches would otherwise offer its own disk cache up for committing.
    assert ".cache/" in (dst / ".gitignore").read_text()

    # Without a rendered answers file `copier update` cannot run at all — copier never writes it
    # on its own, the template has to render it (confirmed against copier 9.17.1, whose
    # `run_update` raises when it's absent). It must also record the answers actually used, or an
    # update would replay the wrong ones.
    answers_file = dst / ".copier-answers.yml"
    assert answers_file.exists()
    recorded = cast("dict[str, object]", yaml.safe_load(answers_file.read_text()))
    assert recorded["_commit"]
    assert recorded["_src_path"]
    assert recorded["package_name"] == pkg

    agents_md = dst / "AGENTS.md"
    assert agents_md.exists()
    claude_md = dst / "CLAUDE.md"
    assert claude_md.is_symlink()
    assert claude_md.resolve() == agents_md.resolve()

    agents_skills = dst / ".agents" / "skills"
    assert (agents_skills / "README.md").exists()
    claude_skills = dst / ".claude" / "skills"
    assert claude_skills.is_symlink()
    assert claude_skills.resolve() == agents_skills.resolve()


def test_mcp_server_seeds_server_entrypoint(render: Render) -> None:
    dst = render(COMBINATIONS["mcp_server-http-single-source"])
    assert (dst / "src" / "example_pkg" / "server.py").exists()
    assert not (dst / "src" / "example_pkg" / "cli.py").exists()


def test_cli_seeds_cli_entrypoint_and_no_fetch_modules(render: Render) -> None:
    dst = render(COMBINATIONS["cli-no-fetch"])
    assert (dst / "src" / "example_pkg" / "cli.py").exists()
    assert not (dst / "src" / "example_pkg" / "core").exists()
    assert not (dst / "src" / "example_pkg" / "server.py").exists()


def test_multi_source_seeds_sources_split(render: Render) -> None:
    dst = render(COMBINATIONS["mcp_server-http-multi-source"])
    assert (dst / "src" / "example_pkg" / "sources" / "base.py").exists()
    assert (dst / "src" / "example_pkg" / "sources" / "olx" / "source.py").exists()
    assert not (dst / "src" / "example_pkg" / "parse.py").exists()


def test_single_source_stays_flat(render: Render) -> None:
    dst = render(COMBINATIONS["mcp_server-http-single-source"])
    assert (dst / "src" / "example_pkg" / "parse.py").exists()
    assert not (dst / "src" / "example_pkg" / "sources").exists()


def test_browser_session_seeds_fetch_browser_not_http_fetch(render: Render) -> None:
    dst = render(COMBINATIONS["mcp_server-browser-session"])
    assert (dst / "src" / "example_pkg" / "core" / "fetch_browser.py").exists()
    assert not (dst / "src" / "example_pkg" / "core" / "fetch.py").exists()
    assert not (dst / "src" / "example_pkg" / "core" / "cache.py").exists()


def test_skill_seeds_agent_skill_dir_and_orchestrator(render: Render) -> None:
    dst = render(COMBINATIONS["skill"])
    # Kebab-case, matching the SKILL.md `name:` field and every skill in the family — the
    # directory name is the skill's identity to Claude Code, so a snake_case package_name must
    # not leak into it.
    assert (dst / ".agents" / "skills" / "example-pkg" / "SKILL.md").exists()
    assert (dst / "src" / "example_pkg" / "orchestrator.py").exists()
    assert not (dst / "src" / "example_pkg" / "core").exists()


def test_library_seeds_nothing_but_the_bare_package(render: Render) -> None:
    dst = render(COMBINATIONS["library"])
    assert (dst / "src" / "example_pkg" / "__init__.py").exists()
    for extra in ("server.py", "cli.py", "app.py", "orchestrator.py", "core", "sources"):
        assert not (dst / "src" / "example_pkg" / extra).exists()
    # .agents/skills/ itself is unconditional (see test_generates_valid_pyproject_and_config) —
    # only a shipped skill payload is interface-specific.
    assert not (dst / ".agents" / "skills" / "example-pkg").exists()


def test_library_seeds_a_smoke_test(render: Render) -> None:
    """Every other interface seeds a test for its own entrypoint; a library has none to exercise,
    so it gets an import smoke test instead. Not boilerplate for its own sake — it's the seed of a
    working test suite, and without it `pytest` exits nonzero (no tests collected) in a freshly
    generated library repo, i.e. `inv quality.check` fails out of the box.

    Under tests/unit/, matching the `testpaths = tests/unit` that repo-tasks' canonical pytest.ini
    ships to every generated repo — a flat tests/ only works via pytest's warn-and-search-from-cwd
    fallback, which is not the layout a fresh repo should start life in."""
    dst = render(COMBINATIONS["library"])
    assert (dst / "tests" / "unit" / "test_example_pkg.py").exists()


def test_with_docs_off_by_default_seeds_no_docs_site(render: Render) -> None:
    dst = render(COMBINATIONS["library"])
    assert not (dst / "mkdocs.yml").exists()
    assert not (dst / "docs").exists()
    assert not (dst / ".github" / "workflows" / "docs.yml").exists()
    assert "docs" not in tomllib.loads((dst / "pyproject.toml").read_text())["dependency-groups"]


def test_with_docs_seeds_docs_site(render: Render) -> None:
    dst = render({**COMBINATIONS["library"], "with_docs": True})

    mkdocs_yml = dst / "mkdocs.yml"
    assert mkdocs_yml.exists()
    mkdocs_text = mkdocs_yml.read_text()
    # site_name is the project, not its one-line description — the description is what
    # site_description is for.
    assert "site_name: example-pkg" in mkdocs_text
    assert "site_description: An example project." in mkdocs_text
    assert "repo_url: https://github.com/TheodoreAD/example-pkg" in mkdocs_text

    assert (dst / "docs" / "index.md").exists()
    assert (dst / ".github" / "workflows" / "docs.yml").exists()

    pyproject = tomllib.loads((dst / "pyproject.toml").read_text())
    assert "zensical" in pyproject["dependency-groups"]["docs"]
    assert "site/" in (dst / ".gitignore").read_text()


def _git(cwd: Path, *args: str) -> None:
    _ = subprocess.run(
        ["git", "-c", "user.name=test", "-c", "user.email=test@example.com", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
    )


def test_copier_update_round_trip(tmp_path: Path) -> None:
    """Render → commit → advance the template → `copier update` actually lands the change.

    This is the only test that proves updating is possible at all: the answers file, every
    `run_update` precondition (git-tracked clean subproject, git-tracked template, a detectable
    version on both sides), and the diff application have to work together. The template side is a
    committed copy in tmp_path — never this repo's real working tree — and it's left untagged like
    the real repo, so this also proves the update survives two dunamai dev versions
    (0.0.0.postN.dev0+hash) on either side of copier's downgrade guard.

    unsafe=True mirrors the real invocation: a template with `_tasks` needs `copier update --trust`
    even though the tasks themselves are copy-only (guarded by `_copier_operation` in copier.yml).
    """
    template_repo = tmp_path / "template_repo"
    template_repo.mkdir()
    _ = shutil.copy(TEMPLATE_DIR / "copier.yml", template_repo)
    _ = shutil.copytree(TEMPLATE_DIR / "template", template_repo / "template", symlinks=True)
    _git(template_repo, "init")
    _git(template_repo, "add", "-A")
    _git(template_repo, "commit", "-m", "template v1")

    dst = tmp_path / "generated"
    _ = copier.run_copy(
        str(template_repo),
        str(dst),
        data={**BASE_ANSWERS, **COMBINATIONS["cli-no-fetch"]},
        defaults=True,
        overwrite=True,
        skip_tasks=True,
    )
    _git(dst, "init")
    _git(dst, "add", "-A")
    _git(dst, "commit", "-m", "generated")
    answers_before = cast("dict[str, object]", yaml.safe_load((dst / ".copier-answers.yml").read_text()))
    commit_before = answers_before["_commit"]

    marker = "A line only the advanced template contains."
    agents_md = template_repo / "template" / "AGENTS.md"
    _ = agents_md.write_text(agents_md.read_text() + f"\n{marker}\n")
    _git(template_repo, "commit", "-am", "template v2")

    _ = copier.run_update(
        str(dst),
        defaults=True,
        overwrite=True,
        skip_tasks=True,
        unsafe=True,
    )

    assert marker in (dst / "AGENTS.md").read_text()
    recorded = cast("dict[str, object]", yaml.safe_load((dst / ".copier-answers.yml").read_text()))
    assert recorded["_commit"] != commit_before  # the answers file moved with the update


def test_answers_file_is_dprint_clean_whatever_the_commit_hash(render: Render) -> None:
    """The stock `to_nice_yaml` answers-file idiom single-quotes any value pyyaml decides needs
    quoting — e.g. an all-digit `_commit` short hash — and the canonical dprint YAML config every
    generated repo pulls enforces double quotes, failing the generated repo's quality gate.
    Whether the e2e test catches that depends on the luck of this repo's current short hash
    (confirmed live 2026-08-23 on hash 4276235), so check the rendered answers file against the
    same canonical dprint config directly."""
    dst = render(COMBINATIONS["library"])
    result = subprocess.run(
        [
            "dprint",
            "check",
            "--config",
            str(TEMPLATE_DIR / "dprint.json"),
            str(dst / ".copier-answers.yml"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
