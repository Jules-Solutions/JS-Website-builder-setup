---
phase: 20
name: Responsive / mobile pass
group: build-integration
pipeline_section: build-integration
skill: wb-build-integration
prev_phase: 19
next_phase: 21
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - DESIGN-phase-contracts.md
  - DESIGN-architecture.md
  - DESIGN-project-scaffold.md
  - DESIGN-context7-integration.md
---

# Phase 20 — Responsive / mobile pass

> An explicit, deliberate mobile pass: every page rendered and adjusted for phone, tablet, and desktop, verified with Playwright snapshots at 360px, 768px, and 1280px. The phase that makes mobile *intentional* instead of *accidental*. The agent refuses to advance until the mobile layout is a decision, not a side-effect of desktop CSS collapsing.

## Mission

Phase 19 assembled the site. It renders — on the agent's desktop. Phase 20 is the explicit pass that makes the site work, intentionally, on a phone and a tablet too. Not "it probably reflows OK" — *verified*: Playwright snapshots at the three reference breakpoints (~360px phone, ~768px tablet, ~1280px desktop), each confirming the layout at that width is a deliberate decision matching the phase-14 responsive intent, not whatever the desktop CSS happened to do when the viewport shrank.

The work product is responsive overrides in the stack code plus a Playwright snapshot record at the three breakpoints for every page. After phase 20, every page has an intentional layout at phone, tablet, and desktop — verified, not assumed.

The discipline of this phase is **mobile is a decision, not a default**. Most muggle-built (and many AI-built) sites are designed at desktop width and "responsive" only in the sense that the desktop layout doesn't completely shatter on a phone. That is accidental mobile, and it is the single most common quality failure in muggle websites — because the builder built at 1280px and never actually looked at 360px. Phase 14 already forced a one-line responsive *intent* per section; phase 20 is where that intent becomes verified reality. The agent refuses to advance with desktop-only thinking.

## Entry conditions

- Phase 19 (composition) complete. Every page in `sitemap.yaml` is assembled, builds cleanly, and renders. Phase 20 adjusts those assembled pages for the three breakpoints — it does not re-compose them.
- Phase 14 (wireframe per page) complete with responsive intent. Every section has a one-line reflow directive (e.g. "desktop: 3-col grid → mobile: stacked 1-col"; "desktop: split text-left/image-right → mobile: image-top/text-below"). Phase 20 verifies the assembled site matches that intent. (Phase 14's gate ensured this exists — even on the explicit-skip path, a per-section reflow note was captured precisely so phase 20 has something to verify against.)
- Phase 17 (design system) complete. The spacing scale, type scale, and any breakpoint tokens are the system phase 20's overrides work within (mobile type sizes come from the phase-17 scale, not arbitrary shrink values).
- Phase 11 (stack decision) complete. The stack's responsive primitives (Tailwind responsive variants + container queries, CSS logical properties, the framework's breakpoint conventions) are what phase 20's overrides are written in.

## What Claude must establish

For every page, an intentional layout at three breakpoints, verified:

1. **Phone (~360px).** Every section reflows per its phase-14 mobile directive. Navigation collapses to the phase-10 mobile pattern (hamburger drawer / bottom bar / etc.). Touch targets are adequately sized. Type uses the phase-17 scale's mobile sizes (reduced, but from the scale — not ad-hoc). Horizontal scroll does not occur. CTAs are reachable and appropriately full-width where the wireframe said so.
2. **Tablet (~768px).** The intermediate layout is intentional — not just "desktop minus a bit" and not "phone stretched." Grids that are 3-col on desktop and 1-col on phone make a deliberate choice at tablet (often 2-col); the agent does not let tablet be an unconsidered tween.
3. **Desktop (~1280px).** The phase-19 desktop composition, confirmed unbroken by the mobile overrides (a common regression: a mobile fix breaks the desktop layout — the agent verifies all three after every change, not just the one being fixed).
4. **Snapshot record.** A Playwright screenshot per page per breakpoint, stored as the verification artifact. The exit criterion is the *record*, not the agent's assertion — "I made it responsive" without snapshots is not a verified responsive pass.
5. **Responsive overrides in stack code.** The actual CSS/utility-class/component changes that produce the intentional layouts — written in the stack's responsive idiom (Tailwind `md:`/`lg:` variants + container queries, CSS media/container queries, the framework's responsive props), referencing phase-17 tokens.

