# Voice-archetype frameworks — phases 4-5

> Loaded on demand when running phase 5 (Brand voice & tone) and the entity-tone read in phase 4. The phase-5 contract (`phase-contracts/05-brand-voice-tone.md`) is authoritative for *what* phase 5 produces (description / attributes / NN4D profile / say-never-say / exemplars) and the gating rules. This file carries the three frameworks the agent reaches for when the user struggles to find voice words. Researched fresh 2026-05-18 — see Sources at bottom.

## When this fires

The user can only offer empty descriptors ("professional / friendly / approachable") and cannot ground them in a say-example, never-say-example, or exemplar brand. The phase-5 contract refuses advancement on empty-descriptors-only. These frameworks give the user typology starting points to react to — they are *scaffolds for finding words*, not a substitute for the user's own say/never-say (cross-phase discipline rule 3: never author the load-bearing artifact for them).

Use them in this order of preference: NN4D first (it is the empirical scaffold the phase-5 contract is built on), then Aaker for personality dimensions, then Jung archetypes for narrative posture. Do not dump all three on the user at once — pick the one that fits where they are stuck.

## Framework 1 — Nielsen Norman 4-Dimensional tone (the primary scaffold)

This is the empirical scaffold the phase-5 contract uses for the `tone_profile_nn4d` artifact. Four independent dimensions, each placed on a 3-point scale (or neutral):

| Dimension | Pole A | Neutral | Pole B |
|---|---|---|---|
| **Humor** | funny | neutral | serious |
| **Formality** | formal | neutral | casual |
| **Respectfulness** | respectful | neutral | irreverent |
| **Enthusiasm** | enthusiastic | neutral | matter-of-fact |

Use it as a cross-check: *"You said 'warm' but also 'matter-of-fact, not enthusiastic' — compatible? Yes: warm can be quiet."* When the user can name one point per dimension, the attribute list reorders into a hierarchy (primary attributes vs flex range). NNG's research establishes that tone of voice measurably shifts brand perception along these axes — this is why the 4D profile is a required phase-5 artifact, not optional color.

## Framework 2 — Aaker's 5 brand-personality dimensions

Jennifer Aaker's framework — five dimensions, each with sub-traits. Useful when the user can describe a *feeling* but not a *register*; map the feeling onto a dimension, then pull the sub-trait that fits.

| Dimension | Sub-traits | Example posture |
|---|---|---|
| **Sincerity** | down-to-earth, honest, wholesome, cheerful | Patagonia-ish: plain, trustworthy, unpretentious |
| **Excitement** | daring, spirited, imaginative, up-to-date | Liquid Death-ish: bold, contrarian, energetic |
| **Competence** | reliable, intelligent, successful, leader | Stripe-ish: assured, precise, assumes intelligence |
| **Sophistication** | upper-class, glamorous, charming, romantic | luxury-editorial: refined, restrained, elevated |
| **Ruggedness** | outdoorsy, tough, masculine, rugged | technical-outdoor: durable, no-frills, grounded |

A brand usually leads with ONE dimension and borrows one sub-trait from a second. Use it to break "professional" — *"Competence-professional (Stripe-quiet) or Sophistication-professional (luxury-editorial)? Different voices entirely."* Maps cleanly into the phase-5 `attributes` list.

## Framework 3 — Jung's 12 brand archetypes (narrative posture)

Carl Jung's universal patterns applied to brand. Useful when the user thinks in *stories / personalities* rather than adjectives. Each archetype carries a built-in say/never-say tendency.

