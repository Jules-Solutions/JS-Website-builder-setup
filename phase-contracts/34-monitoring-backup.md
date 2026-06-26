---
phase: 34
name: Monitoring + backup
group: post-launch
pipeline_section: post-launch
skill: wb-postlaunch
prev_phase: 33
next_phase: ~
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-phase-contracts.md
  - Workstreams/website-builder/foundation/DESIGN-architecture.md
  - Workstreams/website-builder/cross-cutting/DESIGN-post-launch-template.md
  - Workstreams/website-builder/cross-cutting/DESIGN-deploy-providers.md
---

# Phase 34 — Monitoring + backup

> The last phase, and the only post-launch phase with a real gate. Uptime monitoring so the user learns the site is down before their customers do; error tracking so the bugs users hit are visible; a backup strategy so a catastrophe is recoverable. Unlike phases 31-33, **the agent refuses to call the project complete without monitoring** — "I'll know if it goes down" is the failure this phase exists to refute, with real-world evidence that users do not, in fact, know.

## Mission

The site is live, announced, has a roadmap, and a maintenance routine (phases 29-33). Phase 34 is the last phase of the pipeline (`next_phase: ~`) and the one place in the post-launch group where the agent *gates*. It establishes three things the user cannot see the absence of until it is too late: **uptime monitoring** (the user is told the site is down — by a monitor — before a customer tells them, or worse, before nobody tells them and the site is silently dead for days), **error tracking** (the JavaScript errors and failed requests real users hit, which never reach the user otherwise, become visible), and a **backup strategy** (when something catastrophic happens — a bad deploy, a compromised CMS, a deleted database — there is a recovery path that exists *before* it is needed, not improvised during the incident).

The defining behavior, and the reason this phase alone in 31-34 has a refusal gate: **the agent refuses to call the project complete without monitoring.** The seed names the exact failure — the user says "I'll know if it goes down" — and the agent's response is the real-world evidence that they will not: a solo operator does not stare at their own site; an outage at 2am on a Sunday is invisible until Monday's lost conversions; a silent 500 on the checkout page costs money for days before anyone notices. "I'll know" is the single most common and most costly post-launch self-deception, and phase 34 is built specifically to refuse it. The project is not *complete* — the pipeline does not close — until monitoring exists.

Like phase 33, much of phase 34's *content* was pre-decided by the phase-29 deploy wizard (per decision 45/49 — the wizard asked the uptime/error-tracking/backup questions and wrote `config.yaml`). Phase 34 is therefore largely **verification + activation + documentation**: confirm the wizard's choices, *actually activate* the monitors (a configured-but-not-active monitor is the same as no monitor), document the backup strategy per the stack, and map it onto the post-launch maintainer's `monitoring`/`escalate` skills (decision 49) that will watch it ongoing. Phase 34 **references** those maintainer skills; it does **not author them** (Stage 2.B Captain scope).

## Entry conditions

- Phase 33 (maintenance cadence) complete (or skipped with logged decision).
- `.website-builder/post-launch/config.yaml` (phase 29 wizard) — the wizard already captured the uptime provider, error-tracking choice, and backup strategy. Phase 34 verifies + activates these, it does not re-decide them from scratch.
- `.website-builder/project.yaml.stack` + `audit/DEPLOY-REPORT.md` — the backup strategy is stack/host-specific: a Vercel-Next.js site's code is in git (the backup *is* the repo + the host's deploy history); a WordPress site needs an *explicit* DB + uploads backup (git does not cover the WP database); a Payload-CMS site needs DB backups beyond the repo. The agent's backup plan is per the real stack, not generic.
- `.website-builder/keys.yaml` — monitor/error-tracking provider tokens registered as references (per `DESIGN-secrets-and-keys.md`); the secrets stay in `.env`/1Password, used at activation, not persisted in committed state.

## What Claude must establish

Active uptime monitoring, active error tracking (where the stack warrants it), and a documented stack-correct backup strategy — *verified active*, not merely configured. The work product:

