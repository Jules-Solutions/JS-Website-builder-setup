---
name: wb-postlaunch
description: This skill should be used when the website-builder agent reaches the post-launch group — phases 31-34 — after a site is deployed and live. Trigger when the user says "the site is live, what now", "announce the launch", "tell people about the site", "plan v1.1", "what's next after launch", "set up a maintenance routine", "keep the site from rotting", "monitor uptime", "set up error tracking", "make sure I know if the site goes down", "back up the site", or when `.website-builder/project.yaml.current_phase` is 31, 32, 33, or 34. Drives the ONE-TIME launch sequence (announce → roadmap → maintenance cadence → monitoring+backup) and hands off to the separate post-launch maintainer template for all ongoing maintenance.
version: 0.1.0
---

# wb-postlaunch — Post-Launch Launch Sequence (phases 31-34)

> The site is live. This skill runs the four post-launch phases **once, at launch**: announce it, plan v1.1, document the maintenance routine, and stand up monitoring + backup. Then it hands the long-term work to the separate post-launch *maintainer* template.
>
> Design context this skill implements: `DESIGN-post-launch-template.md` (decisions 28/37/45/49 — the launch-once vs ongoing split), `DESIGN-architecture.md` § Skills (lines 193-201), `DESIGN-phase-contracts.md` §§ 31-34. Phase contracts: `phase-contracts/31-launch-announcement.md`, `32-iteration-roadmap.md`, `33-maintenance-cadence.md`, `34-monitoring-backup.md`.

## The one critical distinction (read this first — decision 37 + 49)

There are **two separate systems** in the post-launch space. Confusing them is the primary failure mode this skill must avoid:

| System | What it is | Owned by | Lifetime |
|---|---|---|---|
| **Phases 31-34** (this skill) | The one-time launch sequence: announce, set the v1.1 roadmap, document the maintenance cadence, stand up monitoring+backup | `wb-postlaunch` (this skill) | Runs **once**, at launch, then the pipeline ends |
| **Post-launch maintainer template** | The ongoing maintenance agent — `website-maintainer.md` profile + 8 maintainer skills (`wb-maintain-content` / `-monitoring` / `-deps` / `-content-add` / `-section-add` / `-page-add` / `-iterate` / `-escalate`) | The maintainer template, materialized at **phase 29** by the deploy wizard (decision 45) | Lives with the project **forever**, runs the recurring work |

**This skill does NOT author, install, or re-implement the maintainer template or its 8 skills.** They are materialized at phase 29 (deploy) by the wizard, before this skill ever runs. Phases 33 and 34 *verify the wizard's config* and *document the contract* the maintainer skills fulfil — they reference the maintainer by name and path, they do not build it.

The mental model: **the wizard at phase 29 configured the maintainer; phases 31-34 go-live the launch and verify that config; the maintainer template then takes over ongoing.** The user's experience is: "I built it, launched it, told people, set a forward plan — and now my long-term maintainer is set up and watching."

## Phase map

Each phase is its own contract. Read the contract verbatim when entering the phase — the contract is the authoritative behavior spec; this skill is the cross-phase glue that carries the launch-once-vs-ongoing discipline across all four.

| Phase | Name | Gate? | Contract | Artifact |
|---|---|---|---|---|
| 31 | Launch announcement | No gate | `phase-contracts/31-launch-announcement.md` | `.website-builder/launch/ASSETS.md` |
| 32 | Iteration roadmap | No gate | `phase-contracts/32-iteration-roadmap.md` | `.website-builder/roadmap.md` |
| 33 | Maintenance cadence | No gate | `phase-contracts/33-maintenance-cadence.md` | `.website-builder/maintenance.md` |
| 34 | Monitoring + backup | **HARD GATE** | `phase-contracts/34-monitoring-backup.md` | `.website-builder/monitoring.md` + active monitors |

Phases 31-33 have **no refusal gate** — a user can legitimately skip them, but the skill surfaces the skip cost and logs the decision so it is informed, never a silent evaporation. Phase 34 is **different by design**: the agent refuses to call the project complete without active uptime monitoring. This is the single hard gate in the post-launch group and the pipeline's last gate.

## Cross-phase disciplines (apply to every phase 31-34)

1. **Substance is the user's; shaping is the agent's.** The launch story (phase 31), the v1.1 priorities (phase 32) — the *what and why* is the user's, the agent shapes it to the phase-5 brand voice. The agent never invents the launch hook or imposes its own roadmap. This is the same discipline phase 16 enforced for site copy.
2. **Voice consistency.** Announcement copy is in the phase-5 brand voice (`.website-builder/brand.yaml.voice`), never generic "We're thrilled to announce…" launch-hype. The same say/never-say discipline.
3. **Audience-tied, not generic.** Channels (phase 31) follow the phase-3 audience; roadmap items (phase 32) are grounded in this site's conversion outcome + deferred decisions + analytics signal; the maintenance routine (phase 33) is stack-specific. No generic checklists.
4. **Anti-vagueness.** "Improve SEO", "keep it updated", "post everywhere" are not deliverables. Every artifact is concrete enough that a future session — or a maintainer skill — can act on it cold.
5. **Wizard config is documented, not re-decided.** Phases 33 + 34 read `.website-builder/post-launch/config.yaml` (written by the phase-29 wizard) and *verify + document* it. They do not re-run the wizard or impose a different cadence/provider than the user already chose.
6. **Reference the maintainer, never re-build it.** Every phase points the user at the relevant maintainer skill for the ongoing version of its work — and stops there.

