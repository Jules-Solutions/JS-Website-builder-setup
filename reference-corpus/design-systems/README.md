# `reference-corpus/design-systems/`

> Reference docs for 5 mature, publicly-documented design systems. The agent reads these to learn how *systems* (not one-off palettes) are structured: token taxonomies, naming conventions, and the principles that hold a system together. Each doc captures token systems + principles + when-to-use — enough to apply the system's *thinking*, not to clone the system.

## What's here

| File | Design system | Owner | Best for |
|---|---|---|---|
| `material-3.md` | Material Design 3 (Material You) | Google | Dynamic/adaptive color, Android-leaning products, broad component coverage |
| `apple-hig.md` | Human Interface Guidelines | Apple | Clarity-first apps, premium feel, platform-native iOS/macOS web companions |
| `ibm-carbon.md` | Carbon Design System | IBM | Data-dense enterprise/B2B, dashboards, accessibility-critical products |
| `tailwind.md` | Tailwind CSS design scale | Tailwind Labs | The plugin's default build path; utility-first token mapping |
| `radix-shadcn.md` | Radix Primitives + shadcn/ui tokens | Radix / shadcn | The plugin's default component library; semantic CSS-variable theming |

## Why these five

The first three (Material 3, Apple HIG, Carbon) are the canonical "big" systems every designer references — they cover the spectrum from adaptive-consumer (Material) to clarity-premium (Apple) to data-enterprise (Carbon). The last two (Tailwind, Radix/shadcn) are the ones the **website-builder agent actually emits code against** on its default React/Tailwind/shadcn path — so their token shapes map 1:1 onto `brand.yaml.tokens` and the phase-18 build. A reference corpus that only had the famous-three would teach taste but not the plugin's own output format; including Tailwind + Radix/shadcn closes that gap.

## How the agent uses this dir

- **Phase 2 (vision) / Phase 5 (voice):** sample the *principles* sections to ground aesthetic direction in a coherent philosophy rather than arbitrary picks.
- **Phase 17 (design system creation):** read the *token system* sections as worked examples of color ramps, type scales, spacing, and motion — then generate the project's own `brand.yaml.tokens` (never copy a system's values; learn its structure).
- **Phase 18 (component design/build):** consult the *when-to-use* + *component conventions* sections when choosing component behavior and density.

## Provenance & licensing

Every file in this dir is **original reference prose** written for the website-builder plugin — a summary of each system's *publicly documented* guidelines, not a copy of any copyrighted documentation, token file, or asset. Each system's name, trademarks, fonts, and source documentation remain © their respective owners; links to the canonical docs are in each file's `provenance` frontmatter. The prose in this dir is plugin-owned and freely usable. Fonts named (Roboto, SF Pro, IBM Plex, Inter, etc.) are governed by their own licenses — the docs reference them, they are not bundled here.

## See also

- `../brand-examples/` — complete *brand* systems (voice + tokens + components) vs. these foundational *design* systems.
- `Workstreams/website-builder/foundation/DESIGN-architecture.md` §329 — the spec this dir satisfies.
- `skills/wb-design-system/references/oklch-token-system.md` — the plugin's OKLCH token mechanics.
