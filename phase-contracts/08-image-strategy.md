---
phase: 8
name: Image strategy + generation plan
group: content-foundation
pipeline_section: content-foundation
skill: wb-content-foundation
prev_phase: 7
next_phase: 9
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-phase-contracts.md
  - Workstreams/website-builder/foundation/DESIGN-architecture.md
  - Workstreams/website-builder/cross-cutting/DESIGN-image-gen-consumer.md
  - Workstreams/website-builder/foundation/DESIGN-project-scaffold.md
---

# Phase 8 — Image strategy + generation plan

> Decide what images the site needs and how each will be sourced — existing, stock, photographer, or AI-generated. The phase that converts the phase-7 audit (*what survives*) into a complete sourcing plan (*what we still need and where it comes from*). The discipline: every planned image has a sourcing decision; no placeholder ships.

## Mission

By phase 8 the user knows what they have that's usable (phase 7 audit). Phase 8 produces the complete picture: every image the site will need — by location, by purpose — with a sourcing method and a status for each. The output is `media/IMAGE-PLAN.md`, the document phase 18 (component build) and phase 19 (composition) pull from when they need imagery, and phase 22 (performance) checks against for image budget.

The sourcing decision per image is one of: use-existing (passed phase-7 audit), license-stock (with provenance discipline carried from phase 7), commission-photographer, or AI-generate. The 2026 consensus the agent works from is a *hybrid* model — custom/photographer for hero + brand-identity + trust-critical imagery (founder portraits, where materiality drives the decision); AI-generation for abstract / environmental / texture / volume needs; stock for licensable-realism / authentic-people where AI still reads as AI. The agent surfaces this trade-off honestly, including the 2026 reality that AI-image saturation has eroded trust in digital imagery — so AI-generation is the muggle-friendly default for *some* image jobs, not all.

The AI-generation path is **consumer-fallback** per locked decision 56. The website-builder plugin does not run image-gen infrastructure itself. It consumes one of three paths (per `cross-cutting/DESIGN-image-gen-consumer.md`): the Jules-Solutions platform image-gen API when a JS vault is present and the feature is reachable; a user-configured provider key (Gemini / OpenAI / Stability / Flux / Imagen / Replicate / fal.ai) as the standalone fallback; or — when neither is available — the **structured-image-brief consumer-fallback**: the agent emits a brand-context-rich image brief the user pastes into their preferred image-gen tool (Midjourney / DALL-E / Imagen / Flux), the user pastes the result back, the agent ingests via phase 6.5. Phase 8 plans the strategy and confirms which path applies; it does not generate images itself (generation happens at phase 17/18 when the components needing imagery exist).

## Entry conditions

Phases 6 and 7 are complete. `.website-builder/media/AUDIT.md` exists with `status: audit-complete`; every `needs-replacement` / `unusable` asset has a phase-8 routing acknowledgment; the user confirmed the audit. `current_phase: 8` is set.

