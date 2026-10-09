"""
Phase 2.C — PreToolUse anti-skip gating tests.

Auto-discovered by pytest (per tests/pyproject.toml
`python_files = ["smoke_test.py", "test_*.py"]`). Does NOT touch the shared
TestHookIntegration harness in smoke_test.py — that exercises the SessionStart
hook and must stay 5/5 green; this file is a separate module exercising the
PreToolUse hook only.

Each test invokes `hooks-handlers/pre_tool_use.py` as a subprocess with:
  * a synthesized PreToolUse JSON payload on stdin,
  * `CLAUDE_PLUGIN_ROOT` set to the real plugin root (so the hook can read the
    38 phase contracts for the block rationale + locate skip-decision files),
  * cwd = a tempdir holding a synthetic `.website-builder/` project state,
matching the exact invocation contract the SessionStart harness uses
(cwd-not-argv; the hook reads Path.cwd() and CLAUDE_PLUGIN_ROOT per the CC
spec) and matching how Claude Code actually fires the hook.

The CC contract verified via context7 /anthropics/claude-code (2026-05-19):
ALLOW = exit 0 (+ optional JSON permissionDecision=allow on stdout);
BLOCK = JSON permissionDecision=deny on stdout AND exit 2 with the reason on
stderr (dual-emit for compatibility). Tests assert on both surfaces.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).parent.parent.resolve()
HOOK = PLUGIN_ROOT / "hooks-handlers" / "pre_tool_use.py"

# The hook module itself, for the constants the gate is built from (phase
# order, default exempt paths, tool policy) and for the pure `decide()`.
sys.path.insert(0, str(PLUGIN_ROOT / "hooks-handlers"))
import pre_tool_use as hook  # noqa: E402


# --- helpers --------------------------------------------------------------- #


def _make_project(
    *,
    state: bool = True,
    current_phase: str | None = "1",
    skip_files: list[str] | None = None,
    extra_yaml: list[str] | None = None,
) -> Path:
    """Build a tempdir holding a synthetic user project.

    state=False        → no `.website-builder/` at all (pre-bootstrap).
    current_phase=None  → `.website-builder/project.yaml` exists but has no
                          `current_phase:` line (degraded state).
    skip_files          → names to create under `.website-builder/decisions/`
                          (e.g. ["skip-phase-21.md"]).
    extra_yaml          → raw lines appended to project.yaml (e.g. a
                          `gate_exempt_paths` list).
    """
    tmp = Path(tempfile.mkdtemp(prefix="wb-ptu-test-"))
    if state:
        sd = tmp / ".website-builder"
        sd.mkdir()
        lines = ["name: Test Site", "slug: test-site", "entry_mode: greenfield"]
        if current_phase is not None:
            lines.append(f"current_phase: {current_phase}")
        lines.extend(extra_yaml or [])
        (sd / "project.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")
        if skip_files:
            ddir = sd / "decisions"
            ddir.mkdir()
            for name in skip_files:
                (ddir / name).write_text(
                    "---\ntype: decision\nchosen: skip\n---\nuser authorized.\n",
                    encoding="utf-8",
                )
    return tmp


def _run(project: Path, payload: dict) -> subprocess.CompletedProcess:
    """Invoke the PreToolUse hook the way CC does: payload on stdin,
    CLAUDE_PLUGIN_ROOT in env, cwd = the project dir."""
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env={**os.environ, "CLAUDE_PLUGIN_ROOT": str(PLUGIN_ROOT)},
        cwd=str(project),
        timeout=30,
    )


def _decision(proc: subprocess.CompletedProcess) -> str | None:
    """Pull hookSpecificOutput.permissionDecision out of stdout if present."""
    out = (proc.stdout or "").strip()
    if not out:
        return None
    # stdout may carry the JSON object; tolerate trailing newline / single obj
    try:
        obj = json.loads(out)
    except json.JSONDecodeError:
        # last non-empty line might be the JSON (defensive)
        for line in reversed(out.splitlines()):
            line = line.strip()
            if line.startswith("{"):
                try:
                    obj = json.loads(line)
                    break
                except json.JSONDecodeError:
                    continue
        else:
            return None
    hso = obj.get("hookSpecificOutput") if isinstance(obj, dict) else None
    if isinstance(hso, dict):
        return hso.get("permissionDecision")
    return None


def _assert_allow(proc: subprocess.CompletedProcess) -> None:
    assert proc.returncode == 0, (
        f"expected ALLOW (exit 0); got {proc.returncode}\n"
        f"stdout={proc.stdout!r}\nstderr={proc.stderr!r}"
    )
    dec = _decision(proc)
    # ALLOW is either a silent exit-0 (no stdout) or an explicit allow JSON.
    assert dec in (None, "allow"), f"expected allow/silent; got decision={dec!r}"


def _assert_block(proc: subprocess.CompletedProcess) -> None:
    # Dual-emit contract: exit 2 + reason on stderr + deny JSON on stdout.
    assert proc.returncode == 2, (
        f"expected BLOCK (exit 2); got {proc.returncode}\n"
        f"stdout={proc.stdout!r}\nstderr={proc.stderr!r}"
    )
    assert _decision(proc) == "deny", (
        f"expected permissionDecision=deny on stdout; stdout={proc.stdout!r}"
    )
    assert proc.stderr.strip(), "expected a block reason on stderr"


# --- payload factories ----------------------------------------------------- #


def _edit(path: str) -> dict:
    return {"tool_name": "Edit", "tool_input": {"file_path": path}}


def _write(path: str) -> dict:
    return {"tool_name": "Write", "tool_input": {"file_path": path}}


def _bash(cmd: str) -> dict:
    return {"tool_name": "Bash", "tool_input": {"command": cmd}}


def _ask() -> dict:
    return {"tool_name": "AskUserQuestion", "tool_input": {"questions": []}}


# --------------------------------------------------------------------------- #
# Case 1 — pre-bootstrap (no .website-builder/) → ALLOW
# --------------------------------------------------------------------------- #


class TestPreToolUseGating:
    """The 7 cases the INST mandates, plus the 1→3 walk demonstration."""

    def test_case1_pre_bootstrap_allows(self):
        proj = _make_project(state=False)
        try:
            proc = _run(proj, _write("src/app/page.tsx"))
            _assert_allow(proc)
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    # ---- Case 2 — degraded state (project.yaml, no current_phase) → ALLOW -- #

    def test_case2_degraded_state_soft_allows(self):
        proj = _make_project(current_phase=None)
        try:
            proc = _run(proj, _edit("src/components/Hero.tsx"))
            _assert_allow(proc)
            # soft-allow must surface an advisory systemMessage
            obj = json.loads(proc.stdout.strip())
            assert "current_phase" in obj.get("systemMessage", "")
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    # ---- Case 3 — tool authorized at current phase → ALLOW ---------------- #

    def test_case3a_phase1_askuserquestion_allows(self):
        proj = _make_project(current_phase="1")
        try:
            _assert_allow(_run(proj, _ask()))
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    def test_case3b_phase1_write_project_yaml_allows(self):
        proj = _make_project(current_phase="1")
        try:
            # Write to .website-builder/project.yaml is state-write — allowed
            # at phase 1 (the contract's own output artifact).
            _assert_allow(_run(proj, _write(".website-builder/project.yaml")))
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    # ---- Case 4 — downstream tool at upstream phase → BLOCK --------------- #

    def test_case4a_phase5_edit_tsx_blocked_code_gated_to_18(self):
        proj = _make_project(current_phase="5")
        try:
            proc = _run(proj, _edit("src/components/foo.tsx"))
            _assert_block(proc)
            assert "phase 18" in proc.stderr or "phase 18" in proc.stdout
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    def test_case4b_phase1_write_codefile_blocked(self):
        proj = _make_project(current_phase="1")
        try:
            # Writing a real source file at phase 1 (a phase-18 artifact) is the
            # canonical forward-skip the hook exists to refuse.
            proc = _run(proj, _write("app/page.tsx"))
            _assert_block(proc)
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    def test_case4c_phase14_build_command_blocked(self):
        proj = _make_project(current_phase="14")
        try:
            # `npm run build` is build-deploy — gated until phase 19.
            proc = _run(proj, _bash("npm run build"))
            _assert_block(proc)
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    # ---- Case 5 — phase 6.5 side-channel → ALLOW even for its tools ------- #

    def test_case5a_phase_6_5_is_current_never_blocks(self):
        proj = _make_project(current_phase="6.5")
        try:
            # Even a state-write at 6.5 (its ingestion target) is allowed; the
            # side-channel never blocks the agent from advancing.
            _assert_allow(_run(proj, _write(".website-builder/brand.yaml")))
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    def test_case5b_phase_6_5_playwright_allowed(self):
        proj = _make_project(current_phase="6.5")
        try:
            payload = {
                "tool_name": "mcp__playwright__browser_navigate",
                "tool_input": {"url": "https://example.com"},
            }
            _assert_allow(_run(proj, payload))
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    # ---- Case 6 — skip-decision override → ALLOW with notice ------------- #

    def test_case6_skip_decision_file_overrides_block(self):
        proj = _make_project(
            current_phase="21", skip_files=["skip-phase-21.md"]
        )
        try:
            # At phase 21, code-write would normally be authorized (21 is in
            # build-integration). To prove the override path we attempt a
            # build-deploy at a phase that authorizes it AND a true upstream
            # skip: use phase 14 + skip-phase-14.md instead.
            proj2 = _make_project(
                current_phase="14", skip_files=["skip-phase-14.md"]
            )
            try:
                proc = _run(proj2, _edit("src/components/Hero.tsx"))
                _assert_allow(proc)
                obj = json.loads(proc.stdout.strip())
                assert "skip-phase-14.md" in obj.get("systemMessage", "")
            finally:
                shutil.rmtree(proj2, ignore_errors=True)
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    # ---- Case 7 — authorized-at-current for a mid-pipeline phase → ALLOW -- #

    def test_case7_phase18_edit_tsx_allows(self):
        proj = _make_project(current_phase="18")
        try:
            # Phase 18 is THE codegen gate — code-write is authorized here.
            _assert_allow(_run(proj, _edit("src/components/Hero.tsx")))
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    def test_case7b_phase19_build_allows(self):
        proj = _make_project(current_phase="19")
        try:
            _assert_allow(_run(proj, _bash("pnpm run build")))
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    # ---- DoD demonstration: walk current_phase 1 → 2 → 3 ----------------- #

    def test_dod_walk_1_to_3_allows_in_phase_blocks_forward_skip(self):
        """With current_phase walking 1→2→3: the hook ALLOWs in-phase tools
        (AskUserQuestion, state-write) and BLOCKs every forward-skip attempt
        (code-write / build) at each of the three phases."""
        for phase in ("1", "2", "3"):
            proj = _make_project(current_phase=phase)
            try:
                # in-phase tools allowed
                _assert_allow(_run(proj, _ask()))
                _assert_allow(
                    _run(proj, _write(".website-builder/project.yaml"))
                )
                # forward-skip attempts blocked
                _assert_block(_run(proj, _write("src/app/page.tsx")))
                _assert_block(_run(proj, _bash("next build")))
            finally:
                shutil.rmtree(proj, ignore_errors=True)

    # ---- robustness: malformed payload must not brick (fails open) ------- #

    def test_malformed_payload_fails_open(self):
        proj = _make_project(current_phase="1")
        try:
            proc = subprocess.run(
                [sys.executable, str(HOOK)],
                input="not json at all",
                capture_output=True,
                text=True,
                env={**os.environ, "CLAUDE_PLUGIN_ROOT": str(PLUGIN_ROOT)},
                cwd=str(proj),
                timeout=30,
            )
            # empty/invalid payload → empty tool_name → unknown class → ALLOW;
            # the hook must never brick the session.
            assert proc.returncode == 0
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    def test_unknown_tool_allows(self):
        proj = _make_project(current_phase="1")
        try:
            payload = {"tool_name": "SomeFutureTool", "tool_input": {}}
            _assert_allow(_run(proj, payload))
        finally:
            shutil.rmtree(proj, ignore_errors=True)


# --------------------------------------------------------------------------- #
# Collaboration / project-meta paths are not the site
#
# Two agents that collaborate on a project talk through one markdown file per
# message under comms/, keep the project's records under docs/, and commit and
# push both straight to main. None of that is a forward-skip into building the
# site, so once `.website-builder/project.yaml` exists the gate must still let
# them through at phase 1 -- while code-write and real deploys stay blocked.
# --------------------------------------------------------------------------- #

COMMS_MESSAGE = "comms/2026-10-09/101500-ole-to-jules-status.md"


def _assert_silent_allow(proc: subprocess.CompletedProcess) -> None:
    """ALLOW with no advisory: nothing on stdout."""
    _assert_allow(proc)
    assert proc.stdout.strip() == "", f"expected no advisory; got {proc.stdout!r}"


def _multiedit(path: str) -> dict:
    return {"tool_name": "MultiEdit", "tool_input": {"file_path": path, "edits": []}}


def _decide(proj: Path, payload: dict) -> tuple[bool, str]:
    """The hook's pure decision, in-process (for sweeps too wide to spawn)."""
    return hook.decide(
        root=proj,
        plugin_root=PLUGIN_ROOT,
        tool_name=payload["tool_name"],
        tool_input=payload["tool_input"],
    )


