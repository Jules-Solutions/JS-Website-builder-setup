# DESIGN.md

> Synthetic Stitch DESIGN.md export — fixture for tests/extraction/stitch/.
> Represents the raw artifact a user pastes back after running Stitch against a
> deployed URL (browser-in-loop, Path 1). Mirrors the documented Stitch output
> schema in extraction/stitch.md § "Output schema" + DESIGN-extraction-stitch.md
> § "Output format". Fully synthetic — no real brand, no real client.
>
> The normalization of THIS file → tests/extraction/stitch/expected.yaml is the
> end-to-end contract this fixture asserts (BUILD-strategy DoD line 225).

## Brand Identity
**Name:** Northwind Studio
**Voice:** warm, confident, editorial
**Tagline:** Design that earns trust.

## Design Tokens

### Colors
- primary:    oklch(64% 0.18 30)    # extracted from primary CTA button
- secondary:  oklch(52% 0.12 220)   # extracted from secondary surfaces
- accent:     oklch(76% 0.16 80)
- surface:    oklch(98% 0.01 100)
- on-surface: oklch(20% 0.02 100)
- muted:      oklch(45% 0.02 100)
- danger:     oklch(58% 0.20 25)
- success:    oklch(60% 0.15 145)

### Typography
- display: "Fraunces", Georgia, serif
  - sizes: [3.5rem, 2.5rem, 2rem]
  - weights: [700, 600]
  - line-height: 1.1
- body: "Inter", -apple-system, sans-serif
  - sizes: [1.125rem, 1rem, 0.875rem]
  - weights: [400, 500]
  - line-height: 1.55

### Spacing
- base_unit: 4px
- scale: [4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px, 96px]

### Motion
- duration_med: 280ms
- easing_default: cubic-bezier(0.32, 0.72, 0, 1)

### Dark Mode
- strategy: auto

## Components

### Hero
- recognized: yes
- props: headline, sub_headline, primary_cta_text, primary_cta_href, image
- behaviors: scroll-triggered reveal; CTA hover lift

### Nav
- recognized: yes
- props: logo_text, nav_items
- behaviors: sticky on scroll; mobile hamburger drawer

### Card
- recognized: yes
- props: title, body, icon, href
- behaviors: hover elevation

### Footer
- recognized: yes
- props: copyright, footer_nav_items
- behaviors: none
