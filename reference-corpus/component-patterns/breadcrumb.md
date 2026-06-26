---
type: REFERENCE
corpus: component-patterns
title: Breadcrumb
component_slug: breadcrumb
also_known_as: [breadcrumbs, breadcrumb trail, location trail, hierarchy trail]
consumed_by_phases: [9, 17, 18]
---

# Breadcrumb

> A single-line trail of links showing the current page's position within the site hierarchy, from the root down to the page you're on.

## Purpose

A breadcrumb answers "where am I, and how did I get into this part of the site?" It exposes the parent path so a visitor deep in a hierarchy (a product inside a category inside a department) can jump back up one or several levels in one click, instead of relying on the browser Back button. It is most valuable on sites with genuine depth — catalogs, documentation, multi-level marketing sites — where it reduces disorientation, aids exploration, and gives search engines explicit hierarchy signals.

## When to use / when not

- **Use when:** the site has a clear, multi-level hierarchy (3+ levels) and pages are reached by drilling down — categories, docs trees, nested resource libraries.
- **Avoid when:** the site is flat (one level of top-level pages) or the path is single-step — a breadcrumb of "Home / This page" is noise. Also avoid using it as a substitute for primary navigation; it complements, never replaces, the nav.

## Anatomy

- **`nav` landmark** — a `<nav aria-label="Breadcrumb">` wrapping the trail.
- **Ordered list** — an `<ol>` whose item order encodes hierarchy depth, root-first.
- **Trail items** — each ancestor as a `<li>` containing an `<a href>` to that level.
- **Separators** — visual dividers (`/`, `›`, `→`) between items, presentational only.
- **Current item** — the last `<li>`, representing the current page, not a link, marked current.

## Content slots

| Slot | Required? | Source layer | Notes |
|---|---|---|---|
| Trail item labels | Yes | sitemap.yaml | Ancestor titles derived from the route hierarchy |
| Trail item targets | Yes | sitemap.yaml | Each ancestor's URL; the current page has none |
| Current page label | Yes | content/pages | The leaf node's title, not linked |
| Root label | Yes | content/strings | Usually "Home"; localizable |
| `nav` accessible name | Yes | content/strings | The string "Breadcrumb" (localizable) |
| Separator glyph | No | components.yaml | Presentational; chosen by the component shape |
| Color & type tokens | Yes | brand.yaml | Link color, muted current-item color, focus ring |

## Accessibility requirements

This follows the **WAI-ARIA Authoring Practices Guide breadcrumb pattern** precisely:

- **Landmark + name:** wrap the breadcrumb in a `<nav>` with `aria-label="Breadcrumb"` (or `aria-labelledby`). The label distinguishes it from the primary `<nav>` so landmark navigation lists both clearly.
- **Ordered list:** the set of links is an `<ol>` (order is meaningful — it is the hierarchy), with one `<li>` per level. Do not use a bare row of `<a>` tags; the list structure conveys position and count.
- **Current page:** the link representing the current page carries `aria-current="page"`. Per APG, the current item is typically rendered as plain text rather than a link (or a link to itself with `aria-current="page"`); either way `aria-current="page"` marks it. Only one item has `aria-current="page"`.
- **Separators are presentational:** render `/` or `›` via CSS (`::before`/`::after`) or mark inline separator characters `aria-hidden="true"`. Separators must never be inside the link text or announced as content; assistive tech should hear only the labels.
- **Links:** every ancestor is a real `<a href>` with a discernible text name; keyboard users reach each with `Tab` and activate with `Enter`. Focus order is root-to-leaf, matching the visual order.
- **Focus visibility:** each link shows a visible focus indicator meeting WCAG 2.2 Focus Appearance.
- **Color contrast:** link text meets 4.5:1; the muted current-page text must also meet 4.5:1 — do not drop it below threshold to signal "inactive."
- **No keyboard traps / no extra widgets:** the breadcrumb is static links; it needs no roving tabindex or arrow-key handling. Keep it simple — overriding native link behavior is an anti-pattern here.
- **Reduced motion:** if a collapsed breadcrumb expands (see truncated variant), the expand respects `prefers-reduced-motion: reduce`.

## Common variants

- **Full trail** — every ancestor shown; the canonical form for moderate depth.
- **Truncated / collapsed** — middle items collapse behind an ellipsis disclosure for very deep paths, expanding on activation.
- **Icon root** — the root "Home" item is a home icon with an accessible name instead of text.
- **Current-as-text** — the leaf is non-interactive text with `aria-current="page"` (APG-recommended default).
- **With structured data** — same markup augmented with `BreadcrumbList` schema for search engines.

## Pitfalls

- Putting the separator character inside the link or list text so screen readers announce "Products slash."
- Using an unordered `<ul>` or a flat run of `<a>` tags, losing the meaningful order and item count.
- Omitting `aria-current="page"` on the leaf, so the current location isn't programmatically identifiable.
- Making the current page a normal link to itself with no `aria-current` — a confusing no-op link.
- Treating the breadcrumb as primary navigation, or showing a one-level "Home / Page" trail that adds clutter with no orientation value.
