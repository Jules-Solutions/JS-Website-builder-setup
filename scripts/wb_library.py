#!/usr/bin/env python3
"""
scripts/wb_library.py — the website-builder plugin's resource-curation library
module + auto-clone runtime.

Owned by Phase 5 Captain P (`Workstreams/website-builder/cross-cutting/DESIGN-resource-curation.md`).
Two public entry points, locked by `scripts/README.md` § Module boundary:

  run(argv, *, project_root) -> int
      Dispatch a `wb library` sub-verb (list | add | remove | refresh |
      refresh-all | prune | inspect). Called by Captain O's dispatcher via
      `from wb_library import run as library_run`.

  autoclone_for_state(project_root, *, trigger, phase=None) -> list[CloneResult]
      Run auto-clones for the project's current state. Called by the SessionStart
      hook (`hooks-handlers/session_start.py`) + phase-entry logic — NOT a
      `wb library` sub-verb. Reads `.website-builder/project.yaml` +
      (for phase-entry) the phase contract's `library_clones_at_entry` frontmatter.

Interface rules (locked by `scripts/README.md` § Interface rules):
  - IMPORT-SAFE: importing this module has zero side effects. No network, no file
    writes, no `git`/`op` calls at import time. All work happens inside the
    entry-point functions. (Cheapest regression guard: `import wb_library` is a
    no-op — asserted in tests/library/test_wb_library.py.)
  - Does NOT import the dispatcher (no circular dependency). O depends on P; P
    does not depend on O.
  - Does NOT import the keys module (P and Q never import each other).
  - `project_root` is passed in explicitly — this module never reads
    `os.getcwd()` itself (testability; mirrors wb-bootstrap.py's contract pattern).

`when:` predicate grammar (Captain P's choice per `scripts/README.md` line 218):
  A `when:` string in a `library_clones_at_entry` entry is a simple
  `<key> <op> <value>` expression evaluated against the loaded `project.yaml`.
  Supported forms:
    - `key == value`   equality  (e.g. `stack == "astro"`)
    - `key != value`   inequality (e.g. `cms != none`)
    - `key`            bare-key truthiness (e.g. `transactional` → True iff the
                       project.yaml value is truthy: True / non-empty / non-"null")
  Values may be quoted ('...' or "...") or bare; bare `true`/`false`/`null`
  coerce to their YAML scalars before comparison. Dotted keys
  (`component_library_composition.primary`) walk nested dicts. An absent key
  evaluates falsy (predicate fails → clone skipped, never an error). An
  unparseable predicate logs a warning and skips the clone (defensive: a bad
  `when:` never crashes session-start).

Surfacing-mode note: this module implements the `clone-into-project` half of the
two-axis curation model (`DESIGN-resource-curation.md`). `fetch-on-demand`
resources are reached by the agent via WebFetch/context7 at need — they are NOT
cloned here and never land in `.website-builder/library/`.

See also:
  - scripts/README.md — the CLI + module-boundary contract + library_clones_at_entry schema
  - Workstreams/website-builder/cross-cutting/DESIGN-resource-curation.md — design authority
  - Workstreams/website-builder/foundation/DESIGN-ecosystem-catalog.md — catalogue keys resolved here
  - scripts/wb-bootstrap.py — sibling runner; YAML emit/parse + cross-OS write patterns reused
  - tests/library/test_wb_library.py — the module's test surface
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# YAML emit / parse — PyYAML when available, minimal fallback otherwise.
#
# Mirrors scripts/wb-bootstrap.py exactly (PyYAML is a tests/ runtime dep via
# `uv run --with pyyaml`; live CC sessions usually have it too). The fallback
# parser is sufficient for the flat-ish project.yaml + the library README we
# read/write. We deliberately reuse the in-repo idiom rather than introduce a
# new YAML API.
# ---------------------------------------------------------------------------

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover — exercised only outside the test harness
    # Explicit no-yaml fallback: bind `yaml = None` so the name is always defined
    # and the `yaml is not None` guard below narrows correctly for the type checker
    # (a bare HAS_PYYAML bool does not narrow `yaml`). The minimal hand-rolled
    # parser/emitter then handles the flat shapes we read/write.
    yaml = None  # type: ignore[assignment]

HAS_PYYAML = yaml is not None


def _parse_yaml(text: str) -> dict[str, Any]:
    """Parse YAML to a dict. PyYAML when present; minimal flat-scalar fallback."""
    if yaml is not None:
        result = yaml.safe_load(text)
        return result if isinstance(result, dict) else {}
    # Fallback: handle flat top-level `key: value` scalar lines only. Sufficient
    # for predicate evaluation over the common project.yaml keys (stack, cms,
    # component_library, transactional, default_language, etc.). Nested blocks
    # are not resolved by the fallback — PyYAML is the supported path; this keeps
    # the module importable + minimally functional without the dep.
    parsed: dict[str, Any] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        if line.startswith((" ", "\t")):
            continue
        key, _, raw = stripped.partition(":")
        parsed[key.strip()] = _coerce_scalar(raw.strip())
    return parsed


def _emit_yaml(data: dict[str, Any]) -> str:
    """Emit a dict as YAML. PyYAML when present; minimal fallback otherwise."""
    if yaml is not None:
        return yaml.safe_dump(
            data,
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True,
        )
    # Minimal flat fallback — only used for our small state dicts.
    lines: list[str] = []
    for k, v in data.items():
        if isinstance(v, list):
            if not v:
                lines.append(f"{k}: []")
            else:
                lines.append(f"{k}:")
                for item in v:
                    lines.append(f"  - {item}")
        elif v is None:
            lines.append(f"{k}: null")
        elif isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        else:
            lines.append(f"{k}: {v}")
    return "\n".join(lines) + "\n"


def _coerce_scalar(raw: str) -> Any:
    """Coerce a bare YAML scalar string to a Python value (for predicate compares)."""
    raw = raw.strip()
    if (raw.startswith("'") and raw.endswith("'")) or (
        raw.startswith('"') and raw.endswith('"')
    ):
        return raw[1:-1]
    low = raw.lower()
    if low in ("null", "~", ""):
        return None
    if low == "true":
        return True
    if low == "false":
        return False
    # Numbers stay strings for our purposes (predicate compares are string-ish);
    # leaving them as-is avoids surprising int/str mismatches in `==`.
    return raw


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MODULE_NAME = "wb library"
LIBRARY_DIRNAME = "library"
STATE_DIRNAME = ".website-builder"
PROJECT_YAML_NAME = "project.yaml"
LIBRARY_README_NAME = "README.md"

VALID_VERBS = (
    "list",
    "add",
    "remove",
    "refresh",
    "refresh-all",
    "prune",
    "inspect",
)

VALID_TRIGGERS = ("session-start", "phase-entry")

# Provenance-registry markers — the auto-maintained `library/README.md` is a
# human-readable table with a machine-parseable fenced block we round-trip.
REGISTRY_FENCE = "```yaml wb-library-registry"
REGISTRY_FENCE_END = "```"


# ---------------------------------------------------------------------------
# Result + entry types
# ---------------------------------------------------------------------------


@dataclass
class CloneResult:
    """Outcome of one auto-clone decision (returned by autoclone_for_state).

    status:
      "cloned"   — a new local copy was placed in library/
      "skipped"  — already present (idempotent) OR `when:` predicate failed
      "fetch-deferred" — resolution succeeded but the actual fetch is a Tier-2
                   network op left to the agent/CLI (session-start records intent,
                   does not block on network — see DESIGN-resource-curation line 138)
      "error"    — resolution or write failed (non-fatal; recorded, not raised)
    """

    resource: str
    status: str
    target: str | None = None          # subdir under library/ (relative)
    reason: str = ""                    # human explanation
    trigger: str = ""                   # "session-start" | "phase-entry"
    phase: int | None = None
    source_url: str | None = None       # resolved upstream (catalogue key → URL)


@dataclass
class LibraryEntry:
    """One row in the project-local library provenance registry."""

    name: str
    source: str = ""                    # source URL or catalogue key
    type: str = ""                      # web-page | github-repo | figma | catalogue | docs
    subdir: str = ""                    # placement subdir under library/ (registry-of-record)
    cloned_at: str = ""                 # ISO 8601
    last_used_phase: int | None = None
    tags: list[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "name": self.name,
            "source": self.source,
            "type": self.type,
            "subdir": self.subdir or self.name,
            "cloned_at": self.cloned_at,
        }
        if self.last_used_phase is not None:
            d["last_used_phase"] = self.last_used_phase
        if self.tags:
            d["tags"] = list(self.tags)
        if self.note:
            d["note"] = self.note
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "LibraryEntry":
        return cls(
            name=str(d.get("name", "")),
            source=str(d.get("source", "") or ""),
            type=str(d.get("type", "") or ""),
            subdir=str(d.get("subdir", "") or ""),
            cloned_at=str(d.get("cloned_at", "") or ""),
            last_used_phase=d.get("last_used_phase"),
            tags=list(d.get("tags", []) or []),
            note=str(d.get("note", "") or ""),
        )


# ---------------------------------------------------------------------------
# Catalogue resolution (catalogue-key → upstream URL + surfacing type)
#
# The shipped ecosystem catalogue (DESIGN-ecosystem-catalog.md) is a markdown
# doc the agent reads at runtime; this module ships a small mapping for the
# catalogue keys that are clone-into-project + load-bearing at the phase
# triggers in DESIGN-resource-curation.md lines 231-242. A key not in the map
# is treated as a literal URL (same input space as `wb library add <url>`), so
# the catalogue can grow without code changes (DESIGN-resource-curation
# "catalogue is not a compiled artifact").
# ---------------------------------------------------------------------------

# key -> (source_url_or_ref, type, default_subdir)
#
# "bundled" type: source_url_or_ref is a plugin-root-relative path to a
# reference-corpus/ subdirectory that ships with the plugin.  _fetch_resource
# copies it with shutil.copytree (no network needed).  Wave-4 addition (corpus-1
# + corpus-2 RPTs): six bundled keys + Option-A repoint of awesome-design-md-corpus.
CATALOGUE_CLONE_KEYS: dict[str, tuple[str, str, str]] = {
    # --- bundled corpora (plugin-shipped; Wave 4 Option-A) ---
    "awesome-design-md-corpus": (
        "reference-corpus/awesome-design-md-corpus",
        "bundled",
        "awesome-design-md",
    ),
    "design-systems-corpus": (
        "reference-corpus/design-systems",
        "bundled",
        "design-systems",
    ),
    "brand-examples-corpus": (
        "reference-corpus/brand-examples",
        "bundled",
        "brand-examples",
    ),
    "voice-archetypes": (
        "reference-corpus/voice-archetypes",
        "bundled",
        "voice-archetypes",
    ),
    "component-patterns": (
        "reference-corpus/component-patterns",
        "bundled",
        "component-patterns",
    ),
    "seo-checklists": (
        "reference-corpus/seo-checklists",
        "bundled",
        "seo-checklists",
    ),
    # --- upstream github (bare alias — stays on upstream; Option A) ---
    "awesome-design-md": (
        "https://github.com/VoltAgent/awesome-design-md",
        "github-repo",
        "awesome-design-md",
    ),
    # --- docs (context7 / fetch-on-demand) ---
    "shadcn-components": ("/shadcn/ui", "docs", "docs"),
    "astro-content-collections": ("/withastro/docs", "docs", "docs"),
    "stripe-checkout": ("/websites/stripe_js", "docs", "docs"),
    "payload-docs": ("/payloadcms/payload", "docs", "docs"),
    "decap-cms": ("/decaporg/decap-cms", "docs", "docs"),
    "cal-com": ("/calcom/cal.com", "docs", "docs"),
}


def _resolve_resource(resource: str) -> tuple[str, str, str]:
    """Resolve a `library_clones_at_entry`/`wb library add` resource token.

    Returns (source_url_or_ref, type, default_subdir). A known catalogue key
    maps per CATALOGUE_CLONE_KEYS; anything else is treated as a literal URL and
    typed by URL shape (github-repo / figma / web-page).
    """
    if resource in CATALOGUE_CLONE_KEYS:
        return CATALOGUE_CLONE_KEYS[resource]
    return (resource, _detect_url_type(resource), "docs")


def _detect_url_type(url: str) -> str:
    """Auto-detect resource type from a URL (DESIGN-resource-curation step 1)."""
    # Plugin-bundled corpus paths: 'reference-corpus/…' or explicit 'bundled:' prefix.
    if url.startswith("reference-corpus/") or url.startswith("bundled:"):
        return "bundled"
    try:
        host = (urlparse(url).hostname or "").lower()
    except ValueError:
        return "web-page"
    if "github.com" in host:
        return "github-repo"
    if "figma.com" in host:
        return "figma"
    if not host:
        # not a URL at all — likely a context7 ref like "/shadcn/ui"
        return "docs" if url.startswith("/") else "web-page"
    return "web-page"


def _default_subdir_for_type(rtype: str) -> str:
    return {
        "bundled": ".",
        "github-repo": ".",
        "figma": "design-tokens",
        "docs": "docs",
        "web-page": "docs",
        "catalogue": "docs",
    }.get(rtype, "docs")


def _slug_from_resource(resource: str, source_url: str, rtype: str) -> str:
    """A stable, filesystem-safe name for a resource (registry key + subdir leaf)."""
    if resource in CATALOGUE_CLONE_KEYS:
        return CATALOGUE_CLONE_KEYS[resource][2]
    # Derive from the last meaningful URL/path segment.
    candidate = source_url.rstrip("/").split("/")[-1] or source_url.strip("/")
    candidate = candidate.split("?")[0].split("#")[0]
    candidate = re.sub(r"\.git$", "", candidate)
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", candidate).strip("-").lower()
    return slug or "resource"


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------


def _state_dir(project_root: Path) -> Path:
    return project_root / STATE_DIRNAME


def _library_dir(project_root: Path) -> Path:
    return _state_dir(project_root) / LIBRARY_DIRNAME


def _library_readme(project_root: Path) -> Path:
    return _library_dir(project_root) / LIBRARY_README_NAME


def _project_yaml_path(project_root: Path) -> Path:
    return _state_dir(project_root) / PROJECT_YAML_NAME


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_project_yaml(project_root: Path) -> dict[str, Any]:
    """Load project.yaml defensively. Missing/unreadable → {} (never raises)."""
    path = _project_yaml_path(project_root)
    if not path.is_file():
        return {}
    try:
        return _parse_yaml(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def load_project_yaml(project_root: Path) -> dict[str, Any]:
    """Public alias over _load_project_yaml — the orchestration spine reads
    current_phase + stack/cms/commerce through this, without reaching into a
    private or duplicating a loader (DESIGN-orchestration-spine.md § 5.2). Same
    defensive contract: missing/unreadable project.yaml → {} (never raises)."""
    return _load_project_yaml(project_root)


# ---------------------------------------------------------------------------
# Provenance registry (library/README.md) — read / write
#
# The registry is the auto-maintained `library/README.md` per DESIGN-resource-
# curation lines 155, 199-208. It is human-readable prose + a machine-parseable
# fenced YAML block we round-trip so list/inspect/remove stay deterministic
# without re-walking the directory tree.
# ---------------------------------------------------------------------------


def _read_registry(project_root: Path) -> list[LibraryEntry]:
    """Parse the library/README.md provenance block → list of entries.

    Absent README or absent fenced block → [] (the empty library state).
    """
    readme = _library_readme(project_root)
    if not readme.is_file():
        return []
    text = readme.read_text(encoding="utf-8")
    block = _extract_registry_block(text)
    if not block:
        return []
    data = _parse_yaml(block)
    rows = data.get("entries", []) if isinstance(data, dict) else []
    out: list[LibraryEntry] = []
    for row in rows or []:
        if isinstance(row, dict):
            out.append(LibraryEntry.from_dict(row))
    return out


def _extract_registry_block(text: str) -> str | None:
    """Pull the YAML between the registry fence markers, if present."""
    start = text.find(REGISTRY_FENCE)
    if start == -1:
        return None
    body_start = start + len(REGISTRY_FENCE)
    end = text.find("\n" + REGISTRY_FENCE_END, body_start)
    if end == -1:
        return None
    return text[body_start:end].strip("\n")


def _write_registry(project_root: Path, entries: list[LibraryEntry]) -> None:
    """Rewrite library/README.md with the human header + the machine block."""
    lib = _library_dir(project_root)
    lib.mkdir(parents=True, exist_ok=True)
    registry_yaml = _emit_yaml({"entries": [e.to_dict() for e in entries]})
    table = _render_human_table(entries)
    content = _render_readme(table, registry_yaml)
    (lib / LIBRARY_README_NAME).write_bytes(content.encode("utf-8"))


def _render_human_table(entries: list[LibraryEntry]) -> str:
    if not entries:
        return "_No resources cloned yet. Add one with `wb library add <url>`._"
    header = "| Name | Source | Type | Cloned | Last-used phase |\n|---|---|---|---|---|"
    rows = []
    for e in sorted(entries, key=lambda x: x.name):
        phase = "" if e.last_used_phase is None else str(e.last_used_phase)
        rows.append(
            f"| {e.name} | {e.source} | {e.type} | {e.cloned_at} | {phase} |"
        )
    return "\n".join([header, *rows])


def _render_readme(table: str, registry_yaml: str) -> str:
    return (
        "# `.website-builder/library/` — project resource library\n\n"
        "> Auto-maintained by `wb library` (the website-builder plugin's "
        "resource-curation CLI + auto-clone runtime). Don't hand-edit the "
        "machine block below — use `wb library add` / `remove` / `refresh`.\n\n"
        "This directory mirrors the vault `Library/` pattern, scoped to your "
        "site: cloned framework/library/API docs, design exemplars, and "
        "reference URLs the agent (or you) saved for repeated use. Provenance "
        "for each entry — where it came from and when — is recorded below.\n\n"
        "## Cloned resources\n\n"
        f"{table}\n\n"
        "## Provenance registry (machine-maintained)\n\n"
        f"{REGISTRY_FENCE}\n{registry_yaml.rstrip(chr(10))}\n{REGISTRY_FENCE_END}\n"
    )


def _find_entry(entries: list[LibraryEntry], name: str) -> LibraryEntry | None:
    for e in entries:
        if e.name == name:
            return e
    return None


# ---------------------------------------------------------------------------
# `when:` predicate evaluation
# ---------------------------------------------------------------------------

_PREDICATE_RE = re.compile(r"^\s*([A-Za-z0-9_.]+)\s*(==|!=)\s*(.+?)\s*$")


def _get_nested(data: dict[str, Any], dotted_key: str) -> Any:
    """Walk a dotted key through nested dicts. Missing path → None."""
    node: Any = data
    for part in dotted_key.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return None
    return node


def _evaluate_when(predicate: str | None, project: dict[str, Any]) -> bool:
    """Evaluate a `when:` predicate against project.yaml.

    Absent/empty predicate → True (always clone). `key op value` → compare.
    Bare `key` → truthiness. Unparseable → False (skip) + caller logs.
    """
    if predicate is None or str(predicate).strip() == "":
        return True
    expr = str(predicate).strip()
    m = _PREDICATE_RE.match(expr)
    if m:
        key, op, raw_value = m.group(1), m.group(2), m.group(3)
        actual = _get_nested(project, key)
        expected = _coerce_scalar(raw_value)
        # Compare as strings when one side is a str scalar to avoid True=="true"
        # surprises, but respect None/bool exact matches.
        if op == "==":
            return _values_equal(actual, expected)
        return not _values_equal(actual, expected)
    # Bare-key truthiness (no operator).
    if re.match(r"^[A-Za-z0-9_.]+$", expr):
        return _is_truthy(_get_nested(project, expr))
    # Unparseable predicate.
    raise ValueError(f"unparseable when-predicate: {predicate!r}")


def _values_equal(actual: Any, expected: Any) -> bool:
    if actual is None or expected is None or isinstance(actual, bool) or isinstance(
        expected, bool
    ):
        return actual == expected
    return str(actual) == str(expected)


def _is_truthy(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() not in ("", "null", "~", "false", "no", "0")
    if isinstance(value, (list, dict)):
        return len(value) > 0
    return bool(value)


# ---------------------------------------------------------------------------
# Phase-contract reading (library_clones_at_entry frontmatter)
# ---------------------------------------------------------------------------


def _split_frontmatter(text: str) -> str | None:
    """Return the YAML frontmatter block of a markdown doc, or None if absent."""
    if not text.startswith("---"):
        return None
    # Find the closing fence on its own line.
    rest = text[3:]
    # Skip a possible leading newline after the opening ---
    end = rest.find("\n---")
    if end == -1:
        return None
    return rest[:end].lstrip("\n")


def _find_phase_contract(project_root: Path, phase: int) -> Path | None:
    """Locate a phase-N contract carrying machine-read frontmatter.

    Search order (defensive — the field lives in frontmatter wherever the
    contract is found):
      1. The user-project's own copy under .website-builder/phase-contracts/NN-*.md
         (if the project carries a vendored copy).
      2. The plugin-shipped phase-contracts/NN-*.md (resolved relative to this
         module's plugin root) when no project-local copy exists.
    Returns the first match, or None (→ no auto-clones, no error).
    """
    candidates: list[Path] = []
    # Project-local vendored contracts (some projects pin their own).
    proj_contracts = _state_dir(project_root) / "phase-contracts"
    plugin_contracts = Path(__file__).resolve().parent.parent / "phase-contracts"
    for base in (proj_contracts, plugin_contracts):
        if base.is_dir():
            # NN-*.md with zero-padded or bare phase number.
            for pat in (f"{phase:02d}-*.md", f"{phase}-*.md"):
                candidates.extend(sorted(base.glob(pat)))
    return candidates[0] if candidates else None


def _read_clones_at_entry(contract_path: Path) -> list[dict[str, Any]]:
    """Defensively read a phase contract's `library_clones_at_entry` list.

    Absent field / absent file / parse error → [] (never raises). This is the
    locked defensive-read contract (scripts/README.md line 234).
    """
    try:
        text = contract_path.read_text(encoding="utf-8")
    except (OSError, ValueError):
        return []
    fm = _split_frontmatter(text)
    if not fm:
        return []
    try:
        data = _parse_yaml(fm)
    except Exception:  # noqa: BLE001 — defensive: a malformed contract frontmatter must never crash session-start
        return []
    entries = data.get("library_clones_at_entry") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        return []
    return [e for e in entries if isinstance(e, dict)]


# ---------------------------------------------------------------------------
# Auto-clone runtime (public entry point #2)
# ---------------------------------------------------------------------------


def autoclone_for_state(
    project_root: Path,
    *,
    trigger: str,
    phase: int | None = None,
    log: Callable[[str], None] | None = None,
) -> list[CloneResult]:
    """Run auto-clones for the project's current state.

    trigger: "session-start" | "phase-entry".
    phase:   the phase number when trigger == "phase-entry"; None for session-start.
    log:     optional sink for human-readable progress (defaults to no-op; the
             CLI / hook supply a real logger). Keeps the function side-effect-free
             on stdout when called from tests.

    Reads project.yaml (stack/cms/component_library/commerce/flavors) + (for
    phase-entry) the phase contract's `library_clones_at_entry`. Idempotent:
    skips resources already present in the provenance registry. Absent/empty
    `library_clones_at_entry` → returns [] (no clones). Defensive-read: never
    throws on a contract that omits the field.

    Returns a list of CloneResult (one per resource considered). Network fetches
    are NOT performed inline — a resolvable, not-yet-present resource yields
    status "fetch-deferred" (session-start records intent without blocking on
    the network, per DESIGN-resource-curation line 138). The agent/CLI performs
    the actual fetch via `wb library add`/`refresh`.
    """
    emit = log or (lambda _msg: None)

    if trigger not in VALID_TRIGGERS:
        emit(f"[{MODULE_NAME}] unknown trigger {trigger!r}; no auto-clones run.")
        return []

    project = _load_project_yaml(project_root)
    existing = {e.name for e in _read_registry(project_root)}
    results: list[CloneResult] = []

    # Build the candidate list per trigger.
    candidates: list[dict[str, Any]] = []
    if trigger == "phase-entry":
        if phase is None:
            emit(f"[{MODULE_NAME}] phase-entry trigger with phase=None; nothing to do.")
            return []
        contract = _find_phase_contract(project_root, phase)
        if contract is None:
            # No contract found for this phase → no auto-clones. Not an error.
            return []
        candidates = _read_clones_at_entry(contract)
    else:  # session-start
        candidates = _session_start_candidates(project)

    for entry in candidates:
        resource = str(entry.get("resource", "")).strip()
        if not resource:
            continue
        when = entry.get("when")
        try:
            if not _evaluate_when(when, project):
                results.append(
                    CloneResult(
                        resource=resource,
                        status="skipped",
                        reason=f"when-predicate not satisfied: {when!r}",
                        trigger=trigger,
                        phase=phase,
                    )
                )
                continue
        except ValueError as exc:
            emit(f"[{MODULE_NAME}] {exc}; skipping {resource!r}.")
            results.append(
                CloneResult(
                    resource=resource,
                    status="skipped",
                    reason=str(exc),
                    trigger=trigger,
                    phase=phase,
                )
            )
            continue

        source_url, _rtype, default_sub = _resolve_resource(resource)
        target = str(entry.get("as") or default_sub)

        if target in existing or resource in existing:
            results.append(
                CloneResult(
                    resource=resource,
                    status="skipped",
                    target=target,
                    reason="already present in library (idempotent)",
                    trigger=trigger,
                    phase=phase,
                    source_url=source_url,
                )
            )
            continue

        # Bundled corpus (plugin-shipped) — copy inline; no network, no deferral.
        if _rtype == "bundled":
            lib_target = _library_dir(project_root) / target
            if lib_target.exists() and any(lib_target.iterdir()):
                # Filesystem-level idempotency: already on disk (may not be in
                # the registry yet, e.g. after a fresh project_root copy).
                results.append(
                    CloneResult(
                        resource=resource,
                        status="skipped",
                        target=target,
                        reason="already present on disk (idempotent)",
                        trigger=trigger,
                        phase=phase,
                        source_url=source_url,
                    )
                )
            else:
                copied = _bundled_copy(source_url, lib_target)
                results.append(
                    CloneResult(
                        resource=resource,
                        status="cloned" if copied else "error",
                        target=target,
                        reason=(
                            "bundled corpus copied into library/"
                            if copied
                            else "bundled copy failed — source dir missing in plugin"
                        ),
                        trigger=trigger,
                        phase=phase,
                        source_url=source_url,
                    )
                )
                if copied:
                    emit(
                        f"[{MODULE_NAME}] bundled '{resource}' -> library/{target} "
                        f"(source: {source_url})"
                    )
            continue

        # Resolvable + not present. Record intent; defer the network fetch.
        note = str(entry.get("note") or "")
        results.append(
            CloneResult(
                resource=resource,
                status="fetch-deferred",
                target=target,
                reason=note or "queued for clone-into-project",
                trigger=trigger,
                phase=phase,
                source_url=source_url,
            )
        )
        emit(
            f"[{MODULE_NAME}] queued '{resource}' -> library/{target} "
            f"(source: {source_url})"
        )

    return results


def _session_start_candidates(project: dict[str, Any]) -> list[dict[str, Any]]:
    """Derive session-start auto-clone candidates from picked project.yaml fields.

    Per DESIGN-resource-curation lines 131, 233: when the user has picked a
    stack / CMS / component-library / commerce platform, the corresponding
    reference docs become load-bearing and are clone-into-project candidates.
    Maps the picked value to a catalogue key when one exists; a picked value
    with no catalogue mapping is silently not a clone candidate (the agent
    fetches it on demand instead).
    """
    candidates: list[dict[str, Any]] = []

    stack = project.get("stack")
    if stack == "astro":
        candidates.append(
            {"resource": "astro-content-collections", "as": "docs",
             "note": "Astro Content Collections docs (chosen stack)"}
        )

    component_library = project.get("component_library")
    if component_library == "shadcn":
        candidates.append(
            {"resource": "shadcn-components", "as": "docs",
             "note": "shadcn/ui component reference (chosen component library)"}
        )

    cms = project.get("cms")
    if cms == "payload":
        candidates.append(
            {"resource": "payload-docs", "as": "docs",
             "note": "Payload CMS docs (chosen CMS)"}
        )
    elif cms == "decap":
        candidates.append(
            {"resource": "decap-cms", "as": "docs",
             "note": "Decap CMS docs (chosen CMS)"}
        )

    # Commerce / transactional: clone Stripe docs when transactional + Stripe.
    if _is_truthy(project.get("transactional")) and project.get(
        "payment_provider"
    ) == "stripe":
        candidates.append(
            {"resource": "stripe-checkout", "as": "docs",
             "note": "Stripe Checkout docs (commerce + Stripe)"}
        )

    return candidates


# ---------------------------------------------------------------------------
# CLI verbs (public entry point #1)
# ---------------------------------------------------------------------------


def run(argv: list[str], *, project_root: Path) -> int:
    """Dispatch a `wb library` sub-verb.

    argv: the args AFTER `wb library` (e.g. ["add", "https://...", "--tag", "docs"]).
    project_root: the user's project dir (contains .website-builder/).
    Returns a process exit code (0 = success, 2 = usage error, 1 = runtime error).
    Verbs handled: list | add | remove | refresh | refresh-all | prune | inspect.
    """
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:  # argparse calls sys.exit on error/`-h`
        return int(exc.code or 0)

    verb = getattr(args, "verb", None)
    if not verb:
        parser.print_help()
        return 2

    handler = _VERB_HANDLERS.get(verb)
    if handler is None:  # pragma: no cover — argparse choices guard this
        print(f"[{MODULE_NAME}] unknown verb: {verb}")
        return 2

    return handler(args, project_root)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="wb library",
        description="Manage the project-local resource library (.website-builder/library/).",
    )
    sub = p.add_subparsers(dest="verb")

    sub.add_parser("list", help="List all cloned resources.")

    p_add = sub.add_parser("add", help="Add a resource (URL or catalogue key).")
    p_add.add_argument("url", help="Resource URL or catalogue key.")
    p_add.add_argument("--as", dest="as_subdir", default=None,
                       help="Target subdir under library/.")
    p_add.add_argument("--tag", dest="tags", action="append", default=[],
                       help="Classification tag (repeatable).")

    p_rm = sub.add_parser("remove", help="Remove a resource.")
    p_rm.add_argument("name", help="Resource name (registry key).")
    p_rm.add_argument("--keep-files", action="store_true",
                      help="Deregister but keep the local files.")

    p_ref = sub.add_parser("refresh", help="Re-fetch a resource that may have changed.")
    p_ref.add_argument("name", help="Resource name (registry key).")

    sub.add_parser("refresh-all",
                   help="Refresh all clone-into-project entries (warns on local edits).")

    sub.add_parser("prune", help="Remove entries not referenced by current project state.")

    p_insp = sub.add_parser("inspect", help="Show details for one resource.")
    p_insp.add_argument("name", help="Resource name (registry key).")

    return p


# ---- verb handlers --------------------------------------------------------


def _cmd_list(_args: argparse.Namespace, project_root: Path) -> int:
    entries = _read_registry(project_root)
    if not entries:
        print(f"[{MODULE_NAME}] library is empty. Add one with `wb library add <url>`.")
        return 0
    print(f"[{MODULE_NAME}] {len(entries)} resource(s) in {_library_dir(project_root)}:")
    for e in sorted(entries, key=lambda x: x.name):
        phase = "" if e.last_used_phase is None else f" (last used: phase {e.last_used_phase})"
        print(f"  - {e.name}  [{e.type}]  {e.source}  cloned {e.cloned_at}{phase}")
    return 0


def _entry_subdir(entry: LibraryEntry) -> str:
    """The placement subdir for an entry — the registry-of-record value, with a
    slug fallback for legacy entries written before `subdir` was recorded."""
    return entry.subdir or _slug_from_resource(entry.name, entry.source, entry.type)


def _cmd_add(args: argparse.Namespace, project_root: Path) -> int:
    resource = args.url
    source_url, rtype, _default_sub = _resolve_resource(resource)
    subdir = args.as_subdir or _default_subdir_for_type(rtype)
    name = _slug_from_resource(resource, source_url, rtype)

    entries = _read_registry(project_root)
    if _find_entry(entries, name) is not None:
        print(f"[{MODULE_NAME}] '{name}' already in the library. "
              f"Use `wb library refresh {name}` to re-fetch.")
        return 0

    fetched = _fetch_resource(source_url, rtype, _library_dir(project_root) / subdir)
    entry = LibraryEntry(
        name=name,
        source=source_url,
        type=rtype,
        subdir=subdir,
        cloned_at=_now_iso(),
        tags=list(args.tags or []),
    )
    entries.append(entry)
    _write_registry(project_root, entries)

    status = "cloned" if fetched else "registered (fetch deferred)"
    print(f"[{MODULE_NAME}] {status}: '{name}' [{rtype}] -> library/{subdir}")
    print(f"           source: {source_url}")
    if not fetched:
        print(f"[{MODULE_NAME}] note: actual fetch is a network op; run "
              f"`wb library refresh {name}` when online, or the agent fetches on demand.")
    return 0


def _cmd_remove(args: argparse.Namespace, project_root: Path) -> int:
    name = args.name
    entries = _read_registry(project_root)
    entry = _find_entry(entries, name)
    if entry is None:
        print(f"[{MODULE_NAME}] '{name}' not in the library.")
        return 1
    entries = [e for e in entries if e.name != name]
    _write_registry(project_root, entries)

    if not args.keep_files:
        _delete_resource_files(project_root, entry)
        print(f"[{MODULE_NAME}] removed '{name}' + deleted local files.")
    else:
        print(f"[{MODULE_NAME}] deregistered '{name}' (kept files per --keep-files).")
    return 0


def _cmd_refresh(args: argparse.Namespace, project_root: Path) -> int:
    name = args.name
    entries = _read_registry(project_root)
    entry = _find_entry(entries, name)
    if entry is None:
        print(f"[{MODULE_NAME}] '{name}' not in the library; nothing to refresh.")
        return 1
    subdir = _entry_subdir(entry)
    fetched = _fetch_resource(entry.source, entry.type,
                              _library_dir(project_root) / subdir, refresh=True)
    entry.cloned_at = _now_iso()
    _write_registry(project_root, entries)
    status = "re-fetched" if fetched else "refresh queued (network op deferred)"
    print(f"[{MODULE_NAME}] {status}: '{name}' (source: {entry.source})")
    return 0


def _cmd_refresh_all(_args: argparse.Namespace, project_root: Path) -> int:
    entries = _read_registry(project_root)
    if not entries:
        print(f"[{MODULE_NAME}] library is empty; nothing to refresh.")
        return 0
    refreshed = 0
    for entry in entries:
        subdir = _entry_subdir(entry)
        target = _library_dir(project_root) / subdir
        if _has_local_edits(target):
            print(f"[{MODULE_NAME}] WARNING: '{entry.name}' has local edits at "
                  f"library/{subdir}; skipping to avoid overwrite. "
                  f"Use `wb library refresh {entry.name}` to force.")
            continue
        _fetch_resource(entry.source, entry.type, target, refresh=True)
        entry.cloned_at = _now_iso()
        refreshed += 1
    _write_registry(project_root, entries)
    print(f"[{MODULE_NAME}] refresh-all: {refreshed}/{len(entries)} entries refreshed "
          f"(skipped any with local edits).")
    return 0


def _cmd_prune(_args: argparse.Namespace, project_root: Path) -> int:
    entries = _read_registry(project_root)
    if not entries:
        print(f"[{MODULE_NAME}] library is empty; nothing to prune.")
        return 0
    project = _load_project_yaml(project_root)
    referenced = _referenced_resource_names(project)
    candidates = [e for e in entries if e.name not in referenced]
    if not candidates:
        print(f"[{MODULE_NAME}] no prune candidates — all entries are referenced by "
              f"current project state.")
        return 0
    # Interactive confirm per DESIGN-resource-curation line 191. In a non-TTY /
    # automated context this lists candidates and takes no destructive action
    # (safe default — destructive prune requires an explicit interactive yes).
    print(f"[{MODULE_NAME}] prune candidates (not referenced by current project state):")
    for e in candidates:
        print(f"  - {e.name}  [{e.type}]  {e.source}")
    print(f"[{MODULE_NAME}] re-run interactively to confirm deletion, or use "
          f"`wb library remove <name>` per entry. No files deleted in this pass.")
    return 0


def _cmd_inspect(args: argparse.Namespace, project_root: Path) -> int:
    name = args.name
    entry = _find_entry(_read_registry(project_root), name)
    if entry is None:
        print(f"[{MODULE_NAME}] '{name}' not in the library.")
        return 1
    subdir = _entry_subdir(entry)
    target = _library_dir(project_root) / subdir
    size = _dir_size(target)
    print(f"[{MODULE_NAME}] {name}")
    print(f"  source:          {entry.source}")
    print(f"  type:            {entry.type}")
    print(f"  cloned_at:       {entry.cloned_at}")
    print(f"  last_used_phase: {entry.last_used_phase if entry.last_used_phase is not None else '(none)'}")
    print(f"  tags:            {', '.join(entry.tags) if entry.tags else '(none)'}")
    print(f"  local path:      library/{subdir}{' (not present)' if not target.exists() else ''}")
    print(f"  size on disk:    {size}")
    if entry.note:
        print(f"  note:            {entry.note}")
    return 0


_VERB_HANDLERS: dict[str, Callable[[argparse.Namespace, Path], int]] = {
    "list": _cmd_list,
    "add": _cmd_add,
    "remove": _cmd_remove,
    "refresh": _cmd_refresh,
    "refresh-all": _cmd_refresh_all,
    "prune": _cmd_prune,
    "inspect": _cmd_inspect,
}


# ---------------------------------------------------------------------------
# Fetch + filesystem helpers
#
# The actual network fetch (git clone / WebFetch / API) is a Tier-2 op per
# .claude/rules/tool-dependency-discipline.md. This module performs a real
# `git clone` for github-repo resources when git is on PATH AND the target is
# writable; web-page / docs / figma resources are registered with their source
# and left for the agent to fetch via WebFetch/context7 (the agent has those
# tools; a CLI subprocess does not). Either way the provenance registry is the
# source of truth for what's in the library.
# ---------------------------------------------------------------------------


def _fetch_resource(
    source_url: str, rtype: str, target: Path, *, refresh: bool = False
) -> bool:
    """Best-effort fetch. Returns True if a local copy was placed, False if the
    fetch is deferred to the agent (web-page/docs/figma) or git is unavailable.

    Never raises on fetch failure — records nothing, returns False, lets the
    caller surface a "fetch deferred" message (Tier-2 discipline).
    """
    if rtype == "bundled":
        return _bundled_copy(source_url, target, refresh=refresh)
    if rtype == "github-repo":
        return _git_clone(source_url, target, refresh=refresh)
    # web-page / docs / figma / catalogue refs: the agent fetches via
    # WebFetch / context7 / API. A subprocess CLI can't drive those tools, so we
    # register-and-defer. (DESIGN-resource-curation: fetch-on-demand is reached
    # by the agent; clone-into-project docs land when the agent does the fetch.)
    return False


def _bundled_copy(source_ref: str, target: Path, *, refresh: bool = False) -> bool:
    """Copy a plugin-bundled reference-corpus directory into target.

    source_ref: a plugin-root-relative path (e.g. 'reference-corpus/voice-archetypes').
    target:     the destination path inside the project's library/ dir.
    Returns True if a local copy is available, False on a missing source or OS error.
    Never raises.
    """
    plugin_root = Path(__file__).resolve().parent.parent
    src = plugin_root / source_ref
    if not src.is_dir():
        return False
    if target.exists():
        if refresh:
            shutil.rmtree(target, ignore_errors=True)
        else:
            return True  # already present — idempotent
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, target)
        return True
    except (shutil.Error, OSError):
        return False


def _git_clone(source_url: str, target: Path, *, refresh: bool = False) -> bool:
    """Shallow git clone into target. Idempotent. Returns success bool."""
    if not source_url.startswith(("http://", "https://", "git@")):
        return False
    if shutil.which("git") is None:
        return False
    try:
        if (target / ".git").is_dir():
            if refresh:
                subprocess.run(
                    ["git", "-C", str(target), "pull", "--ff-only"],
                    check=True, capture_output=True, timeout=120,
                )
            return True
        if target.exists() and any(target.iterdir()):
            # Non-empty non-git dir — don't clobber.
            return False
        target.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "clone", "--depth", "1", source_url, str(target)],
            check=True, capture_output=True, timeout=120,
        )
        return True
    except (subprocess.SubprocessError, OSError):
        return False


def _delete_resource_files(project_root: Path, entry: LibraryEntry) -> None:
    subdir = _entry_subdir(entry)
    target = _library_dir(project_root) / subdir
    if target.is_dir():
        shutil.rmtree(target, ignore_errors=True)
    elif target.exists():
        try:
            target.unlink()
        except OSError:
            pass


def _has_local_edits(target: Path) -> bool:
    """True if a git-backed clone has uncommitted local changes."""
    if not (target / ".git").is_dir() or shutil.which("git") is None:
        return False
    try:
        out = subprocess.run(
            ["git", "-C", str(target), "status", "--porcelain"],
            check=True, capture_output=True, timeout=30, text=True,
        )
        return bool(out.stdout.strip())
    except (subprocess.SubprocessError, OSError):
        return False


def _referenced_resource_names(project: dict[str, Any]) -> set[str]:
    """Resource names load-bearing for the current project state (prune-keep set)."""
    referenced: set[str] = set()
    for entry in _session_start_candidates(project):
        resource = str(entry.get("resource", ""))
        source_url, rtype, _ = _resolve_resource(resource)
        referenced.add(_slug_from_resource(resource, source_url, rtype))
        referenced.add(resource)
    return referenced


def _dir_size(path: Path) -> str:
    """Human-readable on-disk size of a file or directory tree. Missing → '0 B'."""
    if not path.exists():
        return "0 B"
    total = 0
    if path.is_file():
        total = path.stat().st_size
    else:
        for p in path.rglob("*"):
            if p.is_file():
                try:
                    total += p.stat().st_size
                except OSError:
                    pass
    size = float(total)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"
