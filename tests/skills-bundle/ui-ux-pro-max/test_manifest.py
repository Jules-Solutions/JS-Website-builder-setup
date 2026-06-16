"""
Manifest-validation tests for skills-bundle/ui-ux-pro-max.md (Phase 5 / Captain M).

These are Tier-1 tests — pure static validation of the composition manifest, with
NO upstream / network / external-tool dependency. They assert the manifest is the
shape that `wb-bootstrap` (flavor pick + install) and the `wb skills update/sync`
verbs read by exact field name at runtime; schema divergence is silent
skill-orchestration failure (per skills-bundle/README.md § "Why exact field names
matter").

Three concerns (per the Captain M INST + tests/README.md § Phase 5):

  1. Schema conformance — every canonical frontmatter field present + correctly
     typed (per skills-bundle/README.md § "Canonical frontmatter schema") + the 7
     mandatory H2 body sections present in canonical order.
  2. install-skills.sh compatibility — the manifest agrees with the *actual*
     scripts/install-skills.sh (read-only substrate): skill_name matches the
     KNOWN_SKILLS row id, install_method maps to the script's method token, and the
     resolved install_target_path matches the script's cc_skills_dir convention.
  3. Upstream-URL well-formedness — upstream_url is a syntactically valid https URL
     (no live fetch — that would be a Tier-2 test).

Run via:
  bash tests/run-tests.sh            # default 'all' mode auto-discovers this file
  cd tests && uv run --with pyyaml --with pytest pytest skills-bundle/ -v
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

import pytest
import yaml

# --- Path resolution (cwd-independent; mirrors smoke_test.py) ---------------

# This file lives at tests/skills-bundle/ui-ux-pro-max/test_manifest.py
# Plugin root is three levels up.
PLUGIN_ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = PLUGIN_ROOT / "skills-bundle" / "ui-ux-pro-max.md"
INSTALL_SCRIPT_PATH = PLUGIN_ROOT / "scripts" / "install-skills.sh"

# --- Canonical schema (per skills-bundle/README.md § frontmatter schema) ----

REQUIRED_FRONTMATTER_FIELDS = [
    "type",
    "skill_name",
    "upstream_id",
    "upstream_url",
    "upstream_license",
    "upstream_attribution",
    "install_method",
    "install_target_path",
    "install_size_estimate_mb",
    "required_for_phases",
    "optional_complementary_with",
    "load_order",
    "default_loaded",
]

VALID_INSTALL_METHODS = {"skill-registry", "git-clone", "curl", "platform-specific"}
VALID_LOAD_ORDERS = {"primary", "secondary"}
REQUIRED_OS_KEYS = {"windows", "macos", "linux"}

# The 7 mandatory H2 body sections, in canonical order (per skills-bundle/README.md
# § "Body-section outline").
REQUIRED_BODY_SECTIONS = [
    "What it provides",
    "How the website-builder uses it",
    "Composition rules",
    "Install",
    "Verification",
    "Uninstall",
    "Upstream attribution",
]


# --- Fixtures ---------------------------------------------------------------


def _split_frontmatter(text: str) -> tuple[dict, str]:
    """Split a markdown file into (frontmatter_dict, body_text)."""
    assert text.startswith("---"), "manifest must open with YAML frontmatter delimiter"
    parts = text.split("---", 2)
    assert len(parts) >= 3, "manifest frontmatter must be closed with a second '---'"
    fm = yaml.safe_load(parts[1])
    body = parts[2]
    return fm, body


@pytest.fixture(scope="module")
def manifest_text() -> str:
    assert MANIFEST_PATH.is_file(), f"manifest not found at {MANIFEST_PATH}"
    return MANIFEST_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def frontmatter(manifest_text: str) -> dict:
    fm, _ = _split_frontmatter(manifest_text)
    assert isinstance(fm, dict), "frontmatter must parse to a mapping"
    return fm


@pytest.fixture(scope="module")
def body(manifest_text: str) -> str:
    _, body_text = _split_frontmatter(manifest_text)
    return body_text


@pytest.fixture(scope="module")
def install_script_text() -> str:
    assert INSTALL_SCRIPT_PATH.is_file(), (
        f"install-skills.sh not found at {INSTALL_SCRIPT_PATH}"
    )
    return INSTALL_SCRIPT_PATH.read_text(encoding="utf-8")


# --- Tests ------------------------------------------------------------------


class TestUiuxManifest:
    """Static validation of the UI/UX Pro Max composition manifest."""

    # --- 1. Schema conformance ---

    def test_manifest_file_exists(self):
        assert MANIFEST_PATH.is_file(), (
            "skills-bundle/ui-ux-pro-max.md must exist (Captain M v0.1 deliverable)"
        )

    def test_frontmatter_parses_as_mapping(self, frontmatter: dict):
        assert isinstance(frontmatter, dict)

    @pytest.mark.parametrize("field", REQUIRED_FRONTMATTER_FIELDS)
    def test_required_field_present(self, frontmatter: dict, field: str):
        assert field in frontmatter, (
            f"canonical frontmatter field '{field}' missing — wb-bootstrap / wb "
            f"skills read it by exact name; absence is silent orchestration failure"
        )

    def test_type_is_skill_manifest(self, frontmatter: dict):
        assert frontmatter["type"] == "SKILL_MANIFEST"

    def test_skill_name_matches_filename_basename(self, frontmatter: dict):
        # skill_name MUST equal the manifest filename basename (and the install dir basename).
        assert frontmatter["skill_name"] == MANIFEST_PATH.stem == "ui-ux-pro-max"

    def test_skill_name_is_kebab_case(self, frontmatter: dict):
        assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", frontmatter["skill_name"]), (
            "skill_name must be kebab-case"
        )

    def test_install_method_is_valid_enum(self, frontmatter: dict):
        assert frontmatter["install_method"] in VALID_INSTALL_METHODS

    def test_load_order_is_valid_enum(self, frontmatter: dict):
        assert frontmatter["load_order"] in VALID_LOAD_ORDERS

    def test_default_loaded_is_false_bool(self, frontmatter: dict):
        # Per the schema, all design flavors are default_loaded: false (context-budget).
        assert frontmatter["default_loaded"] is False

    def test_install_target_path_has_all_three_os_keys(self, frontmatter: dict):
        itp = frontmatter["install_target_path"]
        assert isinstance(itp, dict)
        assert set(itp.keys()) == REQUIRED_OS_KEYS, (
            f"install_target_path needs exactly {REQUIRED_OS_KEYS}, got {set(itp.keys())}"
        )

    def test_install_target_paths_end_with_skill_basename(self, frontmatter: dict):
        # All three OS paths must target a dir whose basename == skill_name.
        name = frontmatter["skill_name"]
        for os_key, p in frontmatter["install_target_path"].items():
            assert p.replace("\\", "/").rstrip("/").endswith(f"/{name}"), (
                f"{os_key} install path '{p}' must end with the skill basename '{name}'"
            )

    def test_install_size_estimate_is_number(self, frontmatter: dict):
        assert isinstance(frontmatter["install_size_estimate_mb"], (int, float))
        assert frontmatter["install_size_estimate_mb"] > 0

    def test_required_for_phases_is_int_list(self, frontmatter: dict):
        phases = frontmatter["required_for_phases"]
        assert isinstance(phases, list) and len(phases) > 0
        assert all(isinstance(p, int) for p in phases)

    def test_required_for_phases_matches_design_source(self, frontmatter: dict):
        # Per DESIGN-skill-uiuxpromax.md § "When loaded / invoked": phases 14, 17, 18, 22.
        assert set(frontmatter["required_for_phases"]) == {14, 17, 18, 22}

    def test_optional_complementary_with_is_string_list(self, frontmatter: dict):
        comp = frontmatter["optional_complementary_with"]
        assert isinstance(comp, list)
        assert all(isinstance(c, str) for c in comp)
        # UI/UX Pro Max must NOT list itself as a complementary flavor.
        assert frontmatter["skill_name"] not in comp

    def test_upstream_license_not_unverified(self, frontmatter: dict):
        # The schema permits 'unverified' (flag-in-body); but for a shipped v0.1
        # default the license must be verified. Captain M verified MIT on 2026-06-12.
        assert frontmatter["upstream_license"] not in ("", "unverified", None), (
            "upstream_license must be a verified license string for the v0.1 default"
        )

    def test_upstream_attribution_nonempty(self, frontmatter: dict):
        assert isinstance(frontmatter["upstream_attribution"], str)
        assert frontmatter["upstream_attribution"].strip()

    # --- Body-section presence + order ---

    def test_all_body_sections_present(self, body: str):
        present = re.findall(r"^## (.+?)\s*$", body, flags=re.MULTILINE)
        for section in REQUIRED_BODY_SECTIONS:
            assert section in present, f"mandatory H2 section '## {section}' missing"

    def test_body_sections_in_canonical_order(self, body: str):
        present = re.findall(r"^## (.+?)\s*$", body, flags=re.MULTILINE)
        # Filter to just the mandatory sections, preserving order of appearance.
        ordered = [s for s in present if s in REQUIRED_BODY_SECTIONS]
        assert ordered == REQUIRED_BODY_SECTIONS, (
            f"H2 sections out of canonical order.\n  expected: {REQUIRED_BODY_SECTIONS}\n"
            f"  found:    {ordered}"
        )

    # --- 2. install-skills.sh compatibility (against the ACTUAL read-only script) ---

    def test_install_script_exists(self, install_script_text: str):
        assert "KNOWN_SKILLS" in install_script_text

    def test_skill_name_is_a_known_skill_id(
        self, frontmatter: dict, install_script_text: str
    ):
        # The script's KNOWN_SKILLS rows are pipe-delimited:
        #   ID|name|method|ref|marketplace_source|status|notes  (marketplace_source added Decision 90).
        # The manifest's skill_name must appear as a KNOWN_SKILLS row id (first field).
        name = frontmatter["skill_name"]
        ids = re.findall(r'^\s*"([a-z0-9-]+)\|', install_script_text, flags=re.MULTILINE)
        assert name in ids, (
            f"manifest skill_name '{name}' is not a KNOWN_SKILLS row id in "
            f"install-skills.sh (found ids: {ids}) — wb-bootstrap invokes "
            f"--primary {name} and the script must recognize it"
        )

    def test_install_method_maps_to_script_method_token(
        self, frontmatter: dict, install_script_text: str
    ):
        # Map the manifest's install_method enum onto the script's row method token.
        #   schema enum 'skill-registry' -> script token 'registry'
        #   schema enum 'git-clone'      -> script token 'git'
        method_map = {"skill-registry": "registry", "git-clone": "git"}
        name = frontmatter["skill_name"]
        # Find the KNOWN_SKILLS row for this skill.
        row_match = re.search(
            rf'^\s*"({re.escape(name)}\|[^"]*)"', install_script_text, flags=re.MULTILINE
        )
        assert row_match, f"no KNOWN_SKILLS row for '{name}'"
        row_fields = row_match.group(1).split("|")
        script_method = row_fields[2]  # ID|name|method|ref|marketplace_source|status|notes
        expected = method_map.get(frontmatter["install_method"])
        assert expected is not None, (
            f"install_method '{frontmatter['install_method']}' has no script-token "
            f"mapping; only skill-registry/git-clone are wired in install-skills.sh v0.1"
        )
        assert script_method == expected, (
            f"manifest install_method '{frontmatter['install_method']}' maps to "
            f"script token '{expected}', but install-skills.sh row uses '{script_method}'"
        )

    def test_install_target_path_matches_script_cc_skills_dir(
        self, frontmatter: dict, install_script_text: str
    ):
        # The script resolves the user-level CC skills dir per OS in cc_skills_dir():
        #   macos|linux   -> ${HOME}/.claude/skills
        #   windows-bash  -> ${USERPROFILE:-${HOME}}/.claude/skills
        # then target_dir="${skills_dir}/${SKILL_ID}". The manifest's install_target_path
        # must agree on the .claude/skills/<skill> shape per OS.
        assert "/.claude/skills" in install_script_text
        name = frontmatter["skill_name"]
        itp = frontmatter["install_target_path"]
        for os_key, p in itp.items():
            norm = p.replace("\\", "/")
            assert "/.claude/skills/" in norm, (
                f"{os_key} install path '{p}' must live under .claude/skills/ "
                f"(matches install-skills.sh cc_skills_dir convention)"
            )
            assert norm.rstrip("/").endswith(f"/{name}")

    # --- 3. Upstream-URL well-formedness (no live fetch — Tier 1) ---

    def test_upstream_url_is_valid_https(self, frontmatter: dict):
        url = frontmatter["upstream_url"]
        parsed = urlparse(url)
        assert parsed.scheme == "https", f"upstream_url must be https, got '{url}'"
        assert parsed.netloc, f"upstream_url must have a host, got '{url}'"
        # No whitespace / placeholder leftovers from the schema template.
        assert "SOURCE_REPO_URL_OR_REGISTRY" not in url
        assert " " not in url

    def test_upstream_id_nonempty_for_registry_method(self, frontmatter: dict):
        # When install_method is skill-registry, upstream_id is the marketplace id and
        # must be non-empty (empty string '' is only valid for non-registry installs).
        if frontmatter["install_method"] == "skill-registry":
            assert frontmatter["upstream_id"], (
                "upstream_id must be non-empty when install_method is skill-registry"
            )
