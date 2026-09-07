---
status: landed
updated: 2026-09-08
---

# GitHub Action versions have drifted, and nothing in this family watches them

## Context

Every CI run in this family now emits a deprecation annotation:

```
Node.js 20 is deprecated. The following actions target Node.js 20 but are being forced to run on
Node.js 24: actions/checkout@v4
```

Noticed 2026-08-29 on two green `ingesta` runs, whose workflow is a byte-identical copy of this
repo's `template/.github/workflows/ci.yml`. So it is not that repo's annotation — it is this
template's, reproduced in every repo generated from it, on every run.

Measured across the six personal repos cloned on this machine: **14 `actions/checkout@v4`
occurrences**, in `ci.yml`, `docs.yml`, `devcontainer.yml`, `docker-release.yml`,
`publish_on_push.yml` and `publish.yml`. Thirteen are ref pins; one, in the release workflow holding
`id-token: write`, is hash-pinned by hand, which is the single deliberate exception the family's
`zizmor.yml` describes.

Checked against the upstream release feeds rather than assumed:

| action               | pinned here | current   | notes                                    |
| -------------------- | ----------- | --------- | ---------------------------------------- |
| `actions/checkout`   | `v4`        | `v7.0.1`  | v4 → node20; v5, v6 and v7 all → node24  |
| `astral-sh/setup-uv` | `v9.0.0`    | `v10.0.1` | one major behind; no deprecation warning |

Two things worth stating because the obvious guess is wrong. **The fix is not "bump to v5"** — that
was the first assumption and it is two majors stale. And `actions/checkout` shipped v4.4.0, v5.1.0,
v6.1.0 and v7.0.1 within half an hour of each other on 2026-07-20, so upstream is actively
maintaining four majors in parallel; being on an older one is a supported position, not neglect.

## Why it has no owner today

This is the cost side of a trade this family took on purpose. The canonical `zizmor.yml` sets a
`ref-pin` policy rather than zizmor's blanket hash-pin default, and its own comment gives the
reason: pinning everywhere without dependabot means pins that silently rot, and dependabot means a
standing PR stream on repos that are pushed to directly.

That reasoning is sound and this plan does not reopen it. What it observes is the half that was
implied and never built: having declined the bot, nothing at all watches these versions, so the
first signal is a deprecation annotation on a green run — which is exactly the kind of output nobody
reads, because the run passed.

## Questions, as answered

~~Which major to land on?~~ **`v7`**, taking the family's reading rather than re-deriving it.
`repo-tasks` checked each major against these repos on 2026-08-29 and `power-user-linux-setup`
re-checked it on 2026-09-04: v5's minimum runner v2.327.1 is a self-hosted concern and every job
here is `ubuntu-latest`; v6 moves where credentials are persisted, not the `persist-credentials`
input, which stays `false` at all three sites here; v7 blocks checking out a fork PR under
`pull_request_target` and `workflow_run`, and no workflow here uses either trigger.

~~Does `setup-uv` move in the same pass?~~ **Same pass, separate commit** — which is what the
"regression is ambiguous" objection actually asks for. `v9.0.0` → `v10.0.1`. v10 disables the cache
under `enable-cache: auto` for `pull_request_target`, `workflow_run` and `release`; the generated CI
workflow triggers on `push` and `pull_request`, the generated docs workflow on `push` alone.

~~What replaces dependabot?~~ **Already built, in `repo-tasks`, and used here.** `ci.check-actions`
asks each action's release feed and compares at the precision the pin states, report-only;
`ci.status` prints a run's annotations rather than only its conclusion. Both arrived 2026-08-29 and
reach every consumer through the tool rather than through a config, so nothing about this repo had
to be built. This repo publishes them already — `tasks.py` is `from repo_tasks import ns` — and
`inv ci.check-actions` is what found the two pins below rather than a reading of the workflow files.

**`peaceiris/actions-gh-pages@v4` is current** and stays: latest is `v4.1.0`, and a bare major pin
is current at the precision it states. It is invisible to
`inv ci.check-actions --path
template/.github/workflows`, which reads only files ending `.yml` — the
generated docs workflow's name is a Jinja conditional, so it was checked by hand.

