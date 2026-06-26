---
type: RPT
captain: corpus-1
program: website-builder remediation — Corpus track (parallel to orchestration-spine waves)
dispatched_by: general-website-builder
relates_to:
  - Workstreams/website-builder/foundation/DESIGN-architecture.md
  - Workstreams/website-builder/cross-cutting/DESIGN-resource-curation.md
  - Workstreams/website-builder/foundation/DESIGN-ecosystem-catalog.md
branch: corpus-1
status: complete
created: 2026-06-26
---

# RPT — corpus-1 (reference-corpus population)

> NOTE TO GENERAL: this RPT lives in the plugin worktree at `reference-corpus/RPT-corpus-1.md` because the worktree cannot write to the vault repo. Relocate it to `Workstreams/website-builder/RPT-corpus-1.md` on review.

## Summary

Populated 3 of the 6 `reference-corpus/` dirs with real, substantive reference content per `DESIGN-architecture.md` §328/329/333 — no stubs, no `.gitkeep`-only dirs. Each dir has a `README.md` index with provenance + consuming phases. Verified the upstream `VoltAgent/awesome-design-md` repo (MIT, 73 exemplars). Did **not** edit `scripts/wb_library.py`; instead this RPT **specifies** the catalogue-entry wiring + a flagged catalogue-schema decision for the General to land post-merge. All 26 content-file frontmatter blocks parse; the existing `tests/library/` suite (39 tests) stays green (doc-only change, no code touched).

## What was done

Created + populated under `reference-corpus/` (branch `corpus-1`, off `dev`):

| Dir | Files | Content |
|---|---|---|
| `design-systems/` | README + **5** docs (`material-3`, `apple-hig`, `ibm-carbon`, `tailwind`, `radix-shadcn`) | Per system: principles + full token system (color/type/spacing/motion) + strengths/trade-offs + when-to-use + how-the-agent-applies-it. §329 wants 3-5 → shipped 5. |
| `brand-examples/` | README + **7** brands (`hearthstone-bakery`, `northbeam`, `lumen-wellness`, `voltic`, `marigold-and-co`, `atelier-nord`, `pip-and-parsnip`) | Per brand: positioning + voice & tone (with sample lines) + OKLCH tokens (mirrors `brand.yaml.tokens` schema exactly, incl. light + dark surface sets) + typography + spacing/radius/motion + component patterns + do/don't. Original + fictional. §328 wants 5-8 → shipped 7 across distinct archetypes (warm↔cool, calm↔bold, serif↔sans, consumer↔B2B). |
| `awesome-design-md-corpus/` | README + **14** exemplars (`claude`, `stripe`, `linear`, `vercel`, `notion`, `figma`, `shopify`, `airbnb`, `spotify`, `apple`, `framer`, `supabase`, `raycast`, `nike`) | `DESIGN.md`-style specs (color/typography/layout/components/motion/voice/signature-moves/when-to-reference), format adopted from MIT-licensed upstream, grounded in each brand's public design language. §333 wants 10-20 → shipped 14 spanning AI/fintech/productivity/dev-tools/design-tools/e-commerce/media/retail. |

