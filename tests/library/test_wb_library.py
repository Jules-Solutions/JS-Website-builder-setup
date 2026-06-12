"""
Tier-1 unit tests for the resource-curation library module + auto-clone runtime
(`scripts/wb_library.py`). Phase 5 / Captain P scope.

No network, no external tools — pure input->output over a synthetic
`.website-builder/` fixture copied into pytest's `tmp_path`. Mirrors
`smoke_test.py`'s tempdir + cwd-via-contract pattern, except `project_root` is
passed in explicitly (per `scripts/README.md` § Interface rules) so no `cwd`
mutation is needed.

Run:
  bash tests/run-tests.sh
  cd tests && uv run --with pyyaml --with pytest pytest library/ -v
"""

from __future__ import annotations

import importlib
import shutil
import sys
from pathlib import Path

import pytest

# Make scripts/wb_library.py importable regardless of pytest's cwd.
PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import wb_library as wl  # noqa: E402  (sys.path mutation must precede)

FIXTURE_DIR = Path(__file__).resolve().parent / "fixture"


# --- Fixtures --------------------------------------------------------------


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    """A throwaway copy of the synthetic .website-builder/ fixture under tmp_path."""
    src = FIXTURE_DIR / ".website-builder"
    assert src.is_dir(), f"missing fixture at {src}"
    dst = tmp_path / ".website-builder"
    shutil.copytree(src, dst)
    return tmp_path


def _read_project_yaml_text(project_root: Path) -> str:
    return (project_root / ".website-builder" / "project.yaml").read_text(encoding="utf-8")


def _set_project_yaml(project_root: Path, text: str) -> None:
    (project_root / ".website-builder" / "project.yaml").write_text(text, encoding="utf-8")


# --- Import safety ---------------------------------------------------------


class TestImportSafety:
    """The interface contract requires the module to be import-safe."""

    def test_import_is_side_effect_free(self):
        # Re-importing must not raise and must not create files. The module was
        # already imported at collection time; re-importing is the regression guard.
        mod = importlib.reload(wl)
        assert hasattr(mod, "run")
        assert hasattr(mod, "autoclone_for_state")

    def test_public_surface_matches_contract(self):
        import inspect

        run_sig = inspect.signature(wl.run)
        assert list(run_sig.parameters) == ["argv", "project_root"]
        assert run_sig.parameters["project_root"].kind == inspect.Parameter.KEYWORD_ONLY

        ac_sig = inspect.signature(wl.autoclone_for_state)
        params = list(ac_sig.parameters)
        assert params[0] == "project_root"
        assert "trigger" in params and "phase" in params
        assert ac_sig.parameters["trigger"].kind == inspect.Parameter.KEYWORD_ONLY

    def test_valid_verbs_exact(self):
        assert wl.VALID_VERBS == (
            "list", "add", "remove", "refresh", "refresh-all", "prune", "inspect",
        )


# --- CLI verbs -------------------------------------------------------------


