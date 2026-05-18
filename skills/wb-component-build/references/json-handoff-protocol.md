# JSON handoff protocol — phase-18 emission point

> Loaded on demand when the user opts into external-tool / freelancer generation for a component. Canonical source: `Workstreams/website-builder/cross-cutting/DESIGN-handoff-protocol.md` (read it for the full design contract). This reference is the phase-18 operational layer. Per locked decisions 24 (protocol is fundamental) + 35 (default is the agent writes code; brief-emit is opt-in per component).

## When this fires

Phase 18 is the protocol's **primary emission point**. Default behavior stays "the agent writes the code directly" (decision 35 — most muggle-friendly). Brief-emit is **opt-in per component**, triggered when the user signals an external tool or a freelancer for a given component: *"I'll do the hero in v0"*, *"send this to my freelancer"*, *"let me run this through ChatGPT"*.

Surface options per component (do not refuse, do not lose discipline):

```
Building <Component>. Options:
  [1] I write the code directly in your stack          (default; fastest)
  [2] I emit a brief; you take it to your AI tool       (ChatGPT / Claude.ai / v0 / Cursor / Lovable)
  [3] I emit a brief; you send it to your freelancer
  [4] You write it yourself; hand me the result when done
```

Most muggles pick `[1]`. Power users mid-flight with another tool pick `[2]`/`[3]`. The discipline holds across the boundary because the brief carries the brand tokens, voice, and a11y obligations.

## Flow A — out (agent → external tool)

Generate a `component-request-v1`-shaped JSON brief to `.website-builder/briefs/{component}-{ts}.json`. Blocks:

- **`subject`** — `{ kind: component|page|section|full-site, name, purpose }`.
- **`brand_context`** — the phase-17 OKLCH `color_palette`, `voice` (descriptors + exemplars_say/avoid from phase 5), `typography` (display/body/mono + scale), `spacing` (base_unit + scale), `motion` (duration/easing/preference), `dark_mode`.
- **`request`** — for a component: `props` (typed, max_chars, required), `behavior` (list), `responsive` (per phase-14 breakpoint), `accessibility` (heading_hierarchy, alt_text_required, contrast_ratio, keyboard_nav), `states`. From the `components.yaml` spec.
- **`output_format`** — `framework`, `library`, `style_system`, `language`, `file_path_hint`, `file_count_hint`. From the phase-11 stack + the chosen library.
- **`iteration_history`** — prior attempts + `issues_found` (empty on round 0). Carries forward what was wrong so the next round-trip improves.
- **`instructions_for_external_tool`** — templated from the other fields: "use ONLY the provided design tokens — do not invent colors/fonts/spacing; use {framework}+{library}+{style_system}; return code only, no prose/markdown/fences; if iteration_history present, address the latest issues_found." User can edit before sending.

Surface: *"Brief saved at briefs/<Component>-{ts}.json. Take it to your tool. Paste the result back or save it to outputs/<Component>-{ts}.{ext} and I'll integrate."*

## Flow B — in (external tool → agent → project state)

The user pastes the output back (or drops it in `.website-builder/outputs/`). **Phase 6.5 (artifact ingestion) fires** — the AI-output parser identifies modality, extracts design tokens (validated against `brand.yaml` — the palette validator flags drift), extracts component code (written to the user's project per stack convention), updates `components.yaml`. The filename binds output to brief (matching `id`); the brief's `iteration_history` records the round-trip. Conflicts surface for **explicit user decision per locked decision 36 (halt + force decision; no silent merge)**.

After ingestion, phase 18 resumes: the ingested component still passes the **token-fidelity self-review sweep** like any agent-written component. External-tool output frequently hardcodes values (the tool's defaults: indigo/slate where the brand tokens belong) — the sweep + the palette validator catch this; the brief's `iteration_history` carries the fix into round 2.

## Per-tool adapter quirks

Plugin ships `handoff-spec/adapter-fixtures/` (one md per tool). Phase-18-relevant quirks:

| Tool | Quirk to handle |
|---|---|
| **ChatGPT** | Truncates briefs > ~8k tokens — emit a trimmed-context version (subset of brand_context, no iteration_history) when truncation is anticipated; warn the user. |
| **Claude.ai** | Better long-context than ChatGPT; honors structured input well — full brief is fine. |
| **v0 (Vercel)** | React/Next-flavored output; auto-handles shadcn — `output_format` library=shadcn maps cleanly; v0 output is Next+shadcn+Tailwind by default. |
| **Cursor** | Wants the brief as a file comment or via chat; outputs to a file. |
| **Lovable / Bolt.new** | Whole-app output; the brief becomes the project description — scope down to a single component in `instructions_for_external_tool`. |
| **Human freelancer** | Same brief format. Package: send the JSON + a summary (brand voice/colors/use case) + prior iterations so the freelancer doesn't repeat the AI tool's mistakes. Capture output the same way (paste-back to `outputs/`). This is mom's pattern made first-class. |

## Cross-stack portability (bonus)

A brief written for React+Tailwind+shadcn re-targets to Vue+Tailwind+DaisyUI by swapping only the `output_format` block — `brand_context` + `request` survive. Brand + content survive a stack migration; only the framework-specific output adapts.

## Failure modes (handle, don't paper over)

- External tool truncates → emit trimmed version + warn.
- Output doesn't match brief → phase 6.5 surfaces mismatch; user decides keep / re-iterate / discard.
- External tool ignores brand tokens → palette validator flags ("this uses #FF0000 not your token primary; swap?"); `iteration_history` carries it to round 2.
- Output file collision (two outputs, same brief id) → surface, ask which to ingest.
- Brief encoding wrong (user copied wrong block) → ingestion looks for the brief id in the output; surface if missing.

## What this protocol is NOT

Not an MCP. Not a code interpreter for output. Not a sync mechanism (each round-trip is explicit). Not authentication-mediated (user uses their own accounts). Not a billing layer. The user copies/pastes; the discipline lives in the brief, not in hoping the external tool behaves.
