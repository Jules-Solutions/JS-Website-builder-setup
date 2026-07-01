# Extraction — Google Stitch

> AI-driven extraction of a design system from any URL or screenshot into a portable open-spec DESIGN.md (color palette, type scale, spacing, component-shape recognition). **MVP-primary extraction tool per locked decision 55** of the website-builder workstream. **Stack-agnostic** — adapters consume the normalized output identically.
>
> Anchor: `DESIGN-ingestion-and-extraction.md` §"Google Stitch (primary URL extractor)" (lines 126-162) + `phase-contracts/06.5-artifact-ingestion.md`.
> External: https://stitch.withgoogle.com
>
> **Phase-5 runtime wiring (2026-06-12):** extended with the end-to-end agent-executable recipe (§ "Runtime recipe — URL → DESIGN.md → integrated project state"), the verified ecosystem state of every invocation path (§ "Two invocation paths" + § "Ecosystem verification"), and the load-bearing finding that no programmatic surface does arbitrary-URL extraction. End-to-end asserted by `tests/extraction/stitch/`.

## What it does

Stitch takes one of:

- **A URL** to a deployed site → walks the visible design surface
- **A screenshot** → vibe-extracts design tokens + component shapes
- **A natural-language prompt** → generates a design system from voice cues

…and produces a portable, AI-readable spec containing:

- Brand identity (name + voice descriptors, inferred)
- Design tokens: color palette (oklch), type scale, spacing scale, motion, dark-mode
- Component shape recognition: hero, nav, card, grid, list, form, footer, etc.

The output format is Stitch's own `DESIGN.md` schema — see "Output schema" below.

## When the agent invokes it

Stitch is the **MVP-primary path for URL/site/screenshot extraction**. The agent reaches for Stitch in:

- **Entry mode `has-existing-site`** — user has a deployed site to migrate (most common phase-6.5 trigger at session start).
- **Entry mode `has-Framer-attempt`** — partial Framer/Webflow/Wix project; Stitch walks the deployed preview.
- **Entry mode `has-ai-output`** — when the AI output is provided as a URL (rare; typically pasted code instead → AI-output parser).
- **User explicit invocation** at any phase: *"extract the design system from https://example.com"*.
- **Phase 17 (design system)** — the agent can use Stitch to seed initial palette + typography options when the user provides reference URLs/screenshots.

Stitch is paired with **Playwright walker** when the target site has dynamic state (hover effects, mobile-emulation variants, auth-walled content) Stitch's static URL crawl misses. See `extraction/playwright-walk.md`.

## Two invocation paths (per phase-6.5 contract)

> **Ecosystem state — verified 2026-06-12** (fresh context7 re-resolve + WebSearch + repo checks; see § "Ecosystem verification" at the foot of this doc for the full audit). Stitch now ships an official SDK, an official Gemini CLI extension, and multiple maintained community MCP servers. **But none of them extract a design from an arbitrary external URL** — they generate UI screens from prompts and fetch the HTML/screenshot of screens that already live inside a Stitch project (by project-id / screen-id). The website-builder's actual `has-existing-site` job — *point at a deployed site I don't control and get its design system back* — is a capability of the **Stitch web tool only**. That makes Path 1 (browser-in-loop) the MVP-primary path **by necessity, not merely friction-avoidance**: Path 2's programmatic surfaces don't do arbitrary-URL extraction. Path 2 earns its keep for the *generate-from-prompt / seed-a-design* use cases (phase 17 design-system seeding from a voice/adjective prompt) — not for migrating an existing third-party site.

### Path 1 — Browser-in-loop (MVP-primary; the only arbitrary-URL extraction path)

The Stitch web UI at https://stitch.withgoogle.com is the canonical surface for arbitrary-URL / screenshot extraction. The MVP flow, as the agent executes it:

