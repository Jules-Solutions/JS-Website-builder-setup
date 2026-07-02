---
name: wb-build-integration
description: This skill should be used when the website-builder agent reaches the build-integration pipeline phases (19-23) — when the user says "compose the pages", "put it all together", "assemble the site", "make it work on mobile", "do a responsive pass", "check it on a phone", "run an accessibility audit", "make it WCAG compliant", "is it accessible", "check the performance", "run Lighthouse", "make it faster", "wire up the contact form", "make the forms work", "hook up the newsletter signup", or otherwise asks to turn built components into a real, fast, accessible, working site. It drives composition, the responsive/mobile pass, the WCAG 2.1 AA accessibility audit, the Lighthouse performance audit, and end-to-end form/interactive wiring. Loads at phase 19 and stays loaded through phase 23.
version: 0.1.0
---

# wb-build-integration — Composition → Responsive → A11y → Perf → Forms

> The single skill for the build-integration phase group (phases 19-23, per locked Decision 64). It assembles the components and content produced by earlier phases into a real site that is intentionally responsive, accessible, fast, and functionally working — verified, not asserted, at every step.
>
> Source of truth: the five phase contracts at `phase-contracts/19-composition.md`, `phase-contracts/20-responsive-mobile.md`, `phase-contracts/21-accessibility-audit.md`, `phase-contracts/22-performance-audit.md`, `phase-contracts/23-forms-interactive.md`. This skill is the procedural overlay; the contracts are authoritative on mission, entry/exit, gating, and outputs. Read the relevant contract verbatim at each phase entry.

## Purpose

Phases 1-18 designed and built every part of the site. This skill governs the five phases that assemble those parts and prove the result works for real visitors:

- **Phase 19 — Composition.** Assemble every `sitemap.yaml` page from phase-18 components, wiring phase-16 content, in the user's chosen stack. The site starts existing.
- **Phase 20 — Responsive pass.** Make mobile a *decision*, not a side-effect. Playwright snapshots at 360 / 768 / 1280 per page.
- **Phase 21 — Accessibility audit.** WCAG 2.1 AA basics verified two independent ways: automated (axe-core / Lighthouse) + manual keyboard walk.
- **Phase 22 — Performance audit.** Lighthouse ≥ 80 (mobile, production build), Core Web Vitals green (LCP < 2.5s, CLS < 0.1, INP < 200ms).
- **Phase 23 — Forms + interactive.** Every form actually works end-to-end; secrets handled by construction; spam-protected.

The cross-phase contract: phases 20-23 each verify the *exact assembled pages* phase 19 produced. The skill stays loaded across all five so the chain holds.

## The one discipline that spans all five phases

**Verified, not asserted. Red flags block.** Every one of these phases has a verification artifact that *is* the exit criterion — not the agent's claim that it did the work:

