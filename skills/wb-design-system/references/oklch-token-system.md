# OKLCH token system — reference

> Loaded on demand during phase 17. The procedural workflow lives in `../SKILL.md`; this file is the OKLCH/contrast/token-schema depth. Do not duplicate procedure here — this is the *how the values are computed and shaped* reference.
>
> Substantive source of truth for phase 17 behavior: `Projects/Jules.Solutions/Subprojects/website-builder/phase-contracts/17-design-system.md`. This reference expands its `## What Claude must establish` and `## Reference materials` sections; it does not replace them. External research current as of **2026-05-18**.

## Why OKLCH (explain once to the user, then move on)

OKLCH = perceived **L**ightness, **C**hroma, **H**ue. Designed on human-vision principles (Björn Ottosson, 2020). The load-bearing property: **equal numeric steps in L look like equal brightness steps** — which is NOT true of HSL/HSV. That single property is what makes a generated color ramp coherent and a contrast-safe palette tractable.

It is also the **rendering target**, not a stylistic preference:

- Tailwind CSS v4 defines theme tokens CSS-first via the `@theme` directive, colors in OKLCH (verified current via context7 `/tailwindlabs/tailwindcss.com`, 2026-05-18). v4 ships a Display-P3 OKLCH default palette; the entire default color scale (`--color-red-500: oklch(63.7% 0.237 25.331)` … all hues × 50→950) is OKLCH.
- shadcn/ui (Tailwind v4 + React 19) themes entirely through OKLCH semantic CSS variables wired via `@theme inline` (verified current via context7 `/shadcn-ui/ui`, 2026-05-18).

So a hex stored in `brand.yaml.tokens` is wrong twice: it breaks the coherent-ramp property and it is not the shape phase 18 consumes. Convert and re-verify (naive hex→OKLCH can land out-of-gamut or hue-shift — verify, do not just convert). Store OKLCH only.

## The luminance-first method (how to actually build the ramp)

Current production practice (WebSearch "OKLCH color space design tokens production design systems 2026", 2026-05-18 — BoldVanta, Evil Martians, LogRocket, Bjango):

1. **Lock the lightness ladder first.** Decide the L values for the neutral ramp (e.g. `50→0.985`, `100→0.967`, … `900→0.205`, `950→0.13`) and for each text role *before* touching hue/chroma. The L ladder is the skeleton; everything else hangs off it.
2. **Layer hue + chroma for brand expression.** Apply the brand hue (H) and a chroma (C) appropriate to the role. UI/neutral ramps keep **C modest** (≤ ~0.04 for near-neutrals) to avoid eye strain. An **accent** can push C higher (0.15–0.30). Data-viz ramps can push highest.
3. **Build the contrast-safe palette by tuning C/h against a locked L.** For any text-on-surface pair, the L gap is the dominant contrast lever. Lock the text L, then adjust C/h to clear WCAG 2.2 — perceptual uniformity makes this predictable instead of trial-and-error.
4. **Single OKLCH source of truth.** Generate HSL/RGB only as a *legacy export* if ever needed. Never maintain a parallel hex table — it drifts.
5. **Progressive-enhance with an sRGB fallback under `@supports`** for old browsers if the brand pushes into Display-P3 chroma. Radix 3 and Tailwind v4 both moved to Display-P3 OKLCH — industry adoption is settled, but a graceful sRGB fallback is still polite for the long tail.

### OKLCH syntax forms (both are valid; be consistent within one file)

- Percent L + decimal C + degrees H: `oklch(63.7% 0.237 25.331)` (Tailwind v4 default-palette form)
- Decimal L + decimal C + H: `oklch(0.637 0.237 25.331)` (shadcn semantic-variable form)

The phase-17 contract's schema uses the decimal-L form (`oklch(0.64 0.18 30)`). Match the contract: **decimal-L form in `brand.yaml.tokens`**, and mirror whatever the chosen stack's scaffold uses in `brand.yaml.tokens.css` (shadcn path → decimal-L; matches `npx shadcn@latest init` output).

## Contrast: lock it at phase 17, do not defer to phase 21

The gate is non-overridable. WCAG 2.2 minimums to clear *here*:

| Pair class | Minimum ratio |
|---|---|
| Body text on its background | 4.5 : 1 |
| Large text (≥ 24px, or ≥ 18.66px bold) | 3 : 1 |
| Non-text UI (borders of inputs, focus ring, icon-only controls, component boundaries) | 3 : 1 |

Verify **every** text/background pair and **every** UI-component pair (not just primary-on-background). Common miss: `muted-foreground` on `muted` / on `background` — it is deliberately low-emphasis, which is exactly where 4.5:1 fails. Lock `muted-foreground`'s L high enough (lower L value = darker = more contrast on a light surface) and tune C down; do not let "it looks subtle enough" substitute for the measured ratio.

