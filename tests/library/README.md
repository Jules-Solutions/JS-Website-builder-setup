# `tests/library/` — Captain P test zone (Phase 5)

Executable unit tests for the resource-curation library module + auto-clone
runtime (`scripts/wb_library.py`). Owned by Phase 5 Captain P.

Per `tests/README.md` § Phase 5 test conventions + `scripts/README.md`
§ Module boundary.

## What's here

```
tests/library/
├── README.md                # this file
├── test_wb_library.py       # Tier-1 unit tests (no network, no external tools)
└── fixture/
    └── .website-builder/
        ├── project.yaml      # synthetic project state (astro + shadcn + transactional)
        ├── library/.gitkeep  # empty library dir the module populates
        └── phase-contracts/
            └── 17-design-system.md   # the library_clones_at_entry working example
```

## What's tested (Tier 1 — always green when code + fixture align)

| Class | Coverage |
|---|---|
| `TestImportSafety` | `import wb_library` succeeds with zero side effects (no files written, no network). The cheapest regression guard for the import-safe interface rule. |
| `TestWbLibraryVerbs` | All 7 verbs dispatch through `run()`: list / add / remove / refresh / refresh-all / prune / inspect. Add registers an entry; remove deregisters; idempotent re-add; `--keep-files`; `--tag`. |
| `TestProvenanceRegistry` | `library/README.md` is created + round-trips entries (machine block parse/emit), `add`→`list`→`inspect`→`remove` stay consistent on the same subdir. |
| `TestAutocloneSessionStart` | `autoclone_for_state(trigger="session-start")` derives candidates from picked project.yaml fields (astro→astro docs, shadcn→shadcn docs, transactional+stripe→stripe docs). |
| `TestAutoclonePhaseEntry` | `autoclone_for_state(trigger="phase-entry", phase=17)` reads `library_clones_at_entry` from the fixture contract; honours `when:` predicates; idempotent (already-present → skipped). |
| `TestDefensiveRead` | Absent `library_clones_at_entry` field → `[]`. Missing contract → `[]`. Unknown trigger → `[]`. Malformed frontmatter → `[]`. None of these raise. |
| `TestWhenPredicate` | `key == value`, `key != value`, bare-key truthiness, dotted keys, absent key falsy, unparseable predicate skips (no crash). |

## Tier 2 (not in this suite)

Real `git clone` of an upstream repo, real WebFetch of a docs page — those touch
the network and are deferred per `tests/README.md` § Phase 5 (the runtime returns
`status="fetch-deferred"` for non-git resources; git resources are cloned only
when `git` is on PATH and the target is writable, which the Tier-1 tests do not
exercise against live remotes).

## Run

```bash
bash tests/run-tests.sh            # full suite (this + Phase 1-4)
cd tests && uv run --with pyyaml --with pytest pytest library/ -v   # just this zone
```
