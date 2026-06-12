"""
Stitch extraction end-to-end test (Phase 5 / Captain N scope).

Asserts the input->output contract that BUILD-strategy DoD line 225 names:
"Stitch extraction runs from a URL -> DESIGN.md import works end-to-end."

The "end-to-end" we can assert WITHOUT a live network is the load-bearing
middle of extraction/stitch.md's runtime recipe:

    fixture/stitch-export.md   (a synthetic Stitch DESIGN.md export — the
                                artifact a Path-1 browser-in-loop run pastes back)
        --[ step 4: Normalize ]-->
    expected.yaml              (the normalized brand.yaml/components.yaml/project.yaml
                                shapes the phase-6.5 import produces)

The live-URL crawl (step 2) is documented procedure, not a network test — there
is no programmatic arbitrary-URL extraction surface (see extraction/stitch.md
§ "Ecosystem verification"), so the fixture embodies a representative extraction
output. This makes the test Tier 1: pure parse -> normalize -> assert, always
green when fixture + spec align (mirrors the Phase-1 detector.py reference-impl
pattern + the Phase-3/4 adapter fixture/expected.yaml convention).

The reference normalizer below IS the executable specification of step 4 of the
runtime recipe. If it drifts from extraction/stitch.md's destination table, this
test surfaces the drift.

Run via:
  ./tests/run-tests.sh            (from plugin root — default 'all' mode, no -k filter)
  cd tests && uv run --with pyyaml --with pytest pytest extraction/stitch -v
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

FIXTURE_DIR = Path(__file__).parent / "fixture"
EXPORT_PATH = FIXTURE_DIR / "stitch-export.md"
EXPECTED_PATH = Path(__file__).parent / "expected.yaml"


# --- Reference normalizer (executable spec of runtime-recipe step 4) -------
#
# Parses a Stitch DESIGN.md export into the normalized project-state shapes per
# extraction/stitch.md § "Output schema" destination table. Stdlib-only parsing
# (the agent does this with reasoning at runtime; this is the deterministic
# reference the fixture asserts against). No side effects, no network.

_KV_LINE = re.compile(r"^-\s*([A-Za-z0-9_-]+):\s*(.+?)\s*(?:#.*)?$")
_BOLD_FIELD = re.compile(r"^\*\*([^:]+):\*\*\s*(.+?)\s*$")
_LIST_FIELD = re.compile(r"^-\s*([A-Za-z0-9_-]+):\s*\[(.*)\]\s*$")
_PLAIN_FIELD = re.compile(r"^-\s*([A-Za-z0-9_-]+):\s*(.+?)\s*$")


def _sections(md: str) -> dict[str, list[str]]:
    """Split a DESIGN.md into {heading: [body lines]} for ## and ### headings."""
    out: dict[str, list[str]] = {}
    current: str | None = None
    for raw in md.splitlines():
        line = raw.rstrip()
        m = re.match(r"^(#{2,3})\s+(.+?)\s*$", line)
        if m:
            heading = m.group(2).strip()   # str — the key, never None
            current = heading
            out.setdefault(heading, [])
            continue
        if current is not None:
            out[current].append(line)
    return out


def _split_list(s: str) -> list[str]:
    return [p.strip().strip('"') for p in s.split(",") if p.strip()]


def _split_behaviors(s: str) -> list[str]:
    """Behaviors in a DESIGN.md export are written as a semicolon- or
    comma-separated phrase list ('scroll-triggered reveal; CTA hover lift')."""
    parts = re.split(r"[;,]", s)
    return [p.strip().strip('"') for p in parts if p.strip()]


def _key(name: str) -> str:
    """Normalize a token key: 'on-surface' -> 'on_surface' (YAML-safe)."""
    return name.strip().lower().replace("-", "_")


