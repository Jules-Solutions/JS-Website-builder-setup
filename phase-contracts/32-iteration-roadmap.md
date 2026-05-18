---
phase: 32
name: Iteration roadmap
group: post-launch
pipeline_section: post-launch
skill: wb-postlaunch
prev_phase: 31
next_phase: 33
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-phase-contracts.md
  - Workstreams/website-builder/foundation/DESIGN-architecture.md
  - Workstreams/website-builder/cross-cutting/DESIGN-post-launch-template.md
---

# Phase 32 — Iteration roadmap

> v1 is a checkpoint, not the finish line. Plan v1.1 — a short, concrete list of the next things to add / change / improve, with rough timing. The phase that reframes launch as the start of the site's life rather than its end. No quality gate. The agent surfaces that v1 is a checkpoint and produces a real 3-5-item roadmap rather than letting the user treat shipping as done.

## Mission

The site is live and announced (phases 29-31). The muggle's instinct at this point is "done — I built a website." Phase 32 reframes that: v1 is a checkpoint. Every site that stays good is iterated; every site that is treated as finished decays into stale-and-ignored. Phase 32 produces a short, concrete **v1.1 roadmap** — 3-5 items, each a real next-thing-to-add/change/improve, with rough timing — so the site has a forward path the user (and the post-launch maintainer) can act on instead of a vague "I should update this someday."

