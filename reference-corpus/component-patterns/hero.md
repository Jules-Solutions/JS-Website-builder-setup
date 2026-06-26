---
type: REFERENCE
corpus: component-patterns
title: Hero
component_slug: hero
also_known_as: [hero section, hero banner, above-the-fold, masthead, jumbotron]
consumed_by_phases: [9, 17, 18]
---

# Hero

> The first full-width block on a landing page: a headline, a supporting subhead, and a primary call-to-action that frames what the site is and what to do next.

## Purpose

The hero is the page's elevator pitch. In the first few seconds a visitor decides whether to stay, so the hero carries the single most important promise (the headline), one line of supporting context (the subhead), and the one action you most want taken (the primary CTA). Everything below the fold is detail; the hero is the offer. A page uses it to set context, establish brand tone instantly through type and imagery, and route the visitor toward the primary conversion path before they scroll.

## When to use / when not

- **Use when:** the page is a landing, marketing, or campaign page where a visitor arrives cold and needs an immediate value proposition plus a clear next step.
- **Avoid when:** the page is a content article, documentation, dashboard, or list view where the user already knows why they're here — a heavy hero just pushes the real content down. Prefer a compact page header instead.

## Anatomy

| Part | Role |
|---|---|
| Region wrapper | The outer landmark container that groups the hero as one unit |
| Eyebrow / kicker | Optional short label above the headline (category, tagline) |
| Headline | The primary promise; the page's `h1` |
| Subhead | One or two sentences of supporting context |
| CTA group | Primary action button + optional secondary link |
| Media | Optional background image, product shot, or illustration |
| Trust strip | Optional logos, rating, or microcopy reinforcing credibility |

## Content slots

| Slot | Required? | Source layer | Notes |
|---|---|---|---|
| Eyebrow text | No | content/strings | Short kicker; ≤ 4 words |
| Headline | Yes | content/pages | Becomes the `h1`; keep ≤ 12 words |
| Subhead | Yes | content/pages | Supporting sentence(s) |
| Primary CTA label + target | Yes | content/strings + sitemap.yaml | Label is microcopy; target route comes from the sitemap |
| Secondary CTA label + target | No | content/strings + sitemap.yaml | E.g. "Learn more" anchored to a section |
| Hero media | No | media | Background or foreground asset; needs `alt` if meaningful |
| Color/typography tokens | Yes | brand.yaml | Surface, on-surface, accent, display type scale |
| Layout variant | Yes | components.yaml | Selects centered / split / media-bg shape |

## Accessibility requirements

- **Semantic element:** wrap the hero in a `<section>`. Give it an accessible name so it appears as a labelled region — either `aria-labelledby` pointing at the headline's `id`, or `aria-label`. A plain `<section>` with no name is not exposed as a landmark.
- **Heading level:** the headline is the page's single `<h1>`. There must be exactly one `h1` per page and the hero is its natural home; do not skip levels (the next section heading is `h2`).
- **CTA semantics:** a CTA that navigates to a URL is an `<a>` (link); a CTA that triggers an in-page action is a `<button>`. Never style a `<div>` as a button — it loses keyboard and role semantics. Each CTA must have a discernible accessible name from its visible text; icon-only CTAs need `aria-label`.
- **Keyboard:** all CTAs are reachable in DOM order with `Tab`, activate on `Enter` (links and buttons) and also `Space` (buttons). Focus order must match visual order.
- **Focus visibility:** every CTA shows a visible focus indicator meeting WCAG 2.2 Focus Appearance; never remove the outline without a replacement.
- **Background media:** if a background image carries meaning it needs a text alternative; if purely decorative, mark it `aria-hidden="true"` / empty `alt=""` and ensure text contrast is computed against the darkest region (use an overlay scrim).
- **Color contrast:** headline and subhead text must meet WCAG 2.2 — 4.5:1 for body-size subhead, 3:1 for large-scale headline text. Verify against the actual pixels behind the text, not the average.
- **Reduced motion:** any autoplaying background video, parallax, or animated gradient must be paused or removed under `prefers-reduced-motion: reduce`, and looping video needs a pause control regardless.

## Common variants

- **Centered** — headline, subhead, CTA stacked and centered; no media or abstract background.
- **Split / asymmetric** — copy on one side, product shot or illustration on the other.
- **Media background** — full-bleed image or video behind the copy with a contrast scrim.
- **Gradient / pattern** — brand-token gradient background, no photographic media.
- **Form-led** — the primary CTA is an inline lead-capture form (email + submit) instead of a button.
- **Animated / sequenced** — staged entrance animation, gated behind reduced-motion.

## Pitfalls

- Using more than one `h1`, or demoting the headline to a styled `<div>` so screen readers lose the page title.
- Two or more competing primary CTAs — dilutes the single conversion action; keep one primary, at most one secondary.
- Text over a busy image with no scrim, failing contrast in the bright regions.
- Autoplaying video or parallax with no reduced-motion fallback and no pause control.
- Hero so tall it pushes all real content below the fold on common laptop viewports, hiding that the page continues.
