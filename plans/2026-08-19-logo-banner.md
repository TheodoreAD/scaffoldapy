---
status: idea
updated: 2026-08-21
---

# README logo/banner for scaffoldapy

## Context

`scaffoldapy` has no visual identity yet — `README.md` opens straight into prose. The name itself is
the brand concept: it's built to _read_ like a spell-word (the `-apy` echo of incantations such as
"solidify"/"nullify"), invoked to take a pile of loose, mismatched project files and make them
snap into the family's harmonious structure (`repo-tasks`, `src/` layout, dedicated per-tool config)
in one shot — the same beat as a wizard's spell resolving chaos into order. Wanted: a
README-header banner/logo that plays that beat visually — **half funny, half serious fantasy, with
tech motifs woven in** (terminal, package/file icons, code fragments) rather than either pure
whimsy or a generic dry corporate mark.

Precedent worth matching in tone, not copying directly: sibling repos in this family
(`repo-tasks`, `olx-polite-mcp`, ...) are plain-prose READMEs with no banner today — this would be
the first piece of visual branding in the family, so it's worth getting the tone right once rather
than a placeholder that sticks around.

## Progress so far

**2026-08-21**: tried generating the cauldron-and-wand concept (prompt #1 in "Candidate prompts"
below) on NightCafe using an early version of that prompt text — results weren't good enough
to use (picky about it, on purpose — this is the first piece of visual branding the family gets, not
a placeholder to settle for). No specific failure mode written down yet; worth noting what actually
went wrong (composition? style read as too cartoonish/too generic-fantasy? cauldron/wand reads
unclear? code-scrap detail illegible at banner size?) next time a batch gets generated, so the next
round of prompts can correct for it specifically rather than just re-rolling the same prompt.
Picking this back up later — plan status stays `idea` until a composition actually lands.

## Open questions

- **Concrete visual concept** — several candidates sketched below, none chosen yet:
  1. **Cauldron-and-wand**: a wizard's hands/sleeves stir a cauldron full of scattered code
     fragments (loose `.toml`/`.py`/`.yml` scraps as parchment bits); the wand is a soldering iron or
     USB‑C cable; the cauldron glows and an orderly `src/` file-tree floats up out of it like a
     conjured result. Strongest "harmonious structure" payoff, most literal read of the spell
     metaphor.
  2. **Open grimoire**: a spellbook whose pages are terminal windows; the "incantations" printed on
     the page are real shell commands (`inv quality.precommit`, `copier copy gh:...`); title reads
     `scaffoldapy` in illuminated-manuscript lettering.
  3. **Sorting-hat**: a wizard hat dropped onto a messy pile of files; files fly up from underneath
     already sorted into a clean directory tree, hat rim glowing along the seam.
  4. **Magic circle**: a summoning circle drawn from file/folder icons and braces instead of runes,
     with the generated project's file tree assembling at the center.
  - [NEEDS CLARIFICATION: pick one of the above, or a hybrid, before drafting]