Inputs in scope: the phase-7 audit register (what survives, what needs replacement, what's unusable); phase 2 vision adjectives + phase 5 voice + phase 3 positioning (the brand context every AI-generation brief carries); the phase-4 entity record (jurisdiction can affect stock-license terms; founder-portrait need is established here). The sitemap does not exist yet (phase 9) — so phase 8 plans imagery at the *known-need* level (hero, founder portrait, section backgrounds, social-share image) and revisits page-specific imagery after phase 9 + phase 13-15 when the page/section structure is concrete. Phase 8 produces the *strategy + the known-image plan*; phase 13-15 add page-specific images into the same `IMAGE-PLAN.md`.

For non-greenfield entry modes, imagery extracted via phase 6.5 from the prior artifact is in the phase-7 audit and carried here — typically the prior site's hero is `unusable` (provenance/brand-fit) and phase 8 plans its replacement.

## What Claude must establish

The work product is `.website-builder/media/IMAGE-PLAN.md` — a complete image plan. Per planned image:

1. **Location** — where it goes (hero / founder-portrait / about-section-background / social-share-OG-image / icon-set / texture / etc.). Page-specific entries are added after phase 9 + 13-15; phase 8 covers the known-now set.
2. **Purpose** — what the image does (establish premium register / humanize the founder / signal trust / provide visual rhythm / give the OG card brand presence).
3. **Sourcing method** — one of: `use-existing` (links to the phase-7 audit row), `license-stock` (with the licensing-proof discipline), `commission-photographer` (with a shot-list the agent drafts), `ai-generate` (with the path: platform-API / provider-key / consumer-brief).
4. **AI-generation path (when method is `ai-generate`)** — which of the three consumer paths applies (platform-API / standalone-provider-key / consumer-brief-handoff), set per `cross-cutting/DESIGN-image-gen-consumer.md` selection logic, recorded in `decisions/image-gen-path-{ts}.md`.
5. **Status** — `sourced` (exists, audited, ready) / `planned-ai` / `planned-stock` / `planned-shoot` / `brief-emitted` / `pending`. No image is `placeholder`.
6. **Brand-context bundle (for AI-generated images)** — the structured brand_context built from `brand.yaml` (voice descriptors, palette tokens, style descriptors, type pairing, motion preference, an "avoid" list) per the `DESIGN-image-gen-consumer.md` schema. This is the discipline that keeps AI imagery on-brand instead of generic.

Output schema (`media/IMAGE-PLAN.md`):

```markdown
---
type: image-plan
planned_at: 2026-05-18T18:05:00Z
total_images_known: 9
image_gen_path: consumer-brief    # platform-api | standalone-provider-key | consumer-brief | mixed
image_gen_provider: null          # set when standalone-provider-key (gemini|openai|stability|flux|imagen|replicate|fal)
status: strategy-set              # strategy-set | page-images-pending-phase-9 | plan-complete
phase: 8
---

# Image plan

## Brand context (applied to every AI-generated image)

```yaml
brand_context:
  voice_descriptors: [warm, direct, contrarian]
  color_palette:
    primary: "oklch(64% 0.18 30)"
    neutral_dark: "oklch(15% 0 0)"
  style_descriptors: ["minimalist", "warm grain photography", "natural light"]
  type_pairing: "Fraunces (display) + Inter (body)"
  motion_preference: "subtle"
  avoid: ["stock-photo aesthetic", "corporate handshakes", "gradient blobs", "obvious-AI faces"]
```

## Known images (phase-8 set)

| # | Location | Purpose | Method | AI path | Status |
|---|---|---|---|---|---|
| 1 | Home hero | Establish premium-editorial register on arrival | ai-generate | consumer-brief | planned-ai |
| 2 | Founder portrait (about) | Humanize; signal real practitioner | commission-photographer | — | planned-shoot |
| 3 | Section textures (x3) | Visual rhythm between long sections | ai-generate | consumer-brief | planned-ai |
| 4 | OG / social-share card | Brand presence in link previews | ai-generate | consumer-brief | planned-ai |
| 5 | Portfolio shots (x4) | Show real work | use-existing | — | sourced (audit #4,5,8,9) |
| 6 | Logo raster + favicon | Browser + nav presence | use-existing | — | sourced (audit #3; variants at phase 17) |

## Page-specific images (added after phase 9 + 13-15)

_(empty until phase 13-15 surface page/section imagery needs; same table shape)_

## Photographer shot list (image #2)

[Agent-drafted shot list grounded in phase-2 vision + phase-5 voice — for the user to hand a photographer]

## Per-image AI briefs

[For each ai-generate image: the full brand_context + per-image prompt fields,
in the format the chosen path consumes — see DESIGN-image-gen-consumer.md]
```

## Gating rules

The agent refuses to advance to phase 9 (sitemap) under three conditions:

1. **Any planned image has no sourcing decision.** The non-negotiable. A known image slot with `method: undecided` cannot pass. The agent refuses: *"This hero slot has no sourcing decision. Every image on the deployed site has to come from somewhere — existing, stock, a photographer, or AI. 'We'll figure it out later' becomes a placeholder on the live site, which is the exact failure the discipline prevents. Let's decide this one now: given phase 2's premium-editorial register, the options are commission a photographer (strongest for a hero on a premium site; ~weeks lead time), AI-generate via brief (fast; works for environmental/abstract heros; weaker if the hero needs a real human), or license stock (fast; risks the generic look phase 3 differentiates against). Which?"*

2. **Placeholder accepted as a final state.** When the user says "just use a grey box / lorem-picsum / a placeholder for now," the agent refuses to record that as a plan: *"A placeholder is a deferred decision, not a sourcing method. The site cannot deploy with placeholders (phase 27 polish + phase 29 deploy gate against it). We can mark an image `planned-ai` or `planned-shoot` and resolve it before phase 19 (composition) — that's a real plan with a deadline. What it can't be is 'placeholder forever.' Which real method?"*

3. **AI-generation chosen without a path resolved.** When the user picks `ai-generate` for an image but the consumer path isn't set (platform-API vs provider-key vs consumer-brief), the agent refuses to advance that entry. It runs the `DESIGN-image-gen-consumer.md` selection logic + records the path in `decisions/image-gen-path-{ts}.md`. If the path is "consumer-brief" (no platform, no key), the agent confirms the user understands the round-trip (brief out → user pastes into their tool → user pastes result back → phase 6.5 ingests) before recording the plan as viable.

The override path applies — the user can defer a *page-specific* image's sourcing until phase 13-15 (legitimate; those images' need isn't fully known until the page/section structure exists — the agent records them `pending-phase-13`), but the *known-now* set (hero, founder portrait, OG card, logo) must each have a real method before phase 9.

## Tools and skills used

- **`Read`** — phase-7 `media/AUDIT.md` (what survives / needs replacement), `brand.yaml` (voice + tokens for the brand_context bundle), `project.yaml` (vision adjectives, positioning, entity, languages, vault-presence for path selection).
- **`AskUserQuestion`** — every sourcing decision per image; the AI-path selection when ambiguous; the cost-trade-off conversations (photographer-vs-AI-vs-stock per image job).
- **Image-gen consumer (per `cross-cutting/DESIGN-image-gen-consumer.md`)** — phase 8 does NOT generate images; it *plans* and *confirms the path*. The selection logic: vault present + platform image-gen reachable → platform-API path; else user-configured provider key → standalone path; else → consumer-brief handoff. The agent runs the detection (checks for the platform image-gen MCP / endpoint; checks `keys.yaml` for a configured provider) and records the path. Per locked decision 56 the v1 default is consumer-fallback (the plugin ships before the platform image-gen feature; even inside a JS vault the standalone/consumer path is used until the platform feature ships).
- **`WebSearch`** — to surface current AI-image-model state to the user when they're choosing a generation path/tool (Midjourney = strongest aesthetic + sref style-reference system; Flux 2 = top photorealism; Imagen = explicit-color-word prompting; DALL-E = broadest accessibility/safety; Ideogram = text-in-image) + current stock-vs-custom-vs-AI trade-off framing.
- **`WebFetch`** — to read a provider's current pricing/limits page when the user is choosing a standalone provider key (cost surfacing — "Gemini ImageGen ~$0.04/image; we're planning ~9 images = ~$0.36"), and to verify a stock-image license term if the user plans `license-stock`.
- **`Write` / `Edit`** — author `media/IMAGE-PLAN.md`; author the photographer shot-list; author the per-image AI briefs in the consumer format; write `decisions/image-gen-path-{ts}.md`.

No `context7` (no library docs at this phase). No Playwright. Subagent spawn only for parallel multi-provider option exploration when the user explicitly wants to compare providers; default in-person.

The agent does NOT generate images at phase 8. Generation is a phase-17/18 action (when the design system + the components needing imagery exist). Phase 8 produces the plan + briefs + path; the actual generate-and-ingest happens later via the image-gen consumer + phase 6.5.

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| `.website-builder/media/IMAGE-PLAN.md` | Image plan per schema above | The sourcing plan; load-bearing for phase 13-15 (page imagery added here), phase 17/18 (generation happens, reading the briefs here), phase 19 (composition pulls images), phase 22 (perf image budget), phase 26 (SEO OG image + alt text), phase 31 (launch social imagery) |
| `.website-builder/decisions/image-gen-path-{ts}.md` | Decision-doc frontmatter + the selected path + selection-logic trace | Audit of which consumer path was chosen (platform-API / provider-key / consumer-brief) and why; per `DESIGN-image-gen-consumer.md` |
| `.website-builder/briefs/image-{location}-{ts}.json` *(per AI-generated image)* | Image brief in the consumer format (brand_context + per-image prompt) | The structured brief the user pastes into their image-gen tool (consumer-brief path) or that's sent to the platform API; ingested back via phase 6.5 when the result returns |
| `.website-builder/decisions/08-image-strategy.md` *(optional)* | Standard decision-doc frontmatter + body | Created when the strategy had a contested trade-off (e.g., "photographer vs AI for the founder portrait" — both viable; user chose; reasoning recorded) |

The `IMAGE-PLAN.md` is the required artifact. The image-gen-path decision doc is required when any image is `ai-generate` (the path must be auditable). Per-image briefs are produced for every `ai-generate` image so phase 17/18 can execute generation without re-deriving brand context.

The agent updates `.website-builder/project.yaml.current_phase` to `9` upon user confirmation that every known-now image has a real sourcing method and AI paths are resolved. Phase 9 (sitemap) loads next.

## Common failure modes

**Stock-photo paralysis.** The user spends an hour browsing stock libraries and can't commit. The agent offers the AI-generation default with brand-consistent prompting: *"Stock-photo paralysis usually means nothing in the libraries matches your specific register — which is the signal that this image job wants generation, not stock. I can emit a brand-consistent brief: it carries your palette (oklch primary), voice descriptors (warm-direct-contrarian), style descriptors (minimalist, warm grain, natural light), and an avoid-list (no stock-handshakes, no gradient blobs, no obvious-AI faces). You paste it into Midjourney or Flux or Imagen, get an on-brand result, paste it back, phase 6.5 ingests it. Want me to draft the brief for this hero?"* This is the documented muggle-default for the stock-paralysis failure.

**The user wants AI-generated images for everything including the founder portrait.** The agent surfaces the 2026 trust reality honestly: *"AI is the right call for the section textures, the OG card, abstract/environmental imagery — fast, on-brand, cheap. For your founder portrait specifically, I'd push back: AI-generated human faces increasingly read as AI to visitors, and a premium-positioned practitioner site trades on being real. A real founder photo signals 'a person actually does this work.' Options: AI for everything except the portrait (portrait = a real photo, even a good phone shot in decent light beats an AI face here); or AI for all if budget/time genuinely forbid a shoot, knowing the trade-off. Which?"* The agent informs; the user decides.

**The user has no platform, no provider key, and doesn't want to set one up.** The consumer-brief path applies — and it's the v1 default per decision 56. The agent confirms the round-trip is understood: *"No platform image-gen, no provider key — that's fine, it's the standard path. Here's how it works: I write a structured brief carrying all your brand context. You open your preferred image tool — Midjourney, DALL-E, Imagen, whatever you already pay for or want to try. You paste the brief, generate, pick the result you like, paste it back here. Phase 6.5 ingests it into the project (and flags if its palette drifted from your brand). You stay in control of the tool; I keep the discipline. Clear?"* Records `image_gen_path: consumer-brief`.

**The user has a provider key but it's for a weak-fit model.** User has an OpenAI key (DALL-E) but the site needs photoreal hero imagery (Flux's strength). The agent surfaces the model-fit reality without forcing a purchase: *"Your DALL-E key works and DALL-E is reliable + safe + broad. For this specific photoreal hero, Flux 2 or Imagen tend to produce stronger results, and Midjourney has the strongest aesthetic control via style-references. Three options: use DALL-E (works; possibly less photoreal-crisp); add a Flux/Replicate key for the hero specifically (the brief is portable — same brief, different tool); or use the consumer-brief path with whatever tool you want to try without committing a key. Which?"* The brief's portability is the load-bearing point — the user isn't locked to one provider.

