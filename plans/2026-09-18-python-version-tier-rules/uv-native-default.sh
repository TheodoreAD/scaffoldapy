#!/usr/bin/env bash
# The user's proposal: keep a default Python, but set it through uv's own managed mechanism rather
# than an exported shell variable. Does `uv python pin --global` give the same default while still
# yielding to a script's or project's own declaration? Sandboxed HOME throughout.
set -uo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
HOME_DIR="$DIR/native-home"
REAL_CACHE="$(uv cache dir)"
REAL_PYTHONS="$(uv python dir)"

rm -rf "$HOME_DIR"
mkdir -p "$HOME_DIR"

sandbox() {
  env -u UV_PYTHON -u VIRTUAL_ENV -u PYTHONPATH \
    HOME="$HOME_DIR" UV_CACHE_DIR="$REAL_CACHE" UV_PYTHON_INSTALL_DIR="$REAL_PYTHONS" "$@"
}

echo "=== uv python pin --global 3.14 ==="
sandbox uv python pin --global 3.14
echo "wrote:"
find "$HOME_DIR" -name '.python-version' -printf '  %p: ' -exec cat {} \; 2> /dev/null

echo
printf '%-42s %s\n' "script" "interpreter chosen"
printf '%-42s %s\n' "requires-python = \">=3.9\"  (unconstrained)" "$(sandbox uv run --no-project "$DIR/unconstrained.py" 2> /dev/null | tail -1)"
printf '%-42s %s\n' "requires-python = \"==3.11.*\" (pinned low)" "$(sandbox uv run --no-project "$DIR/pep723/exact.py" 2> /dev/null | tail -1)"

echo
echo "=== and a project, not a script: does the global pin beat requires-python? ==="
PROJ="$DIR/native-proj"
rm -rf "$PROJ"
mkdir -p "$PROJ"
cat > "$PROJ/pyproject.toml" << 'EOF'
[project]
name = "probe"
version = "0"
requires-python = ">=3.11,<3.12"
EOF
sandbox uv venv --directory "$PROJ" > /dev/null 2>&1
"$PROJ/.venv/bin/python" --version 2> /dev/null || echo "  (no venv built)"
