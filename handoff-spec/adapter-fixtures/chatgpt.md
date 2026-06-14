# Adapter Fixture — ChatGPT

> Per-tool handoff fixture for **ChatGPT** (chat.openai.com / the ChatGPT app). The most common muggle tool — a user who got value from ChatGPT will keep using it, so the protocol embraces it. Canonical design anchor: `Workstreams/website-builder/cross-cutting/DESIGN-handoff-protocol.md` § "Adapter fixtures". Brief contract: `handoff-spec/component-request-v1.md`. Output contract: `handoff-spec/component-output-v1.md`.
>
> Tool behaviour verified 2026-06-14 (see "Sources" at the bottom). Re-verify on a cadence — these tools ship fast.

## How to paste the brief into ChatGPT

1. Open a **new chat** (a fresh thread avoids prior-context contamination of the brand tokens).
2. Pick a current model (GPT-5.x reasoning class). Avoid the smallest free-tier model for anything beyond a trivial component — its output cap truncates long files.
3. Paste the **entire JSON brief** as the message. No preamble needed — `instructions_for_external_tool` inside the brief already tells ChatGPT what to do.
4. Send. Read the first reply; if it wrapped the code in a ```` ```tsx ```` fence (it usually does despite the "no fences" instruction), that's fine — capture the fenced block (see below).

## Tool-specific quirks

- **Output-cap truncation is the real failure, not context truncation.** Modern ChatGPT context windows are large (GPT-5.x reasoning ≈ 400k tokens), so the brief itself fits comfortably — the stale "~8k token brief truncation" concern from early drafts no longer holds. The live risk is the **max-output cap** on a single reply (much smaller than the context window): a long multi-file component can get cut off mid-file. When `file_count_hint > 1` or the component is large, instruct "emit one file per message" or ask it to "continue" to get the rest.
- **It re-adds markdown fences.** ChatGPT almost always wraps code in triple-backtick fences and often prepends a sentence of prose ("Here's your component:") even when the brief says "code only, no fences". The AI-output parser strips fences + leading prose on ingest (Form 1 handling) — so capture the fenced block as-is.
- **It defaults to a generic palette.** Without the brief it would reach for `indigo-500` / `slate-*` (its house style). The brief's `brand_context` + the `MUST use ONLY` clause counter this, but ChatGPT still drifts occasionally — the palette validator catches it on ingest and seeds round 2.
- **It infers missing props.** If a prop is under-specified, ChatGPT invents a reasonable shape rather than asking. Usually fine; the ingest prop-deviation check surfaces anything off-spec.

## Expected output format

Raw component code (usually `.tsx`), most often inside a ```` ```tsx ```` fence, sometimes preceded by a short prose sentence. **Form 1 (pure code)** per `component-output-v1.md` — ChatGPT does not natively emit the Form-2 metadata header. Capture as Form 1.

## How to capture output

- Click the **Copy code** button on the code block (cleanest — gives you the fence contents without prose).
- Paste back into your Claude Code agent chat, **or** save to `.website-builder/outputs/{brief-id}.tsx` (filename = the brief `id`, so the round-trip binds automatically).
- If the file got truncated, ask ChatGPT to "continue from where you stopped" and concatenate.

## Known issues

- **Truncated long files** (output cap) — split into per-file messages; concatenate on capture.
- **Brand drift** (house palette leaks through) — palette validator flags; round-2 brief's `iteration_history.issues_found` lists the offending values with the brand token to use instead.
- **Fence + prose wrapper** — handled by the parser (Form 1 strip); never a blocker.
- **Accessibility omissions** — ChatGPT sometimes drops `alt` or uses `<div>` where the brief asks for `<h1>`; the ingest a11y audit catches these for round 2.

## Sample brief + sample output pair

The schema-valid sample brief: [`samples/chatgpt-brief.json`](samples/chatgpt-brief.json).
The corresponding sample output (Form 1 — fenced + prose wrapper, as ChatGPT really returns it): [`samples/chatgpt-output.tsx`](samples/chatgpt-output.tsx).

These two files are the round-trip pair the test at `tests/handoff-protocol/` exercises: the brief validates against `spec/component-request-v1.json`, and the output ingests cleanly (fence/prose stripped, brand tokens recognised, component shape matched, bound to the brief `id`).

## Sources

- ChatGPT token / context / output-cap limits (2026): https://www.scriptbyai.com/token-limit-openai-chatgpt/ and https://www.ai-toolbox.co/chatgpt-management-and-productivity/chatgpt-limits-messages-tokens-rate-2026 — confirm the context window is large but the per-reply output cap is the practical truncation point.

## See also

- `handoff-spec/component-request-v1.md` — the brief contract
- `handoff-spec/component-output-v1.md` — the return contract (Form 1 / 2 / 3)
- `skills/wb-component-build/references/json-handoff-protocol.md` — phase-18 per-tool quirks table
- `extraction/ai-output.md` — the parser that ingests the output
