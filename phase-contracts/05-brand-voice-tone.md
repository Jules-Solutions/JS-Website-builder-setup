---
phase: 5
name: Brand voice & tone
group: discovery-strategy
pipeline_section: discovery-strategy
skill: wb-discovery
prev_phase: 4
next_phase: 6
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - DESIGN-phase-contracts.md
  - DESIGN-architecture.md
  - DESIGN-content-layers.md
  - DESIGN-i18n.md
  - ${CLAUDE_PLUGIN_ROOT}/reference-corpus/ECOSYSTEM-CATALOG.md
library_clones_at_entry:
  - resource: voice-archetypes
    as: voice-archetypes
    note: "catalogued brand voice exemplars (public voice-guide URLs, NN4D profiles, say/never-say); surfaces 5-10 candidates when the user wants options"
---

# Phase 5 — Brand voice & tone

> Establish the verbal identity — *how* the site sounds, distinct from how it looks. The last phase of discovery-strategy before content capture begins. Locks the voice that phase 16 (copywriting) writes in and phase 17 (design system) reads to find typographic kin.

## Mission

Phase 2 captured the visual register; phase 5 captures the verbal one. They are independent — a brutalist-visual site can sound warm; a soft-pastel-visual site can sound clinical. The agent extracts the voice in its own pass.

Concretely the agent produces five artifacts: a 1-2-sentence voice description; a list of 3-5 voice attributes (grounded in concrete adjectives, not generics like "professional"); a Nielsen Norman 4-dimensional tone profile (humor / formality / respectfulness / enthusiasm — each as a 3-point scale value); examples of phrases the brand *would say* and *would never say* (the say / never-say is more diagnostic than abstract adjectives); and 1-2 voice exemplars (existing brands whose voice the user wants their site to share family with — typically named alongside grounding from the `voice-archetypes/` reference corpus).

The agent uses the Nielsen Norman four-dimensional framework as the structural scaffold; refines into attribute words; grounds in exemplars. The output flows into phase 16 (copywriting — the voice IS the copy direction) and phase 17 (design system — voice descriptors inform type-pairing choices, color temperature, motion preferences). Phase 3 positioning is the upstream input — the voice has to compose with the positioning paragraph (a brand positioned as "rigorous and quietly confident" cannot sound playful-irreverent without contradicting itself).

## Entry conditions

Phase 4 is complete. `.website-builder/project.yaml.entity` exists with name, what-they-do, origin, location, contact, assets; the user has confirmed it. `current_phase: 5` is set.

The phase 1-4 outputs are in scope. The agent rereads the idea + positioning + entity description before opening the phase 5 conversation. The voice has to *fit* the entity — a solo practitioner sounds different from a 50-person agency even when both occupy the same positioning slot.

For non-greenfield entry modes, prior artifacts often contain voice samples (existing site copy in `inbox/`, social posts, prior client emails the user is willing to share). The agent reads what exists before generating new voice descriptors — the *intent* may be sharper than what the user can articulate, and existing copy may show it. The agent surfaces what it observes and lets the user confirm or revise.

If the project's `project.yaml.languages` lists multiple languages (per `DESIGN-i18n.md`), the agent flags upfront that voice attributes have cross-language interaction: warm-direct in English may need different lexical choices to read as warm-direct in German. The voice description lives in `brand.yaml.voice` (single source); per-language renderings happen during phase 16 + via the Content Design JSON layer 3 per `DESIGN-content-layers.md`.

## What Claude must establish

The work product is a structured voice record stored under `.website-builder/brand.yaml.voice` (the first write to `brand.yaml` in the pipeline — phase 17 will populate `brand.yaml.tokens`):

1. **Voice description.** One or two sentences in the agent's prose summarizing how this site sounds. *"Warm and direct, like a friend who tells you the truth even when it's inconvenient — never preachy, never apologetic, never glib."* The description is grounded in specifics, not stacked adjectives.

