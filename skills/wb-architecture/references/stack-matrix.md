# Reference — Stack matrix (phase 11)

> Per-stack prose for the three MVP stacks, the expansion-stack substitution table, the 5-question decision logic, and the complete transactional sibling rulings. Authoritative source of truth is `Workstreams/website-builder/stacks/DESIGN-stack-{framer,nextjs,wordpress}.md` + `phase-contracts/11-stack-decision.md` — read those fully for any stack the user seriously considers. This file is the fast-load summary.

## MVP stacks (decision 52 — build-now for v1)

### Framer

Canvas-first visual design tool with a built-in CMS, a Custom Components SDK (React/TSX via the Framer CLI), and a **Server API** for programmatic project manipulation. The agent uses the Server API to seed pages, CMS Strings collections, brand tokens, and project structure; writes Custom Components in TypeScript; the user composes pages on the canvas guided by per-page wireframe briefs the agent emits. **The agent does not compose pages programmatically end-to-end** — that fights Framer's canvas value prop. Page composition stays a user activity.

- **Sweet spot:** brand-led marketing sites where the user wants visual control after launch but won't learn a code editor. Solo creators, small teams, designer-led businesses. Sister's "Still Humans" Framer project is the canonical cosplay target for the MVP cycle.
- **Trade-offs (surface honestly at decision time):** Framer Publish hosts on Framer's infrastructure only (no Vercel/Cloudflare option); the canvas is not version-controlled the way code is; complex page logic beyond Custom Components gets awkward fast.
- **Natural CMS pairing:** Framer CMS (phase 12 thin pass).
- **Current external state (verified 2026-05-18):** Framer's Server API was published February 2026, free during open beta. It shares Plugin API capabilities — sync CMS collections from external sources, publish changes, update the canvas, change project settings; triggerable by AI agents, webhooks, scheduled jobs. Plugins can read/edit/manage code Components and Overrides. "Workshop" is Framer's AI component generator. Re-verify via `WebFetch` framer.com/developers + framer.com/updates/server-api at phase-11 session start.

### Next.js

React-based meta-framework: App Router file-system routing, hybrid rendering (SSG/ISR/SSR/Server Components), Route Handlers, Vercel-native deploy. Most flexible stack the builder supports — static brochure through full SaaS app fits in one project. Agent writes `.tsx` + `.mdx`, `next-intl` for i18n, `shadcn/ui` default component library, deploys via the Vercel MCP. App Router exclusively for new projects (Pages Router is legacy).

- **Sweet spot:** users who want a real codebase they (or a hired developer) can read, modify, extend a year out. Output is `.tsx`/`.mdx` in a git repo — no canvas state, no platform lock-in.
- **Trade-offs vs Framer:** no visual canvas after launch (edit MDX or use a phase-12 CMS); bigger learning surface if the user has never touched React. **vs WordPress:** smaller plugin ecosystem (compose what you need); user owns more operational surface (no managed-WP backups).
- **Migration landmine (cite to user — verified via context7 `/vercel/next.js` 2026-05-18):** Next.js 15 App Router defaults `fetch()` to **no-store / auto-no-cache** (`finalRevalidate = 0`, reason `auto no cache`). This is a **breaking change from Next.js 14's `force-cache` default**. Server Actions set `fetchCache = 'default-no-store'` explicitly. To restore old caching: per-request `fetch(url, { cache: 'force-cache' })`, or page/layout-level `export const fetchCache = 'default-cache'`. Time-based: `fetch(url, { next: { revalidate: N } })`. i18n: the `getDictionary` dynamic-import pattern (`import('./dictionaries/${locale}.json')`) is the canonical App Router locale-loading shape. This is exactly why context7 is mandatory here — training data is stale on the cache default.
- **Natural CMS pairings:** `none` (file-based markdown), `decap` (git-backed admin), `payload` (schema-as-code) — all decided at phase 12.

### WordPress

~40% of the web. Largest plugin ecosystem, audience-familiar admin UI, strongest built-in path to a content-heavy site managed long-term by non-technical owners. Agent uses the WordPress REST API + an available WordPress MCP (find the most-maintained one via context7 at phase 11), writes a **custom block-theme (Full Site Editing)**, composes pages via Gutenberg blocks (one custom block per phase-15 section type), pairs with WooCommerce when transactional.

- **Sweet spot:** content-heavy sites with non-technical editors who publish often and won't learn a CMS abstraction. Editorial teams, professional services, sites that outlive the developer relationship.
- **Trade-offs vs Framer/Next.js:** needs a host (managed-WP at Kinsta/WP Engine/SiteGround/Cloudways, or VPS/cloud); maintenance discipline (plugin/core updates, security patches, backups); heavier PHP+MySQL footprint. **vs Next.js specifically:** each request goes through WP's full PHP bootstrap (caching mitigates but never matches static export); the modern frontend story is awkward unless headless (WP backend + Next.js frontend — which then makes Next.js the actual stack with WP as CMS layer).
- **Natural CMS pairing:** `wordpress-core` (phase 12 thin pass).
- **Current external state (verified via WebSearch 2026-05-18):** FSE is the 2026 standard, not experimental, not optional. **theme.json v3** is the schema for WordPress 6.6+ (normalizes longhand/shorthand CSS resolution, block style variations as first-class config objects, shadow presets, fluid-typography min/max). Block patterns auto-register from PHP files in `patterns/` via header comments. Block Bindings + Interactivity API + pattern-first are the 2026 development model. theme.json generates CSS custom properties (`--wp--preset--color--primary`) that custom CSS references. Twenty Twenty-Five (block theme) is a strong scaffold base. Re-verify via `WebFetch` developer.wordpress.org at phase-11 session start.

