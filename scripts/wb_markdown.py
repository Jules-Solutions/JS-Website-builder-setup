#!/usr/bin/env python3
"""
scripts/wb_markdown.py — shared markdown + frontmatter parsing primitives.

Atomic-unit extraction per `.claude/rules/modular-build-convention.md`: markdown
section + frontmatter parsing is a genuine reusable primitive. Adapters, phase
contracts, and skills are all markdown-with-H2s; `project.yaml` + frontmatter are
YAML. One module owns these helpers; `wb_orchestrate` consumes them; `wb_library`
/ `wb_keys` can later migrate onto them (an optional dedup pass — this module only
*adds* the primitives, it does not refactor the existing parsers).

Public surface (the orchestration spine's §5.1 contract — see
`Workstreams/website-builder/foundation/DESIGN-orchestration-spine.md`):

    extract_h2_section(text, heading, *, include_heading=True, match="exact")
        -> str | None
        Return the body of the `## {heading}` section, from that heading until the
        next `## ` at the same level or EOF. Fence-aware. None if absent.

    parse_frontmatter(text) -> dict[str, Any]
        Split a leading `---`...`---` YAML frontmatter block and parse it. {} if
        absent. Mirrors wb_library._split_frontmatter + a YAML parse.

    parse_yaml(text) -> dict[str, Any]
        PyYAML-when-available, hand-rolled nested fallback otherwise — the exact
        shape proven in wb_keys.py + wb_library._parse_yaml, consolidated here so
        the fallback parser lives in ONE place.

Interface rules (mirrors the locked wb_keys.py / wb_library.py module contract,
`scripts/README.md` § Interface rules):
  - IMPORT-SAFE: importing this module has NO side effects (no network, no file
    writes, no subprocess at import time). It is a pure-function utility module.
  - Does NOT import the dispatcher, wb_keys, wb_library, or wb_orchestrate (it is
    a leaf in the dependency graph — everyone may depend on it; it depends on
    nobody in-repo).
  - No `os.getcwd()`, no global state — every function is pure over its inputs.

`extract_h2_section`'s fence-awareness is the only non-trivial behavior and is the
load-bearing reason this module exists: a `## ` line that appears inside a fenced
code block (``` or ~~~) is content, NOT a heading boundary. Adapter / contract /
skill markdown routinely embeds `## ` lines inside example code fences; a naive
splitter would mis-cut the section there. See tests/markdown/test_wb_markdown.py.

See also:
  - Workstreams/website-builder/foundation/DESIGN-orchestration-spine.md § 5.1
  - scripts/wb_keys.py (parse_yaml fallback shape this consolidates)
  - scripts/wb_library.py (_split_frontmatter the frontmatter splitter mirrors)
  - adapters/README.md (the H2-section schema extract_h2_section reads at runtime)
"""

from __future__ import annotations

from typing import Any

# ---------- YAML parse (PyYAML-with-fallback, consolidated) ----------
#
# PyYAML is the supported path in every runtime that matters (the test harness
# pins it via `uv run --with pyyaml`; live CC sessions usually have it). The
# hand-rolled fallback covers the nested-dict + scalar shapes we read from
# frontmatter (skill:, description:, name:) and project.yaml so the module stays
# importable + minimally functional on a bare interpreter. Mirrors wb_keys.py.

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover — exercised only outside the test harness
    yaml = None  # name always bound (None when unavailable) so `yaml is not None`
                 # narrows correctly for type-checkers without a possibly-unbound warning.

HAS_PYYAML = yaml is not None


def parse_yaml(text: str) -> dict[str, Any]:
    """Parse YAML to a dict. PyYAML when available; minimal nested fallback else.

    A non-mapping document (list/scalar at the root) yields {} — callers here
    always want a mapping (frontmatter / project.yaml are mappings).
    """
    if yaml is not None:
        result = yaml.safe_load(text)
        return result if isinstance(result, dict) else {}
    return _hand_parse_yaml(text)


def _hand_parse_yaml(text: str) -> dict[str, Any]:
    """Minimal indentation-based YAML parser for the nested-dict + scalar shapes
    we read (block mappings, scalar leaves). Lists at the leaves are NOT resolved
    by the fallback (PyYAML is the supported path for those); a `key:` with a
    following `- item` block parses as an empty dict, which is harmless for the
    scalar fields the spine reads (skill / description / name / current_phase).
    Mirrors wb_keys.py._hand_parse_yaml.
    """
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        # List items are not modelled by the fallback — skip them (PyYAML path
        # handles real lists). This keeps a `key:` that precedes a list block as
        # an empty dict rather than crashing.
        if raw_line.lstrip().startswith("- "):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.split("#", 1)[0].strip() if val else ""
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1] if stack else root
        if val == "":
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = _coerce_scalar(val)
    return root


def _coerce_scalar(raw: str) -> Any:
    """Coerce a bare YAML scalar string to a Python value."""
    raw = raw.strip()
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ("'", '"'):
        return raw[1:-1]
    low = raw.lower()
    if low in ("null", "~", ""):
        return None
    if low == "true":
        return True
    if low == "false":
        return False
    try:
        return int(raw)
    except ValueError:
        pass
    return raw


