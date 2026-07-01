---
phase: 17
name: Design system creation
group: design
pipeline_section: design
skill: wb-design-system
prev_phase: 16
next_phase: 18
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - DESIGN-phase-contracts.md
  - DESIGN-architecture.md
  - DESIGN-project-scaffold.md
  - DESIGN-content-layers.md
  - DESIGN-skill-uiuxpromax.md
  - DESIGN-context7-integration.md
  - DESIGN-resource-curation.md
  - ${CLAUDE_PLUGIN_ROOT}/reference-corpus/ECOSYSTEM-CATALOG.md
# library_clones_at_entry — auto-clone triggers read by wb_library.autoclone_for_state(trigger="phase-entry", phase=17).
# Schema: scripts/README.md § library_clones_at_entry. This is the Phase-5 WORKING EXAMPLE (per the contract,
# Captain P adds the field to phase 17 ONLY; the other 37 contracts are back-filled by a future follow-up INST).
# Triggers per DESIGN-resource-curation.md lines 234-242 + this contract's § Reference materials / § Output artifacts:
#   - the awesome-design-md exemplar corpus subset (always, at phase-17 entry, per decision 42)
#   - the chosen component-library reference (only when the user picked shadcn — load-bearing for the phase-18 build)
library_clones_at_entry:
  - resource: awesome-design-md
    as: awesome-design-md
    note: "10-20 most-relevant DESIGN.md exemplars for the chosen aesthetic (decision 42; § Output artifacts)"
  - resource: shadcn-components
    when: component_library == "shadcn"
    as: docs
    note: "shadcn/ui component reference for the phase-18 build (clone-into-project when shadcn picked)"
---

# Phase 17 — Design system creation

> Turn the brand into a system: color tokens, type scale, spacing, motion, dark-mode strategy — all in OKLCH, all token-first, all grounded in the phase-2 vision and the phase-5 voice. The phase where the site stops being words and structure and gets a coherent visual language. The agent refuses arbitrary color picks; it offers grounded options the user reacts to, then iterates. The chosen design-skill flavor (UI/UX Pro Max as MVP default) drives option-generation.

## Mission

Phase 16 finished the words. Phase 17 builds the system that will make those words look like a single, intentional thing. Not "pick a nice blue" — a *system*: a small set of design tokens (color, type, space, motion) that every component in phase 18 and every page in phase 19 composes from, so the whole site reads as one brand instead of forty disconnected screens.

The work product is `brand.yaml.tokens` plus a generated `brand.yaml.tokens.css` (CSS custom properties). The tokens are stack-independent by construction (per `DESIGN-architecture.md` § Stack-agnostic output design) — they survive a later stack switch because they are values, not framework code. Phase 18 maps them into the chosen stack's theme mechanism; phase 17 only commits the *values*.

The discipline of this phase is **grounded option-generation, not arbitrary preference**. A muggle who says "make it blue" is not wrong to have a preference — but a preference is not a system. The agent's job is to take the phase-2 vision (the reference URLs the user admired + the feel statement) and the phase-5 voice (the verbal identity) and the chosen design-skill flavor, and produce 3-5 *complete palette options* the user reacts to, each internally coherent (semantic roles mapped, contrast-safe, dark-mode-ready). The user picks and iterates; the agent never silently applies an off-brand favorite color, and never surfaces 161 raw palettes (decision-paralysis is a UX failure, per `DESIGN-skill-uiuxpromax.md` § Common failure modes).

Color is specified in **OKLCH**, not HSL/HSV/HEX. This is not a stylistic choice — it is the rendering target. Tailwind CSS v4 (the styling substrate for the React/Tailwind default path) defines its theme tokens in OKLCH via the `@theme` directive, and shadcn/ui's current theming scaffold is entirely OKLCH semantic CSS variables. OKLCH's perceptual uniformity (equal steps in lightness *look* equal across all hues — which is not true of HSL) is what makes a generated color ramp coherent and a contrast-safe palette tractable. The agent works in OKLCH from the first token.

