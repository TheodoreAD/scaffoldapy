"""Shared, importable test support: the COMBINATIONS parametrization source, the answer-set
helpers around it, and the render factory's type.

COMBINATIONS is the single parametrization source for the whole suite, including the real
end-to-end quality gate — see AGENTS.md: never exclude a combination to make a test pass.

Deliberately a module of its own rather than conftest.py. `from conftest import X` is ambiguous
here in two separate ways, both confirmed live: a tier-local tests/integration/conftest.py would
shadow tests/conftest.py for that tier only (silent, direction-dependent ImportError), and this
repo has a *second* tests/conftest.py under template/ that wins outright whenever pytest falls back
to searching from the working directory — which is exactly what the shipped
`testpaths = tests/unit` triggers in a repo that hasn't split its tests yet. A distinct module name
has neither problem."""

from pathlib import Path
from typing import Protocol

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
    # package_name length moves where dprint's 100-column reflow wraps any templated markdown prose
    # that interpolates it — example_pkg (11 chars) passing proves nothing about a longer name.
    # These two combinations are the ones whose markdown interpolates package_name into wrapped
    # prose today (the browser-session README, the skill SKILL.md); the name is the family's
    # longest real one, not an invented worst case.
    "mcp_server-browser-session-long-name": {
        "interface": "mcp_server",
        "fetch_strategy": "browser_session",
        "multi_source": False,
        "source_key": "temu",
        "package_name": "product_research_pipeline",
        "github_repo": "TheodoreAD/product-research-pipeline",
    },
    "skill-long-name": {
        "interface": "skill",
        "package_name": "product_research_pipeline",
        "github_repo": "TheodoreAD/product-research-pipeline",
    },
}


def package_name_of(answers: dict[str, object]) -> str:
    """The package_name a combination actually renders with (its own override, or the base one)."""
    return str({**BASE_ANSWERS, **answers}["package_name"])


class Render(Protocol):
    def __call__(self, answers: dict[str, object], *, run_tasks: bool = False) -> Path: ...
