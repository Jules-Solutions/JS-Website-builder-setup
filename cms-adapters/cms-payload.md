# CMS adapter — Payload CMS

> Runtime artifact the website-builder agent loads when `project.yaml.cms` is `payload`. The `wb-architecture` skill consumes this at phase 12 (CMS decision); `wb-component-build` at phase 18 (component build); the phase-22 i18n + forms integration; the phase-24a/b/c commerce branching; the phase-6.5 re-runnable ingestion at any project lifecycle point. Authored against the canonical 12-section schema in `cms-adapters/README.md`.
>
> Primary design-doc source: `DESIGN-cms-payload.md`. Pairing source: `adapters/stack-nextjs.md` (Captain G's Phase 3 work — the canonical pairing). i18n source: `DESIGN-i18n.md`. Sibling reference site: the `website-starter` workstream (vault-side — SynSol + AWin Payload build; already shipped 17 blocks + token system + theme-generated CSS pattern).

## Mental model

### Identity

- **CMS:** Payload CMS — code-first, fullstack TypeScript framework + headless CMS that drops onto Next.js as a single application
- **Version baseline:** Payload v3.84.x (verified context7 `/payloadcms/payload` 2026-05-20 — 2322 snippets, High reputation, benchmark 82.17; latest stable per https://github.com/payloadcms/payload/releases is v3.84.1 released 2026-04-23). Payload v2 (Express-based, standalone) is legacy; **all new projects use v3** (Next.js-native). Per-version pinning available via `/payloadcms/payload/v3.84.0` if a project pins to a specific version.
- **Canonical context7 ID:** `/payloadcms/payload` (primary; see §"context7 lookups for this CMS" for the full per-phase manifest). Also `/llmstxt/payloadcms_llms-full_txt` (6552 snippets, full-text mirror — useful when context7's primary returns too narrowly).
- **Freshness-check requirement:** the agent invokes context7 at phase 11 (when Next.js stack picked + Payload becomes likely) / 12 (CMS decision lock) / 17 (BrandTokens global authoring) / 18 (Pages + Blocks authoring) / 22 (i18n + forms) / 24a (commerce — Stripe Pay plugin or Stripe SDK) / 28 (deploy + Postgres + migration discipline) to confirm the current surface — **Payload v3 moves fast; training data and even cached docs are stale within 4-6 weeks of any minor release**. Cached docs in `.website-builder/library/docs/payload-*.md` re-fetch on the 30-day threshold per `skills/wb-architecture/references/context7-protocol.md`. The v3.x release cadence (v3.79 → v3.84 in ~5 weeks observed late 2026-Q1/Q2) is the canonical example of why this isn't optional.

Payload thinks in three primitives:

1. **Collections** — sets of documents. Every Collection is a TypeScript `CollectionConfig` defining `slug`, `fields`, `access`, `hooks`, `versions`, `admin` UI. **One config object** becomes: a database table (or Mongo collection), an admin UI section, a REST endpoint at `/api/<slug>`, a GraphQL type, a Local API query target (`payload.find({collection})`), and a generated TypeScript type — all from the same file. The website-starter sibling has 12 such collections (Pages, Posts, Media, Categories, Users, Testimonials, etc.).
2. **Globals** — singletons. Same shape as a Collection but exactly one record exists. Used for site-wide settings (`SiteSettings`, `Header`, `Footer`, `BrandTokens`). The website-starter has 6 such globals — `BrandTokens` is the load-bearing one for the website-builder's Layer 1 (design tokens) mapping.
3. **Fields** — the leaf primitives that compose collections and globals. Field types: `text`, `textarea`, `richText` (Lexical-powered), `number`, `email`, `select`, `checkbox`, `date`, `relationship`, `upload`, `array`, `group`, `tabs`, and — load-bearing for marketing sites — `blocks`.

**The mental shift from Strapi / Directus / Sanity / Contentful:** *the schema IS code*. There's no admin UI for "add a collection." You write `CollectionConfig` in TypeScript, restart the dev server, the migration runs, the admin updates, and the types regenerate. Git is the source of truth for schema; PRs are how schema changes are reviewed; rollbacks are a `git revert` + `pnpm payload migrate:down` away.

**The Blocks field is the load-bearing primitive for marketing-website use cases.** A Blocks field on a `Pages` collection takes an array of block types — `Hero`, `RichText`, `MediaGallery`, `CallToAction`, `LogoCloud`, `Testimonial`, etc. — and the editor picks any block, in any order, any number of times. Each block has its own typed fields. The output is a discriminated-union JSON array the frontend renders by `blockType`. This is how the website-builder's structural-spec layer (Layer 2 — `components.yaml`) becomes a real CMS surface. The website-starter shipped 13-15 such blocks (Hero 4-variant, FeaturesGrid 3-variant, ProcessSteps, Testimonials 3-variant, etc.) — Payload's Blocks field is the proven substrate this adapter standardizes on.

The mental model contract that holds the whole thing together: **what's in the TypeScript config is what exists in the admin, the database, and the API**. No drift. No "where do I configure this." One source. This is the strongest claim Payload makes — and it's why the website-starter sibling chose Payload, and why this adapter recommends it for content-heavy + relational + editorially-managed sites.

## When to pick this CMS

### Pick Payload when

- **The chosen stack is Next.js** (decided phase 11). Payload v3 IS a Next.js application — it installs into your Next.js app's `app/` directory and shares the same dev server. If the user picked Next.js at phase 11, Payload is the strongest CMS option.
- **The user (or someone close to them) is willing to read TypeScript.** They don't have to write much (only field-config touchups), but the schema is code; if "I'll never touch a `.ts` file" is a hard constraint, Decap or `none` fits better.
- **Content is more than a flat list of pages.** Multiple collections (`Pages`, `Posts`, `Authors`, `CaseStudies`, `Products`), relationships between them, role-based access (admin / editor / author) — Payload eats this. Strapi / Directus also handle it; Payload's advantage is TypeScript-end-to-end with code-first schema.
- **The site is or will be transactional.** Payload's Postgres backend (via Drizzle), hooks for side effects (`afterChange` for ISR revalidation, Stripe webhooks, transactional emails), access control (per-collection + per-field + per-operation), and ability to power custom admin views make it a real backend, not just a CMS. The Stripe Pay plugin (`@payloadcms/plugin-stripe`) wires checkout natively when `transactional=true`.
- **The user wants composable page layouts.** The Blocks field is the cleanest implementation of the "marketing page = stack of blocks the editor reorders" pattern across all CMS options. Decap and Tina approximate it via lists of unions; Payload makes it native, typed, and with admin UI auto-generated.
- **Localization needs to be first-class, not bolted on.** Payload's field-level `localized: true` flag plus a `locales` array on the global config gives clean per-locale storage with a single admin UI surface. Per-locale storage is a JSON column (or per-locale row depending on adapter) — the editor sees one page with a locale switcher in the admin, not N parallel records.
- **The user has Jules-Solutions context and the website-starter is a substrate fit.** The Jules-Solutions website-starter (SynSol, AWin) is Payload-based; aligning here means future drop-in blocks, shared learnings, shared ops surface, brand-tokens.json → BrandTokens-global → theme-generated.css patterns already proven in production.

### Don't pick Payload when

- **Stack is anything other than Next.js (v3) or Express (v2 / legacy / standalone).** Payload v3 is Next.js-native. Astro / SvelteKit users CAN consume Payload but in headless mode (two-deploy — see §"Stack pairings"). Hugo / Framer / WordPress users get other CMSes.
- **Hosting is shared / cPanel / no Node runtime.** Payload needs a Node host (Vercel, Render, Railway, Fly, self-hosted Docker on JS-1, Payload Cloud). Plus a Postgres / Mongo / SQLite database. Static-only hosts can't run admin.
- **The team is allergic to TypeScript.** Strapi / Directus give a UI-first experience without ever touching code. Decap gives a YAML-config + admin-UI experience that doesn't touch TS.
- **Content really is just markdown for a static site.** `cms-none` or Decap is lighter — Payload's admin UI loading is a ~Megabyte+ JS bundle; overkill for 5 pages of prose.
- **The user has no editor at all.** If "I am the only person who will ever edit content, and I am comfortable in a code editor," `cms-none` is lighter and faster.

## Auth + setup

**Account / instance setup — three-way decision (Phase 12 surfaces this prompt):** Payload needs a Node runtime + a database. The website-builder agent prompts the user at phase 12 through the three-way choice; see `### Database + hosting choice (Phase 12 decision)` below.

**Project creation (phase 12, once CMS = Payload + stack = Next.js):**

```bash
# Option A — greenfield with Payload + Next.js + a template
pnpm dlx create-payload-app@latest my-site --template website
cd my-site
pnpm dev   # http://localhost:3000 (frontend) + /admin (Payload admin)

# Option B — add to an existing Next.js app already created at phase 11
pnpm i payload @payloadcms/next @payloadcms/db-postgres @payloadcms/richtext-lexical
# Wrap next.config.mjs with withPayload
# Author payload.config.ts + first Collection
# pnpm dev
```

The agent prefers Option B when the user already has a Next.js project at phase 11 (which is the default flow). Option A is for greenfield-Payload-first projects.

**Required env vars (in `.env.local`, never committed):**

| Env var | Purpose | Where it comes from |
|---|---|---|
| `PAYLOAD_SECRET` | Cryptographic secret for sessions / JWTs | Generate with `openssl rand -hex 32`; store in 1Password per `secrets-conventions.md` |
| `DATABASE_URI` | Postgres connection string | Per the three-way DB decision below |
| `NEXT_PUBLIC_SITE_URL` | Site URL (for live preview, `hreflang`, ISR revalidation callbacks) | `http://localhost:3000` for dev; production URL for prod |
| `REVALIDATE_SECRET` | Shared secret for the `afterChange` hook → `/api/revalidate` route | Generate; store in 1Password |
| `PAYLOAD_DISABLE_ADMIN` | Set to `true` if you want to disable admin on a deploy (e.g., scaling decision) | Optional |

**MCP / tooling integrations** (these are stack-level concerns shared with `adapters/stack-nextjs.md`; cross-referencing here for the Payload-specific subset):

- **Payload CMS MCP** (Antler Digital) — recommended when `cms=payload`; auto-generates MCP tools from Payload collections. See §"context7 lookups for this CMS" → MCP audit below for install + fallback. This is the **Payload-specific** MCP integration; the rest are shared with the Next.js stack adapter.
- **Vercel MCP** — official (https://mcp.vercel.com); used at phase 28/29 for deploy + DNS-record + env-var management. Shared with `adapters/stack-nextjs.md`.
- **Cloudflare MCP** — hosted OAuth at https://mcp.cloudflare.com/mcp; used at phase 28 for DNS-record CRUD. Shared with stack-nextjs.
- **Neon MCP** / **Supabase MCP** — official; recommended when Postgres host is Neon / Supabase. See §"context7 lookups" MCP audit.
- **Stripe MCP** — official (https://docs.stripe.com/mcp + https://claude.com/plugins/stripe Anthropic plugin); recommended when `transactional=true`. Shared with stack-nextjs.
- **GitHub MCP** — official (https://github.com/github/github-mcp-server); for PR + repo workflows. Shared with stack-nextjs.
- **context7** — pre-loaded in plugin foundation; queries `/payloadcms/payload` per the manifest in §"context7 lookups".
- **Playwright MCP** — pre-loaded; for visual + admin verification at phase 20/27/29.

### Database + hosting choice (Phase 12 decision)

**Mandatory three-way prompt the agent surfaces explicitly at phase 12** — no silent default. Payload requires a Node runtime AND a database; the choice has cost / DX / data-residency consequences the user should make consciously.

| Option | What it is | Pricing (verified 2026-05-20) | DX | Data residency | When to recommend |
|---|---|---|---|---|---|
| **Payload Cloud (managed)** | Payload's first-party managed hosting. One subscription bundles: Postgres + media storage (S3-compatible) + admin auth + the Node runtime for Payload. | Standard ~$35/mo (3 GB DB + 30 GB file storage + 40 GB bandwidth); Pro ~$199/mo (more resources); Enterprise custom. Overages: $0.50/GB DB, $0.02/GB file storage, $0.20/GB bandwidth. No per-project / per-user fees — one self-hosted-equivalent install. Sources: costbench.com/software/headless-cms/payload-cms, buildwithmatija.com/payload-cms-pricing. | Simplest. Zero ops. Migrations + media + auth handled. | US-region by default; check Payload Cloud docs for EU options. | User wants zero ops; willing to pay a subscription; small-to-medium muggle marketing site or transactional site. **Recommended muggle-default when the user values managed-everything over self-host control.** |
| **Self-host on Vercel + Neon (canonical default)** | Frontend + Payload on Vercel; Postgres on Neon (https://neon.com — what used to be Vercel Postgres). Vercel deprecated its in-house Postgres in December 2024 and migrated all users to Neon — **so "Vercel Postgres" effectively IS Neon**, accessed either via Vercel's Marketplace (one-click setup, billing on Vercel) or via Neon directly (slightly more control). | Neon free tier: 0.5 GB storage + 100 CU-hours/mo + scale-to-zero after 5 min + 10 branches. Suitable for muggle marketing sites with low traffic. Launch tier: $0.106/CU-hour + $0.35/GB-month + $1.50/branch-month. Vercel Hobby: free; Vercel Pro: $20/user/mo. **Total for typical muggle site: $0/mo on Neon free + Vercel Hobby, escalating to ~$20-40/mo on Vercel Pro + Neon Launch as traffic grows.** Sources: neon.com/pricing, vercel.com/pricing, schematichq.com/blog/vercel-pricing, dev.to/aaronksaunders. | Very good. Vercel auto-deploys from `master`; Neon scales-to-zero on hobby tier; both have MCPs. Migration step (`pnpm payload migrate`) wires into Vercel build command per phase 28-29. | Neon EU regions available (Frankfurt, Stockholm, Singapore). Vercel auto-region-selects via the platform. | User is already on Vercel ecosystem; wants self-host control + lowest cost at small scale + escape-hatch to multi-cloud. **Recommended muggle-default per `DESIGN-cms-payload.md` line 564.** |
| **Self-host elsewhere (Render / Railway / Fly / DigitalOcean / own infra)** | Frontend + Payload deployed to user's chosen Node host; Postgres also user-managed (Render Postgres, Railway Postgres, Supabase, DigitalOcean Managed Postgres, or self-hosted). | Variable per host. Render: $7/mo for the web service + $7/mo for Postgres. Railway: $5/mo + usage. Supabase: free tier with 500 MB DB + auth + storage; Pro $25/mo. Self-hosted Docker on JS-1 or own VPS: free except your time. | Most control; most operational burden. Migrations + media + backups + monitoring all user-owned. | Full data-residency control — pick the region. | User has specific data-residency requirements, OR existing infra they want to consolidate onto, OR cost-conscious + comfortable with infra. |

**Recommendation logic the agent applies:**

- If user says "managed, no infra" → Payload Cloud
- If user says "Vercel + cheap" or "I'm already on Vercel" → Vercel + Neon (the canonical default)
- If user says "EU data only / Switzerland data only / GDPR-strict" → Vercel + Neon (Frankfurt region) OR self-host on a Swiss VPS (Hetzner / Infomaniak / Exoscale)
- If user has existing Render / Railway / Supabase → that

**Database adapter choice** (`@payloadcms/db-postgres` vs `@payloadcms/db-mongodb` vs `@payloadcms/db-sqlite`):

- **Postgres (default, recommended):** `@payloadcms/db-postgres` (uses Drizzle ORM under the hood). Proper relational, predictable backups, easy to debug, best ecosystem. **Default for muggle marketing sites per `DESIGN-cms-payload.md` line 564.**
- **Mongo:** `@payloadcms/db-mongodb`. For highly-variable schemas, document-oriented workflows, or teams already on Mongo. Less common in muggle marketing.
- **SQLite:** `@payloadcms/db-sqlite`. For embedded / single-node deployments. Rare in production muggle sites; useful for local dev when Postgres feels heavy.

**Vercel + Neon — what changed (verified 2026-05-20):** Per multiple sources (vercel.com/pricing, schematichq.com/blog/vercel-pricing): "Vercel deprecated its managed Postgres and KV offerings in December 2024, migrating users to Neon (Postgres) and Upstash (Redis) respectively." So when the user picks "Vercel Postgres" via Vercel's Marketplace, they are getting **Neon-powered Postgres**, billed through Vercel. The agent surfaces this so the user understands what they're actually getting + that switching from Vercel-Marketplace-Neon to direct-Neon is a connection-string swap (no migration needed).

**Migration cost between options** (the agent flags this for future flexibility):

- Postgres-to-Postgres (e.g., Neon → Render Postgres → Supabase) is straightforward — `pg_dump | pg_restore` + connection-string swap.
- Switching to/from Mongo is **not** straightforward — schema reshape required. Pick the DB at phase 12; switching later is a project, not a flag.
- Switching from Payload Cloud to self-host (or vice versa) is mostly seamless because Payload Cloud uses standard Postgres + S3-compatible media + Payload's own auth — export DB dump + media bucket + change `DATABASE_URI` + `PAYLOAD_SECRET`.

### CRUD vocabulary

Payload is **schema-as-code + admin-UI + Local API + REST + GraphQL — all generated from one config**. The CRUD verbs translate as follows:

| Universal verb | Payload native concept |
|---|---|
| **Create a collection** | Author `collections/{Name}.ts` (`CollectionConfig` object) → import in `payload.config.ts` → restart dev server → migration runs → admin shows new collection |
| **Create a page (one document)** | Three equivalent paths: (1) admin UI → New Page → fill fields → Save (most common for editors); (2) `payload.create({ collection: 'pages', data: { ... } })` via Local API (for seeds, programmatic flows); (3) REST: `POST /api/pages` with JSON body + auth header (for external integrations) |
| **Edit a page** | Admin UI → click page → edit → Save (autosaves to draft if `versions.drafts: true`). Or `payload.update({ collection, id, data })` via Local API. |
| **Publish a page** | If `versions.drafts: true`: admin → click "Publish" → flips `_status` from `draft` to `published`. Otherwise: any save publishes immediately. |
| **Unpublish a page** | Set `_status: 'draft'` (with versions enabled) OR delete the page entirely OR set a custom `archived: true` field (project-specific). |
| **Schedule publish** | With `versions.drafts.schedulePublish: true`: admin → click "Schedule" → set timestamp. Payload internally cron-checks. |
| **View revisions** | With `versions.drafts: true` + `versions.maxPerDoc: N`: admin → page → "Versions" tab → diff + restore. |
| **Add a field to an existing collection** | Edit `collections/{Name}.ts` → restart dev → `pnpm payload migrate:create` (generates SQL diff) → `pnpm payload migrate` (applies). Production deploy must include the migration step (phase 29 bakes this into the Vercel build command). |
| **Add a new locale** | Edit `payload.config.ts` → add to `localization.locales` → restart dev → migration runs (existing rows get null for new locale; `fallback: true` covers reads). |

The agent uses **Local API** (`payload.create()` / `payload.find()` / `payload.update()`) for seed scripts at phase 18 (per `DESIGN-cms-payload.md` seed pattern lines 403-441) and the **admin UI** for editor handoff (everything post-phase-18 is the user clicking around in admin).

## Authoring patterns

### Pattern: Pages collection with Blocks field for composable layouts

The standard marketing-website pattern. **One `Pages` collection.** Each Page has a `slug`, `title`, `meta`, and a `layout: blocks[]`. The blocks array is where editors compose pages by stacking and reordering blocks.

```ts
// collections/Pages.ts
import type { CollectionConfig } from 'payload'
import { Hero } from '../blocks/Hero'
import { RichText } from '../blocks/RichText'
import { MediaGallery } from '../blocks/MediaGallery'
import { CallToAction } from '../blocks/CallToAction'

export const Pages: CollectionConfig = {
  slug: 'pages',
  admin: {
    useAsTitle: 'title',
    defaultColumns: ['title', 'slug', 'updatedAt'],
    livePreview: {
      url: ({ data, locale }) =>
        `${process.env.NEXT_PUBLIC_SITE_URL}/${locale.code}/${data.slug}?draft=true`,
      breakpoints: [
        { label: 'Mobile', name: 'mobile', width: 375, height: 667 },
        { label: 'Tablet', name: 'tablet', width: 768, height: 1024 },
        { label: 'Desktop', name: 'desktop', width: 1440, height: 900 },
      ],
    },
  },
  versions: {
    drafts: {
      autosave: { interval: 2000 }, // ms
      schedulePublish: true,
      validate: true,
    },
    maxPerDoc: 50,
  },
  access: {
    read: ({ req: { user } }) => {
      if (user) return true
      return { _status: { equals: 'published' } } // public read for published only
    },
    create: ({ req: { user } }) =>
      user?.roles?.some((r) => ['admin', 'editor'].includes(r)) || false,
    update: ({ req: { user } }) =>
      user?.roles?.some((r) => ['admin', 'editor'].includes(r)) || false,
    delete: ({ req: { user } }) => user?.roles?.includes('admin') || false,
  },
  fields: [
    { name: 'title', type: 'text', required: true, localized: true },
    {
      name: 'slug',
      type: 'text',
      required: true,
      unique: true,
      index: true,
      admin: { position: 'sidebar' },
    },
    {
      name: 'meta',
      type: 'group',
      fields: [
        { name: 'title', type: 'text', localized: true },
        { name: 'description', type: 'textarea', localized: true },
        { name: 'image', type: 'upload', relationTo: 'media' },
      ],
    },
    {
      name: 'layout',
      type: 'blocks',
      // localized: NOT here per Approach 2 (Decision 39 Pattern A default) — see § i18n integration
      blocks: [Hero, RichText, MediaGallery, CallToAction],
      minRows: 1,
    },
  ],
  hooks: {
    beforeChange: [
      ({ data, req }) => {
        if (!data.slug && data.title) {
          data.slug = data.title.toLowerCase().replace(/[^a-z0-9]+/g, '-')
        }
        return data
      },
    ],
    afterChange: [
      async ({ doc, operation, req }) => {
        if (operation === 'update' || operation === 'create') {
          await fetch(`${process.env.NEXT_PUBLIC_SITE_URL}/api/revalidate`, {
            method: 'POST',
            body: JSON.stringify({
              path: `/${doc.slug}`,
              secret: process.env.REVALIDATE_SECRET,
            }),
          })
        }
      },
    ],
  },
}
```

Each block lives in its own file:

```ts
// blocks/Hero.ts
import type { Block } from 'payload'

export const Hero: Block = {
  slug: 'hero',
  labels: { singular: 'Hero', plural: 'Hero blocks' },
  fields: [
    { name: 'headline', type: 'text', required: true, localized: true },
    { name: 'sub', type: 'textarea', localized: true },
    {
      name: 'cta',
      type: 'group',
      fields: [
        { name: 'label', type: 'text', localized: true },
        { name: 'href', type: 'text' },
        {
          name: 'variant',
          type: 'select',
          options: ['primary', 'secondary', 'ghost'],
          defaultValue: 'primary',
        },
      ],
    },
    { name: 'background', type: 'upload', relationTo: 'media' },
    {
      name: 'variant',
      type: 'select',
      options: ['text-left', 'text-center', 'image-right'],
      defaultValue: 'text-center',
    },
  ],
}
```

The frontend renders by switching on `blockType`:

```tsx
// components/RenderBlocks.tsx
import { Hero } from './blocks/Hero'
import { RichText } from './blocks/RichText'
import { MediaGallery } from './blocks/MediaGallery'
import { CallToAction } from './blocks/CallToAction'

const blockComponents = {
  hero: Hero,
  richText: RichText,
  mediaGallery: MediaGallery,
  callToAction: CallToAction,
} as const

export function RenderBlocks({ blocks }: { blocks: PageLayout[] }) {
  return blocks.map((block, i) => {
    const Component = blockComponents[block.blockType]
    return Component ? <Component key={i} {...block} /> : null
  })
}
```

**This pattern maps directly onto the website-builder's `components.yaml` (Layer 2):** each block in `components.yaml` becomes one Payload `Block` config; the `props` map onto Payload `fields`; the `variants` map onto a `select` field. The website-starter sibling shipped 13-15 such blocks (Hero 4-variant, FeaturesGrid 3-variant, ProcessSteps, Testimonials 3-variant, TeamGrid, LogoGrid, Contact, FormWizard, BlogArchive) — the pattern is production-proven.

### Pattern: Globals for site-wide settings + brand tokens

```ts
// globals/SiteSettings.ts
import type { GlobalConfig } from 'payload'

export const SiteSettings: GlobalConfig = {
  slug: 'site-settings',
  access: {
    read: () => true,
    update: ({ req: { user } }) => user?.roles?.includes('admin') || false,
  },
  fields: [
    { name: 'siteName', type: 'text', required: true, localized: true },
    { name: 'tagline', type: 'text', localized: true },
    { name: 'logo', type: 'upload', relationTo: 'media' },
    { name: 'favicon', type: 'upload', relationTo: 'media' },
    {
      name: 'social',
      type: 'array',
      fields: [
        { name: 'platform', type: 'select', options: ['twitter', 'linkedin', 'instagram', 'github'] },
        { name: 'url', type: 'text' },
      ],
    },
  ],
}

// globals/BrandTokens.ts — bridges website-builder Layer 1 into Payload
export const BrandTokens: GlobalConfig = {
  slug: 'brand-tokens',
  access: {
    read: () => true,
    update: ({ req: { user } }) => user?.roles?.includes('admin') || false,
  },
  fields: [
    {
      name: 'colors',
      type: 'group',
      fields: [
        { name: 'primary', type: 'text', defaultValue: 'oklch(64% 0.18 30)' },
        { name: 'secondary', type: 'text' },
        { name: 'neutral_50', type: 'text' },
        { name: 'neutral_900', type: 'text' },
      ],
    },
    {
      name: 'typography',
      type: 'group',
      fields: [
        { name: 'displayFamily', type: 'text' },
        { name: 'bodyFamily', type: 'text' },
        { name: 'monoFamily', type: 'text' },
      ],
    },
  ],
}
```

The frontend reads `BrandTokens` once at build time (Server Component) and emits CSS custom properties in `app/globals.css`. When the user updates a token in the admin, the `afterChange` hook on `BrandTokens` triggers a full rebuild (ISR with `revalidatePath('/')` or `revalidateTag('brand-tokens')`).

**The website-starter sibling's pattern:** `brand-config.json` (per-client) → BrandTokens global → `theme.generated.css` (regenerated on every BrandTokens save via the `afterChange` hook). The website-builder agent ports this pattern verbatim at phase 17.

### Pattern: Relationships across collections

```ts
// collections/Posts.ts
fields: [
  {
    name: 'author',
    type: 'relationship',
    relationTo: 'authors',
    required: true,
  },
  {
    name: 'relatedPosts',
    type: 'relationship',
    relationTo: 'posts',
    hasMany: true,
    filterOptions: ({ id }) => ({ id: { not_equals: id } }), // exclude self
  },
  {
    name: 'categories',
    type: 'relationship',
    relationTo: 'categories',
    hasMany: true,
  },
]
```

Relationships generate proper foreign keys (Postgres) or DBRefs (Mongo), get filterable admin UI, and resolve via the `depth` query param at read time:

```ts
const post = await payload.find({
  collection: 'posts',
  where: { slug: { equals: 'my-post' } },
  depth: 2, // populates relationships up to 2 levels deep
  locale: 'en',
})
```

### Pattern: Versioned drafts with live preview

```ts
// inside a Collection config
versions: {
  drafts: {
    autosave: { interval: 2000 },
    schedulePublish: true,
    validate: true,
  },
  maxPerDoc: 50, // GC old versions automatically
},
admin: {
  livePreview: {
    url: ({ data, locale }) =>
      `${process.env.NEXT_PUBLIC_SITE_URL}/${locale.code}/${data.slug}?draft=true`,
    breakpoints: [
      { label: 'Mobile', name: 'mobile', width: 375, height: 667 },
      { label: 'Tablet', name: 'tablet', width: 768, height: 1024 },
      { label: 'Desktop', name: 'desktop', width: 1440, height: 900 },
    ],
  },
},
```

Live preview requires the frontend to handle a `?draft=true` query param: when present, the page route fetches with `draft: true, depth: 2` via the Local API; Payload returns the draft version. This is the single biggest UX advantage Payload has over Decap / `cms-none` / static-CMS approaches for non-technical editors. They edit in admin and see the actual frontend rendering side-by-side, in any locale, at any breakpoint.

### Pattern: Hooks for side effects

```ts
// inside a Collection config
hooks: {
  beforeChange: [
    ({ data, req }) => {
      if (!data.slug && data.title) {
        data.slug = data.title.toLowerCase().replace(/[^a-z0-9]+/g, '-')
      }
      return data
    },
  ],
  afterChange: [
    async ({ doc, req, operation }) => {
      if (operation === 'update' || operation === 'create') {
        await fetch(`${process.env.NEXT_PUBLIC_SITE_URL}/api/revalidate`, {
          method: 'POST',
          body: JSON.stringify({
            path: `/${doc.slug}`,
            secret: process.env.REVALIDATE_SECRET,
          }),
        })
      }
    },
  ],
  afterDelete: [
    async ({ doc, req }) => {
      await fetch(`${process.env.NEXT_PUBLIC_SITE_URL}/api/revalidate`, {
        method: 'POST',
        body: JSON.stringify({
          path: `/${doc.slug}`,
          secret: process.env.REVALIDATE_SECRET,
        }),
      })
    },
  ],
}
```

Common hook uses: ISR revalidation (above), Stripe webhook → Customer collection update, transactional email send (booking confirmation), slug auto-generation, soft-delete enforcement, search-index sync (Algolia, Meilisearch).

### Pattern: Lexical rich text with embedded Blocks (BlocksFeature)

```ts
// inside a Collection or Block field
{
  name: 'content',
  type: 'richText',
  editor: lexicalEditor({
    features: ({ defaultFeatures }) => [
      ...defaultFeatures,
      BlocksFeature({
        blocks: [Banner, CallToAction], // Payload Block configs reusable inside the editor
      }),
    ],
  }),
}
```

This is the powerful Lexical-specific feature: full Payload Blocks (with all field types, hooks, validation, access control) can be embedded directly inside rich text content. An editor writing a long article can mid-paragraph insert a `CallToAction` block, configure its fields, and continue prose around it. The block's data is stored inside the Lexical JSON structure but behaves identically to a Block in a Blocks field.

### Common pitfalls

- **Forgetting `localized: true` on the right level.** Localizing a `blocks` field localizes the entire layout (each locale gets its own block array — Approach 1). Localizing fields *inside* each block keeps shared layout + per-locale text (Approach 2 — default per Decision 39 Pattern A). See § i18n integration. The decision matters for editor workflow and migration cost; surface to user at phase 12.
- **Schema drift between code and DB.** Payload migrations are explicit (`pnpm payload migrate:create`, `pnpm payload migrate`). Don't let agents auto-run migrations in production without a review step. Vercel build command must include `pnpm payload migrate && pnpm build` per phase 29 (see § Common pitfalls under Limitations + escape hatches for the full deploy discipline).
- **Slug field collisions.** A slug field is `unique: true, index: true`; Payload validates uniqueness but doesn't auto-resolve. The `beforeChange` hook above generates from title — add a "if collision, append `-2`" branch for non-unique titles.
- **Block reuse across multiple Pages-like collections.** Define each block in its own file, import into wherever it's used. Don't inline blocks; you lose composability.
- **Nesting Blocks inside Blocks.** Possible but the admin UX gets hairy past 2 levels. Prefer flat layouts with cross-references via relationships.
- **Treating Lexical as "just rich text" or HTML.** Lexical stores **structured JSON**, not HTML. The frontend converts via `@payloadcms/richtext-lexical/react`'s `<RichText />` component. Don't `dangerouslySetInnerHTML` the value — it's not HTML.
- **Missing `useAsTitle` on collections.** Without it the admin list shows internal IDs. Always set `admin: { useAsTitle: 'title' }` (or whatever field is human-readable).
- **Unbounded `versions.maxPerDoc`.** Drafts pile up. Set `maxPerDoc: 50` (or so) to GC old versions automatically.
- **Slow admin on large collections without indexes.** When a collection grows past ~10k docs, set `index: true` on filterable fields (`slug`, `_status`, `author`, `categories`). Payload doesn't auto-index everything.
- **Missing access control on `read`.** Default access is **"anyone"** for read. Add `read` access control on every collection that should not leak data — even drafts of marketing pages. Pattern: `read: ({ req: { user } }) => user ? true : { _status: { equals: 'published' } }`.

## Stack pairings

Per-CMS verdicts from this CMS's perspective. **Strong recommendation: Payload pairs with Next.js as a Native single-deploy.** Other pairings are technically possible — the agent can wire them — but the value-per-effort drops sharply.

| Stack (phase 11 choice) | Payload fit | Notes |
|---|---|---|
| **Framer** | N/A | Framer has its own CMS. Pairing makes no sense. |
| **Next.js + shadcn** | **Native** | Payload v3 IS a Next.js app. Single deploy. `app/(payload)/...` mounts the admin; `app/(frontend)/...` is the user's website. Best DX. **Default for "Next.js + a serious CMS."** See `### Per-pairing recipe — Next.js + Payload (the canonical path)` below. |
| **WordPress** | N/A | WordPress has WP core. Pairing makes no sense. |
| **Astro** | **Possible** | Headless mode — two-deploy. Payload runs as a separate Next.js app exposing REST/GraphQL; Astro consumes via `/api/...`. Works but you maintain two deploys. **See `### Per-pairing recipe — Headless mode (Astro / SvelteKit consuming Payload)` below for the canonical S3 setup.** Decap or TinaCMS usually fits Astro better unless the user needs Payload's relational power. |
| **Hugo** | **Anti-fit** | Hugo is build-time + file-based; pairing with Payload defeats Hugo's chosen simplicity. Use `cms-none` or Decap with Hugo. |
| **SvelteKit** | **Possible** | Same as Astro — Payload as separate API; SvelteKit fetches. Doable; less ergonomic than Sanity for this stack. Two deploys. **See headless mode recipe below.** |
| **Webflow** | N/A | Webflow has its own CMS. |
| **Plain static HTML** | N/A | Use `cms-none` or Decap. Payload's admin needs a Node runtime. |

**Verdict-word semantics** (per `cms-adapters/README.md` cross-CMS × stack anchor): Native / Possible / Awkward / Anti-fit / N/A. Verdicts here match the anchor table verbatim.

Phase 12 surfaces this matrix; if the user picked a non-Next.js stack at phase 11 and is still leaning Payload, the agent walks through the trade-off explicitly. Astro + Payload is a real option for users who want Astro's content-collection ergonomics for static pages PLUS Payload's relational power for blog / catalog / member data — but the user pays in operational complexity (two deploys, two CI/CD pipelines, two URLs).

### Per-pairing recipe — Next.js + Payload (the canonical path)

```bash
# Option A — greenfield with the website template (recommended for marketing sites)
pnpm dlx create-payload-app@latest my-site --template website

# Option B — add to an existing Next.js app already scaffolded at phase 11
cd my-site  # the Next.js project
pnpm i payload @payloadcms/next @payloadcms/db-postgres @payloadcms/richtext-lexical
```

**Wrap `next.config.mjs` with `withPayload`:**

```js
// next.config.mjs
import { withPayload } from '@payloadcms/next/withPayload'

/** @type {import('next').NextConfig} */
const nextConfig = {
  // existing Next.js config
}

export default withPayload(nextConfig, {
  devBundleServerPackages: false, // faster dev compilation (default in create-payload-app since v3.28.0)
})
```

**Key file layout:**

```
app/
├── (payload)/                    # Payload admin routes (do not edit directly)
│   ├── admin/
│   ├── api/
│   └── layout.tsx
├── (frontend)/                   # The user's website — separate route group
│   ├── [locale]/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── [...slug]/
│   │       └── page.tsx          # catch-all: fetches Pages by slug via Local API
│   └── api/
│       └── revalidate/route.ts   # ISR revalidation endpoint hit by Payload's afterChange hook
collections/                       # Payload collection configs (the schema)
├── Pages.ts
├── Posts.ts
├── Media.ts
└── Users.ts
blocks/                            # Block configs (composed into Pages.layout)
├── Hero.ts
├── RichText.ts
├── MediaGallery.ts
└── CallToAction.ts
globals/
├── SiteSettings.ts
├── BrandTokens.ts                 # bridges Layer 1 (brand.yaml.tokens)
└── Header.ts
payload.config.ts                  # Payload master config (imports collections + globals)
.env.local                         # PAYLOAD_SECRET, DATABASE_URI, NEXT_PUBLIC_SITE_URL, REVALIDATE_SECRET
```

The `(payload)` route group keeps admin separate from the user's site. The `(frontend)` group is where the website-builder writes its Next.js code. Both share the same Next.js dev server, the same build, the same deploy.

**Reading content in a frontend route:**

```tsx
// app/(frontend)/[locale]/[...slug]/page.tsx
import { getPayload } from 'payload'
import config from '@/payload.config'
import { RenderBlocks } from '@/components/RenderBlocks'

export default async function Page({
  params,
  searchParams,
}: {
  params: Promise<{ locale: string; slug?: string[] }>
  searchParams: Promise<{ draft?: string }>
}) {
  const { locale, slug = [] } = await params
  const { draft } = await searchParams
  const payload = await getPayload({ config })

  const { docs } = await payload.find({
    collection: 'pages',
    where: { slug: { equals: slug.join('/') || 'home' } },
    locale,
    depth: 2,
    draft: draft === 'true',
    limit: 1,
  })

  const page = docs[0]
  if (!page) notFound()

  return <RenderBlocks blocks={page.layout} />
}
```

### Per-pairing recipe — Headless mode (Astro / SvelteKit consuming Payload)

**S3 — the canonical "two-deploy headless" path. This is the option that makes Payload viable for non-Next.js stacks; without it, agents would route Astro/SvelteKit users away from Payload entirely.**

**Architecture:**

```
┌─────────────────────────────┐       REST or GraphQL       ┌─────────────────────────────┐
│  Astro / SvelteKit site     │  ───────────────────────►   │  Payload (separate Next.js  │
│  (Vercel / Netlify / etc.)  │     /api/pages?...          │  app) + /admin              │
│  Deployment 1               │  ◄───────────────────────   │  Deployment 2               │
│                             │     JSON                    │  (Vercel / Render / Fly)    │
└─────────────────────────────┘                              └─────────────────────────────┘
                                                                       │
                                                                       ▼
                                                              ┌─────────────────┐
                                                              │  Neon / Supabase│
                                                              │  / Payload Cloud│
                                                              │  Postgres        │
                                                              └─────────────────┘
```

**Setup:**

1. **Bootstrap Payload as a standalone Next.js app** (it's still Next.js, just deployed independently from the user's frontend):

   ```bash
   pnpm dlx create-payload-app@latest my-cms --template website
   cd my-cms
   # configure payload.config.ts + collections + .env (DATABASE_URI etc.)
   # deploy to Vercel / Render / Fly as deployment #2
   ```

2. **Configure CORS on Payload to accept requests from the Astro/SvelteKit origin:**

   ```ts
   // payload.config.ts
   export default buildConfig({
     // ...
     cors: [
       'http://localhost:4321',                  // Astro dev
       'https://my-astro-site.vercel.app',       // prod
       process.env.FRONTEND_URL || '',
     ].filter(Boolean),
     csrf: [
       'http://localhost:4321',
       'https://my-astro-site.vercel.app',
     ].filter(Boolean),
   })
   ```

3. **Create a Payload API key user** (Collection-based — use the built-in `Users` collection with `auth: { useAPIKey: true }`) and store the key in the Astro project's `.env`:

   ```env
   # .env (Astro project)
   PAYLOAD_URL=https://my-payload-cms.vercel.app
   PAYLOAD_API_KEY=<API key from Payload admin Users → New User → Enable API Key>
   ```

4. **Consume from Astro pages:**

   ```ts
   // src/pages/[lang]/[...slug].astro
   ---
   const { lang, slug } = Astro.params
   const url = `${import.meta.env.PAYLOAD_URL}/api/pages?where[slug][equals]=${slug?.join('/') || 'home'}&depth=2&locale=${lang}`
   const res = await fetch(url, {
     headers: { Authorization: `Bearer ${import.meta.env.PAYLOAD_API_KEY}` },
   })
   const { docs } = await res.json()
   const page = docs[0]
   if (!page) return Astro.redirect('/404')
   ---
   <Layout title={page.meta?.title || page.title}>
     {page.layout.map(block => (
       <BlockRenderer block={block} />
     ))}
   </Layout>
   ```

5. **Trigger Astro rebuilds on Payload changes** — Payload's `afterChange` hook calls the Astro deploy webhook (Vercel: deploy hook URL; Netlify: build hook):

   ```ts
   // collections/Pages.ts (on the Payload side)
   hooks: {
     afterChange: [
       async ({ doc, operation }) => {
         if (operation === 'update' || operation === 'create') {
           await fetch(process.env.ASTRO_DEPLOY_HOOK_URL!, { method: 'POST' })
         }
       },
     ],
   }
   ```

**The trade-off (the agent surfaces at phase 12):**

- **Cost:** two deployments (Vercel × 2 or Vercel + Render etc.). Both have hosting costs. Two CI/CD pipelines to maintain.
- **Operational complexity:** two URLs to monitor, two deploy histories, two sets of env vars, two backup strategies, CORS to maintain.
- **Latency:** every page render hits the Payload API over the network — for SSR sites this is per-request; for SSG sites this is at build time only.
- **What you gain:** Payload's full feature set (relations, drafts, versions, live preview, RBAC, Lexical, BlocksFeature) WITHOUT giving up Astro's content-collection ergonomics or SvelteKit's component model. Worth it when Payload's relational features are load-bearing and the frontend stack is fixed at Astro/SvelteKit.

**Recommendation:** for muggle marketing sites on Astro/SvelteKit, **Decap or TinaCMS is usually a better fit** — they're git-backed (no separate deploy) and ergonomically aligned with the stack. Payload headless mode is the right choice when (a) the project genuinely needs Payload's relational + transactional power, AND (b) the user is comfortable with two-deploy operational reality.

## Content layer mapping

How the website-builder's 5 content layers (per `DESIGN-content-layers.md`) map onto Payload primitives. **Row labels MUST be identical to `adapters/README.md` §4 (stack) and `commerce-adapters/README.md` §4 (commerce) — same 5 labels, different columns.**

| Layer | CMS native concept |
|---|---|
| **L1 brand.yaml.tokens** | `BrandTokens` Global (one per site). Tokens stored as text fields grouped by concern (colors, typography, spacing, motion). Frontend reads the global at build time (or via Server Component fetch at request time) and emits CSS custom properties in `app/globals.css`. Editor edits in admin → `afterChange` hook on BrandTokens triggers `revalidateTag('brand-tokens')` for ISR refresh. The website-starter sibling's `brand-config.json` → BrandTokens-global → `theme.generated.css` pattern is the proven implementation. Phase 17 seeds the global on initial admin run; ongoing edits via admin. |
| **L2 sitemap.yaml + sections.yaml** | `Pages` collection with `layout: blocks[]` field. Each block in `components.yaml` becomes one `Block` config in `blocks/{Name}.ts`. `sitemap.yaml` becomes the set of Page documents seeded at phase 18 (one `payload.create({collection: 'pages', data: {...}})` per sitemap entry). `sections.yaml` becomes the discriminated-union shape of `layout` — each section maps to a Block invocation with its props as the Block's fields. |
| **L3 strings/{lang}.json** | **Two options. Default = Option A.** **Option A (recommended for muggles, default):** keep CDJSON as-is in `messages/{lang}.json`; reference from React components via `next-intl` (per `adapters/stack-nextjs.md` § i18n integration). Payload doesn't store strings. Editor doesn't touch strings in admin. **Option B (when editors want admin control of microcopy):** `Strings` global with `localized: true` group fields organized by namespace (`nav`, `cta`, `errors`, etc.). Editors get an admin UI for every string; site rebuilds on save via `afterChange` ISR hook. **Surface Option B to the user at phase 12 if they say "I want non-technical editors to change button labels."** Default at phase 12 is Option A. |
| **L4 content/pages/*.md** | `richText` field on the Page document OR a `RichText` Block in the Pages.layout, using Lexical editor. The phase 16 copywriting MD seeds the initial richText value via Local API (`payload.create({collection: 'pages', data: { layout: [{ blockType: 'richText', content: <Lexical-JSON-from-MD> }] }})`). Markdown → Lexical JSON conversion at seed time (Payload v3 has a `@payloadcms/richtext-lexical/markdown` helper). Editors then edit in admin using the Lexical WYSIWYG; never re-edit the MD directly post-seed (it's a snapshot of the pre-CMS state). |
| **L5 briefs/{component}.json** | Out of band — briefs live in `.website-builder/briefs/` regardless of CMS. Payload never sees them. Phase 6.5 ingests external-tool outputs (v0 / Cursor / ChatGPT pastes) back into appropriate Pages / Blocks via the Local API + Block-config updates. (Same row content for all 3 CMSes per `DESIGN-content-layers.md` — briefs are CMS-agnostic by design.) |

**The table is the BUILD-strategy.md Phase 4 DoD verification anchor** — comparing this row-by-row to `cms-adapters/cms-none.md` and `cms-adapters/cms-decap.md` (when those exist; authored in parallel by Captains I + J) proves that "same `.website-builder/` content produces equivalent sites across all 3 v1 CMSes (modulo platform-specific limitations)" per BUILD-strategy.md Phase 4 DoD line 201.

### Seed pattern — porting `.website-builder/` to Payload at phase 18

```ts
// scripts/seed.ts (run once after collection configs are in place)
import payload from 'payload'
import config from '../payload.config'
import fs from 'fs'
import yaml from 'yaml'
import path from 'path'

await payload.init({ config })

const sitemap = yaml.parse(fs.readFileSync('.website-builder/sitemap.yaml', 'utf8'))
const brand = yaml.parse(fs.readFileSync('.website-builder/brand.yaml', 'utf8'))

// Seed BrandTokens global
await payload.updateGlobal({
  slug: 'brand-tokens',
  data: {
    colors: brand.tokens.colors,
    typography: {
      displayFamily: brand.tokens.typography.display,
      bodyFamily: brand.tokens.typography.body,
    },
  },
})

// Seed Pages — one per sitemap entry, per locale
for (const page of sitemap.pages) {
  for (const locale of ['en', 'de', 'fr', 'it']) {
    const mdPath = path.join('.website-builder/content/pages', `${page.slug}.${locale}.md`)
    if (!fs.existsSync(mdPath)) continue
    const pageMd = fs.readFileSync(mdPath, 'utf8')
    // parse frontmatter + body, convert MD to Lexical via @payloadcms/richtext-lexical/markdown
    const layout = buildBlocksFromSections(page.sections, pageMd, locale)
    await payload.create({
      collection: 'pages',
      data: {
        title: page.title,
        slug: page.slug,
        layout,
        _status: 'draft',
      },
      locale,
    })
  }
}

process.exit(0)
```

The seed script is the bridge between phase 16-18 (when content is in `.website-builder/`) and phase 18+ (when content lives in Payload). After seeding, the user edits in admin; the `.website-builder/` files become a historical record of the pre-CMS state plus a regeneration source if the user starts over.

## i18n integration

Payload's localization is **field-level**. Configure once in `payload.config.ts`, then mark fields `localized: true`.

```ts
// payload.config.ts
import { buildConfig } from 'payload'

export default buildConfig({
  // collections, globals, etc.
  localization: {
    locales: [
      { label: 'English', code: 'en' },
      { label: 'Deutsch', code: 'de' },
      { label: 'Français', code: 'fr' },
      { label: 'Italiano', code: 'it' },
      // For RTL languages, set rtl: true:
      // { label: 'العربية', code: 'ar', rtl: true },
    ],
    defaultLocale: 'en',
    fallback: true, // when a locale value is missing, fall back to defaultLocale
  },
})
```

**Per Decision 39 (Pages-per-language Pattern A default — shared structure, translated prose):** all pages exist in all languages with shared structure and translated prose. Payload implements this by setting `localized: true` on `title`, on `meta.title`/`meta.description`, on each text field **inside** each Block (Approach 2). The page document is one row in the database; locale values are stored as JSON columns (Postgres) or per-locale subdocuments (Mongo). The editor sees one page in admin with a locale switcher; switching locales swaps just the localized fields, layout stays.

**Per Decision 40 (Translation Pattern 1 — agent translates inline at phase 16):** the agent at phase 16 generates copy in the source language, then translates per language by calling `payload.update({ collection, id, locale: 'de', data: { title: '...', layout: [...] } })` once per locale. The Pattern-2 translator-handoff upgrade path (Decision 40) is supported via per-locale brief export → external translator → paste back → phase-6.5 ingestion.

**Per Decision 41 (string-missing fallback):** Payload's `localization.fallback: true` covers this at read time. The frontend always renders something (default-language string when target-locale missing). The agent additionally logs a warning during validation when a localized field has no value for a configured locale (cross-language validation per `DESIGN-i18n.md` § "Validation").

### The Blocks localization decision (S3 / S4 not — this is the load-bearing Payload-specific nuance)

This is the one decision worth surfacing explicitly at phase 12 — it changes how editors work and what migration looks like later. **Two approaches; default is Approach 2.**

**Approach 1: localize the entire `layout` field (each locale gets its own block array)**

```ts
{
  name: 'layout',
  type: 'blocks',
  localized: true,        // ← entire layout is per-locale
  blocks: [Hero, RichText, MediaGallery, CallToAction],
}
```

- **Pro:** maximum flexibility per market. A German page can have one structure (Hero + 3 RichText + CTA); a French page can have a different structure (Hero + MediaGallery + RichText + CTA). Matches Decision 39 **Pattern B** (locale-specific content variation) from i18n design.
- **Con:** editors must manually keep parallel layouts in sync; adding a section in EN doesn't add it in DE — editor must duplicate the change per locale. Adding a new locale doubles the structural-edit workload.
- **When to pick:** content varies materially per market (pricing pages with different examples, regional landing pages with different CTAs).

**Approach 2: localize the text fields *inside* each block (layout shared, only text varies) — DEFAULT**

```ts
{
  name: 'layout',
  type: 'blocks',
  // NOT localized at this level — layout is shared across locales
  blocks: [
    {
      slug: 'hero',
      fields: [
        { name: 'headline', type: 'text', localized: true },  // ← localized text
        { name: 'sub', type: 'textarea', localized: true },
        { name: 'background', type: 'upload', relationTo: 'media' }, // shared image
      ],
    },
    // each block exposes only-text-localized
  ],
}
```

- **Pro:** matches Decision 39 **Pattern A** (shared structure, translated prose — default). Editors translate in place; adding a section in EN automatically adds it in DE (DE gets `null` initially; `fallback: true` covers reads until translated). Single source of structural truth.
- **Con:** cannot have structurally different layouts per market without duplicating page documents (e.g., `/about` for EN + `/about-de` for DE — defeats the localization model).
- **When to pick:** default for muggle marketing sites with translated-but-aligned content per market.

**Default = Approach 2** (matches Decision 39 Pattern A default per `DESIGN-cms-payload.md` line 515). Phase 12 dialogue surfaces the choice; if the user has known per-market structural variation needs (pricing pages, regional product variants), the agent recommends switching to Approach 1 for those specific collections — possibly mixing approaches across collections.

### Language switcher in Next.js + Payload

See `i18n/language-switcher.md#next-js--shadcn` for the per-stack implementation (shadcn `DropdownMenu` for ≥4 languages; inline buttons for 2-3 languages). Payload-specific: the locale list is fetched from Payload's `localization.locales` config (via Local API: `payload.config.localization.locales`) OR hardcoded to match Payload's config (the agent prefers the latter to avoid an API round-trip per render).

### hreflang

See `i18n/hreflang.md#next-js--shadcn` for the per-stack emission (Next.js `generateMetadata()` → `alternates.languages` map). Generated from the same locales list. Verified at phase 26 (SEO audit) — `hreflang` tags resolve to existing pages.

### RTL

Payload supports per-locale `rtl: true` (see config example above). For RTL locales the admin UI text-aligns input fields right-to-left. The frontend's `dir="rtl"` on `<html>` is set per locale by the Next.js layout (per `adapters/stack-nextjs.md` § i18n integration). Tailwind 4+ has built-in `rtl:` variants; CSS logical properties cover the rest. See `i18n/rtl.md` (stack-agnostic).

## Phase 6.5 ingestion

Phase 6.5 (re-runnable artifact ingestion) for Payload-stack projects:

1. **Has-AI-output mode** — user pastes one-shot React/HTML/MDX. Agent's AI-output parser extracts component shapes from the JSX, maps to existing Block configs, OR proposes a new Block. **For each new Block:** agent writes `blocks/NewBlock.ts` → adds to `Pages.layout.blocks` array in `collections/Pages.ts` → restarts dev server (or `pnpm payload migrate:create` + `pnpm payload migrate` if schema changes affect DB) → admin reflects new Block immediately. New page content ingests via `payload.create({collection: 'pages', data: { layout: [...] }, locale})` Local API.

2. **Has-existing-site mode** — Stitch / Playwright extracts tokens + structure from the live site. Tokens land in `BrandTokens` global via `payload.updateGlobal({slug: 'brand-tokens', data: {...}})`. Page structures land as `Pages` documents with `layout` arrays composed of recognized Block types. If existing site uses unrecognized block shapes, agent proposes new Block configs.

3. **Has-Figma-file mode** — Figma design-to-json output extracts tokens + frame structures. Tokens → BrandTokens global (same as above). Frame structures map to Block configs (each Figma component frame becomes a candidate Block — the agent proposes "matches existing Hero block" or "create new Block: Testimonial-3col").

4. **Mid-project ingestion (mom's pattern)** — user generates a new section in ChatGPT/v0/Cursor, pastes back. AI-output parser extracts shape. Agent proposes "add to existing Block X (with new fields appended)" OR "create new Block Y". User decides. Payload schema updates → migration runs → admin reflects new Block; frontend renders.

5. **JSON handoff round-trip** — agent emits brief at phase 18 (`briefs/{Component}-{ts}.json`), user iterates in v0/Cursor/ChatGPT, pastes back to `outputs/{Component}-{ts}.tsx`. Same flow as has-AI-output but with `iteration_history` tracked in the brief JSON per `handoff-spec/component-output-v1.md`.

**Conflict resolution for Payload (per Decision 36 — halt + force user decision):**

- **Schema conflict** (incoming Block has different fields than existing Block of same slug) → halt; user picks: rename incoming Block (new slug), merge fields (additive — adds new fields to existing Block; existing Block records get `null` for new fields), or replace existing (destructive — drops the old Block's fields).
- **Document conflict** (incoming `/about` page differs from existing) → halt; user picks: replace (the new content overwrites), append-as-new-version (uses Payload's draft system — incoming becomes a new draft of the existing page), or save as `/about-v2` (new page document with different slug).
- **Token conflict** (incoming `BrandTokens.colors.primary` differs) → halt; user picks per-token: keep existing, take incoming, or merge (e.g., average lightness in OKLCH).

All decisions logged in `.website-builder/decisions/ingest-{ts}.md` per `DESIGN-ingestion-and-extraction.md` § "Conflict resolution patterns".

**Migration discipline during ingestion:** if a new Block changes the database schema (new field types, new required fields, new relationships), the agent runs `pnpm payload migrate:create` to generate the SQL diff, reviews it (the agent reads the generated SQL and surfaces non-trivial changes to the user), then runs `pnpm payload migrate` to apply. Production deploys must include `pnpm payload migrate && pnpm build` in the Vercel build command per phase 29.

## Commerce integration (if transactional=true)

Payload is the **strongest CMS for transactional sites** in the MVP triplet. Native Stripe integration via the official `@payloadcms/plugin-stripe` plugin; structured product catalogs via Collections; order state managed in Collections with hooks for webhook side effects.

Phase 24a (commerce platform setup) + 24b (payment provider wiring) + 24c (commerce-specific legal) branching from this CMS's perspective.

**MCP integrations** (per §"Auth + setup" → MCP servers in the shared stack-nextjs adapter): **Stripe MCP** (`claude.com/plugins/stripe` — Anthropic plugin ships a `stripe-mcp` subagent CC auto-delegates to) recommended at phase 24a/b. **Cal.com MCP** (Claude custom connector — no install command) recommended at phase 24a when `transactional_kind in [bookings, both]`. Cross-ref `commerce-adapters/commerce-stripe.md` (Captain L's Phase 4 work — may not be authored at this Captain's writing time; forward reference per Phase 4 dispatch).

### Phase 24a — Commerce platform setup with Payload

**Pattern 1: Payload's official Stripe plugin (`@payloadcms/plugin-stripe`)** — the canonical path for transactional Payload sites.

```bash
pnpm i @payloadcms/plugin-stripe
```

```ts
// payload.config.ts
import { buildConfig } from 'payload'
import { stripePlugin } from '@payloadcms/plugin-stripe'

export default buildConfig({
  plugins: [
    stripePlugin({
      stripeSecretKey: process.env.STRIPE_SECRET_KEY!,
      stripeWebhooksEndpointSecret: process.env.STRIPE_WEBHOOKS_SECRET!,
      sync: [
        {
          collection: 'products',
          stripeResourceType: 'products',
          stripeResourceTypeSingular: 'product',
          fields: [
            { fieldPath: 'name', stripeProperty: 'name' },
            { fieldPath: 'description', stripeProperty: 'description' },
          ],
        },
        {
          collection: 'customers',
          stripeResourceType: 'customers',
          stripeResourceTypeSingular: 'customer',
          fields: [
            { fieldPath: 'email', stripeProperty: 'email' },
            { fieldPath: 'name', stripeProperty: 'name' },
          ],
        },
      ],
      webhooks: {
        'customer.subscription.created': async ({ event, payload, req }) => {
          // your handler
        },
        'checkout.session.completed': async ({ event, payload, req }) => {
          // your handler — create order, send confirmation email, etc.
        },
      },
    }),
  ],
  collections: [Products, Customers, Orders],
})
```

The plugin auto-syncs Payload Collections (`Products`, `Customers`) with Stripe resources (Products, Customers). Webhook events route through the plugin to your handlers.

**Pattern 2: Stripe SDK directly + Payload Collections (no plugin)** — for cases where the plugin's abstractions don't fit (custom Stripe Connect flows, multi-Stripe-account architectures).

```ts
// app/(frontend)/api/checkout/route.ts (Next.js Route Handler)
import { stripe } from '@/lib/stripe'
import { getPayload } from 'payload'
import config from '@/payload.config'

export async function POST(req: Request) {
  const { productId } = await req.json()
  const payload = await getPayload({ config })
  const product = await payload.findByID({ collection: 'products', id: productId })

  const session = await stripe.checkout.sessions.create({
    line_items: [{ price: product.stripePriceId, quantity: 1 }],
    mode: 'payment',
    success_url: `${process.env.NEXT_PUBLIC_SITE_URL}/checkout/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.NEXT_PUBLIC_SITE_URL}/checkout/cancel`,
    payment_method_types: ['card', 'twint'], // TWINT for Swiss audience
  })

  return Response.json({ url: session.url })
}
```

**TWINT for Swiss audience:** enable in Stripe Dashboard → Settings → Payment Methods → TWINT (toggle on). Stripe Checkout / Payment Element auto-renders TWINT alongside cards when the customer's locale is `de-CH` / `fr-CH` / `it-CH` and the currency is `chf`. Per `commerce-adapters/payment-config-schema.md`. No Payload-specific config beyond `payment_method_types: ['twint', ...]` on the Checkout Session.

### Phase 24b — Payment provider wiring (Payload-side webhook handlers)

```ts
// collections/Orders.ts
import type { CollectionConfig } from 'payload'

export const Orders: CollectionConfig = {
  slug: 'orders',
  fields: [
    { name: 'stripeSessionId', type: 'text', unique: true, required: true, index: true },
    { name: 'customer', type: 'relationship', relationTo: 'customers' },
    { name: 'lineItems', type: 'array', fields: [
      { name: 'product', type: 'relationship', relationTo: 'products' },
      { name: 'quantity', type: 'number' },
      { name: 'priceAtPurchase', type: 'number' }, // captured at purchase time
    ]},
    {
      name: 'status',
      type: 'select',
      options: ['pending', 'paid', 'fulfilled', 'refunded', 'cancelled'],
      defaultValue: 'pending',
      required: true,
    },
    { name: 'paymentMethod', type: 'select', options: ['card', 'twint', 'apple_pay', 'google_pay'] },
    { name: 'totalAmount', type: 'number' },
    { name: 'currency', type: 'select', options: ['chf', 'eur', 'usd'] },
  ],
  hooks: {
    afterChange: [
      async ({ doc, operation, req }) => {
        // send confirmation email on first paid status
        if (doc.status === 'paid' && operation === 'update') {
          await sendOrderConfirmation(doc) // implementation in lib/email.ts
        }
      },
    ],
  },
  access: {
    read: ({ req: { user } }) => {
      if (user?.roles?.includes('admin')) return true
      return { customer: { equals: user?.id } } // customers see only their own orders
    },
    create: () => true, // webhooks need to create
    update: ({ req: { user } }) => user?.roles?.includes('admin') || false,
    delete: ({ req: { user } }) => user?.roles?.includes('admin') || false,
  },
}
```

### Phase 24c — Commerce-specific legal

Refund policy / shipping terms / T&Cs / privacy / cookie notice as Pages collection entries with `slug: 'legal/refund-policy'` etc., using the Lexical richText field for the prose. Linked from checkout flow via Stripe Checkout's `custom_text` and `consent_collection.terms_of_service` configuration. Per-locale variants automatic via `localized: true` on the prose field.

### Booking flows (Cal.com)

Cal.com per Decision 54 MVP default booking provider. Payload's role: a `Bookings` collection captures booking-state via Cal.com webhooks; agent emits the embed `<CalcomEmbed eventTypeSlug="30min" />` in the frontend per `commerce-adapters/booking-calcom.md` (Captain L's Phase 4 territory — forward reference).

### Phase 22 transactional mid-flip

Decision 34 (transactional flag changes mid-project): if the user adds `transactional: true` mid-project, the agent's flow is: (1) install `@payloadcms/plugin-stripe`, (2) add `Products` / `Customers` / `Orders` collections, (3) run migrations, (4) wire frontend checkout routes, (5) update legal pages. The Payload schema additions are non-destructive (new tables / collections); no migration cost on existing content. Cross-ref `DESIGN-cms-payload.md` § "Limitations + escape hatches" for the structural-pivot path.

## Limitations + escape hatches

| Limitation | Escape hatch |
|---|---|
| **Requires Node runtime.** Static-only hosts (GitHub Pages, plain S3, Cloudflare Pages static) can't run Payload admin. | Use static export of frontend + Payload Cloud / Vercel for admin (the headless mode pattern). Or: switch to `cms-none` / Decap for true static. |
| **Requires a database.** No file-based mode. | Pick a managed Postgres (Neon / Supabase / Vercel-Marketplace-Neon / Render Postgres) — covered by §"Auth + setup" → Database + hosting choice. SQLite (`@payloadcms/db-sqlite`) for embedded / single-node. |
| **No native admin for non-developers to add Collections.** Schema is code. | Editors *use* the admin freely (creating Pages, Posts, etc.); they just can't add new Collections without a developer (or the website-builder agent) modifying TypeScript. **This is the design contract; surface clearly to user at phase 12.** |
| **Migrations need to run on every deploy.** Forget once → schema drift OR build failure on production. | Hardcode `pnpm payload migrate && pnpm build` in the Vercel build command (phase 29 enforces this). Verify in CI: the build fails fast if migration step exits non-zero — Vercel rolls back automatically. Note: running migrations on every cold start in serverless is slow; long-running servers (Render / Fly) are gentler on the migration step. |
| **Serverless cold-start cost.** Vercel's serverless functions pay a cold-start penalty when the Payload admin (a full Next.js app) loads from cold. | Use Vercel's standby instances (Pro tier) OR deploy Payload separately to Render / Fly on a persistent container. |
| **Live preview requires the frontend to handle a `?draft=true` param.** | Phase 18 generates the page route with a `searchParams.draft` check that fetches with `draft: true` from Payload Local API. Boilerplate but small; ~10 lines per page route. |
| **Image/media handling assumes a storage backend.** | Default is local filesystem (fine for dev; ephemeral on Vercel). Production: Payload's S3 / Vercel Blob / Cloudflare R2 / Cloudinary plugins (`@payloadcms/storage-s3`, `@payloadcms/storage-vercel-blob`, etc.). Phase 28-29 wires this; Payload Cloud handles it automatically. |
| **Admin URL leakage.** `/admin` is publicly accessible by default (login-gated, but visible). | Phase 24 (integrations) wires basic auth at CDN level (Cloudflare Workers / Vercel Edge Middleware) OR a separate subdomain (`admin.example.com` vs `example.com`) OR relies on Payload's built-in auth (admin requires login regardless — sufficient for most cases). For sensitive deployments, IP-allowlist via Cloudflare WAF. |
| **Admin UI can feel heavy for tiny sites.** Loading the admin = loading a full Next.js admin app (~1-2 MB JS). | If the site really is 5 pages of static prose, surface `cms-none` / Decap as a lighter alternative at phase 12. Don't over-tool. |
| **Custom admin components require React knowledge.** | Default admin UI covers ~95% of cases (auto-generated from CollectionConfig). Custom components only when needed (custom field type, dashboard widget). Surface as out-of-scope for muggle-driven projects; route through Captain G's React patterns if user insists. |
| **Lexical is NOT HTML — it's structured JSON.** Treating it as HTML and `dangerouslySetInnerHTML`-ing the value WILL break. | Use `@payloadcms/richtext-lexical/react`'s `<RichText />` component on the frontend; never raw-render the Lexical JSON. |
| **Vercel Postgres confusion (deprecated December 2024).** "Vercel Postgres" used to mean Vercel's own database; it's now Neon under the hood. | The agent surfaces this at phase 12 so the user understands they're getting Neon either way (via Vercel Marketplace OR direct Neon connection). Switching between the two = connection-string swap. |
| **TypeScript literacy required somewhere.** Schema, hooks, access control = all `.ts` files. | Out-of-scope for projects where no one can read `.ts` — route to Decap or `cms-none`. The website-builder agent CAN write all the TypeScript; the user just needs to understand they own a TypeScript codebase. |

**Structural pivot escape (per Decision 34 — transactional mid-flip pattern applied to CMS choice):** if the user discovers a hard limitation late (e.g., needs offline-capable admin, can't run Node, needs a CMS without a database), the agent surfaces it and routes to phase 11 transactional-flag-equivalent pattern: treat as **structural pivot**, restart phase 12 (CMS choice), pick a different CMS. **Migration cost from Payload to another CMS:** documents export via Local API → JSON dump per Collection; new CMS imports via its native ingestion path. Schema reshape required because CMS primitives differ (Payload's discriminated-union Blocks → Decap's list-with-types ≠ direct mapping). The agent flags the migration cost at phase 12 so the user picks consciously.

## context7 lookups for this CMS

The agent invokes context7 at these phases when Payload is the chosen CMS. Cache to `.website-builder/library/docs/payload-*.md` per the 30-day Lock-3 freshness norm.

| Phase | Library ID | Question template | Cache file |
|---|---|---|---|
| **11** (when Next.js stack picked + Payload becoming likely) | `/payloadcms/payload` | "Payload v3 setup with Next.js — minimum config + dev server installation" | `payload-setup.md` |
| **12** (CMS decision lock) | `/payloadcms/payload` | "Collections, Globals, fields overview — schema-as-code patterns for marketing sites" | `payload-collections-globals-fields.md` |
| **12** | `/payloadcms/payload` | "Localization configuration — locales array, field-level localized flag, fallback strategy" | `payload-localization.md` |
| **12** | `/payloadcms/payload` | "Blocks field — composing dynamic page layouts; localized blocks vs localized fields inside blocks" | `payload-blocks-field.md` |
| **12** (when DB hosting decided) | `/payloadcms/payload` | "Database adapters — Postgres Vercel-Postgres Neon Mongo SQLite — selection and config" | `payload-db-adapters.md` |
| **17** (design system / BrandTokens) | `/payloadcms/payload` | "Globals — site settings + brand tokens patterns + afterChange ISR revalidation" | `payload-globals.md` |
| **18** (component build) | `/payloadcms/payload` | "Block field examples — Hero, RichText, MediaGallery, CTA patterns for marketing pages" | `payload-blocks-examples.md` |
| **18** | `/payloadcms/payload` | "Lexical rich text editor — BlocksFeature for embedding blocks in prose; default features" | `payload-lexical.md` |
| **18** | `/payloadcms/payload` | "Access control patterns — public read for published, admin/editor write" | `payload-access-control.md` |
| **18** | `/payloadcms/payload` | "Versioned drafts + live preview configuration" | `payload-versions-livepreview-hooks.md` |
| **22** | `/payloadcms/payload` | "Form Builder plugin (@payloadcms/plugin-form-builder) — contact forms + submissions collection" | `payload-form-builder.md` |
| **22** | `/payloadcms/payload` | "Email integration (@payloadcms/email-nodemailer / email-resend) — transactional email on hooks" | `payload-email.md` |
| **24a** | `/payloadcms/payload` | "Stripe Pay plugin (@payloadcms/plugin-stripe) — product sync, customer sync, webhook handlers" | `payload-stripe-plugin.md` |
| **28** (deploy) | `/payloadcms/payload` | "Deploying Payload v3 to Vercel — build command, migration step, env vars, Postgres" | `payload-deploy.md` |
| **28** | `/payloadcms/payload` | "Payload Cloud setup" (only if user picks managed hosting) | `payload-cloud.md` |
| **33** (backup / monitoring) | `/payloadcms/payload` | "Backup strategy for Payload — Postgres dumps + media S3 + versioned drafts retention" | `payload-backup.md` |

**Version-specific lookups when the user pins to a specific Payload version:** use `/payloadcms/payload/v3.84.0` (or whatever's current) instead of the unversioned ID. Payload's context7 corpus includes versions v2.12.1 / v2.16.1 / v3.49.1 / v3.53.0 / v3.59.1 / v3.69.0 / v3.77.0 / v3.79.1 / v3.80.0 / v3.81.0 / v3.82.0 / v3.83.0 / v3.84.0 as of 2026-05-20. The agent uses the version-specific ID when (a) the user pinned a specific version in `package.json`, OR (b) when a minor version bump caused behavioral changes the user is investigating (e.g., v3.79 → v3.80 the autosave default changed).

**Secondary mirror:** `/llmstxt/payloadcms_llms-full_txt` (6552 snippets, full-text mirror, benchmark 42.12). Useful when the primary context7 corpus returns too narrowly — the llmstxt mirror has broader-but-less-precise coverage.

### MCP availability audit (per Round-3 doctrine)

Comprehensive enumeration verified 2026-05-20. Each MCP investigated below for the Payload-specific surface. Negative findings documented per Round-3 audit doctrine; the agent does NOT keep searching at runtime for non-existent MCPs.

#### Payload-specific MCPs

##### Payload CMS MCP — Antler Digital plugin (recommend when cms=payload)

- **Canonical URL:** https://payload-plugin-mcp.vercel.app/ + https://github.com/antler-digital/payload-plugin-mcp (the official MCP plugin for Payload, indexed at lobehub). Verified 2026-05-20.
- **Maintainer + recency:** Antler Digital (community, active). Separate from Payload's own Claude Code skill (`github.com/payloadcms/payload/tools/claude-plugin/skills/payload` — that's a development-guidance skill, not an MCP server).
- **Install (Payload v3 + Next.js project, Antler MCP plugin):** added as a Payload **plugin** in `payload.config.ts` (not as a standalone MCP server). After install, the plugin auto-generates MCP tools for every Payload collection (`mcp__payload__pages_*`, `mcp__payload__posts_*`, etc.). HTTP transport (NOT SSE) per the plugin docs.

  ```ts
  // payload.config.ts
  import { mcpPlugin } from '@antler-digital/payload-plugin-mcp'

  export default buildConfig({
    plugins: [
      mcpPlugin({
        // expose specific collections as MCP tools
        collections: ['pages', 'posts', 'media'],
      }),
    ],
  })
  ```

- **Used by agent at:** phase **12** (CMS decision — surfaces Payload's structured-content + RBAC + drafts/versions feature surface to the user via the auto-generated MCP tool descriptions), phase **18** (Block authoring + Collection seeding — agent calls `mcp__payload__pages_create` instead of constructing Local API calls), phase **22** (Payload `localized: true` field-level i18n setup — natural-language "add a German locale + localize the title field on Pages"), **post-launch** (content seeding from `.website-builder/content/pages/*.md` to Payload collections via the auto-generated MCP tools — bulk-import pattern; admin queries: "list all pages published in the last 7 days").
- **Fallback when not installed:** Payload's Local API directly (`payload.create()` / `payload.find()` / `payload.update()` — Payload v3 runs in the same Next.js app so the agent can call from Server Components or scripts). Or the REST API at `/api/<collection>` for cross-process access (with API key header). Functional; agent loses the MCP's auto-generated tool descriptions but retains full programmatic access.

##### Payload Skill (development guidance — NOT an MCP server)

- **Canonical URL:** `github.com/payloadcms/payload/tools/claude-plugin/skills/payload` (the Payload core team's Claude Code Skill, ships with Payload core).
- **What it is:** A Claude Code **Skill** (development-guidance pattern; reference docs + best-practice patterns the agent loads at relevant phases). NOT an MCP server. Loaded automatically when CC detects the user is working in a Payload project (via `payload.config.ts` presence detection).
- **Used by agent at:** phase 12 / 17 / 18 / 22 — provides up-to-date Payload patterns + idioms + common-pitfall reference. Complementary to context7 + the Antler MCP.

##### Drizzle MCP — **no dedicated MCP at the time of this audit (negative finding)**

- **Canonical search:** WebSearch `"Drizzle ORM" MCP server Model Context Protocol Claude 2026` — no Drizzle-specific MCP server surfaced as of 2026-05-20. Drizzle is an ORM library, not a service — its surface is per-database (Postgres, MySQL, SQLite) and tooling-driven (`drizzle-kit` CLI).
- **Why this matters:** Payload v3 uses Drizzle under the hood for its Postgres / SQLite adapters; the agent does NOT need a Drizzle MCP because Payload's own migration commands (`pnpm payload migrate:create`, `pnpm payload migrate`, `pnpm payload migrate:status`) abstract Drizzle entirely. Schema changes flow through Payload's commands, not direct Drizzle.
- **Fallback (canonical path):** Use Payload's migration commands. For raw Drizzle access (rare cases — custom queries, bulk migrations Payload's runner doesn't cover), agents use `drizzle-kit` CLI directly + `psql` for verification. Postgres MCP (below) is the more useful surface for raw DB inspection.

##### Postgres MCP — `crystaldba/postgres-mcp` (recommend for raw DB inspection)

- **Canonical URL:** https://github.com/crystaldba/postgres-mcp (community; well-maintained). Also: `cretueusebiu/postgres-mcp-server` exists. Verified 2026-05-20.
- **Maintainer + recency:** Crystal DB (community); active.
- **Install (Claude Code, stdio):**

  ```bash
  claude mcp add postgres -- uvx postgres-mcp --connection-string "postgresql://..."
  ```

  Reads `DATABASE_URL` from env or `--connection-string` arg.
- **Used by agent at:** phase **28** (migration verification — agent queries `pg_stat_user_tables` / `information_schema` to confirm Payload's migrations landed correctly), **post-launch** (DB inspection without leaving CC, query optimization for slow Payload Collections). NEVER used for direct schema changes (those route through `pnpm payload migrate` per the canonical-tool principle).
- **Fallback when not installed:** `psql` directly from `.env.local`-derived connection string. Or Neon MCP / Supabase MCP if those are installed (they cover the same surface).

##### Neon MCP — official (recommend when DB host = Neon)

- **Canonical URL:** https://neon.com/docs/ai/neon-mcp-server (official) + https://github.com/neondatabase/mcp-server-neon. Verified 2026-05-20.
- **Maintainer + recency:** Neon Database (official).
- **Install (Claude Code, OAuth remote OR API-key stdio):** Remote (preferred):

  ```bash
  claude mcp add --transport http neon https://mcp.neon.com/mcp
  ```

  OAuth flow → user picks Neon project. API-key alternative for stdio: pass `NEON_API_KEY` from `.env.local`.
- **Used by agent at:** phase **12** (when CMS=Payload + Postgres hosting → Neon; the agent drafts `.website-builder/decisions/cms-12-payload-postgres-host.md` at this moment), phase **29** (deploy — `pnpm payload migrate` runs against the Neon connection string; agent uses Neon's `prepare_database_migration` + `complete_database_migration` two-phase pattern for safer schema changes via temporary branches), **post-launch** (schema evolution via natural-language requests + branch-based testing of Payload migrations).
- **Safety note:** Same as Supabase MCP per stack-nextjs adapter — Neon MCP is for development/IDE integration only, not production. Agent applies migrations to a temporary branch first; user confirms before promotion. Two-phase pattern is the discipline.
- **Fallback when not installed:** Neon CLI (`neonctl`) for project/branch ops + `psql` for direct DB access; Payload's `pnpm payload migrate` runner for schema. Functional; loses temporary-branch safety pattern + natural-language interface.

##### Supabase MCP — official (recommend when DB host = Supabase)

- **Canonical URL:** https://supabase.com/docs/guides/ai-tools/mcp + https://github.com/supabase-community/supabase-mcp. Verified 2026-05-20.
- **Maintainer + recency:** Supabase (official Claude connector).
- **Install (Claude Code, OAuth via Claude.ai connector OR Claude Desktop connectors menu):**

  ```bash
  claude mcp add --transport http supabase https://api.supabase.com/mcp
  ```

  Browser OAuth → user selects organization + project.
- **Used by agent at:** phase **12** (when DB hosting choice → Supabase), phase **22** (forms with Supabase as backend for non-Payload CMSes — irrelevant here, but cross-ref), phase **29** (deploy — env var propagation + DB connection-string into Vercel via Vercel MCP).
- **Safety note:** Same as Neon — dev/IDE only, not prod schema changes via MCP. Use `prepare_database_migration` + `complete_database_migration` pattern.
- **Fallback when not installed:** Supabase JS SDK + `supabase` CLI; `psql` for raw DB access. Functional.

##### Lexical MCP — **no MCP at the time of this audit (negative finding)**

- **Canonical search:** WebSearch `"Lexical" editor MCP server Model Context Protocol Claude 2026` — no Lexical-specific MCP. Lexical is Meta's rich-text framework (also embedded in Payload v3); surface is library-only (no service to talk to).
- **Why this matters:** the agent does NOT keep searching at runtime. Lexical configuration (BlocksFeature, default features) happens in `payload.config.ts` via the `lexicalEditor()` factory; the agent edits this file directly via `Edit`/`Write` tools.
- **Fallback (canonical path):** Direct file edits + context7 `/payloadcms/payload` lookups for current Lexical-related Payload patterns (BlocksFeature, EXPERIMENTAL_TableFeature, etc.). Lexical docs themselves at https://lexical.dev when needed (rare).

##### Cross-references to shared stack-level MCPs

These MCPs are already audited in detail in `adapters/stack-nextjs.md` § "Auth + setup" → "MCP servers (recommended at setup)". Cross-referencing here for the Payload-specific subset:

- **Vercel MCP** — official, hosted OAuth at https://mcp.vercel.com. Used at phase 28 (custom-domain DNS) / 29 (production deploy via `mcp__vercel__deploy_to_vercel`) / 30 (analytics) / 34 (monitoring). Critical for the Vercel + Payload deploy path (covers ~70% of Payload deployments).
- **Cloudflare MCP** — hosted OAuth at https://mcp.cloudflare.com/mcp. Used at phase 28 (DNS record CRUD). Two-tool `search()` + `execute()` surface — DNS records routed through `execute()`.
- **Stripe MCP** — Anthropic plugin at `claude.com/plugins/stripe` (ships `stripe-mcp` subagent). Used at phase 24a/b/c when `transactional=true`. Critical for transactional Payload sites.
- **Cal.com MCP** — Claude custom connector (no install command). Used at phase 24a when `transactional_kind in [bookings, both]`.
- **GitHub MCP** — official at https://github.com/github/github-mcp-server. Used at phase 28-30 + post-launch for repo + PR ops.
- **Sentry MCP** — official at https://docs.sentry.io/product/sentry-mcp/. Used at phase 30/34 for monitoring + issue investigation.
- **context7 MCP** — pre-loaded in plugin foundation.
- **Playwright MCP** — pre-loaded; used at phase 6.5 (deployed-site walk, including authenticated Payload admin) + phase 20 (responsive + i18n walk including locale-switch in admin) + phase 22 (a11y audit of Payload admin if user-facing) + phase 27/29 (deploy verification — admin + frontend both walked).

#### Negative findings — explicitly NO MCP at this surface

| Surface | Negative-finding status (2026-05-20) | Canonical fallback |
|---|---|---|
| **Drizzle ORM MCP** | No dedicated MCP. Drizzle is per-DB; tooling is `drizzle-kit` CLI. | Payload's `pnpm payload migrate` commands abstract Drizzle. Direct Drizzle access via `drizzle-kit` CLI when needed (rare). |
| **Lexical MCP** | No MCP exists. Lexical is a library; no service surface. | Direct file edit on `payload.config.ts` for Lexical config; context7 `/payloadcms/payload` for current BlocksFeature / EXPERIMENTAL features. |
| **Payload Cloud admin MCP** | No dedicated MCP for managed-hosting admin ops. Payload Cloud is configuration-via-web. | Direct Payload Cloud web UI; standard Payload API for content ops (the Antler MCP works against any Payload deployment, including Payload Cloud). |

**Setup discipline:** None of these are bundled by the website-builder plugin. The agent enumerates the Payload-relevant MCPs (Antler MCP if cms=payload + the shared stack-level MCPs from stack-nextjs adapter) at first-run setup (phase 11/12) and surfaces install commands for the user to run before phase 28. The agent NEVER pretends an MCP exists when it doesn't (per the negative-findings table) and falls back per `.claude/rules/tool-dependency-discipline.md` Tier 2.

## References

**Foundation design docs (vault-root-relative per link standard):**

- `DESIGN-cms-payload.md` — primary design-doc source for this adapter (~649 lines)
- `DESIGN-content-layers.md` — 5-layer content stack the §6 table maps
- `DESIGN-i18n.md` — i18n model + Decisions 38-41
- `DESIGN-architecture.md` — plugin directory layout (`cms-adapters/` per line 115)
- `DESIGN-phase-contracts.md` — phase 12 (CMS decision) + phase 18 (component build) + phase 22 (forms/i18n) + phase 24a/b/c (commerce)
- `DESIGN-project-scaffold.md` — `.website-builder/` layout the seeds mirror
- `DESIGN-ingestion-and-extraction.md` — phase 6.5 mechanism
- `adapters/README.md` — stack adapter contract; `## Content layer mapping` row labels MUST match
- `adapters/stack-nextjs.md` — Captain G's Phase 3 work; the canonical pairing
- `cms-adapters/README.md` — the 12-section schema contract this file follows
- `commerce-adapters/README.md` — commerce/booking schema contract (sibling Phase 4 prep)
- `commerce-adapters/payment-config-schema.md` — canonical `payment-config.yaml` schema for TWINT-via-Stripe-on-CHF
- `i18n/strings-schema.md` — stack-agnostic CDJSON contract
- `i18n/language-switcher.md` — switcher per-stack
- `i18n/hreflang.md` — hreflang per-stack
- `i18n/rtl.md` — RTL discipline
- `handoff-spec/component-request-v1.md` — Layer 5 brief schema
- `handoff-spec/component-output-v1.md` — Layer 5 output ingestion contract
- `tests/cms-adapters/README.md` — Phase 4 fixture convention this adapter's fixture follows
- `tests/cms-adapters/payload/README.md` — this adapter's test fixture
- `BUILD-strategy.md` Phase 4 — DoD + dispatch model
- `skills/wb-architecture/SKILL.md` — phase 12 consumer
- `skills/wb-component-build/SKILL.md` — phase 18 consumer

**Sibling workstream — Payload reference site (the production proof):**

- The `website-starter` workstream (vault-side; not shipped) — STATE doc + DESIGN-component-library.md; SynSol + AWin Payload-based reference site. 12 collections, 6 globals, 13-15 blocks (Hero 4-variant, FeaturesGrid 3-variant, ProcessSteps, Testimonials 3-variant, TeamGrid, LogoGrid, Contact, FormWizard, BlogArchive). Brand-config.json → BrandTokens-global → theme.generated.css pattern. Deployed via Vercel.

**Payload external references:**

- Payload official docs: https://payloadcms.com/docs
- Payload v3 installation: https://payloadcms.com/docs/getting-started/installation
- Payload Collections: https://payloadcms.com/docs/configuration/collections
- Payload Globals: https://payloadcms.com/docs/configuration/globals
- Payload Fields: https://payloadcms.com/docs/fields/overview
- Payload Blocks field: https://payloadcms.com/docs/fields/blocks
- Payload Localization: https://payloadcms.com/docs/configuration/localization
- Payload Access Control: https://payloadcms.com/docs/access-control/overview
- Payload Versions / Drafts: https://payloadcms.com/docs/versions/overview
- Payload Live Preview: https://payloadcms.com/docs/live-preview/overview
- Payload Hooks: https://payloadcms.com/docs/hooks/overview
- Payload Lexical rich text: https://payloadcms.com/docs/rich-text/overview
- Payload Lexical Blocks feature: https://payloadcms.com/docs/rich-text/blocks
- Payload Migrations: https://payloadcms.com/docs/database/migrations
- Payload Production Deployment: https://payloadcms.com/docs/production/deployment
- Payload Stripe plugin: https://payloadcms.com/docs/plugins/stripe
- Payload Form Builder plugin: https://payloadcms.com/docs/plugins/form-builder
- Payload Email integrations: https://payloadcms.com/docs/email/overview
- Payload Cloud: https://payloadcms.com (hosting tier — pricing per costbench.com/software/headless-cms/payload-cms)
- Payload v3 release notes: https://github.com/payloadcms/payload/releases (verified v3.84.1 latest 2026-05-20)
- Payload website-starter template: https://vercel.com/templates/cms/payload-website-starter
- context7 library ID: `/payloadcms/payload`
- context7 full-text mirror: `/llmstxt/payloadcms_llms-full_txt`
- Antler Digital Payload MCP plugin: https://github.com/antler-digital/payload-plugin-mcp
- Payload Claude Code Skill (development guidance — NOT an MCP): https://github.com/payloadcms/payload/tree/main/tools/claude-plugin/skills/payload

**Database hosting external references:**

- Neon pricing: https://neon.com/pricing (verified 2026-05-20: Free 0.5 GB + 100 CU-hours; Launch $0.106/CU-hour + $0.35/GB-month)
- Neon MCP: https://neon.com/docs/ai/neon-mcp-server
- Supabase pricing: https://supabase.com/pricing (Free 500 MB; Pro $25/mo)
- Supabase MCP: https://supabase.com/docs/guides/ai-tools/mcp
- Vercel pricing: https://vercel.com/pricing (Hobby free; Pro $20/user/mo)
- Vercel + Neon (Postgres deprecation): https://vercel.com/docs (Vercel Postgres deprecated Dec 2024; migrated to Neon)
- Payload Cloud pricing: per costbench.com/software/headless-cms/payload-cms — Standard $35/mo, Pro $199/mo, Enterprise custom

**Migration discipline references:**

- Payload migration vs push mode (production discipline): https://www.buildwithmatija.com/blog/payloadcms-postgres-push-to-migrations
- Payload migrations on Vercel: https://github.com/payloadcms/payload/discussions/11980
- Payload jobs on Vercel serverless: https://dev.to/aaronksaunders/run-payload-jobs-on-vercel-serverless-step-by-step-migration-aj9

**Strategic / coordination references:**

- Locked decision 53 (MVP CMS triplet: none / Decap / Payload): `website-builder.md` decisions ledger
- Locked decision 39 (Pages-per-language Pattern A default): `DESIGN-i18n.md`
- Locked decision 65 (per-Captain worktree isolation): `website-builder.md`
- Phase 4 dispatch model: `BUILD-strategy.md` Phase 4
