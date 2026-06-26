---
name: wb-content-foundation
description: This skill should be used when the website-builder pipeline reaches the content-foundation phases — when the user wants to "dump everything I have", "capture my content", "I have a Google doc / Notion / old site / testimonials", "ingest this" / "I have a new artifact" / "I generated this in ChatGPT" / "integrate this v0 output" (re-runnable phase 6.5), "audit my photos", "check the rights on these images", "plan the images / image strategy", "what images does the site need", or "build the sitemap" / "what pages should the site have". Drives phases 6 (wild content capture), 6.5 (artifact ingestion — re-runnable, fires at ANY lifecycle point), 7 (media asset audit), 8 (image strategy), and 9 (sitemap).
version: 0.1.0
---

# wb-content-foundation — Content-Foundation Phases (6 → 6.5 → 7 → 8 → 9)

> The content-foundation skill. Capture everything the user has (phase 6), fold in external artifacts without losing prior work (phase 6.5, re-runnable), separate what-they-have from what-they-can-ship (phase 7), turn that into a complete sourcing plan (phase 8), and lock the structural skeleton (phase 9). The freelancer agent profile is always loaded; this skill layers on top when the project enters this phase range — and phase 6.5 can be active simultaneously with any other phase.
>
> **Design-doc primacy.** This skill points at design docs and phase contracts; it does not paraphrase them. The phase contracts are the substantive instruction set — read the one for the active phase verbatim before executing it.

## What this skill does

Five phases, one discipline arc: **capture greedily → ingest safely → audit honestly → plan completely → structure ruthlessly.**

| Phase | Name | Re-runnable | The discipline |
|---|---|---|---|
| 6 | Wild content capture | no | Capture is greedy — refuse only silent capture-completion without user confirmation |
| 6.5 | Artifact ingestion | **yes** | No silent overwrite, no silent merge — every conflict halts and forces a user decision |
| 7 | Media / asset audit | no | Surface copyright risk loudly — no shipping unprovenanced images |
| 8 | Image strategy | no | Every planned image has a real sourcing method — no placeholder ships |
| 9 | Sitemap | no | Every page earns its existence against the phase-3 conversion |

Phase 6.5 is unique: **it is the only re-runnable phase**, it fires on demand at *any* project lifecycle point (not just here), and its defining behavior is conflict protection. Mom's canonical pattern — at phase 18 she generates a section in ChatGPT, pastes it back, 6.5 ingests it into existing state with no prior work lost, the project resumes at phase 18 — is the load-bearing use case the whole re-runnability design exists for.

## Phase pointer pattern — read the contract for the active phase

For each phase, read its contract verbatim before acting. The contract owns Mission / Entry / Exit / Gating / Tools / Outputs / Common failures. This skill says *how to execute it well*; the contract says *what the contract is*.

| Active phase | Read this contract first | This skill's execution help |
|---|---|---|
| 6 | `${CLAUDE_PLUGIN_ROOT}/phase-contracts/06-wild-content-capture.md` | Elicitation routine + fresh-generation prompts → `references/capture-elicitation.md` |
| 6.5 | `${CLAUDE_PLUGIN_ROOT}/phase-contracts/06.5-artifact-ingestion.md` | 8-step flow + extractor selection + conflict resolution → `references/ingestion-conflict-resolution.md` |
| 7 | `${CLAUDE_PLUGIN_ROOT}/phase-contracts/07-media-asset-audit.md` | Rights/quality/brand-fit verdict playbook → `references/asset-audit-rights.md` |
| 8 | `${CLAUDE_PLUGIN_ROOT}/phase-contracts/08-image-strategy.md` | Sourcing decision + AI-path selection + brief recipes → `references/image-strategy-briefs.md` |
| 9 | `${CLAUDE_PLUGIN_ROOT}/phase-contracts/09-sitemap.md` | Conversion-test challenge patterns → `references/sitemap-conversion-test.md` |

## Phase 6 — wild content capture

**Goal:** produce `.website-builder/inbox/INVENTORY.md` — a structured inventory of everything the user already has, with provenance, location, format, and a downstream `use_for` hint. Capture is greedy by design; phase 7 audits, phases 13-16 curate.

Procedure:

