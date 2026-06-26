---
type: REFERENCE
corpus: component-patterns
title: Banner / Announcement Bar
component_slug: banner
also_known_as: [announcement bar, notification bar, promo bar, cookie notice, top bar, alert bar]
consumed_by_phases: [9, 17, 18]
---

# Banner / Announcement Bar

> A slim, full-width strip pinned to the top of the page carrying a short, often dismissible message — a promotion, a policy notice, or a status alert.

## Purpose

The announcement bar surfaces one timely, site-wide message without interrupting the page the way a modal would. It's the lightest-weight way to say "free shipping this week," "we use cookies," or "scheduled maintenance tonight." Because it sits above everything and is usually dismissible, it trades a sliver of vertical space for guaranteed visibility. The job is signal, not navigation: one message, optionally one action, and a way to make it go away.

## When to use / when not

- **Use when:** there is exactly one short, broadly-relevant message (promo, legal/consent notice, transient status) that benefits every visitor and can be expressed in a sentence.
- **Avoid when:** the message is page-specific (use an inline notice in context), is critical and blocking (use a modal or inline form error), or when you'd stack multiple bars — a tower of banners erodes trust and pushes content down. One bar at a time.

## Anatomy

- **Region container** — the outer full-width strip, the first element in the page body.
- **Icon** (optional) — a small leading glyph hinting at message type (tag, info, warning).
- **Message text** — the single concise sentence, optionally with an inline link.
- **Action / CTA** (optional) — a link or button to act on the message ("Shop now," "Manage cookies").
- **Dismiss control** — a close button that hides the bar and persists the dismissal.

## Content slots

| Slot | Required? | Source layer | Notes |
|---|---|---|---|
| Message text | Yes | content/strings | One sentence; supports an inline link |
| Inline link / CTA label + target | No | content/strings + sitemap.yaml | Label is microcopy; route from sitemap |
| Leading icon | No | media | Decorative or type hint; hide if decorative |
| Dismiss button accessible name | Yes (if dismissible) | content/strings | E.g. "Dismiss announcement" |
| Severity / type | Yes | components.yaml | Selects promo / info / consent / alert styling + semantics |
| Persistence behavior | Yes | components.yaml | Whether dismissal is remembered (cookie/localStorage) |
| Color & type tokens | Yes | brand.yaml | Bar surface, on-surface, link/focus colors |

## Accessibility requirements

- **Choose the right semantics by urgency — this is the key decision:**
  - For a normal, non-urgent promo/info/consent bar that is present on page load, expose it as a labelled region: `role="region"` with `aria-label` (e.g. `aria-label="Announcement"`), or a `<section aria-label="Announcement">`. This lets users find and skip it without it shouting.
  - Reserve `role="alert"` (an assertive live region) for genuinely urgent, time-sensitive messages that appear dynamically and must interrupt — e.g. "Site going down in 2 minutes." `role="alert"` interrupts the screen-reader user immediately, so misusing it on a marketing bar is hostile. A non-urgent dynamically-inserted update should use `role="status"` / `aria-live="polite"` instead.
  - A consent/cookie notice is a region, not an alert. If it must trap interaction until answered, that's a dialog (`role="dialog"`), not a banner.
- **Dismiss button:** the close control is a real `<button>` with a discernible accessible name (`aria-label="Dismiss announcement"` for an icon-only ✕). It activates on `Enter` and `Space`. On dismiss, after the bar is removed move focus to a sensible place — typically the next focusable element or the page's main heading — so keyboard focus is never left on a detached element.
- **Keyboard:** the inline link/CTA and the dismiss button are reachable in DOM order with `Tab`. The bar must not trap focus (it is not a dialog). There is no required arrow-key behavior.
- **Focus visibility:** the link and dismiss button show a visible focus indicator meeting WCAG 2.2 Focus Appearance.
- **Heading levels:** the bar carries no heading (it's a single message); do not insert an `h1`/`h2` here that would disrupt the page outline. The page's `h1` remains in the main content.
- **Color contrast:** message text, link, and the dismiss icon meet WCAG 2.2 (4.5:1 text; 3:1 non-text/icon/focus). Do not encode meaning by color alone (e.g. a red "alert" bar still needs a word or icon conveying severity).
- **Reduced motion:** any slide-down entrance or auto-rotating multi-message ticker respects `prefers-reduced-motion: reduce`; an auto-advancing ticker also needs a pause control and must not be the only way to read each message.

## Common variants

- **Promo bar** — marketing offer with a "Shop"/"Learn more" link; region semantics.
- **Cookie / consent notice** — privacy disclosure with "Accept"/"Manage" actions; region (or dialog if blocking).
- **Status / maintenance alert** — urgent transient notice; `role="alert"` only when dynamically interrupting.
- **Sticky vs static** — pinned on scroll vs scrolls away with the page.
- **Dismissible vs persistent** — with a remembered close vs always-on (e.g. legal notice).
- **Rotating ticker** — cycles multiple messages; requires pause control + reduced-motion handling.

## Pitfalls

- Slapping `role="alert"` on a non-urgent promo bar, hijacking every screen reader on page load.
- An icon-only ✕ dismiss with no accessible name, announced as a bare "button."
- Removing the bar on dismiss but leaving keyboard focus on the now-detached close button.
- Stacking multiple bars, or re-showing a dismissed bar on every navigation because dismissal isn't persisted.
- Signaling severity with background color only, failing color-independence and often contrast too.
