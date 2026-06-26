---
type: REFERENCE
corpus: component-patterns
title: Form
component_slug: form
also_known_as: [contact form, lead-gen form, signup form, input form, web form]
consumed_by_phases: [9, 17, 18]
---

# Form

> A grouped set of labelled input controls that collects information from the visitor and submits it — a contact, lead-capture, or signup form is the primary on-page conversion mechanism for most sites.

## Purpose

The form is where intent becomes data. A marketing page exists to move a visitor toward an action, and for most service or B2B sites that action is "tell us who you are" — a contact or lead-gen submission. Because every extra field and every confusing error is a point of abandonment, a production form has to be ruthlessly clear: each control labelled, required fields obvious, errors explained inline at the point of failure and summarised at the top, and success unambiguous. The form converts attention into a qualified lead.

## When to use / when not

- **Use when:** the page needs structured input from the visitor — contact, quote request, newsletter signup, demo booking, multi-field application.
- **Avoid when:** a single action with no data needed (use a button/link), or when the data is better captured by a dedicated flow (checkout, multi-step wizard) — those have their own patterns. Don't bolt a 12-field form onto a hero when an email-only capture would convert better.

## Anatomy

| Part | Role |
|---|---|
| `<form>` element | The submission container with `action`/`method` (or a JS submit handler) |
| Error summary | A top-of-form region listing all current errors, each linking to its field (rendered after a failed submit) |
| Fieldset + legend | Groups related controls (e.g. an address block, a radio group) under a shared caption |
| Field block | One `label` + control + optional hint + optional inline error, repeated per input |
| Required indicator | Visual + programmatic marker on mandatory fields |
| Submit button | The `type="submit"` control that triggers validation + submission |
| Status / success region | A live region announcing submit success or a server-level failure |

## Content slots

| Slot | Required? | Source layer | Notes |
|---|---|---|---|
| Form title / intro | No | content/pages | Heading + sentence framing why to fill it in |
| Field set (labels, types, required flags) | Yes | components.yaml | The shape: each field's `name`, `label`, control type, `required`, `autocomplete` token |
| Field hint microcopy | No | content/strings | Per-field helper text wired via `aria-describedby` |
| Error message strings | Yes | content/strings | Per-rule messages (required, format, length); keep specific and human |
| Submit button label | Yes | content/strings | E.g. "Send message" — action-specific, not "Submit" |
| Success message | Yes | content/strings | Confirmation copy announced after submission |
| Submit target / endpoint | Yes | sitemap.yaml | Route or handler the form posts to |
| Token styling (focus, error, valid states) | Yes | brand.yaml | Border/focus-ring/error color tokens for control states |

## Accessibility requirements

Implements standard HTML form semantics plus the **WAI-ARIA APG error-handling guidance** (associated names, `aria-invalid`, `aria-describedby`, and an error summary).

- **Label association:** every control has a programmatically associated `<label for="id">` (preferred) — placeholder text is NOT a label and disappears on input. Group related controls (radio sets, checkbox sets, address blocks) in a `<fieldset>` with a `<legend>`; the legend is the group's accessible name and is read with each control.
- **Required indication:** mark mandatory fields with `required` (or `aria-required="true"` for custom controls) AND a visible indicator. If using a `*`, explain it once at the top ("* required"); never rely on color alone.
- **Autocomplete tokens:** add HTML `autocomplete` tokens (`name`, `email`, `tel`, `street-address`, `postal-code`, `organization`) so browsers and assistive tech can autofill — required for WCAG 2.2 SC 1.3.5 Identify Input Purpose.
- **Inline validation:** on a failed field, set `aria-invalid="true"` and point `aria-describedby` at the id of the visible error message (a field may describe-by both a hint and an error). Remove `aria-invalid` when corrected. Do not validate aggressively on every keystroke; validate on blur and on submit.
- **Error summary + focus management:** on a failed submit, render an error-summary region near the top, give it `role="alert"` or focus it programmatically (a container with `tabindex="-1"`), list each error as a link to the offending field's id, and move keyboard focus to the summary (or directly to the first invalid control). This is the APG-recommended pattern so keyboard and screen-reader users are taken straight to what to fix.
- **Success live region:** announce successful submission via a live region — `role="status"` (polite) for a confirmation message, so it's read without stealing focus. A page navigation to a thank-you page is also acceptable; if you do, ensure the new page's `h1` confirms success.
- **Keyboard:** every control is reachable and operable with `Tab`/`Shift+Tab` in DOM order; `Enter` submits from a text input; the submit button activates on `Enter` and `Space`. No keyboard trap.
- **Contrast & state:** label, hint, and error text meet 4.5:1; focus indicators meet WCAG 2.2 Focus Appearance; error state must be conveyed by more than red color (icon + text). Disabled-while-submitting buttons should not silently swallow `Enter`.

## Common variants

- **Contact form** — name, email, message; the canonical 3-field block.
- **Lead-gen / qualifier** — adds company, role, budget, or a select to score the lead.
- **Inline email capture** — single email + submit, often embedded in a hero or footer.
- **Multi-section** — multiple fieldsets (contact details + project details) on one page.
- **Stepped / wizard** — splits a long form across steps with a progress indicator (each step still follows these rules).
- **Inline-validated** — validates on blur with live per-field feedback as well as the submit-time summary.

## Pitfalls

- Using placeholder text as the only label — it vanishes on focus, fails contrast, and is not a reliable accessible name.
- Showing errors only by turning the border red, with no text and no `aria-invalid` — invisible to screen readers and to colorblind users.
- Validating on every keystroke so errors flash before the user has finished typing.
- A failed submit that doesn't move focus or summarise errors, leaving keyboard users to hunt for the broken field.
- Omitting `autocomplete` tokens, defeating browser autofill and failing SC 1.3.5.
- A success state that only changes a button color, with nothing announced to assistive tech.
