---
phase: 21
name: Accessibility audit
group: build-integration
pipeline_section: build-integration
skill: wb-build-integration
prev_phase: 20
next_phase: 22
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - DESIGN-phase-contracts.md
  - DESIGN-architecture.md
  - DESIGN-project-scaffold.md
  - DESIGN-context7-integration.md
library_clones_at_entry:
  - resource: component-patterns
    as: component-patterns
    note: "canonical accessible patterns for the common component types (the a11y baseline the audit checks against)"
---

# Phase 21 — Accessibility audit

> WCAG 2.1 AA basics, verified: color contrast, alt text, keyboard navigation, screen-reader sniff test, semantic HTML, focus states, form labels. The phase that makes the site usable by people who don't use it the way the builder does. The agent refuses to advance with red flags — no alt text, contrast failures, missing form labels. Automated audit (axe-core / Lighthouse a11y) plus a manual keyboard walk; both must pass.

## Mission

Phase 20 made the site work at every screen size. Phase 21 makes it work for people who navigate by keyboard, by screen reader, with low vision, or with color-vision differences — the audience the sighted-mouse-using builder never tests because they are not it.

The work product is `.website-builder/audit/A11Y-REPORT.md`: an automated audit (axe-core or Lighthouse accessibility category) that passes, plus a manual keyboard-navigation walk that passes, plus confirmation that alt text exists on every meaningful image. After phase 21, the site clears WCAG 2.1 Level AA basics and the report documents that it does.

The discipline of this phase is **the audit is verified, not asserted, and red flags block**. Accessibility is the quality dimension muggles most reliably skip because they cannot see the problem — the site works perfectly for them, so it must be fine. It is not fine for the screen-reader user who hits an unlabeled form field, the keyboard user who cannot reach the menu, or the low-vision user who cannot read 3:1 grey-on-white body text. Phase 17 already locked a contrast-safe palette by construction and phase 18 already wired a11y obligations into the components — phase 21 is where that is *verified end-to-end on the assembled, responsive site*, and where anything that slipped through is caught and fixed before it ships.

## Entry conditions

