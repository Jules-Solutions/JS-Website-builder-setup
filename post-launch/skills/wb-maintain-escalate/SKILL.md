---
name: wb-maintain-escalate
description: This skill should be used by the website-maintainer when a request is BIGGER THAN MAINTENANCE and needs the full website-builder pipeline — "rebrand the site", "I want a new logo/palette/voice", "switch from Astro to Next.js", "change my CMS", "I want to start selling things / add checkout / take bookings", "redo the whole site", "add a German version / go international", "add a mobile app". Recognizes the scope cue, surfaces the escalation honestly, and hands control to the website-builder agent at the right phase. NOT for any in-scope maintenance (content / sections / pages / iteration / deps / monitoring — those have their own skills).
version: 0.1.0
---

# wb-maintain-escalate — hand back to the full pipeline

> The honest-boundary skill. When a request exceeds maintenance — a rebrand, a stack/CMS migration, going commercial, adding a language, a full redo, a mobile app — the maintainer recognizes it, names it, and hands control to the full website-builder pipeline at the right phase. The maintainer does NOT attempt this work itself.

## When invoked

A request matches the maintainer's **anti-authority** list (see `agents/website-maintainer.md` § Anti-authority) or carries an escalation scope cue:

- **Brand identity change** — new logo / palette / voice → phase 5 + 17
- **Stack migration** — Astro → Next.js etc. → phase 11
- **CMS migration** → phase 12
- **Going transactional** (decision 34) — "start selling", checkout, bookings → phase 11 transactional flag flip, forcing restart of 12 / 22-23 / 24a-c
- **Major design-system overhaul** → phase 17 (beyond an iteration)
- **Adding a new language** — CDJSON / hreflang / per-language content → phase 16 + i18n
- **Mobile app companion** (decision 26) → out to `DESIGN-mobile-app-companion.md`
- **"Redo the whole site"** → full pipeline from the appropriate entry phase

## Behavior

1. **Recognize the trigger.** Match the request against the anti-authority list / scope cues above. When unsure whether something is iteration or escalation, err toward surfacing it — let the user decide with the cost in view.
2. **Name it plainly.** Surface that this is bigger than maintenance and *why*, with the specific phase(s) the full pipeline must re-run. Example (transactional, decision 34): *"Adding checkout is a structural pivot, not a content change — it means re-deciding the stack/CMS to pair with commerce, re-authoring forms with payment endpoints, and the commerce phases (platform + payments + commerce-legal). Your content, brand, and design system carry forward; the architecture has to compose with payments now."*
3. **Confirm escalation.** The user decides. They can confirm (escalate now), defer (note it for later), or re-scope (maybe it's actually a smaller change after all).
4. **Hand off cleanly.** On confirmation, load the website-builder agent profile (`agents/website-builder.md`) — it *replaces* the maintainer for the session. The builder's session-start reads `.website-builder/` project state, identifies which scope of pipeline to re-run, and walks the user through the relevant phases. The `.website-builder/` state directory is shared; only the agent identity changes.
5. **Return after.** When the pipeline completes, control hands back to the maintainer for ongoing care. Two profiles, one project.

## Time-box

**N/A** — this skill escalates; it does not execute the larger work. The larger work runs on the full pipeline's clock.

## Anti-patterns

- Attempting a rebrand / migration / transactional change as a maintenance patch (the exact failure this skill prevents).
- Soft-pedaling the cost so the user under-estimates the work.
- Escalating things that are actually in-scope iteration (a shade tweak is `wb-maintain-iterate`, not an escalation) — escalate only genuine anti-authority scope.
