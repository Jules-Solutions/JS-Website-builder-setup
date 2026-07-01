---
name: wb-discovery
description: This skill should be used when the website-builder agent enters the discovery-strategy phase group — phases 1 through 5. Trigger when the user says "let's start", "I have an idea for a website", "help me figure out what I want", "what should my site say", "who is this site for", "what should it look like", "how should my brand sound", "I want it to feel like X", "here are some sites I like", "who are my competitors", or when `project.yaml.current_phase` is 1, 2, 3, 4, or 5. Drives the agent through Idea capture (1), Vision (2), Requirements (3), Project/Company info (4), and Brand voice & tone (5). Conversational and AskUserQuestion-heavy; no code is written in this group.
version: 0.1.0
---

# wb-discovery — Discovery & Strategy (phases 1-5)

> The first conversational arc of the pipeline. Captures *what the site is for* (1), *what it feels like* (2), *who it is for and how it differs* (3), *who is behind it* (4), and *how it sounds* (5). Nothing downstream composes correctly if this group captures someone else's idea in someone else's voice.
>
> Design-doc primacy: this skill *points at* the five phase contracts and design docs; it does not paraphrase them. The contracts are the substantive behavioral spine. Read the contract for the active phase before acting in it.

## What this skill provides

Procedural workflow for the discovery-strategy group. The agent stays in conversational mode the whole time — `AskUserQuestion` is the primary tool across all five phases. The phase contracts at `${CLAUDE_PLUGIN_ROOT}/phase-contracts/0N-name.md` carry per-phase Mission / Entry / Exit / Gating / Tools / Outputs / Failure modes. This skill carries the cross-phase discipline that ties the five together and tells the agent which contract to read when.

Two architectural anchors govern this whole group (locked decisions, STATE doc `website-builder.md`):

- **Decision 2 — audience driven by data, not intuition.** Phase 3's persona is rigorous, grounded in what the user actually says about their buyer — never a guessed-from-vibes persona. (The Tier-1 research questionnaire at `QUESTIONNAIRE-tier-1.md` is a *separate* instrument Jules uses for product research; do not confuse it with the phase-3 persona artifact — phase 3 captures *this user's* buyer into `project.yaml.requirements`.)
- **Decision 4 — no wizard UI; Claude Code is the wizard.** There is no form, no GUI, no multi-step web flow. The conversation *is* the wizard. The agent's questioning discipline is the entire interface. Do not build or imply a UI.

## The five phases — pointer map

For each phase, read the contract first, then run the conversation it specifies. The contract is authoritative for gating; this skill adds the cross-phase glue.

### Phase 1 — Idea → read `phase-contracts/01-idea.md`

Capture one paragraph (3-6 sentences) in the user's own words answering: what the site is fundamentally for, who it exists for (rough sketch), what success looks like in a year. Output: `project.yaml.idea`.

**This skill's discipline:** the agent does NOT write the paragraph and ask for approval — it extracts the user's words, reflects back, iterates, and lets the user confirm "yes, that." Refuse the three anti-patterns the contract names (feature-list-as-idea, aesthetic-as-purpose, premature-handoff). Pure conversation — no WebFetch/WebSearch/context7. The `wb-discovery` skill loads at the transition into phase 2; phase 1 itself runs on the contract + agent profile.

### Phase 2 — Vision → read `phase-contracts/02-vision.md`

Capture 3-5 reference URLs + one sentence per URL on *what* is admired + 1-2 sentences on the imagined feel + an extracted 3-6 adjective set. Output: `project.yaml.vision`.

**This skill's discipline:** convert empty descriptors ("clean", "modern", "professional") into concrete observations grounded in specific examples. Use `WebFetch` to load each reference and *discuss* it (not just list it). When the user has no references, walk them through reference-sourcing per `${CLAUDE_PLUGIN_ROOT}/reference-corpus/ECOSYSTEM-CATALOG.md` § Reference resources (Awwwards, Land-book, One Page Love, Mobbin, SaaS Pages) and the runtime corpus at `.website-builder/library/awesome-design-md/` (the Decision-42 auto-clone of 60+ DESIGN.md exemplars; read it if cloned, else fetch via `wb library`). Do not pick references on the user's behalf — surface a shortlist to react to, never decree taste.

### Phase 3 — Requirements → read `phase-contracts/03-requirements.md`

Capture a primary audience persona (role / trigger / evaluation criteria / arrival channel), a single conversion outcome (enforce *one*), 3-5 competitors with positioning notes, and a positioning paragraph. Output: `project.yaml.requirements`.

**This skill's discipline:** this is the data-driven-audience decision (Decision 2). Force specificity — refuse "everyone is the audience", refuse multiple competing conversion outcomes, refuse zero competitor research, refuse slogan-positioning. Run the competitor scan per the current methodology in `references/competitor-scan-methodology.md`. Use `WebFetch` to read each competitor's high-value pages (home / pricing / product / about) and feed the visible positioning back to the user. Help the user shape positioning; the user owns the words.

