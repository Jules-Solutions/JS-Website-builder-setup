"""
Smoke tests for the website-builder plugin (Phase 1 / Captain E scope).

Two test tiers:

Tier 1 — Reference-detector tests (always runnable, even before B/C/D merge):
  Validates that the entry-mode detector in `detector.py` correctly classifies
  each fixture in `tests/walkthroughs/<entry-mode>/fixture/` against its
  `expected.yaml`. This validates fixture + spec internal consistency.

Tier 2 — Hook-integration tests (runnable post-merge):
  Invokes Captain C's actual SessionStart hook (when it exists at
  `hooks-handlers/session-start.{sh,py}`) and compares its output to
  `expected.yaml`. Skipped with a clear message if the hook script is missing.

Tier 2 — Bootstrap-skill integration tests (runnable post-merge):
  Invokes Captain D's `wb-bootstrap` skill against each fixture and asserts
  the resulting `.website-builder/` matches the `expected.yaml` contract
  (project.yaml shape + required/forbidden paths). Skipped with a clear
  message if the skill is missing.

v0.1 scope: detection + initialization shape. End-to-end agent invocation
(running real CC against a fixture and watching the agent walk phase 1)
is deferred to Phase 7-8 cosplay/Ralph tests per BUILD-strategy.md.

Run via:
  cd tests && uv run pytest -v
  OR
  ./run-tests.sh   (from plugin root)
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import pytest
import yaml

# Allow importing detector.py from this directory regardless of pytest cwd
sys.path.insert(0, str(Path(__file__).parent))
from detector import detect  # noqa: E402


# --- Constants -------------------------------------------------------------

PLUGIN_ROOT = Path(__file__).parent.parent.resolve()
WALKTHROUGHS_DIR = Path(__file__).parent / "walkthroughs"

ENTRY_MODES = [
    "greenfield",
    "has-existing-site",
    "has-AI-output",
    "has-Framer-attempt",
    "has-Figma-file",
]


# --- Fixture loaders -------------------------------------------------------

def _load_expected(entry_mode: str) -> dict:
    expected_path = WALKTHROUGHS_DIR / entry_mode / "expected.yaml"
    if not expected_path.is_file():
        pytest.fail(f"Missing expected.yaml at {expected_path}")
    return yaml.safe_load(expected_path.read_text(encoding="utf-8"))


def _fixture_dir(entry_mode: str) -> Path:
    fix = WALKTHROUGHS_DIR / entry_mode / "fixture"
    if not fix.is_dir():
        pytest.fail(f"Missing fixture/ dir for entry mode {entry_mode}")
    return fix


def _make_tempdir_with_fixture(entry_mode: str) -> Path:
    """Copy fixture/ into a tempdir and return the tempdir path."""
    src = _fixture_dir(entry_mode)
    tmp = Path(tempfile.mkdtemp(prefix=f"wb-test-{entry_mode}-"))
    # Copy fixture contents into the tempdir root
    for item in src.iterdir():
        dst = tmp / item.name
        if item.is_dir():
            shutil.copytree(item, dst)
        else:
            shutil.copy2(item, dst)
    return tmp


# --- Tier 1 — Reference-detector tests -------------------------------------

class TestReferenceDetector:
    """
    Always-runnable. Validates the detector.py reference implementation
    correctly classifies each fixture.
    """

    @pytest.mark.parametrize("entry_mode", ENTRY_MODES)
    def test_entry_mode_classification(self, entry_mode: str):
        expected = _load_expected(entry_mode)
        fixture = _fixture_dir(entry_mode)
        result = detect(fixture)
        assert result.entry_mode == expected["entry_mode"], (
            f"detector classified {entry_mode} fixture as {result.entry_mode}; "
            f"expected.yaml says {expected['entry_mode']}"
        )

    @pytest.mark.parametrize("entry_mode", ENTRY_MODES)
    def test_detection_confidence(self, entry_mode: str):
        expected = _load_expected(entry_mode)
        fixture = _fixture_dir(entry_mode)
        result = detect(fixture)
        assert result.detection_confidence == expected["detection_confidence"], (
            f"detector confidence {result.detection_confidence} != "
            f"expected {expected['detection_confidence']} for {entry_mode}"
        )

    @pytest.mark.parametrize("entry_mode", ENTRY_MODES)
    def test_detection_signals_subset(self, entry_mode: str):
        """
        Every key in expected.detection_signals must be present in the detector
        output and have the same value. Extra keys in the detector output are
        permitted (forward-compat).
        """
        expected = _load_expected(entry_mode)
        fixture = _fixture_dir(entry_mode)
        result = detect(fixture)
        actual_signals = result.detection_signals
        for key, expected_value in expected["detection_signals"].items():
            assert key in actual_signals, (
                f"detector missing signal '{key}' for {entry_mode}; "
                f"expected.yaml requires it"
            )
            assert actual_signals[key] == expected_value, (
                f"signal '{key}' for {entry_mode}: detector={actual_signals[key]} "
                f"!= expected={expected_value}"
            )

    @pytest.mark.parametrize("entry_mode", ENTRY_MODES)
    def test_next_phase_routing(self, entry_mode: str):
        expected = _load_expected(entry_mode)
        fixture = _fixture_dir(entry_mode)
        result = detect(fixture)
        # YAML loads 6.5 as float; our DetectionResult uses float
        expected_phase = float(expected["next_phase"])
        assert result.next_phase == expected_phase, (
            f"next_phase mismatch for {entry_mode}: detector={result.next_phase} "
            f"!= expected={expected_phase}"
        )

    @pytest.mark.parametrize("entry_mode", ENTRY_MODES)
    def test_phase_6_5_at_start(self, entry_mode: str):
        expected = _load_expected(entry_mode)
        fixture = _fixture_dir(entry_mode)
        result = detect(fixture)
        assert result.runs_phase_6_5_at_start == expected["runs_phase_6_5_at_start"], (
            f"runs_phase_6_5_at_start mismatch for {entry_mode}: "
            f"detector={result.runs_phase_6_5_at_start} != "
            f"expected={expected['runs_phase_6_5_at_start']}"
        )


# --- Tier 2 — Hook integration tests ---------------------------------------

def _find_session_start_hook() -> Path | None:
    """
    Locate Captain C's SessionStart hook script.

    Per the canonical CC plugin spec + decision 59:
      hooks/hooks.json references scripts via ${CLAUDE_PLUGIN_ROOT}/hooks-handlers/...

    Captain C's authoring is expected to land:
      - hooks-handlers/session-start.sh OR
      - hooks-handlers/session-start.py OR
      - hooks-handlers/session_start.py (Python naming convention)

    This function looks for any of these.
    """
    candidates = [
        PLUGIN_ROOT / "hooks-handlers" / "session-start.sh",
        PLUGIN_ROOT / "hooks-handlers" / "session-start.py",
        PLUGIN_ROOT / "hooks-handlers" / "session_start.py",
    ]
    for c in candidates:
        if c.is_file():
            return c
    return None


def _hook_invocation_command(hook_path: Path) -> list[str]:
    """
    Build the command to invoke the hook. The caller passes `cwd=str(project_dir)`
    to subprocess.run; the hook reads `Path.cwd()` (matching CC's SessionStart
    semantics — CC sets cwd to the user's project at session start, the hook
    inspects that cwd). We do NOT pass project_dir as argv[1] because Captain C's
    session_start.py reads Path.cwd() directly and ignores argv per the CC spec.
    """
    if hook_path.suffix == ".py":
        return [sys.executable, str(hook_path)]
    # bash script
    return ["bash", str(hook_path)]


_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*\n(\{[\s\S]*?\})\s*\n```", re.MULTILINE)


def _parse_hook_output(stdout: str) -> dict[str, Any] | None:
    """
    Extract the structured hook output dict from stdout.

    Captain C's SessionStart hook emits prose markdown intended for CC to inject
    into the agent's session context (matches CC SessionStart hook semantics:
    stdout becomes agent-readable context, not machine output). Inside that
    prose, the hook embeds a `## Machine-readable summary` section with a
    fenced JSON block carrying the structured fields (`entry_mode`,
    `entry_signals`, `project_root`, etc.).

    Parser strategy, in order:
      1. Whole stdout parses as JSON object → use it (covers a future hook that
         outputs pure JSON, or a custom test runner).
      2. Whole stdout parses as YAML object → use it.
      3. First fenced ```json ... ``` block parses as JSON object → use it
         (Captain C's actual production format; the prose around the fence is
         agent-context, the fence is the machine surface).

    Returns parsed dict or None if all three strategies fail.
    """
    stdout = stdout.strip()
    if not stdout:
        return None
    # Strategy 1 — whole stdout as JSON
    try:
        parsed_json = json.loads(stdout)
        if isinstance(parsed_json, dict):
            return parsed_json
    except json.JSONDecodeError:
        pass
    # Strategy 2 — whole stdout as YAML
    try:
        parsed_yaml = yaml.safe_load(stdout)
        if isinstance(parsed_yaml, dict):
            return parsed_yaml
    except yaml.YAMLError:
        pass
    # Strategy 3 — extract first ```json ... ``` fenced block from markdown prose
    for match in _JSON_FENCE_RE.finditer(stdout):
        candidate = match.group(1)
        try:
            parsed_fence = json.loads(candidate)
            if isinstance(parsed_fence, dict):
                return parsed_fence
        except json.JSONDecodeError:
            continue
    return None


class TestHookIntegration:
    """
    Tier 2. Skipped when Captain C's hook script doesn't exist on the merged
    branch. When it exists, invokes the hook and compares its output to
    expected.yaml.
    """

    # Class-level annotation: tests run only after _skip_if_missing has set this,
    # so within test methods the attribute is guaranteed Path (not None). The
    # annotation tells Pyright the same.
    hook: Path

    @pytest.fixture(autouse=True)
    def _skip_if_missing(self):
        hook = _find_session_start_hook()
        if hook is None:
            pytest.skip(
                "SessionStart hook not yet authored (Captain C scope). "
                "Re-run after Captain C's branch merges to dev."
            )
        self.hook = hook

    @pytest.mark.parametrize("entry_mode", ENTRY_MODES)
    def test_hook_classifies_fixture(self, entry_mode: str):
        expected = _load_expected(entry_mode)
        tempdir = _make_tempdir_with_fixture(entry_mode)
        try:
            cmd = _hook_invocation_command(self.hook)
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env={**os.environ, "CLAUDE_PLUGIN_ROOT": str(PLUGIN_ROOT)},
                cwd=str(tempdir),  # hook reads Path.cwd() per CC SessionStart spec
                timeout=30,
            )
            assert proc.returncode == 0, (
                f"hook exited {proc.returncode} for {entry_mode} fixture\n"
                f"stdout: {proc.stdout}\nstderr: {proc.stderr}"
            )
            output = _parse_hook_output(proc.stdout)
            assert output is not None, (
                f"hook output unparseable for {entry_mode}\nstdout: {proc.stdout}"
            )
            assert output.get("entry_mode") == expected["entry_mode"], (
                f"hook classified {entry_mode} as {output.get('entry_mode')}; "
                f"expected {expected['entry_mode']}"
            )
        finally:
            shutil.rmtree(tempdir, ignore_errors=True)


# --- Tier 2 — detector/hook precedence-parity drift guard (F9) -------------
#
# tests/detector.py is the reference implementation; hooks-handlers/session_start.py
# keeps an INDEPENDENT hand-synced reimplementation of the same entry-mode
# precedence (branch order + gating), not an import — the shipped hook can't
# depend on a tests/-only module. test_hook_classifies_fixture above only
# exercises the 5 walkthrough fixtures, each of which carries exactly ONE
# signal, so it can't catch a precedence-ORDER divergence (e.g. "which mode
# wins when a project has both a .framer/ dir AND a stray .fig file"). This
# class builds synthetic COMBINED-signal projects specifically to make that
# class of drift loud instead of silent — see the sync-contract comments atop
# tests/detector.py::detect() and hooks-handlers/session_start.py::detect_entry_mode().

_COMBINED_SIGNAL_CASES = [
    pytest.param(
        {".framer": "dir", "design.fig": "file"},
        "has-Framer-attempt",
        id="framer-and-figma",
    ),
    pytest.param(
        {"next.config.js": "file", "design.fig": "file"},
        "has-existing-site",
        id="stack-config-and-figma",
    ),
    pytest.param(
        {".framer": "dir", "next.config.js": "file"},
        "has-Framer-attempt",
        id="framer-and-stack-config",
    ),
]


def _build_combined_signal_dir(spec: dict[str, str]) -> Path:
    """Build a synthetic project dir carrying MULTIPLE entry-mode signals at
    once (unlike the single-signal tests/walkthroughs/ fixtures), so precedence
    order between competing signals is actually exercised."""
    tmp = Path(tempfile.mkdtemp(prefix="wb-test-combined-"))
    for name, kind in spec.items():
        if kind == "dir":
            (tmp / name).mkdir(parents=True, exist_ok=True)
        else:
            (tmp / name).write_text("placeholder", encoding="utf-8")
    return tmp


class TestDetectorHookPrecedenceParity:
    """
    Tier 2. Skipped under the same condition as TestHookIntegration (hook not
    yet authored). For each combined-signal case, asserts BOTH the reference
    detector.py AND the production session_start.py hook agree on the winning
    entry_mode — proving the two hand-synced precedence orders haven't drifted.
    """

    hook: Path

    @pytest.fixture(autouse=True)
    def _skip_if_missing(self):
        hook = _find_session_start_hook()
        if hook is None:
            pytest.skip(
                "SessionStart hook not yet authored (Captain C scope). "
                "Re-run after Captain C's branch merges to dev."
            )
        self.hook = hook

    @pytest.mark.parametrize("signals,expected_mode", _COMBINED_SIGNAL_CASES)
    def test_precedence_agrees_on_combined_signals(self, signals, expected_mode):
        tempdir = _build_combined_signal_dir(signals)
        try:
            det_result = detect(tempdir)
            assert det_result.entry_mode == expected_mode, (
                f"tests/detector.py's OWN documented precedence disagrees with "
                f"itself for combined signals {signals}: got "
                f"{det_result.entry_mode}, expected {expected_mode}. Fix the "
                f"test's expectation or detect()'s branch order before "
                f"trusting the cross-hook comparison below."
            )

            cmd = _hook_invocation_command(self.hook)
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env={**os.environ, "CLAUDE_PLUGIN_ROOT": str(PLUGIN_ROOT)},
                cwd=str(tempdir),  # hook reads Path.cwd() per CC SessionStart spec
                timeout=30,
            )
            assert proc.returncode == 0, (
                f"hook exited {proc.returncode} for combined signals {signals}\n"
                f"stdout: {proc.stdout}\nstderr: {proc.stderr}"
            )
            output = _parse_hook_output(proc.stdout)
            assert output is not None, (
                f"hook output unparseable for combined signals {signals}\n"
                f"stdout: {proc.stdout}"
            )
            assert output.get("entry_mode") == expected_mode, (
                f"session_start.py's detect_entry_mode() DISAGREES with "
                f"detector.py's precedence for combined signals {signals}: "
                f"hook picked {output.get('entry_mode')!r}, detector.py picks "
                f"{expected_mode!r}. This is exactly the drift the F9 sync "
                f"contract exists to catch — align detect_entry_mode()'s "
                f"branch order/gating with detect()'s (see the sync-contract "
                f"comments in both files)."
            )
        finally:
            shutil.rmtree(tempdir, ignore_errors=True)


# --- Tier 2 — Bootstrap-skill integration tests ----------------------------

def _find_bootstrap_skill() -> Path | None:
    """
    Locate Captain D's wb-bootstrap skill manifest.

    Per the canonical CC plugin spec + DESIGN-architecture.md:
      skills/wb-bootstrap/SKILL.md
    """
    skill = PLUGIN_ROOT / "skills" / "wb-bootstrap" / "SKILL.md"
    return skill if skill.is_file() else None


def _find_bootstrap_runner() -> Path | None:
    """
    Locate a bootstrap-skill executable runner if one exists.

    Captain D may ship `scripts/install-skills.sh` (per decision 32 / 43) and
    optionally a `scripts/wb-bootstrap.sh` or `scripts/wb-bootstrap.py` runner
    that exercises the skill end-to-end against a project dir. If such a
    runner exists, this test invokes it; otherwise, this Tier 2 test is skipped
    (the SKILL.md exists, but the test harness can't invoke a skill in
    isolation — that requires a live CC session, which is Phase 7-8 scope).

    Discovery preference order: Python runner first, shell runner second. When
    both ship (the Phase 2 CL-1 reality — `.sh` is a thin cross-OS launcher
    that delegates to the `.py` runner where the actual bootstrap logic lives),
    invoking the `.py` runner directly is portable across all subprocess /
    bash combinations (including Windows-Python invoking WSL-bash, where
    `["bash", "C:\\path\\with\\backslashes\\file.sh"]` fails because WSL bash
    mangles backslash escapes and cannot resolve `C:\\` drive paths). The
    `.py` runner runs identically under any Python interpreter the test was
    launched with. Preserving `.sh` as a fallback keeps POSIX-only `.sh`
    deliveries supported.
    """
    candidates = [
        PLUGIN_ROOT / "scripts" / "wb-bootstrap.py",
        PLUGIN_ROOT / "scripts" / "wb_bootstrap.py",
        PLUGIN_ROOT / "scripts" / "wb-bootstrap.sh",
    ]
    for c in candidates:
        if c.is_file():
            return c
    return None


def _path_exists_in(root: Path, relpath: str) -> bool:
    """
    Check whether a path expressed in a fixture's required/forbidden_paths list
    exists under `root`. Supports trailing-slash directory tests and simple
    glob patterns (e.g. `decisions/ingest-*.md`).
    """
    relpath = relpath.rstrip("/")
    if "*" in relpath:
        matches = list(root.glob(relpath))
        return len(matches) > 0
    target = root / relpath
    return target.exists()


class TestBootstrapSkill:
    """
    Tier 2. Validates that Captain D's wb-bootstrap skill produces the
    `.website-builder/` directory matching expected.yaml's contract.

    Two skip paths:
      a. SKILL.md missing → skipped (Captain D not yet shipped)
      b. SKILL.md present but no runnable invocation script → skipped
         (skill must be exercised via real CC session — Phase 7-8 scope)
    """

    # Class-level annotation: tests run only after _skip_if_missing has set this,
    # so within test methods the attribute is guaranteed Path (not None).
    runner: Path

    @pytest.fixture(autouse=True)
    def _skip_if_missing(self):
        skill = _find_bootstrap_skill()
        if skill is None:
            pytest.skip(
                "wb-bootstrap skill not yet authored (Captain D scope). "
                "Re-run after Captain D's branch merges to dev."
            )
        runner = _find_bootstrap_runner()
        if runner is None:
            pytest.skip(
                "wb-bootstrap skill present but no test-runner script found "
                "in scripts/. Skill execution requires a live CC session "
                "(Phase 7-8 cosplay/Ralph tests). To enable this Tier 2 test, "
                "Captain D may add a scripts/wb-bootstrap.{sh,py} runner that "
                "performs the bootstrap actions against a target project dir."
            )
        self.runner = runner

    @pytest.mark.parametrize("entry_mode", ENTRY_MODES)
    def test_bootstrap_creates_website_builder_dir(self, entry_mode: str):
        expected = _load_expected(entry_mode)
        tempdir = _make_tempdir_with_fixture(entry_mode)
        try:
            # Same cwd-not-argv pattern as TestHookIntegration: bootstrap runner
            # operates on Path.cwd() (matching the SessionStart hook's convention,
            # since the wb-bootstrap skill runs in the same CC-set cwd context).
            cmd = (
                [sys.executable, str(self.runner)]
                if self.runner.suffix == ".py"
                else ["bash", str(self.runner)]
            )
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env={**os.environ, "CLAUDE_PLUGIN_ROOT": str(PLUGIN_ROOT)},
                cwd=str(tempdir),  # runner reads Path.cwd() per CC SessionStart spec
                timeout=60,
            )
            assert proc.returncode == 0, (
                f"bootstrap runner exited {proc.returncode} for {entry_mode}\n"
                f"stdout: {proc.stdout}\nstderr: {proc.stderr}"
            )
            # required_paths
            for relpath in expected.get("required_paths", []):
                assert _path_exists_in(tempdir, relpath), (
                    f"required path {relpath} missing after bootstrap of {entry_mode}"
                )
            # forbidden_paths
            for relpath in expected.get("forbidden_paths", []):
                assert not _path_exists_in(tempdir, relpath), (
                    f"forbidden path {relpath} exists after bootstrap of {entry_mode}"
                )
            # project.yaml assertions
            project_yaml = tempdir / ".website-builder" / "project.yaml"
            if project_yaml.is_file():
                proj = yaml.safe_load(project_yaml.read_text(encoding="utf-8"))
                for key, expected_value in expected.get("project_yaml_assertions", {}).items():
                    actual = proj.get(key)
                    assert actual == expected_value, (
                        f"project.yaml.{key} for {entry_mode}: "
                        f"actual={actual!r} != expected={expected_value!r}"
                    )
        finally:
            shutil.rmtree(tempdir, ignore_errors=True)


# --- Smoke meta-test --------------------------------------------------------

class TestFixtureCompleteness:
    """
    Always-runnable. Asserts every entry mode has a complete fixture set:
      walkthroughs/<entry-mode>/
        ├── README.md
        ├── fixture/
        └── expected.yaml
    """

    @pytest.mark.parametrize("entry_mode", ENTRY_MODES)
    def test_fixture_dir_exists(self, entry_mode: str):
        d = WALKTHROUGHS_DIR / entry_mode
        assert d.is_dir(), f"missing walkthrough dir: {d}"
        assert (d / "README.md").is_file(), f"missing README.md in {d}"
        assert (d / "fixture").is_dir(), f"missing fixture/ dir in {d}"
        assert (d / "expected.yaml").is_file(), f"missing expected.yaml in {d}"

    @pytest.mark.parametrize("entry_mode", ENTRY_MODES)
    def test_expected_yaml_parses(self, entry_mode: str):
        path = WALKTHROUGHS_DIR / entry_mode / "expected.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict), f"expected.yaml for {entry_mode} did not parse to a dict"
        # Required top-level keys
        for k in ("entry_mode", "detection_confidence", "detection_signals", "next_phase"):
            assert k in data, f"expected.yaml for {entry_mode} missing required key '{k}'"
