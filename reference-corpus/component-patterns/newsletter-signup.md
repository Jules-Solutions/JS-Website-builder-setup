---
type: REFERENCE
corpus: component-patterns
title: Newsletter Signup
component_slug: newsletter-signup
also_known_as: [email capture, subscribe form, mailing-list signup, lead capture, email opt-in]
consumed_by_phases: [9, 17, 18]
---

# Newsletter Signup

> A small email-capture form — typically one email field, a submit button, and consent microcopy — used to convert anonymous visitors into a contactable audience.

## Purpose

A newsletter signup turns traffic into a relationship. Most visitors are not ready to buy, but many will trade an email for ongoing value, so the signup captures a low-commitment yes and keeps the brand in front of them over time. It works by minimizing friction (ideally one field), making the value explicit ("Monthly tips, no spam"), and handling consent honestly. A page uses it in the footer for persistent reach, inside a CTA section to capitalize on engagement, or as a standalone band on content pages.

## When to use / when not

- **Use when:** you publish recurring content (newsletter, updates, drops) and want to build an owned audience you can reach without paying for re-acquisition.
- **Avoid when:** you have nothing to send or no consent/processing path — collecting emails you never use erodes trust and may breach data law. Avoid stacking it with competing primary CTAs that pull attention from a higher-value action on the same screen.

## Anatomy

| Part | Role |
|---|---|
| Form wrapper | The `<form>` grouping the inputs and submit |
| Prompt / heading | The value proposition for subscribing |
| Email field + label | The single required input |
| Submit button | Triggers the subscription |
| Consent microcopy | Privacy / GDPR statement or checkbox |
| Status region | Live area announcing success or error |

## Content slots

| Slot | Required? | Source layer | Notes |
|---|---|---|---|
| Prompt / heading | Yes | content/strings | "Get monthly tips"; sets the value |
| Email field label | Yes | content/strings | Visible label; e.g. "Email address" |
| Placeholder (optional) | No | content/strings | Hint only — never a label substitute |
| Submit button label | Yes | content/strings | Specific verb ("Subscribe", "Join") |
| Consent / privacy microcopy | Yes | content/strings | GDPR/processing notice; may link to policy |
| Success message | Yes | content/strings | Confirmation text for the live region |
| Error messages | Yes | content/strings | Per validation case (empty, invalid format) |
| Submit endpoint | Yes | components.yaml | Form action / provider config |
| Color/type tokens | Yes | brand.yaml | Surface, accent, error/success colors |

## Accessibility requirements

- **Form + label association:** the email input must have a real, programmatically-associated `<label>` — `<label for="email">Email address</label>` with a matching `id`, or wrapping. A `placeholder` is **not** a label: it vanishes on input and often fails contrast. Set `type="email"`, `name`, `autocomplete="email"`, and `inputmode="email"` so the right keyboard and autofill engage.
- **Required state:** mark the field `required` and, if you show an asterisk, explain it. Use `aria-required="true"` only if not relying on the native `required` attribute.
- **Inline validation with `aria-describedby` / `aria-invalid`:** when validation fails, set `aria-invalid="true"` on the input and link the error message via `aria-describedby="email-error"` so screen readers read the error when the field gets focus. Clear `aria-invalid` (back to `false`/removed) once corrected. Do not signal errors with red color alone (WCAG 1.4.1) — pair color with text and ideally an icon.
- **Status announcement via live region:** success and submission errors must be announced. Put the status message in a container with `role="status"` (polite, for success) or `role="alert"` (assertive, for errors), or `aria-live="polite"`/`"assertive"`. The live region must exist in the DOM before its text is injected so assistive tech registers it. On success, move focus to the confirmation or announce it; never replace the form silently.
- **Consent / GDPR microcopy slot:** an explicit consent statement is required where the law applies. For single opt-in, visible text describes what they're signing up for and links the privacy policy; for explicit consent, use an unchecked (never pre-checked) `<input type="checkbox">` with its own associated `<label>`, included in the form's tab order.
- **Keyboard + focus:** the field and submit are reachable in DOM order with `Tab`; submit fires on `Enter` from the field and on `Enter`/`Space` from the button. Show a visible focus indicator per WCAG 2.2. On error, move focus to the first invalid field.
- **Color contrast:** label, input text, button label, and consent microcopy meet WCAG 2.2 (4.5:1). Input borders and the focus indicator meet 3:1 non-text contrast; error text is not conveyed by color alone.
- **Reduced motion:** any shake-on-error, expanding success animation, or sliding reveal is neutralized under `prefers-reduced-motion: reduce`.

## Common variants

- **Inline single-field** — email + submit on one row; smallest footprint.
- **Footer band** — persistent signup occupying a footer column.
- **Stacked card** — heading, field, button, and consent stacked in a contained card.
- **Two-step / double opt-in** — submit, then a confirm-your-email message.
- **Incentivized** — offers a lead magnet ("Get the free guide") for the email.
- **Modal / slide-in** — appears on intent or scroll (must be dismissible and focus-managed).

## Pitfalls

- Using a `placeholder` as the only label — disappears on typing, fails AT and contrast.
- Errors shown by red color or border only, with no `aria-invalid` and no described text.
- Success/error never announced because there's no live region (or it was injected after the text).
- Pre-checked consent checkboxes, or collecting emails with no privacy notice or processing path.
- Submitting and silently clearing the form so the user has no confirmation anything happened.
