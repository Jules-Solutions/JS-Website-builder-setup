#!/usr/bin/env python3
"""
website-builder — PreToolUse hook handler (Phase 2.C, v1.0).

The anti-skip enforcement hook. The single most load-bearing behavior in the
website-builder product: the agent profile *asks* the user to follow the
38-phase pipeline; this hook is what *mechanically refuses* a forward skip.

Fires before every tool invocation matching the matcher in `hooks/hooks.json`
(currently `Edit|Write|MultiEdit|Bash`). It reads the user project's
`.website-builder/project.yaml.current_phase`, classifies the attempted tool
into a tool-class, looks that class up in the curated `PHASE_TOOL_POLICY`
constant (hand-derived from all 38 phase contracts' `## Tools and skills used`
+ `## Gating rules` + `## Skip authorization` sections), and ALLOWs or BLOCKs.

Enforcement model — LOCKED by Commander decision D-2C-1. Implemented exactly as
specified; not re-derived:

1. Phase graph is deterministic, parsed from the 38 contracts' frontmatter
   (`phase`, `prev_phase`, `next_phase`). Ordering:
   1 → 2 → ... → 6 → 6.5 → 7 → ... → 24 → 24a → 24b → 24c → 25 → ... → 34.
   Phase "6.5" has `re_runnable: true` and is an ingestion side-channel — it
   NEVER blocks and may fire from any phase. Phases 24a/b/c only apply when
   `project.yaml.transactional` is true (informational here — the hook does not
   need the flag to make its allow/deny call, since the policy for 24a/b/c is a
   superset-permissive commerce stage).
2. `PHASE_TOOL_POLICY` is a curated MODULE CONSTANT, not runtime NLP. For each
   phase id (string) it maps to the allow-set of tool *classes*. The hook does
   NOT parse contract prose at runtime — it looks up this table.
3. Tool classification maps an incoming PreToolUse payload to a
   `(tool_class, target_kind)` pair, total + defensive (unknown tool → a
   conservative class the table authorizes broadly; never crash).
4. Decision logic:
   - No `.website-builder/project.yaml` → silent ALLOW (pre-bootstrap; the
     bootstrap skill itself needs Write/Bash to scaffold).
   - `project.yaml` present but `current_phase` missing/unreadable →
     soft-ALLOW + advisory notice.
   - Tool-class in PHASE_TOOL_POLICY[current_phase] → ALLOW.
   - Tool-class authorized only at a downstream phase → BLOCK, quoting the
     current phase contract's `## Gating rules` (and `## Skip authorization`
     if present) so the agent gets the discipline rationale + the legitimate
     override path, plus which downstream phase authorizes the tool.
   - Override: if `.website-builder/decisions/skip-phase-NN.md` exists for the
     phase being skipped → ALLOW with a logged advisory notice.
   - Phase 6.5 current OR a 6.5-authorized tool → never blocks (side-channel).
5. CC contract: emits the modern JSON `hookSpecificOutput.permissionDecision`
   form on stdout with exit 0 (the current canonical contract per context7
   `/anthropics/claude-code` 2026-05-19 fetch), AND for a BLOCK additionally
   exits 2 with the reason on stderr (the documented exit-code fallback so the
   refusal lands regardless of which contract the running CC honors). The
   catch-all `try/except` in `__main__` ALLOWs + emits a diagnostic on any
   internal error — this hook must NEVER brick a session by throwing.

CC PreToolUse output contract (context7 /anthropics/claude-code, fetched
2026-05-19 — see `.claude/temp/ctx7-docs/claude-code-pretooluse.md` +
`claude-code-hook-exitcodes.md`):

    stdout JSON (current/primary):
      {"hookSpecificOutput": {"permissionDecision": "allow|deny|ask"},
       "systemMessage": "..."}
    exit 0  — success; stdout shown in transcript (ALLOW path)
    exit 2  — blocking error; stderr fed back to Claude (BLOCK fallback)
    other   — non-blocking error

Reusable helpers carried over verbatim-in-spirit from the v0.1 stub per the
INST: `read_scalar_yaml`, `read_payload`, `extract_tool_name`,
`extract_tool_input`, and the defensive top-level `try/except`. The v0.1 stub
chased a `gating_rules:` frontmatter key that does NOT exist in any of the 38
contracts — that path is removed; this hook reads contract *body* sections
(`## Gating rules`, `## Skip authorization`) for the block message only, and
otherwise relies entirely on the curated PHASE_TOOL_POLICY constant.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# Reusable helpers (retained from the v0.1 stub per the INST)
# --------------------------------------------------------------------------- #


def project_dir() -> Path:
    """User-project working directory (cwd at session start)."""
    return Path.cwd()


def state_dir(root: Path) -> Path:
    return root / ".website-builder"


def has_state(root: Path) -> bool:
    sd = state_dir(root)
    return sd.is_dir() and (sd / "project.yaml").is_file()


def read_scalar_yaml(path: Path) -> dict:
    """Tolerant top-level-scalar YAML reader (no PyYAML dependency).

    Returns dict of `key: value` for top-level scalar entries. Nested keys and
    list entries are silently skipped — they're not used here. The plugin does
    not own the user's Python env, so a stdlib-only parser is mandatory.
    """
    if not path.exists():
        return {}
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    parsed: dict = {}
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        if line.startswith((" ", "\t")):
            continue
        if ":" not in line:
            continue
        key, _, raw_value = line.partition(":")
        key = key.strip()
        raw_value = raw_value.strip()
        if not raw_value:
            continue
        # strip an inline comment that is clearly not inside a quoted string
        if not raw_value.startswith(("'", '"')) and " #" in raw_value:
            raw_value = raw_value.split(" #", 1)[0].strip()
        if raw_value.startswith(("'", '"')) and raw_value.endswith(("'", '"')):
            raw_value = raw_value[1:-1]
        parsed[key] = raw_value
    return parsed


def read_project_state(root: Path) -> dict:
    """Read .website-builder/project.yaml and return a dict of scalars."""
    return read_scalar_yaml(state_dir(root) / "project.yaml")


def read_payload() -> dict:
    """Read the tool-invocation JSON from stdin.

    Tolerant: if stdin isn't valid JSON or is empty, return {} so the hook can
    fall through to permissive behavior rather than block.
    """
    try:
        raw = sys.stdin.read()
    except (OSError, ValueError):
        return {}
    if not raw or not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def extract_tool_name(payload: dict) -> str:
    """Return the tool name from the payload (best-effort across schema variants)."""
    for key in ("tool_name", "tool", "name"):
        v = payload.get(key)
        if isinstance(v, str) and v:
            return v
    return ""


def extract_tool_input(payload: dict) -> dict:
    """Return the tool input dict from the payload."""
    for key in ("tool_input", "input", "parameters", "args"):
        v = payload.get(key)
        if isinstance(v, dict):
            return v
    return {}


# --------------------------------------------------------------------------- #
# Phase graph — deterministic, derived from the 38 contracts' frontmatter
# --------------------------------------------------------------------------- #

# Canonical pipeline order. Phase ids are STRINGS (`"6.5"`, `"24a"`, `"24b"`,
# `"24c"` exist alongside `"1".."34"`). This list IS the deterministic phase
# graph the 38 contracts' prev_phase/next_phase frontmatter describes; encoded
# as a constant so the hook does not parse 38 files at runtime.
PHASE_ORDER: tuple[str, ...] = (
    "1", "2", "3", "4", "5",
    "6", "6.5", "7", "8", "9",
    "10", "11", "12",
    "13", "14", "15", "16",
    "17", "18",
    "19", "20", "21", "22", "23",
    "24", "24a", "24b", "24c", "25", "26", "27",
    "28", "29", "30",
    "31", "32", "33", "34",
)

# The re-runnable ingestion side-channel. NEVER blocks; may fire from any phase.
SIDE_CHANNEL_PHASE = "6.5"

# Commerce sub-phases — only reached when project.yaml.transactional is true.
# Informational: the hook does not need the flag to make its call (their policy
# is the permissive commerce-stage superset), but the constant documents intent.
COMMERCE_SUBPHASES: frozenset[str] = frozenset({"24a", "24b", "24c"})


def normalize_phase(raw: object) -> str | None:
    """Map a raw project.yaml current_phase value onto a canonical phase id.

    Accepts `17`, `"17"`, `"6.5"`, `6.5`, `"24a"`, `"phase-17"`, `" 17 "`, etc.
    Returns the canonical id (a member of PHASE_ORDER) or None if unmappable.
    """
    if raw is None:
        return None
    s = str(raw).strip().lower()
    if not s:
        return None
    # strip a leading "phase" / "phase-" / "phase " prefix if present
    s = re.sub(r"^phase[\s\-_]*", "", s)
    s = s.strip()
    # exact canonical match
    if s in PHASE_ORDER:
        return s
    # float-shaped "6.5" / "06.5" → "6.5"
    m = re.fullmatch(r"0*(\d+)\.(\d+)", s)
    if m:
        cand = f"{int(m.group(1))}.{m.group(2)}"
        if cand in PHASE_ORDER:
            return cand
    # integer-shaped with leading zeros "06" → "6", or sub-phase "24A" → "24a"
    m = re.fullmatch(r"0*(\d+)([a-z]?)", s)
    if m:
        cand = f"{int(m.group(1))}{m.group(2)}"
        if cand in PHASE_ORDER:
            return cand
    return None


# --------------------------------------------------------------------------- #
# Tool classification
# --------------------------------------------------------------------------- #

# Source-code / build-output file extensions that, when written OUTSIDE
# `.website-builder/`, mean the agent is doing codegen (phase-18+ work).
CODE_EXTENSIONS: frozenset[str] = frozenset({
    ".tsx", ".ts", ".jsx", ".js", ".mjs", ".cjs",
    ".vue", ".svelte", ".astro",
    ".css", ".scss", ".sass", ".less",
    ".html", ".htm", ".php", ".py", ".rb", ".go", ".rs",
    ".json", ".yaml", ".yml", ".toml",
    ".md", ".mdx",
})

# Bash command verbs that mean build / package / deploy (build-deploy class).
BUILD_DEPLOY_RE = re.compile(
    r"(?:^|[\s;&|])(?:"
    r"(?:npm|pnpm|yarn|bun)\s+(?:run\s+)?build"
    r"|next\s+build|astro\s+build|vite\s+build|hugo\b"
    r"|(?:npm|pnpm|yarn|bun)\s+(?:run\s+)?(?:deploy|preview|start)"
    r"|vercel\b|wrangler\b|netlify\b"
    r"|gh\s+[\w-]*\s*deploy|docker\b"
    r"|git\s+push"
    r"|payload\s+migrate"
    r")",
    re.IGNORECASE,
)

# Bash command verbs that are benign inventory/inspection (always-broad class):
# ls, file, du, mkdir, cp, mv, cat, dig, whois, curl-read, identify, exiftool,
# openssl, etc. We do not enumerate exhaustively — anything that is NOT
# build-deploy is treated as benign-bash, which the policy authorizes broadly
# at every phase (the contracts use ls/file/cp/mkdir for inbox scaffolding from
# phase 4 onward; blocking benign bash would break the pipeline).

# Tool classes (the vocabulary PHASE_TOOL_POLICY is keyed on):
#   "state-write"   — Write/Edit/MultiEdit targeting a path under .website-builder/
#   "code-write"    — Write/Edit/MultiEdit targeting a code/source path outside
#                      .website-builder/ (the phase-18-gated class)
#   "build-deploy"  — Bash whose command matches build/deploy/package verbs
#   "benign-bash"   — any other Bash (inventory/inspection/audit shell)
#   "ask"           — AskUserQuestion
#   "read"          — Read/Grep/Glob
#   "web"           — WebFetch/WebSearch
#   "context7"      — context7 MCP lookups
#   "playwright"    — Playwright MCP
#   "mcp-other"     — any other MCP tool (Stripe/Cloudflare/Vercel/etc.)
#   "unknown"       — unclassifiable tool (conservative: treated like benign-bash)


def _is_under_state_dir(target: str) -> bool:
    """True if the (possibly relative) write target is inside .website-builder/."""
    if not target:
        return False
    t = target.replace("\\", "/")
    # normalize: strip a leading "./"
    while t.startswith("./"):
        t = t[2:]
    # match `.website-builder/...` anywhere in the path (absolute or relative)
    return bool(re.search(r"(?:^|/)\.website-builder/", t)) or t == ".website-builder"


def _write_target(tool_input: dict) -> str:
    """Extract the file path a Write/Edit/MultiEdit is targeting."""
    for key in ("file_path", "path", "filePath", "notebook_path", "target_file"):
        v = tool_input.get(key)
        if isinstance(v, str) and v:
            return v
    # MultiEdit-shaped payloads sometimes nest edits; the top-level file_path
    # is the canonical target for all CC edit tools, so the loop above suffices.
    return ""


def _bash_command(tool_input: dict) -> str:
    for key in ("command", "cmd", "script"):
        v = tool_input.get(key)
        if isinstance(v, str) and v:
            return v
    return ""


def classify_tool(tool_name: str, tool_input: dict) -> tuple[str, str]:
    """Map a PreToolUse payload to (tool_class, target_kind).

    Total + defensive: an unknown tool returns ("unknown", "") which the policy
    authorizes broadly (never crash, never spuriously block an unrecognized
    tool the contracts didn't anticipate).
    """
    name = (tool_name or "").strip()
    lname = name.lower()

    # --- write-family: the gate-bearing classification --------------------- #
    if name in ("Write", "Edit", "MultiEdit", "NotebookEdit") or lname in (
        "write", "edit", "multiedit", "notebookedit", "str_replace_editor",
    ):
        target = _write_target(tool_input)
        if _is_under_state_dir(target):
            return ("state-write", target)
        # No target resolvable → conservative: treat as state-write (the
        # benign default; the contracts' early-phase writes are all to
        # .website-builder/, and a target-less edit is almost always a state
        # write or an ambiguous case we should not punish with a block).
        if not target:
            return ("state-write", "")
        ext = ""
        m = re.search(r"(\.[A-Za-z0-9]+)$", target.replace("\\", "/"))
        if m:
            ext = m.group(1).lower()
        # Any write outside .website-builder/ to a code/source extension — OR
        # to anywhere outside .website-builder/ at all — is code-write.
        # (Per the locked model: "Write/Edit/MultiEdit on a code/source file
        #  outside .website-builder/, or anywhere outside .website-builder/".)
        if ext in CODE_EXTENSIONS or ext == "":
            return ("code-write", target)
        return ("code-write", target)

    # --- bash-family ------------------------------------------------------- #
    if name == "Bash" or lname in ("bash", "shell", "sh"):
        cmd = _bash_command(tool_input)
        if cmd and BUILD_DEPLOY_RE.search(cmd):
            return ("build-deploy", cmd)
        return ("benign-bash", cmd)

    # --- conversation / read ---------------------------------------------- #
    if name == "AskUserQuestion" or lname == "askuserquestion":
        return ("ask", "")
    if name in ("Read", "Grep", "Glob") or lname in ("read", "grep", "glob"):
        return ("read", "")

    # --- web --------------------------------------------------------------- #
    if name in ("WebFetch", "WebSearch") or lname in ("webfetch", "websearch"):
        return ("web", "")

    # --- MCP tools --------------------------------------------------------- #
    if lname.startswith("mcp__context7__") or "context7" in lname:
        return ("context7", "")
    if lname.startswith("mcp__playwright__") or "playwright" in lname:
        return ("playwright", "")
    if lname.startswith("mcp__"):
        return ("mcp-other", "")

    return ("unknown", name)


# --------------------------------------------------------------------------- #
# PHASE_TOOL_POLICY — the curated allow-set per phase
# --------------------------------------------------------------------------- #
#
# Hand-derived from ALL 38 phase contracts' `## Tools and skills used`
# + `## Gating rules` + `## Skip authorization` sections (read in full,
# Phase 2.C, 2026-05-19). One entry per phase id; value is the set of
# tool-classes ALLOWED at that phase. A class NOT in a phase's set is
# BLOCKED at that phase (the hook then names the earliest downstream phase
# whose set contains the class).
#
# The load-bearing discriminator across the whole pipeline is `code-write`
# (Write/Edit on source files outside `.website-builder/`):
#   * Phases 1-17 EXCLUDE `code-write`. Contracts 10/11/12/14 say verbatim
#     "No Write/Edit on code files in this phase — those tools are gated
#      until phase 18." Phases 13/15/16/17 write only `.website-builder/`
#     artifacts (content/pages, components.yaml, sections.yaml, strings.json,
#     brand.yaml). So `code-write` upstream of 18 is the canonical skip.
#   * Phase 18 is the codegen gate — first phase that authorizes `code-write`.
#   * Phases 18-34 all authorize `code-write` (+ build-deploy from 19 on).
#
# `state-write`, `ask`, `read`, `web`, `context7`, `benign-bash`,
# `mcp-other`, `unknown` are authorized at EVERY phase (every contract's
# tools list includes AskUserQuestion + Read + Write/Edit-on-state; benign
# bash is used for inbox scaffolding from phase 4 on; the table never blocks
# the conservative/unknown class). `playwright` first appears at 6.5 and from
# 19 on. `build-deploy` first appears at 18/19 (the build phases).
#
# A compact builder keeps this readable: list only the classes that VARY
# (code-write / build-deploy / playwright); the always-allowed base set is
# unioned in. Each phase notes the contract filename it was curated from.

_ALWAYS = frozenset({
    "state-write", "ask", "read", "web", "context7",
    "benign-bash", "mcp-other", "unknown",
})

# Per-phase EXTRA classes beyond _ALWAYS. (class -> first authorizing phase
# is derived from this table by PHASE_ORDER scan.)
_PHASE_EXTRA: dict[str, frozenset[str]] = {
    # ---- discovery-strategy (1-5): conversation only; NO code, NO build ----
    "1":   frozenset(),                                  # 01-idea.md
    "2":   frozenset(),                                  # 02-vision.md (web)
    "3":   frozenset(),                                  # 03-requirements.md
    "4":   frozenset(),                                  # 04-project-company-info.md (ls/file bash = benign)
    "5":   frozenset(),                                  # 05-brand-voice-tone.md
    # ---- content-foundation (6, 6.5, 7, 8, 9) -----------------------------
    "6":   frozenset(),                                  # 06-wild-content-capture.md (mkdir/cp = benign)
    "6.5": frozenset({"playwright"}),                    # 06.5 side-channel — never blocks (handled separately)
    "7":   frozenset(),                                  # 07-media-asset-audit.md
    "8":   frozenset(),                                  # 08-image-strategy.md
    "9":   frozenset(),                                  # 09-sitemap.md
    # ---- architecture (10, 11, 12): "No Write/Edit on code — gated to 18" --
    "10":  frozenset(),                                  # 10-information-architecture.md
    "11":  frozenset(),                                  # 11-stack-decision.md (context7)
    "12":  frozenset(),                                  # 12-cms-decision.md (context7)
    # ---- content-wireframes (13-16): only .website-builder/ artifacts -----
    "13":  frozenset(),                                  # 13-content-per-page.md
    "14":  frozenset(),                                  # 14-wireframe-per-page.md ("gated until 18")
    "15":  frozenset(),                                  # 15-content-per-section.md
    "16":  frozenset(),                                  # 16-copywriting.md
    # ---- design (17 = tokens to brand.yaml; 18 = THE codegen gate) --------
    "17":  frozenset(),                                  # 17-design-system.md (brand.yaml only)
    "18":  frozenset({"code-write", "playwright"}),      # 18-component-design-build.md — codegen authorized
    # ---- build-integration (19-23): code + build + playwright -------------
    "19":  frozenset({"code-write", "build-deploy", "playwright"}),  # 19-composition.md
    "20":  frozenset({"code-write", "build-deploy", "playwright"}),  # 20-responsive-mobile.md
    "21":  frozenset({"code-write", "build-deploy", "playwright"}),  # 21-accessibility-audit.md
    "22":  frozenset({"code-write", "build-deploy", "playwright"}),  # 22-performance-audit.md
    "23":  frozenset({"code-write", "build-deploy", "playwright"}),  # 23-forms-interactive.md
    # ---- pre-launch (24, 24a/b/c, 25, 26, 27) -----------------------------
    "24":  frozenset({"code-write", "build-deploy", "playwright"}),  # 24-integrations.md
    "24a": frozenset({"code-write", "build-deploy", "playwright"}),  # 24a-commerce-platform.md
    "24b": frozenset({"code-write", "build-deploy", "playwright"}),  # 24b-payment-provider.md
    "24c": frozenset({"code-write", "build-deploy", "playwright"}),  # 24c-commerce-legal.md
    "25":  frozenset({"code-write", "build-deploy", "playwright"}),  # 25-legal-pages.md
    "26":  frozenset({"code-write", "build-deploy", "playwright"}),  # 26-seo-structured-data.md
    "27":  frozenset({"code-write", "build-deploy", "playwright"}),  # 27-polish-cross-browser.md
    # ---- deployment (28, 29, 30) ------------------------------------------
    "28":  frozenset({"code-write", "build-deploy", "playwright"}),  # 28-domain-dns-ssl.md
    "29":  frozenset({"code-write", "build-deploy", "playwright"}),  # 29-hosting-deployment.md
    "30":  frozenset({"code-write", "build-deploy", "playwright"}),  # 30-analytics-search-submission.md
    # ---- post-launch (31-34) ----------------------------------------------
    "31":  frozenset({"code-write", "build-deploy", "playwright"}),  # 31-launch-announcement.md
    "32":  frozenset({"code-write", "build-deploy", "playwright"}),  # 32-iteration-roadmap.md
    "33":  frozenset({"code-write", "build-deploy", "playwright"}),  # 33-maintenance-cadence.md
    "34":  frozenset({"code-write", "build-deploy", "playwright"}),  # 34-monitoring-backup.md
}

PHASE_TOOL_POLICY: dict[str, frozenset[str]] = {
    phase: _ALWAYS | _PHASE_EXTRA.get(phase, frozenset())
    for phase in PHASE_ORDER
}

# Tool-classes that 6.5 (the ingestion side-channel) authorizes. Per
# 06.5-artifact-ingestion.md `## Tools and skills used`: Stitch/AI-output
# parser (Read/Write/Edit on .website-builder state — state-write),
# Playwright walker, AskUserQuestion, Read/Write/Edit, Bash (scrape/curl/ls),
# WebFetch. 6.5 explicitly does NOT do codegen (it normalizes artifacts into
# .website-builder/ state). It is the re-runnable side-channel: when 6.5 is
# the current phase, OR a tool that 6.5 authorizes is invoked, the hook NEVER
# blocks (per the locked model point 4 + 06.5 `## Gating rules`: 6.5 gates the
# agent from silently mutating state, not from advancing — and has NO
# `## Skip authorization` section because it is re-runnable, not skippable).
SIDE_CHANNEL_CLASSES: frozenset[str] = frozenset({
    "state-write", "ask", "read", "web", "context7",
    "benign-bash", "playwright", "mcp-other", "unknown",
})


def first_authorizing_phase(tool_class: str) -> str | None:
    """Earliest phase (by PHASE_ORDER) whose policy authorizes tool_class."""
    for phase in PHASE_ORDER:
        if tool_class in PHASE_TOOL_POLICY.get(phase, frozenset()):
            return phase
    return None


# --------------------------------------------------------------------------- #
# Contract gating-text extraction (for the BLOCK message only)
# --------------------------------------------------------------------------- #


def _contract_path(plugin_root: Path | None, phase: str) -> Path | None:
    """Locate the phase-contract MD at ${CLAUDE_PLUGIN_ROOT}/phase-contracts/."""
    if plugin_root is None:
        return None
    cdir = plugin_root / "phase-contracts"
    if not cdir.is_dir():
        return None
    candidates: list[str] = [f"{phase}-*.md"]
    m = re.fullmatch(r"(\d+)\.(\d+)", phase)
    if m:
        candidates.append(f"{phase}-*.md")  # e.g. 6.5-artifact-ingestion.md
    if re.fullmatch(r"\d+", phase):
        candidates.append(f"{int(phase):02d}-*.md")
        candidates.append(f"{int(phase)}-*.md")
    for pat in candidates:
        hits = sorted(cdir.glob(pat))
        if hits:
            return hits[0]
    return None


def _extract_section(md_text: str, heading: str) -> str:
    """Return the body of a `## {heading}` section (trimmed), or ''."""
    pat = re.compile(
        r"^##\s+" + re.escape(heading) + r"\s*$(.*?)(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    m = pat.search(md_text)
    if not m:
        return ""
    body = m.group(1).strip()
    # cap length so the block message stays readable in the agent transcript
    if len(body) > 1400:
        body = body[:1400].rstrip() + "\n…(truncated; see the full contract)"
    return body


def block_rationale(plugin_root: Path | None, phase: str, contract_name: str) -> str:
    """Quote the current phase contract's gating + skip-authorization text."""
    cp = _contract_path(plugin_root, phase)
    if cp is None:
        return (
            f"(Phase contract for phase {phase} not found under "
            f"${{CLAUDE_PLUGIN_ROOT}}/phase-contracts/ — the discipline still "
            f"applies; see the website-builder agent profile § Anti-skip "
            f"enforcement.)"
        )
    try:
        text = cp.read_text(encoding="utf-8")
    except OSError:
        return f"(Could not read {cp.name} for the gating rationale.)"
    parts: list[str] = []
    gating = _extract_section(text, "Gating rules")
    if gating:
        parts.append(f"### {contract_name} — Gating rules\n\n{gating}")
    skip = _extract_section(text, "Skip authorization")
    if skip:
        parts.append(f"### {contract_name} — Skip authorization\n\n{skip}")
    if not parts:
        return f"(No `## Gating rules` / `## Skip authorization` section found in {cp.name}.)"
    return "\n\n".join(parts)


def _contract_display_name(plugin_root: Path | None, phase: str) -> str:
    cp = _contract_path(plugin_root, phase)
    return cp.name if cp is not None else f"phase-{phase}"


# --------------------------------------------------------------------------- #
# Skip-override detection
# --------------------------------------------------------------------------- #


def has_skip_decision(root: Path, phase: str) -> Path | None:
    """Return the skip-decision file for `phase` if the user authorized a skip.

    Per DESIGN-phase-contracts.md lines 229-240 + each contract's
    `## Skip authorization`: an explicitly authorized forward-skip is logged to
    `.website-builder/decisions/skip-phase-NN.md`. The filename uses the bare
    phase id (`skip-phase-21.md`, `skip-phase-14.md`, `skip-phase-6.5.md`).
    We also accept a zero-padded variant defensively.
    """
    ddir = state_dir(root) / "decisions"
    if not ddir.is_dir():
        return None
    names = {f"skip-phase-{phase}.md"}
    if re.fullmatch(r"\d+", phase):
        names.add(f"skip-phase-{int(phase):02d}.md")
    for n in names:
        p = ddir / n
        if p.is_file():
            return p
    return None


# --------------------------------------------------------------------------- #
# CC output emission
# --------------------------------------------------------------------------- #


def emit_allow(notice: str = "") -> int:
    """ALLOW: JSON permissionDecision=allow on stdout, exit 0.

    An empty `notice` emits nothing (silent allow — the common path; the
    matcher only fires on Edit/Write/MultiEdit/Bash so a silent allow keeps
    the in-phase happy path noise-free). A non-empty `notice` is surfaced as
    an advisory `systemMessage` while still allowing the call.
    """
    if notice:
        out = {
            "hookSpecificOutput": {"permissionDecision": "allow"},
            "systemMessage": notice,
        }
        print(json.dumps(out), flush=True)
    return 0


def emit_block(reason: str) -> int:
    """BLOCK: dual-emit for maximum compatibility with the CC contract.

    Per context7 /anthropics/claude-code (2026-05-19): the modern contract is
    a stdout JSON `hookSpecificOutput.permissionDecision: "deny"` with exit 0;
    the documented fallback is exit 2 with the reason on stderr. We emit BOTH
    so the refusal lands regardless of which contract the running CC honors:
    JSON deny on stdout, the same reason on stderr, exit 2.
    """
    out = {
        "hookSpecificOutput": {"permissionDecision": "deny"},
        "systemMessage": reason,
    }
    print(json.dumps(out), flush=True)
    print(reason, file=sys.stderr, flush=True)
    return 2


# --------------------------------------------------------------------------- #
# Main decision logic (locked model point 4)
# --------------------------------------------------------------------------- #


def decide(
    *,
    root: Path,
    plugin_root: Path | None,
    tool_name: str,
    tool_input: dict,
) -> tuple[bool, str]:
    """Return (allow: bool, message: str). Pure — testable in isolation."""

    # (a) Pre-bootstrap: no project.yaml → silent ALLOW. The wb-bootstrap skill
    #     itself needs Write/Bash to scaffold `.website-builder/`.
    if not has_state(root):
        return (True, "")

    project = read_project_state(root)
    raw_phase = project.get("current_phase")
    phase = normalize_phase(raw_phase)

    tool_class, target = classify_tool(tool_name, tool_input)

    # (b) State dir exists but current_phase missing/unreadable → soft-ALLOW
    #     with an advisory notice (the bootstrap skill can reconcile later).
    if phase is None:
        return (
            True,
            "[website-builder] PreToolUse: `.website-builder/project.yaml` "
            "exists but `current_phase` is missing or unreadable "
            f"(value: {raw_phase!r}). Tool call allowed; consider running the "
            "wb-bootstrap skill to reconcile project state.",
        )

    # (f) Phase 6.5 is the re-runnable ingestion side-channel: when 6.5 is the
    #     current phase, OR the attempted tool is one 6.5 authorizes, the hook
    #     NEVER blocks. (Locked model point 4 + 06.5 contract: 6.5 gates the
    #     agent from silently mutating state, not from advancing; it has no
    #     skip-authorization because it is re-runnable, not skippable.)
    if phase == SIDE_CHANNEL_PHASE:
        return (True, "")
    if tool_class in SIDE_CHANNEL_CLASSES and tool_class not in (
        "code-write", "build-deploy",
    ):
        # A class 6.5 always permits (state-write/ask/read/web/playwright/etc.)
        # is allowed at every phase anyway — fast-path it without a policy
        # lookup. code-write/build-deploy are NEVER side-channel classes, so
        # they still fall through to the gate below.
        return (True, "")

    policy = PHASE_TOOL_POLICY.get(phase)
    if policy is None:
        # phase normalized to a member of PHASE_ORDER but somehow not keyed —
        # cannot happen (PHASE_TOOL_POLICY is built from PHASE_ORDER), but be
        # defensive: ALLOW + advisory rather than block on an internal gap.
        return (
            True,
            f"[website-builder] PreToolUse: no policy entry for phase "
            f"{phase!r} (internal); allowing the call. Please report this.",
        )

    # (c) Tool-class authorized at the current phase → ALLOW (silent).
    if tool_class in policy:
        return (True, "")

    # (e) Override: an explicit, logged skip-decision for this phase →
    #     ALLOW with a logged advisory naming the override file.
    skip_file = has_skip_decision(root, phase)
    if skip_file is not None:
        return (
            True,
            f"[website-builder] PreToolUse: `{tool_class}` is not authorized "
            f"at phase {phase}, but an explicit skip authorization exists at "
            f"`{skip_file.as_posix()}` — allowing the call per the user's "
            f"logged override. (The anti-skip discipline was deliberately "
            f"waived for this phase; downstream phases carry the documented "
            f"elevated risk.)",
        )

    # (d) Tool-class authorized only at a downstream phase → BLOCK, quoting the
    #     current contract's gating + skip-authorization text.
    downstream = first_authorizing_phase(tool_class)
    contract_name = _contract_display_name(plugin_root, phase)
    rationale = block_rationale(plugin_root, phase, contract_name)

    human_class = {
        "code-write": "writing/editing source code (a code file outside "
                       "`.website-builder/`)",
        "build-deploy": "running a build/deploy/package command",
    }.get(tool_class, f"a `{tool_class}` operation")

    where = f" → `{target}`" if target else ""
    downstream_txt = (
        f"phase {downstream}" if downstream else "a later phase"
    )

    msg = (
        f"⛔ website-builder anti-skip: BLOCKED.\n\n"
        f"You are in **phase {phase}** ({contract_name}). You attempted "
        f"{human_class}{where}, which the pipeline does not authorize until "
        f"**{downstream_txt}**. This is a forward-skip — exactly the failure "
        f"the website-builder discipline exists to prevent (the user paid for "
        f"the disciplined process, not a fast skip that drifts apart in 3 "
        f"weeks).\n\n"
        f"The legitimate paths forward:\n"
        f"  1. Do the phase-{phase} work this contract specifies, then advance "
        f"`current_phase` when its exit criteria are met.\n"
        f"  2. If the user *explicitly* authorizes skipping phase {phase} "
        f"(having heard the cost), log it to "
        f"`.website-builder/decisions/skip-phase-{phase}.md` per the contract's "
        f"`## Skip authorization` — this hook will then allow the call.\n\n"
        f"The current phase contract's discipline (verbatim):\n\n"
        f"{rationale}"
    )
    return (False, msg)


def main() -> int:
    """Run the PreToolUse handler."""
    payload = read_payload()
    tool_name = extract_tool_name(payload)
    tool_input = extract_tool_input(payload)

    root = project_dir()
    plugin_root_env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    plugin_root = Path(plugin_root_env) if plugin_root_env else None

    allow, message = decide(
        root=root,
        plugin_root=plugin_root,
        tool_name=tool_name,
        tool_input=tool_input,
    )
    if allow:
        return emit_allow(message)
    return emit_block(message)


if __name__ == "__main__":
    # Defensive top-level guard (retained from v0.1): a hook must NEVER brick a
    # session by throwing. On ANY unexpected internal error, ALLOW the call and
    # emit a diagnostic — a broken anti-skip hook that fails open is vastly
    # safer than one that fails closed and blocks every tool in the session.
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 — intentional catch-all in a hook
        print(
            json.dumps({
                "hookSpecificOutput": {"permissionDecision": "allow"},
                "systemMessage": (
                    "[website-builder] PreToolUse handler error (allowing "
                    f"call so the session is not bricked): {exc!r}"
                ),
            }),
            flush=True,
        )
        sys.exit(0)