Output: responsive overrides in the project source + a Playwright snapshot record (per page × {360, 768, 1280}). `.website-builder/project.yaml.current_phase` updates to `21` upon a complete, intentional snapshot record across all pages. Phase 21 (accessibility audit) loads next.

## Gating rules

The agent refuses to advance when:

- **Mobile is accidental, not intentional.** A section that "works on mobile" only because the desktop flexbox happened to wrap — with no deliberate phase-14-aligned reflow decision — fails this gate. The agent makes the mobile layout a decision (per the phase-14 directive) and verifies it. Accidental mobile is the canonical phase-20 failure and the gate exists specifically to refuse it.
- **A breakpoint snapshot is missing.** Every page needs a verified snapshot at 360, 768, and 1280. A page with only a desktop snapshot is not responsive-verified. The exit is the record.
- **Desktop-only thinking shipped.** A page where the agent only checked desktop and assumed the rest. The agent enforces a mobile-first check on every page — phone snapshot first, then up.
- **Horizontal scroll at 360px.** A page that requires horizontal scrolling on a phone (an overflowing element, a fixed-width block, an unbroken long string) is broken on mobile. The agent finds and fixes the overflow source before advance.
- **A mobile fix silently broke desktop (or tablet).** The agent changed a layout for phone and didn't re-verify the other two breakpoints. The agent re-snapshots all three after every responsive change; a regression at any breakpoint blocks advance.
- **Tablet is an unconsidered tween.** A page where 768px is neither the phone layout nor the desktop layout but an accidental in-between nobody decided. The agent makes the tablet layout a deliberate choice.

None of these are overridable — responsive correctness is a non-negotiable per the VISION anti-skip lock (the responsive pass is one of the phases the VISION explicitly forbids skipping). There is no "ship desktop-only with the cost surfaced" path here; mobile is not optional in 2026.

## Tools and skills used

