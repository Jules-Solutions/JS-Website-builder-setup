# Token schema + CSS exemplars — reference

> Loaded on demand when writing `brand.yaml`'s `tokens:` key and the generated `brand.yaml.tokens.css`. Worked, copy-shaped examples. Procedure is in `../SKILL.md`; the OKLCH/contrast method is in `oklch-token-system.md`.
>
> Canonical schema authority: `Projects/Jules.Solutions/Subprojects/website-builder/phase-contracts/17-design-system.md` `## What Claude must establish` + `## Output artifacts`. These are filled-in instances of that schema. Do not invent fields not in the contract.

## `brand.yaml` — the `tokens:` key (full shape)

This is added to the existing `.website-builder/brand.yaml` (phase 5 already wrote `voice:`). Decimal-L OKLCH form throughout (matches the contract schema + shadcn scaffold).

```yaml
tokens:
  generated_at: 2026-05-18T14:32:00Z
  design_skill_flavor: ui-ux-pro-max     # the flavor that drove option-generation
  color_space: oklch
  color:
    primary:    "oklch(0.64 0.18 30)"
    secondary:  "oklch(0.72 0.05 200)"
    neutral:
      "50":  "oklch(0.985 0 0)"
      "100": "oklch(0.967 0 0)"
      "200": "oklch(0.922 0 0)"
      "300": "oklch(0.872 0 0)"
      "400": "oklch(0.704 0 0)"
      "500": "oklch(0.554 0 0)"
      "600": "oklch(0.446 0 0)"
      "700": "oklch(0.372 0 0)"
      "800": "oklch(0.279 0 0)"
      "900": "oklch(0.205 0 0)"
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
    scale_ratio: 1.333                   # Perfect Fourth — named with intent (phase-2 feel: editorial)
    scale:
      h1:    { size: "3.157rem", lh: "1.1", weight: 700 }
      h2:    { size: "2.369rem", lh: "1.2", weight: 700 }
      h3:    { size: "1.777rem", lh: "1.3", weight: 600 }
      body:  { size: "1rem",     lh: "1.6", weight: 400 }
      small: { size: "0.75rem",  lh: "1.5", weight: 400 }
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
    # dark_color: { ... }  generated alongside when strategy != none — see below
```

When `strategy != none`, add a `dark_color:` block mirroring the `color:` shape with the L-inverted set (the deterministic inversion is in `oklch-token-system.md` § Dark mode):

```yaml
  dark_mode:
    strategy: auto
    dark_color:
      primary:    "oklch(0.78 0.16 30)"   # raised L, same H, slightly lower C
      secondary:  "oklch(0.68 0.05 200)"
      surface:
        background:        "oklch(0.145 0 0)"
        foreground:        "oklch(0.985 0 0)"
        muted:             "oklch(0.205 0 0)"
        muted_foreground:  "oklch(0.708 0 0)"
        border:            "oklch(1 0 0 / 10%)"   # low-alpha white on dark
        ring:              "oklch(0.556 0 0)"
      semantic:
        success: "oklch(0.72 0.15 145)"
        warning: "oklch(0.82 0.12 80)"
        danger:  "oklch(0.70 0.19 22)"
        info:    "oklch(0.72 0.10 240)"
```

## `brand.yaml.tokens.css` — generated CSS custom properties

The same tokens emitted in the shape phase 18 consumes. For the React/Tailwind default path this mirrors the Tailwind v4 `@theme` + shadcn `@theme inline` semantic-variable scaffold (current canonical shape, verified via context7 `/tailwindlabs/tailwindcss.com` + `/shadcn-ui/ui`, 2026-05-18).

