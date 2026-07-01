---
name: wb-design-system
description: This skill should be used when the website-builder agent reaches phase 17 (design system creation) — the phase that turns the brand into a system of design tokens. Trigger when the user says "create the design system", "let's do colors / the palette", "set up the type scale / typography", "pick fonts and spacing", "build the design tokens", "do dark mode", "what should the site look like", or when `.website-builder/project.yaml.current_phase` is 17 and copywriting (phase 16) is complete. Drives grounded OKLCH-token option-generation (color, type scale, spacing, motion, dark-mode) using the chosen design-skill flavor; refuses arbitrary color picks, non-OKLCH color, missing semantic roles, unchecked contrast, and deferred dark mode.
version: 0.1.0
---

# wb-design-system — Phase 17: Design system creation

> The phase where the site stops being words + structure and gets a coherent visual language. Turn the phase-2 vision and phase-5 voice into a system of design tokens — color (OKLCH), type scale, spacing, motion, dark-mode — that every phase-18 component and phase-19 page composes from.
>
> **This skill carries phase 17 only.** Phase 18 (component design / build) is a separate skill (`wb-component-build`) per locked decision 64 / Lock M5 — do not bleed into component construction here. Phase 17 commits the *values*; phase 18 maps them into the chosen stack.

## Substantive source of truth — read this first

The authoritative behavior contract for this phase is:

**`Projects/Jules.Solutions/Subprojects/website-builder/phase-contracts/17-design-system.md`** — read it in full at phase entry. It carries the canonical Mission / Entry conditions / What Claude must establish / Gating rules / Tools / Output artifacts / Common failure modes / Reference materials. This skill is the *procedural how-to-execute* layer over that contract; the contract wins on any divergence.

Design-doc grounding (read as needed, do not paraphrase blindly):

- `DESIGN-skill-uiuxpromax.md` — the MVP primary design-skill flavor (locked decision 55). The 50+ styles / 161 palettes / 57 font pairings / 99 UX guidelines surface it drives, plus the option-narrowing discipline and composition/conflict rules.
- `DESIGN-context7-integration.md` — context7 is a foundation tool (locked decision 23); the invocation pattern + when it fires at phase 17.
- `DESIGN-resource-curation.md` — how `${CLAUDE_PLUGIN_ROOT}/reference-corpus/design-systems/` + the awesome-design-md corpus subset surface (read for inspiration, never imported).
- `DESIGN-architecture.md` § Skills + § Stack-agnostic output design — why tokens are stack-independent and survive a stack switch.

## Bundled reference depth (progressive disclosure — load on demand)

- **`references/oklch-token-system.md`** — why OKLCH, the luminance-first ramp method, the WCAG-2.2 contrast method, deterministic dark-mode L-inversion, type-scale ratio selection, motion budgeting, W3C-DTCG interop note, exemplar discipline. Load when computing actual token values.
- **`references/token-schema-examples.md`** — full worked `brand.yaml` `tokens:` key, the generated `brand.yaml.tokens.css` (`:root`/`.dark`/`@theme inline` scaffold), custom-semantic-role pattern, the override decision-log shape. Load when writing the artifacts.

## What this phase produces

Two artifacts in the user's project (schema in the contract `## Output artifacts`; worked instances in `references/token-schema-examples.md`):

1. `.website-builder/brand.yaml` — adds the `tokens:` key: color (OKLCH), typography (pairing + named scale ratio + scale), spacing, motion, dark-mode strategy (+ dark token set when not `none`).
2. `.website-builder/brand.yaml.tokens.css` — the same tokens as CSS custom properties in the shape phase 18 consumes (Tailwind v4 `@theme` / shadcn `@theme inline` `:root`/`.dark` scaffold for the React-Tailwind path).

Plus, **only if the arbitrary-color gate is overridden**: `.website-builder/decisions/17-color-override.md`.

## The core discipline: grounded option-generation, not arbitrary preference

A muggle saying "make it blue" is not wrong to have a preference — but a preference is not a system. The job: take the phase-2 vision (the reference URLs the user admired + the feel statement + adjective set) and the phase-5 voice (verbal identity), feed them through the chosen design-skill flavor, and produce **3–5 *complete* palette options** the user reacts to — each a full role-mapped, contrast-safe, dark-mode-ready system, not 5 raw primary hues. The user picks and iterates. Never silently apply an off-brand favorite color; never surface 161 raw palettes (decision paralysis is a UX failure).

## Procedure

### Step 1 — Verify entry conditions

Before doing anything, confirm (per contract `## Entry conditions`):