class TestGateExemptWrites:
    """Writes to collaboration / project-meta paths are never gated."""

    @pytest.mark.parametrize(
        "path", [COMMS_MESSAGE, "docs/STATE.md", "CLAUDE.md"]
    )
    def test_named_paths_allowed_silently_at_phase_1(self, path):
        proj = _make_project(current_phase="1")
        try:
            _assert_silent_allow(_run(proj, _write(path)))
            _assert_silent_allow(_run(proj, _edit(path)))
            _assert_silent_allow(_run(proj, _multiedit(path)))
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    def test_every_default_entry_allowed_at_every_phase(self):
        """The policy is 'never gated at any phase': sweep the whole pipeline
        with the hook's own phase list and its own default entries."""
        for phase in hook.PHASE_ORDER:
            proj = _make_project(current_phase=phase)
            try:
                for entry in hook.DEFAULT_GATE_EXEMPT_PATHS:
                    for target in (entry, f"{entry}/nested/file.md"):
                        verdict = _decide(proj, _write(target))
                        assert verdict == (True, ""), (phase, target, verdict)
            finally:
                shutil.rmtree(proj, ignore_errors=True)

    def test_meta_write_is_in_every_phase_policy(self):
        for phase in hook.PHASE_ORDER:
            assert "meta-write" in hook.PHASE_TOOL_POLICY[phase], phase
        assert hook.first_authorizing_phase("meta-write") == hook.PHASE_ORDER[0]

    def test_fresh_bootstrap_phase_0_gives_no_advisory_for_comms(self):
        """wb-bootstrap seeds `current_phase: 0`, which is not a pipeline phase
        (the hook soft-allows everything with an advisory). A comms write must
        not be nagged about that."""
        proj = _make_project(current_phase="0")
        try:
            _assert_silent_allow(_run(proj, _write(COMMS_MESSAGE)))
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    # ---- path spellings: CC sends absolute paths; Windows sends backslashes -- #

    def test_absolute_target_inside_project_allowed(self):
        proj = _make_project(current_phase="1")
        try:
            target = str(proj.resolve() / "comms" / "2026-10-09" / "x.md")
            _assert_silent_allow(_run(proj, _write(target)))
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    @pytest.mark.parametrize(
        "path",
        [
            "./comms/2026-10-09/x.md",
            "comms\\2026-10-09\\x.md",
            ".\\docs\\STATE.md",
            "docs//STATE.md",
        ],
    )
    def test_relative_spellings_allowed(self, path):
        proj = _make_project(current_phase="1")
        try:
            _assert_silent_allow(_run(proj, _write(path)))
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    @pytest.mark.skipif(os.name != "nt", reason="drive-letter case folding is Windows-only")
    def test_absolute_target_with_other_drive_case_allowed(self):
        proj = _make_project(current_phase="1")
        try:
            target = str(proj.resolve() / "docs" / "STATE.md")
            flipped = target[0].swapcase() + target[1:]
            assert flipped != target
            _assert_silent_allow(_run(proj, _write(flipped)))
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    # ---- the deny side: the exemption must not become a hole ---------------- #

    def test_code_write_still_blocked_at_phase_1(self):
        proj = _make_project(current_phase="1")
        try:
            proc = _run(proj, _write("src/app/page.tsx"))
            _assert_block(proc)
            assert "phase 18" in proc.stderr
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    @pytest.mark.parametrize(
        "path",
        [
            "comms/../src/app/page.tsx",   # climbs out of an exempt dir
            "docs/../../outside/x.md",     # climbs out of the project
            "commsx/a.md",                 # shares a prefix, is not under comms/
            "docs.tsx",                    # same
            "src/CLAUDE.md",               # entries are project-root-relative
            "app/README.md",
        ],
    )
    def test_look_alikes_and_traversal_still_blocked(self, path):
        proj = _make_project(current_phase="1")
        try:
            _assert_block(_run(proj, _write(path)))
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    def test_absolute_target_outside_project_blocked(self):
        proj = _make_project(current_phase="1")
        other = _make_project(state=False)
        try:
            target = str(other.resolve() / "comms" / "x.md")
            _assert_block(_run(proj, _write(target)))
        finally:
            shutil.rmtree(proj, ignore_errors=True)
            shutil.rmtree(other, ignore_errors=True)


