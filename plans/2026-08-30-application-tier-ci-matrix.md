---
status: idea
updated: 2026-08-30
---

# Does an application-tier repo get the same Python matrix as a library-tier one?

## Context

Filed from `repo-tasks` on 2026-08-30, where it surfaced as an open question in
`plans/2026-08-29-python-floor-in-the-shipped-configs.md` and was rehomed here because it is a
template question rather than a `repo-tasks` one — nothing in `repo-tasks` should grow its own
notion of which tier a repo is in.

The household rule, as restated 2026-08-29:

> **3.11 is the floor** for `repo-tasks`, for libraries, and for anything other people may need to
> run on their own machines — skills and MCP servers included. **Applications start on 3.14.**

`repo-tasks`' own CI runs a four-version unit matrix, verified in its `ci.yml` on 2026-08-30:

```yaml
python-version: ["3.11", "3.12", "3.13", "3.14"]
```

Its stated purpose is to make `requires-python = ">=3.11"` true rather than aspirational — the
matrix is what proves the declared floor is real. That reasoning is sound for a library, whose
consumers genuinely install it on any of those four.

An application controls its own runtime. It declares 3.14, deploys 3.14, and every entry below the
top one is testing a configuration that will never exist. So the same template producing both tiers
has to decide what each gets, and the question was never asked when the matrix was written — it was
written for a library and inherited by anything generated from the same shape.

## Open questions

- [NEEDS CLARIFICATION: does an application-tier generated repo get a single-version CI matrix, or
  keep the range? The cost of keeping it is four jobs proving something nobody needs, on every push,
  forever. The cost of dropping it is that a repo which later reclassifies as a library has a matrix
  to reintroduce, and nothing to notice it should.]

- [NEEDS CLARIFICATION: whichever way it goes, the answer has to agree with what `repo-tasks`'
  `configs.pull` now derives. Since `c514bd9` a consumer's `pyrightconfig.json` gets a
  `pythonVersion` derived from its own `requires-python`, and its `ruff.toml` carries no
  `target-version` at all (`949607c`) so ruff infers the same floor from the same field. Static
  analysis therefore already checks against the declared floor, one value, however many interpreters
  the tests run on — a decision taken deliberately in `repo-tasks` and not something the template
  should contradict. If the matrix and the derived floor disagree about what the repo supports, the
  generated repo has two answers to one question.]

- [NEEDS CLARIFICATION: is the tier a generation-time question with one answer, or does a repo
  change tier later? `repo-tasks`' floor plan assumed the former — "leave the tier question itself
  to `scaffoldapy`, a generation-time answer that fans out to `requires-python` and CI". If a repo
  can move between tiers, then `requires-python` is the single field both the matrix and the derived
  configs should follow, and the tier is not stored anywhere at all.]

## Recommended direction

Rough, and deliberately not prescriptive — the owning decisions are this repo's.

The cheapest shape consistent with what `repo-tasks` already landed is to make `requires-python` the
only declaration and derive the matrix from it, the same way the shipped `ruff.toml` and
`pyrightconfig.json` now derive their floors. A repo declaring `>=3.14` then gets a one-entry matrix
without anyone choosing one, and a repo declaring `>=3.11` gets the range, with no tier flag stored
and nothing to keep in sync.

Worth checking against the e2e tier before believing it: that tier renders every combination and
runs the generated repo's own gate, so a matrix change is verifiable there rather than by
inspection.