class TestWbLibraryVerbs:
    def test_list_empty(self, project_root: Path, capsys):
        rc = wl.run(["list"], project_root=project_root)
        assert rc == 0
        assert "empty" in capsys.readouterr().out.lower()

    def test_add_then_list(self, project_root: Path, capsys):
        rc = wl.run(["add", "https://docs.stripe.com/payments/checkout"],
                    project_root=project_root)
        assert rc == 0
        capsys.readouterr()
        rc = wl.run(["list"], project_root=project_root)
        assert rc == 0
        out = capsys.readouterr().out
        assert "checkout" in out

    def test_add_is_idempotent(self, project_root: Path, capsys):
        wl.run(["add", "https://example.com/docs/widget"], project_root=project_root)
        capsys.readouterr()
        rc = wl.run(["add", "https://example.com/docs/widget"], project_root=project_root)
        assert rc == 0
        assert "already in the library" in capsys.readouterr().out
        # Still exactly one entry.
        assert len(wl._read_registry(project_root)) == 1

    def test_add_with_tag_and_as(self, project_root: Path, capsys):
        rc = wl.run(
            ["add", "https://example.com/guide", "--as", "guides", "--tag", "ref"],
            project_root=project_root,
        )
        assert rc == 0
        entry = wl._read_registry(project_root)[0]
        assert entry.subdir == "guides"
        assert entry.tags == ["ref"]

    def test_remove(self, project_root: Path, capsys):
        wl.run(["add", "https://example.com/docs/thing"], project_root=project_root)
        capsys.readouterr()
        rc = wl.run(["remove", "thing"], project_root=project_root)
        assert rc == 0
        assert wl._read_registry(project_root) == []

    def test_remove_missing_is_error(self, project_root: Path, capsys):
        rc = wl.run(["remove", "nonexistent"], project_root=project_root)
        assert rc == 1

    def test_remove_keep_files(self, project_root: Path, capsys):
        # Add an entry, drop a marker file in its subdir, remove --keep-files,
        # confirm dir survives.
        wl.run(["add", "https://example.com/guide", "--as", "kept"],
               project_root=project_root)
        kept = project_root / ".website-builder" / "library" / "kept"
        kept.mkdir(parents=True, exist_ok=True)
        (kept / "marker.txt").write_text("x", encoding="utf-8")
        capsys.readouterr()
        rc = wl.run(["remove", "guide", "--keep-files"], project_root=project_root)
        assert rc == 0
        assert (kept / "marker.txt").exists()  # files kept
        assert wl._read_registry(project_root) == []  # but deregistered

    def test_inspect(self, project_root: Path, capsys):
        wl.run(["add", "https://docs.stripe.com/payments/checkout"],
               project_root=project_root)
        capsys.readouterr()
        rc = wl.run(["inspect", "checkout"], project_root=project_root)
        assert rc == 0
        out = capsys.readouterr().out
        assert "source:" in out and "stripe.com" in out

    def test_refresh_missing_is_error(self, project_root: Path):
        assert wl.run(["refresh", "nope"], project_root=project_root) == 1

    def test_refresh_all_empty_ok(self, project_root: Path, capsys):
        assert wl.run(["refresh-all"], project_root=project_root) == 0
        assert "nothing to refresh" in capsys.readouterr().out

    def test_prune_lists_unreferenced(self, project_root: Path, capsys):
        # Add an arbitrary resource not referenced by project state.
        wl.run(["add", "https://example.com/random"], project_root=project_root)
        capsys.readouterr()
        rc = wl.run(["prune"], project_root=project_root)
        assert rc == 0
        out = capsys.readouterr().out
        assert "random" in out
        assert "No files deleted" in out  # safe non-destructive default

    def test_no_verb_prints_help(self, project_root: Path):
        assert wl.run([], project_root=project_root) == 2


# --- Provenance registry ---------------------------------------------------


class TestProvenanceRegistry:
    def test_readme_created_on_add(self, project_root: Path):
        wl.run(["add", "https://example.com/docs/x"], project_root=project_root)
        readme = project_root / ".website-builder" / "library" / "README.md"
        assert readme.is_file()
        text = readme.read_text(encoding="utf-8")
        assert wl.REGISTRY_FENCE in text  # machine block present

    def test_registry_round_trips(self, project_root: Path):
        wl.run(["add", "https://example.com/a", "--tag", "t1"], project_root=project_root)
        wl.run(["add", "https://github.com/org/repo"], project_root=project_root)
        entries = wl._read_registry(project_root)
        names = {e.name for e in entries}
        assert "a" in names and "repo" in names
        a = wl._find_entry(entries, "a")
        assert a is not None and a.tags == ["t1"]

    def test_add_inspect_subdir_consistent(self, project_root: Path, capsys):
        # add places a web-page under library/docs; inspect must report the SAME subdir.
        wl.run(["add", "https://docs.stripe.com/payments/checkout"],
               project_root=project_root)
        entry = wl._read_registry(project_root)[0]
        capsys.readouterr()
        wl.run(["inspect", "checkout"], project_root=project_root)
        out = capsys.readouterr().out
        assert f"library/{entry.subdir}" in out


# --- Auto-clone: session-start ---------------------------------------------


class TestAutocloneSessionStart:
    def test_derives_candidates_from_picked_fields(self, project_root: Path):
        # fixture project.yaml: astro + shadcn + transactional + stripe.
        results = wl.autoclone_for_state(project_root, trigger="session-start")
        resources = {r.resource for r in results}
        assert "astro-content-collections" in resources  # astro stack
        assert "shadcn-components" in resources           # shadcn component lib
        assert "stripe-checkout" in resources             # transactional + stripe

    def test_returns_cloneresult_objects(self, project_root: Path):
        results = wl.autoclone_for_state(project_root, trigger="session-start")
        assert results and all(isinstance(r, wl.CloneResult) for r in results)
        # Non-git docs resources are fetch-deferred (not blocked on network).
        assert all(r.status in ("fetch-deferred", "skipped") for r in results)

    def test_empty_project_yaml_no_candidates(self, project_root: Path):
        _set_project_yaml(project_root, "version: 1\n")
        results = wl.autoclone_for_state(project_root, trigger="session-start")
        assert results == []


# --- Auto-clone: phase-entry -----------------------------------------------


