# Reference — CMS matrix (phase 12)

> Per-CMS prose for the three MVP CMS options + stack-built-in defaults, the i18n strategy table, the Decap-maintenance-mode caveat, and the expansion-CMS substitution table. Authoritative source is `cms-adapters/cms-{none,decap,payload}.md` + `phase-contracts/12-cms-decision.md` — read those fully for any CMS the user seriously considers. This file is the fast-load summary.

## The agent's job at phase 12: challenge defaults

Many muggles reach for "the most feature-rich CMS" because the feature list reads impressive. Surface YAGNI honestly — *"you have 5 pages and you'll edit them quarterly; file-based markdown is enough"* — and only escalate to a heavier CMS when the actual content shape demands it (multiple editors, content beyond markdown, structured relationships, role-based access). The CMS choice doesn't eliminate code; it eliminates *content-editing* code-work. Reframe the common "I want a CMS so I don't have to know code" instinct: *"the question isn't whether you'll touch code at all; it's whether ongoing content updates touch code. A CMS removes that touch; everything else still gets built."*

## MVP CMS options (decision 53 — build-now for v1)

### `none` — file-based markdown

Content lives as markdown files in the user's git repo (`content/pages/*.md`, `content/posts/*.md`, `content/strings/{lang}.json`); the framework reads at build; the user edits in any text editor and commits. No admin UI, no auth, no database, no deploy chain beyond `git push`.

- **Right answer for:** one editor, low cadence (weekly or less), content that fits markdown + structured frontmatter (sitemaps, blog posts, marketing pages, portfolios). Most brochure and personal sites.
- **The agent's value here:** make git-based editing feel like a CMS — generate a `.vscode/` workspace with extensions configured, a YAML schema bound to frontmatter for inline validation, a pre-commit hook running Zod schema checks across content files, a `package.json` quick-commit helper. CMS-quality discipline without a CMS.
- **Trade-offs surfaced honestly:** no multi-editor real-time collab, no visual editing, editor must open a code editor, no built-in scheduled publishing.
- **Pairs cleanly with** the MVP static-export-of-Next.js path. (Astro/Hugo are even more natural but ship later.)

### Decap — git-backed admin

Single-page-app admin UI that commits markdown + YAML directly to the user's repo via OAuth. No backend — two files (`admin/index.html` + `admin/config.yml`) served from the site, talking to GitHub/GitLab/Bitbucket/Gitea REST. Every save = a commit; every revert = `git revert`; **the repo is the database**.

- **Pick when:** the user wants a CMS-shaped editor on a static stack without backend operational overhead. 1-3 editors, weekly cadence. The sweet spot between `none` and a heavier CMS. User gets a `/admin` URL, a form per content type, an editorial-workflow drafts-and-PRs view, a media library.
- **Cost:** every save is a commit (10-30s before the new build is live); real-time multi-editor produces git conflicts (no locks, no presence); auth is "you have repo write access or you don't" (no fine-grained RBAC); no content API; UI slows past a few thousand items.
- **Maintenance-mode caveat — surface at decision time:** Decap is in maintenance mode upstream since the Netlify rename. It still works and the agent supports it, but velocity is lower than Payload's. **Active drop-in forks: Sveltia CMS (`github.com/sveltia/sveltia-cms`) and Static CMS (`github.com/StaticJsCMS/static-cms`)** — same config schema, active development. Offer three responses: (1) proceed with Decap and accept the risk, (2) switch to a fork, (3) escalate to Payload. User picks; agent logs.
- **Docs:** `WebFetch` decapcms.org/docs (context7 coverage thin) for config-schema, OAuth backends, i18n. i18n default is Pattern A: `structure: multiple_files` (per decision 39).

### Payload — schema-as-code on Next.js

Payload v3 is a TypeScript framework that drops onto Next.js as headless CMS + admin panel + REST + GraphQL + Local API + generated TS types — all from `CollectionConfig` files. The **Blocks field** is the load-bearing primitive for marketing sites: editors compose pages by stacking/reordering blocks (Hero, RichText, MediaGallery, CallToAction, LogoCloud, Testimonial) the agent defined in TypeScript. Output is a discriminated-union JSON array the frontend renders by `blockType`. **Schema IS code** — git is the source of truth, PRs review schema changes, rollbacks are `git revert`.

