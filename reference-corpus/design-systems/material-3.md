---
type: REFERENCE
corpus: design-systems
title: Material Design 3 (Material You)
provenance:
  describes: "Material Design 3 — Google's open design system"
  official_docs: https://m3.material.io
  authored: "Original summary of publicly-documented guidelines (not a copy)"
  trademarks: '"Material Design" and "Roboto" are (c) Google; referenced, not bundled'
consumed_by_phases: [2, 17, 18]
---

# Material Design 3 (Material You)

Google's third-generation design system. Successor to Material Design 2, introduced 2021. Its headline idea is **dynamic color**: a whole UI palette is algorithmically derived from a single source color (often the user's wallpaper on Android), so the system adapts to the user instead of shipping one fixed brand palette.

## Principles

- **Personal & adaptive** — color, shape, and typography respond to user input and context. The system is a generator, not a fixed sheet.
- **Tonal, not flat** — color is expressed as *tonal palettes* (13 tones from 0=black to 100=white per key hue), and roles are mapped to tones, which is what makes light/dark and contrast guarantees fall out automatically.
- **Expressive but legible** — large rounded shapes, generous touch targets (48dp minimum), strong typographic hierarchy.
- **Accessible by construction** — role-to-tone mapping is designed so on-color pairs meet WCAG contrast without manual tuning.

## Token system

Material 3 separates tokens into three layers — this layering is the most copyable idea:

1. **Reference tokens** — the raw tonal palettes. For each key color (primary, secondary, tertiary, neutral, neutral-variant, error) a ramp of tones `0,10,20,…,100`.
2. **System tokens** — *semantic roles* mapped onto reference tones, e.g. `primary`, `on-primary`, `primary-container`, `on-primary-container`, `surface`, `on-surface`, `surface-variant`, `outline`. Roles, not raw colors, are what components consume.
3. **Component tokens** — per-component bindings (e.g. a filled button's container = `primary`, label = `on-primary`).

| Layer | Example | Maps to website-builder |
|---|---|---|
| Reference | `primary40 = #6750A4` (a tone) | the OKLCH neutral/primary ramp in `brand.yaml.tokens.color` |
| System | `surface`, `on-surface`, `outline` | `surface.background`, `surface.foreground`, `surface.border` |
| Component | button.container = primary | phase-18 component theming |

**Type scale** — 5 roles × 3 sizes = 15 named styles: `display` / `headline` / `title` / `body` / `label`, each in large/medium/small. Default typeface: Roboto (Roboto Flex variable for M3). This role × size matrix maps cleanly onto the plugin's `typography.scale`.

**Shape scale** — corner-radius tokens: none `0` / extra-small `4` / small `8` / medium `12` / large `16` / extra-large `28` / full. Shape is a first-class token, not an afterthought.

**Elevation** — 6 levels (0–5) expressed as tonal *surface* overlays + shadow, not just box-shadows. In M3, raising elevation tints the surface toward `primary`.

**Motion** — "emphasized" and "standard" easing sets; durations 50–700ms bucketed by transition size. `prefers-reduced-motion` respected.

## Strengths / trade-offs

- **Strength:** the tonal-palette + semantic-role model is the cleanest answer to "how do I get light, dark, and accessible contrast from one brand color." Borrow this structure even if you never use Roboto.
- **Strength:** enormous component coverage and documented states.
- **Trade-off:** the dynamic-color, rounded, elevation-tinted look reads as "Android/Google." Heavy-handed use makes any site look like a Google product. Take the *system*, not the *skin*.

## When to use / when not

- **Use** for adaptive consumer apps, Android-first products, dashboards needing broad component coverage, teams wanting strong accessibility defaults.
- **Avoid** the visual skin for editorial, luxury, or strongly-branded sites where the Material look fights the brand. (The token *architecture* is still worth stealing.)

## How the website-builder agent applies it

At phase 17, use M3's three-layer split as the mental model: generate a tonal ramp, map *semantic roles* (`surface`/`on-surface`/`outline`/`primary-container`) onto it, and let components bind to roles — exactly mirroring the plugin's `color.surface` + `color.semantic` token groups. Adopt the role-to-tone discipline (every foreground has a guaranteed-contrast background). Do **not** default to Roboto, full-radius pills, or elevation tinting unless the brief calls for a Material aesthetic.
