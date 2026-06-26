---
type: REFERENCE
corpus: component-patterns
title: Modal Dialog
component_slug: modal
also_known_as: [modal, dialog, lightbox, popup, overlay]
consumed_by_phases: [9, 17, 18]
---

# Modal Dialog

> An overlay window that interrupts the page to demand a focused task or decision, blocking interaction with everything behind it until the user completes or dismisses it.

## Purpose

A modal pulls the user out of the page flow to handle one thing — confirm a destructive action, fill a short form, view enlarged media, or read a critical message — without losing their place. It earns the interruption by being focused: a clear title, the task, and an explicit way out. Because it traps interaction, a modal is a heavy tool; a page uses it only when the task genuinely must be resolved before continuing, or when surfacing it inline would lose context. Misused, it's an annoyance; used well, it removes ambiguity at a decision point.

## When to use / when not

- **Use when:** the task is short and must be completed or explicitly dismissed before continuing (confirm delete, quick edit, required acknowledgement, enlarged image).
- **Avoid when:** the content is long, the task is non-blocking, or it could live inline. Never use a modal for an unsolicited marketing interstitial on load — it's hostile and often fails accessibility. Prefer an inline expand, a separate page, or a non-blocking toast.

## Anatomy

| Part | Role |
|---|---|
| Trigger | The button that opens the dialog (focus returns here on close) |
| Backdrop / scrim | The dimmed overlay covering and inerting the background |
| Dialog container | The `role="dialog"` box, the new focus context |
| Title | The dialog's visible heading, referenced as its accessible name |
| Body | The task content — message, form, or media |
| Action buttons | Confirm / cancel (or just close) |
| Close affordance | An explicit "×" / close button |

## Content slots

| Slot | Required? | Source layer | Notes |
|---|---|---|---|
| Trigger label | Yes | content/strings | The button text that opens the modal |
| Dialog title | Yes | content/pages | Becomes the accessible name via `aria-labelledby` |
| Dialog body copy | Yes | content/pages | Message, form, or media caption |
| Confirm action label | Yes | content/strings | Action-specific ("Delete account", not "OK") |
| Cancel / close label | Yes | content/strings | "Cancel" + an icon close needs an `aria-label` |
| Embedded media | No | media | If the modal is a lightbox; needs `alt` |
| Embedded form fields | No | components.yaml | If the modal hosts a form (follow form.md rules) |
| Overlay + elevation tokens | Yes | brand.yaml | Scrim color/opacity, surface, shadow/elevation |

## Accessibility requirements

Implements the **WAI-ARIA APG "Dialog (Modal)" pattern** exactly — this is the headline contract of this component.

- **Roles & properties:** the dialog container has `role="dialog"` and `aria-modal="true"`. Give it an accessible name with `aria-labelledby` pointing at the visible title's id (or `aria-label` if there is no visible title). If there is descriptive body text the dialog should be introduced by, reference it with `aria-describedby`. (Native `<dialog>` with `showModal()` provides these semantics and the top-layer/inert behaviour for free and is the preferred substrate.)
- **Focus moves IN on open:** when the dialog opens, move keyboard focus into it — to the first interactive element, or to the dialog container (`tabindex="-1"`) if the first focusable element would be undesirable (e.g. a destructive button). Focus must NOT stay on the trigger behind the scrim.
- **Focus trap:** while open, `Tab` and `Shift+Tab` cycle only among focusable elements inside the dialog — `Tab` from the last wraps to the first, `Shift+Tab` from the first wraps to the last. Focus can never reach the inert background. Native `<dialog>.showModal()` enforces this; a custom dialog must implement the wrap manually.
- **Focus RETURNS on close:** when the dialog closes (any path — confirm, cancel, Escape, backdrop), return focus to the element that opened it (the trigger), or to a sensible nearby control if the trigger no longer exists. Losing focus to `<body>` is a defect.
- **Escape closes:** pressing `Escape` closes the dialog from anywhere within it (unless an unsaved-changes guard intentionally intercepts, in which case the guard itself is keyboard-accessible).
- **Background inert:** everything outside the dialog is made non-interactive and hidden from assistive tech for the dialog's lifetime — via the `inert` attribute on the background containers (preferred) or `aria-hidden="true"` plus removing them from the tab order. Background scroll is locked. Native modal `<dialog>` handles inerting via the top layer.
- **Dismiss affordances:** provide at least one explicit visible control to close (a close button and/or cancel); do not rely on Escape alone. An icon-only close button needs `aria-label="Close"`.
- **Contrast & motion:** title, body, and buttons meet WCAG 2.2 contrast; the focus indicator is visible on every control; entrance/exit transitions are reduced or removed under `prefers-reduced-motion: reduce`. The scrim must provide enough separation that the dialog is clearly the active context.

## Common variants

- **Confirmation dialog** — a message plus confirm/cancel (use `role="alertdialog"` when it's an urgent error/destructive confirm so the body is announced immediately).
- **Form modal** — hosts a short form; submit closes on success, errors stay in-dialog.
- **Lightbox** — enlarges an image or gallery item; arrow keys may page between items.
- **Drawer / side sheet** — a modal anchored to a screen edge; same dialog semantics, different position.
- **Non-modal dialog** — `aria-modal` omitted and background left interactive (e.g. a date picker) — NOT a true modal; different focus rules.
- **Cookie / consent dialog** — blocking choice on load; must still trap focus and be keyboard-operable.

## Pitfalls

- A `<div>` overlay with no `role="dialog"`, no `aria-modal`, and no accessible name — invisible structure to screen readers.
- Forgetting to move focus in on open, so keyboard users tab through the hidden page behind the scrim.
- Forgetting to return focus to the trigger on close, dumping focus to `<body>` and losing the user's place.
- No focus trap, letting `Tab` escape to inert background controls.
- Escape doesn't close, or the only dismiss is clicking outside (undiscoverable for keyboard users).
- Background not inerted, so screen readers still read and tab into the page underneath.
