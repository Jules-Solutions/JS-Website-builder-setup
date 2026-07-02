# Extraction — divmagic

> Element-precision + page-level extraction with a programmatic HTTP API. **Expansion path beyond MVP** (per locked decision 55 + phase-6.5 contract — Stitch is MVP-primary; divmagic is the peer for cases Stitch can't address). **Stack-agnostic** output.
>
> Anchor: `DESIGN-ingestion-and-extraction.md` §"divmagic API (element + page level)" (lines 164-172).
> External: https://divmagic.com

## What it does

divmagic offers element-level + page-level extraction with a clean HTTP API. Two surfaces:

- **Element-precision** — target specific DOM elements on a URL (e.g. "extract just the hero from this site, not the whole design system") and get back its CSS, HTML, computed styles, spacing data.
- **Page-level** — full-page extraction with element-tree breakdown.

The defining strength vs Stitch: **programmatic, deterministic, scoped**. Stitch is AI-driven and infers a design system holistically; divmagic gives you a specific element with surgical precision. Use divmagic when the user wants *this exact card pattern* from *that exact site* without dragging in the whole system.

## When the agent invokes it

divmagic is the **expansion-phase-10 path** (post-MVP). Reasons to choose it over Stitch:

- **Phase 18 (component build)** — the user has a specific reference: *"build my hero like https://stripe.com/customers — extract just their hero block."* divmagic extracts the targeted element; agent integrates the shape into `components.yaml`.
- **Phase 6.5 element-precision invocation** — user says *"don't redesign my site; just grab the pricing table from that competitor."* divmagic targets the specific component.
- **Token validation** — agent uses divmagic to compare a reference site's computed primary color against the project's `brand.yaml` (catches drift).

For full design-system extraction at session start (entry mode `has-existing-site`), Stitch remains primary. divmagic is the surgical tool, not the broad-spectrum one.

**MVP runtime support:** the v1 plugin documents divmagic but doesn't deeply wire it. The agent surfaces divmagic as an option when the user names element-precision needs; otherwise routes to Stitch. Full divmagic wiring lands in an expansion phase.

## Invocation path

divmagic exposes a REST API. Authentication via API key in `keys.yaml` (free tier exists as fetch-on-demand per `DESIGN-ingestion-and-extraction.md` line 169).

### Authentication

API key in 1Password (per `secrets-conventions.md`), pulled into env at session start as `DIVMAGIC_API_KEY`. Never hardcoded.

### Example invocation (subject to API verification via context7 at phase 6.5)

```bash
# Element extraction
curl -s "https://api.divmagic.com/v1/extract" \
  -H "Authorization: Bearer $DIVMAGIC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://stripe.com/customers",
    "selector": "section.hero",
    "include": ["css", "html", "computed_styles", "spacing"]
  }' \
  | tee .website-builder/outputs/divmagic-{ts}.json
```

```bash
# Page-level extraction
curl -s "https://api.divmagic.com/v1/page" \
  -H "Authorization: Bearer $DIVMAGIC_API_KEY" \
  -d '{ "url": "https://example.com" }' \
  | tee .website-builder/outputs/divmagic-page-{ts}.json
```

Agent invokes context7 (`/divmagic/divmagic` if listed) or WebFetch https://divmagic.com/docs at phase 6.5 to confirm current API surface — divmagic evolves; verify before invoking.

## Output schema

JSON. Approximate shape (verify per current divmagic docs):

```json
{
  "url": "https://stripe.com/customers",
  "selector": "section.hero",
  "extracted": {
    "html": "<section class=\"hero\">...</section>",
    "css": {
      "background-color": "rgb(99, 91, 255)",
      "padding": "120px 24px",
      "font-family": "...",
      "..."
    },
    "computed_styles": { "...": "..." },
    "spacing": {
      "padding_top_px": 120,
      "padding_inline_start_px": 24,
      "..."
    },
    "children": [ /* nested element tree */ ]
  },
  "screenshot_url": "..."
}
```

Agent normalizes:

| divmagic output | website-builder destination |
|---|---|
| `extracted.html` | Reference shape; the agent re-implements in user's stack (does NOT copy verbatim — license + brand discipline) |
| `extracted.css` colors | Candidate tokens for `brand.yaml.tokens.colors` (with user confirmation per phase-6.5 conflict protocol) |
| `extracted.css` typography | Candidate `brand.yaml.tokens.typography` |
| `extracted.spacing` | Cross-check against `brand.yaml.tokens.spacing` for drift |
| Element shape | Candidate `components.yaml` entry — props inferred from divmagic's child tree |

**Critical discipline:** divmagic-extracted HTML is reference material, NOT verbatim-copied. Copying a competitor's design literally is a brand + legal failure. The agent extracts the *shape* + *patterns* + *token values*, then re-implements per the user's brand.

## Configuration

```yaml
# project.yaml
extraction:
  divmagic:
    enabled: false   # MVP default; opt-in
    api_key_env: DIVMAGIC_API_KEY
    free_tier_only: true   # if user hasn't paid, agent surfaces tier limits
```

## Failure modes

| Failure | Cause | Recovery |
|---|---|---|
| API 401 / 403 | API key missing / invalid | Verify `DIVMAGIC_API_KEY` set; check 1Password entry; check tier limits |
| API 429 | Rate-limited (free tier) | Cache previous output; surface "free tier reached — upgrade to continue / wait" |
| Selector returns empty | Target element doesn't exist on the URL | Agent retries with broader selector OR falls back to Stitch page-level extraction |
| Extracted CSS contains brand-coupled colors | Reference site has tokens specific to its brand | Agent surfaces "these tokens come from $REF_SITE's brand — drift from your `brand.yaml`; recommend mapping not copying" |
| Output unparseable | API changed / new fields | Re-run context7 / WebFetch on divmagic docs; update normalization |

## Quality discipline

- **divmagic is reference-extraction, not blueprint copying.** Always re-implement in user's brand context.
- **Cache outputs** at `.website-builder/outputs/divmagic-{ts}.json` for audit.
- **Log invocations** in `.website-builder/decisions/ingest-{ts}.md` per phase-6.5 schema (`extractor: divmagic`).
- **Pair with screenshot** when possible — visual reference makes the "extract pattern not pixels" discipline obvious to the user.

## See also

- `DESIGN-ingestion-and-extraction.md` §"divmagic API" — design-doc anchor
- `phase-contracts/06.5-artifact-ingestion.md` — invocation contract
- `extraction/stitch.md` — MVP-primary peer; choose Stitch for broad design-system extraction
- `extraction/playwright-walk.md` — walker pairing for dynamic state
- https://divmagic.com — official site