- **Playwright MCP** — the primary tool. The agent drives a browser to each page at viewport widths 360, 768, and 1280, captures a screenshot per page per breakpoint, and inspects the rendered layout. Playwright is how "responsive" stops being an assertion and becomes a verified record. The agent uses Playwright's viewport-resize + screenshot capabilities; it interacts with the page (open the mobile nav drawer, scroll a section) before snapshotting where the layout depends on state.
- **`Edit` / `Write`** — to write the responsive overrides in the stack's idiom (Tailwind responsive variants + container queries, CSS media/container queries, framework responsive props), all referencing phase-17 tokens.
- **`mcp__context7__resolve-library-id` + `mcp__context7__query-docs`** — per `DESIGN-context7-integration.md`, phase 20 invokes context7 for stack-specific responsive primitives (Tailwind container queries + the current responsive-variant API, CSS logical-properties browser support, the framework's breakpoint conventions). Responsive APIs change (Tailwind v4 container queries are core, not a plugin) — the agent verifies current patterns.
- **`Bash`** — to run the dev server / build so Playwright has a live site to snapshot.
- **`Read`** — `content/pages/{slug}.md` (the phase-14 wireframe + its per-section responsive directives — the contract phase 20 verifies against), `brand.yaml.tokens` (the type/spacing scale mobile sizes come from), `sitemap.yaml.navigation` (the phase-10 mobile nav pattern).

The `wb-build-integration` phase-group skill remains loaded (single skill for phases 19-23 per Decision 64). It carries the cross-phase contract that the snapshots produced here are inputs phase 27 (cross-browser/device QA) extends, and that the responsive layout verified here is what phase 21 audits for a11y at mobile widths too (a contrast or touch-target issue can be mobile-specific).

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| Responsive overrides in the project source | per stack responsive idiom (Tailwind variants/container queries, CSS media/container queries) | The actual code that produces intentional layouts at each breakpoint. |
| `.website-builder/audit/responsive/` | Playwright screenshots: `{slug}-360.png`, `{slug}-768.png`, `{slug}-1280.png` per page | The verification record — the exit criterion. Carried into phase 27 QA. |
| `.website-builder/audit/RESPONSIVE-RECORD.md` | per-page table: breakpoint × status × notes | Human-readable summary of the responsive pass; what was adjusted and why. |
| `.website-builder/project.yaml` | `current_phase: 21` on complete record | Phase progression marker. |

The overrides + the snapshot record are the required outputs. "Responsive" without the snapshot record is not a completed phase 20.

## Common failure modes

**Desktop-only thinking.** The canonical failure. The agent (or the user) built and checked at 1280px and assumed the phone "will be fine." It rarely is — text overflows, a 4-col grid becomes an unreadable squeeze, a fixed-width hero forces horizontal scroll. The agent enforces mobile-first: snapshot 360 first, make it intentional per the phase-14 directive, then verify up through 768 and 1280.

**"Responsive" means "doesn't completely break."** A section that technically reflows but reflows *badly* (a 3-col card grid that becomes 3 cramped narrow columns on a phone instead of stacking) passes a naive eyeball and fails the intent. The agent checks the reflow against the phase-14 directive, not against "did it crash."

**A mobile fix breaks desktop.** The agent shrinks a hero for phone and the change (a non-responsive utility, a global override) also shrinks it on desktop. The agent re-snapshots all three breakpoints after every change — never assumes a mobile-targeted fix stayed mobile-scoped.

**Horizontal scroll on phone.** An image, a table, a `min-width`, or an unbreakable long string overflows 360px and the whole page scrolls sideways. The agent hunts the overflow source (the offending element is usually findable by a Playwright width check) and fixes it — `overflow` handling, responsive image sizing, `word-break`, a horizontally-scrollable container scoped to just the table.

**Tablet ignored.** The agent handles phone and desktop and lets 768px be whatever falls out. The agent makes tablet a deliberate decision (frequently the 2-col middle ground between desktop's 3-col and phone's 1-col).

**Touch targets too small on phone.** Desktop hover-sized links/buttons are too small to tap reliably on a phone. The agent sizes interactive targets adequately at mobile width (this also feeds phase 21 — small targets are an a11y concern, WCAG 2.5.5/2.5.8 target size).

**Snapshots skipped — "trust me, it's responsive."** The agent asserts responsiveness without the Playwright record. The exit criterion *is* the record; an assertion is not a verification. The agent produces the snapshots.

**Mobile nav forgotten.** The desktop horizontal nav is left as-is on phone, overflowing or wrapping awkwardly, instead of collapsing to the phase-10 mobile pattern (hamburger drawer / etc.). The agent verifies the nav reflows to its decided mobile pattern, with the drawer actually opening (Playwright interacts before snapshotting).

**Hidden assumption that responsive is a polish step.** It is not — it is a correctness step. The agent surfaces, when the user pushes to skip it ("looks fine on my laptop"), that most of the user's actual visitors are on phones, and an accidental-mobile site fails the majority of its audience. This phase is non-skippable per the VISION lock.

## Reference materials

Foundation docs:

- `DESIGN-phase-contracts.md` § 20 — the seed for this contract.
- `DESIGN-architecture.md` § Integration with Claude Code primitives (Playwright MCP usage) / § context7 integration.
- `DESIGN-project-scaffold.md` § `audit/` directory conventions; the per-page wireframe + responsive-directive location (`content/pages/{slug}.md`).
- `DESIGN-context7-integration.md` — phase 20 invokes context7 for stack responsive primitives (Tailwind container queries, CSS logical properties browser support).

The phase-14 wireframe directives (`content/pages/{slug}.md` § Wireframe → Mobile reflow directives) are the contract phase 20 verifies against — phase 14 is the upstream authority for *what* the responsive behavior should be; phase 20 is where it is *verified true*.

context7 (at this phase — current as of the freshness date): the agent resolves + queries the chosen stack's current responsive API at phase-20 entry — e.g. `/tailwindlabs/tailwindcss.com` (responsive variants + container queries — core in Tailwind v4), framework breakpoint conventions per `reference-corpus/seeds/{stack}.yaml`. Per `DESIGN-context7-integration.md`.

Freshness date for this contract's references: **2026-05-18**.
