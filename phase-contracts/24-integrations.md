---
phase: 24
name: Integrations
group: pre-launch
pipeline_section: pre-launch
skill: wb-prelaunch
prev_phase: 23
next_phase: 25
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - DESIGN-phase-contracts.md
  - DESIGN-architecture.md
  - DESIGN-secrets-and-keys.md
  - DESIGN-deploy-providers.md
---

# Phase 24 — Integrations *(non-commerce)*

> Wire the non-commerce integrations the site actually needs — CRM, mailing list, analytics, chat, search, scheduling-without-payment, whatever phase 3's requirements named. The phase where the site stops being a closed artifact and starts talking to the services that make it operationally real. Then the pivot: phase 24 is the fork in the pipeline. If the site is transactional, the commerce branch (24a → 24b → 24c) activates next; if not, the pipeline jumps straight to phase 25 (legal pages). The agent refuses to advance with an integration configured on staging but absent on the production target, and it refuses to silently skip an integration phase 3 said the site needs.

## Mission

By phase 24 the site is built, responsive, accessible, performant, and its forms work end-to-end (phases 19-23). What it doesn't yet have is its connective tissue: the analytics that tell the user whether anyone is reading, the mailing-list integration that turns a visitor into a subscriber, the CRM that catches a lead before it goes cold, the chat widget that answers a question at 11pm, the site-search that makes a content-heavy site usable. Phase 3 (requirements) named the conversion outcome and, implicitly or explicitly, the integrations that serve it. Phase 24 is where every one of those non-commerce integrations gets configured, keyed, wired, and tested against the real production target — not a staging stand-in.

The discipline of this phase is **parity**. The single most common integration failure is not "the integration doesn't work" — it is "the integration works on the preview deploy and silently doesn't on production" because an environment variable was set in one place and not the other, or because the analytics snippet points at a dev property. The agent treats an integration as configured only when it has fired a real event against the production-bound configuration and seen the event arrive. An integration that "should work" has not been integrated; it has been described.

This phase is also the **pipeline fork**. Phase 11 locked `project.yaml.transactional` to `true` or `false`. Phase 24's exit is conditional on that flag:

- **`transactional: true`** → `next_phase` is `24a` (commerce platform setup). The commerce branch 24a → 24b → 24c runs, then rejoins at phase 25.
- **`transactional: false`** → `next_phase` is `25` (legal pages). The commerce branch is skipped entirely.

The agent surfaces this branch explicitly at phase 24 close so the user understands why the next phase is what it is, and so a user who realizes mid-phase-24 that they actually do need to sell something gets routed through the decision-34 transactional-flag-change path (which forces a restart of phases 12, 22, and 24a-c) rather than silently bolting commerce onto a non-commerce build.

## Entry conditions

