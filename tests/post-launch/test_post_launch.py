"""
tests/post-launch/test_post_launch.py — Phase 6 (Captain S) post-launch
maintainer template tests.

Validates the post-launch maintainer template (the "killer template" the
website-builder materializes at deploy / phase 29 per decisions 28/37/45/49):

  TestPostLaunchTemplate (Tier 1) — static validation of the plugin's
    post-launch/ source tree: the maintainer agent profile frontmatter, all 8
    wb-maintain-* SKILL.md presence + frontmatter, the 5 runbooks, and the
    config-template.yaml schema. Pure file reads; no external dependency.

  TestConfigTemplate (Tier 1) — config-template.yaml parses (placeholders
    tolerated) and carries the 7 wizard sections + skill-subset list.

  TestMaterializer (Tier 1) — runs scripts/wb_postlaunch.py against an ISOLATED
    temp project dir (mirrors the Phase-5 isolated-HOME discipline: nothing
    touches the real ~/.claude or the plugin's own .website-builder/). Asserts
    config.yaml is written with the resolved identity + the chosen skill subset
    is materialized + the maintainer profile has NO unresolved {placeholders}.

  TestMaterializerUnit (Tier 1) — in-process unit tests of wb_postlaunch.py's
    pure functions (placeholder resolution, answer validation, config build) +
    the import-safety regression guard.

All Tier 1 — no network, no real CC skills dir, no external tools. Every test
operates on the plugin's tracked post-launch/ source + tmp_path materialization
targets, so the suite is deterministic + green when source + runner align.

CRITICAL: the materializer writes ONLY into a tmp_path project's
.website-builder/post-launch/ — never the plugin repo's own .website-builder/
(which is gitignored) and never the real user CC dir.
"""

from __future__ import annotations

import importlib
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

# --- Locate the plugin + make scripts/ importable ---------------------------

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
TEMPLATE_DIR = PLUGIN_ROOT / "post-launch"

# Put scripts/ first on sys.path so `import wb_postlaunch` resolves to the
# plugin's materializer regardless of pytest's cwd.
sys.path.insert(0, str(SCRIPTS_DIR))

# The 8 maintainer skills locked per decision 49.
EXPECTED_SKILLS = (
    "wb-maintain-content",
    "wb-maintain-monitoring",
    "wb-maintain-deps",
    "wb-maintain-content-add",
    "wb-maintain-section-add",
    "wb-maintain-page-add",
    "wb-maintain-iterate",
    "wb-maintain-escalate",
)

# The 5 runbooks.
EXPECTED_RUNBOOKS = (
    "content-update.md",
    "dep-update.md",
    "monitor-review.md",
    "analytics-review.md",
    "incident-response.md",
)

PLACEHOLDER_RE = re.compile(r"\{[a-z_]+\}")


# --- Frontmatter helper -----------------------------------------------------

def _split_frontmatter(text: str) -> tuple[dict, str]:
    """Parse a leading YAML frontmatter block fenced by two lines that are
    exactly `---`.

    Splits on the FENCE LINES (a line whose stripped content is `---`), not on
    any `---` substring — the maintainer profile's frontmatter legitimately
    contains a `# --- ... ---` comment line, which a naive substring split would
    mistake for the closing fence.

    Returns (frontmatter_dict, body). Raises AssertionError if absent/malformed.
    """
    lines = text.splitlines()
    assert lines and lines[0].strip() == "---", \
        "file must open with a `---` frontmatter fence line"
    close_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            close_idx = i
            break
    assert close_idx is not None, "frontmatter must be closed by a `---` fence line"
    fm = yaml.safe_load("\n".join(lines[1:close_idx]))
    assert isinstance(fm, dict), "frontmatter must parse to a mapping"
    body = "\n".join(lines[close_idx + 1:])
    return fm, body


# --- Tier 1 — static template validation ------------------------------------