```css
/* .website-builder/brand.yaml.tokens.css
   Generated from brand.yaml `tokens:` at phase 17. Stack-independent values;
   phase 18 maps these into the chosen stack's theme mechanism.
   React/Tailwind path: this IS the @theme inline + :root/.dark scaffold
   `npx shadcn@latest init` expects. */

:root {
  --radius: 0.625rem;

  /* surface roles */
  --background:        oklch(0.99 0 0);
  --foreground:        oklch(0.15 0 0);
  --muted:             oklch(0.96 0 0);
  --muted-foreground:  oklch(0.45 0 0);
  --border:            oklch(0.92 0 0);
  --ring:              oklch(0.71 0 0);

  /* brand */
  --primary:            oklch(0.64 0.18 30);
  --primary-foreground: oklch(0.985 0 0);
  --secondary:          oklch(0.72 0.05 200);

  /* semantic */
  --success: oklch(0.70 0.15 145);
  --warning: oklch(0.80 0.12 80);
  --danger:  oklch(0.60 0.20 25);
  --info:    oklch(0.70 0.10 240);
}

.dark {
  --background:        oklch(0.145 0 0);
  --foreground:        oklch(0.985 0 0);
  --muted:             oklch(0.205 0 0);
  --muted-foreground:  oklch(0.708 0 0);
  --border:            oklch(1 0 0 / 10%);
  --ring:              oklch(0.556 0 0);

  --primary:            oklch(0.78 0.16 30);
  --primary-foreground: oklch(0.205 0 0);
  --secondary:          oklch(0.68 0.05 200);

  --success: oklch(0.72 0.15 145);
  --warning: oklch(0.82 0.12 80);
  --danger:  oklch(0.70 0.19 22);
  --info:    oklch(0.72 0.10 240);
}

/* Tailwind v4: expose tokens as utilities + custom properties.
   Phase 18 owns the actual @import / @theme inline wiring per chosen stack;
   this block documents the expected mapping. */
@theme inline {
  --color-background:        var(--background);
  --color-foreground:        var(--foreground);
  --color-muted:             var(--muted);
  --color-muted-foreground:  var(--muted-foreground);
  --color-border:            var(--border);
  --color-ring:              var(--ring);
  --color-primary:            var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-secondary:          var(--secondary);
  --color-success: var(--success);
  --color-warning: var(--warning);
  --color-danger:  var(--danger);
  --color-info:    var(--info);
  --radius-sm: calc(var(--radius) * 0.6);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) * 1.4);
}
```

Notes:
- The `@custom-variant dark (&:is(.dark *));` line and the `@import "tailwindcss";` / `@import "shadcn/tailwind.css";` lines are **phase-18 wiring**, not phase-17 output. Phase 17 emits the *values*; phase 18 maps them into the stack's theme entry point. Including the `@theme inline` block here is a documentation aid for phase 18, not a claim that phase 17 wires Tailwind.
- For a non-React stack (Framer / WordPress / static), the `:root` / `.dark` custom-property block still applies verbatim (it is plain CSS); only the `@theme inline` Tailwind-specific block is dropped or translated by phase 18's stack adapter.

## Adding a custom semantic role (when the brand needs one beyond the standard set)

shadcn's current pattern (verified via context7 `/shadcn-ui/ui`, 2026-05-18) — three coordinated edits, OKLCH, light + dark, then exposed:

```css
:root { --warning: oklch(0.84 0.16 84); --warning-foreground: oklch(0.28 0.07 46); }
.dark  { --warning: oklch(0.41 0.11 46); --warning-foreground: oklch(0.99 0.02 95); }
@theme inline { --color-warning: var(--warning); --color-warning-foreground: var(--warning-foreground); }
```

Every semantic color gets a paired `-foreground` (the on-color text color), both contrast-checked against each other (≥4.5:1 if text sits on it). A semantic color with no `-foreground` is incomplete.

## The override decision log (only when the arbitrary-color gate is overridden)

Written to `.website-builder/decisions/17-color-override.md` ONLY when the user insists on a specific color against vision fit, with the trade-off surfaced and confirmed. Shape:

```markdown
---
type: DECISION
phase: 17
decision: color-override
date: 2026-05-18
status: locked
---

# Phase 17 — color override

## What the user chose
User insisted on `#E63946` as the system primary.

## Trade-off surfaced (and confirmed by user)
Phase-2 feel statement: "calm, editorial, slow". `#E63946` → `oklch(0.62 0.22 24)` reads
loud/energetic against that feel. Presented: (a) it as system primary, (b) it demoted to
a single accent with a calmer primary, (c) a hue-shifted neighbour keeping the feeling.
User chose (a) with the trade-off understood.

## Resulting system
Primary stored as `oklch(0.62 0.22 24)` (converted from hex, gamut-verified). Coherent
system built around it (neutral ramp + semantic roles tuned to sit with the loud primary).
Contrast re-verified: all pairs clear WCAG 2.2.
```

The OKLCH gate, semantic-role gate, contrast gate, and dark-mode-completeness gate are **not** overridable — only the arbitrary-color gate is, and only via this logged, confirmed trade-off.
