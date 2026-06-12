# `tests/skills-bundle/ui-ux-pro-max/` — manifest-validation tests (Captain M, Phase 5)

Validates `skills-bundle/ui-ux-pro-max.md` (the UI/UX Pro Max composition manifest)
against the canonical schema in `skills-bundle/README.md` and the actual read-only
`scripts/install-skills.sh` substrate.

## What's tested

`test_manifest.py` — class `TestUiuxManifest`, all **Tier 1** (no upstream / network /
external-tool dependency; pure static validation). Three concerns:

1. **Schema conformance** — every canonical frontmatter field present + correctly
   typed (`type`, `skill_name`, `upstream_id`, `upstream_url`, `upstream_license`,
   `upstream_attribution`, `install_method`, `install_target_path`,
   `install_size_estimate_mb`, `required_for_phases`, `optional_complementary_with`,
   `load_order`, `default_loaded`), enum values valid, `install_target_path` has all
   three OS keys ending in the skill basename, and the 7 mandatory H2 body sections
   present **in canonical order** (What it provides → How the website-builder uses it
   → Composition rules → Install → Verification → Uninstall → Upstream attribution).
2. **install-skills.sh compatibility** — the manifest agrees with the *actual*
   `scripts/install-skills.sh` (read-only): `skill_name` is a `KNOWN_SKILLS` row id,
   `install_method` maps to the script's method token (`skill-registry`→`registry`,
   `git-clone`→`git`), and `install_target_path` matches the script's `.claude/skills/<skill>`
   `cc_skills_dir` convention. This guards the consistency interlock flagged in
   `skills-bundle/README.md` § install-skills.sh consistency interlock.
3. **Upstream-URL well-formedness** — `upstream_url` is a syntactically valid https
   URL with a host and no schema-template placeholder leftovers. **No live fetch** —
   a real upstream reachability probe would be a Tier-2 test (skipped until the
   network surface is available); this suite stays Tier-1-always-green.

## Run

```bash
# From plugin root — default 'all' mode auto-discovers this file (pytest recurses):
bash tests/run-tests.sh

# Or just this suite:
cd tests && uv run --with pyyaml --with pytest pytest skills-bundle/ -v
```

## Notes

- **No fixture dir.** Unlike the `library/` and `keys/` Phase 5 subdirs, manifest
  validation needs no synthetic `.website-builder/` scaffold — it reads the committed
  manifest + install script directly. So no `.gitignore` un-ignore line is needed here.
- **Path resolution is cwd-independent** — the test resolves the plugin root via
  `Path(__file__).resolve().parents[3]`, mirroring `smoke_test.py`'s pattern, so it
  runs the same under `bash tests/run-tests.sh` and `cd tests && pytest`.
- **`--tier1` filter:** `TestUiuxManifest` is Tier-1-by-default and runs under the
  no-filter `all` mode (the canonical green check). Adding it to the `-k` expression
  in `run-tests.sh` line 68 is the General's integration step, not race-edited here
  (per `tests/README.md` § "How `run-tests.sh` picks them up").

## See also

- `skills-bundle/README.md` — the canonical manifest-schema contract
- `skills-bundle/ui-ux-pro-max.md` — the manifest under test
- `scripts/install-skills.sh` — the read-only install substrate the manifest must agree with
- `tests/README.md` § "Phase 5 test conventions" — where this subdir fits
