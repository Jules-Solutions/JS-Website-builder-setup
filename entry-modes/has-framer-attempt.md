# Entry mode: has-framer-attempt

> The user started building in Framer, Webflow, Wix, or WordPress — got some distance, and now wants a better-structured result. They have partial work: some design decisions made, some content written, some pages built. The agent extracts the partial work and continues from a known state, without discarding what was already intentional.

## Who this is for

- Someone who built a Framer prototype, got stuck on mobile responsiveness, and wants to rebuild properly
- Someone who hired a Webflow freelancer, got a partial result, and wants to continue in a more developer-owned stack
- Someone who has a WordPress site under active development that they want to migrate to a cleaner stack

The partial platform is treated as a design-and-content source, not as a continuation target (unless the user picks Framer / Webflow / WordPress as their stack at phase 11, in which case the partial work IS continued on that platform).

## Onboarding flow

At session start:

1. The agent sets `project.yaml.entry_mode = "has-framer-attempt"`.
2. The user provides: the published preview URL (if the partial site is live or shared), any exported JSON/ZIP from the tool, and a status description ("I have the homepage done, the about page is empty, the blog section doesn't exist yet").
3. The agent confirms which artifacts are available.

Phase 6.5 fires immediately to ingest what exists before phase 1.

## Phase 6.5 ingestion strategy

### For Framer / Webflow (URL available): Google Stitch + Playwright

If the partial site has a published preview URL:

1. **Stitch** runs against the URL and extracts design tokens (colors, type scale, spacing) into `brand.yaml.tokens` (draft).
2. **Playwright** walks the available pages, captures section structure and text content into `sitemap.yaml` and `content/pages/*.md` (draft).

This captures what's already designed — even partial pages yield useful token data.

### For Framer (JSON export available): divmagic

Framer can export project JSON. The user exports and pastes. The divmagic API (or the agent's own JSON reader) extracts component shape data, token overrides, and text strings with element-level precision.

### For WordPress (admin access): Playwright walker

The agent uses Playwright to walk the live WordPress site, capturing posts, pages, and navigation. The agent does NOT access the WordPress admin panel (it reads the public output, not the backend).

### What always gets extracted (regardless of platform)

- Visible text content per page → `content/pages/*.md` (draft)
- Navigation structure → `sitemap.yaml.navigation` (draft)
- Observable color / type values → `brand.yaml.tokens` (draft)
- Section layout patterns → seeds `components.yaml` (draft)

### What does NOT get extracted

- Database content (WordPress posts, Framer CMS collections) — the agent reads the rendered output, not the CMS
- Private / draft pages — only published / accessible content is captured
- Stack-specific logic (Framer interactions, Webflow IX2 animations) — behavior is noted in the relevant component spec for re-implementation at phase 18

### Conflict detection

The partial work establishes a partial design baseline. At phase 17 (design system) and phase 2 (vision), the extracted tokens become the starting point — the user decides whether to refine the existing direction or pivot. Pivot decisions are logged in `decisions/ingest-{ts}.md`.

### Output files seeded

| Extracted artifact | Destination |
|---|---|
| Design tokens | `brand.yaml.tokens` (draft) |
| Page inventory | `sitemap.yaml.pages` (draft) |
| Navigation | `sitemap.yaml.navigation` (draft) |
| Text per page | `content/pages/*.md` (draft) |
| Component shapes | `components.yaml` (draft) |

## Resume point after ingestion

The pipeline starts at phase 1. The key difference from greenfield: phases 2 and 5 (vision and brand voice) have a starting point — the partial site's aesthetic and copy inform the conversation. The agent surfaces the extracted tokens and copy at each phase rather than starting cold. Phases the user already completed (e.g., "I know what stack I want") can move faster; the agent still confirms the decisions are deliberate.

If the user keeps the same platform (Framer / Webflow / WordPress as the phase-11 stack choice), the partial work is continued directly rather than rebuilt. The agent picks up at the appropriate phase based on the status description from onboarding.
