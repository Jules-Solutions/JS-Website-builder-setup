---
type: REFERENCE
corpus: design-systems
title: Apple Human Interface Guidelines
provenance:
  describes: "Apple Human Interface Guidelines (HIG)"
  official_docs: https://developer.apple.com/design/human-interface-guidelines
  authored: "Original summary of publicly-documented guidelines (not a copy)"
  trademarks: '"Apple", "SF Pro", "San Francisco" are (c) Apple; referenced, not bundled'
consumed_by_phases: [2, 17, 18]
---

# Apple Human Interface Guidelines (HIG)

Apple's design guidance across iOS, iPadOS, macOS, watchOS, visionOS, and tvOS. Less a token file than a *philosophy* with platform-specific rules. The most influential "premium/calm" reference in the industry — when a brief says "make it feel like Apple," this is the source.

## Principles

The HIG's three foundational themes (since iOS 7, still load-bearing):

- **Clarity** — text is legible at every size, icons are precise, adornment is subtle and in service of function. Negative space, color, and typography carry the design.
- **Deference** — the UI defers to content. Chrome recedes; content fills the screen. Translucency and blur hint at context without stealing attention.
- **Depth** — distinct visual layers and realistic motion convey hierarchy and give the interface life (sheets slide, layers parallax).

Supporting values: **consistency** (honor platform conventions so users transfer knowledge), **feedback** (every action acknowledged), **user control** (the user initiates and can cancel).

## Token system

Apple favors **semantic, adaptive** tokens over fixed hex values — this is the key idea to copy:

- **System colors** — `systemBlue`, `systemGreen`, `systemRed`, … that *shift* between light and dark mode automatically (`systemBlue` is a slightly different blue in dark mode for equal perceived vibrancy).
- **Semantic colors** — `label`, `secondaryLabel`, `tertiaryLabel`, `quaternaryLabel` (4 text emphasis levels); `systemBackground`, `secondarySystemBackground`, `tertiarySystemBackground`; `separator`, `fill`. Components reference *roles*, never raw colors, so dark mode and accessibility "just work."
- **Materials** — blur/vibrancy levels (`ultraThin` → `thick`) instead of flat fills for layered surfaces.

**Typography** — the San Francisco family (`SF Pro`, `SF Pro Display` ≥20pt, `SF Pro Text` <20pt, `SF Mono`, `New York` serif). **Dynamic Type**: 11 text styles (`largeTitle`, `title1–3`, `headline`, `body`, `callout`, `subheadline`, `footnote`, `caption1–2`) that scale with the user's accessibility text-size setting. The named-text-style approach maps directly onto the plugin's `typography.scale` roles.

**Spacing & layout** — an 8pt soft grid; generous margins; a minimum 44×44pt hit target (the web-relevant rule: tappable things must be comfortably large).

**Shape** — "continuous" (squircle) corner curvature rather than a simple radius; corner radius scales with element size.

**Motion** — physically-modeled, interruptible, spring-based animation. Motion communicates spatial relationships (where a sheet came from); it is never decorative. Honors Reduce Motion.

## Strengths / trade-offs

- **Strength:** the semantic-adaptive-color + named-text-style model produces effortless dark mode and best-in-class accessibility. The "content over chrome" discipline is the single most useful idea for premium/calm sites.
- **Trade-off:** SF Pro is licensed for Apple-platform UI, **not** for general web use — a web build must substitute (Inter is the canonical SF-alike). The guidance is also platform-app-shaped; translate, don't transplant, to the web.

## When to use / when not

- **Use** as the north star for premium, calm, content-first products; apps with companion marketing sites; anything where restraint signals quality.
- **Avoid** literal transplanting onto the web (don't ship iOS tab bars on a website), and don't use SF Pro on the web — substitute Inter/system-ui.

## How the website-builder agent applies it

Borrow the **semantic adaptive token** model: define `label`/`secondaryLabel`-style text-emphasis tiers (the plugin's `foreground` + `muted_foreground`), define backgrounds as a layered set, and let dark mode fall out of role swaps (matches `dark_mode.strategy: auto`). Adopt named text styles over ad-hoc sizes. Apply "clarity / deference / depth" as a tie-breaker when choosing how much chrome to add: less. On the default React build, substitute **Inter** for SF Pro and `ui-sans-serif, system-ui` as the fallback stack.
