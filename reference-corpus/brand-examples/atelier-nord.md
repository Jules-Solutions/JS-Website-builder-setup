---
type: REFERENCE
corpus: brand-examples
title: Atelier Nord
archetype: Architecture / design studio
provenance:
  authored: Original fictional brand for the website-builder plugin (CC0-equivalent)
  resemblance: Invented; any resemblance to a real studio is coincidental
consumed_by_phases: [2, 5, 17, 18]
---

# Atelier Nord

> A small architecture & interiors studio. Spare, exacting, confident. The work speaks.

**Positioning:** "Less, resolved." Atelier Nord is minimalism done with rigor — a near-monochrome palette, one restrained accent, enormous whitespace, and a grid you can feel. The brand sells taste and precision; the portfolio images do the selling.

## Voice & tone

- **Attributes:** spare, precise, understated, confident. Says little, means it.
- **Sounds like:** an architect describing a decision in one clean sentence — no adjectives wasted.
- **Do:** write short; let nouns carry weight; state, don't sell; use specifics (materials, year, location).
- **Don't:** gush, over-explain, or use marketing superlatives. Whitespace is the rhetoric.

**Sample lines**
- Hero: *"Atelier Nord — architecture and interiors. Stockholm."*
- CTA: *"View work"* / *"Enquire"*
- Project caption: *"Coastal House, Gotland · 2024 · timber, lime plaster, glass."*

## Color tokens (OKLCH)

```yaml
color_space: oklch
color:
  primary:   "oklch(0.50 0.04 250)"    # muted slate — the single restrained accent
  secondary: "oklch(0.62 0.03 60)"     # warm stone (used rarely)
  neutral:                              # near-monochrome, subtle warm tint
    "50":  "oklch(0.98 0.003 80)"
    "100": "oklch(0.95 0.004 80)"
    "300": "oklch(0.86 0.005 75)"
    "500": "oklch(0.58 0.006 70)"
    "700": "oklch(0.36 0.006 65)"
    "900": "oklch(0.18 0.006 60)"
  semantic:
    success: "oklch(0.62 0.10 150)"
    warning: "oklch(0.78 0.10 80)"
    danger:  "oklch(0.56 0.16 28)"
    info:    "oklch(0.58 0.06 240)"
  surface:                              # light, gallery-white
    background:       "oklch(0.99 0.003 85)"
    foreground:       "oklch(0.18 0.006 60)"
    muted:            "oklch(0.96 0.004 80)"
    muted_foreground: "oklch(0.48 0.006 70)"
    border:           "oklch(0.91 0.004 78)"
    ring:             "oklch(0.50 0.04 250)"
  surface_dark:                         # gallery-black
    background:       "oklch(0.16 0.006 60)"
    foreground:       "oklch(0.96 0.004 80)"
    muted:            "oklch(0.22 0.006 60)"
    muted_foreground: "oklch(0.70 0.005 70)"
    border:           "oklch(0.30 0.006 60)"
    ring:             "oklch(0.62 0.04 250)"
```

## Typography

```yaml
typography:
  display: { family: "Neue Haas Grotesk alt → Inter Tight", fallback: "sans-serif", source: "google-fonts" }
  body:    { family: "Inter", fallback: "sans-serif", source: "google-fonts" }
  scale_ratio: 1.250                    # Major Third — quiet, even hierarchy
  scale:
    h1:   { size: "2.441rem", lh: "1.1", weight: 500 }    # restrained — not loud
    h2:   { size: "1.953rem", lh: "1.2", weight: 500 }
    h3:   { size: "1.563rem", lh: "1.3", weight: 400 }
    body: { size: "1rem", lh: "1.6", weight: 400 }
    small:{ size: "0.8125rem", lh: "1.5", weight: 400, tracking: "0.02em" }   # captions, slight tracking
```

## Spacing, radius, motion

```yaml
spacing: { base_unit: "4px", scale: [0,4,8,12,16,24,32,48,64,96,128,160,224] }  # very large top end = whitespace
radius:  { base: "0px", note: "sharp — architectural, no rounding" }
motion:
  duration_default: "300ms"
  easing_default:   "cubic-bezier(0.16, 1, 0.3, 1)"       # smooth, refined ease-out
  preference:       "subtle"
  reduced_motion:   "duration → 0ms; opacity-only transitions retained"
```

## Component patterns

- **Grid:** a visible, strict column grid; full-bleed and grid-aligned project images alternate. Alignment is the brand.
- **Buttons:** text-link or hairline-bordered, zero radius, slate accent. Almost invisible by design.
- **Cards:** image + one-line caption, no chrome, sharp edges, lots of margin.
- **Imagery:** large architectural photography, natural light, muted tones, full-bleed. The work is the design.
- **Icons:** essentially none — type and image only.

## Do / Don't

- **Do:** maximize whitespace, keep the palette near-monochrome with one quiet accent, sharp corners, strict grid alignment, terse copy.
- **Don't:** add color, rounding, shadows, illustrations, or any decoration. For this brand, ornament is failure.
