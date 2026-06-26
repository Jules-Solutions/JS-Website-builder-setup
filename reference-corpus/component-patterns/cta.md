---
type: REFERENCE
corpus: component-patterns
title: Call To Action
component_slug: cta
also_known_as: [CTA section, conversion block, action banner, closing CTA, sign-up band]
consumed_by_phases: [9, 17, 18]
---

# Call To Action

> A focused conversion block — a short headline and one dominant action — placed mid-page or at the end to convert intent into a click after the surrounding content has made its case.

## Purpose

A CTA section exists to capture momentum. By the time a visitor reaches it they have read the value proposition, the features, or the proof; the CTA gives that built-up intent somewhere to go before it dissipates. It works by being singular — one clear ask, stated as a benefit ("Start your free trial"), with minimal competing distraction. A page uses CTA blocks to punctuate the scroll: a mid-page CTA catches visitors already convinced, and a closing CTA is the last, strongest push before the footer.

## When to use / when not

- **Use when:** a section or page has built a case and you want to convert that attention into one specific action (sign up, buy, book, contact).
- **Avoid when:** the visitor lacks the context to act yet (a cold CTA with no preceding value falls flat) or when stacking so many CTA bands that each one dilutes the others. One dominant action per block; resist piling on alternatives.

## Anatomy

| Part | Role |
|---|---|
| Region wrapper | The outer landmark grouping the block as one unit |
| Headline | The benefit-framed prompt to act; a section heading |
| Supporting line (optional) | One sentence removing a final objection |
| Primary action | The single dominant button or link |
| Secondary action (optional) | A lower-emphasis alternative (e.g. "Learn more") |
| Reassurance microcopy (optional) | Risk-reducers like "No card required" |

## Content slots

| Slot | Required? | Source layer | Notes |
|---|---|---|---|
| Headline | Yes | content/pages | Benefit-led prompt; the block's heading |
| Supporting text | No | content/pages | One sentence; objection handling |
| Primary action label | Yes | content/strings | Specific verb phrase ("Start free trial") |
| Primary action target | Yes | sitemap.yaml | Route or external URL the action leads to |
| Secondary action label + target | No | content/strings + sitemap.yaml | Low-emphasis alternative |
| Reassurance microcopy | No | content/strings | "No credit card", "Cancel anytime" |
| Color/type tokens | Yes | brand.yaml | Accent, on-accent, surface for emphasis |
| Layout variant | Yes | components.yaml | Selects banner / centered / split shape |

## Accessibility requirements

- **Semantic element:** wrap the block in a `<section>` and give it an accessible name so it is exposed as a labelled landmark — `aria-labelledby` pointing at the headline `id`, or `aria-label`. An unnamed `<section>` is not announced as a region.
- **Heading level:** the headline is a real heading at the correct level for its position in the document outline (typically `h2` for a section within the page body), never a styled `<div>`. Do not skip levels.
- **Button vs link semantics — the core rule:** if the action *navigates* (goes to another page, an anchor, or an external URL) it must be an `<a>` with an `href`. If the action *does something on the page* (opens a dialog, submits inline, triggers script) it must be a `<button>`. This distinction is functional, not visual: links and buttons differ in keyboard behavior (`Space` activates buttons; links activate on `Enter`), in screen-reader announcement, and in expected outcome. Never style a `<div>` or `<span>` as a CTA — it has no role, no keyboard activation, and is invisible to assistive tech.
- **Accessible name quality:** the action's accessible name should make sense out of context. "Start free trial" is good; "Click here" or "Go" is not, because users who navigate by a list of links/buttons hear only the name. Icon-only actions require `aria-label`.
- **Single dominant action:** there should be exactly one primary action; a secondary action, if present, is visually and semantically subordinate. Two equally-weighted primary CTAs split attention and create a Use-of-Color/hierarchy problem.
- **Keyboard + focus:** actions are reachable in DOM order with `Tab`, activate on `Enter` (and `Space` for buttons), and show a visible focus indicator meeting WCAG 2.2 Focus Appearance. Focus order matches visual order.
- **Color contrast:** headline, supporting text, and action label meet WCAG 2.2 (4.5:1 normal, 3:1 large). A high-saturation accent band must still pass contrast for its on-accent text and any reassurance microcopy.
- **Reduced motion:** animated gradients, sliding entrances, or pulsing buttons must be neutralized under `prefers-reduced-motion: reduce`.

## Common variants

- **Full-width banner** — accent-colored band spanning the viewport with centered copy and action.
- **Centered card** — a contained card on a neutral surface, headline + button stacked.
- **Split** — copy on one side, the action (or a supporting image) on the other.
- **Inline form CTA** — the primary action is an email/lead-capture field plus submit.
- **Sticky CTA** — a persistent bar that follows the scroll (give it a dismiss control).
- **Dual-action** — primary plus a clearly subordinate secondary link.

## Pitfalls

- Using a `<div>`/`<span>` styled as a button — no role, no keyboard activation, invisible to AT.
- Mislabeling navigation as a button or an action as a link — wrong keyboard and announcement behavior.
- Vague accessible names ("Click here", "Submit", "Go") that fail out of context.
- Two co-equal primary CTAs competing for the one decision.
- A cold CTA with no preceding context, or so many CTA bands that none stands out.
