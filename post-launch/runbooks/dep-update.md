# Runbook — dependency update

> Process for evaluating + applying dependency updates on a live site. Backs `wb-maintain-deps`. Customized per project at deploy: the stack-specific tooling below is selected from `project.yaml.stack`.

## Scope

Keeping the site's dependencies current and secure. Categorize by risk; apply safely; escalate breaking majors.

## Preconditions

- Read `project.yaml.stack` (tooling differs per stack) + `config.yaml.iteration_cadence` (cadence) + `config.yaml.deploy_provider`.
- Ensure the project's verify suite (build + tests + Playwright smoke) is runnable.

## Per-stack tooling

| Stack | List outdated | Apply | Verify |
|---|---|---|---|
| Next.js / SvelteKit / Astro (Node) | `npm outdated` / `pnpm outdated` | `npm|pnpm install pkg@version` | build + tests + Playwright smoke |
| Hugo | `hugo mod` / `go.mod` review | module bump | build + Playwright smoke |
| Python-adjacent tooling | `uv` / `pip list --outdated` | `uv` per `conventions.md` | tests |
| WordPress | core + plugin + theme update screen | update (staging first) | smoke on staging then prod |
| Framer / Webflow | platform-managed | platform updates | platform-verified; check integration SDK versions |

## Steps

1. **List outdated** per the stack row above.
2. **Categorize** each dep: **security** (CVE/advisory) / **minor** (low-risk bump) / **major** (potential breaking changes).
3. **Security** — surface the advisory, apply, run the full verify suite, deploy on confirmation. Apply immediately on advisory regardless of cadence.
4. **Minor** — surface, recommend, apply, regression check (build + smoke), deploy on confirmation.
5. **Major** — surface, recommend reading release notes (`WebFetch` changelog; `context7` for the new major's docs). If breaking changes touch the design system or a core flow → **escalate** via `wb-maintain-escalate` (a framework major is pipeline-scale, not a maintenance bump).
6. **One bucket at a time.** Don't bulk-bump everything — a failed build then has N suspects. Apply security first, then minors, then evaluate majors separately.
7. **Deploy** on user confirmation, every time — even a one-line security bump.

## Failure modes

- **Bulk bump** → diffuse failures. Bump in small batches.
- **Major applied blind** → broken build/runtime. Always read release notes first.
- **Skipped regression check** → a "harmless" minor breaks a flow in production.
- **WordPress prod-first update** → a plugin update breaks the live site. Update on staging first where the host supports it.
