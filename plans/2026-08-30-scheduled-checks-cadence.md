---
status: idea
updated: 2026-08-30
---

# Whether a generated repo wants the schedule repo-tasks refused

Filed from a `repo-tasks` session, 2026-08-30. It started life there collecting three of that repo's
own checks; the half that was about `repo-tasks` was decided and written into that repo's
`contributing/quality-gate.md` the same day, and what remained is entirely about what `scaffoldapy`
generates — so it comes here rather than lingering as a mostly-settled plan in the wrong repo.

## Context

Three things in `repo-tasks` share one shape: they answer a question whose answer changes without
any code changing, so they sit correctly outside `quality.check` — and nothing then runs them on a
cadence, so each can sit stale or red with a green terminal everywhere:

1. **`deps.audit`** — an advisory can land during a week with no pushes.
2. **The integration tier** — opt-in and run by nobody's commit. It sat red for an unknown length of
   time on a bad fixture, and while it was red it hid a second, unrelated failure behind it.
3. **`ci.check-actions` and `ci.status`** — both need someone to type them.

**`repo-tasks` settled its own half on 2026-08-30: no scheduled workflow.** The reasoning was that a
schedule surfaces staleness only to a reader, and that repo pushes straight to `main` and reviews no
PRs — so a red scheduled run there has no natural audience, and an unwatched scheduled job is worse
than a known gap because it looks like coverage. The answer there is `ci.status` as a deliberate
pre-push step, the other two run by hand when their subject changes, and the residual staleness
accepted rather than left pending.

## The question that is left

**That reasoning does not transfer, and this is the repo where it stops holding.** A repo generated
from these templates inherits the workflows and the gate, but not the social shape they were
reasoned about. A project with two contributors and a PR review habit **does** have a natural reader
for a red scheduled run, which is the exact premise the decision above turned on. So the answer may
legitimately invert per generated project, and nothing currently lets it.

## Open questions

[NEEDS CLARIFICATION: should `scaffoldapy` offer a scheduled audit workflow at all — as a copier
question, as a template a repo opts into later, or not at all? Against offering it: nothing ships
today, a generated repo can add a schedule in ten lines, and a question asked at generation time is
answered before the project has any idea whether it will have reviewers. For: the schedule is
exactly the thing nobody adds retroactively, and the concerns it covers (an advisory landing in a
quiet week, an action deprecating) are invisible until they bite.]

[NEEDS CLARIFICATION: does the integration tier run in CI at all? It needs a Docker daemon and pulls
`registry:3` plus a Debian base image. GitHub-hosted runners can do it, but it would be the first
thing in this family to need a daemon in CI and the cost is unmeasured. Only worth answering if the
question above says yes — measuring it otherwise is pricing something nobody intends to buy.]

## Recommended direction

Do nothing until there is a generated consumer that actually has reviewers. Until then the honest
answer is that `repo-tasks`' accepted risk is also every current consumer's, because every current
consumer has the same single-contributor shape — and a copier question added now would be asked of
nobody who could answer it usefully.

If it is ever built, the daemon question decides its scope: the two daemon-free checks
(`deps.audit`, `ci.check-actions`) are the cheap version and can ship without ever settling the
integration tier's cost.

Related, in `repo-tasks` rather than here: that repo's own push-triggered `deps.audit` step is a
separate and still-wanted design (`plans/2026-08-30-deps-audit-in-ci.md` there). It is a _trigger_,
not a schedule, so the decision above does not touch it — and whatever it settles about a red `main`
on an unfixable advisory is worth reading before offering the same shape to generated repos.
