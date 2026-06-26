---
phase: 22
name: Performance audit
group: build-integration
pipeline_section: build-integration
skill: wb-build-integration
prev_phase: 21
next_phase: 23
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-phase-contracts.md
  - Workstreams/website-builder/foundation/DESIGN-architecture.md
  - Workstreams/website-builder/foundation/DESIGN-project-scaffold.md
  - Workstreams/website-builder/cross-cutting/DESIGN-context7-integration.md
library_clones_at_entry:
  - resource: seo-checklists
    as: seo-checklists
    note: "Lighthouse-mapped performance + SEO checklists (the baseline phase 22 and 26 audits check against)"
---

# Phase 22 — Performance audit

> Lighthouse 80+ on performance, with Core Web Vitals in the green: LCP, CLS, INP. Image optimization, lazy loading, font-loading strategy. The phase that makes the site fast enough that real visitors on real networks on real phones don't bounce before it loads. The agent refuses to advance with a perf score below 80.

## Mission

Phase 21 made the site usable for everyone. Phase 22 makes it *fast* for everyone — fast on a mid-range phone on a 4G connection, which is what a large share of real visitors actually are, not the developer's wired desktop.

The work product is `.website-builder/audit/PERF-REPORT.md`: a Lighthouse run scoring 80+ on the performance category, with Core Web Vitals in the "good" band — LCP < 2.5s, CLS < 0.1, INP < 200ms (the current CWV thresholds, measured at the 75th percentile; INP replaced FID as a stable Core Web Vital) — plus images served at correct sizes and formats, lazy-loading where appropriate, and an intentional font-loading strategy. After phase 22, the site is fast enough to keep the visitors phase 1-21 worked to earn.

The discipline of this phase is **the score is a verified gate, not a vibe**. "Feels fast on my machine" is the developer testing on a fast machine on a fast network with a warm cache — the opposite of the median visitor. Phase 17 already pre-budgeted heavy motion and phase 18 already enforced lazy-loading on animation-heavy components — phase 22 is where that is *measured on the assembled site* and where anything that slipped (an unoptimized hero image, a render-blocking font, a layout-shifting ad-hoc element) is caught and fixed before it costs real visitors.

## Entry conditions

