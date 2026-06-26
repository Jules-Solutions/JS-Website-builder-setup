---
type: REFERENCE
corpus: component-patterns
title: FAQ
component_slug: faq
also_known_as: [frequently asked questions, Q&A section, help section, common questions]
consumed_by_phases: [9, 17, 18]
---

# FAQ

> A section of question-and-answer pairs that pre-empts the visitor's common objections and doubts, usually rendered as a list of expandable disclosures and often enriched with FAQ structured data for search.

## Purpose

The FAQ does conversion work disguised as a help section: it answers the questions a hesitant visitor would otherwise email about — pricing, process, guarantees, "is this for me?" — removing friction right before they decide. Because the questions map to real search queries and support `FAQPage` rich results, a well-marked FAQ also earns SEO surface area and can occupy extra space on the results page. A page uses it near the conversion point (after pricing, before the footer CTA) to neutralise objections without a sales call.

## When to use / when not

- **Use when:** there's a recurring set of real visitor questions, you want to reduce support load and pre-empt objections, and the answers are short. Especially valuable on pricing, service, and product pages.
- **Avoid when:** you're padding the page with invented questions nobody asks (it reads as filler and Google penalises manufactured FAQ markup), or when the answers are long-form content better given their own pages/anchors. Don't use FAQ structured data for promotional or non-Q&A content — it violates search guidelines.

## Anatomy

| Part | Role |
|---|---|
| Section wrapper | The landmark region grouping the FAQ, with a section heading |
| Section heading | E.g. "Frequently asked questions"; the FAQ's `h2` |
| Q&A item | One question (disclosure header) + answer (collapsible region) |
| Question header | A heading wrapping the disclosure toggle button |
| Answer region | The collapsible content holding the answer |
| Structured-data block | Optional `FAQPage` JSON-LD describing the Q&A pairs for search |

## Content slots

| Slot | Required? | Source layer | Notes |
|---|---|---|---|
| Section heading | Yes | content/strings | "Frequently asked questions" or topical equivalent |
| Question text | Yes | content/pages | The real questions; phrased as visitors ask them |
| Answer text | Yes | content/pages | Concise answers; may include links to deeper pages |
| Heading level per question | Yes | components.yaml | Which `h3`/`h4` wraps each question under the section `h2` |
| Default-open behaviour | No | components.yaml | All collapsed (default) vs first-open |
| FAQPage structured data | No | content/pages | JSON-LD `FAQPage` mirroring the visible Q&A (SEO slot) |
| Token styling (header/divider/focus) | Yes | brand.yaml | Inherits accordion/disclosure tokens |

## Accessibility requirements

The FAQ is built on the **WAI-ARIA APG "Disclosure" pattern** (one independent expand/collapse per question), and when grouped it follows the **Accordion** pattern — see `accordion.md` for the full interaction model, which this component reuses rather than restates.

- **Disclosure model:** each question is a `<button>` with `aria-expanded` (`true`/`false`) and `aria-controls` pointing at its answer region's id. `Enter` and `Space` toggle it. A collapsed answer is removed from the tab order and accessibility tree via the `hidden` attribute, not just visually clipped. FAQ items are independent disclosures (multi-expand by default) — opening one does not close another.
- **Heading structure:** the section has one heading (`h2` typically), and EACH question's button is wrapped in a heading element one level down (`h3`/`h4`). This is essential for FAQs: screen-reader and keyboard users navigate by heading, so every question must be a heading, not a bare button — it lets a user jump question-to-question and gives the page a correct outline.
- **Keyboard:** headers are normal tab stops (no roving tabindex); `Tab`/`Shift+Tab` move through questions and into any open answer's links in DOM order; `Enter`/`Space` toggle. If rendered as a true accordion, the optional `Up`/`Down`/`Home`/`End` header navigation from `accordion.md` applies.
- **Decorative icons:** the +/− or chevron is `aria-hidden="true"`; open/closed state is conveyed by `aria-expanded`, never by the glyph alone.
- **Links in answers:** any link inside an answer must have a discernible accessible name and a visible focus indicator; only reachable when its answer is expanded (since collapsed answers are `hidden`).
- **Structured data must mirror the visible content:** if a `FAQPage` JSON-LD block (schema.org `Question`/`acceptedAnswer`/`Answer`) is emitted, the questions and answers in the markup MUST match what's visible on the page — hidden-only or mismatched FAQ markup violates Google's structured-data policy and risks a manual action. The JSON-LD is an SEO enhancement layered on top; it is not a substitute for accessible HTML.
- **Contrast & motion:** question text and focus indicators meet WCAG 2.2 contrast; expand/collapse animation is reduced or instant under `prefers-reduced-motion: reduce`.

## Common variants

- **Accordion FAQ** — questions in a single accordion group (most common); reuses accordion.md.
- **Independent disclosures** — each Q&A toggles alone with no grouping behaviour.
- **Categorised FAQ** — questions grouped under sub-headings (Billing, Shipping, Account).
- **Static / always-open** — plain heading-and-paragraph pairs with no collapsing (best for print/SEO when the list is short).
- **Searchable FAQ** — a filter input narrows a long question list.
- **Two-column FAQ** — questions laid out in columns on wide viewports; keep DOM/heading order linear.

## Pitfalls

- Manufacturing questions to bulk up the page or to game rich results — reads as filler and breaches structured-data guidelines.
- Emitting `FAQPage` JSON-LD that doesn't match the visible Q&A, or marking up content that isn't genuinely a question/answer.
- Rendering questions as styled `<div>`s instead of headings, destroying heading navigation and the page outline.
- Putting `aria-expanded` on the answer region instead of the question button.
- Hiding answers with CSS only (height/opacity) so collapsed text stays focusable and in the accessibility tree.
- Burying answers that contain the page's only mention of key info, where in-page find and crawlers may miss it if poorly implemented.
