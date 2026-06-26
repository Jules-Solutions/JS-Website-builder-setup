---
type: REFERENCE
corpus: component-patterns
title: Team Grid
component_slug: team-grid
also_known_as: [team section, about-us people, staff grid, meet the team, leadership grid]
consumed_by_phases: [9, 17, 18]
---

# Team Grid

> A grid of people — each a photo, name, and role, with optional bio and social links — used to put faces to a company and build trust through transparency.

## Purpose

A team grid humanizes an organization. Visitors trust businesses run by visible, named people more than faceless brands, so an "about" or "team" page uses a grid of headshots to signal that real, accountable humans stand behind the work. The photo creates connection, the name and role establish expertise and structure, and optional bios or social links let a visitor go deeper or verify credibility. It is a trust and recruiting asset as much as an informational one.

## When to use / when not

- **Use when:** the page is an about, company, or leadership page where showing the people behind the brand builds credibility, or when recruiting and the culture is part of the pitch.
- **Avoid when:** the list is huge and unbounded (a full staff directory is better as a searchable, paginated list, not a flat grid) or when photos are inconsistent placeholders that would undercut rather than build trust. Prefer a simple roster instead.

## Anatomy

| Part | Role |
|---|---|
| Region wrapper | Outer landmark grouping the team as one section |
| Section heading | Names the block (e.g. "Meet the team") |
| List container | The grid itself, marked as a list of people |
| Person item | One list item: photo, name, role, optional bio/social |
| Photo | The headshot establishing the person is real |
| Name | The person's name, the item's primary label |
| Role | Their title or function |
| Social links (optional) | Links to profiles (LinkedIn, etc.) |

## Content slots

| Slot | Required? | Source layer | Notes |
|---|---|---|---|
| Section heading | Yes | content/strings | E.g. "Our team"; the block's heading |
| Person name | Yes | content/pages | Repeated per person |
| Person role | Yes | content/pages | Title or function |
| Person photo | No | media | Headshot; `alt` is the person's name |
| Person bio | No | content/pages | Short paragraph or expandable detail |
| Social link URLs + platform | No | sitemap.yaml | Per-person profile links |
| Person count / order | Yes | components.yaml | Drives the grid items and sequence |
| Color/type tokens | Yes | brand.yaml | Surface, on-surface, accent for links |

## Accessibility requirements

- **List semantics:** the grid of people is a list — render it as `<ul>` with one `<li>` per person (visual grid layout is CSS; the semantics stay a list). This lets screen readers announce "list, N items" so users know the size of the team and can navigate item by item. Do not build it from bare `<div>`s.
- **Photo alt text convention:** each headshot's `alt` is the person's name, e.g. `alt="Maria Chen"` — not "headshot", "photo of a woman", or the filename. If the name already appears as adjacent visible text and is programmatically associated, the photo may instead be decorative with `alt=""` to avoid the name being announced twice; pick one convention and apply it consistently across the grid.
- **Name and role structure:** the person's name should be a heading within the item (e.g. `h3`) or otherwise the item's accessible label, with the role as associated text. Consistent heading levels let users jump person-to-person with heading navigation.
- **Social-icon link accessible names:** icon-only social links (a LinkedIn glyph, an X mark) have no visible text, so each needs an accessible name that includes both the platform and the person — `aria-label="Maria Chen on LinkedIn"`, not just "LinkedIn" repeated N times across the grid (ambiguous out of context). Mark the decorative icon itself `aria-hidden="true"`.
- **Keyboard + focus:** all social links and any "read bio" controls are reachable in DOM order with `Tab`, activate with `Enter` (and `Space` if a control is a `<button>`, e.g. an expandable bio disclosure), and show a visible focus indicator per WCAG 2.2. An expandable bio uses `<button aria-expanded>` controlling the bio region.
- **Color contrast:** names, roles, and bio text meet WCAG 2.2 (4.5:1 normal text). Social-link icons that convey meaning meet 3:1 non-text contrast against their background.
- **Reduced motion:** hover flips, zoom-on-hover, or staggered entrance animations must be disabled under `prefers-reduced-motion: reduce`.

## Common variants

- **Uniform grid** — equal cards, photo above name and role.
- **Leadership-first** — featured larger cards for executives, smaller grid below.
- **Hover-reveal bio** — bio appears on hover/focus (must also work on keyboard focus).
- **Expandable bio** — a disclosure button toggles a longer bio per person.
- **Logo/illustration style** — illustrated avatars instead of photos for a stylized brand.
- **Departmental** — grouped sub-grids under sub-headings per team or function.

## Pitfalls

- Building the grid from `<div>`s so screen readers never announce it as a list or its size.
- Photo `alt` set to "headshot", "team member", or a filename instead of the person's name.
- Icon-only social links all named "LinkedIn" / "Twitter" with no person context — ambiguous.
- Hover-only bios or social reveals that never appear on keyboard focus.
- Decorative social glyphs not hidden from AT, producing doubled or noisy announcements.