**The user picks `license-stock` but can't show the license discipline from phase 7.** The agent carries the phase-7 rights discipline forward: *"Stock is a valid method — but the same provenance rule from phase 7 applies: a stock image needs a real license you can show, not 'I found it on a free site once.' If you license from a known agency (Shutterstock / Getty / Adobe Stock / Unsplash-with-current-license-terms), record the license + its terms here; phase 7's rights-acknowledgment discipline carries forward. Which agency, and do you have/will-you-get a documented license?"*

**Page-specific images can't be planned yet (sitemap doesn't exist).** This is expected, not a failure. The agent scopes correctly: *"We can plan the known set now — hero, founder portrait, OG card, logo, the portfolio shots that survived audit. Page-specific images (a services-page diagram, a pricing-page illustration) depend on the sitemap (phase 9) and the per-section content (phase 13-15) that don't exist yet. I'm marking those `pending-phase-13` in the plan; phase 15 adds them into this same `IMAGE-PLAN.md`. The known set still needs real methods now."* Partial-by-design; the schema accommodates `pending-phase-13`.

**The user wants placeholders "just to see the layout".** The agent distinguishes design-time placeholders from shipped placeholders: *"For previewing layout during phase 14 (wireframes) and phase 18-19 (build), the agent uses dimension-accurate grey blocks labelled with the planned image's purpose — that's a build-time scaffold, fine and expected. What can't happen is a placeholder *surviving to deploy*. The plan records the real method; the build uses labelled scaffolds; phase 19 swaps in the real (or generated) image; phase 27 + 29 gate against any placeholder reaching production. So: yes to layout-preview scaffolds, no to placeholder-as-plan."*

