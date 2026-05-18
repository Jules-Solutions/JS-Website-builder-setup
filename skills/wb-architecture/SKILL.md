---
name: wb-architecture
description: This skill should be used when the website-builder agent reaches phases 10-12 of the pipeline — when the user says "let's set up the navigation", "design the site menu / nav structure", "which stack should I use", "pick a framework", "should I use Next.js / Framer / WordPress", "do I need a CMS", "how will content be managed", "am I selling anything on this site", or when project.yaml.current_phase is 10, 11, or 12. Drives the three architecture decisions — information architecture / navigation (phase 10), technology stack plus the forced transactional sibling (phase 11), and CMS (phase 12).
version: 0.1.0
---

# wb-architecture — Architecture Phases (IA / Nav · Stack · CMS)

> The three structural pivots of a website-builder project. Phase 10 turns the page list into a navigation users can move through. Phase 11 picks the technology stack AND forces the transactional yes/no in the same packet. Phase 12 picks how content is managed on top of the stack. Every downstream phase compiles against what these three decisions produce.
>
> The phase contracts are the authoritative substantive reference. This skill carries the workflow; the contracts carry the per-phase Mission / Entry / Exit / Gating / Tools / Outputs / Common-failures. Always read the contract for the active phase verbatim before driving it.

## What this skill governs

| Phase | Decision | Writes to | Contract |
|---|---|---|---|
| **10** | Information architecture / nav strategy | `.website-builder/sitemap.yaml` → `navigation:` block | `phase-contracts/10-information-architecture.md` |
| **11** | Stack decision **+ transactional sibling (forced together)** | `.website-builder/project.yaml` → `stack`, `stack_reasoning`, `transactional`, `transactional_kind`, `transactional_reasoning` | `phase-contracts/11-stack-decision.md` |
| **12** | CMS decision | `.website-builder/project.yaml` → `cms`, `cms_reasoning`, `cms_hosting`, `cms_i18n_strategy` | `phase-contracts/12-cms-decision.md` |

Phases 10-12 run in strict order. Phase 11 cannot start until phase 10's `navigation:` block exists; phase 12 cannot start until both `stack` and `transactional` are written. No `Write`/`Edit` on code files in any of these phases — code is gated until phase 18. The only writes are to `.website-builder/sitemap.yaml` and `.website-builder/project.yaml` (plus optional `.website-builder/decisions/*.md` logs).

## MVP scope (locked decisions 52 + 53 — non-negotiable for v1)

- **Stacks (decision 52):** MVP supports **Framer, Next.js, WordPress** as build-now options. Astro, Hugo, SvelteKit, Webflow, plain static HTML are *fully designed but expansion-phase-10* — surface them only when the user names one or when an MVP stack is clearly wrong, and route to the closest MVP substitute with a logged deferral. Never pretend MVP runtime support exists when it doesn't.
- **CMS (decision 53):** MVP supports **none, Decap, Payload** plus the stack-built-in defaults (Framer CMS when stack=Framer; wordpress-core when stack=WordPress). Strapi, Sanity, TinaCMS, Directus, Keystone, Ghost are expansion-phase-10 — same surface-and-substitute discipline as expansion stacks.

The agent never numerically scores options or shows a flowchart. It asks the decision questions in the contracts and lets the answers point at a choice.

## Phase 10 — Information architecture / nav strategy

Read `phase-contracts/10-information-architecture.md` verbatim first. The workflow:

1. **Read `.website-builder/sitemap.yaml`** — enumerate every page (slug, page-type, purpose, parent).
2. **Drive the 8 decisions** via `AskUserQuestion`, one or more interaction per decision: primary-nav contents, primary-nav order, dropdown-vs-flat per item, footer-nav contents, utility-nav contents, breadcrumb rules, active-state behavior, mobile pattern. See `references/ia-patterns.md` for archetypes, the Hick's-Law 5-7 ceiling rationale, and per-zone defaults.
3. **Enforce the gating rules** — refuse-once-and-surface-cost on: >7 primary-nav items, an unreachable page, mobile-pattern/nav-count mismatch, missing language-switcher on a multilingual site, omitted breadcrumbs on a deep site. Override is available via explicit user confirmation with the cost stated; the agent surfaces the specific cost ("users will fail to find X% of pages") and logs overrides to `.website-builder/decisions/`.
4. **Write the `navigation:` block** into `.website-builder/sitemap.yaml` per the contract's schema (primary/footer/utility/breadcrumbs/mobile). Use `{strings.nav.*}` references for labels — phase 16 supplies the values; phase 10 stays stack- and language-agnostic.
5. **Challenge the sitemap** if nav work reveals a page with no path or two pages that are really one — surface and briefly re-open phase 9 to resolve, do not paper over.

