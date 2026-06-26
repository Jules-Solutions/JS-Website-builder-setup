# Per-adapter test fixtures — convention

> Where Phase 3 (and subsequent) stack-adapter Captains place their adapter-specific test fixtures. **Stack-agnostic convention**; per-stack fixtures land in subdirectories.
>
> Anchor: `Workstreams/website-builder/BUILD-strategy.md` Phase 3 DoD line 179 (*"Each adapter passes adapter-specific test fixtures"*).

## Directory layout

```
tests/adapters/
├── README.md                       # this file
├── framer/
│   ├── fixture/                    # synthetic .website-builder/ scaffold
│   │   ├── project.yaml
│   │   ├── brand.yaml
│   │   ├── sitemap.yaml
│   │   ├── components.yaml
│   │   ├── content/
│   │   │   ├── pages/
│   │   │   │   └── home.md
│   │   │   └── strings/
│   │   │       └── en.json
│   │   └── ...
│   ├── expected.yaml               # per-phase expected adapter output
│   └── README.md                   # per-stack fixture notes (gotchas, run instructions)
├── nextjs/
│   ├── fixture/
│   ├── expected.yaml
│   └── README.md
└── wordpress/
    ├── fixture/
    ├── expected.yaml
    └── README.md
```

Each stack has its own subdirectory. Subdirectory name matches the adapter file basename (`stack-framer.md` → `framer/`; `stack-nextjs.md` → `nextjs/`; `stack-wordpress.md` → `wordpress/`).

## Minimum contents per stack

Each per-stack subdirectory MUST contain:

### `fixture/`

A synthetic `.website-builder/` scaffold representing a minimal-but-realistic project state at the **phase-11-complete** point in the pipeline (stack picked, transactional sibling decided, ready for phase 12). The scaffold includes:

- `project.yaml` — minimal but valid (`stack: <stack>`, `transactional: false`, default-language, entry-mode greenfield)
- `brand.yaml` — one tokenized palette (3-4 colors), one type scale (h1/h2/body), spacing scale, motion defaults
- `sitemap.yaml` — 3-5 pages (home, about, contact + one or two more) with `navigation:` block
- `components.yaml` — 2-3 components (HeroBlock, NavBar, FooterBlock at minimum)
- `content/pages/*.md` — minimal page MD per sitemap entry, in `default_language` only
- `content/strings/en.json` — minimal CDJSON with `nav`, `cta`, `errors` namespaces
- (Optional, when relevant to test) `content/strings/de.json` for multilingual coverage

The fixture is **synthetic** — no real brand, no real client data. Filler content; the contract is the *shape*, not the content quality.

### `expected.yaml`

A declarative spec of what the adapter SHOULD produce at each pipeline phase. Schema:

```yaml
# tests/adapters/{stack}/expected.yaml
fixture_baseline: phase-11-complete
expected_per_phase:
  phase_12_cms:
    cms_recommendation: <stack-default>          # framer-cms | wordpress-core | none/decap/payload
    confidence: high                              # high if stack-default; ask-user if multiple paths
  phase_17_design_system:
    tokens_written_to: brand.yaml + <stack-specific-path>   # e.g. Framer Color Styles via API
    drift_check: pass                            # no token drift vs fixture brand.yaml
  phase_18_component_build:
    components_generated: [HeroBlock, NavBar, FooterBlock]
    output_paths:                                # per-stack
      HeroBlock: <stack-specific-path>           # e.g. code/HeroBlock.tsx for Framer
      NavBar: <stack-specific-path>
      FooterBlock: <stack-specific-path>
    palette_validator: pass
    a11y_audit: pass
  phase_22_i18n:                                  # when fixture has multilingual
    hreflang_emitted: true
    language_switcher_added: true
    rtl_handling: n/a                            # unless fixture includes ar/he/etc.
  phase_28_deploy:
    target: <stack-specific>                     # framer-publish | vercel | wp-host
    dns_handoff_ready: true
    ssl_strategy: <stack-specific>
expected_limitations:                             # per stack — what the adapter SHOULD surface as cannot-do
  - "Framer doesn't support arbitrary CSS at the canvas level"
  - "WordPress requires hosting decision separately"
  # etc.
expected_failure_modes_covered:                  # per stack — what failure paths the adapter handles
  - "API rate limit"
  - "Auth wall on existing-site walks"
```

This is **executable test guidance** — Phase 3 Captains author it alongside the adapter file. A future testing INST wires `tests/run-tests.sh` to check adapter output against `expected.yaml`. For Phase 3 itself, `expected.yaml` is the contract that proves the adapter is complete (manual verification at General review).

### `README.md` (per-stack)

A short orientation file explaining:

- Which adapter file this fixture tests (`adapters/stack-{name}.md`)
- Any setup the test runner needs (API keys for Framer/divmagic? Local Docker for WordPress? Vercel CLI for Next.js?)
- Known platform-specific gotchas the fixture doesn't cover (and where they're documented)
- How to update the fixture when the adapter's contract evolves

## What lives OUTSIDE per-stack subdirectories

- **Shared fixtures** for protocol-level tests (handoff-spec JSON validation, i18n key sync) live at `tests/walkthroughs/` or `tests/` root — not here.
- **Plugin-level tests** (PreToolUse gating, phase-detection) live at `tests/test_pre_tool_use.py`. Not here.
- **Skill-level tests** live alongside their skills (`skills/wb-{group}/tests/`) when authored. Not here.

`tests/adapters/` is **specifically for adapter-output validation**.

## Out-of-scope for Phase 3 itself

The full **test runner integration** (CI hook wiring `tests/run-tests.sh` to load fixtures, invoke adapter phases, diff against `expected.yaml`) is **Phase 5+ scope** per `BUILD-strategy.md`. Phase 3 Captains:

- Author the `fixture/` + `expected.yaml` + `README.md` per their stack
- Run **manual** verification: walk the fixture through pipeline phases 11→27 mentally, confirm the adapter file would produce what `expected.yaml` claims
- Surface gaps in their adapter file (or the fixture) and resolve them before commit

Captains do **not** need to wire the runner. That's a future INST.

## File naming

- Subdirectory names: kebab-case matching adapter file slug (`framer` / `nextjs` / `wordpress`).
- Fixture file names: standard `.website-builder/` conventions (per `DESIGN-project-scaffold.md`).
- `expected.yaml`: exactly that filename.
- `README.md`: exactly that filename.

## How CMS / commerce adapter Captains use this convention (Phase 4+)

Same pattern, different subdirectory. When Phase 4 ships CMS adapter Captains (Decap / Payload), they'll create `tests/cms-adapters/decap/` + `tests/cms-adapters/payload/`. When Phase 4 ships commerce Captains, `tests/commerce-adapters/stripe-checkout/` + etc.

This README only governs `tests/adapters/`. Sibling READMEs at `tests/cms-adapters/README.md` etc. will be authored when those phases begin.

## See also

- `Workstreams/website-builder/BUILD-strategy.md` Phase 3 DoD — the contract this fixture convention satisfies
- `adapters/README.md` — the per-stack adapter contract these fixtures test
- `Workstreams/website-builder/foundation/DESIGN-project-scaffold.md` — `.website-builder/` layout the fixtures mirror
- `Workstreams/website-builder/foundation/DESIGN-content-layers.md` — the 5-layer structure each fixture must contain
- `tests/walkthroughs/` — sibling test surface (end-to-end pipeline dogfood, not per-adapter)
- `tests/run-tests.sh` — current Python test runner (does not yet load adapter fixtures; future INST)
