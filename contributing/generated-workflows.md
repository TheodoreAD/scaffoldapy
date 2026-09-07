# What CI a generated repo gets, and why it is shaped that way

The template emits `.github/workflows/ci.yml` unconditionally, `security.yml` unconditionally, and
`docs.yml` only under `with_docs`. This file is the reasoning behind those files; `AGENTS.md` says
how to work on them, and the files themselves carry the short version in comments.

## Two workflows, not one, because they fail for different reasons

`CI` runs the generated repo's own `inv quality.check` plus `inv test.integration`. `Security` runs
a dependency audit and nothing else. Keeping them apart is the point rather than tidiness: GitHub
gives every workflow its own check run, name and badge, so a green `CI` beside a red `Security`
reads as "the code is fine, the dependencies are not" with nothing further to configure. Folding the
audit into `ci.yml` would lose that distinction and put a network call inside the workflow whose
whole value is being offline and deterministic.

The generated `AGENTS.md` says the same thing to the repo's own agents, because the natural reaction
to a red check is to look for a code defect, and this one never is.

## The audit is called, never copied

`security.yml` is a caller for a reusable workflow that lives in `repo-tasks`, so the audit has one
definition for the whole family and no per-repo drift for anyone to track. The job installs nothing
— `uv audit --locked` reads `uv.lock` and queries OSV — which is why the same six lines work for
every interface and dependency set this template can produce.

**It works from a private generated repo only because the host repo is public.** On Free, Pro and
Team plans a reusable workflow must live in the same repository or a public one; hosting it in a
private repo would need Enterprise. That property is invisible from either file and is the reason
the audit lives where it does.

**Pinned to a commit, not `@main`.** A moving ref would change a generated repo's audit the moment
the upstream default branch moved, in repos nobody is touching. The pin's trailing `# YYYY-MM-DD`
comment is the readable version, because `repo-tasks` publishes no releases and there is no tag to
name — and that shape (job-level `uses:`, 40-hex SHA, trailing comment) is what
`inv ci.check-actions` parses a version out of. `tests/unit/test_template.py` asserts the shape
rather than the commit, so bumping the pin is free and replacing it with a moving ref is caught.

[PITFALL: **nothing watches that pin.** `ci.check-actions` resolves currency through each action's
`releases/latest`, and `repo-tasks` publishes no releases and carries no tags, so its own reusable
workflow is skipped as nobody's release to track. Every repo generated from here sits on whatever
SHA the template baked in until a human looks. Bump it deliberately when that workflow changes; it
has changed once, at its introduction.]

## Action pins, and what actually watches them

The family declined dependabot — a standing PR stream against repos that push straight to `main` —
and the canonical `zizmor.yml` sets a `ref-pin` policy rather than zizmor's blanket hash-pin
default. What replaced the bot is two report-only tasks that arrive through `repo-tasks` rather than
through any file this template stamps: `inv ci.status` prints a run's **annotations** rather than
only its conclusion, and `inv ci.check-actions` asks each action's release feed and compares at the
precision the pin states (`@v7` against a latest of `v7.0.1` is current, because a bare major is a
moving tag; `@v9.0.0` against `v10.0.1` is behind).

Both are needed, and that was measured rather than assumed. Of the two actions found stale here in
2026-09, GitHub had annotated one and said nothing about the other:

| action               | behind by | GitHub annotated it? |
| -------------------- | --------- | -------------------- |
| `actions/checkout`   | 3 majors  | yes                  |
| `astral-sh/setup-uv` | 1 major   | no                   |

Annotations report what GitHub has decided to deprecate; they say nothing about an action simply
being behind.

[PITFALL: **`ci.check-actions --path template/.github/workflows` does not see the docs workflow.**
It reads files ending `.yml`, and that file's name is a Jinja conditional
(`{% raw %}{% if with_docs %}docs.yml{% endif %}{% endraw %}`), so the whole file is invisible to
the check. Its pins have to be read by hand — which is how `peaceiris/actions-gh-pages` came to be
verified separately during the 2026-09-07 bump. Any interface-conditional workflow added later
inherits this blind spot.]

[PITFALL: **a version bump can invalidate a comment, and no gate can see it.** Both `ci.yml` copies
explained `persist-credentials: false` by saying the token would otherwise be left "in
`.git/config`" — true through `checkout` v5, false from v6, which moved credential persistence to a
separate file. Nothing in actionlint, zizmor or the test suite reads English, so the sentence would
have survived the bump unread, and the template's copy ships it into every generated repo. Fixed in
the same commit as the bump that falsified it, which is the only moment anyone is looking at the
line.]

## A green run is not the check

The Node 20 deprecation rode every green run in this family for roughly eleven months, because a
warning annotation changes nothing about the conclusion. So the check that closes an action bump is
`inv ci.status` on the run after it, reading annotations — and the absence has to be checked against
a call known to work, since an empty result means both "clean" and "the call failed". Confirmed
2026-09-07: the same `gh api repos/<owner>/<repo>/check-runs/<job-id>/annotations` call returned the
Node 20 warning on the previous run and nothing on the new one.

That pair also shows why the conclusion column cannot be the signal. The run carrying the
deprecation was **green**; the clean run after the bump was **red**, on an unrelated upstream defect
in a generated repo's own gate.
