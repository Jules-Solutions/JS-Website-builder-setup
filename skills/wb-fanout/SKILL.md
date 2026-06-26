---
name: wb-fanout
description: This skill should be used ONLY when the user explicitly opts into parallel/faster research at an opt-in phase (2 vision, 3 requirements, 5 brand-voice, 8 image-strategy). Trigger when the user says "scan all 5 at once", "research these in parallel", "do all the competitors at the same time", "fan this out", "split this up and do it faster", "compare these N in parallel", or otherwise asks to gather multi-subject research concurrently instead of one-at-a-time. Decomposes the research brief into N per-subject sub-agent specs via `wb fanout decompose`, has the agent spawn the sub-agents (Agent + TaskCreate), then merges the structured results via `wb fanout aggregate`. Do NOT trigger by default — in-person, one-subject-at-a-time is the default; fan-out is the speed path the user opts into.
version: 0.1.0
---

# wb-fanout — Parallel research fan-out (opt-in)

> The speed path for multi-subject research at the opt-in phases. The user has 5 competitors / 5 voice exemplars / 5 reference sites / 3 image providers to look at; instead of researching them one-at-a-time in conversation, the agent fans the research out across N parallel sub-agents, then merges the structured results into one synthesis to react to.
>
> **This skill is the agent-facing half of the Wave-3b fan-out substrate.** The deterministic parts (decompose a brief, maintain the ledger, aggregate results) live in `${CLAUDE_PLUGIN_ROOT}/scripts/wb_fanout.py` and are reached via `wb fanout ...`. The part a script CANNOT do — spawning the `Agent` tool ×N + `TaskCreate` — is this skill's job: read the emitted spawn-recipe, execute it.

## The load-bearing doctrine: in-person is the default

Every opt-in phase contract states it verbatim — **"No subagent spawn by default … the default is in-person; spawn is the user opting into speed."** Honor it:

- **Do NOT reach for this skill on phase entry, or because there are several subjects.** Several competitors is not a reason to fan out — it is a reason to talk through each one. The default is sequential, in-person conversation where each subject becomes a real anchor for the decision.
- **Reach for it only when the user explicitly opts into speed** — "just scan all five at once", "do these in parallel", "I don't want to go one at a time". The fan-out gathers the raw material faster; it does **not** skip the in-person synthesis. After aggregation, return to the conversation and walk the user through the result.
- If unsure whether the user wants speed, **ask** (`AskUserQuestion`) — "Want to go through these one at a time, or have me scan all of them in parallel and bring back a comparison?" Default the recommendation to in-person.

## When it applies — the four opt-in phases

| Phase | What fans out | Dimensions are usually… |
|---|---|---|
| **2 — Vision** | reference URLs the user admires | visual register: palette / typography / pacing / mood |
| **3 — Requirements** | competitor sites | positioning / pricing / GTM / target-market / strength / weakness |
| **5 — Brand voice & tone** | voice-exemplar brands | voice attributes / NN4D tone profile / say / never-say |
| **8 — Image strategy** | image-gen providers/tools | photoreal fit / aesthetic control / cost / accessibility |

Fan-out at any other phase is off-doctrine; `wb fanout decompose` warns when given a non-opt-in phase.

## The procedure

### Step 1 — decompose the brief

Call `wb fanout decompose` with the current phase, the subjects (the fan-out axis — the N things to research in parallel), and the dimensions every sub-agent must cover (so the N results are comparable). Pass them inline, or write a small YAML brief and pass `--brief`:

```bash
wb fanout decompose --phase 3 \
  --topic "Competitor scan for positioning" \
  --subjects "competitor-a.com,competitor-b.com,competitor-c.com" \
  --dimensions "positioning,pricing,gtm" \
  --synthesis-goal "A positioning matrix the user can react to"
```

