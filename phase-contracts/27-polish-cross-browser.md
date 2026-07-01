---
phase: 27
name: Polish + cross-browser/cross-device QA
group: pre-launch
pipeline_section: pre-launch
skill: wb-prelaunch
prev_phase: 26
next_phase: 28
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - DESIGN-phase-contracts.md
  - DESIGN-architecture.md
---

# Phase 27 — Polish + cross-browser/cross-device QA

> The last look before the site goes live. A real walk-through on Chrome, Firefox, and Safari × iPhone, Android, and desktop — not "it works on my machine." Final visual polish, the Safari-specific bug list, and the verification that everything the pre-launch phases wired (integrations, consent banner, structured data) actually renders and works across the browser matrix. The phase where the agent refuses to deploy a site with a known visual bug, and refuses the desktop-Chrome-only definition of "tested."

## Mission

By phase 27 the site is built, integrated, legally sound, and metadata-complete. Phases 20 (responsive) and 21 (accessibility) already did dedicated mobile and a11y passes. Phase 27 is different: it is the **last cross-cutting look** before deployment — the dress rehearsal that catches what slips through single-browser development. The agent built and tested the site somewhere (usually Chromium); phase 27 verifies it on the matrix users actually arrive with: **Chrome, Firefox, Safari** across **iPhone, Android, desktop**. The defining failure this phase prevents is "it works on my machine" — the site that is flawless in dev-Chrome and broken in mobile Safari, which is a meaningful slice of real traffic.

This phase has two halves. **Polish** — the final visual sweep: a hairline-misaligned section, a hover state that does not exist on touch, a font that flashes (FOUT/FOIT), an image that is crisp on desktop and soft on retina mobile, a focus ring that is invisible on the brand background, a 1px scroll-jank on a sticky header. The small things that, uncorrected, make a careful site feel amateur. **Cross-browser/cross-device QA** — a Playwright walk-through of every page across the browser × device matrix, with a known **Safari-specific bug list** the agent runs deliberately (Safari is where cross-browser bugs concentrate for muggle-built sites). And — because phase 27 sits after the pre-launch phases — it re-verifies that what 24-26 wired actually holds across the matrix: the cookie consent banner is not a dark pattern on Safari mobile and still gates cookies there, the structured data renders server-side in every browser, the integrations fire on Safari (where ITP and stricter defaults break things that work on Chrome).

The gate is absolute: **the agent refuses to deploy with a known visual bug.** Not "we'll fix it post-launch" — a known bug found at phase 27 is fixed at phase 27 or explicitly accepted by the user with the cost surfaced and logged. This is first-principles QA work; there is no batch-specific design doc — cross-browser behavior is a runtime concern verified by actually running the site on the matrix.

## Entry conditions

