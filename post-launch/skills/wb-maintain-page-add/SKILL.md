---
name: wb-maintain-page-add
description: This skill should be used by the website-maintainer when the user wants to add a WHOLE NEW PAGE to a live site within the existing site architecture — "add a services page", "I need a pricing page", "add a contact page", "create an FAQ page", "add a team page", "we need a new landing page for X". Runs an abbreviated single-page pipeline (content → wireframe → sections → copy → composition → SEO) within the existing brand + design system + stack. NOT for adding a section to an existing page (wb-maintain-section-add) or a new content entry in a collection (wb-maintain-content-add).
version: 0.1.0
---

# wb-maintain-page-add — add a whole new page

> Add a new page to the existing site — a `/services`, `/pricing`, `/contact` page. An abbreviated single-page run of the build pipeline, reusing the locked brand + design system + stack. No re-run of discovery or brand. Typically 2-4 hours.

## When invoked

The user wants a new page (not a new content entry, not a new section on an existing page). The page is new; the site, brand, design system, and stack are not.

## Behavior

Run an **abbreviated single-page pipeline** — the relevant build phases, scoped to one page, within the existing constraints:

1. **Content per page (phase 13 subset).** What does this page accomplish? What conversion does it drive? What's its section list? Surface + confirm with the user; don't accept "an about page = our story" — push for the conversion contribution.
2. **Wireframe (phase 14 subset).** Section order, hierarchy, responsive intent for the new page. Offer 2-3 layout options if the user has no strong view.
3. **Sections (phase 15 subset).** Per-section content brief — components, data, placeholders.
4. **Copy (phase 16 subset).** Finalized prose in the phase-5 brand voice. No placeholder/lorem on a live page.
5. **Composition (phase 19 subset).** Assemble the page from existing components (referencing phase-17 tokens). New components needed → same decision-35 path as `wb-maintain-section-add` (write code or emit a handoff brief).
6. **SEO (phase 26 subset).** Page-specific title, meta description, Open Graph, structured data where relevant. Never reuse another page's meta.
7. **Nav update.** Update `sitemap.yaml.navigation` so the page is reachable. A page nobody can navigate to is not done.
8. **Verify + deploy.** Responsive check (Playwright 360/768/1280), a11y sniff (alt text, headings, contrast, focus), SEO present, all links resolve. Deploy on user confirmation. For multi-language sites, create the page in each language per `config.yaml.translation_preference`.

## Time-box

**2-4 hours** for a typical page. If the page needs several new components or implies a new content type/collection, it's at the upper end — and if it implies a structural change to the site's information architecture, escalate.

## Anti-patterns

- Skipping the conversion question ("what's this page for?").
- Placeholder copy on a live page (phase 16 discipline still applies).
- Forgetting the nav update.
- Reusing another page's SEO meta.
- Treating a page that actually requires a new content type or IA change as a simple page-add — escalate.
