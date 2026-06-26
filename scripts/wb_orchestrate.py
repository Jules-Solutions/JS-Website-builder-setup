#!/usr/bin/env python3
"""
scripts/wb_orchestrate.py — the website-builder plugin's orchestration spine.

The keystone of the orchestration-spine remediation program
(`Workstreams/website-builder/foundation/DESIGN-orchestration-spine.md`). Reaching
a phase should *deterministically* load its resources, inject its discipline,
consult the active stack/CMS/commerce adapter, validate state, and surface the
right tools — regardless of whether the agent remembers to. The markdown stays the
source of behavior; this module makes it fire.

Two trigger predicates, one path (§3.4 "fresh session and mid-session advance run
the same path"):
  - on phase advance: hooks-handlers/post_tool_use.py calls run_post_tool_use()
    (fires only when current_phase changed vs the marker).
  - on session resume: hooks-handlers/session_start.py calls run_session_start()
    (unconditionally re-injects the current phase's entry block).

Public surface (DESIGN-orchestration-spine.md § 4.1):

    run_post_tool_use(project_root) -> OrchestrationResult | None
        Resume-on-change entry. None if current_phase == marker.last_phase, else
        runs the phase-entry actions for current_phase, updates the marker, returns
        the result. Called by post_tool_use.py (emits JSON additionalContext).

    run_session_start(project_root) -> OrchestrationResult | None
        Resume entry. Unconditionally renders current_phase's entry block +
        reconciles the marker. None only when there is no resolvable current_phase
        (no state / pre-bootstrap). Called by session_start.py (appends the block
        to its plain-stdout render).

    orchestrate_phase_entry(project_root, phase, *, log=None) -> OrchestrationResult
        The core: runs the 5 phase-entry actions for `phase`. Pure of marker I/O
        (callers own the marker), so it is directly unit-testable with a fixed phase.

    run(argv, *, project_root) -> int
        Internal/debug dispatch (`--phase N` / `--show-marker`). NOT a user-facing
        `wb` verb (the resolver-as-entry-point pattern, mirroring wb_keys.resolve_keys).

Interface rules (mirrors the locked wb_keys.py / wb_library.py module contract,
`scripts/README.md` § Interface rules + DESIGN-orchestration-spine.md § 4):
  - IMPORT-SAFE: importing this module has NO side effects beyond putting its own
    scripts/ dir on sys.path so the sibling imports (wb_markdown, wb_library)
    resolve regardless of caller cwd — no network, no file writes, no subprocess at
    import time. All work happens inside the entry points.
  - `project_root` is passed in explicitly — this module never reads os.getcwd()
    inside its logic (testability; mirrors wb_keys / wb_library).
  - Does NOT import session_start (would be circular — § 4.2). The handlers import
    THIS module, not the reverse.
  - The consumer/validation modules (wb_validate_layers, wb_imagegen — shipped in
    Wave 2) are SOFT-imported + guarded. The guard is RETAINED as defensive
    decoupling (Wave-2 INST locked decision): a present-but-broken module must never
    break the spine import, and an absent module degrades its action to a no-op
    (§ 4.3 import-guard pattern). Actions 4 + 5 fire whenever the modules resolve.

Crash-discipline: every one of the 5 actions is individually wrapped so a single
broken action never breaks the orchestrator; the handlers add their own outer
crash guard on top (a broken spine must never block the user's Edit/Write).

See also:
  - Workstreams/website-builder/foundation/DESIGN-orchestration-spine.md (the contract)
  - scripts/wb_markdown.py (extract_h2_section / parse_frontmatter — consumed here)
  - scripts/wb_library.py (autoclone_for_state + _find_phase_contract + load_project_yaml)
  - hooks-handlers/post_tool_use.py (PostToolUse caller — JSON additionalContext)
  - hooks-handlers/session_start.py (SessionStart caller — plain-stdout appendix)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

# ---------- Sibling imports (wb_markdown + wb_library live in this scripts/ dir) ----------
#
# wb_orchestrate depends on wb_markdown + wb_library (DESIGN-orchestration-spine
# § 4.2). The handlers insert scripts/ on sys.path before importing this module,
# but to keep the module runnable in isolation (tests, `python wb_orchestrate.py`)
# we also ensure our own dir is importable. This is the only import-time effect and
# is idempotent.

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import wb_markdown  # noqa: E402  (sys.path nudge must precede)
import wb_library  # noqa: E402


# ---------- Consumer/validation soft-imports (import-guarded — § 4.3) ----------
#
# wb_validate_layers + wb_imagegen ship in Wave 2 (now present). The guard is
# RETAINED as defensive decoupling (Wave-2 INST locked decision — overrides the
# design's "remove the guards once present" note): `except Exception` (not just
# ImportError) is deliberate — a present-but-broken module must never break the
# spine import; an absent module degrades its action to a no-op.

try:
    from wb_validate_layers import validate_content_layers  # type: ignore
except Exception:  # noqa: BLE001 — absent/broken module degrades action 4 to a no-op
    validate_content_layers = None  # type: ignore[assignment]

try:
    from wb_imagegen import resolve_imagegen_path  # type: ignore
except Exception:  # noqa: BLE001 — absent/broken module degrades action 5 to a no-op
    resolve_imagegen_path = None  # type: ignore[assignment]


# ---------- Constants ----------

MODULE_NAME = "wb orchestrate"
STATE_DIR_NAME = ".website-builder"
PROJECT_YAML_NAME = "project.yaml"
MARKER_NAME = ".orchestrator-state"

# Concision budget (§ 2 / § 4.1): additionalContext "enters context without
# truncation", so render() stays bounded. Soft total cap; any single adapter
# section over the per-section cap is injected as its leading portion + a pointer
# to the adapter file.
TOTAL_SOFT_CAP = 6000
PER_SECTION_CAP = 2000

# Phases that need a resolved image-gen path (action 5). v1: phase 8 (image
# strategy). Extend as more visual-asset phases land.
IMAGEGEN_PHASES: tuple[int, ...] = (8,)

# Phase → adapter-section map (§ 4.4 — the runtime adapter-binding table). Section
# names are the EXACT H2 text (without the leading `## `). The map is the single
# place to extend when expansion stacks/phases land — reviewed against the adapter
# README schemas (adapters/README.md, cms-adapters/README.md, commerce-adapters/
# README.md). Keys are the int current_phase; the string sub-phase keys below are
# forward-room (current_phase resolves to an int in v1, so they aren't reached yet).
PHASE_ADAPTER_SECTIONS: dict[Any, dict[str, list[str]]] = {
    8: {},  # image-strategy: no adapter section — action 5 surfaces the image-gen path
    11: {"stack": ["Mental model", "Limitations + escape hatches", "CMS pairing"]},
    12: {"stack": ["CMS pairing"], "cms": ["Mental model", "Auth + setup"]},
    13: {"stack": ["Content layer mapping"], "cms": ["Content layer mapping"]},
    16: {"stack": ["Content layer mapping"], "cms": ["Content layer mapping"]},
    17: {"stack": ["Content layer mapping", "Component library pairing"]},
    18: {
        "stack": ["Component library pairing", "Auth + setup", "Migration recipe"],
        "cms": ["Auth + setup"],
    },
    19: {"stack": ["Content layer mapping"]},
    22: {"stack": ["Deploy", "context7 lookups for this stack"]},
    28: {"stack": ["Deploy"]},
    29: {"stack": ["Deploy", "Post-launch maintenance pattern"]},
    31: {"stack": ["Post-launch maintenance pattern"]},
    32: {"stack": ["Post-launch maintenance pattern"]},
    33: {"stack": ["Post-launch maintenance pattern"]},
    34: {"stack": ["Post-launch maintenance pattern"]},
    # --- Sub-phase forward-room (§ 4.4 rows for 6.5 / 24a/b/c). current_phase
    # resolves to an int in v1, so these string keys are not reached yet; they
    # carry the binding so a future revision representing those as current_phase
    # tokens injects the right sections with no map change. ---
    "6.5": {"stack": ["Phase 6.5 ingestion"]},
    "24a": {
        "stack": ["Commerce integration (if transactional=true)"],
        "commerce": ["Auth + setup", "Mental model"],
    },
    "24b": {
        "stack": ["Commerce integration (if transactional=true)"],
        "commerce": ["Auth + setup", "Mental model"],
    },
    "24c": {
        "stack": ["Commerce integration (if transactional=true)"],
        "commerce": ["Auth + setup", "Mental model"],
    },
}

# Stack/CMS slug aliases (§ 5.2). Normalize case + the obvious aliases so a
# project.yaml `stack: Next.js` resolves to adapters/stack-nextjs.md.
_STACK_ALIASES = {
    "next.js": "nextjs",
    "next": "nextjs",
    "nextjs": "nextjs",
    "wp": "wordpress",
}
_CMS_ALIASES: dict[str, str] = {}


# ---------- Logging helpers (mirror wb_keys.py) ----------

def _color_supported() -> bool:
    return bool(getattr(sys.stdout, "isatty", lambda: False)())


_USE_COLOR = _color_supported()


def _c(code: str, msg: str) -> str:
    if not _USE_COLOR:
        return msg
    return f"\x1b[{code}m{msg}\x1b[0m"


def log_info(msg: str) -> None:
    print(f"{_c('36', '[wb orchestrate]')} {msg}", flush=True)


def log_warn(msg: str) -> None:
    print(f"{_c('33', '[wb orchestrate]')} {msg}", file=sys.stderr, flush=True)


# ---------- Typed result objects (mirror the wb_keys.py slot-object pattern) ----------


@dataclass
class InjectedSection:
    """One adapter H2 section injected at phase entry (action 2)."""

    adapter: str          # adapter file stem, e.g. "stack-nextjs" | "cms-payload"
    adapter_kind: str     # "stack" | "cms" | "commerce"
    heading: str          # exact H2 text, e.g. "Content layer mapping"
    body: str             # extracted section (verbatim; render() may truncate)
    source_path: str      # repo-relative adapter path (for the truncation pointer)
    full_len: int = 0     # original section length (pre-truncation)


@dataclass
class SkillDirectives:
    """The phase skill's injected directives (action 3)."""

    skill: str                    # "wb-design-system"
    description: str              # frontmatter `description` — the always-present discipline
    discipline: str | None = None  # best-effort "core discipline" H2 body