class TestGateExemptConfig:
    """`gate_exempt_paths` / `gate_exempt_defaults` in project.yaml."""

    EXTRA = "notes/2026-10-09/idea.md"

    def test_unlisted_path_blocked_without_config(self):
        proj = _make_project(current_phase="1")
        try:
            _assert_block(_run(proj, _write(self.EXTRA)))
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    @pytest.mark.parametrize(
        "yaml_lines",
        [
            ["gate_exempt_paths: [notes, \"assets/drafts\"]  # inline flow list"],
            ["gate_exempt_paths:", "  - notes", "  - assets/drafts"],
            ["gate_exempt_paths:", "- notes", "- assets/drafts"],   # PyYAML safe_dump
            ["gate_exempt_paths:", "  - ./notes/   # trailing slash, ./"],
            ["gate_exempt_paths: notes"],                            # bare scalar
        ],
    )
    def test_every_list_spelling_is_honored(self, yaml_lines):
        proj = _make_project(current_phase="1", extra_yaml=yaml_lines)
        try:
            _assert_silent_allow(_run(proj, _write(self.EXTRA)))
            # the project list is added to the defaults, not a replacement
            _assert_silent_allow(_run(proj, _write(COMMS_MESSAGE)))
            # and it exempts only what it names
            _assert_block(_run(proj, _write("src/app/page.tsx")))
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    def test_list_followed_by_other_keys_stops_at_the_next_key(self):
        proj = _make_project(
            current_phase="1",
            extra_yaml=["gate_exempt_paths:", "- notes", "stack: nextjs", "- src"],
        )
        try:
            assert _decide(proj, _write(self.EXTRA)) == (True, "")
            assert _decide(proj, _write("src/app/page.tsx"))[0] is False
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    @pytest.mark.parametrize("off", ["false", "False", "no", "off", "0"])
    def test_defaults_can_be_switched_off(self, off):
        """A site published from docs/ must be able to keep docs/ gated."""
        proj = _make_project(
            current_phase="1",
            extra_yaml=[f"gate_exempt_defaults: {off}", "gate_exempt_paths: [comms]"],
        )
        try:
            assert _decide(proj, _write(COMMS_MESSAGE)) == (True, "")
            verdict = _decide(proj, _write("docs/index.html"))
            assert verdict[0] is False, verdict
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    @pytest.mark.parametrize(
        "entry", [".", "./", "/", "..", "../outside", "C:/", "\"\"", "''"]
    )
    def test_entries_that_would_exempt_everything_are_ignored(self, entry):
        proj = _make_project(
            current_phase="1", extra_yaml=[f"gate_exempt_paths: [{entry}]"]
        )
        try:
            verdict = _decide(proj, _write("src/app/page.tsx"))
            assert verdict[0] is False, (entry, verdict)
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    def test_effective_entries_are_the_defaults_plus_the_project_list(self):
        proj = _make_project(
            current_phase="1", extra_yaml=["gate_exempt_paths: [notes, comms]"]
        )
        try:
            got = hook.effective_exempt_paths(hook.read_project_state(proj), proj)
            assert got == (*hook.DEFAULT_GATE_EXEMPT_PATHS, "notes")  # comms deduped
        finally:
            shutil.rmtree(proj, ignore_errors=True)


