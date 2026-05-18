---
phase: 12
name: CMS decision
group: architecture
pipeline_section: architecture
prev_phase: 11
next_phase: 13
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-phase-contracts.md
  - Workstreams/website-builder/foundation/DESIGN-architecture.md
  - Workstreams/website-builder/foundation/DESIGN-project-scaffold.md
  - Workstreams/website-builder/foundation/DESIGN-content-layers.md
  - Workstreams/website-builder/foundation/DESIGN-i18n.md
  - Workstreams/website-builder/cms/DESIGN-cms-none.md
  - Workstreams/website-builder/cms/DESIGN-cms-decap.md
  - Workstreams/website-builder/cms/DESIGN-cms-payload.md
---

# Phase 12 — CMS decision

> Pick how content is managed. None for static sites the user edits in code; Decap for static stacks that want a free git-backed admin; Payload for Next.js sites that earn a real schema-as-code backend. Or — if the stack from phase 11 has a native CMS (Framer / WordPress) — use it. This phase locks `project.yaml.cms` and pairs it with the stack from phase 11.

## Mission

Phase 11 picked the stack. Phase 12 picks the content management surface on top of it. Two outcomes shape this decision: how content updates happen after the agent leaves, and how much operational footprint the user is willing to carry.

The website-builder MVP supports three CMS choices for users who pick Next.js, plus the natural defaults that ship inside Framer and WordPress as their own stacks. Per locked decision 53: *MVP CMS scope = none + Decap + Payload for v1.* Strapi, Sanity, TinaCMS, Directus, Keystone, and Ghost are designed in full in the workstream and accessible to users who already know them, but they ship in expansion phase 10 of the platform roadmap. The agent surfaces them as future-available paths during the MVP, not as build-now options.

The agent's job in this phase is to challenge defaults. Many muggles reach for "the most feature-rich CMS" because the feature list reads impressive. The agent surfaces YAGNI honestly — *"you have 5 pages and you'll edit them quarterly; file-based markdown is enough"* — and only escalates to a heavier CMS when the actual content shape demands it (multiple editors, content beyond markdown, structured relationships, role-based access).

The agent uses **context7** in this phase to fetch fresh CMS docs for whichever option is on the table. Payload v3 evolves quickly; Decap is in maintenance mode and the agent surfaces the implications; WordPress core and WPML/Polylang shift annually.

## Entry conditions

- Phase 11 (stack decision) complete. `.website-builder/project.yaml.stack` is one of `framer` / `nextjs` / `wordpress` (MVP) or an explicitly-logged expansion stack.
- `.website-builder/project.yaml.transactional` is set (drives some CMS pairings — Ghost for paid memberships, WooCommerce-paired WordPress for transactional sites).
- `.website-builder/sitemap.yaml` exists with the page count (drives the "is a CMS worth the overhead" question).
- `.website-builder/project.yaml.languages` is set or will be set in this phase (CMS choice depends on i18n needs; some CMSes — Decap, Payload — make i18n cheap, others — Strapi, Ghost — make it expensive).

## What Claude must establish

`.website-builder/project.yaml.cms` is set to one of:

- `none` — file-based markdown, no admin surface
- `decap` — git-backed admin UI on top of static-stack markdown
- `payload` — schema-as-code TypeScript CMS embedded in Next.js
- `framer-cms` — Framer's built-in CMS (only when stack is Framer)
- `wordpress-core` — WordPress's native admin (only when stack is WordPress)
- An expansion CMS with an explicitly-logged decision (see Expansion CMS sub-section)

The agent also writes `project.yaml.cms_reasoning` — 2-4 sentences explaining the choice — and, if the chosen CMS requires hosting beyond the stack itself (Payload needs a Node host + database; some expansion CMSes need separate infra), the agent writes `project.yaml.cms_hosting` capturing the planned hosting decision (the actual deploy happens at phase 29).

For multilingual sites, the agent also confirms `project.yaml.cms_i18n_strategy` per the CMS's i18n model (Pattern A or Pattern B per `DESIGN-i18n.md`); the structural choice locks here so phases 13-16 can author content accordingly.

