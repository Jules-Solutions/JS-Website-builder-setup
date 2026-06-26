---
phase: 2
name: Vision
group: discovery-strategy
pipeline_section: discovery-strategy
skill: wb-discovery
prev_phase: 1
next_phase: 3
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-phase-contracts.md
  - Workstreams/website-builder/foundation/DESIGN-architecture.md
  - Workstreams/website-builder/foundation/DESIGN-ecosystem-catalog.md
library_clones_at_entry:
  - resource: brand-examples-corpus
    as: brand-examples
    note: "complete brand systems showing voice + tokens + component patterns; surfaces when user wants to see what a full vision looks like"
  - resource: design-systems-corpus
    as: design-systems
    note: "Material 3 / Apple HIG / IBM Carbon excerpts for reading how mature systems articulate themselves"
---

# Phase 2 — Vision

> Turn the idea into a concrete visual + emotional vision. Reference URLs plus per-URL reasoning plus a sentence or two on the imagined feel of the finished site. The phase that converts *what the site is for* into *what the site is like*.

## Mission

Phase 1 captured what the site is *for*. Phase 2 captures what the site is *like*. Not the design system (phase 17 owns that) and not the brand voice (phase 5 owns that) — the *feel*: the visual register, the emotional posture, the family of sites this one belongs to.

Concretely: the user names three to five reference URLs of existing sites they admire, gives a sentence per URL explaining *what* they admire (palette? typography? pacing? confidence? warmth?), and writes one or two sentences describing what the finished site should feel like to land on. That bundle becomes the vision input to phase 17 (design system creation) and phase 5 (brand voice exemplars).

The agent's job is to convert vague aesthetic descriptors ("clean", "modern", "professional") into concrete observations grounded in specific examples. The agent does not impose taste; it surfaces options + asks the user to point at what resonates + extracts the underlying pattern. By the end of phase 2, the user should be able to read their own vision statement back and say *"yes, that's the family this site is in."*

## Entry conditions

Phase 1 is complete. `.website-builder/project.yaml.idea.paragraph` exists; the user has confirmed it. `current_phase: 2` is set.

The phase 1 idea paragraph is in scope as context — the vision builds on it (a site whose idea is "weekly essays on staying human in 2026" lives in a different visual family than a site whose idea is "Swiss commodity broker desk operations dashboard"). The agent rereads the captured idea before opening the phase 2 conversation.

For non-greenfield entry modes, any prior artifact's design tokens (extracted via phase 6.5 when available) are loaded as a candidate reference. The user is still asked the vision question — the existing artifact is one of the references, not the *only* reference, and the user can keep, extend, or replace it.

## What Claude must establish

The work product of this phase has four parts, all stored under `.website-builder/project.yaml.vision`:

1. **3-5 reference URLs.** Sites the user admires *for some reason*. Not necessarily in the user's industry. Not necessarily in the same stack. The reason matters more than the source.
2. **One sentence per URL.** What the user admires about it. Specific. "I like the way the headline carries the page without a hero image" beats "I like it." The agent forces specificity by asking targeted follow-ups when the answer is vague.
3. **One to two sentences on the imagined feel of the finished site.** Not a description of what's on the home page. A description of what it feels like to land on it — quiet? confident? warm? mechanical? generous? dense?
4. **An extracted pattern set of 3-6 adjectives.** The agent reads the references + the feel statement and extracts a small adjective list (e.g., *minimalist, type-led, generous whitespace, monochrome, warm grain*). The user confirms or revises. These adjectives flow into phase 5 (brand voice) and phase 17 (design system).

Output schema:

```yaml
vision:
  captured_at: 2026-05-18T14:48:00Z
  references:
    - url: https://example.com
      admire: "The way the headline carries the page without a hero image — confidence in typography."
      seen_via: webfetch  # or: user-described-from-memory, screenshot-pasted, prior-artifact
    - url: https://anotherexample.com
      admire: "The pacing between sections — generous whitespace; nothing fights for attention."
  feel: |
    Quiet on arrival. The headline reads like a sentence, not a slogan.
    The page rewards scrolling without urgency. Warm in palette, type-led
    rather than image-led.
  adjectives: [minimalist, type-led, generous-whitespace, warm-palette, quiet]
  iteration_count: 2
```

## Gating rules

The agent refuses to advance to phase 3 (requirements) when any of the following are true:

1. **Empty-descriptor vision.** When the only thing the user can say is *"I want it to look professional / modern / clean / sleek / minimal"* and cannot back it with a single concrete reference, the agent refuses. Those words mean different things to every person; they cannot anchor downstream design decisions. The agent surfaces concrete alternatives: *"'Professional' covers everything from a Swiss bank's site to a brutalist editorial magazine. Show me one site you've seen recently that's professional in the way you want this one to be — even if it's in a different field."*

