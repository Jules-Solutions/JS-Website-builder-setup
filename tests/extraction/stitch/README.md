# tests/extraction/stitch/ — Stitch URL → DESIGN.md → import end-to-end fixture

> Tool under test: `extraction/stitch.md` (Phase-3 substrate, extended in place with Phase-5 runtime wiring by Captain N).
>
> The Phase-5 analog of the Phase-3/4 adapter fixtures (`tests/adapters/*/`), but holding an **executable** test (`test_stitch.py`) per `tests/README.md` § "Phase 5 test conventions" — not just data. Verifies the BUILD-strategy DoD line 225 contract: *"Stitch extraction runs from a URL → DESIGN.md import works end-to-end."*

## What this fixture verifies

The end-to-end flow in `extraction/stitch.md` § "Runtime recipe — URL → DESIGN.md → integrated project state" has five steps. The slice this fixture asserts **without a live network** is the load-bearing middle — step 4 ("Normalize"):

```
fixture/stitch-export.md   ← a synthetic Stitch DESIGN.md export (the artifact a
                             Path-1 browser-in-loop run pastes back into the chat)
      │  test_stitch.py :: normalize_stitch_export()   (executable spec of step 4)
      ▼
expected.yaml              ← the normalized project-state shapes the phase-6.5
                             import produces: brand.yaml.tokens (Layer 1),
                             components.yaml (Layer 2), project.yaml voice seed (Layer 5)
```

`test_stitch.py`'s `TestStitchNormalize` parses the export with a **reference normalizer** (the deterministic, side-effect-free spec of what the agent does with reasoning at runtime — mirrors the Phase-1 `detector.py` reference-implementation pattern) and asserts the output equals `expected.yaml` section by section + as a whole document.

It covers:

1. **Brand Identity → voice seed** — name, tagline, voice descriptors → `project.yaml.voice_descriptors` + `voice/exemplars.md`.
2. **Design Tokens → `brand.yaml.tokens`** — colors (key-normalized: `on-surface` → `on_surface`), typography (display + body faces with sizes/weights/line-height), spacing scale, motion, dark-mode strategy.
3. **Components → `components.yaml`** — one entry per recognized component with `extracted: true`, props, and behaviors (`behaviors: none` → `[]`).
4. **Phase-6.5 hand-off invariants** — the discipline step 5 must honor (halt-and-ask on conflicts per decision 36, always-write decision log, cached raw export, reversibility) recorded in `expected.yaml` as presence/shape checks.

## Why this is Tier 1 (no network)

There is **no programmatic surface that extracts a design from an arbitrary external URL** (verified 2026-06-12 — see `extraction/stitch.md` § "Ecosystem verification"). The SDK / community MCPs / Gemini CLI extension all *generate* screens from prompts and fetch assets by screen-id; none do `extract(url)`. So the live-URL crawl (step 2 of the recipe) is **documented procedure, not a network test** — the fixture embodies a representative extraction output and the test asserts the deterministic normalization contract. Always green when fixture + spec align; no upstream dependency to skip on.

A Tier-2 live-Stitch crawl (real browser-in-loop walk, or a programmatic generate-from-prompt round-trip when `STITCH_API_KEY` / a Stitch MCP is configured) is **out of scope** for this fixture per `tests/README.md` § Phase 5 — it would be a skip-when-absent integration test folded into a later phase, not the DoD-line-225 normalization contract.

## What this fixture does NOT cover

Minimal by design. Out of scope (deferred per `tests/README.md` § Phase 5 + BUILD-strategy):

- **Live URL crawl / real Stitch invocation** — Tier-2 integration; no programmatic arbitrary-URL surface exists anyway.
- **Conflict-resolution interaction** — step 5's `AskUserQuestion` halt/merge flow is agent-interactive (phase-6.5 contract); this fixture asserts only that the normalized shapes *enter* that flow correctly. The conflict-resolution behavior itself is exercised by phase-6.5 integration tests (Phase 7-8 cosplay/Ralph scope).
- **Malformed-export recovery** — the failure modes in `extraction/stitch.md` § "Failure modes" (unparseable output, missing sections, mislabeled components) are agent-recovery paths, not normalization-contract assertions.
- **The other 4 extractors** — `divmagic` / `figma-design-to-json` / `ai-output` / `playwright-walk` (Phase 10 scope per decision 55).

## How to update this fixture when the contract evolves

1. **`extraction/stitch.md` § "Output schema" changes** (a new token section, a new destination-table row) → update `fixture/stitch-export.md` to include the new input + `expected.yaml` to assert the new normalized output + extend the reference normalizer in `test_stitch.py`.
2. **The normalization destination table changes** → update `expected.yaml` `normalization_targets` + the per-section expected shapes; `TestStitchFixtureCompleteness::test_normalization_targets_documented` guards that the targets stay enumerated.
3. **Keep it synthetic** — no real brand, no real client, never a real `STITCH_API_KEY` (`secrets-conventions.md`; `test_no_real_secrets_in_fixture` enforces it).

## File map

```
tests/extraction/stitch/
├── README.md                 # this file
├── expected.yaml             # normalized project-state contract (the DoD-line-225 assertion)
├── test_stitch.py            # TestStitchNormalize + TestStitchFixtureCompleteness (Tier 1)
└── fixture/
    └── stitch-export.md      # synthetic Stitch DESIGN.md export (the input artifact)
```

## How to run

```bash
# from plugin root — default 'all' mode runs everything (no -k filter):
./tests/run-tests.sh

# just this fixture:
cd tests && uv run --with pyyaml --with pytest pytest extraction/stitch -v
```

## Cross-references

- `extraction/stitch.md` — the tool under test (§ "Runtime recipe" + § "Output schema" + § "Ecosystem verification")
- `Workstreams/website-builder/extraction/DESIGN-extraction-stitch.md` — the design authority (output format + phase-6.5 integration)
- `phase-contracts/06.5-artifact-ingestion.md` — the import contract the normalized output feeds (8-step flow, conflict policy)
- `tests/README.md` § "Phase 5 test conventions" — the per-Captain code-test landing-zone convention this dir implements
- `tests/adapters/nextjs/` — the Phase-3 fixture/expected.yaml/README convention this mirrors
- `Workstreams/website-builder/BUILD-strategy.md` Phase 5 DoD line 225 — "Stitch extraction runs from a URL → DESIGN.md import works end-to-end"