## MVP CMS options (full prose)

### `none` — file-based markdown

The simplest and often the right answer. Content lives as markdown files in the user's git repo (`content/pages/*.md`, `content/posts/*.md`, `content/strings/{lang}.json`); the static-site framework reads them at build; the user edits them in VS Code (or any text editor) and commits. There is no CMS — no admin UI, no auth, no separate database, no deploy chain beyond `git push`.

This is the right answer for sites with one editor, low edit cadence (weekly or less), and content that fits markdown plus structured frontmatter (sitemaps, blog posts, marketing pages, portfolios). Most brochure sites and personal sites should pick this. The website-builder still enforces every other discipline — design system, components, accessibility, deploys — but skips CMS overhead.

The agent's value here is making git-based editing feel like a CMS. The agent generates a `.vscode/` workspace with the right extensions configured, a YAML schema attached to frontmatter for inline validation, a pre-commit hook that runs Zod schema checks across all content files, and a `package.json` helper script for quick commits. The user gets CMS-quality discipline without a CMS. Trade-offs surfaced to the user honestly: no multi-editor real-time collab, no visual editing, editor must open a code editor, no scheduled publishing built-in.

The `none` choice pairs cleanly with the MVP static-export-of-Next.js path. Astro and Hugo and the other expansion stacks are even more natural fits but ship later. Full design at `Workstreams/website-builder/cms/DESIGN-cms-none.md`.

### Decap — git-backed admin

Decap CMS (formerly Netlify CMS) is a single-page-app admin UI that commits markdown and YAML directly to the user's git repository via OAuth. There is no backend — Decap is two files (`admin/index.html` + `admin/config.yml`) served from the user's site that talk to GitHub (or GitLab / Bitbucket / Gitea) via REST. Every save in admin is a commit. Every revert is a `git revert`. The repo is the database.

The agent picks Decap when the user wants a CMS-shaped editor surface on a static stack but doesn't want the operational overhead of running a real backend. The user gets a `/admin` URL, a form for each content type, a "Workflow" view for drafts-and-PRs editorial review, and a media library — and the cost is: every save is a commit (so save latency is 10-30 seconds before the new build is live), and real-time multi-editor collaboration produces git conflicts. For 1-3 editors with weekly cadence, Decap is the sweet spot between `none` and a heavier CMS.

The agent surfaces a structural fact at decision time: Decap is in maintenance mode upstream since the Netlify rename. Active forks exist (Sveltia CMS, Static CMS) as drop-in replacements. Decap still works and the agent supports it, but the user should know the project's velocity is lower than Payload's or Strapi's. The Sveltia / Static CMS forks are surfaced as upgrade paths.

The agent invokes context7 for `decapcms.org/docs` (or `WebFetch` if not present in context7 at sufficient quality) at this phase to confirm current config-schema, OAuth backend options, and i18n configuration (`structure: multiple_files` is the Pattern A default per locked decision 39). Full design at `Workstreams/website-builder/cms/DESIGN-cms-decap.md`.

### Payload — schema-as-code on Next.js

Payload v3 is a TypeScript framework that drops onto Next.js as a fully-functional headless CMS plus admin panel plus REST + GraphQL API plus Local API plus generated TypeScript types — all from one set of `CollectionConfig` files. The Pages collection's `blocks` field is the load-bearing primitive for marketing-website use cases: editors compose pages by stacking and reordering blocks (Hero, RichText, MediaGallery, CallToAction, LogoCloud, Testimonial, etc.) the agent has defined in TypeScript.

The agent picks Payload when stack is Next.js, content is more than a flat list of pages, the user values schema-as-code (where the schema lives in git, reviewed via PR, rolled back via `git revert`), and either the team has multiple editors or the site has structured relationships across collections (Pages → Authors → Posts → Categories → Testimonials → Case Studies). Payload's localization is field-level (`localized: true` per field); its versioning + drafts + live-preview support is the strongest among the MVP options; its access control is role-based with collection-level, field-level, and document-level granularity.

