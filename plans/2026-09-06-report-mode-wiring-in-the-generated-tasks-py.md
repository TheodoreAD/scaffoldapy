---
status: idea
updated: 2026-09-06
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

## Open questions

- [NEEDS CLARIFICATION: should the generated `tasks.py` carry `runner.configure(namespace)` by
  default? **For**: this template is the only place that stops the population growing — one repo was
  noticed and fixed by hand, and the generator keeps producing more; a generated repo's owner has no
  reason to suspect the mode exists, so "documented" reaches nobody. **Against**: it puts an
  agent-oriented departure into every generated repo's `tasks.py`, where a human reader meets it
  first — which is the same rule-of-least-surprise objection that inverted `repo-tasks`' design in
  the first place (its own fold-by-default default was reverted for exactly this reason on
  2026-09-05, hours after landing).]

- [NEEDS CLARIFICATION: if yes, is it unconditional or a copier question? A question keeps the
  generated file honest for a repo whose owner does not want it, at the cost of one more prompt in a
  questionnaire that already has several — and `~/AGENTS.md`'s generator guidance is "minimal
  necessary prompts, skip what doesn't apply". Unconditional-with-a-comment is the cheaper shape if
  the answer to the first question is yes, since the call is a no-op when the variable is unset.]

- [NEEDS CLARIFICATION: does the generated `tasks.py` build its own `Collection` for a reason, or
  could it be `from repo_tasks import ns`? If the latter is viable the whole question dissolves —
  `ns` is configured at import and nothing needs generating. Worth answering first, because it is
  the only answer that removes the decision rather than making it.]

## Recommended direction

1. **Answer the third question first.** If the generated `tasks.py` hand-builds its Collection only
   to nest a couple of project-local tasks, `from repo_tasks import ns` plus
   `ns.add_collection(...)` may reach the same place with the configure already done. That is the
   outcome with no departure to justify to a human reader.
2. If it genuinely needs its own root Collection, take the first question deliberately rather than
   by default. Both sides are real and the trade is between a population that silently gets nothing
   and a line in every generated repo that a human meets before an agent does.
3. Either way, add the check to the e2e tier while it is in hand: this repo's integration tier is
   the only thing in the family that tests what the template generates, so a rendered repo asserting
   its own report-mode state is the only place that assertion can live.

[DEFERRED: nothing here measures whether report mode changes anything about how agent sessions read
a gate. The property it was built for — a piped `| tail -3` on a red run ending with the failing
command's name rather than with whatever the tool last printed — is already achieved and does not
depend on this. `power-user-linux-setup`'s `plans/2026-09-05-pipefail-in-the-agent-shell.md` owns
the rate measurement.]
