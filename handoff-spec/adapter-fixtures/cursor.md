# Adapter Fixture — Cursor

> Per-tool handoff fixture for **Cursor** (the AI code editor / IDE). Unlike the chat tools, Cursor operates inside your project — it wants the brief as a file or via chat, and it writes output directly to files. Canonical design anchor: `Workstreams/website-builder/cross-cutting/DESIGN-handoff-protocol.md` § "Adapter fixtures". Brief contract: `handoff-spec/component-request-v1.md`. Output contract: `handoff-spec/component-output-v1.md`.
>
> Tool behaviour verified 2026-06-14 (see "Sources"). Re-verify on a cadence.

## How to paste the brief into Cursor

Two paths — pick based on how you work:

**Path A — brief as a file (recommended for round-trip fidelity):**
1. Save the brief at `.website-builder/briefs/{brief-id}.json` (the agent already wrote it there).
2. In Cursor, open the file, then open **Chat** (or **Agent** mode) and reference it: `@{brief-id}.json generate the component this brief describes`.
3. Cursor reads the JSON, generates the component, and writes it to a file (it asks where, or infers from `file_path_hint`).

**Path B — brief in chat:**
1. Open Cursor Chat / Agent.
2. Paste the JSON brief into the chat box.
3. Cursor generates and offers to write the file(s).

## Tool-specific quirks

- **Writes to files, not a chat bubble.** Cursor's Agent mode reads the codebase, edits/creates files, and can run terminal commands. Output lands as an actual file in your project — capture is "the file Cursor wrote", not a copy-paste from chat.
- **Multi-file by nature.** Agent mode happily creates multiple files with structure + dependencies. When `file_count_hint: 1` it usually respects a single component file, but it may also touch imports / a `lib/utils`. Review the diff before accepting.
- **It reads surrounding project context.** Because Cursor sees your repo, it'll match your existing import aliases + conventions — often *better* brand fidelity than a context-free chat tool, *if* your `brand.yaml`-derived tokens are already wired into the project's Tailwind/CSS-var theme.
- **Agent runs a loop.** It edits, runs, watches output, iterates until done or a guardrail. For a single component this is overkill but harmless; review the final diff.
- **`file_path_hint` is honored more than by chat tools** — Cursor places the file where you (or the brief) point it.

## Expected output format

A written `.tsx` (or stack-appropriate) **file in your project**, **Form 1 (pure code)** per `component-output-v1.md`. Cursor doesn't emit the Form-2 metadata header; the round-trip binds by **filename = brief id** (save/rename the written file to `{brief-id}.{ext}` if Cursor named it after the component).

## How to capture output

- The file Cursor wrote **is** the output. If Cursor wrote it directly into your project tree (e.g. `components/HeroBlock.tsx`), either point the agent at that path on ingest, or copy it to `.website-builder/outputs/{brief-id}.tsx` so the filename binds.
- Accept the diff in Cursor first (so the file actually exists), then ingest.

## Known issues

- **Filename doesn't match the brief id** — Cursor names by component, not brief id; rename or copy to `{brief-id}.{ext}`, or answer the agent's "which brief is this for?" prompt.
- **Touched extra files** — Agent mode may edit imports/config; review the full diff, ingest only the component (or accept the supporting edits knowingly).
- **Project-theme dependency** — Cursor's brand fidelity depends on your project's token wiring already existing; on a greenfield component it can fall back to defaults.

## Sample brief + sample output pair

The schema-valid sample brief: [`samples/cursor-brief.json`](samples/cursor-brief.json).
The corresponding sample output (**Form 1** — a written component file, project-convention imports): [`samples/cursor-output.tsx`](samples/cursor-output.tsx).

The brief validates against `spec/component-request-v1.json`. (Round-trip ingestion assertions in `tests/handoff-protocol/` run on the ChatGPT / Claude.ai / v0 pairs per the DoD's ≥3-of-6 bar; this pair is provided for completeness + the brief-validity sweep.)

## Sources

- Cursor 2026 Agent mode + spec-driven generation: https://aitoolsdevpro.com/ai-tools/cursor-guide/ and https://monday.com/blog/rnd/cursor-ai-integration/ — confirm Agent mode reads a spec, creates multiple files with structure, edits files + runs terminal in a loop.

## See also

- `handoff-spec/component-request-v1.md` — the brief contract
- `handoff-spec/component-output-v1.md` — the return contract
- `skills/wb-component-build/references/json-handoff-protocol.md` — phase-18 per-tool quirks table
- `extraction/ai-output.md` — the parser that ingests the output
