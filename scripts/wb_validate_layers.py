#!/usr/bin/env python3
"""
scripts/wb_validate_layers.py — the website-builder plugin's content-layer validator.

Wave-2 module (orchestration-spine remediation). Lights up the spine's
import-guarded **action 4** (DESIGN-orchestration-spine.md § 4.3) and is also
surfaced as a session-start summary (hooks-handlers/session_start.py).

Public surface (the locked module-boundary contract in `scripts/README.md`,
mirroring wb_keys.resolve_keys / wb_orchestrate.run):

    validate_content_layers(project_root) -> list[str]
        Cross-layer validation of the 5-layer content stack
        (DESIGN-content-layers.md § "Validation across layers", lines 351-362).
        Returns a list of human error/warning strings — each carrying a concrete
        FIX PATH. Empty list ⇒ everything that EXISTS is internally consistent.
        Called by wb_orchestrate._action_validate_layers (action 4) + the
        SessionStart hook. project_root is passed in explicitly (no os.getcwd()).

    run(argv, *, project_root) -> int
        Debug/`wb`-style dispatch: runs validation + prints each finding. `--json`
        emits the findings as a JSON array. NOT a user-facing `wb` verb (the
        resolver-as-entry-point pattern — like wb_keys.resolve_keys /
        wb_orchestrate.run).

    main() -> int
        Standalone entry for isolated debugging. project_root = cwd.

The 7 cross-layer checks (DESIGN-content-layers.md § 351-362):
  1. All YAML / JSON / MD layer files parse.
  2. Page frontmatter conforms to schema (carries the required `slug`).
  3. All `{strings.x.y.z}` references resolve in the relevant language file.
  4. All sections referenced in `content/pages/` exist in `sections.yaml`.
  5. All components referenced in `sections.yaml` exist in `components.yaml`.
  6. All `{tokens.x.y}` references in `components.yaml` resolve to `brand.yaml.tokens`.
  7. All language files share the default-language key structure (no missing
     translations). **Decision 41**: a key present in the default language but
     absent from another language is a *warning* (the runtime falls back to the
     default-language value), NOT a hard error.

**Skip-on-absent contract (load-bearing).** The 5 layers are authored
*progressively* across the pipeline's phases — a phase-8 project has a
project.yaml but no `sections.yaml`/`components.yaml`/pages/strings yet. Validation
therefore only checks references AMONG FILES THAT EXIST: an absent source file
makes its dependent check a no-op, never an error. A greenfield project (only
project.yaml) returns `[]`. This is what keeps action 4 quiet until there is
real content to validate.

Interface rules (mirrors the locked wb_keys.py / wb_markdown.py module contract,
`scripts/README.md` § Interface rules):
  - IMPORT-SAFE: importing this module has NO side effects (no network, no file
    writes, no subprocess at import time). All work happens inside the entry points.
  - `project_root` is passed in explicitly — this module never reads os.getcwd()
    inside its logic (testability; mirrors wb_keys / wb_library / wb_orchestrate).
  - Depends only on the leaf util wb_markdown (parse_yaml / parse_frontmatter) +
    stdlib. Does NOT import the dispatcher, wb_keys, wb_library, or wb_orchestrate
    (no cycle — wb_orchestrate soft-imports THIS module, never the reverse).

See also:
  - DESIGN-content-layers.md § 351-362
  - DESIGN-orchestration-spine.md § 4.3 (action 4)
  - scripts/wb_markdown.py (parse_yaml / parse_frontmatter — consumed here)
  - scripts/wb_orchestrate.py (_action_validate_layers — the action-4 call-site)
  - hooks-handlers/session_start.py (run_validate_layers — the session-start summary)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ---------- Sibling import (wb_markdown lives in this scripts/ dir) ----------
#
# The only import-time effect: put our own dir on sys.path so the wb_markdown
# import resolves regardless of caller cwd (mirrors wb_orchestrate). Idempotent.
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import wb_markdown  # noqa: E402  (sys.path nudge must precede)


# ---------- Constants ----------

MODULE_NAME = "wb validate-layers"
STATE_DIR_NAME = ".website-builder"
CONTENT_LAYERS_DOC = (
    "DESIGN-content-layers.md"
)

# `{strings.a.b.c}` reference (Layer 4 → Layer 3). The capture is the dotted path.
_STRINGS_REF = re.compile(r"\{strings\.([A-Za-z0-9_.\-]+)\}")
# `{tokens.a.b}` reference (Layer 2 components.yaml → Layer 1 brand.yaml.tokens).
_TOKENS_REF = re.compile(r"\{tokens\.([A-Za-z0-9_.\-]+)\}")


# ---------- Logging helpers (mirror wb_keys.py / wb_orchestrate.py) ----------

def _color_supported() -> bool:
    return bool(getattr(sys.stdout, "isatty", lambda: False)())


_USE_COLOR = _color_supported()


def _c(code: str, msg: str) -> str:
    if not _USE_COLOR:
        return msg
    return f"\x1b[{code}m{msg}\x1b[0m"


def log_info(msg: str) -> None:
    print(f"{_c('36', '[wb validate-layers]')} {msg}", flush=True)


def log_warn(msg: str) -> None:
    print(f"{_c('33', '[wb validate-layers]')} {msg}", file=sys.stderr, flush=True)


# ---------- Path helpers ----------

def _state_dir(project_root: Path) -> Path:
    return project_root / STATE_DIR_NAME


def _layer_paths(project_root: Path) -> dict[str, Path]:
    """The canonical 5-layer file locations under `.website-builder/`
    (DESIGN-content-layers.md). Pages + strings are directories of files."""
    sd = _state_dir(project_root)
    return {
        "brand": sd / "brand.yaml",                       # Layer 1
        "sitemap": sd / "sitemap.yaml",                   # Layer 2
        "sections": sd / "content" / "sections.yaml",     # Layer 2
        "components": sd / "components.yaml",              # Layer 2
        "pages_dir": sd / "content" / "pages",            # Layer 4
        "strings_dir": sd / "content" / "strings",        # Layer 3
    }


def _rel(project_root: Path, path: Path) -> str:
    """Project-root-relative POSIX path for clean fix-path messages."""
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return path.as_posix()


# ---------- Parse helpers (each returns (data, error_str|None)) ----------

def _read_text(path: Path) -> tuple[str | None, str | None]:
    try:
        return path.read_text(encoding="utf-8"), None
    except OSError as exc:
        return None, f"could not read {path.name}: {exc}"


def _parse_yaml_file(project_root: Path, path: Path) -> tuple[dict[str, Any] | None, str | None]:
    """Parse a YAML layer file. (None, error) on read/parse failure."""
    text, read_err = _read_text(path)
    if text is None:
        return None, f"[error] {_rel(project_root, path)} — {read_err}"
    try:
        data = wb_markdown.parse_yaml(text)
    except Exception as exc:  # noqa: BLE001 — surface a parse failure as a finding, never raise
        return None, (
            f"[error] {_rel(project_root, path)} — YAML parse failed: {exc}. "
            f"Fix the YAML syntax in {_rel(project_root, path)}."
        )
    return data, None


def _parse_json_file(project_root: Path, path: Path) -> tuple[Any, str | None]:
    """Parse a JSON layer file. (None, error) on read/parse failure."""
    text, read_err = _read_text(path)
    if text is None:
        return None, f"[error] {_rel(project_root, path)} — {read_err}"
    try:
        return json.loads(text), None
    except (ValueError, TypeError) as exc:
        return None, (
            f"[error] {_rel(project_root, path)} — JSON parse failed: {exc}. "
            f"Fix the JSON syntax in {_rel(project_root, path)}."
        )


# ---------- Loaded-layers model ----------

@dataclass
class _PageDoc:
    rel: str
    frontmatter: dict[str, Any]
    raw: str


@dataclass
class _Layers:
    """Parsed 5-layer state. A None field = file absent or unparsable (a parse
    error is recorded in `parse_errors`). Dependent checks skip None sources."""

    brand: dict[str, Any] | None = None
    sitemap: dict[str, Any] | None = None
    sections: dict[str, Any] | None = None
    components: dict[str, Any] | None = None
    pages: list[_PageDoc] = field(default_factory=list)
    strings: dict[str, Any] = field(default_factory=dict)        # lang -> parsed json
    components_raw: str = ""                                       # for {tokens.x} scan
    parse_errors: list[str] = field(default_factory=list)


def _load_layers(project_root: Path) -> _Layers:
    """Load + parse every layer file that EXISTS (check 1). Absent files are
    skipped silently; parse failures are recorded as findings."""
    paths = _layer_paths(project_root)
    layers = _Layers()

    # Layer 1 / 2 single-file YAML layers.
    for attr, key in (("brand", "brand"), ("sitemap", "sitemap"),
                      ("sections", "sections"), ("components", "components")):
        p = paths[key]
        if p.is_file():
            data, err = _parse_yaml_file(project_root, p)
            if err:
                layers.parse_errors.append(err)
            else:
                setattr(layers, attr, data)
            if attr == "components":
                text, _ = _read_text(p)
                layers.components_raw = text or ""

    # Layer 4 pages (markdown + frontmatter).
    pages_dir = paths["pages_dir"]
    if pages_dir.is_dir():
        for page in sorted(pages_dir.glob("*.md")):
            text, read_err = _read_text(page)
            if text is None:
                layers.parse_errors.append(f"[error] {_rel(project_root, page)} — {read_err}")
                continue
            try:
                fm = wb_markdown.parse_frontmatter(text)
            except Exception as exc:  # noqa: BLE001 — a frontmatter parse failure is a finding
                layers.parse_errors.append(
                    f"[error] {_rel(project_root, page)} — frontmatter parse failed: {exc}. "
                    f"Fix the YAML frontmatter in {_rel(project_root, page)}."
                )
                continue
            layers.pages.append(_PageDoc(rel=_rel(project_root, page), frontmatter=fm, raw=text))

    # Layer 3 strings (one JSON file per language).
    strings_dir = paths["strings_dir"]
    if strings_dir.is_dir():
        for sfile in sorted(strings_dir.glob("*.json")):
            lang = sfile.stem
            if lang.startswith("."):
                continue
            data, err = _parse_json_file(project_root, sfile)
            if err:
                layers.parse_errors.append(err)
            elif isinstance(data, dict):
                layers.strings[lang] = data
            else:
                layers.strings[lang] = {}
                layers.parse_errors.append(
                    f"[error] {_rel(project_root, sfile)} — expected a JSON object at the "
                    f"top level (got {type(data).__name__}). Wrap the strings in {{ }}."
                )

    return layers


# ---------- Generic structural helpers ----------

def _flatten_keys(node: Any, prefix: str = "") -> set[str]:
    """Dotted leaf-key paths of a nested dict. Excludes any key beginning with
    `$` (JSON-schema meta keys like `$language` / `$schema`). Non-dict values are
    leaves (their dotted path is recorded)."""
    out: set[str] = set()
    if not isinstance(node, dict):
        return out
    for k, v in node.items():
        if isinstance(k, str) and k.startswith("$"):
            continue
        path = f"{prefix}{k}"
        if isinstance(v, dict) and v:
            out |= _flatten_keys(v, f"{path}.")
        else:
            out.add(path)
    return out


def _resolve_dotted(data: Any, dotted: str) -> bool:
    """True if the dotted path resolves to a present key in the nested dict."""
    node: Any = data
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return False
        node = node[part]
    return True


def _defined_names(node: Any, *, list_keys: tuple[str, ...], name_fields: tuple[str, ...]) -> set[str]:
    """Collect identifier names defined in a Layer-2 spec doc (sections.yaml /
    components.yaml). Tolerant of two common shapes:
      - a top-level mapping whose KEYS are the identifiers, optionally nested under
        one of `list_keys` (e.g. `sections:` / `components:`);
      - a list of entries each carrying a `name`/`id` field (one of `name_fields`).
    """
    names: set[str] = set()
    if not isinstance(node, dict):
        return names

    def _harvest(container: Any) -> None:
        if isinstance(container, dict):
            for k, v in container.items():
                if isinstance(k, str) and not k.startswith("$"):
                    names.add(k)
                if isinstance(v, dict):
                    for nf in name_fields:
                        nm = v.get(nf)
                        if isinstance(nm, str):
                            names.add(nm)
        elif isinstance(container, list):
            for item in container:
                if isinstance(item, dict):
                    for nf in name_fields:
                        nm = item.get(nf)
                        if isinstance(nm, str):
                            names.add(nm)

    used_list_key = False
    for lk in list_keys:
        if lk in node:
            used_list_key = True
            _harvest(node[lk])
    if not used_list_key:
        _harvest(node)
    return names


def _string_list(value: Any) -> list[str]:
    """Coerce a frontmatter `sections:`/`components:` field to a list of strings.
    Accepts a list, a single string, or a comma-separated string."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str):
        s = value.strip().strip("[]")
        if not s:
            return []
        return [part.strip().strip("'\"") for part in s.split(",") if part.strip()]
    return []