The cost is real and surfaced at decision time. Payload needs a Node runtime (Vercel / Render / Railway / Fly / self-hosted Docker on JS-1 — shared hosting and pure-static hosts do not work). Payload v3 requires a database (Postgres via Drizzle is the muggle-friendly default — Vercel Postgres or Neon — with MongoDB and SQLite supported). Migrations run on every deploy (`pnpm payload migrate && next build` in the Vercel build command), and forgetting this once produces schema drift. The admin UI is a full Next.js admin app; for a 5-page brochure site, this is overkill — surface `none` or Decap as alternatives.

Two specific notes the agent surfaces: (1) Payload v3 is Next.js-native — pairing it with Astro or SvelteKit means running it as a separate headless backend, which is doable but loses the single-deploy ergonomics; (2) the Blocks field has a localization choice — localizing the entire `layout` field gives different per-locale layouts (matches `DESIGN-i18n.md` Pattern B); localizing the text fields *inside* each block keeps shared layout with translated prose (matches Pattern A, the default per locked decision 39). The agent walks through this trade-off with the user.

The agent invokes context7 with `/payloadcms/payload` at this phase. Library benchmark 82.1, High reputation, v3.84.0 latest as of 2026-05-18. Cached to `.website-builder/library/docs/payload.md`. Full design at `Workstreams/website-builder/cms/DESIGN-cms-payload.md`.

### Stack-built-in defaults (natural pairings)

When the stack from phase 11 is **Framer**, the natural CMS default is **Framer CMS** — the built-in CMS that ships with Framer Pro plans. The agent surfaces this as the path of least resistance: no separate decision, no separate hosting, no separate auth. Framer CMS handles the common content shapes (blog posts, product listings, team members, testimonials) cleanly; its limits start showing when content modeling needs deep cross-references or unusually structured records. For users who need more than Framer CMS handles, the escape hatch is a headless CMS (Payload, Sanity) consumed via Framer Custom Components — the agent surfaces this trade-off and re-opens the phase-12 decision if applicable.

When the stack is **WordPress**, WordPress IS the CMS. WordPress core's admin UI, custom post types, Advanced Custom Fields (or Meta Box) for structured content, and the Gutenberg block editor cover essentially every content shape. The agent does not pick a "separate CMS" for WordPress sites except in the headless-WordPress case — running WordPress as a REST API consumed by a Next.js or Astro frontend, which then makes Next.js / Astro the actual stack with WordPress as CMS layer. For canonical WordPress sites, `project.yaml.cms = wordpress-core` and the decision is essentially trivial.

These two pairings exist outside the `none` / Decap / Payload MVP triplet because they're built into their respective stacks. The agent surfaces them as defaults when stack is Framer or WordPress and only diverges from them with explicit user reasoning.

## Expansion CMS options (post-MVP, expansion phase 10)

The six CMSes below are fully designed in `Workstreams/website-builder/cms/` and accessible to users who already know them. They ship in expansion phase 10 of the platform roadmap. The agent mentions them only when surfaced by the user; for v1, the agent steers toward the MVP options above.

- **Strapi** — UI-first content modeling (editors build content types via the admin, not via TypeScript). Sweet-spot fit for muggle-friendly teams who want a CMS admin without writing schema code. MVP closest substitute: Payload (for Next.js stacks) or stack-built-in (Framer / WordPress).
- **Sanity** — structured content + portable JSON + GROQ queries + hosted Content Lake. Sweet-spot fit for content with heavy cross-references and real-time collaborative editing. MVP closest substitute: Payload.
- **TinaCMS** — markdown-in-git plus visual editing (click an element on the live preview, edit inline, save commits). Sweet-spot fit for static stacks where the user wants Decap's git-back model with visual editing. MVP closest substitute: Decap (form-based, no visual preview).
- **Directus** — wraps any SQL database and turns it into a CMS with auto-generated REST + GraphQL APIs. Sweet-spot fit for users migrating from existing SQL systems or sharing the database with another application. MVP closest substitute: Payload (with Postgres).
- **Keystone** — typed schema-as-code with a smaller surface than Payload. Sweet-spot fit for TypeScript-heavy teams who want a lighter Payload. MVP closest substitute: Payload.
- **Ghost** — content-first CMS specialized for blogs and newsletters with built-in members and paid subscriptions. Sweet-spot fit for newsletter-shaped sites with paid memberships. MVP closest substitute: Payload (custom-built members) or WordPress (with a membership plugin).

