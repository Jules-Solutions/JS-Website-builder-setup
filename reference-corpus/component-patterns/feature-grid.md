---
type: REFERENCE
corpus: component-patterns
title: Feature Grid
component_slug: feature-grid
also_known_as: [feature list, benefits grid, services grid, icon grid, value props]
consumed_by_phases: [9, 17, 18]
---

# Feature Grid

> A multi-column grid of parallel feature or benefit items, each a small unit of icon + heading + short blurb, used to summarize what a product or service offers.

## Purpose

A feature grid answers the visitor's "what do I get?" question quickly and scannably. By laying out 3–9 parallel value propositions in a consistent icon-heading-blurb shape, it lets the eye sweep across capabilities without reading paragraphs. It converts by turning an abstract pitch into a concrete, comparable list of benefits, and by giving each benefit equal visual weight so none gets buried.

## When to use / when not

- **Use when:** you have several genuinely parallel benefits/features/services to communicate at a glance, typically below a hero on a landing or services page.
- **Avoid when:** items aren't parallel (mixed lengths and kinds read as a dumping ground), there is only one or two points (use a richer split section instead), or each item needs deep explanation (link out to dedicated pages). More than ~9 items overwhelms scanning — paginate or split into categories.

## Anatomy

- **Section wrapper** — optional eyebrow + section heading + intro lead-in.
- **Grid container** — the responsive multi-column layout (collapses to one column on narrow viewports).
- **Feature item** (repeats), each containing:
  - **Icon / glyph** — a small decorative visual cue.
  - **Item heading** — the feature name.
  - **Blurb** — one or two sentences of supporting copy.
  - **Optional link** — "Learn more" to a detail page.

## Content slots

| Slot | Required? | Source layer | Notes |
|---|---|---|---|
| `section_heading` | No | content/pages | The "Why us / Features" overarching title |
| `section_intro` | No | content/pages | Optional lead paragraph |
| `items[].icon` | No | media | SVG glyph; treated as decorative by default |
| `items[].heading` | Yes | content/strings | Short feature name; becomes the `<li>` heading |
| `items[].blurb` | Yes | content/pages | One–two sentence benefit description |
| `items[].href` | No | sitemap.yaml | Optional per-item detail route |
| `columns` | No | components.yaml | Column count / breakpoints; spacing tokens from brand.yaml |
| `icon_style` | No | brand.yaml | Color/size/stroke tokens for the glyphs |

## Accessibility requirements

- **List semantics (the key requirement):** the repeating items are a list — render the grid container as `<ul>` and each feature as `<li>`. This makes assistive tech announce "list, N items" and lets users jump item-to-item. CSS Grid/Flex layout does not change the semantics; keep the list role intact (avoid `list-style:none` wiping the role in Safari/VoiceOver by adding `role="list"` back on the `<ul>` when you remove markers).
- **Heading structure:** the section title is a real heading (`<h2>`). Each item's name should be a heading one level deeper (`<h3>`) so the section forms a coherent outline; if items have no body beyond the blurb, a `<p>` with strong styling is acceptable, but a heading is preferred for navigability.
- **Decorative icons:** icons that merely decorate the heading add no information — mark them `aria-hidden="true"` (and `focusable="false"` on inline `<svg>`) so they aren't announced. If an icon is the *only* carrier of meaning (rare here), give it an accessible name via `<title>` or `aria-label` and don't hide it.
- **Links:** a per-item "Learn more" link must have an accessible name that identifies its target — either visually-distinct text or an `aria-label`/visually-hidden suffix (e.g. "Learn more about analytics") so a screen-reader user reading links out of context isn't faced with five identical "Learn more"s.
- **Keyboard & focus:** only the optional links are interactive; they follow normal `Tab` order with visible `:focus-visible` outlines. The grid itself is not a widget and needs no keyboard handling.
- **Contrast & motion:** blurb text meets ≥ 4.5:1; icon color is not the sole means of distinguishing items. Any staggered entrance animation respects `prefers-reduced-motion: reduce`.

## Common variants

- **Icon-top** — centered icon above heading and blurb (classic 3-up).
- **Icon-left** — icon beside text in a horizontal item (denser, list-like).
- **Numbered steps** — ordered process; use `<ol>` instead of `<ul>`.
- **Bordered cells** — each item gets a card-like border (then follow card a11y too).
- **Two-tier** — large headline feature plus a row of smaller ones.
- **Linked features** — each item is a teaser to a detail page (apply card link discipline).

## Pitfalls

- Building the grid from `<div>`s so it loses list semantics — screen-reader users get no count and no item navigation.
- Leaving decorative icons announced (missing `aria-hidden`), cluttering the audio output with "image, image, image".
- Repeated identical "Learn more" links with no distinguishing accessible name.
- Cramming uneven, non-parallel content into the grid so item heights and meaning diverge.
- Conveying a feature's status purely through icon color (fails for color-blind users).
