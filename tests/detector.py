"""
Reference entry-mode detector for the website-builder plugin.

This module implements the entry-mode detection spec from:
  - Workstreams/website-builder/foundation/DESIGN-architecture.md (Entry modes)
  - Workstreams/website-builder/foundation/DESIGN-ingestion-and-extraction.md
  - Workstreams/website-builder/website-builder.md (locked decision 15)

It is the **reference implementation** the test harness runs against. Captain C's
SessionStart hook (in the plugin proper at hooks-handlers/session-start.{sh,py})
should agree with this detector's output for every fixture in tests/walkthroughs/.

If Captain C's hook disagrees, the integration test (smoke_test.py::test_hook_*)
fails — the General iterates with Captain C until alignment.

The detector is INTENTIONALLY minimal (single-file, no plugin imports) so the
fixture suite can be validated in isolation, and so the reference vs. actual
comparison is unambiguous.

v0.1 scope: entry-mode classification + the structured detection-signals dict.
Real ingestion / phase 6.5 execution is out of scope (deferred to Phase 3+
adapters and Phase 7-8 cosplay/Ralph tests).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path


# --- Detection signal helpers ----------------------------------------------

NEXT_CONFIG_NAMES = {"next.config.js", "next.config.ts", "next.config.mjs"}
ASTRO_CONFIG_NAMES = {"astro.config.js", "astro.config.ts", "astro.config.mjs"}
GATSBY_CONFIG_NAMES = {"gatsby-config.js", "gatsby-config.ts"}
VITE_CONFIG_NAMES = {"vite.config.js", "vite.config.ts"}
SVELTE_CONFIG_NAMES = {"svelte.config.js", "svelte.config.ts"}
HUGO_CONFIG_NAMES = {"hugo.toml", "config.toml"}  # config.toml is ambiguous; checked further
WORDPRESS_MARKERS = {"wp-config.php", "wp-config-sample.php"}

# Files that exist in pre-bootstrap meta-shape and DON'T disqualify "empty".
META_FILES = {".gitkeep", "README.md", "readme.md", "LICENSE", "LICENSE.md", ".gitignore"}


def _list_root_files(project_dir: Path) -> list[Path]:
    """Files directly at project root (no recursion)."""
    if not project_dir.exists():
        return []
    return [p for p in project_dir.iterdir() if p.is_file()]


def _list_root_dirs(project_dir: Path) -> list[Path]:
    """Directories directly at project root (no recursion)."""
    if not project_dir.exists():
        return []
    return [p for p in project_dir.iterdir() if p.is_dir()]


def _looks_empty(project_dir: Path) -> bool:
    """True if the dir has nothing meaningful in it (only meta-files)."""
    files = _list_root_files(project_dir)
    dirs = _list_root_dirs(project_dir)
    if dirs:
        return False
    for f in files:
        if f.name not in META_FILES:
            return False
    return True


def _has_framer_dir(project_dir: Path) -> bool:
    framer_dir = project_dir / ".framer"
    return framer_dir.is_dir()


def _has_figma_files(project_dir: Path) -> list[Path]:
    return [p for p in _list_root_files(project_dir) if p.suffix == ".fig"]


def _read_package_json(project_dir: Path) -> dict | None:
    pkg = project_dir / "package.json"
    if not pkg.is_file():
        return None
    try:
        return json.loads(pkg.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def _detect_stack_from_config(project_dir: Path) -> str | None:
    """Return a stack slug if a stack-config marker file exists."""
    root_file_names = {p.name for p in _list_root_files(project_dir)}
    if root_file_names & NEXT_CONFIG_NAMES:
        return "nextjs"
    if root_file_names & ASTRO_CONFIG_NAMES:
        return "astro"
    if root_file_names & GATSBY_CONFIG_NAMES:
        return "gatsby"
    if root_file_names & SVELTE_CONFIG_NAMES:
        return "sveltekit"
    if root_file_names & VITE_CONFIG_NAMES:
        # Vite is a build tool, not a stack. Need framework signal from package.json.
        return None  # caller will check package.json
    if "hugo.toml" in root_file_names:
        return "hugo"
    if root_file_names & WORDPRESS_MARKERS:
        return "wordpress"
    return None


def _detect_framework_from_package(pkg: dict | None) -> str | None:
    """Inspect package.json dependencies for known frameworks."""
    if not pkg:
        return None
    deps = {**(pkg.get("dependencies") or {}), **(pkg.get("devDependencies") or {})}
    if "next" in deps:
        return "next"
    if "astro" in deps:
        return "astro"
    if "gatsby" in deps:
        return "gatsby"
    if "@sveltejs/kit" in deps:
        return "@sveltejs/kit"
    if "vue" in deps and ("vite" in deps or "@vitejs/plugin-vue" in deps):
        return "vue"
    if "react" in deps and "vite" in deps:
        return "react+vite"
    return None


def _has_app_router(project_dir: Path) -> bool:
    """Next.js app router signal: app/ dir with page or layout file."""
    app_dir = project_dir / "app"
    if not app_dir.is_dir():
        return False
    for child in app_dir.rglob("*"):
        if child.is_file() and child.stem in {"page", "layout"} and child.suffix in {".tsx", ".jsx", ".ts", ".js"}:
            return True
    return False


def _has_pages_router(project_dir: Path) -> bool:
    """Next.js pages router signal: pages/ dir with index.* file."""
    pages_dir = project_dir / "pages"
    if not pages_dir.is_dir():
        return False
    for child in pages_dir.iterdir():
        if child.is_file() and child.stem == "index":
            return True
    return False


# --- AI-output detection ---------------------------------------------------

# Heuristics for AI-output signature in a single .html file.
TAILWIND_UTILITY_RE = re.compile(
    r'\bclassN?ame\s*=\s*["\'][^"\']*'
    r'(flex|grid|min-h-|max-w-|px-\d|py-\d|mx-|my-|mt-|mb-|gap-|rounded|bg-|text-|font-|hover:|focus:|md:|lg:)',
    re.IGNORECASE,
)
JSX_CLASSNAME_RE = re.compile(r'\bclassName\s*=\s*["\']', re.IGNORECASE)
INLINE_STYLE_VARS_RE = re.compile(r'<style[^>]*>[\s\S]*?--[a-z-]+\s*:[\s\S]*?</style>', re.IGNORECASE)


def _detect_ai_output_signature(html_text: str) -> dict[str, bool]:
    """Return signal flags for AI-output classification."""
    # Count distinct utility-class hits
    utility_hits = TAILWIND_UTILITY_RE.findall(html_text)
    jsx_classname = bool(JSX_CLASSNAME_RE.search(html_text))
    inline_style_vars = bool(INLINE_STYLE_VARS_RE.search(html_text))
    return {
        "tailwind_utility_classes": len(utility_hits) >= 10,
        "jsx_classname_attribute": jsx_classname,
        "inline_style_with_css_vars": inline_style_vars,
    }


# --- Detection result dataclass --------------------------------------------

@dataclass
class DetectionResult:
    entry_mode: str  # one of: greenfield | has-existing-site | has-AI-output | has-Framer-attempt | has-Figma-file | ambiguous
    detection_confidence: str  # high | medium | low | none
    detection_signals: dict = field(default_factory=dict)
    next_phase: float = 1.0  # 1.0 = phase 1 (idea); 6.5 = phase 6.5 (artifact ingestion)
    runs_phase_6_5_at_start: bool = False
    phase_6_5_extractors: list[str] = field(default_factory=list)

    # Pre-detected stack hints (consumed by phase 11)
    detected_stack: str | None = None
    detected_cms: str | None = None
    detected_component_library: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


# --- Main detection entry point --------------------------------------------

def detect(project_dir: Path) -> DetectionResult:
    """
    Run entry-mode detection on a fixture's `fixture/` directory (or any
    real user project dir).

    Returns a DetectionResult with the entry mode + structured signals.

    The order matters: stronger signals win. Order of evaluation:
      1. Empty/near-empty → greenfield
      2. .framer/ at root → has-Framer-attempt
      3. .fig file at root → has-Figma-file
      4. stack config OR framework in package.json → has-existing-site
      5. single .html file with AI-output signature → has-AI-output
      6. fallback → ambiguous (let bootstrap ask user)
    """
    if not project_dir.is_dir():
        return DetectionResult(
            entry_mode="ambiguous",
            detection_confidence="none",
            detection_signals={"error": f"project_dir not a directory: {project_dir}"},
        )

    # Step 1 — collect raw signals
    is_empty = _looks_empty(project_dir)
    has_framer = _has_framer_dir(project_dir)
    figma_files = _has_figma_files(project_dir)
    pkg = _read_package_json(project_dir)
    stack_from_config = _detect_stack_from_config(project_dir)
    framework_from_pkg = _detect_framework_from_package(pkg)
    app_router = _has_app_router(project_dir)
    pages_router = _has_pages_router(project_dir)
    root_html = [p for p in _list_root_files(project_dir) if p.suffix.lower() in {".html", ".htm"}]

    base_signals = {
        "empty_or_near_empty": is_empty,
        "has_stack_config": stack_from_config is not None,
        "has_framework_in_package_json": framework_from_pkg is not None,
        "has_framer_dir": has_framer,
        "has_figma_file": bool(figma_files),
        "has_html_artifact": bool(root_html),
    }

    # Step 2 — apply order-sensitive precedence
    # 2a. Empty → greenfield
    if is_empty:
        return DetectionResult(
            entry_mode="greenfield",
            detection_confidence="high",
            detection_signals=base_signals,
            next_phase=1.0,
            runs_phase_6_5_at_start=False,
        )

    # 2b. .framer/ at root → has-Framer-attempt (Framer wins over other framework configs)
    if has_framer:
        signals = dict(base_signals)
        signals["framer_dir_at_root"] = True
        return DetectionResult(
            entry_mode="has-Framer-attempt",
            detection_confidence="high",
            detection_signals=signals,
            next_phase=6.5,
            runs_phase_6_5_at_start=True,
            phase_6_5_extractors=["framer-adapter"],
            detected_stack="framer",
            detected_cms="framer-cms",
            detected_component_library="framer-custom",
        )

    # 2c. .fig file at root (and no other strong stack signal) → has-Figma-file
    if figma_files and not (stack_from_config or framework_from_pkg):
        signals = dict(base_signals)
        signals["figma_file_count"] = len(figma_files)
        signals["figma_file_at_root"] = True
        return DetectionResult(
            entry_mode="has-Figma-file",
            detection_confidence="high",
            detection_signals=signals,
            next_phase=6.5,
            runs_phase_6_5_at_start=True,
            phase_6_5_extractors=["figma-design-to-json"],
        )

    # 2d. Framework signal → has-existing-site
    if stack_from_config or framework_from_pkg:
        stack = stack_from_config or _stack_from_framework(framework_from_pkg)
        signals = dict(base_signals)
        signals["detected_stack"] = stack
        if framework_from_pkg:
            signals["framework"] = framework_from_pkg
        if stack == "nextjs":
            signals["app_router_present"] = app_router
            signals["pages_router_present"] = pages_router
        return DetectionResult(
            entry_mode="has-existing-site",
            detection_confidence="high",
            detection_signals=signals,
            next_phase=6.5,
            runs_phase_6_5_at_start=True,
            phase_6_5_extractors=["playwright-walk", "stitch", "ai-output"],
            detected_stack=stack,
        )

    # 2e. Single .html file at root with AI-output signature → has-AI-output
    if len(root_html) == 1 and not _list_root_dirs(project_dir):
        # Only check AI-output signature if there's exactly one HTML and no other dirs
        # (multi-file static site = has-existing-site fallthrough; not yet a fixture in v0.1)
        html_text = root_html[0].read_text(encoding="utf-8", errors="replace")
        ai_signals = _detect_ai_output_signature(html_text)
        # AI-output signature: at least 2 of 3 sub-signals must hit
        ai_match_count = sum(1 for v in ai_signals.values() if v)
        if ai_match_count >= 2:
            signals = dict(base_signals)
            signals["html_artifact_count"] = 1
            signals["ai_output_signature"] = True
            signals["detected_signals"] = [k for k, v in ai_signals.items() if v]
            return DetectionResult(
                entry_mode="has-AI-output",
                detection_confidence="high",
                detection_signals=signals,
                next_phase=6.5,
                runs_phase_6_5_at_start=True,
                phase_6_5_extractors=["ai-output"],
            )
        else:
            # Single HTML but no AI signature: ambiguous
            signals = dict(base_signals)
            signals["html_artifact_count"] = 1
            signals["ai_output_signature"] = False
            return DetectionResult(
                entry_mode="ambiguous",
                detection_confidence="medium",
                detection_signals=signals,
            )

    # 2f. Fallback → ambiguous
    return DetectionResult(
        entry_mode="ambiguous",
        detection_confidence="low",
        detection_signals=base_signals,
    )


def _stack_from_framework(framework: str | None) -> str | None:
    if framework is None:
        return None
    if framework == "next":
        return "nextjs"
    if framework == "astro":
        return "astro"
    if framework == "gatsby":
        return "gatsby"
    if framework == "@sveltejs/kit":
        return "sveltekit"
    return framework


# --- CLI entry point (smoke check) -----------------------------------------

if __name__ == "__main__":
    import sys
    from pprint import pprint

    if len(sys.argv) < 2:
        print("Usage: python detector.py <project_dir>", file=sys.stderr)
        sys.exit(2)
    target = Path(sys.argv[1]).resolve()
    result = detect(target)
    pprint(result.to_dict())