If the user insists on an expansion CMS for v1, the agent logs the decision in `.website-builder/decisions/cms-expansion-${cms}.md`, surfaces that MVP-runtime adapters are not yet shipped, and either proceeds with degraded support (the user accepts the risk) or routes to an MVP CMS for v1 with an intent-to-migrate note.

## Gating rules

The agent refuses to advance when:

- **CMS pick incompatible with stack.** Payload on Hugo. Decap on plain static HTML without a generator. Framer CMS when stack is Next.js. The agent surfaces the mismatch and offers compatible alternatives. Override on stack-CMS-mismatch requires explicit acceptance of the operational cost.
- **Heavy CMS picked without operational fit.** Payload picked for a 5-page brochure site updated quarterly. The agent surfaces YAGNI — *"you have 5 pages and you'll edit them quarterly; Payload's full admin is heavier than the editing problem. Want me to drop to file-based markdown or Decap?"* — and offers the lighter alternatives. The user can still pick Payload; the agent logs the over-tooling reasoning honestly.
- **Light CMS picked without operational fit.** `none` picked for a 200-page site with three non-technical editors. The agent surfaces the inverse — *"git-based editing breaks down past 2-3 editors with weekly cadence; we'd be back here in 3 months"* — and offers Decap or Payload.
- **Transactional site without transactional-capable CMS.** If `transactional: true` and CMS doesn't support a path to commerce (Decap can't really; `none` only works if commerce is purely embedded Stripe-Buy-Buttons), the agent surfaces the gap and routes to a compatible option. WordPress + WooCommerce, Next.js + Payload, or Framer + embedded checkout are the three MVP-compatible transactional patterns.
- **Multilingual site without i18n-capable CMS strategy.** Decap supports i18n via `structure: multiple_files`. Payload supports field-level localization. `none` (file-based) supports per-language files or per-language folders. The agent confirms the i18n strategy at this phase — failing to lock it now produces drift at phase 16.

Override is available on the YAGNI-direction gates via explicit user confirmation. The "no value set" and "incompatible-with-stack" gates are not overridable — they must be resolved before advance.

## Tools and skills used

- **AskUserQuestion** — the primary tool. The agent presents the MVP options and asks the user to pick after walking through trade-offs.
- **`mcp__context7__resolve-library-id` + `mcp__context7__query-docs`** — invoked for Payload (`/payloadcms/payload`) when on the table; recommended for Decap (`decap-cms` via context7 if available, else `WebFetch` decapcms.org/docs); WordPress-specific lookups when WordPress is the stack. Cached docs land in `.website-builder/library/docs/${cms}.md`.
- **WebFetch** — used for Decap docs when context7 lacks coverage; for current Framer CMS feature list at framer.com; for current WordPress REST + theme.json + Gutenberg block schema; for active-fork docs (Sveltia / Static CMS) when the user asks about Decap alternatives.
- **WebSearch** — sparingly. Used for "Payload v3 deploy Vercel build command 2026" or similar very-recent-pattern lookups.
- **Reference-data load** — agent reads per-CMS design docs at `Workstreams/website-builder/cms/DESIGN-cms-*.md` (full reads for the three MVP options) and the migration-recipe section of `Workstreams/website-builder/foundation/DESIGN-project-scaffold.md` for the chosen stack-CMS pairing.
- **Read** — agent reads `.website-builder/project.yaml.stack`, `.transactional`, `.languages`, and `.sitemap.yaml` to anchor the CMS pick in the project's actual shape.

No `Write` / `Edit` on code files in this phase — those tools are gated until phase 18.

## Output artifacts

The agent writes to `.website-builder/project.yaml`:

```yaml
# .website-builder/project.yaml — values added at phase 12
cms: payload                                # none | decap | payload | framer-cms | wordpress-core (MVP) or expansion CMS with logged decision
cms_reasoning: |
  Picked Payload because stack is Next.js (decided phase 11), content has multiple collections
  (Pages + Posts + Authors + Case Studies per phase 9 sitemap), and the team has three editors
  who need role-based access. None / Decap ruled out at this scale.
cms_hosting: vercel-postgres                # only for CMS choices requiring separate hosting (Payload, headless options)
cms_i18n_strategy: pattern-a                # pattern-a (shared structure, translated prose) | pattern-b (per-locale layouts) — when multilingual
```

The agent also seeds `.website-builder/library/docs/${cms}.md` with the cached context7 / WebFetch output for the chosen CMS, and (when the CMS is Payload + Postgres) drafts a phase-29 readiness note in `.website-builder/decisions/cms-12-payload-postgres-host.md` so the deploy phase has the hosting decision pre-staged.

If the user picked an expansion CMS, the agent writes `.website-builder/decisions/cms-expansion-${cms}.md` documenting the choice, the surfaced cost, and the user's explicit acceptance.

## Common failure modes

**"I want the most feature-rich CMS."** Feature-list seduction. The agent's response: *"feature-rich CMS doesn't mean better site; it means more operational footprint for content updates you may not need. Walk me through your actual content updates — what gets edited, how often, by whom?"* Most muggle sites end up at `none` or Decap after this conversation.

**"I want a CMS so I don't have to know code."** Reasonable instinct; the agent surfaces that the CMS choice doesn't eliminate code — it eliminates *content-editing* code-work. The user (or a developer) still writes the components, the schemas, the migrations, the deploys. The CMS handles content updates after launch. The agent reframes: *"the question isn't whether you'll touch code at all; it's whether ongoing content updates touch code. A CMS removes that touch; everything else still gets built."*

**"What about Webflow's CMS?"** Webflow is an expansion stack for the MVP (per phase 11). If the user picked Webflow at phase 11 with explicit acceptance, Webflow's CMS is the natural pairing; the agent surfaces that the expansion-stack support level applies. If the user picked Webflow's CMS without picking Webflow as stack, the agent re-opens phase 11.

**"Can I use [random hosted SaaS CMS]?"** Outside the design surface. The agent surfaces that the workstream supports nine CMSes (the three MVP + the six expansion) plus stack-built-in, and asks the user to pick from those or explicitly accept the cost of an unsupported CMS (no agent support, no recipe, the user owns the integration entirely).

**"I picked Decap but the upstream is in maintenance mode."** Surfaced at decision time. The agent offers three responses: (1) proceed with Decap and accept the maintenance-mode risk (the project still works; bug fixes may not land), (2) switch to a Decap-fork (Sveltia CMS or Static CMS — same config schema, active development), or (3) escalate to a heavier CMS (Payload or Strapi-via-expansion). The user picks; the agent logs.

**"Payload's admin loads slowly on a small site."** True — Payload's admin is a full Next.js app and feels heavy on tiny sites. The agent surfaces that this is the operational cost of schema-as-code with a real admin; for a 5-page brochure, `none` or Decap is the better fit. The user can still keep Payload if the team or the structural-content needs justify it.

**"I forgot to run migrations on deploy."** A real failure mode but caught at phase 29 (hosting deployment), not phase 12. Phase 12 surfaces that Payload migrations are mandatory and writes the build-command convention into the phase-29 readiness note (`pnpm payload migrate && next build` for Vercel). Phase 29 enforces.

**"What's the difference between Sanity and Payload?"** Outside the MVP scope but the agent surfaces it cleanly: Sanity is hosted Content Lake plus GROQ queries plus self-hosted Studio; Payload is self-hosted everything with TypeScript schema. Sanity is the expansion-phase-10 choice; for MVP, Payload is the closest in capability.

**Hidden assumption that CMS picks deploy provider.** Some CMSes (Payload needs Node, Strapi needs Node, Directus needs Node) constrain the deploy story. The agent surfaces these constraints here so phase 28-29 doesn't surprise. The `cms_hosting` field captures the intent; phase 29 actualizes it.

## Reference materials

Per-CMS design docs (full reads for any CMS the user considers seriously):