| Phase | Verification artifact (the exit criterion) |
|---|---|
| 19 | A clean production build + a Playwright sanity-walk of every page |
| 20 | `.website-builder/audit/responsive/{slug}-{360,768,1280}.png` for every page |
| 21 | `.website-builder/audit/A11Y-REPORT.md` (automated pass + manual keyboard walk) |
| 22 | `.website-builder/audit/PERF-REPORT.md` (Lighthouse ≥ 80, CWV green, production build) |
| 23 | `.website-builder/audit/FORMS-REPORT.md` (every form's *effect* confirmed) |

"It looks responsive" / "Lighthouse felt fast" / "the form submitted without an error" are **not** passes. The artifact is. Producing the artifact is non-optional and is what the agent's parent / the next phase reads.

## How to use this skill at each phase

At the entry of each phase, read that phase's contract verbatim (`phase-contracts/NN-*.md`) — it is authoritative. Then apply the procedure below.

### Phase 19 — Composition (`phase-contracts/19-composition.md`)

Assembly, deliberately low-gating: the discipline already happened upstream (phases 14, 16, 17, 18). Do not re-litigate locked decisions. Procedure:

1. **Read the inputs.** `sitemap.yaml` (pages + routes + shared nav regions), `content/pages/{slug}.md` (prose + the phase-14 wireframe), `content/strings/{lang}.json` (microcopy keys), `components.yaml` (component contracts), `project.yaml` (stack, languages), `brand.yaml.tokens` (token-fidelity check target).
2. **Resolve current stack composition patterns via context7** before writing routes. The chosen stack's routing/composition idiom changes (Next App Router Server/Client rules, Astro island directives, Hugo content+layout pairing). Do not compose from training-data memory. Invocation pattern + per-stack library IDs: `references/context7-and-stack-patterns.md`.
3. **Assemble every page** at its sitemap route in the stack's convention; sections in the phase-14 order, each rendered with its phase-18 component(s) at the phase-14 layout shape; shared header/footer from the phase-10 IA referenced once (never redrawn per page).
4. **Wire content in** — phase-16 prose into sections, phase-16 string keys into microcopy/CTA/state slots. Multilingual sites compose per the locked i18n pattern.
5. **Build + sanity-walk.** Run the stack's production build (`next build`, `astro build`, `hugo`, etc.). Then a Playwright walk: sections in order, content wired, nothing obviously broken. A page that doesn't compile is not composed.

Refuse to advance when: a sitemap page is not composed; the build fails; content overflow breaks section rhythm and was not surfaced; a composed component isn't in `components.yaml` (that is a phase-18 gap — return there for that one component, do not improvise it inline). These are completeness/correctness gates, not overridable preferences. The phase-19 detail (composition-level hardcoding sweep, per-page header drift, the "it renders ≠ it's responsive" boundary) is in `references/phase-procedures.md` § Phase 19.

### Phase 20 — Responsive pass (`phase-contracts/20-responsive-mobile.md`)

**Mobile is a decision, not a default.** Non-skippable per the VISION anti-skip lock. Procedure:

1. **Mobile-first.** For every page, snapshot 360 first via Playwright, make the layout intentional per the page's phase-14 per-section reflow directive (`content/pages/{slug}.md` § Wireframe), then verify up through 768 and 1280.
2. **Tablet is a deliberate choice** — not "desktop minus a bit," not "phone stretched." Decide 768 explicitly (often the 2-col middle ground).
3. **Re-snapshot all three after every change.** A mobile fix that silently breaks desktop/tablet is the canonical regression; never assume a mobile-targeted change stayed mobile-scoped.
4. **Write overrides in the stack's responsive idiom** (Tailwind `md:`/`lg:` variants + container queries, CSS media/container queries, framework responsive props), referencing phase-17 tokens — not ad-hoc shrink values. Verify the current responsive API via context7 (Tailwind v4 container queries are core, not a plugin).
5. **Produce the snapshot record** — `.website-builder/audit/responsive/{slug}-{360,768,1280}.png` per page + `.website-builder/audit/RESPONSIVE-RECORD.md` (per-page breakpoint × status × notes). Interact before snapshotting where layout depends on state (open the mobile nav drawer first).

Refuse to advance when: mobile is accidental not intentional; a breakpoint snapshot is missing; horizontal scroll at 360px; a mobile fix broke another breakpoint; tablet is an unconsidered tween. None overridable. Playwright viewport+screenshot+interact recipe: `references/playwright-recipes.md`.

### Phase 21 — Accessibility audit (`phase-contracts/21-accessibility-audit.md`)

**Two independent passes, both required: automated + manual keyboard walk.** Red-flag gates individually non-overridable; the whole phase is skippable only under explicit cost-surfaced logged authorization (`phase-contracts/21-accessibility-audit.md` § Skip authorization). Procedure:

1. **Automated pass.** Run axe-core (via `@axe-core/playwright`'s `AxeBuilder` builder pattern, scoped with `withTags`) **or** Lighthouse accessibility category, against the live dev/preview server. For state-dependent UI (modals, drawers): interact-then-`analyze()` — open the element with Playwright first, then re-run axe on that state, or axe never sees it. The score is a signal; the underlying axe checks + manual walk are the gate. Tag selection, the builder pattern, interact-then-analyze: `references/axe-lighthouse-recipes.md`.
2. **Manual keyboard walk.** Tab through every page via Playwright: every interactive element reachable in logical order, focus visible at each stop, modals/menus operable and escapable by keyboard, no trap. Automated tools catch ~30-50%; this catches the rest.
3. **Screen-reader sniff test.** `locator.ariaSnapshot()` captures the accessibility tree as structured YAML — confirm headings, landmarks, link text (no bare "click here"), image alts read sensibly.
4. **Fix, don't just report.** Add alt text (meaningful = descriptive in phase-16 voice from the phase-8 image plan; decorative = empty `alt=""`), add programmatic labels (placeholder-as-label fails), fix heading hierarchy, adjust an OKLCH token's lightness for contrast (predictable because phase 17 worked luminance-first), add the missing ARIA, fix focus order.
5. **Write `.website-builder/audit/A11Y-REPORT.md`** (per-criterion: criterion / level / automated result / manual result / fixes applied) + raw tool output to `.website-builder/audit/a11y/`.

The WCAG 2.1 AA criteria this phase verifies (contrast 1.4.3/1.4.11, text alternatives 1.1.1, keyboard 2.1.1/2.1.2, focus visible 2.4.7, structure 1.3.1, form labels 3.3.2/4.1.2, consistent nav 3.2.3) + the WCAG 2.2 superset context + per-criterion red-flag rules: `references/wcag-aa-criteria.md`.

### Phase 22 — Performance audit (`phase-contracts/22-performance-audit.md`)

**Lighthouse ≥ 80, mobile profile, production build.** CWV green. Same skip-authorization shape as phase 21. Procedure:

1. **Production build only.** `next build && next start` / `astro build && astro preview` / equivalent — never the dev server (unminified, unsplit → meaningless number).
2. **Mobile profile is the gating run** (slowest realistic device + network throttling); desktop reported alongside.
3. **Gate on the score + CWV:** Lighthouse performance ≥ 80; LCP < 2.5s; CLS < 0.1; INP < 200ms (current thresholds, 75th percentile is the real-world target; lab is the pre-launch proxy — phase 30 / post-launch monitoring watches field CWV).
4. **Fix the real experience, never game the score.** Optimize the hero image (responsive variants + AVIF/WebP + explicit dimensions + preload the LCP image), font-loading (`font-display: swap`/`optional` + `preconnect`/`preload` + metrics-matched fallback), lazy-load + code-split (dynamic-import heavy/animation components with a static fallback). Verify the stack's current perf primitives via context7 (`next/image`, `next/font`, `next/dynamic`, Astro `<Image>`).
5. **Write `.website-builder/audit/PERF-REPORT.md`** (per-page: score / LCP / CLS / INP / top opportunities / fixes) + raw Lighthouse JSON/HTML to `.website-builder/audit/perf/`.

Refuse to advance when: score < 80 (mobile, prod); LCP ≥ 2.5s; CLS ≥ 0.1; INP ≥ 200ms; audited the dev server; unoptimized hero shipped; score asserted not measured. Lighthouse CLI / Lighthouse CI assertion config (the `categories:performance ["error", {"minScore": 0.8}]` gate) + CWV detail: `references/axe-lighthouse-recipes.md`.

### Phase 23 — Forms + interactive (`phase-contracts/23-forms-interactive.md`)

**A form without a working endpoint is a broken form.** "I'll set up the email later" is the exact failure this phase exists to prevent — refuse it, and make the fix feel *small* (a Formspree form ID is a 60-second signup). Procedure:

1. **For every form** (contact, newsletter, lead, booking-intent, search, filter): decide + configure a working endpoint matched to the stack (static/no-backend → public-endpoint-ID provider like Formspree/Formspark/Basin; has a server route → transactional API like Resend/Mailgun with the key server-side; backend → the stack's own API route).
2. **Wire the submit handler** to the real endpoint, with loading/success/error states bound to the phase-16 `strings.json` microcopy (the moment a user is most anxious is exactly where brand voice matters).
3. **Verify the effect end-to-end** — Playwright submits test data; then confirm the *effect*: the test email arrived in the configured inbox, the test signup appears in the list, the search returned the expected filtered results. Success-state-shown ≠ submission-received.
4. **Spam-protect public forms** — honeypot minimum; Cloudflare Turnstile is the 2026 recommended default for public lead/contact forms (low-friction, privacy-respecting, free); always verify the challenge token **server-side** before the business action — a client-only "passed" state is forgeable.
5. **Secrets by construction.** Public endpoint IDs (Formspree form ID) are not secrets — fine in markup. API keys (Resend/Mailgun) are secrets — server-side only, env-referenced, registered in `keys.yaml` (references only) + `.env.example` (placeholder), never persisted in project state, never client-side, never `NEXT_PUBLIC_`. The full secrets pattern (the 5-step keys protocol, the anti-patterns the agent refuses, prod-sync deferred to phase 29): `references/secrets-and-forms.md` — this is the secrets authority for phase 23, derived from `DESIGN-secrets-and-keys.md` (locked decisions 29, 44).

Refuse to advance when: any form has no configured endpoint; a form not verified end-to-end; a form secret hardcoded/client-exposed; a public form has no spam mitigation; a promised interactive feature is faked; a client token trusted without server verification. A genuinely form-less brochure site is *inapplicable* (phase runs, finds nothing, exits clean) — not skipped. Form-provider matrix + Playwright submission-verification recipe: `references/secrets-and-forms.md` + `references/playwright-recipes.md`.

## Recommended composable skills (surface to the user; do NOT vendor)

This skill points the user at upstream composables; it does not embed them. When the user reaches the relevant phase, recommend invoking them via the `Skill` tool:

- **Phase 21** — recommend `accessibility-compliance:wcag-audit-patterns` for deep WCAG 2.2 audit methodology + remediation patterns beyond the AA basics this phase gates, and `accessibility-compliance:screen-reader-testing` for thorough VoiceOver/NVDA/JAWS validation when the `ariaSnapshot` sniff test surfaces something that needs real-AT confirmation.
- **Phases 19-23** — recommend `document-skills:webapp-testing` for richer Playwright-driven interaction/debugging when the sanity-walk (19), responsive snapshots (20), or form verification (23) need more than the recipes here.
- **Phase 22** — recommend the `performance-testing-review:performance-engineer` subagent (via the `Agent` tool) when a Lighthouse < 80 result needs root-cause profiling deeper than the Lighthouse "Opportunities" section provides.

Phrase each as: "for this phase, you can also invoke `<composable>` via the Skill tool for `<specific purpose>`." Do not auto-invoke; the user opts in.

## Reference files

Detailed material is in `references/` — loaded on demand to keep this file lean:

- **`references/phase-procedures.md`** — per-phase deep procedure + the full common-failure-mode catalog (content overflow, accidental mobile, decorative-vs-meaningful alt, unoptimized hero, "I'll set up email later", etc.) for all five phases.
- **`references/playwright-recipes.md`** — Playwright MCP recipes: viewport resize + screenshot per breakpoint, interact-then-snapshot for stateful UI, keyboard tab-walk, `ariaSnapshot` accessibility-tree capture, form fill+submit+effect-verification.
- **`references/axe-lighthouse-recipes.md`** — `@axe-core/playwright` `AxeBuilder` builder pattern + `withTags`/`include`/`exclude` + interact-then-`analyze()`; Lighthouse CLI + Lighthouse CI (`lighthouserc` assertion config, the 80+ gate, CWV assertions); production-build invocation.
- **`references/wcag-aa-criteria.md`** — the WCAG 2.1 AA criteria phase 21 gates, per-criterion red-flag rules, the WCAG 2.2 (87 criteria / 9 new) superset context, and the axe-core WCAG tag map (`wcag2a`/`wcag2aa`/`wcag21aa`/`wcag22aa`).
- **`references/secrets-and-forms.md`** — phase-23 form-provider matrix (Formspree/Formspark/Basin vs Resend/Mailgun vs stack route), the 5-step keys protocol, spam-protection layering + server-side token verification, the secrets anti-patterns the agent refuses.
- **`references/context7-and-stack-patterns.md`** — the context7 invocation pattern for this phase group, per-stack library-id manifest (`reference-corpus/seeds/{stack}.yaml`), when to skip context7, resolution-failure fallback.

## Cross-references

- Phase contracts (authoritative): `phase-contracts/19-composition.md`, `20-responsive-mobile.md`, `21-accessibility-audit.md`, `22-performance-audit.md`, `23-forms-interactive.md`
- Architecture (skill load model): `DESIGN-architecture.md` § Skills — one per phase group
- context7 integration: `DESIGN-context7-integration.md`
- Secrets authority (phase 23): `DESIGN-secrets-and-keys.md` (locked decisions 29, 44)
- Project scaffold (`audit/` + `keys.yaml` locations): `DESIGN-project-scaffold.md`
- Content layers (`strings.json` Layer 3, phase-16 microcopy): `DESIGN-content-layers.md`
- Locked decisions 29, 44, 50, 64 — STATE doc: `website-builder.md`
- Vault secrets / tool-dependency rules: `.claude/rules/secrets-conventions.md`, `.claude/rules/tool-dependency-discipline.md`
