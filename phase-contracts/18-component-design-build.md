---
phase: 18
name: Component design / build
group: design
pipeline_section: design
skill: wb-component-build
prev_phase: 17
next_phase: 19
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-phase-contracts.md
  - Workstreams/website-builder/foundation/DESIGN-architecture.md
  - Workstreams/website-builder/foundation/DESIGN-project-scaffold.md
  - Workstreams/website-builder/foundation/DESIGN-content-layers.md
  - Workstreams/website-builder/components/DESIGN-components-react.md
  - Workstreams/website-builder/components/DESIGN-components-tailwind.md
  - Workstreams/website-builder/components/DESIGN-components-headless.md
  - Workstreams/website-builder/cross-cutting/DESIGN-handoff-protocol.md
  - Workstreams/website-builder/cross-cutting/DESIGN-context7-integration.md
---

# Phase 18 — Component design / build

> Design *and* build every component the site needs, in the user's chosen stack, against the phase-17 design tokens. The phase where the system becomes code. Each component gets a spec (props, behavior, responsive rules, a11y) and working code the agent writes and the user reviews. The agent refuses page composition before all components exist and refuses any code that doesn't reference the phase-17 tokens. The JSON handoff protocol is available here: the agent can emit a brief the user takes to ChatGPT / v0 / Cursor / a freelancer, then ingest the result via phase 6.5.

## Mission

Phase 17 produced the vocabulary — color/type/space/motion tokens. Phase 13-15 produced the component inventory — every section across every page named the components it needs. Phase 18 builds those components: for each one, a spec (the contract) and working code in the user's chosen stack (the implementation), reviewed by the user.

The work product is `.website-builder/components.yaml` (the specs) plus actual component code written into the user's project per the chosen stack's convention. The component library picked at this phase (shadcn/ui by default for React+Tailwind, DaisyUI for non-React Tailwind stacks, Radix when total control is needed, etc. — see `## What Claude must establish`) provides primitives the agent *composes from*; the agent does not re-implement a button from scratch when an accessible, token-driven one is one `npx shadcn add button` away.

