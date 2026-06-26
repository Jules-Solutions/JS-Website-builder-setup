---
type: REFERENCE
corpus: component-patterns
title: Testimonial
component_slug: testimonial
also_known_as: [customer quote, social proof, review card, endorsement, pull quote]
consumed_by_phases: [9, 17, 18]
---

# Testimonial

> A short customer quote presented with attribution — name, role, and a photo or company logo — used as social proof that other people trust the thing the page is selling.

## Purpose

A testimonial borrows credibility. A visitor discounts what a brand says about itself but trusts what a customer says about the brand, so the testimonial converts skepticism into confidence at the exact moment a decision is being weighed. The quote carries the emotional payoff ("it saved us a week"), the attribution makes it believable (a real named person at a real company), and an optional rating or logo amplifies authority. A page uses testimonials near pricing, near a CTA, or as a standalone wall of proof to reduce the perceived risk of acting.

## When to use / when not

- **Use when:** the page asks the visitor to commit (buy, sign up, book) and you have genuine, attributable customer praise that speaks to a specific outcome or objection.
- **Avoid when:** the quote is anonymous, invented, or generic ("Great product!") — unattributed or vague testimonials read as filler and can erode trust rather than build it. Prefer a concrete case-study stat instead.

## Anatomy

| Part | Role |
|---|---|
| Figure wrapper | Outer container grouping the quote with its attribution as one unit |
| Quote body | The customer's words, the emotional core of the block |
| Rating (optional) | Star or score indicator reinforcing satisfaction |
| Attribution line | Who said it — name, role, company |
| Avatar / logo | Customer photo or company mark establishing they are real |
| Source link (optional) | Link to the original review, case study, or profile |

## Content slots

| Slot | Required? | Source layer | Notes |
|---|---|---|---|
| Quote text | Yes | content/pages | The testimonial prose; keep to 1-3 sentences |
| Attribution name | Yes | content/strings | Full name of the person quoted |
| Attribution role + company | Yes | content/strings | E.g. "Head of Ops, Northbeam" |
| Avatar image | No | media | Customer headshot; needs descriptive `alt` |
| Company logo | No | media | Alternative to avatar; `alt` is the company name |
| Star rating value | No | components.yaml | Numeric value (e.g. 5 of 5) rendered as stars |
| Source URL | No | sitemap.yaml | Link to the full review or case study |
| Color/type tokens | Yes | brand.yaml | Surface, on-surface, accent for marks/stars |

## Accessibility requirements

- **Semantic structure:** wrap the unit in `<figure>`, put the quote in `<blockquote>`, and place the attribution in `<figcaption>`. The attribution is *not* part of the quotation, so it belongs in `figcaption`, never inside `blockquote`. Use `<cite>` around the work or source name within the caption, not around a person's name (per HTML spec, `cite` is for titles of works).
- **Avatar alt text:** a customer photo gets descriptive alt naming the person, e.g. `alt="Maria Chen"`. A company logo gets the company name as alt, e.g. `alt="Northbeam"`. Never leave a meaningful avatar with empty `alt`; if the same name already appears as visible text in the caption, the photo is decorative and may take `alt=""` to avoid duplicate announcement.
- **Star ratings need a text equivalent:** stars rendered as icons, glyphs, or background images convey nothing to a screen reader. Provide an accessible text equivalent — either visually-hidden text ("Rated 5 out of 5 stars") or `role="img"` with `aria-label="5 out of 5 stars"` on the rating wrapper. Do not rely on color or filled-vs-empty shape alone.
- **Keyboard:** a static testimonial has no interaction; if a source link is present it is a standard focusable `<a>`, reachable with `Tab` and activated with `Enter`, with a discernible accessible name (avoid bare "Read more" — use "Read Maria Chen's full review").
- **Color contrast:** quote and attribution text meet WCAG 2.2 — 4.5:1 for normal text, 3:1 for large-scale pull-quote text. Decorative star fills are not held to text contrast but should still be distinguishable.
- **Reduced motion:** if testimonials auto-rotate in a carousel, pause under `prefers-reduced-motion: reduce` and always provide a manual pause control and prev/next buttons regardless of motion preference.

## Common variants

- **Single quote** — one centered testimonial, often oversized as a pull quote.
- **Grid / wall** — multiple cards in a responsive grid for cumulative proof.
- **Carousel** — rotating quotes with pause and prev/next controls.
- **Logo-led** — company logo replaces the avatar, for B2B credibility.
- **Rating-led** — prominent star score above the quote (e.g. review aggregations).
- **Video testimonial** — a thumbnail plays a customer clip; needs captions and a transcript.

## Pitfalls

- Putting the attribution inside `<blockquote>` so it reads as part of the quotation.
- Star ratings with no text equivalent — invisible to screen readers and colorblind users.
- Avatars with empty or filename `alt`, or duplicate announcement when the name is already visible.
- Auto-rotating carousels with no pause control and no reduced-motion fallback.
- Fabricated or anonymous quotes ("A happy customer") that read as filler and damage trust.