- **Pick when:** stack=Next.js, content is more than a flat page list (multiple collections + relationships: Pages→Authors→Posts→Categories→CaseStudies), the user values schema-as-code, and either multiple editors or structured cross-collection relationships. Strongest versioning/drafts/live-preview among MVP options; role-based access at collection/field/document granularity. Aligns with the Jules-Solutions website-starter substrate (also Payload-based).
- **Cost (real — surface at decision time):** needs a Node runtime (Vercel/Render/Railway/Fly/self-hosted Docker on JS-1 — shared hosting and pure-static hosts don't work); needs a database (**Postgres via Drizzle is the muggle-friendly default** — Vercel Postgres or Neon; MongoDB and SQLite supported); **migrations run on every deploy** (`pnpm payload migrate && next build` in the Vercel build command — forgetting once produces schema drift, caught at phase 29); the admin is a full Next.js app — overkill for a 5-page brochure (surface `none` or Decap).
- **Two notes the agent surfaces:** (1) Payload v3 is Next.js-native — pairing with Astro/SvelteKit means a separate headless backend, losing single-deploy ergonomics. (2) Blocks-field localization choice: localizing the entire `layout` field → different per-locale layouts (i18n Pattern B); localizing text fields *inside* each block → shared layout + translated prose (Pattern A, the decision-39 default). Walk this trade-off with the user.
- **Install (verified via context7 `/payloadcms/payload` 2026-05-18):** `pnpm i payload @payloadcms/next @payloadcms/richtext-lexical sharp` + `@payloadcms/db-postgres`; wrap `next.config` with `withPayload(nextConfig)` (ESM required). Drafts + RBAC pattern: `versions: { drafts: true }` + `access.read` returning `{ _status: { equals: 'published' } }` for unauthenticated users, `true` for authenticated. Payload v3.84.0 latest, benchmark 82.1, High reputation. Cache to `.website-builder/library/docs/payload.md`.

### Stack-built-in defaults (natural pairings — thin confirmation pass)

- **Stack = Framer → `framer-cms`.** Framer's built-in CMS (Framer Pro plans). No separate decision, hosting, or auth. Handles blog posts, product listings, team members, testimonials cleanly; limits show at deep cross-references or unusually-structured records. Escape hatch for more: a headless CMS (Payload/Sanity) via Framer Custom Components — re-opens phase-12 if applicable.
- **Stack = WordPress → `wordpress-core`.** WordPress IS the CMS — admin UI, custom post types, ACF/Meta Box for structured content, Gutenberg block editor. Essentially trivial decision. Only exception: headless-WordPress (WP REST consumed by a Next.js/Astro frontend) — which makes Next.js/Astro the actual stack with WP as CMS layer, re-opening phase 11.

Surface these as defaults when stack is Framer or WordPress; diverge only with explicit user reasoning.

## i18n strategy (lock at phase 12 — failing to lock now = drift at phase 16)

For multilingual sites, write `cms_i18n_strategy`:

| CMS | Pattern A (shared structure, translated prose — decision-39 default) | Pattern B (per-locale layouts) |
|---|---|---|
| `none` | per-language files or per-language folders | per-language folders with distinct page structure |
| `decap` | collection `i18n: true` + per-field `i18n: true/false`; `structure: multiple_files` → `post.en.md` / `post.de.md` | distinct file collections per locale |
| `payload` | `localized: true` on `title`, `meta.*`, and each text field *inside* each block; one DB row, locale values as JSON columns; `localization.fallback: true` for string-missing fallback (decision 41) | `localized: true` on the entire `layout` blocks field — each locale gets its own block array |

## Gating (phase 12)

- **Incompatible-with-stack** (Payload on Hugo, Decap on plain static HTML without a generator, Framer-CMS on Next.js) — surface mismatch + compatible alternatives. Override requires explicit acceptance of operational cost. "No `cms` value set" — not overridable.
- **Heavy CMS without operational fit** (Payload for a 5-page quarterly-edit brochure) — surface YAGNI, offer lighter. Overridable with honest logging of the over-tooling reasoning.
- **Light CMS without operational fit** (`none` for a 200-page 3-non-technical-editor site) — surface the inverse ("git-based editing breaks past 2-3 editors at weekly cadence"), offer Decap/Payload. Overridable with logging.
- **Transactional site without transactional-capable CMS** — the three MVP-compatible transactional patterns: WordPress+WooCommerce, Next.js+Payload, Framer+embedded checkout. Decap can't really; `none` only if commerce is purely embedded Stripe Buy-Buttons.
- **Multilingual without an i18n-capable strategy** — confirm the strategy this phase.

## Expansion CMS options (post-MVP — expansion phase 10)

Fully designed in the website-builder workstream (vault-side), accessible to users who know them, not first-class in MVP. Mention only when surfaced by the user.

| Expansion CMS | What it is | Closest MVP substitute |
|---|---|---|
| **Strapi** | UI-first content modeling (build content types via admin, not TS) | Payload (Next.js) or stack-built-in (Framer/WP) |
| **Sanity** | Structured content + portable JSON + GROQ + hosted Content Lake | Payload |
| **TinaCMS** | Markdown-in-git + visual inline editing on live preview | Decap (form-based, no visual preview) |
| **Directus** | Wraps any SQL DB → CMS with auto REST + GraphQL | Payload (with Postgres) |
| **Keystone** | Typed schema-as-code, lighter than Payload | Payload |
| **Ghost** | Content-first blog/newsletter CMS with built-in members + paid subs | Payload (custom members) or WordPress (membership plugin) |

If the user insists on an expansion CMS for v1: log `.website-builder/decisions/cms-expansion-${cms}.md`, surface that MVP runtime adapters aren't shipped, and either proceed with degraded support or route to an MVP CMS with an intent-to-migrate note. Random hosted SaaS CMSes outside the nine-CMS-plus-stack-built-in surface get no agent support, no recipe — the user owns the integration entirely.

## project.yaml output (phase 12)

```yaml
cms: payload                     # none | decap | payload | framer-cms | wordpress-core (MVP) or expansion w/ logged decision
cms_reasoning: |
  2-4 sentences: why this CMS given stack (phase 11) + content shape (phase 9 sitemap)
  + editor count + i18n needs; what was ruled out.
cms_hosting: vercel-postgres     # only for CMS needing separate hosting (Payload, headless options)
cms_i18n_strategy: pattern-a     # pattern-a | pattern-b — when multilingual
```

When CMS=Payload+Postgres, also draft `.website-builder/decisions/cms-12-payload-postgres-host.md` (phase-29 readiness note with the `pnpm payload migrate && next build` build-command convention pre-staged). Seed `.website-builder/library/docs/${cms}.md` with cached docs.
