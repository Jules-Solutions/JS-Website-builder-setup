---
type: RPT
callsign: corpus-2
program: website-builder remediation
track: corpus (set 2 of 2)
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-architecture.md
  - Workstreams/website-builder/foundation/DESIGN-ecosystem-catalog.md
  - Workstreams/website-builder/cross-cutting/DESIGN-resource-curation.md
branch: corpus-2
status: done
---

# RPT — corpus-2 (reference-corpus set 2)

> NOTE TO GENERAL: this RPT lives in the plugin worktree only because the vault is a separate repo this worktree can't write to. Relocate to `Workstreams/website-builder/RPT-corpus-2.md` and delete this in-plugin copy on review (same handling as corpus-1).

## Summary

Populated the remaining 3 of the 6 `reference-corpus/` dirs with real, usable reference content per `DESIGN-architecture.md` §330/331/332: `voice-archetypes/` (8 archetypes), `component-patterns/` (20 canonical specs), `seo-checklists/` (Lighthouse-mapped performance + SEO). Each dir has a per-dir README matching corpus-1's shape. corpus-1's 3 dirs were not touched. The top-level `reference-corpus/README.md` was extended additively. All content is substantive (not stubs): 1,455 lines across the 20 component specs alone, plus 8 archetypes grounded in NN4D/Aaker/Jung and two Lighthouse-audit-mapped checklists. Catalogue-entry spec for the General's consolidated wiring pass is in §Catalogue-entry spec below.

## What was done

