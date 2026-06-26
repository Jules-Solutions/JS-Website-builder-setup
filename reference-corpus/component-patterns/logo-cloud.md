---
type: REFERENCE
corpus: component-patterns
title: Logo Cloud
component_slug: logo-cloud
also_known_as: [logo bar, trusted by, client logos, partner strip, press logos, as seen in]
consumed_by_phases: [9, 17, 18]
---

# Logo Cloud

> A horizontal strip or grid of client, partner, or press logos that signals "trusted by these organizations".

## Purpose

A logo cloud is fast, recognizable social proof: showing the marks of known clients, partners, integrations, or press outlets borrows their credibility. It does the conversion job of *trust transfer* — a visitor who recognizes a logo extends that recognition to the site. It usually sits just below the hero ("Trusted by") or near a pricing/contact CTA to reduce hesitation right before action.

## When to use / when not

- **Use when:** you have permission to display recognizable third-party marks that lend authority — real clients, integration partners, or press mentions.
- **Avoid when:** the logos aren't recognizable to the target audience (no trust is transferred), you lack rights to display them, or the row is padded with obscure/irrelevant marks (it reads as filler and can *reduce* trust). Don't use it as decorative texture — if it conveys "who", it conveys information.

## Anatomy

- **Section wrapper** — optional lead-in label ("Trusted by teams at", "As seen in").
- **Logo container** — the row/grid/marquee that holds the marks.
- **Logo item** (repeats) — the logo image, optionally wrapped in a link to the partner/press piece.
- **Optional divider / fade** — visual separators or edge fade on a scrolling marquee.

## Content slots

| Slot | Required? | Source layer | Notes |
|---|---|---|---|
| `lead_in` | No | content/strings | "Trusted by" / "Our partners" microcopy |
| `items[].logo` | Yes | media | Mono or full-color logo asset (prefer SVG) |
| `items[].name` | Yes | content/strings | Company/outlet name → the image's accessible name (alt) |
| `items[].href` | No | sitemap.yaml | Optional link to a case study, partner page, or press article |
| `items[].link_label` | Conditional | content/strings | Accessible name for the link if it differs from the logo name |
| `layout` | No | components.yaml | static-grid / row / marquee; gap + grayscale tokens from brand.yaml |
| `monochrome` | No | brand.yaml | Whether logos render desaturated until hover |

## Accessibility requirements

- **Accessible names (the key requirement):** each logo is an image whose `alt` is the **organization's name** (e.g. `alt="Acme Corp"`), not "logo" or "Acme logo" — the word "logo" is redundant and the role is already conveyed. Because the strip's whole *meaning* is "who trusts us", the logos are informative, **not** decorative: do not use `alt=""`. Even a visually muted/grayscale row must still expose each company name to assistive tech.
- **List semantics:** the logos are a list — render the container as `<ul>` with each logo an `<li>` so AT announces "list, N items" and the count communicates the breadth of the proof. If you strip list markers in CSS, re-assert `role="list"` on the `<ul>` for Safari/VoiceOver.
- **Linked logos:** when a logo links out, wrap the `<img>` in an `<a>`; the link's accessible name comes from the `alt` (or an explicit `aria-label`/visually-hidden text that says where it goes, e.g. "Read the Acme case study"). Avoid five links all named just the company with no destination cue if they go to different page types.
- **Lead-in association:** the "Trusted by" label should be a real heading or be referenced so the relationship is clear; if it's a heading, use an appropriate level (often `<h2>` or a visually-small `<p>` is fine when it's a caption-style lead-in).
- **Decorative-only edge case:** if a logo row is genuinely ornamental (rare), it should be removed from the accessibility tree entirely (`aria-hidden` on the group) rather than left as a row of nameless images — but if it conveys *who*, it is informative and must carry names. Don't half-do it.
- **Marquee/auto-scroll:** an auto-scrolling logo marquee is moving content — provide a pause mechanism or pause on hover/focus (WCAG 2.2.2), and stop the animation under `prefers-reduced-motion: reduce`. Non-animated static rows have no keyboard interaction and need no roles beyond the list.
- **Contrast:** monochrome/low-opacity logos must still meet non-text contrast (≥ 3:1) against the background to remain perceivable; don't fade them so far they're invisible to low-vision users.

## Common variants

- **Static row** — a single centered line of marks.
- **Grid** — multiple rows for many logos.
- **Marquee** — continuously scrolling strip (needs pause + reduced-motion handling).
- **Grayscale-to-color** — desaturated logos that colorize on hover/focus.
- **Linked logos** — each mark links to a case study or press article.
- **Press "as seen in"** — media outlet logos rather than client logos.

## Pitfalls

- Using `alt="logo"` or `alt=""` so screen-reader users never learn *who* trusts the site — the entire point is lost.
- Building the strip from bare `<img>`s with no list semantics, hiding the count that signals breadth.
- Auto-scrolling marquees with no pause control and no reduced-motion fallback.
- Fading logos to near-invisibility for "subtle" styling, failing non-text contrast.
- Identical link names on logos that lead to different destinations, leaving link-list users lost.
