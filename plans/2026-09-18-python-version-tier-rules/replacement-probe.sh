#!/usr/bin/env bash
# If UV_PYTHON is the thing defeating every declared floor, what replaces it without losing the
# behaviour it exists for? Two legs:
#   1. does a global ~/.python-version still default an *unconstrained* script to 3.14?
#   2. does `uv tool install` even need it -- i.e. with nothing set, what does it pick?
# Everything runs under a fake HOME and a sandboxed tool dir. The real install is never touched.
set -uo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
HOME_DIR="$DIR/replacement-home"
REAL_CACHE="$(uv cache dir)"
REAL_PYTHONS="$(uv python dir)"

rm -rf "$HOME_DIR"
mkdir -p "$HOME_DIR"

cat > "$DIR/unconstrained.py" << 'EOF'
# /// script
# requires-python = ">=3.9"
# ///
import sys

print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
EOF

run() { # run <description> <extra env...>
  local label="$1"
  shift
  local out
  out=$(env -u UV_PYTHON -u VIRTUAL_ENV -u PYTHONPATH \
    HOME="$HOME_DIR" UV_CACHE_DIR="$REAL_CACHE" UV_PYTHON_INSTALL_DIR="$REAL_PYTHONS" \
    "$@" 2>&1 | tail -1)
  printf '%-52s %s\n' "$label" "$out"
}

echo "=== leg 1: does a global .python-version still supply the default? ==="
rm -f "$HOME_DIR/.python-version"
run "unconstrained script, nothing set" uv run --no-project "$DIR/unconstrained.py"
echo "3.14" > "$HOME_DIR/.python-version"
run "unconstrained script, global .python-version=3.14" uv run --no-project "$DIR/unconstrained.py"
run "==3.11.* script,    global .python-version=3.14" uv run --no-project "$DIR/pep723/exact.py"

echo
echo "=== leg 2: what does uv tool install pick with nothing set? ==="
rm -f "$HOME_DIR/.python-version"
TOOLS="$DIR/replacement-tools"
rm -rf "$TOOLS"
env -u UV_PYTHON -u VIRTUAL_ENV -u PYTHONPATH \
  HOME="$HOME_DIR" UV_CACHE_DIR="$REAL_CACHE" UV_PYTHON_INSTALL_DIR="$REAL_PYTHONS" \
  UV_TOOL_DIR="$TOOLS" UV_TOOL_BIN_DIR="$TOOLS/bin" \
  uv tool install --force /home/tdumitrescu/projects/github.com-personal/repo-tasks > /dev/null 2>&1
found=$(find "$TOOLS" -maxdepth 4 -name 'python3.*' -type l 2> /dev/null | head -1)
echo "repo-tasks declares >=3.11; uv tool install with nothing set chose:"
"$TOOLS/repo-tasks/bin/python" --version 2> /dev/null || echo "  (interpreter link: ${found:-not found})"
