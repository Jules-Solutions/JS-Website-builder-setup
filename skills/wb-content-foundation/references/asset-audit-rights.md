# Phase 7 — Media asset audit + rights playbook reference

> Loaded when running phase 7. Usability + rights verdict definitions, the reverse-image-search provenance playbook, the inherited-liability framing, the rights-acknowledgment decision-doc schema. Source of truth: `${CLAUDE_PLUGIN_ROOT}/phase-contracts/07-media-asset-audit.md` + `DESIGN-project-scaffold.md` § media/.

## The two verdicts per asset

Every visual asset (every visual row in `inbox/INVENTORY.md` + `entity.existing_assets.logo` + phase-6.5-extracted imagery) gets both.

**Usability verdict:**
- `ready-to-use` — quality sufficient, rights clean, on-brand.
- `needs-edit` — fixable (crop / color-correct / format-convert / background-remove / upscale); the fix is named.
- `needs-replacement` — quality/brand-fit insufficient, unsalvageable by editing; routes to phase-8 sourcing.
- `unusable` — rights-blocked or quality-fatal; must not ship; routes to phase-8 sourcing.

**Rights verdict:**
- `owned` — user created it / holds full rights (user attests).
- `licensed-with-proof` — license held; proof location recorded.
- `cleared-by-creator` — photographer/designer/contributor cleared use; clearance recorded.
- `unknown-provenance` — user can't show origin → treated as `unusable` until provenance established.
- `known-infringing` — confirmed third-party-owned without license → `unusable`, surfaced loudly.

Plus a quality assessment (resolution px / format / size / responsive-variant readiness — hero needs source ≥1920px / color profile / compression artifacts) and a brand-fit assessment (does the aesthetic match phase-2 vision adjectives + phase-5 voice + provisional phase-17 direction) and a recommended action.

## Tools

- `Read` — read images directly (multimodal: resolution, composition, exposure, aesthetic register, whether it reads as the phase-2 vision adjectives).
- `Bash` — hard quality data: `file` (format), `identify`/`exiftool` (dimensions, color profile, EXIF — EXIF can reveal a stock-agency watermark or a camera mismatching claimed authorship), `du` (size).
- `WebFetch` / `WebSearch` — reverse-image-search-driven provenance + licensing-term lookups. **Never auto-upload the user's images anywhere** — search is user-driven or operates on results the user pastes back. The user's unpublished photography must not be indexed without their explicit choice.
- `AskUserQuestion` — every rights attestation, every quality/brand-fit judgment call, every `needs-replacement`/`unusable` routing decision.
- `Write`/`Edit` — author `media/AUDIT.md`; perform agent-doable `needs-edit` fixes inline when the user wants.

## Reverse-image-search provenance playbook

Loaded fresh 2026-05-18 (also cited in the phase-7 contract):

- **TinEye** — the load-bearing tool for "where did this first appear" / "is this stock" / proving first-publication for a license dispute. Exact-match digital-fingerprint; indexes ~77B+ images; finds the oldest known occurrence.
- **Google Lens** — visual similarity + product/landmark/stock-agency identification.
- **Yandex** — aggressive facial recognition + strong Eastern-Europe/Asia coverage.
- **Practical rule:** always run a provenance-critical image through more than one engine (Google + TinEye minimum) — different web regions, different matching.

The agent guides the user through running the search (which tool, what to look for) or works on results the user pastes back. Tools comparison + best-2026 list URLs are in the phase-7 contract's Reference materials section.

## The non-negotiable discipline

Surface copyright risk **loudly**. This is risk-surfacing, not legal advice. Reverse-image-search-driven copyright demand letters are a documented, automated, expensive cottage industry; "I didn't know" is not a defense.

Refuse to advance to phase 8 under three conditions:

1. **Unresolved rights on any asset slated for use.** `unknown-provenance` / `known-infringing` + user wants to use it → refuse silent infringement. Three options: (a) establish provenance (help reverse-image-search); (b) drop + source at phase 8; (c) the user explicitly accepts the risk *in writing in the decision log*. Strongly recommend (a) or (b). Option (c) requires the mandatory `decisions/07-rights-acknowledgment.md`.
2. **Audit incomplete** (`status: audit-in-progress` with un-verdicted visual assets). Refuse — but make it fast: *"For each, just tell me 'I made it / I licensed it / I don't know.' Quality + brand-fit I assess by looking. ~10 minutes; prevents the phase-8 surprise."*
3. **`needs-replacement`/`unusable` assets without a phase-8 routing acknowledgment.** Lightweight ("yes, source a replacement at phase 8") but explicit so phase 8 inherits a clean picture.

Override path: the user can accept rights risk (logged, informed), advance with brand-fit-flagged-but-rights-clean assets (cost flagged to phase 27), or defer some quality edits to a phase-20 note.

## The rights-acknowledgment decision doc (mandatory when overridden)

`.website-builder/decisions/07-rights-acknowledgment.md` — required *if and only if* the user overrides a rights flag (gating rule 1 option c). The one place in this phase a decision doc is mandatory, not optional, because it is the user's informed-consent record. Standard decision-doc frontmatter + the agent's surfaced risk verbatim + the user's explicit informed acceptance. The framing to the user: *"That protects you from a 'the agent did it without telling me' situation and gives you a clear record. Confirm and I'll log it."*

## Failure-mode handling (anti-vision lock: never mock the user's work)

| Situation | Handling |
|---|---|
| **Selfie-quality photos, premium-positioned site** | Flag the brand-fit gap directly, never patronizing. Founder portraits: lean re-shoot or hire-photographer; backgrounds: AI-generate at phase 8 fine. The user decides; the audit records routing. |
| **Stock photo from old site, license unknown** | `unknown-provenance`. Reverse-image-search (TinEye for source + first-publication; Google Lens for agency). Unlicensed → `unusable` → phase 8. |
| **User insists on rights-unclear image** | Refuse silent shipping, respect autonomy. Surface the risk; offer the logged-acknowledgment path → `decisions/07-rights-acknowledgment.md`. |
| **Wrong format/resolution** | `needs-edit` with the specific fix (higher-res original / AI-upscale-with-preview / re-source). |
| **Logo is a low-res PNG screenshot** | Flag: phase 17 needs vector/high-res source. Ask for the original; note phase-17 recovery path if lost. |
| **Huge unoptimized video** (4GB ProRes) | `needs-edit: transcode-at-phase-18` — fine as source, fatal as web asset; phase 8 plans around the optimized version. |
| **Phase-6.5-extracted imagery, worst provenance** | Name the inherited-liability explicitly: *"On the old site this was the previous freelancer's risk; on the new site it becomes yours."* Treat as `unusable`, source at phase 8. |
| **Rights-clean + high-quality but off-register** | `brand-fit` flag (not usability). Options: color-grade toward the register / keep for a context where it fits / replace at phase 8. Flags are choices, not condemnations. |

## Output

`.website-builder/media/AUDIT.md` (required) — per the phase-7 contract schema (frontmatter counts + per-asset table + rights-unresolved + quality-flags + brand-fit-flags sections). Audited assets move from `inbox/` into `.website-builder/media/images/` with clean names. `decisions/07-rights-acknowledgment.md` (conditional — required iff a rights override happens). Advance to phase 8 only when audit complete + all `needs-replacement`/`unusable` have a routing decision.
