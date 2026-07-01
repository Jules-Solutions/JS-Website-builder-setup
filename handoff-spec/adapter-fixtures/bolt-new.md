# Adapter Fixture — Bolt.new

> Per-tool handoff fixture for **Bolt.new** (bolt.new by StackBlitz). Like Lovable, a whole-app builder — scope the brief down to a single component or you get a project scaffold. Cleaner, more modular code than Lovable, with direct file/terminal access. Canonical design anchor: `DESIGN-handoff-protocol.md` § "Adapter fixtures". Brief contract: `handoff-spec/component-request-v1.md`. Output contract: `handoff-spec/component-output-v1.md`.
>
> Tool behaviour verified 2026-06-14 (see "Sources"). Re-verify on a cadence.

## How to paste the brief into Bolt.new

1. Open bolt.new, start a **new project**.
2. Paste the JSON brief, **prepended with a scope-down instruction**: *"Generate ONLY the single component below as one file. Do not scaffold a full app or backend."* (The brief's `instructions_for_external_tool` says this; reinforce it — Bolt's default is a project scaffold.)
3. Bolt generates a project scaffold; files appear in the file tree and the live preview takes shape.
4. Open the single component file in the file tree to capture it. Bolt gives you direct access to the code + a terminal.

## Tool-specific quirks

- **Project-scaffold default.** Bolt generates a scaffold with files in a tree + a live preview — not a lone component. The scope-down instruction keeps it to one file (or at least makes the target file obvious).
- **Cleaner, more modular, less opinionated than Lovable.** Bolt gives direct code + terminal access for refactoring and generates more modular code, but it's *less opinionated* — it makes fewer automatic architectural decisions, so brand fidelity leans harder on the brief's `brand_context` + discipline clause. Watch for default Tailwind palette (`slate`/`zinc`) leaking in.
- **Frontend-focused.** Bolt is fundamentally a frontend tool; it won't over-wire a backend the way Lovable does — *good* for a presentational component handoff (fewer stray data imports to strip).
- **Deploy step is separate** (Netlify/Vercel) — irrelevant to the handoff; you only need the one component file.
- **Direct terminal** means Bolt may run installs; ignore for capture — you want the source file, not Bolt's node_modules.

## Expected output format

A single React `.tsx` component file from the generated scaffold, **Form 1 (pure code)** per `component-output-v1.md`. More modular but possibly with default-Tailwind-palette drift. No Form-2 metadata header.

## How to capture output

- Open the component file in Bolt's file tree and **copy** it (or download the project, pull the one file).
- Save to `.website-builder/outputs/{brief-id}.tsx` so the filename binds.
- Ingest; the palette validator flags any `slate-*`/`zinc-*` default-palette drift for round 2.

## Known issues

- **Project-scaffold sprawl** — without scope-down you get a scaffold; reinforce single-component scope.
- **Default Tailwind palette drift** — Bolt's less-opinionated output leans on Tailwind defaults; palette validator catches it.
- **Modular split** — Bolt may extract a sub-component or util; review and decide what to ingest.

## Sample brief + sample output pair

The schema-valid sample brief: [`samples/bolt-new-brief.json`](samples/bolt-new-brief.json).
The corresponding sample output (**Form 1** — modular component with a default-palette drift the ingest flags): [`samples/bolt-new-output.tsx`](samples/bolt-new-output.tsx).

The brief validates against `spec/component-request-v1.json`. (Round-trip ingestion assertions in `tests/handoff-protocol/` run on the ChatGPT / Claude.ai / v0 pairs per the DoD's ≥3-of-6 bar; this pair is provided for completeness + the brief-validity sweep.)

## Sources

- Bolt.new 2026 scaffold generation + limitations: https://www.nxcode.io/resources/news/bolt-new-vs-lovable-2026 and https://aidevstack.vercel.app/blog/bolt-new-vs-lovable-vs-v0-2026 — confirm project-scaffold-in-file-tree generation, cleaner/modular/less-opinionated code with direct code+terminal access, frontend focus, separate Netlify/Vercel deploy.

## See also

- `handoff-spec/component-request-v1.md` — the brief contract
- `handoff-spec/component-output-v1.md` — the return contract
- `skills/wb-component-build/references/json-handoff-protocol.md` — phase-18 per-tool quirks table
- `extraction/ai-output.md` — the parser that ingests the output