Also: lightly updated the top-level `reference-corpus/README.md` (additive — indexes the 3 new dirs; left Captain P's `seeds/` Phase-5 framing intact).

Total: **29 files** (26 content + 3 dir-READMEs), ~180 KB of real content. Token-format alignment to `phase-contracts/17-design-system.md` schema (decimal-L OKLCH, 4px spacing base, named type scale, motion tokens, light+dark surfaces).

## DoD evidence

1. **Each of the 3 dirs populated per §328/329/333 (NOT .gitkeep-only); per-dir README with provenance.**
   - `find reference-corpus -type f | sort` → 5 design-systems docs + 7 brand-examples + 14 corpus exemplars, each dir with a `README.md` carrying a provenance + licensing section + consuming-phase mapping. Counts hit each section's numeric range.
   - Render/parse check: `uv run --with pyyaml` walk over all 30 `.md` → **26 frontmatter blocks parse OK, 0 bad, 4 READMEs (frontmatter-free, expected)**. (A first pass caught 5 malformed-YAML frontmatter blocks in design-systems — unquoted `trademarks:` values with embedded quotes/commas; fixed by quoting + normalizing `©`→`(c)`; re-ran green.)
2. **Catalogue-entry spec (resource-id → path → type) for all 3 dirs, in this RPT.** → see `## Catalogue-entry spec` below.
3. **Note which `tests/library/` catalogue tests need extending.** → see `## tests/library extensions` below.
4. **No regression** (ship-verification): `pytest tests/library/ -q` → **39 passed** (doc-only change; `wb_library.py` untouched).

## Catalogue-entry spec (SPECIFY — General wires into `wb_library.py` post-merge)

`scripts/wb_library.py` resolves catalogue keys via `CATALOGUE_CLONE_KEYS: dict[str, tuple[source_url_or_ref, type, default_subdir]]` → `_resolve_resource()` → `_fetch_resource()`. Current `_fetch_resource` has exactly two behaviors: `type == "github-repo"` → `git clone --depth 1`; everything else → register-and-defer (agent fetches via WebFetch/context7). **There is no type for "copy a directory bundled inside the plugin into the project library."** That gap is the one catalogue-schema decision the General must resolve. Two ways to surface these dirs:

### Mode 1 — agent-read-in-place (zero code; ships today) — RECOMMENDED as the v1 default

Treat all 3 dirs like `reference/voice-archetypes/` (per `DESIGN-resource-curation.md` line 100, surfacing mode "n/a — ships with plugin"): the agent simply **Reads them from the plugin's `reference-corpus/`** at phase 17. No catalogue entry, no fetch, no clone. The wiring is a read-path reference in the phase-17 skill/contract (`skills/wb-design-system/` + `phase-contracts/17-design-system.md`), e.g.:
> *Reference corpora (read in place): `reference-corpus/design-systems/`, `reference-corpus/brand-examples/`, `reference-corpus/awesome-design-md-corpus/`.*

This is the lowest-risk, works-immediately path and matches how bundled exemplars are already specified.

### Mode 2 — clone-into-project (needs a new `bundled` type) — the enhancement the INST's catalogue-entry spec targets

To make these "selectively cloneable into the user's project" (the `reference-corpus/README.md` framing), add a **new resource type `bundled`** whose source is a plugin-relative path and whose fetch is a local copy (not a network op). Proposed `CATALOGUE_CLONE_KEYS` additions:

```python
# Bundled plugin-local reference corpora (committed under reference-corpus/).
# tuple = (source_url_or_ref, type, default_subdir)
"design-systems-corpus":    ("reference-corpus/design-systems",           "bundled", "design-systems"),
"brand-examples-corpus":    ("reference-corpus/brand-examples",           "bundled", "brand-examples"),
"awesome-design-md-corpus": ("reference-corpus/awesome-design-md-corpus", "bundled", "awesome-design-md"),  # see DECISION below
```

Minimal code to support `bundled` (General's call; ~15 lines):
- `_default_subdir_for_type`: add `"bundled": "docs"` (or per-key default).
- `_resolve_resource`: bundled keys already resolve via `CATALOGUE_CLONE_KEYS`; the source is a plugin-relative path — resolve it against the plugin root using the **same anchor `_find_phase_contract` already uses**: `Path(__file__).resolve().parent.parent`.
- `_fetch_resource`: add `if rtype == "bundled": shutil.copytree(plugin_root / source_rel, target, dirs_exist_ok=False)` — idempotent (skip if `target` exists), **local copy → returns True (status "cloned")**, never "fetch-deferred" (no network).
- `autoclone_for_state`: because a bundled source resolves to a real local path, it can be copied inline at phase-entry → `CloneResult.status == "cloned"` rather than `"fetch-deferred"`.

### DECISION the General must make — `awesome-design-md-corpus` key collision

`awesome-design-md-corpus` **already exists** in `CATALOGUE_CLONE_KEYS`, pointing at the full upstream GitHub clone (`https://github.com/VoltAgent/awesome-design-md`, `github-repo`). My shipped curated subset is a *different source* for the same logical resource. Pick one:

- **Option A (recommended):** repoint `awesome-design-md-corpus` → the bundled curated subset (`("reference-corpus/awesome-design-md-corpus","bundled","awesome-design-md")`), and **leave `awesome-design-md` pointing at the full upstream github clone**. Clean semantics: bare key = full upstream (network clone), `-corpus` suffix = shipped curated subset (offline, vetted). **No existing test breaks** — phase-17's contract uses `resource: awesome-design-md` (still github), and `test_reads_clones_at_entry_from_contract` / `test_idempotent_skips_present` reference `awesome-design-md` (unchanged).
- **Option B:** make the shipped subset the phase-17 default — repoint the phase-17 contract `resource: awesome-design-md` → `awesome-design-md-corpus` and the corpus key → bundled. Offline-first + vetted-by-default, but requires editing `phase-contracts/17-design-system.md` **and** the existing tests that assert `awesome-design-md` resolves to github.

I recommend **Mode 1 for v1 (ship now) + Option A for the Mode-2 enhancement** (clean, non-breaking, lets `wb library add awesome-design-md-corpus` pull the curated subset while the full upstream clone stays available under the bare key). I did not bake either into code — this is the General's wiring + resolvability-verification step per the INST.

## tests/library extensions (General wires + extends post-merge)

If Mode 2 / the `bundled` type lands:
- `_resolve_resource("design-systems-corpus")` → asserts `("reference-corpus/design-systems","bundled","design-systems")` (+ same for `brand-examples-corpus`, `awesome-design-md-corpus`).
- `_detect_url_type` / `_default_subdir_for_type` coverage for `"bundled"`.
- `_fetch_resource` bundled branch: temp plugin dir with a bundled source → assert `copytree` into target; assert idempotent skip when target present; assert returns True (local copy completes).
- `autoclone_for_state(trigger="phase-entry")` with a contract listing a bundled resource → `status == "cloned"` (not `"fetch-deferred"`).
- Option A: add a test that `awesome-design-md-corpus` now resolves bundled while `awesome-design-md` stays `github-repo` (guards the split). Option B additionally updates `test_reads_clones_at_entry_from_contract` expectations.

If Mode 1 only (no code): no `wb_library` tests change. Instead validate the phase-17 skill/contract gains the read-path references (a contract test + a `Path.exists()` check that the three `reference-corpus/` dirs are present).

## Decisions made

1. **reference-corpus/ vs reference/ placement.** `DESIGN-architecture.md` §326-333 lists `brand-examples/`, `design-systems/`, `awesome-design-md-corpus/` under **`reference/`**; the INST explicitly + repeatedly directs `reference-corpus/`. Followed the INST (it's the contract; General owns it; the `reference-corpus/README.md` "ships + selectively-cloneable" framing fits these dirs well). Flagged as a docs-update follow-up so the General can reconcile §326-333. The existing `reference/` dir still holds only `.gitkeep`.
2. **Original-derived content vs verbatim upstream copy** (for `awesome-design-md-corpus`). Upstream is MIT (redistribution allowed with attribution), so verbatim copies *would* be legal. I shipped **original, transformative `DESIGN.md`-style exemplars** grounded in each brand's public design facts instead, because: (a) consistent format the agent greps uniformly; (b) lower risk than committing verbatim third-party-*brand* guideline text I hadn't read in full; (c) per-file provenance points at the upstream `design-md/<brand>` entry so a verbatim swap is clean if the General prefers it. The corpus README documents the MIT attribution + the swap path.
3. **Brand-examples are original + fictional** (zero trademark/licensing risk) and span deliberately diverse archetypes; tokens mirror the real `brand.yaml.tokens` schema so each reads as a valid phase-17 output example. The Jules.Solutions brand was a **shape reference only** — none of its content reproduced.
4. **Fixed real YAML defects the verification caught** (5 design-systems frontmatter blocks) rather than papering over — quoted the values, normalized `©`→`(c)` for parser portability.

## Follow-ups filed

- **DESIGN doc reconciliation:** update `DESIGN-architecture.md` §326-333 so the `reference/` vs `reference-corpus/` home for these 3 dirs matches where they actually shipped (or move/symlink). General's call.
- **Wire the catalogue + phase-17 read paths** per the spec above (Mode 1 now; Mode 2 `bundled` type as enhancement) + extend `tests/library/` accordingly.
- **Remaining 3 of 6 reference-corpus dirs** (`voice-archetypes/`, `component-patterns/`, `seo-checklists/` per §330/331/332) are out of this packet's scope — likely corpus-2 / a follow-up.
- **Verbatim-vs-original swap** for `awesome-design-md-corpus`: if the General wants the actual upstream files, clone `VoltAgent/awesome-design-md` `design-md/` subset + commit the MIT `LICENSE`; per-file provenance frontmatter already names the upstream paths.

## Ship Verification

- **Files exist (not stubs):** `find reference-corpus -type f` → 29 files; `du -sh` per dir → design-systems 48K, brand-examples 64K, awesome-design-md-corpus 68K.
- **Markdown/frontmatter parses:** `uv run --with pyyaml` validator → 26 OK / 0 bad / 4 frontmatter-free READMEs; required keys (`type`,`corpus`,`provenance`,`consumed_by_phases`) present on every content file.
- **No code regression:** `uv run --with pyyaml --with pytest pytest tests/library/ -q` → **39 passed in ~1.8s** (catalogue resolution unaffected; `wb_library.py` not edited).
- **Upstream verified:** `VoltAgent/awesome-design-md` confirmed live, **MIT-licensed**, 73 exemplars in `design-md/` (WebFetch 2026-06-26).
- **Branch:** `corpus-1` (off `dev`). **Final commit sha:** recorded in the corpus-1 branch tip / reported in the dispatch final message. **Not merged, not pushed** per INST.

## Retro notes

- The frontmatter-validation pass earned its keep — caught 5 real parse breaks that would have silently failed any downstream YAML tooling. Worth keeping as a corpus lint.
- The one genuine architectural question (bundled-resource type) was specifiable rather than blocking, so I produced a decision-with-options instead of halting the whole packet — the corpus population (the bulk DoD) was fully independent of the catalogue wiring the General owns.
