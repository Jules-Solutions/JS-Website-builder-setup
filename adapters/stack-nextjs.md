# Stack adapter — Next.js + shadcn

> Runtime artifact the website-builder agent loads when `project.yaml.stack` is `nextjs`. The `wb-architecture` skill consumes this at phase 11 (stack decision); `wb-component-build` at phase 18 (component build); the phase-6.5 re-runnable ingestion at any project lifecycle point. Authored against the canonical 14-section schema in `adapters/README.md`.
>
> Primary design-doc source: `Workstreams/website-builder/stacks/DESIGN-stack-nextjs.md`. Pairing source: `Workstreams/website-builder/components/DESIGN-components-react.md` (shadcn/ui as default). i18n source: `Workstreams/website-builder/foundation/DESIGN-i18n.md`.

## Mental model

### Identity

- **Stack:** Next.js + shadcn/ui (App Router exclusively; Pages Router is legacy and never recommended for greenfield)
- **Version baseline:** Next.js 15+ (verified context7 `/vercel/next.js` 2026-05-18 — v16.x current, v15.x supported, benchmark 89.84, High reputation, 2178 snippets). Next.js 15 introduced the `fetch()` no-store default — a breaking change vs Next.js 14's `force-cache` default (see §"Limitations + escape hatches" → `### Failure modes` and §"context7 lookups for this stack" for the migration-landmine note).
- **Canonical context7 ID:** `/vercel/next.js` (primary); `/shadcn-ui/ui` (component library default); `/tailwindlabs/tailwindcss.com` (CSS); `/payloadcms/payload` (deepest CMS pairing — see §"CMS pairing"); `/radix-ui/primitives` (under shadcn's hood). Per-stack manifest in `skills/wb-component-build/references/per-stack-codegen.md#nextjs`.
- **Freshness-check requirement:** the agent invokes context7 at phase 11 / 17 / 18 / 28-30 to confirm the current surface — **this stack evolves fast; training data is stale within 6 months**. Cached docs in `.website-builder/library/docs/nextjs-*.md` re-fetch on the 30-day threshold per `skills/wb-architecture/references/context7-protocol.md`. The Next.js 15 `fetch` default change alone is the canonical example of why this isn't optional.

Next.js is layered:

1. **App Router (default modern):** file-system routing where each `app/{route}/page.tsx` is a route. Server Components by default; `"use client"` directive opts into client components. Built-in layouts via `app/{route}/layout.tsx`. The agent uses App Router exclusively for new projects — Pages Router is legacy and not recommended for greenfield.
2. **Rendering modes:** any route can be Static (default at build), ISR (Incremental Static Regeneration via `export const revalidate = N`), SSR (server-rendered per request via `export const dynamic = 'force-dynamic'`), or fully Edge (via `export const runtime = 'edge'`). Agent picks per page based on content type.
3. **Route Handlers:** `app/api/{route}/route.ts` exposes server-side endpoints. Used for forms (phases 22-23), webhooks (Stripe per §"Commerce integration"), and custom logic.
4. **React Server Components (RSC):** by default everything renders on the server; client-side interactivity is opt-in via the `'use client'` directive **at the top of the file before imports**. Reduces bundle size dramatically for content sites.
5. **MDX:** `.mdx` extension lets MD pages embed React components inline. Enables rich content authoring without abandoning React.
6. **Vercel-native:** Vercel built Next.js; deploy is one `git push` away. Edge Functions, Image Optimization (`next/image`), Analytics, Speed Insights all integrate cleanly.

Three things to know about how Next.js thinks:

- **Server-first.** Default to Server Components; opt into client components only when interactivity is needed (forms, animations, state). Reduces JS shipped to the browser.
- **File-system routing.** No routing config; the file structure IS the routes. `app/about/page.tsx` → `/about`.
- **Convention over configuration.** Specific file names (`page.tsx` / `layout.tsx` / `loading.tsx` / `error.tsx` / `not-found.tsx` / `route.ts`) have specific roles. Agent uses these conventions exactly.

**The muggle needs to understand:** the agent ships a real codebase the user owns. The site is a directory of `.tsx` and `.mdx` files in their git repo. They (or a developer they hire) can read, modify, and extend it. Vercel handles deploy magic; the agent writes the code.

## Auth + setup

**Account:** user creates a Vercel account at vercel.com. The free Hobby tier is enough for most muggle projects; Pro ($20/mo) for higher bandwidth + analytics.

**Project creation (phase 11 — once stack decision is locked):**

```bash
npx create-next-app@latest my-site --typescript --app --tailwind --eslint
cd my-site
```

The agent runs this with explicit flags: `--app` (App Router; Pages Router is never the answer for new projects), `--typescript`, `--tailwind` (the CSS default for shadcn pairing), `--eslint` (linting on by default).

**Local dev:**

```bash
pnpm install   # or npm install / yarn / bun — pnpm preferred per Payload + Next.js convention
pnpm dev       # http://localhost:3000
```

**MCP / tooling:**

- **Vercel MCP** — official; used at phases 28-29 for deploy + DNS + env-var management
- **Cloudflare MCP** — when DNS is on Cloudflare; used at phase 28
- **context7** — invoked at phases 11 / 17 / 18 / 28 for fresh Next.js / React / shadcn / Tailwind docs (see §"context7 lookups for this stack")
- **Playwright MCP** — for visual verification at phases 20 + 27 + 29

**Authentication for the site itself** (when the site needs user auth — dashboards, members-only content, paid memberships): the agent recommends **Better Auth** (https://better-auth.com) — vault-canonical pick, full-featured, TypeScript-native, integrates with Drizzle / Prisma / etc. Out of scope for most muggle marketing sites; surfaced only when project requirements call for it (e.g., transactional site with member dashboards per §"Commerce integration").

**API keys + secrets:** stored in `.website-builder/keys.yaml` (references — never values) and the project's `.env.local` (gitignored by default per Next.js scaffold) OR 1Password references (opt-in per `.claude/rules/secrets-conventions.md`). Vercel deploy reads env vars from Vercel's Project Settings → Environment Variables UI; the agent walks the user through copying from `.env.local` to Vercel via the Vercel MCP at phase 29.

### CRUD vocabulary

Next.js has no central project-management API surface — it's a code framework, not a managed platform. The CRUD vocabulary translates as follows:

| Universal verb | Next.js native concept |
|---|---|
| **Create project** | `npx create-next-app@latest` scaffolds a new project directory |
| **Create page** | Author `app/{slug}/page.tsx` (and `content/pages/{slug}.mdx` for prose-driven pages) |
| **Update page** | Edit `app/{slug}/page.tsx` or the associated MDX file |
| **Delete page** | Delete the `app/{slug}/` directory; Next.js routing follows the file system |
| **Upload asset** | Place in `public/` (Vercel serves directly) OR upload to Vercel Blob / Cloudflare R2 for larger media |
| **Publish** | `git push` to `main` triggers Vercel auto-deploy; first deploy via `vercel` CLI or Vercel MCP |
| **Unpublish** | Remove from Vercel (Project → Deployments → … → Delete) OR `git revert` + push |

The agent NEVER does CRUD through a Vercel UI — every change is a code change committed to git. That's the point: the user owns a real codebase.

### MCP servers (recommended at setup)

The plugin does NOT bundle any MCP server — same pattern as `mcp__playwright__*` in the existing plugin. Each MCP below is a separate user-side install via the canonical CC config (`.mcp.json` project-scoped OR `~/.claude.json` user-scoped). The agent USES the MCP when present and **falls back cleanly to direct REST/CLI/SDK** when not. Per the connector-setup discipline locked by Commander: setup-is-part-of-connector-setup, not bundled.

The audit below is exhaustive per Round 3. Every MCP investigated is listed, including **negative findings** (no MCP exists yet for that surface) — the negative findings are themselves load-bearing for the agent at runtime ("don't keep searching for a `next-intl` MCP — there isn't one; fall back to next-intl CLI/scripts").

#### Core platform MCPs (high-leverage; recommend at first-run setup)

##### Vercel MCP — official, public beta (mandatory for deploy automation)

- **Canonical URL:** https://vercel.com/docs/mcp/vercel-mcp + https://mcp.vercel.com (the remote OAuth endpoint)
- **Maintainer + recency:** Vercel (official); Public Beta announced via `vercel.com/changelog/vercels-mcp`; verified 2026-05-20
- **Install (Claude Code, HTTP transport, OAuth):**
  ```bash
  claude mcp add --transport http vercel https://mcp.vercel.com
  ```
  Project-scoped `.mcp.json` snippet (equivalent):
  ```json
  {
    "mcpServers": {
      "vercel": {
        "type": "http",
        "url": "https://mcp.vercel.com"
      }
    }
  }
  ```
  First invocation triggers OAuth flow in the browser — user authorizes which Vercel team(s) Claude may access.
- **Used by agent at:** phases **28** (custom-domain add + DNS-record set), **29** (production deploy via `mcp__vercel__deploy_to_vercel`; preview deploy on PR), **30** (analytics enable: Vercel Analytics + Speed Insights toggle), **34** (post-launch monitoring access to deploy history + runtime logs), **22** (perf audit reads from Speed Insights). Cross-ref §"Deploy" Phase 28-30.
- **Fallback when not installed:** `npm install -g vercel` → `vercel` + `vercel --prod` + `vercel domains add` + `vercel env add/pull` from the CLI; or REST API via `Bash + curl` against `https://api.vercel.com/v9/projects` etc. with a Vercel Personal Access Token from `.env.local`. Functional but loses the OAuth-scoped permission boundary the MCP gives.

##### shadcn/ui MCP — official, in-tree (mandatory for component build)

- **Canonical URL:** https://ui.shadcn.com/docs/mcp (official) — verified 2026-05-20. Community alternative: https://github.com/Jpisnice/shadcn-ui-mcp-server (multi-framework: React, Svelte, Vue, React Native; needs a GitHub API token to avoid rate-limit).
- **Maintainer + recency:** shadcn-ui org (official); Jpisnice (community, active multi-framework). Both indexed in context7 as `/shadcn-ui/ui` (1129 snippets, High reputation, benchmark 83.03, verified 2026-05-20).
- **Install (Claude Code, official):** per https://ui.shadcn.com/docs/mcp — `.mcp.json` project-scoped:
  ```json
  {
    "mcpServers": {
      "shadcn": {
        "command": "npx",
        "args": ["-y", "shadcn@latest", "mcp"]
      }
    }
  }
  ```
  Then `/mcp` in CC to verify the server registered.
  
  Install (community, Jpisnice — better when working in Svelte / Vue / React Native too):
  ```bash
  claude mcp add shadcn -- bunx -y @jpisnice/shadcn-ui-mcp-server --github-api-key YOUR_GITHUB_PAT
  ```
- **Used by agent at:** phase **18** (component build) — Browse Components by registry; Search across registries; Get Component Source Code (latest shadcn v4 TypeScript); Get Blocks (full dashboard/form scaffolds); Install components with natural language ("add the form + dropdown-menu primitives + the dashboard-01 block"). Cross-ref §"Component library pairing".
- **Fallback when not installed:** `npx shadcn@latest init` + `npx shadcn@latest add <primitive>` CLI directly; agent reads cached docs at `.website-builder/library/docs/shadcn-components.md` (auto-cloned at phase 18 entry per per-stack-codegen.md). Functional but loses the natural-language "install the dashboard block + its 6 dependencies" turn-around — agent has to enumerate primitives one by one.

##### context7 MCP — already in plugin foundation (mandatory for Lock-3 freshness)

- **Canonical:** `/vercel/next.js`, `/shadcn-ui/ui`, `/tailwindlabs/tailwindcss.com`, `/payloadcms/payload`, `/radix-ui/primitives`, etc. (see §"context7 lookups for this stack" for the full manifest).
- **Maintainer + recency:** Upstash; already pre-loaded in plugin foundation per `.claude/rules/context7.md` — no install action by the user.
- **Install:** N/A — bundled with the foundation pack.
- **Used by agent at:** every Lock-3 freshness invocation per §"context7 lookups for this stack".
- **Fallback when not installed:** WebFetch the canonical doc URLs (`nextjs.org/docs`, `ui.shadcn.com/docs`, etc.). Slower; no semantic search.

##### Playwright MCP — already in plugin foundation (mandatory for visual verification)

- **Canonical:** `@playwright/mcp` — already bundled with the plugin per `mcp__playwright__*` tools.
- **Maintainer + recency:** Microsoft Playwright (official); pre-loaded.
- **Install:** N/A — bundled with the foundation pack.
- **Used by agent at:** phase **6.5** (deployed-site walk + AI-output cross-validation — cross-ref §"Phase 6.5 ingestion" walk procedure step 3), phase **20** (responsive + i18n walk, RTL pages where applicable), phase **22** (a11y audit + Lighthouse harness), phase **27/29** (deploy verification — every page walked at production URL), language-switcher + hreflang verification (cross-ref `i18n/language-switcher.md#next-js--shadcn` validation paragraph + `i18n/hreflang.md#next-js--shadcn` production validation).
- **Fallback when not installed:** N/A — Playwright MCP is foundation-required. If unavailable, this is a Tier-1 system-integrity issue per `.claude/rules/tool-dependency-discipline.md`; the agent escalates immediately rather than degrading.

#### Optional MCPs (recommend conditionally per project shape)

##### Cloudflare MCP — when DNS is on Cloudflare (recommend at phase 28)

> **Two distinct Cloudflare MCPs exist** — pick the right one:
> - **`https://mcp.cloudflare.com/mcp`** (hosted OAuth): two-tool `search()` + `execute()` surface over 2,500+ Cloudflare API endpoints; DNS record CRUD available via `execute()`. Preferred for deploy phases needing DNS record creation.
> - **`github.com/cloudflare/mcp-server-cloudflare`** (open-source monorepo): 18 focused sub-servers; `dns-analytics` for traffic verification only. **Does NOT include a DNS-records-management sub-server** — for DNS record creation/CRUD, fall back to Cloudflare REST API + `wrangler` CLI.
>
> The hosted OAuth path below is the recommended default for this adapter at phase 28 (DNS record CRUD via `execute()`). The open-source monorepo's `dns-analytics` sub-server is a supplementary verification surface at phase 30 / 34.

- **Canonical URL:** https://developers.cloudflare.com/agents/model-context-protocol/mcp-servers-for-cloudflare/ (official Cloudflare-hosted set) + https://developers.cloudflare.com/agent-setup/claude-code/ (Claude Code setup). Verified 2026-05-20.
- **Maintainer + recency:** Cloudflare (official); also community options: `cloudflare-dns-mcp` (uv-based zero-install), `daniil-shumko/cloudflare-dns-mcp`, `@thelord/mcp-cloudflare`.
- **Install (Claude Code, OAuth, hosted):** Cloudflare hosts the official MCP server with OAuth — no API-key management on the user side. Per `developers.cloudflare.com/agent-setup/claude-code/`:
  ```bash
  claude mcp add --transport http cloudflare https://mcp.cloudflare.com
  ```
  First invocation triggers OAuth grant flow; user picks zones + permissions to expose.
- **Used by agent at:** phase **28** (DNS-record set when custom domain is on Cloudflare — CNAME/A/AAAA records, MX if user has email on the domain, TXT for verification + SPF) via the hosted-OAuth `execute()` tool. Cross-ref §"Deploy" Phase 28 DNS.
- **Fallback when not installed:** `Bash + curl` against Cloudflare REST API `https://api.cloudflare.com/client/v4/zones/{id}/dns_records` with a Cloudflare API token from `.env.local` (scoped to DNS-edit on the user's zone — never global). Or `wrangler` CLI for users who prefer Cloudflare's first-party tool. Or manual DNS-record set in the Cloudflare dashboard with agent emitting copy-paste instructions.

##### GitHub MCP — official, for git ops + PR automation (recommend at phases 28-30 + post-launch)

- **Canonical URL:** https://github.com/github/github-mcp-server (official GitHub MCP). Verified 2026-05-20.
- **Maintainer + recency:** GitHub (official). **The npm package `@modelcontextprotocol/server-github` is DEPRECATED as of April 2025** — use the official GitHub MCP instead. The agent surfaces this if the user has the deprecated one installed.
- **Install (Claude Code, HTTP + PAT):** CC 2.1.1+ format:
  ```bash
  claude mcp add-json github '{"type":"http","url":"https://api.githubcopilot.com/mcp","headers":{"Authorization":"Bearer YOUR_GITHUB_PAT"}}'
  ```
  Or Docker setup for `~/.claude.json` with `GITHUB_PERSONAL_ACCESS_TOKEN` env var (per github/github-mcp-server install docs). User creates a fine-grained PAT in GitHub Settings → Developer settings → Personal access tokens, scoped to the project's repo only.
- **Used by agent at:** phase **28** (initial repo push setup if the user doesn't have one yet), phase **29** (PR creation per `dev → master` workflow per `.claude/rules/git-and-deploy.md`), phase **30** (Dependabot / Renovate workflow file authoring + PR), **post-launch** (issue triage, security alerts from Dependabot, PR review automation for the user's maintenance loop). The Better Auth route, Stripe webhook signature verification fix, etc. — agent opens PRs against the user's repo via this MCP rather than asking the user to copy-paste from CC.
- **Fallback when not installed:** `gh` CLI (`gh pr create`, `gh issue list`, `gh repo view`) with `gh auth login` — covered by `git-and-deploy.md` for vault sister-repo work. Or `Bash + git` directly for the core push/pull/branch ops. Functional but loses PR-list-with-context + issue triage.

##### Stripe MCP — when `transactional=true` (mandatory for phase 24a/b/c)

- **Canonical URL:** https://docs.stripe.com/mcp + https://claude.com/plugins/stripe (Anthropic plugin catalog). Verified 2026-05-20.
- **Maintainer + recency:** Stripe (official MCP + the Anthropic Stripe Plugin which wraps it with subagents).
- **Install (Claude Code, plugin):**
  ```bash
  claude plugin install stripe@anthropic
  ```
  Or direct MCP without plugin wrapper — per `docs.stripe.com/mcp` install panel with one-click setup for Claude Code, Cursor, VS Code, etc. The Anthropic plugin path is preferred — it ships a `stripe-mcp` subagent CC automatically delegates to when the user asks about checkout / subscriptions / webhooks.
- **Used by agent at:** phase **24a** (Checkout Session creation pattern + recommended-API surface; surfaces Stripe-recommended best practices for Next.js Route Handlers in `app/api/checkout/route.ts`), phase **24b** (payment provider wiring incl. TWINT enable in Stripe Dashboard for Swiss audience), phase **24c** (legal-page Stripe-tax integration), **post-launch** (refund flows, subscription state, dispute response). Cross-ref §"Commerce integration".
- **Fallback when not installed:** Stripe Node SDK directly (`pnpm add stripe @stripe/stripe-js`) + agent codegens Route Handler from cached `docs.stripe.com` content. Functional but loses the "create a TWINT-enabled subscription Checkout Session with metadata" turn-around — agent has to compose from API-reference rather than ask the Stripe MCP for the canonical pattern.

##### Payload CMS MCP — when `cms=payload` (recommend at phase 12)

- **Canonical URL:** https://payload-plugin-mcp.vercel.app/ + https://github.com/antler-digital/payload-plugin-mcp (the official MCP plugin for Payload, authored by Antler Digital, indexed at lobehub). There is ALSO a separate `payloadcms/payload` Claude Code Skill at FastMCP — that's a skill (development guidance), not an MCP server. The MCP server is the Antler-Digital plugin which auto-generates MCP tools from your Payload collections. Verified 2026-05-20.
- **Maintainer + recency:** Antler Digital (community); active. Payload's own SKILL (development guidance) is maintained by Payload core team at `github.com/payloadcms/payload/CLAUDE.md` — separate concern.
- **Install (Payload v3 + Next.js project, Antler MCP plugin):** added as a plugin to Payload's config (not as a standalone MCP). After install, the plugin auto-generates MCP tools for every Payload collection (Pages, Posts, Media, etc.); agent calls them via `mcp__payload__<collection>_*` patterns. HTTP transport (NOT SSE) per the plugin docs.
- **Used by agent at:** phase **12** (CMS decision — surfaces Payload's structured-content + RBAC + drafts/versions feature surface to the user), phase **22** (Payload `localized: true` field-level i18n setup), **post-launch** (content seeding from `.website-builder/content/pages/*.md` to Payload collections via the auto-generated MCP tools — bulk-import pattern).
- **Fallback when not installed:** Payload's Local API directly (Payload v3 runs in the same Next.js app, so the agent can call `payload.create()` / `payload.find()` from Server Components or scripts). Or the REST API at `/api/<collection>` for cross-process access. Functional; agent loses the MCP's auto-generated tool descriptions but retains full programmatic access.

##### Decap CMS MCP — **no MCP currently exists (negative finding)**

- **Canonical search:** WebSearch `"Decap CMS" MCP server Model Context Protocol Claude 2026` returned zero matches for a Decap-specific MCP. Verified 2026-05-20. The MCP ecosystem highlights Webflow MCP as the surveyed CMS option; Decap is absent.
- **Why this matters:** the agent does NOT keep searching at runtime — there isn't one. Decap is **git-backed** (commits to user's repo via the `/admin` UI); CMS operations are git operations, not API operations. The git/GitHub MCP path covers most of what a Decap MCP would offer (commit auditing, branch protection on `master`).
- **Fallback (canonical path):** Decap's own `/admin` UI for user-facing edits + GitHub MCP (or `gh` CLI) for git-side observation. Agent's phase-12 + post-launch flow uses these directly.

##### next-intl MCP — **no MCP currently exists (negative finding)**

- **Canonical search:** WebSearch `"next-intl" MCP server Model Context Protocol Claude Code 2026` returned zero matches. Verified 2026-05-20. next-intl is a library, not a service — the only "API surface" is the file-based `messages/{lang}.json` files + the i18n config files, which the agent edits directly via `Edit`/`Write` tools.
- **Fallback (canonical path):** N/A — there's no API to fall back from. Agent reads + edits `messages/{lang}.json` + `i18n/request.ts` + `i18n/routing.ts` + `i18n/navigation.ts` files directly via `Edit`/`Write`. For freshness on next-intl API surface, context7 `/amannn/next-intl` (verify via `resolve-library-id` at phase 22 entry) covers the docs side.

##### Supabase MCP — official (recommend when user picks Supabase Postgres for Payload or Better Auth)

- **Canonical URL:** https://supabase.com/docs/guides/ai-tools/mcp (official) + https://github.com/supabase-community/supabase-mcp. Verified 2026-05-20. Supabase is now an official Claude connector (per `supabase.com/blog/supabase-is-now-an-official-claude-connector` 2026).
- **Maintainer + recency:** Supabase (official). Moved to HTTP transport with OAuth in 2026.
- **Install (Claude Code, OAuth via Claude.ai connector OR Claude Desktop connectors menu):** for CC specifically:
  ```bash
  claude mcp add --transport http supabase https://api.supabase.com/mcp
  ```
  Browser OAuth flow → user selects which Supabase organization + project to expose.
- **Used by agent at:** phase **12** (when CMS=Payload + Postgres hosting → Supabase Postgres), phase **22** (forms with Supabase as backend for non-payload-CMS sites), phase **29** (deploy — env var propagation + DB connection-string into Vercel via Vercel MCP). 32 tools cover DB management (SQL execution, schema design, list tables), project ops (list/create projects, cost estimates), branching/migrations (dev branches, merge changes), storage, edge functions.
- **Critical safety note:** Supabase MCP is "designed for development and testing purposes; never connect the MCP server to production data." Agent surfaces this at install time + refuses to apply schema migrations directly against the production project via MCP (uses the `prepare_database_migration` + `complete_database_migration` two-phase pattern instead).
- **Fallback when not installed:** Supabase JS SDK (`@supabase/supabase-js`) for runtime; `supabase` CLI for migrations + schema; psql for direct DB access. Functional; loses the MCP's natural-language schema-design turn-around.

##### Neon MCP — official (recommend when user picks Neon Postgres for Payload or Better Auth)

- **Canonical URL:** https://neon.com/docs/ai/neon-mcp-server (official) + https://github.com/neondatabase/mcp-server-neon. Verified 2026-05-20.
- **Maintainer + recency:** Neon Database (official).
- **Install (Claude Code, OAuth remote OR API-key stdio):** Remote (preferred):
  ```bash
  claude mcp add --transport http neon https://mcp.neon.com/mcp
  ```
  OAuth flow → user picks Neon project. API-key alternative for stdio: pass `NEON_API_KEY` from `.env.local`.
- **Used by agent at:** phase **12** (when CMS=Payload + Postgres hosting → Neon, often the muggle-friendly default since Neon scales-to-zero on Hobby tier; the agent drafts `.website-builder/decisions/cms-12-payload-postgres-host.md` at this moment), phase **29** (deploy — `pnpm payload migrate` runs against the Neon connection string; agent uses Neon's `prepare_database_migration` + `complete_database_migration` two-phase pattern for safer schema changes via temporary branches), **post-launch** (schema evolution via natural-language requests).
- **Safety note:** Same as Supabase — Neon MCP is for development/IDE integration only, not production. Agent applies migrations to a temporary branch first; user confirms before promotion to production branch (Neon's `prepare/complete` pattern handles this).
- **Fallback when not installed:** Neon CLI (`neonctl`) for project/branch ops + psql for direct DB access; Drizzle/Prisma migration runners for schema. Functional; loses the temporary-branch safety pattern + natural-language interface.

##### Sentry MCP — official (recommend at phase 34 post-launch monitoring)

- **Canonical URL:** https://docs.sentry.io/product/sentry-mcp/ (official) + https://mcp.sentry.dev/mcp (hosted endpoint). Verified 2026-05-20.
- **Maintainer + recency:** Sentry (official). Cloud + local stdio transports both supported.
- **Install (Claude Code, plugin):**
  ```bash
  claude plugin marketplace add getsentry/sentry-mcp
  claude plugin install sentry-mcp@sentry-mcp
  ```
  This installs the plugin + a `sentry-mcp` subagent CC delegates to automatically for Sentry-related queries. Or HTTP transport directly:
  ```bash
  claude mcp add --transport http sentry https://mcp.sentry.dev/mcp
  ```
  OAuth flow on first invocation.
- **Used by agent at:** phase **30** (configure Sentry SDK in the Next.js project — `pnpm add @sentry/nextjs` + `sentry.client.config.ts` + `sentry.server.config.ts`), phase **34** (monitoring cadence + alert thresholds + first-issue triage), **post-launch** (issue investigation — agent reads stack trace + event details + tags via `search_issues` / `search_events` and proposes fixes; Seer analysis for AI-suggested root cause).
- **Fallback when not installed:** Sentry web UI + Sentry CLI for source-map upload + `@sentry/nextjs` SDK directly for runtime instrumentation. Functional; loses the agent's ability to investigate issues directly from CC.

##### GA4 / Plausible MCPs — when user picks third-party analytics (recommend at phase 30)

- **GA4 — community options (no single official):** `surendranb/google-analytics-mcp` (open-source, comprehensive); Stape's hosted `https://mcp-ga.stape.ai/mcp` (managed); Cogny's managed remote MCP with OAuth (no GCP project needed); `mario-hernandez/google-analytics-mcp-claude-code` (read-only with anti-hallucination provenance + diagnostic SEO/marketing intelligence). Verified 2026-05-20. Pick based on user's existing GA4 setup posture.
  - Install (Stape remote, no install dance):
    ```bash
    claude mcp add --transport http ga4 https://mcp-ga.stape.ai/mcp
    ```
- **Plausible MCP:** **Preferred — `getsentry/plausible-mcp`** (https://github.com/getsentry/plausible-mcp; under Sentry's umbrella; last push 2026-05-13; multi-tenant; Stats API v2) — the more recently maintained of the available Plausible MCPs as of 2026-05-20. Peer alternatives: Plausible Skill (https://mcpmarket.com/tools/skills/plausible-analytics) and community `alexanderop/plausible-mcp` (https://github.com/alexanderop/plausible-mcp, MIT — older / less actively maintained). All env-var-driven API key + URL configuration. Verified 2026-05-20.
  - Install (preferred, getsentry):
    ```bash
    claude mcp add plausible -- npx -y @getsentry/plausible-mcp
    ```
    Then set `PLAUSIBLE_API_KEY` + `PLAUSIBLE_SITE_ID` in `.env.local`.
  - Install (peer alternative, alexanderop / MIT):
    ```bash
    claude mcp add plausible -- npx -y plausible-mcp
    ```
    Then set `PLAUSIBLE_API_KEY` + `PLAUSIBLE_SITE_ID` in `.env.local`.
- **Used by agent at:** phase **30** (analytics injection — surfaces traffic, page-views, source attribution, conversion goals; agent uses these to verify analytics is actually firing post-deploy), phase **34** (weekly monitoring review cadence — query traffic trends, anomaly detection, top pages, traffic source shifts; for GA4 community `mario-hernandez` server's anomaly-detection + traffic-drop classification surfaces are directly useful in this loop).
- **Fallback when not installed:** Plausible/GA4 web dashboards + their respective REST APIs via `Bash + curl` for scripted queries. Functional; loses the agent's natural-language anomaly investigation.

##### Cal.com MCP — when `transactional=true` AND `transactional_kind in [bookings, both]` (recommend at phase 24a)

- **Canonical URL:** https://cal.com/blog/how-to-connect-calcom-to-claude-using-mcp (official setup guide) + Cal.com's custom-connector flow in Claude. Verified 2026-05-20.
- **Maintainer + recency:** Cal.com (official); no installation — added as a custom connector inside Claude with OAuth-style permission granting.
- **Install:** Per cal.com/blog/how-to-connect-calcom-to-claude-using-mcp — add Cal.com as a custom connector via Claude's connectors UI. No CC config file edit; Cal.com MCP is invoked through Claude's connector layer.
- **Used by agent at:** phase **24a** (booking-platform setup — Cal.com is decision-54 MVP default booking provider for the Next.js stack), **post-launch** (booking-state queries, event-type CRUD, availability updates).
- **Fallback when not installed:** Cal.com Atoms (`@calcom/atoms`) for embedding + Cal.com REST API directly via `Bash + curl` for booking ops. Functional; loses natural-language booking-state queries.

##### Image-generation MCPs — when phase 8 image-gen runs locally (recommend conditionally)

- **Canonical:** Multiple community options exist; no single official:
  - `guinacio/claude-image-gen` (Gemini-only; CC Skills + MCP) — https://github.com/guinacio/claude-image-gen
  - `lansespirit/image-gen-mcp` (gpt-image-1 + Gemini Imagen4) — https://github.com/lansespirit/image-gen-mcp
  - `@fastmcp-me/imagegen-mcp` (npm; multi-provider DALL-E + Gemini + Replicate Flux)
  - MCP-Imagenate (Gemini + GPT + FLUX; hit 1000 npm downloads in 4 days)
- **Maintainer + recency:** All community-maintained as of 2026-05-20; no Anthropic-official image-gen MCP.
- **Install (lansespirit, multi-provider):**
  ```bash
  claude mcp add imagegen -- npx -y @fastmcp-me/imagegen-mcp
  ```
  Set provider API keys in `.env.local` (`OPENAI_API_KEY`, `GEMINI_API_KEY`, `REPLICATE_API_TOKEN` per the provider(s) user chose).
- **Used by agent at:** phase **8** (image direction — when user wants generated hero / product / illustration images rather than stock photo or photographer-shot), **post-launch** (image refresh via `consumers/image-gen.md`). Per locked decision 56 the plugin uses the consumer-fallback path (user provides their own keys) so this is opt-in.
- **Fallback when not installed:** Direct API calls to Gemini / OpenAI / Replicate via `Bash + curl` with user-provided keys; or user generates images in the provider's web UI and pastes into `public/images/`. Functional; loses the inline-generation turn-around.

#### Negative findings — explicitly NO MCP at this surface

These are documented so the agent doesn't keep searching at runtime:

| Surface | Negative-finding status (2026-05-20) | Canonical fallback |
|---|---|---|
| **Decap CMS MCP** | No MCP exists. Decap is git-backed; ops are git ops. | `/admin` UI + GitHub MCP / `gh` CLI for git-side observation. |
| **next-intl MCP** | No MCP exists. next-intl is a library — file-based, no API surface. | Direct `Edit`/`Write` on `messages/{lang}.json` + `i18n/*.ts`. context7 `/amannn/next-intl` for docs freshness. |
| **MDX MCP** | No MCP exists. MDX is a parser/compiler; no service surface to talk to. | `@next/mdx` config in `next.config.mjs` + agent reads MDX with frontmatter via standard fs. |
| **Tailwind CSS MCP** | No dedicated MCP found at the time of this audit. Tailwind is a build-time tool, not a service. | context7 `/tailwindlabs/tailwindcss.com` for docs freshness; `tailwind.config.ts` + `app/globals.css` via direct edit. |
| **Better Auth MCP** | No dedicated MCP found at the time of this audit (Better Auth is library-only). | Direct integration via the SDK + Supabase/Neon MCP for the underlying DB. |
| **Anthropic-official image-gen MCP** | None — only community-maintained options. | Community `@fastmcp-me/imagegen-mcp` OR direct provider API. |

#### Setup discipline

- **None of these are bundled by the website-builder plugin.** Each user installs the MCPs they need; the agent uses them when present.
- **First-run setup walk at phase 11:** the agent enumerates the **mandatory** core MCPs (Vercel + shadcn) + the conditional ones the user's project shape requires (Cloudflare if DNS-on-Cloudflare; Stripe if transactional; Payload if CMS=Payload; Supabase/Neon if Postgres-backend; Sentry/GA4/Plausible at phase 30; Cal.com if booking) and surfaces install commands for the user to run before phase 28.
- **The agent NEVER pretends an MCP exists when it doesn't.** Per the negative-findings table, the agent uses the fallback path documented above without keep-searching the registry. Per `.claude/rules/tool-dependency-discipline.md` Tier 2, MCP unreachability surfaces explicitly + falls back with the fallback path noted; the agent does not silently degrade.

## Migration recipe

Pre-step-11 canonical `.website-builder/` → Next.js project structure. Run once at phase 11+ when the stack is locked.

```
.website-builder/                            →  user-website-project/ (Next.js App Router)
├── content/pages/{slug}.md                  →  content/pages/{slug}.mdx
│                                                (MDX frontmatter; loaded via contentlayer OR
│                                                 fumadocs OR hand-rolled fs+gray-matter — agent
│                                                 picks at phase 12 alongside CMS decision)
├── content/pages/{slug}.{lang}.md           →  content/pages/{lang}/{slug}.mdx
│                                                (per-locale subdir; routed via app/[lang]/...)
├── content/strings/{lang}.json              →  messages/{lang}.json
│                                                (loaded via next-intl per §"i18n integration")
├── content/sections.yaml                    →  lib/sections.ts (TypeScript types) +
│                                                components/sections/{Section}.tsx (one
│                                                component per section type; agent-generated
│                                                at phase 18)
├── components.yaml + components/code        →  components/{ComponentName}.tsx
│                                                (React components with TypeScript types from
│                                                 components.yaml; agent writes from spec at
│                                                 phase 18 — composes shadcn primitives)
├── brand.yaml.tokens                        →  app/globals.css + tailwind.config.ts
│                                                (CSS custom properties from OKLCH tokens in
│                                                 :root / .dark + `@theme inline` mapping
│                                                 declaring Tailwind utilities — see §"Component
│                                                 library pairing" for the shadcn pattern)
├── sitemap.yaml                             →  app/[lang]/{slug}/page.tsx (one per route per
│                                                language) + app/sitemap.ts (programmatic
│                                                sitemap.xml) + app/robots.ts (programmatic
│                                                robots.txt)
├── decisions/                               →  decisions/ (kept in repo as historical record)
├── audit/                                   →  audit/ (kept in repo)
├── media/                                   →  public/images/, public/videos/
│                                                (Vercel serves; or Vercel Blob / Cloudflare R2
│                                                 for larger media)
├── briefs/, outputs/                        →  .website-builder/briefs/, outputs/
│                                                (kept in repo; not deployed — `.gitignore` or
│                                                 read-only mirror via deploy hook)
└── (project files)                          →  package.json, tsconfig.json, next.config.mjs,
                                                 tailwind.config.ts, .env.local, etc.
```

**Key insight (this is the muggle-shift):** unlike Framer / Webflow / WordPress, Next.js is **just code in the user's repo.** The agent writes `.tsx`/`.mdx` files; git is the version control; Vercel is the deploy target. `.website-builder/` stays as the canonical pre-step-11 state alongside the actual website code; the agent maintains sync between them. When the user edits an MDX file directly (post-launch), the agent re-syncs to `.website-builder/content/pages/{slug}.md` via phase 6.5 if requested, or keeps both in sync via the session-start hook.

**MDX loader picked at phase 12** (CMS decision): `none` → hand-rolled `fs` + `gray-matter` + `@next/mdx`; `decap` → same plus Decap admin UI at `/admin`; `payload` → Payload's collection-driven page model (MDX as a richtext-lexical-rendered field). See §"CMS pairing".

## Content layer mapping

| Layer | Next.js + shadcn native concept |
|---|---|
| **L1 brand.yaml.tokens** | OKLCH CSS custom properties in `app/globals.css` `:root` + `.dark` blocks, mapped to Tailwind utilities via `@theme inline { --color-x: var(--x) }`. `tailwind.config.ts` references `@theme inline` declarations. shadcn `components.json` `tailwind.cssVariables: true` is the integration pattern. |
| **L2 sitemap.yaml + sections.yaml** | App Router `app/[lang]/{slug}/page.tsx` (one route per page per language) + `lib/sections.ts` TypeScript types + `components/sections/{Section}.tsx` React Server Components (one per section type, Server unless interactivity needed) |
| **L3 strings/{lang}.json** | `messages/{lang}.json` consumed via `next-intl` (`useTranslations()` hook in components; `getTranslations()` in Server-Component async functions); loaded per locale via `getRequestConfig()` in `i18n/request.ts` |
| **L4 content/pages/*.md** | `content/pages/{lang}/{slug}.mdx` (Pattern A — shared structure, translated prose, default per decision 39) OR loaded by chosen CMS adapter at phase 12 (`@next/mdx` direct; Decap git-backed admin; Payload `pages` collection with field-level `localized: true`) |
| **L5 briefs/{component}.json** | `components/{ComponentName}.tsx` (the React component the brief targets) PLUS `.website-builder/briefs/{component}-{ts}.json` (the brief artifact itself, kept in repo for iteration history per `DESIGN-content-layers.md` Layer 5) |

The table is the BUILD-strategy.md Phase 3 DoD verification anchor — comparing this row-by-row to `adapters/stack-framer.md` and `adapters/stack-wordpress.md` proves that "same `.website-builder/` content produces equivalent sites on all 3 stacks (modulo platform-specific limitations)" per BUILD-strategy.md line 181.

## i18n integration

**Library:** `next-intl` (https://next-intl-docs.vercel.app/) — the most popular and best-maintained Next.js i18n library, App Router-aware, mature. Verified live at context7 `/amannn/next-intl` at phase-11 entry per `skills/wb-architecture/references/context7-protocol.md`; the agent re-fetches if cached docs are >30 days old.

**Routing-strategy default:** prefix (per locked decision 38 in `DESIGN-i18n.md`). next-intl ships routing helpers for prefix routing via the `[lang]` dynamic segment in App Router.

**Per-language pages pattern:** Pattern A — shared structure across languages, prose translated (default per locked decision 39).

**Translation workflow:** Pattern 1 — agent translates `messages/{lang}.json` + per-locale MDX inline at phase 16 (default per locked decision 40). Pattern 2 (translator handoff via brief) flows through phase 6.5 ingestion when project surfaces brand/legal/commercial sensitivity.

**Setup:**

```bash
pnpm add next-intl
```

```ts
// next.config.mjs
import createNextIntlPlugin from 'next-intl/plugin';
const withNextIntl = createNextIntlPlugin('./i18n/request.ts');

/** @type {import('next').NextConfig} */
const nextConfig = { /* other config */ };
export default withNextIntl(nextConfig);
```

```ts
// i18n/request.ts (canonical App Router dynamic-import pattern — verified context7 2026-05-18)
import { getRequestConfig } from 'next-intl/server';
import { routing } from './routing';

export default getRequestConfig(async ({ requestLocale }) => {
  let locale = await requestLocale;
  if (!locale || !routing.locales.includes(locale)) {
    locale = routing.defaultLocale;
  }
  return {
    locale,
    messages: (await import(`../messages/${locale}.json`)).default,
  };
});
```

```ts
// i18n/routing.ts
import { defineRouting } from 'next-intl/routing';

export const routing = defineRouting({
  locales: ['en', 'de', 'fr', 'it'],
  defaultLocale: 'en',
});
```

```tsx
// app/[lang]/layout.tsx — Server Component
import { NextIntlClientProvider } from 'next-intl';
import { getMessages, setRequestLocale } from 'next-intl/server';
import { notFound } from 'next/navigation';
import { routing } from '@/i18n/routing';

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ lang: locale }));
}

export default async function RootLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ lang: string }>;
}) {
  const { lang } = await params;
  if (!routing.locales.includes(lang)) notFound();
  setRequestLocale(lang);
  const messages = await getMessages();
  return (
    <html lang={lang} dir={['ar', 'he', 'fa', 'ur'].includes(lang) ? 'rtl' : 'ltr'}>
      <body>
        <NextIntlClientProvider messages={messages}>{children}</NextIntlClientProvider>
      </body>
    </html>
  );
}
```

```tsx
// Any Server or Client Component
import { useTranslations } from 'next-intl';
export function HeroBlock() {
  const t = useTranslations();
  return <h1>{t('home.hero.headline')}</h1>;
}
```

**Strings (Layer 3):** `messages/{lang}.json` mirrors `.website-builder/content/strings/{lang}.json`. The agent maintains a one-way sync from `.website-builder/` → `messages/` at phase 16 (and on every subsequent phase-6.5 ingestion of new strings).

**Pages (Layer 4):** per-locale MDX files at `content/pages/{lang}/{slug}.mdx`; the dynamic `[lang]` segment loads the right file via `generateStaticParams()` + a per-locale loader function in `lib/content.ts`.

**Language switcher:** see `i18n/language-switcher.md#next-js--shadcn` for the per-stack implementation (shadcn `DropdownMenu` for ≥4 languages; inline buttons for 2-3 languages).

