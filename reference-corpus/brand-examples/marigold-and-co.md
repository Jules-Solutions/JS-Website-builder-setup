---
type: REFERENCE
corpus: brand-examples
title: Marigold & Co.
archetype: Editorial / lifestyle blog
provenance:
  authored: Original fictional brand for the website-builder plugin (CC0-equivalent)
  resemblance: Invented; any resemblance to a real publication is coincidental
consumed_by_phases: [2, 5, 17, 18]
---

# Marigold & Co.

> A personal food-and-living journal. Long reads, seasonal recipes, warm photography.

**Positioning:** "A slower table." Marigold is editorial-first — the writing and photography are the product. The brand sells a point of view and a voice you want to return to weekly. Design serves reading: big type, generous measure, warm neutrals.

## Voice & tone

- **Attributes:** literary, sensory, personal, observational, a little wry. First-person, opinionated, generous.
- **Sounds like:** a favorite columnist — vivid, specific, never padded.
- **Do:** open with a scene; use concrete sensory detail; vary sentence length; let personality through.
- **Don't:** write SEO-keyword mush, listicle filler, or brand-neutral corporate prose. This brand lives or dies on voice.

**Sample lines**
- Hero: *"Marigold & Co. — recipes, essays, and the occasional strong opinion about butter."*
- CTA: *"Read the latest"* / *"Subscribe to the Sunday letter"*
- Card kicker: *"Essays · 8 min read"*

## Color tokens (OKLCH)

```yaml
color_space: oklch
color:
  primary:   "oklch(0.66 0.15 65)"     # marigold / amber
  secondary: "oklch(0.45 0.08 30)"     # deep terracotta-brown ink
  neutral:                              # warm paper neutrals
    "50":  "oklch(0.985 0.008 75)"
    "100": "oklch(0.96 0.01 75)"
    "300": "oklch(0.87 0.012 70)"
    "500": "oklch(0.60 0.014 65)"
    "700": "oklch(0.38 0.016 60)"
    "900": "oklch(0.22 0.018 55)"
  semantic:
    success: "oklch(0.64 0.13 150)"
    warning: "oklch(0.80 0.13 80)"
    danger:  "oklch(0.58 0.18 28)"
    info:    "oklch(0.66 0.09 230)"
  surface:                              # warm paper, the reading surface
    background:       "oklch(0.985 0.01 80)"     # off-white paper
    foreground:       "oklch(0.24 0.018 55)"     # warm near-black ink
    muted:            "oklch(0.95 0.01 78)"
    muted_foreground: "oklch(0.46 0.016 60)"
    border:           "oklch(0.90 0.012 72)"
    ring:             "oklch(0.66 0.15 65)"
  surface_dark:                         # sepia night-reading mode
    background:       "oklch(0.20 0.016 55)"
    foreground:       "oklch(0.94 0.01 78)"
    muted:            "oklch(0.26 0.016 55)"
    muted_foreground: "oklch(0.72 0.014 65)"
    border:           "oklch(0.32 0.016 55)"
    ring:             "oklch(0.70 0.14 65)"
```

## Typography

```yaml
typography:
  display: { family: "Fraunces", fallback: "serif", source: "google-fonts" }     # expressive editorial serif
  body:    { family: "Source Serif 4", fallback: "serif", source: "google-fonts" }  # serif body = reading comfort
  ui:      { family: "Inter", fallback: "sans-serif", source: "google-fonts" }    # chrome / nav only
  scale_ratio: 1.333                    # Perfect Fourth — strong editorial hierarchy
  scale:
    h1:   { size: "3.157rem", lh: "1.1", weight: 600 }
    h2:   { size: "2.369rem", lh: "1.2", weight: 600 }
    h3:   { size: "1.777rem", lh: "1.3", weight: 500 }
    body: { size: "1.1875rem", lh: "1.7", weight: 400 }   # large reading size + open leading
    small:{ size: "0.875rem", lh: "1.5", weight: 400 }
```

## Spacing, radius, motion

```yaml
spacing: { base_unit: "4px", scale: [0,4,8,12,16,24,32,48,64,96,128] }
radius:  { base: "2px", note: "minimal — editorial print feel, not app-rounded" }
motion:
  duration_default: "220ms"
  easing_default:   "cubic-bezier(0.25, 0.46, 0.45, 0.94)"
  preference:       "subtle"
  reduced_motion:   "duration → 0ms; opacity-only transitions retained"
```

## Component patterns

- **Article layout:** single column, ~68ch measure, serif body, drop-cap optional, pull-quotes in display serif. Reading is sacred.
- **Buttons:** quiet — text-link or thin outline; the amber primary used sparingly for subscribe.
- **Cards:** photo-led, kicker + headline + read-time, minimal chrome, hairline divider.
- **Imagery:** warm, editorial food/lifestyle photography — full-bleed, generous. The photos and the words alternate.
- **Icons:** minimal; this brand is type and photography, not iconography.

## Do / Don't

- **Do:** prioritize reading comfort (serif body, big measure, open leading), warm paper surfaces, photo-led cards, distinctive voice.
- **Don't:** use app-style heavy rounding, dense dashboards, cold grays, or generic blog templates. The brand is a *publication*, not a SaaS.