The agent does NOT write the nav component code here. Phase 18 does, per the chosen stack. Phase 10 produces the structural contract the component reads. Defer sticky-nav / visual-behavior questions to phase 17/18 (see contract Common failure modes).

## Phase 11 — Stack decision + transactional sibling

Read `phase-contracts/11-stack-decision.md` verbatim first. **Two decisions, one packet — the agent refuses to advance with one resolved and the other floating.**

### Stack sub-decision

1. **Mandatory context7 before recommending.** Stacks drift; training data is stale. Per the matrix, context7 is mandatory for this group. Invoke per `references/context7-protocol.md`:
   - `mcp__context7__query-docs` `/vercel/next.js` — App Router, RSC, rendering modes, the Next.js 15 fetch no-store default change (breaking vs Next.js 14 `force-cache`).
   - `mcp__context7__query-docs` `/payloadcms/payload` — used here for the Next.js + Payload pairing preview (full coverage at phase 12).
   - Framer — `mcp__context7__resolve-library-id` for "Framer"; if not present at sufficient quality, `WebFetch` framer.com/developers + framer.com/help for current Server API + Custom Components SDK + Framer CMS.
   - WordPress — `WebFetch` developer.wordpress.org for current `theme.json` schema, REST API, Gutenberg/FSE.
   - Cache fetched docs to `.website-builder/library/docs/${stack}.md` for re-read at phases 17/18/22/28-30. Re-fetch if cached doc is >30 days old.
2. **Walk the 5 decision questions** (who edits after launch / where to host / canvas-after-launch load-bearing / growth trajectory / code comfort 1-5). Let the answers point at Framer, Next.js, or WordPress. Full per-stack prose, sweet-spots, and trade-offs are in `references/stack-matrix.md`.
3. **Expansion-stack discipline** — if the user names Astro/Hugo/SvelteKit/Webflow/static-html, surface the expansion-phase-10 framing, offer the closest MVP substitute, and either proceed on the MVP stack or log `.website-builder/decisions/stack-expansion-${stack}.md` with the user's explicit acceptance. Never silently accept.
4. **Write** `project.yaml.stack` + `project.yaml.stack_reasoning` (2-4 sentences — re-read at phases 12 and 18, not throwaway).

### Transactional sub-decision (the sibling)

The agent asks **exactly these two questions, verbatim, in this order**, via `AskUserQuestion`:

> **"Is anyone going to pay anything on this site?"**
>
> **"Is anyone going to book anything on this site?"**

Yes to either → `transactional: true`. No to both → `transactional: false`. "Maybe later" routes to the follow-up *"is the site shipping with payments or bookings before v1 launch, or are those v1.1?"* which resolves to a concrete boolean plus a `transactional_followup` note. Edge-case rulings (affiliate links / ads = false; donations = true; free booking = true; newsletter = false; paid course/membership = true) are in `references/stack-matrix.md` § Transactional.

**Surface the mid-project-pivot cost loudly when asking** (locked decision 34): changing this flag later forces a restart of phases 12 + 22 + 24a/b/c. Say it explicitly — "answer carefully; if you change your mind at phase 20, we restart from 12." The user can still change later; they decide knowing the cost.

When `transactional: true`, ask the one follow-up *"payments, bookings, or both?"* and record `project.yaml.transactional_kind` so phases 24a-c branch correctly.

**Gating:** "no stack value" and "no transactional value" gates are NOT overridable — both must be written before advancing to phase 12. Stack/site-shape mismatch and expansion-stack gates are overridable with cost surfaced.

## Phase 12 — CMS decision

Read `phase-contracts/12-cms-decision.md` verbatim first. The workflow:

1. **Read** `project.yaml.stack`, `.transactional`, `.languages`, `.sitemap.yaml` (page count) — anchor the CMS pick in the project's actual shape.
2. **Stack-native fast path.** When stack=Framer → default `framer-cms`; when stack=WordPress → default `wordpress-core`. Surface as the path of least resistance; only diverge with explicit user reasoning (the headless-WordPress / headless-Framer escape hatch re-opens phase 11). This is a thin confirmation pass, not a skip.
3. **Next.js → the MVP triplet.** Walk `none` / `decap` / `payload` trade-offs. Challenge defaults — surface YAGNI honestly ("5 pages edited quarterly = file-based markdown is enough") and only escalate when content shape demands it (multiple editors, structured relationships, role-based access, non-markdown content). Full per-CMS prose, fit/anti-fit, and the Decap-maintenance-mode caveat are in `references/cms-matrix.md`.
4. **Mandatory context7 for the CMS on the table** (per matrix):
   - `mcp__context7__query-docs` `/payloadcms/payload` — Collections, Blocks field, field-level localization, access control, drafts/versions, live preview, Next.js install, Postgres adapter, the `pnpm payload migrate && next build` deploy command.
   - Decap — `WebFetch` decapcms.org/docs (context7 coverage thin) for config-schema, OAuth backends, `structure: multiple_files` i18n. Surface active forks Sveltia CMS + Static CMS as upgrade paths since Decap upstream is in maintenance mode.
   - Cache to `.website-builder/library/docs/${cms}.md`.
