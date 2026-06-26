---
type: REFERENCE
corpus: component-patterns
title: Gallery
component_slug: gallery
also_known_as: [image grid, masonry, portfolio grid, photo gallery, carousel, slider]
consumed_by_phases: [9, 17, 18]
---

# Gallery

> A collection of visual work — images shown as a grid, masonry, or carousel — often with an enlarged lightbox view on selection.

## Purpose

A gallery showcases visual proof: portfolio pieces, product photos, event shots, case-study screenshots. Its job is to let visitors browse a body of imagery efficiently and inspect any item closely. For a freelancer or studio site it is the central credibility surface — the work *is* the pitch — so the gallery converts by making that work easy to scan and rewarding to explore.

## When to use / when not

- **Use when:** the content is fundamentally visual and there are several items worth browsing — portfolios, product imagery, photo collections.
- **Avoid when:** there are only one or two images (place them inline), the images are decorative chrome (use background imagery, not a gallery), or the items carry essential text that shouldn't live inside an image. Prefer a static grid over a carousel unless space is truly constrained — carousels hide content and have well-documented engagement and a11y costs.

## Anatomy

- **Section wrapper** — optional heading, intro, and filter controls.
- **Layout container** — grid / masonry / carousel track.
- **Thumbnail item** (repeats) — image plus optional caption/overlay, acting as the trigger to enlarge.
- **Lightbox / dialog** (optional) — modal overlay with the enlarged image, caption, close control, and prev/next.
- **Carousel controls** (carousel only) — previous/next buttons, slide picker dots, and a play/pause toggle for auto-rotation.

## Content slots

| Slot | Required? | Source layer | Notes |
|---|---|---|---|
| `items[].image` | Yes | media | Thumbnail + full-size source (responsive `srcset`) |
| `items[].alt` | Yes | content/strings | Describes the image content; empty only if truly decorative |
| `items[].caption` | No | content/pages | Visible caption / project title |
| `items[].href` | No | sitemap.yaml | If a thumb links to a case-study page instead of a lightbox |
| `layout` | No | components.yaml | grid / masonry / carousel; columns + gap tokens from brand.yaml |
| `lightbox_enabled` | No | components.yaml | Whether selecting a thumb opens a dialog |
| `autorotate` | No | components.yaml | Carousel auto-advance on/off + interval |
| `section_heading` | No | content/pages | Gallery section title |

## Accessibility requirements

- **Alt text:** every informative image needs `alt` describing its content/purpose; purely decorative images use `alt=""`. Captions don't replace alt — a caption is for everyone, alt is the image's text alternative.
- **Thumbnail triggers:** a thumbnail that opens a lightbox is a `<button>` (not a bare `<img>` or `<div>`), with an accessible name like "View full size: <caption>". A thumbnail that navigates is an `<a>` with a descriptive name.
- **Lightbox = APG modal dialog:** implement per the WAI-ARIA APG Dialog (Modal) pattern: container has `role="dialog"` (or native `<dialog>`), `aria-modal="true"`, and an accessible name via `aria-labelledby` (the image caption) or `aria-label`. On open, **move focus into the dialog** (the close button or the image region); **trap focus** so `Tab`/`Shift+Tab` cycle only within the dialog; `Esc` closes it; on close, **return focus to the thumbnail trigger** that opened it. Background content gets `inert` or `aria-hidden="true"` while the dialog is open. Prev/next inside the lightbox are real `<button>`s with names ("Previous image" / "Next image"); announce the new image (e.g. update the dialog's labelled caption).
- **Carousel = APG Carousel pattern:** wrap in a region with `role="region"` (or `role="group"`) and `aria-roledescription="carousel"` plus an `aria-label` ("Featured work"). Slides are a rotation container with `aria-atomic="false"` and `aria-live="off"` while auto-rotating, switched to `aria-live="polite"` when rotation is stopped or the user navigates manually. Previous/Next are `<button>`s; slide-picker dots are `<button>`s in a `role="tablist"`-style group or labelled "Go to slide N", with the current one marked (`aria-disabled` or current state).
- **Auto-rotation pause (required for carousels):** if slides auto-advance, you MUST provide a visible, keyboard-reachable **play/pause** button (WCAG 2.2.2 Pause, Stop, Hide). Auto-rotation must also pause on hover and on keyboard focus anywhere within the carousel, and stay paused once the user explicitly pauses it.
- **Keyboard:** all controls reachable by `Tab` with visible `:focus-visible` outlines; `Enter`/`Space` activate buttons. Don't bind arrow keys in a way that hijacks page scrolling; if arrow-key slide navigation is offered, scope it to focus within the carousel.
- **Motion & contrast:** honor `prefers-reduced-motion: reduce` — disable auto-rotation and slide-transition animation. Control icons/overlays meet contrast minimums; the lightbox overlay scrim must keep caption text ≥ 4.5:1.

## Common variants

- **Uniform grid** — equal-sized thumbnails in a clean matrix.
- **Masonry** — variable-height tiles packed to minimize gaps.
- **Lightbox grid** — grid whose items open an APG modal dialog.
- **Carousel/slider** — one-at-a-time rotating view with controls (heaviest a11y burden).
- **Filterable gallery** — category buttons that filter items (announce result count via live region).
- **Linked portfolio** — thumbs navigate to per-project case-study pages.

## Pitfalls

- Auto-rotating carousels with no pause control (WCAG 2.2.2 failure) that also don't pause on hover/focus.
- Lightboxes that don't trap focus, don't close on `Esc`, or don't restore focus to the trigger on close.
- Clickable `<div>`/`<img>` thumbnails with no button/link role — invisible to keyboard users.
- Missing or unhelpful `alt` (filename-as-alt, or `alt=""` on images that carry meaning).
- Carousels left as `aria-live="polite"` while auto-advancing, spamming screen readers with every slide change.