**hreflang:** see `i18n/hreflang.md#next-js--shadcn` for the per-stack emission (Next.js `generateMetadata()` → `alternates.languages` map). Verified at phase 26 (SEO audit).

**RTL:** `dir="rtl"` set on `<html>` for RTL locales (see layout snippet above); CSS uses logical properties (`margin-inline-start`, `padding-inline-end`); Tailwind 4+ has built-in RTL utilities via the `rtl:` variant. Agent uses these from phase 18 onward, making RTL "free" for simple cases. Complex bidirectional content (mixed LTR/RTL on same page, form inputs with bidi text) tested at phase 20 via Playwright with locale set to an RTL language. See `i18n/rtl.md` (stack-agnostic) for the broader discipline.

**Date / Number / Currency formatting:** next-intl ships `useFormatter()` wrapping `Intl.DateTimeFormat` + `Intl.NumberFormat`; agent uses these throughout instead of hardcoding format strings. Strings file's `dates.format_short` / `dates.format_long` keys are reference patterns the formatter consumes.

## Phase 6.5 ingestion

Phase 6.5 fires when entry mode is `has-existing-site` on a Next.js project, `has-ai-output` from v0 / Cursor / ChatGPT (output is Next.js + shadcn + Tailwind by default), or at any project lifecycle point when the user pastes a new artifact. See `Workstreams/website-builder/foundation/DESIGN-ingestion-and-extraction.md` for the cross-stack phase-6.5 mechanism.

