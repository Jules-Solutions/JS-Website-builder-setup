# Phase 6.5 — Artifact ingestion + conflict resolution reference

> Loaded when running phase 6.5. The 8-step flow in detail, the extractor matrix, the Stitch browser-in-loop vs SDK/MCP decision, conflict-resolution patterns, the ingest-decision-log schema, and the canonical mom's-pattern walkthrough. Source of truth: `${CLAUDE_PLUGIN_ROOT}/phase-contracts/06.5-artifact-ingestion.md` + `DESIGN-ingestion-and-extraction.md` + `DESIGN-extraction-stitch.md` (read the patched 2026-05-18 version) + `DESIGN-handoff-protocol.md`. Decisions: 15, 16, 24, 36.

## Why 6.5 is re-runnable

The website-builder picks users up wherever they are. 5 entry modes (greenfield / has-existing-site / has-ai-output / has-Framer-attempt / has-Figma-file). Modes 2-5 trigger 6.5 at session start. **But 6.5 is also re-runnable at ANY lifecycle point** — that is what makes the agent a long-term collaborator instead of a restart-or-lose tool.

`current_phase` is NOT advanced to 6.5 as a linear step. The agent records the *return phase* (where the project was when 6.5 fired) and resumes there. `next_phase: 7` is the entry-time route only (after onboarding-time artifact ingestion). There is no skip-authorization — 6.5 is re-runnable, not skippable; no artifact → it never fires.

## The 8-step flow

1. **Identify artifact type + select extractor** (matrix below).
2. **Run extractor; capture raw output.** Preserve the original in `inbox/` before normalization (provenance). Stitch → DESIGN.md spec; AI-output parser → AST + strings + classes; Figma plugin → JSON; Playwright → DOM walk + per-section screenshots.
3. **Normalize into the 5 content layers:**
   - Layer 1 design tokens → `brand.yaml`
   - Layer 2 page structure → `sitemap.yaml`; section/component shapes → `components.yaml`
   - Layer 3 microcopy → `content/strings/{lang}.json`
   - Layer 4 page prose → `content/pages/{slug}.md`
   - Layer 5 iteration history → `briefs/{component}-{ts}.json`
4. **Detect conflicts** vs existing state — token / component / string / page.
5. **Surface every conflict** via `AskUserQuestion` (keep-current / use-incoming / merge) + per-option cost.
6. **Apply** non-conflicting changes + user-resolved conflicts.
7. **Re-run cross-layer validation** (same checks as the session-start hook: all YAML/JSON/MD parses, frontmatter conforms, `{strings.x.y.z}` refs resolve, sitemap pages exist in `content/pages/`, sections exist in `components.yaml`, token refs resolve).
8. **Determine next phase** — record `return_phase`; resume there. New content surfacing gaps → route to the relevant phase. Entry-time route → advance to phase 7.

## Extractor matrix

Per decision 55: Stitch is MVP-primary; AI-output parser + JSON-handoff ingestor are also load-bearing in MVP; divmagic + Figma-plugin + Peel/Codia are expansion paths.

| Artifact | Extractor | Notes |
|---|---|---|
| URL / deployed site | **Stitch** (+ optional Playwright for dynamic state) | Browser-in-loop MVP-primary; SDK/MCP when present |
| HTML / React / Vue / Svelte code | **AI-output parser** | Built-in; `has-ai-output` mode + phase-18 JSON-handoff round-trip (Flow B) |
| Live auth-walled / dynamic site | **Playwright walker** (`mcp__playwright__*`) | User supplies auth; walks authenticated state |
| Screenshot | **Stitch** (vibe extraction) | Tailwind Theme Maker = expansion |
| JSON-handoff-protocol output | **AI-output parser** via the handoff ingestion contract | The Flow-B side of DESIGN-handoff-protocol.md |
| Figma file | Figma design-to-json plugin *(expansion; MVP fallback = Stitch screenshot)* | `has-Figma-file` mode |
| Element-precision extract | divmagic API *(expansion beyond MVP)* | `keys.yaml` API key if user has one |

### Stitch: browser-in-loop vs programmatic

Check at 6.5 entry for `STITCH_API_KEY` env or a configured Stitch MCP:

- **Absent → browser-in-loop (MVP-primary).** Walk the user: open https://stitch.withgoogle.com, sign in, paste URL/screenshot, run extraction, copy the resulting design spec back. Lowest-friction, zero-dependency — works for every muggle. This is the path the design doc + decision 55 lead with.
- **Present → programmatic.** Use the SDK/MCP path (no user-in-the-loop). The SDK exposes `STITCH_API_KEY` env + `project.generate(prompt)` → `screen.getHtml()` / `screen.getImage()`. Defer exact invocation to `${CLAUDE_PLUGIN_ROOT}/extraction/stitch.md` + the design doc.