## Landed 2026-09-07

| action               | sites | was      | now       | annotated by GitHub? |
| -------------------- | ----- | -------- | --------- | -------------------- |
| `actions/checkout`   | 3     | `v4`     | `v7`      | yes                  |
| `astral-sh/setup-uv` | 3     | `v9.0.0` | `v10.0.1` | no                   |

Three sites each: this repo's own `ci.yml`, the template's byte-identical copy, and the template's
conditional `docs.yml`. Two commits, split so a regression is attributable to one bump — and the
split is what the annotated/not-annotated column makes worth keeping: the second bump was invisible
to every signal GitHub emits.

**The comment fix rode along with the checkout bump, deliberately.** Both `ci.yml` copies explained
`persist-credentials: false` by saying the token is otherwise left "in `.git/config`" — true through
v5, false from v6, and the template's copy ships that sentence into every generated repo. Nothing in
actionlint, zizmor or the suite reads English, so a bump on its own would have left it standing and
wrong. Flagged in advance by `repo-tasks`' own plan, which hit the same sentence in a sibling repo.

`inv test.all` after both: 9 of 10 e2e combinations green, `web_service-no-fetch` red on an
unrelated upstream defect filed for `repo-tasks` the same day (starlette 1.6.0 tripping the shipped
`filterwarnings = error` through a deprecated anyio alias). Not caused by, and not affected by, this
change.

**Verified by annotation, 2026-09-07, on the first run after the push** — and checked the only way
that answers it, since the run was not even green:

| run           | commit            | annotations                                      |
| ------------- | ----------------- | ------------------------------------------------ |
| `33220460012` | before, **green** | `warning \| Node.js 20 is deprecated … @v4`      |
| `34162377835` | after, **red**    | `failure \| Process completed with exit code 1.` |

Nothing about Node 20 on the new one, and the same
`gh api repos/<owner>/<repo>/check-runs/<job-id>/annotations` call returns the warning on the older
run — so the silence is real rather than a call that failed, which is the check this plan insisted
on because `[]` means both.

The pairing is sharper than the one `repo-tasks` recorded for itself: there, the annotated run was
green and the clean one was green. Here the annotated run is the **green** one and the clean run is
**red**, on an unrelated upstream defect in a generated repo's own gate. Two runs, and the
conclusion column gets both of them backwards.

## Merged in: `2026-08-27-checkout-action-node20-deprecation.md`

The same subject, filed two days earlier and narrower — it had the annotation, the two line numbers
and the byte-identity note, and its recommended direction ("bump both pins, let `inv test.all` run
the integration tier") is what happened. Nothing in it survives that is not above. Its one open
question does not die with it, though: see below.

## What is left, and it is not about actions

How a template fix reaches already-generated repos is the one question this work does not settle,
and it was never an action-pin question: a change here makes every existing generated copy diverge
until someone pulls it forward, and nothing prompts them to. Both merged plans raised it, and the
2026-08-27 one said outright that it "may deserve its own plan". It has one now —
`plans/2026-09-08-reaching-already-generated-repos.md` — rather than being carried here, where it
would keep a closed piece of work open.

## Migrated to

- [`contributing/generated-workflows.md`](../contributing/generated-workflows.md) — the pin
  decisions, what watches them (annotations and `ci.check-actions`, and why one is not enough), the
  `.yml`-extension blind spot that hides the conditional docs workflow, the
  version-bump-invalidates- a-comment pitfall, and the annotation-not-conclusion check with the run
  pair that proves it.

Deliberately not migrated: the upstream reading of `checkout` v5/v6/v7 and `setup-uv` v10, which is
`repo-tasks`' `plans/2026-08-28-node20-action-deprecation.md` and its `contributing/quality-gate.md`
to keep current — this repo consumed that reading rather than producing it, and a second copy would
diverge. The 14-occurrence machine-wide census is a measurement of a moment, not a fact about this
repo. The verification transcript itself stays in git.
