---
name: wb-maintain-iterate
description: This skill should be used by the website-maintainer for a MEDIUM design iteration on a live site — "tweak the colors", "adjust the spacing", "change the type scale", "refine the buttons", "update the design tokens", "re-touch these components", "the spacing feels off", "make it tighter/airier". Re-runs a phase-17 (design-system tweak) + selective phase-18 (component re-touch) pass WITHOUT re-doing discovery or brand identity. For changes within the existing brand. NOT for a full rebrand/new palette/new voice (that is wb-maintain-escalate) or simple content edits (wb-maintain-content).
version: 0.1.0
---

# wb-maintain-iterate — medium design iteration

> A medium iteration: adjust design tokens (palette shade, spacing scale, type scale, motion) and re-touch the affected components — without re-running discovery or changing the brand identity. The line: a *tweak within the brand* is this skill; a *new brand* is `wb-maintain-escalate`. Typically half a day to a day.

## When invoked

The user wants a visual refinement — tighter spacing, a refined button, a tweaked shade, a type-scale adjustment. The brand identity (palette intent, voice, logo) stays; the execution gets refined. If the request is a *new* palette / logo / voice, that's a brand change — escalate.

## Behavior

1. **Identify scope.** Which design tokens change (`brand.yaml.tokens` — colors / type / spacing / motion)? Which components are affected (`components.yaml` + the component code that references those tokens)? Be precise — a "spacing tweak" that touches every component is a bigger job than one that touches two.
2. **Confirm it's within the brand.** A shade adjustment of an existing primary is iteration. A *new* primary color, a new logo, a new voice — that's phase 5 + 17 brand territory; escalate via `wb-maintain-escalate`. State the line clearly to the user.
3. **Generate a diff preview.** Show before/after: the token change (palette swatch before/after, spacing/type values) and a visual diff of the affected components (Playwright screenshots before/after at key breakpoints). Let the user react before applying.
4. **User approves / adjusts.** Iterate on the preview until the user is happy. The taste decision is the user's; you surface grounded options, you don't decree.
5. **Apply.** Update `brand.yaml.tokens` (+ regenerate `brand.yaml.tokens.css`), regenerate/re-touch the affected component code (referencing the new tokens, `context7` for current framework docs). Keep everything composing from the tokens — no inline arbitrary values.
6. **Verify + deploy.** Re-run the responsive + a11y checks on the affected pages (contrast can break when a shade changes — re-check WCAG AA). Deploy on user confirmation.

## Time-box

**Half a day to one day.** A single-token tweak touching a couple of components is fast; a spacing-scale change rippling through every component is the upper end.

## Anti-patterns

- Letting an iteration become a rebrand (new palette/voice/logo → that's escalation, not iteration).
- Applying token changes without re-checking contrast (a shade tweak can break WCAG AA).
- Hardcoding the new value inline in components instead of updating the token (defeats the design system).
- Skipping the diff preview (the user should see before/after before it ships).
