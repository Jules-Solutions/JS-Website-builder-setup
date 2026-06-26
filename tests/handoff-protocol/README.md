# tests/handoff-protocol/ — JSON handoff protocol round-trip fixture

> Tool under test: the **JSON handoff protocol** (Phase 6 / Captain R scope) — `spec/component-request-v1.json` (the machine-validatable request schema), the 7 adapter fixtures under `handoff-spec/adapter-fixtures/`, and the bidirectional brief↔output round-trip.
>
> The Phase-6 analog of the Phase-5 Stitch fixture (`tests/extraction/stitch/`), holding an **executable** test (`test_handoff_protocol.py`) per `tests/README.md` § "Phase 5 test conventions" — not just data. Verifies the BUILD-strategy Phase 6 DoD (line 253): *"Handoff protocol round-trips: agent emits brief → AI tool produces output → agent re-imports cleanly on ≥3 of the 6 AI-tool fixtures."*

## What this verifies

Three DoD contracts, each fixture-validated (no network — the protocol is explicit manual copy-paste per `DESIGN-handoff-protocol.md` § "What this protocol is NOT"):

```
spec/component-request-v1.json
      │  (a) MiniSchemaValidator.check_schema()   → well-formed Draft-2020-12
      ▼
handoff-spec/adapter-fixtures/samples/*-brief.json
      │  (b) MiniSchemaValidator.validate(brief)  → each of 7 briefs valid
      ▼
handoff-spec/adapter-fixtures/samples/*-output.tsx
      │  (c) ingest_output(output, filename, briefs) → round-trip on 3/6
      ▼
{ bound_brief_id, component_name, props, palette_drift, on_brand }
```

- **(a) Schema well-formedness** — `TestSchemaWellFormed`. A stdlib reference validator (`MiniSchemaValidator`) walks the schema and raises on any malformed node, unknown keyword, unresolved `$ref`, or invalid regex. Also asserts the required top-level keys match the markdown contract block-by-block (SSOT: `handoff-spec/component-request-v1.md` line 38) and the `subject.kind` + `output_format.*` enums are present.
- **(b) Brief validity** — `TestSampleBriefsValidate`. All 7 sample briefs (6 AI tools + human-freelancer) validate against the schema. Plus two cross-field doctrine invariants the schema can't express (`iteration == len(iteration_history)`; `id` is colon-free + Z-suffixed).
- **(c) Round-trip ingestion** — `TestRoundTripIngestion`. The `ingest_output` reference implements the phase-6.5 AI-output-parser contract (`handoff-spec/component-output-v1.md` § "What the parser does"): identify modality → strip fences/prose → bind to brief → extract component name + props → palette-validate. Run on **3 of the 6 AI-tool fixtures** (≥3 DoD bar):

  | Fixture | Modality | Binds by | Brand verdict | Exercises |
  |---|---|---|---|---|
  | **ChatGPT** | Form 1 (fenced + prose) | filename = brief id | drift caught (`bg-indigo-600`) | fence/prose strip, palette validator flags non-brand token, round-2 seed |
  | **Claude.ai** | Form 2 (metadata header) | `brief_id` in `/* */` header | on-brand | metadata-header bind, header stripped from code, all-OKLCH on-brand |
  | **v0** | Form 1 (pure code) | filename = brief id | on-brand | shadcn CSS-variable token refs recognised as on-brand (not raw-palette drift) |

  Cursor / Lovable / Bolt.new ship sample briefs (covered by (b)) + sample outputs for completeness, but the round-trip *assertions* run on the three above per the ≥3-of-6 bar.

## Why this is Tier 1 (no network)

The protocol is **explicitly manual copy-paste** — there is no MCP / API integration with the external tools (`DESIGN-handoff-protocol.md` § "What this protocol is NOT": *"the user manually copies + pastes"*). So a "live ChatGPT/v0 round-trip" is not a thing to network-test; the fixtures embody representative external-tool outputs and the test asserts the deterministic ingestion contract. Always green when fixtures + spec align; no upstream dependency to skip on. Mirrors the Phase-1 `detector.py` + Phase-5 `test_stitch.py` reference-implementation pattern.

## Why stdlib-only (no `jsonschema` dependency)