**The brand_context the agent builds drifts from the locked brand.** The agent self-checks: the `brand_context` bundle is derived mechanically from `brand.yaml` (palette tokens verbatim, voice descriptors verbatim, style descriptors from the phase-2 vision adjectives). If the agent finds itself inventing style descriptors not grounded in phase 2/5, it stops and surfaces: *"I'm about to put 'cinematic dramatic lighting' in the brief but that's not in your phase-2 vision (which said 'quiet, type-led, warm') — I'd be drifting the brand. Should the brief say 'quiet natural light' to match phase 2, or has the visual direction changed (which would be a phase-2 revisit)?"* Brand-context must trace to locked decisions, not agent taste.

**The platform image-gen feature is referenced but not yet shipped.** Per `DESIGN-image-gen-consumer.md`, even inside a JS vault the v1 path is standalone/consumer until the platform feature ships. The agent does not assume the platform path: *"This is running in a Jules-Solutions vault, but the platform image-gen feature isn't shipped yet (it's a separate cross-workstream effort). So v1 uses the standalone/consumer path like everyone else. When the platform feature ships, switching is a small follow-up (`wb image migrate-to-platform`) — for now, consumer-brief or your own provider key. Which?"* Forward-compat without false assumption.

## Reference materials

- **Design doc — phase pipeline source:** `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` § 8 (seed for this contract)
- **Design doc — the image-gen consumer contract (READ IN FULL per Lock 4):** `Workstreams/website-builder/cross-cutting/DESIGN-image-gen-consumer.md` — the three execution paths (platform-API / standalone-provider-key / consumer-brief), the selection logic, the brand_context schema, versioning + storage layout, post-processing (format conversion / responsive variants / alt-text / palette-validation), the phase-contract invocation table (phase 8 sets strategy; 17/18 generate; 19 composes; 20 variants; 22 perf-checks), cost surfacing, failure modes — this is the load-bearing design doc for phase 8 per locked decision 56
- **Design doc — pipeline integration:** `Workstreams/website-builder/foundation/DESIGN-architecture.md` § Cross-workstream platform-feature consumers (`consumers/image-gen.md`)
- **Design doc — media/ + briefs/ layout:** `Workstreams/website-builder/foundation/DESIGN-project-scaffold.md` § `media/` + § `briefs/` + § `decisions/`
- **External — AI image-gen current state (loaded fresh 2026-05-18 for this contract):**
  - 2026 model landscape — https://medium.com/@cliprise/ai-image-generation-in-2026-midjourney-flux-2-imagen-4-and-beyond-7934a9228e98 (Midjourney = strongest aesthetic + mature sref style-reference system; Flux 2 Pro = top photorealism/product accuracy; Imagen = explicit-color-word prompting; DALL-E 4o = broad accessibility/safety; Ideogram V3 = text-in-image)
  - Prompt-pattern fundamentals — https://www.novakit.ai/blog/ai-image-generation-tutorial (subject → action → environment → lighting → lens/camera → style; negative prompts mostly obsolete in 2026; model-specific styles: Flux wants photo params like "50mm f/1.8 Kodak Portra 400 grain", Midjourney wants style refs, Imagen wants explicit color words)
  - AI-gen APIs compared — https://www.novakit.ai/blog/ai-image-generation-apis-2026-compared (provider-key path options)
  - Stock-vs-custom-vs-AI 2026 strategy — https://www.stockphotosecrets.com/stock-agency-insights/stock-photos-vs-custom-photography-in-2026-shutterstock.html (hybrid model: custom/photographer for hero+brand+trust-critical; AI for 70-80% of volume/abstract; stock for licensable-realism)
  - Website image-system planning — https://www.technosidd.com/2026/03/building-website-image-system-sourcing-stock-photos-for-every-page-type.html (treat visuals as brand infrastructure: define photo style, map page-types to image jobs, standardize aspect ratios, consistent editing recipe, source in cohesive batches)
  - 2026 trust reality — https://www.photocase.com/guide/stock-photography-or-custom-shoots-in-2026-shutterstock/ (AI-image saturation eroding trust in digital imagery; audiences increasingly drawn to visuals that feel real — why the agent pushes back on AI founder portraits)
- **Locked decisions:** decision 56 (cross-workstream platform features absorbed via consumer-fallback in v1 — STATE doc `Workstreams/website-builder/website-builder.md`); decision 9 + 3 (image-gen scope cross-workstream; plugin works fully standalone with provider-key fallback)
- **Agent profile — anti-vision lock:** `${CLAUDE_PLUGIN_ROOT}/agents/website-builder.md` § What you do NOT do ("Generate placeholder images on a deployed site" — refuse; every planned image has a sourcing decision) + § Voice characteristics (surfaces AI-vs-photographer trade-offs as honest options, not decrees)
- **Cross-rule:** `.claude/rules/tool-dependency-discipline.md` (image-gen provider APIs are Tier 2 third-party tools; the consumer-brief path is the documented fallback, not a silent degradation; key failures surface per Tier 2)
