# WCAG AA criteria — what phase 21 gates

> The WCAG criteria the accessibility audit (phase 21) verifies, the per-criterion red-flag rule, and the WCAG 2.2 superset context. The canonical source is W3C: WCAG 2.1 (`https://www.w3.org/TR/WCAG21/`) and WCAG 2.2 (`https://www.w3.org/TR/WCAG22/`). Verified via WebSearch W3C/WAI 2026-05-18.

## What phase 21 gates: WCAG 2.1 Level AA basics

Phase 21's contract gates the WCAG 2.1 AA *basics* — the criteria most reliably skipped by sighted-mouse builders because the problem is invisible to them. Each is a **red-flag, individually non-overridable** gate (the whole phase is skippable only under explicit cost-surfaced logged authorization per the contract's § Skip authorization; a partial "ship with just this one failure" is never a path).

| # | Criterion | Level | What it requires | Red-flag (blocks advance) |
|---|---|---|---|---|
| 1 | **1.4.3 Contrast (Minimum)** | AA | Text ≥ 4.5:1 vs background (≥ 3:1 for large text ≥ 24px or ≥ 18.66px bold) | Any text failing the ratio against the phase-17 tokens — verified at light AND dark mode if phase-17 strategy is auto/opt-in |
| 2 | **1.4.11 Non-text Contrast** | AA | UI components + meaningful graphics ≥ 3:1 vs adjacent colors | A button border / icon / focus ring / chart element below 3:1 |
| 3 | **1.1.1 Non-text Content** | A | Every meaningful image has alt serving its equivalent purpose; decorative → empty `alt=""`; functional (icon button) → accessible name | A meaningful image with no alt, or junk alt (the filename). Non-overridable — author meaningful alt from the phase-8 image plan + phase-16 voice before advance |
| 4 | **2.1.1 Keyboard** | A | Every interactive element reachable + operable by keyboard alone, logical order | An unreachable interactive element |
| 5 | **2.1.2 No Keyboard Trap** | A | Focus is never trapped; modals/drawers return focus + are escapable by keyboard | A keyboard trap |
| 6 | **2.4.7 Focus Visible** | AA | A visible focus indicator on every keyboard-operable element | No visible focus (the phase-17 `ring` token must actually render + clear 3:1 per 1.4.11) |
| 7 | **1.3.1 Info and Relationships** | A | One `h1`/page, logical heading nesting (no skipped levels), landmarks (`header`/`nav`/`main`/`footer`), lists as lists, structure programmatically determinable | Heading hierarchy faked with styled divs (no document outline for a screen reader) |
| 8 | **3.3.2 Labels or Instructions** | A | Every form input has a programmatic label (NOT placeholder-as-label) | A form input with no programmatic label. Placeholder-as-label does not count. Non-overridable |
| 9 | **4.1.2 Name, Role, Value** | A | Inputs/controls expose name/role/value to assistive tech | A control AT can't identify (custom widget with no role/name) |
| 10 | **3.2.3 Consistent Navigation** | AA | The shared nav appears in consistent order/presentation on every page | Per-page nav drift introduced at phase 19/20 (also a phase-19 header-drift failure) |

Plus the **screen-reader sniff test** (not a single SC — a cross-cutting confirmation via `locator.ariaSnapshot()`): headings, landmarks, link text (no bare "click here"), image alts read sensibly through the accessibility tree.

### Verification = two independent passes, both required