**Verified live via context7 2026-05-18** (the design doc's 2026-05-18 patch is current): `/google-labs-code/stitch-sdk` (official SDK, 103 snippets), `/davideast/stitch-mcp` (MCP, highest community benchmark 90), `/obinnaokechukwu/stitch-mcp` (Go MCP proxy with auth/token-refresh resilience), `/gemini-cli-extensions/stitch` (official Gemini CLI extension). Per decision 23 + `.claude/rules/context7.md`, re-verify Stitch currency via `mcp__context7__*` at 6.5 entry rather than trusting training data — Google Labs may change Stitch without notice.

**User pastes the vibe-prompt instead of the output** — common confusion (Stitch's Agent Protocol directs the agent to formulate a vibe-prompt for the user to paste *into* Stitch). Detect: *"That looks like the vibe-prompt I'd send you to paste into Stitch, not Stitch's output. The flow is: I give you a vibe-prompt → you paste it into stitch.withgoogle.com → Stitch generates → you copy *that* back."*

**SDK/MCP present but mis-keyed** — Tier 2 per `.claude/rules/tool-dependency-discipline.md`: surface the 401, offer (a) re-check key per DESIGN-secrets-and-keys.md, (b) fall back to browser-in-loop, (c) skip Stitch + use AI-output parser if the artifact is code. Never silently degrade.

## Conflict-resolution patterns (decision 36 — halt + force user decision)

No silent overwrite (even "obviously better"). No silent merge. No partial ingestion reported as complete. No state mutation without a decision log. No phase advancement masked as ingestion. Always surface the *cost* of each option.

**Token conflict:** incoming `oklch(58% 0.16 240)` vs existing `oklch(60% 0.18 245)`, phase 17 complete + 4 components built against existing. Surface: *"(a) keep existing — the 4 components stay valid, incoming remapped to your token [recommended]; (b) accept incoming — phase-17 review re-runs + 4 components need token-ref re-check; (c) blend to intermediate with explicit reasoning. Which?"*

**Component conflict:** incoming `Hero {title, subtitle, cta_text, cta_href}` vs existing `Hero {headline, body, cta}`. Surface: *"(a) keep existing — incoming Hero re-mapped to your prop names; (b) accept incoming — existing Hero code at [path] needs prop renames; (c) per-prop audit and decide each. Which?"*

**String conflict:** incoming `cta.subscribe = "Sign up free"` vs existing `"Get the newsletter"`. Surface: keep existing / use incoming / update everywhere.

**Page conflict (recency-aware):** *"yours has 412 chars edited 12 min ago; incoming has 1,847 chars. (a) keep yours; (b) replace; (c) merge — I'll show both side-by-side, pick per-section; (d) save incoming as `about-v2.md`, decide later."* Recently-edited content gets extra framing weight (surface "you just edited this 12 minutes ago", don't bury it).

**Partial / incomplete artifact:** *"The code renders `<PricingCard />` three times but there's no `PricingCard` definition in the paste. (a) paste the missing component; (b) I infer its shape from usage, you confirm; (c) ingest the rest, log `PricingCard` as a known gap before phase 19."* Never report success on a partial ingestion.

**Stack mismatch / language mismatch / brand drift / hidden dependencies** — each surfaces as a *question of intent* with cost-laden options; hidden deps are surfaced per `tool-dependency-discipline.md` (verify real packages, never blind-install).

## Ingest decision log (always produced — even zero-conflict runs)

`.website-builder/decisions/ingest-{timestamp}.md`. Frontmatter: `type: decision`, `subtype: ingest`, `ingest_id`, `phase: "6.5"`, `fired_from` (return phase or `session-start`), `return_phase`, `entry_mode_at_session`, `artifact: {type, source, extractor}`, `conflicts_detected`, `conflicts_resolved: [{locus, incoming, existing, resolution, reasoning}]`, `files_modified`, `validation`. Body: full narrative — what the artifact was, what was extracted, what conflicted, how each conflict resolved, what changed, where the project resumes. This audit trail is what makes re-runnability safe + reversible.

## Mom's canonical pattern (the load-bearing use case)

1. Mom is at phase 18 (component build) — project mid-flight.
2. New idea for a Testimonials section; she generates it in ChatGPT (or her freelancer drafts it).
3. She pastes the output back.
4. 6.5 fires: AI-output parser extracts the Testimonials component shape + placeholder copy + inline tokens.
5. Conflict detected (ChatGPT output used its own blue; project primary is locked orange).
6. Surface the token conflict (keep existing orange, remap the incoming).
7. Integrate: new `Testimonials` → `components.yaml`; section → the relevant `content/pages/{slug}.md`; copy → `content/strings/{lang}.json`.
8. Log `decisions/ingest-{ts}.md` with `return_phase: 18`.
9. Resume phase 18 with the new component available. **No prior work lost. The project did not restart.**

Same flow for a human freelancer's HTML delivery (the JSON-handoff brief format is portable per DESIGN-handoff-protocol.md — JSON + markdown a freelancer can read).

## What does NOT go through 6.5

Direct edits are not ingestion: "add a Pricing page" (agent writes `content/pages/pricing.md` + updates `sitemap.yaml` inline); editing `brand.yaml` to change a color; `wb update content/pages/about.md`. 6.5 is specifically for ingesting *external artifacts* generated outside the agent's direct authorship.
