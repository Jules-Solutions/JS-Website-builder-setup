# `reference-corpus/brand-examples/`

> 7 **complete, internally-coherent brand systems** the agent reads as worked examples of "what a finished brand looks like." Each one carries the full stack — positioning → voice & tone → design tokens (OKLCH) → component patterns → do/don'ts — so the agent can see how voice and visuals reinforce one *single intentional thing*, not forty disconnected screens.

## Why these exist

A muggle says "make it feel warm and handmade" or "make it look serious and precise." The agent needs reference points that show what those words become as a *complete system*: a warm voice with a warm palette and rounded components; a precise voice with a cool palette and tight components. These exemplars span the archetypes a small-site brief most often lands on, so the agent always has a nearby, fully-worked example to reason from (never to copy verbatim).

## The seven

| File | Brand | Archetype | Voice in one word | Vibe |
|---|---|---|---|---|
| `hearthstone-bakery.md` | Hearthstone Bakery | Local artisan food / craft | Warm | Earthy, generous, homemade |
| `northbeam.md` | Northbeam | B2B SaaS / analytics | Precise | Cool, confident, technical |
| `lumen-wellness.md` | Lumen Wellness | Wellness / studio | Calm | Soft, grounding, unhurried |
| `voltic.md` | Voltic | Fitness / performance | Bold | High-contrast, electric, direct |
| `marigold-and-co.md` | Marigold & Co. | Editorial / lifestyle blog | Literary | Warm-neutral, sensory, personal |
| `atelier-nord.md` | Atelier Nord | Architecture / design studio | Spare | Monochrome, exacting, premium |
| `pip-and-parsnip.md` | Pip & Parsnip | Kids' education / family | Cheerful | Bright, friendly, simple |

The spread is deliberate: warm↔cool, calm↔bold, serif↔sans, light↔dark-leaning, consumer↔B2B. Together they bracket most of the small-site aesthetic space.

## How the agent uses this dir

- **Phase 2 (vision) / Phase 5 (voice):** match the user's stated direction to the nearest archetype; read that brand's *voice & tone* section as a model for how to write the project's own.
- **Phase 17 (design system):** read the *tokens* block as a complete, coherent worked example (OKLCH ramp + type pairing + spacing + motion that all agree with the voice). Generate the project's own tokens in the same shape — **do not copy these values**.
- **Phase 18 (components):** read the *component patterns* section for how each brand expresses buttons/cards/inputs consistently with its tokens.

## Token format

Every brand's color/type/spacing/motion block mirrors the plugin's `brand.yaml.tokens` schema exactly (OKLCH decimal-L color form, 4px spacing base, named type scale, motion tokens, light + dark surface sets) — see `phase-contracts/17-design-system.md`. This means an exemplar can be read as a literal, valid example of the phase-17 output.

## Provenance & licensing

**All seven brands are original and fictional**, authored for the website-builder plugin. Names, palettes, copy, and positioning are invented; any resemblance to a real company is coincidental. This content is plugin-owned (CC0-equivalent) and freely usable. The *shape* of a complete brand doc was informed by the real `Agents/Skills/design/_shared/brands/jules-solutions/` brand (Jules.Solutions) as a structural reference only — none of that brand's content is reproduced here. Fonts named (Fraunces, Inter, Space Grotesk, etc.) are real, open-licensed Google Fonts referenced by name, not bundled.

## See also

- `../design-systems/` — foundational *design* systems (Material/Apple/Carbon/Tailwind/Radix) vs. these complete *brand* systems.
- `DESIGN-architecture.md` §328 — the spec this dir satisfies.
