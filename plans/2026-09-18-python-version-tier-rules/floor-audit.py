"""Read-only: where each personal Python repo's declared floor, its pin, and its actual venv
disagree. Nothing is written and no repo's tasks are run — this reads three files and asks each
existing .venv's interpreter for its own version.

Scoped to the personal account root deliberately: the rule under test is about what this account
publishes and what other projects resolve into their environments.
"""

import subprocess
import tomllib
from pathlib import Path

ROOT = Path("/home/tdumitrescu/projects/github.com-personal")


def declared(repo: Path) -> str:
    pyproject = repo / "pyproject.toml"
    if not pyproject.exists():
        return "-"
    with pyproject.open("rb") as f:
        data = tomllib.load(f)
    return str(data.get("project", {}).get("requires-python", "-")).removeprefix(">=").strip() or "-"


def pinned(repo: Path) -> str:
    path = repo / ".python-version"
    return path.read_text(encoding="utf-8").strip() if path.exists() else "-"


def venv_version(repo: Path) -> str:
    python = repo / ".venv" / "bin" / "python"
    if not python.exists():
        return "-"
    result = subprocess.run([str(python), "--version"], capture_output=True, text=True, check=False)
    return result.stdout.strip().removeprefix("Python ") or "?"


def is_packaged(repo: Path) -> bool:
    """Whether this repo builds a distribution at all — the thing another project could resolve."""
    pyproject = repo / "pyproject.toml"
    if not pyproject.exists():
        return False
    with pyproject.open("rb") as f:
        return "build-system" in tomllib.load(f)


rows: list[tuple[str, str, str, str, str]] = []
for repo in sorted(p for p in ROOT.iterdir() if p.is_dir() and not p.name.startswith(".")):
    floor, pin, venv = declared(repo), pinned(repo), venv_version(repo)
    if floor == "-" and venv == "-":
        continue
    kind = "packaged" if is_packaged(repo) else "not packaged"
    rows.append((repo.name, floor, pin, venv, kind))

width = max(len(r[0]) for r in rows)
print(f"{'repo':<{width}}  {'floor':<6} {'pin':<6} {'venv':<9} kind")
for name, floor, pin, venv, kind in rows:
    above = (
        venv != "-"
        and floor != "-"
        and tuple(int(p) for p in venv.split(".")[:2]) > tuple(int(p) for p in floor.split("."))
    )
    mark = "  <-- venv above floor" if above else ""
    print(f"{name:<{width}}  {floor:<6} {pin:<6} {venv:<9} {kind}{mark}")