1. **Automated** — `@axe-core/playwright` `AxeBuilder` scoped `withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa'])` (add `'wcag22aa'` if the project targets 2.2 AA), interact-then-`analyze()` for state-dependent UI, OR Lighthouse a11y category. The audit must be *clean* (no violations of the above) — a high Lighthouse score with a hidden axe violation is NOT a pass. Recipe: `axe-lighthouse-recipes.md`.
2. **Manual keyboard walk** — Playwright tab-walk; automated tools catch ~30-50%, the manual walk catches keyboard order, focus management, trap, and whether alt text is *meaningful* (axe can't judge meaningfulness). Recipe: `playwright-recipes.md` § 3.

Automated-only is not a phase-21 pass. Manual-only is not either. Both, clean, then the report.

## WCAG 2.2 superset context (why "2.1 AA basics" still references 2.2)

WCAG 2.2 was published as a W3C Recommendation on 2023-10-05. It is the current standard:

- **87 total success criteria** (up from WCAG 2.1's 78): **9 new criteria added, 1 removed** (4.1.1 Parsing — obsolete, removed in 2.2).
- **Level AA = 55 criteria** (all A + AA; the legally-referenced conformance level in most jurisdictions — EU European Accessibility Act, US ADA Title III + Section 508, UK Equality Act).
- The 9 new criteria (mostly cognitive + mobile): **2.4.11 Focus Not Obscured (Minimum)** AA, 2.4.12 Focus Not Obscured (Enhanced) AAA, **2.4.13 Focus Appearance** AAA, **2.5.7 Dragging Movements** AA, **2.5.8 Target Size (Minimum)** AA, **3.2.6 Consistent Help** A, **3.3.7 Redundant Entry** A, **3.3.8 Accessible Authentication (Minimum)** AA, 3.3.9 Accessible Authentication (Enhanced) AAA.

**Phase-21 stance:** the contract gates the 2.1 AA *basics* as the hard floor (the 10-row table above). The 2.2 additions most likely to bite this plugin's sites are surfaced as **strong recommendations**, not hard gates, because they overlap work already done upstream or in adjacent phases:

- **2.5.8 Target Size (Minimum)** AA — touch targets ≥ 24×24 CSS px (or adequate spacing). Phase 20 already sized touch targets for mobile; phase 21 confirms it meets 2.5.8 and flags any that don't.
- **2.4.11 Focus Not Obscured (Minimum)** AA — a focused element must not be entirely hidden by sticky headers/footers. Verify during the manual keyboard walk (a sticky nav covering the focused field is a common phase-19/20 regression).
- **3.3.7 Redundant Entry** A + **3.3.8 Accessible Authentication** AA — relevant to phase-23 multi-step forms / any auth; phase 21 flags, phase 23 wires.

When the user's jurisdiction expects current conformance (EU EAA enforcement, ADA litigation exposure — surfaced in the contract's § Skip authorization), recommend the project target full WCAG 2.2 AA: add `'wcag22aa'` to the axe `withTags` and treat the 2.2 AA additions as gates too. Surface this as a recommendation with the concrete legal-exposure framing — do not silently widen the gate without the user's informed choice; and do not silently narrow it to "2.1 only" when the user operates where 2.2 is the expected standard.

## What the agent fixes (not just reports)

Phase 21 is a fix phase, not only a report phase. Per failure → fix:

- Missing/junk alt → meaningful alt in the phase-16 brand voice from the phase-8 image-plan intent; decorative → empty `alt=""`.
- Placeholder-as-label → a programmatic `<label>` (visible, or visually-hidden if the design truly requires, but present + associated).
- Contrast fail → adjust the offending OKLCH token's lightness — predictable because phase 17 worked luminance-first; trace whether it's the token or a composition-level one-off.
- Faked heading → real semantic heading; restore one h1/page + no skipped levels + landmarks.
- Missing role/name → add the ARIA the primitive didn't supply.
- No focus indicator → ensure the phase-17 `ring` token renders + clears 3:1.
- Keyboard trap / unreachable control → fix focus management (containment while open, restore on close, full reachability).
- Reduced-motion gap → add the `prefers-reduced-motion` gate (phase 17 budgeted it, 18 was to wire it, 21 verifies + fixes).

## Source freshness

- WCAG 2.1 / 2.2 criteria, 87-total / 9-new / 4.1.1-removed / 55-AA, the 9 new SCs: WebSearch W3C WAI "What's New in WCAG 2.2" + W3C TR/WCAG22 + Level Access checklist, 2026-05-18.
- Canonical sources: `https://www.w3.org/TR/WCAG21/`, `https://www.w3.org/TR/WCAG22/`, `https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/`.
- axe-core WCAG tag mapping: context7 `/dequelabs/axe-core` API.md, 2026-05-18 (see `axe-lighthouse-recipes.md`).