@dataclass
class ImagegenStatus:
    """The resolved image-gen path surfaced at phase 8 (action 5)."""

    available: bool
    detail: str


@dataclass
class OrchestrationResult:
    """The outcome of one phase-entry orchestration. render() produces the bounded
    markdown block injected as PostToolUse additionalContext / appended to the
    SessionStart plain-stdout render."""

    phase: int
    autoclone: list = field(default_factory=list)            # list[wb_library.CloneResult]
    adapter_sections: list = field(default_factory=list)     # list[InjectedSection]
    skill_directives: SkillDirectives | None = None
    validation_errors: list[str] = field(default_factory=list)
    imagegen: ImagegenStatus | None = None

    def is_empty(self) -> bool:
        """True when no action produced anything to inject (render would be a bare
        header). Lets callers / the handler choose silence over a content-free block."""
        return not (
            self.autoclone
            or self.adapter_sections
            or self.skill_directives
            or self.validation_errors
            or self.imagegen
        )

    def render(self) -> str:
        """Produce the bounded markdown block (§ 2 concision budget)."""
        lines: list[str] = []
        lines.append(f"# website-builder — phase {self.phase} entry (orchestration spine)")
        lines.append("")
        lines.append(
            "> Deterministic phase-entry context: the phase's resources, the phase "
            "skill's standing discipline, and the active stack/CMS adapter's sections "
            "relevant to this phase. Injected by the orchestration spine."
        )
        lines.append("")

        # --- Action 1: phase-entry resource clones ---
        if self.autoclone:
            lines.append("## Phase-entry resource clones")
            lines.append("")
            deferred = False
            for r in self.autoclone:
                resource = getattr(r, "resource", "?")
                status = getattr(r, "status", "?")
                target = getattr(r, "target", None)
                reason = getattr(r, "reason", "")
                tstr = f" → library/{target}" if target else ""
                rstr = f" — {reason}" if reason else ""
                lines.append(f"- `{resource}` [{status}]{tstr}{rstr}")
                if status == "fetch-deferred":
                    deferred = True
            lines.append("")
            if deferred:
                lines.append(
                    "Network fetches are deferred — the agent (or `wb library "
                    "add`/`refresh`) performs the actual clone on demand."
                )
                lines.append("")

        # --- Action 3: phase-skill directives ---
        if self.skill_directives:
            sd = self.skill_directives
            lines.append(f"## Phase skill — `{sd.skill}`")
            lines.append("")
            lines.append(
                f"Invoke the `{sd.skill}` skill (Skill tool) for the full phase "
                "procedure. Its standing discipline (in force regardless of whether "
                "the skill was invoked):"
            )
            lines.append("")
            lines.append(sd.description.strip())
            lines.append("")
            if sd.discipline:
                lines.append(_cap(sd.discipline.strip(), PER_SECTION_CAP))
                lines.append("")

        # --- Action 2: active-adapter sections (concision-budgeted) ---
        #
        # The hard bound is the PER-SECTION cap: every adapter section over the cap
        # is injected as its leading portion + a pointer to the adapter file (§ 2).
        # The TOTAL soft cap is a *target* — with each section bounded, the total
        # lands near it. A high safety ceiling (2× soft) only fires for a
        # pathological phase with many large sections, so the mapped sections for a
        # normal phase (e.g. phase 17's two sections) are all injected.
        if self.adapter_sections:
            lines.append("## Active-adapter sections (runtime binding)")
            lines.append("")
            running = len("\n".join(lines))
            hard_ceiling = TOTAL_SOFT_CAP * 2
            for sec in self.adapter_sections:
                heading_line = f"### `{sec.adapter}` → `## {sec.heading}`"
                body = sec.body
                if len(body) > PER_SECTION_CAP:
                    body = _truncate_with_pointer(
                        body, PER_SECTION_CAP, sec.heading, sec.source_path
                    )
                block = f"{heading_line}\n\n{body}\n"
                if running + len(block) > hard_ceiling:
                    lines.append(
                        "_(further adapter sections omitted at the concision ceiling "
                        "— read them in their adapter files.)_"
                    )
                    lines.append("")
                    break
                lines.append(heading_line)
                lines.append("")
                lines.append(body)
                lines.append("")
                running += len(block)

        # --- Action 4: content-layer validation ---
        if self.validation_errors:
            lines.append("## Content-layer validation")
            lines.append("")
            for e in self.validation_errors:
                lines.append(f"- {e}")
            lines.append("")

        # --- Action 5: image-gen path ---
        if self.imagegen:
            lines.append("## Image generation")
            lines.append("")
            lines.append(f"- {self.imagegen.detail}")
            lines.append("")

        return "\n".join(lines).rstrip() + "\n"


