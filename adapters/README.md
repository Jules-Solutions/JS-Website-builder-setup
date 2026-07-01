# Adapters — canonical section schema

> Every stack adapter at `adapters/stack-<name>.md` MUST follow the 14-section schema below. The skills (`wb-architecture` phase 11, `wb-component-build` phase 18, the phase-6.5 re-runnable ingestion) look up sections by exact name at runtime — schema divergence is silent skill failure across the pipeline.
>
> This README is the contract Phase 3 stack-adapter Captains (Framer / Next.js+shadcn / WordPress) build against. Subsequent stack adapters (Astro / Hugo / SvelteKit / Webflow / static-html, all post-MVP expansion) follow the same schema.

## Why exact section names matter

Two load-bearing reasons:

1. **Runtime skill lookups.** When the agent reaches phase 11 (stack decision), phase 17 (design system), phase 18 (component build), phase 24a/b/c (commerce branching), phase 26 (SEO), phase 28-30 (deploy), or phase 6.5 (re-runnable ingestion), it reads the active stack's adapter file and locates the relevant section by exact H2 name. A renamed or merged section means the agent reads stale or irrelevant content — degraded behavior the user can't easily diagnose.
2. **Cross-stack consistency check.** The BUILD-strategy.md Phase 3 DoD (line 181) requires *"same `.website-builder/` content produces equivalent sites on all 3 stacks (modulo platform-specific limitations)."* The `## Content layer mapping` table (§4 below) is the verification mechanism — same row labels in every adapter, one column per stack, side-by-side comparable.

The schema is also the contract that lets the JSON handoff protocol be portable: `component-request-v1` briefs cross stacks by swapping only `output_format`. That portability rests on every adapter speaking the same vocabulary for what its stack does at each layer.

## The 14 required H2 sections — exact order

Every `adapters/stack-<name>.md` MUST contain all 14 sections below as H2 headings, in this exact order. Renaming or reordering is prohibited. Adding stack-specific subsections (H3 / H4) within a section is allowed and encouraged. Adding entirely new H2 sections at the end (15, 16, ...) is allowed for stack-specific concerns the schema doesn't cover (the schema is the floor, not the ceiling).

| # | Section | Purpose |
|---|---|---|
| 1 | `## Mental model` | What the stack IS — the user's mental shape. **First paragraph or `### Identity` H3 encodes stack name + version + canonical context7 ID + freshness-check requirement.** Anchor for the user's intuition + the agent's phase-11 explanation. |
| 2 | `## Auth + setup` | Credentials, env vars, project bootstrap, local-dev install, MCP/tooling. Where relevant, `### CRUD vocabulary` H3 subsection translates project/page/asset/publish verbs into the stack's native API surface. |
| 3 | `## Migration recipe` | Pre-step-11 canonical `.website-builder/` → this stack. Per-layer mapping (deeper than the §4 table — narrative + recipes + edge cases). |
| 4 | `## Content layer mapping` | **REQUIRED table** — 5 row labels in exact order: `L1 brand.yaml.tokens`, `L2 sitemap.yaml + sections.yaml`, `L3 strings/{lang}.json`, `L4 content/pages/*.md`, `L5 briefs/{component}.json`. One column "Stack native concept" filled in per stack. Cross-stack verification anchor. |
| 5 | `## i18n integration` | Stack-level summary of i18n approach + cross-references to `i18n/language-switcher.md#<stack-slug>` + `i18n/hreflang.md#<stack-slug>` for deep per-stack specifics. |
| 6 | `## Phase 6.5 ingestion` | Extraction tools used for this stack (cross-references `extraction/*.md`) + normalization output paths into `.website-builder/` + auth-walled / dynamic-state handling per stack. |
| 7 | `## Commerce integration (if transactional=true)` | Phase 24a/b/c branching per phase contracts. The conditional clause `(if transactional=true)` is part of the H2 heading verbatim. |
| 8 | `## CMS pairing` | Phase 12 CMS decision — which CMSes pair well/poorly with this stack, defaults, escape hatches. |
| 9 | `## Component library pairing` | Phase 18 component-build pairings. Cross-references `skills/wb-component-build/references/per-stack-codegen.md#<stack-slug>` (the read-only anchor authored in Phase 2.B). |
| 10 | `## Deploy` | Canonical deploy target + DNS pattern + SSL story + analytics injection + performance budget. |
| 11 | `## Post-launch maintenance pattern` | Per locked decision 37 (launch-once phases 31-34 vs ongoing post-launch maintainer template). Adapter-specific — what the user's ongoing maintenance loop looks like on this stack. |
| 12 | `## Limitations + escape hatches` | What this stack CAN'T do (surfaced at phase 11 for user override). Where relevant, `### Failure modes` H3 subsection enumerates common errors + recovery paths. |
| 13 | `## context7 lookups for this stack` | Per Lock-3 freshness pattern — canonical context7 IDs the agent invokes at phases 11/17/18/22/24a/28-30, plus WebFetch fallback URLs when context7 coverage is thin. |
| 14 | `## References` | Foundation design-doc paths + per-stack external references (official docs, API references, community resources). |

