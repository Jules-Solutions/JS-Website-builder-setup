# Phase procedures + common failure modes (phases 19-23)

> Deep per-phase procedure and the full failure-mode catalog. SKILL.md carries the lean procedure; this file is the detail loaded when a phase is actively running. The five phase contracts (`phase-contracts/19..23-*.md`) remain authoritative — this is the procedural overlay, not a substitute.

## Phase 19 — Composition

### Procedure detail

The discipline-heavy refusals already happened upstream (phase 14 refused to skip wireframing, 16 refused placeholder copy, 17 refused arbitrary color, 18 refused hardcoded values). Phase 19 is faithful assembly + catching the class of problem invisible until assembly.

1. Read `sitemap.yaml.pages[]` (route + section list), `sitemap.yaml.navigation` (shared header/footer regions), `content/pages/{slug}.md` (prose + the phase-14 wireframe = the assembly blueprint), `content/strings/{lang}.json`, `components.yaml`, `project.yaml` (stack/languages), `brand.yaml.tokens`.
2. context7 the stack's current routing/composition idiom before writing any route — this is where stale routing knowledge produces broken builds. Per-stack IDs in `context7-and-stack-patterns.md`.
3. For each page: create the route file in the stack convention (`app/{route}/page.tsx`, `src/pages/{route}.astro`, `content/{route}.md` + layout, etc.), compose sections in the phase-14 committed order with their phase-18 components at the phase-14 layout shape, reference the shared layout (never redraw the header per page).
4. Wire phase-16 prose + string keys. Multilingual: compose per the locked i18n Pattern A (shared structure) / Pattern B (market variation).
5. Run the production build. Then a Playwright sanity-walk of every page.
6. Composition-level token sweep: no one-off inline styles at the page level (`<section style={{marginTop: 80}}>`) where a phase-17 spacing token belongs — page assembly must be as token-faithful as the components.

### Common failure modes (phase 19)

- **Content overflow on long sections** — the canonical one. Phase-14 wireframe assumed a 2-line headline; phase-16 copy is 4 lines; the section breaks at desktop width. Surface it with the two fixes ("tighten the headline → thin phase-16 re-touch, or adjust the section → thin phase-14 re-touch — which?") and apply the user's choice. Never silently ship the broken section.
- **Build breaks on a Server/Client boundary** — Next App Router: a Server-component page imports a Client form component without the boundary handled. Verify current App Router rules via context7; the form is `'use client'`, the page stays Server. Don't guess from training data.
- **Assembly reveals a missing component** — a section needs a component nobody specced/built. Do NOT improvise it inline (bypasses phase-18 discipline). Surface the gap, return to phase 18 for that one component (specced, built, reviewed), resume.
- **Hardcoding at composition level** — pasted code drops a one-off inline style. The token sweep catches it.
- **Per-page header/footer drift** — header re-implemented slightly differently on one page. Shared regions are phase-10-locked, phase-18-built once; every page references the same layout. Unify any drift (consistent-navigation, WCAG 2.4.5/3.2.3 — phase 21 would otherwise flag it).
- **"Just assemble it, we'll see how it looks"** — composition without build or render produces a non-compiling or broken site found 3 phases later. Build + Playwright sanity-walk are part of phase 19.
- **Treating the sanity-walk as the responsive pass** — phase 19's visual check confirms sections render in order with content wired; it is NOT the phase-20 verification (snapshots at 360/768/1280). Surface the boundary: "it renders" (19) ≠ "it's responsive" (20).
- **"Composition is the finished site"** — it is not. Surface that phase 19 produces a rendered site still needing responsive (20), a11y (21), perf (22), forms (23) before launch-ready.

## Phase 20 — Responsive / mobile pass

### Procedure detail

Non-skippable per the VISION anti-skip lock. Mobile is a decision, not whatever the desktop CSS did when the viewport shrank.

