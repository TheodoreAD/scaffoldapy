---
status: idea
updated: 2026-08-23
---

# Cover the `library` interface in the e2e `quality.check` test

## Context

`tests/test_template.py::test_generated_repo_passes_quality_check_out_of_the_box` renders a real
generated project (no `skip_tasks`) and asserts `inv quality.check` exits 0 — the one test that
would catch a bug like the dprint markdown-wrap or `orchestrator.py` `contextlib.suppress`/
`async with` bugs fixed 2026-08-23 (see the now-retired
`plans/2026-08-23-template-content-bugs.md`, no longer present). It's parametrized over every
`COMBINATIONS` entry except `library`: the `library` interface generates zero test files, so
`pytest` itself exits nonzero (no tests collected) inside the generated repo's own
`inv quality.check` — a failure unrelated to what this test is actually checking, so `library` is
skipped rather than producing a permanently-red, uninformative test.

This means `library`-specific template content (its `pyproject.toml.jinja`, `README.md.jinja`
branch, whatever else varies for that interface) currently has no e2e coverage at all — only the
faster `skip_tasks=True` structural tests (`test_library_seeds_nothing_but_the_bare_package`, etc.)
touch it.

## Open questions

- [NEEDS CLARIFICATION: does the `library` interface generate a package worth having *any* test
  for, or is "zero test files" itself the right output for a pure library template — in which case
  the fix belongs in the test's assertion (special-case success on pytest's "no tests collected"
  exit code for this one interface), not in the template?]
- [NEEDS CLARIFICATION: alternatively, should the `library` interface seed a trivial smoke test
  (e.g. `test_import.py` asserting the package imports) so pytest has something to collect —
  changing generated output instead of the test?]

## Recommended direction

Leaning toward the assertion-side fix (special-case the `library` combo's expected `pytest` exit
code inside the e2e test) over seeding a placeholder test file into every generated `library`
project — a synthetic `test_import.py` a user didn't ask for is noise in their repo, whereas the
test's own exclusion logic is already there for the `library` combo and knows why. Not scoped
further than that; worth a second look before promoting to `planned`.
