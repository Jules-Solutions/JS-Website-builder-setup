---
phase: 33
name: Maintenance cadence
group: post-launch
pipeline_section: post-launch
skill: wb-postlaunch
prev_phase: 32
next_phase: 34
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-phase-contracts.md
  - Workstreams/website-builder/foundation/DESIGN-architecture.md
  - Workstreams/website-builder/cross-cutting/DESIGN-post-launch-template.md
---

# Phase 33 — Maintenance cadence

> A site is not a finished object; it is a thing that rots if left alone. Document the ongoing maintenance routine — content freshness, dependency updates, security patches, broken-link checks — and how often each happens. The phase that prevents the 6-month decay into a stale, vulnerable, broken-link site. No quality gate. The agent surfaces the rot-risk and produces a real `maintenance.md` rather than letting the user assume a deployed site stays good on its own.

## Mission

The site is live, announced, and has a v1.1 roadmap (phases 29-32). Phase 33 addresses the unglamorous truth the seed states bluntly: **no plan = site rots in 6 months.** Dependencies accrue security advisories. Content goes stale (the "2024 roadmap" still on the homepage in 2026). Links rot (a linked partner site moves; a CDN asset 404s). The platform under it shifts (a framework major, a host policy change). A site with no maintenance routine is not "done" — it is "decaying on a delay." Phase 33 produces `maintenance.md`: what to check, how often, and how — so the rot is prevented by routine rather than discovered by an embarrassed user (or a security incident).

This is a post-launch-group phase (run once at launch). Critically, phase 33's *content* is largely **pre-decided by the phase-29 deploy wizard** (per decision 49 / `DESIGN-post-launch-template.md`): the wizard already captured the iteration cadence, the backup strategy, the CMS-notification preference, and which maintainer skills are installed. Phase 33 is therefore mostly **verification + documentation**: confirm the wizard's `config.yaml` cadence is right, write the human-readable `maintenance.md` that explains the routine in the user's terms, and ensure the routine maps onto the post-launch *maintainer*'s `content` / `deps` / `monitoring` skills (decision 49) that will actually execute it. Phase 33 **references** those maintainer skills (they do the recurring work) but **does not author them** (Stage 2.B Captain work, out of scope) — phase 33 documents the *cadence and the checklist*; the maintainer *runs* it.

The discipline is the same anti-vagueness as phase 32: "keep it updated" is not a maintenance plan. The agent produces a concrete routine — *check X every N, here's how, here's the skill that does it* — grounded in this site's actual stack (a WordPress site's maintenance is plugin/core/security-heavy; a static-Astro site's is mostly dep-bumps + content + link-checks; a Payload-CMS site adds migration discipline).

## Entry conditions