- Phase 23 (forms + interactive logic) complete. Every form on the site has a verified endpoint; `.website-builder/audit/FORMS-REPORT.md` exists and is green. Integrations frequently piggyback on forms (a newsletter signup form *is* a mailing-list integration's front end), so forms must work before their integrations are wired.
- `.website-builder/project.yaml.requirements` (phase 3) lists the conversion outcome and the integrations that serve it. This is the contract phase 24 fulfills — the agent re-reads it to enumerate what must be wired.
- `.website-builder/project.yaml.transactional` (phase 11) is set. The agent reads it at phase entry to know which branch phase 24's exit takes.
- `.website-builder/keys.yaml` (per `DESIGN-secrets-and-keys.md`) exists from bootstrap. Each integration's API key is registered here as a reference (source `env` or `onepassword`); the actual secret lives in `.env` or 1Password, never in committed state.
- The site has a known production deploy target (chosen at phase 11, actualized at phase 29 — but the *target* is known here so parity can be checked against it). If the deploy target is genuinely undecided, the agent surfaces that integration parity cannot be verified until phase 28-29 and either defers the parity check with an explicit logged note or routes the deploy decision forward.

## What Claude must establish

Every non-commerce integration named in phase 3 (and any the site's actual shape demands that phase 3 missed) is configured, keyed, wired into the site's stack, and tested against the production-bound configuration. The work product is twofold:

1. **Live, tested integrations** in the user's project. Each integration's client code (snippet, SDK call, embed, webhook handler) is written in the user's chosen stack per that stack's convention, references its key via `process.env.{KEY}` (resolved through the `keys.yaml` mechanism, never hardcoded), and has been exercised with a real event that the agent confirmed arrived at the provider.

2. **`.website-builder/audit/INTEGRATIONS-REPORT.md`** — one section per integration recording: provider, purpose (which phase-3 requirement it serves), where the key lives (env-var name + source), where the client code lives (file:line), the parity check performed (what event was fired, against which configuration, what confirmed receipt), and any caveat (e.g., "GA4 may not fire on Safari due to ITP — verified on Chrome + mobile Safari separately").

Common non-commerce integration classes and what "configured + tested" means for each:

- **Analytics** (GA4 / Plausible / Fathom / Cloudflare Web Analytics). Snippet installed on every page (not just the home page); a test pageview fired; the provider's real-time view confirmed showing the visit. Cookie-setting analytics (GA4) flag a dependency: phase 25 must wire cookie consent before this integration is launch-legal in the EU.
- **Mailing list** (Mailchimp / ConvertKit / Buttondown / Resend Audiences / Beehiiv). The signup form (built in phase 23) posts to the provider; a test signup added a real subscriber to the real list (then removed); double-opt-in flow, if the provider uses one, exercised end-to-end.
- **CRM** (HubSpot / Pipedrive / Attio / a Notion-or-Airtable-as-CRM). A test lead submitted via the relevant form created a record in the real CRM; field mapping verified (name → name, not name → company).
- **Chat / support** (Crisp / Intercom / Tawk.to / Cal.com-without-payment for "book a call" that doesn't take money). Widget loads on the configured pages; a test message arrived in the provider's inbox; the widget does not block render or tank Lighthouse (re-check against phase 22's budget).
- **Site search** (Pagefind / Algolia DocSearch / a CMS-native search). Index built against real content; a test query returned correct results; the index is regenerated on content change (build-step wired, not a one-time manual index).
- **Scheduling without payment** (Cal.com / Calendly free-tier embed for a no-cost booking). Embed renders; a test booking landed on the connected calendar; this is *not* the transactional booking path (that is phase 24a) — a free "book a 15-min intro call" with no money changing hands is a phase-24 integration, and the agent draws that line explicitly per the phase-11 transactional decision-tree edge cases.

The agent updates `.website-builder/project.yaml.current_phase` upon completion — to `24a` if `transactional: true`, to `25` if `transactional: false`. The conditional is the agent's, computed from the locked flag, surfaced to the user, not guessed.

## Gating rules

The agent refuses to advance when:

- **An integration phase 3 named is missing.** If `requirements` says the conversion path is "visitor → newsletter subscriber" and there is no mailing-list integration wired, the agent refuses and surfaces the gap: "Phase 3 said the whole point of this site is newsletter signups. There's no mailing-list integration. We can't launch the site that's supposed to grow a list without the list." The agent does not silently treat a missing integration as out of scope; it surfaces and resolves.
- **An integration the site's shape demands is missing even though phase 3 didn't name it.** If the site has a 200-post blog and no site-search, the agent surfaces: "Phase 3 didn't list search, but a 200-post archive with no search is a usability hole users will hit on day one. Add it now, or log an explicit decision that search is deferred to v1.1 and accept that gap." This is a surface-and-recommend gate, overridable with an explicit logged decision.
- **Parity failure: configured on staging/preview, absent on production target.** The defining gate of this phase. If the analytics property the snippet points at is a dev property, or the mailing-list API key in production env is the test key, or the CRM webhook URL points at a preview deploy, the agent refuses to mark the integration done. It surfaces the specific mismatch and the fix (set the production env var; point the snippet at the prod property; update the webhook URL). This gate is **not overridable** — a launched site with analytics silently writing to a throwaway dev property is the exact failure phase 24 exists to prevent.
- **Cookie-setting integration wired without a phase-25 dependency flagged.** If an integration sets non-essential cookies (GA4, some chat widgets, some CRM trackers), the agent records a hard dependency that phase 25 must wire cookie consent gating before launch. It does not refuse phase 24 advance for this — the dependency is forward-looking — but it writes the dependency into `INTEGRATIONS-REPORT.md` and surfaces it so phase 25 cannot miss it. (A launched EU site dropping GA4 cookies before consent is a real legal exposure; phase 25 owns the fix, phase 24 owns the flag.)
- **Transactional fork ambiguity.** If `project.yaml.transactional` is somehow unset (it should be impossible — phase 11 is not skippable — but a corrupted state or a manual edit could produce it), the agent refuses to compute `next_phase` and routes back to phase 11's transactional decision rather than guessing the branch.

Override is available on the "phase-3 didn't name it but the shape demands it" and "deferred integration" gates via explicit user confirmation with the cost logged in `.website-builder/decisions/`. The parity gate and the unset-transactional-flag gate are not overridable.

## Tools and skills used

- **The provider's MCP, where one exists** — the canonical-tool-first principle. If the analytics/CRM/mailing provider publishes an MCP, the agent uses it for configuration and verification rather than hand-rolling REST calls.
- **`Bash`** — for provider CLIs (where the provider ships one) and for `curl`-based REST configuration + verification when no MCP/CLI exists. Also for build-step wiring (e.g., adding the search-index build to the deploy pipeline).
- **`Edit` / `Write`** — to write integration client code (snippets, SDK calls, webhook handlers, embeds) into the user's project in the chosen stack's convention. Server-side secrets are referenced via env vars (per `DESIGN-secrets-and-keys.md`), never inlined.
- **`Playwright` MCP** — the parity-verification workhorse. The agent loads the production-bound build, fires the real event (pageview, form submit, chat message), and confirms the event arrived at the provider. Playwright is also how the agent re-checks that a heavy chat widget didn't regress the phase-22 Lighthouse budget.
- **`WebFetch` / `WebSearch`** — to confirm a provider's current snippet/embed/API shape when the agent's training data may be stale (analytics SDKs and embed snippets change). Used per-integration as needed; cited in `INTEGRATIONS-REPORT.md`.
- **`AskUserQuestion`** — for the keys the agent cannot self-serve (the user creates the GA4 property, the Mailchimp list, the CRM pipeline; the agent walks them through it and consumes the resulting key per `DESIGN-secrets-and-keys.md`'s provider-key UX).
- **`Read`** — `.website-builder/project.yaml.requirements` (the integration contract), `.transactional` (the fork), `keys.yaml` (the key registry), `audit/FORMS-REPORT.md` (the forms integrations piggyback on).

No subagent spawn by default. When phase 3 named many independent integrations and the user wants parallel configuration, the agent may surface that option, but the default is sequential so each integration's parity check is a real, observed event rather than a batched assumption.

The `wb-prelaunch` phase-group skill (loaded at the transition into the pre-launch group) carries the cross-phase contract for phases 24-27: the integrations wired here, the legal pages phase 25 adds (cookie consent gating the analytics wired here), the structured data phase 26 emits, and the cross-browser pass phase 27 runs all compose on the same site. The commerce branch 24a/b/c shares the `wb-prelaunch` skill (per Decision 64 — there is no separate commerce skill).

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| `.website-builder/audit/INTEGRATIONS-REPORT.md` | One section per integration: provider, purpose (phase-3 requirement served), key location (env-var + source), client-code location (file:line), parity check (event fired, configuration targeted, receipt confirmed), caveats | The audit trail proving each integration is live against production, not staging; read by phase 27 (QA), phase 29 (deploy parity), and the post-launch maintainer |
| Integration client code in the user's project | Per stack convention | The actual snippets/SDK calls/webhook handlers/embeds — live code, not described |
| `.website-builder/keys.yaml` (updated) | Per `DESIGN-secrets-and-keys.md` — references only | New integration keys registered as references; secrets stay in `.env`/1Password |
| `.website-builder/decisions/integration-deferred-{slug}.md` *(when applicable)* | Standard decision-doc frontmatter + body | Created only when an integration the site's shape demanded was explicitly deferred to v1.1 with the user's logged acceptance of the gap |

The `INTEGRATIONS-REPORT.md` is the required artifact. The agent writes the cookie-consent dependency for any cookie-setting integration into this report explicitly so phase 25 cannot miss it.

## Common failure modes

**Integration works on the preview deploy, silently doesn't on production.** The canonical failure. The user (or the agent, sloppily) sets the analytics property / API key / webhook URL in the preview environment, sees the test event arrive, and calls it done — then production launches pointed at nothing. The agent's parity gate exists for exactly this: the test event must be fired against the *production-bound* configuration, and "I'll set the prod env var at deploy" is a deferred-not-done state the agent records as a phase-29 dependency, not a phase-24 completion.

**The user wired analytics but the site is now an unconsented-tracking liability.** GA4 (and many CRM/chat trackers) drop non-essential cookies the moment the page loads. For an EU/Swiss audience, that is a consent violation the instant the site launches. The agent does not treat "analytics installed" as "analytics done" — it writes the hard dependency that phase 25 must gate this integration behind cookie consent, and surfaces it so the user understands that phase 25 is not optional polish for them, it is the thing standing between this integration and a legal exposure.

**"Just add Google Analytics, everyone has it."** Cargo-culting the integration. The agent surfaces that GA4 is a specific choice with specific consequences (Google data-sharing, cookie-consent burden, ITP/Safari measurement gaps) and that for a privacy-conscious audience Plausible / Fathom / Cloudflare Web Analytics are cookieless alternatives that sidestep the phase-25 consent dependency entirely. The agent does not refuse GA4; it makes the choice informed.

**The mailing-list integration "works" but the test never created a real subscriber.** The agent submitted the form, got a 200, and called it done — but the 200 was the form provider accepting the POST, not the mailing-list provider adding the subscriber. The agent's parity check requires confirming the subscriber appeared in the *real list* (and removing the test subscriber after), not that the form returned success. Form-accepted ≠ subscriber-created; the agent verifies the latter.

**Chat widget tanks performance.** A heavy Intercom/Drift bundle loads on every page and the phase-22 Lighthouse 80+ is now a 60. The agent re-runs the phase-22 budget check after wiring any render-affecting integration and surfaces the regression: "the chat widget cost you 20 Lighthouse points — defer-load it, lazy-mount it on interaction, or accept the score drop with explicit confirmation." Integrations are not exempt from the performance discipline phase 22 established.

**The user thinks a free booking link is the same as commerce.** "I'm adding a Cal.com 'book a free intro call' button — does that make me transactional?" Per the phase-11 decision-tree edge cases: free booking with no payment is a phase-24 integration, not the phase-24a commerce branch. The agent draws the line explicitly — money or a time-commitment-that-needs-payment-rails routes to 24a; a no-cost calendar embed is just an integration here — and does *not* flip the transactional flag (which would force a decision-34 restart) for a free booking.

**An integration phase 3 named is quietly dropped because it's annoying to wire.** The CRM integration is fiddly, so it gets left out and nobody mentions it. The agent's first gate catches this by re-reading `requirements` and enumerating every named integration; a phase-3 integration is either wired, or explicitly deferred with a logged decision and the user's acceptance — never silently absent.

**The transactional fork is taken on a guess.** The agent reaches phase 24 close and assumes "this looks like a portfolio, probably non-transactional, jump to 25" without reading the locked flag. The agent computes `next_phase` strictly from `project.yaml.transactional` — never from the site's vibe — and surfaces the computed branch so the user can catch a wrong phase-11 decision before the pipeline commits to it.

## Reference materials

- **Design doc — phase pipeline source:** `DESIGN-phase-contracts.md` § 24 (seed for this contract) + the pipeline-overview branch diagram (24 → 24a/25 fork)
- **Design doc — pipeline integration + the conditional fork:** `DESIGN-architecture.md` § Phase contracts
- **Design doc — key handling for every integration:** `DESIGN-secrets-and-keys.md` § The hybrid mechanism + § Provider key configuration UX + § Phase contracts that invoke this concern (phase 24 listed there)
- **Design doc — production deploy target (parity is checked against this):** `DESIGN-deploy-providers.md` § Phase contracts that invoke this concern (phase 24 listed there — "some hosting features may load-bear integrations")
- **Phase 11 transactional decision (the fork's source of truth):** `phase-contracts/11-stack-decision.md` § Transactional decision — the two seed questions, the edge cases (free booking = non-transactional-ish but routes to 24a only when a time-commitment needs payment rails; the agent applies the same line here), and decision 34's mid-project-change cost
- **Phase 3 requirements (the integration contract):** `phase-contracts/03-requirements.md` § What Claude must establish — the conversion outcome the integrations serve
- **Phase 22 / 23 (the budget + forms this phase composes on):** `phase-contracts/16-copywriting.md` voice baseline; phase-22 Lighthouse budget and phase-23 forms reports are the constraints integrations must not regress
- **Config vs secret discriminator:** `.claude/rules/config-conventions.md` + `.claude/rules/secrets-conventions.md` — provider *names* are config; provider *keys* are secrets; the agent never inlines the latter

No website-builder design doc is dedicated solely to non-commerce integrations — the integration set is project-specific, derived from phase-3 requirements. This contract is the canonical reference for the phase; provider-current snippet/API shapes are confirmed via `WebFetch`/`WebSearch` at authoring-of-the-user's-site time and cited in `INTEGRATIONS-REPORT.md`. Freshness date for this contract: **2026-05-18**.
