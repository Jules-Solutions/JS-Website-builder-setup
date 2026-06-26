---
type: REFERENCE
corpus: component-patterns
title: Navigation Bar
component_slug: nav
also_known_as: [navbar, primary navigation, header nav, top nav, masthead navigation]
consumed_by_phases: [9, 17, 18]
---

# Navigation Bar

> The site-wide primary navigation, usually pinned to the top of every page, exposing the main routes and the home/brand link.

## Purpose

The navigation bar is the persistent map of the site. It tells visitors where they can go, signals where they currently are, and gives a one-click route home via the brand. Because it appears on every page, it is the backbone of orientation and a major driver of cross-page exploration — a clear nav reduces bounce by making the site's breadth legible. On small screens the same routes collapse behind a toggle to preserve space without losing access.

## When to use / when not

- **Use when:** the site has more than one page or section and visitors need a consistent way to move between top-level destinations.
- **Avoid when:** the page is a focused single-task flow (checkout, onboarding wizard, distraction-free landing) where you deliberately strip navigation to keep the user on one path — use a minimal logo-only header instead.

## Anatomy

- **`nav` landmark** — the outer container marking primary navigation.
- **Brand / home link** — logo or wordmark linking to the home route (top-left in LTR).
- **Skip link** — a visually-hidden-until-focused link as the first focusable element, jumping to `#main`.
- **Navigation list** — an unordered list of top-level link items.
- **Active item** — the link matching the current page, marked as current.
- **Dropdown / submenu** (optional) — disclosure-revealed group of child links under a top-level item.
- **Utility cluster** (optional) — search, account, locale, or a primary CTA.
- **Mobile toggle** — the hamburger button that discloses the collapsed menu below a breakpoint.

## Content slots

| Slot | Required? | Source layer | Notes |
|---|---|---|---|
| Brand mark + home target | Yes | media + sitemap.yaml | Logo asset; home route from sitemap root |
| Top-level link labels + targets | Yes | sitemap.yaml | The nav order mirrors the sitemap's top level |
| Submenu groupings | No | sitemap.yaml | Nested sitemap children become dropdowns |
| Active-state rules | Yes | sitemap.yaml | Current route → `aria-current="page"` |
| Skip-link label | Yes | content/strings | E.g. "Skip to main content" |
| Mobile toggle accessible name | Yes | content/strings | E.g. "Menu" / "Open navigation" |
| Utility/CTA label + target | No | content/strings + sitemap.yaml | Optional account/search/CTA |
| Color, height, type tokens | Yes | brand.yaml | Surface, on-surface, focus ring, sticky shadow |

## Accessibility requirements

- **Landmark:** wrap the navigation in a `<nav>` element. If a page has more than one `<nav>` (e.g. primary + footer), give each a distinct `aria-label` (`aria-label="Primary"`). One unnamed `<nav>` is fine; multiple must be labelled.
- **List semantics:** render links as `<li>` inside a `<ul>`, so assistive tech announces item count. Use real `<a href>` elements for navigation, not click-handled `<div>`s.
- **Current page:** mark the link for the current page with `aria-current="page"`. Do not rely on color alone to show the active item.
- **Skip link:** the first focusable element in the DOM is a skip link (`<a href="#main">`) that is off-screen until focused, then visible. The target container must be focusable (`id="main"`, on a `<main>` or with `tabindex="-1"`).
- **Mobile toggle (disclosure pattern, per WAI-ARIA APG):** the hamburger is a `<button>` with `aria-expanded` reflecting state (`false` collapsed, `true` open) and `aria-controls` pointing at the menu container's `id`. It needs an accessible name ("Menu") even when icon-only. `Enter`/`Space` toggle it; the label/icon may swap to a close affordance when open.
- **Focus management on toggle:** opening the menu moves focus into or keeps it logically adjacent to the menu; pressing `Escape` while the menu is open closes it and returns focus to the toggle button. Tab order must not leak to off-screen items while the menu is collapsed (use `hidden`/`display:none`, not just visual offset).
- **Dropdown submenus:** if a top-level item opens a submenu, the trigger is a `<button>` with `aria-expanded` + `aria-controls`; `Escape` closes it and returns focus to the trigger. A simple hover-only menu must also be operable by keyboard.
- **Color contrast:** link text and the focus indicator meet WCAG 2.2 (4.5:1 text; 3:1 non-text/focus). The active-item indicator must be perceivable without color (underline, weight, or marker).
- **Reduced motion:** slide/expand animations on the mobile drawer and sticky-header transitions respect `prefers-reduced-motion: reduce` (collapse instantly, no large-motion transitions).

## Common variants

- **Horizontal bar** — top-level links in a row; the default desktop layout.
- **Sticky / pinned** — stays fixed on scroll, often with a condensed height after scrolling.
- **Centered logo** — brand centered with links split left/right.
- **Mega-menu** — wide multi-column dropdown for sites with many sections.
- **Off-canvas drawer** — mobile menu slides in from the side as a disclosure panel.
- **Transparent-over-hero** — nav overlays the hero, then gains a solid background on scroll.

## Pitfalls

- Hamburger as a `<div>` or `<span>` with no `aria-expanded` and no real button semantics — invisible/unoperable to screen readers and keyboards.
- Collapsed mobile menu hidden only with `opacity`/`transform`, leaving its links in the Tab order off-screen.
- No skip link, forcing keyboard users to tab through the entire nav on every page.
- Marking the active item with color only, failing both contrast and color-independence requirements.
- Forgetting `Escape`-to-close and focus-return on the toggle/dropdown, trapping or disorienting keyboard users.
