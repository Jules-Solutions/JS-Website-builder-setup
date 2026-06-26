---
type: REFERENCE
corpus: design-systems
title: Radix Primitives + shadcn/ui Token Model
provenance:
  describes: "Radix Primitives (behavior) + shadcn/ui (the plugin's default component layer)"
  official_docs: "https://www.radix-ui.com / https://ui.shadcn.com"
  authored: "Original summary of publicly-documented guidelines (not a copy)"
  trademarks: '"Radix" (c) WorkOS; "shadcn/ui" (c) shadcn; both MIT-licensed; referenced, not bundled'
consumed_by_phases: [17, 18]
---

# Radix Primitives + shadcn/ui Token Model

The **default component library** for the website-builder's React path. Two layers:

- **Radix Primitives** — unstyled, fully-accessible behavior primitives (Dialog, Popover, Dropdown, Tabs, Accordion, …). They ship *no* visual design — only correct keyboard nav, focus management, ARIA, and state. They solve "the hard, invisible 80%."
- **shadcn/ui** — a set of components you **copy into your repo** (not an npm dependency) that style Radix primitives with Tailwind, using a **semantic CSS-variable** token system. You own the code, so you theme by editing variables.

This pairing is the plugin's default because it gives accessible behavior for free + full design control via tokens + no version-lock (the components live in the user's repo).

## Principles

- **Behavior and style are separate** — Radix owns behavior/accessibility; your tokens own appearance. You never reimplement focus traps or ARIA.
- **Own your components** — shadcn components are copied in, so the design system is fully editable, not a black box.
- **Semantic variables, not raw colors** — components reference role variables (`--primary`, `--muted`), so re-theming and dark mode are variable swaps.
- **Accessible by default** — every primitive ships WAI-ARIA-correct keyboard + screen-reader behavior.

## Token system (the part to copy exactly)

shadcn/ui defines a **semantic CSS-variable** layer — this is the canonical shape the plugin's `brand.yaml.tokens.css` emits:

| Variable pair | Role |
|---|---|
| `--background` / `--foreground` | page surface + text |
| `--card` / `--card-foreground` | card surface + text |
| `--popover` / `--popover-foreground` | floating surface + text |
| `--primary` / `--primary-foreground` | primary action + on-color |
| `--secondary` / `--secondary-foreground` | secondary action |
| `--muted` / `--muted-foreground` | subdued surface + de-emphasized text |
| `--accent` / `--accent-foreground` | hover/active accent |
| `--destructive` / `--destructive-foreground` | danger/delete |
| `--border` / `--input` / `--ring` | borders, field borders, focus ring |
| `--radius` | global corner-radius base |

- **Color form:** decimal-L OKLCH (`oklch(0.64 0.18 30)`) in current shadcn. The plugin matches this exactly — `brand.yaml.tokens.color.surface` ↔ these variables 1:1.
- **Dark mode:** a `.dark` selector re-binds the same variable names to a dark token set (matches `dark_mode.strategy: auto`). Components don't change — only the variables do.
- **Every `*-foreground` is contrast-guaranteed against its surface** — same on-color discipline as Material/Apple/Carbon, expressed as variable pairs.

## Strengths / trade-offs

- **Strength:** accessibility is handled by Radix (huge); theming is pure token-swapping; the component code is yours to extend. The semantic-variable model is the plugin's native output shape — zero translation.
- **Trade-off:** the *default* shadcn look (neutral, slightly-rounded, restrained) is now visually ubiquitous — "shadcn default" is a recognizable aesthetic. Differentiate via the brand's OKLCH ramp, font pairing, radius, and motion, or sites blur together.

## When to use / when not

- **Use** on essentially every React default-path build — accessible behavior + token theming is the plugin's sweet spot.
- **Consider alternatives** (DaisyUI, Park UI, Aceternity/Magic UI for motion-heavy) when the brief wants a distinctive look the agent would otherwise have to fight the shadcn defaults for. The behavior layer (Radix) stays useful regardless.

## How the website-builder agent applies it

This is the **target format** at phase 17: generate `brand.yaml.tokens` so the surface/semantic groups map directly onto the shadcn variable pairs above, in decimal-L OKLCH, with a `.dark` rebind. At phase 18, build components by copying shadcn primitives and binding them to the project's variables — never hard-code colors. Always keep the `*-foreground` contrast-pairing intact. To avoid the generic "shadcn default" look, push the brand layer (custom ramp hue/chroma, distinctive type pairing, intentional `--radius`, motion tokens) hard.