- Phase 16 (copywriting) complete — `.website-builder/content/pages/*.md` + `content/strings/*.json` have no placeholders. Design against *real content*; designing around lorem ipsum produces a system that breaks when real words arrive.
- Phase 2 vision present — `.website-builder/project.yaml.vision` (reference URLs + per-URL admiration note + feel statement + adjectives).
- Phase 5 voice present — `.website-builder/brand.yaml.voice`.
- The design-skill flavor is known (UI/UX Pro Max default per decision 55; loaded if user never picked).
- If a phase-6.5 artifact was ingested (`has-existing-site` / `has-Figma-file` / `has-ai-output`), load the extracted token seed (Stitch `DESIGN.md` / divmagic / Figma export) — phase 17 then becomes a *refine-and-extend* pass from that seed, reconciled against the phase-2 vision, not a blank page.

If an entry condition is unmet, stop and route the user back — do not design on a missing foundation.

### Step 2 — Auto-clone the inspiration corpus + verify the stack token API

At phase-17 entry:

- The awesome-design-md corpus subset auto-clones into `.website-builder/library/awesome-design-md/` (10–20 entries matched to the user's aesthetic direction, decision 42). Read these for *how mature systems articulate themselves in prose* — never to copy values. Same for `${CLAUDE_PLUGIN_ROOT}/reference-corpus/design-systems/` (Material 3 / Apple HIG / IBM Carbon role taxonomies).
- **context7 fires here** (foundation tool, decision 23 — the agent works with a *named* technology, Tailwind v4, whose token API changed materially v3→v4). Resolve + query:
  - `mcp__context7__resolve-library-id` → `mcp__context7__query-docs` for `/tailwindlabs/tailwindcss.com` — verify the current `@theme` directive + OKLCH default-palette shape + `--ease-*` tokens.
  - Same for `/shadcn-ui/ui` — verify the current `:root`/`.dark` OKLCH semantic-variable + `@theme inline` scaffold (this is the exact shape `brand.yaml.tokens.css` mirrors for the default path).
  - Use the user's actual phase context as the query, not vague single words. Cache in-session; do not re-query the same library/topic. On context7 failure, fall back to WebFetch the canonical docs URL and surface to the user (Tier 2 per tool-dependency-discipline) — never silently trust stale training data on a token API that changed.
- Surface 3–5 stack-matched templates for **aesthetic-vocabulary discussion only** (per `${CLAUDE_PLUGIN_ROOT}/reference-corpus/ECOSYSTEM-CATALOG.md`). Studied, never shipped.

### Step 3 — Generate 3–5 grounded options via the design-skill flavor

Invoke the loaded design-skill flavor (UI/UX Pro Max by default) with design verbs (`design`, `create`, `plan`). The flavor is installed at bootstrap by `wb-bootstrap`'s `scripts/install-skills.sh` into the user's CC skills dir (per `DESIGN-skill-distribution.md` + decision 32/55) and invoked here via the `Skill` tool — not read as a doc. It carries the 161 palettes / 57 font pairings / 50+ styles / 99 UX guidelines. **Narrow** it: produce 3–5 complete options, each tied back to a specific phase-2 reference or feel adjective so the user reacts with grounded reasons, not vibes. Each option is a full system: primary/secondary + neutral ramp + semantic roles + surface roles + a font pairing + a named scale ratio + spacing + motion preference. Build every option luminance-first in OKLCH from the first token (method in `references/oklch-token-system.md`).

Use `AskUserQuestion` to surface the options — it blocks for a real answer and keeps the agent from interrogating. The user reacts; iterate.

### Step 4 — Lock each token group with intent

Per contract `## What Claude must establish` (depth in the two reference files):

1. **Color (OKLCH).** Primary, secondary, neutral ramp (50→900), semantic (`success`/`warning`/`danger`/`info`), surface/on-surface pairs. Luminance-first ramp. UI ramps keep chroma modest; an accent can push it.
2. **Type scale.** Display+body pairing (source noted, system fallback specified) + a modular scale of 4–6 sizes (size+lh+weight each). **Name the ratio and tie it to the phase-2 feel** — surface the choice, never default silently (editorial/slow → larger ratio; dense UI → tighter).
3. **Spacing scale.** One modular scale on a base unit (typically 4px). One scale, used everywhere — ad-hoc pixels in phase 18/19 are a gating failure this phase prevents.
4. **Motion.** Default duration + easing cubic-bezier + stated preference (`subtle`/`expressive`/`minimal`) + `prefers-reduced-motion` posture (pre-budgeted here so phase 21/22 find no surprise).
5. **Dark-mode strategy.** `auto` | `opt-in` | `none`. For `auto`/`opt-in`, produce the dark token set *here* via deterministic L-inversion (in `references/oklch-token-system.md`).

### Step 5 — Enforce the gates (refuse to advance when violated)

Per contract `## Gating rules`:

- **Arbitrary color instead of generated** → refuse to write tokens from a bare preference; run the grounded-option round. *Overridable* only via explicit user confirmation with the trade-off surfaced, logged to `decisions/17-color-override.md`.
- **Color not in OKLCH** → hard fail. Convert + gamut-re-verify any supplied hex; store OKLCH only. **Not overridable.**
- **No semantic role mapping** → a swatch is not a system. **Not overridable.**
- **Contrast not checked** → verify every text/bg and UI-component pair against WCAG 2.2 (4.5:1 body, 3:1 large/UI) *here*, locking text L and tuning C/h. **Not overridable.**
- **Dark-mode undecided, or auto/opt-in without the dark set** → decide here; produce the dark set before advance. **Not overridable.**
- **System contradicts the voice** → reconcile voice/visual drift (warm-contrarian voice ≠ cold-corporate palette).

### Step 6 — Write the artifacts + advance

Write `brand.yaml` `tokens:` + `brand.yaml.tokens.css` (worked shapes in `references/token-schema-examples.md`). On user confirmation that the system "reads true", update `.website-builder/project.yaml.current_phase` to `18`. Phase 18 (`wb-component-build`) loads next and maps these values into the chosen stack — do not pre-empt it.

## Composable skills to recommend (do not vendor — point the user)

When the user reaches phase 17, recommend invoking via the `Skill` tool, for the stated purpose only:

- **`document-skills:frontend-design`** (Anthropic) — for the *aesthetic-direction* conversation: its anti-"AI-slop" heuristics (distinctive display+refined body type pairing; dominant color with sharp accents over timid even palettes; high-impact orchestrated motion over scattered micro-interactions; bold intentional direction). Recommend at Step 3 when the user wants a stronger point of view than the flavor defaults. *"For a bolder aesthetic stance, also pull in `document-skills:frontend-design` — it's tuned to avoid generic AI defaults."*
- **`ui-ux-pro-max:ui-ux-pro-max`** — the upstream of the MVP primary flavor itself; recommend invoking directly when the user wants to browse its full palette/style/font surface rather than the agent's narrowed 3–5. (`plugin:skill` invoke form — distinct from the `ui-ux-pro-max@ui-ux-pro-max-skill` *install* id.)
- **`document-skills:canvas-design`** — when the user wants a visual *mood/specimen board* (a rendered swatch+type specimen artifact) to react to alongside the in-chat options.
- **`document-skills:brand-guidelines`** — when the brand already has guidelines (colors/type) the system must conform to rather than generate from scratch; recommend at Step 1 to seed the option round from the existing brand.

Expansion design-skill flavors (surfaced as upgrade paths, not used by default — per contract `## Reference materials`): *Impeccable* (marketing-vs-product rule split), *Emil Kowalski* + *Framer Motion* (motion craft when motion is part of the brand), *Taste* (overrides palette/font defaults when the user has a definite aesthetic stance), *21st.dev* (agent-UX patterns). Conflict default: the more specialized loaded flavor wins on the axis it specializes; UI/UX Pro Max keeps product-type/archetype authority.

## Common failure modes (recovery in the contract `## Common failure modes` — read it)

Headlines: "you pick the colors" (premature handoff — generate grounded options instead); decision paralysis from raw 161; "use my exact hex everywhere" (surface the trade-off, don't refuse outright, log if overridden); style/audience mismatch (brutalism for enterprise SaaS — surface the risk); HSL/HEX habit (convert+verify+explain-once); type scale by reflex (name it, tie to feel); dark mode deferred (it's structural — decide here); contrast discovered at phase 21 (lock it here); "the design system is the design" (it's the *vocabulary*; phase 18 builds the components that speak it); treating the flavor's defaults as the brand (ground every option in *this* project).

## Cross-phase contract

The tokens committed here are exactly what phase 18 maps into the chosen stack's theme mechanism. No re-architecting downstream — values are locked at phase 17. The JSON handoff protocol may *optionally* be invoked here (emit a `DESIGN.md`-shaped brief to an external tool for parallel exploration, ingest the result via phase 6.5 as alternate options) — opt-in, not default (per `DESIGN-handoff-protocol.md`).