- Phase 20 (responsive / mobile pass) complete. Every page has an intentional, snapshot-verified layout at 360/768/1280. Phase 21 audits the responsive site (some a11y issues are breakpoint-specific — a contrast or touch-target problem that only appears on mobile).
- Phase 17 (design system) complete with a contrast-locked palette. The phase-17 tokens were already tuned to clear WCAG 2.2 contrast minimums by construction; phase 21 verifies that held through composition and didn't regress (a low-contrast one-off introduced at phase 19/20).
- Phase 18 (component build) complete with a11y wired per spec. Each `components.yaml` entry declared its a11y obligations (heading hierarchy, alt-text props, keyboard order, ARIA where the primitive didn't supply it); phase 21 verifies those obligations are met in the assembled pages, not just specced.
- Phase 16 (copywriting) complete. Alt text for meaningful images is content (it carries the image's equivalent purpose, in the brand voice); it was authored at phase 16 against the phase-8 image plan. Phase 21 verifies it exists and is meaningful (not "image1.jpg"), and that decorative images carry empty `alt=""`.

## What Claude must establish

A WCAG 2.1 Level AA basics pass, verified two ways (automated + manual), covering at minimum:

1. **Color contrast** (WCAG 1.4.3 Contrast Minimum, AA; 1.4.11 Non-text Contrast, AA). Text ≥ 4.5:1 against its background (≥ 3:1 for large text); UI components + meaningful graphics ≥ 3:1 against adjacent colors. Verified on the rendered site at light and dark mode (if phase-17 strategy is auto/opt-in).
2. **Text alternatives** (WCAG 1.1.1 Non-text Content, A). Every meaningful image has descriptive alt text serving its equivalent purpose; every decorative image has empty `alt=""` so screen readers skip it; functional images (icon buttons) have an accessible name.
3. **Keyboard operability** (WCAG 2.1.1 Keyboard, A; 2.1.2 No Keyboard Trap, A). Every interactive element is reachable and operable by keyboard alone, in a logical order; focus is never trapped (modals/drawers return focus correctly and can be closed by keyboard).
4. **Focus visible** (WCAG 2.4.7 Focus Visible, AA). A visible focus indicator on every keyboard-operable element (the phase-17 `ring` token is the system's focus treatment; phase 21 verifies it actually shows and clears 3:1).
5. **Semantic HTML / structure** (WCAG 1.3.1 Info and Relationships, A). One `h1` per page, logical heading nesting (no skipped levels), landmarks (`header`/`nav`/`main`/`footer`), lists as lists, the structure programmatically determinable — not divs faking headings.
6. **Form labels** (WCAG 3.3.2 Labels or Instructions, A; 4.1.2 Name Role Value, A). Every form input has a programmatic label (not placeholder-as-label); inputs expose name/role/value to assistive tech.
7. **Consistent navigation** (WCAG 3.2.3 Consistent Navigation, AA). The shared nav (phase-10 IA, phase-18 component) appears in consistent order/presentation on every page — verified, since phase 19/20 are where per-page drift could have crept in.
8. **Screen-reader sniff test.** A pass through the page's accessibility tree (the structure a screen reader announces) confirming headings, landmarks, link text (no bare "click here"), and image alts read sensibly.

Verification is **two independent passes, both required**:

- **Automated** — axe-core (via the Playwright integration, `@axe-core/playwright`'s builder pattern: configure with `withTags`, `analyze()` the page in its tested state — including states behind UI interaction, so the agent opens the modal/drawer and re-`analyze()`s) **or** Lighthouse accessibility category. The automated audit must pass (no violations of the criteria above; Lighthouse a11y score is reported and the underlying axe-core checks must be clean — a high score with a hidden violation is not a pass).
- **Manual keyboard walk** — the agent tab-walks each page via Playwright: every interactive element reached in logical order, focus visible at each stop, modals/menus operable and escapable, no trap. Automated tools catch ~30-50% of issues; the manual walk catches the rest (keyboard order, focus management, "does the tab sequence make sense").

Output: `.website-builder/audit/A11Y-REPORT.md`. `.website-builder/project.yaml.current_phase` updates to `22` only when both passes are clean (or a documented, user-confirmed skip per `## Skip authorization`). Phase 22 (performance audit) loads next.

## Gating rules

The agent refuses to advance with any of these **red flags**:

- **A meaningful image with no alt text** (or junk alt like the filename). WCAG 1.1.1 fail. Non-overridable — the agent authors meaningful alt (from the phase-8 image plan + phase-16 voice) before advance.
- **A contrast failure** on text or a UI component against the phase-17 tokens. WCAG 1.4.3/1.4.11 fail. The agent traces it to the token or the composition and fixes it (re-tune the OKLCH lightness — predictable because phase 17 worked luminance-first).
- **A form input with no programmatic label.** WCAG 3.3.2/4.1.2 fail. Placeholder-as-label does not count. Non-overridable.
- **A keyboard trap or an unreachable interactive element.** WCAG 2.1.1/2.1.2 fail. The site must be fully keyboard-operable.
- **No visible focus indicator.** WCAG 2.4.7 fail. The phase-17 focus token must actually render and clear 3:1.
- **The automated audit was not run, or was run but not actually clean.** "Lighthouse said 95" with an unaddressed axe violation underneath is not a pass — the score is reported but the criteria must be clean.
- **The manual keyboard walk was skipped.** Automated-only is not a phase-21 pass; ~half the issues are only catchable by the manual walk.

These red-flag gates are **not individually overridable** — they are correctness failures, not preferences. The *entire phase* can be skipped only under the explicit, cost-surfaced, logged authorization in `## Skip authorization` below; partial "ship with this one contrast failure" is not a path.

## Tools and skills used

- **`Bash`** — to run the automated audit: axe-core CLI / the `@axe-core/playwright` runner, or Lighthouse CLI (`lighthouse <url> --only-categories=accessibility`) / Lighthouse CI (`lhci` with an accessibility assertion). The agent runs against the live dev/preview server.
- **Playwright MCP** — for the manual keyboard walk (tab through each page, observe focus, operate modals/menus by keyboard) and for axe-core's Playwright integration (the agent navigates + interacts to reveal state-dependent UI, then runs the axe builder's `analyze()` on that state — per current `@axe-core/playwright` practice; Playwright's `ariaSnapshot()` captures the accessibility tree as structured YAML for the screen-reader sniff test).
- **`mcp__context7__resolve-library-id` + `mcp__context7__query-docs`** — per `DESIGN-context7-integration.md`, phase 21 invokes context7 for the current a11y tooling invocation (`/dequelabs/axe-core` for the current CLI/Playwright API, `/GoogleChrome/lighthouse` for the current a11y category + scoring) and for the chosen component library's a11y patterns (e.g. Radix focus-management specifics). a11y tooling APIs change; the agent verifies current invocation rather than trusting training data.
- **`Edit` / `Write`** — to fix the issues the audit surfaces (add alt text, add a label, fix a heading level, adjust a token's OKLCH lightness for contrast, add an ARIA attribute the primitive didn't supply, fix a focus order) and to write `audit/A11Y-REPORT.md`.
- **`Read`** — `components.yaml` (the per-component a11y obligations declared at phase 18 — the contract phase 21 verifies), `brand.yaml.tokens` (the contrast-locked palette), `media/IMAGE-PLAN.md` + `content/pages/{slug}.md` (image purpose → meaningful vs decorative alt-text decisions).

The `wb-build-integration` phase-group skill remains loaded (single skill for phases 19-23, Decision 64). It carries the cross-phase contract that phase 21 verifies the a11y obligations phase 18 specced, and that phase 22 (perf) and phase 27 (cross-browser QA) build on the audited, accessible site.

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| `.website-builder/audit/A11Y-REPORT.md` | per-criterion table (criterion / level / automated result / manual result / fixes applied) + the raw axe-core / Lighthouse output | The verification record — the exit criterion. Carried into phase 27 QA and the post-launch maintenance template. |
| `.website-builder/audit/a11y/` | raw tool output (axe JSON, Lighthouse a11y JSON, accessibility-tree YAML snapshots) | Auditable evidence behind the report. |
| Fixes in the project source | alt text, labels, ARIA, heading fixes, token contrast adjustments, focus-order fixes | The actual remediation — phase 21 fixes, not just reports. |
| `.website-builder/project.yaml` | `current_phase: 22` on clean dual pass | Phase progression marker. |
| `.website-builder/decisions/skip-phase-21.md` *(only if skipped)* | decision-doc frontmatter + surfaced cost + user confirmation | Logged only on an authorized skip per `## Skip authorization`. |

`A11Y-REPORT.md` + the applied fixes are the required outputs.

## Common failure modes

**Decorative images getting descriptive alt text (and vice versa).** The canonical phase-21 failure. A purely decorative background flourish gets `alt="decorative swirl graphic"` (a screen reader now announces noise); a meaningful product photo gets `alt=""` (the screen-reader user loses real information). The agent enforces the rule: decorative → empty `alt=""` (skipped by AT); meaningful → descriptive alt serving the equivalent purpose, written in the phase-16 brand voice from the phase-8 image-plan intent.

**Placeholder used as a label.** A form input with only a `placeholder="Email"` and no `<label>`. Placeholders vanish on input and aren't reliably announced — this is a 3.3.2/4.1.2 fail. The agent wires a programmatic label (visible, or visually-hidden when the design truly requires it, but present and associated).

**Lighthouse-score-as-pass.** "Lighthouse a11y says 96, ship it." Lighthouse's a11y category is a useful signal but the score can be high while a real violation persists (and it does not catch keyboard-order issues at all). The agent treats the underlying axe-core checks + the manual keyboard walk as the gate, the score as a secondary signal.

**Automated-only audit.** The agent runs axe-core, it's green, the agent advances. Automated tools catch only a portion of issues — keyboard order, focus management, "is the tab sequence sensible," whether alt text is *meaningful* (axe can't judge that) all require the manual walk. The agent does both passes.

**Animation-library a11y gap.** An Aceternity/Magic-UI motion component doesn't respect `prefers-reduced-motion`, or a custom interactive widget has no keyboard support. Phase 17 pre-budgeted reduced-motion and phase 18 was supposed to wire it; phase 21 verifies it on the assembled site and fixes any gap (the agent adds the reduced-motion gate / keyboard handler).

**Contrast regression after phase 17.** Phase 17 locked a contrast-safe palette, but a one-off color was introduced at composition (a muted caption on a tinted surface) that fails 4.5:1. The agent traces it, and because phase 17 worked luminance-first in OKLCH, the fix is a predictable lightness adjustment, not a guess.

**Heading hierarchy faked with styled divs.** The visual hierarchy looks right but it's `<div class="text-3xl">` instead of `<h1>`/`<h2>` — a screen reader gets no document outline. The agent enforces real semantic headings (one h1/page, no skipped levels) + landmarks.

**"It works fine for me."** The user (or the agent) tests with a mouse and good vision and concludes the site is accessible. The agent surfaces that the entire point of the audit is the users who *don't* use it that way, and runs the real verification regardless of how it "feels."

**Hidden assumption that a11y is a nice-to-have.** It is a correctness dimension (and in many jurisdictions a legal requirement). The agent surfaces the real cost of skipping — see `## Skip authorization`.

## Reference materials

Foundation docs:

- `DESIGN-phase-contracts.md` § 21 — the seed for this contract.
- `DESIGN-architecture.md` § Integration with Claude Code primitives (Playwright + Bash audit tooling) / § context7 integration.
- `DESIGN-project-scaffold.md` § `audit/` conventions; `components.yaml` a11y-obligation fields.
- `DESIGN-context7-integration.md` — phase 21 invokes context7 for axe-core + Lighthouse current invocation + library a11y patterns; cross-stack a11y library IDs (`/dequelabs/axe-core`, `/GoogleChrome/lighthouse`).
- `${CLAUDE_PLUGIN_ROOT}/reference-corpus/component-patterns/` — canonical accessible patterns for the common component types (the a11y baseline the audit checks against).

WCAG + tooling (mandatory at this phase — current as of the freshness date):

- **WebFetch — W3C WCAG 2.1 (`https://www.w3.org/TR/WCAG21/`), the canonical source.** The Level-AA-relevant criteria verified in this phase: **1.4.3 Contrast (Minimum)** AA — text ≥ 4.5:1 (large text exception); **1.4.11 Non-text Contrast** AA — UI components/graphics ≥ 3:1; **1.1.1 Non-text Content** A — text alternatives serving equivalent purpose; **2.1.1 Keyboard** A + **2.1.2 No Keyboard Trap** A — full keyboard operability, no trap; **2.4.7 Focus Visible** AA — visible focus indicator; **1.3.1 Info and Relationships** A — programmatically determinable structure; **3.3.2 Labels or Instructions** A + **4.1.2 Name, Role, Value** A — labeled, AT-exposed inputs; **3.2.3 Consistent Navigation** AA — consistent repeated nav.
- **WebSearch "axe-core CLI / @axe-core/playwright 2026"** — current practice: `@axe-core/playwright` is Deque's official Playwright integration; the builder pattern (`new AxeBuilder({ page }).withTags([...]).analyze()`); `include()`/`exclude()` to scope; **interact-then-analyze** for state-dependent UI (open the modal/drawer with Locators + `waitFor`, then `analyze()` — otherwise axe doesn't see those elements); Playwright `locator.ariaSnapshot()` (v1.49+) captures the accessibility tree as structured YAML for the screen-reader sniff test; works across Chromium/Firefox/WebKit. Sources: [Accessibility testing — Playwright docs](https://playwright.dev/docs/accessibility-testing), [axe-playwright — npm](https://www.npmjs.com/package/axe-playwright), [Accessibility audits with Playwright, Axe, GitHub Actions — DEV](https://dev.to/jacobandrewsky/accessibility-audits-with-playwright-axe-and-github-actions-2504).
- **WebSearch "Lighthouse a11y category 2026"** — current practice: Lighthouse's accessibility category is a 0-100 aggregate scored from axe-core checks under the hood; Lighthouse CI (`@lhci/cli`, LHCI 0.15.x / Lighthouse 12.x) supports a `categories:accessibility` assertion (`["error", { "minScore": 1 }]`) for a CI gate; the score is a signal, the underlying checks + manual walk are the gate. Sources: [Lighthouse accessibility scoring — Chrome for Developers](https://developer.chrome.com/docs/lighthouse/accessibility/scoring), [Lighthouse CI guide — Unlighthouse](https://unlighthouse.dev/learn-lighthouse/lighthouse-ci), [lighthouse-ci configuration — GitHub](https://github.com/GoogleChrome/lighthouse-ci/blob/main/docs/configuration.md).

Freshness date for this contract's references: **2026-05-18**.

## Skip authorization

**Phase 21 is one of the phases the VISION anti-skip lock treats as load-bearing. The individual red-flag gates are NOT overridable. The entire phase may be skipped only under explicit, cost-surfaced, logged user authorization — and the agent surfaces the cost in concrete, not abstract, terms.**

**Why users push to skip:** the most common is *"the site works fine, let's just deploy — I'll do accessibility later."* "Later" almost never comes, and retrofitting a11y onto a launched site is more expensive than building it in (every component touched again, contrast re-tuned, content re-alt-texted).

**The skip cost, surfaced concretely:**

- The site becomes unusable for screen-reader users (no alt text → images are silent; no labels → forms cannot be completed), keyboard-only users (unreachable nav/CTAs), and low-vision users (sub-4.5:1 text is literally unreadable for them). That is not an edge — it is a meaningful fraction of any real audience.
- **Legal exposure.** In many of the jurisdictions this plugin's users operate in (EU — the European Accessibility Act; US — ADA Title III + Section 508; UK — Equality Act), an inaccessible commercial site is a compliance and litigation risk. The agent surfaces this explicitly, not as a scare tactic but as a fact the user should weigh before skipping.
- **SEO + reach cost.** Semantic structure and a11y overlap heavily with what search engines and AI crawlers parse; an inaccessible site is also a less-discoverable one.

**When the skip is legitimately allowed:**

1. **Explicit user authorization with the cost acknowledged.** The user, having heard the concrete cost above, explicitly confirms. The agent logs `.website-builder/decisions/skip-phase-21.md` with: the surfaced cost (verbatim), the user's confirmation, the date, and a flag that phases 22+ and the launched site carry an un-audited-a11y risk. The agent refuses once, surfaces, and respects the user's authority over their own project — but it does not let the skip be silent.
2. **A prior verified audit is still valid.** Re-entering after a thin change that provably doesn't touch a11y surface (a copy typo fix) — the agent confirms the prior `A11Y-REPORT.md` still holds rather than re-running fully. Not a skip; a scoped re-validation.

**When the skip is NOT allowed even on request:**

- Silently. The cost must be surfaced and the override logged.
- Partially. "Ship with just this one contrast failure / this one unlabeled form" is not a path — the gates are individually non-overridable; it is the whole phase under explicit authorization, or it is the fixes. (The reason: a half-audited site gives false confidence; an explicitly-skipped one at least flags the risk honestly.)

The skip log uses the standard decision-doc frontmatter (`type: decision`, `phase: 21`, `made_at`, `alternatives_considered`, `chosen: skip`, `reasoning`) plus `surfaced_cost:` and the user's confirmation quote. Phase 22+ and the post-launch maintenance template read this log; if present, the maintenance template re-surfaces the un-audited-a11y risk at its first review cadence.
