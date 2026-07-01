# CMS adapters — canonical section schema

> Every CMS adapter at `cms-adapters/cms-<name>.md` MUST follow the 12-section schema below. The skills (`wb-architecture` phase 12, `wb-component-build` phase 18, the phase-6.5 re-runnable ingestion, the phase-22 i18n integration) look up sections by exact name at runtime — schema divergence is silent skill failure across the pipeline.
>
> This README is the contract Phase 4 CMS-adapter Captains (`none` / Decap / Payload) build against. Subsequent CMS adapters (Sanity / Strapi / Tina / Storyblok / Contentful / Ghost / Sveltia / Static CMS — Phase 10 expansion) follow the same schema.

## Why exact section names matter

Two load-bearing reasons:

1. **Runtime skill lookups.** When the agent reaches phase 12 (CMS decision), phase 17 (design system), phase 18 (component build), phase 22 (i18n + forms / transactional), phase 24a/b/c (commerce branching), or phase 6.5 (re-runnable ingestion), it reads the active CMS adapter file and locates the relevant section by exact H2 name. A renamed or merged section means the agent reads stale or irrelevant content — degraded behavior the user can't easily diagnose.
2. **Cross-CMS + cross-stack consistency check.** The BUILD-strategy.md Phase 4 DoD (line 201) requires *"pipeline phases 12 + 22 + 24a/b/c work end-to-end with all 3 v1 CMSes."* The `## Content layer mapping` table (§4 below) is the per-CMS verification mechanism — same 5 L-row labels as the stack adapters' equivalent table (`adapters/README.md` §4), one column per CMS — side-by-side comparable across CMSes AND comparable against stack adapters. The cross-CMS × stack compatibility table further down anchors how each CMS pairs with each stack, with verbatim verdicts the agent reads at phase 12.

The schema is also the contract that lets phase-12's CMS decision dialogue stay portable: the agent gives the user a consistent shape per CMS (what is it, when do I pick it, how does authoring feel, what stacks pair with it, what does the content look like in my 5-layer stack, what about i18n, what about ingestion, what about commerce, what are the limits, what does context7 cover, what reference docs back this up).

## The 12 required H2 sections — exact order

Every `cms-adapters/cms-<name>.md` MUST contain all 12 sections below as H2 headings, in this exact order. Renaming or reordering is prohibited. Adding CMS-specific subsections (H3 / H4) within a section is allowed and encouraged. Adding entirely new H2 sections at the end (13, 14, ...) is allowed for CMS-specific concerns the schema doesn't cover (the schema is the floor, not the ceiling).