### What's NOT an H2 (deliberately)

The following are required content but live as H3 subsections within other H2s — the runtime skills don't need them as top-level lookups, and the existing design docs treat them as subsections:

- **CRUD vocabulary** — H3 inside `## Auth + setup` when a stack's CRUD surface needs explicit translation
- **Identity** — first paragraph (or H3) inside `## Mental model`, encoding stack name + version + canonical context7 ID + freshness-check requirement
- **Failure modes** — H3 inside `## Limitations + escape hatches`, when notable failure paths deserve a dedicated enumeration

## Per-section content guidance

What each section is for + what design-doc anchors it derives from. Captains author per their stack's specifics; this section establishes the floor.

### `## Mental model`

What the stack IS — the user's mental shape. The agent uses this at phase 11 to explain the stack to the user in their own terms. The first paragraph (or an explicit `### Identity` H3) encodes:

- Stack name + version baseline (e.g. "Framer", "Next.js 15 App Router", "WordPress 6.8")
- Canonical context7 library ID (e.g. `/vercel/next.js`)
- Freshness-check requirement note: *"agent invokes context7 at phase 11 / 17 / 18 / 28 to confirm current surface — this stack evolves; training data is stale"*

The body of `## Mental model` is the narrative — what the stack does well, what its trade-offs are, the muggle-level explanation of "what does using this stack feel like."

### `## Auth + setup`