### Phase 4 — Project / Company info → read `phase-contracts/04-project-company-info.md`

Capture the real entity: name (+ legal name if different), one-sentence what-they-do, origin, location + **jurisdiction** (load-bearing for phase 25 legal), contact channels, existing-assets inventory. Output: `project.yaml.entity` + seeds `inbox/INVENTORY.md`.

**This skill's discipline:** capture what exists; do not invent and do not let the user invent unless the project is explicitly fictional/portfolio (`entity.fictional_or_portfolio: true`). Jurisdiction is mandatory — refuse advancement without it (DACH imprint is legally mandatory; EU GDPR+ePrivacy; CH revFADP). The entity what-they-do must match phase 3 positioning specificity. `WebFetch` is courtesy verification only (confirm a named domain/handle resolves), never investigation.

### Phase 5 — Brand voice & tone → read `phase-contracts/05-brand-voice-tone.md`

Capture five artifacts: a 1-2 sentence voice description, 3-5 voice attributes, a Nielsen Norman 4-dimensional tone profile (humor / formality / respectfulness / enthusiasm, each 3-point), say / never-say example lists, and 1-2 voice exemplars. Output: `brand.yaml.voice` (the FIRST write to `brand.yaml`).

**This skill's discipline:** the never-say list is more diagnostic than the say list — a brand defines itself by what it refuses. The NN4D framework is the empirical scaffold; ground attributes in it. The voice MUST compose with phase 3 positioning — refuse a voice that contradicts it. Surface voice-archetype frameworks (see `references/voice-archetype-frameworks.md`) when the user struggles to find words. No bundled voice corpus ships in v1 — ground the voice work in the NN4D + Aaker + Jung scaffolds in `references/voice-archetype-frameworks.md` and use `WebFetch` to pull named exemplars' public voice guides fresh (Slack, Mailchimp, Patagonia, Stripe). (A curated voice-exemplar corpus is tracked content-authoring follow-up.)

## Cross-phase discipline (the glue)

These hold across all five phases and are why a single skill spans the group rather than five disconnected contracts:

1. **Reread upstream at every phase entry.** Phase 2 rereads the idea; phase 3 rereads idea+vision; phase 4 rereads idea+positioning; phase 5 rereads idea+positioning+entity. The artifacts compose — a vision that ignores the idea, or a voice that contradicts the positioning, is a defect. The agent reads `project.yaml` before opening each phase's conversation.

2. **Refuse generic by reflex, accept partial by judgment.** Every phase has a "refuse empty descriptors / slogans / feature-lists" rule. But every phase also allows *partial* answers to pass with the missing parts surfaced downstream — the user can override a gate with explicit cost-acknowledgement (per `${CLAUDE_PLUGIN_ROOT}/agents/website-builder.md` § Anti-skip enforcement). Refuse genericness; do not refuse a user who has a rough-but-real answer and accepts the documented cost of thinness.

3. **Never write the user's load-bearing artifact for them.** The idea paragraph (1), the positioning paragraph (3), and the voice say/never-say (5) are the artifacts the agent must NOT author on the user's behalf. "Just write it for me" gets a polite refusal + a different question angle, every time. The agent may offer drafts to react to, shortlists to pick from, and frameworks to think with — never the final words.

4. **Decision-2 / Decision-4 hold the whole group.** No wizard UI anywhere (the conversation is the interface). The phase-3 persona is data-driven from what the user says about their buyer, not vibes. These are not phase-local; they shape every interaction in 1-5.

5. **Entry-mode awareness.** For non-greenfield modes (has-existing-site / has-AI-output / has-Framer-attempt / has-Figma-file per `${CLAUDE_PLUGIN_ROOT}/agents/website-builder.md`), prior artifacts are *input*, not *the answer*. Phase 1 still captures the idea independently of what was already tried; phases 2-5 treat extracted prior tokens/copy/voice as one candidate among the user's current intent. Honor prior work; do not adopt it verbatim without the user confirming it still says what they mean now.

## Composable the agent may recommend

This skill does not bundle other skills. At phase 5, recommend the user also invoke `document-skills:brand-guidelines` via the `Skill` tool when they want a fuller brand-voice articulation (it applies a structured brand lens to the voice work). Phrase it as: *"For deeper brand-voice structure, you can also invoke the `brand-guidelines` skill — it gives the voice work a fuller treatment. Optional; we can also stay in our own flow."* Do not vendor or embed it; just point.

`AskUserQuestion` is the core tool across the entire group — it is a CC affordance, not a composable, and it is used liberally everywhere in 1-5.

## Brand-aware behavior

