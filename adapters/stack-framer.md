# Stack adapter — Framer

> Framer is a visual canvas WYSIWYG + a code-extensible runtime: React/TSX Code Components, a built-in CMS, a Plugins API, and (per Framer's 2026-05-19 developer reference) a Localization + Managed Collection REST surface. The website-builder picks Framer when the user wants a polished, design-led site they can keep editing visually after the agent leaves — and is willing to live with Framer's hosting + canvas-bound conventions. **The agent ships Code Components and seeds CMS content; the user composes pages on the canvas. The agent does NOT compose pages programmatically — that fights Framer's value prop.** Sister's "Still Humans" project (per `Workstreams/website-builder/website-builder.md` decision 10) is the canonical Framer cosplay test target.
>
> Schema: this file conforms to the 14-section schema in `adapters/README.md`. Section names + order are runtime-load-bearing — the `wb-architecture` skill at phase 11 and `wb-component-build` skill at phase 18 look up sections by exact H2.
>
> Design-doc anchors: `Workstreams/website-builder/stacks/DESIGN-stack-framer.md`, `Workstreams/website-builder/foundation/DESIGN-content-layers.md`, `Workstreams/website-builder/foundation/DESIGN-i18n.md`, `Workstreams/website-builder/foundation/DESIGN-ingestion-and-extraction.md`.

## Mental model

### Identity

- **Stack name + version baseline:** Framer (continuously deployed; no semantic version surface). Code Components built on **React 18+ / TypeScript** semantics; runtime is Framer's edge.
- **Canonical context7 library ID:** `/websites/framer_developers` (primary, 1,048 snippets, High reputation as of 2026-05-19). Secondary: `/websites/framer_developers_assets`, `/websites/framer_developers_plugins-quick-start`.
- **WebFetch fallback URLs** (per S3.5 below — context7 coverage is thinner than Next.js; the Framer developer site has restructured several times in 2026): `https://www.framer.com/developers` (overview), `https://www.framer.com/developers/property-controls` (ControlType surface), `https://www.framer.com/developers/cms` (Plugins CMS API), `https://www.framer.com/developers/components-reference` (`useLocaleInfo` + component hooks).
- **Freshness-check requirement:** the agent invokes context7 (`/websites/framer_developers`) at phases 11 / 17 / 18 / 24a / 28-30 to confirm current surface — Framer's developer API evolves quickly; training data older than ~2026-04 is stale on the Plugins API surface, the `framer-plugin` package, and `useLocaleInfo` (the name `useLocale` predates the current API). When context7 is unreachable, fall back to the WebFetch URLs above and log the gap per `.claude/rules/tool-dependency-discipline.md` Tier 2.

### What Framer feels like to use

Framer is two products living together:

1. **A canvas WYSIWYG editor** — drag-and-drop layout, visual styling, animation timelines, the surface most muggles see and want.
2. **A code-extensible runtime** — Code Components written in React/TSX that plug into the canvas, a CMS for structured content, a Plugins API for programmatic project manipulation, the Localization API for multi-language sites.

The canvas is what the user keeps. The agent writes Code Components and seeds CMS items via the Plugins / Managed Collection APIs; **the user composes pages on the canvas**. This is load-bearing: trying to compose pages programmatically end-to-end fights Framer's value prop (the canvas). Page composition stays a user activity; the agent provides primitives + recipes + wireframe briefs.

Three things to know about how Framer thinks:

- **Pages are canvas documents,** not file-based routes. Each page is a Framer "Frame" the user lays out visually. The agent does NOT create finished page layouts; the agent emits per-page wireframe briefs the user follows on the canvas.
- **CMS items are structured records,** queryable from Code Components and bindable to canvas elements. Good for blog posts, product listings, testimonials, anything repeating. The CMS is exposed via the Plugins API (`framer.getCollection()` / `collection.addItems()`) and the Managed Collection REST surface.
- **Code Components are React/TSX modules** uploaded into the project. They expose props that show up as controls in the canvas's properties panel via `addPropertyControls()`. This is where the agent ships substantive component code.

The muggle understanding: *the agent writes the components and seeds the content; the user assembles the pages on the canvas.* Hands stay clean on both sides.

Derives from `Workstreams/website-builder/stacks/DESIGN-stack-framer.md` lines 15-34 ("Mental model").

## Auth + setup

**Account:** user creates a Framer account at `framer.com`. **Pro plan** recommended — it unlocks Code Components, CMS at full capacity, custom domains, and the Plugins / Localization API surfaces.

### API tokens — `FRAMER_API_TOKEN`

The Plugins and Managed Collection REST APIs require an authentication token generated from the user's Framer account.

- **Env var:** `FRAMER_API_TOKEN` (per `secrets-conventions.md`).
- **Storage:** pulled from 1Password by the website-builder's session-start hook into the agent's runtime env; *never* hardcoded; *never* written to `.website-builder/keys.yaml` or any committed file.
- **1P item:** the user creates `op://shared/framer-api-token/credential` (or equivalent path) and the agent's session-start hook adds the entry to its ITEM_MAP. Pre-launch, the agent prompts the user to set this up.
- **Scope:** project-bound. One token per Framer project; rotates on user demand. The agent surfaces "if you regenerate your Framer token, update 1P and restart the session" at phase 11 setup.

### Local development for Code Components

Framer's CLI (`framer-cli`) provides local-dev affordances. As of 2026-05-19, the canonical installation surface is npm-based:

```bash
npm install -g framer-cli   # verify exact package name via context7 at session-setup time
framer login                # opens browser OAuth flow
```

Code Components are written locally in `code/` (Framer convention), pushed via `framer push` (CLI) or via the Plugins API's code-upload endpoint (verify surface via context7 at phase 18). The agent edits these files directly via Edit/Write in the user's project worktree.

**Verify-at-entry:** the exact `framer-cli` package name + command surface has shifted across Framer releases. Re-fetch from context7 `/websites/framer_developers` or WebFetch `https://www.framer.com/developers` at the user's setup step.

### MCP servers (recommended at setup)

The plugin does **not** bundle any MCP server — same discipline as the existing `mcp__playwright__*` integration: the user installs each MCP they want in their own Claude Code config (`.mcp.json` project-scoped OR `~/.claude.json` user-scoped per CC plugin spec); the agent uses each MCP when present and falls back to direct REST/CLI when not. The agent's session-start checks tool-surface availability and surfaces missing MCPs at phase 11 setup so the user can install the ones they want before the pipeline reaches the phase that consumes them.

Verified-current ecosystem as of 2026-05-20. Per Lock-3 + `.claude/rules/tool-dependency-discipline.md` Tier-2 discipline: re-verify install snippets via context7 / WebFetch at the user's setup step — MCP install commands + auth surfaces drift.

#### Framer-specific MCPs

| MCP | Maintainer + canonical URL | Install path | Agent uses at | Fallback when not installed |
|---|---|---|---|---|
| **"MCP: AI Plugin" (Framer Marketplace, Tommy D. Rossi)** | Community / free. Marketplace: https://www.framer.com/marketplace/plugins/mcp/ — author profile https://www.framer.com/@unframer/ | (1) Install the Framer plugin from the Marketplace into the user's Framer project (one-click in Editor). (2) Open the plugin in the Editor — it generates a per-project WebSocket tunnel URL via a Cloudflare Worker, keyed by the user's Framer ID. (3) Add to user's CC config as a remote/HTTP MCP entry per the URL the plugin shows. Plugin must stay OPEN in the Framer Editor for the tunnel to be live. | **Phase 17** (push Color/Text Styles into the open project's canvas) · **Phase 18** (insert generated Code Components directly via the running plugin instead of `framer push`) · **Phase 22** (rewrite copy via canvas-driven CMS updates) · **Phase 6.5** (read canvas state for re-ingestion / drift detection) | All operations route through Plugins API + REST surface per `### CRUD vocabulary` — `framer push` for Code Components, `framer.plugins.createCollection` / `collection.addItems` for CMS, `/api/managed-collection/*` REST for headless seeding. Slower (user re-loads Editor to see API-pushed changes) but functionally equivalent. |
| **"Design Bridge MCP" (Framer Marketplace, Jay Wilcox)** | Community / free. Marketplace: https://www.framer.com/marketplace/plugins/design-bridge-mcp/ — third-party catalog: https://www.framerjungle.com/plugins/design-bridge-mcp | Same as above (install Framer plugin → plugin emits a tunnel URL → add to CC MCP config). 70 automation tools per the marketplace description (frames / text / images / SVGs / layer management / CMS); narrower than Tommy D. Rossi's plugin in some areas, broader in others. | **Phase 18** (frame primitives + SVG insertion on canvas) · **Phase 14** (wireframe Frame seeding) — useful when Tommy D. Rossi's plugin isn't installed AND user wants any canvas-side automation | Same fallback as above (REST / CLI surface). |
| **Sheshiyer/framer-plugin-mcp (GitHub)** | Community / GitHub: https://github.com/Sheshiyer/framer-plugin-mcp — Awesome MCP listing: https://mcpservers.org/servers/Sheshiyer/framer-plugin-mcp | **OUT OF SCOPE for this adapter.** Per the README intro: this MCP **scaffolds new Framer plugins** (with web3 capabilities); it does NOT operate existing Framer sites. Listed here so future Captains don't confuse it with the marketplace MCP plugins above. | n/a — not consumed by the website-builder pipeline | n/a |

#### Framer-official MCP status (per Commander Round-3 verification)

There is **no first-party Framer-built MCP server** as of 2026-05-20. The Framer community thread "Support for MCP Server Integration in Framer" (https://www.framer.community/c/support/support-for-mcp-server-integration-in-framer) is open; the agent re-checks at phase 11 setup via context7 + WebFetch. The two marketplace plugins above are **community-maintained**; they're the strongest available signal that Framer-side MCP integration is real, viable, and CC-compatible — but they are NOT Framer-maintained. Surface this to the user at phase 11 with the explicit "community-maintained, may break with Framer Editor updates" caveat.

#### Cross-cutting MCPs that apply to Framer's pipeline

| MCP | Maintainer + canonical URL | Install path | Agent uses at | Fallback when not installed |
|---|---|---|---|---|
| **Playwright MCP** (`@playwright/mcp`) | Microsoft, official: https://github.com/microsoft/playwright-mcp — v0.0.75 released 2026-05-07. **Foundation-bundled in this plugin** (already exposed as `mcp__playwright__*` per the existing plugin's foundation pack — no user install required). | N/A — bundled with the foundation pack. The agent expects Playwright MCP to be available at every session. | **Phase 6.5** ingestion of existing Framer / non-Framer sites (paired with Stitch screenshot mode per `extraction/playwright-walk.md`) · **Phase 20** responsive walk · **Phase 22** a11y + perf walk · **Phase 29** deploy verification walk · **Phase 30** analytics + hreflang verification | **N/A — Playwright MCP is foundation-required for this adapter** (same tier as Next.js + WordPress adapters). If unavailable, this is a **Tier-1 system-integrity issue** per `.claude/rules/tool-dependency-discipline.md`; the agent escalates immediately rather than degrading. |
| **Cloudflare MCP** (`mcp.cloudflare.com`) | Cloudflare, official: https://developers.cloudflare.com/agents/model-context-protocol/mcp-servers-for-cloudflare/ | `.mcp.json`: `{"mcpServers": {"cloudflare": {"url": "https://mcp.cloudflare.com/mcp"}}}` — OAuth on first invocation (no API token needed; user picks scopes in browser). Single "API" server exposes all 2,500+ endpoints via two tools (`search()` + `execute()`); product-specific servers also available (DNS Analytics, Workers, etc.). | **Phase 28** custom domain setup — DNS CNAME / A record creation against the user's Cloudflare zone; verifying SSL propagation. Replaces the existing § "Deploy" guidance "walks user through setting CNAME / A records on their registrar" with automated DNS record creation. | User manually creates DNS records in their Cloudflare dashboard (or whatever DNS provider they use — Cloudflare MCP doesn't help if they're on Namecheap/Route53/etc.). Agent provides explicit copy-paste-ready record values. Note: the older community DNS-only MCP at `IAMSamuelRodda/cloudflare-mcp` was **archived 2026-02-16** — point users at the official Cloudflare URL above. |
| **Stripe MCP** (`@stripe/mcp`) | Stripe, official: https://docs.stripe.com/mcp. Alternative install path: Anthropic ships a blessed Stripe plugin at `https://claude.com/plugins/stripe` (install via `claude plugin install stripe@anthropic`) wrapping `@stripe/mcp` + shipping a `stripe-mcp` subagent. G's adapter treats this as the preferred path; pick either based on user preference for plugin-managed vs direct MCP install. | `.mcp.json` local: `{"mcpServers": {"stripe": {"command": "npx", "args": ["-y", "@stripe/mcp@latest"], "env": {"STRIPE_SECRET_KEY": "<your-test-key>"}}}}` — OR remote: `{"servers": {"stripe": {"type": "http", "url": "https://mcp.stripe.com"}}}` — OR Anthropic-plugin: `claude plugin install stripe@anthropic`. Auth: STRIPE_SECRET_KEY env var OR OAuth via remote endpoint. | **Phase 24a** commerce platform setup — create products / prices / Payment Links / Checkout Sessions for the Framer site's Stripe-backed buy buttons · **Phase 24b** payment-provider wiring — confirm TWINT / iDEAL / SEPA / Klarna enabled on the user's Stripe account for the target market | Without Stripe MCP, agent emits configuration instructions for the user to apply manually in Stripe dashboard + generates the Stripe.js client-side embed code from the existing `### Commerce integration` recipes. Slower, fully functional. |
| **Lemon Squeezy MCP** (community: `IntrepidServicesLLC/lemonsqueezy-mcp-server`) | Community / GitHub: https://github.com/IntrepidServicesLLC/lemonsqueezy-mcp-server — multiple alternates (`atharvagupta2003/mcp-lemonsqueezy`, `MichaelWeed/lemon-squeezy-mcp`); none Lemon Squeezy-official yet | Per chosen implementation's README (varies). Typically: clone repo → `npm install && npm run build` → add to `.mcp.json` with `LEMONSQUEEZY_API_KEY` env var. Re-verify maintenance status at session-setup — community implementations vary in update velocity. | **Phase 24a** (Lemon Squeezy is the recommended-default commerce platform for Framer per § "Commerce integration"). Create products / variants / discounts; pull order data for the site's success-page; manage subscriptions. | Lemon Squeezy's own dashboard + REST API directly via `curl` from the agent. Agent generates Buy Button HTML / Code Component wrapper from existing recipes; user wires the embed manually. |
| **GitHub MCP** (official) | GitHub, official: https://github.com/github/github-mcp-server (Note: `@modelcontextprotocol/server-github` was deprecated April 2025; use `github/github-mcp-server` going forward — current canonical.) | `.mcp.json` remote: `{"servers": {"github": {"type": "http", "url": "https://api.githubcopilot.com/mcp/"}}}` (OAuth via VS Code 1.101+ / Claude Code). OR local Docker: `docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server`. 80+ tools across repos / issues / PRs / Actions / code security / discussions. | **Phase 18** when user wants `code/{Component}.tsx` Code Components tracked in their own GitHub repo (alternate to Framer-only source-of-truth) — agent commits + opens PRs directly · **Phase 28** when deploy involves a GitHub-triggered Cloudflare Worker or Vercel webhook · **Post-launch** repo maintenance loops | Without GitHub MCP, the agent uses `gh` CLI (foundation-pack-equivalent) for the same operations — functionally complete, slightly more friction per command. |
| **Sentry MCP** (`@sentry/mcp-server`) | Sentry, official: https://github.com/getsentry/sentry-mcp — hosted at https://mcp.sentry.dev | Remote: OAuth via `https://mcp.sentry.dev`. Local: `.mcp.json`: `{"mcpServers": {"sentry": {"command": "npx", "args": ["@sentry/mcp-server"], "env": {"SENTRY_ACCESS_TOKEN": "<token>"}}}}`. Tools: `search_events`, `search_issues`, full event/trace pull. | **Phase 34** post-launch monitoring — if user wired Sentry into their Framer site (via Custom Code head injection of the Sentry browser SDK), agent investigates errors directly without leaving the session. Optional but recommended for production Framer sites. | User pastes Sentry dashboard errors into the chat; agent reasons from prose. Tier-2 friction; agent surfaces "wire Sentry MCP for tighter monitoring loops" as a follow-up. |
| **Plausible MCP** (preferred: `getsentry/plausible-mcp`; peer: `alexanderop/plausible-mcp`) | **Preferred — `getsentry/plausible-mcp`** (under Sentry's umbrella; last push 2026-05-13; multi-tenant; Stats API v2). Peer alternative — `alexanderop/plausible-mcp` (community, v1.0.0; few commits — older / less actively maintained). The getsentry option is the more recently maintained of the two as of 2026-05-20 and the preferred default. | Per chosen implementation. getsentry: `.mcp.json` with `PLAUSIBLE_API_KEY` env var (Stats API v2 + Site Provisioning API; multi-tenant). alexanderop: build-from-source currently (no npx package yet) — `git clone ... && npm install && npm run build`; tools: `plausible_query`, `plausible_aggregate`, `plausible_breakdown`, `plausible_timeseries`. | **Phase 34** post-launch monitoring — if user picked Plausible at phase 28 analytics, agent pulls site stats directly into the session. | Plausible dashboard URL; user pastes screenshots / stats; agent reasons from those. |
| **Google Analytics MCP / GA4** (third-party via Composio etc.) | Multiple third-party implementations (Composio: https://composio.dev/toolkits/google_analytics/framework/claude-code); no Google-official MCP as of 2026-05-20 | Per implementation. Composio's: managed OAuth + tool-router pattern (account-bound rather than self-hosted). | **Phase 34** post-launch monitoring (alternate to Plausible) | Same as Plausible fallback. |
| **Image-generation MCPs** (multiple) | Several active implementations: `TamerinTECH/claude-code-generate-images-mcp` (Azure OpenAI + Flux + Gemini); `GongRzhe/Image-Generation-MCP-Server` (Replicate Flux); various others | Per implementation. TamerinTECH's: `git clone + ./install.sh`; env vars per provider (`GEMINI_API_KEY` or `AZURE_OPENAI_*`). | **Phase 8** image strategy + **Phase 17** brand visual generation + **Phase 18** Code Component asset generation — generate hero images, illustrations, OG images, favicons in-session and upload to Framer Assets | Per `consumers/image-gen.md` (the plugin's existing consumer-fallback path per locked decision 56 v1 strategy): user pastes images they generated externally; agent ingests via phase 6.5. Slower; pre-existing v1 path. |
| **Vercel MCP** (official) | Vercel, official: https://vercel.com/docs/mcp/vercel-mcp — remote at https://mcp.vercel.com (Beta as of 2026-02-12) | `claude mcp add --transport http vercel https://mcp.vercel.com` (CC native command). OAuth on first invocation. Tools: project/deployment management, deployment log analysis, Vercel docs search. | **Out of scope for Framer stack** — Framer publishes to Framer's own edge, NOT Vercel. Listed here for cross-reference because the Next.js + shadcn stack (Captain G) will rely on this. Only relevant to Framer if user pivots to Next.js via the escape hatch at phase 11 transactional flag mid-project change. | n/a |
| **Snipcart MCP** | **None verified to exist** as of 2026-05-20 (web search returned no Snipcart MCP server). | n/a | n/a — agent uses Snipcart's direct REST API / embed snippet per existing § "Commerce integration" | The existing direct-API path is fully functional; no degradation. |
| **Cal.com MCP** | Cal.com (official) — setup guide: https://cal.com/blog/how-to-connect-calcom-to-claude-using-mcp. Added as a **Claude custom connector** (OAuth-style permission granting via Claude's connectors UI), not a traditional `claude mcp add` install. Verified 2026-05-20. | Per cal.com/blog/how-to-connect-calcom-to-claude-using-mcp — added as a custom connector inside Claude with OAuth-style permission granting. No CC config file edit; Cal.com MCP is invoked through Claude's connector layer. | **Phase 24a** booking-platform setup if user chooses Cal.com as the booking provider for the Framer site (decision 54 default for free booking) · **Post-launch** booking-state queries, event-type CRUD, availability updates. | Cal.com Atoms / embed script as Code Component (`code/CalEmbed.tsx`) + Cal.com REST API directly via `curl` for booking ops. Functional; loses natural-language booking-state queries. |
| **Calendly MCP** | **None verified to exist** as of 2026-05-20 (Calendly's API is documented but no official MCP wrapper found). | n/a | n/a — agent uses Calendly's direct REST API / embed snippet per existing § "Booking flows" | The existing direct-API path is fully functional; no degradation. |

> **Two distinct Cloudflare MCPs exist** — pick the right one:
> - **`https://mcp.cloudflare.com/mcp`** (hosted OAuth): two-tool `search()` + `execute()` surface over 2,500+ Cloudflare API endpoints; DNS record CRUD available via `execute()`. Preferred for deploy phases needing DNS record creation.
> - **`github.com/cloudflare/mcp-server-cloudflare`** (open-source monorepo): 18 focused sub-servers; `dns-analytics` for traffic verification only. **Does NOT include a DNS-records-management sub-server** — for DNS record creation/CRUD, fall back to Cloudflare REST API + `wrangler` CLI.
>
> For this Framer adapter the hosted OAuth path (`https://mcp.cloudflare.com/mcp`) is the recommended default at phase 28 (DNS record CRUD via `execute()` against the user's Cloudflare zone). The open-source monorepo's `dns-analytics` sub-server is a supplementary verification surface at phase 30 / 34.

#### Setup-flow summary

At phase 11 setup the agent surfaces the relevant MCPs the user should consider installing for their flavor of site:

- **Always recommend:** Playwright MCP (if `has-existing-site` entry mode) + one of the Framer Marketplace MCP plugins (Tommy D. Rossi's first by surface breadth; Design Bridge as alternate).
- **Recommend if applicable:** Cloudflare MCP (if user's DNS is on Cloudflare), Stripe MCP (if `transactional=true` + Stripe), Lemon Squeezy MCP (if `transactional=true` + Lemon Squeezy), GitHub MCP (if user wants Code Components in their own repo), Sentry / Plausible MCP (post-launch monitoring).
- **Surface but don't bundle install instructions:** image-generation MCPs (user picks per provider preference / cost).

The agent re-checks tool-surface availability (the `mcp__*` tool list visible in its session) at the start of each phase that has an MCP option, and degrades silently to the documented REST/CLI fallback when an expected MCP isn't present. No silent skipping — the agent surfaces "Playwright MCP not detected; falling back to manual screenshot capture" per `.claude/rules/tool-dependency-discipline.md` Tier-2 protocol.

### Project bootstrap

Two paths depending on whether the user already has a Framer project:

- **Greenfield:** user creates the Framer project manually in the Framer Editor (the agent CANNOT create projects via API as of 2026-05-19; project creation is Editor-only). Once the user provides a project ID + token, the agent seeds CMS collections + locales + styles via API.
- **Existing project:** user provides project ID + token; agent reads current state (locales, collections, styles) via the Localization + Managed Collection APIs, reconciles against `.website-builder/`, and surfaces any drift per phase 6.5.

### CRUD vocabulary

Translates the website-builder's project verbs into Framer's API surface:

| Website-builder verb | Framer API surface (verified 2026-05-19) |
|---|---|
| Create CMS collection | `framer.plugins.createCollection({ name, fields })` (Plugins API) — Plugin mode only, then surfaces in Editor |
| List collection items | `framer.getCollection()` → `collection.getItems()` |
| Add / update collection items | `collection.addItems([...])` (upsert: matching `id` updates, missing creates) |
| Remove collection items | `collection.removeItems(ids)` |
| Set collection field schema | `collection.setFields([...])` |
| Get locales | REST `GET /api/localization/get-locales` |
| Get active locale | REST `GET /api/localization/get-active-locale` (also `useLocaleInfo().activeLocale` from inside a Code Component) |
| Get default locale | REST `GET /api/localization/get-default-locale` |
| Update localization data | REST `POST /api/localization/set-localization-data` |
| Read locale + locale-list from Code Component | `const { activeLocale, locales, setLocale } = useLocaleInfo()` |
| Add new Code Component | `code/{ComponentName}.tsx` + `framer push` (or Plugins API code-upload — verify) |
| Publish site | Editor "Publish" action (no public REST equivalent as of 2026-05-19) |

Derives from `Workstreams/website-builder/stacks/DESIGN-stack-framer.md` lines 36-53 ("Auth + setup") + verified-current API surface (context7 + WebFetch 2026-05-19).

## Migration recipe

Maps pre-step-11 canonical `.website-builder/` content → Framer. Per-layer narrative + recipes + edge cases.

```
.website-builder/                            →  Framer project (Plugins API + canvas)
├── content/pages/{slug}.md                  →  Framer Pages (Frame docs)
│                                                Page metadata (title, slug, SEO) seeded via API where possible
│                                                Visual composition: USER on the canvas
│                                                Agent emits per-page wireframe brief at
│                                                .website-builder/handoff/{slug}-wireframe.md
│                                                (NO programmatic page composition — see "Canvas-as-source-of-truth")
├── content/strings/{lang}.json              →  Framer CMS "Strings" collection
│                                                One CMS item per locale, with FLAT field names
│                                                (Framer CMS does not support nested objects; agent flattens
│                                                 dot-notation to underscore-namespace per recipe below)
│                                                Loaded into Code Components via the framer-plugin runtime
│                                                or rendered via Framer's native localization layer
├── content/sections.yaml                    →  Framer Code Components (one per section type)
│                                                Section spec → React component with addPropertyControls
│                                                The user drops the component on a Frame
├── components.yaml + components/code        →  code/{ComponentName}.tsx
│                                                React/TSX with addPropertyControls(Component, { ... })
│                                                + ControlType.{String|Number|Color|Enum|Image|...}
│                                                Pushed via `framer push`
├── brand.yaml.tokens                        →  Framer Color Styles + Text Styles + code/tokens.ts
│                                                colors → Framer Color Styles (one per palette entry,
│                                                 created via Editor or Plugin)
│                                                typography → Framer Text Styles (per type-scale level)
│                                                spacing + motion → code/tokens.ts (utility module
│                                                 imported by Code Components — Framer has NO first-class
│                                                 spacing tokens at the project level)
├── sitemap.yaml                             →  Framer Pages routing
│                                                Each page seeded as a Frame with the slug from
│                                                sitemap.yaml; nav structure encoded as a Code Component
│                                                reading from a CMS "NavLinks" collection
├── decisions/                               →  Kept in user's git (Framer doesn't store decision logs
│                                                natively — .website-builder/ stays as the canonical
│                                                source-of-truth for non-canvas state)
└── media/                                   →  Framer Assets library (upload via Editor; or
                                                 reference external URLs hosted on Cloudflare R2 /
                                                 Vercel Blob / similar)
```

### Canvas-as-source-of-truth (load-bearing)

**The agent does NOT translate `.website-builder/content/pages/{slug}.md` into a finished Framer page programmatically.** This is the load-bearing discipline that protects Framer's value prop (per `DESIGN-stack-framer.md` lines 95-97). The Plugins API can seed Frame shells + metadata; visual composition is canvas work. The agent emits a per-page **wireframe brief** the user follows on the canvas, and the Code Components + CMS content the user needs are already in the project.

What this means concretely:

- **Yes**: agent creates Code Components, seeds CMS items, configures locales, creates Color/Text Styles.
- **Yes**: agent writes a `.website-builder/handoff/{slug}-wireframe.md` per page describing structural intent (above-the-fold layout, sections sequence, content references, accessibility notes).
- **No**: agent does NOT auto-place Code Components on Frames via API. The user does this on the canvas, guided by the wireframe brief.
- **No**: agent does NOT manipulate Frame-level styling via API. The user does this on the canvas, with Color/Text Styles already seeded.

If you find yourself spec'ing programmatic page composition, you're shipping an antipattern. Surface and stop.

### Strings flattening recipe (Framer CMS field-name constraint)

**Problem (Risk S6, locked in INST):** `i18n/strings-schema.md` mandates nested keys up to 3 levels deep (`nav.primary.home`, `cta.subscribe`, `errors.validation_email`). Framer's CMS Strings collection uses **flat field names** — no nested objects.

**Outbound (`.website-builder/` → Framer CMS):**

1. Walk the source-language `content/strings/{lang}.json` (`en.json` by default).
2. For each leaf string, build a flat key by joining the path with underscores:
   - `cta.subscribe` → field name `cta_subscribe`
   - `nav.primary.home` → field name `nav_primary_home`
   - `errors.validation_email` → field name `errors_validation_email`
3. Reserved keys (`$language`, `$schema`) are NOT pushed (Framer-internal noise).
4. ICU MessageFormat values are pushed verbatim — Framer doesn't parse them, but downstream Code Components do (via a runtime MessageFormat parser the agent ships in `code/i18n.ts`).
5. Push as one CMS item per locale, where each item's `slug` is the locale code (`en`, `de`, `fr`) and `fieldData` carries the flat fields.

Reference shape via `framer-plugin`:

```typescript
import { framer, CollectionItem } from 'framer-plugin'

const collection = await framer.getCollection()   // "Strings" collection, pre-created by agent
const items: CollectionItem[] = [
  {
    id: 'strings-en',
    slug: 'en',
    fieldData: {
      cta_subscribe: { value: "Get the newsletter" },
      cta_subscribe_loading: { value: "Subscribing..." },
      nav_primary_home: { value: "Home" },
      errors_validation_email: { value: "That doesn't look like a valid email." },
      // ... 50-100+ flat fields per locale ...
    },
  },
  // ... one item per locale ...
]
await collection.addItems(items)
```

**Inbound (Framer CMS → `.website-builder/` on phase 6.5 re-ingestion):**

1. Pull each "Strings" CMS item via `framer.getCollection().getItems()`.
2. Walk each `fieldData` key.
3. Re-nest by underscore-split heuristic: split on `_`, build nested object incrementally.
4. **Ambiguity caveat:** a Framer field named `errors_validation_email` re-nests as `errors.validation_email` (3 underscores → 3 levels OR underscores within a key like `validation_email` are level-2). The agent uses the source-language schema (`en.json`) as the canonical key-tree, matches each flat Framer field back to its nested counterpart in the schema, and flags mismatches for user confirmation per phase 6.5 conflict protocol (locked decision 36 — halt-and-force-decision on conflict). A flat field that does NOT appear in the schema is surfaced as a new key the user can route into the nested tree.
5. Write back to `content/strings/{lang}.json` preserving the canonical nested shape per `i18n/strings-schema.md`.

This recipe is bi-directional and lossless when the source-language schema is intact. New keys added in Framer that aren't in the schema halt for user routing decision.

### Per-layer migration recipes

- **Layer 1 (brand.yaml.tokens) → Framer Color Styles + Text Styles:**
  - Color tokens (oklch) → one Framer Color Style per palette entry. Color Style names mirror the token key (`primary`, `neutral_900`, `semantic_error`). Created via Editor (Plugin if/when the Styles API is GA — verify at phase 17).
  - Type-scale levels (`h1`, `h2`, `body`, ...) → one Framer Text Style per level. Family + size + weight + line-height encoded per Style.
  - Spacing scale + motion tokens have NO first-class Framer representation. Agent puts them in `code/tokens.ts` and Code Components import from there. The user does NOT see them in the canvas as Styles; they're locked into Component behavior.

- **Layer 2 (sitemap.yaml + sections.yaml + components.yaml) → Frames + Code Components:**
  - `sitemap.yaml` pages → Frame shells (one per slug). Created via Editor; agent reminds user to create one per slug.
  - `sections.yaml` section types → Code Components (one per section type). Agent writes `.tsx` files; user drops on Frames.
  - `components.yaml` atomic components → Code Components (one per atomic component, but typically agent inlines small ones into the section components for canvas-ergonomics).

- **Layer 3 (strings/{lang}.json) → Framer CMS "Strings" collection** per the flattening recipe above. Plus Framer's native Localization API for any text that lives directly on Frames (per-locale Frame variants).

- **Layer 4 (content/pages/{slug}.md) → Frame composition by user, with wireframe brief from agent:**
  - Per-page MD frontmatter → page metadata seeded on the Frame (title, slug, SEO) via API where possible; rest is user.
  - Per-page MD body → split into sections per the frontmatter `sections:` list. Each section becomes a Code Component instance the user drops on the Frame.
  - Wireframe brief at `.website-builder/handoff/{slug}-wireframe.md` describes layout, sequence, content references, accessibility notes the user follows on the canvas.

- **Layer 5 (briefs/{component}.json) → `code/{Component}.tsx` via `component-request-v1` → external-tool → `component-output-v1` round-trip:**
  - The brief's `output_format` block is set to `{ framework: "framer-custom-component", library: "framer-stock", style_system: "framer-style", language: "tsx" }`.
  - External tool returns TSX; phase 6.5 ingests; agent verifies palette tokens + props + `addPropertyControls` shape against `request.props`.

Derives from `DESIGN-stack-framer.md` lines 55-97 ("Migration recipe") + `DESIGN-content-layers.md` Layer-1-through-5 + `DESIGN-i18n.md` lines 113-118 (Framer CMS Strings model).

## Content layer mapping

The mandatory cross-stack verification table. Per `adapters/README.md` §4 the row labels MUST appear verbatim.

| Layer | Framer native concept |
|---|---|
| L1 brand.yaml.tokens | Framer Color Styles (colors) + Text Styles (typography) created via Editor / Plugins API; spacing + motion encoded in `code/tokens.ts` (imported by Code Components — Framer has no first-class spacing/motion tokens at project level) |
| L2 sitemap.yaml + sections.yaml | Frames (one per sitemap page; user-composed) + Code Components (one per `sections.yaml` section type, exposed via `addPropertyControls`); nav structure as a Code Component reading from a CMS "NavLinks" collection |
| L3 strings/{lang}.json | Framer CMS "Strings" collection (one item per locale); FLAT field names per the strings-flattening recipe (`cta.subscribe` → `cta_subscribe`); accessed via `framer-plugin` runtime + Framer's native Localization API |
| L4 content/pages/*.md | **Frame composition by user on the canvas; agent provides per-page wireframe brief at `.website-builder/handoff/{slug}-wireframe.md`.** NO programmatic page generation via API — page composition is the canvas's value prop and stays a user activity. Page metadata (title, slug, SEO) seeded on the Frame via Plugins API where supported. |
| L5 briefs/{component}.json | `code/{Component}.tsx` (Framer Code Component); brief's `output_format` block targets `{ framework: "framer-custom-component", library: "framer-stock", style_system: "framer-style", language: "tsx" }` — re-targetable cross-stack per `handoff-spec/component-request-v1.md` |

**Verification anchor:** the BUILD-strategy.md Phase 3 DoD requires "same `.website-builder/` content produces equivalent sites on all 3 stacks (modulo platform-specific limitations)." Framer's L4 row is its largest divergence — it embraces user-canvas composition rather than programmatic page generation; this is *the* Framer-specific limitation surfaced at phase 11.

## i18n integration

Stack-level summary; per-stack deep specifics in the shared anchors.

- **Library:** Framer has built-in localization. As of 2026-05-19 (per the context7 Localization API surface) it ships:
  - REST endpoints under `/api/localization/*` (`get-locales`, `get-active-locale`, `get-default-locale`, `get-localization-groups`, `set-localization-data`).
  - The `useLocaleInfo()` hook inside Code Components, returning `{ activeLocale, locales, setLocale }`. (Note: `DESIGN-stack-framer.md` line 117 + `i18n/language-switcher.md#framer` original placeholder mention `useLocale()` — the verified-current API name is `useLocaleInfo()`.)
- **Routing strategy default:** `prefix` (per locked decision 38). Framer supports per-locale path prefixes (`/`, `/de/`, `/fr/`) via the project's locale settings. Subdomain and TLD routing require DNS-level setup outside Framer.
- **Per-language structure (Pattern A default per locked decision 39):** Most sites use Pattern A — shared Frame structure across languages, with locale-bound text rendered via `useLocaleInfo()` + the CMS "Strings" collection per locale. Pattern B (per-locale-content variation) uses per-locale Frame variants composed manually by the user on the canvas.
- **Translation workflow:** Pattern 1 (inline at phase 16) is default per locked decision 40. Agent translates strings + per-locale page MD; the CMS "Strings" items are upserted per locale via `collection.addItems()`. Pattern 2 (translator handoff via brief) uses the standard `briefs/translation-{lang}-{ts}.json` flow; the result paste-back routes through phase 6.5 → updated CMS items via the strings-flattening recipe.
- **RTL:** Framer supports RTL languages but layout mirroring depends on Code Component implementation. The agent uses CSS logical properties (`margin-inline-start`, `padding-inline-end`) per `i18n/rtl.md`. For canvas-composed Frame layouts the user manages mirroring themselves; the agent surfaces this trade-off explicitly at phase 11 if the language set includes Arabic / Hebrew / Persian / Urdu.

**Deep cross-references** (per schema § "i18n integration" guidance):

- Switcher implementation: `i18n/language-switcher.md#framer` (this packet authors the section)
- hreflang emission: `i18n/hreflang.md#framer` (this packet authors the section)
- RTL discipline: `i18n/rtl.md` (stack-agnostic)
- Strings CDJSON contract: `i18n/strings-schema.md` (stack-agnostic; consumed via the flattening recipe in § "Migration recipe" above)

Derives from `DESIGN-stack-framer.md` lines 99-127 ("i18n integration") + `DESIGN-i18n.md` lines 218-253 + verified-current `useLocaleInfo` + Localization REST API (context7 2026-05-19).

## Phase 6.5 ingestion

Re-runnable artifact ingestion. Per the schema, this is its own H2 (not nested under Migration) because phase 6.5 fires at multiple lifecycle points + the 5 extraction tools each need per-stack normalization.

> **MCP cross-reference:** existing-site walks at phase 6.5 prefer the Playwright MCP (`@playwright/mcp`) for hover/scroll/auth-walled state capture; the Framer-Marketplace MCP plugins (Tommy D. Rossi or Design Bridge) can read live canvas state when the user has them installed. See § "MCP servers (recommended at setup)" above for install paths + fallbacks.

### Extraction tool choices per entry mode

| Entry mode | Primary tool | Pair-with | Why |
|---|---|---|---|
| `has-existing-site` (deployed Framer site to migrate) | Stitch (`extraction/stitch.md`) on the published URL | Playwright walker (`extraction/playwright-walk.md`) for hover states + scroll-triggered animations + mobile-emulation variants Stitch's static crawl misses | Framer-published sites often have substantial canvas-driven animation + dynamic state |
| `has-Framer-attempt` (partial Framer project) | Stitch on preview URL | Playwright walker | Same dynamic-state concerns; canvas animations are the differentiator |
| `has-figma-file` (Figma export feeding Framer) | Figma design-to-json (`extraction/figma-design-to-json.md`) | (none) | Figma is structural; no live canvas to walk |
| `has-ai-output` (pasted-back component code) | AI-output parser (`extraction/ai-output.md`) | (none) | Code-shaped; not visual |
| `has-existing-non-Framer-site` (migrating IN to Framer) | Stitch + Playwright walker | divmagic (`extraction/divmagic.md`) for element-precision targeting of specific components the user wants to preserve | Need broad design extraction + targeted component extraction |

### Stack-specific normalization gotchas

- **Canvas Frames are NOT programmatically composable.** When phase 6.5 walks an existing Framer site, the agent captures the structural shape (sections sequence, copy, design tokens) but does NOT attempt to reverse-engineer the Frame composition into auto-placement instructions. The user re-composes on the canvas during phase 18+ using wireframe briefs.
- **Strings re-nesting (the S6 inverse path).** Re-ingesting CMS "Strings" items walks the flat field names back into nested CDJSON per the inverse-flattening recipe in § "Migration recipe". Ambiguous splits (where the schema's intended nesting depth diverges from the underscore count) halt per locked decision 36.
- **Color Styles → brand.yaml.tokens.colors.** Framer's Color Styles export as named OKLCH (or hex/rgb depending on user input). Agent normalizes to OKLCH for `brand.yaml`; surfaces drift if existing tokens differ.
- **Text Styles → brand.yaml.tokens.typography.** Framer's Text Styles map cleanly to the type-scale shape; agent surfaces any Style without a matching scale level.
- **Code Components extraction.** Phase 6.5 can read `code/{Component}.tsx` files directly from the user's Framer project local checkout; props (from `addPropertyControls`) feed `components.yaml`; default values feed `content/sections.yaml`.

### Auth-walled / dynamic-state handling

- **Auth-walled Framer sites:** Playwright walker handles login per `extraction/playwright-walk.md` — user provides test creds inline; Playwright authenticates; walks authenticated state.
- **Heavily-animated canvas pages:** Playwright walker captures multiple viewport sizes + hover/scroll states; Stitch's screenshot mode processes the captures.

### Round-trip ingestion output paths (Framer-specific)

- Stitch / Playwright artifacts → `.website-builder/outputs/stitch-{ts}.md` + `.website-builder/outputs/playwright-{ts}/`
- Normalized brand → `.website-builder/brand.yaml`
- Normalized components → `.website-builder/components.yaml` + (Code Component code) `code/{Component}.tsx` in the Framer project worktree
- Normalized strings → `.website-builder/content/strings/{lang}.json` (post-re-nesting)
- Ingestion decision log → `.website-builder/decisions/ingest-{ts}.md` per `phase-contracts/06.5-artifact-ingestion.md`

Derives from `DESIGN-ingestion-and-extraction.md` + `extraction/stitch.md` + `extraction/playwright-walk.md` + `extraction/divmagic.md` + `extraction/ai-output.md`.

## Commerce integration (if transactional=true)

Framer is not a commerce platform. For transactional sites on Framer the agent wires an external commerce stack via phase 24a / 24b / 24c.

> **MCP cross-reference:** Stripe ships an official MCP (`@stripe/mcp` or `https://mcp.stripe.com`); Lemon Squeezy has community MCP implementations; Snipcart / Cal.com / Calendly have no MCP servers verified as of 2026-05-20 (direct REST / embed-snippet only). See § "MCP servers (recommended at setup)" above for install paths + fallbacks.

### Phase 24a — Commerce platform setup

Recommended commerce platforms for Framer (in approximate fit order):

- **Lemon Squeezy** — recommended default for Framer commerce. Drop-in checkout buttons + overlay; minimal Framer integration. Code Component wraps the Lemon Squeezy Buy Button with brand-styled `addPropertyControls`. Best for digital products + subscriptions; works globally.
- **Stripe Checkout / Payment Links** — second default. Embedded via Code Component using `@stripe/stripe-js` loaded at runtime (lazy import via `next/dynamic`-equivalent or React lazy + Suspense). Good when the user wants control over checkout flow + custom payment methods (TWINT for CH per locked decision 47 flows through Stripe).
- **Snipcart** — works cleanly on Framer. The agent injects the Snipcart script via Framer's project-level "Custom Code" head/body panel; Code Components for buy buttons use Snipcart's `data-item-*` attributes. Snipcart's cart UI is overlay-only — no per-page cart routing complexity.
- **Shopify** — possible via Shopify Buy Button SDK embedded in a Code Component, OR via Shopify Storefront API + custom React rendering. Deeper integration is awkward — surface this trade-off; Shopify-heavy sites are often better on Shopify-native templates than Framer.
- **Gumroad / Sellfy / Paddle** — embedded via Code Component wrapping the respective embed snippet. Simple buy-buttons; minimal customization.

### Phase 24b — Payment provider wiring

Delegated to whichever commerce platform the user picks. Lemon Squeezy / Stripe / Snipcart each handle this internally:

- **TWINT (CH-specific, per locked decision 47):** configured in Stripe or Mollie within the platform; Framer doesn't touch payment-provider config directly.
- **Other regional methods (iDEAL / SEPA / Klarna):** same — platform-internal.

The agent's job at 24b: confirm with user that their commerce platform's regional config matches their target market, and Code Components surface region-correct payment buttons (Stripe Payment Element auto-handles this; Lemon Squeezy needs no per-region config).

### Phase 24c — Commerce-specific legal

Refund policy, shipping policy, T&Cs, privacy policy:

- **Pages** for these created as Frames in the Framer project (user composes on canvas; agent provides drafts in `.website-builder/content/pages/legal-{slug}.md`).
- **Linked from checkout flows** configured in the commerce platform (Lemon Squeezy / Stripe / Snipcart all let the user paste in legal page URLs).
- **Cookie consent banner:** Code Component wrapping a cookie-consent library (e.g. `react-cookie-consent` or `cookie-consent-by-osano`); placed in the project root and surfaced on every Frame via Framer's "Custom Code" body injection.

### Booking flows

Cal.com / Calendly / SimplyBook.me embedded as Code Components wrapping the official embed scripts. Framer's iframe support is solid; embedding works cleanly. The agent ships per-provider Code Components (`code/CalEmbed.tsx`, `code/CalendlyEmbed.tsx`) with `addPropertyControls` for event-type slug + theme.

Derives from `DESIGN-stack-framer.md` lines 128-144 ("Commerce integration") + `phase-contracts/24*.md`.

## CMS pairing

Phase 12 CMS decision for Framer sites.

### Default pairing: Framer CMS (built-in)

- **Why default:** tight integration; no extra hosting; CMS items query directly from Code Components via `framer-plugin`'s `framer.getCollection()` API.
- **Sweet spot:** blog posts, products-light (under ~500 SKUs), testimonials, team members, events, navigation links, the "Strings" collection (per the flattening recipe).
- **Field-shape constraint:** Framer CMS collections are flat field lists — no nested objects. This is the constraint the strings-flattening recipe addresses; same constraint applies to any other nested-shape content (e.g. multi-level product categories must flatten via `category_parent_id` references).
- **Capacity:** verify current limits via context7 at phase 12 (`/websites/framer_developers` or WebFetch `https://www.framer.com/cms`). As of 2026-05-19, free / Pro / Team plans differ on item count + concurrent collection count; the agent surfaces the user's plan limit at decision time.

### Headless CMS via Code Components (escape hatch)

When the user needs richer content modeling than Framer CMS offers:

- **Sanity, Payload, Strapi, TinaCMS, Ghost** — Code Component fetches from the headless CMS at render time, with response caching. The agent wires this when the phase-12 CMS decision picks a headless option AND stack is Framer.
- **Trade-off surfaced at phase 12:** the user loses the "edit content directly in Framer Editor" convenience and gains richer field shapes. For sites with structured nested content (product variants, multi-level category trees, related-content graphs), this is the right call.

### CMS pairings to avoid on Framer

- **Decap CMS** — Decap edits files in a git repo; Framer doesn't expose its source as files. Anti-fit; agent recommends Framer CMS or a headless option instead.
- **WordPress as headless CMS** — possible (WordPress REST API), but the operational complexity (two systems for the user to maintain) typically isn't worth it for a Framer site. Agent surfaces and prefers Framer CMS or Sanity.

### Markdown via Code Components (niche)

If the user wants markdown content in a Framer site (e.g. content in a public GitHub repo edited via PRs), a Code Component fetches the markdown URL and renders via `react-markdown`. Niche; surface trade-offs at phase 12.

Per-CMS deep specifics live in `cms-adapters/<cms>.md` (authored in Phase 4); this H2 carries the stack→CMS compatibility view only.

Derives from `DESIGN-stack-framer.md` lines 173-181 ("CMS pairing") + verified-current Framer CMS API (context7 2026-05-19).

## Component library pairing

Phase 18 component-build pairings for Framer. Cross-references `skills/wb-component-build/references/per-stack-codegen.md#framer` (the read-only Phase-2.B anchor — see lines 46-49 of that file for the canonical Framer codegen shape).

### Recommended libraries

Framer Code Components are React; any React component library works in principle, but Framer's hosted runtime adds two constraints: (a) the runtime is Framer's edge, so bundle size matters; (b) Code Components must expose their props via `addPropertyControls` to be canvas-usable. Pairings:

- **Framer's stock components** — always available; the agent leans on them for layout primitives (Stack, Grid, Container, Text) before reaching for external libraries. Zero bundle cost.
- **shadcn/ui** — works; copy components into `code/` and re-export from Code Components with `addPropertyControls`. Most flexibility, requires Tailwind config inside the Code Component (not Framer's Style system — surface trade-off).
- **Radix Primitives** — works well as headless accessibility layer; the agent wraps Radix primitives in Framer-aware Code Components with property controls. Recommended for any interactive primitive (Dialog, DropdownMenu, Popover) where accessibility-by-construction matters. Verify Radix status via context7 at phase 18 — Radix's update velocity post-WorkOS acquisition is the open question per `per-stack-codegen.md` line 27.
- **Mantine / Chakra / NextUI (HeroUI) / Material UI** — usable but bundle-size cost is significant; Framer's perf budget tightens. Agent surfaces the cost. Mantine + Chakra are tree-shake-friendly; MUI heavier.
- **Aceternity UI / Magic UI** — animation-rich React components; pair beautifully with Framer's native motion model. **Recommended when the user picks the Emil Kowalski / Framer Motion design-skill flavor** (per locked decision 17).

### Per-skill-flavor pairings (per locked decision 17)

| Skill flavor | Recommended primary library | Rationale |
|---|---|---|
| UI-UX Pro Max | Framer stock + custom code in `code/` | Maximum bespoke; visual polish through hand-written Code Components |
| Impeccable | Framer stock + Radix (accessibility floor) + Tailwind (in Code Components) | Production-grade accessibility + design discipline |
| Emil Kowalski / Framer Motion | Framer stock + Aceternity / Magic UI + Framer Motion | Native motion model + curated motion components |
| Taste | Framer stock + shadcn/ui (copy-paste into `code/`) | Tasteful defaults; minimal custom code |
| 21st.dev Magic | 21st.dev components imported into `code/` | Curated catalog of magic-UI components |

### Bundle-size + perf trade-offs

Framer Publish hosts on Framer's edge; perf budget is real:

- **Code Components are bundled per-Frame at publish time.** Heavy libraries imported in widely-used components inflate every page.
- **Animation-heavy components** (Aceternity, Magic UI, Framer Motion) — gate with `prefers-reduced-motion` per `i18n/rtl.md` + accessibility discipline. The phase-17 motion budget pre-allocates this — surface at phase 22 if it's been blown.
- **Lazy-load expensive components** via React `lazy()` + Suspense; Framer's edge handles code-splitting cleanly.

### Cross-reference

Phase 18 codegen pattern detail: `skills/wb-component-build/references/per-stack-codegen.md#framer` (read-only — DO NOT EDIT from this packet). The codegen shape is:

```typescript
// code/{ComponentName}.tsx
import { addPropertyControls, ControlType } from "framer"
import { tokens } from "./tokens"   // spacing + motion utility

export function HeroBlock(props) {
  return (
    <section style={{ padding: tokens.spacing[8] }}>
      <h1>{props.headline}</h1>
      <p>{props.sub}</p>
      <button>{props.cta_text}</button>
    </section>
  )
}

HeroBlock.defaultProps = {
  headline: "Hello",
  sub: "Sub copy",
  cta_text: "Get started",
}

addPropertyControls(HeroBlock, {
  headline: { type: ControlType.String, title: "Headline" },
  sub: { type: ControlType.String, title: "Subhead", displayTextArea: true },
  cta_text: { type: ControlType.String, title: "CTA label" },
  background_image: { type: ControlType.ResponsiveImage, title: "Background" },
})
```

Verified canonical pattern via context7 2026-05-19; ControlType surface per § "context7 lookups" below.

Derives from `DESIGN-stack-framer.md` lines 183-193 ("Component library pairing") + `per-stack-codegen.md` lines 46-49 + verified-current `addPropertyControls` / `ControlType` (context7 2026-05-19).

## Deploy

> **MCP cross-reference:** Cloudflare ships an official MCP at `https://mcp.cloudflare.com/mcp` (OAuth, two-tool `search()` + `execute()` surface over all 2,500+ Cloudflare API endpoints incl. DNS / zone / SSL); GitHub MCP (`https://api.githubcopilot.com/mcp/` OAuth or local Docker) handles repo + Actions if user wants source-of-truth in their own repo. Phase 29 deploy verification consumes Playwright MCP per § "Phase 6.5 ingestion". See § "MCP servers (recommended at setup)" above for full install paths + fallbacks.

### Hosting

**Framer Publish (built-in).** One-click publish from the Framer canvas; deploys to Framer's global edge. The agent verifies deploy via Playwright walkthrough at phase 29.

### Custom domain

Configured in Framer project settings → Domain. Framer provides DNS instructions (CNAME / A records). The agent walks the user through setting records on their registrar (or via the official Cloudflare MCP at `https://mcp.cloudflare.com/mcp` if the user's DNS is on Cloudflare — see § "MCP servers (recommended at setup)" for OAuth-based install).

### SSL

Automatic via Framer's edge — no agent action needed. Lets-Encrypt-equivalent; auto-renewing.

### Analytics

- **Framer's built-in analytics** — page views, top pages, referrers. Surfaced in the Framer dashboard. Default on.
- **For deeper tracking** — agent injects GA4 / Plausible / Fathom / Umami via Framer's project-level "Custom Code" panel (head + body injection points). Validated at phase 30 via Playwright.
- **Privacy:** consent-required regions (EU, CH per revFADP) need a cookie-consent banner (per § "Commerce integration" Phase 24c) wired BEFORE analytics tags fire.

### Performance

Framer's edge is reasonably fast. Lighthouse 80+ achievable on most Framer Pro sites; LCP depends on image-loading strategy. The agent enforces:

- **Responsive images** via Framer's `ResponsiveImage` ControlType (`srcSet` + `alt`) in Code Components — never raw `<img src=...>` for hero / above-the-fold images.
- **Animation-perf gating** — `prefers-reduced-motion` gate on animation-heavy components.
- **Bundle discipline** per § "Component library pairing" — heavy libraries surface at phase 22.

### Phase 29 deploy verification

Playwright walks the published site:

- Every page resolves at its `sitemap.yaml` slug + correct locale prefix.
- hreflang tags present per `i18n/hreflang.md#framer`.
- Language switcher functional (per `i18n/language-switcher.md#framer`).
- No 404s on internal links.
- Analytics events fire (if consent given).
- Lighthouse run captured + flagged.

### Limitation flagged at deploy

**Framer Publish hosts on Framer's infrastructure.** Users wanting full control over hosting (Vercel / Cloudflare Pages / their own server) cannot use Framer Publish. Surface at phase 11 AND phase 28 — escape hatch is export-to-code (Framer supports this on some plans) and pivot to Next.js via locked decision 34's mid-project stack switch.

Derives from `DESIGN-stack-framer.md` lines 146-158 ("Deploy").

## Post-launch maintenance pattern

Per locked decision 37 — Framer's hosted-no-build model gives a maintenance loop shaped by canvas-edit + code-edit duality. The post-launch maintainer template (per locked decision 28) installs into `.website-builder/post-launch/` at deploy.

### The user's long-term maintenance loop

*Describe what they want → agent edits code or CMS or surfaces wireframe brief → user opens canvas to verify or compose.*

### Per-task patterns

- **Content edits (CMS + page text):** user edits CMS items + page text directly in Framer canvas. The maintainer template reminds them to mirror substantive edits back into `.website-builder/content/` if they want the canonical record kept current. Agent can re-sync via phase 6.5 with Framer URL as artifact source (Stitch + Playwright walk on the published site → re-normalize).
- **Component edits:** user requests changes; agent edits the `code/{ComponentName}.tsx` file locally, pushes via `framer push`, the canvas reflects the new prop controls / behavior automatically. User does NOT need to re-drop components on Frames — `addPropertyControls` updates propagate.
- **CMS schema changes (adding/removing fields on a collection):** agent uses the Plugins API `collection.setFields([...])` to update schema; existing items adapt (new fields default-null; removed fields drop). Re-fetch `framer-plugin` API surface via context7 if migration involves data transformation.
- **Style token updates:** agent updates `code/tokens.ts` (spacing/motion) + Framer Color/Text Styles (via Plugin or Editor) for colors/typography; canvas auto-reflects on next publish.
- **Image-gen iteration:** new images generated (per `consumers/image-gen.md`), uploaded to Framer Assets via Editor, swapped into pages on canvas by user. Agent provides the image; user places it.
- **Adding a new language:** agent ships translated CMS "Strings" item per the flattening recipe; per-locale page MDs translated and re-pushed; user verifies on canvas. Language switcher + hreflang auto-update once the locale is added in Framer project settings.

### Re-sync from canvas drift

A common post-launch pattern: the user edits substantively on the canvas (rewrites copy, restructures a section, adds a new collection field). The agent's `.website-builder/` falls out of sync. Phase 6.5 re-ingestion against the published site re-normalizes; the agent surfaces drift and offers to update `.website-builder/` (or accept canvas as current truth and update accordingly).

Derives from `DESIGN-stack-framer.md` lines 160-170 ("Post-launch maintenance pattern") + locked decision 37.

## Limitations + escape hatches

What Framer CAN'T do (surfaced at phase 11 for user override + reaffirmed at phase 28).

### Hard limitations (structural)

- **Cannot compose finished pages programmatically.** The Plugins API creates Frame shells + metadata; visual composition is canvas work. Agent emits wireframe briefs the user follows. (This is canvas-as-source-of-truth — see § "Migration recipe" / "Canvas-as-source-of-truth".)
- **Cannot bypass Framer's hosting.** Framer sites publish to Framer's edge; no Vercel / Cloudflare Pages / self-host path. User who wants their own hosting → wrong stack.
- **CMS field-shape is flat.** No nested objects in CMS items. Constrains strings (mitigated by flattening recipe); constrains any other nested data shape (workaround: reference IDs / flat denormalization).
- **No granular spacing tokens at project level.** Framer Color Styles + Text Styles only; spacing/motion live in `code/tokens.ts` and only apply inside Code Components — Frame-level spacing on canvas is manual numeric input by the user.
- **Deep version control of canvas-composed Frames is shallow.** Framer has its own history; git tracks `.website-builder/` + `code/` but not the canvas state. Surface this trade-off at phase 11.
- **No public project-creation REST API as of 2026-05-19.** User creates projects via Editor; agent operates against existing project IDs.
- **No public publish-trigger REST API as of 2026-05-19.** Publish is Editor-only — agent cannot deploy programmatically; user clicks Publish in Framer.

### Soft limitations (workable but awkward)

- **Canvas-vs-code split** — beginners get confused about which surface owns what. The post-launch maintainer template addresses this with explicit "if it's *this* kind of change, you edit *here*" guidance.
- **Custom CSS at the canvas level** — Frames composed on the canvas use Framer's style system; Code Components can ship any CSS. Agent works within both; surfaces the boundary at phase 17.
- **Headless CMS adds a system to maintain** — if the user picks Sanity / Payload over Framer CMS at phase 12, they're juggling two CMSes' worth of operational surface. Framer CMS is preferred unless content modeling demands more.
- **Animation perf at scale** — heavy motion components (Aceternity / Magic UI) at scale tank Lighthouse. Phase 17 motion budget allocates; phase 22 catches drift.

### Escape hatches per limitation

- **User wants control beyond canvas:** export to code (Framer supports this on some plans) and pivot to Next.js. Phase 11 transactional flag mid-project change pattern (locked decision 34) handles the restart.
- **User wants to keep Framer but needs more content structure:** add a headless CMS via Code Components (Sanity / Payload); agent wires per phase 12. Trade-off: lose in-Editor content editing convenience.
- **User wants offline-first / no Framer dependency:** wrong stack — agent surfaces at phase 11 and offers Astro / Next.js as alternatives (Astro is the closer fit for "static-feeling content site without Framer").
- **User wants programmatic publish (CI/CD-style deploys):** not supported as of 2026-05-19; agent surfaces "publish is human-in-the-loop on Framer." User accepts or pivots.

### Failure modes

| Failure | Cause | Recovery |
|---|---|---|
| Plugins API returns 401 / 403 | `FRAMER_API_TOKEN` missing / wrong / revoked | Verify 1P entry; ask user to regenerate Framer token; update 1P; restart session |
| `framer push` fails (Code Component upload) | Token scope, `framer-cli` outdated, network | Re-fetch CLI surface via context7; reinstall CLI; retry; surface verbatim error to user |
| CMS `addItems` succeeds but items don't appear in Editor | Item `slug` collides with existing | Inspect collection via `getItems`; surface duplicate slug; ask user to disambiguate |
| Localization REST 404 | Project not on a plan that supports localization | Surface plan-tier issue; user upgrades or accepts single-language |
| `useLocaleInfo()` returns `undefined` in a Code Component | Component rendered in static context (e.g. SSG preview) before Framer's locale hydration | Defer hook usage to client-side; gate with `if (!activeLocale) return null` |
| Canvas Frame loses content after Color Style rename | Framer doesn't always cascade Style renames into Frame bindings | Re-fetch Style ID via Plugins API after renames; surface a list of bindings the user should manually update on canvas |
| Strings flattening creates ambiguous re-nesting | Underscore appearing in a leaf key (e.g. `validation_email`) | Per § "Migration recipe" strings recipe: use source-language schema as canonical key-tree; halt + ask user on mismatch |
| Bundle size exceeds Framer edge limits | Heavy component library or many Code Components per page | Per § "Component library pairing": lazy-load; tree-shake; surface trade-off |
| RTL layout breaks unexpectedly | Code Component uses physical CSS properties (`margin-left` instead of `margin-inline-start`) | Switch to CSS logical properties per `i18n/rtl.md`; verify at phase 22 Playwright walk |

Derives from `DESIGN-stack-framer.md` lines 195-209 ("Limitations + escape hatches") + verified-current Plugins/Localization REST surface (context7 2026-05-19).

## context7 lookups for this stack

Per the Lock-3 freshness pattern.

### Phases + library IDs

| Phase | Primary context7 ID | Question template | WebFetch fallback (when context7 unreachable — Tier 2) |
|---|---|---|---|
| 11 (stack decision) | `/websites/framer_developers` | "current Framer Plugins API + Code Components + Localization + Pro-plan capabilities" | `https://www.framer.com/developers` |
| 12 (CMS decision) | `/websites/framer_developers` | "current Framer CMS collection limits + field types + plan-tier differences" | `https://www.framer.com/cms` + `https://www.framer.com/developers/cms` |
| 17 (design system) | `/websites/framer_developers` | "current Framer Color Styles + Text Styles + Plugins API for styles creation" | `https://www.framer.com/developers` |
| 18 (component build) | `/websites/framer_developers` + `/websites/framer_developers_assets` | "current `addPropertyControls` + `ControlType` enum + `framer-plugin` package + canvas-bundle perf" | `https://www.framer.com/developers/property-controls` + `https://www.framer.com/developers/code-components` |
| 22 (i18n + a11y + perf) | `/websites/framer_developers` | "current `useLocaleInfo` hook + Localization REST API + hreflang emission + RTL handling" | `https://www.framer.com/developers/components-reference` |
| 24a (commerce) | `/websites/framer_developers` | "current Framer + {Lemon Squeezy | Stripe | Snipcart} integration patterns + Buy Button SDKs" | platform's own docs (`https://docs.stripe.com`, `https://docs.lemonsqueezy.com`, etc.) |
| 28-30 (deploy) | `/websites/framer_developers` | "current Framer Publish + custom domain + DNS + analytics injection patterns" | `https://www.framer.com/help` |
| 11 setup — MCP ecosystem | (no canonical context7 ID — MCP install surfaces change frequently) | n/a | Framer Marketplace `https://www.framer.com/marketplace/plugins/mcp/` + `https://www.framer.com/marketplace/plugins/design-bridge-mcp/` ; Framer community thread `https://www.framer.community/c/support/support-for-mcp-server-integration-in-framer` ; cross-cutting MCP canonical URLs in § "MCP servers (recommended at setup)" above |

### Cache discipline

- Cache home: `.website-builder/library/docs/framer-*.md` per the clone-into-project pattern (locked decision 42).
- Re-fetch threshold: **30 days** per the locked Lock-3 freshness norm.
- On context7 unreachable: WebFetch the fallback URL, save to the cache path, log Tier-2 gap per `.claude/rules/tool-dependency-discipline.md`.
- **Provenance discipline:** every cached doc has a header `<!-- fetched from {URL} at {ISO-8601 UTC}; ref: phase {N} -->`.

### Why WebFetch is mandatory for this stack

Per Risk S3.5 (locked at INST authoring): Framer's developer API has restructured several times in 2026 (the Plugins API + `framer-plugin` package + Localization REST surface all post-date most LLM training cutoffs). Context7 coverage is more current than training data but still varies — the `useLocaleInfo` hook name vs the older `useLocale` is one example. WebFetch against `https://www.framer.com/developers/*` is the freshest signal; pair with context7 at every phase entry.

### Verified-current surface (this packet, 2026-05-19)

For provenance: at INST authoring, context7 + WebFetch confirmed:

- `addPropertyControls(Component, { propName: { type: ControlType.X, title: ... } })` — verified verbatim from context7 example.
- `ControlType` enum (verified verbatim from WebFetch `https://www.framer.com/developers/property-controls` 2026-05-19): `String, Number, Boolean, Color, Enum, ResponsiveImage, File, Link, Object, Array, ComponentInstance, Padding, BorderRadius, Border, BoxShadow, Date, EventHandler, Cursor, Font, Gap, Transition, TrackingId`. Common per-control fields: `title, hidden, description` plus type-specific fields.
- `import { framer, CollectionItem } from 'framer-plugin'` — verified verbatim from context7.
- `framer.getCollection()`, `collection.getFields()`, `collection.addItems(items)`, `collection.removeItems(ids)`, `collection.setFields(fields)` — verified.
- `framer.plugins.createCollection({ name, fields })` — verified.
- `const { activeLocale, locales, setLocale } = useLocaleInfo()` — verified (verbatim from context7 `https://www.framer.com/developers/components-reference`); supersedes the `useLocale()` placeholder in older docs.
- Localization REST API at `/api/localization/{get-locales,get-active-locale,get-default-locale,get-localization-groups,set-localization-data}` — verified verbatim from context7.
- Managed Collection REST API at `/api/managed-collection/{add-items,get-fields,get-items-ids,remove-items,set-as-active,set-fields,set-item-order}` — verified verbatim.

## References

### Foundation design docs (vault-root-relative)

- [VISION-website-builder.md](Workstreams/website-builder/VISION-website-builder.md)
- [BUILD-strategy.md](Workstreams/website-builder/BUILD-strategy.md)
- [DESIGN-architecture.md](Workstreams/website-builder/foundation/DESIGN-architecture.md)
- [DESIGN-project-scaffold.md](Workstreams/website-builder/foundation/DESIGN-project-scaffold.md)
- [DESIGN-content-layers.md](Workstreams/website-builder/foundation/DESIGN-content-layers.md)
- [DESIGN-i18n.md](Workstreams/website-builder/foundation/DESIGN-i18n.md)
- [DESIGN-ingestion-and-extraction.md](Workstreams/website-builder/foundation/DESIGN-ingestion-and-extraction.md)
- [DESIGN-phase-contracts.md](Workstreams/website-builder/foundation/DESIGN-phase-contracts.md)
- [DESIGN-stack-framer.md](Workstreams/website-builder/stacks/DESIGN-stack-framer.md) — primary design-doc source for this adapter

### Plugin shared anchors (read-only — referenced from this adapter)

- [adapters/README.md](adapters/README.md) — 14-section schema this adapter conforms to
- [i18n/language-switcher.md](i18n/language-switcher.md) — `### Framer` section authored in this packet
- [i18n/hreflang.md](i18n/hreflang.md) — `### Framer` section authored in this packet
- [i18n/strings-schema.md](i18n/strings-schema.md) — CDJSON contract; consumed via flattening recipe
- [i18n/rtl.md](i18n/rtl.md) — stack-agnostic RTL discipline
- [extraction/stitch.md](extraction/stitch.md)
- [extraction/playwright-walk.md](extraction/playwright-walk.md)
- [extraction/divmagic.md](extraction/divmagic.md)
- [extraction/ai-output.md](extraction/ai-output.md)
- [extraction/figma-design-to-json.md](extraction/figma-design-to-json.md)
- [handoff-spec/component-request-v1.md](handoff-spec/component-request-v1.md)
- [handoff-spec/component-output-v1.md](handoff-spec/component-output-v1.md)
- [skills/wb-component-build/references/per-stack-codegen.md](skills/wb-component-build/references/per-stack-codegen.md) — Framer codegen at lines 46-49
- [tests/adapters/README.md](tests/adapters/README.md) — fixture convention
- [tests/adapters/framer/README.md](tests/adapters/framer/README.md) — this stack's fixture

### External Framer references (URLs, verified surface 2026-05-19)

- Framer official: https://www.framer.com
- Framer Developers (entry): https://www.framer.com/developers
- Framer Property Controls reference: https://www.framer.com/developers/property-controls
- Framer Components Reference (incl. `useLocaleInfo`): https://www.framer.com/developers/components-reference
- Framer Plugins (entry): https://www.framer.com/developers/plugins
- Framer Plugins CMS API: https://www.framer.com/developers/cms
- Framer CMS marketing/help: https://www.framer.com/cms
- Framer Motion: https://www.framer.com/motion
- Framer Help articles: https://www.framer.com/help

### context7 library IDs (canonical)

- Primary: `/websites/framer_developers`
- Secondary: `/websites/framer_developers_assets`, `/websites/framer_developers_plugins-quick-start`

### Sister project — cosplay test target

"Still Humans" — per [website-builder.md](Workstreams/website-builder/website-builder.md) locked decision 10. The canonical Framer cosplay test once the v1 plugin ships.
