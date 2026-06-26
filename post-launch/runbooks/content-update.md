# Runbook — content update

> Process for content-only changes on a live site. Backs `wb-maintain-content` (edits) and the simple path of `wb-maintain-content-add` (additions). Customized per project at deploy: the stack, CMS, languages, and deploy provider below are filled from `config.yaml`.

## Scope

- Editing existing prose / microcopy (typo, stat, link, wording).
- Adding a new entry to an existing collection (essay / post / case study).

Out of scope: new pages (`page-add`), new sections (`section-add`), design changes (`iterate`).

## Preconditions

- Read `.website-builder/project.yaml` (stack, CMS, languages) + `.website-builder/post-launch/config.yaml` (deploy provider, translation preference) + `brand.yaml.voice`.

## Steps

1. **Locate.** `Grep` for the target string in `.website-builder/content/pages/{slug}.md` (Layer 4 prose) or `content/strings/{lang}.json` (Layer 3 CDJSON). Confirm the exact target with the user if multiple matches.
2. **Edit.** Apply the change via `Edit`. For additions, write the new content file + update the collection index.
3. **Multi-language.** If `config.yaml.languages` has more than one language, apply across all language files per `config.yaml.translation_preference`:
   - `1` (default) — translate the change inline.
   - `2` — emit `briefs/translation-{lang}-{ts}.json` for the changed content; ingest the translated return via phase 6.5.
   - `3` — ask the user each time.
4. **Voice check.** Read against `brand.yaml.voice` (say / never-say). A change that drifts off-voice is not a clean content edit — surface it.
5. **Validate.** CDJSON keys resolve; frontmatter parses; changed external links reachable (`WebFetch`); run the project content-lint if present.
6. **Diff + confirm.** Show before/after. Get explicit "yes, deploy".
7. **Deploy.** Via the project's provider (git-integration push or provider CLI per `config.yaml.deploy_provider`). Never autonomous.
8. **Verify live.** Walk the changed page at the real domain (Playwright); confirm the change rendered + nothing else broke.

## Failure modes

- **Multi-language drift** — one language edited, others stale. Always reconcile per the translation preference.
- **Off-voice "small" edit** — surface, don't ship silently.
- **Broken CDJSON reference** — a renamed/removed key leaves a dangling reference; validate before deploy.
