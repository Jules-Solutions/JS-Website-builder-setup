# `cms-none` fixture — orientation

> Test fixture for the `cms-none` CMS adapter. Phase 4 manual verification surface; Phase 5+ test-runner integration is out of scope.

## What this fixture tests

**Adapter file:** `cms-adapters/cms-none.md`

**Pipeline phase baseline:** `phase-12-complete` — Phase 11 stack chosen (Astro), Phase 11 transactional sibling decided (`transactional: false`), Phase 12 CMS chosen (`cms: none`). Ready for phase 17 (design system) → 18 (component build) → 22 (i18n).

**Paired stack:** **Astro** — the `Native` default pairing for `cms-none` per `cms-adapters/README.md` cross-CMS × stack compatibility anchor (Astro Content Collections + Zod is the gold standard for file-based content).

Other paired-stack fixtures (Hugo + `none`, 11ty + `none`, Next.js static-export + `none`) are Phase 10+ scope.

## What's exercised by this fixture

- **L1 brand.yaml.tokens** — 3-color OKLCH palette + type scale + spacing + motion defaults
- **L2 sitemap.yaml + sections.yaml** — 3 pages (home / about / contact) + nav structure; components.yaml has 3 components (HeroBlock / NavBar / FooterBlock) mapping to 3 Zod discriminated-union section types
- **L3 strings/{lang}.json** — per-language CDJSON with `nav` + `cta` + `errors` namespaces; both `en.json` and `de.json` present
- **L4 content/pages/*.md** — per-language-folder pattern (Decision 39 default for cms-none + Astro); content at `content/pages/en/{home,about,contact}.md` and `content/pages/de/{home,about}.md` (intentional `contact.de.md` gap exercises Decision 41 missing-locale fallback)
- **L5 briefs/{component}.json** — NOT in fixture (briefs live in `.website-builder/briefs/` — agent-internal, not part of CMS-adapter validation)
- **Phase 22 i18n** — multilingual (en + de); routing strategy `prefix`; per-language folders; missing-locale fallback documented
- **Phase 24a commerce** — NOT exercised; `transactional: false` in `project.yaml`

## Setup the test runner needs

**None.** This fixture is fully self-contained markdown.

- No OAuth credentials (cms-none has no auth surface)
- No database (cms-none has no DB)
- No external services (cms-none uses filesystem + git only)
- No `.git/` directory in fixture (the "first content item created" entry in `expected.yaml` documents what creating the file IS, per the S1 CRUD vocabulary, but the actual git operations are not part of the fixture state)

Phase 5+ runner integration WOULD validate:

- Zod schema generation from `components.yaml`
- Per-locale file presence walking
- Strings file shape validation against `i18n/strings-schema.md` CDJSON contract
- Pre-commit lint script generation in `package.json`

Runner integration cannot validate:

- Actual git commit semantics (no `.git/` in fixture)
- Actual deploy via Vercel / Netlify / Cloudflare Pages (no live host)

## Known platform-specific gotchas

These are documented in `cms-adapters/cms-none.md` § "Common failure modes" and § "Limitations + escape hatches":

- **CRUD vocabulary for filesystem + git** (per S1 callout) — `cms-none`'s "API" is filesystem ops + git commands. The fixture's `expected.yaml.phase_12_cms.first_content_item_created` documents `content/pages/en/about.md (committed to git)` — the "committed" half is the load-bearing edge case. The adapter file's `## Auth + setup → ### CRUD vocabulary` section enumerates the full mapping.
- **No CMS layer** — Layer 1 design tokens never touch a CMS. They live in `src/styles/tokens.css` (or stack-equivalent). The fixture's `brand.yaml` is the SSOT; the rendered `tokens.css` is a build artifact (not in fixture — generated at phase 17).
- **Section discriminator naming** — the fixture's `components.yaml` includes a `section_type` field per component (e.g., `HeroBlock.section_type: hero`). This is the literal value used in page frontmatter `sections[].type`. Adapter file's `## Authoring patterns → Pattern 2` shows the Zod discriminated-union compilation.

## Cross-references

- **Adapter file:** `cms-adapters/cms-none.md`
- **Source design doc:** `Workstreams/website-builder/cms/DESIGN-cms-none.md`
- **Schema contract:** `cms-adapters/README.md` (12-section H2 contract + cross-CMS × stack anchor)
- **Sibling fixture conventions:**
  - `tests/cms-adapters/decap/README.md` (Captain J's deliverable)
  - `tests/cms-adapters/payload/README.md` (Captain K's deliverable)
  - `tests/cms-adapters/README.md` (CMS-adapter convention parent)
  - `tests/adapters/none/` — no such fixture (cms-none is a CMS, not a stack; the stack-adapter equivalent is `tests/adapters/astro/`)
- **Cached context7 snapshots used in adapter authoring:**
  - `.website-builder/library/docs/cms-none-astro.md`
  - `.website-builder/library/docs/cms-none-hugo.md`
  - `.website-builder/library/docs/cms-none-11ty.md`

## How to update this fixture

When the `cms-adapters/cms-none.md` contract evolves (new authoring pattern, new layer mapping, schema additions):

1. Update the corresponding fixture file (e.g., new section type → add to `components.yaml` + new sample `sections[]` entry in a page MD).
2. Update `expected.yaml.expected_per_phase` to reflect new phase outputs.
3. Update this README's "What's exercised by this fixture" section.
4. If the change introduces a new locked decision (38-41 i18n style), document the decision number in `expected.yaml` comments.

If the change affects the cross-CMS × stack compatibility anchor in `cms-adapters/README.md`, coordinate with sibling CMS Captains (J/K) and the General — that's a Phase 4 Captain 0 schema change requiring shared-substrate review.

## Fixture provenance

Authored 2026-05-20 by `wb-phase4-captain-i-cms-none-1` per `Workstreams/website-builder/INST` Phase 4 Captain I dispatch. Worktree: `Projects/Jules.Solutions/Subprojects/website-builder.captain-i/` on branch `phase-4-captain-i`. Validated manually against the 12-section schema in `cms-adapters/README.md` + the source design doc.