| Archetype | Core drive | Exemplar | Voice tendency |
|---|---|---|---|
| Innocent | optimism, purity | Coca-Cola | warm, simple, hopeful — never cynical |
| Everyman | belonging, realism | IKEA | plain, inclusive, unpretentious — never elitist |
| Hero | courage, triumph | Nike | bold, motivating, decisive — never timid |
| Outlaw | revolution, disruption | Harley-Davidson | contrarian, raw, defiant — never compliant |
| Explorer | adventure, freedom | The North Face | independent, restless, expansive — never settled |
| Creator | innovation, vision | Apple | inventive, precise, aspirational — never derivative |
| Ruler | control, leadership | Mercedes | authoritative, composed, premium — never chaotic |
| Magician | transformation, dreams | Disney | visionary, wondrous, transformative — never mundane |
| Lover | passion, intimacy | (luxury / beauty) | sensory, intimate, devoted — never clinical |
| Caregiver | nurturing, protection | Johnson & Johnson | reassuring, gentle, protective — never cold |
| Jester | joy, humour | Ben & Jerry's | playful, irreverent, light — never pompous |
| Sage | wisdom, expertise | Google | clear, knowledgeable, calm — never glib |

The "never" column is a fast path to the phase-5 never-say list — pick the archetype, the contradicting register becomes the never-say seed.

## Using the three together at phases 4-5

- **Phase 4 (entity-tone read):** the entity what-they-do sentence has an implicit register. Use Aaker to name it lightly so it composes with phase-3 positioning vocabulary — do not over-engineer; phase 4 is short.
- **Phase 5 (full voice):** NN4D is the required scaffold (4D profile is a deliverable). Aaker breaks empty descriptors into dimensions → attributes. Jung gives narrative posture + a fast never-say seed. The frameworks *converge*: a Sage archetype reads as Competence-dominant (Aaker) with serious-humor / neutral-formality / respectful / matter-of-fact (NN4D). When they diverge for a given user, the user's own say/never-say examples are the tiebreaker — frameworks scaffold, examples decide.

## Guardrails (carry the SKILL.md cross-phase discipline)

- Frameworks are scaffolds to *find words*, never the final voice. The user owns the say/never-say.
- The captured voice MUST compose with phase-3 positioning. If an archetype the user reaches for contradicts the positioning (e.g., Outlaw voice vs "rigorous, quietly confident" positioning), surface the contradiction and force a choice — do not silently let both stand (phase-5 gating rule 4).
- Voice exemplars need not be in the user's industry — Stripe's voice is referenced by wellness brands; what transfers is verbal posture, not category.
- For multi-language projects, the NN4D profile is language-neutral; specific attribute words + say/never-say need per-language analogues at phase 16 (record deferred items in `voice.i18n_notes` per the phase-5 contract + `DESIGN-i18n.md`).
- The plugin's own anti-vision (corporate-AI-cheerleader phrasing per `${CLAUDE_PLUGIN_ROOT}/agents/website-builder.md` § Anti-pattern cheat sheet) is a reliable universal never-say seed — "unlock your potential", "cutting-edge solutions", "we're passionate about delivering value" usually trigger immediate user refusal and unlock the never-say list.

## Sources (researched 2026-05-18)

- [Define Brand Personality with Jungian Archetypes (Umbrex)](https://umbrex.com/resources/frameworks/marketing-frameworks/brand-archetypes-framework-jungian-archetypes/)
- [Brand Personality vs Archetypes: What's the Difference? (Britopian)](https://www.britopian.com/content/brand-personality/)
- [Brand Personality Framework (Bonfire)](https://bonfireci.com/brand-personality-framework/)
- [Branding Psychology: Archetypes for Strong Voice & Copy (Phoebe Lown)](https://www.phoebelown.com/blog/using-archetypes-to-build-tone-of-voice)
- [How brand archetypes create a cohesive brand voice in the age of AI (Toast Studio, updated 2025)](https://www.toaststudio.com/en/articles/brand-archetypes-a-new-way-to-approach-tone-and-manner-in-content-marketing/)
- Nielsen Norman Group — The Four Dimensions of Tone of Voice + The Impact of Tone of Voice on Users' Brand Perception (cited in the phase-5 contract's own external-research list; NN4D is the contract's empirical scaffold)