The test harness ships exactly `pytest` + `pyyaml` (`tests/pyproject.toml`; `run-tests.sh` runs `uv run --with pyyaml --with pytest pytest`). Rather than add a `jsonschema` dependency — which would force an edit to `pyproject.toml` / `uv.lock` / the shared `run-tests.sh` `--with` list (a shared-substrate race per `tests/README.md` § Phase 5) — this test embeds a **stdlib-only `MiniSchemaValidator`** covering exactly the Draft-2020-12 keyword subset `spec/component-request-v1.json` uses. This is the same discipline as the Stitch precedent's stdlib reference normalizer: hermetic, collision-free, zero dependency churn for the General's merge. `MiniSchemaValidator` is conservative — it flags any schema keyword outside its known set, so it can never silently under-enforce.

## What this fixture does NOT cover

Minimal by design. Out of scope (deferred):

- **Live external-tool invocation** — no programmatic surface exists (manual copy-paste protocol); a live round-trip is not network-testable.
- **The full phase-6.5 conflict-resolution flow** — the `AskUserQuestion` halt/merge on token/component/string/page conflict (locked decision 36) is agent-interactive; this fixture asserts only that ingestion produces the normalized result + drift verdict that *enters* that flow. The interactive resolution is Phase 7-8 cosplay/Ralph scope.
- **Writing to real project state** — `ingest_output` returns the normalized result; it does not write `components.yaml` / `brand.yaml` / the user's project files (that's the agent's job at runtime, exercised by phase-6.5 integration tests).
- **Cursor / Lovable / Bolt.new round-trip assertions** — their sample briefs are validated; their outputs ship for completeness but the ≥3 round-trip bar is met by ChatGPT / Claude.ai / v0.
- **AST-grade parsing** — `ingest_output` uses the same light regex extraction the agent does with reasoning at runtime, not a full TS parser.

## How to update this fixture when the contract evolves

1. **`spec/component-request-v1.json` adds a keyword** → if it's outside `MiniSchemaValidator`'s known set, extend `_KNOWN_KEYWORDS` + the validator (the well-formedness check will fail loudly until you do — that's the drift guard).
2. **A new block / required key** → update the brief samples + `TestSchemaWellFormed::test_schema_required_top_level_keys_match_contract`.
3. **A new round-trip modality / form** → add a sample output + a `TestRoundTripIngestion` case + extend `ingest_output`'s modality detection.
4. **Keep it synthetic** — no real brand, no real client, never a real API key (`secrets-conventions.md`; `test_no_real_secrets_in_samples` enforces it).

## File map

```
tests/handoff-protocol/
├── README.md                  # this file
└── test_handoff_protocol.py   # MiniSchemaValidator + ingest_output + 4 test classes (Tier 1)
```

The fixtures themselves live with the plugin substrate (one source of truth, referenced by both the docs and these tests):

```
spec/component-request-v1.json                        # the schema under test
handoff-spec/adapter-fixtures/{chatgpt,claude-ai,v0,cursor,lovable,bolt-new,human-freelancer}.md
handoff-spec/adapter-fixtures/samples/*-brief.json    # 7 sample briefs
handoff-spec/adapter-fixtures/samples/*-output.tsx    # 5 sample outputs (3 asserted in round-trip)
```

## How to run

```bash
# from plugin root — default 'all' mode runs everything (no -k filter):
./tests/run-tests.sh

# just this fixture:
cd tests && uv run --with pyyaml --with pytest pytest handoff-protocol -v
```

## Cross-references

- `spec/component-request-v1.json` — the schema under test
- `handoff-spec/component-request-v1.md` — the human-readable block-by-block SSOT the schema realises
- `handoff-spec/component-output-v1.md` — the permissive return contract (Form 1 / 2 / 3) `ingest_output` implements
- `handoff-spec/adapter-fixtures/` — the 7 per-tool fixtures + their sample brief/output pairs
- `extraction/ai-output.md` — the phase-6.5 parser `ingest_output` is the executable reference of
- `Workstreams/website-builder/cross-cutting/DESIGN-handoff-protocol.md` — the design authority (both flows, fixture shape, failure modes)
- `tests/README.md` § "Phase 5 test conventions" — the per-Captain code-test landing-zone convention this dir follows
- `tests/extraction/stitch/` — the Phase-5 fixture/reference-impl precedent this mirrors
- `Workstreams/website-builder/BUILD-strategy.md` Phase 6 DoD line 253 — the round-trip contract
```
