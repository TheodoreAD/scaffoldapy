#!/usr/bin/env bash
# "We don't want to actively change what uv does on install, and if there's a clash I'd like to
# know." This is that test, on the one case that can differ: a tool that declares it cannot run on
# the default. Everything sandboxed -- fake HOME, throwaway tool dir, the real install untouched.
set -uo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
HOME_DIR="$DIR/clash-home"
PKG="$DIR/clash-pkg"
REAL_CACHE="$(uv cache dir)"
REAL_PYTHONS="$(uv python dir)"

rm -rf "$HOME_DIR" "$PKG"
mkdir -p "$HOME_DIR" "$PKG/src/clashprobe"

cat > "$PKG/pyproject.toml" << 'EOF'
[project]
name = "clashprobe"
version = "0"
# The whole point: this tool says it cannot run on 3.14.
requires-python = ">=3.11,<3.12"

[project.scripts]
clashprobe = "clashprobe:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
EOF

cat > "$PKG/src/clashprobe/__init__.py" << 'EOF'
import sys


def main() -> None:
    print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
EOF

attempt() { # attempt <label> <env assignments...>
  local label="$1"
  shift
  local tools="$DIR/clash-tools"
  rm -rf "$tools"
  local out
  out=$(env -u UV_PYTHON -u VIRTUAL_ENV -u PYTHONPATH \
    HOME="$HOME_DIR" UV_CACHE_DIR="$REAL_CACHE" UV_PYTHON_INSTALL_DIR="$REAL_PYTHONS" \
    UV_TOOL_DIR="$tools" UV_TOOL_BIN_DIR="$tools/bin" \
    "$@" uv tool install --force "$PKG" 2>&1)
  local chosen
  chosen=$("$tools/clashprobe/bin/python" --version 2> /dev/null || echo "install failed")
  local note=""
  echo "$out" | rg -qi 'incompatible|does not satisfy|no interpreter' && note="  (uv complained)"
  printf '%-40s %s%s\n' "$label" "$chosen" "$note"
}

echo "clashprobe declares requires-python = \">=3.11,<3.12\""
echo
printf '%-40s %s\n' "default mechanism" "interpreter the tool got"
rm -f "$HOME_DIR/.config/uv/.python-version"
attempt "UV_PYTHON=3.14 (today)" env UV_PYTHON=3.14
attempt "nothing set" env
env -u UV_PYTHON HOME="$HOME_DIR" uv python pin --global 3.14 > /dev/null 2>&1
attempt "uv python pin --global 3.14" env