1. Mobile-first per page: Playwright at 360 first → make it intentional per the page's phase-14 per-section reflow directive (`content/pages/{slug}.md` § Wireframe → mobile reflow notes) → then 768 → then 1280.
2. Tablet (768) is a deliberate choice — frequently the 2-col middle ground between desktop 3-col and phone 1-col. Never an unconsidered tween.
3. Nav: verify the desktop horizontal nav collapses to the decided phase-10 mobile pattern (hamburger drawer / bottom bar). Playwright opens the drawer before snapshotting (the layout depends on state).
4. Touch targets adequately sized at mobile width (also feeds phase 21 — WCAG 2.5.5/2.5.8 target size).
5. Write overrides in the stack's responsive idiom referencing phase-17 tokens (mobile type sizes come from the phase-17 scale, not arbitrary shrink). context7 the current responsive API (Tailwind v4 container queries are core, not a plugin).
6. After EVERY change, re-snapshot all three breakpoints — a mobile fix that silently changed desktop/tablet is the canonical regression.
7. Exit = the record: `.website-builder/audit/responsive/{slug}-{360,768,1280}.png` per page + `.website-builder/audit/RESPONSIVE-RECORD.md` (per-page breakpoint × status × notes).

### Common failure modes (phase 20)

- **Desktop-only thinking** — built/checked at 1280, assumed the phone is fine. Enforce mobile-first: 360 first, intentional per phase-14 directive, then up.
- **"Responsive" = "doesn't completely break"** — a 3-col grid that becomes 3 cramped narrow columns on a phone instead of stacking passes a naive eyeball, fails the intent. Check the reflow against the phase-14 directive, not against "did it crash."
- **A mobile fix breaks desktop** — a non-responsive utility / global override leaks. Re-snapshot all three after every change.
- **Horizontal scroll at 360px** — an image, table, `min-width`, or unbreakable long string overflows. Hunt the source (Playwright width check), fix with `overflow` handling / responsive image sizing / `word-break` / a scoped scroll container.
- **Tablet ignored** — make 768 a deliberate decision.
- **Touch targets too small on phone** — desktop hover-sized targets fail tap reliability; size them adequately (WCAG 2.5.5/2.5.8).
- **Snapshots skipped — "trust me, it's responsive"** — the exit criterion *is* the record; produce the snapshots.
- **Mobile nav forgotten** — desktop horizontal nav left as-is on phone; verify it collapses to the decided pattern with the drawer actually opening (Playwright interacts before snapshot).
- **"Responsive is a polish step"** — it is a correctness step; most real visitors are on phones. Non-skippable per the VISION lock.

## Phase 21 — Accessibility audit

### Procedure detail

Two independent passes, both required. Phase 17 locked a contrast-safe palette by construction; phase 18 wired a11y obligations into components; phase 21 verifies end-to-end on the assembled, responsive site and fixes anything that slipped.

1. **Automated** — `@axe-core/playwright` `AxeBuilder` scoped with `withTags` (`wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`; the project may opt into `wcag22aa`) **or** Lighthouse accessibility category, against the live dev/preview server. Interact-then-`analyze()` for state-dependent UI: open the modal/drawer with Playwright Locators + `waitFor`, then `analyze()` on that state — axe doesn't see hidden elements otherwise. Recipe: `axe-lighthouse-recipes.md`.
2. **Manual keyboard walk** — Playwright tab-walk each page: every interactive element reached in logical order, focus visible per the phase-17 `ring` token, modals/menus operable + escapable, no trap. ~half the issues are only catchable here.
3. **Screen-reader sniff test** — `locator.ariaSnapshot()` → structured-YAML accessibility tree; confirm one h1/page, logical heading nesting, landmarks, link text (no bare "click here"), image alts read sensibly.
4. **Fix** — meaningful image → descriptive alt in phase-16 voice from the phase-8 image plan; decorative → empty `alt=""`; functional (icon button) → accessible name. Programmatic label (not placeholder). Real semantic headings + landmarks. OKLCH lightness adjustment for contrast (predictable: phase 17 worked luminance-first). ARIA the primitive didn't supply. Focus order.
5. Write `.website-builder/audit/A11Y-REPORT.md` (per-criterion: criterion / level / automated / manual / fixes) + raw output to `.website-builder/audit/a11y/`.

Criteria + per-criterion red-flag rules: `wcag-aa-criteria.md`.

### Common failure modes (phase 21)