1. **Agent formulates and surfaces the walk-through.** Per the Stitch Agent Protocol (`/llmstxt/...stitch...llms_txt`, verified 2026-06-12), Stitch's web tool is vibe-prompt-driven (3-layer prompt: Anatomy / Vibe / Content). For a *URL extraction* the agent tells the user precisely: *"Open https://stitch.withgoogle.com, sign in with a Google account, paste your URL (or upload a screenshot, or describe the design in words), let Stitch generate the design, then use its DESIGN.md / HTML export and paste that back here."*
2. **User pastes the export back** into the chat (or saves it to `.website-builder/outputs/stitch-{ts}.md`, which the phase-6.5 "detected file in outputs/" route picks up).
3. **Agent caches + normalizes.** Agent saves the raw export to `.website-builder/outputs/stitch-{ts}.md` (audit trail) and runs the normalization in § "Output schema" → `brand.yaml.tokens` + `components.yaml`, then hands off to the phase-6.5 conflict-resolution flow.

The user-in-loop step is the cost of arbitrary-URL fidelity; Stitch's web UI produces the highest-quality output and is the only surface that reads a site the user doesn't own.

### Path 2 — SDK / Gemini CLI / MCP (programmatic; generate-and-fetch, NOT arbitrary-URL extraction)

These paths exist and are maintained as of 2026-06-12, but their shape is **generate-a-screen-then-fetch-its-assets**, keyed by project-id / screen-id — there is no `extract(url)` primitive in any of them. Use them when the task is *generate a design from a prompt* (phase-17 seeding) or *round-trip a Stitch-hosted project*, and when the runtime has the key/extension configured. The agent checks for `STITCH_API_KEY` / a Stitch MCP / the Gemini extension at phase-6.5 entry; **absence → Path 1; presence → Path 2 is available for the generate-from-prompt sub-case only.**

**SDK — `@google/stitch-sdk`** (`/google-labs-code/stitch-sdk`, verified 2026-06-12). TypeScript/Node. `STITCH_API_KEY` env (pulled via `secrets-conventions.md` from 1Password — never hardcode):

```typescript
import { stitch } from "@google/stitch-sdk";       // npm install @google/stitch-sdk
// STITCH_API_KEY must be set in the environment
const project = await stitch.createProject("My App");
const screen   = await project.generate("A login page with email and password fields");
const htmlUrl  = await screen.getHtml();   // download URL → fetch() → HTML text
const imageUrl = await screen.getImage();  // download URL → screenshot
```

Note: `generate()` takes a *prompt*, not a URL. The HTML it returns is of the screen Stitch *generated*, which the agent then feeds through the same § "Output schema" normalization.

**Gemini CLI extension** (`/gemini-cli-extensions/stitch`, verified 2026-06-12) — install once, drive from inside Gemini CLI:

```bash
gemini extensions install https://github.com/gemini-cli-extensions/stitch --auto-update
# then, inside Gemini CLI:
#   /stitch Design a modern e-commerce checkout page        # generate (Gemini 3 Flash default; "...using Gemini 3 Pro" for higher quality)
#   /stitch Download the HTML of screen <screen-id>          # → ./screen_<id>.html (full doc + Tailwind CDN config)
#   /stitch Download the image of screen <screen-id>         # → ./screen_<id>.png
```

**Community MCP servers** (verified maintained 2026-06-12) — use whichever the user already has configured:
- `@_davideast/stitch-mcp` (`npx @_davideast/stitch-mcp proxy`; npm updated Mar 2026; benchmark 85.5) — CLI + MCP; tools `build_site` / `get_screen_code` / `get_screen_image`; local Vite preview + Astro site builder. Auth: `STITCH_API_KEY` or `STITCH_USE_SYSTEM_GCLOUD=1` or guided `init` OAuth.
- `obinnaokechukwu/stitch-mcp` (Go proxy; published Feb 2026) — resilient screen generation with gcloud auth/token-refresh + connection-drop recovery.

Per locked decision 23 (pin/verify at runtime), re-confirm the current surface via context7 at phase-6.5 invocation if cached findings are >30 days old — Stitch and its ecosystem evolve; training data is stale.

## Output schema (Stitch DESIGN.md)

Stitch emits markdown with a predictable structure (verbatim from `DESIGN-ingestion-and-extraction.md`):