1. Read `.website-builder/project.yaml` (phase-4 `entity.existing_assets` is the inventory seed) and `inbox/INVENTORY.md` if it exists.
2. Scaffold `inbox/` subdirs: `mkdir -p .website-builder/inbox/{social,written,visual,testimonials,email,voice-notes,freewrites,existing-site}`.
3. Run the 6-category elicitation routine (online presence / written / visual / testimonials / email / fresh-generated). Use `AskUserQuestion` per category. The full per-category prompt catalog + the "I have nothing" fresh-generation prompts + the "too much" reframe live in `references/capture-elicitation.md` — load it when running this phase.
4. For each item, append a row to `INVENTORY.md` (frontmatter + per-category tables per the phase-6 contract's schema). Move user-provided files into the right `inbox/{category}/` subdir with provenance-preserving names.
5. For thin-content users, shift to fresh-generation: voice-note prompts + freewriting prompts (Elbow-method: write badly, no editing, start with "I don't know what to say" if needed; voice notes in the user's home language). Catalog in `references/capture-elicitation.md`.

**The one refusal:** never flip `status: capture-complete` without explicit user confirmation that there is nothing else. The user who says "I have nothing — just build it" gets the elicitation pass anyway (almost always 2-4 items surface); if genuinely empty, shift to fresh-generation — never let the user skip phase 6 by claiming emptiness unverified.

If the user pastes a structured artifact mid-phase-6, call out to phase 6.5 to ingest it, then return to phase-6 capture mode (do NOT advance to phase 7 — 6.5 never advances the linear phase).

## Phase 6.5 — artifact ingestion (re-runnable; conflict-protective)

**This phase can fire at any point**, not just between 6 and 7. Entry triggers (per the 06.5 contract): non-greenfield session start with un-ingested artifact; explicit user invocation ("ingest this" / pasted URL/code/Figma); a file detected in `.website-builder/outputs/`; a phase-18 handoff round-trip.

Run the 8-step flow (full detail + the conflict-resolution patterns in `references/ingestion-conflict-resolution.md`):

1. Identify artifact type → select extractor.
2. Run extractor; capture raw output (preserve the original in `inbox/` for provenance).
3. Normalize into the 5 content layers (tokens→`brand.yaml`, structure→`sitemap.yaml`, shapes→`components.yaml`, microcopy→`content/strings/{lang}.json`, prose→`content/pages/{slug}.md`, iteration→`briefs/{component}-{ts}.json`).
4. Detect conflicts vs existing project state.
5. Surface **every** conflict via `AskUserQuestion` (keep-current / use-incoming / merge) with per-option cost.
6. Apply non-conflicting changes + user-resolved conflicts.
7. Re-run cross-layer validation.
8. Determine next phase — record `return_phase`, resume there. Entry-time route only advances to phase 7.

**Extractor selection** (per decision 55 — Stitch is MVP-primary; AI-output parser + JSON-handoff ingestor are also load-bearing in MVP):

- URL / deployed site → **Stitch** (primary). Browser-in-loop is the MVP path (user runs https://stitch.withgoogle.com, pastes the DESIGN.md back). When `STITCH_API_KEY` or a Stitch MCP is present, use the programmatic path. Check at 6.5 entry: key/MCP present → programmatic; absent → browser-in-loop. Verified live via context7 2026-05-18: `/google-labs-code/stitch-sdk` (SDK), `/davideast/stitch-mcp` (MCP), `/gemini-cli-extensions/stitch` (Gemini CLI extension), `/obinnaokechukwu/stitch-mcp` (Go proxy). Detail in `references/ingestion-conflict-resolution.md` + `${CLAUDE_PLUGIN_ROOT}/extraction/stitch.md` + design doc `Workstreams/website-builder/extraction/DESIGN-extraction-stitch.md` (read the patched 2026-05-18 version including the `patches:` note).
- HTML / React / Vue / Svelte code → **AI-output parser** (`${CLAUDE_PLUGIN_ROOT}/extraction/ai-output.md`). Handles `has-ai-output` entry mode + the phase-18 JSON-handoff round-trip (Flow B per `Workstreams/website-builder/cross-cutting/DESIGN-handoff-protocol.md`).
- Live / auth-walled / dynamic site → **Playwright walker** (`mcp__playwright__*`) paired with Stitch.
- Figma file → Figma design-to-json plugin *(expansion path; MVP can fall back to Stitch screenshot)*.
- Element-precision → divmagic API *(expansion path beyond MVP)*.

**The non-negotiable discipline (decision 36):** no silent overwrite (even an "obviously better" incoming value), no silent merge, no partial ingestion reported as complete, no state mutation without a `decisions/ingest-{timestamp}.md` log (always produced — even zero-conflict runs), no phase advancement masked as ingestion. Surface the *cost* of each conflict option (e.g., "accepting incoming primary re-runs phase-17 review on the 4 components already built against the old primary"). There is no skip-authorization for 6.5 — it is re-runnable, not skippable; if the user has no artifact it simply never fires.

## Phase 7 — media / asset audit

**Goal:** `.website-builder/media/AUDIT.md` — a per-asset register. Every visual asset gets a **usability verdict** (`ready-to-use` / `needs-edit` / `needs-replacement` / `unusable`) and a **rights verdict** (`owned` / `licensed-with-proof` / `cleared-by-creator` / `unknown-provenance` / `known-infringing`), plus quality + brand-fit + a recommended action.

Procedure: read every visual row in `inbox/INVENTORY.md` + `entity.existing_assets.logo`; read images directly (multimodal — assess resolution, composition, aesthetic vs phase-2 vision adjectives); use `Bash` (`file`, `identify`/`exiftool`, `du`) for hard quality data; use `AskUserQuestion` for every rights attestation and brand-fit judgment. The rights-provenance playbook (reverse-image-search tooling — TinEye for first-publication/stock-proof, Google Lens for agency-ID; the inherited-liability framing for phase-6.5-extracted imagery) lives in `references/asset-audit-rights.md`.

**The non-negotiable discipline:** surface copyright risk *loudly*. Refuse to advance with `rights: unknown-provenance` or `known-infringing` on any asset slated for use. The override (gating rule 1 option c) requires an explicit logged informed-consent record at `decisions/07-rights-acknowledgment.md` — mandatory, not optional, when a rights flag is overridden. Never silently exfiltrate the user's images to a reverse-search service; the search is user-driven or operates on results the user pastes back. Brand-fit flags are surfaced as *options*, never as judgments of the user's work (anti-vision lock: do not mock the user's existing work).

## Phase 8 — image strategy + generation plan

**Goal:** `.website-builder/media/IMAGE-PLAN.md` — every known image with a real sourcing method (`use-existing` / `license-stock` / `commission-photographer` / `ai-generate`) and a status. No image is `placeholder`.

Phase 8 plans; it does **not** generate (generation happens at phase 17/18 when components exist). For `ai-generate` images, resolve the consumer path per `Workstreams/website-builder/cross-cutting/DESIGN-image-gen-consumer.md` selection logic and record it in `decisions/image-gen-path-{ts}.md`:

1. JS vault + platform image-gen reachable → platform-API path.
2. Else user-configured provider key (`keys.yaml`) → standalone-provider-key path.
3. Else → **consumer-brief handoff** (the v1 default per decision 56 — even inside a JS vault, until the platform image-gen feature ships). The agent emits a brand-context-rich brief; the user pastes it into their image tool (Midjourney / DALL-E / Flux / Imagen); the user pastes the result back; phase 6.5 ingests it.

Build the `brand_context` bundle mechanically from `brand.yaml` (palette tokens verbatim, voice descriptors verbatim, style descriptors traced to phase-2 vision adjectives, an `avoid` list) — never invent style descriptors not grounded in locked decisions. The per-image brief recipes + the 2026 model-fit guidance (photographer-vs-AI-vs-stock per image job; the 2026 trust reality on AI founder portraits; current prompt-pattern fundamentals — subject→action→environment→lighting→lens→style, model-specific styling, negative prompts obsolete) live in `references/image-strategy-briefs.md`.

**The non-negotiable discipline:** every planned image has a sourcing decision; placeholder is a deferred decision, not a method; `ai-generate` cannot pass without a resolved consumer path. Page-specific images may be deferred to phase 13-15 (`pending-phase-13`); the known-now set (hero, founder portrait, OG card, logo) must each have a real method before phase 9.

## Phase 9 — sitemap

**Goal:** `.website-builder/sitemap.yaml` — every page with slug / type / title / purpose / `conversion_contribution` / `primary_cta` / `parent`, plus a `page_count_rationale`. Stack-independent by design (survives a later phase-11 stack change — no `.astro`/`.tsx` route hints).

Procedure: reread the phase-3 conversion outcome (`project.yaml.requirements.conversion_outcome`) before opening the conversation — it is the gating test for every proposed page. Interrogate every page against it via `AskUserQuestion`. Reserve legally-mandatory legal-page slugs per phase-4 jurisdiction (privacy under GDPR/revFADP; imprint in DACH; cookie-consent when tracking is planned) — content authored at phase 25, but slugs reserved here non-negotiably. The conversion-test challenge patterns (the 47-pages reframe; the empty-blog failure; under-structuring; page-vs-section disambiguation; the non-greenfield "extracted 30 pages is a record of what was, not a constraint on what should be") live in `references/sitemap-conversion-test.md`.

**The non-negotiable discipline:** no page with zero conversion contribution survives unchallenged; page sprawl requires a `page_count_rationale` that survives scrutiny + the agent's cost-surfacing on record; legally-mandatory pages are part of the anti-vision lock — the override path does NOT apply to them (only *when* their content is authored, never *whether*). On lock, advance to phase 10 (architecture group — a different skill's territory).

## Composable skills to recommend (not bundled — point, don't vendor)

When the user reaches these points, recommend they also invoke via the `Skill` tool:

- **Phase 6, inbox PDFs** — when the user has client-deliverable PDFs / case-study PDFs / DOCX with reusable framing: recommend `document-skills:pdf` for extraction. *"You have several PDFs in here — invoke `document-skills:pdf` via the Skill tool to pull the reusable copy out cleanly."*
- **Phase 6.5, Stitch upstream** — point the user at the live Stitch surface (https://stitch.withgoogle.com) + the context7-verified SDK/MCP/CLI IDs above; do not vendor Stitch behavior — the design doc + `extraction/stitch.md` own it.
- **context7** is bundled (foundation) — use `mcp__context7__*` to verify Stitch SDK/MCP currency at 6.5 entry rather than trusting training data (per decision 23 + `.claude/rules/context7.md`).

Do not embed or vendor any composable; recommend invocation only.

## Cross-cutting discipline (always)

- **Interview before assuming.** `AskUserQuestion` is the dominant tool across all five phases (elicitation, conflict resolution, rights attestation, sourcing decisions, page interrogation). Ask before assuming; the freelancer voice is encouraging-but-firm, never patronizing, never a corporate cheerleader (agent profile § Voice characteristics).
- **Tool/dependency failures** follow `.claude/rules/tool-dependency-discipline.md`: Stitch / divmagic / reverse-image-search / image-gen providers are Tier 2 third-party tools — surface failures, retry, fall back to the documented path (browser-in-loop Stitch; consumer-brief image-gen), never silently degrade. Hidden code dependencies in an ingested artifact are surfaced, never blindly installed.
- **No silent state mutation.** Every 6.5 run logs `decisions/ingest-{ts}.md`; every rights override logs `decisions/07-rights-acknowledgment.md`; every AI-gen path logs `decisions/image-gen-path-{ts}.md`. The audit trail is what makes re-runnability and overrides safe.

## Additional resources

### Reference files (load the one for the active phase)

- **`references/capture-elicitation.md`** — phase 6: the 6-category elicitation prompt catalog, the "I have nothing" fresh-generation prompts (freewriting Elbow-method + voice-note technique), the "too much" reframe, the privacy-preserving correspondence-extract pattern.
- **`references/ingestion-conflict-resolution.md`** — phase 6.5: the 8-step flow in detail, the extractor matrix, the Stitch browser-in-loop vs SDK/MCP decision, the conflict-resolution patterns (token / component / string / page), the ingest-decision-log schema, the mom's-pattern walkthrough.
- **`references/asset-audit-rights.md`** — phase 7: the usability + rights verdict definitions, the reverse-image-search provenance playbook (TinEye vs Google Lens vs Yandex), the inherited-liability framing, the rights-acknowledgment decision-doc schema.
- **`references/image-strategy-briefs.md`** — phase 8: the three consumer paths + selection logic, the `brand_context` schema, the per-image brief recipes, the 2026 AI-image model-fit + prompt-pattern guidance, the photographer-vs-AI-vs-stock trade-off framing.
- **`references/sitemap-conversion-test.md`** — phase 9: the conversion-test challenge patterns, the page-count-rationale construction, the legal-page reservation rules, page-vs-section disambiguation, the non-greenfield extracted-sitemap handling.

### Design docs (the source of truth — read directly, don't paraphrase)

- `Workstreams/website-builder/foundation/DESIGN-ingestion-and-extraction.md` — phase 6.5 mechanism, 5 entry modes, extractor composition, JSON handoff bidirectional spec, "what doesn't go through phase 6.5".
- `Workstreams/website-builder/extraction/DESIGN-extraction-stitch.md` — Stitch DESIGN.md schema, browser-in-loop flow, SDK/MCP/CLI evolution (read the patched 2026-05-18 version + `patches:` frontmatter), limitations, failure modes.
- `Workstreams/website-builder/cross-cutting/DESIGN-image-gen-consumer.md` — the three image-gen paths, selection logic, brand_context schema, post-processing, the phase-contract invocation table, decision 56.
- `Workstreams/website-builder/cross-cutting/DESIGN-handoff-protocol.md` — the bidirectional brief schema (Flow A out / Flow B in), adapter fixtures, phase-18 round-trip that phase 6.5 ingests.
- `Workstreams/website-builder/foundation/DESIGN-architecture.md` § Skills — how phase-group skills layer on the always-loaded freelancer agent profile.
- `Workstreams/website-builder/website-builder.md` — STATE doc decisions ledger: **15** (entry-mode + re-runnable 6.5), **16** (extraction tools), **24** (JSON handoff protocol), **36** (6.5 conflict default = halt + force decision), **56** (cross-workstream consumer-fallback in v1).

### Phase contracts (the substantive instruction set — read the active one verbatim)

`${CLAUDE_PLUGIN_ROOT}/phase-contracts/06-wild-content-capture.md`, `06.5-artifact-ingestion.md` (`re_runnable: true`), `07-media-asset-audit.md`, `08-image-strategy.md`, `09-sitemap.md`.