2. **Voice attributes.** 3-5 specific adjectives. Not "professional" — "rigorous", "quietly confident", "plainspoken". The agent challenges generic words; reaches for the attribute corpus in `${CLAUDE_PLUGIN_ROOT}/reference-corpus/voice-archetypes/` when the user struggles to find words.

3. **Nielsen Norman 4D tone profile.** Each of four dimensions placed on a 3-point scale (or left neutral for that dimension):
   - **Humor:** funny / neutral / serious
   - **Formality:** formal / neutral / casual
   - **Respectfulness:** respectful / neutral / irreverent
   - **Enthusiasm:** enthusiastic / neutral / matter-of-fact

   This is the empirical scaffold beneath the attributes — research from Nielsen Norman Group establishes that tone is comparably profiled along these axes; the agent uses them for cross-checking ("you said 'warm' but you also said matter-of-fact-not-enthusiastic — are those compatible? yes, warm can be quiet").

4. **Say / never-say examples.** 3-5 phrases the brand would say + 3-5 phrases the brand would never say. The never-say list is more diagnostic than the say list — the brand defines itself partly by what it refuses. *Say*: "You're not broken; the world is heavy." *Never say*: "Optimize your wellness journey." The agent surfaces patterns: corporate-AI-cheerleader vocabulary, LinkedIn-buzzword stack, anti-vision phrases from the agent profile, generic-marketing-speak.

5. **1-2 voice exemplars.** Existing brands whose voice the user wants the site to share family with. The agent loads from `${CLAUDE_PLUGIN_ROOT}/reference-corpus/voice-archetypes/` (Mailchimp, Slack, Patagonia, Liquid Death, Stripe, Apple, Notion etc. — each catalogued with their published voice guide) and helps the user pick 1-2 that resonate. Voice exemplars do NOT have to be in the user's industry — Stripe's voice is referenced by writers building consumer wellness brands; what matters is the verbal posture, not the category.

Output schema:

```yaml
voice:
  captured_at: 2026-05-18T16:08:00Z
  description: |
    Warm and direct, like a friend who tells you the truth even when it's
    inconvenient — never preachy, never apologetic, never glib.
  attributes: [warm, direct, contrarian, plainspoken, quietly-confident]
  tone_profile_nn4d:
    humor: neutral           # funny | neutral | serious
    formality: casual        # formal | neutral | casual
    respectfulness: respectful  # respectful | neutral | irreverent
    enthusiasm: matter-of-fact  # enthusiastic | neutral | matter-of-fact
  say:
    - "You're not broken; the world is heavy."
    - "We make things slowly because we make them once."
    - "Here's what I would do — your call."
  never_say:
    - "Optimize your wellness journey."
    - "Unlock your potential."
    - "Revolutionary cutting-edge solutions."
    - "We're committed to excellence."
  exemplars:
    - brand: Patagonia
      url: https://www.patagonia.com
      what_resonates: "Refusal posture; doesn't apologize for the discipline; technical without being clinical."
    - brand: Stripe
      url: https://stripe.com
      what_resonates: "Quiet confidence; assumes intelligence in the reader; never overstated."
  i18n_notes: |
    Voice in DE may need different lexical pacing — German tends to register
    'direct' as terse rather than warm. Phase 16 translation pass will adjust
    sentence rhythm while preserving the four-dimensional profile.
  iteration_count: 2
```

## Gating rules

The agent refuses to advance to phase 6 (wild unstructured content capture) under four conditions:

1. **Empty descriptors only.** When the user can only offer "professional / friendly / approachable / clean" as voice descriptors and cannot ground them in any specific say-example, never-say-example, or exemplar brand, the agent refuses. *Professional* and *friendly* are placeholder words; they map onto dozens of distinct voices in practice. The agent reflects: *"Those words could mean Mailchimp-playful, Stripe-quiet-confident, Slack-helpful, Patagonia-refusal — all 'friendly and approachable' in some sense. Which family is this in? Let me load the voice-archetype corpus and we walk through it."*