Account creation flow, API token / API key management (via `secrets-conventions.md` from 1Password — never hardcoded), env var names, local-dev install commands, MCP/tooling integration, project bootstrap procedure. If the stack has a notable CRUD vocabulary (project create / page create / asset upload / publish / unpublish translates non-obviously into the stack's native verbs), document as `### CRUD vocabulary` H3 subsection.

### `## Migration recipe`

Pre-step-11 canonical `.website-builder/` content → this stack. Narrative + per-file/per-layer recipes + edge cases. The deep version of the §4 table. Anchor: existing design docs' `## Migration recipe` sections (lines vary per stack doc — Framer §"Migration recipe (pre-step-11 canonical → Framer)" lines 55-95).

### `## Content layer mapping`

**Mandatory table.** Five rows, two columns, exact labels:

| Layer | Stack native concept |
|---|---|
| L1 brand.yaml.tokens | (per stack — e.g. Framer Color/Text Styles via Server API; Next.js CSS variables in `globals.css` + Tailwind config; WordPress `theme.json` color/typography presets) |
| L2 sitemap.yaml + sections.yaml | (per stack — e.g. Framer Frames + Custom Components; Next.js App Router `app/[lang]/.../page.tsx`; WordPress Pages + Patterns/Blocks) |
| L3 strings/{lang}.json | (per stack — e.g. Framer CMS "Strings" collection; Next.js `messages/{lang}.json` via next-intl; WordPress Polylang/WPML strings + theme `lang/*.po`) |
| L4 content/pages/*.md | (per stack — e.g. Framer Frame composition; Next.js MDX or `generateStaticParams()` per locale; WordPress Pages content) |
| L5 briefs/{component}.json | (per stack — e.g. Framer `code/{Component}.tsx`; Next.js `components/{Component}.tsx`; WordPress block patterns or theme template parts) |

The table is the verification mechanism for the BUILD-strategy.md DoD: side-by-side comparison across all three Phase 3 stacks proves "same `.website-builder/` content produces equivalent sites on all 3 stacks." This is also the table downstream agents (CMS-adapter Captains in Phase 4; CMS-stack pairings) grep for when wiring across stack + CMS combinations.

### `## i18n integration`

Stack-level summary of i18n approach:

- Recommended library (`next-intl` for Next.js; Polylang/WPML for WP; Framer built-in localization)
- Routing-strategy defaults (per `project.yaml.language_routing` — prefix/subdomain/tld; defaults per locked decision 38)
- Per-language pages pattern (Pattern A shared structure vs Pattern B per-locale-content; default Pattern A per locked decision 39)
- Pattern 1 (inline translate at phase 16) vs Pattern 2 (translator handoff) vs Pattern 3 (user-driven external) — defaults per locked decision 40

Then cross-references the shared anchors for deep specifics:

- `i18n/language-switcher.md#<stack-slug>` — switcher component implementation
- `i18n/hreflang.md#<stack-slug>` — hreflang emission mechanism
- `i18n/rtl.md` (stack-agnostic; references CSS logical properties + `dir="rtl"` discipline)
- `i18n/strings-schema.md` (stack-agnostic; the CDJSON contract)

The H2 summary is short; the deep per-stack content lives in the shared files' per-stack sections.

### `## Phase 6.5 ingestion`

**Promoted from implicit to explicit H2** in the locked schema — was H2 in DESIGN-stack-nextjs.md only; Framer/WordPress design docs folded it into `## Migration recipe`. The schema requires it as its own H2 because:

- Phase 6.5 is re-runnable at any project lifecycle point — the agent looks up this section often, not just at entry-mode setup
- The 5 extraction tools (`extraction/stitch.md` / `divmagic.md` / `figma-design-to-json.md` / `ai-output.md` / `playwright-walk.md`) all need per-stack ingestion recipes
- The phase-18 round-trip ingestion (external-tool output → AI-output parser → component code in user's project) needs per-stack normalization paths

Required content:

- Per-entry-mode extraction tool choices (e.g. `has-framer-attempt` → Stitch + Playwright walker; `has-figma-file` → Figma design-to-json plugin; `has-ai-output` → AI-output parser)
- Stack-specific gotchas during normalization (e.g. Framer canvas Frames can't be programmatically composed — agent emits wireframe brief; WordPress block-to-`components.yaml` mapping; Next.js JSX-to-`components.yaml` extraction)
- Auth-walled site handling per stack
- Round-trip ingestion output paths (where extracted code lands in user's project per stack)

### `## Commerce integration (if transactional=true)`

Phase 24a (commerce platform setup) + 24b (payment provider wiring) + 24c (commerce-specific legal) branching per stack. Required content:

- Recommended commerce platforms for this stack (e.g. Framer → Lemon Squeezy / Stripe Checkout / Snipcart; Next.js → Stripe + custom checkout / Shopify Hydrogen / Lemon Squeezy embed; WordPress → WooCommerce native / Stripe / external)
- Payment provider wiring (TWINT for Swiss audience per locked decision 47 — usually flows through Stripe or Mollie regardless of stack)
- Commerce-specific legal page generation (refund / shipping / T&Cs) per stack

The `(if transactional=true)` conditional in the H2 is verbatim per design-doc convention — phase 11's transactional sibling decision gates whether this section is consumed.

### `## CMS pairing`

Phase 12 CMS decision — which CMSes pair well/poorly with this stack:

- Default pairing (stack-native: Framer CMS for Framer, WordPress-core for WordPress, none/decap/payload triplet for Next.js)
- Compatibility matrix (which CMSes are anti-fit — e.g. Decap doesn't fit Framer; Payload doesn't fit Hugo)
- Headless-CMS escape hatches (when user wants richer content modeling than the stack-native CMS)
- Hosting implications (e.g. Next.js + Payload requires Postgres separately; Next.js + none = file-based markdown)

Per-CMS deep specifics live in `cms-adapters/<cms>.md` (authored in Phase 4); this H2 carries the stack→CMS compatibility view.

### `## Component library pairing`

Phase 18 component-build pairings. Required content:

- Recommended libraries for this stack (e.g. Framer → stock components + Aceternity / Magic UI; Next.js → shadcn/ui + Radix + Tailwind; WordPress → block patterns + Tailwind via theme.json; specifics evolve)
- Per-skill-flavor pairings (UI-UX Pro Max / Impeccable / Emil Kowalski / Taste / 21st.dev Magic — per locked decision 17)
- Bundle-size + perf trade-offs per pairing
- Cross-reference: `skills/wb-component-build/references/per-stack-codegen.md#<stack-slug>` — the read-only Phase-2.B anchor that already covers MVP stacks' codegen shape

### `## Deploy`

Canonical deploy target + DNS pattern + SSL + analytics + performance budget:

- Hosting target (Framer Publish / Vercel / WP host of user's choice)
- DNS instructions (CNAME / A records / Cloudflare integration via MCP where available)
- SSL automation (built-in / Let's Encrypt via host / manual)
- Custom-domain flow
- Analytics injection (GA4 / Plausible / Fathom — per stack)
- Lighthouse / performance expectations per stack
- Phase 29 deploy verification mechanism (Playwright walkthrough)

### `## Post-launch maintenance pattern`

Per locked decision 37 (launch-once phases 31-34 vs ongoing post-launch maintainer template). Adapter-specific because:

- **Framer**: user edits CMS + page text in the canvas; agent edits `code/{Component}.tsx` files + re-syncs via Server API
- **Next.js**: agent edits source code, user commits + push triggers Vercel auto-deploy; CMS work depends on CMS choice
- **WordPress**: user edits content in wp-admin; agent updates theme files + plugin configurations as code

Required content per stack:

- Content-edit loop (who edits what + where)
- Component-edit loop (agent edits which files + how user sees the change)
- Style-token-update loop (agent edits tokens + how they propagate)
- Image-gen iteration (per `consumers/image-gen.md`)
- The user's long-term maintenance description in a single sentence

### `## Limitations + escape hatches`

What this stack CAN'T do (surfaced at phase 11 for user override + reaffirmed at phase 28). Required content:

- Hard limitations (the stack's structural constraints — e.g. Framer can't bypass its hosting; WordPress requires server-side hosting; Next.js requires Node runtime)
- Soft limitations (where the stack is awkward but workable — e.g. Framer canvas-vs-code split; WordPress block-vs-classic editor; Next.js client/server-component complexity)
- Escape hatches per limitation (when the user wants to switch stacks mid-project — phase 11 transactional flag mid-project pattern per locked decision 34; export-to-code paths)

Where relevant, `### Failure modes` H3 subsection enumerates common errors during pipeline phases + recovery paths.

### `## context7 lookups for this stack`

Per Lock-3 freshness pattern — explicit list of context7 IDs the agent invokes at each phase + WebFetch fallback URLs when context7 coverage is thin. Required content:

- Phase 11 (stack decision): canonical context7 ID + question template
- Phase 12 (CMS decision): per-CMS-pairing context7 lookups
- Phase 17 (design system): stack-specific token/style-system docs
- Phase 18 (component build): library + framework current API
- Phase 24a-c (commerce): per-commerce-platform integration docs for this stack
- Phase 28-30 (deploy): deploy mechanism + analytics + custom domain docs

Plus a "cache to" line — `.website-builder/library/docs/<stack>-*.md` is the cache home; re-fetch threshold 30 days per locked Lock-3 freshness norm.

### `## References`

Foundation design-doc paths (vault-root-relative per `vault-workstreams.md` link standard) + per-stack external references (official docs, API references, community resources). Conventional last section per design-doc shape.

## Per-stack write zone for Phase 3 Captains

Each Phase 3 Captain has an exclusive write zone. Stay inside it; everything else is read-only.

| Captain | Stack | Write paths (exclusive) |
|---|---|---|
| **Captain F** | Framer | `adapters/stack-framer.md` (full file) + `### Framer` section in `i18n/language-switcher.md` + `### Framer` section in `i18n/hreflang.md` + `tests/adapters/framer/` (full subdirectory: `fixture/`, `expected.yaml`, `README.md`) |
| **Captain G** | Next.js + shadcn | `adapters/stack-nextjs.md` (full file) + `### Next.js + shadcn` section in `i18n/language-switcher.md` + `### Next.js + shadcn` section in `i18n/hreflang.md` + `tests/adapters/nextjs/` (full subdirectory) |
| **Captain H** | WordPress | `adapters/stack-wordpress.md` (full file) + `### WordPress` section in `i18n/language-switcher.md` + `### WordPress` section in `i18n/hreflang.md` + `tests/adapters/wordpress/` (full subdirectory) |

### READ-ONLY for all Phase 3 Captains

The following files were authored as Phase 3 prep (this packet). They are the shared substrate. **Do NOT modify** during Phase 3 Captain work — modifications surface as architectural concerns requiring General review:

- `adapters/README.md` (this file — the schema contract)
- `i18n/strings-schema.md` (stack-agnostic CDJSON spec)
- `i18n/rtl.md` (stack-agnostic RTL discipline)
- `i18n/language-switcher.md` Overview + Required behavior + non-`### {your-stack}` sections
- `i18n/hreflang.md` Overview + Required behavior + non-`### {your-stack}` sections
- `extraction/stitch.md`, `extraction/divmagic.md`, `extraction/figma-design-to-json.md`, `extraction/ai-output.md`, `extraction/playwright-walk.md` (all stack-agnostic)
- `handoff-spec/component-request-v1.md`, `handoff-spec/component-output-v1.md` (v1 contracts; cross-stack-portable by design)
- `tests/adapters/README.md` (test fixture convention)

Adapter files may *reference* (cross-link to) any of these read-only anchors; they may not edit them.

### Worktree discipline

If multiple Phase 3 Captains run in parallel against the plugin repo, each Captain uses a per-callsign worktree to avoid filesystem collisions on the read-only shared files. Worktree pattern per `git-and-deploy.md`. The General coordinates merge order.

## See also

- `BUILD-strategy.md` Phase 3 — DoD + dispatch model (lines 164-184)
- `DESIGN-stack-framer.md` — Captain F's primary design-doc source
- `DESIGN-stack-nextjs.md` — Captain G's primary design-doc source
- `DESIGN-stack-wordpress.md` — Captain H's primary design-doc source
- `DESIGN-architecture.md` — plugin directory layout (the canonical `adapters/`/`i18n/`/`extraction/`/`handoff-spec/` structure)
- `DESIGN-content-layers.md` — the 5 content layers the §4 table maps
- `DESIGN-i18n.md` — i18n model + per-stack hooks
- `DESIGN-ingestion-and-extraction.md` — phase 6.5 mechanism
- `skills/wb-architecture/SKILL.md` + `references/stack-matrix.md` — phase 11 consumer of adapter files
- `skills/wb-component-build/SKILL.md` + `references/per-stack-codegen.md` — phase 18 consumer of adapter files
- `phase-contracts/06.5-artifact-ingestion.md` — phase 6.5 contract
- Phase 4+ (later) — CMS adapter README at `cms-adapters/README.md`, commerce adapter README at `commerce-adapters/README.md` (same convention, different scope)
