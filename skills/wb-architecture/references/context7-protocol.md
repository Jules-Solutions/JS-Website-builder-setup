# Reference — context7 / WebFetch protocol (phases 11-12)

> The exact external-doc invocation pattern for stack + CMS decisions, the caching convention, the freshness rule, and the verified-current findings from the 2026-05-18 authoring pass. Authoritative source is `phase-contracts/11-stack-decision.md` + `phase-contracts/12-cms-decision.md` + `DESIGN-context7-integration.md`. context7 is the load-bearing external surface for this phase group — it is mandatory, not optional.

## Why context7 is mandatory here

Stacks and CMSes evolve quarterly. Training-data snapshots drift 12-18 months. The agent's recommendations must reflect what's actually current, not what was true at model-training time. The single clearest example: **Next.js 15 changed the default `fetch()` cache mode to no-store** (breaking vs Next.js 14's `force-cache`) — an agent reasoning from stale training data would give wrong data-fetching guidance. Always fetch fresh at phase-11/12 session start; re-fetch cached docs older than 30 days.

## Invocation pattern

### Phase 11 — stack docs

For every stack the user is seriously considering:

1. **Next.js (mandatory if Next.js is on the table):**
   `mcp__context7__query-docs` libraryId `/vercel/next.js` — query App Router fundamentals, Server Components, rendering modes (SSG/ISR/SSR), the fetch caching default change, MDX, next-intl i18n.
2. **Payload (Next.js + Payload pairing preview — full coverage at phase 12):**
   `mcp__context7__query-docs` libraryId `/payloadcms/payload`.
3. **Framer:** `mcp__context7__resolve-library-id` libraryName "Framer". If not present at sufficient quality, `WebFetch` `https://www.framer.com/developers/` and `https://www.framer.com/updates/server-api` for current Server API + Custom Components SDK + Framer CMS.
4. **WordPress:** `WebFetch` `https://developer.wordpress.org/` for current `theme.json` schema, REST API surface, Gutenberg/FSE.

Cache each to `.website-builder/library/docs/${stack}.md`.

### Phase 12 — CMS docs

For the CMS on the table:

1. **Payload (mandatory when on the table):** `mcp__context7__query-docs` `/payloadcms/payload` — query Collections, Blocks field, field-level localization, access control / roles, drafts/versions, live preview, Next.js installation, Postgres adapter, the `pnpm payload migrate && next build` deploy build command.
2. **Decap:** `WebFetch` `https://decapcms.org/docs/` (context7 coverage thin) — config-schema, OAuth backend options, `structure: multiple_files` i18n. Also note active forks: Sveltia CMS (`https://github.com/sveltia/sveltia-cms`), Static CMS (`https://github.com/StaticJsCMS/static-cms`).
3. **Framer CMS / WordPress core:** `WebFetch` framer.com / developer.wordpress.org/rest-api as needed for the stack-built-in pairing.

Cache each to `.website-builder/library/docs/${cms}.md`.

`WebSearch` is used sparingly — only for very-recent patterns context7 doesn't cover yet (e.g., "Next.js 15 [feature] 2026", "Payload v3 deploy Vercel build command 2026").

## Caching + freshness convention

- Cache fetched docs to `.website-builder/library/docs/${name}.md` (name = stack or CMS slug).
- These caches are re-read at later phases: stack docs at 17 / 18 / 22 / 28-30; CMS docs at 18 / 22 / 29.
- Re-fetch if the cached file is **more than 30 days old** at the time the relevant phase becomes active.
- The agent re-validates current state via context7 at session start when phase 11 or 12 is the active phase.

## Verified-current findings (authoring pass — 2026-05-18)

These are the freshness-dated facts gathered while authoring this skill. They seed the agent's first pass; the agent still re-validates at runtime per the freshness rule.

### Next.js (context7 `/vercel/next.js`, fetched 2026-05-18; v16.x current, v15.x supported, benchmark 89.84, High reputation, 2178 snippets)

- **Default fetch cache is no-store in App Router** (Next.js 15+): `autoNoCache` true → `finalRevalidate = 0`, cacheReason `auto no cache`. Breaking change from Next.js 14's `force-cache`.
- **Server Actions** set `workStore.fetchCache = 'default-no-store'` explicitly.
- Restore caching: per-request `fetch(url, { cache: 'force-cache' })`; or page/layout `export const fetchCache = 'default-cache'`. Time-based: `fetch(url, { next: { revalidate: N } })`.
- i18n: canonical App Router pattern is dynamic-import `getDictionary` — `dictionaries[locale]?.() ?? dictionaries.en()` with `import('./dictionaries/${locale}.json')`, `import "server-only"`.

### Payload (context7 `/payloadcms/payload`, fetched 2026-05-18; v3.84.0 latest, benchmark 82.1, High reputation, 2279 snippets)

- Install into existing Next.js: `pnpm i payload @payloadcms/next @payloadcms/richtext-lexical sharp` + a DB adapter (`@payloadcms/db-postgres` for the muggle-friendly Postgres default).
- Integration: wrap config with `withPayload(nextConfig)` — `import { withPayload } from '@payloadcms/next/withPayload'`; ESM required for `next.config.js`.
- Drafts + RBAC pattern: `versions: { drafts: true }`, `access.read` returns `{ _status: { equals: 'published' } }` for unauthenticated, `true` for authenticated.
- Production build: `pnpm build` creates the `.next` admin bundle; deploy build command convention is `pnpm payload migrate && next build` (the migration step is mandatory — forgetting produces schema drift, enforced at phase 29).

### Framer (WebSearch 2026-05-18; framer.com/developers, framer.com/updates/server-api)

- **Server API** published February 2026, free during open beta. Programmatic access from any server without opening Framer; shares Plugin API capabilities — sync CMS collections from external sources (Notion/Airtable), publish changes, update the canvas, change project settings; triggerable by AI agents, webhooks, scheduled jobs.
- Plugins can read/edit/manage code Components and Overrides. Custom React code components run inside the editor and on published sites (dynamic content, API integrations, custom animations).
- "Workshop" is Framer's AI component generator.
- Re-verify via `WebFetch` framer.com/developers + framer.com/updates/server-api at phase-11 session start (Server API is beta — surface may shift).

### WordPress (WebSearch 2026-05-18; developer.wordpress.org)

- FSE is the 2026 standard — not experimental, not optional for serious theme development. Default themes Twenty Twenty-Three through Twenty Twenty-Five are all block themes.
- **theme.json v3** is the schema for WordPress 6.6+: normalizes longhand/shorthand CSS resolution, block style variations as first-class config objects, shadow presets, fluid-typography global min/max.
- 2026 development model: theme.json v3 + Block Hooks + Interactivity API + Block Bindings + pattern-first. Block patterns auto-register from PHP files in `patterns/` via header comments.
- theme.json generates CSS custom properties (`--wp--preset--color--primary`) that custom CSS references — custom CSS automatically respects Global Styles user changes.
- Twenty Twenty-Five is a strong block-theme scaffold base. Re-verify via `WebFetch` developer.wordpress.org at phase-11 session start.

## Sources (authoring pass)

- context7 `/vercel/next.js` — App Router migration, patch-fetch.ts, action-handler.ts, i18n-routing example (fetched 2026-05-18).
- context7 `/payloadcms/payload` — installation.mdx, COLLECTIONS.md, db-postgres README, live-preview example (fetched 2026-05-18).
- WebSearch "WordPress block themes Full Site Editing theme.json 2026" — developer.wordpress.org, fullsiteediting.com, kinsta.com, brndle.com (2026-05-18).
- WebSearch "Framer sites API Custom Components SDK 2026" — framer.com/developers, framer.com/updates/server-api, framer.com/developers/server-api-introduction (2026-05-18).
