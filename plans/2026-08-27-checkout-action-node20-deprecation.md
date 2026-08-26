---
status: idea
updated: 2026-08-27
---

# `actions/checkout@v4` Node 20 deprecation

## Context

Surfaced 2026-08-26 by the first CI run of a freshly generated repo. The run passed, with an
annotation:

> Node.js 20 is deprecated. The following actions target Node.js 20 but are being forced to run on
> Node.js 24: `actions/checkout@v4`.

GitHub is currently forcing these onto Node 24 rather than failing them, so this is a warning and
not a break. It will stop being a warning.

The pin sits at line 12 of both `.github/workflows/ci.yml` and `template/.github/workflows/ci.yml`.
Those two files are byte-identical by design and `tests/unit/test_repo_sync.py` fails if they
diverge, so this is one change applied to both, not a choice about which to fix.

The reason it is worth a plan rather than a drive-by edit: every repo generated from this template
carries the pin, and each one only picks up a fix through a deliberate `copier update`. The blast
radius is every generated repo's CI, and the annotation is easy to keep not-noticing precisely
because the run is green.

## Recommended direction

Bump both pins to the current major of `actions/checkout` and let `inv test.all` render and run the
integration tier, which exercises a real generated repo's own gate. Check whether
`astral-sh/setup-uv` carries the same annotation in the same run before deciding this is a
one-action change.

Worth deciding at the same time, since it is the same question one layer up: whether action pins
should be maintained by hand at all, or whether this repo should take Dependabot or Renovate for its
workflow files so the next runtime deprecation arrives as a pull request instead of as an annotation
somebody happens to read.

## Open questions

[NEEDS CLARIFICATION: Whether generated repos should be told about the update. A fix here reaches
only repos that later run `copier update`, and nothing currently prompts them to. That is a general
property of this template's relationship to its output, not specific to this bump, and it may
deserve its own plan.]