class TestReadYamlList:
    @pytest.mark.parametrize(
        "text, expected",
        [
            ("k: [a, b]\n", ["a", "b"]),
            ("k: ['a b', \"c\"]\n", ["a b", "c"]),
            ("k: []\n", []),
            ("k:\n  - a\n  - b\nother: 1\n", ["a", "b"]),
            ("k:\n- a\n- b\nother: 1\n", ["a", "b"]),
            ("k:\n  # note\n  - a\n\n  - b  # tail\n", ["a", "b"]),
            ("k: a\n", ["a"]),
            ("other: 1\n", []),
            ("  k: [nested]\n", []),            # only top-level keys
            ("kk: [a]\nk: [b]\n", ["b"]),       # exact key, not a prefix
            ("", []),
        ],
    )
    def test_shapes(self, tmp_path, text, expected):
        f = tmp_path / "project.yaml"
        f.write_text(text, encoding="utf-8")
        assert hook.read_yaml_list(f, "k") == expected

    def test_missing_file(self, tmp_path):
        assert hook.read_yaml_list(tmp_path / "nope.yaml", "k") == []

    def test_non_utf8_file_degrades_to_empty(self, tmp_path):
        f = tmp_path / "project.yaml"
        f.write_bytes(b"k: [\xff\xfe]\n")
        assert hook.read_yaml_list(f, "k") == []


