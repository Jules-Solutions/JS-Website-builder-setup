---
phase: 23
name: Forms + interactive logic
group: build-integration
pipeline_section: build-integration
skill: wb-build-integration
prev_phase: 22
next_phase: 24
re_runnable: false
type: PHASE-CONTRACT
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-phase-contracts.md
  - Workstreams/website-builder/foundation/DESIGN-architecture.md
  - Workstreams/website-builder/foundation/DESIGN-project-scaffold.md
  - Workstreams/website-builder/cross-cutting/DESIGN-secrets-and-keys.md
  - Workstreams/website-builder/cross-cutting/DESIGN-context7-integration.md
---

# Phase 23 — Forms + interactive logic

> Every form on the site actually works, end to end. Contact forms email a real person. Signup forms add to a real list. Search filters real results. The phase that makes the site *do* something, not just look like it does. The agent refuses to deploy a form that has no endpoint configured — "I'll set up the email later" is exactly the failure this phase exists to prevent.

## Mission

Phases 19-22 produced a fast, accessible, responsive, assembled site. But a contact form that doesn't send anywhere is not a contact form — it is a contact-form-shaped div that silently drops every message a real visitor sends. Phase 23 makes every form and interactive surface on the site *actually function*, verified end-to-end.

The work product is `.website-builder/audit/FORMS-REPORT.md`: every form on the site tested via a real Playwright submission plus endpoint verification — the contact form's test submission actually arrives in the configured inbox; the newsletter signup actually adds to the configured list; the search actually filters results. After phase 23, the site's interactive promises are kept, not faked.

The discipline of this phase is **a form without a working endpoint is a broken form, and the agent refuses to ship one**. The canonical muggle failure is "I'll set up the email later" — the form looks done, the site launches, and weeks of leads silently vanish into a form that posts to nowhere. The agent refuses that path and, critically, makes setting up the endpoint feel *small* (it usually is — a Formspree form ID is a 60-second signup) rather than letting it feel like a blocker the user defers forever.