# ---------- Frontmatter ----------


def parse_frontmatter(text: str) -> dict[str, Any]:
    """Split a leading `---`...`---` YAML frontmatter block and parse it to a dict.

    Absent frontmatter -> {}. Mirrors wb_library._split_frontmatter (the closing
    fence is the first line that is exactly `---` after the opening) + a parse_yaml
    of the inner block.
    """
    fm = _split_frontmatter(text)
    if fm is None:
        return {}
    return parse_yaml(fm)


def _split_frontmatter(text: str) -> str | None:
    """Return the YAML frontmatter block of a markdown doc, or None if absent.

    Mirrors wb_library.py._split_frontmatter exactly so the two helpers agree on
    where frontmatter ends.
    """
    if not text.startswith("---"):
        return None
    rest = text[3:]
    end = rest.find("\n---")
    if end == -1:
        return None
    return rest[:end].lstrip("\n")


# ---------- H2 section extraction (fence-aware — the load-bearing primitive) ----------


def _fence_marker(line: str) -> str | None:
    """Return the fence delimiter char ('`' or '~') if `line` opens/closes a fenced
    code block (>= 3 of the same char after optional leading whitespace), else None.

    Per CommonMark, a fenced code block is delimited by >= 3 backticks or >= 3
    tildes. We track the delimiter char so a ``` block isn't closed by a ~~~ line
    and vice-versa.
    """
    stripped = line.lstrip()
    for ch in ("`", "~"):
        if stripped.startswith(ch * 3):
            return ch
    return None


def _h2_text(line: str) -> str | None:
    """Return the heading text if `line` is a level-2 (`## `) heading, else None.

    `## ` requires the third char to be a space, which already excludes `###`+
    (deeper headings) — those keep their content *inside* the enclosing `##`
    section per adapters/README.md:18. Trailing whitespace on the heading line is
    tolerated (CRLF-safe: splitlines() already stripped the line ending).
    """
    s = line.rstrip()
    if s.startswith("## "):
        return s[3:].strip()
    return None


def _heading_matches(actual: str, target: str, match: str) -> bool:
    """Compare an H2's text against the target per the `match` mode.

    match="exact"    -> case-sensitive exact compare on the stripped heading text.
    match="contains" -> case-insensitive substring (target in actual); used for the
                        skill "core discipline" lookup (§4.3.3) where the full
                        heading text isn't known, only that it contains a keyword.
    """
    if match == "contains":
        return target.strip().lower() in actual.lower()
    return actual == target.strip()


def extract_h2_section(
    text: str,
    heading: str,
    *,
    include_heading: bool = True,
    match: str = "exact",
) -> str | None:
    """Return the body of the `## {heading}` section, or None if the heading is absent.

    Behavior (locked — DESIGN-orchestration-spine.md § 5.1):
      - The section runs from the matched `## ` heading until the next `## `
        (level-2) heading at the same level, or EOF.
      - `### ` (and deeper) sub-headings stay INSIDE their `##` section — they are
        not boundaries (adapters/README.md:18 "Adding H3/H4 within a section is
        allowed").
      - Fence-aware: a `## ` line inside a fenced code block (``` or ~~~) is content,
        NOT a heading boundary. Fence open/close state is tracked while scanning,
        for both the section-start search AND the section-end search.
      - include_heading=True prepends the matched heading line (rstripped); False
        returns only the body below it.
      - match="exact" (default) compares the heading text case-sensitively and
        exactly; match="contains" does a case-insensitive substring match and
        returns the FIRST matching section (the discipline-lookup variant).
      - Trailing blank lines before the next heading / EOF are trimmed.

    Returns the section text (LF-joined) or None. Line endings are normalized to LF
    (splitlines drops the original ending) — acceptable for context injection.
    """
    lines = text.splitlines()
    target = heading.strip()

    in_fence = False
    fence_ch = ""
    collecting = False
    collected: list[str] = []

    for line in lines:
        fm = _fence_marker(line)

        if in_fence:
            # Inside a code fence: every line is content (including the closing
            # delimiter). A `## ` here is NOT a heading.
            if fm == fence_ch:
                in_fence = False
                fence_ch = ""
            if collecting:
                collected.append(line)
            continue

        if fm:
            # This line opens a code fence — it is content, never a heading.
            in_fence = True
            fence_ch = fm
            if collecting:
                collected.append(line)
            continue

        # Not in a fence and not a fence delimiter: this line may be a heading.
        h2 = _h2_text(line)
        if h2 is not None:
            if collecting:
                # The next level-2 heading terminates the section.
                break
            if _heading_matches(h2, target, match):
                collecting = True
                if include_heading:
                    collected.append(line.rstrip())
            continue

        if collecting:
            collected.append(line)

    if not collecting:
        return None

    # Trim trailing blank lines (noise before the next heading / EOF).
    while collected and collected[-1].strip() == "":
        collected.pop()

    return "\n".join(collected)