class TestGitShipsCommsMessage:
    """Sending a comms message is `git add` + `git commit` + `git push`; none of
    that is a build or a deploy."""

    @pytest.mark.parametrize(
        "cmd",
        [
            "git add comms/2026-10-09/x.md",
            "git commit -- comms/x.md",
            "git commit -m \"comms: ole to jules\" -- comms/x.md",
            "git push origin main",
            "git pull --rebase origin main && git add comms/x.md && "
            "git commit -m 'comms: x' -- comms/x.md && git push origin main",
            # a message about the site's tooling is still just a message
            "git commit -m \"comms: vercel preview is up, docker not needed\" -- comms/x.md",
            "git commit -m \"$(cat <<'EOF'\ncomms: fix the vercel and netlify notes\n\n"
            "docker is out of scope\nEOF\n)\" -- comms/x.md",
            "git -C . push origin main",
            "GIT_TRACE=1 git push origin main",
        ],
    )
    def test_ship_commands_allowed_at_phase_1(self, cmd):
        proj = _make_project(current_phase="1")
        try:
            _assert_silent_allow(_run(proj, _bash(cmd)))
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    @pytest.mark.parametrize(
        "cmd",
        [
            "vercel --prod",
            "npx vercel deploy",
            "netlify deploy --prod",
            "wrangler deploy",
            "docker compose up",
            "npm run build",
            "pnpm build",
            # a deploy chained after git is still a deploy
            "git commit -m x -- comms/x.md && vercel --prod",
            "git push origin main; npm run build",
            "git push origin main | vercel --prod",
            "git commit -m 'x' \n vercel --prod",
        ],
    )
    def test_real_deploy_and_build_commands_still_blocked_at_phase_1(self, cmd):
        proj = _make_project(current_phase="1")
        try:
            proc = _run(proj, _bash(cmd))
            _assert_block(proc)
            assert "build/deploy" in proc.stderr
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    def test_is_build_deploy_agrees_with_the_regex_for_non_git_commands(self):
        for cmd in ("vercel --prod", "npm run build", "docker ps", "ls -la", "cat x"):
            assert hook.is_build_deploy(cmd) == bool(hook.BUILD_DEPLOY_RE.search(cmd)), cmd

    def test_splitter_keeps_quoted_separators_inside_their_segment(self):
        cmd = "git commit -m \"a; b && c | d\" && ls"
        assert hook._split_shell_segments(cmd) == [
            "git commit -m \"a; b && c | d\"",
            "ls",
        ]


