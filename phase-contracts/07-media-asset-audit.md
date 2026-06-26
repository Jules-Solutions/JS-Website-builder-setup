---
phase: 7
name: Media refinement / asset audit
group: content-foundation
pipeline_section: content-foundation
skill: wb-content-foundation
prev_phase: 6
next_phase: 8
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-phase-contracts.md
  - Workstreams/website-builder/foundation/DESIGN-architecture.md
  - Workstreams/website-builder/foundation/DESIGN-project-scaffold.md
---

# Phase 7 — Media refinement / asset audit

> Assess every existing media asset — photos, video, logos — for usability: quality, rights, brand-fit. The phase that separates *what the user has* (phase 6 captured it) from *what the user can actually ship* (rights-cleared, quality-sufficient, on-brand). The discipline of phase 7 is surfacing copyright risk loudly.

## Mission

Phase 6 captured everything the user has into `inbox/`. Phase 7 audits it. Every image, video, and logo gets a usability verdict: ready-to-use, needs-edit, needs-replacement, or unusable. Every asset gets a rights verdict: owned / licensed-with-proof / cleared-by-creator / unknown-provenance / known-infringing. The output is `media/AUDIT.md` — the asset register phase 8 (image strategy) consumes to decide what still needs sourcing.

The non-negotiable discipline of phase 7: the agent surfaces copyright issues *loudly* and refuses to proceed with stock photos or third-party images the user cannot show provenance for. This is not legal advice — it is risk surfacing. A site that ships an unlicensed stock photo carries a real, common, expensive liability (reverse-image-search-driven copyright demand letters are a documented cottage industry). The agent's job is to make sure the user is choosing knowingly, never drifting into infringement by omission.

Phase 7 also assesses *quality* and *brand-fit*. A selfie-quality headshot on a site positioned as premium-editorial is a brand-fit failure even if the rights are clean. The agent flags these and offers paths (re-shoot, hire a photographer, AI-generate in phase 8) — it does not decide for the user, but it does not let a brand-fit failure slide past unmentioned.

## Entry conditions

Phase 6 is complete. `.website-builder/inbox/INVENTORY.md` exists with `status: capture-complete`; the user confirmed capture is done. `current_phase: 7` is set.

The phase 6 inventory is the input. Every visual asset row in `INVENTORY.md` (category: visual sources, plus any visual items in testimonials / existing-presence) is in scope for the audit. Logo files from `project.yaml.entity.existing_assets.logo` are in scope. The phase 4 entity record's `photography.status` and `logo.status` flags are cross-checked against what's actually in `inbox/`.

