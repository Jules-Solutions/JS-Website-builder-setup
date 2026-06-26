---
type: REFERENCE
corpus: component-patterns
title: Stat Block
component_slug: stat-block
also_known_as: [stats bar, metrics row, key figures, by-the-numbers, KPI strip]
consumed_by_phases: [9, 17, 18]
---

# Stat Block

> A row or grid of big-number metrics, each pairing a prominent figure with a descriptive label (e.g. "10k+ users"), used to convey credibility and scale at a glance.

## Purpose

A stat block turns proof points into a punchy, scannable strip — "500+ clients", "99.9% uptime", "12 years in business". It does the conversion job of *social proof and credibility*: large numbers are visually arresting and communicate scale faster than prose. It typically sits below a hero or near a testimonial section to reinforce trust right before a call to action.

## When to use / when not

- **Use when:** you have a few concrete, impressive, verifiable metrics that build trust (counts, percentages, durations, ratings).
- **Avoid when:** the numbers are weak, vague, or unverifiable (they erode trust rather than build it), or when there are too many to compare meaningfully — 3 to 5 is the sweet spot. Don't use a stat block for data that needs context or a trend (use a chart) or for a single number (just state it inline).

## Anatomy

- **Section wrapper** — optional heading ("By the numbers") and intro.
- **Stat container** — the responsive row/grid (collapses to stacked on mobile).
- **Stat item** (repeats), each containing:
  - **Value** — the big number, often with a prefix/suffix (`$`, `+`, `%`, `k`, `M`).
  - **Label** — the short description of what the number measures.
  - **Optional detail** — a tiny clarifier or source note.
  - **Optional divider** — visual separator between items.

## Content slots

| Slot | Required? | Source layer | Notes |
|---|---|---|---|
| `section_heading` | No | content/pages | "By the numbers" / "Our impact" |
| `items[].value` | Yes | content/pages | The figure incl. prefix/suffix; the visually dominant element |
| `items[].label` | Yes | content/strings | What the number means; must be programmatically tied to the value |
| `items[].detail` | No | content/strings | Optional footnote/source microcopy |
| `items[].sr_value` | Conditional | content/strings | Spelled-out value for screen readers if the display form is ambiguous (e.g. "10k+" → "more than 10,000") |
| `columns` | No | components.yaml | Item count / layout; gap + divider tokens from brand.yaml |
| `value_style` | No | brand.yaml | Type-scale token for the big number (display/headline size) |

## Accessibility requirements

- **Programmatic association (the key requirement):** the big number and its label must be one announced unit, in the right reading order — value then label — so a screen reader says "10,000 plus, active users", not two orphaned fragments. Two robust patterns: (1) wrap each stat in a `<dl>` with the label as `<dt>` and the value as `<dd>` (description-list semantics bind them), or (2) group value + label in a single container and expose a combined accessible name via `aria-label` on the wrapper (e.g. `aria-label="More than 10,000 active users"`) while hiding the visual pieces from separate announcement. Do not rely on visual proximity alone — DOM order and grouping carry the meaning.
- **Reading order:** ensure the DOM order is value-before-label (or supply `aria-label`) even if CSS visually places the label above the number; screen readers follow the DOM, not the painted layout.
- **Ambiguous display values:** abbreviated/symbolic values ("10k+", "$2.4M", "99.9%") may be misread. Provide a clear spoken form via visually-hidden text or `aria-label` (e.g. show "10k+", expose "more than ten thousand"). Keep the `%` / `$` meaningful to AT — symbols are generally announced, but compact forms like "k"/"M" are not reliably expanded.
- **Heading/structure:** the section title is a real `<h2>`; the stat labels are usually `<dt>`/`<p>` text, not headings, since they aren't navigational landmarks.
- **Not interactive:** a stat block has no widgets, no keyboard interaction, and needs no roles beyond the list/description-list semantics. If a stat links to a source, treat that link with normal link a11y (descriptive accessible name).
- **Animated count-up:** if numbers animate from 0 to the target, the final value must be present in the DOM (set the real value as text and animate visually, or update `aria-label` to the final value) so AT never reads a mid-animation number; suppress the count-up under `prefers-reduced-motion: reduce`.
- **Contrast:** the big number and its label both meet contrast minimums (≥ 3:1 for the large value as large text, ≥ 4.5:1 for the smaller label).

## Common variants

- **Inline row** — single horizontal strip with dividers between figures.
- **Grid** — 2×2 or 3×N blocks for more metrics.
- **Icon + stat** — a small decorative glyph above each figure (`aria-hidden`).
- **Animated count-up** — figures tick up on scroll into view (with reduced-motion fallback).
- **Stat + trend** — value plus a small up/down indicator (give the indicator a text equivalent).
- **Card stats** — each stat in its own bordered surface.

## Pitfalls

- Marking up value and label as two separate, unlinked elements so AT reads them disconnected or out of order.
- Leaving compact values ("10k+", "1.2M") with no spelled-out screen-reader equivalent.
- Animating count-up without committing the final value to the DOM, so AT reads a wrong, transient number.
- CSS reordering label-above-value while the DOM has them reversed, breaking spoken reading order.
- Presenting weak or unsourced numbers that undercut credibility instead of building it.