**Primary MCP:** the **Playwright MCP** (foundation-bundled — see §"Auth + setup" → `### MCP servers` → Playwright MCP) drives the deployed-site walk in step 3 of the walk procedure below. No fallback path — Playwright MCP is Tier-1 infrastructure for this stack adapter; absence escalates per `.claude/rules/tool-dependency-discipline.md`.

### Per-entry-mode extraction tool choices

| Entry artifact | Primary extractor | Secondary | Cross-reference |
|---|---|---|---|
| **Deployed Next.js site (URL)** | Playwright walker (`extraction/playwright-walk.md`) — paired with Stitch for design-token extraction | divmagic for element-level precision | `extraction/playwright-walk.md`, `extraction/stitch.md` |
| **AI-generated React/JSX/TSX code paste** | AI-output parser (`extraction/ai-output.md`) — parses JSX AST, extracts Tailwind classes → tokens, extracts text nodes → strings + prose | — | `extraction/ai-output.md` |
| **v0 export (Next.js project)** | AI-output parser (recognizes v0's shadcn + Tailwind + Next App Router shape) — straight-line normalization | — | `extraction/ai-output.md` |
| **Cursor / ChatGPT one-shot landing-page output** | AI-output parser (JSX or HTML); if HTML, secondary Stitch run for design tokens | — | `extraction/ai-output.md`, `extraction/stitch.md` |
| **Figma file** | Figma design-to-json plugin (user runs in Figma, pastes output) | — | `extraction/figma-design-to-json.md` |

### Walk procedure (deployed Next.js site)

1. **Read `package.json`** to detect Next.js version, App Router vs Pages Router (refuse to ingest Pages Router projects without explicit user acceptance — they're legacy; agent surfaces migration cost), key dependencies (next-intl, shadcn, Tailwind, MDX loader, CMS, commerce SDKs).
2. **Walk file structure** to identify routes (`app/[lang]/...` vs `app/...`), components (`components/ui/` is shadcn-resident; `components/{Custom}.tsx` is user code; `components/magicui/` is animation companion), content (MDX or external CMS), config files (`next.config.mjs`, `tailwind.config.ts`, `i18n/request.ts`, `i18n/routing.ts`).
3. **Playwright walks the deployed site** (if deployed) at desktop 1280 + tablet 768 + mobile 360 viewports — captures rendered output per breakpoint, hovers/scrolls to trigger animations, surfaces auth-walled pages.
4. **Stitch / divmagic extraction (optional)** for cross-validation against the project's `tailwind.config.ts` + `app/globals.css` OKLCH tokens.
5. **Normalize into `.website-builder/` project state:**
   - Tailwind theme + globals.css OKLCH vars → `brand.yaml.tokens` (Layer 1)
   - Routes from `app/[lang]/...` → `sitemap.yaml` (Layer 2)
   - JSX text content + MDX bodies → `content/pages/{slug}.md` per `[lang]` (Layer 4)
   - JSX component structure → `components.yaml` + the agent retains live code reference (Layer 5 round-trip)
   - `messages/{lang}.json` → `content/strings/{lang}.json` (Layer 3)
6. **Conflict resolution** per locked decision 36 default: halt + force user decision per conflict; no silent merge or overwrite (see `DESIGN-ingestion-and-extraction.md` § "Conflict resolution patterns").
7. **Decision log** at `.website-builder/decisions/ingest-nextjs-{timestamp}.md`.

### Auth-walled handling

If the deployed site requires login (Better Auth, NextAuth, custom JWT, etc.), the user provides credentials; Playwright authenticates; walks the authenticated state. The agent NEVER stores user credentials — they're entered into the Playwright session live and discarded after the walk.

### Round-trip ingestion (phase-18 component handoff)

The "mom's pattern" common case: user wants a new section, generates it in v0 (or ChatGPT, or Cursor), pastes the output back. The agent emits a phase-18 brief targeting `react-shadcn-tailwind` (the canonical Next.js + shadcn flavor); user pastes the brief into v0 / ChatGPT / Cursor; gets `.tsx` output back; pastes to `.website-builder/outputs/{component}-{ts}.tsx`; phase 6.5 ingests via the AI-output parser, normalizes the JSX, integrates as a new file under `components/{ComponentName}.tsx`, updates `components.yaml`, updates the relevant `sections.yaml` entries, updates `content/pages/{slug}.md` if new strings or new section refs surfaced. Cross-references: `handoff-spec/component-request-v1.md` + `handoff-spec/component-output-v1.md`.

### Common AI-output ingestion case (v0)

v0 (Vercel's design tool) outputs Next.js + shadcn + Tailwind by default — perfect fit for this stack. Agent ingests directly: walks file structure, recognizes shadcn `components/ui/` primitives, recognizes Tailwind utility classes, normalizes OKLCH theme tokens from `globals.css`, integrates with existing project state. If v0 used Tailwind v3 patterns and the project is on v4 (or vice versa), the agent migrates utility-class syntax (e.g., `text-gray-900` → `text-foreground` semantic token) at ingest time and logs the migration in the decision file.

## Commerce integration (if transactional=true)

Next.js + Vercel pairs cleanly with most commerce platforms. Phase 24a (commerce platform setup) + 24b (payment provider wiring) + 24c (commerce-specific legal) branching per `phase-contracts/24a/b/c`.

**MCP integrations** (per §"Auth + setup" → `### MCP servers`): **Stripe MCP** (`claude.com/plugins/stripe` — official; ships a `stripe-mcp` subagent) recommended at phase 24a for Checkout / Subscription / Webhook best-practice patterns. **Cal.com MCP** (custom Claude connector — no install command) recommended at phase 24a when `transactional_kind in [bookings, both]`. Fallbacks: Stripe Node SDK + Cal.com Atoms + REST APIs documented per-MCP entry in §"Auth + setup".

### Phase 24a — Commerce platform setup

| Platform | When to recommend | Integration pattern |
|---|---|---|
| **Stripe Checkout / Payment Links** *(primary default)* | Most muggle-friendly; minimal code; no PCI complications | `app/api/checkout/route.ts` creates Stripe Checkout Sessions; client `<Link>` redirects to Stripe-hosted page; webhook handler at `app/api/stripe-webhook/route.ts` updates order state |
| **Lemon Squeezy** *(second default)* | Merchant-of-Record (handles VAT/tax for digital products in EU) — best for solo creators selling digital products globally | SDK + webhooks; agent integrates per https://docs.lemonsqueezy.com/api |
| **Shopify Hydrogen Storefront API** | When user wants Shopify backend + Next.js frontend (not Hydrogen itself — Hydrogen is Remix-based) | Apollo / graphql-request against Shopify Storefront GraphQL API |
| **Snipcart** | Drop-in cart for content-led sites that need a checkout without backend complexity | Custom-element injection in client component; minimal Next.js plumbing |
| **Paddle** | B2B SaaS billing with subscription management + tax compliance | SDK in `app/api/paddle-webhook/route.ts` + Paddle.js for inline checkout |
| **WooCommerce headless** | When user has existing WP content + commerce; Next.js is the frontend | Next.js consumes WP REST API or WPGraphQL — note this makes the actual stack pairing "WordPress + Next.js"; agent flags the architecture trade-off |
| **Saleor** | Open-source GraphQL commerce, full backend control | Apollo client or graphql-request to Saleor's GraphQL endpoint |

The MVP default per BUILD-strategy.md Phase 4 (decision 54) is **Stripe Checkout** — covers TWINT for Swiss audience via Stripe Dashboard's TWINT-enable toggle (no per-payment-method code change required).

### Phase 24b — Payment provider wiring

| Provider | Use when | Notes |
|---|---|---|
| **Stripe** *(primary)* | Default for most projects; TWINT for Swiss audience via Stripe Dashboard toggle | `pnpm add stripe @stripe/stripe-js`; env vars `STRIPE_SECRET_KEY` + `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`; webhook at `app/api/stripe-webhook/route.ts` with `stripe.webhooks.constructEvent()` |
| **Mollie** | EU-friendly; broader EU payment-method coverage (iDEAL, Bancontact, etc.) | `pnpm add @mollie/api-client` |
| **PayPal** | When user explicitly requests PayPal coverage | `pnpm add @paypal/react-paypal-js` for client + REST API for server |
| **TWINT (Switzerland)** | Swiss-audience sites | Via Stripe — enable in Stripe Dashboard; no Next.js code change beyond Stripe baseline |
| **Square** | US-centric POS-integrated commerce | `pnpm add square` |
| **Klarna** | Buy-now-pay-later for consumer commerce | Via Stripe (Klarna BNPL enabled in Dashboard) OR direct Klarna integration |

Decision tree per `Workstreams/website-builder/foundation/DESIGN-ecosystem-catalog.md` payment-providers section.

### Phase 24c — Commerce-specific legal

Refund policy / shipping terms / T&Cs / privacy / cookie notice as MDX pages at `content/pages/legal/*.mdx`. Linked from checkout flow. Per-locale variants for multilingual sites. Stripe Checkout's hosted-page UI links to these via the Checkout Session configuration.

### Booking flows

Cal.com / Calendly / SimplyBook.me embedded as React components using their official SDKs:

- **Cal.com** *(MVP default per decision 54)* — `pnpm add @calcom/embed-react` for inline + popup embeds; works in both Server-rendered routes (popup) and Client components (inline)
- **Calendly** — `pnpm add react-calendly`
- **SimplyBook.me** — iframe embed

## CMS pairing

Phase 12 (CMS decision) picks per project complexity. The MVP triplet (locked decision 53) is **none / Decap / Payload**, plus expansion options:

**MCP integrations** (per §"Auth + setup" → `### MCP servers`): **Payload CMS MCP** (Antler Digital — auto-generates MCP tools from Payload collections; HTTP transport) recommended when `cms=payload`. **Decap CMS has NO MCP** (git-backed; ops route through GitHub MCP / `gh` CLI). **`cms=none`** has no CMS-specific MCP need.

| CMS | When to recommend | Anti-fit | Hosting |
|---|---|---|---|
| **none (file-based MDX)** *(default for content-light sites)* | 5-15 pages, infrequent updates, user is OK editing MDX directly | Multiple editors needing role-based access; non-developer editorial workflow | Same as Next.js (Vercel) |
| **Decap CMS** | Git-backed visual editing; admin UI at `/admin`; commits land in user's repo; works for non-developer editors who can tolerate a basic UI | Heavy structured content (relations across content types); WYSIWYG-heavy editorial workflow. **Decap upstream state — verify current at phase 12 via context7** (re-verified 2026-05-20: Decap revitalized with v3.12.2 April 2026 active cadence; Sveltia CMS active fork; Static CMS archived 2024-09-09 — drop from recommendations) | Same as Next.js (Vercel) — Decap is static |
| **Payload CMS** *(vault-canonical pick — decision 53)* | TypeScript-first; runs in same Next.js app (Payload v3 is Next-native — one-line install via `@payloadcms/next`); structured content + relations; drafts + versions; live preview; RBAC; the user wants a real CMS without leaving the Next.js stack | Tiny content-light sites where it's overkill | **Postgres separately needed** — Neon / Supabase / Railway / self-hosted; flag at phase 12 + draft `.website-builder/decisions/cms-12-payload-postgres-host.md` for phase 29 readiness |
| **Sanity** *(expansion)* | Structured content + GROQ queries; great for content-heavy sites with editorial teams; managed SaaS | Solo muggle who doesn't want a separate SaaS account | Sanity Cloud (managed) |
| **TinaCMS** *(expansion)* | MDX + visual editing; cloud-hosted or self-hosted | Sites without an editorial team | Tina Cloud or self-host |
| **Contentful** *(expansion)* | Managed SaaS; mature; team has structured-content workflow already | Solo creators; tier pricing for muggles is awkward | Contentful Cloud |
| **Strapi** *(expansion)* | Open-source; UI-first content-type builder | Sites that don't want a separate Node service | Self-hosted Node / Strapi Cloud |
| **Ghost** *(expansion)* | Newsletter + blog primary; minimal CMS surface | Sites that aren't newsletter-led | Ghost Pro or self-host |
| **Headless WordPress** *(expansion)* | User has existing WP content they don't want to migrate | New projects (use WP-as-stack instead) | WP host (managed-WP / VPS) |

**Default for muggle:** Decap CMS for content-light sites (sites with <15 pages, ~quarterly updates); Payload for content-heavy sites (editorial teams, multiple editors, structured relationships). The agent surfaces both at phase 12 and walks the trade-offs honestly.

**Decap upstream verification (cite to user at phase 12):** The agent verifies current upstream + fork state via context7 + WebFetch at phase 12. Current state (re-verified 2026-05-20 per Captain J Phase-4 research): **Decap is in active maintenance** (v3.12.2 April 2026); the sole active fork is **Sveltia CMS** (https://github.com/sveltia/sveltia-cms); **Static CMS is archived** (2024-09-09, https://github.com/StaticJsCMS/static-cms). The agent recommends Decap by default + names Sveltia as a Svelte-based alternative; escalates to Payload only when structured content needs exceed Decap's `list + types` shape.

**i18n strategy locked at phase 12** for multilingual sites (per `wb-architecture/SKILL.md` line 87): Decap → `structure: multiple_files` config; Payload → field-level `localized: true` + `localization.fallback: true`. None → per-locale MDX files at `content/pages/{lang}/{slug}.mdx` (the default migration recipe in §"Migration recipe").

Per-CMS deep recipes: `Workstreams/website-builder/cms/DESIGN-cms-{none,decap,payload}.md` (full coverage authored separately).

## Component library pairing

**Default per decision 55 + BUILD-strategy: shadcn/ui** — primary default for Next.js. Verified live at context7 `/shadcn-ui/ui` 2026-05-18 (open-code copy-paste, Tailwind v4 + React 19, OKLCH semantic CSS-variable theming via `@theme inline`).

Cross-reference for codegen detail: `skills/wb-component-build/references/per-stack-codegen.md#nextjs` (Phase 2.B read-only anchor — the agent reads this verbatim at phase 18 entry alongside this section).

**MCP integration** (per §"Auth + setup" → `### MCP servers` → shadcn/ui MCP): the official `shadcn` MCP (https://ui.shadcn.com/docs/mcp) is mandatory at phase 18 for natural-language component install + block scaffolding. Fallback to `npx shadcn@latest add <name>` CLI when MCP not installed (functional; loses "install the dashboard-01 block + all dependencies in one turn" surface).

### Why shadcn is the default

| Reason | Detail |
|---|---|
| **User owns the code** | Copy-paste via `npx shadcn@latest add <name>`; component source lands in `components/ui/`. Not an npm import — user can read, edit, fork. Agent can read/modify alongside other components. |
| **AI-aware design** | Documented for AI consumption (the docs include AI-friendly install patterns; v0 outputs shadcn by default). |
| **Tailwind v4 native** | OKLCH defaults wired via `@theme inline`. Exactly the shape phase-17's `brand.yaml.tokens.css` produces. |
| **Massively adopted** | Largest React + Tailwind component library ecosystem; pairs cleanly with Magic UI (animation companion), Aceternity UI (full-section motion), Radix (under the hood). |
| **Bundle weight ~zero** | Only what's imported; no library overhead. |

### Setup at phase 18 (the canonical install dance)

```bash
# 1. Initialize shadcn in the project (run once)
npx shadcn@latest init

# 2. Per-component install as components.yaml dictates
npx shadcn@latest add button card dialog input form dropdown-menu sheet skeleton
```

Components land in `components/ui/` by default (path configurable in `components.json`). The CLI updates `app/globals.css` with OKLCH `:root` + `.dark` CSS variables AND `@theme inline` Tailwind mappings; updates `components.json` with project config.

### Tokens → `app/globals.css` (the OKLCH + `@theme inline` pattern)

```css
/* app/globals.css — generated from .website-builder/brand.yaml.tokens.css at phase 17 */
@import "tailwindcss";

:root {
  --background: oklch(100% 0 0);
  --foreground: oklch(15% 0 0);
  --primary: oklch(64% 0.18 30);
  --primary-foreground: oklch(98% 0 0);
  /* ...full token set per brand.yaml */
}

.dark {
  --background: oklch(15% 0 0);
  --foreground: oklch(98% 0 0);
  --primary: oklch(70% 0.18 30);
  --primary-foreground: oklch(15% 0 0);
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  /* ... */
}
```

This is exactly the shape phase-17's `brand.yaml.tokens.css` produces — the agent generates `globals.css` directly from the canonical token file. **Never hardcode a color anywhere in component code.** Custom brand colors beyond shadcn's default set: declare the variable in `:root` / `.dark`, then map via `@theme inline { --color-x: var(--x) }` — that adds the color as a Tailwind utility class automatically.

`components.json`:

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "",
    "css": "app/globals.css",
    "baseColor": "neutral",
    "cssVariables": true
  },
  "aliases": {
    "components": "@/components",
    "ui": "@/components/ui",
    "utils": "@/lib/utils",
    "lib": "@/lib",
    "hooks": "@/hooks"
  }
}
```

`tailwind.cssVariables: true` is non-negotiable for the website-builder's token-driven workflow. **This cannot be changed after init** — the agent locks this at phase 18 init.

### Server / Client component boundary (NON-NEGOTIABLE discipline)

- **Server Components by default.** Pages are Server; layouts are Server; static section blocks are Server.
- **`'use client'` only where interactivity is needed** — forms, animations, state hooks, `useEffect`, `localStorage`, `useRouter` for client-side navigation.
- **Directive placement:** `'use client'` MUST be at the file top, **before any imports**. Marks the server/client module-graph boundary.
- **Once a file is `'use client'`, all its imports and directly-rendered components join the client bundle.** Don't re-add the directive to every child — it cascades.
- **shadcn forms are Client components** (they use React Hook Form + state); shadcn primitives that wrap Radix are Client because Radix uses React state. **Static-display shadcn primitives** (Card, Skeleton) work in Server contexts.
- **Pages can be Server** even when they render shadcn forms — the form component itself is the Client island.

Wrong placement breaks hydration; the agent enforces this at phase 18 codegen and verifies at phase 20.

### Variants + forms

- **Variants:** `class-variance-authority` (`cva`) ships with shadcn by default — used for variant-driven styling (size, intent, etc.).
- **Forms:** React Hook Form + Zod validation (shadcn `Form` component wraps these — `Form`, `FormField`, `FormItem`, `FormLabel`, `FormControl`, `FormMessage`).

### Animation companions

| Companion | When | Folder |
|---|---|---|
| **Magic UI** *(default animation pairing)* | Scroll-driven micro-animations, sparkles, ticker numbers, gradient borders, marquees | `components/magicui/` (keep namespace clean from `components/ui/`) |
| **Aceternity UI** | Full-section motion (hero takeovers, agency/portfolio aesthetic) | `components/effects/` |

Both use Tailwind + Framer Motion + the same OKLCH theme. `prefers-reduced-motion` gate is non-negotiable (added at component level for every animation import); static SSR fallback for any client-only animation; dynamic import for heavy WebGL/Three.js components.

### Customized shadcn → `components/custom/` (overwrite-safe namespace)

If the user customizes a shadcn primitive (e.g., a `Button` variant the upstream doesn't have), the agent moves the customized version to `components/custom/Button.tsx` to escape the regenerate path. `npx shadcn add button` re-run would otherwise overwrite the customization in `components/ui/button.tsx`. The agent notes the customization in `components.yaml` and surfaces the move to the user.

### Alternative React libraries (when not shadcn)

Per `Workstreams/website-builder/components/DESIGN-components-react.md` capability matrix:

- **Mantine** — when user wants batteries-included; forms-heavy site; least DIY
- **Aceternity UI** — animation-heavy portfolio / agency
- **Magic UI** — sibling to shadcn (use as companion, not primary)
- **Once UI** — token-driven brand customization; Next.js-first
- **Chakra UI** — style-prop syntax; rapid prototyping; a11y-first
- **NextUI / HeroUI** — consumer-app smooth-motion polish (verify brand-rename status via context7 — NextUI → HeroUI in flight)
- **Material UI (MUI + Joy UI)** — Material Design adherence or Joy UI for free-brand Material structure
- **Ant Design** — enterprise admin / dense data tables

The agent ALWAYS surfaces the default (shadcn) + 1-2 alternatives with trade-offs; user picks; phase 18 records the choice in `project.yaml.component_library`.

## Deploy

**Hosting target:** Vercel (primary — Vercel built Next.js; first-party deploy story). Alternatives: Cloudflare Pages, Netlify, AWS Amplify, Render, Railway, self-hosted Docker + Node.

**MCP integrations** (per §"Auth + setup" → `### MCP servers`):

- **Vercel MCP** (https://mcp.vercel.com) — **mandatory** at phases 28-30 for deploy / DNS / SSL / analytics / env-var management. Fallback: `vercel` CLI + REST API.
- **Cloudflare MCP** (https://mcp.cloudflare.com) — recommended at phase 28 when user's domain is on Cloudflare for DNS-record automation. Fallback: Cloudflare REST API via `Bash + curl` OR `wrangler` CLI OR manual dashboard set.
- **GitHub MCP** (`api.githubcopilot.com/mcp`) — recommended at phase 29 for PR automation per `dev → master` workflow; at phase 30 for Dependabot/Renovate config; post-launch for issue triage. Fallback: `gh` CLI.
- **Sentry MCP** (https://mcp.sentry.dev/mcp) — recommended at phase 30 for error-monitoring setup + at phase 34 + post-launch for issue triage. Fallback: Sentry SDK + web dashboard.
- **GA4 / Plausible MCP** — recommended at phase 30 for analytics surface verification; at phase 34 for weekly monitoring cadence. Fallbacks: respective web dashboards + REST APIs.
- **Supabase / Neon MCP** — recommended at phase 12+29 when Postgres backend is on Supabase or Neon (typical with `cms=payload` or with Better Auth for transactional sites). Fallbacks: respective CLIs (`supabase`, `neonctl`) + psql.

### Phase 28 — Domain + DNS

- Vercel auto-provisions `*.vercel.app` subdomain on first deploy. User adds custom domain in Vercel Dashboard → Project → Settings → Domains, or via the Vercel MCP (`mcp__vercel__add_domain`).
- DNS: agent walks user through CNAME (subdomain) or A-record (apex domain) setup. If user's domain is on Cloudflare, the agent uses Cloudflare MCP to set records; otherwise emits manual DNS instructions and verifies via `dig +short example.com`.
- SSL: Vercel auto-provisions Let's Encrypt; verification automatic; agent confirms via `curl -v https://example.com` returning a 200 + valid cert.

### Phase 29 — Hosting deployment

**First deploy:**

```bash
# Option A — Vercel CLI
pnpm add -g vercel
vercel                                # interactive setup; links project to Vercel account
vercel --prod                         # production deploy

# Option B — Vercel MCP (preferred for the agent)
mcp__vercel__deploy_to_vercel(...)
```

**Subsequent deploys:** `git push` to `main` (or whichever branch is set as Production in Vercel) triggers Vercel auto-deploy. Preview deploys on every PR by default.

**Verification:** agent runs Playwright walk against the production deploy URL — checks every page renders, hreflang tags emit correctly, language switcher works, forms submit to API routes, Stripe Checkout (if transactional) reaches the hosted page.

### Phase 29 — Payload-specific deploy gate (when CMS=Payload)

Before `next build`, the agent MUST run the Payload migrate command:

```bash
pnpm payload migrate && next build
```

Forgetting `payload migrate` produces silent schema drift between dev and prod. The agent encodes this as the production build command in `package.json`:

```json
{
  "scripts": {
    "build": "pnpm payload migrate && next build"
  }
}
```

Verified context7 `/payloadcms/payload` 2026-05-18. Enforced at phase 29 via deploy-pipeline check.

### Phase 30 — Analytics + search submission

| Surface | Setup |
|---|---|
| **Vercel Analytics** | Built-in; enable via Vercel Dashboard or MCP. Privacy-friendly page-view tracking; no cookie banner needed for basic mode. |
| **Vercel Speed Insights** | Real User Monitoring (RUM); enable alongside Analytics; surfaces Core Web Vitals trends. |
| **Plausible / Fathom / GA4** | Third-party; install via `app/layout.tsx` `<Script>` tag or env-var-driven conditional injection. The agent uses Plausible by default for muggle-friendly privacy posture. |
| **Sitemap submission** | `app/sitemap.ts` auto-generates `/sitemap.xml`; agent submits to Google Search Console + Bing Webmaster via WebFetch + form posts at phase 30. |

### Performance budget

Next.js + Vercel hits Lighthouse 90+ out of the box for content sites. Agent uses:

- **`next/image`** for all images (auto-format negotiation — AVIF/WebP fallback, responsive sizes, lazy loading by default).
- **`next/font`** for self-hosted fonts (no FOIT, no third-party request).
- **Static generation** by default; ISR (`export const revalidate = N`) for content that changes; SSR (`export const dynamic = 'force-dynamic'`) only when truly needed.
- **Server Components** to minimize the client bundle; `'use client'` only at the interactivity boundary.
- **Vercel Image Optimization** (default with `next/image`).
- **Heavy animation components**: dynamic import + `prefers-reduced-motion` gate + static SSR fallback **at build time** so phase 22 doesn't rediscover the perf cost (the phase-17 motion budget pre-allocates this).

Phase 22 (perf audit) verifies Lighthouse score against the budget locked at phase 17.

## Post-launch maintenance pattern

Per locked decision 37 — phases 31-34 run once at launch (announce, set roadmap, set maintenance cadence, configure monitoring); after that the post-launch maintainer template (per `DESIGN-post-launch-template.md`) takes over for ongoing maintenance. Next.js-specific adaptations:

### Content edits

- **None (file-based MDX):** user edits `content/pages/{lang}/{slug}.mdx` directly in their editor of choice (VS Code, Cursor, Obsidian — anything that edits markdown). Commit + push → Vercel auto-deploys.
- **Decap:** user logs into `/admin` (Decap UI), edits content visually, saves → Decap commits to git → Vercel auto-deploys.
- **Payload:** user logs into Payload admin (auto-mounted at `/admin` in the same Next.js app), edits in Payload's TypeScript-first CMS UI, saves → Payload writes to Postgres → next request renders updated content. No deploy needed for content-only changes.

Maintainer template explains all three paths at launch.

### Component edits

- **Simple text/style tweaks:** user edits `components/{Name}.tsx` directly. Tailwind class changes are immediate; layout changes need testing.
- **Non-trivial changes:** agent re-engaged. The agent reads `components.yaml` + the existing component, makes the change, runs phase 18 sub-flow (token re-validation, a11y check), commits.

### Style token updates

- User edits `.website-builder/brand.yaml`; agent regenerates `app/globals.css` (OKLCH `:root` + `@theme inline`) from the canonical tokens; commit + push.
- The cascade: tokens change → utility-class behavior changes everywhere → no per-component edits needed (this is the payoff of the token-first discipline).

### Image-gen iteration

Per `consumers/image-gen.md` — user requests new images (hero, product shots, etc.); image-gen consumer produces; agent integrates into `public/images/` + updates the component referencing the image. Subject to `next/image` size/format optimization.

### Dependency updates

- `pnpm update` cadence documented (monthly). Agent surfaces breaking changes via context7 lookups for major version bumps — particularly Next.js (App Router behavior shifts), shadcn (Tailwind v3 → v4 migration), next-intl (API evolution).
- Security patches: `pnpm audit` + Dependabot/Renovate Bot configured at deploy via `.github/dependabot.yml` (or Vercel's auto-Dependabot if enabled).

### Performance regressions

Vercel Speed Insights surfaces Core Web Vitals trends; agent configures alert thresholds at phase 30 (LCP > 2.5s, INP > 200ms, CLS > 0.1).

### Adding pages

User requests a new page (e.g., "add a Pricing page"); agent creates `app/[lang]/pricing/page.tsx` + `content/pages/{lang}/pricing.mdx` + updates `sitemap.yaml` + emits a phase-26 hreflang re-check. Commit + push.

### Adding components

User requests; agent runs phase 18 again for the new component (read `components.yaml`, install shadcn primitives, write `components/{Name}.tsx`, a11y check).

### The user's long-term maintenance loop

*Describe what they want → agent edits code (or user edits MDX directly, or user edits in the chosen CMS) → git push → Vercel auto-deploys.* That's the entire loop. No staging environment friction; preview deploys per PR; production deploy on merge to `main`.

## Limitations + escape hatches

What Next.js + shadcn CAN'T do that other stacks can:

- **No visual canvas.** Users uncomfortable with code can't visually compose pages — they edit MDX or work via a CMS. If the user can't tolerate ANY code, Framer / Webflow / WordPress are better picks. The agent surfaces this honestly at phase 11.
- **Complex routing requires understanding App Router conventions.** Catch-all routes (`[...slug]`), parallel routes (`@modal`), intercepting routes (`(.)photo`) — power-user features the agent applies when needed but the user may not understand without help.
- **Server-side complexity** when adding Route Handlers / DB / auth. The agent surfaces if project scope is creeping toward full-stack-app territory vs. content site — this is a pivot moment per decision 34 (transactional flag mid-project change forces a phase-12/22/24a-c restart).
- **The Next.js 15 `fetch` no-store default** is a footgun for developers migrating from Next.js 14 — see `### Failure modes` below.
- **Vercel pricing** at scale: Hobby tier (free) is generous but capped at 100 GB bandwidth + 100k function invocations / month; Pro tier ($20/month) is fine for muggle sites; beyond that, costs scale with usage. Agent surfaces at phase 11 + phase 28.
- **shadcn lock-in to Tailwind:** if the user prefers CSS modules / styled-components / vanilla-extract, shadcn fights the workflow. Switching to Mantine / Chakra / Material UI is the escape — phase 18 component-library re-pick per `DESIGN-components-react.md` § Migration between libraries.
- **Copy-paste shadcn means the repo grows** — every component installed adds files. Some users find this overwhelming. Mitigation: agent groups related components (`components/forms/`, `components/data-display/`, `components/marketing/`) and adds README.md per folder.

### Failure modes

| Failure | Cause | Recovery |
|---|---|---|
| **Hydration mismatch error in browser console** | Server-rendered output ≠ client-rendered output. Usually: a Server Component reading `Date.now()` / `Math.random()` / browser-only API. | Move the offending logic to a Client Component OR use `useEffect` for browser-only values OR pass values from server via props. |
| **`'use client'` directive ignored** | Placed after imports, or inside a function. | Move to file top, line 1, before all imports. |
| **next-intl `useTranslations` throws "No intl context"** | Component using `useTranslations` is rendered outside `<NextIntlClientProvider>` boundary OR is a Server Component without `setRequestLocale()` called in parent layout. | Wrap with `NextIntlClientProvider` OR use `getTranslations()` async function in Server Components. |
| **OKLCH colors not rendering in Safari < 15.4 / Chrome < 111** | Older browser without OKLCH support. | Tailwind v4's OKLCH defaults include sRGB fallback via `color-mix()`; if user needs deeper compat, agent generates fallback `rgb()` values from `brand.yaml.tokens` for legacy browsers (phase 17 trade-off). |
| **Stripe webhook 400s with "signature verification failed"** | Webhook handler reading parsed body instead of raw body. | Use `await req.text()` for raw body; pass to `stripe.webhooks.constructEvent(body, sig, secret)`. Document in `app/api/stripe-webhook/route.ts` comments. |
| **Payload admin not loading after deploy** | `pnpm payload migrate` was skipped before `next build`. | Re-run the canonical build command (see §"Deploy" Phase 29 — Payload-specific deploy gate). |
| **`app/sitemap.ts` returns empty** | Routes are dynamic (`app/[lang]/[slug]/page.tsx`) and `generateStaticParams` is missing or returning empty. | Verify `generateStaticParams` returns the full param matrix per locale × page. |
| **Vercel deploy fails on `pnpm install`** | Lockfile out of date OR private dep not authenticated. | Check `pnpm-lock.yaml` is committed; verify Vercel env has `NPM_TOKEN` / GitHub package auth if private deps used. |
| **Image optimization 504s on Vercel** | `next/image` source URL not in `images.remotePatterns` in `next.config.mjs`. | Add the source pattern; redeploy. |
| **hreflang missing on production but present locally** | `generateMetadata` returns `alternates.languages` only on the locale-matching path; the agent's pattern always returns the full map. | Verify per `i18n/hreflang.md#next-js--shadcn`. |

### Escape hatches per limitation

- **User wants WYSIWYG editing post-launch:** add Payload's admin UI (Payload v3 mounts inside the same Next.js project at `/admin`), TinaCMS visual editing, or pivot the stack to headless Webflow + Next.js frontend. The phase-11 transactional-flag-mid-project change pattern (decision 34) covers the restart cost if mid-project pivot.
- **User wants edge-only / no Node runtime:** `export const runtime = 'edge'` per route; deploys to Vercel Edge or Cloudflare Pages. Some Node-only APIs become unavailable (e.g., parts of `fs`, certain crypto modes); agent verifies route compatibility before locking.
- **Static-only export:** `next.config.mjs` with `output: 'export'` produces fully static output deployable to GitHub Pages / S3 / Cloudflare Pages without Vercel. Loses ISR + Route Handlers + Image Optimization (uses unoptimized images instead); agent surfaces the trade-off at phase 28.
- **User outgrows Vercel pricing:** migrate to self-hosted (Docker + Node + Nginx), Cloudflare Pages (mostly compatible with Vercel features), or Netlify (mostly compatible). Agent flags the architectural delta at the migration moment.

## context7 lookups for this stack

Per Lock-3 freshness pattern. The agent invokes context7 at the following phases for fresh Next.js / React / shadcn / Tailwind / next-intl / Payload docs. **Cached docs land in `.website-builder/library/docs/nextjs-*.md`, `react-*.md`, `tailwind-*.md`, `shadcn-*.md`, `next-intl-*.md`, `payload-*.md`. Re-fetch threshold: 30 days** (per `skills/wb-architecture/references/context7-protocol.md`). Next.js evolves fast — training data is stale within ~6 months on App Router behavior, fetch caching semantics, and the i18n surface.

**Adjacent surface:** §"Auth + setup" → `### MCP servers (recommended at setup)` enumerates the MCPs the agent uses at runtime. context7 (this section) is the **docs-freshness** layer (knowing what to do); the MCP layer is the **operational** surface (actually doing it). Both are required; neither substitutes for the other.

### Phase 11 (stack decision)

| Library ID | Question template | Why |
|---|---|---|
| `/vercel/next.js` | "current App Router + RSC + rendering modes; **the fetch no-store default** in Next.js 15+; next-intl integration patterns" | **MANDATORY.** The fetch default change alone justifies this; without context7, the agent recommends Next.js 14 patterns that break on 15+. |
| `/payloadcms/payload` | "current Next.js + Payload v3 install pattern; Postgres adapter; `pnpm payload migrate && next build` build command" | Used here as a CMS-pairing preview (full coverage at phase 12). |
| Framer/WordPress comparison | "Framer Server API state; WordPress FSE + theme.json v3" | The agent walks 5-question stack-decision logic per `wb-architecture/references/stack-matrix.md`; comparison fairness requires fresh competitor data too. |

### Phase 12 (CMS decision)

| Library ID | Question template |
|---|---|
| `/payloadcms/payload` | "Collections, Blocks field, field-level localization (`localized: true`), access control / roles, drafts/versions, live preview, Postgres adapter setup, the production build command" |
| `/decaporg/decap-cms` (or WebFetch decapcms.org/docs — context7 coverage thin) + `/websites/decapcms` (per Captain J Phase-4 research, benchmark 93.5) | "config-schema, OAuth backends, `structure: multiple_files` i18n, current upstream + Sveltia fork state (re-verify each phase-12 invocation; Static CMS archived 2024-09-09 — do NOT recommend)" |

### Phase 17 (design system)

| Library ID | Question template |
|---|---|
| `/tailwindlabs/tailwindcss.com` | "Tailwind v4 `@theme inline` directive; OKLCH color system; CSS-first config; migration from v3 if needed" |
| `/shadcn-ui/ui` | "current shadcn theming pattern; `components.json` config schema; CSS-variable vs Tailwind-utility theming trade-off; the `--no-css-variables` flag and when NOT to use it" |

### Phase 18 (component build)

| Library ID | Question template |
|---|---|
| `/shadcn-ui/ui` | "current `npx shadcn add` recipe per component; Server / Client component boundary; React Hook Form + Zod `Form` wrapping" |
| `/radix-ui/primitives` | "primitive composition patterns; Dialog / DropdownMenu / Popover compound parts; controlled vs uncontrolled" |
| `/vercel/next.js` | "Server Action patterns; Route Handler patterns; `'use client'` directive placement" |
| Animation companion (when picked) | `/magicuidesign/magicui` OR `/aceternityui/aceternity-ui` — verify current install pattern via `resolve-library-id` first |

### Phase 22 (perf audit)

- `/vercel/next.js` — `next/image` + `next/font` + `<Script>` + caching options for the Next.js 15+ baseline
- `/GoogleChrome/lighthouse` — current scoring thresholds; agent runs Lighthouse against the Vercel preview deploy

### Phase 24a (commerce)

- `/stripe/stripe-docs` — current Checkout Session API + webhook signature verification + TWINT enable pattern
- (When booking) `/calcom/cal.com` — `@calcom/embed-react` current install + props

### Phases 28-30 (deploy)

- `/vercel/next.js` — current Vercel deploy mechanics + Image Optimization remote-patterns + env-var management
- WebFetch `vercel.com/docs` for deploy-specific knobs context7 may not cover yet

### WebFetch fallback URLs

When context7 coverage is thin or stale (Tier 2 fallback per `.claude/rules/tool-dependency-discipline.md`):

- `https://nextjs.org/docs` (canonical Next.js docs)
- `https://ui.shadcn.com/docs` (canonical shadcn docs)
- `https://tailwindcss.com/docs` (canonical Tailwind docs)
- `https://next-intl-docs.vercel.app/` (canonical next-intl docs)
- `https://payloadcms.com/docs` (canonical Payload docs)
- `https://vercel.com/docs` (canonical Vercel deploy docs)

The agent cites URL + fetch date in any cached-doc file.

## References

### Foundation design docs (vault-root-relative per `vault-workstreams.md` link standard)

- [DESIGN-stack-nextjs](Workstreams/website-builder/stacks/DESIGN-stack-nextjs.md) — primary source for this adapter
- [DESIGN-content-layers](Workstreams/website-builder/foundation/DESIGN-content-layers.md) — 5-layer content stack (§4 row labels source)
- [DESIGN-i18n](Workstreams/website-builder/foundation/DESIGN-i18n.md) — i18n model (Pattern A/B, routing strategies)
- [DESIGN-ingestion-and-extraction](Workstreams/website-builder/foundation/DESIGN-ingestion-and-extraction.md) — phase 6.5 mechanism
- [DESIGN-architecture](Workstreams/website-builder/foundation/DESIGN-architecture.md) — agent profile + skills + phase contracts
- [DESIGN-components-react](Workstreams/website-builder/components/DESIGN-components-react.md) — full React component-library capability matrix; shadcn deep dive
- [DESIGN-project-scaffold](Workstreams/website-builder/foundation/DESIGN-project-scaffold.md) — `.website-builder/` layout
- [DESIGN-phase-contracts](Workstreams/website-builder/foundation/DESIGN-phase-contracts.md) — pipeline phases this adapter is consumed at
- [DESIGN-ecosystem-catalog](Workstreams/website-builder/foundation/DESIGN-ecosystem-catalog.md) — payment-providers, animation-libraries cross-references
- [BUILD-strategy](Workstreams/website-builder/BUILD-strategy.md) Phase 3 — the DoD this adapter satisfies
- [VISION-website-builder](Workstreams/website-builder/VISION-website-builder.md) — strategic anchor

### Plugin internal cross-references (vault-root-relative paths to the plugin worktree)

- `adapters/README.md` — the 14-section schema this file implements
- `i18n/language-switcher.md#next-js--shadcn` — per-stack language switcher implementation (paired)
- `i18n/hreflang.md#next-js--shadcn` — per-stack hreflang emission (paired)
- `i18n/strings-schema.md` — stack-agnostic CDJSON contract
- `i18n/rtl.md` — stack-agnostic RTL discipline
- `extraction/playwright-walk.md` — primary URL extractor for deployed-site ingestion
- `extraction/ai-output.md` — primary parser for AI/v0/Cursor output ingestion
- `extraction/stitch.md` — design-token cross-validation
- `handoff-spec/component-request-v1.md` + `handoff-spec/component-output-v1.md` — round-trip handoff contracts
- `skills/wb-architecture/SKILL.md` — phase 11/12 skill that consumes this adapter at the stack-decision moment
- `skills/wb-architecture/references/stack-matrix.md` — phase 11 stack-comparison reference
- `skills/wb-architecture/references/context7-protocol.md` — Lock-3 freshness protocol
- `skills/wb-component-build/SKILL.md` — phase 18 skill that consumes this adapter at component-build
- `skills/wb-component-build/references/per-stack-codegen.md#nextjs` — phase 18 read-only codegen anchor
- `phase-contracts/06.5-artifact-ingestion.md` — phase 6.5 contract this adapter's §"Phase 6.5 ingestion" implements
- `phase-contracts/11-stack-decision.md` — phase 11 contract that names this adapter as the Next.js stack-pick consumer
- `tests/adapters/nextjs/` — adapter-specific test fixture for this stack

### External references

- Next.js: https://nextjs.org (and App Router: https://nextjs.org/docs/app)
- Vercel: https://vercel.com
- next-intl: https://next-intl-docs.vercel.app
- shadcn/ui: https://ui.shadcn.com
- Tailwind CSS: https://tailwindcss.com (v4 CSS-first directive: https://tailwindcss.com/docs/theme)
- Radix Primitives: https://www.radix-ui.com
- MDX: https://mdxjs.com
- React Server Components: https://react.dev/reference/rsc/server-components
- Better Auth: https://better-auth.com
- Payload CMS: https://payloadcms.com (Payload v3 Next-native install: https://payloadcms.com/docs/getting-started/installation)
- Sanity: https://sanity.io
- Decap CMS: https://decapcms.org (active fork: https://github.com/sveltia/sveltia-cms)
- Stripe: https://stripe.com (Stripe Checkout: https://docs.stripe.com/payments/checkout)
- Lemon Squeezy: https://lemonsqueezy.com
- Cal.com: https://cal.com (`@calcom/embed-react`: https://cal.com/docs/embeds/react)
- Magic UI: https://magicui.design
- Aceternity UI: https://ui.aceternity.com
