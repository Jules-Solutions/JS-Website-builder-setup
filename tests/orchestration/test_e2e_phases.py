"""
End-to-end orchestration-spine run — drive a synthetic GREENFIELD project through
phases 1 -> 18 and assert the spine fires correctly at every advance.

Wave 5 / Captain verify-1 — the program headline DoD
(DESIGN-orchestration-spine.md § 10): "Fresh greenfield dir ... drive
project.yaml.current_phase ... PostToolUse fires ... the orchestrator (a)
auto-cloned, (b) injected the skill directives, (c) injected the adapter design
section ...".

Where Wave-1 `test_wb_orchestrate.py` proves the 16->17 fire in isolation, this
walks the WHOLE early pipeline (1->18) against the REAL plugin adapters / skills /
phase-contracts (resolved via wb_orchestrate._plugin_root() = the worktree), over a
synthetic `.website-builder/project.yaml` built inline in pytest's tmp_path (nothing
ships; no .gitignore exception).

Stack under test: nextjs / cms=none / component_library=shadcn (the program DoD
stack). Each advance is asserted to:
  * fire exactly once (run_post_tool_use returns a result on the advance, None on a
    same-phase re-call),
  * advance the `.orchestrator-state` marker to the new phase,
  * emit a valid PostToolUse payload envelope, and
  * inject the phase's bound skill directives (action 3 fires every phase).

Then per-phase assertions confirm the resource/adapter/skill/imagegen actions at the
phases that bind them (02, 05, 08, 11, 12, 13, 16, 17, 18).

Run:
  bash tests/run-tests.sh
  cd tests && uv run --with pyyaml --with pytest pytest orchestration/test_e2e_phases.py -v
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import wb_orchestrate as wo  # noqa: E402  (sys.path mutation must precede)


# --- Fixture helpers --------------------------------------------------------

# The program DoD greenfield stack (DESIGN-orchestration-spine § 10.1).
GREENFIELD = {
    "stack": "nextjs",
    "cms": "none",
    "component_library": "shadcn",
    "entry_mode": "greenfield",
    "languages": "en",
    "transactional": "false",
}

# Each early-pipeline phase binds exactly one skill (verified against the shipped
# phase-contracts/ frontmatter). Action 3 must inject this skill at every advance.
EXPECTED_SKILL = {
    1: "wb-discovery", 2: "wb-discovery", 3: "wb-discovery",
    4: "wb-discovery", 5: "wb-discovery",
    6: "wb-content-foundation", 7: "wb-content-foundation",
    8: "wb-content-foundation", 9: "wb-content-foundation",
    10: "wb-architecture", 11: "wb-architecture", 12: "wb-architecture",
    13: "wb-content", 14: "wb-content", 15: "wb-content", 16: "wb-content",
    17: "wb-design-system", 18: "wb-component-build",
}


def _write_project(root: Path, phase: int, **overrides) -> None:
    """(Re)write .website-builder/project.yaml at `phase` with the greenfield stack."""
    fields: dict[str, object] = dict(GREENFIELD)
    fields.update(overrides)
    fields["current_phase"] = phase
    sd = root / ".website-builder"
    sd.mkdir(parents=True, exist_ok=True)
    body = "\n".join(f"{k}: {v}" for k, v in fields.items()) + "\n"
    (sd / "project.yaml").write_text(body, encoding="utf-8")


def _advance(root: Path, phase: int, **overrides):
    """Write current_phase=phase and fire the PostToolUse entry. Returns the result."""
    _write_project(root, phase, **overrides)
    return wo.run_post_tool_use(root)


def _as_posttooluse_payload(block: str) -> dict:
    """Wrap a rendered block in the LOCKED PostToolUse envelope (§2) + round-trip it
    through json so the test proves the exact payload the handler emits is valid."""
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": block,
        }
    }
    return json.loads(json.dumps(payload))


def _autoclone_resources(result) -> set:
    return {getattr(c, "resource", None) for c in result.autoclone}


def _adapter_headings(result) -> set:
    return {s.heading for s in result.adapter_sections}


@pytest.fixture
def walk(tmp_path: Path):
    """Drive one greenfield project through phases 1->18 once, returning
    (root, {phase: OrchestrationResult}). Shared by the per-phase action tests so the
    expensive real-adapter/real-skill walk runs once per test that needs it."""
    root = tmp_path
    results = {}
    for phase in range(1, 19):
        results[phase] = _advance(root, phase)
    return root, results


# --- The headline: fire-exactly-once across the whole 1->18 walk ------------


class TestE2EPhaseWalk:
    def test_every_advance_fires_exactly_once(self, tmp_path: Path):
        root = tmp_path
        for phase in range(1, 19):
            result = _advance(root, phase)
            # (1) the advance fires
            assert result is not None, f"phase {phase} advance did not fire"
            assert result.phase == phase
            # (2) it fires EXACTLY once — a same-phase re-call is a no-op
            assert wo.run_post_tool_use(root) is None, f"phase {phase} re-fired"
            # (3) the marker advanced to this phase
            assert wo._read_marker(root)["last_phase"] == phase

    def test_every_advance_emits_valid_posttooluse_payload(self, tmp_path: Path):
        root = tmp_path
        for phase in range(1, 19):
            result = _advance(root, phase)
            assert result is not None, f"phase {phase} advance did not fire"
            payload = _as_posttooluse_payload(result.render())
            hso = payload["hookSpecificOutput"]
            assert hso["hookEventName"] == "PostToolUse"
            assert isinstance(hso["additionalContext"], str)
            assert f"phase {phase} entry" in hso["additionalContext"]

    def test_skill_directives_inject_at_every_phase(self, walk):
        _root, results = walk
        for phase, skill in EXPECTED_SKILL.items():
            sd = results[phase].skill_directives
            assert sd is not None, f"phase {phase} injected no skill directives"
            assert sd.skill == skill, f"phase {phase} bound {sd.skill}, expected {skill}"
            assert sd.description.strip(), f"phase {phase} skill description empty"


# --- Per-phase action assertions (02/05/08/11/12/13/16/17/18) ----------------


class TestPhase02Vision:
    def test_autoclones_brand_and_design_corpora(self, walk):
        _root, results = walk
        resources = _autoclone_resources(results[2])
        assert "brand-examples-corpus" in resources
        assert "design-systems-corpus" in resources

    def test_bundled_corpora_land_on_disk(self, walk):
        root, _results = walk
        lib = root / ".website-builder" / "library"
        for slug in ("brand-examples", "design-systems"):
            assert (lib / slug).is_dir(), f"bundled corpus {slug} not copied"
            assert any((lib / slug).iterdir()), f"bundled corpus {slug} is empty"


class TestPhase05BrandVoice:
    def test_autoclones_voice_archetypes(self, walk):
        root, results = walk
        assert "voice-archetypes" in _autoclone_resources(results[5])
        assert (root / ".website-builder" / "library" / "voice-archetypes").is_dir()


class TestPhase08ImageStrategy:
    def test_surfaces_imagegen_path(self, walk):
        _root, results = walk
        # phase 8 is the IMAGEGEN phase — action 5 resolves the consumer image-gen path.
        assert results[8].imagegen is not None
        assert "Image generation" in results[8].render()

    def test_no_adapter_section_at_phase_8(self, walk):
        _root, results = walk
        # § 4.4: phase 8 maps to {} — no adapter section (action 5 carries it).
        assert results[8].adapter_sections == []


class TestPhase11StackDecision:
    def test_injects_nextjs_adapter_sections(self, walk):
        _root, results = walk
        r = results[11]
        assert r.adapter_sections, "no stack-adapter sections at phase 11"
        assert all(s.adapter == "stack-nextjs" for s in r.adapter_sections)
        # § 4.4 maps phase 11 to Mental model / Limitations / CMS pairing.
        assert _adapter_headings(r) & {
            "Mental model", "Limitations + escape hatches", "CMS pairing"
        }

    def test_astro_clone_skipped_for_nextjs(self, walk):
        _root, results = walk
        # phase-11 contract clones astro docs ONLY when stack == astro; nextjs → skipped.
        astro = [c for c in results[11].autoclone
                 if getattr(c, "resource", None) == "astro-content-collections"]
        assert astro and astro[0].status == "skipped"


class TestPhase12CmsDecision:
    def test_cms_none_injects_only_stack(self, walk):
        _root, results = walk
        # greenfield cms=none → no CMS adapter binding, only stack CMS-pairing.
        kinds = {s.adapter_kind for s in results[12].adapter_sections}
        assert "cms" not in kinds


class TestPhase13ContentPerPage:
    def test_autoclones_component_patterns(self, walk):
        root, results = walk
        assert "component-patterns" in _autoclone_resources(results[13])
        assert (root / ".website-builder" / "library" / "component-patterns").is_dir()

    def test_injects_content_layer_mapping(self, walk):
        _root, results = walk
        assert "Content layer mapping" in _adapter_headings(results[13])


class TestPhase16Copywriting:
    def test_injects_content_layer_mapping(self, walk):
        _root, results = walk
        assert "Content layer mapping" in _adapter_headings(results[16])


class TestPhase17DesignSystem:
    """The program-DoD keystone phase, walked in-context (not in isolation)."""

    def test_autoclone_design_corpus(self, walk):
        _root, results = walk
        resources = _autoclone_resources(results[17])
        assert "awesome-design-md" in resources          # always
        assert "shadcn-components" in resources           # when component_library==shadcn

    def test_design_system_directives(self, walk):
        _root, results = walk
        sd = results[17].skill_directives
        assert sd is not None and sd.skill == "wb-design-system"
        assert "OKLCH" in sd.description
        assert "refuses arbitrary color picks" in sd.description

    def test_nextjs_design_sections(self, walk):
        _root, results = walk
        headings = _adapter_headings(results[17])
        assert "Content layer mapping" in headings
        assert "Component library pairing" in headings
        assert all(s.adapter == "stack-nextjs" for s in results[17].adapter_sections)

    def test_rendered_block_carries_all_three_injections(self, walk):
        _root, results = walk
        block = results[17].render()
        assert "awesome-design-md" in block               # (a) autoclone
        assert "wb-design-system" in block                # (b) skill directives
        assert "## Content layer mapping" in block        # (c) adapter section
        assert "## Component library pairing" in block


class TestPhase18ComponentBuild:
    def test_injects_build_sections(self, walk):
        _root, results = walk
        headings = _adapter_headings(results[18])
        # § 4.4 maps phase 18 to Component library pairing / Auth + setup / Migration recipe.
        assert "Component library pairing" in headings
        assert headings & {"Component library pairing", "Auth + setup", "Migration recipe"}

    def test_binds_component_build_skill(self, walk):
        _root, results = walk
        assert results[18].skill_directives.skill == "wb-component-build"