The discipline of this phase is **token fidelity and self-consistency**. Two specific failures the agent refuses: (1) code that hardcodes a color/size/font instead of referencing the phase-17 token (a `#FF0000` where a `var(--color-primary)` belongs), and (2) components written in inconsistent style (one component using the design system's spacing scale, the next using ad-hoc pixels; one accessible, the next not). The agent enforces a self-review pass against the design system before declaring a component done — the same "read it aloud" discipline phase 16 applies to copy, applied to code.

This is the heaviest single phase in the build group. It is the most context7-dependent (component-library APIs change fast — shadcn moved to Tailwind v4 + React 19; NextUI is rebranding to HeroUI; Base UI's package name has shifted across releases — training data is stale on all of this). It is also where the **JSON handoff protocol** most often fires: a muggle mid-flight with ChatGPT or v0 can take a structured brief out and bring a result back, and the agent's discipline holds across that boundary.

## Entry conditions

- Phase 17 (design system) complete. `.website-builder/brand.yaml.tokens` holds the OKLCH color system, type scale, spacing scale, motion tokens, dark-mode strategy; `brand.yaml.tokens.css` holds the generated CSS-variable form. Phase 18 builds *against* these — a component that doesn't reference them is a gating failure.
- Phase 11 (stack decision) complete. `.website-builder/project.yaml.stack` holds the chosen stack (and `project.yaml.transactional`). The stack determines the component-library candidate set (React libraries for Next/Astro-React/Vite-React/Remix; Tailwind-plugin libraries for Hugo/Astro-pure/static-HTML/WordPress; per `DESIGN-components-react.md` / `-tailwind.md` / `-headless.md`).
- Phases 13-15 complete. `.website-builder/content/pages/*.md` + `content/sections.yaml` name every component the site needs (the inventory phase 18 must fully satisfy).
- Phase 16 (copywriting) complete. Components are built against real content, not placeholders — a card built around lorem ipsum breaks when the real testimonial is three lines longer.

## What Claude must establish

For **every** component named across phases 13-15, two things:

1. **A component spec in `components.yaml`** — props (typed, with constraints + required flags), behavior (what it does, its states: default/loading/success/error/disabled where applicable), responsive rules (how it reflows at the phase-14 breakpoints — ~360px / ~768px / ~1280px), and accessibility (heading hierarchy contribution, alt-text requirements, contrast obligations against the phase-17 tokens, keyboard-nav order, ARIA where the primitive doesn't supply it).

2. **Working code in the chosen stack**, written by the agent and reviewed by the user, that:
   - References phase-17 tokens (Tailwind theme variables / CSS custom properties / the library's theme object fed from `brand.yaml`) — never hardcoded values.
   - Composes from the chosen component library's primitives rather than re-implementing accessible behavior the primitive already provides.
   - Respects the phase-17 motion tokens + `prefers-reduced-motion` posture.
   - Is grouped sanely in the source tree (per stack convention; e.g. shadcn primitives in `components/ui/`, composites in `components/`, animation companions in `components/magicui/` — kept in clean namespaces).

**Component-library selection** happens at this phase. The agent runs the selection logic from the component-library design docs and *always surfaces the default + 1-2 alternatives with trade-offs* — the user picks:

- React stacks (Next.js / Astro+React / Vite+React / Remix), no strong preference → **shadcn/ui** as primary (copy-paste, user owns the code, AI-aware, Radix-backed a11y, Tailwind-v4 + OKLCH theming aligns exactly with phase-17 output); propose **Magic UI** as animation companion for motion-heavy sections, **Aceternity UI** if the phase-2 vision leaned premium/agency/portfolio.
- "Everything out of the box" → **Mantine**. "Rapid prototyping" → **Chakra UI**. Admin/dashboard/dense data → **Ant Design** or **Material UI**. Consumer app polish + motion → **NextUI/HeroUI** (verify current naming via context7 — rebrand in flight). Material adherence → **Material UI**; Material foundations + own brand → **Joy UI**.
- Non-React Tailwind stacks (Hugo / Astro-pure / static-HTML / WordPress-Tailwind) → **DaisyUI** (pure-CSS, works everywhere, 35 themes, ~88% fewer classes); pair with **Headless UI** / **Alpine.js** for the JS interactivity DaisyUI's CSS-only patterns don't cover. **Tailwind UI** ($299 — surface the cost explicitly) if the user has the budget and wants pro templates as starting structure. **Park UI** for Ark-UI behavior + Panda/Tailwind, multi-framework.
- Total visual control / a library is missing a primitive / building a design system from scratch → **headless primitives**: Radix (28+, underpins shadcn — surface directly only for primitives shadcn doesn't wrap), Headless UI (10, Tailwind-team, smaller scope), Base UI (MUI-team, verify production-readiness + package name via context7).

The choice is recorded in `.website-builder/project.yaml.component_library: { primary: <lib>, complementary: [<lib>] }`. **Composition rules** (enforced): one primary library per project; up to two complementary libraries for specialized concerns (motion, data tables); `brand.yaml` tokens drive *all* libraries (mixing libraries' own brand presets is forbidden); don't double-wrap (Radix directly *or* via shadcn, not both for the same primitive).

Output schema in `.website-builder/components.yaml`:

```yaml
components:
  HeroBlock:
    spec:
      props:
        headline:   { type: string, max_chars: 60,  required: true }
        sub:        { type: string, max_chars: 120, required: true }
        cta_text:   { type: string, max_chars: 24,  required: true }
        background: { type: image,  required: false }
      states: [default]
      responsive:
        mobile_360:  { layout: stacked, headline_token: h2 }
        tablet_768:  { layout: stacked, headline_token: h1 }
        desktop_1280:{ layout: stacked, headline_token: h1 }
      a11y:
        heading: "headline = h1 on home, h2 elsewhere (only one h1/page)"
        alt_text_required: [background]
        contrast: "headline vs background ≥ 4.5:1 (token-checked)"
        keyboard: "skip-to-content → headline → CTA"
      tokens_used: [color.primary, color.surface.foreground, typography.h1, spacing.32, motion.default]
    impl:
      library: shadcn-ui
      composes: [Button]                       # shadcn primitive
      file: components/HeroBlock.tsx
      reviewed_by_user: true
  # ... every component from phases 13-15 ...
project_yaml_patch:
  component_library: { primary: shadcn-ui, complementary: [magic-ui] }
```

The agent updates `.website-builder/project.yaml.current_phase` to `19` upon user confirmation that every component is specced, built, and reviewed. Phase 19 (composition) loads next.

## Gating rules

The agent refuses to advance when:

- **Any component named in phases 13-15 has no spec + code.** The inventory is the contract; an unbuilt component means phase 19 cannot compose its pages. Partial coverage is not advance-able.
- **Code hardcodes a value the phase-17 system owns.** A literal hex, a literal font, an ad-hoc pixel spacing where a token belongs. The agent's self-review sweep flags every one and rewrites it to the token reference. This gate is not overridable — phase 19/20/21/22 all assume token fidelity.
- **Component style is inconsistent across the set.** One component uses the spacing scale, the next uses raw pixels; one is keyboard-accessible, the next is not; one references the motion token, the next hardcodes a duration. The agent reads the whole component set against the design system (the "read it aloud" cross-check, code edition) and reconciles drift before advance.
- **Page composition attempted before all components exist.** The agent refuses to start phase 19 work (assembling pages) while any component is still a spec without code. Components first, composition second — non-negotiable.
- **A11y obligations from the spec are unmet in the code.** Missing alt-text wiring on an image prop, no keyboard order on an interactive component, an ARIA role the primitive didn't supply and the code didn't add, contrast not actually clearing the phase-17-locked bar. Phase 21 audits this formally, but shipping known a11y holes into phase 19 is the gating failure phase 21 then pays for.
- **Component library mixed incoherently.** Two primary libraries; a complementary library's own brand preset bleeding in instead of `brand.yaml` tokens; the same primitive double-wrapped (Radix directly *and* via shadcn). The agent enforces the composition rules.

Override is not available on these gates — they are correctness prerequisites for phases 19-23. (The *brief-vs-direct-codegen* choice below is a per-component preference, not a gate override.)

## Tools and skills used

- **`Edit` / `Write`** — the primary tools. The agent writes component code in the user's chosen stack's conventions and edits across review rounds. This is the most code-generation-heavy phase in the pipeline.
- **`mcp__context7__resolve-library-id` + `mcp__context7__query-docs`** — heavily used. Per `DESIGN-context7-integration.md`, phase 18 is one of the most context7-dependent phases because component-library + framework APIs drift fast. The agent verifies the *current* state of the chosen library (registry/CLI install command, theming-integration shape, primitive composition pattern) and the framework (Server vs Client component rules for Next App Router, Astro island directives) before writing code, rather than trusting training data. Cached into `.website-builder/library/docs/` per the clone-into-project pattern (decision 42) because phase 18 queries the same library dozens of times.
- **The design-skill flavor (loaded skill, secondary here)** — UI/UX Pro Max's component element library (button/modal/navbar/card/table/form/chart with style-aware variants) is consulted as a secondary reference to keep components consistent with the phase-17 aesthetic. Per `DESIGN-skill-uiuxpromax.md`, complementary flavors (Emil Kowalski / Framer Motion) layer in for animation-heavy components.
- **Reference-data load** — `reference/component-patterns/` (canonical specs for the ~20 most common component types) and the chosen `component-libraries/{stack}.md` capability matrix. Per `DESIGN-resource-curation.md`, patterns are studied; the chosen library's reference docs auto-clone into `.website-builder/library/docs/` at phase-18 entry.
- **`AskUserQuestion`** — for the component-library selection (default + alternatives + trade-offs), per-component review confirmation, and the per-component brief-vs-direct-codegen choice.
- **The JSON handoff protocol** — see the dedicated sub-section below. Opt-in per component.

The `wb-component-build` phase-group skill is loaded at entry. Note this is a *distinct* skill from phase 17's `wb-design-system` even though both share `group: design`: the design-doc-level grouping is `design`, but the canonical 11-skill scheme (Decision 64) separates design-system creation (phase 17 → `wb-design-system`) from component design/build (phase 18 → `wb-component-build`) because they are different work with different tool loadouts — phase 17 is option-generation + token authoring; phase 18 is codegen against a chosen library. The skill carries the cross-phase contract that phase 19 composes pages *only* from components built here.

## JSON handoff protocol (component generation via external tools)

Per locked decision 24, the bidirectional JSON handoff protocol (`cross-cutting/DESIGN-handoff-protocol.md`) is fundamental to the pipeline, and phase 18 is its **primary emission point**. Default phase-18 behavior is "the agent writes the code directly in the user's stack" (locked decision 35 — most muggle-friendly). Brief-emit mode is **opt-in per component**, on user request.

**The trigger.** When the user signals they want to use an external tool or a human freelancer for a given component — *"I'll do the hero in v0"*, *"send this to my freelancer"*, *"let me run this through ChatGPT"* — instead of refusing or losing discipline, the agent emits a structured brief. The agent surfaces options per component:

```
Building HeroBlock. Options:
  [1] I write the code directly in your stack          (default; fastest)
  [2] I emit a brief; you take it to your AI tool       (ChatGPT / Claude.ai / v0 / Cursor / Lovable)
  [3] I emit a brief; you send it to your freelancer
  [4] You write it yourself; hand me the result when done
```

**The round-trip (Flow A out, Flow B in).**

1. *Out.* The agent generates a `component-request-v1`-shaped JSON brief to `.website-builder/briefs/{component}-{ts}.json`. The brief encodes: `brand_context` (the phase-17 OKLCH palette tokens, voice descriptors from phase 5, type scale, spacing, motion preference, dark-mode), `request` (props/behavior/responsive/accessibility/states from the `components.yaml` spec), `output_format` (target framework + library + style-system + language + file-path hint, from the phase-11 stack + the chosen library), `iteration_history` (prior attempts + what was wrong with them — empty on round 0), and a templated `instructions_for_external_tool` block ("use ONLY the provided design tokens — do not invent colors/fonts/spacing; return code only, no prose"). The agent surfaces: *"Brief saved at briefs/HeroBlock-{ts}.json. Take it to your tool. Paste the result back or save it to outputs/HeroBlock-{ts}.tsx and I'll integrate."*
2. *External.* The user goes to ChatGPT / Claude.ai / v0 / Cursor / Lovable / Bolt.new / a human freelancer. The plugin ships per-tool adapter fixtures (`handoff-spec/adapter-fixtures/`) covering each tool's quirks (ChatGPT truncates briefs > ~8k tokens — the agent emits a trimmed-context version when anticipated; v0 auto-handles shadcn; Cursor wants the brief as a file comment; the same brief format works for a human freelancer — mom's pattern, made first-class).
3. *In.* The user pastes the output back (or drops it in `.website-builder/outputs/`). Phase 6.5 (artifact ingestion) fires: the AI-output parser identifies modality, extracts design tokens (validated against `brand.yaml` — the palette validator flags drift, e.g. *"this uses #FF0000, not your token primary; swap?"*), extracts component code (written to the user's project per stack convention), updates `components.yaml`. The filename binds the output to its brief (matching `id`); the brief's `iteration_history` records the round-trip. Conflicts surface for explicit user decision per locked decision 36 (halt + force user decision; no silent merge).

**Why this matters.** Without the brief, a muggle pastes "make me a hero" into ChatGPT and gets output that knows nothing of the brand tokens, voice, or a11y obligations — drift. With the brief, the external tool sees the constraints; output stays on-system. The discipline holds across the tool boundary. The protocol is opt-in, not default; it is OPT-IN per request; most muggles pick `[1]`; power users mid-flight with another tool pick `[2]`/`[3]`. It is **not** an MCP, **not** a sync mechanism, **not** authentication-mediated — the user copies/pastes with their own accounts. Cross-stack portability is a bonus: a brief written for React+Tailwind+shadcn re-targets to Vue+Tailwind+DaisyUI by swapping only the `output_format` block; `brand_context` + `request` survive.

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| `.website-builder/components.yaml` | per the schema above (spec + impl per component) | The component contracts + their implementation pointers. Load-bearing for phase 19 composition. |
| Component code in the user's project | per chosen stack convention (e.g. `components/ui/*.tsx`, `components/*.tsx`) | The actual working components, token-driven, reviewed by the user. |
| `.website-builder/project.yaml` | sets `component_library: { primary, complementary }` | The locked library choice; enforced through phases 19-23. |
| `.website-builder/briefs/{component}-{ts}.json` *(only if handoff used)* | `component-request-v1` shape | Emitted brief for an external tool / freelancer; carries `iteration_history` across round-trips. |
| `.website-builder/outputs/{component}-{ts}.{ext}` *(only if handoff used)* | whatever the external tool produced | The returned artifact; ingested via phase 6.5. |
| `.website-builder/library/docs/{library}.md` *(auto-cloned)* | current library docs (via context7) | The chosen component-library reference, cloned at phase-18 entry, queried repeatedly during build. |

`components.yaml` + the component code are the always-required artifacts. The brief/output files exist only when the handoff protocol was used for a given component.

## Common failure modes

**Components written in inconsistent style.** The canonical phase-18 failure. The hero uses the spacing scale; the feature grid uses raw pixels; the card references the motion token; the modal hardcodes a duration. Common because each component "feels" independent. The agent runs the self-review pass (the "read it aloud" cross-check, code edition) against `brand.yaml.tokens` and surfaces the drift: *"these three components reference the design system; this fourth one hardcodes its spacing — same system, everywhere."* It rewrites the drifting component to the tokens.

**Hardcoded values instead of token references.** `style={{ color: '#FF0000' }}` where `text-primary` (Tailwind theme var fed from `brand.yaml`) belongs; `padding: 17px` where `spacing.16` belongs. Especially common in pasted external-tool output. The agent's token-fidelity sweep catches every literal and rewrites it to the phase-17 token. For handoff-ingested code, phase 6.5's palette validator flags this on round 1 and the brief's `iteration_history` carries the fix into round 2.

**Re-implementing accessible behavior a primitive provides.** The agent (or an external tool's output) hand-rolls a dropdown with `onClick` handlers and no keyboard support, when `npx shadcn add dropdown-menu` (Radix-backed, WAI-ARIA-correct, keyboard-complete) is one command away. The agent composes from the primitive and surfaces *why*: accessible interactive behavior is hard to get right; the library already did.

**Stale library knowledge.** The agent writes shadcn against the v3 Tailwind JS-config pattern when shadcn is now Tailwind v4 + React 19 + the `@theme inline` OKLCH variable scaffold; or imports `@mui/base` (deprecated) instead of the current Base UI package; or uses the NextUI name when it's rebranding to HeroUI. Correct behavior: context7 every chosen library at phase-18 entry and verify the current install command + theming shape + package name before writing a line. Training data is stale on all of these.

**Next.js Server/Client boundary errors.** shadcn forms are Client components; pages can be Server components. The agent puts `'use client'` in the wrong place and hydration breaks. Correct behavior: verify the current App Router Server/Client rules via context7 and enforce the boundary per the stack adapter.

**Overwrite risk on copy-paste libraries.** User customizes a shadcn component, later runs `npx shadcn add` for the same name, loses the customization. The agent advises copying customized components to a `components/custom/` namespace to escape the library's regenerate path, and notes this in `components.yaml`.

**External tool ignores the brand tokens.** The user takes a brief to ChatGPT; the output uses indigo/slate (the tool's defaults) instead of the project tokens. Expected — phase 6.5's palette validator flags it, the agent surfaces *"this output isn't using your tokens; want me to swap them in?"*, and the brief's `iteration_history` carries the issue so round 2 is corrected. The discipline is in the protocol, not in hoping the external tool behaves.

**"Just build all of them however — we'll fix it in composition."** Phase 19 is assembly, not repair. The agent surfaces that composition assumes the components are correct and consistent; building them sloppily means phase 19 discovers structural problems that are far more expensive to fix than building consistently the first time (the same logic as phase 14's skip cost, one layer down).

**Animation-heavy component blows the perf budget before phase 22.** An Aceternity hero with Three.js is dropped in without lazy-loading or `prefers-reduced-motion`. Correct behavior: the phase-17 motion budget pre-allocated this; the agent enforces dynamic import + reduced-motion gating + a static SSR fallback *at build time here*, so phase 22 doesn't rediscover the cost.

**Hidden assumption that the component library is the design system.** It is not. The library provides accessible primitives; `brand.yaml.tokens` (phase 17) provides the visual identity. The agent surfaces, when needed, that a library's default look is not the brand — every primitive is themed from the phase-17 tokens, never shipped with the library's preset.

## Reference materials

Foundation + component docs:

- `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` § 18 — the seed for this contract.
- `Workstreams/website-builder/foundation/DESIGN-architecture.md` § Component breakdown / `component-libraries/` / phase-18 default behavior (decision 35: agent writes code by default; brief-emit opt-in) / § context7 integration.
- `Workstreams/website-builder/foundation/DESIGN-project-scaffold.md` § `components.yaml` + `project.yaml.component_library` + `briefs/` + `outputs/` locations.
- `Workstreams/website-builder/foundation/DESIGN-content-layers.md` — Layer 2 (structural specs / components.yaml). Phase 18 fills Layer 2.
- `Workstreams/website-builder/components/DESIGN-components-react.md` — shadcn/ui (default), Mantine, Aceternity, Magic UI, Once UI, Chakra, NextUI/HeroUI, Material UI / Joy UI, Ant Design: capability matrix, selection logic, per-library codegen patterns, composition + migration.
- `Workstreams/website-builder/components/DESIGN-components-tailwind.md` — DaisyUI (S-tier non-React Tailwind pick), Tailwind UI ($299, surface cost), Park UI: matrix, selection, codegen.
- `Workstreams/website-builder/components/DESIGN-components-headless.md` — Radix Primitives (28+, underpins shadcn), Headless UI (10, Tailwind-team), Base UI (MUI-team, verify maturity): when total control is warranted.
- `Workstreams/website-builder/cross-cutting/DESIGN-handoff-protocol.md` — the bidirectional JSON brief: schema (`brand_context`/`request`/`output_format`/`iteration_history`/`instructions_for_external_tool`), the two flows, adapter fixtures per tool, the human-freelancer fixture, failure modes.
- `Workstreams/website-builder/cross-cutting/DESIGN-context7-integration.md` — the resolve→query pattern, per-stack library-id manifest, caching, fallback-on-resolution-failure.

context7 (mandatory at this phase — citations current as of the freshness date):

- **`/shadcn-ui/ui`** — shadcn/ui verified current: open-code copy-paste distribution (component source lands in the user's repo, not an npm import), built on **Tailwind CSS v4 + React 19**, semantic CSS-variable theming with **OKLCH** defaults wired via `@theme inline`, `npx shadcn@latest init` for setup + `npx shadcn@latest add <component>` per primitive, `components.json` config (style/baseColor/cssVariables/rsc/aliases). Custom tokens added by declaring the variable in `:root`/`.dark` and exposing via `@theme inline` — exactly the shape phase 17's `brand.yaml.tokens.css` produces for the default path.
- **`/radix-ui/primitives`** — Radix verified current: unstyled accessible React primitives; the canonical composition pattern is compound parts (`Dialog.Root` → `Dialog.Trigger` → `Dialog.Portal` → `Dialog.Overlay` → `Dialog.Content` → `Dialog.Title`/`Dialog.Description`/`Dialog.Close`); `Portal` is required for correct overlay layering; controlled + uncontrolled patterns both supported; animation is supported via presence management + `data-state` data attributes (style on `data-[state=open]`). shadcn wraps these with styled, token-fed defaults — surface Radix directly only for primitives shadcn doesn't expose.
- **`/tailwindlabs/tailwindcss.com`** — Tailwind v4 verified current: CSS-first `@theme` directive, OKLCH theme tokens become utility classes *and* CSS variables automatically. Same lookup as phase 17 (re-pulled fresh is fine; the scope is identical — the OKLCH `@theme` token API the components style against).
- **WebFetch — Anthropic `frontend-design` skill (upstream, if referenced by `skills/DESIGN-skill-uiuxpromax.md`):** UI/UX Pro Max's component element library composes against current frontend-design practice; the agent surfaces the upstream skill if the loaded design-skill flavor references it. (Not separately re-fetched here when the loaded skill already carries the guidance.)

Verify-at-phase-18 reminders (naming/version drift, per the design docs):

- NextUI → **HeroUI** rebrand in flight — verify package + docs via context7 before writing.
- Base UI extracted from `@mui/base` (deprecated path) and relaunched standalone — verify current package name + production-readiness via context7.
- Chakra v2 → v3 is a non-trivial migration — verify current version via context7; don't mix v2/v3 patterns.

Freshness date for this contract's references: **2026-05-18**.