def _cap(text: str, cap: int) -> str:
    """Trim `text` to at most `cap` chars on a line boundary, appending an ellipsis
    note when truncated."""
    if len(text) <= cap:
        return text
    head = text[:cap].rsplit("\n", 1)[0].rstrip()
    return head + "\n… (truncated for concision)"


def _truncate_with_pointer(body: str, cap: int, heading: str, source_path: str) -> str:
    """Inject the leading portion of an over-cap section + a pointer to the full
    section in its adapter file (§ 2 / § 4.1)."""
    head = body[:cap].rsplit("\n", 1)[0].rstrip()
    return (
        f"{head}\n\n→ section truncated for concision; read the full "
        f"`## {heading}` in `{source_path}`."
    )


# ---------- Path / marker helpers ----------


def _plugin_root() -> Path:
    """The plugin install root (parent of scripts/). Adapters, skills, and phase
    contracts are PLUGIN content — resolved relative to this module, never relative
    to the user's project_root."""
    return _THIS_DIR.parent


def _state_dir(project_root: Path) -> Path:
    return project_root / STATE_DIR_NAME


def _project_yaml_path(project_root: Path) -> Path:
    return _state_dir(project_root) / PROJECT_YAML_NAME


def _marker_path(project_root: Path) -> Path:
    return _state_dir(project_root) / MARKER_NAME


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_marker(project_root: Path) -> dict[str, Any]:
    """Read the orchestrator marker. Missing/unreadable/non-dict → {} (never raises)."""
    path = _marker_path(project_root)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_marker(project_root: Path, *, last_phase: Any, digest: str) -> None:
    """Write the marker (last_phase + diagnostics). Best-effort: a write failure is
    swallowed (a marker that can't persist degrades to re-firing on the next event,
    never a crash)."""
    path = _marker_path(project_root)
    payload = {
        "last_phase": last_phase,
        "last_fired_utc": _now_iso(),
        "project_yaml_digest": digest,
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:  # pragma: no cover — defensive
        log_warn(f"could not persist marker at {path}: {exc}")


def _project_yaml_digest(project_root: Path) -> str:
    """Short sha256 (16 hex) of project.yaml bytes. Forward-room for detecting
    project.yaml changes that don't change current_phase (§ 3.2). Missing → ''."""
    path = _project_yaml_path(project_root)
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    except OSError:
        return ""


def _coerce_phase(raw: Any) -> int | None:
    """Coerce a project.yaml current_phase value to an int. Non-integer / absent →
    None (the marker types last_phase as int|null; orchestrate_phase_entry is typed
    `phase: int`). Sub-phase tokens like '6.5'/'24a' are not representable as the v1
    fire-key and resolve to None (no fire) — forward-room, not a regression."""
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, int):
        return raw
    s = str(raw).strip()
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        return None


