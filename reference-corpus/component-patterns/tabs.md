---
type: REFERENCE
corpus: component-patterns
title: Tabs
component_slug: tabs
also_known_as: [tab panel, tabbed interface, tab strip, segmented content]
consumed_by_phases: [9, 17, 18]
---

# Tabs

> A set of layered content panels where only one is visible at a time, switched by a horizontal (or vertical) row of tab controls — letting a page present parallel slices of content in a single compact area.

## Purpose

Tabs organise several peer chunks of content into one footprint, so the visitor scans the labels and reveals just the slice they want. They work when the chunks are genuinely alternatives — "Overview / Specs / Reviews", "Monthly / Annual" pricing, "For teams / For individuals" — and the user rarely needs two at once. A page uses tabs to reduce scroll and visual noise while keeping related content one click apart, without sending the user to a new page.

## When to use / when not

- **Use when:** content divides into a few mutually-exclusive, peer categories the user toggles between, and seeing one at a time is fine.
- **Avoid when:** the user needs to compare panels side by side, the content is sequential (use steps), there are many tabs that won't fit (use a menu or sub-navigation), or the panels are long-form content better suited to anchored sections or an accordion. Tabs hide content from search-in-page and can hurt SEO if critical copy is buried in an inactive panel.

## Anatomy

| Part | Role |
|---|---|
| Tablist | The container grouping the tab controls |
| Tab | One clickable control naming a panel; the selected one is highlighted |
| Tab panel | The content region paired 1:1 with a tab; only the active one is shown |
| Active indicator | The visual marker (underline, fill) showing the selected tab |

## Content slots

| Slot | Required? | Source layer | Notes |
|---|---|---|---|
| Tab labels | Yes | content/strings | Short noun labels; one per panel, order is meaningful |
| Panel content | Yes | content/pages | The body for each tab; prose, media, or nested components |
| Default selected tab | No | components.yaml | Which tab is active on load (defaults to first) |
| Orientation | No | components.yaml | Horizontal (default) or vertical tablist |
| Activation mode | No | components.yaml | Automatic vs manual activation (see a11y) |
| Tablist accessible name | No | content/strings | `aria-label` describing the group ("Pricing options") |
| Token styling (active/hover/focus) | Yes | brand.yaml | Indicator color, tab text states, focus ring |

## Accessibility requirements

Implements the **WAI-ARIA APG "Tabs" pattern** exactly.

- **Roles & structure:** the tablist container has `role="tablist"`; each tab has `role="tab"`; each panel has `role="tabpanel"`. Render tabs as real `<button>`s carrying `role="tab"`. Give the tablist an accessible name with `aria-label` or `aria-labelledby`. If the tablist is vertical, set `aria-orientation="vertical"` (default is horizontal).
- **Wiring tabs to panels:** each tab has `aria-controls` pointing at its panel's id; each panel has `aria-labelledby` pointing at its tab's id, so the panel is named by its tab.
- **Selected state:** exactly one tab has `aria-selected="true"`; all others `aria-selected="false"`. The matching panel is shown; the rest are hidden (`hidden` attribute or `display:none`) so they're out of the tab order and the accessibility tree.
- **Roving tabindex:** only the selected tab is in the Tab sequence (`tabindex="0"`); every other tab has `tabindex="-1"`. `Tab` therefore moves focus INTO the tablist (landing on the active tab) and OUT to the active panel — it does not step through individual tabs.
- **Keyboard — within the tablist:** `Left`/`Right` arrows move between tabs in a horizontal tablist (`Up`/`Down` for vertical), wrapping from last to first and first to last. `Home` moves to the first tab, `End` to the last. As focus moves, the roving `tabindex="0"` moves with it.
- **Activation mode:** with **automatic activation** (recommended when revealing a panel is cheap), arrowing to a tab selects it and shows its panel immediately. With **manual activation** (when showing a panel is expensive, e.g. a network fetch), arrowing only moves focus; the user presses `Enter` or `Space` to activate — set this when panels are heavy so users aren't forced through every panel.
- **Panel focus:** `Tab` from the active tab moves focus to its panel. If the panel has no focusable children, give the panel `tabindex="0"` so keyboard users can reach and scroll its content; if it has focusable children, leave it out of the tab order.
- **Contrast & motion:** the selected-tab indicator must be conveyed by more than color (an underline/weight change, not just a hue); tab text and indicator meet WCAG 2.2 contrast (3:1 for the indicator as a UI component); focus indicators are always visible; any sliding-indicator animation respects `prefers-reduced-motion: reduce`.

## Common variants

- **Horizontal tabs** — the default top strip with an underline indicator.
- **Vertical tabs** — tablist on the side with `aria-orientation="vertical"`; arrows are Up/Down.
- **Pill / segmented control** — visually a toggle group but the same tab semantics.
- **Scrollable / overflow tabs** — many tabs that scroll horizontally on narrow viewports.
- **Manual-activation tabs** — panels loaded on Enter/Space to defer expensive fetches.
- **Tabs-to-accordion (responsive)** — collapse into an accordion on small screens; swap roles at the breakpoint, never mix them.

## Pitfalls

- Building tabs from `<div>`s with click handlers and no `role="tab"`/`tablist`/`tabpanel` — no semantics, no keyboard model.
- Leaving all tabs in the Tab order instead of using roving tabindex, so `Tab` laboriously steps through every tab.
- Arrow keys do nothing — the single most common APG-conformance failure for tabs.
- Inactive panels left in the DOM as merely visually hidden, so they stay in the tab order and accessibility tree.
- Signalling the active tab with color alone, failing for colorblind users.
- Burying SEO- or task-critical content in a non-default panel where it's hidden from in-page find and may be devalued by crawlers.
