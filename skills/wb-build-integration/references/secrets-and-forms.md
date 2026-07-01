# Secrets + forms (phase 23)

> The phase-23 secrets authority + form-provider matrix. Derived from `DESIGN-secrets-and-keys.md` (locked decisions 29 + 44) and `phase-contracts/23-forms-interactive.md` § Secrets handling. Provider patterns verified via WebSearch (Formspree / Resend / Mailgun / Cloudflare Turnstile) 2026-05-18. On conflict, the design doc + contract win.

## The discipline (one line)

**A form without a working endpoint is a broken form, and its secret (if any) is server-side + env-referenced + never persisted into project state + never in client code.** Public endpoint IDs are *not* secrets.

## Step 1 — classify the endpoint

| Endpoint type | Is there a secret? | Where it goes |
|---|---|---|
| **Public form-handler endpoint** (Formspree `https://formspree.io/f/{id}`, Formspark, Basin) | **No.** The form ID is a public identifier, not a key. | Directly in the markup. Server-side validation + spam filtering happen at the provider. |
| **Transactional email API** (Resend, Mailgun) | **Yes** — the API key. | Server-side only — a server route / serverless function. Never client, never `NEXT_PUBLIC_`/`PUBLIC_`. |
| **Stack's own API route** (Next route handler, SvelteKit endpoint, Astro server endpoint) | Depends — whatever that route calls (an email API key, a DB string). | Server-side in the route; env-referenced. |
| **Public publishable keys** (e.g., Stripe publishable — phase 24's concern, noted for completeness) | **No** — designed to be public. | Env or inline; not a secret per `config-conventions.md`. |

The classifying question (per `.claude/rules/config-conventions.md` / `secrets-conventions.md`): *"would exposing this in the browser bundle be a security problem?"* Formspree form ID → no → markup is fine. Resend API key → yes → server-side only.

## Step 2 — match the endpoint to the stack

| Stack situation | Recommended endpoint | Why |
|---|---|---|
| Static / no backend (Hugo, plain HTML, static Astro/Next export, Framer) | **Formspree / Formspark / Basin** — public form ID | No server to hold a secret; the provider does validation + spam + delivery. The recommended path for muggle static sites. |
| Has a server route (Next App Router, SvelteKit, Astro SSR, Next API routes) | **Resend / Mailgun via a server route** | The route holds the key server-side; the form POSTs to the site's own route; the route calls the provider. |
| Has a full backend / DB | The stack's own API route | Already has the server surface; wire the route to the provider or the DB. |
| Newsletter list-add | The newsletter platform's signup API (Mailchimp/ConvertKit/Buttondown/etc.) | List-add forms post to the platform; key server-side if the API requires one, public embed if the platform provides one. |

**Failure mode this prevents:** picking a server-side email API (Resend) for a purely static site with no server route to hold the key. Match the endpoint to the stack.

## Step 3 — the keys protocol (for secret-bearing endpoints only)

Per `DESIGN-secrets-and-keys.md`'s hybrid `.env` / 1Password model:

1. **Classify** (Step 1). Public ID → markup, done, no `keys.yaml` entry. Secret → continue.
2. **Register, don't embed.** Add a references-only entry to `.website-builder/keys.yaml` (committed; NO secret value):

   ```yaml
   email:
     resend:
       api_key:
         source: env            # env (.env, gitignored) | onepassword (op:// ref)
         env_var: RESEND_API_KEY
   ```

   And add the placeholder line to `.website-builder/.env.example` (committed, empty value).
3. **User supplies at the moment of use.** Walk the user through creating the key at the provider and putting it in the gitignored `.env` line (muggle default) or a 1Password `op://` reference (opt-in upgrade). Do NOT ask the user to paste the secret into the chat or into any file the agent then commits.
4. **Server-side only.** The key is read in a server route / serverless function via `process.env.RESEND_API_KEY` — never a client component, never a `NEXT_PUBLIC_`/`PUBLIC_`-prefixed var. The form POSTs to the site's own server route; the route holds the key and calls the provider.
5. **Prod parity is a phase-29 follow-through.** Phase 23 establishes only the local + reference setup. Flag (do NOT perform here) that phase 29 (deploy) syncs the production key to the hosting provider's env — explicitly, loudly, never silent. (Note: prod keys differ from local — e.g. `sk_test_` local vs `sk_live_` prod.)

The `source: onepassword` path resolves via `op run --env-file=.website-builder/.env.op` at process start; the resolver always produces an env var so code is uniform regardless of source. `.gitignore` already excludes `.env`/`.env.*` (set up by `wb-bootstrap`).

## Step 4 — spam protection (public forms)

WebSearch-verified 2026 practice:

- **Honeypot** — the baseline non-intrusive layer; a hidden field bots fill and humans don't. Always present on public forms. The Playwright test must leave it empty (see `playwright-recipes.md` § 5).
- **Cloudflare Turnstile** — the **recommended 2026 default** for genuinely public lead/contact forms: free, low-friction, privacy-respecting CAPTCHA replacement. hCaptcha / reCAPTCHA are alternatives (reCAPTCHA triggers more visible challenges).
- **Layered defense** for high-value forms — honeypot + Turnstile + provider-side filtering (Formspree ML spam filter, Akismet).
- **Server-side token verification is non-negotiable.** A bot can forge a client-side "passed" state. The challenge token MUST be verified server-side against the provider before the business action (send the email / add to the list) runs. A client-only check is the canonical phase-23 spam failure. Turnstile's server-verify secret is itself a secret → Step 3.

## Step 5 — verify the effect end-to-end

Per `playwright-recipes.md` § 5. The exit is the **verified effect**, not the success state. Playwright submits test data → confirm the effect via the path that fits: web-visible effect → browser assertion; provider API queryable → Bash provider query; only the user can see the inbox → `AskUserQuestion` ("did the test email arrive at `<inbox>`?"). Wire loading/success/error states to the phase-16 `strings.json` microcopy — the anxious moments are where brand voice matters most.

## Anti-patterns the agent refuses (per `.claude/rules/secrets-conventions.md` + the design doc)

- An API-key literal in source (`const KEY = "re_..."`).
- A key in any committed file (incl. `keys.yaml` — that holds references only).
- A key in `NEXT_PUBLIC_`/`PUBLIC_`/client scope.
- A key pasted into the chat then committed, or into a commit message / PR / issue.
- A secret written to `.website-builder/` state files (only `keys.yaml` references live there).
- A client-side challenge token trusted without server-side verification.
- Deferring endpoint setup ("I'll set up the email later") — the form silently drops every lead. Refuse; make the fix feel small (a Formspree signup is ~60 seconds).

The agent emits an env-var reference, never the literal key. The secrets-anti-pattern hooks would refuse a hardcoded-key Edit anyway — but the discipline is the agent's, not the hook's safety net.

## Provider quick-reference (verified 2026-05-18)

| Provider | Pattern | Secret? | Notes |
|---|---|---|---|
| **Formspree** | HTML form `action="https://formspree.io/f/{form_id}"` | No | Form ID is the sole identifier in markup; Formspree does server-side validation + ML spam filtering + email notification + submission storage. Recommended for static/no-backend. User registers to get the form ID. |
| **Formspark / Basin** | Same shape as Formspree (public POST endpoint ID) | No | Alternatives to Formspree; same no-backend pattern. |
| **Resend** | Server route calls the Resend API (`from`/`to`/`subject`/`html`); API key authenticates | Yes | Founded 2023, modern DX. **API key server-side only — Resend's own docs are explicit it must never reach client code.** Use when the stack has a server route. |
| **Mailgun** | Server route calls the Mailgun messages API; HTTP Basic Auth (`api:YOUR_API_KEY`) | Yes | Same server-side-only shape as Resend. Private API key (starts `key-`) for server ops. |
| **Cloudflare Turnstile** | Client widget + server-side `siteverify` of the token | Yes (the verify secret) | 2026 default challenge for public forms. Server-verify the token before the business action — always. |

Pick the canonical current provider doc via context7 / WebFetch at phase-23 entry per the chosen provider (provider integrations change).

## Source freshness

- Formspree no-backend / public-form-ID pattern: WebSearch formspree.io, 2026-05-18.
- Resend server-side-only key + modern transactional API: WebSearch resend.com + Courier "best email API 2026", 2026-05-18.
- Mailgun private-key server-side + HTTP Basic Auth (`api:KEY`): WebSearch Mailgun docs + AeroLeads guide, 2026-05-18.
- Cloudflare Turnstile as 2026 default + server-side token verification: WebSearch (per the phase-23 contract's verified sources), 2026-05-18.
- Hybrid `.env`/1Password keys protocol, `keys.yaml` references-only, anti-patterns: `DESIGN-secrets-and-keys.md` (locked decisions 29, 44), 2026-05-10.
