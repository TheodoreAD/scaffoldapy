---
status: idea
updated: 2026-09-08
---

# A template fix reaches nobody who already generated

## Context

Split out of the now-retired `plans/2026-08-29-action-version-drift.md` when that landed, because it
was never an action-pin question and kept a finished piece of work looking open. Both that plan and
the 2026-08-27 one it merged raised it; the earlier said outright that it "may deserve its own
plan". `plans.py archive --file 2026-08-29-action-version-drift.md` reads either back.

Every fix made here reaches only repos generated after it. An existing generated repo picks it up
through `copier update` and through nothing else — and nothing prompts anyone to run one. The
generated `.copier-answers.yml` makes an update mechanically possible (`_commit`, `_src_path`, the
answers actually used, all asserted by `tests/unit/test_template.py`), which is the half that is
already solved.

Three fixes in the last fortnight each grew the gap, and they are different enough to show the
shape:

- **The action bump, 2026-09-07.** `ci.yml` is byte-identical between this repo's root and the
  template, and a generated repo's copy is byte-identical too until this repo changes. `ingesta`
  re-established that identity on 2026-08-29 and lost it again eight days later without anything
  happening in that repo.
- **The security workflow, 2026-09-07.** A whole file that did not exist before, so an existing repo
  is not diverged — it is simply missing a check it would want.
- **A generated repo's `AGENTS.md`,** which an owner may have edited. The one class where an update
  genuinely conflicts rather than fast-forwarding.

## Open questions

[NEEDS CLARIFICATION: is this a `copier update` story or a per-file one? `copier update` is the
supported mechanism and handles all three classes above, at the cost of re-running the whole
questionnaire and producing conflicts in files the owner has since edited. A per-file "copy this one
line across" is what has actually happened so far, by hand, and it does not scale past a handful of
repos or past a change nobody remembers to propagate.]

[NEEDS CLARIFICATION: what does the noticing? A generated repo has no idea it is behind, and this
repo has no list of its output — there is no registry of generated repos anywhere, deliberately.
Options, none evaluated: the generated `AGENTS.md` telling an agent to check periodically; a
`repo-tasks` task comparing `.copier-answers.yml`'s `_commit` against the template's current `HEAD`
(the same shape as `ci.check-actions`, which reports rather than edits, and would reach every
consumer through the tool rather than through a file this template stamps); or accepting that the
owner is the trigger and saying so.]

[NEEDS CLARIFICATION: is "byte-identical with the template" a claim worth keeping in a generated
repo at all? `tests/unit/test_repo_sync.py` enforces it between this repo's root and `template/`,
which is real and checkable. The same sentence about a _generated_ repo is true only until the next
template commit, so a generated `ci.yml` carrying a comment implying it stays in step would be
another instance of the class of stale comment the action bump had to fix.]

## Recommended direction

Answer the second question first, because it decides whether the first one matters. A mechanism
nobody is prompted to run is the state today, and adding a better mechanism without a trigger just
moves where the not-happening happens.

The cheapest honest shape, if nothing gets built: say in the generated `AGENTS.md` that the repo was
generated from a template that keeps moving, name `copier update` as how to take the changes, and
state that nothing will remind them. That is a sentence, and it is strictly better than the current
silence — but it should be chosen deliberately rather than because it is cheap, since it accepts the
gap rather than closing it.
