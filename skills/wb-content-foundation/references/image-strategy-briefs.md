# Phase 8 — Image strategy + generation-brief reference

> Loaded when running phase 8. The three consumer paths + selection logic, the `brand_context` schema, per-image brief recipes, 2026 AI-image model-fit + prompt-pattern guidance, and the photographer-vs-AI-vs-stock trade-off framing. Source of truth: `${CLAUDE_PLUGIN_ROOT}/phase-contracts/08-image-strategy.md` + `DESIGN-image-gen-consumer.md` (READ IN FULL per Lock 4). Decision 56.

## What phase 8 produces

`.website-builder/media/IMAGE-PLAN.md` — per planned image: location / purpose / sourcing method (`use-existing` | `license-stock` | `commission-photographer` | `ai-generate`) / AI path (when `ai-generate`) / status (`sourced` | `planned-ai` | `planned-stock` | `planned-shoot` | `brief-emitted` | `pending` — never `placeholder`) / brand-context bundle (for AI images). Phase 8 plans + confirms the path; it does **not** generate (generation is phase 17/18 when components exist). Page-specific images may defer to phase 13-15 (`pending-phase-13`); the known-now set (hero, founder portrait, OG card, logo) must each have a real method before phase 9.

## The three consumer paths + selection logic

Per `DESIGN-image-gen-consumer.md`:

```
if vault_detected() and platform_image_gen_reachable():  → Path 1 platform-API
elif user_provider_key_configured():                     → Path 2 standalone-provider-key
else:                                                    → Path 3 consumer-brief handoff
```

- **Path 1 — platform image-gen API.** JS vault + platform image-gen feature reachable. Server-side routing/versioning/post-processing. NOTE: per decision 56, the platform feature is not yet shipped — so **even inside a JS vault, v1 uses Path 2/3**. Do not assume Path 1. Forward-compat: when the feature ships, `wb image migrate-to-platform` switches existing projects.
- **Path 2 — standalone provider key.** `keys.yaml` configured (Gemini / OpenAI / Stability / Flux / Replicate / fal.ai). Direct HTTP via Bash + curl per the per-provider recipe. Client-side post-processing (format conversion + responsive variants — needs `sharp`/Pillow).
- **Path 3 — consumer-brief handoff (the v1 default per decision 56).** No platform, no key. The agent emits a brand-context-rich brief; the user pastes it into their image tool (Midjourney / DALL-E / Flux / Imagen); the user pastes the result back; **phase 6.5 ingests it** (and flags palette drift). The user stays in control of the tool; the agent keeps the discipline.

Record the chosen path in `decisions/image-gen-path-{ts}.md` (required when any image is `ai-generate`). Path 3 confirmation: ensure the user understands the round-trip (brief out → user pastes into their tool → user pastes result back → 6.5 ingests) before recording the plan as viable.

Surface the gap (Path 3 fallback prompt) honestly — never silently fall back to placeholders (Tier 4 per `.claude/rules/tool-dependency-discipline.md`).

## brand_context schema (built mechanically from brand.yaml)

```yaml
brand_context:
  voice_descriptors: [warm, direct, contrarian]       # verbatim from brand.yaml
  color_palette:
    primary: "oklch(64% 0.18 30)"                     # tokens verbatim
    neutral_dark: "oklch(15% 0 0)"
  style_descriptors: ["minimalist", "warm grain photography", "natural light"]  # traced to phase-2 vision adjectives
  type_pairing: "Fraunces (display) + Inter (body)"
  motion_preference: "subtle"
  avoid: ["stock-photo aesthetic", "corporate handshakes", "gradient blobs", "obvious-AI faces"]
```

**Brand-context must trace to locked decisions, not agent taste.** If about to write a style descriptor not grounded in phase-2/5, stop and surface: *"I'm about to put 'cinematic dramatic lighting' in the brief but that's not in your phase-2 vision (which said 'quiet, type-led, warm'). Should it say 'quiet natural light' to match, or has the visual direction changed (a phase-2 revisit)?"*

## 2026 AI-image model-fit + prompt patterns

