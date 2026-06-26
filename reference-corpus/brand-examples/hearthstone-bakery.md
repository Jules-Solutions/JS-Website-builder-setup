---
type: REFERENCE
corpus: brand-examples
title: Hearthstone Bakery
archetype: Local artisan food / craft
provenance:
  authored: Original fictional brand for the website-builder plugin (CC0-equivalent)
  resemblance: Invented; any resemblance to a real bakery is coincidental
consumed_by_phases: [2, 5, 17, 18]
---

# Hearthstone Bakery

> A neighborhood sourdough bakery. Wood-fired, slow-fermented, sold out by noon.

**Positioning:** "Bread worth waking up for." Hearthstone is the opposite of industrial — handmade, seasonal, rooted in one corner. The brand sells warmth, craft, and the smell of a Saturday morning.

## Voice & tone

- **Attributes:** warm, generous, unhurried, a little old-fashioned, never precious.
- **Sounds like:** a baker leaning on the counter telling you the rye came out especially good today.
- **Do:** speak in plain, sensory language ("crackly crust," "still warm"); use first person plural ("we proof overnight"); be generous with detail about process.
- **Don't:** use foodie jargon, hype words ("artisanal-grade," "elevated"), exclamation spam, or corporate politeness.

**Sample lines**
- Hero: *"We get up at four so you don't have to. Fresh loaves, every morning, until they're gone."*
- CTA: *"See today's bake"* / *"Reserve a loaf"*
- Empty/sold-out: *"Sold out — that's the sourdough life. Back at 6am tomorrow."*

## Color tokens (OKLCH)

```yaml
color_space: oklch
color:
  primary:   "oklch(0.55 0.13 55)"     # warm terracotta / crust
  secondary: "oklch(0.68 0.09 95)"     # wheat / golden
  neutral:                              # warm-tinted grays (not pure neutral)
    "50":  "oklch(0.98 0.008 70)"
    "100": "oklch(0.95 0.012 70)"
    "300": "oklch(0.86 0.014 70)"
    "500": "oklch(0.62 0.016 70)"
    "700": "oklch(0.42 0.018 65)"
    "900": "oklch(0.24 0.02 60)"
  semantic:
    success: "oklch(0.66 0.14 145)"
    warning: "oklch(0.80 0.13 80)"
    danger:  "oklch(0.58 0.19 28)"
    info:    "oklch(0.70 0.08 230)"
  surface:                              # light (primary mode for this warm brand)
    background:       "oklch(0.985 0.012 80)"   # warm cream, never pure white
    foreground:       "oklch(0.26 0.02 60)"
    muted:            "oklch(0.95 0.012 75)"
    muted_foreground: "oklch(0.48 0.018 65)"
    border:           "oklch(0.90 0.014 70)"
    ring:             "oklch(0.55 0.13 55)"
  surface_dark:                         # cozy dark for evening / hero overlays
    background:       "oklch(0.22 0.02 60)"
    foreground:       "oklch(0.95 0.012 75)"
    muted:            "oklch(0.28 0.02 60)"
    muted_foreground: "oklch(0.72 0.016 70)"
    border:           "oklch(0.34 0.02 60)"
    ring:             "oklch(0.68 0.12 60)"
```

## Typography

```yaml
typography:
  display: { family: "Fraunces", fallback: "serif", source: "google-fonts" }   # soft, characterful serif
  body:    { family: "Inter",    fallback: "sans-serif", source: "google-fonts" }
  scale_ratio: 1.250                    # Major Third — gentle, readable
  scale:
    h1:   { size: "3.052rem", lh: "1.1", weight: 600 }
    h2:   { size: "2.441rem", lh: "1.2", weight: 600 }
    h3:   { size: "1.953rem", lh: "1.25", weight: 500 }
    body: { size: "1.0625rem", lh: "1.65", weight: 400 }
    small:{ size: "0.875rem", lh: "1.5", weight: 400 }
```

## Spacing, radius, motion

```yaml
spacing: { base_unit: "4px", scale: [0,4,8,12,16,24,32,48,64,96,128] }
radius:  { base: "10px", note: "soft, hand-rounded — never sharp" }
motion:
  duration_default: "260ms"
  easing_default:   "cubic-bezier(0.22, 0.61, 0.36, 1)"   # gentle ease-out
  preference:       "subtle"
  reduced_motion:   "duration → 0ms; opacity-only transitions retained"
```

## Component patterns

- **Buttons:** filled primary = terracotta surface, cream label, 10px radius, slight warm shadow on hover; secondary = wheat outline. No hard edges.
- **Cards:** cream surface, soft border, generous 24px padding, product photo top, price as a quiet detail (warmth over commerce).
- **Inputs:** 1px warm border, focus ring = primary, comfortable 44px height, label above (never placeholder-only).
- **Imagery:** real photos of bread, hands, flour, morning light. Warm white balance. Never stock-photo "smiling models."
- **Icons:** Lucide, 1.5px stroke, used sparingly — the photography carries the brand.

## Do / Don't

- **Do:** lean on warm cream surfaces, photography, and roomy spacing. Let the type breathe.
- **Don't:** use pure white/black, cool grays, neon, tight corporate density, or hype copy. That would make Hearthstone feel like a chain.