- `Workstreams/website-builder/cms/DESIGN-cms-none.md` — MVP
- `Workstreams/website-builder/cms/DESIGN-cms-decap.md` — MVP
- `Workstreams/website-builder/cms/DESIGN-cms-payload.md` — MVP
- `Workstreams/website-builder/cms/DESIGN-cms-strapi.md` — expansion phase 10
- `Workstreams/website-builder/cms/DESIGN-cms-sanity.md` — expansion phase 10
- `Workstreams/website-builder/cms/DESIGN-cms-tinacms.md` — expansion phase 10
- `Workstreams/website-builder/cms/DESIGN-cms-directus.md` — expansion phase 10
- `Workstreams/website-builder/cms/DESIGN-cms-keystone.md` — expansion phase 10
- `Workstreams/website-builder/cms/DESIGN-cms-ghost.md` — expansion phase 10

Foundation docs:

- `Workstreams/website-builder/foundation/DESIGN-content-layers.md` § Layer 2 + Layer 3 — the structural-specs layer and the Content Design JSON layer that every CMS choice must accommodate.
- `Workstreams/website-builder/foundation/DESIGN-i18n.md` § Translation workflow + Pattern A/B — the i18n strategy locked at this phase.
- `Workstreams/website-builder/foundation/DESIGN-project-scaffold.md` § Migration recipes — the stack-CMS pairing recipes for Astro+Decap, Next.js+Payload, WordPress+native, Framer+Framer-CMS.

Context7 lookups (mandatory when the relevant CMS is on the table):

- `/payloadcms/payload` — Payload v3 (benchmark 82.1, High reputation, 2279 code snippets, v3.84.0 latest as of 2026-05-18). Topics fetched at phase 12: Collections, Blocks field, localization, access control, drafts/versions, live preview, Next.js installation. Cached to `.website-builder/library/docs/payload.md`.
- Decap CMS — `WebFetch` decapcms.org/docs/ for current config-schema, OAuth backend options, i18n configuration. Active forks: Sveltia CMS (https://github.com/sveltia/sveltia-cms), Static CMS (https://github.com/StaticJsCMS/static-cms). Cached to `.website-builder/library/docs/decap.md`.
- Framer CMS — `WebFetch` framer.com for current built-in CMS capabilities, collection model, Strings collection patterns for i18n.
- WordPress core — `WebFetch` developer.wordpress.org/rest-api for current REST endpoints, theme.json schema, Gutenberg block development.

Freshness date for this contract's references: **2026-05-18** (date of authoring). The agent re-validates current state via context7 at session start when phase 12 is the active phase, and re-fetches if cached `.website-builder/library/docs/${cms}.md` is more than 30 days old.

## Skip authorization

Phase 12 is not skippable. The CMS decision shapes:

- The phase-18 migration recipe (which files get written where, what schemas get authored).
- The phase-22 forms integration (whether forms hit a CMS endpoint, an external service, or a static-host serverless function).
- The phase-24 integrations (the CMS's API affects how analytics / mailing-list / chat integrations attach).
- The phase-29 deploy chain (Payload needs Node + DB; Decap needs OAuth provider; `none` needs only static hosting).

Three narrow legitimate paths around phase 12:

1. **Stack-native CMS auto-pick.** When stack is Framer, `cms: framer-cms` is the default; the agent surfaces it and asks only if the user wants something else. When stack is WordPress, `cms: wordpress-core` is similar. Not a skip; a thin pass with confirmation.
2. **Entry-mode pre-fill from `has-existing-site`.** Phase 6.5 may have detected the CMS from the existing artifact (the user pointed at a WordPress site; phase 11 set stack to `wordpress`; phase 12 sets `cms: wordpress-core` automatically). Phase 12 still runs as a confirmation pass.
3. **Mid-project transactional pivot (decision 34).** If phase 11's transactional flag flips mid-project, the agent may re-run phase 12 to add a transactional-capable CMS pairing if the original choice didn't support commerce. Logged as a phase replay.

Skipping phase 12 entirely is not authorized. If the user requests it, the agent surfaces that without a `cms` value, the agent has no instructions on where to write content at phase 18 and which schemas to author.
