---
status: idea
updated: 2026-09-18
source_repo: github.com-personal/repo-tasks
source_session: 14237e4b-3a66-4207-8a3a-882552c86680.jsonl
source_moment: 2026-09-18T09:40:00Z
source_plan: plans/2026-08-29-python-floor-in-the-shipped-configs.md
---

# Python version tiers: the rules, and what the template has to generate

## Context

The household rule has been stated three times — 2026-08-29, 2026-09-13, 2026-09-18 — and enforced
by nothing. The third statement asked for the exercise this file is: **categories and decisions for
every use case**, settled rather than restated.

The rule as given, 2026-09-18:

> for libraries, or things that may have to arrive in users' venvs, we stay with 3.11, pinned,
> matrix tested if deemed necessary up to 3.14. for applications that we deploy, like ingesta, we
> use 3.14, pinned.

and the constraint that decides the hard case:

> we need users to be able to use our skills without uv or any special system setup. we expect them
> to have at least python 3.11, that is the basic requirement, otherwise the toml configs fall
> apart.

This file belongs here because the answers are **generation-time** answers. Which tier a project is
in is chosen when it is created, and it fans out to `requires-python`, `.python-version`, the CI
matrix and the dev venv. `repo-tasks` reads the result (`configs.pull` derives `pythonVersion` from
`requires-python`) and has no opinion about which tier a repo is in — that split was settled
2026-08-30 and is unchanged.

## The axis

Not "library or application". **What stands between the code and the interpreter**, which is the
question with a mechanical answer:

| what stands between              | who picks the interpreter      | what a floor declaration does |
| -------------------------------- | ------------------------------ | ----------------------------- |
| our own resolver, at deploy time | us                             | pins one version              |
| the consumer's resolver          | them, bounded by our floor     | binds                         |
| their `uv tool install`          | their uv, bounded by our floor | binds                         |
| **nothing — ambient `python3`**  | **the caller's PATH**          | **nothing exists to declare** |

Rows two and three collapse: `uv tool install` reads `requires-python` like any resolver, so an MCP
server is a library for this purpose and needs no special case. Verified rather than assumed —
`olx-polite-mcp` declares `requires-python = ">=3.11"` with a `[project.scripts]` entry point, which
is exactly the shape uv resolves against.

Row four is the only genuinely different one, and it is where the skills live.

## The categories, and the decision for each

| tier                      | examples                                | `requires-python` | `.python-version` | dev venv | CI matrix                |
| ------------------------- | --------------------------------------- | ----------------- | ----------------- | -------- | ------------------------ |
| **Library / shared dep**  | `repo-tasks`, `invoke-stubs`            | `>=3.11`          | `3.11`            | 3.11     | 3.11 → 3.14 if warranted |
| **Installed tool**        | the three `*-polite-mcp` servers        | `>=3.11`          | `3.11`            | 3.11     | 3.11 → 3.14 if warranted |
| **Ambient-artifact repo** | `agent-skills`                          | `>=3.11`          | `3.11`            | 3.11     | 3.11 → 3.14 if warranted |
| **Deployed application**  | `ingesta`                               | `>=3.14`          | `3.14`            | 3.14     | 3.14 only                |
| **Local tooling**         | `scaffoldapy`, `power-user-linux-setup` | `>=3.14`          | `3.14`            | 3.14     | 3.14 only                |

[DECISION: **`repo-tasks` is a library, not a local tool, and the reason is worth keeping.**
Resolved by the user 2026-09-18: it can run as a user-wide `uv tool` install _and_ be installed into
a project's own venv — `invoke-stubs` and `power-user-linux-setup` both take it as a dependency — so
compatibility has to be maintained for the second case even though the first is how it is usually
reached. A repo that is usually a tool but can be a dependency is a dependency.]

