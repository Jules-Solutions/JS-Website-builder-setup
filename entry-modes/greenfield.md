# Entry mode: greenfield

> Nothing yet. This is a brand new site with no existing design artifacts, no prior AI output, no Figma files, no deployed pages. The cleanest starting point — and the default when no entry mode is specified.

## Who this is for

- Someone building a site for the first time
- Someone rebuilding a site from scratch (deliberately not carrying forward the old design)
- Someone whose prior work was not digital (e.g., a flyer / pitch deck / verbal brief) — those artifacts flow in through phase 1 or phase 6 as raw source material, not structured design data

If the user "has a rough idea" but nothing else, greenfield is the right mode.

## Onboarding flow

Phase 1 (Idea capture) runs in full without modification. The agent asks the three seed questions:

1. What is the site for? (the idea sentence — product, service, event, creative work)
2. Who is it for? (the user, not the audience — what does the builder know about the domain?)
3. Is there anything the builder already has? (Phase 1 accepts: a rough outline, a company name, a tagline, an existing logo file, a printed brochure, a pitch deck — none of these trigger phase 6.5; they are reference material, not structured artifacts)

`project.yaml.entry_mode` is written as `"greenfield"` at phase 1 exit.

## Phase 6.5 at session start

**Phase 6.5 does not fire.** There are no artifacts to ingest. The pipeline runs straight through: 1 → 2 → 3 → 4 → 5 → 6 → 7 → ...

Phase 6.5 CAN be triggered mid-project if the user acquires a new artifact (e.g., generates a landing page in ChatGPT at phase 13, or gets a Figma file from a freelancer at phase 18). That invocation is on-demand, not entry-mode-driven.

## Key constraint

The greenfield constraint is that there is **no prior aesthetic**. The agent cannot shortcut phases 2 and 5 (vision and brand voice) by extracting from an existing artifact — those phases run in full conversational mode, because nothing has been decided yet. Any attempt to skip phases 2-5 on the grounds of "we'll figure that out later" is a failure mode; the agent surfaces this and refuses.