| # | Section | Purpose |
|---|---|---|
| 1 | `## Mental model` | What the CMS IS — the user's mental shape. **First paragraph or `### Identity` H3 encodes CMS name + version baseline + canonical context7 ID + freshness-check requirement.** Anchor for the user's intuition + the agent's phase-12 explanation. |
| 2 | `## When to pick this CMS` | Decision criteria for phase 12 — when this CMS fits, when it doesn't. Two H3 subsections: "Pick X when" + "Don't pick X when". The phase-12 dialogue reads this verbatim to drive the recommend-or-deflect decision. |
| 3 | `## Auth + setup` | Credentials, env vars, OAuth flows, account / instance setup, local-dev install, MCP/tooling. Where relevant, `### CRUD vocabulary` H3 subsection translates content / collection / item / publish verbs into the CMS's native API surface (per S1 — for `cms-none`, this translates to filesystem + git ops). |
| 4 | `## Authoring patterns` | Canonical content-authoring patterns + common pitfalls for muggles. H3 subsections per pattern (e.g., `### Pattern: Folder collection for a blog`, `### Pattern: File collection for site settings`, `### Pattern: Blocks-via-list-types`, `### Common pitfalls`). The phase-12 + phase-18 skills consume this when generating CMS config / collections / blocks. |
| 5 | `## Stack pairings` | Phase 12 cross-CMS × stack matrix from the CMS's perspective — which stacks pair well/poorly with this CMS, defaults, per-pairing recipes. The agent reads this to validate phase-11's stack choice is compatible. |
| 6 | `## Content layer mapping` | **REQUIRED table** — 5 row labels in exact order: `L1 brand.yaml.tokens`, `L2 sitemap.yaml + sections.yaml`, `L3 strings/{lang}.json`, `L4 content/pages/*.md`, `L5 briefs/{component}.json`. One column "CMS native concept" filled in per CMS. Cross-CMS verification anchor + cross-anchor consistency with `adapters/README.md` §4 (same 5 L-row labels). |
| 7 | `## i18n integration` | Per-CMS i18n model + cross-references to `i18n/strings-schema.md` + `i18n/language-switcher.md` + `i18n/hreflang.md`. Per-language storage + per-locale fallback + translation handoff patterns (decisions 38-41 i18n defaults). |
| 8 | `## Phase 6.5 ingestion` | Per-CMS extraction + normalization recipe for the 5 entry modes (greenfield / has-AI-output / has-existing-site / has-Figma-file / mid-project / JSON-handoff-round-trip). Conflict-resolution per decision 36 (halt + force user decision). |
| 9 | `## Commerce integration (if transactional=true)` | Phase 24a/b/c branching from the CMS's perspective. Some CMSes natively support commerce (Payload via Stripe collections / WooCommerce-on-WordPress); some pair with external commerce (`none` / Decap delegate to stack + commerce adapter). The conditional clause `(if transactional=true)` is part of the H2 heading verbatim, matching the stack-adapter convention. |
| 10 | `## Limitations + escape hatches` | What this CMS CAN'T do (surfaced at phase 12 for user override). Limitation column + escape-hatch column. **For `cms-decap` this section MUST prominently disclose the maintenance-mode status + name active forks per S2.** |
| 11 | `## context7 lookups for this CMS` | Per Lock-3 freshness pattern — canonical context7 IDs the agent invokes at phases 12 / 17 / 18 / 22 / 24a / 28, plus WebFetch fallback URLs when context7 coverage is thin. |
| 12 | `## References` | Foundation design-doc paths (vault-root-relative per `vault-workstreams.md` link standard) + per-CMS external references (official docs, API references, community resources, source design doc). |

### What's NOT an H2 (deliberately)

The following are required content but live as H3 subsections within other H2s — the runtime skills don't need them as top-level lookups, and the existing design docs treat them as subsections:

- **CRUD vocabulary** — H3 inside `## Auth + setup` when the CMS's content-mutation surface needs explicit translation (e.g. `cms-none`: "create page" = `vim content/pages/about.md; git add; git commit; git push`; `cms-decap`: editor opens admin → form → save → Decap commits; `cms-payload`: `payload.create({collection, data})` or admin UI form)
- **Identity** — first paragraph (or H3) inside `## Mental model`, encoding CMS name + version + canonical context7 ID + freshness-check requirement
- **Common pitfalls** — H3 inside `## Authoring patterns`, when notable pitfall paths deserve a dedicated enumeration

## Per-section content guidance

What each section is for + what design-doc anchors it derives from. Captains author per their CMS's specifics; this section establishes the floor.

### `## Mental model`

What the CMS IS — the user's mental shape. The agent uses this at phase 12 to explain the CMS to the user in their own terms. The first paragraph (or an explicit `### Identity` H3) encodes:

- CMS name + version baseline (e.g. "Decap CMS (formerly Netlify CMS), v3.x", "Payload CMS v3", "file-based — no CMS, just `git` + a code editor")
- Canonical context7 library ID (e.g. `/payloadcms/payload`, `/decaporg/decap-cms`)
- Freshness-check requirement note: *"agent invokes context7 at phase 12 / 17 / 18 / 22 to confirm current surface — this CMS evolves; training data is stale"*

The body of `## Mental model` is the narrative — the core primitives (Collections / Globals / Fields for Payload; Collections / Fields / git-workflow for Decap; "files are the database" for none), what each one does, what makes this CMS distinct from peers.

### `## When to pick this CMS`

