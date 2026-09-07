---
status: blocked on the globally installed repo-tasks predating runner.py
updated: 2026-09-08
source_repo: github.com-personal/repo-tasks
source_session: a3c12c26-55b9-4ed1-941f-42898b4bf565.jsonl
source_moment: 2026-09-05T21:17:08Z
---

# Every generated repo is born without report mode, and nothing says so

## Context

`repo-tasks` ships an agent output mode: with `REPO_TASKS_RUN_REPORT` set, every command run with
`echo=True` collapses to one delimited line, its output folded on success and replayed whole on
failure, and a gate ends with a verdict —

```
ruff check . | ok | 0.0s | All checks passed!
basedpyright | ok | 2.5s | 0 errors, 0 warnings, 0 notes
quality.precommit | PASS | 15 steps | 4.7s
```

`power-user-linux-setup`'s `[packages.claude-code]` exports that variable in every agent shell,
under the same `CLAUDECODE` guard that already carries `PIPE_FAIL`. So the population the mode
exists for has it switched on with nothing typed.

**The variable is not the whole switch.** `repo-tasks` installs the runner with
`ns.configure({"runners": {"local": ReportingLocal}})` on **its own** `ns`. A `tasks.py` that says
`from repo_tasks import ns` gets it; a `tasks.py` that hand-builds its own root `Collection` never
touches that object, so the variable is set, `repo_tasks.runner.enabled()` is true, and the gate
prints stock invoke output.

**This template generates the second kind.** Every repo it produces is therefore in that state at
birth, and the gap is silent in both directions: no warning, no probe, and no way to tell "the
variable is unset" from "the variable is set and unreachable" by reading the output.

> **Wrong, and this sentence is the whole reason the plan exists.** It generates the first kind. See
> "The premise is false" below; the paragraph is left standing because what it claims is what got
> checked.

`repo-tasks` shipped the consumer-side call on 2026-09-06:

```python
from repo_tasks import runner

runner.configure(namespace)  # returns False and touches nothing unless the env var is set
```

Its docstring, `contributing/quality-gate.md`'s "Turning it on in a consumer" and
`contributing/consumer-sweep.md` all carry it. **What is left is this repo's decision**, and only
this repo's: whether the generated `tasks.py` should carry that call.

## Evidence

Two sessions, in order.

1. `power-user-linux-setup`, session `25ea8788-b99d-43a2-9611-2d0c1f207694.jsonl`, around
   2026-09-05T18:20Z. The export was deployed and verified present in a fresh agent shell; a bare
   `inv quality.precommit` in that repo then printed stock invoke output — every command echoed,
   every line streamed, no verdict. Adding the wiring to that repo's own `tasks/__init__.py`
   produced `quality.check | PASS | 11 steps | 6.1s` immediately. That repo's plan file for the
   change had called the export "the whole change"; it was not.
2. `repo-tasks`, session `a3c12c26-55b9-4ed1-941f-42898b4bf565.jsonl`, 2026-09-05T21:17:08Z, which
   shipped `runner.configure` and filed this. Its plan
   `plans/2026-09-05-run-reporting-as-an-opt-in-agent-mode.md` §9 holds the design and names this
   repo in `depends_on`; the phrase to search for there is "`scaffoldapy`'s template is the
   multiplier".

**A repro that needs no generation run**: in any repo whose `tasks.py` builds its own `Collection`,
`REPO_TASKS_RUN_REPORT=1 inv quality.check` prints stock invoke output, and
`rg -n 'runner.configure' tasks/` returns nothing. Both are true of what this template generates
today.

## The premise is false, checked 2026-09-08

**This template does not generate a `tasks.py` that hand-builds a `Collection`.** It generates
exactly nine lines, three of which are the import:

```python
from repo_tasks import ns  # pyright: ignore[reportMissingImports, reportUnknownVariableType]

__all__ = ["ns"]
```

That is `template/tasks.py`, byte-identical to this repo's own root copy and guarded by
`tests/unit/test_repo_sync.py`. `repo_tasks/__init__.py` ends with `runner.configure(ns)`, so every
generated repo takes report mode with the object it imports, and the plan's third question — the one
it named as the only answer that removes the decision rather than making it — is answered by the
file that already exists. The first two questions never arise.

The plan was written from a repro run in `repo-tasks` and in `power-user-linux-setup`, both of which
**do** hand-build a root `Collection`. Neither is what this repo generates, and the "true of the
tool that found it, false of the tool that has to change" shape is one the family has recorded
before.

~~Should the generated `tasks.py` carry the call?~~ It cannot: there is no namespace of its own to
pass. ~~Unconditional or a copier question?~~ Moot. ~~Does it build its own Collection?~~ No.

## Recommended direction

Nothing to build in the template. What is left is one check, and it is worth stating plainly rather
than folding into a green result:

[UNVERIFIED: report mode has never actually been observed in a generated repo, and cannot be today —
the globally installed `repo-tasks` is v0.2.0, which ships no `runner.py` at all, so
`from repo_tasks import ns` currently imports a namespace with no reporting runner on it. The
mechanism above is read from the source of the `repo-tasks` checkout, not from a run. After the next
`inv repo-tasks.update`, `REPO_TASKS_RUN_REPORT=1 inv quality.check` in this repo — which imports
`ns` exactly the way a generated repo does — is the one-command check, and a rendered repo asserting
its own report-mode state is the e2e assertion this plan's third direction asked for. Neither is
worth doing before the tool moves.]

The `DEFERRED` below stands unchanged, and this outcome does not touch it.

[DEFERRED: nothing here measures whether report mode changes anything about how agent sessions read
a gate. The property it was built for — a piped `| tail -3` on a red run ending with the failing
command's name rather than with whatever the tool last printed — is already achieved and does not
depend on this. `power-user-linux-setup`'s `plans/2026-09-05-pipefail-in-the-agent-shell.md` owns
the rate measurement.]
