# `reference-corpus/voice-archetypes/`

> Eight reference voices spanning the verbal-identity spectrum. The agent reads these at phases 4-5 to give a stuck user *typology starting points to react to* — concrete voices with worked sample copy — never to author the user's voice for them. Each archetype is grounded in the three frameworks the plugin's phase-5 contract is built on: **NN4D** (Nielsen Norman's 4 tone dimensions), **Aaker** (5 brand-personality dimensions), and **Jung** (12 brand archetypes). The frameworks scaffold; the user's own say / never-say examples decide.

## What's here

| File | Voice | NN4D shorthand | Aaker | Jung | One-liner |
|---|---|---|---|---|---|
| `calm-expert.md` | Calm Expert | serious · formal-neutral · respectful · matter-of-fact | Competence | Sage | Quiet authority that assumes the reader is smart. |
| `warm-guide.md` | Warm Guide | neutral · casual · respectful · enthusiastic | Sincerity | Caregiver | Reassuring hand-on-the-shoulder expert. |
| `playful-challenger.md` | Playful Challenger | funny · casual · irreverent · enthusiastic | Excitement | Jester | Irreverent, contrarian, allergic to corporate. |
| `bold-motivator.md` | Bold Motivator | serious · casual · respectful · enthusiastic | Excitement / Ruggedness | Hero | Second-person imperatives that push you to act. |
| `refined-luxe.md` | Refined Luxe | serious · formal · respectful · matter-of-fact | Sophistication | Lover / Ruler | Restrained, sensory, lets silence do the work. |
| `everyman-plainspoken.md` | Plainspoken Everyman | neutral · casual · respectful · matter-of-fact | Sincerity | Everyman | Plain, inclusive, jargon-free — says it straight. |
| `warm-contrarian.md` | Warm Contrarian | neutral-funny · casual · irreverent-but-kind · enthusiastic | Sincerity / Excitement | Outlaw (tempered) | Takes a stance against the industry, stays kind. |
| `visionary-creator.md` | Visionary Creator | serious · neutral · respectful · enthusiastic | Competence / Sophistication | Creator | Inventive and precise; sells the future, plainly. |

The eight are chosen to *spread* across the NN4D space rather than cluster: serious↔funny, formal↔casual, respectful↔irreverent, matter-of-fact↔enthusiastic each have voices at both poles. Together they give a stuck user enough contrast to point and say "that one, not that one" — which is what unlocks their own words.

## How the agent uses this dir

- **Phase 4 (entity-tone read):** the user's "what we do" sentence has an implicit register. Skim the table to name it lightly so it composes with phase-3 positioning — don't over-engineer; phase 4 is short.
- **Phase 5 (brand voice & tone):** the primary consumer. When a user can only offer empty descriptors ("professional / friendly / approachable") and cannot ground them in a say-example or exemplar, surface ONE archetype that fits where they're stuck (per the framework-preference order: NN4D first, then Aaker, then Jung). Read its `## Sample copy` aloud as a reaction-prompt; use its `## Say / never-say` to seed the user's own lists. The user reacts, adjusts, and lands on their own voice — the archetype is the scaffold, never the deliverable.

**Discipline (carried from `skills/wb-discovery/references/voice-archetype-frameworks.md`):** never dump all eight (or all three frameworks) on the user at once — pick the one that fits. The captured voice MUST compose with phase-3 positioning; if an archetype the user reaches for contradicts it, surface the contradiction and force a choice (phase-5 gating rule 4). Voice exemplars need not be in the user's industry — what transfers is verbal posture, not category. For multi-language projects the NN4D profile is language-neutral; per-language attribute words are a phase-16 deferral.

## How to read each file

Every archetype follows one shape: **Voice description → Framework grounding (NN4D / Aaker / Jung) → Attributes → Say / never-say → Sample copy (hero + CTA + microcopy) → Best for / avoid for.** The `## Sample copy` section is the load-bearing part for phase 5 — it is the concrete artifact the user reacts to.

## Provenance & licensing

Every file is **original reference prose** written for the website-builder plugin — plugin-owned and freely usable. The frameworks summarized are publicly documented: Nielsen Norman Group's *Four Dimensions of Tone of Voice*, Jennifer Aaker's *Dimensions of Brand Personality* (1997), and Carl Jung's archetypes as applied to branding. Exemplar brands named (Stripe, Nike, IKEA, Apple, Patagonia, etc.) are referenced to illustrate a *verbal posture* — their trademarks remain © their owners; no brand's copy is reproduced. Sample copy is invented for fictional businesses.

## See also

- `skills/wb-discovery/references/voice-archetype-frameworks.md` — the canonical NN4D / Aaker / Jung reference these archetypes operationalize (and the phase-4/5 firing rules).
- `../brand-examples/` — complete brand systems whose `## Voice & tone` sections show a single voice fully dressed with tokens + components.
- `../component-patterns/` — microcopy slots (CTA labels, form errors, empty states) inherit voice from the chosen archetype.
- `Workstreams/website-builder/foundation/DESIGN-architecture.md` §330 — the spec this dir satisfies.
