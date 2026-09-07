# Agent instructions

Cross-tool instructions for AI coding agents working in this repo. Universal conventions (sudo/ssh
askpass, Bash/allowlist discipline, cross-session memory policy) live in `~/AGENTS.md` — no need to
repeat them here, only what's specific to this repo.

## Build & test

- `inv dev-env.setup` once after cloning — creates `.venv`, activates it via direnv, and wires
  Claude Code's Bash tool to pick it up too.
- `inv quality.precommit` before considering a change done — fixes what's auto-fixable, then runs
  the full check gate.
- `pytest` — tests live in `tests/unit/`, the tier the quality gate runs.

Two workflows report on a push, and they fail for different reasons. `CI` runs the gate above.
`Security` runs a dependency audit against the OSV database and nothing else, so a red one means a
known advisory against something in `uv.lock`, not a defect in this repo's code — the fix is a
version bump, and there is no suppression list. It is push-triggered, so an advisory published
during a quiet week is not seen until the next push.

## Conventions

<!-- code style, architecture notes, anything an agent should know before making changes -->
