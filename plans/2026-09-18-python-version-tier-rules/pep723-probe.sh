#!/usr/bin/env bash
# Can a standalone script pin its own interpreter, and does the machine-wide UV_PYTHON defeat that
# the way it defeats .python-version? The second question is the one that matters: if it does, PEP
# 723 is no better than the pin we already found to be worthless.
set -uo pipefail

DIR="$(dirname "$0")/pep723"
rm -rf "$DIR"
mkdir -p "$DIR"

write_script() { # write_script <file> <requires-python>
  cat > "$1" << EOF
# /// script
# requires-python = "$2"
# ///
import sys

print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
EOF
}

write_script "$DIR/floor.py" ">=3.11"
write_script "$DIR/exact.py" "==3.11.*"
write_script "$DIR/high.py" ">=3.14"

echo "UV_PYTHON in this shell: ${UV_PYTHON:-<unset>}"
echo

printf '%-34s %-22s %s\n' "script requires-python" "UV_PYTHON" "interpreter uv chose"
for spec in "floor.py:>=3.11" "exact.py:==3.11.*" "high.py:>=3.14"; do
  file="${spec%%:*}"
  req="${spec#*:}"
  with=$(cd "$DIR" && UV_PYTHON=3.14 uv run --no-project "$file" 2>&1 | tail -1)
  without=$(cd "$DIR" && env -u UV_PYTHON uv run --no-project "$file" 2>&1 | tail -1)
  printf '%-34s %-22s %s\n' "$req" "3.14 (as exported)" "$with"
  printf '%-34s %-22s %s\n' "" "unset" "$without"
done

echo
echo "warm-run cost, floor.py, UV_PYTHON as exported:"
cd "$DIR" && time (for _ in 1 2 3; do uv run --no-project floor.py > /dev/null; done)
