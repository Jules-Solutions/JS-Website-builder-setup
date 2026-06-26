---
type: REFERENCE
corpus: component-patterns
title: Pricing Table
component_slug: pricing-table
also_known_as: [pricing tiers, plan comparison, pricing cards, plan picker, tier grid]
consumed_by_phases: [9, 17, 18]
---

# Pricing Table

> A side-by-side presentation of two or more pricing tiers, each listing its price, included features, and a call-to-action, so a visitor can compare plans and choose one.

## Purpose

The pricing table is where consideration becomes commitment. It has to make the differences between tiers scannable, steer most visitors toward the intended plan (usually via a "most popular" highlight), and remove friction from the final click. Good pricing tables reduce decision paralysis: clear feature deltas, an obvious recommended tier, and a per-tier CTA that names the plan it commits to. A page uses it as the conversion engine of a SaaS, service, or membership offer — everything else on the page exists to get the visitor here ready to pick.

## When to use / when not

- **Use when:** you sell two or more distinct, comparable plans and the visitor's main job is to choose between them on price and features.
- **Avoid when:** there is a single offer (use a focused CTA block instead) or pricing is fully custom/quote-based (use a "contact sales" path). A multi-column table for one real plan manufactures false choice.

## Anatomy

| Part | Role |
|---|---|
| Region wrapper | Outer landmark grouping all tiers as one comparison unit |
| Billing toggle (optional) | Switch between monthly / annual pricing |
| Tier column / card | One plan: name, price, features, CTA |
| Tier name | The plan label (e.g. Starter, Pro, Enterprise) |
| Price + period | The amount and its billing cadence |
| Feature list | What the tier includes; ideally aligned across tiers |
| Highlight badge | "Most popular" / "Recommended" marker on one tier |
| Per-tier CTA | The button or link that selects that specific plan |

## Content slots

| Slot | Required? | Source layer | Notes |
|---|---|---|---|
| Tier names | Yes | components.yaml | Ordered list of plans driving the columns |
| Price + period per tier | Yes | components.yaml | Amount + cadence; currency from brand.yaml/locale |
| Feature rows | Yes | content/pages | Per-tier inclusions; phrase consistently across tiers |
| CTA label per tier | Yes | content/strings | Must be unique per tier (see accessibility) |
| CTA target per tier | Yes | sitemap.yaml | Checkout / signup route for that plan |
| "Most popular" label | No | content/strings | Text label, not just a color accent |
| Billing-toggle labels | No | content/strings | "Monthly" / "Annual (save 20%)" |
| Color/type tokens | Yes | brand.yaml | Surface, accent, on-accent for the highlight |

## Accessibility requirements

- **Cards vs real table semantics:** if tiers are independent "cards," each is a `<section>`/`<article>` with the tier name as its heading (e.g. `h3`), and feature lists are real `<ul>`. If you present a true feature-comparison matrix (features as rows, tiers as columns), use a semantic `<table>` with `<th scope="col">` for tier headers and `<th scope="row">` for feature names so screen readers announce the cell's row and column context. Do not fake a grid with `<div>`s when the data is genuinely tabular.
- **"Most popular" highlight needs a text label:** the recommended tier must be marked with actual text ("Most popular"), not color or a border alone — color is not perceivable to colorblind or screen-reader users (WCAG 1.4.1 Use of Color). Associate the badge with the tier programmatically, e.g. `aria-describedby` from the heading to the badge, or include it in the heading's accessible name.
- **Unique CTA accessible names:** every per-tier button must have a distinct accessible name. Three buttons all labelled "Choose" or "Get started" are ambiguous out of context to a screen-reader user navigating by buttons. Use "Choose Starter", "Choose Pro", "Choose Enterprise" — either as visible text or via `aria-label` that includes the tier name.
- **Button vs link semantics:** a CTA that navigates to a checkout/signup URL is an `<a>`; one that triggers an in-page action (open a modal, add to cart via script) is a `<button>`.
- **Billing toggle:** implement as a grouped control — either two `role="radio"` options in a `role="radiogroup"` with an accessible group label, or a labelled `<button>` with `aria-pressed`. Toggling must update prices in a way screen readers notice (move focus or use a polite live region); never change prices silently.
- **Keyboard + focus:** all toggles and CTAs are reachable in DOM order with `Tab`, activate on `Enter` (links/buttons) and `Space` (buttons), and show a visible focus indicator per WCAG 2.2 Focus Appearance.
- **Color contrast:** prices, feature text, and CTA labels meet 4.5:1 (3:1 for large display prices). The highlighted tier's accent background must still pass contrast against its on-accent text.

## Common variants

- **Two-tier** — simple good/better split.
- **Three-tier with highlight** — the classic Starter / Pro / Enterprise with Pro recommended.
- **Feature-matrix** — a true comparison table, features as rows, tiers as columns.
- **Toggle-driven** — monthly/annual switch recomputes all prices.
- **Usage-based** — a slider or input estimates price from a usage metric.
- **Contact-sales tier** — final column swaps price for a "Talk to us" link.

## Pitfalls

- Identical CTA labels ("Choose", "Buy") across tiers — ambiguous to screen-reader and voice users.
- Marking the popular plan with color/border only, with no text label.
- Rendering a genuine comparison matrix as nested `<div>`s, losing row/column announcement.
- Toggling billing period without announcing the price change to assistive tech.
- Inconsistent feature wording between tiers so the actual delta is hard to scan.