If phase 6 has `pending` items (assets the user promised but didn't supply), phase 7 surfaces them: it does not advance with `pending` visual assets still outstanding when those assets are load-bearing for phase 8. The agent asks the user to supply them or explicitly re-classify them as not-coming (which routes their slot to phase 8 sourcing).

For non-greenfield entry modes, assets ingested via phase 6.5 (extracted from a deployed site, a Figma file, an AI artifact) are audited here too — extracted imagery often has the worst provenance story (a deployed site's hero image may be an unlicensed stock photo the user never knew was a liability).

## What Claude must establish

The work product is `.website-builder/media/AUDIT.md` — a per-asset audit register. Each visual asset gets:

1. **Usability verdict** — one of:
   - `ready-to-use` — quality sufficient, rights clean, on-brand
   - `needs-edit` — fixable (crop, color-correct, format-convert, background-remove, resolution-upscale) — the fix is named
   - `needs-replacement` — quality or brand-fit insufficient; cannot be salvaged by editing; routes to phase 8 sourcing
   - `unusable` — rights-blocked or quality-fatal; must not ship; routes to phase 8 sourcing

2. **Rights verdict** — one of:
   - `owned` — user created it or holds full rights (user attests)
   - `licensed-with-proof` — user has a license; the proof location is recorded
   - `cleared-by-creator` — photographer / designer / contributor cleared use; clearance recorded
   - `unknown-provenance` — user cannot show where it came from → treated as `unusable` until provenance established
   - `known-infringing` — confirmed third-party-owned without license → `unusable`, surfaced loudly

3. **Quality assessment** — resolution (px), format, file size, whether it meets the responsive-variant requirements phase 20 will impose (needs source ≥1920px wide for hero use), color profile sanity, compression artifacts.

4. **Brand-fit assessment** — does this asset's aesthetic match the phase-2 vision adjectives + phase-5 voice + (provisionally) the phase-17 design direction? A technically-perfect image that contradicts the visual register is a brand-fit flag.

5. **Recommended action** — concrete next step per asset (use as-is / specific edit / re-shoot / hire photographer / AI-generate in phase 8 / drop entirely).

Output schema (`media/AUDIT.md`):

```markdown
---
type: media-audit
audited_at: 2026-05-18T17:30:00Z
total_assets: 23
ready_to_use: 11
needs_edit: 5
needs_replacement: 4
unusable: 3
rights_unresolved: 3
status: audit-complete  # audit-in-progress | audit-complete
phase: 7
---

# Media audit

| # | Asset | Source (inbox path) | Usability | Rights | Quality | Brand-fit | Action |
|---|---|---|---|---|---|---|---|
| 1 | Founder headshot | inbox/visual/headshot-2024.jpg | needs-edit | owned | 1200x1600, jpg, slight under-exposure | on-brand | Color-correct + upscale to 2400px (phase 7 edit) |
| 2 | Old-site hero image | inbox/existing-site/hero.jpg | unusable | unknown-provenance | 1920x1080, looks like stock | off-brand (generic) | Drop; AI-generate replacement at phase 8 |
| 3 | Logo (final) | assets/logo-original.svg | ready-to-use | owned | vector, clean | on-brand | Use as-is; generate raster variants at phase 17 |
| 4 | Portfolio shot — Project A | inbox/visual/proj-a-01.jpg | ready-to-use | owned | 3000x2000, sharp | on-brand | Use as-is |
| ... |

## Rights-unresolved (BLOCKING for phase 8 if used)

| # | Asset | Why unresolved | Resolution path |
|---|---|---|---|
| 2 | Old-site hero | Pulled from prior site; user doesn't know original source | Reverse-image-search to identify; if stock-without-license → drop |
| 17 | "Team photo" | Downloaded from a Google search years ago | Almost certainly infringing; drop + replace |
| 19 | Background texture | "I think a designer made it but I'm not sure" | Contact designer for clearance OR replace |

## Quality flags

[Per-asset detail on what's wrong + the fix]

## Brand-fit flags

[Per-asset detail on aesthetic mismatch + options]
```

## Gating rules

The agent refuses to advance to phase 8 (image strategy + generation plan) under three conditions:

1. **Unresolved rights on any asset slated for use.** The non-negotiable. When an asset has `rights: unknown-provenance` or `rights: known-infringing` and the user wants to use it anyway, the agent refuses. It surfaces loudly: *"This image has no provenance — you don't know where it came from. Shipping it is a real, common liability: reverse-image-search-driven copyright demand letters are a documented industry, and 'I didn't know' is not a defense. Three options: (a) establish provenance — I'll help you reverse-image-search it to find the source; if it's yours or licensable, we clear it; (b) drop it and source a replacement at phase 8; (c) you explicitly accept the risk in writing in the decision log — I'll record that you were informed and chose to proceed. I strongly recommend (a) or (b)."* The agent does not block the user's autonomy permanently, but it refuses to let infringement happen silently — option (c) requires an explicit logged acknowledgment.

2. **Audit incomplete.** When visual assets in the phase-6 inventory have no audit verdict (the user wants to "skip the boring part"), the agent refuses to advance with `status: audit-in-progress`. Every visual asset gets a verdict, even a fast one. The agent surfaces the cost: phase 8 (image strategy) plans sourcing based on the audit; un-audited assets become phase-8 surprises ("we thought we had a hero image; it turned out unusable, and now we're sourcing under launch pressure").

3. **`needs-replacement` / `unusable` assets without a phase-8 routing decision.** When an asset is verdicted `needs-replacement` or `unusable`, the agent requires the user to acknowledge that its slot routes to phase 8 sourcing. This prevents the failure where phase 8 plans around assets that the audit already condemned. The acknowledgment is lightweight (the user just confirms "yes, source a replacement at phase 8"), but it must be explicit so phase 8 inherits a clean picture.

The override path applies — the user can explicitly accept rights risk (logged, informed), advance with brand-fit-flagged-but-rights-clean assets (the agent flags the cost to phase 27 polish), or defer some quality edits to a "fix at phase 20 responsive pass" note.

## Tools and skills used

- **`Read`** — to read `.website-builder/inbox/INVENTORY.md` + the visual asset files themselves. The agent reads images directly (it is multimodal) to assess quality + brand-fit — resolution, composition, exposure, aesthetic register, whether the image reads as the phase-2 vision adjectives.
- **`Bash`** — for technical asset inspection: `file` (format), `identify` / `exiftool` (dimensions, color profile, EXIF metadata — EXIF can reveal a stock-agency watermark or a camera that doesn't match the user's claimed authorship), `du` (file size), `ls`. Used to populate the quality column with hard data, not guesses.
- **`WebFetch`** — for reverse-image-search-driven provenance checks. When an asset has `unknown-provenance`, the agent (with user permission) constructs reverse-image-search queries and surfaces what comes back. The agent does NOT auto-upload the user's images anywhere; it guides the user through running the reverse search OR fetches public results when the user provides them.
- **`WebSearch`** — to surface current reverse-image-search tooling state to the user (which tool to use for which provenance question — see Reference materials) + to look up licensing terms when an asset's source is identified (e.g., "this is an Unsplash image — what does the current Unsplash license actually permit?").
- **`AskUserQuestion`** — for every rights attestation ("did you take this photo, or do you have a license for it?"), every quality/brand-fit judgment call surfaced to the user, every routing decision for `needs-replacement` / `unusable` assets.
- **`Write` / `Edit`** — to author and update `.website-builder/media/AUDIT.md`; to perform `needs-edit` fixes that are agent-doable (format conversion via Bash + an image tool, simple crop) when the user wants the agent to do them inline.

No `context7` (no library docs at this phase). No Playwright (asset inspection is local; phase 6.5 owns site walks). Subagent spawn only for genuinely parallel reverse-image-search across many flagged assets — default is in-person per-asset.

The agent does NOT silently exfiltrate the user's images to any third-party reverse-search service. Reverse-image-search is user-driven (the agent tells the user which tool and what to look for) or operates on results the user pastes back. This matters: the user's unpublished photography should not be uploaded to an indexing service without their explicit choice.

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| `.website-builder/media/AUDIT.md` | Media audit register per schema above | The asset register; load-bearing for phase 8 (sourcing plan), phase 18 (component imagery), phase 20 (responsive variants), phase 22 (perf — image budget), phase 26 (SEO — alt text) |
| `.website-builder/media/images/` *(reorganized)* | Audited assets moved from `inbox/` into the working media tree with clean names | Assets that passed audit move from raw inbox into the structured media tree per `DESIGN-project-scaffold.md` |
| `.website-builder/decisions/07-rights-acknowledgment.md` *(conditional — REQUIRED if user overrides a rights flag)* | Decision-doc frontmatter + the agent's surfaced risk + the user's explicit informed acceptance | The audit trail proving the user was informed of a rights risk and chose to proceed; non-optional when a rights override happens |

The `media/AUDIT.md` register is the required artifact. The rights-acknowledgment decision doc is required *if and only if* the user overrides a rights flag (gating rule 1 option c) — it is the one place in this phase where a decision doc is mandatory, not optional, because it is the user's informed-consent record.

The agent updates `.website-builder/project.yaml.current_phase` to `8` upon user confirmation that the audit is complete and all `needs-replacement` / `unusable` assets have a phase-8 routing decision. Phase 8 (image strategy + generation plan) loads next.

## Common failure modes

**The user has selfie-quality photos for a premium-positioned site.** Phase 3 positioned the site as premium-editorial; the user's headshots are phone selfies in poor light. The agent flags the brand-fit gap directly (never patronizing): *"These headshots are clean-rights (you took them) but they read casual-snapshot, and phase 3 positioned this as premium-editorial. A premium site with snapshot photography reads as inconsistent — visitors notice without being able to name why. Three paths: (a) re-shoot with intentional lighting (I can give you a shot list matching the phase-2 vision); (b) hire a photographer (worth it for the founder shots on a premium site — usually 1 shoot covers it); (c) AI-generate brand-consistent imagery at phase 8 (works for environment / texture / abstract; weaker for a real founder portrait — visitors increasingly clock AI faces). For founder portraits specifically I lean (a) or (b); for backgrounds (c) is fine. Which?"* The user decides; the audit records the routing.

**The user has a stock photo from their old site and doesn't know if it was licensed.** The agent flags it `unknown-provenance` and surfaces the reverse-image-search path: *"This hero image on your old site — do you have a license for it? If the prior site was built by someone else, the license (if any) may not have transferred to you. Let's reverse-image-search it: I'll walk you through running it on TinEye (best for finding the original source + first-publication date — useful for proving or disproving a license claim) and Google Lens (best for identifying the stock agency). If it's an unlicensed stock image, it has to be dropped — those exact images are what reverse-search-driven demand letters target."* The agent helps identify; if unlicensed, the asset is `unusable` and routes to phase 8.

**The user insists on using a rights-unclear image.** *"It's fine, no one will notice, just use it."* The agent refuses to proceed silently but respects autonomy: *"I can't clear this — but the decision is yours. What I won't do is let it ship without you knowing the risk. Reverse-image-search-driven copyright claims are common, automated, and expensive (typical demand letters run four figures; 'I didn't know' isn't a defense). If you want to proceed anyway, I'll record in the decision log that I flagged this, explained the risk, and you chose to use it knowingly. That protects you from a 'the agent did it without telling me' situation and gives you a clear record. Confirm and I'll log it."* This produces `decisions/07-rights-acknowledgment.md`.

**The user has high-quality images in the wrong format / resolution.** A 600px-wide JPEG slated for a full-bleed hero. The agent flags `needs-edit` with the specific fix: *"This image is on-brand and rights-clean, but it's 600px wide and the hero needs ≥1920px for the responsive variants phase 20 will generate. Options: (a) you have a higher-res original somewhere — that's the cleanest fix; (b) AI-upscale (works for some images; introduces artifacts on others — I'll show you the result before committing); (c) re-source. Which?"* The audit records the action; the fix happens here or routes forward explicitly.

**The user's logo is a low-res PNG screenshot of a logo, not the source file.** The agent flags it: *"This logo is a 400px PNG that looks like a screenshot — phase 17 (design system) needs a vector or high-res source to extract palette anchors and generate the raster/favicon variants cleanly. Do you have the original (SVG / AI / source PNG ≥2000px)? If the original is genuinely lost, phase 17 has a recovery path (re-vectorize from the best available raster), but it's better to find the source now."* Logo source state is recorded for phase 17.

**The user has video that's huge and unoptimized.** A 4GB ProRes file slated for a background hero loop. The agent flags `needs-edit` and defers the heavy work: *"This is a 4GB master — fine as a source, fatal as a web asset (phase 22 perf budget would reject it instantly). It needs transcoding to a web-optimized loop (typically <3MB for a background loop: H.264/H.265 + WebM, short loop, no audio track). The transcode happens at phase 18-20 when the component using it exists; for now I'm logging it `needs-edit: transcode-at-phase-18` so phase 8 plans around the optimized version, not the master."*

**Extracted imagery from phase 6.5 has the worst provenance.** A deployed site was ingested; its hero is an unlicensed stock photo the user inherited from a previous freelancer. The agent surfaces: *"The hero image from your old site has no provenance you can show — the previous freelancer may or may not have licensed it; you can't prove either way. On the old site this was the previous person's risk; on the new site it becomes yours. Treating it as `unusable` and sourcing a replacement at phase 8 is the clean path. Agree?"* Inherited-liability is named explicitly so the user understands the risk transferred.

**The user wants to skip the audit ("the images are fine, trust me").** The agent refuses to advance with `audit-in-progress` but makes it fast: *"We don't need a slow audit — a fast one. I'll go through them quickly: for each, just tell me 'I made it / I licensed it / I don't know.' Quality and brand-fit I can assess by looking. The whole pass is usually 10 minutes and it prevents the phase-8 surprise where we discover at launch that the hero image is a liability."* Speed addresses the user's resistance without skipping the discipline.

**An asset is rights-clean and high-quality but contradicts the visual register.** A sharp, owned, professional photo — but it's a warm-golden-hour aesthetic and phase 2's vision adjectives are cool-clinical-minimal. The agent flags `brand-fit` (not usability): *"This photo is clean and yours — no rights or quality issue. But it's warm-golden and phase 2's visual register is cool-clinical-minimal. Using it creates a register clash visitors feel without naming. Options: (a) color-grade it toward the cool register (phase 7 edit — I can do this); (b) keep it for a context where warm fits (an about-page human moment can intentionally break the register); (c) replace at phase 8. Which?"* Brand-fit flags are surfaced as choices, not condemnations.

## Reference materials

- **Design doc — phase pipeline source:** `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` § 7 (seed for this contract)
- **Design doc — pipeline integration:** `Workstreams/website-builder/foundation/DESIGN-architecture.md` § Phase contracts
- **Design doc — media/ layout + AUDIT.md location:** `Workstreams/website-builder/foundation/DESIGN-project-scaffold.md` § `media/` (the structured media tree assets move into post-audit) + § `decisions/`
- **Design doc — downstream consumers of the audit:** phase 8 (image strategy — sources around `needs-replacement`/`unusable`), phase 18 (component imagery), phase 20 (responsive variants need ≥1920px sources), phase 22 (perf image budget), phase 26 (SEO alt text) — all in `DESIGN-phase-contracts.md`
- **External — reverse-image-search tooling (loaded fresh 2026-05-18 for this contract):**
  - Tool comparison (Google Lens vs TinEye vs Yandex) — https://toolspivot.com/blog/google-lens-vs-tineye-vs-yandex/ (Google = visual similarity + product/landmark ID; TinEye = exact-match digital fingerprint + first-publication date; Yandex = aggressive facial recognition + Eastern-Europe/Asia coverage)
  - Best reverse-image-search tools 2026 (tested) — https://socialcatfish.com/scamfish/best-reverse-image-search-tools/
  - Multi-engine search (run the same image through several — results vary by region/subject) — https://berify.com/reverse-image-search/
  - **Rights-provenance use:** TinEye is the load-bearing tool for "where did this image first appear" / "is this stock" / proving first-publication for a license dispute (indexed ~77B+ images, finds oldest known occurrence) — https://socialcatfish.com/scamfish/best-reverse-image-search-tools/
  - Practical guidance: always run a provenance-critical image through more than one engine (Google + TinEye minimum); they crawl different web regions and use different matching
- **Agent profile — anti-vision lock:** `${CLAUDE_PLUGIN_ROOT}/agents/website-builder.md` § What you do NOT do ("Mock the user's existing work" — when an asset is poor, the agent names what's wrong without making the user feel small; brand-fit flags are options, not judgments) + § Voice characteristics (encouraging-but-firm; surfaces the rights risk loudly without lecturing)
- **Cross-rule:** `.claude/rules/tool-dependency-discipline.md` (reverse-image-search services are Tier 2 third-party tools; the agent surfaces failures rather than silently skipping a provenance check)
