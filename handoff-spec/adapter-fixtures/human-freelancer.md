# Adapter Fixture — Human Freelancer

> Per-tool handoff fixture for a **human freelancer**. The same brief format used for AI tools works for a person — this is "mom's pattern" made first-class: she hires a freelancer for a section and wants on-brand work back. Canonical design anchor: `DESIGN-handoff-protocol.md` § "Human-freelancer fixture". Brief contract: `handoff-spec/component-request-v1.md`. Output contract: `handoff-spec/component-output-v1.md`.
>
> Not an AI tool — there are no "tool behaviours" to verify, but the packaging discipline below is what keeps a freelancer's output on-brand.

## How the brief works for a human freelancer

The brief is JSON + a human-readable instruction string. A freelancer reading it sees: "warm/direct voice, OKLCH colors, 64px h1, max-60-char headline, 4.5:1 contrast, React + shadcn + Tailwind". That's a complete, portable spec — the same discipline an AI tool gets, in a form a person can read. The freelancer produces output to spec and hands it back; you ingest it via the same phase-6.5 flow as any AI-tool output.

## How to package for a freelancer

1. **Send the JSON brief** (`.website-builder/briefs/{brief-id}.json`) — the full spec.
2. **Send a short summary** (email/chat) of the key points so they don't have to parse JSON to get started: brand voice + the 4-6 palette tokens + the use case + the one-sentence purpose.
3. **Include prior iterations** if any — paste the latest `iteration_history.issues_found` so the freelancer doesn't repeat mistakes an AI tool (or a previous freelancer) already made.
4. **Specify output-format expectations** explicitly: the file extension, the framework (`output_format.framework`), and whether you want a single file or multiple (`file_count_hint`). Freelancers vary more than tools — be concrete.
5. **Name the brief id** as the requested filename so the round-trip binds: "please name the file `{brief-id}.tsx`".

## Quirks (human, not tool)

- **Variance is the quirk.** A freelancer may deliver in a different framework, add their own polish, or interpret the voice loosely. The brief constrains this, but a person exercises judgment a tool doesn't — review the deviation list on ingest.
- **They may not read the JSON.** Hence the summary (step 2) — the JSON is the contract, the summary is the on-ramp.
- **Round-trips are slower** (days, not seconds) — but `iteration_history` works identically: round 2's brief carries what round 1 got wrong.

## Expected output format

Whatever you specified in step 4 — typically a code file in the requested framework, **Form 1 (pure code)** per `component-output-v1.md`. A diligent freelancer can include the Form-2 metadata header if you ask (with `tool_used: "human-freelancer-{name}"`), but most will just deliver the file.

## How to capture output

- Save the delivered file to `.website-builder/outputs/{brief-id}.{ext}` (ask the freelancer to name it the brief id, or rename on receipt).
- Ingest via phase 6.5 — identical to the AI-tool path: design tokens validated against `brand.yaml`, component shape checked against the brief, `iteration_history` updated.
- If the freelancer delivered HTML rather than the requested framework, the AI-output parser still extracts tokens/content/shape; the agent offers to translate or surfaces the framework mismatch.

## Known issues

- **Framework mismatch** — freelancer delivered HTML, project is React; ingest surfaces it, offers translation.
- **Brand drift / loose voice** — palette validator + voice cross-check flag drift; round 2 carries the fix.
- **No brief-id binding** — freelancer named the file their own way; rename to `{brief-id}.{ext}` or answer the agent's "which brief?" prompt.
- **Hidden dependencies** — freelancer used a library you don't have; per `tool-dependency-discipline.md` Tier 3 the agent never silent-installs — it flags + asks.

## Sample brief

The schema-valid sample brief: [`samples/human-freelancer-brief.json`](samples/human-freelancer-brief.json).

No sample *output* is shipped for this fixture — a freelancer's deliverable is indistinguishable in shape from an AI-tool output (it ingests via the identical Form-1/2 paths the AI-tool fixtures already exercise), so the round-trip is covered by those. The brief validates against `spec/component-request-v1.json` in the `tests/handoff-protocol/` brief-validity sweep, demonstrating the format is genuinely tool-agnostic — the same contract a machine consumes, a person can read.

## See also

- `handoff-spec/component-request-v1.md` — the brief contract (the portable spec)
- `handoff-spec/component-output-v1.md` — the return contract (Form 1 / 2 / 3 — freelancer output ingests the same way)
- `DESIGN-ingestion-and-extraction.md` § "Bonus surface: human freelancer handoff" — design-doc anchor
- `extraction/ai-output.md` — the parser that ingests the output
