---
status: idea
updated: 2026-09-02
source_repo: github.com-personal/power-user-linux-setup
source_session: 361b5d16-284b-4286-8233-45c011924707.jsonl
source_moment: 2026-09-02T15:35:11+03:00
---

# Should a generated repo's AGENTS.md require a commit body?

## Context

`~/AGENTS.md` gained a rule on 2026-09-02: **every commit has a body, and the body says why.** It
lives in `power-user-linux-setup`'s `config/agents-md/git.md`, extending
`### Committing multi-part work`, and reaches every agent session on that machine.

The question this plan exists for is whether `scaffoldapy` should stamp the same rule into the
`AGENTS.md` it generates. It is genuinely open, because **the argument that justifies the rule is
partly a property of one machine and partly not**:

- **Transfers.** An agent arriving at a commit has no memory of the change. The log is not a
  supplement to its recollection, it is the whole of its access. That is true of any agent in any
  repo.
- **Does not transfer.** On the authoring machine, parallel sessions share one working tree, so
  checking out an old commit to understand it moves a tree somebody else is working in — which makes
  `git log` and `git show` the only safe reads and the body the _only_ channel rather than the
  convenient one. A generated repo's contributors have their own clones and can check out freely.

So the rule's premise survives the move but its strongest supporting argument does not, and a rule
stamped into somebody else's repo is a rule they did not choose. Worth deciding deliberately rather
than by copying.

The related half is already settled and should not be re-litigated here: **nothing enforces it.** No
`commit-msg` hook, on the standing principle that agents get the same standard as developers —
taught, not silently corrected. A generated repo inherits that reasoning whether or not it inherits
the rule.

## Evidence

- Transcript:
  `~/.claude/projects/-home-tdumitrescu-projects-github-com-personal-power-user-linux-setup/361b5d16-284b-4286-8233-45c011924707.jsonl`,
  turn at `2026-09-02T15:35:11+03:00`. The phrase to search for is the user's own: **"weren't we
  supposed to have a commit description?"** — asked on a commit that had gone out with a subject
  line and nothing else.
- The originating plan is `plans/2026-09-01-every-commit-carries-a-why.md` in
  `power-user-linux-setup`, which carries the full argument, the measured failure shape (17 commits,
  15 with real bodies, 2 with only a `Co-Authored-By:` trailer) and the two guards.
- The exact wording that landed is in that repo's `config/agents-md/git.md` under
  `### Committing multi-part work`. Read it there rather than from this summary; it is the artifact,
  and it may have moved on.
- The repro is not a bug. It is: generate a repo, read its `AGENTS.md`, and ask whether a
  contributor who has never seen the authoring machine's `~/AGENTS.md` is told to write commit
  bodies. Today they are not.

## Open questions

[NEEDS CLARIFICATION: whether the rule belongs in the generated `AGENTS.md` at all, or whether it is
a personal-machine convention that generated repos should stay neutral on. A generated repo may go
to contributors with their own conventions, and `scaffoldapy` stamping an opinion about commit prose
is a different kind of claim than stamping a tool configuration.]

[NEEDS CLARIFICATION: if adopted, whether it is stamped in full or trimmed. The full version carries
two clauses that are specific to the authoring machine — the shared-working-tree argument, and the
plans-store exception naming `<repo>: <what it is>`. A generated repo has neither, so a verbatim
copy would ship reasoning that is false there, which is worse than shipping nothing.]

[NEEDS CLARIFICATION: whether the trailer trap needs restating for a repo that may use different
trailers. The guard is that `Co-Authored-By:` alone satisfies `%b`, so any check written against
this rule has to strip trailers first. That generalises to whatever trailers a consumer repo uses,
and is the half most likely to be dropped as machine-specific detail when it is the half that is
not.]

## Recommended direction

Decide the first question before touching the template. If the answer is yes, stamp a **trimmed**
version: the premise (an agent's only access to a change is the log), the floor-not-ceremony guard,
and the trailer trap — dropping the shared-working-tree argument and the plans-store exception, both
of which are true only on the authoring machine.

Filed rather than performed: writing into another repo is out, and this wants a session that belongs
to `scaffoldapy` and can run its own gate and e2e tier against a regenerated fixture.
