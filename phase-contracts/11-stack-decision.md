---
phase: 11
name: Stack decision (plus sibling, transactional decision)
group: architecture
pipeline_section: architecture
skill: wb-architecture
prev_phase: 10
next_phase: 12
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - DESIGN-phase-contracts.md
  - DESIGN-architecture.md
  - DESIGN-project-scaffold.md
  - DESIGN-stack-framer.md
  - DESIGN-stack-nextjs.md
  - DESIGN-stack-wordpress.md
  - DESIGN-stack-astro.md
  - DESIGN-stack-hugo.md
  - DESIGN-stack-sveltekit.md
  - DESIGN-stack-webflow.md
  - DESIGN-stack-static-html.md
library_clones_at_entry:
  - resource: astro-content-collections
    when: stack == "astro"
    as: docs
    note: "Astro Content Collections reference docs (clone when Astro chosen at phase 11)"
---

# Phase 11 — Stack decision *(plus sibling — transactional decision)*

> The two structural pivots of the project. Picking the stack locks what code looks like, what hosting feels like, what the user does in `/admin` (or doesn't), and what every later phase compiles to. Picking transactional vs not locks whether phases 24a / 24b / 24c activate. Both decisions live here so the agent never lets the user advance with one resolved and the other floating.

## Mission

Phase 11 is two decisions in one packet. The first picks the technology stack — the engine that produces the deployed site. The second locks whether the site is transactional — whether anyone pays for anything or books anything on it. Both reshape every downstream phase, so the agent forces them together and refuses to advance until both are written to `project.yaml`.

The stack decision lives in `project.yaml.stack`. The website-builder MVP supports three stacks fully: **Framer**, **Next.js**, and **WordPress**. The full eight-stack design surface in the workstream covers Astro, Hugo, SvelteKit, Webflow, and plain static HTML as well, but those ship in expansion phase 10 of the platform roadmap; the agent surfaces them as future-available paths during the MVP, not as build-now options. The full prose discussion of the three MVP stacks is below; the expansion-stack mention block frames the others. Per locked decision 52: *MVP stack scope = Framer + Next.js + WordPress for v1.*

The transactional decision lives in `project.yaml.transactional` as either `true` or `false`. When `true`, phases 24a (commerce platform setup), 24b (payment provider wiring), and 24c (commerce-specific legal) activate downstream. When `false`, those phases skip. The decision is straightforward — the agent asks two specific questions described below in the **Transactional decision** sub-section — but it is non-negotiable: the agent refuses to advance to phase 12 without a clear yes-or-no.

The agent uses **context7** in this phase to fetch fresh framework docs for each stack the user is seriously considering. Stacks evolve. Training-data snapshots drift. The agent's recommendations should reflect what's actually current, not what was true twelve to eighteen months ago.

## Entry conditions

- Phase 9 (sitemap) complete. `.website-builder/sitemap.yaml.pages[]` lists every page the site needs.
- Phase 10 (information architecture) complete. `.website-builder/sitemap.yaml.navigation` exists with primary/footer/utility nav structure.
- Phases 1-5 (discovery and brand) complete. The agent uses the audience (phase 3), conversion outcome (phase 3), and brand voice (phase 5) to weight stack recommendations.

## What Claude must establish

Two things, both written to `.website-builder/project.yaml`:

1. **`project.yaml.stack`** — the chosen technology stack. For the MVP, one of `framer` / `nextjs` / `wordpress`. The agent walks the user through the three MVP stacks (full prose below), invokes context7 to confirm each one's current capabilities, and asks `AskUserQuestion` for the pick. If the user signals interest in one of the five expansion stacks (Astro / Hugo / SvelteKit / Webflow / static-html), the agent surfaces the expansion-phase-10 framing — explains the stack is fully designed and accessible but not yet first-class in the MVP — and offers either to pick the closest MVP alternative or to log the expansion-stack intent in `.website-builder/decisions/stack-expansion-deferred-{slug}.md` and proceed with an MVP stack for v1.
2. **`project.yaml.transactional`** — `true` or `false`. The agent asks the two seed questions verbatim (see Transactional decision sub-section). Yes to either is `transactional: true`.

The agent also writes `project.yaml.stack_reasoning` — a 2-4 sentence prose explanation of why this stack was chosen — and `project.yaml.transactional_reasoning` — a similar prose note explaining the yes-or-no. These are not throwaway; they get re-read by the agent during phase 12 (CMS decision) and phase 18 (component build) to keep the project anchored in the rationale.

## MVP stacks (full prose)

The three stacks the MVP supports fully. Pick one for v1. Per locked decision 52: this is the v1 scope.

### Framer

Framer is a canvas-first visual design tool with a built-in CMS, a Custom Components SDK (React/TSX), and a Server API for programmatic project manipulation. The website-builder picks Framer when the user wants a polished design-led site they can keep editing visually after the agent leaves, and is willing to live with Framer's hosting and canvas-bound conventions. The agent uses the Server API to seed pages, CMS Strings collections, brand tokens, and project structure; it writes Custom Components in TypeScript via the Framer CLI; the user composes pages on the canvas guided by per-page wireframe briefs the agent emits.

Framer's sweet spot is brand-led marketing sites where the user wants visual control after launch but doesn't want to learn a code editor. Solo creators, small teams, designer-led businesses. Sister's "Still Humans" Framer project is the canonical cosplay target for the MVP cycle. Trade-offs: Framer Publish hosts on Framer's infrastructure (no Vercel or Cloudflare option), the canvas is not version-controlled the way code is, and complex page logic beyond what Custom Components support quickly becomes awkward. The agent surfaces all of these honestly at decision time.

Full per-stack design at `DESIGN-stack-framer.md`. The agent invokes `mcp__context7__resolve-library-id` for "Framer" plus `WebFetch` against framer.com/developers at this phase to confirm the current Server API surface, Custom Components SDK, and Framer CMS capabilities — these evolve quarterly.

### Next.js

Next.js is the React-based meta-framework that ships file-system routing, hybrid rendering (SSG / ISR / SSR / Server Components), API routes, Route Handlers, and a Vercel-native deploy story. The website-builder picks Next.js when the user wants the most flexible stack the builder supports — anything from a static brochure site to a full SaaS app fits inside one Next.js project. The agent writes React components in TypeScript, uses MDX for page-level prose, integrates `next-intl` for i18n, picks `shadcn/ui` as the default component library, and deploys via the Vercel MCP.

Next.js's sweet spot is users who want a real codebase they (or a developer they hire) can read, modify, and extend a year from now. The output is `.tsx` and `.mdx` files in a git repo — no canvas state, no platform lock-in, no "Framer-export needed" path off. Trade-offs vs Framer: no visual canvas after launch (the user edits MDX files or works through a CMS picked at phase 12), and the learning surface is bigger if the user has never touched React. Trade-offs vs WordPress: smaller plugin ecosystem (the user composes what they need rather than installing-and-configuring), and the user owns more of the operational surface (no managed-WP backups out of the box).

Note for migrators on Next.js 15+: `fetch()` is no-store by default, which is a breaking change from Next.js 14's `force-cache` default. The agent uses this fact to surface that data-fetching patterns differ from older training data; context7 lookups in this phase and again at phase 18 keep the agent current. Reference: [Next.js auto no-cache default](https://github.com/vercel/next.js/blob/canary/packages/next/src/server/lib/patch-fetch.ts).

Full per-stack design at `DESIGN-stack-nextjs.md`. The agent invokes `mcp__context7__query-docs` against `/vercel/next.js` for current App Router + RSC + rendering mode patterns. Caches to `.website-builder/library/docs/nextjs.md`.

### WordPress

WordPress runs roughly 40 percent of the web. The website-builder picks WordPress when the user wants the largest plugin ecosystem on earth, an audience-familiar admin UI, and the strongest built-in path to a content-heavy site managed long-term by non-technical owners. The agent uses the WordPress REST API plus available WordPress MCP servers (the agent invokes context7 at this phase to find the most maintained one), writes a custom block-theme (Full Site Editing), composes pages via Gutenberg blocks (one custom block per section type from phase 15), and pairs with WooCommerce when transactional.

WordPress's sweet spot is content-heavy sites with non-technical editors who need to publish often and don't want to learn a CMS abstraction. Editorial teams, professional services, sites that will outlive the developer-relationship. Trade-offs vs Framer and Next.js: WordPress needs a host (managed-WP at Kinsta / WP Engine / SiteGround / Cloudways, or VPS / cloud), maintenance discipline (plugin updates, core updates, security patches, backups), and the PHP-plus-MySQL operational footprint is heavier than the alternatives. Trade-offs vs Next.js specifically: each page request goes through WP's full PHP bootstrap (mitigated by caching but never as fast as static export), and the modern frontend story is awkward unless the user goes headless (WP backend + Next.js frontend) — which then makes Next.js the actual stack with WP as CMS layer.

Full per-stack design at `DESIGN-stack-wordpress.md`. The agent invokes `WebFetch` against developer.wordpress.org for current `theme.json` schema, REST API surface, and Block Editor (Gutenberg) capabilities — these also evolve.

### Choosing between the three (decision logic)

The agent does not score the stacks numerically or present a flowchart. The agent asks five questions and lets the answers point at a stack:

1. **"After this site launches, who edits it?"** Solo / designer → Framer leans heavier. Editorial team / non-developer → WordPress leans heavier. The user themselves in a code editor (or a developer they hire) → Next.js leans heavier.
2. **"Where do you want to host?"** Framer-hosted only → Framer. Vercel / Cloudflare / Netlify / self-hosted Node → Next.js. Managed WordPress host or own VPS → WordPress.
3. **"Visual canvas after launch — load-bearing or nice-to-have?"** Load-bearing → Framer. Nice-to-have → either of the others, with a CMS at phase 12 closing the gap.
4. **"How much will the site grow in the next year?"** Stay small (5-15 pages) → any. Grow into a content-heavy publication or product catalog → WordPress or Next.js, not Framer. Grow toward SaaS app territory → Next.js.
5. **"How comfortable is the user in code, on a 1-5 scale?"** 1-2: Framer or WordPress (with a page-builder or block-theme defaults). 3-5: Next.js opens up.

The agent surfaces tradeoffs with concrete language ("if you pick Framer, you can't migrate to a different host without leaving Framer entirely; if you pick Next.js, you'll edit MDX files unless we pick a CMS at the next phase"). The user picks; the agent writes `project.yaml.stack` plus the prose reasoning.

## Expansion stacks (post-MVP, expansion phase 10)

The five stacks below are fully designed in the website-builder workstream (vault-side design; not shipped as MVP adapters) and accessible to users who already know them, but they are **not first-class in the MVP**. Per locked decision 52, they ship in expansion phase 10 of the platform roadmap. The agent mentions them only when the user names one specifically or when an MVP stack is clearly the wrong fit. For v1, the agent steers toward one of the three MVP stacks above.

- **Astro** — content-focused meta-framework, zero JavaScript by default, component islands for opt-in interactivity. The sweet-spot fit for fast content sites (blog, marketing, docs, portfolio). For MVP, the closest substitute is Next.js with the static-export config. Full design at `DESIGN-stack-astro.md`.
- **Hugo** — Go-based static site generator; the fastest in the world (rebuilds 50k-page sites in seconds). Sweet-spot fit for very large content-heavy sites where build time matters. For MVP, the closest substitute is Next.js static export. Full design at `DESIGN-stack-hugo.md`.
- **SvelteKit** — Svelte's meta-framework; smallest bundles among the SSR-capable stacks (no virtual DOM, no runtime). Sweet-spot fit for users who want Next.js-class flexibility with simpler component syntax and smaller payloads. For MVP, the closest substitute is Next.js. Full design at `DESIGN-stack-sveltekit.md`.
- **Webflow** — visual canvas + CMS + hosting in one, similar in spirit to Framer but with deeper CSS-class controls and a Logic flow system. Sweet-spot fit for designer-led teams that want hosted infrastructure. For MVP, the closest substitute is Framer. Full design at `DESIGN-stack-webflow.md`.
- **Plain static HTML** — no framework, no build pipeline, no Node runtime. Just HTML / CSS / vanilla JavaScript files. Sweet-spot fit for tiny sites (1-5 pages) where the user wants maximum code transparency and deployability-anywhere. For MVP, the closest substitute is Next.js static export or — if the user wants the absolute simplest path — wait for expansion phase 10. Full design at `DESIGN-stack-static-html.md`.

If the user insists on an expansion stack for v1, the agent logs the decision in `.website-builder/decisions/stack-expansion-${stack}.md`, surfaces that the in-MVP support level is "design exists, runtime adapters not yet shipped," and either proceeds with degraded support (the user accepts the risk) or routes to an MVP stack with a documented future migration intent. The agent does not pretend MVP support exists when it doesn't.

## Transactional decision (sibling)

A separate sub-decision living in the same phase. Locks `project.yaml.transactional` to `true` or `false`. Drives whether phases 24a / 24b / 24c activate downstream.

The agent asks exactly two questions, verbatim, in this order:

> **"Is anyone going to pay anything on this site?"**
> 
> **"Is anyone going to book anything on this site?"**

Yes to either means transactional. No to both means non-transactional. There is no in-between answer; "maybe later" routes to a follow-up question — *"is the site shipping with payments or bookings before the v1 launch, or are those v1.1?"* — that resolves to a current `true` or `false` and a logged "intended-to-add-later" note in `project.yaml.transactional_followup`.

Edge cases the agent handles:

- **Affiliate links / display ads.** Not transactional. The site does not process payment; an external network does. `transactional: false`, even when the user expects revenue.
- **Newsletter signups / lead-gen forms.** Not transactional. No payment, no booking. `transactional: false`.
- **Donations.** Transactional. Money changes hands; phases 24a / 24b activate. The user picks a payment provider in phase 24b — Stripe is the default MVP path per locked decision 54, with the appropriate non-profit configuration.
- **Free booking calendars without payment.** Transactional. The user is committing time on the site; phases 24a / 24b activate to wire Cal.com (MVP default per locked decision 54). Phase 24b is light when no payment is involved but still runs.
- **Paid course / membership site.** Transactional. Phases 24a-c all activate; the agent recommends Lemon Squeezy or Stripe Checkout (MVP support) at phase 24a.

Per locked decision 34, **changing this flag mid-project triggers a forced restart** of relevant downstream phases (12 CMS may need to change; 22 forms now need payment; 24a/b/c activate from scratch). The agent surfaces this loudly when the question is asked — "answer carefully; if you change your mind at phase 20, we restart from 12." The user can still change their mind, but they do it knowing the cost.

## Gating rules

The agent refuses to advance when:

- **No stack chosen.** No `project.yaml.stack` value, no advance. The agent does not pick a default and proceed.
- **No transactional decision.** No `project.yaml.transactional` value, no advance. The two seed questions must be asked and answered. The agent does not infer the answer from the requirements doc; it asks explicitly.
- **Stack chosen but obvious mismatch with site shape.** If the sitemap shows 200+ pages and the user picked Framer, the agent surfaces the canvas-and-CMS-volume mismatch and asks for a re-decision. If the user is on a regulated industry and picked plain static HTML, the agent surfaces the operational gap (no audit trail of edits, no role-based admin). The agent does not refuse the choice; it surfaces the cost and lets the user confirm.
- **Expansion stack picked without explicit acceptance.** If the user picks Astro / Hugo / SvelteKit / Webflow / static-html for v1, the agent surfaces the expansion-phase-10 framing and writes the explicit-acceptance note to `.website-builder/decisions/stack-expansion-${stack}.md` before proceeding. The agent does not silently accept the expansion stack.
- **Transactional `true` without payment / booking specifics.** If transactional is `true`, the agent asks one follow-up — *"payments, bookings, or both?"* — and records the answer in `project.yaml.transactional_kind` so phases 24a-c can branch correctly when activated.

Override is available on the stack mismatch and expansion-stack gates via explicit user confirmation with the cost surfaced. The "no decision recorded" gate is not overridable — the values must be written before advance.

## Tools and skills used

- **AskUserQuestion** — the primary tool. The agent presents the three MVP stacks, walks through the five decision questions, asks the two transactional-decision questions verbatim, and surfaces the expansion-stack framing when relevant.
- **`mcp__context7__resolve-library-id` + `mcp__context7__query-docs`** — invoked for each stack the user is seriously considering. Required for `/vercel/next.js` if Next.js is on the table; recommended for the others. The agent caches fetched docs to `.website-builder/library/docs/${stack}.md` for re-read at phases 17 / 18 / 22 / 28-30. See [`DESIGN-context7-integration.md`](../../../DESIGN-context7-integration.md) for the invocation pattern.
- **`WebFetch`** — used when context7 lacks fresh coverage. The agent fetches framer.com/developers, developer.wordpress.org, and similar canonical-source docs to confirm current capabilities. URLs are recorded in the reference-materials section of this contract and re-fetched at later phases if stale.
- **`WebSearch`** — used sparingly. The agent may search "Next.js 15 [feature] 2026" or similar when context7 results need supplementing for very recent capabilities.
- **Reference-data load** — the agent reads the per-stack design docs (`stacks/DESIGN-stack-*.md` in the workstream) for capability matrices, auth models, output mappings, deploy notes, and known limitations. These are the source of truth, not the agent's training data.
- **Read** — agent reads `.website-builder/sitemap.yaml`, `.website-builder/brand.yaml.voice`, `.website-builder/project.yaml.requirements` to anchor the stack recommendation in the project's actual shape.

No `Write` / `Edit` on code files in this phase — those tools are gated until phase 18.

## Output artifacts

The agent writes to `.website-builder/project.yaml`:

```yaml
# .website-builder/project.yaml — values added at phase 11
stack: nextjs                              # framer | nextjs | wordpress (MVP) or expansion stack with logged decision
stack_reasoning: |
  Picked Next.js because the user wants a real codebase they can read,
  the site grows toward a SaaS app over the next year (per phase 3 requirements),
  and they're comfortable in a code editor (level 4 of 5 on the discovery questionnaire).
  Framer ruled out (no canvas-after-launch need); WordPress ruled out (operational overhead too high for solo).
transactional: true                        # true | false
transactional_kind: payments               # payments | bookings | both | none (when transactional=false)
transactional_reasoning: |
  Site sells digital downloads (paid PDFs). User confirmed "yes" to payment question.
  Phases 24a (commerce platform), 24b (payment provider), 24c (commerce legal) will activate.
transactional_followup: ~                  # null when transactional decided cleanly; populated when "v1.1 intent" surfaces
```

The agent also seeds `.website-builder/library/docs/${stack}.md` with the cached context7 / WebFetch output for the chosen stack.

If the user picked an expansion stack, the agent writes `.website-builder/decisions/stack-expansion-${stack}.md` documenting the choice, the agent's surfaced cost, and the user's explicit acceptance.

## Common failure modes

**"I've heard people talk about Next.js, let's go with that."** Cargo-culting. The agent surfaces that "I've heard of it" is not a stack-fit signal and walks the five-question decision logic. Common outcome: the user finds out their site is better fit for Framer or WordPress and updates their picture of what Next.js actually is.

**"My designer says use Webflow."** Webflow is an expansion stack for the MVP. The agent surfaces the closest MVP substitute (Framer) and offers either to use Framer with explicit acceptance, or to log Webflow as a v1.1 migration target and proceed on Framer for v1. The agent does not pretend Webflow is MVP-supported.

**"Why can't I just use [framework du jour]?"** New frameworks appear every cycle. The agent uses context7 to confirm whether the named framework has reached mainstream adoption (snippet count, source reputation, benchmark score). If yes, the agent surfaces the trade-off explicitly: the MVP supports three stacks; building on something outside that set means MVP support gaps. If the user accepts, the same expansion-stack logging path applies.

**"I don't know if I'm transactional. Maybe I'll add payments later."** The agent asks: *"is the site shipping with payments before v1 launch?"* Yes → `transactional: true` now. No → `transactional: false` now, with `transactional_followup: "user intends to add payments post-launch"` recorded so the user knows the cost of changing later (phase restart of 12, 22, 24a-c).

**"I want Framer but with a custom backend."** Common designer-developer collision. The agent surfaces the option: Framer for the marketing front-end, Next.js + Payload (decided at phase 12) for the backend, with the Framer site embedding into or linking out to the application. This works but is two projects; the agent recommends picking one for v1 and adding the second post-launch.

**"What about [WordPress.com / Wix / Squarespace / Carrd / Webflow]?"** WordPress in the MVP is **self-hosted or managed-WP (Kinsta / WP Engine / SiteGround / Cloudways)** — WordPress.com Business+ is supported as a managed option but the lower plans (Free / Personal / Premium) cannot install custom themes and are not MVP-compatible. Wix / Squarespace / Carrd are outside the eight-stack design surface; the agent does not support them. Webflow is expansion-phase-10 (see above).

**User wants to defer the transactional decision.** Not allowed. The agent surfaces that without a `transactional` value, phase 12 (CMS decision) cannot proceed (some CMS choices — Ghost, certain WooCommerce setups — depend on transactional intent), and phases 24a-c floats indefinitely. The two seed questions get asked again.

**Hidden assumption that the stack picks the CMS.** Stack and CMS are separate decisions; phase 11 picks stack, phase 12 picks CMS. The agent surfaces that pairing happens at phase 12 — *"we'll pick how content is managed in the next phase; for now, focus on the framework"*. Some stack-CMS pairings are natural (WordPress with WordPress core; Framer with Framer CMS; Next.js with Payload / Decap / file-based markdown), and the agent will guide toward those at phase 12.

**Stack changed mid-project.** Phase 11's stack decision is not as locked as the transactional flag — the agent supports stack change mid-project but with a forced phase-18 (component build) restart for the new stack. The pre-step-11 stack-agnostic artifacts (`brand.yaml`, `sitemap.yaml`, `content/pages/*.md`, `content/strings/*.json`, `components.yaml`) survive the stack switch; the post-step-18 stack-specific code does not. The agent surfaces this when stack-change is requested.

## Reference materials

Per-stack design docs (full reads for any stack the user considers seriously):

- `DESIGN-stack-framer.md` — MVP
- `DESIGN-stack-nextjs.md` — MVP
- `DESIGN-stack-wordpress.md` — MVP
- `DESIGN-stack-astro.md` — expansion phase 10
- `DESIGN-stack-hugo.md` — expansion phase 10
- `DESIGN-stack-sveltekit.md` — expansion phase 10
- `DESIGN-stack-webflow.md` — expansion phase 10
- `DESIGN-stack-static-html.md` — expansion phase 10

Foundation docs:

- `DESIGN-project-scaffold.md` § migration recipes — the per-stack mapping from `.website-builder/` to deployed code.
- `DESIGN-architecture.md` § Component breakdown — how the chosen stack interacts with the plugin's adapter layer.
- `DESIGN-context7-integration.md` — context7 invocation pattern for stack docs.

Context7 lookups (mandatory for the MVP stack the user picks; recommended for the others when surfaced as alternatives):

- `/vercel/next.js` — Next.js (benchmark 89.84, High reputation, 2178 code snippets). Current as of 2026-05-18 fetch. Versions: v16.x current; v15.x supported. Cached to `.website-builder/library/docs/nextjs.md`.
- `/payloadcms/payload` — Payload v3 (benchmark 82.1, High reputation, 2279 code snippets, v3.84.0 latest). Used at phase 11 for Next.js + Payload pairing preview; full coverage at phase 12. Cached to `.website-builder/library/docs/payload.md`.
- Framer — `mcp__context7__resolve-library-id` first; if not present at sufficient quality, `WebFetch` framer.com/developers and framer.com/help for current Server API + Custom Components SDK + Framer CMS capabilities.
- WordPress — `WebFetch` developer.wordpress.org for current `theme.json` schema, REST API surface, and Gutenberg block editor capabilities.

Freshness date for this contract's references: **2026-05-18** (date of authoring). The agent re-validates current state via context7 at session start when phase 11 is the active phase, and re-fetches if cached `.website-builder/library/docs/${stack}.md` is more than 30 days old.

## Skip authorization

Phase 11 is not skippable. The two decisions it produces are load-bearing for every downstream phase: the stack drives migration recipes (phase 18+), and the transactional flag drives whether 24a/b/c activate.

The two narrow legitimate paths around phase 11:

1. **Entry-mode pre-fill from `has-existing-site` / `has-framer-attempt` / `has-figma-file`.** Phase 6.5 (artifact ingestion) may have already detected the stack from the existing artifact (e.g., the user has a deployed Next.js site at the URL they provided; the entry-mode flow set `project.yaml.stack = nextjs` automatically). In this case, phase 11 still runs but as a confirmation pass: the agent surfaces "phase 6.5 detected Next.js as your existing stack — confirm or change?" plus the transactional decision (which is never auto-detected). Not a skip; a thin pass.
2. **Pure-API site (no frontend).** Out of scope for the website-builder — this is a different product. The agent surfaces that this workstream produces websites; pure APIs are platform-tier work. Routes to platform-General or similar.

Skipping phase 11 entirely is not authorized. If the user requests it, the agent surfaces that without `stack` and `transactional` set, every downstream phase has missing context, and routes back to the two-question transactional decision plus the five-question stack decision.