- Phase 32 (iteration roadmap) complete (or skipped with logged decision).
- `.website-builder/post-launch/config.yaml` (phase 29 wizard) — the **primary input**: the chosen iteration/notification cadence, the backup strategy per stack, the CMS-notification preference, and `maintainer_skills_installed` (which of the 8 maintainer skills the user has — `content`, `deps`, `monitoring` are the ones phase 33's cadence drives). Phase 33 documents *this*, it does not re-decide it.
- `.website-builder/project.yaml.stack` (phase 11) — the maintenance shape is stack-specific (WordPress = core+plugin+security updates; static = dep-bumps + link-checks; Payload/Next.js = deps + migration discipline; Framer/Webflow = platform-managed, lighter).
- `.website-builder/audit/DEPLOY-REPORT.md` (phase 29) — what is deployed and where, so the maintenance routine targets the real stack + host (e.g., a Vercel-Next.js site's "security patch" routine is `pnpm audit` + dependabot-style review + redeploy; a managed-WP site's is the host's update mechanism).

## What Claude must establish

A documented, concrete, stack-appropriate maintenance routine mapped to the maintainer skills that execute it. The work product:

1. **`maintenance.md`** — the routine, in the user's terms, with four standard sections sized to the stack:
   - **Content freshness** — what content goes stale (dated copy, "current" claims, the year in the footer, the roadmap reference), checked at the chosen cadence; executed by the maintainer's `content` skill.
   - **Dependency updates** — `pnpm/npm outdated` / `pip outdated` / WP plugin+core updates, categorized security (apply ASAP on advisory) / minor (apply with a regression check) / major (read release notes, escalate if it touches the design system or core flows); executed by the maintainer's `deps` skill.
   - **Security patches** — the security-advisory path: how the user (or the maintainer's `deps` skill) learns of an advisory and applies it fast; for WordPress, the heavier core+plugin+theme security discipline.
   - **Broken-link checks** — internal + outbound link verification at the chosen cadence (a rotted partner link or 404'd asset quietly erodes trust); executed by the maintainer's `monitoring`/`content` skills.
2. **Cadence per item**, taken from (and verified against) the phase-29-wizard `config.yaml` — not invented. If the wizard says "monthly", the maintenance routine is monthly-shaped; the agent confirms the wizard's cadence is still right and documents it, rather than imposing a different one.
3. **Mapping to the maintainer skills.** Each routine item names the post-launch maintainer skill that performs it (`content` / `deps` / `monitoring`) so `maintenance.md` is not a document the user has to execute by hand — it is the human-readable spec for what the already-materialized maintainer does on schedule. (Phase 33 documents the contract; it does not write the skills.)

The agent updates `.website-builder/project.yaml.current_phase` to `34` upon completion. Phase 34 (monitoring + backup) is the last phase — and, unlike 31-33, it *does* have a refusal gate.

## Skip authorization

Phase 33 has no refusal gate, but its skip cost is the bluntest in the post-launch group and the agent surfaces it without softening:

- **Skipping the maintenance plan is choosing for the site to rot.** The seed states it: no plan = site rots in 6 months. Not "might rot" — *will*. Dependencies will accrue vulnerabilities; content will go stale; links will break. The decay is not a risk the user is accepting; it is the default outcome the maintenance plan exists to prevent. The agent surfaces this as the certain consequence it is, not a probabilistic caution.
- **The cost compounds with 32 and is distinct from 34.** Phase 32 = "keep improving" (skip → static). Phase 33 = "keep from rotting" (skip → decay/vulnerability). Phase 34 = "know when it breaks" (and 34 *does* gate). Skipping 33 specifically means a site that may be monitored (34) but is never patched — the monitor will eventually alert on a problem the skipped maintenance would have prevented.
- **Mitigant the agent surfaces:** if the phase-29 wizard already installed the `deps`/`content`/`monitoring` maintainer skills, much of the routine is *already wired to run* — skipping phase 33's documentation does not un-install the maintainer; it just leaves the user without the human-readable spec of what it does and when. The agent surfaces that the rot-protection is partly automatic *if* the maintainer was materialized, while still recommending the documented routine so the user understands and can adjust it.

If the user skips, the agent logs `.website-builder/decisions/skip-phase-33.md` with the surfaced (certain, not probabilistic) cost and advances to phase 34. It does not refuse — but it does not let "a deployed site stays good on its own" pass as an unexamined assumption.

## Gating rules

Phase 33 has **no refusal gate** (per the seed — `Gating: none`). The standards that still apply:

- **The plan is concrete and stack-appropriate, not "keep it updated."** A static-Astro site does not get a WordPress-plugin-security routine; a WordPress site does not get a "just bump npm deps" plan that ignores its core/plugin/theme security surface. The agent writes the routine for *this* stack. Not a pipeline gate, but the agent does not hand the user a generic maintenance platitude.
- **The cadence is the wizard's, verified — not re-invented.** Phase 33 documents the phase-29-wizard `config.yaml` cadence (confirming it is still right with the user), it does not impose a fresh schedule the user did not choose.
- **Each item maps to the maintainer skill that executes it.** `maintenance.md` is the spec for what the materialized maintainer does, not a manual chore list the user is expected to perform unaided. The agent makes the maintainer-skill mapping explicit.

## Tools and skills used

- **`Edit` / `Write`** — to author `maintenance.md` (the four-section routine, the cadence, the maintainer-skill mapping) in the user's project.
- **`Read`** — `post-launch/config.yaml` (the wizard-chosen cadence + installed maintainer skills — the primary input, documented not re-decided), `project.yaml.stack` (the maintenance shape), `audit/DEPLOY-REPORT.md` (the real stack+host the routine targets).
- **`AskUserQuestion`** — to confirm the wizard cadence is still right ("the deploy wizard set monthly dependency checks — does that still fit how often you'll engage with this site?") and to surface the rot-cost if the user signals they intend to "just leave it." The agent does not re-run the wizard; it verifies + documents.

No subagent spawn, no mandatory external research (per the INST — phase 33 is first-principles authoring; the maintenance routine is derived from the wizard config + the stack, not fetched docs). The `wb-postlaunch` phase-group skill carries phases 31-34. The recurring maintenance work is **performed by the post-launch maintainer's `content`/`deps`/`monitoring` skills** (decision 49) — phase 33 documents the cadence/checklist contract those skills fulfil; it does **not author the skills** (Stage 2.B Captain scope).

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| `.website-builder/maintenance.md` | Four-section routine (content freshness / dep updates / security patches / broken-link checks), per-item cadence (from the phase-29-wizard config, verified), each item mapped to the maintainer skill that executes it | The human-readable maintenance spec; the contract the post-launch maintainer's content/deps/monitoring skills run on schedule |
| `.website-builder/decisions/skip-phase-33.md` *(when applicable)* | Standard decision-doc frontmatter + body | Created only when the user deliberately skipped the maintenance plan with the (certain) rot-cost surfaced |

The `maintenance.md` (or the logged skip with surfaced rot-cost) is the artifact.

## Common failure modes

**"It's deployed, it stays good on its own."** The unexamined assumption phase 33 exists to break. Software does not stay good untouched — deps rot, content stales, links break, security advisories land. The agent surfaces that decay is the *default*, not a risk, and produces the routine that prevents it.

**"Keep it updated" passed off as a maintenance plan.** A one-line "remember to update things sometimes" is not a routine. The agent produces the concrete four-section spec — what, how often, executed by which maintainer skill — grounded in the actual stack.

**Wrong-stack maintenance routine.** A WordPress site handed a "bump your npm deps monthly" plan that ignores its core/plugin/theme security surface (where WP sites actually get compromised); or a static-Astro site burdened with a WordPress-grade security routine it does not need. The agent writes the routine for *this* stack's real maintenance surface.

**The agent re-invents the cadence the wizard already set.** Phase 29's wizard captured the user's chosen cadence; phase 33 imposing a different one creates a `maintenance.md` that contradicts `config.yaml` and the materialized maintainer's configured behavior. Phase 33 documents-and-verifies the wizard cadence; it does not override it.

**`maintenance.md` written as a manual chore list.** A document that says "you should run `npm outdated` monthly" with no connection to the materialized maintainer that *can run it for you*. The agent maps each item to the maintainer skill (`deps`/`content`/`monitoring`) so the spec describes an executable routine, not a guilt-list of chores the user will not do.

**Skip cost softened.** The agent says "you might want to maintain it" instead of "without this, it will rot in 6 months." The seed is blunt and the agent is too — the decay is certain, not optional; softening it makes the skip an uninformed choice.

## Reference materials

- **Design doc — phase pipeline source:** `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` § 33 (seed — `Gating: none`; common failure = no plan = site rots in 6 months, agent surfaces this risk)
- **Design doc — post-launch maintainer (the content/deps/monitoring skills that execute this routine + the wizard that pre-decided the cadence, decisions 45/49):** `Workstreams/website-builder/cross-cutting/DESIGN-post-launch-template.md` § Maintenance skill bundle (`wb-maintain-content` / `wb-maintain-deps` / `wb-maintain-monitoring`) + § Wizard-driven customization (the phase-29 cadence/backup inputs phase 33 documents) — **referenced, not authored here**
- **Design doc — pipeline integration:** `Workstreams/website-builder/foundation/DESIGN-architecture.md` § Phase contracts
- **Phase 29 (the wizard that pre-decided the cadence + the deploy this maintains):** `phase-contracts/29-hosting-deployment.md` § What Claude must establish (the post-launch wizard + `config.yaml`)
- **Phase 32 (the prior post-launch phase; the compounding skip-cost):** `phase-contracts/32-iteration-roadmap.md` § Skip authorization
- **Phase 34 (the next + last phase — monitoring/backup, which *does* gate):** `phase-contracts/34-monitoring-backup.md`
- **Locked decisions 45 + 49** (the deploy wizard pre-decides the cadence; the 8-skill maintainer owns ongoing) — STATE doc: `Workstreams/website-builder/website-builder.md`

No mandatory external research for this phase (per the INST). Freshness date for this contract: **2026-05-18**.
