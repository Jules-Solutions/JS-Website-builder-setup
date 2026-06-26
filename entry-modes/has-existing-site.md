# Entry mode: has-existing-site

> The user has a live deployed website they want to redesign, migrate, or extend. The existing site is a goldmine of constraints: it already has content, some audience, some design language — and probably some debt. The agent's job is to extract what's worth keeping and replace what isn't.

## Who this is for

- Small businesses with an aging WordPress / Wix / Squarespace site
- Freelancers or agencies taking over a client's existing presence
- Anyone whose prior site was built without intentional design and now needs proper structure

The existing site is on ANY platform. The agent doesn't need access to the CMS or source code — it reads the deployed URL.

## Onboarding flow

At session start, the agent sets `project.yaml.entry_mode = "has-existing-site"` and collects the following before phase 1:

1. **The URL.** The live site (or staging URL if the live site is down). One URL is sufficient; the agent can discover sub-pages.
2. **The brief.** What is wrong with the current site? What must change? What must NOT change? (Existing content that maps into the new site saves phase 16 work.)
3. **Redirect policy.** Is the user keeping the same domain? If yes, URL structure changes require redirect planning (flagged at phase 29).

Phase 6.5 fires immediately after this intake, before phase 1.

## Phase 6.5 ingestion strategy

### Primary extractor: Google Stitch

The agent asks the user to run [Stitch](https://stitch.withgoogle.com) against the existing site's URL and paste the resulting DESIGN.md. Stitch extracts:

- Color palette → seeds `brand.yaml.tokens.colors` (pending user review at phase 17)
- Type scale → seeds `brand.yaml.tokens.typography`
- Spacing system → seeds `brand.yaml.tokens.spacing`
- Component shapes → seeds initial entries in `components.yaml`

The user reviews the extraction at phase 17 (design system) and confirms or overrides each token. No token is automatically accepted — it is seeded for discussion, not committed.

### Secondary: Playwright walker

After Stitch, the agent walks the live site with Playwright:

- Enumerates pages by following navigation links → seeds `sitemap.yaml.pages`
- Captures page structure (headline / body / CTA per page) → seeds `content/pages/*.md` briefs
- Screenshots each page for the user to review side-by-side

The Playwright walk is bounded: the agent stops after 20 pages or 3 nav levels, whichever comes first.

### Conflict detection

The existing site's design tokens and structure are treated as **candidates**, not facts. At each phase that touches extracted data, the user confirms:

- Keep extracted token / use new token / merge
- Keep existing page / drop it / split it
- Keep existing copy / rewrite in the new brand voice

Conflict decisions are logged in `decisions/ingest-{ts}.md`.

### Output files seeded

| Extracted artifact | Destination |
|---|---|
| Color / type / spacing tokens | `brand.yaml.tokens` (draft) |
| Page inventory | `sitemap.yaml.pages` (draft) |
| Page-level content | `content/pages/{slug}.md` (draft) |
| Component shapes | `components.yaml` (draft) |
| Microcopy strings | `content/strings/{lang}.json` (draft) |

All files are marked `status: extracted-pending-review` until confirmed at the relevant phase.

## Resume point after ingestion

After phase 6.5, the pipeline continues at phase 1 (Idea capture) but with pre-populated context. Phases 2-5 (vision, entity, requirements, brand voice) run in full — extraction tells you what IS, the conversation tells you what SHOULD BE. By phase 6 (wild content capture), the user has a URL-catalog anchor for reference site selection, which is faster than greenfield.
