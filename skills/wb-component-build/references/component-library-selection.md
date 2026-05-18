# Component-library selection — full per-stack-class logic

> Loaded on demand during phase 18 when the agent runs component-library selection. The canonical source is the per-ecosystem design docs (`Workstreams/website-builder/components/DESIGN-components-{react,tailwind,headless,vue,svelte}.md`) — read those for per-library detail (install commands, codegen patterns, limitations, failure modes). This reference is the consolidated selection-decision layer.

## The selection contract

At phase 18 entry, after the stack is known (phase 11) and the design system exists (phase 17):

1. Determine the stack-class (React / non-React-Tailwind / Vue / Svelte / headless-from-scratch).
2. Run the matching decision tree below.
3. **Surface the default + 1–2 alternatives with trade-offs via `AskUserQuestion`.** Never pick silently. The user picks.
4. Record: `project.yaml.component_library: { primary: <lib>, complementary: [<lib>] }`.

The composition rules (below) are enforced regardless of which library is chosen.

## React stacks (Next.js / Astro+React / Vite+React / Remix)

```
IF no strong preference:
    primary  = shadcn/ui          (copy-paste; user owns code; AI-aware; Radix-or-BaseUI-backed
                                    a11y; Tailwind-v4 + OKLCH aligns exactly with phase-17 output)
    propose  Magic UI as animation companion  IF site has motion-heavy sections
    propose  Aceternity UI                     IF phase-2 vision leaned premium/agency/portfolio
IF "everything out of the box"      → Mantine        (120+ components + forms + hooks; least DIY)
IF "rapid prototyping"              → Chakra UI      (style props fastest to write)
IF admin / dashboard / dense data   → Ant Design OR Material UI
IF consumer app + smooth motion     → NextUI/HeroUI  (VERIFY name via context7 — rebrand in flight)
IF Material Design adherence        → Material UI
IF Material foundations, own brand  → Joy UI
IF brand-customization velocity     → Once UI        (Next-first; token-driven)
```

Most-recommended default composition: **shadcn/ui + Magic UI** (structural primitives + motion micro-components, same copy-paste Tailwind philosophy). **shadcn/ui + Aceternity UI** for portfolio/agency. **shadcn/ui + Ant Design** for marketing+admin hybrid (shadcn on marketing pages, Ant on `/admin/*`).

Per-library detail: `Workstreams/website-builder/components/DESIGN-components-react.md`.

## Non-React Tailwind stacks (Hugo / Astro-pure / static-HTML / WordPress-Tailwind)

```
IF fastest-to-ship CSS-only         → DaisyUI        (best for muggles; ~88% fewer classes;
                                                       35+ themes; works in any Tailwind project)
IF $299 budget + pro templates now  → Tailwind UI    (SURFACE THE $299 COST EXPLICITLY; per-dev
                                                       license; use as starting structure)
IF behavior-primitive separation    → Park UI        (Ark UI + Panda/Tailwind; multi-framework)
```

DaisyUI ships **no JS interactivity** — modals/dropdowns/tabs use CSS-only patterns (checkbox-hack, focus-within). For richer interactivity, pair with **Headless UI** (React/Vue) or **Alpine.js** / **Stimulus** (non-React). Lock the interactivity strategy at phase 17, before phase 18 writes markup. DaisyUI's a11y varies per component — run phase 21 aggressively + add ARIA manually where the default isn't enough.

Per-library detail: `Workstreams/website-builder/components/DESIGN-components-tailwind.md`.

## Vue stacks (Nuxt / Vite+Vue / Astro+Vue islands)

```
IF Material Design aesthetic        → Vuetify        (best-supported Material in Vue)
IF comprehensive + token brand      → PrimeVue       (Aura theme; deepest Vue library; Volt
                                                       unstyled mode for Tailwind-driven projects)
IF admin / dense data               → Element Plus   (desktop-enterprise sweet spot)
IF Tailwind-driven                  → PrimeVue+Volt OR DaisyUI OR shadcn-vue (verify maturity)
IF picked Quasar at phase 11        → Quasar's components ARE the library (no separate decision)
IF interactive primitives needed    → Headless UI Vue is always a viable pair
```

Vue ecosystem strongly prefers **single-library architecture** (no clear shadcn equivalent — `shadcn-vue` is a community port, maturity varies). Lean single-library unless the user has a specific compose reason. Up to **one** complementary library max for Vue (not two).