def _referenced_components(node: Any) -> set[str]:
    """Walk sections.yaml collecting component references (any `component:` scalar
    or `components:` list value)."""
    refs: set[str] = set()

    def _walk(n: Any) -> None:
        if isinstance(n, dict):
            for k, v in n.items():
                if k == "component" and isinstance(v, str):
                    refs.add(v.strip())
                elif k == "components":
                    for item in _string_list(v):
                        refs.add(item)
                    if isinstance(v, (dict, list)):
                        _walk(v)
                else:
                    _walk(v)
        elif isinstance(n, list):
            for item in n:
                _walk(item)

    _walk(node)
    refs.discard("")
    return refs


# ---------- The 7 checks ----------

def _check_string_refs(project_root: Path, layers: _Layers, default_lang: str | None) -> list[str]:
    """Check 3 — `{strings.x.y.z}` references resolve in the page's language file."""
    out: list[str] = []
    if not layers.strings:
        return out  # no strings files → cannot validate refs (skip-on-absent)
    for page in layers.pages:
        refs = sorted(set(_STRINGS_REF.findall(page.raw)))
        if not refs:
            continue
        lang = page.frontmatter.get("language")
        lang = str(lang) if isinstance(lang, (str, int)) else default_lang
        strings_data = layers.strings.get(lang or "")
        if strings_data is None and default_lang:
            strings_data = layers.strings.get(default_lang)
        if strings_data is None:
            continue  # no strings file for this page's language → skip
        for ref in refs:
            if not _resolve_dotted(strings_data, ref):
                lang_label = lang or default_lang or "?"
                out.append(
                    f"[error] {page.rel} references {{strings.{ref}}} but key `{ref}` is "
                    f"not defined in content/strings/{lang_label}.json. Add `{ref}` to that "
                    f"strings file, or fix the reference in {page.rel}."
                )
    return out