2. **Zero references.** Fewer than three reference URLs (or three distinct artifacts — screenshots, Pinterest boards, the user's own old site, a magazine page) is insufficient input for phase 17 (design system). The agent does not enforce *exactly* five references, but it does enforce that the input set is rich enough that an adjective extraction won't be guessing. If the user genuinely has no references, the agent walks them through reference-sourcing — Awwwards, Land-book, Mobbin, One Page Love (catalogued in `DESIGN-ecosystem-catalog.md`) — and stays in this phase until references exist.

3. **References without reasoning.** When the user lists URLs but cannot articulate what is admirable about any of them — *"I just like it"* — the agent refuses. The reason matters; without it, phase 17 cannot extract the right pattern and ends up mimicking surface features instead of underlying logic. The agent probes: *"OK, look at it again. If you had to point at one element on this page and say 'do more of this' — what would it be? The headline? The space? The mood? The pacing?"*

4. **Vision-as-purpose backslide.** When the user starts answering vision questions with idea-shaped answers (*"the vision is to help businesses succeed"*), the agent refuses. The agent reflects: *"That's what we captured in phase 1 — the purpose. Phase 2 is the visual register: what should it feel like to land on this site? What family of sites is it in?"*

The override path applies — the user can explicitly confirm advancement with an incomplete vision and the agent flags the cost: phase 17 will be harder; phase 5 voice exemplars will be thinner; risk of generic AI-default aesthetics is higher.

## Tools and skills used

- **`AskUserQuestion`** — the dominant tool. Used for the opening question, per-reference follow-ups, the feel statement, and adjective confirmation.
- **`WebFetch`** — used to load each reference URL and *discuss* it with the user. The agent fetches the page, summarizes its visual register (type families it appears to use, dominant colors, page layout, pacing), and asks the user to confirm or refute. WebFetch is also used when the user describes a site from memory and the agent wants to verify the actual current state of that site before treating it as reference data.
- **`WebSearch`** — used sparingly, when the user describes a site by recall but cannot name it (*"there was this minimalist site about journals, I think — it had a serif headline?"*) and the agent helps locate it.
- **`Read`** — to read `.website-builder/project.yaml.idea` (phase 1 output) at phase entry.
- **`Write` / `Edit`** — to update `.website-builder/project.yaml` with the captured vision.
- **Reference-data load** — the agent reads catalogued exemplar libraries from `.website-builder/library/brand-examples/` and `.website-builder/library/awesome-design-md/` (per `DESIGN-ecosystem-catalog.md`) when the user wants the agent to surface candidate references rather than coming with their own.

No `context7` lookups (no library docs needed at this phase). No Playwright (phase 6.5 owns live-site walking; phase 2 stays at the surface-level WebFetch for reference-loading).

No subagent spawns by default. If the user wants a parallel "scan five reference URLs at once for me" pass, the agent may spawn a research subagent — but the default is in-person, per-URL conversation so each reference becomes a real talking point, not a checked box.

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| `.website-builder/project.yaml` | adds `vision:` key per schema above | The captured references + feel + adjectives; load-bearing for phases 5, 17 |
| `.website-builder/library/inspiration/reference-sites.md` *(when load-bearing)* | List of reference URLs + screenshots + notes | The user's growing inspiration library; copied here from in-flight conversation so it persists past the session |
| `.website-builder/decisions/02-vision-adjectives.md` *(optional)* | Standard decision-doc frontmatter + body | Created when the adjective extraction surfaced a non-obvious choice (e.g., "warm" vs "cool" was contested) |

The vision block in `project.yaml` is the required artifact. The inspiration directory entry is created when the user's references are diverse enough to warrant their own home (typically when 4+ references emerge); when 3 references are clean, they live entirely inside `project.yaml.vision.references`.

The agent updates `.website-builder/project.yaml.current_phase` to `3` upon user confirmation that the vision reads true. Phase 3 (requirements) loads next.

## Common failure modes

**The user says "I want it to look like Apple."** Apple covers many aesthetics across product surfaces and a decade of design evolution. The agent reflects: *"Apple's a big surface. Are we talking apple.com homepage (lots of product photography, generous whitespace, big typography)? Or are we talking iOS settings (clean lists, tight grids, neutral)? Or are we talking the Apple events page (cinematic video, dark mode, bold type)? Each of those is 'Apple' in a different register."* Then the agent unpacks: minimalist / generous whitespace / type-led / monochrome — and asks if all four are wanted or just one.

**The user says "I want it to look professional."** *Professional* is one of the empty descriptors per the gating rules. The agent surfaces the spectrum: *"Professional can mean: Swiss-bank serious (lots of weight, dark typography, dense data); editorial-magazine confident (generous whitespace, type-led, restrained); tech-startup polished (sans-serif, brand color accents, conversion-oriented). Where in that spectrum is this site?"* The agent forces a choice among concrete alternatives before allowing the descriptor to stick.

**The user's references are all in the same narrow niche.** All five references are direct-competitor sites. The agent flags the risk: *"Picking references that all do the same thing as your site is going to push us toward a same-as-competitor design. Have you seen sites in entirely different industries that move you? A magazine, a museum, a designer's portfolio — those often reveal what you actually like, not just what you're used to seeing in your space."* Encourages broadening; does not force it.

**The user picks references that are visually incompatible with each other.** Three references: one is a brutalist editorial, one is a soft consumer SaaS, one is a Y Combinator startup landing page. The agent surfaces the tension: *"These three sites have very different visual registers. If I had to extract a pattern, I'd pull in three contradictory directions. Which of these is closest to the actual feel you want — or is there a fourth reference that sits between them?"* The conflict gets resolved before adjective extraction.

**The user's "vision" is actually a feature list.** *"I want a big hero image, a three-column features section, a testimonial carousel, and a pricing table."* Those are phase-9 (sitemap) + phase-13 (content per page) + phase-15 (content per section) artifacts. The agent reflects: *"Those are pieces — I'll come back to them at phases 9 and 13. Phase 2 is about the visual register of the whole thing. What should the experience of arriving feel like before any specific section loads?"*

**The user pasted a single one-shot AI-tool screenshot and says "make it look like that".** The screenshot is one reference; phase 2 wants 3-5. The agent acknowledges: *"This screenshot is a useful anchor. Treat it as one of the references — what specifically is admirable about it? Pull out the part that's actually you. Then let's add 2-3 more references so phase 17 has range to compose from, not just one source."*

**The user wants the agent to "just generate a vision".** *"I don't have time for this — pick five sites you like for me."* The agent refuses politely: *"This is one of the load-bearing decisions. If I pick references on your behalf, phases 5 and 17 inherit my taste, not yours, and the site ends up reading as 'an agent's idea of what your site should be.' I can offer you a curated shortlist from the corpus we have — design exemplars and category libraries — and we narrow from there. Want me to surface 10 candidates for you to react to?"* This route loads from `.website-builder/library/brand-examples/` + `.website-builder/library/awesome-design-md/` + the catalogued external libraries (Awwwards, Land-book, etc. per `DESIGN-ecosystem-catalog.md`).

**The references the user names cannot be loaded by WebFetch (Cloudflare gate, login-walled, dead URL).** The agent surfaces the load failure: *"That URL didn't load — looks like the site requires login or has changed. Want to point at a different reference, or describe what you remembered about it so we can capture the intent without the artifact?"* Memory-based references are valid; they just live with `seen_via: user-described-from-memory` in the schema.

## Reference materials

- **Design doc — phase pipeline source:** `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` § 2 (seed for this contract)
- **Design doc — pipeline integration:** `Workstreams/website-builder/foundation/DESIGN-architecture.md` § Phase contracts
- **Design doc — reference catalogue:** `Workstreams/website-builder/foundation/DESIGN-ecosystem-catalog.md` § Reference resources (the external inspiration sources the agent surfaces when the user has no references: Awwwards, Dribbble, Behance, Land-book, One Page Love, Mobbin, SaaS Pages)
- **Design doc — adjective output target:** `Workstreams/website-builder/foundation/DESIGN-content-layers.md` § Layer 1 — Design tokens (the adjective set seeds phase-17 token generation)
- **Plugin corpus — design exemplars:** `.website-builder/library/awesome-design-md/` — cloned from VoltAgent/awesome-design-md; 60+ DESIGN.md exemplars from Claude / Shopify / Stripe / Figma / Notion / IBM etc.; agent greps for patterns when surfacing candidate adjective sets
- **Plugin corpus — brand examples:** `.website-builder/library/brand-examples/` — 5-8 complete brand systems showing voice + tokens + component patterns; useful when the user wants to see "what a complete vision looks like" before committing
- **External libraries** (fetch-on-demand per catalog):
  - Awwwards — https://www.awwwards.com (award-winning sites by style + tech stack)
  - Land-book — https://land-book.com (landing-page gallery)
  - One Page Love — https://onepagelove.com (single-page site gallery)
  - Mobbin — https://mobbin.com (mobile-app patterns; useful when the site has a mobile-heavy audience)
  - SaaS Pages — https://saaspages.xyz (SaaS-specific landing patterns)
  - Dribbble — https://dribbble.com / Behance — https://behance.net (designer portfolios; broad visual inspiration)
