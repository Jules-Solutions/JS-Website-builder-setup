---
type: REFERENCE
corpus: component-patterns
title: Card
component_slug: card
also_known_as: [content card, tile, panel, teaser]
consumed_by_phases: [9, 17, 18]
---

# Card

> A self-contained, rectangular container that groups a single subject's media, heading, text, and optional action so it reads and behaves as one unit.

## Purpose

A card packages one coherent thing — a blog post, a product, a service, a team member — into a scannable block that can sit beside its peers in a grid or list. It does the UX job of *chunking*: it lets a visitor compare many items at a glance and pick one to act on. Cards convert because they give each item a clear visual boundary, a hierarchy (image → title → supporting text → action), and an obvious tap target, which lowers the cost of choosing.

## When to use / when not

- **Use when:** presenting a collection of similar, independent items where each has its own image/title/summary and (usually) its own destination — listings, galleries-of-articles, product grids, feature teasers.
- **Avoid when:** the items are not parallel (use prose or a definition list), there is only one item (use a plain section/hero), or the content is dense tabular data (use a table). Don't nest cards inside cards — the boundaries stop meaning anything.

## Anatomy

| Part | Role |
|---|---|
| Container | The bounding surface (border, radius, shadow, padding) that signals "one unit" |
| Media | Optional leading image/illustration/video thumbnail |
| Eyebrow / category | Optional small label above the title (tag, date, type) |
| Heading | The card's title — the primary identifier, and the link target when the card links |
| Body text | A short supporting summary or excerpt |
| Metadata | Optional author, date, price, rating |
| Action | Optional explicit control (button or link) — "Read more", "Add to cart" |

## Content slots

| Slot | Required? | Source layer | Notes |
|---|---|---|---|
| `media` | No | media | Decorative or informative; alt text comes from `content/strings` |
| `media_alt` | Conditional | content/strings | Required if media is informative; empty `alt=""` if purely decorative |
| `eyebrow` | No | content/strings | Category/date/tag microcopy |
| `heading` | Yes | content/pages | Wraps the primary link if the whole card is clickable |
| `href` | No | sitemap.yaml | Destination route; resolved from sitemap, not hand-typed |
| `body` | No | content/pages | Excerpt or summary prose |
| `metadata` | No | content/pages | Author/date/price pulled from page front-matter or item data |
| `action_label` | No | content/strings | CTA microcopy when an explicit button is used |
| `variant` | No | components.yaml | Selects elevated / outlined / horizontal shape + radius/shadow tokens from brand.yaml |

## Accessibility requirements

- **Element & landmark:** render as `<article>` when the card is a self-contained composition; a grid of cards is best wrapped in a `<ul>` with each card an `<li>` so assistive tech announces the count.
- **Heading level:** the card title is a real heading (`<h2>`/`<h3>`) chosen to fit the page's outline — never a styled `<div>`.
- **Whole-card-clickable trade-off (the key decision):** prefer the *one accessible link* pattern — put a single `<a>` around the heading text and stretch it over the whole card visually (e.g. an absolutely-positioned `::after` overlay on the link). This gives exactly one tab stop and one descriptive accessible name (the title), while the entire surface is still clickable by mouse/touch. Do **not** wrap the whole card markup in one `<a>` (it swallows the image, text, and any inner controls into one giant, noisy link name), and do **not** add an `onclick` to a `<div>` (not keyboard-focusable, no role).
- **Multiple actions:** if a card needs more than one target (title link *and* an "Add to cart" button), the stretched-link pattern breaks — use distinct, separately-focusable controls and ensure inner interactive elements sit above the overlay (`position: relative; z-index`).
- **Keyboard & focus:** the link/button is reached with `Tab`, activated with `Enter` (and `Space` for buttons). Show a visible `:focus-visible` outline on the focused control; the hover affordance on the card must have a focus equivalent.
- **ARIA:** usually none needed — semantic `<article>`/`<a>`/`<h*>` carry the meaning. If the card surfaces a state (e.g. selected), expose it on the control with `aria-pressed` or `aria-current`, not on the container.
- **Contrast & motion:** text over media needs a scrim/overlay to keep ≥ 4.5:1 (3:1 for large text); hover lift/scale animations must be suppressed under `prefers-reduced-motion: reduce`.

## Common variants

- **Elevated** — shadow-raised surface, no border.
- **Outlined** — border, no shadow (flatter, denser grids).
- **Horizontal** — media beside text instead of above (good for list rows).
- **Media-overlay** — text sits on top of a full-bleed image with a scrim.
- **Action card** — body plus a prominent footer button.
- **Skeleton/loading** — placeholder shimmer with `aria-busy="true"` while data loads.

## Pitfalls

- Wrapping the entire card in one `<a>`, producing an unusable, verbose link name and trapping inner controls.
- Using a clickable `<div>` with `onclick` — invisible to keyboard and screen-reader users.
- Putting interactive elements (a button, a second link) *inside* a stretched-link overlay so they become unclickable.
- Decorative card images with redundant or missing `alt` (use `alt=""` for purely decorative; never repeat the title).
- Low-contrast text on busy hero imagery with no scrim, failing WCAG 1.4.3.