def _check_sections_exist(project_root: Path, layers: _Layers) -> list[str]:
    """Check 4 — sections referenced by pages exist in sections.yaml."""
    out: list[str] = []
    if layers.sections is None:
        return out  # no sections.yaml → skip
    defined = _defined_names(layers.sections, list_keys=("sections",), name_fields=("name", "id"))
    for page in layers.pages:
        for sec in _string_list(page.frontmatter.get("sections")):
            if sec not in defined:
                out.append(
                    f"[error] {page.rel} references section `{sec}` which is not defined in "
                    f"content/sections.yaml. Add a `{sec}` section there, or fix the "
                    f"`sections:` list in {page.rel}."
                )
    return out


def _check_components_exist(project_root: Path, layers: _Layers) -> list[str]:
    """Check 5 — components referenced in sections.yaml exist in components.yaml."""
    out: list[str] = []
    if layers.sections is None or layers.components is None:
        return out  # need both files → skip
    defined = _defined_names(layers.components, list_keys=("components",), name_fields=("name", "id"))
    for comp in sorted(_referenced_components(layers.sections)):
        if comp not in defined:
            out.append(
                f"[error] content/sections.yaml references component `{comp}` which is not "
                f"defined in components.yaml. Add a `{comp}` component spec there, or fix the "
                f"reference in content/sections.yaml."
            )
    return out