```markdown
# DESIGN.md
## Brand Identity
**Name:** [extracted]
**Voice:** [extracted/inferred]

## Design Tokens
### Colors
- primary: oklch(...)
- secondary: oklch(...)
- neutral_900: oklch(...)
- semantic_error: oklch(...)
- ...

### Typography
- display: [font-family]
- body: [font-family]
- scale:
  - h1: { size: ..., lh: ..., weight: ... }
  - h2: { ... }
  - body: { ... }

### Spacing
- base_unit: ...
- scale: [...]

### Motion
- duration_med: ...
- easing_default: ...

### Dark Mode
- strategy: auto | manual | none

## Components
### Hero
- [recognized props + behaviors]
### Nav
- [...]
### Card
- [...]
...
```

Agent normalizes into:

| Stitch section | website-builder destination |
|---|---|
| Brand Identity → Voice | `project.yaml.voice_descriptors` + `voice/exemplars.md` (Layer 5 seed) |
| Design Tokens → Colors | `brand.yaml.tokens.colors` (Layer 1) |
| Design Tokens → Typography | `brand.yaml.tokens.typography` (Layer 1) |
| Design Tokens → Spacing | `brand.yaml.tokens.spacing` (Layer 1) |
| Design Tokens → Motion | `brand.yaml.tokens.motion` (Layer 1) |
| Design Tokens → Dark Mode | `brand.yaml.tokens.dark_mode` (Layer 1) |
| Components → Hero / Nav / etc. | `components.yaml` (Layer 2) — one entry per recognized component |

The normalization is the agent's responsibility — Stitch produces semi-structured markdown; the agent maps it onto YAML. Conflict-resolution (incoming vs existing) follows the phase-6.5 protocol.

## Runtime recipe — URL → DESIGN.md → integrated project state (the end-to-end flow)

This is the concrete, agent-executable sequence Phase 5 wires together: *user has a URL → run Stitch extraction → DESIGN.md lands in the project → phase-6.5 import integrates it.* It is the Stitch-specific instantiation of the 8-step phase-6.5 flow in `phase-contracts/06.5-artifact-ingestion.md` — read that contract for the full conflict-resolution discipline; this recipe is the Stitch entry path into it. The end-to-end is verified by the test fixture at `tests/extraction/stitch/` (a recorded DESIGN.md export → `expected.yaml` normalized state, asserting steps 4-5 below without any live network).

**Step 0 — Decide the path.** At phase-6.5 entry the agent checks `project.yaml.extraction.stitch.prefer` + whether `STITCH_API_KEY` / a Stitch MCP / the Gemini CLI extension is present. For the canonical `has-existing-site` job (extract an arbitrary deployed URL) the answer is **always Path 1 / browser-in-loop** — no programmatic surface extracts arbitrary URLs (§ invocation paths). Path 2 is selected only for a generate-from-prompt sub-case (e.g. phase-17 seeding from voice/adjective cues).

**Step 1 — Capture the URL.** The user supplies the deployed URL (entry mode `has-existing-site` / `has-Framer-attempt`, or an explicit "extract the design from https://…" at any phase). The agent records it in `.website-builder/inbox/` for provenance before extraction.