## How to execute each phase

### Phase 31 — Launch announcement

For full behavior read `phase-contracts/31-launch-announcement.md`. This skill's role:

- Read `brand.yaml.voice` (the voice), `project.yaml.requirements` (the audience + their real channels), `post-launch/config.yaml` (the maintainer's future announcement capability — referenced, not duplicated).
- Use `AskUserQuestion` for the substance the agent must not invent: the actual story of *why this site matters*, the channels the user actually has (LinkedIn presence? email list? internal stakeholders?), and the committed launch date/time.
- Produce `.website-builder/launch/ASSETS.md`: per-channel copy in the brand voice (short social post, LinkedIn post, IG caption + visual note, email/newsletter, internal-stakeholders note), the ranked audience-tied channel plan, and a concrete staggered schedule.
- Surface the skip cost (launching into silence; launch-moment attention is a one-time asset that decays) if the user wants to skip; log `.website-builder/decisions/skip-phase-31.md` if they do. No gate — informed choice.
- For announcement copy patterns and the channel-sequencing template, load `references/launch-announcement.md`.

### Phase 32 — Iteration roadmap

For full behavior read `phase-contracts/32-iteration-roadmap.md`. This skill's role:

- Read the highest-quality inputs: `decisions/*deferred*.md` (consciously-deferred build decisions), `project.yaml.requirements` (the conversion outcome), `post-launch/config.yaml` (the chosen iteration cadence — timing aligns to this), `audit/POST-DEPLOY-REPORT.md` (analytics signal), `sitemap.yaml` (archive types with one entry = concrete candidates).
- Use `AskUserQuestion` for the user's own sense of what is next (the substance); the agent surfaces strong candidates but does not impose its own priorities.
- Produce `.website-builder/roadmap.md`: 3-5 *specific* v1.1 items (named page / named integration / named experiment), each with what / why-it-matters (tied to conversion or a deferred decision) / rough-when (aligned to the chosen cadence), ordered by leverage.
- The roadmap is a standing input for the maintainer's `wb-maintain-iterate` / `-section-add` / `-page-add` skills — say so in the artifact (referenced, not authored here).
- Surface the skip cost (v1 treated as the finish line → slow irrelevance; compounds with phase 33) and log `decisions/skip-phase-32.md` if skipped. No gate.

### Phase 33 — Maintenance cadence

For full behavior read `phase-contracts/33-maintenance-cadence.md`. This skill's role:

- The primary input is `post-launch/config.yaml` (the phase-29-wizard cadence + `maintainer_skills_installed`). Phase 33 **documents + verifies this**, it does not re-decide it. Also read `project.yaml.stack` and `audit/DEPLOY-REPORT.md` (the maintenance shape is stack-specific).
- Use `AskUserQuestion` only to confirm the wizard cadence is still right and to surface the rot-cost if the user signals "I'll just leave it."
- Produce `.website-builder/maintenance.md`: a four-section routine — **content freshness / dependency updates / security patches / broken-link checks** — sized to the actual stack (WordPress = core+plugin+theme security heavy; static = dep-bumps + link-checks; Payload/Next.js = deps + migration discipline; Framer/Webflow = platform-managed, lighter). Each item carries its cadence (from the verified wizard config) and **maps to the maintainer skill that executes it** (`content` / `deps` / `monitoring`).
- The skip cost here is the bluntest in the group and stated without softening: **no plan = the site rots in 6 months** (certain, not probabilistic). Log `decisions/skip-phase-33.md` with the certain cost surfaced if skipped. Still no gate — but the bluntness is the discipline.
- For the per-stack maintenance-routine matrix, load `references/maintenance-and-monitoring.md`.

### Phase 34 — Monitoring + backup (THE GATE)

For full behavior read `phase-contracts/34-monitoring-backup.md`. This is the last phase (`next_phase: ~`) and the only post-launch phase that gates. This skill's role:

- Verify + **activate** (not just configure) the phase-29-wizard choices in `post-launch/config.yaml`. A configured-but-paused monitor is the same as no monitor.
- **Uptime monitoring — active and tested.** Per the wizard choice (UptimeRobot's free tier is the strong default — 50 monitors @ 5-min, the most generous free plan in 2026; Better Stack / Cloudflare Health Checks / Pingdom are wizard alternatives). Use `Bash` (UptimeRobot API / provider CLI) or the **Cloudflare MCP** (when the wizard chose Cloudflare Health Checks — canonical-tool path, integrated with phase-28 DNS) to create the monitor, confirm it is polling, and **verify the alert path reaches a channel the user actually watches** (trigger a test notification). `AskUserQuestion` confirms the alert-channel destination.
- **Error tracking — considered, not reflexive.** For sites with non-trivial JS (Next.js/SvelteKit/interactive), wire Sentry (the wizard default) or the alternative and confirm receipt via a **`Playwright` MCP**-triggered test error landing in the dashboard. Configure it GDPR-correctly (`send_default_pii: false`, server-side data scrubbing for email/token/credit-card fields, `before_send` PII filter — see `references/maintenance-and-monitoring.md`). For a static no-JS brochure site, record error tracking as a *considered decline with reason* — never a silent omission.
- **Backup strategy — documented and stack-correct.** Per the real stack: code → git + the host's deploy/rollback history (confirm the rollback actually works); Layer-4 content → git; CMS content → the CMS-specific path. State explicitly what git does **not** cover (a WordPress *database* + uploads, a Payload Postgres DB are not in the repo — "I assumed git was a backup" is itself a failure mode). Verify the recovery path, do not assert an untested escape hatch.
- Produce `.website-builder/monitoring.md`: active monitor (provider / target / interval / alert channel verified-reaching-user), error-tracking state (active w/ test-error confirmed, or considered-and-declined-with-reason), stack-correct backup strategy with verified recovery path, mapped to the maintainer's `wb-maintain-monitoring` / `-escalate` skills.
- **The gate (not overridable except by the explicit logged informed-refusal path):** do not mark the project complete without active, verified uptime monitoring. Meet "I'll know if it goes down" with the documented reality (solo operators do not watch their own sites; outages strike nights/weekends; a silent checkout-500 bleeds revenue for days; the first to find out is a customer or nobody) and refuse the silent skip. The only exception is a loud, logged `.website-builder/decisions/no-monitoring.md` with the user's explicit acknowledgement, the restated risks, and the agent's recorded contrary recommendation. Never a quiet "complete" over silence.

On completion the agent updates `.website-builder/project.yaml.current_phase` — and because `next_phase: ~`, **this is the pipeline's end. The project is complete** (only once the gate is satisfied).

## Hand-off to the post-launch maintainer

When phase 34 closes, the launch sequence is done. State to the user, in their site's voice, that the long-term maintainer (materialized at phase 29 at `.website-builder/post-launch/`) now takes over: small content edits → `wb-maintain-content`; weekly monitoring review → `wb-maintain-monitoring`; dep updates → `wb-maintain-deps`; new essay/section/page → `-content-add` / `-section-add` / `-page-add`; medium iteration → `-iterate`; anything bigger than maintenance → `-escalate` back to the full website-builder pipeline. The maintainer is invoked via `/wb-maintain` or `wb maintain`. This skill **does not invoke or author the maintainer** — it points at it and ends.

## Composable the user may invoke (recommend, do not vendor)

At **phase 32**, when the user wants the v1.1 roadmap kept as a living changelog/release-notes document over time, recommend they also invoke the **`documentation-generation:changelog-automation`** skill via the Skill tool — for automating changelog/release-notes generation from commits and PRs following Keep a Changelog format as the roadmap items ship under the maintainer. Do **not** vendor or embed it; point the user at it. It composes with `wb-maintain-iterate`'s shipping cadence.

## Additional resources

### Reference files

- **`references/launch-announcement.md`** — per-channel announcement copy patterns (social / LinkedIn / IG / email / internal), the launch-day sequencing template, 2026 launch best-practice (5-email countdown, 2-3-week social ramp, LinkedIn personal-hook pattern), and the skip-cost framing language for phase 31.
- **`references/maintenance-and-monitoring.md`** — the per-stack maintenance-routine matrix (phase 33), the 2026 uptime-provider comparison (UptimeRobot / Better Stack / Pingdom / Cloudflare Health Checks free tiers), the GDPR-compliant Sentry config recipe (phase 34), the stack-correct backup matrix, and the phase-34 gate verification checklist.

## Cross-references

- Design — post-launch maintainer template + the launch-once-vs-ongoing split (decisions 28/37/45/49): `DESIGN-post-launch-template.md`
- Design — Skills anatomy + how phase-group skills layer on the agent profile: `DESIGN-architecture.md` § Skills (lines 193-201)
- Design — pipeline *design ancestry* (seeded the contracts; NOT runtime authority): `DESIGN-phase-contracts.md` §§ 31-34
- Phase contracts (**authoritative** per-phase runtime behavior — read these, not the design ancestry above): `phase-contracts/31-launch-announcement.md`, `32-iteration-roadmap.md`, `33-maintenance-cadence.md`, `34-monitoring-backup.md`
- Phase 29 (the deploy wizard that pre-decides cadence/monitoring/backup — read before phases 33/34): `phase-contracts/29-hosting-deployment.md`
- Secrets handling (monitor/error-tracking tokens — user-supplied, referenced not persisted): `DESIGN-secrets-and-keys.md`
- Locked decisions 28 / 37 / 45 / 49 — STATE doc: `website-builder.md`
