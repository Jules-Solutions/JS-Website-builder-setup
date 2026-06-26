---
type: REFERENCE
corpus: brand-examples
title: Northbeam
archetype: B2B SaaS / analytics
provenance:
  authored: Original fictional brand for the website-builder plugin (CC0-equivalent)
  resemblance: Invented; any resemblance to a real company is coincidental
consumed_by_phases: [2, 5, 17, 18]
---

# Northbeam

> Attribution analytics for operators who want the truth, not a dashboard that flatters them.

**Positioning:** "Know what's actually working." Northbeam is a precise, technical B2B product. The brand sells clarity, rigor, and respect for the buyer's intelligence. No fluff, no growth-hack theater.

## Voice & tone

- **Attributes:** precise, confident, calm, technical, plainspoken. Smart but never showing off.
- **Sounds like:** a senior engineer explaining a system clearly — assumes you're capable, doesn't condescend.
- **Do:** lead with the concrete claim; use specific numbers; short declarative sentences; name the mechanism.
- **Don't:** use hype ("revolutionary," "game-changing," "10x"), vague benefit-speak, or exclamation marks. No emoji.

**Sample lines**
- Hero: *"See which channels actually drive revenue. Multi-touch attribution that reconciles to the penny."*
- CTA: *"Start free trial"* / *"Book a technical demo"*
- Feature: *"Server-side tracking. First-party data. No cookie guesswork."*

## Color tokens (OKLCH)

```yaml
color_space: oklch
color:
  primary:   "oklch(0.58 0.16 250)"    # confident blue
  secondary: "oklch(0.70 0.13 200)"    # cyan-teal accent for data
  neutral:                              # true cool neutral
    "50":  "oklch(0.985 0 0)"
    "100": "oklch(0.96 0 0)"
    "300": "oklch(0.87 0.004 250)"
    "500": "oklch(0.60 0.006 250)"
    "700": "oklch(0.40 0.008 250)"
    "900": "oklch(0.20 0.01 250)"
  semantic:
    success: "oklch(0.68 0.15 150)"
    warning: "oklch(0.80 0.12 75)"
    danger:  "oklch(0.60 0.20 25)"
    info:    "oklch(0.62 0.14 250)"
  surface:                              # dark-first (analytics products live in dark)
    background:       "oklch(0.18 0.012 250)"
    foreground:       "oklch(0.97 0 0)"
    muted:            "oklch(0.24 0.012 250)"
    muted_foreground: "oklch(0.68 0.008 250)"
    border:           "oklch(0.30 0.012 250)"
    ring:             "oklch(0.58 0.16 250)"
  surface_light:                        # light mode (docs / marketing)
    background:       "oklch(0.99 0 0)"
    foreground:       "oklch(0.20 0.01 250)"
    muted:            "oklch(0.96 0 0)"
    muted_foreground: "oklch(0.46 0.006 250)"
    border:           "oklch(0.91 0.004 250)"
    ring:             "oklch(0.58 0.16 250)"
```

## Typography

```yaml
typography:
  display: { family: "Space Grotesk", fallback: "sans-serif", source: "google-fonts" }
  body:    { family: "Inter",         fallback: "sans-serif", source: "google-fonts" }
  mono:    { family: "JetBrains Mono", fallback: "monospace", source: "google-fonts" }  # for data/metrics
  scale_ratio: 1.333                    # Perfect Fourth — clear hierarchy
  scale:
    h1:   { size: "3.157rem", lh: "1.05", weight: 700 }
    h2:   { size: "2.369rem", lh: "1.15", weight: 600 }
    h3:   { size: "1.777rem", lh: "1.25", weight: 600 }
    body: { size: "1rem", lh: "1.6", weight: 400 }
    small:{ size: "0.8125rem", lh: "1.5", weight: 400 }
```

## Spacing, radius, motion

```yaml
spacing: { base_unit: "4px", scale: [0,4,8,12,16,24,32,48,64,96,128] }
radius:  { base: "6px", note: "tight, precise — software, not soft goods" }
motion:
  duration_default: "180ms"
  easing_default:   "cubic-bezier(0.2, 0, 0, 1)"          # crisp, functional
  preference:       "subtle"
  reduced_motion:   "duration → 0ms; opacity-only transitions retained"
```

## Component patterns

- **Buttons:** filled primary = blue, white label, 6px radius, no shadow theatrics; secondary = ghost with border. States are obvious, fast.
- **Cards:** dark surface, 1px subtle border, metric/number rendered in JetBrains Mono, tight 16–20px padding (density is a virtue here).
- **Inputs:** dark field, subtle border, blue focus ring, monospace for numeric/API values.
- **Data viz:** restrained — one accent (cyan) over neutral; never rainbow. Numbers are the hero.
- **Icons:** Lucide, 1.5px stroke, functional only.

## Do / Don't

- **Do:** dark-first, tight density, monospace for data, one cool accent, plainspoken copy.
- **Don't:** warm tones, rounded "friendly" shapes, illustrations of smiling people, hype words, or decorative gradients. Northbeam earns trust by looking like a serious tool.
