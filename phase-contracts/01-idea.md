---
phase: 1
name: Idea
group: discovery-strategy
pipeline_section: discovery-strategy
skill: wb-discovery
prev_phase: ~
next_phase: 2
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - DESIGN-phase-contracts.md
  - DESIGN-architecture.md
  - DESIGN-project-scaffold.md
---

# Phase 1 — Idea

> Capture the user's idea in their own words. The first thing the agent does. The smallest exit criterion in the pipeline — one paragraph — but the load-bearing one: everything downstream composes from it.

## Mission

This is where the project starts. The user shows up wanting "a website" and the agent's job is to extract what that actually means *for them*, in *their own words*, before any opinion gets imposed on it.

The agent is not trying to write marketing copy here. It is not trying to draft a vision statement. It is trying to surface the underlying intent — the answer to *"if this site succeeds, what does the world look like?"* — in language the user themselves would recognize as theirs. That paragraph is the seed. Phase 2 (vision) layers the visual + emotional shape on top; phase 3 (requirements) layers the audience + conversion on top of that; phase 5 (brand voice) extracts how it should sound. None of those phases can do their work cleanly if phase 1 has captured someone else's idea phrased in someone else's voice.

The output is one paragraph stored in `.website-builder/project.yaml.idea`. Short. Specific. The user's words. The agent does not polish. The agent does not "professionalize." The agent extracts and reflects back until the user reads it and says *"yes, that."*

## Entry conditions

The user has invoked the website-builder agent — via the `/website-builder` slash command, a "help me build a website" / "I need a website for X" prompt, a pasted artifact (one-shot AI output, Figma URL, deployed-site URL), or a partial project the bootstrap skill routed into the pipeline.

`.website-builder/` may or may not exist yet. The bootstrap skill (`wb-bootstrap`, shipped Phase 1 of the build) has already run if the directory is being initialized this session; project.yaml exists with at least `name`, `slug`, `started_at`, `entry_mode`, and `current_phase: 1` set. If the user is mid-project resuming and `current_phase` is past 1, this contract does not fire — the relevant downstream phase's contract does.

For non-greenfield entry modes (`has-existing-site` / `has-ai-output` / `has-Framer-attempt` / `has-Figma-file`), phase 1 still runs first to capture the underlying idea — the artifact is the *what they tried so far*, not the *what they want*. The agent surfaces this distinction and asks the user to articulate the idea independently of what they've already produced.

## What Claude must establish

The work product of this phase is a single paragraph — three to six sentences — written in the user's voice that answers, at minimum, three implicit questions:

1. **What is this site for, fundamentally?** Not the deliverable ("a landing page", "a portfolio") but the underlying purpose ("a place where people who care about X can find me and what I do").
2. **For whom does it exist?** A first-pass audience sketch. Not personas yet (phase 3 owns that); just a rough sense of who the user imagines reading or using the site.
3. **What does success look like one year from now?** The future-state the site is meant to contribute to. The implicit theory of change.

The agent extracts these by conversation. Typical opening question: *"Before we talk about how it should look or what pages it should have — tell me, in your own words, what this site is for. If it succeeds, what does the world look like a year from now?"*

The user's answer is rarely complete on the first pass. The agent reflects back, asks follow-ups, and lets the paragraph develop iteratively until the user explicitly confirms the captured version. The agent does NOT write the paragraph and ask the user to approve — it captures the user's words as they speak them, then offers the user the chance to read it back and edit.

Output schema in `.website-builder/project.yaml`:

```yaml
idea:
  captured_at: 2026-05-18T14:32:00Z
  paragraph: |
    [The user's one-paragraph statement in their own words.
    3-6 sentences. Specific verbs. Specific outcomes.
    Audience hint. Success-state hint.]
  captured_via: conversation  # or: pasted-by-user, freewrite
  iteration_count: 2          # how many rounds of refinement
```

## Gating rules

This is the pipeline entry point — there is no prior phase to gate against. **The phase has no upstream gates.**

The agent does, however, refuse to advance to phase 2 (vision) without the idea paragraph being captured AND the user having confirmed it reads true. The exit criterion is the artifact, not the conversation; the agent verifies that the captured paragraph satisfies the three implicit questions above before allowing phase progression.

The agent refuses three specific anti-patterns during this phase:

1. **The feature-list disguised as an idea.** When the user opens with *"I need a website with a home page, an about page, a services page, and a blog"*, the agent refuses to capture that as the idea. That is a sitemap (phase 9). The agent reflects: *"That's what the site has. What's it for? If you imagine the about page is read by exactly the right person on exactly the right day, what just happened in their life?"*

2. **The aesthetic-as-purpose substitution.** When the user says *"I want something clean and modern and professional"*, the agent refuses to treat that as the idea. That is vision (phase 2). The agent reflects: *"Those are visual notes I'll come back to next. Right now, what is the site for? Not what it looks like — what it does for the people who arrive."*

3. **The premature-handoff move.** When the user says *"just write me one — figure it out, you know what's good"*, the agent refuses. The user paid for discipline; delivering "I'll figure it out" produces a generic site that drifts apart in 3 weeks. The agent reflects: *"I won't make this decision for you — it's the only one that's actually yours. Try the question one more way: what do you want to be true after this site exists that isn't true now?"*

The agent does NOT refuse the user proceeding to phase 2 if they cannot answer the *full* three-question shape — partial answers are allowed; the missing parts surface in phase 2 or phase 3. The minimum is one paragraph that includes a verb (what the site does) and an object (who or what is on the receiving end). Anything below that is not yet an idea; it is a desire for an idea.

## Tools and skills used

