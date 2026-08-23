---
status: idea
updated: 2026-08-23
---

## Context

`README.md` tells you to run `copier update` from inside a generated repo "which keeps its own
`.copier-answers.yml`". It doesn't, and it can't: the template never renders that file.

Copier does not write the answers file on its own — the template has to contain
`{{ _copier_conf.answers_file }}.jinja`, whose body is `{{ _copier_answers|to_nice_yaml }}`. This
template has no such file, confirmed by rendering: `.copier-answers.yml` is absent from every
generated tree.

[PITFALL: without it `copier update` fails outright — `copier/_main.py`'s `run_update` raises
"Cannot update because cannot obtain old template references from `.copier-answers.yml`" (verified
against the installed copier 9.17.1). Not a degraded update, no update at all.]

This isn't a cosmetic gap. `copier update` is the entire reason Copier was chosen over Cookiecutter
in the first place — see `power-user-linux-setup/plans/2026-08-14-python-repo-scaffolding.md` §B,
"`copier update` applies template changes to an already-generated project; Cookiecutter has no
native equivalent." Every improvement made to this template since it was written has been
unreachable by any repo generated from it.

Nothing has been generated from the template yet, so no repo is stranded today. That window closes
the moment the first one is.

`run_update` has four more preconditions worth knowing before writing the fix, all from the same
function: the generated repo must be git-tracked and clean, the template must be git-tracked, and
_both_ sides must have a detectable version. This repo has no git tags, so its version currently
resolves to a dev string like `0.0.0.post24.dev0+40d5644`.

[UNVERIFIED: whether two such dev versions compare correctly through `run_update`'s
`subproject.template.version > self.template.version` downgrade guard. Tagging the template is the
obvious way to sidestep the question, and `repo-tasks` already ships `version.bump`/`gitflow` for it
— but no repo in the family has tagged anything yet, so this would be the first.]

## Open questions

- **Where the answers file goes.** It belongs inside `template/`, since `_subdirectory: template` is
  set — but its own name is a Jinja expression that renders to a dotfile.

  [NEEDS CLARIFICATION: does `template/{{ _copier_conf.answers_file }}.jinja` interact badly with
  the interface-conditional filename scheme already in use here, or with `_preserve_symlinks`?
  Nothing suggests it should; it just hasn't been tried.]

- **What to exclude from the recorded answers.** Copier records every answer by default.

  [NEEDS CLARIFICATION: is there anything in `copier.yml` that shouldn't be replayed on update, or
  does the whole answer set round-trip safely?]

- **Whether to tag the template.** See the `[UNVERIFIED:` note above.

  [NEEDS CLARIFICATION: does `copier update` behave correctly between two untagged dev versions, or
  does this force a first `v0.1.0` tag on `scaffoldapy` before updates work at all? Answerable in
  one experiment — render, commit, advance the template, update.]

## Recommended direction

1. Add `template/{{ _copier_conf.answers_file }}.jinja` containing
   `{{ _copier_answers|to_nice_yaml }}`.
2. Assert its presence in `test_generates_valid_pyproject_and_config`, alongside the existing
   file-tree assertions.
3. Write the actual round-trip test — render, `git init` + commit, advance the template, run
   `copier update`, assert it succeeds and the change lands. That test is the only thing that would
   have caught this, and it belongs with the rest of the e2e hardening in
   `plans/2026-08-23-e2e-coverage-holes.md`.
4. Fix `README.md`'s update instructions once they're true.
