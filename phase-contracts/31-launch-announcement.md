---
phase: 31
name: Launch announcement
group: post-launch
pipeline_section: post-launch
skill: wb-postlaunch
prev_phase: 30
next_phase: 32
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-phase-contracts.md
  - Workstreams/website-builder/foundation/DESIGN-architecture.md
  - Workstreams/website-builder/cross-cutting/DESIGN-post-launch-template.md
---

# Phase 31 — Launch announcement

> The site is live; now tell people. Draft the launch announcement in the brand voice — social, email, IG, LinkedIn, internal stakeholders — identify the channels, set a schedule. The phase that turns "it's deployed" into "people know about it." First phase of the post-launch group. No quality gate (you can launch silently and the site still works), but the agent makes "tell people" an explicit step rather than the afterthought it usually becomes.

## Mission

The site is live, verified, discoverable to search engines (phases 29-30). What it does not yet have is an audience that knows it exists. Phase 31 closes that gap: it drafts the launch announcement assets — in the brand voice established at phase 5 — for the channels the project actually reaches, identifies which channels matter, and sets a schedule so the announcement happens on purpose rather than "whenever I get around to it" (which, for muggles, is usually never).

This is the first phase of the **post-launch group** (31-34), which runs **once, at launch**. Per locked decision 49 + 37, ongoing maintenance is owned by the post-launch *maintainer* template (materialized at phase 29's wizard) and its 8-skill bundle — content / monitoring / deps / content-add / section-add / page-add / iterate / escalate. Phase 31 maps to the maintainer's eventual "launch announcement" capability surface, but **phase 31 does not author those skills** — they are a Stage 2.B Captain's work. Phase 31 references the future skill path (so the user knows the maintainer can re-run a thinner version of this for a v1.1 announcement) and produces the *one-shot launch* assets here.

The defining discipline is small but real: **the announcement is a step, not an afterthought.** The seed names the failure precisely — muggles forget to tell anyone. They spend weeks on a disciplined build and then launch into silence because "announcing" never made it onto the list. Phase 31 puts it on the list. There is no refusal gate (a user *can* deliberately soft-launch with no announcement), but the agent does not let the announcement silently not-happen — it surfaces the cost of silence and produces the assets so the only reason it does not happen is a deliberate user choice.

## Entry conditions

- Phase 30 (analytics + search submission) complete. The site is live, discoverable, and measurable — announcing now means the agent can later tell (via the phase-30 analytics) whether the announcement drove traffic.
- `.website-builder/brand.yaml.voice` (phase 5) — the announcement is written in *this brand's voice*, not generic launch-hype. The same say/never-say discipline phase 16 enforced for site copy applies to the announcement copy.
- `.website-builder/project.yaml.requirements` (phase 3) — the primary audience and the channels they actually arrive through (the phase-3 likely-arrival-channel) inform which announcement channels matter. A B2B consulting site's launch goes to LinkedIn + an email list; a creator's goes to IG + their newsletter — the channels follow the audience, not a generic checklist.
- `.website-builder/post-launch/config.yaml` (materialized at phase 29) — records the iteration cadence + the maintainer config; phase 31's announcement is the launch-moment one-shot, and the maintainer's future "announcement" capability is referenced, not duplicated.

## What Claude must establish

Drafted launch-announcement assets, channel plan, and schedule — produced, not just discussed. The work product:

1. **Announcement copy per channel, in the brand voice.** The asset set the project's actual channels need: a short social post (X/Bluesky/Mastodon shape), a LinkedIn post (longer, professional register if that is the audience), an Instagram caption (+ a note on the visual the user needs), an email/newsletter announcement, and an internal-stakeholders note (telling the people who should hear it first — partners, team, the people whose project this represents). Each in the phase-5 voice — warm-and-specific if that is the brand, not "We're thrilled to announce…" generic launch-speak (the same AI-generic register phase 16 refuses).
2. **Channel plan.** Which channels, in what order, with what rationale tied to the phase-3 audience. Not "post everywhere" — the channels the audience actually uses, ranked.
3. **Schedule.** When each asset goes out (a sequence, not a single blast — e.g., internal note first, then LinkedIn + email same day, social staggered). A concrete date/time the user commits to, not "soon."
4. **`launch/ASSETS.md`** in the user's project — the drafted assets, the channel plan, the schedule, in one place the user (or the post-launch maintainer later) can pick up.

The agent updates `.website-builder/project.yaml.current_phase` to `32` upon completion.

## Skip authorization

Phase 31 is **commonly skipped** by users who want to ship-and-move-on — and the seed acknowledges this is a legitimate (if often regretted) choice. Phase 31 has no refusal gate; the agent does not block the pipeline if the user declines an announcement. But the agent documents the **skip cost** explicitly so the choice is informed:

- **Skipping the announcement is launching into silence.** The disciplined build is invisible if nobody is told. For a site whose phase-3 conversion outcome depends on people arriving (almost all of them), no announcement means no initial traffic, no first conversions, no momentum — the analytics wired at phase 30 will show a flat line, and the user will (often) wonder why "the site isn't working" when the site is fine and the silence is the problem.
- **The cost is asymmetric and recoverable-but-decayed.** The announcement *can* be done later (the post-launch maintainer's announcement capability re-runs a thinner phase 31). But launch-moment attention is a one-time asset — a "we just launched" announcement three weeks late lands softer than one on day one. The agent surfaces this so "I'll announce later" is understood as a real decay, not a free deferral.
- **Legitimate skip cases the agent does not over-push:** a deliberate soft launch (gather a few real users quietly before a bigger push), an internal/private site (no public audience by design), a site replacing an existing one where the audience already knows the URL. For these the agent records the skip rationale in `.website-builder/decisions/skip-phase-31.md` and moves on without friction — the discipline is *informed* choice, not forced announcement.

If the user skips, the agent logs the decision + the surfaced cost and advances to phase 32. It does not refuse; it does not silently let the announcement evaporate without the user having seen the cost.

## Gating rules

Phase 31 has **no refusal gate** (per the seed — `## Gating: none`). The site is already live and functional; an unannounced site is a quiet site, not a broken one. The agent does not block the pipeline here. The standards that still apply (not gates, but rigor):

- **The announcement copy is in the brand voice, not generic launch-hype.** "We're incredibly excited to announce the launch of our brand-new website!" is the AI-generic register phase 16 refuses; the agent writes the announcement the way *this brand* would say it. Not a pipeline gate, but the agent does not hand the user voiceless copy.
- **Channels follow the phase-3 audience, not a generic checklist.** The agent does not pad the plan with channels the audience does not use (a B2B firm does not need a TikTok launch); it ties the channel plan to the real audience.
- **The skip is a documented decision, not a silent evaporation.** If the announcement does not happen, it is because the user chose that with the cost surfaced — the agent's only firm behavior here is refusing to let "tell people" silently fall off the list unacknowledged.

## Tools and skills used

- **`Edit` / `Write`** — to draft `launch/ASSETS.md` (the per-channel copy, the plan, the schedule) into the user's project.
- **`AskUserQuestion`** — the channels the user actually has (do they have a LinkedIn presence? an email list? who are the internal stakeholders to tell first?), the launch date/time they commit to, and — for the substance the agent must not invent — the actual story of *why* this site/project matters (the announcement's hook is the user's, shaped to voice by the agent, the same phase-16 substance-is-yours/shaping-is-mine discipline).
- **`Read`** — `brand.yaml.voice` (the voice the announcement is written in), `project.yaml.requirements` (the audience + their channels), `post-launch/config.yaml` (the iteration cadence; the maintainer's future announcement capability).
- **`WebSearch`** — only if the user wants current best-practice for a specific channel's launch format (optional, not mandatory per the INST — phase 31 is first-principles authoring; voice + audience-fit consistency is the gating concern, not external research).

No subagent spawn. The `wb-postlaunch` phase-group skill (loaded at the post-launch-group transition, per Lock M5 — phases 31/32/33/34) carries the cross-phase contract: phases 31-34 run **once at launch**; the materialized post-launch *maintainer* (phase 29) and its 8-skill bundle (decision 49) own everything ongoing. Phase 31 references the maintainer's future "launch announcement" capability path but does **not author it** (Stage 2.B Captain work — out of this contract's scope).

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| `.website-builder/launch/ASSETS.md` | Per-channel announcement copy (in phase-5 voice), the channel plan (ranked, audience-tied), the schedule (concrete dates/times) | The drafted launch assets the user (or the post-launch maintainer) executes; the one-shot launch-moment announcement |
| `.website-builder/decisions/skip-phase-31.md` *(when applicable)* | Standard decision-doc frontmatter + body | Created only when the user deliberately skipped the announcement with the cost surfaced + the skip rationale logged |

The `ASSETS.md` (or, if skipped, the logged skip decision with surfaced cost) is the artifact.

## Common failure modes

**The muggle forgets to tell anyone.** The exact failure the seed names. Weeks of disciplined work, then launch into silence because "announcing" was never a step. Phase 31's whole reason to exist is to make it a step — the agent produces the assets and surfaces the cost of silence so the only path to "nobody knew" is a deliberate, logged user choice, not an accidental omission.

**Generic launch-hype instead of the brand voice.** "We're thrilled to announce our brand-new website is now live!" — the voiceless register that sounds like every other launch and like nobody. The agent writes the announcement in the phase-5 voice (the same standard phase 16 held the site copy to); the announcement is the brand's first impression on a fresh wave of attention and it should sound like the brand.

**"Post everywhere" channel spray.** A B2B consulting site with a TikTok launch plan it does not need. The agent ties channels to the phase-3 audience — the channels the audience actually uses, ranked, with a rationale — not a generic every-platform checklist.

**The announcement is "discussed" but never drafted.** The agent talks about the launch plan and moves on without producing `ASSETS.md`. The deliverable is the *drafted assets*, not a conversation about them — phase 31 leaves the user with copy they can post, not advice that they should.

**"I'll announce later" treated as free.** Launch-moment attention is a one-time asset; a late announcement decays. The agent surfaces the asymmetry so "later" is an informed trade-off, not an assumed-costless deferral — and notes the post-launch maintainer can re-run a thinner announcement, while being honest that it lands softer than day-one.

**The agent invents the launch story.** "Just write the announcement for me." The substance — *why this matters, what changed, what the reader should do* — is the user's; the agent shapes it to voice but does not fabricate the hook (same phase-16 discipline: substance is yours, shaping is mine). An invented launch story reads as hollow as invented site copy.

## Reference materials

- **Design doc — phase pipeline source:** `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` § 31 (seed — `Gating: none`; common failure = muggles forget to tell anyone, agent makes "tell people" a step)
- **Design doc — post-launch maintainer template (the once-at-launch vs ongoing split, decision 37/49):** `Workstreams/website-builder/cross-cutting/DESIGN-post-launch-template.md` § Phase 31-34 vs maintainer template (decision 37) — phase 31 maps to the maintainer's eventual launch-announcement capability; **referenced, not authored here**
- **Design doc — pipeline integration:** `Workstreams/website-builder/foundation/DESIGN-architecture.md` § Phase contracts
- **Phase 5 (the voice the announcement is written in):** `brand.yaml.voice`
- **Phase 16 (the substance-is-yours / shaping-is-mine discipline applied to announcement copy):** `phase-contracts/16-copywriting.md` § Common failure modes
- **Phase 3 (the audience + channels the announcement targets):** `phase-contracts/03-requirements.md` § What Claude must establish — primary audience + likely-arrival-channel
- **Phase 30 (the analytics that will show whether the announcement worked):** `phase-contracts/30-analytics-search-submission.md`
- **Locked decisions 37 + 49** (phases 31-34 run once at launch; post-launch 8-skill maintainer split owns ongoing) — STATE doc: `Workstreams/website-builder/website-builder.md`

No mandatory external research for this phase (per the INST — phases 31/32/33 are first-principles authoring from the seed; the gating concern is voice + audience-fit consistency across the batch, not fetched docs). Freshness date for this contract: **2026-05-18**.