- **`AskUserQuestion`** — the primary tool of this phase. The agent uses it for the opening question + each follow-up + the final confirmation read-back. Liberal use; this is conversation, not interrogation.
- **`Write`** — to update `.website-builder/project.yaml` with the captured idea.
- **`Edit`** — to refine the paragraph across iteration rounds before final user confirmation.
- **`Read`** — only to re-read prior conversation context if the agent loses thread; no design-doc reads are needed during the conversation itself.

No external tools (no WebFetch, no WebSearch, no context7, no Playwright) — this phase is pure conversation. The agent is establishing the *what* before the *how*; outside reference does not help here.

No subagent spawns. The agent does this phase in-person, not delegated; the muscle of asking, listening, reflecting is the actual product.

No phase-group skill is loaded yet beyond `wb-bootstrap` (which has just finished). The `wb-discovery` phase-group skill is the next thing to load at the transition into phase 2; phase 1's instructions live entirely in this contract MD plus the agent profile.

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| `.website-builder/project.yaml` | adds `idea:` key per schema above | The captured paragraph + capture metadata; load-bearing for phases 2-5 |
| `.website-builder/decisions/01-idea-captured.md` *(optional)* | Standard decision-doc frontmatter + body | Created only when the idea-capture surfaced a non-obvious decision (e.g., the user reframed from a feature-list to a purpose-statement); not always needed |

The idea paragraph is the *only* required artifact. Decision logs are surfaced when warranted, not produced by reflex.

The agent updates `.website-builder/project.yaml.current_phase` to `2` upon user confirmation that the idea reads true and the agent is satisfied the three implicit questions are addressed at the minimum bar. Phase 2 (vision) loads next.

## Common failure modes

**The user has a half-formed idea expressed as a feature list.** *"I need a website with a home page, an about, services, contact, and a blog. The blog should have categories. The contact form should send to my email."* The agent reflects: *"Those are pieces. Let's back up. If this site succeeds and you imagine the right person reading exactly the right page on exactly the right day — what happened in their life? What did they do next?"* The agent then captures *that* answer as the idea, holding the feature list for the sitemap phase (9).

**The user has a half-formed idea expressed as aesthetic preferences.** *"I want something minimal, clean, professional, like Apple but warmer."* The agent reflects: *"Those notes are gold — I'll bring them back at phase 2. Right now, the question is different. What does this site *do* for the people who arrive? Why does it exist?"* The visual notes are stored in conversation memory and surface again in phase 2 (vision) when they have a home.

**The user has a half-formed idea expressed as comparison.** *"I want a site like X.com but for my industry."* The agent doesn't immediately load X.com. First it reflects: *"What about X.com makes it the model? Is it the audience they reach? The way they sound? The thing they help people do? Pull out the part of X.com that is actually about your project, and let's start there."* The competitor reference itself becomes input to phase 2-3, not phase 1.

**The user gives a generic, on-brand-for-everyone description.** *"We help businesses succeed by leveraging cutting-edge solutions."* The agent reflects: *"That description fits a million companies. What's the specific verb? Who, specifically, does the site help? When they walk away, what do they have that they didn't have before?"* The agent forces specificity. If the user genuinely cannot specify, that is a phase-3 problem (requirements) — but the agent surfaces it now: *"You may not know yet who this is for. That's OK; phase 3 will tighten it. For phase 1, capture even the rough version — 'people who [do thing]' — so we have something to work with."*

**The user has the idea fully formed but in a different domain.** They are a Swiss commodity trader explaining a site for fellow traders in the language of trading desks. The agent does NOT translate to muggle-friendly language. The agent captures the user's words — domain vocabulary intact — and lets the *user's* customers read it later in their shared vocabulary. The agent's only intervention is to ensure the paragraph would be readable by *someone* (not undefined acronyms that even the trader's customers wouldn't know), and even that intervention is offered as a question, not imposed as a fix.

**The user wants the agent to "just write it for them."** *"You know what good websites say. Write me a good idea statement."* The agent refuses. *"This is the one thing I can't delegate back to me. The idea is the only artifact that has to be yours — every other thing the site eventually does composes from this. If I write it, I'm building someone else's site with your name on it. Let's try the question one more way."* The agent tries a different angle (the future-state question, the audience question, the *why-now* question) until the user produces something they recognize as theirs.

**The user is ingesting a prior artifact (entry modes 2-5) and wants to use the artifact's existing copy as the idea.** *"The hero copy on my old site says it all — just use that."* The agent honors the prior work but does not skip the question: *"That hero copy is a useful anchor. Read it now and tell me: does it still say what you actually mean? Or has your thinking moved? The site we're building is the version you want now, not the version you had then."* The captured idea reflects current intent; the prior copy is logged as reference, not adopted verbatim.

## Reference materials

- **Design doc — phase pipeline source:** `DESIGN-phase-contracts.md` § 1 (seed for this contract)
- **Design doc — pipeline integration:** `DESIGN-architecture.md` § Phase contracts (the schema authority for all 38 contracts)
- **Design doc — output location:** `DESIGN-project-scaffold.md` § `project.yaml` (schema for the `idea:` key)
- **Agent profile — anti-skip enforcement:** `${CLAUDE_PLUGIN_ROOT}/agents/website-builder.md` § Anti-skip enforcement + § Voice characteristics (this contract's gating-refusal language must match the agent's voice)
- **VISION doc — why phase 1 exists at all:** `VISION-website-builder.md` (the rationale for discipline-over-output-speed)

No external reference data (no `voice-archetypes/`, no `awesome-design-md-corpus/`, no Library/) is read in phase 1 — that catalogue load happens at phase 2 onward when the *how* surfaces.
