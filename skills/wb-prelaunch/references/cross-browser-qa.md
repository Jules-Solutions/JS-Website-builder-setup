# Reference — Polish + cross-browser/cross-device QA (phase 27)

> Loaded for phase 27. The contract is `phase-contracts/27-polish-cross-browser.md`. **No external research is mandated for this phase** — cross-browser behavior is a runtime concern verified by *actually running the site* on the matrix via Playwright, not by fetched docs. Browser-engine bug behavior is confirmed by Playwright execution against the live build, never by training-data assumptions. Freshness baseline for this file: 2026-05-18.

## The absolute gate

**The agent refuses to deploy with a known visual bug.** A defect found in the walk-through is fixed *here* (phase 27, not deferred) — or **explicitly accepted by the user with the cost surfaced and a decision logged** at `.website-builder/decisions/qa-accepted-{slug}.md`. "Ship it and fix later" is not a default; it is an explicit, logged user choice. The agent does not unilaterally decide a bug is acceptable. Function-affecting bugs, Safari breakage that breaks usability, and pre-launch-layer regressions are **not silently overridable**; only individual *cosmetic* polish items are user-overridable with a logged decision.

"Tested" means the **matrix**, not desktop-Chrome-only. A single-engine pass is refused.

## The browser × device matrix

Walk every page in `.website-builder/sitemap.yaml` via Playwright across all cells:

| Engine | Mobile (~390px iPhone / ~360px Android) | Tablet (~768px) | Desktop (~1280px+) |
|---|---|---|---|
| **Chromium** (Chrome / Edge) | ☐ | ☐ | ☐ |
| **Firefox** (Gecko) | ☐ | ☐ | ☐ |
| **WebKit** (Safari) | ☐ | ☐ | ☐ |

"Exercised" per cell = renders correctly, navigates, interactions work (menus, forms, the cookie banner, any modal/accordion), no layout break, no console error that affects function. Record each cell as **pass / fixed / accepted-with-link** in the QA report grid.

## The Safari-specific bug checklist (run deliberately — these are predictable)

Safari/WebKit is where cross-browser bugs concentrate for muggle-built sites. Run each item; record the result:

| Bug class | Symptom | Fix |
|---|---|---|
| `100vh` mobile-viewport overflow | A `height: 100vh` hero overflows under Safari's dynamic toolbar; the page can't scroll past it on iPhone | `100dvh` / `-webkit-fill-available` |
| `position: sticky` quirks | Sticky header jumps / detaches on WebKit scroll | check parent `overflow`/`height`; sticky-context fix |
| Video autoplay/inline | Hero video is a black box on mobile Safari | `playsinline` + `muted` (+ `autoplay`) attributes |
| `backdrop-filter` support | Glass/blur effect missing or wrong on WebKit | `-webkit-backdrop-filter` prefix; graceful fallback |
| Smooth-scroll / scroll-snap | Janky or absent on Safari | feature-detect; reduce reliance or polyfill |
| Flexbox `gap` on older WebKit | Gaps collapse on older Safari | margin fallback where the audience includes old WebKit |
| Date input rendering | `<input type=date>` looks/behaves differently | custom date control or accept the native variance, logged |
| Font-rendering weight | Weights render heavier/lighter on WebKit | `-webkit-font-smoothing`; intentional weight choice |
| `:focus-visible` behavior | Focus ring missing/inconsistent on Safari | explicit `:focus-visible` styles; verify on brand bg |
| ITP impact on integrations | An analytics/tracker fires on Chrome, silently blocked by Safari Intelligent Tracking Prevention | verify the phase-24 `INTEGRATIONS-REPORT.md` Safari/ITP caveat is *true* — the integration works on Safari or its documented ITP limitation is real and the user knows |
| Hover-only interaction | A `:hover` dropdown is unreachable on touch | add a tap/focus path |

## Final visual polish sweep

- Alignment + spacing rhythm (no hairline-misaligned sections).
- Hover-vs-touch state parity.
- Font-loading: `font-display` set intentionally (no jarring FOUT/FOIT on first paint — a small thing that disproportionately undermines a careful design).
- Image crispness across DPRs (crisp desktop, soft retina-mobile → fix `srcset`/sizing).
- Focus-ring visibility on brand backgrounds.
- Sticky-header scroll behavior (no 1px jank).
- No horizontal scroll on mobile.
- Motion respects `prefers-reduced-motion`.

## Pre-launch-layer re-verification (the 24-26 deliverables must hold on every engine)

Phase 27 sits after the pre-launch phases, so it re-verifies their compliance on the *actual matrix*:

- **Phase 25 cookie consent** — re-run the network-level proof **on WebKit**: the non-essential cookie does **not** set before consent on Safari, and the banner is not a dark pattern on Safari mobile (Accept/Reject equally prominent, same layer). A consent-script quirk that lets the cookie fire pre-consent only on Safari is a phase-25 *statutory* failure surfacing on the engine the dev browser wasn't — a hard gate.
- **Phase 26 structured data** — the metadata + JSON-LD is in the server HTML and parses correctly in *every* engine (a block that renders in Chrome but is malformed in Safari's parse is a phase-27 catch).
- **Phase 24 integrations** — fire on Safari, or their documented ITP caveat is verified true (not assumed from the Chrome result).

A cross-browser regression of any 24-26 deliverable is a **hard gate** — the earlier phase's compliance is only real if it holds on every engine.

## Deploy-target context (why phase 27 tests the production build)

Phase 27 tests a *production build* (local production build or a preview deploy) before phases 28-29 do the real deploy — the cross-browser walk must run against the build that will actually ship, not a dev server. The deploy target was chosen at phase 11 and is actualized at phase 29; phase 27's parity discipline (integrations/consent/structured-data verified on the production-bound build) is the same parity principle phase 24 established. Deploy-provider specifics (Vercel-default-for-Next.js, Cloudflare-Pages-for-static, Netlify cross-stack — decision 50) and how some hosting features load-bear integrations: `Workstreams/website-builder/cross-cutting/DESIGN-deploy-providers.md` § Phase contracts that invoke this concern. Phase 27 does not deploy — it verifies the build phase 28-29 will deploy is matrix-clean first.

## Not a substitute for the dedicated passes

Phase 27 is the integrated final look, **not** a replacement for phase 20 (responsive) or phase 21 (a11y). If those dedicated passes were skipped, surface that phase 27 catches *some* of what they would have but is not a substitute — do not let phase 27 retroactively cover a skipped dedicated pass. Phase 27 must also not regress the phase-20/21/22 baselines (`A11Y-REPORT.md`, `PERF-REPORT.md`).

## Output

`.website-builder/audit/QA-REPORT.md` — the browser × device grid (pass/fixed/accepted-with-link per cell), the Safari bug-pass checklist with each item's result, polish items addressed, before/after screenshots of fixes, accepted-defect decision links, and the pre-launch-layer (consent / structured-data / integration) re-verification per engine. The required artifact. Read by phase 29 (deploy gate — no known bug ships) and the post-launch maintainer. Defect fixes are applied in the project here, per stack convention — not deferred.

## Tools

`Playwright` MCP is the phase's primary and near-only tool (drives Chromium + Firefox + WebKit, device profiles, screenshots, interactions, network inspection, console). `Edit`/`Write` for the fixes. `Bash` to serve the production build locally for Playwright when there is no preview deploy yet. `AskUserQuestion` only when a found defect is a genuine judgment call (so an accepted defect is the user's explicit logged choice, not a silent pass). No subagent spawn — the cross-browser walk is the agent's own hands-on verification; delegating it would lose the observed-not-assumed property the gate depends on.