This is a post-launch-group phase (31-34), running **once at launch**. The roadmap it produces (`roadmap.md`) becomes a standing touch-point for the post-launch *maintainer* (materialized at phase 29's wizard, per decision 49) — the maintainer's `iterate` / `section-add` / `page-add` skills read this roadmap when the user comes back wanting to do "the next thing." Phase 32 **references** those future maintainer skills (so the user understands the roadmap is not a dead document — the maintainer will help execute it) but **does not author them** (Stage 2.B Captain work, out of scope).

The discipline is anti-vagueness. A roadmap of "improve SEO, add more content, make it better" is not a roadmap — it is a restatement of "keep working on it." The agent produces *specific* items grounded in what this site actually is: the phase-3 conversion outcome that could be sharpened, the phase-30 analytics that will reveal what to fix, the content type the sitemap could grow into, the section the user mentioned-but-deferred during the build. Each item is concrete enough that a future session (or the maintainer's `iterate` skill) can pick it up and act without re-deriving what was meant.

## Entry conditions

- Phase 31 (launch announcement) complete (or skipped with logged decision). The site is live, announced, and the analytics is recording — the roadmap can be grounded in what the live site is doing, not pure speculation.
- `.website-builder/project.yaml.requirements` (phase 3) — the conversion outcome and audience; v1.1 items often sharpen the conversion path or deepen the audience fit.
- Any deferred-during-build decisions — `.website-builder/decisions/*deferred*.md` (an integration deferred at phase 24, a stack-expansion logged at phase 11, a section the user wanted but cut). These are the highest-quality roadmap inputs: things the user already wanted that were consciously deferred, not invented future work.
- `.website-builder/post-launch/config.yaml` (phase 29 wizard) — the iteration cadence the user chose (weekly/monthly/quarterly/ad-hoc); the roadmap's rough timing aligns to that cadence rather than inventing a schedule the user did not pick.

## What Claude must establish

A concrete, actionable v1.1 roadmap. The work product:

1. **3-5 roadmap items, each specific.** Not "improve the site" — concrete: "add a case-study page for the [named] project (the phase-9 sitemap has a `/work` archive type but only one entry)", "wire the newsletter integration deferred at phase 24 once the list platform is chosen", "A/B the hero CTA copy against the phase-30 analytics once there's a month of baseline", "add the German translation (phase-16 i18n Pattern A is set up; only `en` shipped)". Each item names *what*, *why it matters* (tied to the conversion outcome or a deferred decision), and roughly *when* (aligned to the chosen cadence).
2. **Rough timing per item**, aligned to the phase-29-wizard iteration cadence (a quarterly-cadence user does not get a weekly roadmap). Rough is fine — "next month", "after a month of analytics", "when the user has the case-study content" — concrete enough to act on, not false-precision Gantt.
3. **`roadmap.md`** in the user's project — the 3-5 items, ordered by leverage, in a form the post-launch maintainer's `iterate`/`section-add`/`page-add` skills can read and execute against.

The agent updates `.website-builder/project.yaml.current_phase` to `33` upon completion.

## Skip authorization

Phase 32, like phase 31, is **commonly skipped** by ship-and-move-on users, and has no refusal gate. The agent documents the **skip cost**:

- **Skipping the roadmap is treating v1 as the finish line.** The seed names the failure: muggles see v1 as the end; the agent surfaces that v1 is a checkpoint. A site with no forward plan is a site that will not be iterated — and an un-iterated site decays (content goes stale, the conversion path is never sharpened, the deferred-but-wanted features never land). The cost is not immediate breakage; it is slow irrelevance.
- **The cost compounds with phase 33.** Phase 33 (maintenance cadence) is "keep it from rotting"; phase 32 is "keep it improving." Skipping both is the strongest version of the decay path. Skipping 32 alone means the site is maintained-but-static — alive but never better.
- **Legitimate skip cases:** a genuinely one-shot site with no intended future (a single-event landing page that will be retired after the event), or a user who explicitly wants to run v1 untouched for a long observation period before deciding anything. For these the agent records the rationale in `.website-builder/decisions/skip-phase-32.md` and moves on — informed choice, not forced planning.

If skipped, the agent logs the decision + surfaced cost and advances to phase 33. It does not refuse; it does not let "v1 is done forever" pass without the user having seen the checkpoint framing.

## Gating rules

Phase 32 has **no refusal gate** (per the seed — `Gating: none`). The standards that still apply:

- **Roadmap items are specific, not a restatement of "keep working."** "Improve SEO" is not a roadmap item; "add FAQ structured data to the 3 service pages once we see which questions show up in Search Console" is. The agent produces actionable specificity, not vague aspiration. Not a pipeline gate, but the agent does not hand the user a roadmap that is really just "do more, somehow."
- **Items are grounded in this site, not generic web advice.** The best items come from the phase-3 conversion outcome, the phase-30 analytics signal, and the consciously-deferred decisions — not a generic "every site should add a blog" checklist. The agent grounds the roadmap in what this specific project is and already wanted.
- **Timing aligns to the chosen cadence.** A quarterly-cadence user gets quarterly-shaped timing, not a weekly sprint plan they will not follow.

## Tools and skills used

- **`Edit` / `Write`** — to author `roadmap.md` in the user's project.
- **`AskUserQuestion`** — the user's own sense of what is next (the highest-value input — the agent surfaces deferred-decision candidates and analytics-driven candidates, but the user's "the thing I really want next is X" is the substance; the agent shapes it into a concrete item, does not invent the priority).
- **`Read`** — `decisions/*deferred*.md` (consciously-deferred build decisions = top-quality roadmap inputs), `project.yaml.requirements` (the conversion outcome v1.1 items sharpen), `post-launch/config.yaml` (the iteration cadence the timing aligns to), `audit/POST-DEPLOY-REPORT.md` (the analytics that will reveal what to prioritize).
- **`Read` (sitemap):** `sitemap.yaml` — archive types with one entry, content types the site is structured for but has not grown into = concrete roadmap candidates.

No subagent spawn. The `wb-postlaunch` phase-group skill carries phases 31-34 (run once at launch); the `roadmap.md` is a standing input for the post-launch *maintainer*'s `iterate`/`section-add`/`page-add` skills (decision 49) — **referenced, not authored here**.

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| `.website-builder/roadmap.md` | 3-5 specific v1.1 items (what / why / rough-when), ordered by leverage, aligned to the chosen iteration cadence | The site's forward path; a standing input the post-launch maintainer's iterate/section-add/page-add skills execute against |
| `.website-builder/decisions/skip-phase-32.md` *(when applicable)* | Standard decision-doc frontmatter + body | Created only when the user deliberately skipped roadmap planning with the checkpoint-framing cost surfaced |

The `roadmap.md` (or the logged skip with surfaced cost) is the artifact.

## Common failure modes

**v1 treated as the finish line.** The seed's named failure. The user ships and mentally closes the project; the site never improves and slowly stops mattering. Phase 32's whole job is the reframe — produce a concrete forward path so "what's next" has an answer the user and the maintainer can act on, rather than a vague intention that never resolves.

**A roadmap that is just "keep working on it."** "Improve content, improve SEO, improve conversion" — five ways of saying "do more." Not a roadmap. The agent produces items specific enough to pick up cold: named page, named integration, named experiment, with the why and the rough when.

**Generic web-advice items instead of site-grounded ones.** "Add a blog, add testimonials, add a newsletter" — pulled from a generic checklist, not from what this project is or wanted. The agent grounds items in the phase-3 conversion outcome, the consciously-deferred decisions, and the analytics signal — the roadmap is *this site's* next steps, not web-best-practices boilerplate.

**False-precision timing.** A week-by-week Gantt for a user who picked a quarterly cadence and will look at the site four times a year. The agent's timing is rough and cadence-aligned — actionable, not theatre.

**The agent decides the priorities.** The user's sense of what matters next is the substance; the agent surfaces strong candidates (deferred decisions, analytics-driven fixes) and shapes the user's priority into concrete items — it does not impose its own roadmap over the user's actual intent (same substance-is-yours discipline as phases 16 + 31).

## Reference materials

- **Design doc — phase pipeline source:** `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` § 32 (seed — `Gating: none`; common failure = muggles see v1 as the end, agent surfaces v1 is a checkpoint)
- **Design doc — post-launch maintainer (the iterate/section-add/page-add skills the roadmap feeds, decision 49):** `Workstreams/website-builder/cross-cutting/DESIGN-post-launch-template.md` § Maintenance skill bundle (`wb-maintain-iterate` / `wb-maintain-section-add` / `wb-maintain-page-add`) + § Phase 31-34 vs maintainer template — **referenced, not authored here**
- **Design doc — pipeline integration:** `Workstreams/website-builder/foundation/DESIGN-architecture.md` § Phase contracts
- **Phase 3 (the conversion outcome v1.1 items sharpen):** `phase-contracts/03-requirements.md` § What Claude must establish
- **Phase 31 (the prior post-launch phase; the once-at-launch framing):** `phase-contracts/31-launch-announcement.md` § Mission
- **Phase 33 (the maintenance-cadence phase whose skip-cost compounds with this one):** `phase-contracts/33-maintenance-cadence.md`
- **Locked decisions 37 + 49** (phases 31-34 run once; maintainer 8-skill bundle owns ongoing) — STATE doc: `Workstreams/website-builder/website-builder.md`

No mandatory external research for this phase (per the INST — first-principles authoring; the gating concern is site-grounded specificity + voice/consistency across the batch). Freshness date for this contract: **2026-05-18**.