## Entry conditions

- Phase 16 (copywriting) complete. Every content slot has finalized prose in the phase-5 brand voice; `.website-builder/content/pages/*.md` and `content/strings/*.json` have no placeholders. Phase 17 designs against *real content* — designing around lorem ipsum produces a system that breaks when real words arrive (the same structural-anchoring problem phase 14's skip causes, one layer up).
- Phase 2 (vision) complete. `.website-builder/project.yaml.vision` holds the 3-5 reference URLs the user admired, a sentence per URL on what they admired, the feel statement, and the adjective set. This is the primary grounding input for option-generation.
- Phase 5 (brand voice & tone) complete. `.website-builder/brand.yaml.voice` holds the voice description + attributes + exemplars. Visual identity must agree with verbal identity (a warm-contrarian voice does not get a cold-corporate palette).
- The design-skill flavor is known. The bootstrap skill (`wb-bootstrap`) recorded the user's primary design-skill flavor (UI/UX Pro Max by default per locked decision 55) plus any complementary flavors. If the user never picked, UI/UX Pro Max is the default and is loaded.
- If entry mode included artifact ingestion (phase 6.5 fired for `has-existing-site` / `has-Figma-file` / `has-ai-output`), the Stitch-extracted `DESIGN.md` / divmagic output / Figma-token export is loaded as the *seed*. Phase 17 extends from there rather than from a blank page — the agent surfaces the extracted tokens, reconciles them against the phase-2 vision (the old site may pre-date the articulated vision), and proceeds as a refine-and-extend pass.

## What Claude must establish

A complete, internally coherent design system written to `brand.yaml.tokens`, in five token groups:

1. **Color tokens (OKLCH).** Primary, secondary, and a neutral ramp (50→900 or equivalent), plus the semantic roles: `success`, `warning`, `danger`/`error`, `info`, and surface/on-surface pairs (`background`, `foreground`, `muted`, `muted-foreground`, `border`, `ring`). Every color is an OKLCH triple (`oklch(L C H)`). The ramp is generated luminance-first: lock the lightness ladder, then layer hue + chroma for brand expression (per current OKLCH design-system practice — see `## Reference materials`). UI ramps keep chroma modest to avoid eye strain; an accent can push chroma higher.

2. **Type scale.** A display + body font pairing (web-font source noted; system-stack fallback specified, per `DESIGN-skill-uiuxpromax.md`) and a **modular type scale of 4-6 sizes**, each with a line-height and weight. The agent picks a ratio with intent and names it: Major Third (1.250) and Perfect Fourth (1.333) are the safe interface defaults (clear hierarchy without an extreme jump between title sizes); Golden Ratio (1.618) for a larger, more editorial contrast. The agent does not silently default — it surfaces the ratio choice and ties it to the phase-2 feel ("editorial / slow pacing → larger ratio; dense UI → tighter ratio").

3. **Spacing scale.** A modular spacing scale on a base unit (typically 4px), expressed as an ordered token set (e.g., `0 4 8 12 16 24 32 48 64 96 128`). One scale, used everywhere — ad-hoc pixel values in phase 18/19 are a gating failure.

4. **Motion tokens.** A default duration and a default easing curve (cubic-bezier), plus a stated motion *preference* (`subtle` | `expressive` | `minimal`) and the `prefers-reduced-motion` posture (motion tokens degrade to near-zero duration under reduced-motion; this is pre-budgeted here so phase 21's a11y audit does not have to rediscover it). If the chosen stack/library leans animation-heavy (Aceternity/Magic UI per `DESIGN-components-react.md`), the agent pre-budgets the hero-animation cost here so phase 22's perf audit does not find a surprise.

5. **Dark-mode strategy.** One of `auto` (follows `prefers-color-scheme`), `opt-in` (a user toggle; this becomes a component spec in phase 18), or `none`. When `auto` or `opt-in`, the agent produces the dark token set alongside the light set (the OKLCH lightness inversion is deterministic and is part of this phase, not deferred).

Output schema in `.website-builder/brand.yaml`:

```yaml
tokens:
  generated_at: 2026-05-18T14:32:00Z
  design_skill_flavor: ui-ux-pro-max     # the flavor that drove option-generation
  color_space: oklch
  color:
    primary:    "oklch(0.64 0.18 30)"
    secondary:  "oklch(0.72 0.05 200)"
    neutral:
      "50":  "oklch(0.98 0 0)"
      "100": "oklch(0.96 0 0)"
      # ... ladder ...
      "900": "oklch(0.15 0 0)"
    semantic:
      success: "oklch(0.70 0.15 145)"
      warning: "oklch(0.80 0.12 80)"
      danger:  "oklch(0.60 0.20 25)"
      info:    "oklch(0.70 0.10 240)"
    surface:
      background:        "oklch(0.99 0 0)"
      foreground:        "oklch(0.15 0 0)"
      muted:             "oklch(0.96 0 0)"
      muted_foreground:  "oklch(0.45 0 0)"
      border:            "oklch(0.92 0 0)"
      ring:              "oklch(0.71 0 0)"
  typography:
    display: { family: "Fraunces", fallback: "serif", source: "google-fonts" }
    body:    { family: "Inter",    fallback: "sans-serif", source: "google-fonts" }
    scale_ratio: 1.333                   # Perfect Fourth — named with intent
    scale:
      h1:   { size: "3.157rem", lh: "1.1",  weight: 700 }
      h2:   { size: "2.369rem", lh: "1.2",  weight: 700 }
      h3:   { size: "1.777rem", lh: "1.3",  weight: 600 }
      body: { size: "1rem",     lh: "1.6",  weight: 400 }
      small:{ size: "0.75rem",  lh: "1.5",  weight: 400 }
  spacing:
    base_unit: "4px"
    scale: [0, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128]
  motion:
    duration_default: "240ms"
    easing_default:   "cubic-bezier(0.2, 0, 0, 1)"
    preference:       "subtle"
    reduced_motion:   "duration → 0ms; opacity-only transitions retained"
  dark_mode:
    strategy: auto                       # auto | opt-in | none
    # dark token set generated alongside light when strategy != none
```

The agent also generates `.website-builder/brand.yaml.tokens.css` — the same tokens emitted as CSS custom properties in the shape phase 18 will consume. For the React/Tailwind default path this mirrors the Tailwind v4 `@theme` + shadcn `@theme inline` semantic-variable scaffold (current canonical shape per context7; see `## Reference materials`):

```css
:root {
  --color-primary: oklch(0.64 0.18 30);
  --background:     oklch(0.99 0 0);
  --foreground:     oklch(0.15 0 0);
  /* ... full token set ... */
  --radius: 0.625rem;
}
.dark {
  --background: oklch(0.15 0 0);
  --foreground: oklch(0.98 0 0);
  /* ... dark inversions ... */
}
```

The agent updates `.website-builder/project.yaml.current_phase` to `18` upon user confirmation that the system reads true. Phase 18 (component design / build) loads next.

## Gating rules

The agent refuses to advance when:

- **Color was picked arbitrarily instead of generated.** A single hex the user named without a grounded option round is not a design system. The agent refuses to write `brand.yaml.tokens` from a bare preference; it generates 3-5 complete options grounded in phase-2 vision + phase-5 voice + the chosen design-skill flavor, the user reacts/picks, the agent iterates. (Override path below — the user can insist on a specific color *with the trade-off surfaced and confirmed*.)
- **Color is not in OKLCH.** HSL/HSV/HEX in `brand.yaml.tokens` is a hard fail. OKLCH is the rendering target (Tailwind v4 + shadcn current state) and the precondition for a coherent generated ramp and tractable contrast. The agent converts and re-verifies if a user supplies a hex; it does not store the hex.
- **No semantic role mapping.** A palette of named colors with no `primary`/`secondary`/surface/semantic role assignment is a swatch, not a system. Phase 18 components reference roles, not raw colors.
- **Contrast is not checked.** The agent verifies text/background pairs and UI-component pairs against WCAG 2.2 minimums (4.5:1 body text, 3:1 large text and non-text UI) *here*, locking lightness for text and adjusting chroma/hue to clear the bar. Phase 21 (a11y audit) re-verifies, but a system that ships known contrast failures into phase 18 is the gating failure phase 21 then pays for.
- **Dark-mode strategy undecided, or decided as auto/opt-in without the dark token set.** "We'll do dark mode later" is the failure phase 18/19/21 pay for. The strategy is decided here; if it is `auto` or `opt-in`, the dark token set exists in `brand.yaml.tokens` before advance.
- **The system contradicts the voice.** A warm, contrarian, human phase-5 voice paired with a cold corporate palette is voice/visual drift — the same class as phase 16's voice-drift gate, one layer over. The agent surfaces the mismatch and reconciles.

Override is available **only** on the arbitrary-color gate, and only via explicit user confirmation with the trade-off surfaced (the user genuinely may want their brand color even though it fights the vision — that is their call to make, logged to `.website-builder/decisions/17-color-override.md`). The OKLCH gate, the semantic-role gate, the contrast gate, and the dark-mode-completeness gate are not overridable — they are correctness prerequisites for phase 18.

## Tools and skills used

- **`AskUserQuestion`** — the primary tool. Used to surface the 3-5 grounded palette options, the type-pairing options, the scale-ratio choice, the dark-mode-strategy decision, and each iteration round. The user reacts; the agent does not interrogate.
- **The design-skill flavor (loaded skill)** — UI/UX Pro Max by default (per locked decision 55). It drives palette generation (narrowing its 161 palettes to 3-5 grounded in phase-2 vision + phase-5 voice + chosen style), the 57 font pairings, the 50+ aesthetic styles, the 99 UX guidelines (spacing rhythm, type rhythm, motion timing). The agent invokes it with design verbs (`design`, `create`, `plan`). See `DESIGN-skill-uiuxpromax.md` for the full surface and the expansion-flavor composition rules.
- **`mcp__context7__resolve-library-id` + `mcp__context7__query-docs`** — for the current Tailwind CSS v4 token API (the OKLCH `@theme` directive, the `@theme inline` semantic-variable pattern shadcn uses). Per `DESIGN-context7-integration.md`, context7 fires here because the agent works with a *named* technology (Tailwind v4) whose token API has changed materially (v3 JS config → v4 CSS-first `@theme`). The agent verifies the current syntax rather than trusting training data.
- **Reference-data load** — `${CLAUDE_PLUGIN_ROOT}/reference-corpus/design-systems/` (Material 3 / Apple HIG excerpts / IBM Carbon as structural exemplars), `.website-builder/library/awesome-design-md/` (DESIGN.md exemplars from Stripe / Shopify / Notion / etc. — a 10-20-entry subset auto-cloned at phase 17 entry per decision 42, chosen by the user's aesthetic direction). Per `DESIGN-resource-curation.md`, these are inspiration exemplars the agent reads — never templates it imports.
- **Stitch / divmagic / Figma-token output (from phase 6.5, if applicable)** — when entry mode ingested an artifact, the extracted token seed is loaded and extended.
- **Template inspiration (read-only)** — per `DESIGN-templates-catalog.md`, the agent surfaces 3-5 stack-matched templates at the start of phase 17 *for aesthetic-vocabulary discussion only*, never to import. Templates are studied, never shipped.
- **`Write` / `Edit`** — to write `brand.yaml.tokens` + `brand.yaml.tokens.css`, and to iterate them across review rounds.

The `wb-design-system` phase-group skill is loaded at entry; it carries this contract as its instruction body and the cross-phase contract that the tokens here are exactly what phase 18 maps into the chosen stack's theme. No re-architecting downstream — the values are locked here.

The JSON handoff protocol may optionally be invoked here (per `DESIGN-handoff-protocol.md` § Phase contracts that invoke this protocol): the agent can emit a `DESIGN.md`-shaped brief to an external tool for parallel design exploration, then ingest the result via phase 6.5 as alternate options. This is opt-in, not default.

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| `.website-builder/brand.yaml` | adds `tokens:` key per the schema above | The design system — color (OKLCH), type scale, spacing, motion, dark-mode. Load-bearing for every phase 18 component + every phase 19 page. |
| `.website-builder/brand.yaml.tokens.css` | CSS custom properties (Tailwind v4 `@theme` / shadcn `@theme inline` shape for the React-Tailwind path) | The generated CSS-variable form phase 18 consumes directly. |
| `.website-builder/library/awesome-design-md/` *(auto-cloned subset)* | exemplar DESIGN.md files | The 10-20 most-relevant design exemplars for the chosen aesthetic; read for inspiration, not imported. |
| `.website-builder/decisions/17-color-override.md` *(only if overridden)* | standard decision-doc frontmatter + surfaced-trade-off + user confirmation | Logged only when the user overrode the grounded-option gate with a specific color against vision fit. |

The `tokens:` block is the only always-required artifact. The override decision log is produced only when the override gate fires.

## Common failure modes

**"Just make it look good — you pick the colors."** The premature-handoff move (same anti-pattern phase 1 and phase 16 name). The agent does not invent the brand's visual identity from nothing: *"the look has to come from your project, not my taste, or it'll read like every other AI-built site. You showed me three sites you admired at phase 2 and we captured your voice at phase 5 — I'll generate options grounded in those, and you tell me which one is yours."* The agent generates the grounded options rather than picking unilaterally.

**Decision paralysis from too many options.** The design skill carries 161 palettes; surfacing them raw is a UX failure (per `DESIGN-skill-uiuxpromax.md`). The agent narrows to 3-5, each a *complete* coherent system (not 5 primary hues — 5 full role-mapped systems), each tied back to a phase-2 reference or feel adjective so the user reacts with grounded reasons, not vibes.

**"My favorite color is this exact hex — use it everywhere."** The aesthetic-as-system substitution. The agent does not refuse the preference outright; it surfaces the trade-off: *"that color against your phase-2 'calm, editorial, slow' feel reads loud — here's it as the system primary, here's it demoted to a single accent with a calmer primary, here's a hue-shifted neighbour that keeps the feeling you like but fits the vision. Your call — but I want you to see the trade before we lock it."* If the user still wants the literal hex as primary, the agent converts it to OKLCH, builds the coherent system around it, and logs `decisions/17-color-override.md`.

**Style + audience mismatch.** User picks brutalism for an enterprise-SaaS dashboard, or glassmorphism for a law firm. The agent surfaces the audience-fit risk (per `DESIGN-skill-uiuxpromax.md` § Common failure modes) and offers alternatives; it refuses to silently apply a style that fights the phase-3 audience.

**HSL/HEX habit.** The user (or a pasted artifact) supplies colors in hex. The agent converts to OKLCH, re-checks gamut (naive hex→OKLCH conversion can land out-of-gamut or hue-shift — the agent verifies, not just converts), and stores OKLCH. It explains once *why* (perceptual uniformity → coherent ramp + tractable contrast; OKLCH is the Tailwind-v4/shadcn rendering target) so the user understands the system, then moves on.

**Type scale chosen by reflex, not intent.** The agent defaults silently to 1.250 without tying it to the project. Correct behavior: surface the ratio choice, name it, and connect it to the phase-2 feel — a writing-led editorial site wants a larger ratio (more drama between H1 and body); a dense dashboard wants a tighter one (less title/body jump). The ratio is a design decision, not a default.

**Dark mode deferred.** "We'll add dark mode after launch." The agent surfaces that dark-mode strategy is structural — phase 18 components and phase 19 pages are built against the token set, and retrofitting a dark set after components exist is the expensive path. The strategy (and, for auto/opt-in, the dark token set) is decided here.

**Contrast discovered at phase 21 instead of locked at phase 17.** The agent ships a palette that looks good in the option round but fails 4.5:1 on muted text. Correct behavior: lock text lightness and tune chroma/hue to clear WCAG 2.2 *here*, using OKLCH's perceptual-uniformity property to do it predictably. Phase 21 then verifies a system that was already contrast-safe by construction.

**Hidden assumption that the design system is the design.** It is not. The agent surfaces, when needed, that `brand.yaml.tokens` is the *vocabulary*; phase 18 builds the components that speak it and phase 19 assembles the pages. A token file that "looks complete" is still pre-component.

**Treating the design-skill flavor's defaults as the brand.** UI/UX Pro Max is broad-coverage; a site built on its raw defaults can feel generic (the default-aesthetic risk in `DESIGN-skill-uiuxpromax.md` § Limitations). The agent grounds every option in *this* project's phase-2 vision + phase-5 voice, and surfaces complementary-flavor options where the brand wants a sharper stance (see expansion flavors below).

## Reference materials

Foundation + skill docs:

- `DESIGN-phase-contracts.md` § 17 — the seed for this contract.
- `DESIGN-architecture.md` § Stack-agnostic output design — why tokens are stack-independent and survive a stack switch; § Resource curation pattern; § context7 integration.
- `DESIGN-project-scaffold.md` § `brand.yaml` — the `tokens:` key schema.
- `DESIGN-content-layers.md` — Layer 1 (design tokens); phase 17 is where Layer 1 is established and every later layer composes against it.
- `DESIGN-skill-uiuxpromax.md` — **the MVP primary design-skill flavor (locked decision 55)**. The 50+ styles, 161 palettes, 57 font pairings, 99 UX guidelines, 25 chart types it provides; the option-narrowing discipline; the composition + conflict-resolution rules with complementary flavors.

Design-skill flavor scope (locked decision 55):

- **Primary MVP flavor — UI/UX Pro Max.** Drives all option-generation in this contract. The agent invokes it for palette/font/spacing/motion option-generation, narrowed to 3-5 grounded options.
- **Expansion flavors (beyond MVP — surfaced as upgrade paths, not used by default):**
  - *Impeccable* — splits design rules for marketing pages vs product UI within one site; layer on when the site has a distinct app surface and marketing surface (per `skills/DESIGN-skill-impeccable.md`).
  - *Emil Kowalski* — motion taste + design-engineering depth; layer on when motion is part of the brand and UI/UX Pro Max's motion-token level is not enough (per `skills/DESIGN-skill-emil-kowalski.md`).
  - *Taste* — flavor variants (taste / soft / minimalist / brutalist) that *override* palette/font defaults when the user has taken a definite aesthetic stance (per `skills/DESIGN-skill-taste.md`).
  - *21st.dev Magic* — agent-UX component patterns; layer on when the site itself includes agent-driven features (per `skills/DESIGN-skill-21st-dev.md`).
  - *Framer Motion* — animation-API companion on React stacks, paired with Emil's lens (per `skills/DESIGN-skill-framer-motion.md`).
  Conflict-resolution default: the more specialized loaded flavor wins on the axis it specializes; UI/UX Pro Max keeps authority over product-type/archetype breadth.

context7 / WebSearch / WebFetch (mandatory at this phase — citations are current as of the freshness date below):

- **context7 `/tailwindlabs/tailwindcss.com`** — Tailwind CSS v4. Verified current: theme tokens are defined CSS-first via the `@theme` directive (replacing the v3 `tailwind.config.js` approach), colors specified in **OKLCH**, e.g. `@theme { --color-avocado-500: oklch(0.84 0.18 117.33); --ease-snappy: cubic-bezier(0.2,0,0,1); }`. Theme variables become utility classes *and* CSS custom properties automatically. Tailwind v4 ships a Display-P3 OKLCH palette by default. This is the rendering target the `brand.yaml.tokens.css` mirrors for the React-Tailwind path.
- **context7 `/shadcn-ui/ui`** — shadcn/ui. Verified current: built on Tailwind CSS v4 + React 19; theming is a semantic CSS-variable system with **OKLCH** defaults (`:root { --background: oklch(1 0 0); --primary: oklch(0.205 0 0); ... } .dark { ... }`) wired through `@theme inline`; `npx shadcn@latest init` scaffolds it; custom tokens (e.g. a `warning` role) are added by declaring the variable in `:root`/`.dark` and exposing it via `@theme inline`. This is the exact shape phase 18 expects `brand.yaml.tokens.css` to be in for the default path.
- **WebSearch "OKLCH color space design tokens production design systems 2026"** — current practice: keep a single OKLCH source of truth (generate HSL/RGB only for legacy export); design luminance-first (lock the L ladder, then layer hue + chroma); UI ramps keep chroma modest, data-viz/accent ramps can push it; build the contrast-safe palette by locking L for text and tuning C/h to meet WCAG 2.2 (4.5:1 body, 3:1 large/UI); progressive-enhance with an sRGB fallback under `@supports` for older browsers; Radix 3 and Tailwind v4 both moved to Display-P3 OKLCH (industry adoption confirmed). Sources: [Designing Luminance-First Color Systems with OKLCH — BoldVanta](https://www.boldvanta.com/design/designing-luminance-cefirst-color-systems-with-oklch-tokens-ramps-and-real-ceworld-pitfalls.html), [OKLCH in CSS: why we quit RGB/HSL — Evil Martians](https://evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl), [How to Use OKLCH in CSS (2026 Guide) — HexPickr](https://hexpickr.com/learn/oklch-css-guide), [Design systems need a colour space — Bjango](https://bjango.com/articles/designsystemcolourspace/).
- **WebSearch "modular type scale ratios 2026"** — current practice: a modular scale multiplies a base size by a fixed ratio; Major Third (1.250) and Major Second (1.125) for tight title/body difference, Perfect Fourth (1.333) as the safe versatile default, Golden Ratio (1.618) / Perfect Fifth for editorial drama. Choose the ratio from the desired title-to-body contrast, which the agent ties to the phase-2 feel. Sources: [Typographic scaling — LogRocket](https://blog.logrocket.com/ux-design/typographic-scaling/), [Different type scale types — Cieden](https://cieden.com/book/sub-atomic/typography/different-type-scale-types), [Practical guide to modular scale type — UX-Republic](https://www.ux-republic.com/en/practical-guide-to-creating-a-modular-scale-type-for-your-interfaces/).

Inspiration corpus (read, never imported):

- `${CLAUDE_PLUGIN_ROOT}/reference-corpus/design-systems/` — Material 3 / Apple HIG / IBM Carbon excerpts as structural exemplars (how a mature system maps roles).
- `.website-builder/library/awesome-design-md/` — DESIGN.md exemplars (Stripe / Shopify / Notion / Figma etc.); a 10-20-entry aesthetic-matched subset auto-clones into `.website-builder/library/awesome-design-md/` at phase-17 entry per decision 42.
- Template catalog (per `DESIGN-templates-catalog.md`) — stack-matched templates surfaced for aesthetic-vocabulary discussion at phase-17 start. Studied, never shipped.

Freshness date for this contract's references: **2026-05-18**.