- **Format** — static PNG/JPEG dropped in `assets/`, or a hand/AI-drafted **inline SVG** (fits this
  family's existing "self-contained, no external asset host" instinct — see the `artifact-design`
  skill's constraints elsewhere in this session — and scales cleanly at any README width)?
  [NEEDS CLARIFICATION]
- **Light/dark handling** — GitHub READMEs render in both themes. A `<picture>` element with two
  exported variants (light-bg / dark-bg) is the standard GitHub trick if a flat image is chosen; an
  SVG could instead use `prefers-color-scheme` media queries directly, one asset, no duplication.
  [NEEDS CLARIFICATION: is dark-mode fidelity worth the SVG complexity, or is a single light-bg PNG
  good enough]
- **Wordmark treatment** — does "scaffoldapy" get custom lettering (illuminated/ornate, matching the
  spellbook feel) baked into the banner image itself, or does the banner stay a pure illustration
  with the existing plain Markdown `# scaffoldapy` heading doing the text job right below it?
- **Scope beyond the README** — just a `README.md` header image, or also a small square mark usable
  as a repo social-preview image / future docs-site favicon? Affects whether a square crop needs
  producing alongside the wide banner.
- **Production tool** — draft candidate compositions with the `design` skill (Claude Design canvas,
  multi-artboard, lets the banner be visually refined by hand afterward) vs. an external
  AI-image-generation tool vs. hand-authored SVG illustration. The `design` skill is the one already
  available in this environment purpose-built for exactly this ("landing pages," "marketing and
  social graphics," visual layouts meant to be tweaked by hand) — leaning toward it, but not decided.
- **Generator/engine choice** — first attempt used NightCafe and didn't land. Open whether the fix is
  better prompting on the same tool (more specific art-style reference, explicit negative-prompt
  guidance — see "Candidate prompts" below) or switching engines/tools entirely (NightCafe exposes
  several backends — e.g. a Stable Diffusion XL variant vs. its DALL-E option — worth trying a
  different one before concluding the tool itself is the problem).

  **Researched 2026-08-21: NightCafe has no public API** — confirmed no developer docs/API-key flow
  exist on its own site; a third-party NightCafe-alternatives roundup states it directly ("no API to
  test... no production API, no programmatic access"). It's web-UI-only, so any iteration has to stay
  manual (one prompt/seed at a time through the site) unless the tool itself is swapped out.

  If switching to something API-scriptable (submit prompt → poll → download, several seeds per
  prompt in one script run — a much better fit for "picky, wants to compare many variants" than
  NightCafe's manual flow): **[fal.ai](https://fal.ai)** (pay-as-you-go, no subscription, 600+
  models incl. Flux/SDXL, generally cheapest/fastest, well documented) or
  **[Replicate](https://replicate.com)** (pay-per-use, huge catalog incl. community fine-tunes/LoRAs
  — useful for chasing a specific illustrator-style checkpoint, e.g. painterly fantasy book-cover
  style — pricier than fal.ai but stronger docs/community) are the two most commonly recommended
  aggregators right now. Also considered: Stability AI's own direct API (SDXL only, narrower),
  OpenAI's Images API (cleaner/more polished-cartoon, less painterly-fantasy — probably the wrong
  register for this brief), Ideogram (strong at in-image text, irrelevant since text is deliberately
  excluded from the brief). **Midjourney has no official API** — only unofficial third-party proxies
  (e.g. Apiframe) that wrap it against its own ToS; not recommending that route despite Midjourney's
  style arguably being the closest aesthetic match, since it requires a ToS-violating workaround.
  [NEEDS CLARIFICATION: stick with NightCafe's web UI (just iterate prompts/styles further) vs. move
  to fal.ai/Replicate for scriptable multi-seed generation]

## Candidate prompts (queued for next attempt)

The first four are the original concept prompts (one per "Concrete visual concept" candidate above);
5-7 are follow-up variations anchored to a specific art style/reference, added after the first
NightCafe batch on prompt 1 didn't land — generic "fantasy illustration" framing is likely part of
why, and a reference-artist/genre anchor tends to give a generator a much sharper, less generic
target than adjectives alone.

1. **Cauldron-and-wand** (primary recommendation — see "Recommended direction" below for why):
   > A wizard's silhouette in a hooded robe, seen from the side, stirring a glowing bubbling cauldron
   > with a wand shaped like a USB-C cable — the cable's plug end sparks like a wand tip. The cauldron
   > is full of scattered torn parchment scraps printed with fragments of code (`.toml`, `.py`, curly
   > braces, YAML-looking lines) instead of potion ingredients. Out of the cauldron's glow, a small,
   > neat, glowing tree of folder and file icons rises upward like conjured smoke, already tidy and
   > organized — the visual payoff of the spell. Wide horizontal banner composition, painterly fantasy
   > illustration style with a wink of humor, moody blues and violets lit by warm cauldron glow, no
   > text in the image, clean empty margin on both left and right for cropping, transparent or solid
   > dark background.

2. **Open grimoire**:
   > An open ancient spellbook floating in dim candlelight, its pages rendered as glowing terminal
   > windows instead of parchment — the "incantations" on the page are real shell command lines
   > (monospace font, green-on-black terminal glow) rather than runes. Faint magical runes drift up
   > from the pages as glowing particles. Illustrated fantasy style, half whimsical half serious, dark
   > background with warm candle and cool terminal-glow lighting, wide horizontal banner composition,
   > no legible large text/title baked in, empty margins on both sides for cropping.

3. **Sorting-hat**:
   > A tattered wizard's hat sitting atop a chaotic pile of loose scattered papers and folders on an
   > old wooden desk, with a soft magical glow along the hat's brim. From underneath the hat, neat
   > glowing folder and file icons fly upward in an orderly stream, already sorted into a clean
   > vertical stack. Fantasy illustration with a touch of humor, warm magical light against a dark
   > background, wide horizontal banner composition, no text, clean margins on both sides.

4. **Square mark** (social-preview/favicon crop, not the main banner):
   > A minimalist square emblem: a wizard's hand holding a wand shaped like a soldering iron, tip
   > sparking, inside a circular magic sigil made of small file and folder icons instead of runes.
   > Flat-ish fantasy-tech illustration style, bold enough to read small, dark background, centered
   > composition, no text, square 1:1 aspect ratio.

5. **Brian Froud-style** (the _Labyrinth_/_Dark Crystal_ concept artist — whimsical goblins sitting
   right next to genuinely serious, atmospheric fantasy art, which is close to exactly the "half
   funny half serious" brief):
   > A wizard in the style of Brian Froud's Labyrinth and Dark Crystal concept art, whimsical but
   > richly detailed, stirring a bubbling cauldron with a wand that is actually a USB-C cable, sparks
   > flying from the plug end. The cauldron is full of torn scraps of paper printed with code
   > fragments instead of potion ingredients. A small orderly stream of glowing folder and file icons
   > rises from the cauldron like conjured smoke. Muted earthy fantasy palette with warm magical
   > glow, richly textured illustration, wide horizontal banner composition, no text anywhere in the
   > image, empty margins on both sides for cropping.

6. **Vintage tabletop-RPG box-art style** (leans into the "funny" half more directly — this is the
   register of old D&D/Baldur's Gate boxes, which already read as a little tongue-in-cheek by today's
   standards):
   > A wizard rendered in the style of a 1980s tabletop RPG box-art illustration — bold heroic
   > lighting played slightly for laughs — holding aloft a soldering-iron wand that's casting a spell
   > over a messy pile of scattered code-covered parchment scraps, which are visibly reorganizing
   > themselves into a tidy glowing stack of folders. Painterly airbrushed style, warm dramatic
   > lighting, wide horizontal banner composition, no text, empty margins on both sides.

7. **Woodcut/engraving style** (a more serious, restrained register — good control variant if 5/6
   still read as too cartoonish):
   > A wizard stirring a cauldron with a wand shaped like a cable, rendered as a detailed woodcut
   > engraving in the style of an old alchemical manuscript illustration, fine crosshatched linework,
   > black and warm sepia tones only. The cauldron contains scraps of paper with code-like symbols;
   > a small tidy stack of folder/document icons rises from the steam. Wide horizontal banner
   > composition, no text, empty margins on both sides for cropping.

**Practical notes for the next batch:**

- **Never ask the generator to render "scaffoldapy" as text in the image** — every mainstream image
  generator (NightCafe's engines included) garbles embedded text badly at this length. Keep the
  wordmark as a separate step (plain Markdown heading, or a hand-set SVG lettering overlay) instead
  of expecting the illustration to carry it.
- Generate several seeds per prompt, not just one — the concept can be right while a single seed's
  composition/anatomy is off (a common generator failure mode, not a sign the prompt itself needs
  rewriting).
- Worth writing down, next time a batch is picky-rejected, _specifically_ what was wrong (style too
  generic, composition unclear, wrong tone, bad anatomy, ...) — that's what turns the next prompt
  iteration into a correction instead of a re-roll.

## Recommended direction

Cauldron-and-wand (#1) is the strongest single concept: it's the only one of the four that visually
shows _both_ halves of the brief in one beat — funny (a wizard elbow-deep in a bubbling pot of
`.toml` scraps) and serious-fantasy (a proper spell-conjuring silhouette, not a cartoon caricature) —
while making "loose files → harmonious structure" legible at a glance without needing the viewer to
already know the name's pun. Pair the wand with a tech-literal object (USB‑C cable, soldering iron,
or a terminal-cursor-shaped wand tip) rather than a generic sparkly stick, so the "tech motifs" half
of the brief reads immediately rather than needing the caption to carry it.

**Production route settled 2026-08-21, superseding the earlier design-skill-first framing above**:
the `design` skill composes HTML/CSS/inline SVG — good for geometric/flat/icon-style graphics and
layout, but not for painterly character illustration (a wizard, a bubbling cauldron, textured
lighting) — anything it drew here would read as a flat pictogram, not the illustrated register this
concept needs. Image generation is the right tool for the hero illustration itself; the `design`
skill's role, if any, narrows to a possible follow-up for a geometric alternate (concept #4,
magic-circle-of-file-icons) or for composing the final wordmark/layout around a chosen illustration,
not for drafting the illustration itself.

Suggested next step: work through the "Candidate prompts" list above on NightCafe (or a different
engine/backend if switching per the open "Generator/engine choice" question), several seeds each,
starting with #1/#5/#6 since those anchor the concept most concretely. Once a result actually lands,
send the file over — from there: pick format (flat PNG/JPEG vs. redrawing as SVG), decide light/dark
handling, decide wordmark treatment, and wire it into `README.md`'s header.