- Phase 26 (SEO + structured data) complete. `audit/SEO-REPORT.md` exists — phase 27 re-verifies the structured data and metadata render correctly in the server HTML across browsers (a meta/JSON-LD block that renders in Chrome but is malformed in Safari's parse is a phase-27 catch).
- Phases 19-23 complete (composition, responsive, a11y, performance, forms) — phase 27 is not a substitute for the dedicated responsive (20) and a11y (21) passes; it is the integrated final look that catches what the focused passes plus single-browser development missed.
- Phase 24-25 complete — the integrations and consent mechanism exist; phase 27 verifies them on the *actual browser matrix* (the phase-24 parity check confirmed they work against production config; phase 27 confirms they work in Safari/Firefox/mobile, not just the dev browser).
- A runnable build of the site (local production build or a preview deploy) reachable by Playwright across the configured browser engines.

## What Claude must establish

A site verified working and polished across the real browser × device matrix, with every found defect either fixed or explicitly accepted-and-logged. The work product:

1. **Cross-browser/cross-device walk-through** — every page in `sitemap.yaml`, exercised via Playwright across **Chromium (Chrome/Edge), Firefox (Gecko), WebKit (Safari)** at the device profiles **mobile (~390px iPhone, ~360px Android), tablet (~768px), desktop (~1280px+)**. "Exercised" means: render correctly, navigate, interact (menus, forms, the cookie banner, any modal/accordion), no layout break, no console error that affects function.
2. **The Safari-specific bug pass** — a deliberate checklist the agent runs because these break specifically on WebKit for muggle-built sites: sticky/`position: sticky` quirks, `100vh` mobile-viewport overflow (Safari's dynamic toolbar), video autoplay/inline playback (`playsinline`, muted-autoplay rules), date input rendering, backdrop-filter support, smooth-scroll and scroll-snap differences, flexbox-gap on older WebKit, font-rendering weight differences, `:focus-visible` behavior, and ITP impact on the analytics/integrations wired at phase 24 (a tracker that fires on Chrome and is silently blocked on Safari).
3. **Final visual polish** — alignment, spacing rhythm, hover-vs-touch state parity, font-loading strategy (no jarring FOUT/FOIT — `font-display` set intentionally), image crispness across DPRs, focus-ring visibility on brand backgrounds, sticky-header scroll behavior, no horizontal scroll on mobile, motion respecting `prefers-reduced-motion`.
4. **Pre-launch-layer re-verification across the matrix** — the cookie banner shows and *still gates non-essential cookies on Safari* (phase 25's network-level proof, re-run on WebKit), the structured data is in the server HTML in every engine (phase 26), the integrations fire (or their Safari/ITP caveat is documented — phase 24's `INTEGRATIONS-REPORT.md` Safari notes verified true).
5. **`.website-builder/audit/QA-REPORT.md`** — the browser × device matrix as a grid (pass / fixed / accepted-with-link per cell), the Safari bug-pass checklist with each item's result, the polish items addressed, screenshots of any fixed defect (before/after) and any accepted defect (with the decision link), and the pre-launch-layer re-verification results.

The agent updates `.website-builder/project.yaml.current_phase` to `28` upon completion. Phase 28 (domain + DNS) begins the deployment group.

## Gating rules

The agent refuses to advance when:

- **A known visual bug exists, unfixed and unaccepted.** The defining gate. A defect the agent found in the walk-through is fixed, or the user explicitly accepts it with the cost surfaced and a decision logged (`.website-builder/decisions/qa-accepted-{slug}.md`). "Ship it and fix later" is not a default — it is an explicit, logged user choice. **Not overridable silently** — the gate is the explicit decision, not the agent quietly letting it through.
- **"Tested" means desktop-Chrome-only.** If the QA walk-through did not actually run on WebKit and Gecko at mobile + desktop profiles, the site is not tested. The agent refuses to mark phase 27 done on a single-engine pass — the matrix is the requirement, not a sample of it.
- **Safari-specific breakage.** A `100vh` overflow that makes mobile Safari unscrollable, a video that does not play inline on iPhone, a sticky header that jumps on WebKit — found by the Safari bug pass and not fixed. The agent has a Safari checklist precisely because these are predictable; finding one and shipping it anyway is the failure this phase exists to prevent.
- **A pre-launch-layer regression on the matrix.** The cookie banner gates cookies on Chrome but a Safari quirk lets the analytics cookie fire pre-consent (a phase-25 statutory failure surfacing only on Safari); or structured data is malformed in WebKit's parse (a phase-26 failure). The agent treats a cross-browser regression of a 24-26 deliverable as a hard gate — the earlier phase's compliance is only real if it holds on every engine.
- **Console errors that affect function.** A JS error that breaks the mobile menu on Firefox, a failed resource that blanks a section on Safari. Cosmetic console noise is noted; function-affecting errors block.

Override is available only on individual *cosmetic* polish items (a 1px imperfection the user judges not worth the time) via an explicit logged decision. Function-affecting bugs, Safari breakage that breaks usability, and pre-launch-layer regressions are not silently overridable.

## Tools and skills used

- **`Playwright` MCP** — the phase's primary and near-only tool. Playwright drives Chromium, Firefox, and WebKit; the agent runs the full page set across the three engines at the device profiles, captures screenshots per cell, exercises interactions (nav, forms, cookie banner, modals), inspects the network (re-verify consent gating on WebKit; confirm integrations fire or document the ITP caveat), and reads the console per browser.
- **`Edit` / `Write`** — to fix the defects found (CSS for layout/Safari quirks, `font-display` for FOUT, `playsinline` for video, focus-ring contrast, `100vh` → `100dvh`/`-webkit-fill-available` for the mobile-Safari viewport bug, `prefers-reduced-motion` guards). Fixes happen in this phase, not deferred.
- **`Read`** — `sitemap.yaml` (the page set to walk), `audit/SEO-REPORT.md` + `audit/INTEGRATIONS-REPORT.md` + `audit/LEGAL-REPORT.md` (the 24-26 deliverables to re-verify on the matrix), `audit/A11Y-REPORT.md` + `audit/PERF-REPORT.md` (phase 20-22 baselines — phase 27 should not regress them).
- **`AskUserQuestion`** — only when a found defect is a genuine judgment call ("this hairline gap is visible on Safari mobile only — fix it, or accept it as within tolerance?") so an accepted defect is the user's explicit, logged choice, not the agent's silent pass.
- **`Bash`** — to run/serve the production build locally for Playwright when there is no preview deploy yet (phase 28-29 do the real deploy; phase 27 tests the production build pre-deploy).

No subagent spawn — the cross-browser walk is the agent's own hands-on verification; delegating it would lose the observed-not-assumed property the gate depends on. `wb-prelaunch` phase-group skill carries phases 24-27; phase 27 is the skill's closing verification before the deployment group.

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| `.website-builder/audit/QA-REPORT.md` | Browser × device pass/fixed/accepted grid; the Safari bug-pass checklist with per-item results; polish items addressed; before/after screenshots of fixes; accepted-defect decision links; pre-launch-layer (consent/structured-data/integration) re-verification per engine | The audit trail proving the site was verified on the real matrix, not one browser; read by phase 29 (deploy gate — no known bug ships) and the post-launch maintainer |
| Defect fixes in the project | Per stack convention | The actual CSS/markup/JS fixes — applied here, not deferred |
| `.website-builder/decisions/qa-accepted-{slug}.md` *(when applicable)* | Standard decision-doc frontmatter + body | Created only when the user explicitly accepted a known cosmetic defect with the cost surfaced |

The `QA-REPORT.md` with the populated matrix grid + Safari checklist is the required artifact.

## Common failure modes

**"It works on my machine."** Dev-Chrome flawless; mobile Safari broken. The canonical failure and the entire reason phase 27 exists. The agent's matrix is not a recommendation — a single-engine pass is not a pass; the site is tested when Chromium *and* Firefox *and* WebKit at mobile *and* desktop have been walked.

**`100vh` makes mobile Safari unscrollable.** The classic WebKit viewport bug — `height: 100vh` on a hero overflows under Safari's dynamic toolbar and the page cannot scroll past it on iPhone. It is on the agent's Safari checklist precisely because it is predictable; the fix (`100dvh` / `-webkit-fill-available`) is applied here, not discovered by a frustrated user post-launch.

**Video does not autoplay/play inline on iPhone.** A hero video that plays on desktop is a black box on mobile Safari without `playsinline` + `muted`. On the Safari checklist; fixed in-phase.

**Hover-only interaction with no touch path.** A dropdown that opens on `:hover` is unreachable on a touch device. The agent's matrix walk on mobile profiles catches the no-touch-equivalent and the fix (tap/focus path) is applied.

**The cookie banner gates cookies on Chrome but not Safari.** A consent-script quirk lets the analytics cookie fire pre-consent specifically on WebKit — a phase-25 *statutory* failure that only surfaces on the engine the dev browser was not. The agent re-runs phase-25's network-level proof on WebKit; a compliance deliverable is only real if it holds on every engine.

**Integrations silently dead on Safari (ITP).** GA4 fires on Chrome and is blocked by Safari's Intelligent Tracking Prevention; the user thinks analytics works and is missing a chunk of traffic. The agent verifies the phase-24 `INTEGRATIONS-REPORT.md` Safari caveats are *true* (the integration either works on Safari or its documented ITP limitation is real and the user knows) rather than assuming the Chrome result generalizes.

**Font flash makes a polished site feel cheap.** No `font-display` strategy → a jarring FOIT/FOUT on first paint. A small thing that disproportionately undermines the careful design. Caught in the polish sweep, fixed with an intentional `font-display`.

**A bug is found and deferred without anyone deciding to defer it.** The agent notices a Safari layout break, mentally files it as "minor", and ships. The gate is explicit: a known defect is fixed or *explicitly accepted by the user with the cost surfaced and logged* — the agent does not unilaterally decide a bug is acceptable.

**Phase 27 used as a substitute for the dedicated a11y/responsive passes.** Phase 27 is the integrated final look, not a replacement for phase 20 (responsive) and phase 21 (a11y). If those passes were skipped, the agent surfaces that phase 27 catches *some* of what they would have but is not a substitute — it does not let phase 27 retroactively cover a skipped dedicated pass.

## Reference materials

- **Design doc — phase pipeline source:** `DESIGN-phase-contracts.md` § 27 (seed) — explicit Safari-specific-bug-list callout
- **Design doc — pipeline integration:** `DESIGN-architecture.md` § Phase contracts
- **Phase 20 / 21 / 22 (the dedicated passes phase 27 integrates, does not replace):** `DESIGN-phase-contracts.md` §§ 20-22 — responsive snapshots, a11y audit, performance budget; phase 27 must not regress these
- **Phase 24 / 25 / 26 (the pre-launch deliverables phase 27 re-verifies on the matrix):** `phase-contracts/24-integrations.md` (Safari/ITP caveats), `phase-contracts/25-legal-pages.md` (consent network-level proof re-run on WebKit), `phase-contracts/26-seo-structured-data.md` (server-rendered metadata/JSON-LD per engine)
- **Phase 16 voice baseline (polish includes voice-consistent microcopy in error/empty states surfaced during the walk):** `phase-contracts/16-copywriting.md`

No batch-specific external research is mandated for this phase (per the INST — phases 27/31/32/33 are first-principles authoring; cross-browser behavior is a runtime concern verified by running the site, not by fetched docs). Browser-engine bug behavior is confirmed by Playwright execution against the live build, not by training-data assumptions. Freshness date for this contract: **2026-05-18**.
