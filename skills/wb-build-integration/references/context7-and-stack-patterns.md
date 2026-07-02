# context7 + per-stack patterns (phases 19-23)

> When and how this phase group uses context7, the per-stack library-id manifest it reads, and the resolution-failure fallback. Derived from `DESIGN-context7-integration.md` (locked decision 23) + `.claude/rules/context7.md`. On conflict, the design doc wins.

## Why context7 is load-bearing here

Phases 19, 20, 22 all write or verify **stack-specific code** (routing/composition, responsive primitives, perf primitives). Phase 23 wires **provider/library integrations** (form libraries, providers). Training-data drift is real and a muggle can't catch a subtly-wrong-but-plausible old pattern (the canonical example: emitting Pages-Router `getServerSideProps` when the project is App Router). context7 is the live read-through path. The rule: **context7 fires when the agent works with a *named* technology; never for stack-agnostic decisions.**

## Invocation pattern

```
1. Identify the named library/framework the agent needs docs for
2. mcp__context7__resolve-library-id(library_name, the user's actual phase-context question)
     → ranked library IDs (format /org/project)
3. Pick the best ID (exact name match → description relevance → snippet count → reputation → benchmark)
4. mcp__context7__query-docs(library_id, the specific phase-context question)
5. Apply to what the agent is about to write/verify; surface to the user when material
   ("Per current Next.js docs, App Router uses..." — not silently emitting app/ code)
```

Skip step 2 (resolve) when the user gave an exact ID or there is a recent in-session cached resolution. Query phrasing: specific beats vague — `query-docs("/vercel/next.js", "dynamic catch-all routes with i18n in App Router")`, not `query-docs("/vercel/next.js", "routing")`.

## Per-phase context7 usage in this group

| Phase | What to look up | Typical query |
|---|---|---|
| **19 composition** | Chosen stack's current routing + composition idiom | "App Router layout nesting + Server/Client component rules" (Next); "dynamic params + island hydration directives" (Astro); "content + layout pairing" (Hugo) |
| **20 responsive** | Stack's current responsive primitives | "container queries + current responsive-variant API" (Tailwind v4 — container queries are core, not a plugin); framework breakpoint conventions |
| **21 a11y** | a11y tooling current invocation + library a11y patterns | `/dequelabs/axe-core` current CLI/Playwright API; `/GoogleChrome/lighthouse` current a11y category; chosen component library's focus-management specifics (e.g. Radix) |
| **22 perf** | Stack's current perf primitives + Lighthouse scoring | `/vercel/next.js` `next/image`/`next/font`/`next/dynamic`; Astro `<Image>` + asset processing; `/GoogleChrome/lighthouse` current scoring + CI config |
| **23 forms** | Form library + chosen provider current integration | "react-hook-form + zod resolver"; the stack's form action/route pattern; the chosen provider's current integration (`formspree setup`, Resend server-route quickstart) |

context7 does **not** fire for stack-agnostic work — there is none of that in 19-23 except phase-19's content-overflow reconciliation (a layout judgment, not a library lookup) and the manual keyboard walk in 21 (a Playwright-driven inspection, not a doc lookup).

## Per-stack library-id manifest

The agent reads the per-stack manifest at `reference-corpus/seeds/{stack}.yaml` (set when the stack was chosen at phase 11). The IDs relevant to *this* phase group, by stack (from `DESIGN-context7-integration.md`):

| Stack | Phase-19/20/22 primary | Phase-21/22 cross-stack |
|---|---|---|
| **Next.js** | `/vercel/next.js` (App Router routing/composition, `next/image`, `next/font`, `next/dynamic`) + `/tailwindlabs/tailwindcss.com` (responsive) | — |
| **Astro** | `/withastro/docs` (routing, island hydration, `<Image>`, asset processing) + `/tailwindlabs/tailwindcss.com` | — |
| **Hugo** | `/gohugoio/hugo` (content+layout pairing, image pipeline) | — |
| **SvelteKit** | `/sveltejs/kit` (+ `/sveltejs/svelte`) | — |
| **Framer** | `/framer/server-api-docs` (+ `/framer/motion`) | — |
| **WordPress** | `/wordpress/wp-rest-api` (+ block-editor-handbook) | — |
| **Webflow** | `/webflow/webflow-api` | — |
| **Plain static HTML** | `/tailwindlabs/tailwindcss.com` | — |
| **All stacks (phase 21/22)** | — | `/dequelabs/axe-core` (a11y, phase 21), `/GoogleChrome/lighthouse` (a11y + perf, phases 21+22), `/microsoft/playwright` (driving 20/21/23) |

`use_at_phases` arrays in the manifests already mark which IDs apply at 17/18/19/20/21/22/26/29 — phases 19-23 read the entries tagged for them.

## Caching (per the design doc)

Three layers, to avoid latency/token cost:

1. **In-session memory** — same-session repeated queries on the same library/topic don't re-call.
2. **`clone-into-project`** — when a phase queries a library repeatedly (phase-22 hitting `next/image`/`next/font` patterns, phase-21 hitting axe-core patterns), clone the relevant docs to `.website-builder/library/docs/{name}.md` with `library/.metadata.yaml` (source, library_id, cloned_at, freshness cadence). Read the local clone first.
3. **Re-fetch on freshness flag** — when the cadence elapses, prompt the user at session-start ("cached shadcn/ui docs from {date} — refresh?"). User-driven; never silent re-fetch.

Not cached: one-off API queries, failed resolutions (re-resolve next time).

## Resolution-failure fallback (Tier 2 per `tool-dependency-discipline.md`)

If `resolve-library-id` returns no match:

1. Re-query with alternate names ("next.js" not "nextjs"; "tailwind css" not "tailwindcss").
2. WebFetch the canonical docs URL directly (e.g. `https://docs.astro.build`, `https://playwright.dev/docs/accessibility-testing`, `https://web.dev/articles/vitals`).
3. Surface to the user: *"context7 didn't have this library; I'm reading from {URL} instead. Heads up if anything looks off — my training data may be stale on this."*
4. Log the fallback to `.website-builder/decisions/context7-fallback-{ts}.md` for audit.

If context7 is unreachable entirely: surface ("context7 isn't responding"), offer the WebFetch fallback, continue the phase, log the gap, let the user retry later (`wb library refresh`). Soft-stop + fall-back-with-diagnosis — never silently proceed on stale training data for a named-technology code path.

If context7 returns a suspected-stale answer (references an API the agent knows was deprecated): surface it, WebFetch the canonical docs URL to verify, prefer the canonical source.

## Source freshness

- context7 invocation pattern, per-stack manifest, per-phase usage table, caching, fallback: `DESIGN-context7-integration.md` (locked decision 23), 2026-05-10.
- The actual current API shapes this phase group depends on were independently verified via context7 2026-05-18 — see `playwright-recipes.md` + `axe-lighthouse-recipes.md` § Source freshness.
- context7 rule: `.claude/rules/context7.md`. Tool-dependency tiers: `.claude/rules/tool-dependency-discipline.md`.