5. **Lock the i18n strategy now** for multilingual sites — `cms_i18n_strategy: pattern-a` (shared structure, translated prose — the decision-39 default) or `pattern-b` (per-locale layouts). Failing to lock here produces drift at phase 16. Decap → `structure: multiple_files`; Payload → field-level `localized: true` + `localization.fallback: true`.
6. **Enforce gating** — incompatible-with-stack (Payload on Hugo, Framer-CMS on Next.js) is not overridable; YAGNI-direction gates (heavy CMS on a tiny site, `none` on a 200-page 3-editor site) are overridable with honest logging. Transactional sites need a transactional-capable CMS path (WP+WooCommerce, Next.js+Payload, or Framer+embedded checkout).
7. **Write** `project.yaml.cms` + `cms_reasoning` + (if separate hosting needed) `cms_hosting` + (if multilingual) `cms_i18n_strategy`. When CMS=Payload+Postgres, also draft the phase-29 readiness note `.website-builder/decisions/cms-12-payload-postgres-host.md` so the deploy phase has hosting pre-staged. Expansion-CMS picks log to `.website-builder/decisions/cms-expansion-${cms}.md` with explicit acceptance.

## Cross-phase discipline

- **Stack and CMS are separate decisions.** Phase 11 = stack only; phase 12 = CMS. Some pairings are natural (WordPress↔wordpress-core, Framer↔framer-cms, Next.js↔none/decap/payload) and the agent guides toward them at phase 12 — but never lets the user think the stack auto-picks the CMS.
- **Stack change mid-project** is supported (forced phase-18 restart for the new stack; pre-phase-18 stack-agnostic artifacts survive). Transactional change mid-project is heavier (decision 34 forced restart of 12/22/24a-c). Surface both costs when the relevant change is requested.
- **Entry-mode thin passes** — when phase 6.5 detected an existing stack/CMS from an ingested artifact, phases 11/12 still run as confirmation passes ("phase 6.5 detected Next.js — confirm or change?") plus the never-auto-detected transactional decision. Not a skip.
- **Pause-and-report** — surface architectural ambiguities to the General via a `kind: question` standup. Do not modify foundation docs, phase contracts, or the agent profile — those are out of scope.

## Composable plugin skills

This phase group has **no bundled composables** — context7 is the load-bearing external surface (per matrix). The agent relies on `mcp__context7__*` + `WebFetch` for current stack/CMS docs, not on third-party skills. Do not recommend design/build composables here; those belong to phases 17-18.

## Additional resources

### Reference files (load on demand)

- **`references/stack-matrix.md`** — full per-stack prose (Framer / Next.js / WordPress sweet-spots, trade-offs, decision logic), expansion-stack substitution table, and the complete transactional edge-case rulings + mid-project-pivot cost.
- **`references/cms-matrix.md`** — full per-CMS prose (none / Decap / Payload fit and anti-fit), stack-built-in defaults, the Decap-maintenance-mode caveat + fork upgrade paths, the i18n strategy table, and the expansion-CMS substitution table.
- **`references/ia-patterns.md`** — navigation archetypes per zone, the Hick's-Law 5-7 ceiling rationale, mobile-pattern selection guide, breadcrumb/SEO rules, the single-page degenerate-IA case, and the `navigation:` block schema with annotated examples.
- **`references/context7-protocol.md`** — exact context7/WebFetch invocation pattern for stack + CMS docs, the caching convention (`.website-builder/library/docs/${name}.md`), freshness/re-fetch rule, and the verified-current external-source findings (2026-05-18).

### Authoritative substantive references (read verbatim per active phase)

- `phase-contracts/10-information-architecture.md`, `phase-contracts/11-stack-decision.md`, `phase-contracts/12-cms-decision.md`
- Per-stack design: `Workstreams/website-builder/stacks/DESIGN-stack-{framer,nextjs,wordpress}.md` (MVP) — read fully for any stack the user considers seriously.
- Per-CMS design: `Workstreams/website-builder/cms/DESIGN-cms-{none,decap,payload}.md` (MVP) — read fully for any CMS the user considers seriously.
- Foundation: `Workstreams/website-builder/foundation/DESIGN-ecosystem-catalog.md` (IA pattern subset), `foundation/DESIGN-i18n.md` (Pattern A/B), `foundation/DESIGN-project-scaffold.md` (sitemap.yaml + project.yaml schema + migration recipes), `foundation/DESIGN-architecture.md` § Skills.