def _resolve_current_phase(project_root: Path) -> int | None:
    project = wb_library.load_project_yaml(project_root)
    return _coerce_phase(project.get("current_phase"))


# ---------- Slug normalization + adapter resolution ----------


def _normalize_stack_slug(raw: Any) -> str | None:
    if not raw:
        return None
    s = str(raw).strip().lower()
    if not s or s in ("none", "null", "~"):
        return None
    return _STACK_ALIASES.get(s, s)


def _normalize_cms_slug(raw: Any) -> str | None:
    if not raw:
        return None
    s = str(raw).strip().lower()
    if s in ("none", "null", "~", ""):
        return "none"
    return _CMS_ALIASES.get(s, s)


def _truthy(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() not in ("", "null", "~", "false", "no", "0")
    if isinstance(value, (list, dict)):
        return len(value) > 0
    return bool(value)


def _stack_adapter_path(slug: str) -> Path:
    return _plugin_root() / "adapters" / f"stack-{slug}.md"


def _cms_adapter_path(slug: str) -> Path:
    return _plugin_root() / "cms-adapters" / f"cms-{slug}.md"


def _resolve_commerce_adapter(project: dict[str, Any]) -> Path | None:
    """Resolve the active commerce/booking adapter file from project.yaml. Tries
    commerce-{payment_provider}.md then booking-{booking_provider}.md (§ 4.3 action
    2). First existing file wins; None if neither is present."""
    root = _plugin_root() / "commerce-adapters"
    candidates: list[Path] = []
    payment = project.get("payment_provider")
    booking = project.get("booking_provider")
    if payment:
        candidates.append(root / f"commerce-{str(payment).strip().lower()}.md")
    if booking:
        candidates.append(root / f"booking-{str(booking).strip().lower()}.md")
    for c in candidates:
        if c.is_file():
            return c
    return None


def _repo_rel(path: Path) -> str:
    """Plugin-root-relative path with POSIX separators (clean in injected context
    across OSes — never a Windows backslash path)."""
    try:
        return path.relative_to(_plugin_root()).as_posix()
    except ValueError:
        return path.name


# ---------- The 5 phase-entry actions ----------


def _action_autoclone(project_root: Path, phase: int, emit: Callable[[str], None]) -> list:
    """Action 1 — fire the phase-entry auto-clone (the existing-but-never-invoked
    wb_library branch). Returns list[CloneResult]; defensive (never raises)."""
    try:
        return wb_library.autoclone_for_state(
            project_root, trigger="phase-entry", phase=phase, log=emit
        )
    except Exception as exc:  # noqa: BLE001 — a broken autoclone must not break the spine
        emit(f"[{MODULE_NAME}] autoclone failed: {exc}")
        return []


def _extract_sections(
    path: Path | None,
    kind: str,
    headings: list[str],
    emit: Callable[[str], None],
) -> list[InjectedSection]:
    """Read an adapter file + extract the named H2 sections. Absent file / absent
    section ⇒ skip silently (the agent still has context7/WebFetch — § 4.3)."""
    out: list[InjectedSection] = []
    if path is None or not path.is_file():
        return out
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        emit(f"[{MODULE_NAME}] could not read adapter {path}: {exc}")
        return out
    rel = _repo_rel(path)
    label = path.stem
    for heading in headings:
        body = wb_markdown.extract_h2_section(text, heading)
        if body is None:
            continue  # absent section — defensive skip
        out.append(
            InjectedSection(
                adapter=label,
                adapter_kind=kind,
                heading=heading,
                body=body,
                source_path=rel,
                full_len=len(body),
            )
        )
    return out


def _action_adapter_sections(
    project_root: Path,
    project: dict[str, Any],
    phase: int,
    emit: Callable[[str], None],
) -> list[InjectedSection]:
    """Action 2 — load + inject the active adapter section(s) for this phase. THIS
    is what makes the adapters actually consulted at runtime (gap #3)."""
    try:
        mapping = PHASE_ADAPTER_SECTIONS.get(phase)
        if not mapping:
            return []
        out: list[InjectedSection] = []

        # stack adapter
        if "stack" in mapping:
            stack_slug = _normalize_stack_slug(project.get("stack"))
            if stack_slug:
                out += _extract_sections(
                    _stack_adapter_path(stack_slug), "stack", mapping["stack"], emit
                )

        # CMS adapter (only when cms set + ≠ none)
        if "cms" in mapping:
            cms_slug = _normalize_cms_slug(project.get("cms"))
            if cms_slug and cms_slug != "none":
                out += _extract_sections(
                    _cms_adapter_path(cms_slug), "cms", mapping["cms"], emit
                )

        # commerce/booking adapter (only when transactional)
        if "commerce" in mapping and _truthy(project.get("transactional")):
            commerce_path = _resolve_commerce_adapter(project)
            out += _extract_sections(commerce_path, "commerce", mapping["commerce"], emit)

        return out
    except Exception as exc:  # noqa: BLE001 — adapter injection must not break the spine
        emit(f"[{MODULE_NAME}] adapter-section injection failed: {exc}")
        return []


def _action_skill_directives(
    project_root: Path, phase: int, emit: Callable[[str], None]
) -> SkillDirectives | None:
    """Action 3 — inject the phase-group skill's directives. Reads the phase
    contract's `skill:` frontmatter, resolves skills/{skill}/SKILL.md, injects the
    (required) frontmatter `description` + the (best-effort) "core discipline" H2.
    Requires ZERO skill edits (gap #4)."""
    try:
        contract = wb_library._find_phase_contract(project_root, phase)
        if contract is None:
            return None
        ctext = contract.read_text(encoding="utf-8")
        cfm = wb_markdown.parse_frontmatter(ctext)
        skill = cfm.get("skill")
        if not skill or not isinstance(skill, str):
            return None
        skill_md = _plugin_root() / "skills" / skill / "SKILL.md"
        if not skill_md.is_file():
            return None
        stext = skill_md.read_text(encoding="utf-8")
        sfm = wb_markdown.parse_frontmatter(stext)
        description = sfm.get("description")
        if not description or not isinstance(description, str):
            return None  # description is the REQUIRED directive; absent → no inject
        discipline = wb_markdown.extract_h2_section(stext, "discipline", match="contains")
        return SkillDirectives(skill=skill, description=description, discipline=discipline)
    except Exception as exc:  # noqa: BLE001 — skill injection must not break the spine
        emit(f"[{MODULE_NAME}] skill-directive injection failed: {exc}")
        return None


def _action_validate_layers(
    project_root: Path, emit: Callable[[str], None]
) -> list[str]:
    """Action 4 — run content-layer validation (wb_validate_layers, import-guarded).
    Fires when the module resolves; no-op when it is absent/broken."""
    if validate_content_layers is None:
        return []
    try:
        errs = validate_content_layers(project_root)
        return [str(e) for e in errs] if errs else []
    except Exception as exc:  # noqa: BLE001 — validation must not break the spine
        emit(f"[{MODULE_NAME}] content-layer validation failed: {exc}")
        return []


def _action_imagegen(
    project_root: Path, phase: int, emit: Callable[[str], None]
) -> ImagegenStatus | None:
    """Action 5 — surface the resolved image-gen path at phases that need generated
    visual assets (wb_imagegen, import-guarded + phase-gated to IMAGEGEN_PHASES).
    Fires when the module resolves + the phase needs it; no-op otherwise."""
    if phase not in IMAGEGEN_PHASES or resolve_imagegen_path is None:
        return None
    try:
        resolved = resolve_imagegen_path(project_root)
        return ImagegenStatus(available=True, detail=f"image-gen provider/path: {resolved}")
    except Exception as exc:  # noqa: BLE001 — imagegen resolution must not break the spine
        return ImagegenStatus(available=False, detail=f"image-gen resolution failed: {exc}")


# ---------- Core: orchestrate_phase_entry (§ 4.1 / § 4.3) ----------


def orchestrate_phase_entry(
    project_root: Path,
    phase: int,
    *,
    log: Callable[[str], None] | None = None,
) -> OrchestrationResult:
    """Run the 5 phase-entry actions for `phase`. Pure of marker I/O (callers own
    the marker), so it is directly unit-testable with a fixed phase."""
    emit = log or (lambda _msg: None)
    project = wb_library.load_project_yaml(project_root)

    autoclone = _action_autoclone(project_root, phase, emit)
    adapter_sections = _action_adapter_sections(project_root, project, phase, emit)
    skill_directives = _action_skill_directives(project_root, phase, emit)
    validation_errors = _action_validate_layers(project_root, emit)
    imagegen = _action_imagegen(project_root, phase, emit)

    return OrchestrationResult(
        phase=phase,
        autoclone=autoclone,
        adapter_sections=adapter_sections,
        skill_directives=skill_directives,
        validation_errors=validation_errors,
        imagegen=imagegen,
    )


# ---------- Public entry points (§ 4.1) ----------


def run_post_tool_use(project_root: Path) -> OrchestrationResult | None:
    """Resume-on-change entry. None if current_phase == marker.last_phase, else runs
    the phase-entry actions for current_phase, updates the marker, returns the
    result. Idempotent within a session; fires exactly once per advance."""
    phase = _resolve_current_phase(project_root)
    if phase is None:
        return None
    marker = _read_marker(project_root)
    if marker.get("last_phase") == phase:
        return None
    result = orchestrate_phase_entry(project_root, phase)
    _write_marker(
        project_root, last_phase=phase, digest=_project_yaml_digest(project_root)
    )
    return result


def run_session_start(project_root: Path) -> OrchestrationResult | None:
    """Resume entry. Unconditionally renders current_phase's entry block + reconciles
    the marker. None only when there is no resolvable current_phase (no state /
    pre-bootstrap). A resumed session lost its context window, so re-injecting the
    current phase's resources/skill/adapter is correct; action 1 is idempotent."""
    phase = _resolve_current_phase(project_root)
    if phase is None:
        return None
    result = orchestrate_phase_entry(project_root, phase)
    _write_marker(
        project_root, last_phase=phase, digest=_project_yaml_digest(project_root)
    )
    return result


# ---------- run (internal/debug dispatch — NOT a user-facing wb verb) ----------


def run(argv: list[str], *, project_root: Path) -> int:
    """Internal/debug dispatch. `--phase N` fires orchestrate_phase_entry + prints
    the rendered block; `--show-marker` prints the marker. Mirrors wb_keys: the
    resolver is an entry point, not a `wb` verb."""
    parser = argparse.ArgumentParser(
        prog="wb_orchestrate",
        description="Orchestration-spine debug entry (not a user-facing wb verb).",
    )
    parser.add_argument("--phase", type=int, default=None,
                        help="Fire orchestrate_phase_entry for PHASE and print the block.")
    parser.add_argument("--show-marker", action="store_true",
                        help="Print the current .orchestrator-state marker.")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code or 0)

    if args.show_marker:
        print(json.dumps(_read_marker(project_root), indent=2))
        return 0
    if args.phase is not None:
        result = orchestrate_phase_entry(project_root, args.phase, log=log_info)
        print(result.render())
        return 0
    parser.print_help()
    return 2


def main(argv: list[str] | None = None) -> int:
    """Standalone entry for isolated debugging. project_root = cwd."""
    args = list(argv if argv is not None else sys.argv[1:])
    return run(args, project_root=Path.cwd())


if __name__ == "__main__":
    sys.exit(main())
