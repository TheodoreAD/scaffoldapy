# Agent instructions

Cross-tool instructions for AI coding agents working in this repo. Universal conventions (sudo/ssh
askpass, Bash/allowlist discipline, cross-session memory policy) live in `~/AGENTS.md` — no need to
repeat them here, only what's specific to this repo.

## Build & test

- `inv dev-env.setup` once after cloning — creates `.venv`, activates it via direnv, and wires
  Claude Code's Bash tool to pick it up too.
- `inv quality.precommit` before considering a change done — fixes what's auto-fixable, then runs
  the full check gate.
- `pytest` — tests live in `tests/`.

## Conventions

<!-- code style, architecture notes, anything an agent should know before making changes -->
