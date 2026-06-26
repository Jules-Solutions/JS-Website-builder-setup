---
type: REFERENCE
corpus: brand-examples
title: Lumen Wellness
archetype: Wellness / studio
provenance:
  authored: Original fictional brand for the website-builder plugin (CC0-equivalent)
  resemblance: Invented; any resemblance to a real studio is coincidental
consumed_by_phases: [2, 5, 17, 18]
---

# Lumen Wellness

> A small yoga + breathwork studio. Unhurried, grounding, quietly premium.

**Positioning:** "Room to breathe." Lumen sells calm and space. The brand is restrained on purpose — generous whitespace, soft palette, slow motion. Everything signals "you can slow down here."

## Voice & tone

- **Attributes:** calm, gentle, grounding, sincere, present. Never clinical, never woo.
- **Sounds like:** an experienced teacher with a low, steady voice — invitational, not instructional.
- **Do:** use simple, sensory, present-tense language ("settle in," "soften your shoulders"); short lines with breathing room; invite rather than command.
- **Don't:** use hustle language, superlatives, medical claims, or spiritual cliché ("manifest your best self"). No exclamation marks.

**Sample lines**
- Hero: *"Slow mornings. Steady breath. A practice that meets you where you are."*
- CTA: *"Find a class"* / *"Begin"*
- Booking: *"Saturday, 8am — Gentle Flow. Six spaces left."*

## Color tokens (OKLCH)

```yaml
color_space: oklch
color:
  primary:   "oklch(0.62 0.06 155)"    # soft sage
  secondary: "oklch(0.78 0.05 60)"     # warm sand
  neutral:                              # gentle warm-cool balance
    "50":  "oklch(0.98 0.006 120)"
    "100": "oklch(0.96 0.008 120)"
    "300": "oklch(0.88 0.01 130)"
    "500": "oklch(0.64 0.012 140)"
    "700": "oklch(0.44 0.012 150)"
    "900": "oklch(0.26 0.012 155)"
  semantic:
    success: "oklch(0.66 0.10 155)"
    warning: "oklch(0.82 0.10 80)"
    danger:  "oklch(0.62 0.14 30)"
    info:    "oklch(0.72 0.06 220)"
  surface:                              # light, airy
    background:       "oklch(0.99 0.006 120)"   # barely-there warm white
    foreground:       "oklch(0.30 0.012 155)"
    muted:            "oklch(0.96 0.008 120)"
    muted_foreground: "oklch(0.52 0.012 145)"
    border:           "oklch(0.92 0.008 130)"
    ring:             "oklch(0.62 0.06 155)"
  surface_dark:                         # dim, candle-lit evening mode
    background:       "oklch(0.24 0.012 155)"
    foreground:       "oklch(0.95 0.008 120)"
    muted:            "oklch(0.30 0.012 155)"
    muted_foreground: "oklch(0.74 0.01 140)"
    border:           "oklch(0.36 0.012 155)"
    ring:             "oklch(0.66 0.07 155)"
```

## Typography

```yaml
typography:
  display: { family: "Cormorant Garamond", fallback: "serif", source: "google-fonts" }  # light, elegant
  body:    { family: "Nunito Sans",        fallback: "sans-serif", source: "google-fonts" }
  scale_ratio: 1.200                    # Minor Third — soft, low-contrast hierarchy
  scale:
    h1:   { size: "2.488rem", lh: "1.15", weight: 500 }
    h2:   { size: "2.074rem", lh: "1.2", weight: 500 }
    h3:   { size: "1.728rem", lh: "1.3", weight: 400 }
    body: { size: "1.0625rem", lh: "1.7", weight: 400 }   # extra line-height = calm
    small:{ size: "0.875rem", lh: "1.6", weight: 400 }
```

## Spacing, radius, motion

```yaml
spacing: { base_unit: "4px", scale: [0,4,8,12,16,24,32,48,64,96,128,160] }  # extra-roomy top end
radius:  { base: "14px", note: "soft, pebble-like" }
motion:
  duration_default: "380ms"             # deliberately slow
  easing_default:   "cubic-bezier(0.33, 1, 0.68, 1)"      # very gentle ease-out
  preference:       "subtle"
  reduced_motion:   "duration → 0ms; opacity-only transitions retained"
```

## Component patterns

- **Buttons:** soft sage fill or quiet outline, 14px radius, slow fade on hover. Calm, never urgent.
- **Cards:** lots of whitespace, single soft image, minimal text, generous 32px padding. The space is the design.
- **Inputs:** low-contrast border, gentle focus ring, comfortable height, labels above.
- **Imagery:** soft natural light, plants, linen, hands, negative space. Muted, never saturated.
- **Icons:** thin-stroke (1.25px) line icons, used minimally.

## Do / Don't

- **Do:** maximize whitespace, slow the motion, keep contrast low and the palette soft. Let pages feel empty in a good way.
- **Don't:** crowd the layout, use urgent CTAs, saturate colors, or speed up animation. Density and urgency break the entire promise of the brand.
