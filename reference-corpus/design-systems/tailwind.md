---
type: REFERENCE
corpus: design-systems
title: Tailwind CSS Design Scale
provenance:
  describes: "Tailwind CSS — the default token scale and design constraints"
  official_docs: https://tailwindcss.com/docs
  authored: "Original summary of publicly-documented guidelines (not a copy)"
  trademarks: '"Tailwind CSS" is (c) Tailwind Labs; MIT-licensed framework; referenced, not bundled'
consumed_by_phases: [17, 18]
---

# Tailwind CSS Design Scale

Not a "brand" design system but a **design-constraint system**: Tailwind ships an opinionated, well-tuned default scale (spacing, type, color ramps, radii, shadows) that thousands of sites build on. It matters here because the website-builder's **default build path is React + Tailwind v4 + shadcn/ui** — so Tailwind's token shapes are the ones the agent actually emits. Learn this scale and `brand.yaml.tokens` maps onto real CSS with no impedance mismatch.

## Principles

- **Utility-first** — style by composing small single-purpose classes (`flex`, `pt-4`, `text-lg`) rather than authoring bespoke CSS. The design system *is* the constraint set those utilities expose.
- **Constraints over freedom** — a curated scale (only certain spacings, sizes, colors exist by default) prevents the "1px off, 17 shades of gray" entropy that kills consistency.
- **Design tokens are CSS-first (v4)** — Tailwind v4 defines theme tokens via the `@theme` directive as CSS custom properties, with the **default color palette in OKLCH** (Display-P3). This is exactly the plugin's `brand.yaml.tokens.css` shape.

## Token system

- **Spacing scale** — a `0.25rem` (4px) base unit; the numeric scale `0,0.5,1,1.5,2,2.5,3,4,5,6,8,10,12,16,20,24,…` where `4` = `1rem`/16px. Maps directly onto the plugin's `spacing.base_unit: 4px` + `spacing.scale`.
- **Color ramps** — every hue ships a `50→950` ladder (11 steps), all OKLCH in v4 (e.g. `--color-red-500: oklch(63.7% 0.237 25.331)`). The 50→950 luminance ladder is the exact structure the plugin generates for its neutral + brand ramps.
- **Type scale** — `text-xs`(0.75rem) → `text-9xl`, each pairing a size with a sensible default line-height. A modular, named set — maps onto `typography.scale`.
- **Radius** — `rounded-none/sm/DEFAULT/md/lg/xl/2xl/3xl/full` tokens.
- **Shadow** — `shadow-sm/DEFAULT/md/lg/xl/2xl/inner` elevation tokens.
- **Breakpoints** — `sm 640 / md 768 / lg 1024 / xl 1280 / 2xl 1536`px, mobile-first (`min-width`). The plugin's responsive phase (20) builds against these.

## v4 specifics worth knowing

- Tokens live in CSS via `@theme { --color-brand-500: oklch(...); --spacing: 0.25rem; ... }`. No `tailwind.config.js` required.
- shadcn/ui layers **semantic** variables (`--background`, `--foreground`, `--primary`, `--border`, `--ring`) on top via `@theme inline`, in the decimal-L OKLCH form (`oklch(0.64 0.18 30)`) — this is what the plugin's `brand.yaml.tokens.css` mirrors on the default path.
- Dark mode via a `.dark` class (or `prefers-color-scheme`) that re-binds the semantic variables — matches `dark_mode.strategy: auto`.

## Strengths / trade-offs

- **Strength:** it *is* the plugin's output substrate. Knowing the scale means generated tokens compile to real utilities with zero translation. The OKLCH-first v4 palette aligns perfectly with the plugin's color discipline.
- **Trade-off:** Tailwind defaults are excellent but generic — a site that uses only defaults looks like every other Tailwind site. The brand layer (custom OKLCH ramp + type pairing + motion) is what differentiates; defaults are the floor, not the ceiling.

## When to use / when not

- **Use** on essentially every default-path build (React/Tailwind/shadcn). Treat the scale as the substrate; override the *color + type + motion* layer with the project's brand.
- **Not relevant** as a *visual* reference for non-Tailwind stacks, but the scale discipline (one spacing unit, ramps over ad-hoc colors) is portable to any stack.

## How the website-builder agent applies it

At phase 17, generate `brand.yaml.tokens` so it lands cleanly into a Tailwind v4 `@theme` block: 4px spacing base, 50→950 OKLCH ramps, named type scale, shadcn semantic variables in decimal-L OKLCH. At phase 18/20, build with utilities off this scale — never ad-hoc pixel values (an off-scale value is a gating failure per the phase-17 contract). Use Tailwind defaults as the floor; the brand's OKLCH ramp + font pairing + motion tokens are the differentiator.