# --------------------------------------------------------------------------- #
# Enforcement: what Claude Code actually receives
#
# The hook's verdict only counts if it reaches Claude Code. Two things used to
# stop that, and the pytest suite above could not see either (it calls the hook
# directly): (1) the deny JSON lacked `hookEventName` / `permissionDecisionReason`
# and Claude Code 2.1.295 ignored it; (2) hooks.json ran `python3 X || python X
# || py X`, so the exit 2 of a block started the next interpreter on an already
# consumed stdin, which allowed the call and exited 0. These tests run the
# command string from hooks/hooks.json itself, through sh, the way Claude Code
# does (Git Bash on Windows, with ${CLAUDE_PLUGIN_ROOT} in forward-slash form).
# --------------------------------------------------------------------------- #

HOOKS_JSON = PLUGIN_ROOT / "hooks" / "hooks.json"
SH = shutil.which("sh")
needs_sh = pytest.mark.skipif(SH is None, reason="no POSIX sh on PATH")


def _hook_command(event: str) -> str:
    cfg = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
    return cfg["hooks"][event][0]["hooks"][0]["command"]


def _run_configured(
    event: str,
    cwd: Path,
    stdin: str,
    *,
    path: str | None = None,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    """Run hooks/hooks.json's command for `event` as Claude Code does.

    With `path` the child runs on that PATH only; the command's leading `sh` is
    then spelled as its absolute path so the private PATH needs no `sh` in it."""
    assert SH is not None
    command = _hook_command(event)
    env = {**os.environ, "CLAUDE_PLUGIN_ROOT": PLUGIN_ROOT.as_posix()}
    if path is not None:
        assert command.startswith("sh ")
        command = f'"{Path(SH).as_posix()}" ' + command[len("sh "):]
        env["PATH"] = path
    env.update(extra_env or {})
    return subprocess.run(
        [SH, "-c", command],
        input=stdin,
        capture_output=True,
        text=True,
        env=env,
        cwd=str(cwd),
        timeout=60,
    )


class TestBlockEmission:
    """The deny output follows the documented Claude Code contract."""

    def test_deny_json_carries_event_name_decision_and_reason(self):
        proj = _make_project(current_phase="1")
        try:
            proc = _run(proj, _write("src/app/page.tsx"))
            _assert_block(proc)
            out = json.loads(proc.stdout.strip())
            hso = out["hookSpecificOutput"]
            assert hso["hookEventName"] == "PreToolUse"
            assert hso["permissionDecision"] == "deny"
            assert hso["permissionDecisionReason"].startswith(
                "⛔ website-builder anti-skip: BLOCKED"
            )
            assert "src/app/page.tsx" in hso["permissionDecisionReason"]
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    def test_advisory_allow_never_carries_a_permission_decision(self):
        """`allow` with a hookEventName auto-approves the call and skips the
        user's permission prompt; an advisory must not do that."""
        proj = _make_project(current_phase=None)  # degraded state -> advisory
        try:
            proc = _run(proj, _edit("src/components/Hero.tsx"))
            _assert_allow(proc)
            out = json.loads(proc.stdout.strip())
            assert "current_phase" in out["systemMessage"]
            assert "hookSpecificOutput" not in out
        finally:
            shutil.rmtree(proj, ignore_errors=True)


@needs_sh
class TestConfiguredHookLauncher:
    """The command strings in hooks/hooks.json, run through sh."""

    @pytest.mark.parametrize("event", ["SessionStart", "PreToolUse", "PostToolUse"])
    def test_every_hook_goes_through_the_launcher_and_has_no_fallback_chain(self, event):
        command = _hook_command(event)
        assert "hooks-handlers/run.sh" in command
        assert "||" not in command, (
            "a `||` interpreter chain re-runs the handler on a non-zero exit "
            "with stdin already consumed"
        )

    def test_block_keeps_exit_2_and_the_payload_reaches_the_handler(self):
        proj = _make_project(current_phase="1")
        try:
            proc = _run_configured(
                "PreToolUse", proj, json.dumps(_write("src/app/page.tsx"))
            )
            assert proc.returncode == 2, (proc.returncode, proc.stdout, proc.stderr)
            out = json.loads(proc.stdout.strip().splitlines()[0])
            # the verdict names the target: the handler really read the payload
            assert "src/app/page.tsx" in out["hookSpecificOutput"]["permissionDecisionReason"]
            assert out["hookSpecificOutput"]["permissionDecision"] == "deny"
            assert "BLOCKED" in proc.stderr
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    def test_permit_keeps_exit_0_and_is_silent(self):
        proj = _make_project(current_phase="1")
        try:
            proc = _run_configured("PreToolUse", proj, json.dumps(_write(COMMS_MESSAGE)))
            assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
            assert proc.stdout.strip() == ""
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    def test_session_start_and_post_tool_use_run_clean(self):
        proj = _make_project(current_phase="1")
        try:
            start = _run_configured("SessionStart", proj, "")
            assert start.returncode == 0, (start.returncode, start.stderr)
            assert "website-builder" in start.stdout
            post = _run_configured("PostToolUse", proj, json.dumps(_write(COMMS_MESSAGE)))
            assert post.returncode == 0, (post.returncode, post.stderr)
        finally:
            shutil.rmtree(proj, ignore_errors=True)

    # ---- interpreter selection, with stand-in interpreters on a private PATH -- #

    @staticmethod
    def _fake(bin_dir: Path, name: str, *, version_line: str, version_exit: int = 0,
              run_exit: int = 0, log: Path | None = None, tag: str = "") -> None:
        """A stand-in `python3`/`python`: `-V` prints `version_line`; anything
        else logs `tag` plus the first stdin line to `log` and exits `run_exit`."""
        script = (
            "#!/bin/sh\n"
            'if [ "$1" = "-V" ] || [ "$2" = "-V" ]; then\n'   # `python -V` / `py -3 -V`
            f"  echo '{version_line}'\n"
            f"  exit {version_exit}\n"
            "fi\n"
            "IFS= read -r line\n"
            f"echo '{tag}' >> '{log.as_posix() if log else '/dev/null'}'\n"
            f"echo \"$line\" >> '{log.as_posix() if log else '/dev/null'}'\n"
            f"exit {run_exit}\n"
        )
        path = bin_dir / name
        path.write_text(script, encoding="utf-8", newline="\n")
        path.chmod(0o755)

    def test_handler_runs_once_and_its_exit_code_survives(self, tmp_path):
        """The first working interpreter runs the handler; its exit 2 is the
        launcher's; no later candidate is started."""
        bin_dir, log = tmp_path / "bin", tmp_path / "calls.log"
        bin_dir.mkdir()
        self._fake(bin_dir, "python3", version_line="Python 3.99.0", run_exit=2,
                   log=log, tag="python3-ran")
        self._fake(bin_dir, "python", version_line="Python 3.99.0", run_exit=0,
                   log=log, tag="WRONG-second-interpreter-ran")
        payload = '{"tool_name":"Write","tool_input":{"file_path":"x"}}'
        proc = _run_configured("PreToolUse", tmp_path, payload + "\n", path=str(bin_dir))
        assert proc.returncode == 2, (proc.returncode, proc.stdout, proc.stderr)
        assert log.read_text(encoding="utf-8").splitlines() == ["python3-ran", payload]

    def test_store_stub_and_python2_are_skipped(self, tmp_path):
        """A python3 that only opens the Store (non-zero `-V`) and a Python 2
        `python` are passed over."""
        bin_dir, log = tmp_path / "bin", tmp_path / "calls.log"
        bin_dir.mkdir()
        self._fake(bin_dir, "python3", version_line="Python was not found; run without "
                   "arguments to install from the Microsoft Store", version_exit=49,
                   log=log, tag="WRONG-stub-ran")
        self._fake(bin_dir, "python", version_line="Python 2.7.18", log=log,
                   tag="WRONG-python2-ran")
        self._fake(bin_dir, "py", version_line="Python 3.99.0", log=log, tag="py-ran")
        proc = _run_configured("PreToolUse", tmp_path, "payload\n", path=str(bin_dir))
        assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
        assert log.read_text(encoding="utf-8").splitlines() == ["py-ran", "payload"]

    def test_no_usable_interpreter_is_a_non_blocking_error_not_a_block(self, tmp_path):
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        self._fake(bin_dir, "python", version_line="Python 2.7.18")
        proc = _run_configured("PreToolUse", tmp_path, "{}", path=str(bin_dir))
        assert proc.returncode == 1, (proc.returncode, proc.stdout, proc.stderr)
        assert "no Python 3 interpreter" in proc.stderr
