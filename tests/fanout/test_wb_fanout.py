"""
tests/fanout/test_wb_fanout.py — unit tests for the parallel-research fan-out
substrate (Wave 3b — DESIGN-orchestration-spine.md § 8, gap #8).

Validates scripts/wb_fanout.py:
  - build_run()         — a research brief → N per-subject sub-agent specs (pure core)
  - render_spawn_recipe() — the markdown the in-session agent executes (Agent + TaskCreate)
  - record_run()/_load_runs() — the .website-builder/tasks.yaml fan-out ledger,
    round-trip-preserving (never clobbers the agent's phase-progress mirror)
  - aggregate_results() — N structured sub-agent results → a synthesis (matrix + gaps)
  - run()               — the `wb fanout` verb dispatch (decompose | aggregate | status)
  - dispatch routing    — `wb fanout ...` → wb_fanout.run via scripts/wb.py

All tests are Tier 1 (mirror the Phase-5 convention in tests/README.md): pure
input→output over tmp_path project roots, no network / external tools / live agents.
The Agent/TaskCreate spawn itself is the in-session agent's job (a script cannot call
those tools); these tests cover everything the helper deterministically owns.

project_root is always passed in (per the scripts/README.md interface contract), so
tests hand a tmp_path dir rather than relying on cwd. No committed `.website-builder/`
fixture is needed (and none is added — `.website-builder/` is gitignored at the repo
root and read-only for this Captain): every test writes into its own tmp_path.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

# --- Locate the plugin + make scripts/ importable ---------------------------

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import wb_fanout  # noqa: E402
import wb  # noqa: E402  (the dispatcher — for routing tests)


FIXED_NOW = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
EXPECTED_RUN_ID = "fanout-p3-20260102T030405Z"


def _competitor_brief() -> dict:
    return {
        "phase": 3,
        "topic": "Competitor scan for positioning",
        "subjects": ["competitor-a.com", "competitor-b.com", "competitor-c.com"],
        "dimensions": ["positioning", "pricing", "gtm"],
        "synthesis_goal": "A positioning matrix the user can react to",
    }


def _competitor_results() -> list[wb_fanout.SubjectResult]:
    return [
        wb_fanout.SubjectResult(
            subject="competitor-a.com",
            findings={
                "positioning": "Premium generalist; named enterprise clients",
                "pricing": "Quote-only; no public pricing",
                "gtm": "Outbound sales + referrals",
            },
            notes="Strong brand, opaque pricing",
        ),
        wb_fanout.SubjectResult(
            subject="competitor-b.com",
            findings={
                "positioning": "Productized templates at a fixed price",
                "pricing": "Transparent tiers from $49/mo",
                "gtm": "SEO + content-led inbound",
            },
        ),
        wb_fanout.SubjectResult(
            subject="competitor-c.com",
            findings={
                "positioning": "Boutique editorial studio",
                # pricing intentionally absent → coverage gap
                "gtm": "Word of mouth",
            },
        ),
    ]


# --- Import safety ----------------------------------------------------------


class TestWbFanoutImportSafety:
    """The interface contract requires the module to be import-safe."""

    def test_import_is_side_effect_free(self):
        # The top-level `import wb_fanout` already happened with no error; assert the
        # public surface exists (the cheapest import-safety regression guard).
        for name in ("build_run", "render_spawn_recipe", "aggregate_results",
                     "record_run", "run", "main"):
            assert hasattr(wb_fanout, name), f"missing public symbol {name}"


# --- build_run (decompose core) ---------------------------------------------


class TestBuildRun:
    """A seeded brief → the expected per-subject specs (pure, no I/O)."""

    def test_seeded_brief_produces_expected_specs(self):
        run = wb_fanout.build_run(_competitor_brief(), now=FIXED_NOW)
        assert run.run_id == EXPECTED_RUN_ID
        assert run.phase == 3
        assert run.status == "decomposed"
        assert run.dimensions == ["positioning", "pricing", "gtm"]
        # One task per subject, in order.
        assert [t.subject for t in run.tasks] == [
            "competitor-a.com", "competitor-b.com", "competitor-c.com"
        ]
        assert [t.task_id for t in run.tasks] == [
            f"{EXPECTED_RUN_ID}-01", f"{EXPECTED_RUN_ID}-02", f"{EXPECTED_RUN_ID}-03"
        ]
        # Each spec names its subject + every dimension, and asks for a YAML return.
        for t in run.tasks:
            assert t.subject in t.spec
            for dim in run.dimensions:
                assert dim in t.spec
            assert "```yaml" in t.spec
            assert t.status == "pending"
            assert t.agent_task_ref is None

    def test_run_id_is_deterministic_with_fixed_now(self):
        a = wb_fanout.build_run(_competitor_brief(), now=FIXED_NOW)
        b = wb_fanout.build_run(_competitor_brief(), now=FIXED_NOW)
        assert a.run_id == b.run_id == EXPECTED_RUN_ID

    def test_comma_string_subjects_and_dimensions(self):
        brief = {
            "phase": 2,
            "subjects": "x.com, y.com , z.com",
            "dimensions": "palette, typography",
        }
        run = wb_fanout.build_run(brief, now=FIXED_NOW)
        assert [t.subject for t in run.tasks] == ["x.com", "y.com", "z.com"]
        assert run.dimensions == ["palette", "typography"]

    def test_no_dimensions_spec_uses_summary(self):
        brief = {"phase": 2, "subjects": ["one.com"]}
        run = wb_fanout.build_run(brief, now=FIXED_NOW)
        assert run.dimensions == []
        assert "summary" in run.tasks[0].spec

    def test_agent_type_default_and_override(self):
        default = wb_fanout.build_run({"phase": 3, "subjects": ["a"]}, now=FIXED_NOW)
        assert default.agent_type == wb_fanout.DEFAULT_AGENT_TYPE
        custom = wb_fanout.build_run(
            {"phase": 3, "subjects": ["a"], "agent_type": "general-purpose"}, now=FIXED_NOW
        )
        assert custom.agent_type == "general-purpose"

    def test_missing_phase_raises(self):
        with pytest.raises(wb_fanout.BriefError):
            wb_fanout.build_run({"subjects": ["a.com"]})

    def test_missing_subjects_raises(self):
        with pytest.raises(wb_fanout.BriefError):
            wb_fanout.build_run({"phase": 3})

    def test_non_mapping_brief_raises(self):
        with pytest.raises(wb_fanout.BriefError):
            wb_fanout.build_run(["not", "a", "dict"])  # type: ignore[arg-type]


# --- spawn-recipe render ----------------------------------------------------


class TestSpawnRecipe:
    """The emitted recipe carries the parts the agent must execute + the doctrine."""

    def test_recipe_contains_subjects_calls_and_aggregate(self):
        run = wb_fanout.build_run(_competitor_brief(), now=FIXED_NOW)
        recipe = wb_fanout.render_spawn_recipe(run)
        # Every subject + its spec appears.
        for t in run.tasks:
            assert t.subject in recipe
            assert t.task_id in recipe
        # The parts only the agent can do are named.
        assert "Agent(subagent_type=" in recipe
        assert "TaskCreate(" in recipe
        # The follow-up command + the run id.
        assert "wb fanout aggregate" in recipe
        assert run.run_id in recipe
        # The load-bearing doctrine is restated.
        assert "in-person" in recipe.lower()

    def test_recipe_includes_results_schema(self):
        run = wb_fanout.build_run(_competitor_brief(), now=FIXED_NOW)
        recipe = wb_fanout.render_spawn_recipe(run)
        assert "results:" in recipe
        # The results schema lists each subject under the results block.
        assert "subject: competitor-a.com" in recipe


# --- ledger round-trip ------------------------------------------------------


class TestLedger:
    """The .website-builder/tasks.yaml fan-out ledger round-trips + preserves siblings."""

    def test_record_and_load_round_trip(self, tmp_path: Path):
        run = wb_fanout.build_run(_competitor_brief(), now=FIXED_NOW)
        wb_fanout.record_run(tmp_path, run)
        loaded = wb_fanout._load_runs(tmp_path)
        assert len(loaded) == 1
        got = loaded[0]
        assert got.run_id == run.run_id
        assert got.phase == run.phase
        assert got.dimensions == run.dimensions
        assert [t.subject for t in got.tasks] == [t.subject for t in run.tasks]
        # The spec (a multi-line block scalar) survives the YAML round-trip verbatim.
        assert got.tasks[0].spec == run.tasks[0].spec

    def test_ledger_preserves_non_fanout_keys(self, tmp_path: Path):
        # Seed tasks.yaml with the agent's phase-progress mirror BEFORE fanout writes.
        import yaml
        state = tmp_path / wb_fanout.STATE_DIR_NAME
        state.mkdir(parents=True)
        (state / wb_fanout.TASKS_YAML_NAME).write_text(
            yaml.safe_dump({"phases": {"current": 3, "log": ["did phase 2"]}}),
            encoding="utf-8",
        )
        run = wb_fanout.build_run(_competitor_brief(), now=FIXED_NOW)
        wb_fanout.record_run(tmp_path, run)
        doc = wb_fanout._load_tasks_doc(tmp_path)
        # Both the pre-existing key AND the new fanout subtree survive.
        assert doc["phases"]["current"] == 3
        assert doc["phases"]["log"] == ["did phase 2"]
        assert wb_fanout.LEDGER_KEY in doc
        assert doc[wb_fanout.LEDGER_KEY]["runs"][0]["run_id"] == run.run_id

    def test_record_run_idempotent_replace(self, tmp_path: Path):
        run = wb_fanout.build_run(_competitor_brief(), now=FIXED_NOW)
        wb_fanout.record_run(tmp_path, run)
        # Re-record the same run id (e.g. after an aggregate status flip).
        run.status = "aggregated"
        wb_fanout.record_run(tmp_path, run)
        loaded = wb_fanout._load_runs(tmp_path)
        assert len(loaded) == 1  # replaced, not duplicated
        assert loaded[0].status == "aggregated"


# --- aggregate core ---------------------------------------------------------


class TestAggregate:
    """Structured results → synthesis (matrix + per-dimension cross-cut + gaps)."""

    def test_builds_matrix_and_flags_gap(self):
        run = wb_fanout.build_run(_competitor_brief(), now=FIXED_NOW)
        synthesis = wb_fanout.aggregate_results(
            run, _competitor_results(), now=FIXED_NOW
        )
        assert synthesis.dimensions == ["positioning", "pricing", "gtm"]
        rendered = synthesis.render()
        # Matrix header carries the dimensions.
        assert "| Subject | positioning | pricing | gtm |" in rendered
        # Every subject + a sample finding appear.
        assert "competitor-a.com" in rendered
        assert "Transparent tiers from $49/mo" in rendered
        # The missing pricing cell for c.com is flagged as a coverage gap.
        assert any("competitor-c.com" in g and "pricing" in g for g in synthesis.gaps)
        assert "Coverage gaps" in rendered
        # The optional note surfaces.
        assert "Strong brand, opaque pricing" in rendered

    def test_no_gaps_when_full_coverage(self):
        run = wb_fanout.build_run(_competitor_brief(), now=FIXED_NOW)
        results = _competitor_results()
        results[2].findings["pricing"] = "Project-based; from $5k"  # fill the gap
        synthesis = wb_fanout.aggregate_results(run, results, now=FIXED_NOW)
        assert synthesis.gaps == []
        assert "every subject covered every declared dimension" in synthesis.render()

    def test_union_dimensions_without_run(self):
        # No run record → dimensions derived from the union of findings keys (ordered).
        synthesis = wb_fanout.aggregate_results(
            None, _competitor_results(), now=FIXED_NOW
        )
        assert synthesis.dimensions == ["positioning", "pricing", "gtm"]
        assert synthesis.run_id == "fanout-adhoc"

    def test_explicit_dimensions_override(self):
        synthesis = wb_fanout.aggregate_results(
            None, _competitor_results(), dimensions=["pricing"], now=FIXED_NOW
        )
        assert synthesis.dimensions == ["pricing"]

    def test_dimension_with_no_findings_flagged(self):
        results = [
            wb_fanout.SubjectResult(subject="a", findings={"x": "found"}),
            wb_fanout.SubjectResult(subject="b", findings={"x": "found"}),
        ]
        synthesis = wb_fanout.aggregate_results(
            None, results, dimensions=["x", "y"], now=FIXED_NOW
        )
        assert any("`y`" in g and "no subject" in g for g in synthesis.gaps)

    def test_empty_results_raises(self):
        with pytest.raises(wb_fanout.ResultsError):
            wb_fanout.aggregate_results(None, [], now=FIXED_NOW)

    def test_subjectresult_missing_subject_raises(self):
        with pytest.raises(wb_fanout.ResultsError):
            wb_fanout.SubjectResult.from_dict({"findings": {"x": "y"}})

    def test_subjectresult_non_mapping_findings_raises(self):
        with pytest.raises(wb_fanout.ResultsError):
            wb_fanout.SubjectResult.from_dict({"subject": "a", "findings": ["x"]})


# --- CLI (run + project_root) -----------------------------------------------


class TestCli:
    """The `wb fanout` verb dispatch over a tmp_path project root."""

    def test_decompose_writes_ledger_and_prints_recipe(self, tmp_path, capsys):
        rc = wb_fanout.run(
            ["decompose", "--phase", "3",
             "--topic", "Competitor scan",
             "--subjects", "a.com,b.com,c.com",
             "--dimensions", "positioning,pricing,gtm"],
            project_root=tmp_path,
        )
        assert rc == 0
        ledger = tmp_path / ".website-builder" / "tasks.yaml"
        assert ledger.is_file()
        out = capsys.readouterr().out
        assert "Parallel research fan-out" in out
        assert "wb fanout aggregate" in out
        # The ledger has exactly one run with 3 tasks.
        runs = wb_fanout._load_runs(tmp_path)
        assert len(runs) == 1 and len(runs[0].tasks) == 3

    def test_aggregate_writes_synthesis_and_updates_ledger(self, tmp_path, capsys):
        import yaml
        # decompose first so the run is in the ledger.
        wb_fanout.run(
            ["decompose", "--phase", "3", "--topic", "Competitor scan",
             "--subjects", "competitor-a.com,competitor-b.com,competitor-c.com",
             "--dimensions", "positioning,pricing,gtm"],
            project_root=tmp_path,
        )
        capsys.readouterr()  # drain
        run_id = wb_fanout._load_runs(tmp_path)[0].run_id
        # Assemble a results file the way the agent would.
        results_file = tmp_path / "results.yaml"
        results_file.write_text(
            yaml.safe_dump({
                "results": [
                    {"subject": "competitor-a.com",
                     "findings": {"positioning": "premium", "pricing": "quote-only",
                                  "gtm": "outbound"}},
                    {"subject": "competitor-b.com",
                     "findings": {"positioning": "productized", "pricing": "$49/mo",
                                  "gtm": "inbound"}},
                    {"subject": "competitor-c.com",
                     "findings": {"positioning": "boutique", "gtm": "word of mouth"}},
                ]
            }),
            encoding="utf-8",
        )
        rc = wb_fanout.run(
            ["aggregate", "--run", run_id, "--results", str(results_file)],
            project_root=tmp_path,
        )
        assert rc == 0
        synthesis = tmp_path / ".website-builder" / "library" / f"{run_id}-synthesis.md"
        assert synthesis.is_file()
        body = synthesis.read_text(encoding="utf-8")
        assert "Comparison matrix" in body
        assert "Coverage gaps" in body
        # The ledger run flipped to aggregated + every task is done.
        run = wb_fanout._load_runs(tmp_path)[0]
        assert run.status == "aggregated"
        assert run.synthesis_path is not None
        assert all(t.status == "done" for t in run.tasks)

    def test_aggregate_defaults_to_latest_run(self, tmp_path):
        import yaml
        wb_fanout.run(["decompose", "--phase", "3", "--subjects", "a,b",
                       "--dimensions", "x"], project_root=tmp_path)
        results_file = tmp_path / "r.yaml"
        results_file.write_text(
            yaml.safe_dump({"results": [
                {"subject": "a", "findings": {"x": "ax"}},
                {"subject": "b", "findings": {"x": "bx"}},
            ]}),
            encoding="utf-8",
        )
        # No --run → defaults to the most-recent run.
        rc = wb_fanout.run(["aggregate", "--results", str(results_file)],
                           project_root=tmp_path)
        assert rc == 0

    def test_status_lists_runs(self, tmp_path, capsys):
        wb_fanout.run(["decompose", "--phase", "3", "--subjects", "a.com,b.com",
                       "--dimensions", "x"], project_root=tmp_path)
        capsys.readouterr()
        rc = wb_fanout.run(["status"], project_root=tmp_path)
        assert rc == 0
        out = capsys.readouterr().out
        assert "phase 3" in out
        assert "a.com" in out and "b.com" in out

    def test_status_empty_ledger(self, tmp_path, capsys):
        rc = wb_fanout.run(["status"], project_root=tmp_path)
        assert rc == 0
        assert "No fan-out runs recorded." in capsys.readouterr().out

    def test_no_args_returns_2(self, tmp_path):
        assert wb_fanout.run([], project_root=tmp_path) == 2

    def test_unknown_verb_returns_2(self, tmp_path):
        assert wb_fanout.run(["bogus"], project_root=tmp_path) == 2

    def test_decompose_missing_phase_returns_1(self, tmp_path):
        # A FanoutError (BriefError) surfaces as exit 1 via run()'s handler.
        assert wb_fanout.run(["decompose", "--subjects", "a"],
                             project_root=tmp_path) == 1

    def test_aggregate_missing_results_file_returns_1(self, tmp_path):
        assert wb_fanout.run(
            ["aggregate", "--results", str(tmp_path / "nope.yaml")],
            project_root=tmp_path,
        ) == 1


# --- dispatch routing (via scripts/wb.py) -----------------------------------


class TestDispatch:
    """`wb fanout ...` routes through the real dispatcher to wb_fanout.run."""

    def test_wb_routes_fanout_status(self, tmp_path):
        rc = wb.main(["--project-dir", str(tmp_path), "fanout", "status"])
        assert rc == 0

    def test_wb_routes_fanout_decompose_end_to_end(self, tmp_path):
        rc = wb.main(["--project-dir", str(tmp_path), "fanout", "decompose",
                      "--phase", "3", "--subjects", "a.com,b.com", "--dimensions", "x"])
        assert rc == 0
        # Proves the argv passed through the dispatcher to the verb handler.
        assert (tmp_path / ".website-builder" / "tasks.yaml").is_file()
        assert len(wb_fanout._load_runs(tmp_path)[0].tasks) == 2

    def test_wb_routes_fanout_unknown_verb_returns_2(self, tmp_path):
        rc = wb.main(["--project-dir", str(tmp_path), "fanout", "bogus-verb"])
        assert rc == 2
