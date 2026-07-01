# Adapter Fixture — Lovable

> Per-tool handoff fixture for **Lovable** (lovable.dev). A whole-app builder, not a component tool — so the brief must be scoped down to a single component in `instructions_for_external_tool`, or Lovable will generate an entire app around it. Canonical design anchor: `DESIGN-handoff-protocol.md` § "Adapter fixtures". Brief contract: `handoff-spec/component-request-v1.md`. Output contract: `handoff-spec/component-output-v1.md`.
>
> Tool behaviour verified 2026-06-14 (see "Sources"). Re-verify on a cadence.

## How to paste the brief into Lovable

1. Open Lovable, start a **new project** (or open an existing one if you want the component dropped into it).
2. Paste the JSON brief — but **prepend a scope-down instruction**: *"Generate ONLY the single component described below. Do not scaffold an app, backend, auth, or database. Output just the component file."* (The brief's `instructions_for_external_tool` already says this; reinforce it because Lovable's default is whole-app.)
3. Lovable builds in a single generation cycle and shows the result in its preview + file tree.
4. Navigate to the single component file in Lovable's file tree to capture it.

## Tool-specific quirks

- **Whole-app generation is the default.** Lovable builds the entire application — frontend and backend — in one cycle, including auth, a Postgres DB with RLS, and a polished React+Tailwind UI. For a single-component handoff this is far too much; the scope-down instruction is **load-bearing**. The brief becomes the "project description" otherwise.
- **Opinionated, shadcn-consistent code.** Lovable uses shadcn/ui consistently and a predictable project structure — good for brand fidelity, less flexible. Extract just the component file; ignore the surrounding scaffold.
- **Auto-Supabase wiring.** Lovable tends to wire Supabase and then ask you to "connect Supabase". For a presentational component this is noise — strip any data-layer imports the component doesn't need on ingest.
- **The component is buried in a generated tree.** You're hunting one file out of a generated app. Use the file tree; the component is usually under `src/components/`.

## Expected output format

A single React `.tsx` component file **extracted from a generated app tree**, **Form 1 (pure code)** per `component-output-v1.md`. May carry Supabase/data imports the component doesn't strictly need — strip on ingest. No Form-2 metadata header.

## How to capture output

- In Lovable's file tree, open the single component file and **copy** it (or download the project and pull out the one file).
- Save to `.website-builder/outputs/{brief-id}.tsx` so the filename binds to the brief.
- On ingest, the parser flags any imports (Supabase, app-router) the component doesn't need — confirm removal.

## Known issues

- **Whole-app sprawl** — without the scope-down instruction you get an app, not a component. Always reinforce single-component scope.
- **Stray data-layer imports** — Supabase wiring leaks into a presentational component; ingest surfaces the unused deps (per `tool-dependency-discipline.md` Tier 3 the agent never silent-installs them).
- **Finding the file** — the component is one file in a generated tree; capture the right one.

## Sample brief + sample output pair

The schema-valid sample brief: [`samples/lovable-brief.json`](samples/lovable-brief.json).
The corresponding sample output (**Form 1** — a single component extracted from a generated app, with a stray data-layer import the ingest strips): [`samples/lovable-output.tsx`](samples/lovable-output.tsx).

The brief validates against `spec/component-request-v1.json`. (Round-trip ingestion assertions in `tests/handoff-protocol/` run on the ChatGPT / Claude.ai / v0 pairs per the DoD's ≥3-of-6 bar; this pair is provided for completeness + the brief-validity sweep.)

## Sources

- Lovable 2026 whole-app generation + limitations: https://www.nxcode.io/resources/news/bolt-new-vs-lovable-2026 and https://www.nxcode.io/resources/news/lovable-vs-bolt-new-2026-ai-app-builder-comparison — confirm full-app single-cycle generation (frontend + backend + Supabase RLS), shadcn-consistent opinionated code, "connect Supabase" friction.

## See also

- `handoff-spec/component-request-v1.md` — the brief contract
- `handoff-spec/component-output-v1.md` — the return contract
- `skills/wb-component-build/references/json-handoff-protocol.md` — phase-18 per-tool quirks table
- `extraction/ai-output.md` — the parser that ingests the output