**Step 2 — Run the extraction.**
- *Path 1 (primary):* the agent surfaces the browser-in-loop walk-through (§ Path 1). User runs Stitch at https://stitch.withgoogle.com against the URL, copies the DESIGN.md / HTML export, pastes it back (or drops it into `.website-builder/outputs/`).
- *Path 2 (generate sub-case only):* the agent calls the SDK / MCP / Gemini CLI to generate from a prompt and fetch the HTML — same downstream normalization.
- *Dynamic-state pairing:* if `pair_with_playwright` fires (hover/scroll/auth-walled state Stitch's static crawl misses), the Playwright walker (`extraction/playwright-walk.md`) captures per-state screenshots first; those feed Stitch's screenshot mode. Auth-walled sites: Playwright authenticates with user-supplied creds, captures, hands screenshots to Stitch.

**Step 3 — Land the raw export (the "DESIGN.md lands in the project" moment).** The agent writes the verbatim Stitch output to `.website-builder/outputs/stitch-{ts}.md`. This is the auditable artifact (§ Quality discipline); re-extractions are diffable against prior ones.

**Step 4 — Normalize.** The agent parses the DESIGN.md per § "Output schema" and maps each section onto project-state shapes via the destination table above: `Design Tokens → brand.yaml.tokens.{colors,typography,spacing,motion,dark_mode}` (Layer 1); `Brand Identity → Voice → project.yaml.voice_descriptors` + `voice/exemplars.md`; `Components → components.yaml` (Layer 2, one entry per recognized component, `extracted: true`). This is the input→output contract the test fixture asserts.

**Step 5 — Hand off to phase-6.5 import (the "integrate it" moment).** The normalized shapes enter the phase-6.5 conflict-resolution flow (steps 4-8 of `06.5-artifact-ingestion.md`):
- The agent detects conflicts against existing project state (incoming `primary` ≠ existing `primary`, incoming `Hero` shape ≠ existing).
- Every conflict **halts** and surfaces via `AskUserQuestion` with keep-current / use-incoming / merge options + per-option cost (locked decision 36 — no silent overwrite, no silent merge).
- Non-conflicting changes + user-resolved conflicts are applied to `brand.yaml` / `components.yaml` / etc.
- Cross-layer validation re-runs (token refs resolve, components exist).
- A `decisions/ingest-{ts}.md` log is **always** written (even zero-conflict), making the integration reversible.
- The agent resumes the recorded `return_phase` (mid-project re-run) or advances to phase 7 (entry-time onboarding route).

**Result:** the user's deployed-site design is now structured project state — design tokens in `brand.yaml`, component shapes in `components.yaml`, voice seed in `voice/exemplars.md` — with a full audit trail and zero prior work lost. The whole flow is re-runnable: re-extract the same URL later and step 5 diffs against the prior `decisions/ingest-*.md`.

## Configuration

```yaml
# project.yaml
extraction:
  stitch:
    enabled: true
    api_key_env: STITCH_API_KEY   # path 2 only (SDK/MCP/Gemini-CLI); ignored on path 1 (browser-in-loop)
    pair_with_playwright: auto    # auto | always | never
    prefer: browser-in-loop       # browser-in-loop | programmatic. Default browser-in-loop:
                                  #   the only path that does arbitrary-URL extraction (see § invocation paths).
                                  #   `programmatic` is honored only for generate-from-prompt sub-cases (phase-17 seeding).
```

`api_key_env` names the env var the SDK / MCP / Gemini-CLI paths read; it is resolved through `keys.yaml` → 1Password / `.env` per `cross-cutting/DESIGN-secrets-and-keys.md` and the Captain-Q resolver — **never hardcode `STITCH_API_KEY`** (`secrets-conventions.md`). On Path 1 the key is unused.

`pair_with_playwright: auto` triggers a Playwright walk when Stitch's URL crawl is suspected to miss dynamic state (heuristic: site has reported hover states, scroll-triggered animations, or auth wall).

## Failure modes

| Failure | Cause | Recovery |
|---|---|---|
| Stitch output incomplete (missing sections) | Site's design system is sparse / inconsistent | Agent flags gaps; falls back to manual phase-17 design-system option generation |
| Tokens don't match site reality (visible drift) | Stitch hallucinated values | Agent surfaces drift via screenshot comparison; user picks corrected values |
| Components mis-identified (e.g. "Card" labeled "Hero") | Vibe-detection error | Agent surfaces per-component review at phase 17 / 18 ingestion gate |
| Output unparseable (free-form prose instead of structured markdown) | Stitch produced wrong format | Agent asks user to re-run Stitch with the "DESIGN.md export" option explicitly |
| URL extraction fails entirely (Stitch returns nothing) | Site is JS-heavy SPA without server-rendered content | Switch to Playwright walker → screenshot → Stitch screenshot mode |
| Auth-walled site | Stitch can't reach private content | Use Playwright walker with user-supplied auth; capture screenshots; pass screenshots to Stitch |

## Quality discipline

- **Always pair Stitch output with user review** before applying — token conflicts halt per phase-6.5 protocol.
- **Cache the raw Stitch output** at `.website-builder/outputs/stitch-{ts}.md` so re-extractions are auditable.
- **Log the ingestion** in `.website-builder/decisions/ingest-{ts}.md` per phase-6.5 schema.
- **Re-fetch context7 / WebFetch** on `https://stitch.withgoogle.com` if cached docs are >30 days old (Stitch capabilities continue to evolve).

## Ecosystem verification (audit log — re-verify when stale)

> Recorded so future agents don't redo these searches (Phase 3/4 precedent: positive AND negative findings documented). **Verified 2026-06-12** via fresh context7 re-resolve (`Google Stitch`, not copy-pasted IDs) + WebSearch + repo README checks. Re-verify per locked decision 23 if >30 days stale.

**Positive findings — these programmatic surfaces exist and are maintained:**

| Surface | ID / install | Shape | State (2026-06-12) |
|---|---|---|---|
| Official SDK | `@google/stitch-sdk` · `/google-labs-code/stitch-sdk` (103 snippets, benchmark 79) | `createProject` → `generate(prompt)` → `getHtml()` / `getImage()`; `STITCH_API_KEY` env | Maintained (google-labs-code) |
| Gemini CLI extension | `/gemini-cli-extensions/stitch` (benchmark 77) · `gemini extensions install …/gemini-cli-extensions/stitch` | `/stitch <prompt>` generate (Gemini 3 Flash/Pro) + download HTML/image by screen-id | Maintained (official) |
| Community MCP — davideast | `@_davideast/stitch-mcp` · `npx @_davideast/stitch-mcp proxy` (benchmark 85.5) | CLI + MCP; tools `build_site` / `get_screen_code` / `get_screen_image`; Vite preview + Astro builder; auth via `STITCH_API_KEY` / `STITCH_USE_SYSTEM_GCLOUD=1` / guided `init` OAuth | Maintained (npm updated Mar 2026) |
| Community MCP — obinnaokechukwu | `/obinnaokechukwu/stitch-mcp` (Go, benchmark 85.5) | Go proxy; resilient screen generation; gcloud auth/token-refresh + connection-drop recovery | Maintained (published Feb 2026) |
| Newer entrants (noted, not pinned) | `oogleyskr/stitch-mcp-server` (25-tool combined: design/analysis/export/proxy), `piyushcreates/stitch-mcp` (transparent proxy) | Various | Present 2026-06-12; not evaluated in depth |
| Web tool (canonical) | https://stitch.withgoogle.com · `/llmstxt/…stitch…llms_txt` (High reputation) | Vibe-driven generation, 3-layer prompt (Anatomy/Vibe/Content), Agent Protocol directs agent to formulate a vibe-prompt for the user | Live (Google Labs experimental) |

**Negative finding (load-bearing — do not re-litigate):** **No programmatic surface (SDK, any community MCP, or the Gemini CLI extension) extracts a design from an arbitrary external URL the user does not control.** They all operate on screens *generated inside* a Stitch project, keyed by project-id / screen-id — `generate(prompt)`, not `extract(url)`. The website-builder's `has-existing-site` job (read a deployed third-party site → DESIGN.md) is therefore a **Stitch web-tool-only** capability → **Path 1 / browser-in-loop is MVP-primary by necessity, not just friction-avoidance.** Path 2's value is the generate-from-prompt sub-case (phase-17 seeding), not third-party-site migration. A future agent tempted to "just call the SDK on the URL" should stop here — that primitive does not exist.

## See also

- `DESIGN-ingestion-and-extraction.md` — full extraction model
- `phase-contracts/06.5-artifact-ingestion.md` — invocation contract + 8-step flow
- `extraction/divmagic.md` — element-precision peer for targeted extracts
- `extraction/playwright-walk.md` — paired walker for dynamic-state sites
- `extraction/ai-output.md` — code-based artifact ingestion (different path)
- `handoff-spec/component-output-v1.md` — JSON-handoff round-trip uses the AI-output parser, not Stitch
- https://stitch.withgoogle.com — official site