def _check_token_refs(project_root: Path, layers: _Layers) -> list[str]:
    """Check 6 — `{tokens.x.y}` references in components.yaml resolve to brand.yaml.tokens."""
    out: list[str] = []
    if not layers.components_raw or layers.brand is None:
        return out  # need both → skip
    tokens_tree = layers.brand.get("tokens") if isinstance(layers.brand, dict) else None
    refs = sorted(set(_TOKENS_REF.findall(layers.components_raw)))
    for ref in refs:
        if not (isinstance(tokens_tree, dict) and _resolve_dotted(tokens_tree, ref)):
            out.append(
                f"[error] components.yaml references {{tokens.{ref}}} but `tokens.{ref}` is "
                f"not defined in brand.yaml. Add it under `tokens:` in brand.yaml, or fix the "
                f"reference in components.yaml."
            )
    return out


def _check_language_parity(project_root: Path, layers: _Layers, default_lang: str | None) -> list[str]:
    """Check 7 — language files share the default-language key structure.

    Decision 41: a key present in the default language but missing from another
    language is a WARNING (runtime falls back to the default-language value), not a
    hard error.
    """
    out: list[str] = []
    if len(layers.strings) < 2:
        return out  # need >= 2 languages to compare → skip

    # Reference language: project.yaml default_language when its file is present,
    # else the lexicographically-first available language.
    ref_lang = default_lang if (default_lang and default_lang in layers.strings) else None
    if ref_lang is None:
        ref_lang = "en" if "en" in layers.strings else sorted(layers.strings)[0]

    ref_keys = _flatten_keys(layers.strings[ref_lang])
    for lang in sorted(layers.strings):
        if lang == ref_lang:
            continue
        lang_keys = _flatten_keys(layers.strings[lang])
        missing = sorted(ref_keys - lang_keys)
        for key in missing:
            out.append(
                f"[warning] i18n: content/strings/{lang}.json is missing key `{key}` "
                f"(present in {ref_lang}.json). It falls back to the {ref_lang} value at "
                f"runtime (decision 41). To localize it, add `{key}` to "
                f"content/strings/{lang}.json."
            )
    return out