- **Decorative images getting descriptive alt (and vice versa)** — the canonical one. Decorative flourish → empty `alt=""` (AT skips it); meaningful product photo → descriptive alt. Enforce the rule from the phase-8 image-plan intent + phase-16 voice.
- **Placeholder used as a label** — `placeholder="Email"` with no `<label>`. Placeholders vanish on input + aren't reliably announced. 3.3.2/4.1.2 fail. Wire a programmatic label (visible, or visually-hidden if the design truly requires, but present + associated).
- **Lighthouse-score-as-pass** — "a11y says 96, ship it." The score can be high with a real violation persisting and it doesn't catch keyboard-order at all. axe checks + manual walk are the gate; score is secondary.
- **Automated-only audit** — axe green, advance. Automated catches a portion; keyboard order, focus management, "is the tab sequence sensible," whether alt is *meaningful* (axe can't judge) need the manual walk. Do both.
- **Animation-library a11y gap** — an Aceternity/Magic-UI motion component ignores `prefers-reduced-motion`, or a custom widget has no keyboard support. Phase 17 budgeted reduced-motion, 18 was to wire it; 21 verifies + fixes the gap.
- **Contrast regression after phase 17** — a one-off color at composition (a muted caption on a tinted surface) fails 4.5:1. Trace it; fix is a predictable OKLCH lightness adjustment.
- **Heading hierarchy faked with styled divs** — `<div class="text-3xl">` instead of `<h1>`/`<h2>`; a screen reader gets no outline. Enforce real semantic headings (one h1/page, no skipped levels) + landmarks.
- **"It works fine for me"** — tested with a mouse + good vision. The whole point is the users who don't. Run the real verification regardless of how it feels.
- **"A11y is a nice-to-have"** — it is a correctness dimension + a legal requirement in many jurisdictions (EU European Accessibility Act, US ADA Title III + Section 508, UK Equality Act). Surface the concrete cost per the contract's § Skip authorization.

## Phase 22 — Performance audit

### Procedure detail

Lighthouse ≥ 80, mobile profile, production build. Phase 17 pre-budgeted heavy motion; phase 18 wired lazy-loading on heavy components; phase 22 measures on the assembled site + fixes what slipped.

1. Production build (`next build && next start`, `astro build && astro preview`, `hugo`, `vite build && vite preview`) — never the dev server.
2. Lighthouse CLI / Lighthouse CI, mobile profile with throttling = the gating run; desktop reported alongside. Recipe: `axe-lighthouse-recipes.md`.
3. Gate: performance ≥ 80; LCP < 2.5s; CLS < 0.1; INP < 200ms. (75th-percentile field data is the real target; lab here is the pre-launch proxy — phase 30 / post-launch monitoring watches field CWV.)
4. Fixes, optimizing the real experience (never score-gaming): hero image → responsive variants (`srcset`/`sizes`) + AVIF/WebP w/ fallback + explicit dimensions (kills CLS) + preload the LCP image; fonts → `font-display: swap`/`optional` + `preconnect`/`preload` critical font + metrics-matched fallback; lazy-load below-the-fold images + dynamic-import heavy/animation components with a static SSR fallback. context7 the stack's current perf primitives (`next/image`, `next/font`, `next/dynamic`, Astro `<Image>`).
5. Write `.website-builder/audit/PERF-REPORT.md` (per-page: score / LCP / CLS / INP / top opportunities / fixes) + raw Lighthouse JSON/HTML to `.website-builder/audit/perf/`.

### Common failure modes (phase 22)

- **Unoptimized hero image** — the canonical one + usually the biggest LCP killer (a 3MB PNG hero at full res to a phone). Responsive variants + AVIF/WebP + explicit dimensions + preload the LCP image.
- **Audited the dev server** — unminified/unsplit/HMR overhead → meaningless number → panic-fixing non-issues. Always the production build.
- **"Feels fast on my machine"** — fast wired desktop + warm cache is the opposite of the median visitor. Run the *mobile* throttled profile — the run that predicts real bounce.
- **CLS from un-dimensioned media or late fonts** — set explicit dimensions on every image; metrics-matched fallback + `font-display` so nothing reflows.
- **Render-blocking font load** — display font loaded synchronously. `font-display: swap`/`optional`, `preconnect`/`preload`, matched fallback metrics.
- **Heavy animation component blows LCP/INP** — Aceternity + Three.js eager hero. Phase 17 budgeted it, 18 was to dynamic-import w/ static fallback; 22 verifies + enforces.
- **Score-gaming** — stripping content / lazy-loading the LCP image to bump the number while worsening the experience. Optimize the real experience; CWV reflect it.
- **Treating lab CWV as final** — lab is one synthetic run; field (75th pct real users) is the truth. Surface that lab is the pre-launch proxy; phase 30 / monitoring watches field.
- **"Performance is a polish step"** — it is a conversion + reach step (slow sites lose visitors before they see anything; CWV is a ranking signal). Surface the concrete cost per the contract's § Skip authorization.

## Phase 23 — Forms + interactive logic

### Procedure detail

A form without a working endpoint is a broken form. Make the fix feel small; refuse the deferral.

1. For each form (contact / newsletter / lead / booking-intent / search / filter): decide + configure a working endpoint matched to the stack. Provider matrix: `secrets-and-forms.md`.
2. Wire the submit handler to the real endpoint; bind loading/success/error states to the phase-16 `strings.json` microcopy keys.
3. Verify the *effect* end-to-end — Playwright submits test data, then confirm the effect (email arrived in the configured inbox; signup appears in the list; search returned the expected filtered results). Where the effect isn't web-visible, use `AskUserQuestion` to have the user confirm receipt, or query the provider API via Bash.
4. Spam-protect public forms: honeypot minimum; Cloudflare Turnstile (2026 default) for genuinely public lead/contact forms; always verify the token server-side before the business action.
5. Secrets by construction per the keys protocol (`secrets-and-forms.md`): public endpoint IDs in markup; API keys server-side + env-referenced + registered in `keys.yaml` (references only) + `.env.example`; never persisted in project state, never client-side. Prod-sync of the live key is a phase-29 follow-through (flag it; don't do it here).
6. Write `.website-builder/audit/FORMS-REPORT.md` (per-form: form / endpoint / provider / spam-protection / test-submission result / effect-verified Y-N) + the `keys.yaml`/`.env.example` entries for any secret-bearing endpoint.

A genuinely form-less brochure site is *inapplicable* — the phase runs, finds nothing to wire, exits clean (not a skip; see `phase-contracts/23-forms-interactive.md` and `DESIGN-phase-contracts.md` § Phase-skip authorization "inapplicable phase").

### Common failure modes (phase 23)

- **"I'll set up the email later"** — the canonical one (named in the seed). Form looks done, launches, silently drops every lead. Refuse; make it small: "60-second step, not a project — sign up at Formspree, paste the form ID, your contact form is real. Let's do it now so you don't lose a single message."
- **Form "works" because no JS error — but posts to nowhere** — verify the *effect* (email actually arrived), not the absence of an error. Success-state-shown ≠ submission-received.
- **Secret in client code** — a Resend/Mailgun key in a client component or `NEXT_PUBLIC_`/`PUBLIC_` var, exposed in the browser bundle. Wire server-side only, env-referenced, per the keys protocol.
- **Public form with no spam protection** — drowned in spam within days; provider rate-limits/suspends; real leads lost in the noise. Honeypot minimum + Turnstile for public forms, server-side token verify.
- **Client-side captcha "pass" trusted** — a bot forges the passed state. Verify the token server-side against the provider before the business action.
- **Search that doesn't search / filter that doesn't filter** — faked promised interactivity; same failure class as a dead form. Make it actually function or surface that it can't be built as promised + reconcile scope.
- **Form-state microcopy left generic** — "Submitted"/"Error" instead of the phase-16 voiced strings. Wire loading/success/error to the phase-16 `strings.json` keys — the anxious moments are exactly where voice matters.
- **Provider chosen without fitting the stack** — a server-side email API for a purely static site with no server route to hold the key. Match the endpoint to the stack (static → public-endpoint-ID provider; server route → transactional API key server-side).
- **"A pretty form is a working form"** — the form's entire purpose is the effect. An unverified form is functionally decorative until the effect is confirmed.
