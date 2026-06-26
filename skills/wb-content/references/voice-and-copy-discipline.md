# Phase 16 — Voice & Copy Discipline

Detailed patterns for the phase-16 copywriting workflow. The discipline of this phase is voice. Source of truth: `Projects/Jules.Solutions/Subprojects/website-builder/phase-contracts/16-copywriting.md` + `.website-builder/brand.yaml.voice` (phase-5 output, the voice contract).

## The two refusals

1. **Placeholder copy on a deployed site** — lorem ipsum, `[headline here]`, `TODO: write this`, `(write this)`, empty string-keys, any slot still holding a phase-15 placeholder spec. **Not overridable** — a site with placeholder copy is broken; phase 17 would design around the hole.
2. **AI-generic LinkedIn-speak** — the flattened voiceless register LLMs default to. Overridable with explicit confirmation (the user may want a deliberately different register for a specific section, or accept a flagged phrase).

## The AI-generic LinkedIn-speak phrase bank

Refuse copy that pattern-matches this register. Non-exhaustive — also catch the *register* even when the exact phrase isn't listed:

- "unlock your potential" / "unlock the power of"
- "optimize your X journey" / "take your X to the next level"
- "we help businesses succeed" / "empowering businesses to..."
- "in today's fast-paced world" / "in today's digital landscape"
- "seamless" / "cutting-edge" / "innovative" / "robust" / "leverage" / "synergy" / "best-in-class" / "game-changing" / "revolutionary" as filler adjectives/verbs
- "elevate" / "supercharge" / "transform your..." as empty intensifiers
- Any sentence that "could be on any of ten thousand sites" — says nothing specific, sounds like nobody.

The phase-5 `never_say` exemplars are the explicit per-project reference; this bank catches the generic register beyond the explicit list.

### The before/after teaching pattern

When LinkedIn-speak slips in, do not just rewrite silently. Surface it and teach:

> *"This sentence could be on any of ten thousand sites — it says nothing specific and sounds like nobody. Your voice (from phase 5) is warm, direct, slightly contrarian. What does this section actually mean, said the way you'd say it to a friend?"*

Then show before/after so the user learns to catch it themselves:

> Before: *"We help businesses unlock their potential through innovative solutions."*
> After (warm-direct-contrarian): *"You don't need another tool. You need the thing you already do to actually work. That's what this is."*

## The voice cross-check ("read it aloud")

Phase 5 captured: a voice description, 3-5 attributes, say/never-say exemplars, 1-2 voice-exemplar brands. Phase 16 writes every word against that and cross-checks:

1. Re-read `.website-builder/brand.yaml.voice` **per section** — not once at the start; per section, because drift accumulates.
2. After writing a section, read it against the phase-5 exemplars: does this sound like the brand, or like generic AI marketing copy?
3. Read the whole site together at the end: if the hero sounds warm and the FAQ sounds like a legal disclaimer, voice is drifting. Common because different sections "feel like they should" sound different.
4. WebFetch the phase-5 `exemplar_brands` live site(s) and study their actual microcopy + headline register to calibrate the cross-check against a real example (studied for voice, never copied — per `DESIGN-templates-catalog.md`).

Voice-drift gate is overridable with explicit confirmation; the rewrite-to-locked-voice is the default action.

## Getting the user's words (never invent substance)

The brand's voice is theirs, not the agent's to invent. For sections where the user has raw material, draw from `.website-builder/inbox/INVENTORY.md` (phase-6 source content). Where they have nothing, use the phase-6 fallback — guided freewriting prompts, voice-note transcription, structured questions — to generate raw material the agent then *shapes*. The shaping is the agent's; the substance is the user's.

The premature-handoff move: *"just write all the copy for me — you know what's good."* Refuse:

> *"The words have to be yours or they'll read like every other AI-written site. Give me the raw material — what actually happened, in your words — and I'll shape it to the voice without flattening it. The shaping is mine; the substance is yours."*

## Microcopy carries voice too

The most-abandoned place. Users write brand-voiced headlines then leave loading/error/success as "Loading…", "An error occurred", "Success". Microcopy is where voice is *most* distinctive and *most* often dropped — the moments a user is most frustrated or most relieved.

> *"These three strings are the moments a user is most frustrated or most relieved — exactly where your voice matters most. 'An error occurred' is nobody's voice. What does your brand say when something breaks?"*

Mukti's canonical example — "FOUR different ways to say 'transaction failed' across one platform" — is the inconsistency a single Content Design JSON source prevents (see `references/content-design-json.md`). Phase 16 is where that single source gets its voiced values.

## The placeholder-copy exit sweep

Before allowing advance to phase 17: sweep every `content/pages/*.md` and every `strings/*.json`. Any lorem ipsum, `[...]`, `TODO`, `(write this)`, empty string-key, or surviving phase-15 placeholder spec → refuse, surface every one, do not advance until all resolved. **Not overridable.**

## Common failure modes (phase 16)

| Failure | Recovery |
|---|---|
| "Just write all the copy for me" | The premature-handoff refusal above. Raw material from the user; shaping from the agent. |
| AI-generic LinkedIn-speak | The phrase bank + before/after teaching pattern. Reads as "professional" to muggles — most insidious failure. |
| Voice drift across the site | Read whole site against phase-5 exemplars; rewrite drifting sections to the locked voice. Even error messages sound like the same brand. |
| Placeholder surviving to deploy | The exit sweep. Not overridable. |
| "German translation can wait until after launch" | Decision 39 (Pattern A) = all configured-language pages exist at launch. Decision 41 fallback is a render-time safety net, not a license to ship half-translated. Recommend Pattern 2 for high-stakes copy. See `references/i18n-translation-workflow.md`. |
| Microcopy left voiceless | The microcopy prompt above. Loading/error/success are where voice matters most. |
| Copy contradicts the wireframe's space | Phase 14 gave the hero one line; copy is a 3-line paragraph. Surface the structural conflict; tighten copy to the wireframe OR flag a thin phase-14 revision. Copy and structure must agree before phase 17. |
| "Phase 17 will fix weak copy with design" | It will not. Design *amplifies* copy: strong copy designed well is strong; weak copy designed well is weak copy that looks expensive. Words carry their own weight first. |

## Output artifact schemas (phase 16)

- `.website-builder/content/pages/{slug}.md` — placeholders replaced with finalized prose; `status:` promoted `draft` → `active`; `seo_title`/`seo_description` finalized prose (phase 26 may refine).
- `.website-builder/content/strings/${default_language}.json` — every key valued, in voice (including loading/success/error states; ICU plurals for variable copy).
- Multilingual: `content/pages/{slug}.{lang}.md` (Pattern A: shared frontmatter, translated body) + `content/strings/{lang}.json` per language + `briefs/translation-{lang}-{ts}.json` for Pattern 2 handoff. See `references/i18n-translation-workflow.md`.

Exact worked schemas in the phase-16 contract `## Output artifacts`.