2. **Stacked-adjective vagueness.** When the user offers 7+ attributes ("warm, professional, friendly, modern, sleek, trustworthy, approachable, innovative, authentic") and refuses to cut, the agent refuses. Voice is a constraint; 7 attributes is the absence of one. The agent surfaces the cost: phase 16 (copywriting) cannot write to 7 competing attributes; pages drift into average-of-all-attributes = generic. The agent forces a cut to 3-5 by asking which the user would refuse to lose first.

3. **No never-say list, or a never-say list that contradicts the say list.** When the user can list 5 say-examples but cannot list any never-say example, the agent refuses. The never-say discriminates; without it, the say list is unanchored. The agent reflects: *"What would make you cringe to see on this site? What does the bad version sound like? Sometimes finding the never-say is the fastest way to lock the say."* If the say and never-say contradict each other ("would say: cutting-edge innovation; never say: corporate buzzwords"), the agent surfaces the contradiction.

4. **Voice that contradicts phase 3 positioning.** When the captured voice contradicts the positioning paragraph (positioning: "rigorous, quietly confident, refuses to oversell"; voice: "playful, enthusiastic, exclamation-mark-heavy"), the agent refuses. The agent reflects: *"These are pulling against each other. The positioning says 'quiet confidence'; the voice profile says 'enthusiastic'. One of them is the real one — which should the site read as?"* The user picks; the conflicting one gets revised back to consistency.

The override path applies — the user can advance with thin voice and the agent flags that phase 16 will produce thinner copy, phase 17 typographic choices will lean neutral-default, and phase 5 may need to re-fire mid-project when content phases surface the gaps.

## Tools and skills used

