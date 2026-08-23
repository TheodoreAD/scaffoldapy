---
status: idea
updated: 2026-08-23
---

## Context

`AGENTS.md` already states the rule that matters here: never exclude a combination from the e2e test
to make it pass, because `test_generated_repo_passes_quality_check_out_of_the_box` is the only test
that catches template _content_ bugs, and only for combinations it actually runs. A 2026-08-23
review found three things that rule doesn't yet cover.

### 1. `browser_session` × `multi_source` generates code that cannot import

`sources/base.py` does `from {{ package_name }}.core.fetch import PoliteFetcher` and calls
`self._fetcher.get(url)`. But `core/fetch.py` renders only when `fetch_strategy == "http"` — with
`browser_session` the package gets `core/fetch_browser.py`, whose class is `PoliteBrowserFetcher`
and whose method is `fetch()`, not `get()`.

Confirmed by rendering that combination: no `core/fetch.py` in the tree, while `sources/base.py`
imports it. `copier.yml` asks `multi_source` whenever `fetch_strategy != 'none'`, so this is a
combination a real person can pick from the prompts today.

`COMBINATIONS` has `mcp_server-browser-session` with `multi_source: False`, and
`mcp_server-http-multi-source` with `fetch_strategy: http` — the two axes are each covered, their
intersection isn't.

[PITFALL: covering each axis value once is not the same as covering the combinations. Both existing
entries pass; the bug lives only where they cross.]

### 2. Generated markdown wrapping depends on `package_name` length

`dprint` reflows markdown at 100 columns, and `quality.check` verifies it. Any template prose
containing `{{ package_name }}` mid-paragraph is only known to be dprint-clean for the one name the
tests use — `example_pkg`, 11 characters. A longer package name shifts the wrap and can push the
rendered file out of dprint-clean shape, failing the generated repo's very first CI run.

Known live instance: `README.md.jinja`'s Chrome-session bullet interpolates `{{ package_name }}`
into `--user-data-dir=~/.cache/{{ package_name }}-chrome` mid-line. The seeded `SKILL.md` had the
same shape until `28df7e5` restructured it so paths sit on their own lines.

This is a whole class of bug, not one instance, and one test parameter closes it.

### 3. The `copier update` round-trip is untested

Because it's currently impossible — see `plans/2026-08-23-copier-update-is-impossible.md`, which has
to land first. Once it does, the round-trip test is what stops it regressing.

## Decisions already taken

[DECISION: harden the existing `tmp_path`-based e2e first, rather than moving generation into a
container. The temp-dir tests already catch real template bugs and need no new infrastructure; the
holes above are all closable with parametrization. Chosen over a container-backed tier on
2026-08-23.]

## Open questions

- **How to parametrize the long name.** Adding a second `package_name` doubles the e2e matrix, and
  each entry pays for a real `uv sync` over the network.

  [NEEDS CLARIFICATION: run the long name against every combination, or pick the one or two
  combinations whose templates actually interpolate `package_name` into wrapped prose (the
  `browser_session` README, the `skill` SKILL.md) and cover it there only? The second keeps the
  matrix affordable but relies on knowing which templates interpolate — which drifts.]

- **How long is long enough.** The wrap only breaks past some threshold that depends on the
  surrounding sentence.

  [NEEDS CLARIFICATION: is there a principled maximum (a real package name from the family, e.g.
  `product_research_pipeline` at 25 characters), or should the test use a deliberately absurd name
  to catch the whole class?]

- **How to fix the `browser_session` × `multi_source` crossing.** Two shapes, not obviously equal.

  [NEEDS CLARIFICATION: give both fetchers a common `get()` method so `sources/base.py` works
  against either (smallest diff, but renames `PoliteBrowserFetcher.fetch` and slightly obscures that
  a CDP fetch is not an HTTP GET), or introduce a small `Fetcher` protocol in `core/` that both
  implement and `base.py` depends on (more explicit, more files in a template that deliberately
  seeds few)?]

## Recommended direction

In order, since each step's failure teaches something about the next:

1. Add the `browser_session` × `multi_source` entry to `COMBINATIONS` and watch it fail — that
   failure is the specification for the fix.
2. Fix the template, per whichever shape the open question above resolves to.
3. Add the long-`package_name` case, fix whatever wrapping it breaks, and record the rule that
   avoids the class: keep code spans and paths out of the middle of wrapped prose in any templated
   markdown.
4. After `plans/2026-08-23-copier-update-is-impossible.md` lands, add the render → `git init` →
   advance template → `copier update` round-trip.

[DEFERRED: a container-backed e2e tier, so generation no longer depends on this machine's global
`repo-tasks` install, `direnv`, or an inherited `PATH` — closer to what a generated repo's real CI
runner sees. Deliberately not now (see the DECISION above); revisit if a bug ever slips through that
the temp-dir tier structurally could not have caught. `repo-tasks`' own `tests/integration/` plus
`pytest.ini`'s `--ignore` is the shape to copy if it happens.]