This phase also handles **secrets correctly by construction**: form endpoints that need an API key (Resend, Mailgun) get the key handled per the keys protocol — user-supplied at the moment of use, referenced by env var, never persisted into project state and never in client code. Endpoints that need no secret (Formspree's public endpoint ID) get exactly that and nothing more.

## Entry conditions

- Phase 22 (performance audit) complete. The site scores ≥ 80 on perf with green CWV (or a logged, authorized skip). Phase 23 wires the forms on the fast, audited site.
- Phase 21 (accessibility audit) complete. Forms already cleared the a11y form-label/name-role-value gates (3.3.2, 4.1.2) at phase 21; phase 23 makes the already-accessible forms also *functional* (the two are orthogonal — an accessible form that posts to nowhere is still broken).
- Phase 18 (component build) complete. The form components exist (specced + built + token-faithful); phase 23 wires their submission logic + endpoints, it does not re-build the form UI.
- Phase 3 (requirements) complete. The site's conversion outcome (the *one* thing the site is for — contact / subscribe / book / buy) is known; the primary form is the one that serves it, and it gets the most rigorous end-to-end verification.
- The keys protocol is initialized (`wb-bootstrap` set up `.website-builder/keys.yaml` + `.gitignore` for `.env`/`.env.*`). Phase 23 is one of the phases that adds entries to `keys.yaml` (email/form-provider keys, per `DESIGN-secrets-and-keys.md`).

## What Claude must establish

Every form and interactive surface on the site, verified working end-to-end:

1. **Every form has a configured, working endpoint.** For each form (contact, newsletter signup, lead capture, booking-intent, search, filter):
   - The endpoint is decided + configured (a form-handling provider — Formspree / Formspark / Basin for static-friendly no-backend; a transactional-email API — Resend / Mailgun — when the stack has a server route; the stack's own API route when it has a backend; the newsletter platform's signup API for list-add forms).
   - The form actually submits to it (the component's submit handler posts to the real endpoint, with loading/success/error states wired to the phase-16 `strings.json` microcopy — "Signing you up…" / "You're in." / "Hmm, that didn't work.").
2. **End-to-end verification per form.** Playwright submits the form with test data; the agent then verifies the *effect*: the test email arrived in the configured inbox, the test signup appears in the configured list, the search returned the expected filtered results. The exit is the verified effect, not "the form submitted without a JS error."
3. **Spam protection on public-facing forms.** At minimum a honeypot field; for forms that attract real spam (public contact/lead forms), a current bot-mitigation layer — Cloudflare Turnstile is the recommended 2026 default for most lead forms (low friction, privacy-respecting, free); hCaptcha/reCAPTCHA as alternatives — always with **server-side token verification** (never trust the client token alone). Layered defense (honeypot + Turnstile + provider spam filtering) for high-value forms.
4. **Interactive logic that isn't forms.** Search/filter that actually filters the real content; any client-side interactive feature promised in phases 13-15 actually functions (a pricing toggle changes the displayed price; a tabbed interface switches content; a load-more actually loads more).
5. **Secrets handled correctly.** Any form endpoint requiring a secret has it wired per the keys protocol (see `## Secrets handling` below): referenced by env var, user-supplied at the moment of use, never persisted in project state, never in client-side code. Public endpoint IDs (Formspree form ID) are *not* secrets and are fine in the markup.

Output: `.website-builder/audit/FORMS-REPORT.md`. `.website-builder/project.yaml.current_phase` updates to `24` only when every form is verified working end-to-end and every required endpoint is configured. Phase 24 (integrations — non-commerce) loads next.

## Gating rules

The agent refuses to advance when:

- **Any form has no configured endpoint.** The headline gate. A form that posts to nowhere is broken. The agent refuses to ship it and walks the user through configuring an endpoint *now* — making it feel small (a Formspree signup is 60 seconds), not deferred. Non-overridable: a deployed form that silently drops submissions is worse than no form.
- **A form was not verified end-to-end.** "It submitted without an error" is not verification — the agent confirms the *effect* (email received / list updated / results filtered). A form whose effect wasn't verified is not done.
- **A form endpoint needs a secret and the secret is hardcoded or client-side-exposed.** A Resend/Mailgun API key in client code (or committed) is a security failure (and would be caught by the secrets anti-pattern hooks). The key must be server-side + env-referenced per the keys protocol. Non-overridable.
- **A public form has no spam mitigation.** A public contact/lead form with no honeypot and no bot challenge will be drowned in spam within days; that is a broken form by another route (the real submissions get lost in the noise, the provider may rate-limit/suspend). The agent wires at least a honeypot, and a current challenge layer for genuinely public forms.
- **Search/filter or a promised interactive feature doesn't actually work.** A search box that doesn't search, a filter that doesn't filter, a pricing toggle that doesn't toggle — promised interactivity that's faked is the same class of failure as a dead form.
- **Client token trusted without server verification** (for Turnstile/hCaptcha/reCAPTCHA). A bot can forge a client-side "passed" state; the token must be verified server-side against the provider before the business action (send the email / add to list) runs.

Override is not available on the endpoint, verification, or secrets gates — they are correctness/security prerequisites for a launchable site. (A genuinely form-less site — a pure brochure with no interactive surface — is *inapplicable*, not skipped: the phase runs, finds nothing to wire, and exits clean; see `DESIGN-phase-contracts.md` § Phase-skip authorization "inapplicable phase".)

## Tools and skills used

- **Playwright MCP** — the primary verification tool. The agent fills + submits each form with test data in a real browser and drives the verification (and, where the effect is web-visible — a success page, a list that shows the new entry — confirms it via the browser).
- **`Bash`** — to verify the *effect* of a submission where it isn't web-visible: checking that a test email was delivered (querying the provider's API/inbox where possible, or guiding the user to confirm receipt), confirming a list-add via the newsletter platform's API, running the stack's API route locally to test the server handler.
- **`AskUserQuestion`** — for endpoint configuration (which provider; the provider's form ID / API key at the moment of use), the spam-protection choice (Turnstile recommended default vs hCaptcha/reCAPTCHA), and confirming the user received the test email when only the user can see the inbox.
- **`mcp__context7__resolve-library-id` + `mcp__context7__query-docs`** — per `DESIGN-context7-integration.md`, phase 23 invokes context7 for the form-handling library's current API (`react-hook-form` + `zod` resolver, the stack's form action/route pattern) and the chosen provider's current integration. Provider integrations + form-library APIs change; the agent verifies current patterns.
- **`Edit` / `Write`** — to wire submit handlers to endpoints, add server-side token verification, add the honeypot + challenge, wire loading/success/error states to the phase-16 strings, add the `keys.yaml` entry + `.env.example` line, and write `audit/FORMS-REPORT.md`.
- **`Read`** — `keys.yaml` (the secret registry — phase 23 adds form-provider entries), `content/strings/{lang}.json` (the phase-16 form-state microcopy the handlers wire to), `components.yaml` (the form components built at phase 18), `project.yaml.requirements` (the conversion outcome → the primary form to verify most rigorously).

The `wb-build-integration` phase-group skill remains loaded (single skill for phases 19-23, Decision 64). It carries the cross-phase contract that phase 23 is the last build-integration phase — after it, the site *works*, and phase 24 (integrations) layers non-form integrations (analytics/CRM/chat) on top of a site whose forms already function.

The JSON handoff protocol may optionally be invoked here (`DESIGN-handoff-protocol.md` § Phase contracts that invoke this protocol): the agent can emit a form-component brief to an external tool. Default is agent-direct wiring.

## Output artifacts

| Path | Schema | Purpose |
|---|---|---|
| `.website-builder/audit/FORMS-REPORT.md` | per-form table (form / endpoint / provider / spam-protection / test-submission result / effect-verified Y-N) | The verification record — the exit criterion. Carried into phase 27 QA + post-launch monitoring (a broken form is a post-launch incident). |
| Form wiring in the project source | submit handlers → endpoints, server-side token verification, honeypot + challenge, states wired to strings.json | The actual functional forms — phase 23 makes them work, not just reports. |
| `.website-builder/keys.yaml` | adds form/email-provider key references (`source: env` / `source: onepassword`, `env_var`) | Declarative secret registry entry for any endpoint needing a key — references only, never the secret. |
| `.env.example` | adds the placeholder line for any new key (committed; empty value) | Surfaces the required key to the user without holding the secret. |
| `.website-builder/project.yaml` | `current_phase: 24` on all-forms-verified | Phase progression marker. |

`FORMS-REPORT.md` + the working forms are the required outputs. `keys.yaml`/`.env.example` entries exist only for forms whose endpoint needs a secret.

## Common failure modes

**"I'll set up the email later."** The canonical phase-23 failure, named in the seed. The form looks done; the user wants to launch; endpoint setup gets deferred; the launched contact form silently drops every lead. The agent refuses — and crucially makes the fix feel small: *"this is a 60-second step, not a project. Sign up at Formspree, paste me the form ID, and your contact form is real. Let's just do it now so you don't lose a single message."* The agent removes the friction rather than accepting the deferral.

**Form "works" because no JS error — but posts to nowhere.** The submit handler runs, shows the success state, and the data goes into the void (no endpoint, or a placeholder endpoint). The agent verifies the *effect* (the email actually arrived), not the absence of an error. Success-state-shown ≠ submission-received.

**Secret in client code.** The agent (or pasted code) puts a Resend/Mailgun API key in a client component or `NEXT_PUBLIC_`-prefixed env var, exposing it in the browser bundle. This is a security failure (and the secrets-anti-pattern hooks would refuse it). The agent wires the key server-side only (a server route / serverless function), env-referenced, per the keys protocol — see `## Secrets handling`.

**Public form with no spam protection.** A bare public contact form gets thousands of spam submissions within days, the provider rate-limits or suspends the account, real leads drown. The agent wires at least a honeypot, and Cloudflare Turnstile (2026 default) for genuinely public forms, with server-side token verification.

**Client-side captcha "pass" trusted.** The agent checks the Turnstile/reCAPTCHA token only in the browser; a bot forges the passed state and submits anyway. The agent verifies the token server-side against the provider before running the business action.

**Search that doesn't search / filter that doesn't filter.** A promised interactive feature is faked (a search box that's decorative, a filter UI with no logic). Same failure class as a dead form — the agent makes it actually function or surfaces that it can't be built as promised and reconciles scope with the user.

**Form-state microcopy left generic.** The handler shows "Submitted" / "Error" instead of the phase-16 voiced strings ("You're in. Check your inbox." / "Hmm, that didn't work. Try again?"). The agent wires the loading/success/error states to the phase-16 `strings.json` keys — the moments a user is most anxious are exactly where the brand voice matters most (the phase-16 microcopy discipline, enforced at wiring time).

**Provider chosen without fitting the stack.** The agent picks a server-side email API (Resend) for a purely static site with no server route to hold the key. The agent matches the endpoint to the stack: static/no-backend → a form-handling service whose endpoint ID is public (Formspree/Formspark/Basin); has a server route → a transactional API with the key server-side.

**Hidden assumption that a pretty form is a working form.** The agent surfaces, when the user equates the two, that the form's entire purpose is the effect (a message received, a subscriber added) — and an unverified form is, functionally, a decorative element until the effect is confirmed.

## Secrets handling

Per locked decisions 29 + 44 and `cross-cutting/DESIGN-secrets-and-keys.md`, form-endpoint secrets are handled **user-supplied at the moment of use, referenced by env var, never persisted into project state, never in client code**. Phase 23 is explicitly one of the phases that touches the keys protocol (`DESIGN-secrets-and-keys.md` § Phase contracts that invoke this concern → "Phase 23 (forms) — email / form-handling provider keys").

**The pattern:**

1. **Classify the endpoint.** Public endpoint identifiers are *not* secrets and belong in the markup as-is — a Formspree form ID (`https://formspree.io/f/{form_id}`) needs no API key in client code; the endpoint URL is the only thing in the HTML, server-side validation + ML spam filtering happen at Formspree. A transactional-email API key (Resend, Mailgun) *is* a secret and must never reach the client — Resend's own docs are explicit that the API key is server-side only, never exposed to client code.
2. **For secret-bearing endpoints, register, don't embed.** The agent adds an entry to `.website-builder/keys.yaml` (committed; references only, no secret value) naming the env var and source:
   ```yaml
   email:
     resend:
       api_key:
         source: env                 # env (.env, gitignored) | onepassword (op:// ref)
         env_var: RESEND_API_KEY
   ```
   and adds the placeholder line to `.env.example` (committed, empty). The actual value goes in the gitignored `.env` (muggle default) or a 1Password `op://` reference (opt-in upgrade) — never in any committed or project-state file.
3. **User supplies at the moment of use.** When the form first needs the key, the agent walks the user through getting it (where to create it at the provider) and where to put it (the `.env` line, or the 1Password reference) — it does not ask the user to paste the secret into the chat or into any file the agent then commits. The resolver populates `process.env.RESEND_API_KEY` at runtime; the server route reads `process.env.RESEND_API_KEY`.
4. **Server-side only.** The key is read in a server route / serverless function, never a client component, never a `NEXT_PUBLIC_`/`PUBLIC_`-prefixed var. The form posts to the site's own server route; the server route holds the key and calls the provider.
5. **Production parity at deploy.** Phase 29 (deploy) syncs the production key to the hosting provider's env (explicitly, loudly — never silent), per `DESIGN-secrets-and-keys.md` § What lives in production env vs `.env`. Phase 23 only establishes the local + reference setup; it flags the prod-sync as a phase-29 follow-through.

**Anti-patterns the agent refuses** (per `.claude/rules/secrets-conventions.md` + `DESIGN-secrets-and-keys.md`): an API key literal in source; a key in a committed file; a key in `NEXT_PUBLIC_`/client scope; a key pasted into a commit message or the chat-then-committed. The agent emits an env-var reference, never the literal key.

## Reference materials

Foundation docs:

- `Workstreams/website-builder/foundation/DESIGN-phase-contracts.md` § 23 — the seed for this contract; § Phase-skip authorization ("inapplicable phase" — a form-less site).
- `Workstreams/website-builder/foundation/DESIGN-architecture.md` § Integration with Claude Code primitives (Playwright + Bash + AskUserQuestion) / § context7 integration.
- `Workstreams/website-builder/foundation/DESIGN-project-scaffold.md` § `audit/` conventions; `keys.yaml` location.
- `Workstreams/website-builder/cross-cutting/DESIGN-secrets-and-keys.md` — **the secrets authority for this phase**. The hybrid `.env` / 1Password model (decisions 29, 44); the `keys.yaml` declarative registry; the resolver always producing env vars; per-stack secret-loading recipes; the explicit list naming phase 23 (forms) as a key-touching phase; the anti-patterns the agent refuses; production-env sync at phase 29.
- `Workstreams/website-builder/cross-cutting/DESIGN-context7-integration.md` — phase 23 invokes context7 for the form library + provider integration (`react-hook-form` + `zod`, `formspree setup`, the stack's form-action pattern).
- `Workstreams/website-builder/foundation/DESIGN-content-layers.md` — Layer 3 (`strings.json`): the phase-16 form-state microcopy phase 23 wires the handlers to.

Form providers + spam protection (mandatory at this phase — current as of the freshness date):

- **WebFetch — Formspree (`https://formspree.io/`):** the canonical no-backend form pattern. The user registers to get a unique form ID; the HTML form's `action` points at `https://formspree.io/f/{form_id}`; **no API key/secret is needed in client code — the endpoint ID is the sole identifier in the markup**; Formspree validates server-side and uses ML spam filtering, emails notifications, stores submissions. Enables a functional form with no server infrastructure — the recommended path for static/no-backend stacks.
- **WebFetch — Resend (`https://resend.com/docs/introduction`):** the transactional-email API pattern when the stack has a server route. An API key authenticates; an API call sends mail (`from`/`to`/`subject`/`html`); **the API key is server-side only and must never be exposed to client-side code** — exactly the secrets-handling rule above. Mailgun follows the same shape (server-side key). The agent picks the canonical current doc per chosen provider at phase-23 entry.
- **WebSearch "form spam protection 2026"** — current practice: honeypot is the baseline non-intrusive layer; **Cloudflare Turnstile is the recommended 2026 default for most lead forms** (free, low-friction, privacy-respecting CAPTCHA replacement); hCaptcha/reCAPTCHA are alternatives (reCAPTCHA triggers more visible challenges). Layered defense (honeypot + Turnstile + provider filtering/Akismet) for high-value forms; **never trust the client token alone — always verify server-side before the business action**. Sources: [Cloudflare Turnstile](https://www.cloudflare.com/application-services/products/turnstile/), [Honeypot vs reCAPTCHA vs Turnstile 2026 comparison — 3Zero Digital](https://www.3zerodigital.com/blog/how-to-protect-your-forms-from-spam-bots-honeypot-vs-google-recaptcha-vs-cloudflare-turnstile-2025-comparison), [Formspark spam protection](https://documentation.formspark.io/setup/spam-protection.html).

Freshness date for this contract's references: **2026-05-18**.