Verified via WebSearch 2026-05-18 (consistent with the phase-8 contract's cited research):

- **Prompt structure:** subject → action → environment → lighting → lens/camera → style. Negative prompts are mostly obsolete in 2026 (modern models follow positive instructions; verbose negative lists hurt).
- **Model-specific styling:**
  - **Flux 2** — top photorealism; wants photo params ("85mm, f/1.8, shallow depth of field, warm color temperature, Kodak Portra 400 grain"). Executes exact composition briefs with higher fidelity than Midjourney.
  - **Midjourney** — strongest aesthetic; responds to artistic direction + mood + style-references (sref system); aesthetically *interprets* rather than literally follows.
  - **DALL-E** — broadest accessibility/safety; forgiving of imprecise natural-language prompts; rewrites internally.
  - **Imagen** — explicit-color-word prompting.
  - **Ideogram** — text-in-image; specify exact text/formatting/placement.
- **The core advice:** pick the model whose default aesthetic is closest to what you want, then nudge — don't fight the model. The brief is portable across providers (same brand_context + prompt; different `output_format`).

## Photographer vs AI vs stock — the 2026 trade-off framing

The 2026 hybrid consensus (also in the phase-8 contract's research): custom/photographer for hero + brand-identity + trust-critical (founder portraits — materiality matters); AI-generation for abstract/environmental/texture/volume (70-80%); stock for licensable-realism where AI still reads as AI. **AI-image saturation has eroded trust in digital imagery in 2026** — push back honestly on AI founder portraits: *"AI-generated human faces increasingly read as AI; a premium practitioner site trades on being real. A real founder photo signals 'a person actually does this work.'"* Inform; the user decides.

## Per-image brief recipe (for ai-generate images)

`.website-builder/briefs/image-{location}-{ts}.json` per AI image. The brand_context block (above) + per-image prompt fields:

```yaml
prompt:
  subject: "Hero image for the home page of <project>"
  composition: "warm wood surface; coffee cup with steam; weathered notebook"
  mood: "quiet morning intentionality"
  technical: { aspect_ratio: "16:9", resolution_target: "1920x1080", format: "webp" }
```

Translate per provider (Gemini wants natural-language descriptors woven in; DALL-E a single rich English prompt; Stability/Flux map the `avoid` list to a negative prompt; Replicate/fal.ai vary per model). Detail in `${CLAUDE_PLUGIN_ROOT}/consumers/image-gen.md` per-provider recipes.

## Gating + failure-mode handling

The non-negotiable discipline: every planned image has a sourcing decision; placeholder is a deferred decision not a method (build-time labelled grey scaffolds for layout preview are fine; placeholder-as-plan / placeholder-surviving-to-deploy is not — phase 27 + 29 gate against it); `ai-generate` cannot pass without a resolved consumer path.

| Situation | Handling |
|---|---|
| **Stock-photo paralysis** | Signal that the image job wants generation, not stock. Offer the brand-consistent brief (palette + voice + style + avoid-list); user pastes into Midjourney/Flux/Imagen; 6.5 ingests. The documented muggle-default. |
| **User wants AI for the founder portrait** | Surface the 2026 trust reality. AI for textures/OG/abstract; push back on the portrait (a good phone shot in decent light beats an AI face here). Inform; user decides. |
| **No platform, no key, won't set one up** | Path 3 consumer-brief — the v1 default. Confirm the round-trip is understood. Record `image_gen_path: consumer-brief`. |
| **Provider key for a weak-fit model** | Surface model-fit without forcing a purchase. The brief is portable — use the key, add a Flux/Replicate key for the hero specifically, or use the consumer-brief path with any tool. |
| **`license-stock` without phase-7 rights discipline** | Carry the phase-7 rights rule forward — a real license you can show, from a known agency, terms recorded. |
| **Page-specific images can't be planned yet** | Expected, not a failure. Plan the known-now set; mark page-specific `pending-phase-13`; phase 15 adds them to the same IMAGE-PLAN.md. |
| **Platform image-gen referenced but unshipped** | Don't assume Path 1. v1 uses Path 2/3 even in a JS vault. Forward-compat without false assumption. |

Provider failures (rate limit / content-policy refusal / invalid key / network) are Tier 2 per `.claude/rules/tool-dependency-discipline.md` — surface, retry, fall back to consumer-brief, never silently degrade. Cost-surface on first use of each provider (loud first, muted totals after).
