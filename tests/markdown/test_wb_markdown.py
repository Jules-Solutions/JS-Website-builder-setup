"""
Unit tests for the shared markdown/frontmatter primitives (`scripts/wb_markdown.py`).
Wave 1 / Captain spine-1 scope (orchestration spine § 5.1).

The fence-edge tests are LOAD-BEARING (DESIGN-orchestration-spine.md § 5.1): a
`## ` inside a fenced code block must NOT split a section, `###` sub-headings must
stay inside their `##`, and trailing-whitespace / CRLF headings must still match.

No network, no external tools — pure input->output.

Run:
  bash tests/run-tests.sh
  cd tests && uv run --with pyyaml --with pytest pytest markdown/ -v
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

# Make scripts/wb_markdown.py importable regardless of pytest's cwd.
PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import wb_markdown as wm  # noqa: E402  (sys.path mutation must precede)


# --- Import safety ---------------------------------------------------------


class TestImportSafety:
    def test_import_is_side_effect_free(self):
        mod = importlib.reload(wm)
        assert hasattr(mod, "extract_h2_section")
        assert hasattr(mod, "parse_frontmatter")
        assert hasattr(mod, "parse_yaml")

    def test_public_surface(self):
        import inspect

        sig = inspect.signature(wm.extract_h2_section)
        params = list(sig.parameters)
        assert params[0] == "text" and params[1] == "heading"
        assert sig.parameters["include_heading"].kind == inspect.Parameter.KEYWORD_ONLY
        assert sig.parameters["match"].kind == inspect.Parameter.KEYWORD_ONLY


# --- extract_h2_section: basic behavior ------------------------------------


class TestExtractBasic:
    def test_simple_section(self):
        text = "## Alpha\nbody a\n\n## Beta\nbody b\n"
        out = wm.extract_h2_section(text, "Alpha")
        assert out == "## Alpha\nbody a"

    def test_exclude_heading(self):
        text = "## Alpha\nbody a\n## Beta\nbody b\n"
        out = wm.extract_h2_section(text, "Alpha", include_heading=False)
        assert out == "body a"

    def test_last_section_runs_to_eof(self):
        text = "## Alpha\nbody a\n## Beta\nbody b\nmore b\n"
        out = wm.extract_h2_section(text, "Beta")
        assert out == "## Beta\nbody b\nmore b"

    def test_absent_heading_returns_none(self):
        text = "## Alpha\nbody a\n"
        assert wm.extract_h2_section(text, "Gamma") is None

    def test_exact_match_is_case_sensitive(self):
        text = "## Content layer mapping\nrow\n"
        assert wm.extract_h2_section(text, "content layer mapping") is None
        assert wm.extract_h2_section(text, "Content layer mapping") is not None

    def test_heading_with_parens_verbatim(self):
        # The commerce section keeps `(if transactional=true)` verbatim.
        text = "## Commerce integration (if transactional=true)\nrows\n## Next\nx\n"
        out = wm.extract_h2_section(text, "Commerce integration (if transactional=true)")
        assert out == "## Commerce integration (if transactional=true)\nrows"


# --- extract_h2_section: H3 sub-headings stay inside ------------------------


class TestSubHeadingsStayInside:
    def test_h3_does_not_terminate_section(self):
        text = (
            "## Auth + setup\n"
            "intro\n"
            "### CRUD vocabulary\n"
            "crud body\n"
            "#### deeper\n"
            "deep body\n"
            "## Migration recipe\n"
            "next\n"
        )
        out = wm.extract_h2_section(text, "Auth + setup")
        assert "### CRUD vocabulary" in out
        assert "#### deeper" in out
        assert "deep body" in out
        assert "Migration recipe" not in out

    def test_only_level2_terminates(self):
        text = "## A\nx\n### A.1\ny\n## B\nz\n"
        assert wm.extract_h2_section(text, "A", include_heading=False) == "x\n### A.1\ny"


# --- extract_h2_section: fence-awareness (LOAD-BEARING) ---------------------


class TestFenceAwareness:
    def test_h2_inside_backtick_fence_is_not_a_boundary(self):
        text = (
            "## Mental model\n"
            "intro\n"
            "```jsonc\n"
            "## this is example code, not a heading\n"
            "{ }\n"
            "```\n"
            "after fence\n"
            "## CMS pairing\n"
            "next\n"
        )
        out = wm.extract_h2_section(text, "Mental model")
        # The fenced `## ...` must be retained as content, not split.
        assert "## this is example code, not a heading" in out
        assert "after fence" in out
        assert "CMS pairing" not in out

    def test_h2_inside_tilde_fence_is_not_a_boundary(self):
        text = (
            "## Deploy\n"
            "~~~\n"
            "## fenced with tildes\n"
            "~~~\n"
            "real body\n"
            "## References\n"
            "refs\n"
        )
        out = wm.extract_h2_section(text, "Deploy")
        assert "## fenced with tildes" in out
        assert "real body" in out
        assert "References" not in out

    def test_backtick_fence_not_closed_by_tilde(self):
        # A ``` block must only close on ```, not on ~~~ — so a `## ` after the
        # tilde line but still inside the backtick block is content.
        text = (
            "## Section\n"
            "```\n"
            "~~~ not a close\n"
            "## still code\n"
            "```\n"
            "tail\n"
            "## Other\n"
            "o\n"
        )
        out = wm.extract_h2_section(text, "Section")
        assert "## still code" in out
        assert "tail" in out
        assert "Other" not in out

    def test_fence_with_info_string_opens(self):
        text = (
            "## S\n"
            "```python\n"
            "## not heading\n"
            "```\n"
            "## T\n"
            "t\n"
        )
        out = wm.extract_h2_section(text, "S")
        assert "## not heading" in out
        assert "T" not in out.replace("python", "")

    def test_terminating_heading_after_fence_closes(self):
        # After a fence closes, a real `## ` DOES terminate.
        text = (
            "## First\n"
            "```\n"
            "code\n"
            "```\n"
            "## Second\n"
            "second body\n"
        )
        out = wm.extract_h2_section(text, "First")
        assert out == "## First\n```\ncode\n```"
        assert "Second" not in out


# --- extract_h2_section: whitespace / CRLF tolerance ------------------------


class TestWhitespaceTolerance:
    def test_trailing_whitespace_on_heading(self):
        text = "## Alpha   \nbody\n## Beta\nx\n"
        out = wm.extract_h2_section(text, "Alpha")
        assert out is not None
        assert out.startswith("## Alpha")
        assert "body" in out

    def test_crlf_line_endings(self):
        text = "## Alpha\r\nbody a\r\n## Beta\r\nbody b\r\n"
        out = wm.extract_h2_section(text, "Alpha")
        assert out == "## Alpha\nbody a"

    def test_trailing_blank_lines_trimmed(self):
        text = "## Alpha\nbody\n\n\n## Beta\nx\n"
        out = wm.extract_h2_section(text, "Alpha")
        assert out == "## Alpha\nbody"


# --- extract_h2_section: contains-match (discipline lookup) -----------------


class TestContainsMatch:
    def test_contains_finds_first_matching(self):
        text = (
            "## Intro\nx\n"
            "## The core discipline: grounded option-generation\n"
            "disc body\n"
            "## Outro\ny\n"
        )
        out = wm.extract_h2_section(text, "discipline", match="contains")
        assert out is not None
        assert "disc body" in out
        assert "Outro" not in out

    def test_contains_is_case_insensitive(self):
        text = "## CORE DISCIPLINE\nbody\n"
        out = wm.extract_h2_section(text, "discipline", match="contains")
        assert out is not None
        assert "body" in out

    def test_contains_absent_returns_none(self):
        text = "## Something else\nbody\n"
        assert wm.extract_h2_section(text, "discipline", match="contains") is None


# --- parse_frontmatter ------------------------------------------------------


class TestParseFrontmatter:
    def test_basic_frontmatter(self):
        text = "---\nname: wb-design-system\nskill: wb-design-system\n---\n# Body\n"
        fm = wm.parse_frontmatter(text)
        assert fm.get("name") == "wb-design-system"
        assert fm.get("skill") == "wb-design-system"

    def test_absent_frontmatter_returns_empty(self):
        assert wm.parse_frontmatter("# No frontmatter here\n") == {}

    def test_description_scalar_extracted(self):
        text = (
            "---\n"
            "skill: wb-design-system\n"
            'description: "Trigger at phase 17; refuses non-OKLCH color."\n'
            "---\n"
            "body\n"
        )
        fm = wm.parse_frontmatter(text)
        assert "OKLCH" in fm.get("description", "")

    def test_no_closing_fence_returns_empty(self):
        text = "---\nkey: val\nbody without closing fence\n"
        assert wm.parse_frontmatter(text) == {}


# --- parse_yaml -------------------------------------------------------------


class TestParseYaml:
    def test_flat_scalars(self):
        data = wm.parse_yaml("current_phase: 17\nstack: nextjs\n")
        assert data["current_phase"] == 17
        assert data["stack"] == "nextjs"

    def test_non_mapping_returns_empty(self):
        assert wm.parse_yaml("- just\n- a\n- list\n") == {}
