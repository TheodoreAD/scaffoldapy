---
status: landed
updated: 2026-08-23
---

## Context

`README.md` told you to run `copier update` from inside a generated repo "which keeps its own
`.copier-answers.yml`". It didn't, and couldn't: the template never rendered that file, and copier
does not write it on its own — `copier update` failed outright ("Cannot update because cannot obtain
old template references from `.copier-answers.yml`", verified against copier 9.17.1).
`copier update` is the entire reason Copier was chosen over Cookiecutter. Nothing had been generated
from the template yet, so no repo was stranded.

## Design (as landed, 2026-08-23)

1. `template/{{ _copier_conf.answers_file }}.jinja` renders the answers file. Not the stock
   `to_nice_yaml` idiom: pyyaml single-quotes values that need quoting (e.g. an all-digit `_commit`
   short hash), and the canonical dprint YAML config every generated repo pulls enforces double
   quotes — caught live by the e2e on hash `4276235`. Each scalar is JSON-encoded instead (a valid
   YAML subset, always double-quoted strings); rationale in the template file's own comment,
   regression-guarded by `test_answers_file_is_dprint_clean_whatever_the_commit_hash`.
2. `copier.yml`'s `_tasks` gained `when: "{{ _copier_operation == 'copy' }}"` guards: an update
   re-renders the template three times (old + new temp copies, plus the destination) with
   `_copier_operation` set to `update` throughout, so unguarded tasks would hit the network in
   throwaway temp dirs and skew the computed diff. Rationale in `copier.yml`'s comment.
3. `test_generates_valid_pyproject_and_config` asserts the answers file exists and records
   `_commit`/`_src_path`/the real answers, for every combination.
4. `test_copier_update_round_trip` renders from a committed tmp copy of the template, advances it,
   runs `copier.run_update`, and asserts the change lands — the test that would have caught all of
   this, satisfying item 3 of `plans/2026-08-23-e2e-coverage-holes.md`.
5. `README.md` now says `copier update --trust` — `--trust` is required because the template
   declares `_tasks` (copier's `_check_unsafe` flags them on update even when they're copy-only).

## Resolved questions

- The Jinja-expression filename coexists fine with the interface-conditional filename scheme and
  `_preserve_symlinks` — every combination renders and the round-trip passes.
- The whole answer set round-trips safely; nothing needed excluding from the recorded answers.
- No tag is needed: both sides of `run_update`'s downgrade guard resolve to dunamai dev versions
  (`0.0.0.postN.dev0+hash`), and `postN` grows with commit distance, so new > old compares
  correctly. Verified by the round-trip test, whose tmp template copy is untagged like this repo.

## Verification

Full suite green 2026-08-23 (`inv quality.precommit`: 37 passed, e2e's 10 combinations included).
