# DNS + SSL Verification — phase 28 workhorse

> Reference for phase 28. The phase contract `phase-contracts/28-domain-dns-ssl.md` is the substantive source of truth; this file is the verification command toolkit the skill loads on demand.
>
> External patterns confirmed fresh 2026-05-18 via WebSearch (Cloudflare SSL/TLS Domain-Control-Validation docs, Vercel domains troubleshooting, DNS-over-HTTPS). DNS/SSL practice + CA policy evolve — re-check at session start when phase 28 is active. **The defining discipline: verify by observation, never by assumption.** An API 200 is not propagation; "the host does SSL automatically" is not a valid certificate.

## The verification principle

DNS is "done" when `dig` / DNS-over-HTTPS observes the records resolving to the right target — not when the registrar API returned 200. SSL is "done" when `openssl` / `curl` observes a valid certificate covering apex+www with HTTPS enforced — not because the host auto-provisions. Propagation is waited-for and verified, not hoped-through. The agent surfaces the realistic propagation window honestly and observes the end state.

Propagation reality to surface to the user up front:
- Standard records (A, AAAA, CNAME, TXT): typically minutes, occasionally up to a few hours.
- **Nameserver delegation changes: up to 24-48 hours** to fully propagate.

## Ownership verification (whois)

```bash
whois example.com | grep -iE 'registrar|registrant|creation|expiry|name server'
```

Confirm the domain is registered and the registrar matches what the user said. The domain must be in the **user's own registrar account** — never the agent's or a third party's. This is non-overridable per the contract.

## Propagation verification (dig + DNS-over-HTTPS, multiple resolvers)

Query from multiple independent resolvers — a single resolver's cache is not propagation:

```bash
# Apex + www, against several public resolvers
dig +short example.com A @1.1.1.1
dig +short example.com A @8.8.8.8
dig +short example.com A @9.9.9.9
dig +short www.example.com CNAME @1.1.1.1

# Authoritative answer (bypass resolver caches)
dig +trace example.com A
dig NS example.com +short          # confirm the nameserver delegation took effect

# Any host-required verification TXT
dig +short _vercel.example.com TXT @1.1.1.1
dig +short example.com TXT @1.1.1.1

# DNS-over-HTTPS cross-check (encrypted query, resolver-independent)
curl -s 'https://cloudflare-dns.com/dns-query?name=example.com&type=A' \
  -H 'accept: application/dns-json' | python3 -m json.tool
curl -s 'https://dns.google/resolve?name=www.example.com&type=CNAME' | python3 -m json.tool
```

Mark DNS done **only** when the records resolve to the expected target (the phase-29 host's IP/CNAME per `deploy-provider-matrix.md` § DNS records per host) from multiple resolvers *and* the DoH cross-check agrees. If a resolver still shows the old value, propagation is incomplete — wait and re-check, do not declare done.

Failure pattern to catch: the agent set records via API, got a 200, called it done — but the records were set on the wrong zone, or have not propagated, and the domain still 404s an hour later. The API 200 is not the proof; the observed resolution is.

## SSL verification (openssl + curl)

Run **after** DNS resolves (SSL cannot provision until DNS points right):

```bash
# Certificate issuer, validity window, SAN coverage
echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null \
  | openssl x509 -noout -issuer -subject -dates -ext subjectAltName

# Confirm SAN covers BOTH apex and www
echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null \
  | openssl x509 -noout -ext subjectAltName | grep -iE 'example\.com|www\.example\.com'

# HTTPS enforced — HTTP must redirect to HTTPS
curl -sI http://example.com  | grep -iE '^location:|^HTTP/'
curl -sI https://example.com | grep -iE '^HTTP/|^strict-transport-security:'

# Full handshake + redirect chain (apex ⇄ www canonical)
curl -sIL https://example.com      | grep -iE '^HTTP/|^location:'
curl -sIL https://www.example.com  | grep -iE '^HTTP/|^location:'
```

Mark SSL done **only** when: the issuer is the expected CA (Let's Encrypt or the platform CA), the cert is not expired, the SAN covers both apex and www, and HTTPS is enforced (HTTP → HTTPS redirect + ideally HSTS). "The host auto-provisions SSL" is not "SSL is active" — provisioning can fail silently.

## Apex + www + canonical redirect

Both `example.com` and `www.example.com` must resolve, and one must canonically redirect to the other — the user's choice, applied consistently. This must match:
- The phase-26 canonical URL (the `<link rel="canonical">` host).
- The phase-30 Google Search Console property (GSC does not follow redirects — the submitted sitemap must be on the canonical host).

Failure pattern: a CNAME on `www` but no apex `A`/`ALIAS`, so `example.com` 404s while `www.example.com` works (or vice-versa). Both must resolve; the redirect direction must be set and observed in the `curl -sIL` chain above.

## CAA + Domain-Control-Validation troubleshooting

If the certificate does not issue, diagnose before shipping an HTTP-only site:

```bash
# CAA record — does an existing CAA permit the CA the host uses?
dig +short example.com CAA @1.1.1.1
dig +short example.com CAA @8.8.8.8
```

- **CAA blocking issuance** is the classic silent failure: an existing `CAA` record permits only a different CA, so Let's Encrypt / the platform CA cannot issue and SSL silently never provisions. Fix: add `example.com. CAA 0 issue "letsencrypt.org"` (for Let's-Encrypt-backed hosts like Vercel/Netlify) alongside any existing CAA, or the CA the chosen host documents.
- **Domain Control Validation (DCV) methods** (per Cloudflare SSL/TLS DCV docs, 2026): the CA proves domain control via one of — HTTP token at `/.well-known/pki-validation/` (HTTP method), a `TXT` record at the authoritative DNS (DNS method, TXT), or TLS-ALPN. On a Cloudflare **full setup** (Cloudflare runs the authoritative nameservers), Cloudflare handles DCV automatically via a TXT record on the user's behalf. **Wildcard domains support only DNS-01** — which on Vercel requires the Vercel-managed-nameservers path.
- **DNS not yet pointing right** — DCV fails because the challenge target is unreachable; resolve the propagation step first, then the cert issues.
- **`AAAA` record breaking issuance (Framer)** — Framer's SSL is blocked by any `AAAA` record; remove `AAAA` records for a Framer-hosted apex (per `deploy-provider-matrix.md` § DNS records per host).
- **Cloudflare proxy redirect loop (Framer)** — if DNS is on Cloudflare and the host (Framer) provides its own SSL+CDN, set the record proxy status to **DNS-only (gray cloud)**; proxied (orange cloud) creates a redirect loop.

## DOMAIN-REPORT.md evidence checklist

The phase-28 artifact `.website-builder/audit/DOMAIN-REPORT.md` records (per the contract schema):

- Domain + registrar, with **ownership confirmed** (the `whois` evidence + the user's account confirmation).
- DNS records set (type / name / value / the target host they point at).
- **Propagation verification** — the `dig` / DoH output showing resolution + a timestamp.
- **SSL verification** — issuer, validity window, SAN coverage (apex + www), HTTPS-enforced.
- The **canonical-redirect direction** (apex→www or www→apex), observed in the redirect chain.

The report's value is the *observed* propagation + SSL evidence — pasted command output with a timestamp, not a claim that "it was verified."