# ---------- The validator (public entry point) ----------

def validate_content_layers(project_root: Path) -> list[str]:
    """Run the 7 cross-layer checks over the 5-layer content stack.

    Returns a list of human findings — each carrying a concrete fix path. Errors
    are prefixed `[error]`; i18n fallbacks (decision 41) are prefixed `[warning]`.
    Empty list ⇒ everything that EXISTS is internally consistent. Absent files make
    their dependent checks no-ops (the layers are authored progressively across
    phases — a greenfield project returns `[]`). Never raises (a defensive caller —
    wb_orchestrate action 4 — wraps this too, but the contract is no-raise).

    project_root is passed in explicitly (no os.getcwd()).
    """
    findings: list[str] = []
    try:
        layers = _load_layers(project_root)
    except Exception as exc:  # noqa: BLE001 — a loader bug yields one finding, never a crash
        return [f"[error] content-layer validation could not load layer files: {exc}"]

    # Check 1 — parse errors gathered during load.
    findings.extend(layers.parse_errors)

    # Default language (Layer 3 reference) from project.yaml.
    default_lang = _read_default_language(project_root)

    # Check 2 — page frontmatter schema (require the `slug` identity field).
    for page in layers.pages:
        if "slug" not in page.frontmatter:
            findings.append(
                f"[error] {page.rel} — page frontmatter is missing the required `slug:` "
                f"field. Add `slug: /your-path` to the frontmatter (Layer 4, "
                f"{CONTENT_LAYERS_DOC})."
            )

    # Checks 3-7.
    findings.extend(_check_string_refs(project_root, layers, default_lang))
    findings.extend(_check_sections_exist(project_root, layers))
    findings.extend(_check_components_exist(project_root, layers))
    findings.extend(_check_token_refs(project_root, layers))
    findings.extend(_check_language_parity(project_root, layers, default_lang))

    return findings


def _read_default_language(project_root: Path) -> str | None:
    """Read `default_language` from `.website-builder/project.yaml` (Layer 3
    reference). Absent / unreadable → None."""
    p = _state_dir(project_root) / "project.yaml"
    if not p.is_file():
        return None
    text, _ = _read_text(p)
    if text is None:
        return None
    try:
        doc = wb_markdown.parse_yaml(text)
    except Exception:  # noqa: BLE001 — a broken project.yaml is not this check's concern
        return None
    val = doc.get("default_language")
    return str(val) if isinstance(val, (str, int)) else None


# ---------- run (debug dispatch — NOT a user-facing wb verb) ----------

def run(argv: list[str], *, project_root: Path) -> int:
    """Debug dispatch: validate + print findings. `--json` emits a JSON array.
    Returns 0 always (a reporter, not a gate — the spine decides what to do with
    the findings). Mirrors wb_orchestrate.run: the resolver is an entry point, not
    a user-facing `wb` verb."""
    parser = argparse.ArgumentParser(
        prog="wb_validate_layers",
        description="Content-layer validation (DESIGN-content-layers.md § 351-362).",
    )
    parser.add_argument("--json", action="store_true",
                        help="Emit findings as a JSON array (else human lines).")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code or 0)

    findings = validate_content_layers(project_root)
    if args.json:
        print(json.dumps(findings, indent=2))
        return 0
    if not findings:
        log_info("content layers OK — no cross-layer inconsistencies found.")
        return 0
    log_info(f"{len(findings)} content-layer finding(s):")
    for f in findings:
        print(f"  - {f}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Standalone entry for isolated debugging. project_root = cwd."""
    args = list(argv if argv is not None else sys.argv[1:])
    return run(args, project_root=Path.cwd())


if __name__ == "__main__":
    sys.exit(main())
