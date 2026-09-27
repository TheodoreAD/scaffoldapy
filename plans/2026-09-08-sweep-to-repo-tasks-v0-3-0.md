---
status: idea
updated: 2026-09-13
source_repo: github.com-personal/repo-tasks
source_session: e0a0f092-e55e-4429-95e5-1882a6b773be.jsonl
source_moment: 2026-09-08T00:00:00Z
source_plan: plans/2026-08-25-consumer-transitions.md
---

# Sweep this repo onto repo-tasks v0.3.0 — four measured items

## Context

This repo is the outstanding half of the batched consumer sweep that `repo-tasks`'
`plans/2026-08-25-consumer-transitions.md` has been carrying since 2026-08-29. The
`power-user-linux-setup` half ran 2026-09-05; this one is still owed, **and it is the half that
matters most**, because this repo's end-to-end tier is the only thing in the family that tests what
it generates rather than what it is.

Filed from `repo-tasks` rather than performed, because writing into another repo's working tree is
out — parallel sessions share these checkouts.

**The drift was measured, not listed.** Run 2026-09-08 read-only from outside this repo, using the
installed `repo-tasks v0.3.0` tool's own `configs.diff` and `link_check` against this tree. Nothing
here was written, pulled or staged.

## Evidence

Session `e0a0f092-e55e-4429-95e5-1882a6b773be.jsonl` under
`~/.claude/projects/-home-tdumitrescu-projects-github-com-personal-repo-tasks/`, 2026-09-08. The
distinctive phrase to search that transcript for is "What both consumers are actually behind on".

The repro needs no session — one command, from anywhere:

```shell
python3 -c "import glob,os,sys; sys.path.insert(0, glob.glob(os.path.expanduser('~/.local/share/uv/tools/repo-tasks/lib/python*/site-packages'))[0]); os.chdir('<this repo>'); from invoke import Context; from repo_tasks import configs; configs.diff(Context())"
```

Or simply `inv configs.diff` from inside this repo, which resolves the same global tool.

### What this repo is behind on

| item                                                 | landed in `repo-tasks`   |
| ---------------------------------------------------- | ------------------------ |
| `ruff.toml` — `sys.path` / `site.addsitedir` bans    | `1c91c2e`                |
| `dprint.json` — sha256 checksums on all five plugins | 2026-09-06               |
| `pytest.ini` — the starlette `anyio` ignore          | `487c9c8`                |
| dev group — `hadolint-py` missing `!=2.15.1.2`       | manifest, date not taken |

`power-user-linux-setup` reported **identical** drift when this was written, so none of it is
specific to this repo.

**Re-measured 2026-09-13, same method, and the four items are unchanged** — no new drift in five
days, so nothing here needs re-scoping and the table above can be acted on as written.
`power-user-linux-setup` is no longer a comparison: it was swept to `v0.3.0` on 2026-09-10 and all
four of its items are closed, which leaves this repo as the one that still owes them.

That same re-measurement found two consumers `repo-tasks` had never recorded at all, `ingesta` and
`invoke-stubs`, one of them drifting worse than this repo. Nothing for this repo to do about it —
noted only because it means the sweep's scope grew after this plan was filed, and this plan is not
the whole of it. `repo-tasks`' `plans/2026-08-25-consumer-transitions.md` carries the measurement.

### What this repo is _not_ behind on, contrary to the sweep checklist

This repo takes `repo-tasks` as the **global uv tool**, already at `v0.3.0`, so every task-code
change is live here the moment the tool moves. Only the pulled config _files_ and the dev group are
snapshots that drift.

- `7fc0b23` (link-check anchor resolution) is already in effect here, and `link_check` reports **no
  broken links** against this tree. The `repo-tasks` checklist sequenced this first on the theory
  that a stricter check turns a green consumer red; measured, it does not.

## The one item with a consequence beyond configuration

`487c9c8` — `ignore:The anyio.abc.BlockingPortal alias is deprecated` in the shipped `pytest.ini`.
Every other item moves this repo; this one **fixes** it.

Under the current shipped `pytest.ini`, `filterwarnings = error` turns an import-time
`DeprecationWarning` inside `starlette.testclient` into a collection error, so a repo whose tests
touch `fastapi.testclient` reports `collected 0 items / 1 error` and cannot run pytest at all. That
is one parametrized case of this repo's end-to-end tier —
`test_generated_repo_passes_quality_check_out_of_the_box[web_service-no-fetch]`, 9 of 10
combinations green.

`repo-tasks`' `plans/2026-09-07-starlette-anyio-deprecation-breaks-web-consumers.md` owns the fix
and carries an `[UNVERIFIED:]` that **only this repo can discharge**: the fix is verified against a
throwaway project but never against the repro that produced it. Its two stated prerequisites are
both met as of 2026-09-08 — `487c9c8` is on `origin/main`, it is contained in `v0.3.0`, and the
global tool is already at `v0.3.0` (confirmed: the installed `configs/pytest.ini` carries the
entry). So `inv repo-tasks.update` is a no-op and nothing is blocking.

[PITFALL: the generated repos render against the **globally installed** `repo-tasks`, not against a
checkout, which is why the ordering note in that plan exists at all. It is satisfied now; the note
predates the release and reads as though it is not.]

## Open questions

[NEEDS CLARIFICATION: does the `ruff.toml` coupling ban (`sys.path`, `site.addsitedir`) need
anything in the **template** as well as in this repo's own config? The ban is inert in a
single-distribution repo, which every generated repo currently is — but this repo generates them,
and the shipped `ruff.toml` reaches them at generation time rather than through a sweep. Worth
checking whether a generated repo pulls the new file or a snapshot.]

[NEEDS CLARIFICATION: the `hadolint-py` constraint is a dev-group edit, and `configs.ensure-deps` is
additive — it will not rewrite an entry already present. So this one is a hand edit, per
`configs.diff`'s own next-steps output. Confirm that is still true rather than assuming.]

## Recommended direction

The sequence `configs.diff` itself prints, in order:

```shell
inv configs.pull            # the three config files
# then edit dependency-groups.dev by hand: "hadolint-py" -> "hadolint-py!=2.15.1.2"
inv configs.ensure-deps
inv deps.lock               # review the diff
inv venv.sync
inv quality.precommit
inv test.integration        # the half that actually matters here
```

`test.integration` is the step this whole item exists for — it is not finished at
`quality.precommit`, per the correction the 2026-08-26 walk-through already made to `repo-tasks`'
`contributing/consumer-sweep.md`. Expect the `web_service` combination to go from red to green, and
record which way it went: that is the answer the starlette plan is waiting on.

**Do not start from `repo-tasks`' sweep checklist.** Measured 2026-09-08, it named one of these four
items; two more were found by reading source that morning and two only by running `configs.diff`.
The command is the list.
