"""
Wave-5 — exercise the Wave-3b / Wave-4 surfaces end-to-end (Captain verify-1):

  A. Fan-out (Wave 3b) — `wb fanout decompose` + `aggregate` integrate THROUGH the
     `wb` dispatcher (scripts/wb.py), over a seeded brief at an opt-in phase, producing
     per-subject specs (decompose) + a synthesis artifact (aggregate). The wb_fanout
     cores are unit-tested in tests/fanout/; here we confirm the dispatcher wiring.

  B. Bundled-catalogue clone (Wave 4) — `autoclone_for_state(trigger="phase-entry")`
     copies the plugin-bundled `reference-corpus/<slug>` into
     `.website-builder/library/<slug>/` at a phase whose contract carries a
     `library_clones_at_entry` corpus key (02 -> brand-examples/design-systems;
     13 -> component-patterns).

  C. FU-2 ground-truth (reconciled by Decision 91 — "ship the menu, fetch the
     meals", supersedes Decision 88 + the original FU-2 library repoint). Bundled
     corpora (design-systems / brand-examples / component-patterns / seo-checklists)
     are now READ from the guaranteed-present bundled path
     ${CLAUDE_PLUGIN_ROOT}/reference-corpus/<slug>/ — a runtime read-instruction
     (in skills/ or phase-contracts/) points there. awesome-design-md stays a
     genuinely-cloned-at-runtime resource read from .website-builder/library/
     awesome-design-md/ (bundled subset ships as reference-corpus/awesome-design-md-
     corpus/). The Decision-42 autoclone machinery is kept (bundled corpora still
     materialize at library/<slug>/ at phase entry — harmless, now redundant).

Run:
  cd tests && uv run --with pyyaml --with pytest pytest orchestration/test_e2e_surfaces.py -v
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
SKILLS_DIR = PLUGIN_ROOT / "skills"
REFERENCE_CORPUS = PLUGIN_ROOT / "reference-corpus"
sys.path.insert(0, str(SCRIPTS_DIR))

import wb_library  # noqa: E402

GREENFIELD = {
    "stack": "nextjs",
    "cms": "none",
    "component_library": "shadcn",
    "entry_mode": "greenfield",
    "languages": "en",
    "transactional": "false",
}

# The five FU-2 slugs the General repointed (skills reference/<slug>/ -> library/<slug>/).
FU2_SLUGS = ("design-systems", "awesome-design-md", "component-patterns",
             "seo-checklists", "brand-examples")

# Decision 91 (supersedes Decision 88 + the original FU-2 library repoint):
# bundled corpora are READ from ${CLAUDE_PLUGIN_ROOT}/reference-corpus/<slug>/
# (guaranteed present on any install), not from the runtime clone. awesome-design-md
# stays a genuinely-cloned-at-runtime resource (the full VoltAgent corpus, network-
# cloned at phase 17) read from .website-builder/library/awesome-design-md/; its
# bundled 14-exemplar subset ships as reference-corpus/awesome-design-md-corpus/.
BUNDLED_READ_SLUGS = ("design-systems", "brand-examples",
                      "component-patterns", "seo-checklists")
RUNTIME_READ_SLUGS = ("awesome-design-md",)


def _write_project(root: Path, phase: int, **overrides) -> Path:
    fields: dict[str, object] = dict(GREENFIELD)
    fields.update(overrides)
    fields["current_phase"] = phase
    sd = root / ".website-builder"
    sd.mkdir(parents=True, exist_ok=True)
    body = "\n".join(f"{k}: {v}" for k, v in fields.items()) + "\n"
    (sd / "project.yaml").write_text(body, encoding="utf-8")
    return root


def _wb(root: Path, *args: str) -> subprocess.CompletedProcess:
    """Invoke the `wb` dispatcher as a subprocess (cwd = the project root, so
    project_root defaults to it) — the faithful through-the-dispatcher path.

    PYTHONIOENCODING=utf-8 mirrors CC's UTF-8 bash runtime so the dispatcher's
    em-dashes round-trip (the wb CLI prints plain text; on a cp1252-captured pipe
    without this, Windows would mangle non-ASCII — a console-encoding property of
    every wb verb, not a Wave-5 behavior)."""
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "wb.py"), *args],
        cwd=str(root),
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )


def _skills_reference_slug(slug: str) -> list[str]:
    """Skill files that point at `.website-builder/library/<slug>/`."""
    needle = f".website-builder/library/{slug}/"
    hits: list[str] = []
    for md in SKILLS_DIR.rglob("*.md"):
        try:
            if needle in md.read_text(encoding="utf-8"):
                hits.append(md.relative_to(PLUGIN_ROOT).as_posix())
        except OSError:
            continue
    return hits


# The agent's runtime read-instructions live in two surfaces: the phase-group
# skills and the phase contracts. Decision 91 points bundled-corpus reads at the
# bundled path from whichever surface instructs that phase.
READ_INSTRUCTION_DIRS = (SKILLS_DIR, PLUGIN_ROOT / "phase-contracts")


def _files_reference_bundled(slug: str) -> list[str]:
    """Runtime read-instruction files (skills/ or phase-contracts/) that point at
    the guaranteed-present bundled path ${CLAUDE_PLUGIN_ROOT}/reference-corpus/<slug>/."""
    needle = f"reference-corpus/{slug}/"
    hits: list[str] = []
    for base in READ_INSTRUCTION_DIRS:
        for md in base.rglob("*.md"):
            try:
                if needle in md.read_text(encoding="utf-8"):
                    hits.append(md.relative_to(PLUGIN_ROOT).as_posix())
            except OSError:
                continue
    return hits


# --- A. Fan-out through the `wb` dispatcher ----------------------------------


class TestFanoutThroughDispatcher:
    BRIEF = (
        "phase: 2\n"
        "topic: Compare three brand references for visual direction\n"
        "subjects: [stripe, linear, vercel]\n"
        "dimensions: [palette, typography, voice]\n"
        "synthesis_goal: pick one aesthetic direction\n"
    )

    def _results_yaml(self) -> str:
        return (
            "results:\n"
            "  - subject: stripe\n"
            "    findings: {palette: \"cool neutrals\", typography: \"sohne sans\", voice: \"precise\"}\n"
            "  - subject: linear\n"
            "    findings: {palette: \"violet dark\", typography: \"inter\", voice: \"crisp\"}\n"
            "  - subject: vercel\n"
            "    findings: {palette: \"mono black\", typography: \"geist\", voice: \"terse\"}\n"
        )

    def test_decompose_then_aggregate_via_dispatcher(self, tmp_path: Path):
        root = _write_project(tmp_path, 2)
        brief = root / "brief.yaml"
        brief.write_text(self.BRIEF, encoding="utf-8")

        # --- decompose (through `wb fanout`) ---
        dec = _wb(root, "fanout", "decompose", "--brief", str(brief))
        assert dec.returncode == 0, dec.stderr
        # the spawn-recipe (per-subject specs) is on stdout
        assert "Step 1 — spawn the sub-agents" in dec.stdout
        for subj in ("stripe", "linear", "vercel"):
            assert subj in dec.stdout
        # the ledger was written into .website-builder/tasks.yaml by the dispatcher
        assert (root / ".website-builder" / "tasks.yaml").is_file()

        run_id_match = re.search(r"fanout-p\d+-\d{8}T\d{6}Z", dec.stdout)
        assert run_id_match, "could not find a run_id in the decompose output"
        run_id = run_id_match.group(0)

        # --- aggregate (through `wb fanout`) ---
        results = root / "results.yaml"
        results.write_text(self._results_yaml(), encoding="utf-8")
        agg = _wb(root, "fanout", "aggregate", "--run", run_id, "--results", str(results))
        assert agg.returncode == 0, agg.stderr

        # synthesis artifact landed under .website-builder/library/
        synth = root / ".website-builder" / "library" / f"{run_id}-synthesis.md"
        assert synth.is_file(), "aggregate did not write the synthesis artifact"
        text = synth.read_text(encoding="utf-8")
        assert "## Comparison matrix" in text
        assert "## By dimension" in text
        for subj in ("stripe", "linear", "vercel"):
            assert subj in text
        for dim in ("palette", "typography", "voice"):
            assert dim in text

    def test_status_verb_lists_the_run(self, tmp_path: Path):
        root = _write_project(tmp_path, 2)
        brief = root / "brief.yaml"
        brief.write_text(self.BRIEF, encoding="utf-8")
        assert _wb(root, "fanout", "decompose", "--brief", str(brief)).returncode == 0
        st = _wb(root, "fanout", "status")
        assert st.returncode == 0
        assert "phase 2" in st.stdout
        assert "stripe" in st.stdout and "linear" in st.stdout


# --- B. Bundled-catalogue clone (phase-entry trigger) ------------------------


class TestBundledCatalogueClone:
    @pytest.mark.parametrize(
        "phase,slugs,corpus_keys",
        [
            (2, ("brand-examples", "design-systems"),
             ("brand-examples-corpus", "design-systems-corpus")),
            (13, ("component-patterns",), ("component-patterns",)),
        ],
    )
    def test_phase_entry_copies_bundled_corpus(self, tmp_path, phase, slugs, corpus_keys):
        root = _write_project(tmp_path, phase)
        results = wb_library.autoclone_for_state(root, trigger="phase-entry", phase=phase)
        resources = {getattr(r, "resource", None) for r in results}
        for key in corpus_keys:
            assert key in resources, f"phase {phase} did not consider {key}"
            res = next(r for r in results if getattr(r, "resource", None) == key)
            assert res.status == "cloned", f"{key} status was {res.status}, expected cloned"

        lib = root / ".website-builder" / "library"
        for slug in slugs:
            target = lib / slug
            assert target.is_dir(), f"bundled corpus not copied to library/{slug}/"
            # content parity: the copied corpus carries the plugin's shipped files.
            shipped = {p.name for p in (REFERENCE_CORPUS / _corpus_dirname(slug)).iterdir()}
            copied = {p.name for p in target.iterdir()}
            assert shipped <= copied, f"library/{slug}/ missing files from the shipped corpus"

    def test_phase_entry_is_idempotent_on_disk(self, tmp_path: Path):
        root = _write_project(tmp_path, 2)
        wb_library.autoclone_for_state(root, trigger="phase-entry", phase=2)
        # second fire → already-on-disk → skipped, never re-copies / crashes.
        again = wb_library.autoclone_for_state(root, trigger="phase-entry", phase=2)
        for r in again:
            if getattr(r, "resource", None) in ("brand-examples-corpus", "design-systems-corpus"):
                assert r.status == "skipped"


def _corpus_dirname(slug: str) -> str:
    """Map a library subdir slug back to its shipped reference-corpus dir name."""
    # awesome-design-md ships under reference-corpus/awesome-design-md-corpus; the
    # bundled corpora otherwise share the slug name.
    return "awesome-design-md-corpus" if slug == "awesome-design-md" else slug


# --- C. FU-2 ground-truth: clone targets line up with skill pointers ---------


class TestFU2GroundTruth:
    def test_bundled_slugs_read_from_the_shipped_corpus(self):
        """Decision 91: each bundled FU-2 slug is READ from the guaranteed-present
        bundled path ${CLAUDE_PLUGIN_ROOT}/reference-corpus/<slug>/ — a runtime
        read-instruction (a skill or a phase contract) points there and the shipped
        corpus dir exists. This is the portability fix: the agent no longer depends
        on a runtime clone having materialized before it can read the corpus."""
        mismatches: list[str] = []
        for slug in BUNDLED_READ_SLUGS:
            if not (REFERENCE_CORPUS / slug).is_dir():
                mismatches.append(f"{slug}: shipped corpus dir missing")
            if not _files_reference_bundled(slug):
                mismatches.append(
                    f"{slug}: no read-instruction points at reference-corpus/{slug}/"
                )
        assert not mismatches, "bundled-read mismatch:\n  " + "\n  ".join(mismatches)

    def test_runtime_slug_reads_from_the_library_clone(self):
        """awesome-design-md stays a genuinely-cloned-at-runtime resource: a skill
        points at .website-builder/library/awesome-design-md/ (the full VoltAgent
        corpus, cloned at phase 17), and its bundled subset ships as
        reference-corpus/awesome-design-md-corpus/."""
        for slug in RUNTIME_READ_SLUGS:
            assert _skills_reference_slug(slug), (
                f"no skill points at .website-builder/library/{slug}/"
            )
            assert (REFERENCE_CORPUS / _corpus_dirname(slug)).is_dir(), (
                f"bundled subset missing for {slug}"
            )

    def test_corpus_dirs_ship_for_the_bundled_fu2_slugs(self):
        # design-systems / component-patterns / seo-checklists / brand-examples are
        # bundled (plugin-shipped); awesome-design-md ships as awesome-design-md-corpus.
        for slug in FU2_SLUGS:
            corpus = REFERENCE_CORPUS / _corpus_dirname(slug)
            assert corpus.is_dir(), f"shipped corpus dir missing for {slug}: {corpus}"
            assert any(corpus.iterdir()), f"shipped corpus {corpus} is empty"

    def test_bundled_corpora_still_autoclone_to_library(self, tmp_path: Path):
        """Decision 91 keeps the Decision-42 autoclone machinery: bundled corpora still
        materialize at .website-builder/library/<slug>/ at phase entry (harmless — the
        agent now READS them from reference-corpus/). Removing this now-redundant clone
        so library/ is reserved for genuinely-cloned resources is a follow-up for the
        General (surfaced in the catalogue/de-vault RPT)."""
        root = _write_project(tmp_path, 2)
        wb_library.autoclone_for_state(root, trigger="phase-entry", phase=2)   # brand-examples, design-systems
        wb_library.autoclone_for_state(root, trigger="phase-entry", phase=13)  # component-patterns
        wb_library.autoclone_for_state(root, trigger="phase-entry", phase=22)  # seo-checklists
        lib = root / ".website-builder" / "library"
        for slug in ("brand-examples", "design-systems", "component-patterns", "seo-checklists"):
            assert (lib / slug).is_dir(), f"bundled slug {slug} did not land at library/{slug}/"