If a `.website-builder/brand.yaml` already exists (re-entry / ingestion), read it and respect the declared brand. If running inside the Jules.Life vault dogfooding context, the Jules.Solutions brand reference at `Agents/Skills/design/_shared/brands/jules-solutions/brand-summary.md` is a *constraint surface only when the user is building for Jules.Solutions or a franchise* — never imposed on an unrelated user's project. Default: brand-neutral.

## What this skill must NOT do

- Build, imply, or describe a wizard UI / form / GUI (Decision 4 — the conversation is the wizard).
- Write the user's idea paragraph, positioning paragraph, or voice say/never-say on their behalf.
- Skip the upstream-reread at any phase entry.
- Treat the Tier-1 research questionnaire as the phase-3 persona source (different instrument; phase 3 captures this user's buyer fresh).
- Accept a phase-3 persona that is intuition/vibes rather than grounded in what the user says about their actual buyer (Decision 2).
- Advance phase 4 without a jurisdiction, or phase 5 with a voice that contradicts phase 3 positioning.
- Adopt a non-greenfield artifact's copy/tokens/voice verbatim without the user confirming current intent.

## Additional resources

### Reference files (loaded on demand)

- **`references/competitor-scan-methodology.md`** — current (2026) B2B competitor-scan methodology for phase 3: primary/secondary/tertiary categorization, the ~5-competitor rule, high-value-page focus list, SWOT + Importance-Performance Analysis, Jobs-to-Be-Done breadth, Kalungi-style scoring matrix. Load when running phase 3 competitor research.
- **`references/voice-archetype-frameworks.md`** — Nielsen Norman 4D scaffold, Aaker's 5 brand-personality dimensions, Jung's 12 brand archetypes (with brand exemplars), and how to use them together at phases 4-5 when the user struggles to find voice words. Load when running phase 5 (and the entity-tone read in phase 4).

### Phase contracts (authoritative — read the one for the active phase)

- `${CLAUDE_PLUGIN_ROOT}/phase-contracts/01-idea.md`
- `${CLAUDE_PLUGIN_ROOT}/phase-contracts/02-vision.md`
- `${CLAUDE_PLUGIN_ROOT}/phase-contracts/03-requirements.md`
- `${CLAUDE_PLUGIN_ROOT}/phase-contracts/04-project-company-info.md`
- `${CLAUDE_PLUGIN_ROOT}/phase-contracts/05-brand-voice-tone.md`

### Design docs (the source of truth this skill points at)

- `DESIGN-phase-contracts.md` § 1-5 — seed for the five contracts
- `DESIGN-architecture.md` § Skills — how phase-group skills layer on the agent
- `${CLAUDE_PLUGIN_ROOT}/reference-corpus/ECOSYSTEM-CATALOG.md` § Reference resources — vision (phase 2) reference-sourcing + competitor (phase 3) sources
- `DESIGN-content-layers.md` § Layer 1 (adjectives → tokens) + § Layer 3 (Content Design JSON, voice → microcopy)
- `DESIGN-i18n.md` § Translation workflow — multi-language voice interaction (phase 5 captures language-neutral profile)
- `DESIGN-project-scaffold.md` § `project.yaml` — schema for `idea` / `vision` / `requirements` / `entity` keys + `inbox/INVENTORY.md` seed
- STATE doc decisions ledger: `website-builder.md` (decisions 2, 4)
- Agent profile: `${CLAUDE_PLUGIN_ROOT}/agents/website-builder.md` § Anti-skip enforcement + § Voice characteristics + § Anti-pattern cheat sheet

### Runtime corpus (cloned into the project — loaded when the user wants to react to options rather than start cold)

- `.website-builder/library/awesome-design-md/` — 60+ DESIGN.md exemplars (phase 2 adjective grounding). This is the Decision-42 auto-clone runtime path (the `awesome-design-md` catalogue key in `scripts/wb_library.py` clones the VoltAgent corpus here at phase-17 entry / session-start). Same SSOT `wb-design-system` cites (`references/oklch-token-system.md`) — read the cloned corpus if present; the agent fetches it via `wb library` if not.

> **No bundled `brand-examples` / `voice-archetypes` corpus ships in v1.** There is neither a bundled copy nor a catalogue clone-key for these. For the phase-2 vision/brand-systems grounding and the phase-5 voice corpus, use the inline phase-2/5 discipline this skill already carries (see § The five phases — phases 2 + 5 — and the cross-phase glue): ground adjectives in the user's specific references via `WebFetch`; build voice via the NN4D + Aaker + Jung scaffolds in `references/voice-archetype-frameworks.md`; pull named exemplars' public voice guides fresh via `WebFetch` (Slack, Mailchimp, Patagonia, Stripe). A curated brand/voice exemplar corpus is tracked content-authoring follow-up, not a v1 dependency.
