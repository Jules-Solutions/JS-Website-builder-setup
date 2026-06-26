---
type: REFERENCE
corpus: component-patterns
title: Accordion
component_slug: accordion
also_known_as: [collapsible, disclosure group, expander, expand/collapse list]
consumed_by_phases: [9, 17, 18]
---

# Accordion

> A vertical stack of headers that each expand to reveal a region of content, letting the user open the sections they care about and keep the rest collapsed.

## Purpose

An accordion compresses a long page into a scannable list of headers, so the visitor reads the labels first and expands only what's relevant. It suits content that is naturally segmented and where most users want a subset — feature details, policy sections, spec breakdowns, or a FAQ. By collapsing everything by default it shortens the page, surfaces structure, and reduces cognitive load, while keeping each section one click away rather than on a separate page.

## When to use / when not

- **Use when:** content is divided into independent, labelled sections and users typically want only some of them; vertical space is at a premium; the labels alone help users navigate.
- **Avoid when:** users need to read everything (collapsing just adds clicks and hides content from in-page find/print), the content is a single short block, or the sections are alternatives shown one at a time (use tabs). Don't hide SEO-critical copy in collapsed panels without confirming it's still in the DOM and crawlable.

## Anatomy

| Part | Role |
|---|---|
| Accordion root | The container grouping all the items |
| Item | One header + panel pair |
| Header | A heading element wrapping the toggle button |
| Toggle button | The control that expands/collapses, carrying the expanded state |
| Panel / region | The collapsible content revealed by its header |
| Expand/collapse icon | The chevron or +/− reflecting open state (decorative) |

## Content slots

| Slot | Required? | Source layer | Notes |
|---|---|---|---|
| Item headers | Yes | content/strings | Short section titles, one per item; order is meaningful |
| Item body content | Yes | content/pages | Prose, lists, media, or nested components per section |
| Heading level | Yes | components.yaml | Which `h2`–`h4` wraps each header, fitting the page outline |
| Single vs multi-expand | No | components.yaml | Whether opening one closes the others |
| Default-open items | No | components.yaml | Which items (if any) start expanded |
| Icon set | No | media | Chevron/plus-minus glyphs (marked decorative) |
| Token styling (header/hover/focus/divider) | Yes | brand.yaml | Header background, focus ring, border tokens |

## Accessibility requirements

Implements the **WAI-ARIA APG "Accordion" pattern** exactly.

- **Header is a heading + button:** each accordion header is a real heading element (`<h2>`–`<h6>` at the level that fits the page outline) whose ONLY child is a `<button>`. The button carries the interaction; the heading carries the document structure so screen-reader users can jump between sections by heading. Do not put a non-heading `<div>` role-button as the header.
- **Expanded state:** the header button has `aria-expanded="true"` when its panel is open and `aria-expanded="false"` when collapsed. This is the single most important attribute — it's how assistive tech announces "collapsed/expanded".
- **Button controls panel:** the button has `aria-controls` pointing at its panel's id. The panel is a `role="region"` (or a `<section>`) named by its header via `aria-labelledby` pointing back at the button's id, so the region announces which section it belongs to. (For very many items, the `region` role may be omitted to avoid landmark noise — that's an allowed APG relaxation.)
- **Collapsed panels are removed:** a collapsed panel is hidden with the `hidden` attribute (or `display:none`) so its content is out of the tab order and the accessibility tree — not merely visually clipped with `height:0`.
- **Keyboard — required:** `Enter` and `Space` on a focused header button toggle that section. `Tab`/`Shift+Tab` move through the headers (and into the open panel's focusable content) in DOM order. The header button is a normal tab stop (`tabindex="0"`) — accordions do NOT use roving tabindex.
- **Keyboard — optional (APG-recommended):** `Down`/`Up` arrows move focus between header buttons (not into panels); `Home` moves to the first header, `End` to the last. These are optional but recommended for fast navigation when there are many items.
- **Single vs multi-expand:** if the accordion permits only one open item at a time, opening one collapses the rest — but do NOT disable the open item's button (a disabled control can't be focused, and users must be able to collapse it). If a panel cannot be collapsed once open, signal that with `aria-disabled="true"` rather than removing it from focus.
- **Icon & motion:** the chevron/±icon is decorative (`aria-hidden="true"`) — state comes from `aria-expanded`, not the glyph. Header text and focus indicator meet WCAG 2.2 contrast; expand/collapse height transitions are reduced or instant under `prefers-reduced-motion: reduce`.

## Common variants

- **Single-expand** — opening one item collapses the others (radio-like).
- **Multi-expand** — any number of items open at once (the more accessible default).
- **First-open** — the first item is expanded on load to hint the interaction.
- **FAQ accordion** — each header is a question; see faq.md for the SEO/structured-data layer.
- **Nested accordion** — panels contain sub-accordions; keep heading levels consistent with depth.
- **Bordered / card** — visually separated items vs a flush divider list; purely presentational.

## Pitfalls

- Headers built as `<div onclick>` with no `aria-expanded` and no heading element — no state announcement and no heading navigation.
- Putting `aria-expanded` on the panel instead of on the toggle button (it belongs on the control).
- Hiding collapsed panels with CSS `height:0`/`opacity:0` while leaving them in the tab order, so keyboard focus disappears into invisible content.
- Disabling the button of the currently-open item in single-expand mode, trapping the user unable to collapse it.
- Relying on the chevron rotation alone to signal open/closed, with no `aria-expanded`.
- Wrapping the whole header row in the button (including large empty areas) without ensuring the accessible name is just the section title.