def normalize_stitch_export(md: str) -> dict:
    """Stitch DESIGN.md export -> normalized project-state shapes.

    Returns a dict with keys: project_yaml, brand_yaml, components_yaml.
    Mirrors extraction/stitch.md § "Output schema" + the destination table.
    Pure function — no I/O, no network.
    """
    secs = _sections(md)

    # --- Brand Identity -> project.yaml voice seed -------------------------
    project_yaml: dict = {"voice_descriptors": []}
    for line in secs.get("Brand Identity", []):
        bm = _BOLD_FIELD.match(line.strip())
        if not bm:
            continue
        field, value = bm.group(1).strip().lower(), bm.group(2).strip()
        if field == "name":
            project_yaml["brand_name"] = value
        elif field == "tagline":
            project_yaml["tagline"] = value
        elif field == "voice":
            project_yaml["voice_descriptors"] = _split_list(value)

    # --- Design Tokens -> brand.yaml.tokens --------------------------------
    tokens: dict = {}

    # Colors
    colors: dict = {}
    for line in secs.get("Colors", []):
        cm = _KV_LINE.match(line.strip())
        if cm:
            colors[_key(cm.group(1))] = cm.group(2).strip()
    if colors:
        tokens["colors"] = colors

    # Typography (display + body blocks with nested sizes/weights/line-height)
    typography = _parse_typography(secs.get("Typography", []))
    if typography:
        tokens["typography"] = typography

    # Spacing
    spacing: dict = {}
    for line in secs.get("Spacing", []):
        lm = _LIST_FIELD.match(line.strip())
        if lm:
            spacing[_key(lm.group(1))] = _split_list(lm.group(2))
            continue
        pm = _PLAIN_FIELD.match(line.strip())
        if pm:
            spacing[_key(pm.group(1))] = pm.group(2).strip()
    if spacing:
        tokens["spacing"] = spacing

    # Motion
    motion: dict = {}
    for line in secs.get("Motion", []):
        pm = _PLAIN_FIELD.match(line.strip())
        if pm:
            motion[_key(pm.group(1))] = pm.group(2).strip()
    if motion:
        tokens["motion"] = motion

    # Dark Mode -> scalar strategy
    for line in secs.get("Dark Mode", []):
        pm = _PLAIN_FIELD.match(line.strip())
        if pm and _key(pm.group(1)) == "strategy":
            tokens["dark_mode"] = pm.group(2).strip()

    brand_yaml = {"tokens": tokens}

    # --- Components -> components.yaml (one entry per ### under Components) -
    components = _parse_components(md)
    components_yaml = {"components": components}

    return {
        "project_yaml": project_yaml,
        "brand_yaml": brand_yaml,
        "components_yaml": components_yaml,
    }


def _parse_typography(lines: list[str]) -> dict:
    """Parse the Typography block: each '- display: ...' starts a face whose
    indented '  - sizes/weights/line-height' lines are its attributes."""
    faces: dict = {}
    current: str | None = None
    for raw in lines:
        if not raw.strip():
            continue
        indent = len(raw) - len(raw.lstrip())
        stripped = raw.strip()
        face_head = re.match(r"^-\s*(display|body):\s*(.+?)\s*$", stripped)
        if indent <= 0 and face_head:
            current = face_head.group(1)
            faces[current] = {"family": face_head.group(2).strip()}
            continue
        if current is None:
            continue
        attr = re.match(r"^-\s*([A-Za-z0-9_-]+):\s*(.+?)\s*$", stripped)
        if not attr:
            continue
        key, val = _key(attr.group(1)), attr.group(2).strip()
        if val.startswith("[") and val.endswith("]"):
            items = _split_list(val[1:-1])
            if key == "weights":
                faces[current][key] = [int(x) for x in items]
            else:
                faces[current][key] = items
        elif key == "line_height":
            faces[current][key] = float(val)
        else:
            faces[current][key] = val
    return faces


def _parse_components(md: str) -> list[dict]:
    """Walk ### headings under the '## Components' section into entries."""
    out: list[dict] = []
    in_components = False
    current: dict | None = None
    for raw in md.splitlines():
        line = raw.rstrip()
        h2 = re.match(r"^##\s+(.+?)\s*$", line)
        if h2:
            in_components = h2.group(1).strip().lower() == "components"
            current = None
            continue
        if not in_components:
            continue
        h3 = re.match(r"^###\s+(.+?)\s*$", line)
        if h3:
            current = {"name": h3.group(1).strip(), "extracted": True,
                       "props": [], "behaviors": []}
            out.append(current)
            continue
        if current is None:
            continue
        field = _PLAIN_FIELD.match(line.strip())
        if not field:
            continue
        key, val = field.group(1).lower(), field.group(2).strip()
        if key == "props":
            current["props"] = _split_list(val)
        elif key == "behaviors":
            current["behaviors"] = [] if val.lower() == "none" else _split_behaviors(val)
        # 'recognized: yes' is implied by presence -> extracted: true; skip.
    return out


# --- Fixtures --------------------------------------------------------------

