# `reference-corpus/awesome-design-md-corpus/`

> A **curated subset** of `DESIGN.md`-style exemplars — focused, copy-and-reference design specs for well-known brand design systems. The agent greps these at phase 17 for color + typography + layout patterns when the user's chosen aesthetic resembles a known system ("make it feel like Linear," "clean like Stripe").

## What a `DESIGN.md` exemplar is

The pattern comes from **VoltAgent/awesome-design-md** — a curated collection of single-file design specs you drop into a project and tell an AI agent "build UI that matches this." Each file distills one brand's public design language into a compact, machine-readable brief: color tokens, typography, spacing, components, motion, and the "signature moves" that make the look recognizable. The website-builder uses them as *reference*, never as templates to clone outright.

## The 14 in this subset

Chosen as the highest-signal spread across the upstream's 73, covering the aesthetics small-site briefs most often invoke:

| File | Brand | Category | Recognizable for |
|---|---|---|---|
| `claude.md` | Claude (Anthropic) | AI / LLM | Warm, literary, paper-and-ink calm |
| `stripe.md` | Stripe | Fintech | Gradient hero, precise, developer-premium |
| `linear.md` | Linear | Productivity | Dark, fast, keyboard-first, purple glow |
| `vercel.md` | Vercel | Dev tools | Pure black/white, geometric, sharp |
| `notion.md` | Notion | Productivity | Friendly, editorial, monochrome + emoji |
| `figma.md` | Figma | Design tool | Playful-pro, multicolor, canvas energy |
| `shopify.md` | Shopify | E-commerce | Approachable, green, merchant-trust |
| `airbnb.md` | Airbnb | Travel / marketplace | Warm, rounded, Cereal, belonging |
| `spotify.md` | Spotify | Media | Bold dark, vibrant green, big imagery |
| `apple.md` | Apple | Tech / retail | Premium minimal, huge type, product-hero |
| `framer.md` | Framer | Design tool | Bold, motion-led, gradient |
| `supabase.md` | Supabase | Backend / dev | Dark, signature green, terminal-adjacent |
| `raycast.md` | Raycast | Dev tool | Sleek dark, glassy, command-palette |
| `nike.md` | Nike | Retail / athletic | Bold black/white, motion, attitude |

## Provenance & licensing

- **Upstream:** [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — a curated DESIGN.md collection, **MIT-licensed** (verified 2026-06-26; 73 exemplars in its `design-md/` directory).
- **What these files are:** the format and curation idea are adopted from the MIT-licensed upstream. Each file here is an **original, transformative summary** of the named brand's *publicly observable* design language (public site, public brand pages), written in the DESIGN.md style — **not** a verbatim copy of any upstream file or of any brand's private brand book. Per-file `provenance` frontmatter records the upstream repo + license, the brand's public source, and a pointer to the corresponding upstream `design-md/<brand>` entry.
- **Trademarks:** each brand name, logo, font, and color is © its owner and referenced descriptively (nominative use) for design-reference purposes. Fonts named are not bundled.
- **MIT attribution (upstream):** Copyright (c) VoltAgent — used under the MIT License. The plugin retains this attribution per the MIT terms.
- **Swapping for verbatim upstream:** because the upstream is MIT, the General may, post-merge, choose to replace these originals with verbatim upstream `design-md/*.md` files (with the MIT `LICENSE` + attribution committed alongside). This README's per-file provenance makes that swap clean. See `RPT-corpus-1.md` for the rationale behind shipping originals (consistency + lower trademark-copy risk) vs. verbatim.

## How the agent uses this dir

At **phase 17 (design system)**, when the user's aesthetic direction maps onto a known system, the agent reads the nearest exemplar(s) to ground concrete token choices (which hue, which type pairing, how much radius, how much motion) — then generates the project's *own* `brand.yaml.tokens`. These are inspiration + pattern references; the agent never ships a brand's actual palette as the user's brand.

## See also

- `../design-systems/` — foundational design *systems* (Material/Apple/Carbon/Tailwind/Radix).
- `${CLAUDE_PLUGIN_ROOT}/reference-corpus/ECOSYSTEM-CATALOG.md` line 273 — the catalogue entry for the upstream.
- `DESIGN-architecture.md` §333 — the spec this dir satisfies.
