"""
Unit tests for the content-layer validator (`scripts/wb_validate_layers.py`).
Wave 2 / Captain modules-1 scope (DESIGN-content-layers.md § 351-362 +
DESIGN-orchestration-spine.md § 4.3 action 4).

Fixtures are built inline in pytest's tmp_path (mirrors tests/orchestration/) — no
shipped fixture files, no .gitignore exception needed.

Run:
  bash tests/run-tests.sh
  cd tests && uv run --with pyyaml --with pytest pytest validate-layers/ -v
"""

from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import wb_validate_layers as vl  # noqa: E402  (sys.path mutation must precede)


# --- Fixture helpers --------------------------------------------------------


def _state(tmp_path: Path) -> Path:
    sd = tmp_path / ".website-builder"
    sd.mkdir(parents=True, exist_ok=True)
    return sd


def _project(tmp_path: Path, **fields) -> None:
    sd = _state(tmp_path)
    lines = [f"{k}: {v}" for k, v in fields.items()]
    (sd / "project.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _strings(tmp_path: Path, lang: str, data: dict) -> None:
    d = _state(tmp_path) / "content" / "strings"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{lang}.json").write_text(json.dumps(data), encoding="utf-8")


def _page(tmp_path: Path, name: str, body: str = "", **frontmatter) -> None:
    d = _state(tmp_path) / "content" / "pages"
    d.mkdir(parents=True, exist_ok=True)
    fm = "\n".join(f"{k}: {v}" for k, v in frontmatter.items())
    (d / f"{name}.md").write_text(f"---\n{fm}\n---\n\n{body}\n", encoding="utf-8")


def _write(tmp_path: Path, rel: str, text: str) -> None:
    p = _state(tmp_path) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


# --- Import safety ----------------------------------------------------------


class TestImportSafety:
    def test_public_surface(self):
        for name in ("validate_content_layers", "run", "main"):
            assert hasattr(vl, name), name

    def test_signature(self):
        params = list(inspect.signature(vl.validate_content_layers).parameters)
        assert params == ["project_root"]
        run_sig = inspect.signature(vl.run)
        assert run_sig.parameters["project_root"].kind == inspect.Parameter.KEYWORD_ONLY


# --- Skip-on-absent (the load-bearing contract) -----------------------------


class TestSkipOnAbsent:
    def test_greenfield_only_project_yaml_is_clean(self, tmp_path: Path):
        _project(tmp_path, current_phase=17)
        assert vl.validate_content_layers(tmp_path) == []

    def test_no_state_dir_at_all_is_clean(self, tmp_path: Path):
        assert vl.validate_content_layers(tmp_path) == []

    def test_single_language_no_parity_check(self, tmp_path: Path):
        _project(tmp_path, default_language="en")
        _strings(tmp_path, "en", {"$language": "en", "cta": {"go": "Go"}})
        # Only one language → check 7 can't run → clean.
        assert vl.validate_content_layers(tmp_path) == []


# --- Check 7: language parity (the DoD seeded-invalid case) ------------------


class TestLanguageParity:
    def test_seeded_de_missing_key_is_warning_with_fixpath(self, tmp_path: Path):
        _project(tmp_path, default_language="en", languages="[en, de]")
        _strings(tmp_path, "en", {"$language": "en", "cta": {"subscribe": "Subscribe", "contact": "Contact"}})
        _strings(tmp_path, "de", {"$language": "de", "cta": {"contact": "Kontakt"}})  # missing cta.subscribe
        findings = vl.validate_content_layers(tmp_path)
        assert len(findings) == 1
        f = findings[0]
        assert f.startswith("[warning]")            # decision 41 → warning, not error
        assert "cta.subscribe" in f                  # the missing key
        assert "de.json" in f                        # the file to fix (fix-path)
        assert "decision 41" in f                    # the fallback rationale
        assert "falls back to the en value" in f

    def test_identical_languages_are_clean(self, tmp_path: Path):
        _project(tmp_path, default_language="en")
        shape = {"cta": {"a": "A", "b": "B"}, "nav": {"home": "Home"}}
        _strings(tmp_path, "en", {"$language": "en", **shape})
        _strings(tmp_path, "de", {"$language": "de", **shape})
        assert vl.validate_content_layers(tmp_path) == []

    def test_meta_dollar_keys_are_not_flagged(self, tmp_path: Path):
        # en carries $schema; de doesn't — $-keys must be excluded from parity.
        _project(tmp_path, default_language="en")
        _strings(tmp_path, "en", {"$language": "en", "$schema": "spec/strings-v1.json", "cta": {"go": "Go"}})
        _strings(tmp_path, "de", {"$language": "de", "cta": {"go": "Los"}})
        assert vl.validate_content_layers(tmp_path) == []

    def test_default_language_inferred_when_project_absent(self, tmp_path: Path):
        # No default_language in project.yaml → reference falls back to en when present.
        _project(tmp_path, current_phase=16)
        _strings(tmp_path, "en", {"$language": "en", "cta": {"x": "X", "y": "Y"}})
        _strings(tmp_path, "de", {"$language": "de", "cta": {"x": "X"}})  # missing cta.y
        findings = vl.validate_content_layers(tmp_path)
        assert any("cta.y" in f and "de.json" in f for f in findings)


# --- Check 3: string references ---------------------------------------------


class TestStringRefs:
    def test_unresolved_ref_is_error(self, tmp_path: Path):
        _project(tmp_path, default_language="en")
        _strings(tmp_path, "en", {"$language": "en", "cta": {"subscribe": "Sub"}})
        _page(tmp_path, "home", body="CTA: {strings.cta.nonexistent}", slug="/", language="en")
        findings = vl.validate_content_layers(tmp_path)
        assert any("cta.nonexistent" in f and "home.md" in f and f.startswith("[error]") for f in findings)

    def test_resolved_ref_is_clean(self, tmp_path: Path):
        _project(tmp_path, default_language="en")
        _strings(tmp_path, "en", {"$language": "en", "cta": {"subscribe": "Sub"}})
        _page(tmp_path, "home", body="CTA: {strings.cta.subscribe}", slug="/", language="en")
        assert vl.validate_content_layers(tmp_path) == []

    def test_ref_uses_default_when_page_language_absent(self, tmp_path: Path):
        _project(tmp_path, default_language="en")
        _strings(tmp_path, "en", {"$language": "en", "cta": {"go": "Go"}})
        _page(tmp_path, "home", body="{strings.cta.go}", slug="/")  # no language frontmatter
        assert vl.validate_content_layers(tmp_path) == []


# --- Check 2: page frontmatter schema ---------------------------------------


class TestPageSchema:
    def test_page_missing_slug_is_error(self, tmp_path: Path):
        _project(tmp_path)
        _page(tmp_path, "about", body="About.", title="About")  # no slug
        findings = vl.validate_content_layers(tmp_path)
        assert any("about.md" in f and "slug" in f for f in findings)

    def test_page_with_slug_is_clean(self, tmp_path: Path):
        _project(tmp_path)
        _page(tmp_path, "about", body="About.", slug="/about", title="About")
        assert vl.validate_content_layers(tmp_path) == []


# --- Check 4: sections exist ------------------------------------------------


class TestSectionsExist:
    def test_missing_section_is_error(self, tmp_path: Path):
        _project(tmp_path)
        _write(tmp_path, "content/sections.yaml", "sections:\n  bio: {}\n  philosophy: {}\n")
        _page(tmp_path, "about", body="x", slug="/about", sections="[bio, philosophy, ghost-section]")
        findings = vl.validate_content_layers(tmp_path)
        assert any("ghost-section" in f and "sections.yaml" in f for f in findings)

    def test_all_sections_present_is_clean(self, tmp_path: Path):
        _project(tmp_path)
        _write(tmp_path, "content/sections.yaml", "sections:\n  bio: {}\n  philosophy: {}\n")
        _page(tmp_path, "about", body="x", slug="/about", sections="[bio, philosophy]")
        assert vl.validate_content_layers(tmp_path) == []

    def test_no_sections_yaml_skips_check(self, tmp_path: Path):
        _project(tmp_path)
        _page(tmp_path, "about", body="x", slug="/about", sections="[bio]")
        # sections.yaml absent → check 4 skipped (skip-on-absent).
        assert vl.validate_content_layers(tmp_path) == []


# --- Check 5: components exist ----------------------------------------------


class TestComponentsExist:
    def test_missing_component_is_error(self, tmp_path: Path):
        _project(tmp_path)
        _write(tmp_path, "content/sections.yaml",
               "sections:\n  hero:\n    component: HeroBlock\n")
        _write(tmp_path, "components.yaml",
               "components:\n  - name: SomethingElse\n")
        findings = vl.validate_content_layers(tmp_path)
        assert any("HeroBlock" in f and "components.yaml" in f for f in findings)

    def test_present_component_is_clean(self, tmp_path: Path):
        _project(tmp_path)
        _write(tmp_path, "content/sections.yaml",
               "sections:\n  hero:\n    component: HeroBlock\n")
        _write(tmp_path, "components.yaml",
               "components:\n  - name: HeroBlock\n")
        assert vl.validate_content_layers(tmp_path) == []


# --- Check 6: token references ----------------------------------------------


class TestTokenRefs:
    def test_unresolved_token_is_error(self, tmp_path: Path):
        _project(tmp_path)
        _write(tmp_path, "brand.yaml", "tokens:\n  colors:\n    primary: oklch(64% 0.18 30)\n")
        _write(tmp_path, "components.yaml",
               'components:\n  - name: Hero\n    bg: "{tokens.colors.missing}"\n')
        findings = vl.validate_content_layers(tmp_path)
        assert any("colors.missing" in f and "brand.yaml" in f for f in findings)

    def test_resolved_token_is_clean(self, tmp_path: Path):
        _project(tmp_path)
        _write(tmp_path, "brand.yaml", "tokens:\n  colors:\n    primary: oklch(64% 0.18 30)\n")
        _write(tmp_path, "components.yaml",
               'components:\n  - name: Hero\n    bg: "{tokens.colors.primary}"\n')
        assert vl.validate_content_layers(tmp_path) == []


# --- Check 1: parse errors --------------------------------------------------


class TestParseErrors:
    def test_malformed_json_is_error(self, tmp_path: Path):
        _project(tmp_path, default_language="en")
        d = _state(tmp_path) / "content" / "strings"
        d.mkdir(parents=True, exist_ok=True)
        (d / "en.json").write_text("{ not valid json", encoding="utf-8")
        findings = vl.validate_content_layers(tmp_path)
        assert any("en.json" in f and "JSON parse failed" in f for f in findings)


# --- run() debug dispatch ---------------------------------------------------


class TestRun:
    def test_run_clean_returns_zero(self, tmp_path: Path, capsys):
        _project(tmp_path, current_phase=17)
        assert vl.run([], project_root=tmp_path) == 0
        assert "content layers OK" in capsys.readouterr().out

    def test_run_reports_findings(self, tmp_path: Path, capsys):
        _project(tmp_path, default_language="en")
        _strings(tmp_path, "en", {"$language": "en", "cta": {"a": "A"}})
        _strings(tmp_path, "de", {"$language": "de"})
        rc = vl.run([], project_root=tmp_path)
        assert rc == 0
        assert "cta.a" in capsys.readouterr().out

    def test_run_json(self, tmp_path: Path, capsys):
        _project(tmp_path, default_language="en")
        _strings(tmp_path, "en", {"$language": "en", "cta": {"a": "A"}})
        _strings(tmp_path, "de", {"$language": "de"})
        rc = vl.run(["--json"], project_root=tmp_path)
        assert rc == 0
        payload = json.loads(capsys.readouterr().out)
        assert isinstance(payload, list) and any("cta.a" in x for x in payload)