- Phase 21 (accessibility audit) complete. The site clears WCAG 2.1 AA basics (or has a logged, authorized a11y skip). Phase 22 audits the same assembled, responsive, accessible site for speed.
- Phase 20 (responsive pass) complete. Performance is measured on the responsive site, mobile-first (the mobile Lighthouse run is the one that matters most — it's the slowest realistic profile).
- Phase 17 (design system) complete with a motion budget. The phase-17 motion tokens + `prefers-reduced-motion` posture pre-allocated the cost of any heavy animation; phase 22 verifies the assembled site stays inside that budget.
- Phase 18 (component build) complete with lazy-loading wired on heavy components. Animation-heavy library components (Aceternity/Magic UI, Three.js-backed effects) were supposed to ship with dynamic-import + reduced-motion + static SSR fallback at phase 18; phase 22 verifies that held and the hero doesn't blow the LCP budget.
- Phase 8 (image strategy) complete. Every image had a sourcing + purpose decision; phase 22 verifies they're served optimized (right format, right responsive sizes), not as the 4MB original.

## What Claude must establish

A verified performance pass on the assembled, responsive site:

1. **Lighthouse performance score ≥ 80.** Run via Lighthouse CLI / Lighthouse CI against the production build (not the dev server — dev builds are unoptimized and give a falsely low score; the agent audits a `next build && next start` / `astro build && preview` / equivalent). Mobile profile is the gating run (slowest realistic device + network throttling); desktop reported alongside.
2. **Core Web Vitals in the good band:**
   - **LCP < 2.5s** — the largest contentful paint (usually the hero image or headline) renders within 2.5s. Lab metric here; the agent notes that field data (75th percentile, real users) is the true target and lab is the proxy.
   - **CLS < 0.1** — cumulative layout shift; nothing jumps as the page loads (un-dimensioned images, late-loading fonts causing reflow, injected content).
   - **INP < 200ms** — interaction to next paint; the page responds to taps/clicks within 200ms (INP is the stable Core Web Vital that replaced FID; the agent budgets main-thread work accordingly).
3. **Image optimization.** Every image served in a modern format (AVIF/WebP with fallback), at responsive sizes (not one 4MB desktop original shipped to a phone), with explicit dimensions (prevents CLS), lazy-loaded below the fold, eager + preloaded for the LCP image.
4. **Font-loading strategy.** The phase-17 fonts loaded without blocking render and without causing a layout shift — `font-display: swap` (or `optional`), `preconnect`/`preload` for the critical font, system-stack fallback metrics-matched to minimize the swap shift. Self-hosted or properly-hinted Google-Fonts loading per stack.
5. **Lazy loading + code splitting.** Below-the-fold images and heavy interactive/animation components dynamically imported; the critical path kept lean. Heavy library components (the phase-18 Aceternity/Three.js case) confirmed dynamically imported with a static fallback.

Output: `.website-builder/audit/PERF-REPORT.md`. `.website-builder/project.yaml.current_phase` updates to `23` only when perf ≥ 80 and CWV are green (or a documented, user-confirmed skip per `## Skip authorization`). Phase 23 (forms + interactive logic) loads next.

## Gating rules

The agent refuses to advance when:

- **Lighthouse performance score < 80** (mobile profile, production build). This is the headline gate. The agent does not advance a slow site; it identifies the largest opportunities (Lighthouse's own "Opportunities" + "Diagnostics" sections name them) and fixes them.
- **LCP ≥ 2.5s.** The most-impactful CWV. Usually an unoptimized/unpreloaded hero image or a render-blocking resource. The agent fixes the LCP element (optimize + preload the hero, remove the blocker) — non-overridable as a target, because LCP is what the visitor experiences as "is this site even loading."
- **CLS ≥ 0.1.** Visible layout jump as the page settles. The agent finds the shifting element (un-dimensioned media, late font swap, injected content) and pins it.
- **INP ≥ 200ms.** The page feels laggy on interaction. The agent reduces main-thread work (split heavy JS, defer non-critical script).
- **The audit ran against the dev server, not the production build.** A dev-build Lighthouse number is meaningless (unminified, unsplit). The agent re-runs against the real build.
- **An unoptimized hero image shipped.** The single most common perf killer in muggle sites — a 3MB PNG hero. The agent generates responsive variants + modern format + correct sizing before advance.
- **The score was asserted, not measured.** "It's fast" without a Lighthouse run + the report is not a phase-22 pass.

The score/CWV gates are **not individually overridable** — they are correctness thresholds. The *entire phase* may be skipped only under the explicit, cost-surfaced, logged authorization in `## Skip authorization`; "ship at score 62 because it's close" is not a path.

## Tools and skills used

- **`Bash`** — to produce the production build (`next build && next start`, `astro build && astro preview`, `hugo`, `vite build && vite preview`) and run the audit: Lighthouse CLI (`lighthouse <url> --only-categories=performance --preset=desktop`/mobile) or Lighthouse CI (`lhci autorun` with a `categories:performance` assertion + CWV assertions). The agent audits the production build, throttled to a mobile profile.
- **Playwright MCP** — for targeted measurement + reproduction: capturing the LCP element, observing the layout shift live, profiling an interaction's responsiveness, and confirming a fix at the same viewport phase 20 verified.
- **`mcp__context7__resolve-library-id` + `mcp__context7__query-docs`** — per `DESIGN-context7-integration.md`, phase 22 invokes context7 for the stack's current performance primitives (`/vercel/next.js` `next/image` + `next/font` + dynamic-import API, `/withastro/docs` asset processing + `<Image>` + island hydration strategy, `/GoogleChrome/lighthouse` current scoring + CI config) and `.website-builder/library/seo-checklists/` Lighthouse-mapped checklists. Perf APIs change (the framework's image/font components evolve); the agent verifies current patterns.
- **The image-gen consumer / image tooling** — when an image needs responsive variants + format conversion, the agent uses the phase-8 image pipeline (per `DESIGN-architecture.md` § consumers) to generate optimized sizes/formats, or the stack's build-time image optimizer (`next/image`, Astro `<Image>`, an Eleventy/Hugo image pipeline).
- **`Edit` / `Write`** — to apply the fixes (swap to `next/image`/`<Image>`, add `font-display` + preload, dynamic-import a heavy component, add explicit image dimensions, split a bundle) and write `audit/PERF-REPORT.md`.
- **`Read`** — `brand.yaml.tokens` (the phase-17 motion budget + fonts), `components.yaml` (which components were flagged heavy at phase 18), `media/IMAGE-PLAN.md` (image inventory + the LCP candidate).

The `wb-build-integration` phase-group skill remains loaded (single skill for phases 19-23, Decision 64). It carries the cross-phase contract that phase 22 verifies the perf budget phase 17/18 set, and that phase 27 (cross-browser QA) and phase 30 (post-deploy analytics) build on a fast site (and that field CWV — real-user data — is monitored post-launch, lab CWV here being the pre-launch proxy).

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| `.website-builder/audit/PERF-REPORT.md` | per-page table (score / LCP / CLS / INP / top opportunities / fixes applied) + raw Lighthouse output | The verification record — the exit criterion. Carried into phase 27 QA + post-launch monitoring (field-CWV baseline). |
| `.website-builder/audit/perf/` | raw Lighthouse JSON/HTML per page (mobile + desktop) | Auditable evidence behind the report. |
| Optimized assets + fixes in the project source | responsive image variants, modern formats, font-loading config, dynamic imports, explicit dimensions | The actual remediation — phase 22 fixes, not just reports. |
| `.website-builder/project.yaml` | `current_phase: 23` on a clean perf pass | Phase progression marker. |
| `.website-builder/decisions/skip-phase-22.md` *(only if skipped)* | decision-doc frontmatter + surfaced cost + user confirmation | Logged only on an authorized skip per `## Skip authorization`. |

`PERF-REPORT.md` + the applied optimizations are the required outputs.

## Common failure modes

**Unoptimized hero image.** The canonical phase-22 failure and usually the single biggest LCP killer — a 3MB PNG/JPEG hero shipped at full resolution to a phone. The agent generates responsive variants (srcset/sizes), converts to AVIF/WebP with a fallback, sets explicit dimensions (kills the CLS from the late image), and preloads the LCP image. This was foreshadowed at phase 8 (image strategy) and phase 17 (motion budget); phase 22 is where it's enforced on the built site.

**Audited the dev server.** The agent runs Lighthouse against `npm run dev` and gets a score of 50, panics, "fixes" things that aren't broken. Dev builds are unminified, unsplit, with HMR overhead — the number is meaningless. The agent always audits the production build.

**"Feels fast on my machine."** The developer (or user) tests on a fast wired desktop with a warm cache and concludes the site is fast. The agent runs the *mobile* Lighthouse profile with throttling — the realistic median visitor — because that is the run that predicts real bounce.

**CLS from un-dimensioned media or late fonts.** Images without width/height attributes (or aspect-ratio) push content down as they load; a web font swapping in late reflows text. The agent sets explicit dimensions on every image and a metrics-matched fallback + `font-display` strategy on the fonts so nothing jumps.

**Render-blocking font load.** The phase-17 display font is loaded synchronously, blocking first paint. The agent moves to `font-display: swap`/`optional`, `preconnect`/`preload`s the critical font, and matches the fallback metrics to minimize the swap shift.

**Heavy animation component blows LCP/INP.** An Aceternity hero with Three.js loads eagerly and tanks LCP and INP. Phase 17 budgeted this and phase 18 was supposed to dynamic-import it with a static fallback; phase 22 verifies and, if it slipped, enforces the dynamic import + reduced-motion + SSR static fallback.

**Score-gaming.** Stripping content or lazy-loading the LCP image to bump the number while making the actual experience worse. The agent optimizes the real experience (the CWV reflect it); it does not game the score at the expense of the visitor.

**Treating lab CWV as the final word.** Lighthouse gives lab CWV (one synthetic run); the true target is field CWV (75th percentile of real users). The agent surfaces that lab is the pre-launch proxy and that phase 30 / the post-launch monitoring template watches the field numbers — the lab gate here is necessary, not sufficient.

**Hidden assumption that performance is a polish step.** It is a conversion and reach step — slow sites lose visitors before they see anything, and CWV are a ranking signal. The agent surfaces the concrete cost when the user pushes to skip — see `## Skip authorization`.

## Reference materials

Foundation docs:

- `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` § 22 — the seed for this contract.
- `Workstreams/website-builder/foundation/DESIGN-architecture.md` § consumers (image-gen pipeline for responsive variants) / § Integration with Claude Code primitives / § context7 integration.
- `Workstreams/website-builder/foundation/DESIGN-project-scaffold.md` § `audit/` conventions; `media/IMAGE-PLAN.md` (the LCP-candidate inventory).
- `Workstreams/website-builder/cross-cutting/DESIGN-context7-integration.md` — phase 22 invokes context7 for stack perf primitives + Lighthouse scoring; `/GoogleChrome/lighthouse` cross-stack ID.
- `.website-builder/library/seo-checklists/` — Lighthouse-mapped performance + SEO checklists (the baseline phase 22 audits against; SEO overlaps at phase 26).

Core Web Vitals + Lighthouse (mandatory at this phase — current as of the freshness date):

- **WebFetch — web.dev Core Web Vitals (`https://web.dev/articles/vitals`), the canonical source.** Verified current thresholds: **LCP < 2.5s**, **INP < 200ms**, **CLS < 0.1**, each assessed at the **75th percentile** of page loads, segmented mobile/desktop. **INP has replaced FID** (INP became a stable Core Web Vital in 2024; FID retired). Lab CWV (Lighthouse) is the pre-launch proxy; field CWV (real users, 75th pct) is the true target monitored post-launch.
- **WebSearch "Lighthouse CI 2026"** — current practice: Lighthouse CI (`@lhci/cli`, LHCI 0.15.x, Lighthouse 12.x) runs Lighthouse in CI; `lighthouserc` assertions gate on category scores — `"categories:performance": ["error", { "minScore": 0.8 }]` (the 80+ gate) plus CWV assertions; assertion levels `warn` (stderr, non-blocking) vs `error` (non-zero exit, blocking). Audit the production build, mobile profile. Sources: [Performance monitoring with Lighthouse CI — web.dev](https://web.dev/articles/lighthouse-ci), [Lighthouse CI complete guide — Unlighthouse](https://unlighthouse.dev/learn-lighthouse/lighthouse-ci), [lighthouse-ci configuration — GitHub](https://github.com/GoogleChrome/lighthouse-ci/blob/main/docs/configuration.md).
- **context7 (at this phase):** the agent resolves + queries the chosen stack's current perf primitives at phase-22 entry — `/vercel/next.js` (`next/image`, `next/font`, `next/dynamic`), `/withastro/docs` (`<Image>`, asset processing, island hydration), `/GoogleChrome/lighthouse` (current scoring weights + CI config). Per `DESIGN-context7-integration.md` per-stack manifest at `reference-corpus/seeds/{stack}.yaml`.

Freshness date for this contract's references: **2026-05-18**.

## Skip authorization

**Phase 22 is the second of the two build-integration phases users most want to skip to "deploy faster." The individual score/CWV gates are NOT overridable. The entire phase may be skipped only under explicit, cost-surfaced, logged user authorization.**

**Why users push to skip:** *"it's fast enough on my machine, let's just launch — I'll optimize later."* "Later" rarely comes, and the visitors lost to slowness in the meantime are lost silently (they bounce; the user never sees them).

**The skip cost, surfaced concretely:**

- **Bounce.** Real-world data is consistent: load time and bounce rate are tightly coupled — a meaningful fraction of mobile visitors abandon a page that takes more than ~3s to become usable. A slow site loses the visitors phases 1-21 worked to earn, before they ever see the content.
- **Search + AI-crawler ranking.** Core Web Vitals are a ranking signal; a site failing CWV ranks lower and is surfaced less by AI answer engines. Skipping perf is also skipping reach.
- **The fix gets harder, not easier, after launch.** Optimizing a live site means re-touching images, fonts, and component loading on a system real users are now on — more constrained than doing it here.

**When the skip is legitimately allowed:**

1. **Explicit user authorization with the cost acknowledged.** The user, having heard the concrete cost, explicitly confirms. The agent logs `.website-builder/decisions/skip-phase-22.md` with the surfaced cost (verbatim), the user's confirmation, the date, and a flag that the launched site carries an un-audited-perf risk and that post-launch monitoring should watch field CWV closely. The agent refuses once, surfaces, respects the user's authority — but does not let it be silent.
2. **A prior verified audit is still valid.** Re-entering after a thin change that provably doesn't affect the critical path (a copy typo) — the agent confirms the prior `PERF-REPORT.md` still holds rather than re-running. Not a skip; a scoped re-validation.

**When the skip is NOT allowed even on request:**

- Silently. The cost must be surfaced and the override logged.
- Partially / score-shopping. "Ship at 62, it's close" is not a path — the gate is a threshold, not a negotiation; it is the whole phase under explicit authorization, or it is the optimizations.

The skip log uses the standard decision-doc frontmatter (`type: decision`, `phase: 22`, `made_at`, `alternatives_considered`, `chosen: skip`, `reasoning`) plus `surfaced_cost:` and the user's confirmation quote. The post-launch monitoring template reads this log; if present, it prioritizes field-CWV alerting from day one.
