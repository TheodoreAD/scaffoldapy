"""Renders a representative spread of copier.yml answer combinations and asserts the resulting file
tree/config is well-formed. test_generated_repo_passes_quality_check_out_of_the_box is the one
real end-to-end check — runs _tasks for real (network + uv) and asserts the generated repo's own
`inv quality.check` actually exits 0, not just that its files look right — slower than the rest
of this suite but still a real pytest test, not a manual step to remember."""

import tomllib

import pytest
from conftest import COMBINATIONS, Render, package_name_of, run_in_generated_repo


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
    generated library repo, i.e. `inv quality.check` fails out of the box."""
    dst = render(COMBINATIONS["library"])
    assert (dst / "tests" / "test_example_pkg.py").exists()


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


@pytest.mark.parametrize("combo_name", COMBINATIONS)
def test_generated_repo_passes_quality_check_out_of_the_box(render: Render, combo_name: str) -> None:
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

    result = run_in_generated_repo(dst, "inv", "quality.check")
    assert result.returncode == 0, result.stdout + result.stderr