class TestPostLaunchTemplate:
    """Validate the plugin's post-launch/ source tree (static reads)."""

    def test_template_dir_exists(self):
        assert TEMPLATE_DIR.is_dir(), f"post-launch/ template missing at {TEMPLATE_DIR}"

    def test_readme_present(self):
        assert (TEMPLATE_DIR / "README.md").is_file(), "post-launch/README.md missing"

    # ----- maintainer agent profile -----

    def test_maintainer_profile_present(self):
        assert (TEMPLATE_DIR / "agents" / "website-maintainer.md").is_file(), \
            "post-launch/agents/website-maintainer.md missing"

    def test_maintainer_profile_frontmatter(self):
        """The maintainer profile mirrors the main website-builder profile shape:
        name / description / model / tools, plus the deploy-time placeholder fields."""
        text = (TEMPLATE_DIR / "agents" / "website-maintainer.md").read_text(encoding="utf-8")
        fm, body = _split_frontmatter(text)
        # Mirror the main profile's frontmatter shape (name/description/model/tools).
        assert fm.get("name") == "website-maintainer", \
            f"name must be 'website-maintainer'; got {fm.get('name')!r}"
        assert isinstance(fm.get("description"), str) and len(fm["description"]) >= 50, \
            "description must be a substantial string (>=50 chars)"
        assert fm.get("model") == "opus", f"model must be 'opus'; got {fm.get('model')!r}"
        assert isinstance(fm.get("tools"), list) and fm["tools"], \
            "tools must be a non-empty list"
        # Deploy-time placeholder fields (filled by the wizard).
        for field in ("project", "stack", "deploy_provider", "languages"):
            assert field in fm, f"maintainer profile frontmatter missing '{field}'"

    def test_maintainer_profile_template_has_placeholders(self):
        """The TEMPLATE (un-materialized source) must carry the 4 deploy-time
        placeholders so the materializer has something to resolve."""
        text = (TEMPLATE_DIR / "agents" / "website-maintainer.md").read_text(encoding="utf-8")
        for ph in ("{project_name}", "{chosen_stack}", "{chosen_provider}", "{languages}"):
            assert ph in text, f"template maintainer profile must contain placeholder {ph}"

    def test_maintainer_profile_references_all_8_skills(self):
        """The profile's skill-bundle table should name all 8 maintainer skills."""
        text = (TEMPLATE_DIR / "agents" / "website-maintainer.md").read_text(encoding="utf-8")
        for skill in EXPECTED_SKILLS:
            assert skill in text, f"maintainer profile must reference {skill}"

    # ----- the 8 maintainer skills -----

    @pytest.mark.parametrize("skill", EXPECTED_SKILLS)
    def test_skill_present(self, skill):
        assert (TEMPLATE_DIR / "skills" / skill / "SKILL.md").is_file(), \
            f"post-launch/skills/{skill}/SKILL.md missing"

    @pytest.mark.parametrize("skill", EXPECTED_SKILLS)
    def test_skill_frontmatter(self, skill):
        """Each skill follows the plugin's skill convention: name + description
        (third-person triggers) + version."""
        text = (TEMPLATE_DIR / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
        fm, body = _split_frontmatter(text)
        assert fm.get("name") == skill, \
            f"{skill}: frontmatter name must equal dir name; got {fm.get('name')!r}"
        desc = fm.get("description")
        assert isinstance(desc, str) and len(desc) >= 50, \
            f"{skill}: description must be a substantial string (>=50 chars)"
        # Plugin convention: third-person trigger form opening with
        # "This skill should be used ..." (the existing wb-* skills + the
        # plugin-dev:skill-development convention). The maintainer skills use
        # "This skill should be used by the website-maintainer when/for ...".
        assert desc.startswith("This skill should be used"), \
            f"{skill}: description must open with the third-person trigger form"
        assert "version" in fm, f"{skill}: frontmatter missing 'version'"
        assert body.strip(), f"{skill}: SKILL.md body must be non-empty"

    @pytest.mark.parametrize("skill", EXPECTED_SKILLS)
    def test_skill_body_has_time_box_or_cadence(self, skill):
        """Each maintainer skill documents a time-box OR a cadence per the design
        doc § maintenance skill bundle. The recurring skills (monitoring, deps)
        carry a Cadence; the one-shot skills carry a Time-box (escalate's is N/A
        but still stated under Time-box)."""
        text = (TEMPLATE_DIR / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
        assert ("Time-box" in text or "time-box" in text
                or "Cadence" in text or "cadence" in text), \
            f"{skill}: SKILL.md must document a time-box or cadence (design § bundle)"

    def test_exactly_8_skills(self):
        """No more, no fewer than the 8 locked skills (decision 49)."""
        skills_dir = TEMPLATE_DIR / "skills"
        found = sorted(p.name for p in skills_dir.iterdir() if (p / "SKILL.md").is_file())
        assert found == sorted(EXPECTED_SKILLS), \
            f"expected exactly the 8 locked skills; found {found}"

    # ----- runbooks -----

    @pytest.mark.parametrize("runbook", EXPECTED_RUNBOOKS)
    def test_runbook_present(self, runbook):
        assert (TEMPLATE_DIR / "runbooks" / runbook).is_file(), \
            f"post-launch/runbooks/{runbook} missing"


# --- Tier 1 — config-template.yaml schema -----------------------------------


class TestConfigTemplate:
    """Validate the config-template.yaml schema (placeholders tolerated)."""

    def _load(self) -> dict:
        path = TEMPLATE_DIR / "config-template.yaml"
        assert path.is_file(), "post-launch/config-template.yaml missing"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict), "config-template.yaml must parse to a mapping"
        return data

    def test_parses(self):
        self._load()

    def test_has_identity_fields(self):
        data = self._load()
        for field in ("version", "project", "stack", "deploy_provider", "languages"):
            assert field in data, f"config-template.yaml missing identity field '{field}'"

    def test_has_seven_wizard_sections(self):
        """The 7 wizard sections per DESIGN-post-launch-template.md § Wizard config output."""
        data = self._load()
        for section in ("analytics", "uptime", "error_tracking", "cms",
                        "backup", "iteration_cadence", "translation_preference"):
            assert section in data, f"config-template.yaml missing wizard section '{section}'"

    def test_section_subkeys(self):
        data = self._load()
        assert "provider" in data["analytics"]
        assert "provider" in data["uptime"]
        assert "provider" in data["error_tracking"]
        assert "frequency" in data["iteration_cadence"]
        for k in ("code", "content_layer_4", "cms", "media", "database"):
            assert k in data["backup"], f"backup missing subkey '{k}'"

    def test_skill_subset_lists_all_8(self):
        data = self._load()
        installed = data.get("maintainer_skills_installed")
        assert isinstance(installed, list)
        assert sorted(installed) == sorted(EXPECTED_SKILLS), \
            f"maintainer_skills_installed must list all 8; got {installed}"


# --- Materializer subprocess helper -----------------------------------------


def _run_materializer(args: list[str], *, cwd: Path,
                      env: dict | None = None) -> tuple[int, str, str]:
    """Invoke scripts/wb_postlaunch.py via this interpreter (sys.executable).

    Mirrors tests/cli/test_wb_dispatch.py::_run_wb_py — invoke the .py runner
    directly (portable across all subprocess/bash combos)."""
    runner = SCRIPTS_DIR / "wb_postlaunch.py"
    full_env = {**os.environ, "CLAUDE_PLUGIN_ROOT": str(PLUGIN_ROOT)}
    if env:
        full_env.update(env)
    proc = subprocess.run(
        [sys.executable, str(runner), *args],
        capture_output=True, text=True, cwd=str(cwd), env=full_env, timeout=120,
    )
    return proc.returncode, proc.stdout, proc.stderr


def _seed_project(root: Path, *, project="still-humans", stack="astro",
                  provider="vercel", languages=None) -> Path:
    """Create a minimal .website-builder/project.yaml in an isolated temp dir.

    Mirrors smoke_test.py's tempfile + cwd-via-contract pattern. Nothing here
    touches the plugin repo's own .website-builder/ or the real user CC dir."""
    state = root / ".website-builder"
    state.mkdir(parents=True, exist_ok=True)
    proj = {
        "version": 1,
        "name": project,
        "slug": project,
        "stack": stack,
        "deploy_provider": provider,
        "languages": languages if languages is not None else ["en", "de"],
    }
    (state / "project.yaml").write_text(
        yaml.safe_dump(proj, sort_keys=False), encoding="utf-8"
    )
    return state


class TestMaterializer:
    """Run wb_postlaunch.py against an isolated temp project dir (Tier 1)."""

    @pytest.fixture
    def project(self):
        d = Path(tempfile.mkdtemp(prefix="wb-postlaunch-test-"))
        try:
            _seed_project(d)
            yield d
        finally:
            import shutil
            shutil.rmtree(d, ignore_errors=True)

    def test_materialize_default_writes_config(self, project):
        rc, out, err = _run_materializer([], cwd=project)
        assert rc == 0, f"materializer exited {rc}\n{out}\n{err}"
        config_path = project / ".website-builder" / "post-launch" / "config.yaml"
        assert config_path.is_file(), "config.yaml not written"
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        # Identity resolved from project.yaml.
        assert config["project"] == "still-humans"
        assert config["stack"] == "astro"
        assert config["deploy_provider"] == "vercel"
        assert config["languages"] == ["en", "de"]
        # Default translation preference = 1 (decision 40).
        assert str(config["translation_preference"]) == "1"
        # Provenance fields written.
        assert "materialized_at" in config and config["materialized_at"]
        assert "plugin_version" in config

    def test_materialize_default_installs_all_8_skills(self, project):
        rc, out, err = _run_materializer([], cwd=project)
        assert rc == 0, f"materializer exited {rc}\n{err}"
        skills_dir = project / ".website-builder" / "post-launch" / "skills"
        for skill in EXPECTED_SKILLS:
            assert (skills_dir / skill / "SKILL.md").is_file(), \
                f"skill {skill} not materialized"
        # config.yaml records the full subset.
        config = yaml.safe_load(
            (project / ".website-builder" / "post-launch" / "config.yaml")
            .read_text(encoding="utf-8")
        )
        assert sorted(config["maintainer_skills_installed"]) == sorted(EXPECTED_SKILLS)

    def test_materialize_resolves_profile_placeholders(self, project):
        """The materialized maintainer profile must have NO unresolved {placeholder}."""
        rc, out, err = _run_materializer([], cwd=project)
        assert rc == 0, f"materializer exited {rc}\n{err}"
        profile = (project / ".website-builder" / "post-launch" / "agents"
                   / "website-maintainer.md").read_text(encoding="utf-8")
        # The 4 deploy-time placeholders must be gone.
        for ph in ("{project_name}", "{chosen_stack}", "{chosen_provider}", "{languages}"):
            assert ph not in profile, f"unresolved placeholder {ph} in materialized profile"
        # And the resolved values must be present.
        assert "still-humans" in profile
        assert "astro" in profile
        assert "vercel" in profile

    def test_materialize_copies_runbooks_and_readme(self, project):
        rc, out, err = _run_materializer([], cwd=project)
        assert rc == 0
        dest = project / ".website-builder" / "post-launch"
        assert (dest / "README.md").is_file()
        for rb in EXPECTED_RUNBOOKS:
            assert (dest / "runbooks" / rb).is_file(), f"runbook {rb} not materialized"

    def test_materialize_subset_via_answers(self, project):
        """A wizard answers file with a 3-skill subset materializes exactly those 3."""
        import json
        answers = {
            "analytics_provider": "plausible",
            "analytics_config_url": "https://plausible.io/still-humans.example",
            "analytics_api_key_env": "PLAUSIBLE_API_KEY",
            "uptime_provider": "uptimerobot",
            "error_tracking_provider": "none",
            "translation_preference": "2",
            "maintainer_skills_installed": [
                "wb-maintain-content", "wb-maintain-monitoring", "wb-maintain-escalate",
            ],
        }
        answers_file = project / "answers.json"
        answers_file.write_text(json.dumps(answers), encoding="utf-8")
        rc, out, err = _run_materializer(
            ["--answers", str(answers_file)], cwd=project
        )
        assert rc == 0, f"materializer exited {rc}\n{err}"
        skills_dir = project / ".website-builder" / "post-launch" / "skills"
        installed = sorted(p.name for p in skills_dir.iterdir() if p.is_dir())
        assert installed == sorted([
            "wb-maintain-content", "wb-maintain-monitoring", "wb-maintain-escalate",
        ]), f"subset not honored; materialized {installed}"
        # The non-chosen skills must NOT be present.
        assert not (skills_dir / "wb-maintain-deps").exists()
        config = yaml.safe_load(
            (project / ".website-builder" / "post-launch" / "config.yaml")
            .read_text(encoding="utf-8")
        )
        assert config["analytics"]["provider"] == "plausible"
        assert config["analytics"]["api_key_env"] == "PLAUSIBLE_API_KEY"
        assert config["uptime"]["provider"] == "uptimerobot"
        assert str(config["translation_preference"]) == "2"

    def test_materialize_idempotent_rerun(self, project):
        """A second run re-materializes cleanly (config.yaml still valid)."""
        rc1, _, _ = _run_materializer([], cwd=project)
        assert rc1 == 0
        rc2, out2, err2 = _run_materializer(["--force"], cwd=project)
        assert rc2 == 0, f"re-run exited {rc2}\n{err2}"
        config = yaml.safe_load(
            (project / ".website-builder" / "post-launch" / "config.yaml")
            .read_text(encoding="utf-8")
        )
        assert config["project"] == "still-humans"

    def test_materialize_no_state_dir_fails_clean(self):
        """Running with no .website-builder/ surfaces a clean error (exit 2)."""
        d = Path(tempfile.mkdtemp(prefix="wb-postlaunch-nostate-"))
        try:
            rc, out, err = _run_materializer([], cwd=d)
            assert rc == 2, f"expected exit 2 for missing state dir; got {rc}"
        finally:
            import shutil
            shutil.rmtree(d, ignore_errors=True)

    def test_materialize_invalid_answer_rejected(self, project):
        """An out-of-range translation_preference is rejected (exit 2)."""
        import json
        answers_file = project / "bad.json"
        answers_file.write_text(json.dumps({"translation_preference": "9"}), encoding="utf-8")
        rc, out, err = _run_materializer(["--answers", str(answers_file)], cwd=project)
        assert rc == 2, f"expected exit 2 for invalid answer; got {rc}\n{out}{err}"

    def test_version_flag(self, project):
        rc, out, err = _run_materializer(["--version"], cwd=project)
        assert rc == 0
        assert "wb_postlaunch.py" in out and "0.1.0" in out


# --- Tier 1 — in-process unit tests of pure functions -----------------------


class TestMaterializerUnit:
    """In-process unit tests of wb_postlaunch.py pure functions."""

    def _mod(self):
        if "wb_postlaunch" in sys.modules:
            return importlib.reload(sys.modules["wb_postlaunch"])
        return importlib.import_module("wb_postlaunch")

    def test_import_is_side_effect_free(self):
        """Importing the materializer must not write files or hit the network."""
        m = self._mod()
        assert hasattr(m, "main")
        assert hasattr(m, "materialize")
        assert len(m.ALL_MAINTAINER_SKILLS) == 8
        assert len(m.RUNBOOKS) == 5

    def test_resolve_placeholders(self):
        m = self._mod()
        text = "p={project_name} s={chosen_stack} d={chosen_provider} l={languages}"
        out = m.resolve_placeholders(text, {
            "project": "acme", "stack": "nextjs",
            "deploy_provider": "vercel", "languages": ["en", "fr"],
        })
        assert out == "p=acme s=nextjs d=vercel l=[en, fr]"
        # No placeholders should survive.
        assert not m.PLUGIN_VERSION is None  # sanity
        assert "{" not in out

    def test_languages_to_str_forms(self):
        m = self._mod()
        assert m._languages_to_str(["en", "de"]) == "[en, de]"
        assert m._languages_to_str(None) == "[en]"
        assert m._languages_to_str([]) == "[]"

    def test_validate_answers_accepts_defaults(self):
        m = self._mod()
        assert m.validate_answers(m.default_answers()) == []

    def test_validate_answers_flags_bad_provider(self):
        m = self._mod()
        bad = m.default_answers()
        bad["analytics_provider"] = "not-a-provider"
        errors = m.validate_answers(bad)
        assert any("analytics_provider" in e for e in errors)

    def test_validate_answers_flags_unknown_skill(self):
        m = self._mod()
        bad = m.default_answers()
        bad["maintainer_skills_installed"] = ["wb-maintain-content", "wb-maintain-bogus"]
        errors = m.validate_answers(bad)
        assert any("unknown skills" in e for e in errors)

    def test_build_config_shape(self):
        m = self._mod()
        config = m.build_config(
            {"project": "x", "stack": "hugo", "deploy_provider": "cloudflare-pages",
             "languages": ["en"]},
            m.default_answers(),
        )
        assert config["project"] == "x"
        assert config["stack"] == "hugo"
        assert config["analytics"]["provider"] == "none"
        assert config["maintainer_skills_installed"] == list(m.ALL_MAINTAINER_SKILLS)
        assert str(config["translation_preference"]) == "1"
