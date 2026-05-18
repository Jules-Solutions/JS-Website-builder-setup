# Launch Announcement — Reference (phase 31)

> Loaded on demand when executing phase 31. Per-channel copy patterns, the launch-day sequencing template, 2026 launch best-practice, and the skip-cost framing language. The authoritative behavior spec is `phase-contracts/31-launch-announcement.md`; this file is the working reference for *producing* the assets.

## The non-negotiable: substance is the user's

The announcement's hook — *why this site/project matters, what changed, what the reader should do* — is the user's. The agent extracts it via `AskUserQuestion` and shapes it to the phase-5 brand voice. The agent never fabricates the launch story. An invented hook reads as hollow as invented site copy (the same phase-16 discipline). If the user says "just write the announcement for me", surface that the substance must be theirs and ask the 2-3 questions that get it: *what changed / why now*, *who most needs to hear this*, *what you want them to do when they see it*.

## Per-channel copy patterns

Produce only the channels the project's phase-3 audience actually uses. Each in the phase-5 voice, never generic launch-hype.

### Short social post (X / Bluesky / Mastodon shape)

- One or two sentences. The hook + the link. No "We're thrilled to announce".
- Pattern: `[the specific thing that's now true/possible] → [link]`. Lead with the value to the reader, not the milestone to the user.
- One concrete detail beats three adjectives. "The booking flow now takes 20 seconds" > "an amazing new streamlined experience".

### LinkedIn post

- Longer, professional register *only if that is the audience*. A creator's LinkedIn is still warm; a B2B consultancy's is precise.
- 2026 best-practice (per launch-strategy research): LinkedIn announcements land best with a **relatable, personal hook** (the story/challenge behind the build), not a promotional lede. Tag and thank contributors — it builds goodwill and boosts reach.
- Structure: personal hook (1-2 lines) → what the site does and who it's for → one concrete proof point → the link → thanks/tags. End with a question or invitation, not a hard CTA.

### Instagram caption (+ visual note)

- The caption is voice-shaped; the *visual* is the work. Always include a one-line note telling the user what visual they need (a screenshot of the hero, a short screen-recording of the key flow, a before/after if it's a redesign) — the caption without the visual is not the asset.
- Front-load the hook in the first line (the rest is truncated in-feed).

### Email / newsletter announcement

- 2026 best-practice (per email research): write it as a conversation, not a press release. Greet, say it's live, state the benefit in plain language, one clear link/CTA.
- For an existing list, a **5-email countdown series** is the strong pattern when the launch warrants it (teaser → behind-the-scenes → benefit-focused → launch-day → follow-up/testimonials). For most muggle sites a single well-shaped launch email + one follow-up is enough — match the series length to the audience size and the user's appetite, do not over-engineer a 5-email funnel for a 40-person list.
- Segment if the list has clear segments (existing customers vs cold subscribers get different framing of the same news).

### Internal-stakeholders note

- The people who should hear it *first*: partners, team, the people whose project this represents. Often forgotten because it is not "marketing".
- Plain, direct, no marketing voice. "The site is live at [url]. Here's what's new and what I'd love your help amplifying."
- Sequence this **before** the public channels (see schedule below) — internal people hearing about a launch from social media is an avoidable own-goal.

## Channel plan — ranked, audience-tied

Do **not** "post everywhere". Tie channels to the phase-3 audience and rank them:

- A B2B consulting site → LinkedIn + email list + internal stakeholders. No TikTok launch it does not need.
- A creator/portfolio site → Instagram + their newsletter + the platform their audience already follows them on.
- A local-service site → the local channels + email + any community/partner networks.

The plan states *which channels, in what order, with a one-line rationale per channel tied to where the audience actually arrives* (the phase-3 likely-arrival-channel). Channels the audience does not use are omitted with no apology — a tight 3-channel plan the user will execute beats an 8-channel plan they will not.

## Launch-day sequencing template

A staggered sequence, not a single simultaneous blast. Concrete dates/times the user commits to (not "soon"). Typical shape — adjust to the project:

```
T-2 to T-3 weeks  (optional, audience-dependent): social ramp — share aspects
                   of the build (a feature, a benefit, a behind-the-scenes)
                   to warm the audience before launch day.
Launch day  T-0    08:00  Internal-stakeholders note (they hear it first)
            T-0    10:00  LinkedIn post + email/newsletter (the primary push,
                           same-day, mutually reinforcing)
            T-0    13:00  Short social post (X/Bluesky/Mastodon)
            T-0    15:00  Instagram (with the prepared visual)
T+3 to T+7 days    Follow-up: a reminder / a testimonial from an early visitor
                   / a post-launch piece — keep momentum (per 2026 research,
                   the follow-up is where most launches under-invest).
```

The 2-3-week social ramp is optional and audience-dependent (per 2026 social research, it works for product/creator launches with an engaged following; it is over-investment for a small B2B site whose launch is a LinkedIn post + an email). Recommend it, do not impose it.

## Skip-cost framing language (phase 31 — no gate)

If the user wants to skip the announcement, the agent does not block (no gate) but surfaces the cost so the choice is informed, then logs `.website-builder/decisions/skip-phase-31.md`:

- **Skipping is launching into silence.** "Weeks of disciplined work, and then the site launches and nobody is told. For a site whose phase-3 conversion outcome depends on people arriving, no announcement means a flat analytics line — and you wondering why 'the site isn't working' when the site is fine and the silence is the problem."
- **The cost is asymmetric and decays.** "You *can* announce later — the post-launch maintainer can re-run a thinner version of this. But launch-moment attention is a one-time asset. A 'we just launched' three weeks late lands softer than day one. 'I'll announce later' is a real decay, not a free deferral."
- **Legitimate skip cases the agent does not over-push:** a deliberate soft launch (quiet real-user gathering before a bigger push), an internal/private site (no public audience by design), a replacement site whose audience already knows the URL. For these: log the rationale, move on without friction. The discipline is *informed* choice, not forced announcement.

## Sources (external research, loaded fresh 2026-05-18)

- Website launch announcement email ideas + 5-email countdown pattern + ~30% open rate / high-ROI framing: [7 Website Launch Announcement Email Ideas 2026](https://getwpfunnels.com/website-launch-announcement/), [5 New Website Announcement Email Examples](https://designmodo.com/new-website-announcement-email/), [5+ New Website Announcement Email Templates](https://moosend.com/blog/new-website-announcement-emails/)
- 2-3-week social ramp + multi-platform strategy + post-launch momentum: [Guide to Make your New Website Announcement Stand Out](https://www.emailaudience.com/new-website-announcement/), [33 product launch social media posts examples](https://www.contentstadium.com/blog/product-launch-social-media-posts-examples/)
- LinkedIn personal-hook + tag-contributors pattern: [9 Examples of New Website Launch Announcements](https://musemind.agency/blog/new-website-launch-announcements), [Website Announcement LinkedIn Post Template — Visme](https://www.visme.co/templates/social-media-graphics/website-announcement-linkedin-post-1425284110/)
