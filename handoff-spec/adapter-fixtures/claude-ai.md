# Adapter Fixture — Claude.ai

> Per-tool handoff fixture for **Claude.ai** (claude.ai web app). Better long-context handling than ChatGPT and honors structured input well — the full brief, including `iteration_history`, fits without trimming. Canonical design anchor: `Workstreams/website-builder/cross-cutting/DESIGN-handoff-protocol.md` § "Adapter fixtures". Brief contract: `handoff-spec/component-request-v1.md`. Output contract: `handoff-spec/component-output-v1.md`.
>
> Tool behaviour verified 2026-06-14 (see "Sources"). Re-verify on a cadence.

## How to paste the brief into Claude.ai

1. Open a **new chat** (or a Project if you want the brand context to persist across components — paste the brief once per component regardless).
2. Use a current model (Sonnet/Opus 4.6+ class). The 200k chat context comfortably holds the full brief.
3. Paste the **entire JSON brief**. The `instructions_for_external_tool` block drives generation; no extra preamble needed.
4. Claude opens an **Artifact** side-panel with a live preview of the component. The code lives in that panel, not inline in the chat.

## Tool-specific quirks

- **Artifacts panel, not inline code.** Substantial code (React components, HTML, SVG) renders in a right-side Artifact with a live preview. You capture from the Artifact's copy button, not from the chat body. This is the single biggest workflow difference vs ChatGPT.
- **Honors structured input + the discipline clause well.** Claude.ai reliably respects the `MUST use ONLY the provided design tokens` clause and the full `brand_context` — brand drift is rare. It also tends to honor `iteration_history.issues_found` faithfully on round 2.
- **Will emit the Form-2 metadata header if asked.** Because it follows instructions closely, a brief whose `instructions_for_external_tool` requests the `component-output-v1` metadata header often gets it (ChatGPT usually ignores the same request). When present, the round-trip binds via the header's `brief_id` rather than via filename.
- **Long context = full brief is safe.** Unlike ChatGPT's output-cap concern, the practical limit here is generous; multi-file output (`file_count_hint > 1`) usually comes back complete in one Artifact.
- **May add a one-line summary in chat** alongside the Artifact. Ignore it; the Artifact is the deliverable.

## Expected output format

Component code in an **Artifact**, usually clean (no stray fences inside the Artifact). Either **Form 1 (pure code)** or **Form 2 (code + metadata header)** per `component-output-v1.md` — Form 2 when the brief requested the header. Both ingest cleanly.

## How to capture output

- Click **Copy** at the top of the Artifact panel (gives the raw code, no chat prose).
- Paste back into your Claude Code agent, **or** save to `.website-builder/outputs/{brief-id}.tsx`.
- If Claude emitted the Form-2 header, keep it — the parser binds via `brief_id` in the header.

## Known issues

- **Capturing from chat instead of the Artifact** — users sometimes copy Claude's chat summary instead of the Artifact code. Capture from the Artifact panel's copy button.
- **Over-helpfulness** — Claude.ai may add extra states or a dark-mode variant unasked. Usually a feature, but the ingest prop/shape-deviation check surfaces additions for your decision.
- **Artifact iteration drift** — if you iterate inside the same Artifact several times, capture the final version; intermediate versions are not what the brief tracked.

## Sample brief + sample output pair

The schema-valid sample brief: [`samples/claude-ai-brief.json`](samples/claude-ai-brief.json).
The corresponding sample output (**Form 2** — metadata-headed, on-brand, no drift, as Claude.ai returns when the header is requested): [`samples/claude-ai-output.tsx`](samples/claude-ai-output.tsx).

These are the round-trip pair the test at `tests/handoff-protocol/` exercises: the brief validates against `spec/component-request-v1.json`; the output ingests via the Form-2 `brief_id` binding, brand tokens are recognised as on-brand (no palette-validator flags), and the component shape matches the brief.

## Sources

- Claude.ai 2026 context window + Artifacts: https://suprmind.ai/hub/claude/features/ and https://albato.com/blog/publications/how-to-use-claude-artifacts-guide — confirm 200k chat context (1M API), Artifacts side-panel output for code/React/HTML.

## See also

- `handoff-spec/component-request-v1.md` — the brief contract
- `handoff-spec/component-output-v1.md` — the return contract (Form 2 metadata header detailed here)
- `skills/wb-component-build/references/json-handoff-protocol.md` — phase-18 per-tool quirks table
- `extraction/ai-output.md` — the parser that ingests the output