Per-library detail: `Workstreams/website-builder/components/DESIGN-components-vue.md`.

## Svelte / SvelteKit stacks

```
IF comprehensive out of the box     → Skeleton UI    (Mantine analog; design system + components)
IF source-ownership shadcn-style    → Bits UI / shadcn-svelte  (VERIFY current CLI/package via
                                                       context7 — Svelte ecosystem in flux here)
IF total visual freedom, headless   → Melt UI        (the Svelte Radix; "builders" API)
IF Tailwind class-shortcuts too     → DaisyUI pairs with any of the above
```

Use Svelte 5 runes (`$state`/`$derived`/`$effect`) for new code; verify library compatibility via context7 (some library docs still show Svelte 4 patterns). Svelte ships first-class `transition:`/`in:`/`out:`/`animate:` directives — use these for in/out motion by default; reserve Motion/GSAP for complex orchestration only.

Per-library detail: `Workstreams/website-builder/components/DESIGN-components-svelte.md`.

## Headless / unstyled primitives (total control / missing primitive / design system from scratch)

```
IF shadcn is primary:
    Radix is automatically present (shadcn imports from Radix). Surface Radix directly ONLY for
    a primitive shadcn doesn't wrap (AspectRatio.Root, ScrollArea.Root).
IF total control + Tailwind + minimal deps + small component set → Headless UI (~10-16 components)
IF a primitive Headless UI / Radix don't cover well             → Base UI (verify package + maturity)
IF building everything from scratch + full breadth              → Radix (28+) OR Base UI
```

**Maintenance-drift note (verify at every phase-18 entry via context7 — do NOT bake either as canonical):** as of 2026-05, Radix was acquired by WorkOS and update velocity slowed for some complex components (Combobox, multi-select commonly cited). Base UI (MUI-team, full-time engineering backing) is now the more actively-maintained primitive layer, and shadcn/ui has a Base UI path in addition to its Radix path. This extends the design doc's standing "verify Base UI package name + production-readiness via context7" warning to "verify Radix maintenance status too, and surface the Radix-vs-Base-UI trade-off to the user with current context7 data." The decision is the user's; the agent's job is current, accurate trade-off data — not a frozen recommendation. Headless UI remains the Tailwind-team's small (~10-16) accessible set.

Per-library detail: `Workstreams/website-builder/components/DESIGN-components-headless.md`. WAI-ARIA Authoring Practices is the spec the headless libs implement: https://www.w3.org/WAI/ARIA/apg/.

## Composition rules (enforced — independent of library choice)

1. **One primary library per project.** Handles forms, navigation, modals, common UI.
2. **Up to two complementary libraries** for specialized concerns (motion, data tables). React allows two; Vue/Svelte the norm is one. More than the cap risks design incoherence — this cap is the antidote to the every-shadcn-Aceternity-MagicUI mashup (per locked decision 46).
3. **`brand.yaml` tokens drive ALL libraries.** `brand.yaml` is SSOT. Mixing a library's own brand preset (Mantine's defaults, Ant's design language, a DaisyUI bundled theme un-overridden) is forbidden. Every library imports from phase-17 tokens.
4. **Never double-wrap.** Radix directly *or* via shadcn for the same primitive, not both. Melt UI directly *or* via Bits UI, not both. Base UI *or* MUI core for the same purpose, not both.
5. **Compose blocks from primitives.** The 2026 shadcn composition model: blocks are reusable UI sections (pricing, feature grid, auth form, data table) built from primitives, sitting between raw primitives and full pages. Build composites this way, not by stacking whole libraries.

## Migration between libraries (phase-18 re-entry on a switch)

Portable across a switch: `brand.yaml` tokens, `components.yaml` specs, `content/`, `sitemap.yaml`/`sections.yaml`. NOT portable: component code, library-specific theme objects, form-handling (RHF+shadcn vs Mantine `useForm` vs Ant `Form` are not interchangeable), a11y verification (re-run phase 21).

Recipe: record the migration in `decisions/{NN}-component-library-switch.md`; regenerate each `components.yaml` entry with the new library's primitives; regenerate the theme integration; re-run phase 21 (a11y) + phase 22 (perf); remove the old library + components in a **separate commit** so git history shows the switch. Surface the cost first — typically 0.5–3 days for a mid-sized site depending on component count and ecosystem.
