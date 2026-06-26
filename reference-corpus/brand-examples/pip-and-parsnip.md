---
type: REFERENCE
corpus: brand-examples
title: Pip & Parsnip
archetype: Kids' education / family
provenance:
  authored: Original fictional brand for the website-builder plugin (CC0-equivalent)
  resemblance: Invented; any resemblance to a real company is coincidental
consumed_by_phases: [2, 5, 17, 18]
---

# Pip & Parsnip

> A playful early-learning app + activity box for ages 3–7. Cheerful, simple, encouraging.

**Positioning:** "Big curiosity, small humans." Pip & Parsnip sells joyful, screen-light learning to parents while delighting kids. The brand is bright and friendly without being chaotic — a curated, tasteful playfulness that parents trust and children love.

## Voice & tone

- **Attributes:** cheerful, warm, simple, encouraging, gently funny. Two audiences (kid-facing delight, parent-facing reassurance).
- **Sounds like:** a kind kindergarten teacher — clear, positive, never baby-talk-y or condescending to parents.
- **Do:** short friendly sentences; positive framing ("you did it!"); for parents, lead with reassurance + evidence; light, never sugary.
- **Don't:** be loud/hyper, use babytalk, overpromise ("genius in 30 days"), or scold. Keep parent-copy calm and credible.

**Sample lines**
- Hero (parent): *"Hands-on learning that doesn't need a screen. New activity box every month, designed by early-years teachers."*
- Kid microcopy: *"Nice work! Ready for the next one?"*
- CTA: *"Start the first box"* / *"See a sample week"*

## Color tokens (OKLCH)

```yaml
color_space: oklch
color:
  primary:   "oklch(0.70 0.17 245)"    # friendly blue
  secondary: "oklch(0.78 0.16 145)"    # fresh green (the "parsnip" leaf)
  tertiary:  "oklch(0.80 0.15 60)"     # sunny yellow accent
  neutral:                              # soft, slightly-warm grays
    "50":  "oklch(0.99 0.005 250)"
    "100": "oklch(0.97 0.006 250)"
    "300": "oklch(0.89 0.008 250)"
    "500": "oklch(0.64 0.01 250)"
    "700": "oklch(0.44 0.012 250)"
    "900": "oklch(0.26 0.014 250)"
  semantic:
    success: "oklch(0.74 0.16 145)"
    warning: "oklch(0.82 0.15 80)"
    danger:  "oklch(0.62 0.18 28)"
    info:    "oklch(0.72 0.13 245)"
  surface:                              # light, bright, friendly
    background:       "oklch(0.99 0.005 250)"
    foreground:       "oklch(0.28 0.014 250)"
    muted:            "oklch(0.97 0.008 245)"
    muted_foreground: "oklch(0.50 0.012 250)"
    border:           "oklch(0.92 0.01 250)"
    ring:             "oklch(0.70 0.17 245)"
  surface_dark:                         # optional gentle dark (bedtime mode)
    background:       "oklch(0.26 0.014 250)"
    foreground:       "oklch(0.96 0.006 250)"
    muted:            "oklch(0.32 0.014 250)"
    muted_foreground: "oklch(0.74 0.01 250)"
    border:           "oklch(0.38 0.014 250)"
    ring:             "oklch(0.72 0.15 245)"
```

## Typography

```yaml
typography:
  display: { family: "Baloo 2", fallback: "cursive", source: "google-fonts" }     # rounded, friendly, kid-safe
  body:    { family: "Nunito", fallback: "sans-serif", source: "google-fonts" }    # rounded, highly legible
  scale_ratio: 1.250                    # Major Third
  scale:
    h1:   { size: "2.488rem", lh: "1.15", weight: 700 }
    h2:   { size: "2.074rem", lh: "1.2", weight: 700 }
    h3:   { size: "1.728rem", lh: "1.3", weight: 600 }
    body: { size: "1.0625rem", lh: "1.6", weight: 400 }
    small:{ size: "0.875rem", lh: "1.5", weight: 400 }
```

## Spacing, radius, motion

```yaml
spacing: { base_unit: "4px", scale: [0,4,8,12,16,24,32,48,64,96,128] }
radius:  { base: "18px", note: "very rounded, soft, safe — no sharp corners for kids" }
motion:
  duration_default: "260ms"
  easing_default:   "cubic-bezier(0.34, 1.56, 0.64, 1)"   # gentle bounce — playful but not frantic
  preference:       "expressive"
  reduced_motion:   "duration → 0ms; opacity-only transitions retained"
```

## Component patterns

- **Buttons:** big, very-rounded (18px+), friendly blue/green/yellow, bold rounded label, gentle bounce on press. Large tap targets (kids' fingers).
- **Cards:** rounded, soft shadow, cheerful illustration or photo, clear single action.
- **Inputs (parent flows):** rounded, calm, clear labels — the parent UI is reassuring and uncluttered, distinct from the playful kid UI.
- **Imagery:** bright, simple custom illustration (the Pip & Parsnip characters) + real photos of kids doing activities. Tasteful, not garish.
- **Icons:** rounded, friendly, often filled, slightly oversized.

## Do / Don't

- **Do:** keep it bright but curated; very-rounded shapes; big targets; playful-but-gentle motion; split the kid-delight and parent-trust voices.
- **Don't:** go garish/chaotic, use babytalk, sharp corners, or tiny controls. And never let kid-playfulness leak into the parent purchase flow — parents need calm credibility there.