This records the run in the `.website-builder/tasks.yaml` fan-out ledger and prints a **spawn-recipe** to stdout — the markdown to execute in Step 2. It contains one ready-to-use sub-agent prompt per subject (each instructs the sub-agent to return a structured YAML block in the exact shape `aggregate` consumes).

### Step 2 — spawn the sub-agents (this is the part only the agent can do)

Read the emitted spawn-recipe. For each subject it lists, do both, and **issue all the `Agent` calls in a SINGLE message so they run concurrently**:

- `TaskCreate(subject="fanout: <subject>", description="Parallel research — <subject>")` — so the user sees progress.
- `Agent(subagent_type="researcher", description="research <subject>", prompt=<the SPEC block for that subject>)` — copy the recipe's `<<<SPEC>>>` text verbatim as the prompt.

Use `subagent_type="researcher"` (the read-only research agent) unless the recipe names another type. Each sub-agent returns a single YAML block: `subject`, a `findings` map (one key per dimension), and optional `notes`.

### Step 3 — assemble the results

When **all** sub-agents have returned, collect their YAML blocks into one results file at the path the recipe names (`.website-builder/fanout-results-<run_id>.yaml`):

```yaml
results:
  - subject: competitor-a.com
    findings:
      positioning: "Premium generalist; named enterprise clients"
      pricing: "Quote-only; no public pricing"
      gtm: "Outbound sales + referrals"
    notes: "Strong brand, opaque pricing"   # optional
  - subject: competitor-b.com
    findings:
      positioning: "..."
      pricing: "..."
      gtm: "..."
```

A subject that genuinely could not be covered on a dimension simply omits that key — `aggregate` flags it as a coverage gap rather than inventing data.

### Step 4 — aggregate

```bash
wb fanout aggregate --run <run_id> \
  --results .website-builder/fanout-results-<run_id>.yaml
```

(`--run` defaults to the most-recent run if omitted.) This writes a synthesis artifact to `.website-builder/library/<run_id>-synthesis.md` and prints it: a **subjects × dimensions comparison matrix**, a **per-dimension cross-cut** (every subject's finding side by side), any **cross-cutting notes**, and **coverage gaps**. It also flips the run to `status: aggregated` in the ledger and marks each subject's task done.

### Step 5 — return to the conversation

The synthesis is raw material, not a decision. **Go back to the in-person conversation** and walk the user through it — the matrix is the anchor, the user makes the call (which references resonate, which competitor to differentiate against, which voice exemplar fits, which image provider to use). This is the in-person synthesis the doctrine protects.

## Inspecting the ledger

`wb fanout status` lists every recorded run with its phase, status, dimensions, synthesis path, and per-task state. Use it to recover state after a context reset (the ledger persists in `.website-builder/tasks.yaml`).

## What this skill does NOT do

- **Does not auto-spawn.** It never fans out because a phase has many subjects — only when the user opts into speed.
- **Does not skip the conversation.** Aggregation precedes, never replaces, the in-person walk-through (Step 5).
- **Does not own the live task handles.** `wb fanout` tracks the specs + structured state; the agent owns the live `Agent` / `TaskCreate` handles (record the spawned task ids back if you want them in the ledger).
- **Does not generate or fabricate findings.** The sub-agents do the research; the helper only structures and merges what they return.

## Reference

- `${CLAUDE_PLUGIN_ROOT}/scripts/wb_fanout.py` — the substrate (`decompose` / `aggregate` / `status` + the importable `build_run` / `aggregate_results` cores).
- `Workstreams/website-builder/foundation/DESIGN-orchestration-spine.md` § 8 — the Wave-3b contract this skill implements.
- `phase-contracts/{02,03,05,08}-*.md` — the opt-in phases; each carries the in-person-default doctrine verbatim in its "Tools and skills used" section.
- `${CLAUDE_PLUGIN_ROOT}/agents/website-builder.md` § Tool usage discipline — `Agent` (parallelizable research) + `TaskCreate` / `.website-builder/tasks.yaml` mirror.