### Choosing between the three (the 5-question decision logic)

No numeric scoring, no flowchart. Ask, let answers point:

1. **"After this site launches, who edits it?"** Solo/designer → Framer. Editorial team/non-developer → WordPress. The user in a code editor (or a hired dev) → Next.js.
2. **"Where do you want to host?"** Framer-hosted only → Framer. Vercel/Cloudflare/Netlify/self-hosted Node → Next.js. Managed-WP or own VPS → WordPress.
3. **"Visual canvas after launch — load-bearing or nice-to-have?"** Load-bearing → Framer. Nice-to-have → either other, CMS at phase 12 closes the gap.
4. **"How much will the site grow in the next year?"** Stay small (5-15 pages) → any. Content-heavy publication/catalog → WordPress or Next.js. Toward SaaS → Next.js.
5. **"How comfortable in code, 1-5?"** 1-2 → Framer or WordPress. 3-5 → Next.js opens up.

Surface trade-offs in concrete language ("pick Framer, you can't migrate hosts without leaving Framer; pick Next.js, you'll edit MDX unless we pick a CMS next phase"). User picks; agent writes `stack` + 2-4 sentence `stack_reasoning`.

## Expansion stacks (post-MVP — expansion phase 10)

Fully designed in `Workstreams/website-builder/stacks/`, accessible to users who already know them, **not first-class in MVP**. Mention only when the user names one or an MVP stack is clearly wrong. Steer toward an MVP stack for v1.

| Expansion stack | What it is | Closest MVP substitute |
|---|---|---|
| **Astro** | Content-focused, zero-JS-by-default, component islands | Next.js with static-export config |
| **Hugo** | Go SSG, fastest builds (50k pages in seconds) | Next.js static export |
| **SvelteKit** | Svelte meta-framework, smallest SSR bundles | Next.js |
| **Webflow** | Visual canvas + CMS + hosting, deeper CSS-class control than Framer | Framer |
| **Plain static HTML** | No framework, no build, just HTML/CSS/JS | Next.js static export (or wait for expansion phase 10) |

If the user insists on an expansion stack for v1: log `.website-builder/decisions/stack-expansion-${stack}.md`, surface that in-MVP support is "design exists, runtime adapters not yet shipped," and either proceed with degraded support (user accepts the risk) or route to an MVP stack with documented future-migration intent. Never pretend MVP support exists.

**Out-of-design-surface stacks:** Wix / Squarespace / Carrd are outside the eight-stack design surface — not supported. WordPress.com Business+ counts as managed-WP; lower plans (Free/Personal/Premium) can't install custom themes → not MVP-compatible.

## Transactional sibling — complete rulings

Two questions, **verbatim, in order**, via `AskUserQuestion`:

> **"Is anyone going to pay anything on this site?"**
> **"Is anyone going to book anything on this site?"**

Yes to either = `transactional: true`. No to both = `false`. No in-between. "Maybe later" → follow-up *"shipping with payments/bookings before v1 launch, or v1.1?"* → resolves to a concrete boolean + `transactional_followup` note.

| Scenario | Ruling | Why |
|---|---|---|
| Affiliate links / display ads | `false` | The site doesn't process payment; an external network does |
| Newsletter signups / lead-gen forms | `false` | No payment, no booking |
| Donations | `true` | Money changes hands; 24a/24b activate; non-profit Stripe config at 24b |
| Free booking calendars (no payment) | `true` | User commits time on-site; 24a/24b activate (Cal.com, MVP default decision 54); 24b light but runs |
| Paid course / membership site | `true` | 24a-c all activate; recommend Lemon Squeezy or Stripe Checkout at 24a |

When `true`: ask the one follow-up *"payments, bookings, or both?"* → write `transactional_kind` (`payments` | `bookings` | `both`; `none` when false).

**Mid-project-pivot cost (decision 34) — surface LOUDLY when asking the two questions:** changing this flag later forces a restart of phases 12 (CMS may need to change) + 22 (forms now need payment) + 24a/b/c (activate from scratch). Say it explicitly: *"answer carefully; if you change your mind at phase 20, we restart from 12."* The user can still change later — they decide knowing the cost.

**Gating:** "no transactional value recorded" is NOT overridable — the two questions must be asked and answered before phase 12 (some CMS pairings depend on it, and 24a-c floats indefinitely without it). The agent never infers the answer from the requirements doc; it asks explicitly.

## project.yaml output (phase 11)

```yaml
stack: nextjs                    # framer | nextjs | wordpress (MVP) or expansion stack w/ logged decision
stack_reasoning: |
  2-4 sentences: why this stack, what it ruled out, anchored in phase-3 requirements
  + phase-5 voice + the 5-question answers. Re-read at phases 12 and 18.
transactional: true              # true | false
transactional_kind: payments     # payments | bookings | both | none
transactional_reasoning: |
  2-4 sentences: which question got "yes", what activates downstream (24a/b/c).
transactional_followup: ~        # null when decided cleanly; populated on "v1.1 intent"
```

Also seed `.website-builder/library/docs/${stack}.md` with cached context7/WebFetch output for the chosen stack (re-read at 17/18/22/28-30; re-fetch if >30 days old).
