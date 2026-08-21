"""Renders a representative spread of copier.yml answer combinations and asserts the resulting file
tree/config is well-formed. A full `uv sync && inv quality.check` run against a generated instance is
a manual end-to-end check (see README.md), too slow/networked for routine test runs."""

import tomllib
from pathlib import Path

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


def _render(tmp_path: Path, answers: dict[str, object]) -> Path:
    dst = tmp_path / "generated"
    _ = copier.run_copy(
        str(TEMPLATE_DIR),
        str(dst),
        data={**BASE_ANSWERS, **answers},
        defaults=True,
        overwrite=True,
        unsafe=False,
        vcs_ref="HEAD",
    )
    return dst


@pytest.mark.parametrize("answers", COMBINATIONS.values(), ids=COMBINATIONS.keys())
def test_generates_valid_pyproject_and_config(tmp_path: Path, answers: dict[str, object]) -> None:
    dst = _render(tmp_path, answers)

    pyproject = dst / "pyproject.toml"
    assert pyproject.exists()
    parsed = tomllib.loads(pyproject.read_text())
    assert parsed["project"]["name"] == "example-pkg"

    ruff_toml = dst / "ruff.toml"
    assert ruff_toml.exists()
    ruff_parsed = tomllib.loads(ruff_toml.read_text())
    assert ruff_parsed["lint"]["isort"]["known-first-party"] == ["example_pkg"]

    pyright_config = dst / "pyrightconfig.json"
    # JSONC (basedpyright accepts `//` comments) — not valid strict JSON, just check it's there.
    assert pyright_config.exists()
    assert pyright_config.read_text().strip()

    assert (dst / "README.md").exists()
    assert (dst / "LICENSE").exists()
    assert (dst / ".github" / "workflows" / "ci.yml").exists()

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


def test_mcp_server_seeds_server_entrypoint(tmp_path: Path) -> None:
    dst = _render(tmp_path, COMBINATIONS["mcp_server-http-single-source"])
    assert (dst / "src" / "example_pkg" / "server.py").exists()
    assert not (dst / "src" / "example_pkg" / "cli.py").exists()


def test_cli_seeds_cli_entrypoint_and_no_fetch_modules(tmp_path: Path) -> None:
    dst = _render(tmp_path, COMBINATIONS["cli-no-fetch"])
    assert (dst / "src" / "example_pkg" / "cli.py").exists()
    assert not (dst / "src" / "example_pkg" / "core").exists()
    assert not (dst / "src" / "example_pkg" / "server.py").exists()


def test_multi_source_seeds_sources_split(tmp_path: Path) -> None:
    dst = _render(tmp_path, COMBINATIONS["mcp_server-http-multi-source"])
    assert (dst / "src" / "example_pkg" / "sources" / "base.py").exists()
    assert (dst / "src" / "example_pkg" / "sources" / "olx" / "source.py").exists()
    assert not (dst / "src" / "example_pkg" / "parse.py").exists()


def test_single_source_stays_flat(tmp_path: Path) -> None:
    dst = _render(tmp_path, COMBINATIONS["mcp_server-http-single-source"])
    assert (dst / "src" / "example_pkg" / "parse.py").exists()
    assert not (dst / "src" / "example_pkg" / "sources").exists()


def test_browser_session_seeds_fetch_browser_not_http_fetch(tmp_path: Path) -> None:
    dst = _render(tmp_path, COMBINATIONS["mcp_server-browser-session"])
    assert (dst / "src" / "example_pkg" / "core" / "fetch_browser.py").exists()
    assert not (dst / "src" / "example_pkg" / "core" / "fetch.py").exists()
    assert not (dst / "src" / "example_pkg" / "core" / "cache.py").exists()


def test_skill_seeds_agent_skill_dir_and_orchestrator(tmp_path: Path) -> None:
    dst = _render(tmp_path, COMBINATIONS["skill"])
    assert (dst / ".agents" / "skills" / "example_pkg" / "SKILL.md").exists()
    assert (dst / "src" / "example_pkg" / "orchestrator.py").exists()
    assert not (dst / "src" / "example_pkg" / "core").exists()


def test_library_seeds_nothing_but_the_bare_package(tmp_path: Path) -> None:
    dst = _render(tmp_path, COMBINATIONS["library"])
    assert (dst / "src" / "example_pkg" / "__init__.py").exists()
    for extra in ("server.py", "cli.py", "app.py", "orchestrator.py", "core", "sources"):
        assert not (dst / "src" / "example_pkg" / extra).exists()
    # .agents/skills/ itself is unconditional (see test_generates_valid_pyproject_and_config) —
    # only a shipped skill payload is interface-specific.
    assert not (dst / ".agents" / "skills" / "example_pkg").exists()


def test_with_docs_off_by_default_seeds_no_docs_site(tmp_path: Path) -> None:
    dst = _render(tmp_path, COMBINATIONS["library"])
    assert not (dst / "mkdocs.yml").exists()
    assert not (dst / "docs").exists()
    assert not (dst / ".github" / "workflows" / "docs.yml").exists()
    assert "docs" not in tomllib.loads((dst / "pyproject.toml").read_text())["dependency-groups"]


def test_with_docs_seeds_docs_site(tmp_path: Path) -> None:
    dst = _render(tmp_path, {**COMBINATIONS["library"], "with_docs": True})

    mkdocs_yml = dst / "mkdocs.yml"
    assert mkdocs_yml.exists()
    mkdocs_text = mkdocs_yml.read_text()
    assert "site_name: An example project." in mkdocs_text
    assert "repo_url: https://github.com/TheodoreAD/example-pkg" in mkdocs_text

    assert (dst / "docs" / "index.md").exists()
    assert (dst / ".github" / "workflows" / "docs.yml").exists()

    pyproject = tomllib.loads((dst / "pyproject.toml").read_text())
    assert "zensical" in pyproject["dependency-groups"]["docs"]
    assert "site/" in (dst / ".gitignore").read_text()