1. **Uptime monitoring — active and tested.** A monitor (per the phase-29-wizard choice — UptimeRobot's free tier is the strong default: 50 monitors at 5-min intervals, the most generous free plan in 2026; Better Stack / Cloudflare Health Checks / Pingdom are the wizard alternatives) configured against the live domain *and verified firing*: the agent confirms the monitor is active, polling, and that its alert channel reaches the user (a monitor whose alert goes to an unmonitored inbox is no monitor — the agent verifies the alert path, ideally by triggering a test notification).
2. **Error tracking — active where the stack warrants it.** For sites with non-trivial JavaScript (a Next.js/SvelteKit app, an interactive site), Sentry (the wizard default — free tier, widely used) or the wizard alternative is wired and confirmed receiving (the agent triggers a test error and confirms it lands in the dashboard). For a purely static brochure site with negligible JS, the agent surfaces that error tracking may be low-value and records that as the considered decision rather than installing it reflexively.
3. **Backup strategy — documented and stack-correct.** Per the real stack: code → git (the repo + the host's deploy/rollback history; the agent confirms the rollback path actually works on the chosen host); content Layer-4 markdown → git; CMS content → the CMS-specific path (a Payload Postgres DB needs a real DB backup; a WordPress site needs DB + uploads backup — git does *not* cover these and the agent says so explicitly); media → git/git-LFS or the documented store; database → the host/DB backup mechanism. The strategy is written so a future incident has a recovery path that already exists.
4. **Mapping to the maintainer's monitoring/escalate skills.** The ongoing watching is the post-launch maintainer's `monitoring` skill (weekly review of uptime + errors) and `escalate` skill (when something is bigger than the maintainer can handle); phase 34 documents the contract and confirms the maintainer was materialized with those skills (phase 29) — it does not author them.
5. **`.website-builder/monitoring.md`** — the active monitors (provider, what they watch, alert channel verified), the error-tracking state (active/considered-and-declined-with-reason), the stack-correct backup strategy with the verified recovery path, and the maintainer-skill mapping.

On completion the agent updates `.website-builder/project.yaml.current_phase` — and, because `next_phase: ~`, this is the **pipeline's end**: the project is complete. The agent marks the project complete *only* once monitoring is active (the gate below).

## Skip authorization

Phase 34's skip authorization is **categorically different from phases 31-33's**: 31-33 have no refusal gate; **phase 34 does**. The agent **refuses to call the project complete without monitoring.** This is the seed's explicit instruction and the one hard gate in the post-launch group.

- **The refusal is the point.** "I'll know if it goes down" is the failure phase 34 exists to refute. The agent does not accept it. The real-world evidence the agent surfaces: solo operators do not watch their own sites; outages happen at nights/weekends when nobody is looking; a silent checkout-500 or a down site costs conversions/revenue/trust for the entire invisible window; the people who *do* find out first are customers (the worst possible discovery path) or nobody (worse). The agent presents this not as a scare tactic but as the documented common reality, and **does not let the project close as "complete" without at least uptime monitoring active.**
- **What is genuinely skippable vs not:** *uptime monitoring is not skippable for a launched site* — it is the floor; the agent will not stamp the project complete without it. *Error tracking* is conditionally skippable (a static no-JS site may legitimately not need it — the agent records that as a considered decision, not a silent omission). *The backup strategy* must at minimum be *documented* even when it is trivially "code is in git + the host keeps deploy history" — the documentation is the deliverable, because "I assumed git was a backup" is itself a failure mode for stacks where it is not (WordPress, Payload).
- **The only override is explicit and loud.** If the user genuinely refuses uptime monitoring, the agent does not silently comply — it records `.website-builder/decisions/no-monitoring.md` with the user's explicit acknowledgement that the project is being declared complete *without* the safety net the agent strongly recommended, the specific risks restated, and the agent's recommendation on the record. The pipeline does not quietly close on an un-monitored site; it closes, if at all, on an explicitly-logged informed refusal. Even then the agent surfaces the post-launch maintainer's `monitoring` skill as the cheap path to add it later.

This is the strongest skip-authorization stance in the entire 38-contract pipeline, by design — it is the last gate before the pipeline declares the work done, and a launched site nobody is watching is the failure that most undermines the whole disciplined build.

## Gating rules

The agent refuses to call the project complete when:

- **No active uptime monitoring.** The defining gate of this phase and the pipeline's final gate. Not "a monitor was configured" — a monitor that is *active, polling, and whose alert reaches the user* (verified). A configured-but-paused monitor, or one alerting to an inbox nobody reads, is no monitor. **Not overridable except by the explicit, logged, informed-refusal path** above (and even then the agent records its recommendation against).
- **Monitoring "configured" but not verified active.** The agent set up UptimeRobot but never confirmed it is polling and the alert path works. The agent verifies the monitor is live and the notification reaches the user (test alert) before marking phase 34 — and the project — complete. Configured ≠ active; the gate is active.
- **Backup strategy undocumented, or wrong for the stack.** A WordPress site with "it's fine, the code's in git" (git does not back up the WP database or uploads — a real data-loss exposure); a Payload site with no DB backup plan. The agent refuses to call the project complete with a backup strategy that does not actually cover what would be lost. The strategy must be documented and stack-correct.
- **Recovery path asserted but never verified.** "You can roll back on Vercel" — but the agent never confirmed the rollback actually works for this project. The agent verifies the recovery path it documents (the host's rollback, the DB-restore step) rather than asserting an untested escape hatch.
- **Error tracking silently omitted on a JS-heavy site.** A Next.js app with real interactivity and no error tracking, with no recorded decision. The agent either wires it or records the considered-and-declined rationale — silent omission on a stack that warrants it is the gate (declining on a static site with a logged reason is fine).

Override exists only via the explicit, loud, logged informed-refusal decision doc — and the agent records its contrary recommendation on that document. No silent close on an un-monitored site.

## Tools and skills used

- **`Bash`** — the monitor/error-tracking provider CLIs + REST APIs (UptimeRobot API, Sentry CLI/API, Cloudflare Health Checks via the Cloudflare API) to *create and activate* the monitors and confirm they are polling; the host's rollback/deploy-history command to verify the recovery path.
- **Cloudflare MCP** — when the wizard chose Cloudflare Health Checks (canonical-tool path; integrated with the phase-28 Cloudflare DNS).
- **`WebSearch`** — **mandatory at this phase**: current uptime-monitor SaaS state 2026 (UptimeRobot 50-monitor free tier confirmed the strongest; Better Stack / Pingdom / Cloudflare Health Checks / BetterStack feature+pricing). Cited.
- **`WebFetch`** — **mandatory at this phase**: Sentry current state (`https://sentry.io/welcome/` — free-tier limits, the SDK install per stack). Cited. Tier-2 fall-back to WebSearch if the canonical page is thin.
- **`Playwright` MCP** — to trigger a test error against the live site and confirm it reaches the error-tracking dashboard (the "verify active, not just configured" discipline applied to error tracking).
- **`AskUserQuestion`** — confirm the wizard's monitor/error/backup choices are still right; the alert-channel destination (where the uptime alert must reach the user — the agent verifies this is a channel the user actually watches); and, if the user resists monitoring, the explicit informed-refusal acknowledgement (never a silent accept).
- **`Read` / `Write`** — `post-launch/config.yaml` (the wizard choices to verify+activate), `project.yaml.stack` + `audit/DEPLOY-REPORT.md` (the stack-correct backup shape), `keys.yaml` (provider token references); writes `monitoring.md`.

No subagent spawn, and the recurring watching is the post-launch maintainer's `monitoring`/`escalate` skills (decision 49) — phase 34 documents+verifies the contract, **does not author the skills** (Stage 2.B Captain scope). The `wb-postlaunch` phase-group skill closes the pipeline here.

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| `.website-builder/monitoring.md` | Active uptime monitor (provider, target, interval, alert channel verified-reaching-user), error-tracking state (active w/ test-error-confirmed, or considered-and-declined-with-reason), stack-correct backup strategy with verified recovery path, mapping to the maintainer monitoring/escalate skills | The monitoring+backup record; the spec the post-launch maintainer's monitoring/escalate skills run on; the proof the project is safe to call complete |
| Active monitors at the provider(s) | Provider-native | Live uptime + error monitoring (the user-owned provider accounts) |
| `.website-builder/decisions/no-monitoring.md` *(only via the explicit informed-refusal path)* | Standard decision-doc frontmatter + body; the user's explicit acknowledgement + restated risks + the agent's recorded contrary recommendation | The single, loud, logged exception — never a silent close on an un-monitored site |

The `monitoring.md` with the *verified-active* monitor + the *verified* recovery path is the required artifact and the pipeline's closing deliverable.

## Common failure modes

**"I'll know if it goes down."** The seed's named failure and the reason this phase gates. The user will not know — solo operators do not watch their own sites; outages strike nights/weekends; a silent checkout-500 bleeds revenue for days; the first to find out is a customer or nobody. The agent meets "I'll know" with the documented reality and refuses to close the project without monitoring; this is not negotiable down to a silent skip.

**Monitoring "set up" but not active.** UptimeRobot configured and then left paused, or alerting to an inbox the user never opens. A monitor that is not polling, or whose alert does not reach a watched channel, is the same as no monitor. The agent verifies it is *active and the alert path works* (test notification) — configured is not the bar; active-and-reaching-the-user is.

**Git mistaken for a backup on a stack where it is not.** A WordPress site owner thinks "the code's in git, I'm backed up" — but the WordPress *database* (every post, every setting) and the uploads directory are not in git. A Payload site's Postgres data is not in the repo. The agent's backup strategy is stack-correct and explicitly says what git does *not* cover, with the real backup mechanism for the data git misses.

**A recovery path asserted but never tested.** "You can roll back on Vercel if a deploy breaks" — stated, never verified for this project. The agent confirms the rollback (or the DB restore) actually works rather than documenting an escape hatch that fails when first needed during a real incident.

**Error tracking installed reflexively on a static site, or silently skipped on a JS app.** The agent adds Sentry to a 5-page no-JS brochure where it is near-useless (noise, a dependency, a cookie/consent concern) — or omits it from a real Next.js app with interactivity and no recorded reason. The agent makes error tracking a *considered* decision per the stack: wire it where it earns its place, decline it with a logged reason where it does not.

**The project declared "complete" on an unmonitored site.** The agent reaches phase 34, the user shrugs at monitoring, and the agent stamps it done. This is precisely the close the gate forbids. The pipeline ends in one of two states only: monitoring active, or an explicit loud logged informed-refusal with the agent's recommendation against on the record — never a quiet "complete" over silence.

**Skip cost softened to a suggestion.** The agent says "you should probably set up monitoring" and lets it slide. Phases 31-33 are no-gate and the agent surfaces-and-respects the skip; phase 34 is *different by design* — the agent's stance here is refusal, not suggestion, and softening it collapses the one safety gate that stands between a launched site and silent failure.

## Reference materials

- **Design doc — phase pipeline source:** `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` § 34 (seed — **the gating one**: agent refuses to call the project complete without monitoring; common failure = "I'll know if it goes down", agent surfaces real-world evidence that users do not)
- **Design doc — post-launch maintainer (the monitoring/escalate skills + the wizard that pre-decided uptime/error/backup, decisions 45/49):** `Workstreams/website-builder/cross-cutting/DESIGN-post-launch-template.md` § Maintenance skill bundle (`wb-maintain-monitoring` / `wb-maintain-escalate`) + § Wizard-driven customization (uptime/error/backup wizard sections) — **referenced, not authored here**
- **Design doc — deploy providers (per-host backup story + rollback path):** `Workstreams/website-builder/cross-cutting/DESIGN-deploy-providers.md` § Phase contracts that invoke this concern (phase 34 = "per-provider backup story documented; uptime monitoring configured")
- **Design doc — pipeline integration:** `Workstreams/website-builder/foundation/DESIGN-architecture.md` § Phase contracts
- **Phase 29 (the wizard that pre-decided monitoring/backup + the deploy this watches):** `phase-contracts/29-hosting-deployment.md` § What Claude must establish
- **Phase 33 (the prior post-launch phase; the no-gate contrast this phase breaks):** `phase-contracts/33-maintenance-cadence.md` § Skip authorization
- **Secrets handling (monitor/error-tracking tokens — user-supplied, not persisted):** `Workstreams/website-builder/cross-cutting/DESIGN-secrets-and-keys.md` § Phase contracts (phase 34 = "uptime monitor / error tracking secrets")
- **External research (loaded fresh 2026-05-18 for this contract):**
  - Uptime monitoring SaaS 2026 (WebSearch) — UptimeRobot free tier = 50 monitors @ 5-min (strongest free plan; Solo $7/mo, Team $15/mo); Better Stack free = 10 monitors @ 3-min + incident mgmt/status pages/logs; Pingdom free = 1; StatusCake 10; Cloudflare Health Checks (paid-tier-included). Confirmed 2026-05-18.
  - Sentry (WebFetch sentry.io/welcome + corroborated) — free tier, widely used, per-stack SDK; LogRocket/Raygun alternatives. Confirmed 2026-05-18.
- **Locked decisions 37 + 45 + 49** (phases 31-34 run once; the deploy wizard pre-decides; the 8-skill maintainer's monitoring/escalate own ongoing) — STATE doc: `Workstreams/website-builder/website-builder.md`

Freshness date for this contract: **2026-05-18**. Monitor/error-tracking provider state evolves; the agent re-checks current SaaS state at session start when phase 34 is active and verifies every monitor is *active and alerting to a watched channel* — the pipeline does not close on a configured-but-not-verified monitor.