class TestAutoclonePhaseEntry:
    def test_reads_clones_at_entry_from_contract(self, project_root: Path):
        results = wl.autoclone_for_state(project_root, trigger="phase-entry", phase=17)
        resources = {r.resource for r in results}
        # awesome-design-md is unconditional; shadcn + stripe are when-gated and
        # the fixture project.yaml satisfies both gates.
        assert "awesome-design-md" in resources
        assert "shadcn-components" in resources
        assert "stripe-checkout" in resources

    def test_when_predicate_gates_clone(self, project_root: Path):
        # Flip component_library away from shadcn → the shadcn clone is skipped.
        text = _read_project_yaml_text(project_root).replace(
            'component_library: "shadcn"', 'component_library: "daisyui"'
        )
        _set_project_yaml(project_root, text)
        results = wl.autoclone_for_state(project_root, trigger="phase-entry", phase=17)
        by_resource = {r.resource: r for r in results}
        assert by_resource["shadcn-components"].status == "skipped"
        assert "when-predicate" in by_resource["shadcn-components"].reason
        # awesome-design-md is unconditional → still queued.
        assert by_resource["awesome-design-md"].status == "fetch-deferred"

    def test_idempotent_skips_present(self, project_root: Path):
        # Pre-register awesome-design-md so the runtime sees it as present.
        wl.run(["add", "https://github.com/VoltAgent/awesome-design-md",
                "--as", "awesome-design-md"], project_root=project_root)
        results = wl.autoclone_for_state(project_root, trigger="phase-entry", phase=17)
        by_resource = {r.resource: r for r in results}
        assert by_resource["awesome-design-md"].status == "skipped"
        assert "already present" in by_resource["awesome-design-md"].reason


# --- Defensive read --------------------------------------------------------


class TestDefensiveRead:
    def test_missing_contract_returns_empty(self, project_root: Path):
        # No phase-99 contract exists → [] (no error).
        assert wl.autoclone_for_state(project_root, trigger="phase-entry", phase=99) == []

    def test_unknown_trigger_returns_empty(self, project_root: Path):
        assert wl.autoclone_for_state(project_root, trigger="bogus") == []

    def test_phase_entry_without_phase_returns_empty(self, project_root: Path):
        assert wl.autoclone_for_state(project_root, trigger="phase-entry", phase=None) == []

    def test_contract_without_field_returns_empty(self, project_root: Path):
        # Drop a phase-20 contract that omits library_clones_at_entry entirely.
        contracts = project_root / ".website-builder" / "phase-contracts"
        (contracts / "20-build.md").write_text(
            "---\nphase: 20\ngroup: build\n---\n\n# Phase 20 — Build\n",
            encoding="utf-8",
        )
        assert wl.autoclone_for_state(project_root, trigger="phase-entry", phase=20) == []

    def test_malformed_frontmatter_returns_empty(self, project_root: Path):
        contracts = project_root / ".website-builder" / "phase-contracts"
        # Frontmatter that is not a mapping / not valid YAML for the field.
        (contracts / "21-x.md").write_text(
            "---\nthis: [is, : broken yaml\n---\nbody\n", encoding="utf-8"
        )
        # Must not raise; returns [].
        assert wl.autoclone_for_state(project_root, trigger="phase-entry", phase=21) == []

    def test_missing_project_yaml_no_crash(self, tmp_path: Path):
        # No .website-builder/ at all → session-start yields [], no crash.
        assert wl.autoclone_for_state(tmp_path, trigger="session-start") == []


# --- when: predicate grammar -----------------------------------------------


class TestWhenPredicate:
    PROJECT = {
        "stack": "astro",
        "cms": "none",
        "transactional": True,
        "component_library": "shadcn",
        "component_library_composition": {"primary": "shadcn"},
    }

    def test_equality_true(self):
        assert wl._evaluate_when('stack == "astro"', self.PROJECT) is True

    def test_equality_false(self):
        assert wl._evaluate_when('stack == "nextjs"', self.PROJECT) is False

    def test_inequality(self):
        assert wl._evaluate_when("cms != none", self.PROJECT) is False
        assert wl._evaluate_when("cms != payload", self.PROJECT) is True

    def test_bare_key_truthiness(self):
        assert wl._evaluate_when("transactional", self.PROJECT) is True
        assert wl._evaluate_when("nonexistent", self.PROJECT) is False

    def test_dotted_key(self):
        assert wl._evaluate_when(
            'component_library_composition.primary == "shadcn"', self.PROJECT
        ) is True

    def test_absent_key_is_falsy(self):
        assert wl._evaluate_when('missing == "x"', self.PROJECT) is False

    def test_empty_predicate_is_true(self):
        assert wl._evaluate_when(None, self.PROJECT) is True
        assert wl._evaluate_when("", self.PROJECT) is True

    def test_unparseable_predicate_raises(self):
        with pytest.raises(ValueError):
            wl._evaluate_when("this is not a predicate !! @@", self.PROJECT)

    def test_bool_value_coercion(self):
        assert wl._evaluate_when("transactional == true", self.PROJECT) is True
        assert wl._evaluate_when("transactional == false", self.PROJECT) is False