def _load_expected() -> dict:
    return yaml.safe_load(EXPECTED_PATH.read_text(encoding="utf-8"))


def _normalized() -> dict:
    return normalize_stitch_export(EXPORT_PATH.read_text(encoding="utf-8"))


# --- Tier 1 — Stitch normalization (always runnable, no network) -----------

class TestStitchNormalize:
    """The end-to-end input->output contract: DESIGN.md export -> normalized
    project state. Tier 1 — pure, deterministic, no upstream dependency."""

    def test_fixture_export_exists(self):
        assert EXPORT_PATH.is_file(), f"missing fixture export at {EXPORT_PATH}"

    def test_expected_parses(self):
        exp = _load_expected()
        assert isinstance(exp, dict) and "brand_yaml" in exp

    def test_brand_name_and_voice(self):
        result = _normalized()
        exp = _load_expected()["project_yaml"]
        assert result["project_yaml"]["brand_name"] == exp["brand_name"]
        assert result["project_yaml"]["tagline"] == exp["tagline"]
        assert result["project_yaml"]["voice_descriptors"] == exp["voice_descriptors"]

    def test_colors_normalize(self):
        result = _normalized()["brand_yaml"]["tokens"]["colors"]
        expected = _load_expected()["brand_yaml"]["tokens"]["colors"]
        assert result == expected, (
            f"color normalization drift:\n  got      {result}\n  expected {expected}"
        )

    def test_typography_normalizes(self):
        result = _normalized()["brand_yaml"]["tokens"]["typography"]
        expected = _load_expected()["brand_yaml"]["tokens"]["typography"]
        assert result == expected, (
            f"typography drift:\n  got      {result}\n  expected {expected}"
        )

    def test_spacing_motion_darkmode(self):
        tokens = _normalized()["brand_yaml"]["tokens"]
        exp = _load_expected()["brand_yaml"]["tokens"]
        assert tokens["spacing"] == exp["spacing"]
        assert tokens["motion"] == exp["motion"]
        assert tokens["dark_mode"] == exp["dark_mode"]

    def test_components_normalize(self):
        result = _normalized()["components_yaml"]["components"]
        expected = _load_expected()["components_yaml"]["components"]
        assert result == expected, (
            f"component normalization drift:\n  got      {result}\n  expected {expected}"
        )

    def test_every_component_flagged_extracted(self):
        # DESIGN-extraction-stitch.md § Output format: extracted components get
        # an extracted: true flag. The normalizer must set it on every entry.
        for comp in _normalized()["components_yaml"]["components"]:
            assert comp.get("extracted") is True, (
                f"component {comp.get('name')} missing extracted: true flag"
            )

    def test_full_normalized_shape_matches_expected(self):
        # Whole-document assertion: the three normalized shapes equal the
        # expected.yaml contract end-to-end (the DoD-line-225 assertion).
        result = _normalized()
        exp = _load_expected()
        assert result["project_yaml"]["voice_descriptors"] == exp["project_yaml"]["voice_descriptors"]
        assert result["brand_yaml"] == {"tokens": exp["brand_yaml"]["tokens"]}
        assert result["components_yaml"] == {"components": exp["components_yaml"]["components"]}


class TestStitchFixtureCompleteness:
    """The fixture dir is a complete, self-describing contract (mirrors the
    Phase-1 TestFixtureCompleteness + Phase-3/4 adapter fixture convention)."""

    def test_required_files_present(self):
        assert EXPORT_PATH.is_file(), "fixture/stitch-export.md missing"
        assert EXPECTED_PATH.is_file(), "expected.yaml missing"
        assert (Path(__file__).parent / "README.md").is_file(), "README.md missing"

    def test_normalization_targets_documented(self):
        # expected.yaml records the destination-table mapping; assert it covers
        # every section the normalizer emits (drift guard on the contract).
        targets = _load_expected()["normalization_targets"]
        for key in ("design_tokens_colors", "design_tokens_typography",
                    "design_tokens_spacing", "design_tokens_motion",
                    "design_tokens_dark_mode", "components", "brand_identity_voice"):
            assert key in targets, f"normalization_targets missing {key}"

    def test_no_real_secrets_in_fixture(self):
        # Synthetic-only discipline (secrets-conventions.md): the fixture must
        # not embed anything resembling a real API key.
        text = EXPORT_PATH.read_text(encoding="utf-8")
        assert "STITCH_API_KEY=" not in text
        assert "sk-" not in text