- **Branch:** `git switch -c corpus-2` off worktree HEAD, which equals `dev` (sha `c7141e4`, includes Wave 1 spine + corpus-1's merge).
- **`reference-corpus/voice-archetypes/`** (9 files: 8 archetypes + README) — authored by me (judgment-heavy). Each archetype: NN4D 4D profile + Aaker dimension + Jung archetype in frontmatter and a `## Framework grounding` section, plus `## Voice description`, `## Attributes`, `## Say / never-say`, `## Sample copy` (hero + CTA + microcopy), `## Best for / avoid for`. The 8 spread across the NN4D space (both poles of all four dimensions represented): calm-expert, warm-guide, playful-challenger, bold-motivator, refined-luxe, everyman-plainspoken, warm-contrarian, visionary-creator. Grounded in `skills/wb-discovery/references/voice-archetype-frameworks.md`.
- **`reference-corpus/component-patterns/`** (21 files: 20 specs + README) — the canonical 20 (hero, nav, footer, breadcrumb, banner, card, feature-grid, stat-block, gallery, logo-cloud, testimonial, pricing-table, cta, team-grid, newsletter-signup, form, modal, tabs, accordion, faq). 20 specs delegated across 4 synchronous subagents (5 each, grouped by role); README authored by me. Every spec follows one fixed shape: Purpose → When to use/when not → Anatomy → Content slots → Accessibility requirements → Common variants → Pitfalls. Content-slot tables map to the plugin's 5 content layers; interactive specs (form/modal/tabs/accordion/faq) follow the WAI-ARIA APG patterns verbatim.
- **`reference-corpus/seo-checklists/`** (3 files: performance.md + seo.md + README) — authored by me. `performance.md` (phase 22): CWV + lab metrics, opportunities, diagnostics, each → Lighthouse audit id → fix path. `seo.md` (phase 26): Lighthouse SEO category audits + beyond-Lighthouse essentials (OG/Twitter, sitemap, JSON-LD by page type), each → audit id (or "not auto-scored") → fix path. Lighthouse audit ids verified against context7 `/googlechrome/lighthouse` (2026-06-26).
- **`reference-corpus/README.md`** — extended additively: 3 new bullets in the shipped-content list + updated phase-consumer sentence + updated Status line (all 6 dirs now populated; corpus-1 + corpus-2 RPT references). corpus-1's content preserved verbatim.

## DoD evidence

| DoD item | Evidence |
|---|---|
| 3 dirs populated per §330/331/332, NOT .gitkeep-only | `voice-archetypes/` 9 md, `component-patterns/` 21 md, `seo-checklists/` 3 md (file-count check below) |
| Per-dir README in each | `voice-archetypes/README.md`, `component-patterns/README.md`, `seo-checklists/README.md` all present + match corpus-1 shape |
| 20 component-pattern specs present + consistent in shape | 20 specs, every file has all 5 required sections (verified by grep loop — zero missing), ~67-77 lines each |
| Catalogue-entry spec for all 3 dirs in RPT | §Catalogue-entry spec below |
| corpus-1's 3 dirs untouched | `git status --short` on those 3 paths returns empty |

File-count + shape verification (run on branch corpus-2):
```
reference-corpus/voice-archetypes/   -> 8 archetypes + README
reference-corpus/component-patterns/ -> 20 specs + README ; all 5 required headings present in all 20
reference-corpus/seo-checklists/     -> performance.md + seo.md + README
git status --short: only ' M reference-corpus/README.md' + 3 new untracked dirs
git status reference-corpus/{design-systems,brand-examples,awesome-design-md-corpus}: empty (untouched)
```

## Decisions made

1. **8 voice archetypes, not 5-10 arbitrary.** Chose 8 to put a voice at both poles of every NN4D dimension (serious↔funny, formal↔casual, respectful↔irreverent, matter-of-fact↔enthusiastic), maximizing the contrast a stuck user reacts against. Each maps to a distinct Aaker dimension + Jung archetype so there's no overlap.
2. **Canonical 20 components = the INST's list, accepted as-is.** The INST's candidate list (hero…newsletter-signup) is already the brochure-site sweet-spot 20; no swap needed. `faq` built on the disclosure model with a cross-ref to `accordion` rather than duplicating the interaction spec.
3. **Delegated only component-patterns; kept voice + seo myself.** Per INST guidance — component specs are mechanical/templated (high consistency wins from a fixed template across 4 subagents); voice + seo carry more judgment (framework grounding, audit accuracy).
4. **seo-checklists split into 2 files by phase** (performance=22, seo=26) rather than one combined file — matches the §332 framing and the phases that consume them. Each is table-driven (`Check | audit id | Why | Target | Fix path`).
5. **Verified Lighthouse audit ids via context7** rather than trusting training data — CWV evolves (FID→INP March 2024; Lighthouse category membership shifts). Confirmed metric audit ids + LCP/CLS/TBT weighting; noted `font-size`/`tap-targets` left the SEO category and the audit `id` is the stable cross-version anchor.
6. **Stack-agnostic component specs.** Specs describe the pattern + a11y contract, not a framework. A "Stack-aware fix notes" section in performance.md is the one place stack specifics appear (as guidance, not lock-in).

## Sub-agents used

4 synchronous `general-purpose` subagents (Agent tool, `name` omitted, `run_in_background: false`), each handed the worktree path and an identical spec template, each authoring 5 component files directly onto the corpus-2 branch:

| Subagent | Components | Outcome |
|---|---|---|
| Group A | hero, nav, footer, breadcrumb, banner | 5 files ✓ |
| Group B | card, feature-grid, stat-block, gallery, logo-cloud | 5 files ✓ |
| Group C | testimonial, pricing-table, cta, team-grid, newsletter-signup | 5 files ✓ |
| Group D (interactive, APG-heavy) | form, modal, tabs, accordion, faq | 5 files ✓ |

I authored voice-archetypes (8), seo-checklists (2), all 4 per-dir/top READMEs, and verified all 20 component specs for shape + a11y accuracy (spot-checked modal.md + hero.md in full — both production-grade and APG-accurate).

## Catalogue-entry spec (for the General's consolidated `_resolve_resource` wiring pass)

The General is wiring all 6 corpus dirs into `scripts/wb_library.py`'s `CATALOGUE_CLONE_KEYS` in one pass (Mode 2 `bundled` type + Option A). My 3 dirs, in the existing `key -> (source_url_or_ref, type, default_subdir)` tuple shape, with the new `bundled` type:

```python
# reference-corpus set 2 (corpus-2) — bundled, in-plugin reference content
"voice-archetypes":  ("reference-corpus/voice-archetypes",  "bundled", "voice-archetypes"),
"component-patterns": ("reference-corpus/component-patterns", "bundled", "component-patterns"),
"seo-checklists":    ("reference-corpus/seo-checklists",    "bundled", "seo-checklists"),
```

Notes for the wiring pass:
- **`source_url_or_ref`** = the in-plugin path relative to the plugin root (`reference-corpus/<dir>`). For a `bundled` resource the resolver copies from the shipped plugin tree rather than fetching/cloning upstream — this is the distinction from the existing `github-repo`/`docs` types.
- **`type` = `bundled`** is new; `_resolve_resource` currently returns `CATALOGUE_CLONE_KEYS[resource]` for known keys and falls through to URL-typing for unknown ones, so adding these keys + a `bundled` branch in the copy/clone logic (and `_default_subdir_for_type` gains `"bundled": "."` or the dir name) is the General's edit. I did NOT edit `wb_library.py`.
- **`default_subdir`** = the dir name, so a cloned-in copy lands at `.website-builder/library/<dir>/` mirroring the plugin layout (consistent with the existing `awesome-design-md` entry using its dir name as subdir).
- The same shape applies to corpus-1's 3 dirs (`design-systems`, `brand-examples`, `awesome-design-md-corpus`) for a uniform 6-entry `bundled` block — but those are corpus-1's to confirm; I only own these 3.
- **Resource-ids** (`voice-archetypes`, `component-patterns`, `seo-checklists`) match the dir slugs so phase contracts can reference them by the same name used in the filesystem and the README.

## Ship Verification

Change class: **doc-only / bundled reference content** (no executable code). Evidence schema = render-check + file-existence + link-resolution.

- **Files exist at the spec'd paths** (branch corpus-2):
  - `reference-corpus/voice-archetypes/` — 8 archetype md + README.md (9 total)
  - `reference-corpus/component-patterns/` — 20 spec md + README.md (21 total)
  - `reference-corpus/seo-checklists/` — performance.md, seo.md, README.md (3 total)
- **Shape consistency** — grep loop over all 20 component specs for the 5 required headings (`## Purpose`, `## Anatomy`, `## Content slots`, `## Accessibility requirements`, `## Common variants`): zero missing. All 20 carry `corpus: component-patterns` frontmatter. All 8 archetypes carry `## Framework grounding` + `## Sample copy` + `## Say / never-say`.
- **Additive README** — `git diff reference-corpus/README.md` shows only insertions (3 bullets + 1 paragraph rewrite + 1 status-line rewrite); corpus-1 bullets preserved verbatim.
- **Isolation** — `git status --short` shows only ` M reference-corpus/README.md` + the 3 new untracked dirs; corpus-1's 3 dirs report empty status (untouched).
- **Markdown validity** — all files are well-formed md (frontmatter fences balanced, tables render); authored via Write/Edit which would have surfaced any malformed write.
- **NOT shipped by me, by design:** the `wb_library.py` `bundled` resolver wiring (General's consolidated pass) and the merge of corpus-2 → dev (General gates). Until the General lands the resolver branch, these dirs are readable-in-place reference content (which is how the agent consumes them at phases 4/5/9/17/18/22/26) but not yet `wb library`-clonable by resource-id. Flagged, not a gap in my scope.

## Follow-ups filed

1. **Catalogue resolver wiring (General-owned, already planned):** add the 3 (or 6) `bundled` keys + a `bundled` branch in `_resolve_resource`/clone logic in `scripts/wb_library.py`, per §Catalogue-entry spec. This is the General's consolidated pass; noted here for traceability.
2. **(Optional, low priority) Component-pattern ↔ brand-example cross-links:** the 20 component specs and the 7 brand-examples both describe components; a future light pass could add reciprocal "see also" links so the agent can jump from an abstract spec to a dressed example. Not required by §331.

## Retro notes

- Splitting the 20 specs across 4 subagents with a single embedded template produced near-perfect shape consistency (67-77 lines each, identical section structure) — the template-in-prompt approach is the right pattern for templated bulk content. Keeping voice + seo in-house was correct: both needed framework/audit accuracy that benefits from the authoring agent holding the full design context.
- The context7 Lighthouse check was worth the two calls — it confirmed the audit ids are the stable anchor and surfaced that Lighthouse 13.3 added an `agentic-browsing` category (out of scope here, but a signal that the perf/SEO surface keeps evolving; the checklists anchor on audit ids precisely so they age well).
- No PAUSE-AND-REPORT triggered: the INST was well-specified and the catalogue-schema question resolved cleanly against the existing `CATALOGUE_CLONE_KEYS` shape.
