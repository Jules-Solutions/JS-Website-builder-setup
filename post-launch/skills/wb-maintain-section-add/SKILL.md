---
name: wb-maintain-section-add
description: This skill should be used by the website-maintainer when the user wants to add a NEW section to an EXISTING page on a live site — "add a press-mentions section to the about page", "add a testimonials block", "put a FAQ on the services page", "add a logos strip to the homepage", "insert a new section between X and Y". For composing a new section onto a page that already exists, reusing or extending the design system. NOT for editing existing copy (wb-maintain-content), adding a new page (wb-maintain-page-add), or a design-token change (wb-maintain-iterate).
version: 0.1.0
---

# wb-maintain-section-add — add a section to an existing page

> Add a new section to a page that already exists — a press-mentions block, a testimonials strip, a FAQ. Composes from the existing design system; emits a handoff brief or writes the component code when the section needs a new component. Typically 1-3 hours.

## When invoked

The user wants a new section on an existing page. The page exists; the section is new. If the page itself is new, that's `wb-maintain-page-add`. If it's a token/visual change to existing sections, that's `wb-maintain-iterate`.

## Behavior

1. **Read the page + its sections.** `.website-builder/content/pages/{slug}.md` (the page MD, including its wireframe/section order) + `.website-builder/components.yaml` (available component shapes). Understand where the new section fits in the page's flow.
2. **Design the section.** Walk the user through: composition (which components, in what order), content (the actual copy, in brand voice), and placement (where in the section order). Surface 2-3 options when the user has no strong preference — grounded in the existing design system, never arbitrary.
3. **Component decision (per locked decision 35).** Does the section reuse existing components, or does it need a new one?
   - **Reuses existing** → compose from `components.yaml` shapes; no new component code.
   - **Needs a new component** → either write the component code directly in the site's stack (referencing the phase-17 design tokens, using `context7` for current framework/library docs), OR emit a structured JSON handoff brief (per `handoff-spec/component-request-v1.md`) the user can run through v0/ChatGPT/a freelancer, then ingest the result via phase 6.5. Default to writing it; brief-emit is opt-in per the user's request.
4. **Apply to project state.** Update the page MD (new section + updated section order), `components.yaml` (if a new component), and the component code. For multi-language sites, follow `config.yaml.translation_preference` for the new copy.
5. **Verify + deploy.** Render-check the page at all breakpoints (Playwright at 360/768/1280), confirm the new section composes cleanly + the design system holds, deploy on user confirmation.

## Time-box

**1-3 hours** for a new section. If it needs a genuinely new component plus several variants, it's at the upper end; if it reuses existing components, the lower end.

## Anti-patterns

- Writing a section that introduces off-system spacing/color/type (it must compose from phase-17 tokens).
- Skipping the responsive check (a section that looks right on desktop and breaks on mobile).
- Treating a section that actually needs a brand/design-system change as a section-add — escalate to `wb-maintain-iterate` or the full pipeline.
