---
type: REFERENCE
corpus: component-patterns
title: Footer
component_slug: footer
also_known_as: [site footer, page footer, contentinfo, fat footer]
consumed_by_phases: [9, 17, 18]
---

# Footer

> The site-wide closing block at the bottom of every page: secondary navigation columns, legal links, contact, and social — the page's reference shelf.

## Purpose

The footer is where visitors land when they've scrolled past the main content looking for "the other stuff": contact details, legal pages, secondary navigation, and proof-of-life signals like social accounts and copyright. It does double duty as a sitemap for SEO and exploration, and as the canonical home for compliance links (privacy, terms, accessibility statement) that must appear on every page. A good footer answers "is this real, how do I reach them, and where's everything else" without competing with the primary content.

## When to use / when not

- **Use when:** the site has more than one page and needs a consistent place for legal links, contact info, and secondary navigation — i.e. almost every public site.
- **Avoid when:** a deliberately chromeless single-task flow (full-screen checkout step, kiosk mode, immersive demo) where any footer would distract; even then keep a minimal legal line if required by law.

## Anatomy

- **`contentinfo` landmark** — the outer `<footer>` container scoped to the whole page.
- **Brand block** — logo, short descriptor or tagline, sometimes a newsletter signup.
- **Link columns** — grouped secondary navigation (Product, Company, Resources, Legal), each with a column heading.
- **Contact block** — address, email, phone, or a contact-page link.
- **Social row** — icon links to external profiles.
- **Legal / utility bar** — copyright line, privacy/terms/accessibility links, locale or theme switcher.

## Content slots

| Slot | Required? | Source layer | Notes |
|---|---|---|---|
| Brand mark + tagline | No | media + content/strings | Small logo + one-line descriptor |
| Link-column headings | Yes | sitemap.yaml | Group labels for secondary nav |
| Link-column items + targets | Yes | sitemap.yaml | Secondary routes drawn from the sitemap |
| Contact details | No | content/strings | Email, phone, address microcopy |
| Social profile links | No | content/strings + media | External URLs + icon assets |
| Legal links + targets | Yes | sitemap.yaml | Privacy, Terms, Accessibility, Cookies |
| Copyright line | Yes | content/strings | Year + entity; year can be templated |
| Newsletter form labels | No | content/strings | Field label + submit microcopy if present |
| Color, divider, type tokens | Yes | brand.yaml | Footer surface, on-surface, muted text, border |

## Accessibility requirements

- **Landmark:** the page footer is a single `<footer>` element placed as a direct child of `<body>` (or otherwise not nested inside `<article>`/`<section>`/`<main>`), which exposes it as the `contentinfo` landmark. There must be only one `contentinfo` per page; a `<footer>` nested inside an article is a sectioning footer, not the page footer.
- **Nested navigation:** wrap the link columns in a `<nav>` with a distinct `aria-label` (e.g. `aria-label="Footer"`) so it doesn't collide with the primary `nav`. Render columns as `<ul>`/`<li>` lists; the column title should be a real heading (`<h2>`/`<h3>` in the page outline) associated with its list, not a styled `<div>`.
- **Links:** all destinations are `<a href>`. External/social links use a discernible accessible name — icon-only links require `aria-label` (e.g. "Jules.Solutions on LinkedIn"), and a visually-hidden text label is preferable to title-only.
- **Heading levels:** column headings continue the page's heading hierarchy (do not jump from `h1` straight to `h4`); they sit below the main content's deepest top-level sections.
- **Keyboard:** every link and the newsletter form are reachable in DOM order with `Tab`, activate with `Enter` (and `Space` for any buttons). Focus order matches the visual column order.
- **Focus visibility:** links and form controls show a visible focus indicator meeting WCAG 2.2 Focus Appearance.
- **Forms:** a newsletter input has an associated `<label>` (or `aria-label`); the submit is a real `<button type="submit">`; validation/success messages are announced (e.g. an `aria-live="polite"` status region).
- **Color contrast:** footer text is frequently muted on a dark surface — verify body links meet 4.5:1 and that the muted copyright/legal text is not dropped below 4.5:1 for the sake of subtlety.
- **Reduced motion:** any hover reveal, accordion collapse (mobile footers often collapse columns into accordions), or scroll-triggered animation respects `prefers-reduced-motion: reduce`; collapsed accordion columns still use `aria-expanded` on their toggle buttons.

## Common variants

- **Fat footer** — multiple link columns plus brand and contact; the default for content-rich sites.
- **Minimal footer** — single row: copyright + a few legal links.
- **Newsletter-led** — prominent signup block above the link columns.
- **Accordion footer** — columns collapse into expandable sections on mobile (disclosure pattern).
- **Mega footer with sitemap** — near-complete site index for large sites and SEO.
- **CTA footer** — a final conversion prompt sits atop the standard footer content.

## Pitfalls

- Multiple `<footer>` elements at page scope, producing more than one `contentinfo` landmark and confusing landmark navigation.
- Icon-only social links with no accessible name — screen readers announce "link" with no destination.
- Muted legal/copyright text styled below 4.5:1 contrast in the name of visual quietness.
- Mobile accordion columns toggled by non-button elements lacking `aria-expanded`, so state is invisible to assistive tech.
- Treating the footer as a dumping ground — burying the required legal links among dozens of low-value links so they're hard to find.