[DECISION: **`agent-skills` is 3.11, and it is its own category rather than an exception.** Its
shipped artifacts are scripts run by a consumer's ambient `python3`, so the floor is a property of
the artifact rather than of the repo. Developing at that floor makes the ordinary `pytest` run the
floor check, with nothing separate to keep alive. Stated as a rule so the next repo of this shape
inherits it: **a repo whose shipped artifacts run on an interpreter it does not choose develops at
those artifacts' floor.**]

[DECISION: **`scaffoldapy` and `power-user-linux-setup` are 3.14.** Nothing resolves either into
anyone's environment. But the tier of a repo and the tier of **what it emits** are different
questions, and `scaffoldapy` is where that distinction is load-bearing: its own tree may be 3.14
while the repos it generates must be tiered per the table above. `power-user-linux-setup` currently
declares `>=3.11` and pins `3.14`, which is the one outright contradiction in the family; its
declaration is the half that is wrong.]

## What the template has to do

1. **Ask which tier**, at generation, and fan the answer out to `requires-python`,
   `.python-version`, the generated CI matrix and the first `uv sync`. One answer, four files —
   which is the whole reason this is a generation question and not a per-file one.
2. **Emit `.python-version` always.** Six of nine repos in the family have none, and a repo without
   one has nothing to state its intent to a human or to uv.
3. **Match the CI matrix to the tier.** Library/tool/ambient tiers run the floor plus whatever upper
   versions are warranted; the application tier runs one version, because a matrix over interpreters
   nobody deploys is cost without a question behind it.

[PITFALL: **the generated repo's tier is not the generator's tier**, and the template is the one
place both are in scope at once. A generation run that inherits `scaffoldapy`'s own 3.14 into a
library-tier repo produces a package that fails to install for every 3.11 consumer, and nothing in
that repo would ever say so — its own CI would be green on 3.14.]

## Skills: the category with no resolver

**The rules, all four load-bearing:**

1. **Floor 3.11**, because `tomllib` is stdlib from 3.11 and the skills read TOML. Stated by the
   user as the basic requirement; 3.11 is old enough that it costs adopters little.
2. **Standard library only.** No third-party imports, and **no `uv` requirement** — a consumer must
   be able to run a skill with nothing but a Python interpreter. This is what rules out the
   otherwise-obvious mechanism; see the decision below.
3. **A version guard at the top of every script**, before any 3.11-only import, failing with a
   sentence that names the requirement.
4. **The repo develops at the floor**, so the ordinary test run is the check.

[DECISION: **PEP 723 inline metadata plus `uv run` is rejected, on the requirement rather than on
the mechanics.** It is the natural answer — it inserts a resolver where there is none, declaring
`requires-python` in the script itself — and it measures well: 26ms warm, and it picks correctly
once nothing overrides it. It is rejected because it makes `uv` a hard requirement for every skill
invocation, and the user's constraint is that skills work "without uv or any special system setup".

Two further findings make the rejection easy rather than reluctant. **`UV_PYTHON` overrides a
script's own declaration**, so the guarantee is void on exactly the machine that sets it — measured
2026-09-13 on uv 0.11.19, a script declaring `==3.11.*` ran on 3.14.5 with uv printing
`warning: The requested interpreter resolved to Python 3.14.5, which is incompatible with the
script's Python requirement`
and proceeding. And a harness that "cooks up" an environment is precisely where uv is least likely
to be present.]

[PITFALL: **the floor is currently undeclared, unenforced and already inconsistent.** Measured
2026-09-18 across the twelve scripts in `agent-skills`: all twelve compile under 3.9, and two —
`plan-docs/scripts/plans.py` and `session-harvest/scripts/harvest.py` — carry an unguarded
`import tomllib`, so they die on 3.10 with `ModuleNotFoundError: No module named 'tomllib'`. Run,
not inferred. A consumer on 3.10 gets that traceback mid-task, and it does not mention 3.11, which
is what rule 3 above exists to fix.]

[PITFALL: **`python3` is not one interpreter, and the variance is invisible.** It resolves to the
active venv's interpreter before the distro's. Measured in one session on one machine on one day:
3.11.15 inside `repo-tasks`, 3.14.5 in any other personal repo, 3.12.3 with no venv active. The same
skill script therefore ran on two different interpreters an hour apart during the session that wrote
this file. Nothing reports it.]

## The machine-level precondition

None of the above binds on this machine while `UV_PYTHON=3.14` is exported — it outranks
`.python-version`, a project's `requires-python`, and a script's own PEP 723 declaration. Owned by
`power-user-linux-setup` and filed there as `2026-09-13-uv-python-defeats-every-library-floor.md`;
the replacement is `uv python pin --global`, which was measured to keep the 3.14 default for
everything unconstrained while yielding to every declared floor. It is a precondition rather than a
companion task: adopting the table above without it produces repos that declare a floor the dev
machine ignores.

## Recommended direction

1. **The machine-level fix first**, since nothing else binds until it lands.
2. **The template's tier question**, which is this file's own subject and the thing that stops the
   problem recurring in repos that do not exist yet.
3. **The per-repo straightening**, filed separately for each: `agent-skills`, `invoke-stubs`, the
   three `*-polite-mcp` servers, `ingesta`, and this repo. `repo-tasks` is already correct as of
   2026-09-13 and is the worked example of what "correct" looks like.

[UNVERIFIED: that a 3.11 venv is even resolvable in the six repos that would move to one. It was in
`repo-tasks` — full gate green on 3.11.15, 691 tests — but that repo has been type-checking at its
floor since 2026-08-30. A repo that has never had anything run at 3.11 is where the
`typing.override` class of finding lives, and turning some up is the expected outcome of the sweep
rather than a reason to stop it.]

## Attachments

- `pep723-probe.sh` — committed, 1 KB, attached 2026-09-18
- `replacement-probe.sh` — committed, 2 KB, attached 2026-09-18
- `uv-native-default.sh` — committed, 2 KB, attached 2026-09-18
- `tool-install-clash.sh` — committed, 2 KB, attached 2026-09-18
- `floor-audit.py` — committed, 2 KB, attached 2026-09-18