The decision criteria for phase 12. Two H3 subsections — "Pick X when" (positive criteria, 5-8 bullets) + "Don't pick X when" (anti-criteria, 4-6 bullets). The phase-12 dialogue reads this verbatim and surfaces the criteria to the user as the recommend-or-deflect rationale.

**This REPLACES the stack-adapter's `## Migration recipe`** — CMS adapters don't have a single canonical "pre-step-12 → this CMS" migration; they have selection criteria (does this fit, or not?). The migration shape is per-stack-pairing and lives in `## Stack pairings` per-pairing recipes (§5).

For the strongest signal, follow the design docs' rubric: name the kinds of project shapes that fit (volume, editor count, edit cadence, content shape, hosting constraints, user comfort with code/admin) and the kinds that don't.

### `## Auth + setup`

Account / instance creation flow, API key management (via `secrets-conventions.md` from 1Password — never hardcoded), env var names, OAuth provider config (for Decap: GitHub OAuth App + Git Gateway alternatives; for Payload: database choice + Payload's built-in admin auth), local-dev install commands, MCP/tooling integration, project bootstrap procedure.

If the CMS has a notable CRUD vocabulary that translates non-obviously into native API verbs, document as `### CRUD vocabulary` H3 subsection. This is mandatory for `cms-none` (where "publish a page" = "commit + push a markdown file") per S1.

**For Payload (S4):** `## Auth + setup` MUST surface the three-way database / hosting decision as an explicit Phase 12 prompt — Payload Cloud (managed; simplest) vs Vercel Postgres (Vercel-bundled; ~$20/mo) vs Neon (best free tier) — with cost / DX / data-residency trade-offs. Derived from `DESIGN-cms-payload.md` lines 564-569.

### `## Authoring patterns`

Canonical content-authoring patterns + common pitfalls. H3 subsections per pattern (e.g., `### Pattern: Folder collection`, `### Pattern: File collection`, `### Pattern: Blocks-via-list-types` for Decap; `### Pattern: Pages collection with Blocks field`, `### Pattern: Globals for site settings`, `### Pattern: Relationships across collections`, `### Pattern: Versioned drafts with live preview`, `### Pattern: Hooks for side effects` for Payload; per-stack content-directory layouts for `none`).

The phase-12 + phase-18 skills consume this when generating CMS config / collections / blocks. Patterns SHOULD include short code blocks (YAML / TypeScript / Markdown frontmatter) that the agent uses as a starter — verbatim from the design doc when possible.

`### Common pitfalls` is a required H3 subsection inside `## Authoring patterns`. It enumerates muggle-level gotchas (smart quotes, schema drift, forgotten OAuth setup, image-path mismatches, etc.). The phase-12 dialogue surfaces these as caveats before lock-in.

### `## Stack pairings`

Phase 12 cross-CMS × stack pairings from this CMS's perspective. Required content:

- **Table** — one row per phase-11 stack choice (Framer / Next.js / WordPress / Astro / Hugo / SvelteKit / Webflow / Plain static HTML), columns: stack + fit verdict + notes
- **Verbatim verdicts** — use the canonical verdict words: `Native` (CMS is designed for this stack OR vice versa) / `Possible` (works but requires non-default config) / `Awkward` (works but fights the design) / `Anti-fit` (technically possible but not recommended) / `N/A` (incompatible — usually because the stack has its own CMS)
- **Per-pairing recipes** — when the pairing is `Native` or `Possible`, embed a short recipe (file layout + bootstrap commands + minimum config) as an H3 subsection (e.g., `### Per-pairing recipe — Astro + Decap`)

**For Payload (S3):** `## Stack pairings` MUST capture the "two-deploy headless mode" path for Payload + Astro / SvelteKit (per `DESIGN-cms-payload.md` lines 379-388), not just the native Next.js path. The headless-mode recipe is materially different from the native-Next.js recipe and the phase-12 dialogue branches on it.

This per-CMS table feeds into the **cross-CMS × stack compatibility table** below (§ "Cross-CMS × stack compatibility anchor") — the anchor table that Captains I/J/K all reference and the phase-12 skill grep-loads to pick the per-cell verdict word.

### `## Content layer mapping`

**Mandatory table.** Same 5-row contract as the stack-adapter equivalent (`adapters/README.md` §4) — IDENTICAL row labels in exact order, one column per CMS:

| Layer | CMS native concept |
|---|---|
| L1 brand.yaml.tokens | (per CMS — e.g. `none`: stays in `src/styles/tokens.css`; Decap: optionally a `BrandTokens` file collection; Payload: `BrandTokens` global) |
| L2 sitemap.yaml + sections.yaml | (per CMS — e.g. `none`: markdown files + Zod schema; Decap: folder collection + list/types blocks; Payload: `Pages` collection + `blocks[]` field) |
| L3 strings/{lang}.json | (per CMS — e.g. `none`: per-language JSON files in `src/content/strings/`; Decap: file collection per language; Payload: optional Strings global with localized fields OR keep CDJSON in-repo) |
| L4 content/pages/*.md | (per CMS — e.g. `none`: markdown files with frontmatter; Decap: folder-collection items with markdown widget; Payload: `richText` field on Page or RichText Block, using Lexical) |
| L5 briefs/{component}.json | (per CMS — usually "out of band; briefs live in `.website-builder/briefs/`; CMS doesn't see them" — same for all CMSes per `DESIGN-content-layers.md`) |

**Cross-anchor consistency rule.** The row labels MUST be identical across `adapters/README.md` §4 (stack), `cms-adapters/README.md` §4 (this one), and `commerce-adapters/README.md` §4 (commerce + booking, often resolving to "n/a / handled via stack" but still mandatory). This is what makes side-by-side L1-L5 cross-adapter verification work across stack + CMS + commerce simultaneously.

### `## i18n integration`

Per-CMS i18n model. Required content:

- **Configuration mechanism** — how this CMS configures locales (Payload: `localization.locales[]` config + `localized: true` flag per field; Decap: `i18n: true` on collection + structure choice; `none`: per-language file naming OR per-language folders)
- **Per-locale storage** — where translations live (Payload: localized JSON columns OR per-locale entries; Decap: `multiple_files` vs `multiple_folders` per Decision 39; `none`: filename convention or folder convention)
- **The blocks-localization decision** — for CMSes that have a blocks-style primitive (Payload, Decap-via-list/types): document whether to localize the layout array (per-locale layouts) OR the text fields inside blocks (shared layout, translated text) — Decision 39 Pattern A default = approach 2 (shared layout)
- **Pattern 1 (inline translate at phase 16) vs Pattern 2 (translator handoff) vs Pattern 3 (user-driven external)** — defaults per locked decision 40
- **String-missing fallback** — what happens when a target-locale string is empty (Decision 41 — fall back to default-locale; render-time + warning)

Then cross-references the shared anchors for deep specifics:

- `i18n/strings-schema.md` (stack-agnostic CDJSON contract)
- `i18n/language-switcher.md` (cross-cuts CMS + stack; switcher implementation per-stack)
- `i18n/hreflang.md` (cross-cuts CMS + stack; hreflang emission per-stack)
- `i18n/rtl.md` (CMS-agnostic; CSS logical properties + `dir="rtl"` discipline)

The H2 summary is short; the deep per-stack content lives in the shared files' per-stack sections.

### `## Phase 6.5 ingestion`

**Required H2** (per the locked schema — same status as the stack-adapter equivalent). Phase 6.5 is re-runnable at any project lifecycle point — the agent looks up this section often, not just at entry-mode setup. For CMS adapters, phase 6.5 ingestion concerns include:

- **Per-entry-mode extraction → CMS-native primitive recipes** (e.g., `has-AI-output` mode → AI-output parser extracts Block-shape JSON → for Payload: agent writes new `blocks/NewBlock.ts` + adds to `Pages.layout.blocks` array; for Decap: agent appends new entry to `config.yml`'s `types` list; for `none`: agent creates a new markdown file)
- **Stack-specific gotchas during normalization** (Payload + Postgres migration handling; Decap + repo-scope OAuth limitations; `none` + frontmatter-schema-drift)
- **Conflict resolution per Decision 36** — halt + force user decision when ingested content conflicts with existing
- **JSON handoff round-trip output paths** — where the v0/Cursor round-trip output lands (per-CMS recipe; same handoff-spec contract; CMS-shaped destination)

### `## Commerce integration (if transactional=true)`

Phase 24a (commerce platform setup) + 24b (payment provider wiring) + 24c (commerce-specific legal) branching from this CMS's perspective. Required content:

- **Whether this CMS natively supports commerce** — Payload natively via Stripe app + custom collections; WordPress natively via WooCommerce (out-of-scope for Phase 4 — that's WooCommerce-on-stack-wordpress); Decap + `none` delegate to stack-adapter commerce surface
- **External-commerce pairing model** — when the CMS doesn't natively handle commerce, the commerce adapter (`commerce-stripe.md` / `booking-calcom.md`) sits next to the CMS and writes into the stack's commerce-config path; the CMS adapter's role is to document HOW the external commerce surfaces in CMS-authoring (e.g., Decap can have a `Products` folder collection that gets ingested into Stripe via a custom build step)
- **Phase 22 transactional mid-flip** — Decision 34 (transactional flag changes mid-project) — per-CMS recipe for picking up commerce after the CMS is already wired

The `(if transactional=true)` conditional in the H2 is verbatim per design-doc convention — phase 11's transactional sibling decision (or Decision 34's mid-flip) gates whether this section is consumed.

### `## Limitations + escape hatches`

What this CMS CAN'T do (surfaced at phase 12 for user override). Required content:

- **Hard limitations** — the CMS's structural constraints (e.g., Decap = git-only; no API for content; Payload = Node-runtime; static-only hosts can't run admin; `none` = code-editor required; no admin UI)
- **Soft limitations** — where the CMS is awkward but workable (e.g., Decap = slow saves; one git commit per save; Payload = schema-in-code requires TypeScript literacy somewhere)
- **Escape hatches per limitation** — per Decision 34 (transactional mid-flip pattern), per-CMS escape: "if user later wants X that this CMS can't do, route to phase 12 restart, pick CMS Y, run migration"

**For `cms-decap` (S2):** this section MUST prominently disclose Decap is in maintenance mode (per `DESIGN-cms-decap.md` line 403) AND name the active forks: **Sveltia CMS** (https://github.com/sveltia/sveltia-cms) + **Static CMS** (https://github.com/StaticJsCMS/static-cms). The disclosure must be a top-level row in the limitations table (not a buried bullet) — phase-12 dialogue reads this verbatim to warn the user.

### `## context7 lookups for this CMS`

Per Lock-3 freshness pattern — explicit list of context7 IDs the agent invokes at each phase + WebFetch fallback URLs when context7 coverage is thin. Required content (table form, per phase):

- Phase 12 (CMS decision): canonical context7 ID + question template
- Phase 17 (design system): per-CMS BrandTokens-style implementation
- Phase 18 (component build): per-CMS Block / Collection / Field config reference
- Phase 22 (forms / i18n / transactional): per-CMS forms + per-CMS i18n config
- Phase 24a-c (commerce, if transactional): per-CMS commerce integration docs
- Phase 28 (deploy): per-CMS deploy + admin-hosting + DB-migration

Plus a "cache to" line — `.website-builder/library/docs/<cms>-*.md` is the cache home; re-fetch threshold 30 days per locked Lock-3 freshness norm.

### `## References`

Foundation design-doc paths (vault-root-relative per `vault-workstreams.md` link standard) + per-CMS external references (official docs, API references, community resources, GitHub repos, active forks). Conventional last section per design-doc shape.

## Cross-CMS × stack compatibility anchor

The phase-12 skill reads this single table to surface CMS-stack pairings to the user. Each cell uses one of the canonical verdict words: **Native / Possible / Awkward / Anti-fit / N/A**. Captains I/J/K populate their own CMS's `## Stack pairings` section per-CMS — they MUST reference this table verbatim for their column's cell verdicts and per-stack notes, so the cross-CMS pairing matrix and the per-CMS pairing tables stay in sync.

| CMS \ Stack | Framer | Next.js + shadcn | WordPress | Astro | Hugo | SvelteKit | Webflow | Plain static HTML |
|---|---|---|---|---|---|---|---|---|
| **`cms-none` (file-based markdown)** | N/A | Possible (static export, MDX + `gray-matter`) | N/A | **Native** (default; Astro Content Collections + Zod) | **Native** (Hugo content/) | Possible (`mdsvex`) | N/A | Possible (build script: Pandoc / custom Node) |
| **Decap CMS** | N/A | Possible (static export, MDX in `content/`) | N/A | **Native** (default for Astro + a CMS) | **Native** (`static/admin/`) | Possible (`adapter-static`) | N/A | Awkward (Decap commits markdown; plain HTML doesn't render markdown without a generator) |
| **Payload CMS** | N/A — Framer has its own CMS | **Native** (Payload v3 IS a Next.js app) | N/A — WordPress has WP core | Possible (headless mode; two-deploy: Payload as separate Next.js + Astro fetches REST/GraphQL) | Anti-fit (Hugo is build-time + file-based; pairing fights both designs) | Possible (headless mode; two-deploy) | N/A — Webflow has its own CMS | N/A |

### Verdict-word semantics (locked)

- **Native** — the CMS is designed for this stack, OR the stack is designed to consume this CMS. Default recommendation when both are picked.
- **Possible** — the CMS works on this stack but requires non-default config (e.g., Decap + Next.js requires `next export`; Payload + Astro requires two-deploy headless mode). Surface the trade-off at phase 12.
- **Awkward** — the CMS works but fights the stack's design (e.g., Decap + Plain static HTML — Decap commits markdown, but plain HTML doesn't render markdown without a generator; user must add a build step). Phase 12 should challenge the choice.
- **Anti-fit** — technically possible but not recommended (e.g., Payload + Hugo — defeats both designs' simplicity). Phase 12 actively deflects.
- **N/A** — incompatible, usually because the stack has its own first-party CMS (Framer CMS, WordPress core, Webflow CMS) and pairing with a different CMS makes no sense.

**Verbatim populated cells per the design docs:**

- `cms-none` row from `DESIGN-cms-none.md` § "Stack pairings" lines 293-306
- `cms-decap` row from `DESIGN-cms-decap.md` § "Stack pairings" lines 213-224 — Decap + Next.js (static export) verdict per line 220 is "Possible"
- `cms-payload` row from `DESIGN-cms-payload.md` § "Stack pairings" lines 322-333 — Payload + Framer / WordPress / Plain static HTML verdict per line 329 is "N/A — those have their own CMSes"

## Per-Captain write zones for Phase 4 CMS work

Each Phase 4 CMS Captain has an exclusive write zone. Stay inside it; everything else is read-only.

| Captain | CMS | Write paths (exclusive) |
|---|---|---|
| **Captain I** | `none` (file-based) | `cms-adapters/cms-none.md` (full file) + `tests/cms-adapters/none/` (full subdirectory: `fixture/`, `expected.yaml`, `README.md`) |
| **Captain J** | Decap | `cms-adapters/cms-decap.md` (full file) + `tests/cms-adapters/decap/` (full subdirectory) |
| **Captain K** | Payload | `cms-adapters/cms-payload.md` (full file) + `tests/cms-adapters/payload/` (full subdirectory) |

### READ-ONLY for all Phase 4 CMS Captains

The following files are shared substrate authored in Phase 4 Captain 0 prep. **Do NOT modify** during Phase 4 Captain work — modifications surface as architectural concerns requiring General review:

- `cms-adapters/README.md` (this file — the schema contract)
- `commerce-adapters/README.md` (commerce + booking schema contract — referenced by CMS adapters' §9 `## Commerce integration (if transactional=true)` for delegation patterns)
- `commerce-adapters/payment-config-schema.md` (canonical `payment-config.yaml` schema — referenced by CMS adapters' §9 when describing commerce-pairing TWINT)
- `tests/cms-adapters/README.md` (test fixture convention for CMS adapters)
- `tests/commerce-adapters/README.md` (test fixture convention for commerce/booking adapters)
- `adapters/README.md` + `adapters/stack-*.md` (Phase 3 stack adapters — referenced by CMS adapters' §5 `## Stack pairings`)
- `i18n/strings-schema.md`, `i18n/rtl.md`, `i18n/language-switcher.md`, `i18n/hreflang.md` (Phase 3 i18n substrate)
- `handoff-spec/component-request-v1.md`, `handoff-spec/component-output-v1.md` (Phase 3 handoff contracts)

CMS adapter files may *reference* (cross-link to) any of these read-only anchors; they may not edit them.

### Worktree discipline (Decision 65 forward-doctrine)

Per Decision 65 (worktree isolation) and forward-doctrine baked at Phase 3 cohesion: each Phase 4 Captain uses a per-callsign git worktree under `Projects/Jules.Solutions/Subprojects/website-builder.captain-{i,j,k,l}/` to avoid filesystem collisions on the read-only shared substrate. Worktree pattern per `git-and-deploy.md`. **No-push-from-Captain rule** — Captains commit on their per-callsign branch (`phase-4-captain-{i,j,k,l}`) inside their worktree; General does sequential merges + single push at end of Phase 4 wave (matching Phase 3 final commit `6935643` pattern).

## S-risk callouts — bake into Captain prompts

The pre-dispatch researcher identified 4 S-risks (Captain-specific surprises) that must be explicitly surfaced in the Captain prompts so they're not buried inside design-doc reading:

### S1 — Captain I (`cms-none`): CRUD vocabulary for filesystem + git

`cms-adapters/cms-none.md` § "Auth + setup" MUST include an `### CRUD vocabulary` H3 subsection. For `cms-none` the CRUD verbs translate non-obviously:

- "Create a page" = "create `src/content/pages/{slug}.md`; `git add; git commit; git push`"
- "Edit a page" = "open `{slug}.md` in editor; save; `git commit; git push`"
- "Publish a page" = "merge to `main` branch; CI/CD picks up the next build"
- "Unpublish a page" = "delete the file OR set `draft: true` in frontmatter; commit; push"
- "Schedule publish" = "merge to a `scheduled` branch with date frontmatter; CI cron deploys on date"
- "View revisions" = "`git log {slug}.md`"

The phase-12 skill needs this CRUD-vocabulary explicitly written so the dialogue can teach muggles what authoring feels like on `cms-none`. Without it, the dialogue defaults to "edit the file" which under-specifies the commit-and-push step.

**Source anchor:** `DESIGN-cms-none.md` § "Mental model" lines 44-58 (the editing-flow narrative — convert verbatim into CRUD verb mappings).

### S2 — Captain J (`cms-decap`): Maintenance mode disclosure + active forks

`cms-adapters/cms-decap.md` § "Limitations + escape hatches" MUST disclose Decap's maintenance-mode status as a top-level limitation row (not a buried bullet). Per `DESIGN-cms-decap.md` line 403: *"Decap is in maintenance mode (since the Netlify-Decap rename). Active forks exist (Sveltia CMS, Static CMS). The agent surfaces this at phase 12 — Decap still works but the user should know the project's velocity."*

The disclosure must:

- Name the maintenance-mode status explicitly
- Name **Sveltia CMS** (https://github.com/sveltia/sveltia-cms) as an active fork
- Name **Static CMS** (https://github.com/StaticJsCMS/static-cms) as an active fork
- Surface the upgrade path: "if user wants active velocity, point them at Sveltia or Static CMS — drop-in replacements with the same config format"
- Be in the limitations table verbatim so phase-12's dialogue can read it directly

### S3 — Captain K (`cms-payload`): Two-deploy headless mode

`cms-adapters/cms-payload.md` § "Stack pairings" MUST capture the "two-deploy headless mode" path for Payload + Astro / SvelteKit, NOT just the native Next.js path. Per `DESIGN-cms-payload.md` lines 379-388: *"Payload runs as a separate Next.js app (or Express v2); Astro consumes `/api/...` REST or GraphQL. Works but you maintain two deploys."*

The Stack pairings table row for Astro / SvelteKit must:

- Verdict word: `Possible` (NOT `Native` — that's reserved for Next.js)
- Note: "Two-deploy headless mode: Payload runs as a standalone Next.js app exposing REST/GraphQL; the user's Astro/SvelteKit frontend consumes `/api/...`"
- Per-pairing recipe sketch: minimum env vars (`PAYLOAD_URL`, `PAYLOAD_API_KEY`) + sample fetch (e.g., `await fetch(`${PAYLOAD_URL}/api/pages?where[slug][equals]=${slug}&depth=2&locale=${locale}`, {headers: {Authorization: `Bearer ${PAYLOAD_API_KEY}`}})`)
- Trade-off callout: two deploys to maintain, two CI/CD pipelines, two URLs to monitor — phase 12 surfaces the cost

### S4 — Captain K (`cms-payload`): Database / hosting decision

`cms-adapters/cms-payload.md` § "Auth + setup" MUST surface the three-way decision as an explicit Phase 12 prompt (not buried in pitfalls):

- **Payload Cloud** — managed; simplest; subscription pricing (~$25/user/mo at time of writing; verify via context7 at phase 12)
- **Vercel Postgres** — Vercel-bundled; ~$20/mo + Vercel's standard pricing; tight Vercel integration; easy if user is already deploying frontend to Vercel
- **Neon** — best free tier (~3GB; suitable for muggle-scale sites); standalone Postgres; works with any Node host

Per `DESIGN-cms-payload.md` lines 564-569: *"Default for muggle marketing sites: Postgres via Vercel Postgres or Neon."* The CMS adapter must make this decision explicit at phase 12 rather than defaulting silently.

The H3 subsection inside `## Auth + setup` should:

- Be titled `### Database + hosting choice (Phase 12 decision)`
- Surface all three options with cost / DX / data-residency trade-offs
- Recommend a default (Vercel Postgres for users already on Vercel; Neon for cost-conscious; Payload Cloud for managed-everything)
- Note the migration cost between options (Postgres-to-Postgres is straightforward; switching to/from Mongo is not — agent flags this for future flexibility)

## See also

- `BUILD-strategy.md` Phase 4 — DoD + dispatch model (lines 187-209)
- `DESIGN-cms-none.md` — Captain I's primary design-doc source
- `DESIGN-cms-decap.md` — Captain J's primary design-doc source
- `DESIGN-cms-payload.md` — Captain K's primary design-doc source
- `DESIGN-architecture.md` — plugin directory layout (`cms-adapters/` per line 115)
- `DESIGN-content-layers.md` — the 5 content layers the §6 table maps
- `DESIGN-i18n.md` — i18n model + per-CMS hooks
- `DESIGN-phase-contracts.md` — phase 12 (CMS decision) + phase 22 (forms / transactional) + phase 24a/b/c (commerce branching)
- `DESIGN-ingestion-and-extraction.md` — phase 6.5 mechanism
- `adapters/README.md` — stack adapter contract (Phase 3 prep); the `## Content layer mapping` row labels MUST match
- `commerce-adapters/README.md` — commerce + booking adapter contract (sibling Phase 4 prep)
- `commerce-adapters/payment-config-schema.md` — canonical `payment-config.yaml` schema for TWINT-via-Stripe-on-CHF Swiss-market constraint
- `tests/cms-adapters/README.md` — per-CMS-adapter test fixture convention
- `skills/wb-architecture/SKILL.md` — phase 12 consumer of CMS adapter files
- `skills/wb-component-build/SKILL.md` — phase 18 consumer of CMS adapter files
- Phase 10+ (later) — CMS expansion: Sanity, Strapi, Tina, Storyblok, Contentful, Ghost, Sveltia CMS, Static CMS — all follow this same 12-section schema
