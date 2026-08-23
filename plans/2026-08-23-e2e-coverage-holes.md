---
status: blocked on plans/2026-08-23-copier-update-is-impossible.md landing
updated: 2026-08-23
---

## Context

`AGENTS.md` already states the rule that matters here: never exclude a combination from the e2e test
to make it pass, because `test_generated_repo_passes_quality_check_out_of_the_box` is the only test
that catches template _content_ bugs, and only for combinations it actually runs. A 2026-08-23
review found three things that rule doesn't yet cover. Items 1 and 2 landed the same day; the whole
plan now waits on item 3's prerequisite.

### 1. `browser_session` × `multi_source` generated code that couldn't import — FIXED

`sources/base.py` imported `core.fetch`'s `PoliteFetcher`, which only renders when
`fetch_strategy == "http"`. Landed as: a structural `Fetcher` protocol defined in `base.py` itself,
plus a `mcp_server-browser-multi-source` entry in `COMBINATIONS` that failed before the fix and
passes after.

[DECISION: fixed via a `typing.Protocol` inside `sources/base.py` (method `fetch(url: str) -> str`),
renaming `PoliteFetcher.get` to `fetch`, rather than a conditional Jinja import of whichever
concrete fetcher was generated. The protocol removes the cross-conditional import entirely — the
failure mode becomes structurally impossible instead of merely covered — costs no new seeded file,
and renaming the http fetcher's `get` (instead of the browser fetcher's `fetch`) avoids implying a
CDP page render is an HTTP GET. `PoliteBrowserFetcher.fetch` already matched.]

[PITFALL: covering each axis value once is not the same as covering the combinations. Both
pre-existing entries passed; the bug lived only where they crossed. Now also recorded in AGENTS.md's
e2e section.]

### 2. Generated markdown wrapping depended on `package_name` length — FIXED

dprint reflows generated markdown at 100 columns; prose interpolating `{{ package_name }}` mid-line
was only known dprint-clean for `example_pkg` (11 chars). Landed as: two long-name `COMBINATIONS`
entries (`mcp_server-browser-session-long-name`, `skill-long-name`) rendering with
`product_research_pipeline` (25 chars), which caught `README.md.jinja`'s Chrome-session bullet
exactly as predicted; the bullet's command moved into a fenced code block and the other
interpolation became "this package". Rule recorded in AGENTS.md ("Keep `{{ package_name }}` out of
mid-line wrapped prose in templated markdown").

[DECISION: long-name coverage targets the two combinations whose markdown interpolates
`package_name` into wrapped prose today, not the whole matrix — each e2e entry pays for a real
`uv sync`, and doubling all of them buys nothing for combinations whose markdown doesn't
interpolate. The drift risk ("which templates interpolate" changes over time) is carried by the
AGENTS.md rule plus the crossing lesson above, not by brute-forcing the matrix.]

[DECISION: the long name is `product_research_pipeline` — the family's longest real package name —
rather than an invented absurd one. It's the principled realistic maximum, and it caught the known
live instance; an absurd name would also break the rendered artifacts in ways no real generation
hits.]

Alongside these, the suite's render machinery moved into `tests/conftest.py` — a `render` fixture
factory (takes the answers dict, `run_tasks` opting into the real `_tasks` render) sandboxed in
`tmp_path`, a `run_in_generated_repo` helper carrying the PATH-isolation logic, and
`COMBINATIONS`/`BASE_ANSWERS` as the shared parametrization source — so a new test (or a quick check
of a suspect combination) is one fixture call, never a throwaway render script.

### 3. The `copier update` round-trip is untested — REMAINING

Because it's currently impossible — see `plans/2026-08-23-copier-update-is-impossible.md`, which has
to land first. Once it does, the round-trip test (render → `git init` + commit → advance the
template → `copier update` → assert the change lands) is what stops it regressing. It belongs in
this suite, on the conftest machinery above.

## Decisions already taken

[DECISION: harden the existing `tmp_path`-based e2e first, rather than moving generation into a
container. The temp-dir tests already catch real template bugs and need no new infrastructure; the
holes above were all closable with parametrization. Chosen over a container-backed tier on
2026-08-23.]

[DEFERRED: a container-backed e2e tier, so generation no longer depends on this machine's global
`repo-tasks` install, `direnv`, or an inherited `PATH` — closer to what a generated repo's real CI
runner sees. Deliberately not now (see the DECISION above); revisit if a bug ever slips through that
the temp-dir tier structurally could not have caught. `repo-tasks`' own `tests/integration/` plus
`pytest.ini`'s `--ignore` is the shape to copy if it happens.]
