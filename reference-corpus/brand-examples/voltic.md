---
type: REFERENCE
corpus: brand-examples
title: Voltic
archetype: Fitness / performance
provenance:
  authored: Original fictional brand for the website-builder plugin (CC0-equivalent)
  resemblance: Invented; any resemblance to a real company is coincidental
consumed_by_phases: [2, 5, 17, 18]
---

# Voltic

> A strength-and-conditioning gym + app. Loud, high-contrast, built to make you move.

**Positioning:** "Show up. Lift heavy. Repeat." Voltic sells energy and momentum. The brand is bold and confrontational in a motivating way — black backgrounds, an electric accent, big type. It should feel like a coach who believes in you and won't let you coast.

## Voice & tone

- **Attributes:** energetic, direct, motivating, blunt, a little swaggering. Confident, never mean.
- **Sounds like:** a coach mid-session — short, punchy, second-person, action-first.
- **Do:** use imperatives ("Earn it." "Add weight."); short, hard-hitting lines; second person; specific numbers (reps, PRs).
- **Don't:** be soft, hedging, or apologetic; avoid wellness-y calm. (One exclamation max — let the design shout, not the punctuation.)

**Sample lines**
- Hero: *"Stronger every week. No fluff, no machines you'll never use — just the work that moves the needle."*
- CTA: *"Start training"* / *"Claim your first week"*
- Stat: *"4 sessions a week. 12-week strength block. Track every lift."*

## Color tokens (OKLCH)

```yaml
color_space: oklch
color:
  primary:   "oklch(0.78 0.20 95)"     # electric lime/volt yellow
  secondary: "oklch(0.62 0.24 25)"     # hot red for intensity accents
  neutral:                              # near-black ramp
    "50":  "oklch(0.97 0 0)"
    "100": "oklch(0.90 0 0)"
    "300": "oklch(0.72 0 0)"
    "500": "oklch(0.50 0 0)"
    "700": "oklch(0.30 0 0)"
    "900": "oklch(0.16 0 0)"
  semantic:
    success: "oklch(0.78 0.20 140)"
    warning: "oklch(0.82 0.16 80)"
    danger:  "oklch(0.60 0.24 25)"
    info:    "oklch(0.70 0.14 230)"
  surface:                              # dark-first, near-black
    background:       "oklch(0.14 0 0)"          # true near-black
    foreground:       "oklch(0.98 0 0)"
    muted:            "oklch(0.20 0 0)"
    muted_foreground: "oklch(0.68 0 0)"
    border:           "oklch(0.28 0 0)"
    ring:             "oklch(0.78 0.20 95)"
  surface_light:                        # optional light mode (high-contrast)
    background:       "oklch(0.98 0 0)"
    foreground:       "oklch(0.16 0 0)"
    muted:            "oklch(0.94 0 0)"
    muted_foreground: "oklch(0.42 0 0)"
    border:           "oklch(0.88 0 0)"
    ring:             "oklch(0.66 0.18 95)"
```

## Typography

```yaml
typography:
  display: { family: "Archivo", fallback: "sans-serif", source: "google-fonts" }   # heavy, condensed-capable
  body:    { family: "Inter",   fallback: "sans-serif", source: "google-fonts" }
  scale_ratio: 1.414                    # Augmented Fourth — dramatic, big jumps
  scale:
    h1:   { size: "4.0rem", lh: "0.95", weight: 800 }     # huge, tight, loud
    h2:   { size: "2.827rem", lh: "1.0", weight: 800 }
    h3:   { size: "2.0rem", lh: "1.1", weight: 700 }
    body: { size: "1.0625rem", lh: "1.55", weight: 400 }
    small:{ size: "0.875rem", lh: "1.45", weight: 600 }
```

## Spacing, radius, motion

```yaml
spacing: { base_unit: "4px", scale: [0,4,8,12,16,24,32,48,64,96,128] }
radius:  { base: "4px", note: "sharp, hard edges — strength, not softness" }
motion:
  duration_default: "150ms"             # snappy, punchy
  easing_default:   "cubic-bezier(0.4, 0, 0.2, 1)"
  preference:       "expressive"        # bold transforms / hover scale on CTAs
  reduced_motion:   "duration → 0ms; opacity-only transitions retained"
```

## Component patterns

- **Buttons:** volt-yellow fill, near-black label, 4px radius, uppercase, bold weight, slight scale-up + glow on hover. Impossible to miss.
- **Cards:** near-black surface, sharp edges, big numeric stat, hairline border, accent stripe.
- **Inputs:** dark field, bright focus ring, bold labels.
- **Imagery:** high-contrast action photography (motion blur, sweat, chalk), duotone toward the accent. Never serene.
- **Icons:** Lucide, 2px stroke, can go solid for emphasis.

## Do / Don't

- **Do:** go near-black, oversize the headlines, use ONE electric accent hard, keep motion snappy, write in imperatives.
- **Don't:** soften corners, use pastels, add whitespace-as-calm, or hedge the copy. Restraint reads as weakness for this brand.