- **`AskUserQuestion`** — heavy use. The voice extraction is conversation-shaped; each of the five output parts (description / attributes / NN4D profile / say-never-say / exemplars) emerges via several rounds of questioning + reflecting.
- **`Read`** — to read `.website-builder/project.yaml` (idea + vision + requirements + entity) at phase entry; to read any prior artifact's voice samples when entry mode is non-greenfield (existing site copy, social posts, client emails).
- **`Write` / `Edit`** — to update `.website-builder/brand.yaml.voice`. This is the first write to `brand.yaml` in the pipeline.
- **Reference-data load** — `${CLAUDE_PLUGIN_ROOT}/reference-corpus/voice-archetypes/` is the core corpus, catalogued in `DESIGN-ecosystem-catalog.md`. Each archetype entry has: brand name, public voice guide URL, attributes, NN4D profile, say/never-say excerpts. Agent surfaces 5-10 candidates when the user wants to react to options rather than start cold.
- **`WebFetch`** — used to load voice-guide pages of named exemplars when they're public (Slack's voice guide at api.slack.com/start/designing/voice-tone; Mailchimp's at mailchimp.com/resources/issue-19-brand-voice/; etc.). Fresh-fetched at this phase so training-data drift doesn't matter. Also used when the user names a smaller brand the agent doesn't have catalogued — the agent fetches their site, reads the about + footer + a representative page, and summarizes the voice for the user to confirm.
- **`WebSearch`** — used when the user wants exposure to current voice-guide methodologies (Nielsen Norman's 4D framework, Mailchimp's brand archetype framework, Slack's voice + tone playbook, Bigeye / Frontify / Sprout Social guides) but doesn't have a particular reference in mind.

No subagent spawn by default. When the user wants to parallel-explore 5 exemplar brands at once, agent may spawn a research subagent — but the default is in-person walkthrough so each exemplar becomes a real anchor for the voice discussion.

No context7 (no library docs at this phase). No Playwright. No `Bash` beyond `ls`-style asset inventory if voice exemplar PDFs / files are in the user's local project.

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| `.website-builder/brand.yaml` | adds `voice:` key per schema above (FIRST write to `brand.yaml` — file is created here) | Voice description + attributes + NN4D + say/never-say + exemplars; load-bearing for phase 16 copywriting + phase 17 design-system type-pairing + phases 5 reads at every later content-touching phase |
| `.website-builder/decisions/05-voice-archetype.md` *(optional)* | Standard decision-doc frontmatter + body with alternatives considered + reasoning | Created when voice required deliberate tradeoff (e.g., "warm + matter-of-fact" was chosen over "warm + enthusiastic"; both could have worked) |

The `brand.yaml.voice` block is the required artifact. The decision log is created when the choice was non-obvious, per the canonical decision-doc pattern in `DESIGN-project-scaffold.md`.

The agent updates `.website-builder/project.yaml.current_phase` to `6` upon user confirmation. Phase 6 (wild unstructured content capture) loads next — the entry to the content-foundation phase group.

## Common failure modes

**The user picks "all of the above" — wants the site to sound warm AND authoritative AND playful AND quietly confident AND clinical when needed.** The agent surfaces tradeoffs: *"Some of these are compatible (warm + quietly confident); some pull against each other (playful + clinical; warm + authoritative-distant). The site has one dominant register that can flex slightly per page. Which is the *dominant*? Where can it flex?"* The agent uses the NN4D profile to clarify — if the user can name *one* point per dimension, the attribute list reorders into a hierarchy (primary attributes vs flex range).

**The user offers "professional" as the only descriptor.** *"I want it to sound professional."* The agent refuses (per gating rule 1) and reflects: *"Every site says 'professional.' That word maps onto a Swiss bank's voice AND a brutalist editorial magazine AND a B2B SaaS startup. Where in that space?"* Then loads `voice-archetypes/` and walks through 5 contrasting "professional" examples.

**The user names a voice exemplar that contradicts the positioning.** *"The voice should be like Liquid Death — irreverent, edgy, contrarian."* But phase 3 positioning is "rigorous, quietly confident, refuses to oversell." The agent surfaces: *"Liquid Death's voice is irreverent-loud-confrontational; your positioning is rigorous-quiet-confident. Either the positioning needs to be revised (we can do that) or the exemplar needs to be revised. Which is the real anchor — the positioning or the Liquid Death feel?"* The user picks; the contradiction resolves before phase 16 inherits it.

**The user can list say-examples but freezes on never-say-examples.** *"I don't know what we wouldn't say."* The agent prompts with concrete anti-patterns: *"What would make you cringe? Try these — would you say 'Unlock your potential'? 'Cutting-edge solutions'? 'Game-changing experience'? 'We're passionate about delivering value'?"* These corporate-AI-cheerleader phrases (which are also in the agent's own anti-vision lock per `agents/website-builder.md`) usually surface immediate refusal — *"god no, never that"* — and the user can build out from those.

**The user's existing site already has voice; the user wants to keep it.** Agent reads the existing copy and reflects: *"The existing site has these patterns — short declarative sentences, contractions throughout, no exclamation marks, no superlatives. NN4D profile reads: neutral humor / casual formality / respectful / matter-of-fact. Does that match what you want to keep, or has your thinking evolved?"* If keep — capture as voice. If evolved — the new voice is captured and the existing copy gets the "to-be-rewritten" tag at phase 6.

**The voice extracted reads identical to a competitor named in phase 3.** The agent surfaces: *"This voice profile is very close to [competitor]'s public voice guide. Is the goal to share their voice family, or to differentiate? Both are valid — sites in the same family with shared voice can co-exist by visual register or by audience — but the choice should be deliberate, not accidental."* The user decides intentional-shared-family or intentional-differentiation.

**The user is uncomfortable with the say/never-say exercise — feels constraining.** The agent reframes: *"The never-say isn't a constraint; it's a clarification. Phase 16 (copywriting) has to know what to avoid. Without a never-say list, AI-generic phrasing drifts in by default — that's the failure mode the discipline prevents. Let's just write down what you'd cringe at; it'll come naturally."* Usually 3-5 phrases surface without resistance once the framing changes.

**Multi-language site: voice attributes read fine in English but the user is unsure how they'll translate.** The agent flags + defers: *"Voice profile lives at this layer; lexical-level translation happens at phase 16 with the translator-pattern from `DESIGN-i18n.md`. The four-dimensional profile is language-neutral; the specific attribute words and say/never-say examples will need per-language analogues at phase 16. Capture the English version now; we'll surface DE/FR/IT translation needs at phase 16."* The `voice.i18n_notes` field records the deferred items.

**The user wants the site to sound nothing like them personally — they're building a brand, not exposing themselves.** The agent honors: *"Voice is the brand's persona, not yours. Plenty of solo practitioners build brands that sound different from how they speak in person — that's a legitimate choice. Capture the brand's voice; we don't need it to match how you'd speak at dinner."* The voice record captures the brand voice; the user's personal voice can be a separate consideration if relevant (e.g., for video content phases handled by the post-launch maintainer).

**The brand archetype the user reaches for is unfamiliar to the agent.** The agent (with permission) WebFetches the brand's public voice guide or representative copy, then reads-aloud the inferred profile back to the user for confirmation: *"From their about page and three product pages, here's the profile I'm reading: [X]. Does that match what you wanted to reference, or were you reaching at something else in them?"*

## Reference materials

- **Design doc — phase pipeline source:** `DESIGN-phase-contracts.md` § 5 (seed for this contract)
- **Design doc — pipeline integration:** `DESIGN-architecture.md` § Phase contracts
- **Design doc — voice-output layer (CDJSON):** `DESIGN-content-layers.md` § Layer 3 — Content Design JSON (microcopy + UI strings) — the voice lives in `brand.yaml.voice`; phase 16 + content phases write strings that reflect it; the methodology source for that pattern is https://uxcontent.com/content-design-json/
- **Design doc — multi-language voice interaction:** `DESIGN-i18n.md` § Translation workflow (per-language voice rendering happens at phase 16; this phase captures the language-neutral profile)
- **Design doc — voice-archetype corpus catalogue:** `${CLAUDE_PLUGIN_ROOT}/reference-corpus/ECOSYSTEM-CATALOG.md` § Reference resources (catalog entry for `voice-archetypes/`)
- **Plugin corpus — voice archetypes:** `${CLAUDE_PLUGIN_ROOT}/reference-corpus/voice-archetypes/` — catalogued brand voice exemplars with public voice-guide URLs, NN4D profiles, say/never-say excerpts
- **External methodology (loaded fresh 2026-05-18 for this contract):**
  - Nielsen Norman Group — The Four Dimensions of Tone of Voice — https://www.nngroup.com/articles/tone-of-voice-dimensions/ (the empirical scaffold this contract uses: humor / formality / respectfulness / enthusiasm, each as a 3-point scale)
  - Nielsen Norman Group — The Impact of Tone of Voice on Users' Brand Perception — https://www.nngroup.com/articles/tone-voice-users/ (research grounding why voice matters in UX context)
  - Mailchimp — Brand Archetypes guide — https://mailchimp.com/resources/brand-archetypes/ (Jungian-rooted 12-archetype framework; useful when the user wants typology starting points)
  - Mailchimp — Brand Voice essay — https://mailchimp.com/resources/issue-19-brand-voice/ ("Fun but not silly. Confident but not cocky. Smart but not stodgy." — a canonical short voice description; agent uses as a model for the description field)
  - Slack — Voice and Tone for app design — https://api.slack.com/start/designing/voice-tone (Slack's "clear, concise, and human, like a friendly, intelligent coworker" — a canonical voice guide referenced when users want B2B-tool-shaped voice references)
  - Bigeye — Ultimate Guide to Brand Voice Frameworks — https://www.bigeyeagency.com/insights/ultimate-brand-voice-frameworks-guide
  - Frontify — Brand Voice Examples — https://www.frontify.com/en/guide/brand-voice-examples
- **Agent profile — voice-related anti-patterns:** `${CLAUDE_PLUGIN_ROOT}/agents/website-builder.md` § Anti-pattern cheat sheet ("sounding like a corporate AI cheerleader" — the agent's own anti-vision applies as a useful never-say list seed for many users)