Method, using OKLCH's uniformity: hold the text L fixed, walk C and h until the computed contrast ratio clears the bar, then stop. Because L is perceptual, the ratio moves predictably with the L gap — no random hunting.

If a generated option looks great in the option round but a pair fails: that is not a "phase 21 will catch it" situation — it is the phase-17 gating failure phase 21 then pays for. Fix the L/C/h here; re-present if the fix visibly changes the option.

## Dark mode: deterministic L-inversion, produced here

If strategy is `auto` or `opt-in`, the dark token set exists in `brand.yaml.tokens` **before advance** (non-overridable gate). The inversion is deterministic:

- Surface roles invert across the L axis: light `background ≈ oklch(0.99 0 0)` → dark `background ≈ oklch(0.145 0 0)`; light `foreground ≈ oklch(0.145 0 0)` → dark `foreground ≈ oklch(0.985 0 0)`. (These exact values are the shadcn current defaults, verified via context7 2026-05-18 — use them as the neutral baseline, shift hue/chroma for brand.)
- Brand `primary` typically *lightens* in dark mode (a mid-L brand color on a near-black surface needs more L to keep contrast and presence). shadcn's neutral default flips `primary` from `oklch(0.205 0 0)` (light) to `oklch(0.922 0 0)` (dark) — same idea applies to a hued brand primary: raise L, keep H, often reduce C slightly.
- **Re-run the full contrast check on the dark set.** Light-mode-safe ≠ dark-mode-safe. `border: oklch(1 0 0 / 10%)` (alpha-on-dark) is shadcn's current dark-border pattern — borders often go to a low-alpha white in dark mode rather than a solid L.

"We'll add dark mode after launch" is the expensive path: phase 18 components and phase 19 pages are built against the token set; retrofitting a dark set after components exist costs far more than producing it here. The strategy decision (`auto` | `opt-in` | `none`) and, for the first two, the dark set, are locked at phase 17.

## Type scale — choose the ratio with intent

A modular scale multiplies a base size by a fixed ratio. The ratio is a **design decision tied to the phase-2 feel**, never a silent default (WebSearch "modular type scale ratios 2026", 2026-05-18 — LogRocket, Cieden, UX-Republic):

| Ratio | Name | Use when |
|---|---|---|
| 1.125 | Major Second | Very tight title/body difference — dense dashboards, data UIs |
| 1.250 | Major Third | Clear hierarchy, modest jump — safe interface default |
| 1.333 | Perfect Fourth | Versatile safe default — strong hierarchy without an extreme H1↔body jump |
| 1.500 | Perfect Fifth | More editorial drama |
| 1.618 | Golden Ratio | Largest contrast — writing-led / editorial / slow-pacing sites |

Tie the choice to the phase-2 feel statement and surface it: *"your phase-2 reference sites read editorial and slow, so I'm proposing Perfect Fourth (1.333) for a clear H1→body drama; a dense-dashboard feel would want Major Third or tighter — say the word and I'll reflow the scale."* Name the ratio in `brand.yaml.tokens` (`scale_ratio: 1.333`) so phase 18/19 inherit the *reasoning*, not just numbers.

Each scale step carries size + line-height + weight. Larger sizes get tighter line-height (1.1–1.2); body gets looser (1.5–1.6). Pick a display + body font **pairing** (distinctive display, refined body — per the frontend-design composable's typography heuristic), note the web-font source, and always specify a system-stack fallback (the chosen-stack's font-loading cost is a real engineering concern flagged in `DESIGN-skill-uiuxpromax.md` § Common failure modes — surface it on Hugo/static stacks).

## Spacing scale — one scale, used everywhere

A modular spacing scale on a base unit (typically 4px), expressed as an ordered token set: `[0, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128]`. The discipline is **one scale, no ad-hoc pixel values** — an arbitrary `padding: 13px` in phase 18/19 is a gating failure those phases inherit. Phase 17 commits the scale; phase 18 composes from it; phase 19 assembles from it.

## Motion tokens — pre-budget here so phase 22 finds no surprise

Minimum motion token set:

- `duration_default` (e.g. `240ms`) and `easing_default` (a cubic-bezier — Tailwind v4's `--ease-snappy: cubic-bezier(0.2,0,0,1)` is a good neutral default, verified via context7 2026-05-18).
- A stated motion **preference**: `subtle` | `expressive` | `minimal` — ties to the phase-2/5 brand stance.
- `prefers-reduced-motion` posture: under reduced-motion, duration → ~0ms, transitions degrade to opacity-only. **Budget this here** so phase 21's a11y audit verifies an already-correct posture instead of rediscovering it.
- If the chosen stack/library leans animation-heavy (Aceternity / Magic UI on React per `DESIGN-components-react.md`), pre-budget the hero-animation cost here so phase 22's perf audit finds no surprise. Motion is a design-system concern with a downstream perf and a11y bill — pay it at phase 17.

UI/UX Pro Max covers motion only at the token level (duration/easing); it does not teach motion *craft*. When motion is part of the brand identity, surface the Emil Kowalski + Framer Motion expansion flavors as an upgrade path (see `../SKILL.md` § Composable skills).

## Token schema interop note (W3C DTCG)

Current standards context (WebSearch "design system token schema 2026 W3C Design Tokens", 2026-05-18 — W3C DTCG, designtokens.org, Style Dictionary, Tokens Studio): the **Design Tokens Format Module reached its first stable version (2025.10)** — JSON interchange, media type `application/design-tokens+json`, extensions `.tokens` / `.tokens.json`, with theming + modern-color-space + cross-tool interop support. Style Dictionary v4 has first-class DTCG support (full 2025.10 support is v5 WIP); Tokens Studio exports need `@tokens-studio/sd-transforms`.

**For phase 17 the canonical artifact is `brand.yaml`'s `tokens:` key + the generated `brand.yaml.tokens.css`** (per the phase-17 contract `## Output artifacts`), NOT a `.tokens.json` DTCG file — the contract's schema is YAML-in-brand.yaml, stack-independent by construction. The DTCG awareness matters as an **export path**: if a user later wants Figma/Tokens-Studio round-tripping, the `tokens:` block maps cleanly to DTCG JSON (luminance-first OKLCH values + semantic role names are already DTCG-shaped). Mention this only if the user asks about Figma/design-tool interop; do not author DTCG files by default — that is scope creep beyond the contract.

## Reference exemplars (read, never import)

Per `DESIGN-resource-curation.md` + the phase-17 contract `## Reference materials`:

- `.website-builder/library/design-systems/` — Material 3 / Apple HIG / IBM Carbon excerpts. Read for **how a mature system maps semantic roles** (their role taxonomy), not for their specific colors.
- `.website-builder/library/awesome-design-md/` — DESIGN.md exemplars (Stripe / Shopify / Notion / Figma). A 10–20-entry aesthetic-matched subset auto-clones into `.website-builder/library/awesome-design-md/` at phase-17 entry (decision 42). Read for **how they articulate a system in prose**, not to copy.
- Template catalog (`DESIGN-templates-catalog.md`) — 3–5 stack-matched templates surfaced at phase-17 start for **aesthetic-vocabulary discussion only**. Studied, never shipped.

The discipline: exemplars expand the agent's and user's shared vocabulary for *reacting to options*. They are never a source the system is assembled from. The system comes from this project's phase-2 vision + phase-5 voice + the chosen design-skill flavor.

## Sources (external research, 2026-05-18)

Context7 (verified current):
- `/tailwindlabs/tailwindcss.com` — v4 `@theme` directive, OKLCH default palette, `--ease-*` tokens, CSS-variable auto-generation.
- `/shadcn-ui/ui` — OKLCH semantic CSS variables, `@theme inline` mapping, `:root`/`.dark` token sets, `--radius`, custom-role (`warning`) extension pattern.

WebSearch:
- [Designing Luminance-First Color Systems with OKLCH — BoldVanta](https://www.boldvanta.com/design/designing-luminance-cefirst-color-systems-with-oklch-tokens-ramps-and-real-ceworld-pitfalls.html)
- [OKLCH in CSS: why we quit RGB/HSL — Evil Martians](https://evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl)
- [OKLCH in CSS: Consistent, accessible color palettes — LogRocket](https://blog.logrocket.com/oklch-css-consistent-accessible-color-palettes)
- [Design systems need a colour space — Bjango](https://bjango.com/articles/designsystemcolourspace/)
- [Design Tokens Format Module 2025.10 — W3C DTCG](https://www.designtokens.org/tr/drafts/format/)
- [Design Tokens Community Group | Style Dictionary](https://styledictionary.com/info/dtcg/)
- [Token Format - W3C DTCG vs Legacy — Tokens Studio](https://docs.tokens.studio/manage-settings/token-format)
- [Typographic scaling — LogRocket](https://blog.logrocket.com/ux-design/typographic-scaling/)
- [Different type scale types — Cieden](https://cieden.com/book/sub-atomic/typography/different-type-scale-types)
- [Practical guide to modular scale type — UX-Republic](https://www.ux-republic.com/en/practical-guide-to-creating-a-modular-scale-type-for-your-interfaces/)
