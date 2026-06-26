---
type: REFERENCE
corpus: design-systems
title: IBM Carbon Design System
provenance:
  describes: "Carbon Design System — IBM's open-source design system"
  official_docs: https://carbondesignsystem.com
  authored: "Original summary of publicly-documented guidelines (not a copy)"
  trademarks: '"IBM", "Carbon", "IBM Plex" are (c) IBM; IBM Plex is OFL-licensed; referenced, not bundled'
consumed_by_phases: [2, 17, 18]
---

# IBM Carbon Design System

IBM's open-source design system, built for **data-dense, enterprise, productivity** software. Where Material is consumer-adaptive and Apple is premium-calm, Carbon is the reference for *serious tools*: dashboards, admin consoles, B2B SaaS, data tables. Grounded in the IBM Design Language and rigorously documented.

## Principles

- **The 2x Grid** — a strict, mathematically-consistent grid (columns + a 16px base mini-unit) is the backbone. Everything aligns; nothing is arbitrary.
- **Clarity for complexity** — Carbon's job is to make dense information legible. Hierarchy, whitespace discipline, and restrained color do the work.
- **Open & accessible** — WCAG 2.1 AA is a baseline requirement, not a nice-to-have; every component documents its accessibility behavior.
- **Consistent & systematic** — tokens over values, components over snowflakes. Predictability is a feature for enterprise users.

## Token system

Carbon's tokens are **role-based and theme-able** — four built-in themes (White, Gray-10, Gray-90, Gray-100) all consume the same token names, which is the model to copy for robust theming:

- **Color tokens by role:** `background`, `layer-01/02/03` (nested surface layers — critical for dense UIs), `field-01/02`, `text-primary`, `text-secondary`, `text-placeholder`, `text-on-color`, `border-subtle`, `border-strong`, `link-primary`, `support-error/success/warning/info`, `interactive`, `focus`. Components reference these role names; switching theme swaps the underlying values.
- **Layering model:** the `layer` tokens are Carbon's standout idea — a documented system for surfaces stacked on surfaces (a modal on a card on a page), each step keeping contrast legible. Directly relevant to any dashboard.

**Typography** — **IBM Plex** (Sans, Serif, Mono; open-source under the SIL Open Font License — usable on the web). The **type scale** is a documented set of named tokens: `caption-01`, `label-01`, `body-01/02`, `heading-01…07`, `display-01…04`, `fluid-heading-*`, each with size/line-height/weight. Productive vs. Expressive type sets (tighter for tools, looser for marketing).

**Spacing** — a named spacing scale `$spacing-01`…`$spacing-13` mapped to `2,4,8,12,16,24,32,40,48,64,80,96,160`px. One scale everywhere. Maps directly onto the plugin's `spacing.scale`.

**Motion** — two easing styles: **Productive** (fast, functional — for frequent actions in tools) and **Expressive** (slower, characterful — for moments of delight). Standard durations `fast-01`…`slow-02` (70–700ms). Naming motion by *intent* is the copyable idea.

**Iconography** — a large, consistent 16/20/24/32px icon grid with strict stroke and keyline rules.

## Strengths / trade-offs

- **Strength:** the layering tokens + Productive/Expressive split + strict grid make Carbon the best reference for **information-dense** products. IBM Plex is genuinely web-usable (OFL).
- **Trade-off:** Carbon's default look is corporate-IBM (cool grays, precise, restrained). It can feel cold for warm/playful/consumer brands. Use the *structure* (grid, layers, role tokens); re-skin the hue.

## When to use / when not

- **Use** for dashboards, admin panels, B2B/enterprise SaaS, data tables, anything with dense controls or multiple surface layers, accessibility-critical products.
- **Avoid** the default skin for warm consumer, editorial, lifestyle, or luxury brands — the cool corporate tone fights them.

## How the website-builder agent applies it

When a project is dashboard-shaped or enterprise-B2B, reach for Carbon's mental model at phase 17: lock a strict spacing scale, define **layered surface tokens** (the plugin's `surface` group, extended with `layer-01/02/03` for nested cards/modals), and split motion into productive-vs-expressive intents. Use IBM Plex when an open, neutral, technical typeface fits (it's OFL — safe to load). Re-skin hue/chroma for the brand; keep Carbon's discipline.
