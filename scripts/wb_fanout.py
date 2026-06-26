#!/usr/bin/env python3
"""
scripts/wb_fanout.py — the website-builder plugin's parallel-research fan-out helper.

Gap #8 of the orchestration-spine remediation program
(`Workstreams/website-builder/foundation/DESIGN-orchestration-spine.md` § 8, Wave 3b
row). Parallel-agent research fan-out was prompt-only recipe text in the opt-in phase
contracts (2 / 3 / 5 / 8). This module makes the parts Python CAN do real + tested.

The honest split (DESIGN-orchestration-spine § 8 "a helper the agent invokes"):
a Python subprocess CANNOT call the in-session CC `Agent` / `TaskCreate` tools — only
the agent can. So this module does the deterministic, testable parts:

  - DECOMPOSE a research brief ("compare 5 competitors across positioning/pricing/gtm")
    into N structured per-subject sub-task specs, and EMIT a spawn-recipe block (the
    markdown the in-session agent executes to spawn the N sub-agents + TaskCreate each).
  - Maintain the `.website-builder/tasks.yaml` fan-out LEDGER (the local task mirror
    named in agents/website-builder.md:217) — round-trip-preserving so it never
    clobbers the agent's phase-progress task mirror; it owns only the `fanout:` subtree.
  - AGGREGATE the N structured sub-agent results back into a single synthesis artifact
    (a subjects × dimensions comparison matrix + per-dimension cross-cut + coverage gaps).

The part this module CANNOT do — spawning the `Agent` tool ×N + `TaskCreate` — is the
`wb-fanout` skill's job (`skills/wb-fanout/SKILL.md`): the agent reads the emitted
spawn-recipe and executes it. This module is the deterministic substrate beneath that.

**The in-person-default doctrine is LOAD-BEARING** (verbatim in phase-contracts
02/03/05/08: "No subagent spawn by default … the default is in-person; spawn is the
user opting into speed"). This helper ENABLES user-initiated fan-out; it must never make
spawning always-on. The opt-in is enforced behaviorally by the skill + the phase
contracts — this module is a mechanical helper invoked only after the user opts in. It
warns (does not silently proceed) when asked to decompose for a non-opt-in phase.

Public surface (mirrors the locked wb_keys.py / wb_orchestrate.py entry-point contract):

    run(argv, *, project_root) -> int
        Dispatch a `wb fanout` sub-verb: decompose | aggregate | status.

    build_run(brief, *, now=None) -> FanoutRun
        Pure core: a brief dict → a FanoutRun with N per-subject task specs. No I/O —
        directly unit-testable (seeded brief → expected specs).

    render_spawn_recipe(run) -> str
        Pure render: a FanoutRun → the markdown spawn-recipe block the agent executes.

    aggregate_results(run, results, *, dimensions=None, now=None) -> SynthesisResult
        Pure core: a run (or None) + structured sub-agent results → a SynthesisResult
        whose render() is the synthesis markdown. No I/O — directly unit-testable.

Interface rules (locked — scripts/README.md § Interface rules + the spine module contract):
  - IMPORT-SAFE: importing this module has NO side effects beyond putting its own
    scripts/ dir on sys.path so the sibling import (wb_markdown) resolves regardless of
    caller cwd — no network, no file writes, no subprocess at import time.
  - `project_root` is passed in explicitly — this module never reads os.getcwd() inside
    its logic (testability; mirrors wb_keys / wb_orchestrate).
  - Does NOT import the dispatcher (no circular dependency). Does NOT import wb_keys /
    wb_library / wb_orchestrate. Depends only on wb_markdown (a leaf util) + stdlib.

See also:
  - Workstreams/website-builder/foundation/DESIGN-orchestration-spine.md § 8 (the contract)
  - skills/wb-fanout/SKILL.md (the agent-facing surface that executes the spawn-recipe)
  - scripts/wb_markdown.py (parse_yaml — brief + results + ledger reads)
  - scripts/wb.py (the `wb fanout` dispatch route)
  - phase-contracts/{02,03,05,08}-*.md (the opt-in phases + in-person-default doctrine)
  - agents/website-builder.md (Agent / TaskCreate / .website-builder/tasks.yaml mirror)
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------- Sibling import (wb_markdown lives in this scripts/ dir) ----------
#
# The dispatcher inserts scripts/ on sys.path before importing this module, but to
# keep the module runnable in isolation (tests, `python wb_fanout.py`) we also ensure
# our own dir is importable. This is the only import-time effect and is idempotent.

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import wb_markdown  # noqa: E402  (sys.path nudge must precede)

# PyYAML for the ledger/synthesis WRITE path (parse reuses wb_markdown.parse_yaml).
# PyYAML is the supported path everywhere that matters (the test harness pins it via
# `uv run --with pyyaml`; live CC usually has it). The fallback emits JSON — which IS
# valid YAML — so a bare interpreter still writes a parseable, round-trippable ledger.
try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover — exercised only outside the test harness
    yaml = None  # name always bound so `yaml is not None` narrows for type-checkers


# ---------- Constants ----------

MODULE_NAME = "wb fanout"
STATE_DIR_NAME = ".website-builder"
TASKS_YAML_NAME = "tasks.yaml"      # the local task mirror (agents/website-builder.md:217)
LEDGER_KEY = "fanout"               # this module owns ONLY this subtree of tasks.yaml
LIBRARY_DIR_NAME = "library"        # synthesis artifacts land in .website-builder/library/

DESIGN_DOC = "Workstreams/website-builder/foundation/DESIGN-orchestration-spine.md"

# The phases that surface the parallel-research opt-in (§ 8 + phase-contracts).
# Fan-out at any other phase is a warning, not a hard error: the helper stays callable
# for debugging/expansion, but the doctrine is that 2/3/5/8 are where it belongs.
OPT_IN_PHASES: tuple[int, ...] = (2, 3, 5, 8)

# Default sub-agent type the spawn-recipe names. The phase contracts all say "spawn a
# research subagent"; `researcher` is the read-only research/analysis agent.
DEFAULT_AGENT_TYPE = "researcher"

# Matrix-cell soft cap: keep the comparison table scannable; the full finding text is
# always reproduced verbatim in the per-dimension section below the matrix.
MATRIX_CELL_CAP = 140


# ---------- Logging helpers (mirror wb_keys.py / wb_orchestrate.py) ----------

def _use_color() -> bool:
    return bool(getattr(sys.stdout, "isatty", lambda: False)())


def _c(code: str, msg: str) -> str:
    if not _use_color():
        return msg
    return f"\x1b[{code}m{msg}\x1b[0m"


def log_info(msg: str) -> None:
    print(f"{_c('36', '[wb fanout]')} {msg}", file=sys.stderr, flush=True)


def log_ok(msg: str) -> None:
    print(f"{_c('32', '[wb fanout]')} {msg}", file=sys.stderr, flush=True)


def log_warn(msg: str) -> None:
    print(f"{_c('33', '[wb fanout]')} {msg}", file=sys.stderr, flush=True)


def log_err(msg: str) -> None:
    print(f"{_c('31', '[wb fanout]')} {msg}", file=sys.stderr, flush=True)


# ---------- Typed errors (the fix-path-carrying contract, mirrors wb_keys.py) ----------

class FanoutError(Exception):
    """Base class for fan-out errors. Carries a human fix-path message."""


class BriefError(FanoutError):
    """A decompose brief is malformed / missing required fields."""


class ResultsError(FanoutError):
    """An aggregate results bundle is malformed / missing required fields."""


class LedgerError(FanoutError):
    """The fan-out ledger could not be read / a referenced run is absent."""


# ---------- Typed records (mirror the wb_keys.py / wb_orchestrate.py dataclass pattern) ----------


@dataclass
class FanoutTask:
    """One per-subject sub-task: the spec the agent hands to one spawned sub-agent."""

    task_id: str
    subject: str
    spec: str                              # the prompt for the spawned sub-agent
    status: str = "pending"                # pending | done
    agent_task_ref: str | None = None      # the TaskCreate id the agent fills in (round-trip)
    result_ref: str | None = None          # where this subject's result landed

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "subject": self.subject,
            "spec": self.spec,
            "status": self.status,
            "agent_task_ref": self.agent_task_ref,
            "result_ref": self.result_ref,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "FanoutTask":
        return cls(
            task_id=str(d.get("task_id", "")),
            subject=str(d.get("subject", "")),
            spec=str(d.get("spec", "")),
            status=str(d.get("status", "pending")),
            agent_task_ref=_opt_str(d.get("agent_task_ref")),
            result_ref=_opt_str(d.get("result_ref")),
        )


@dataclass
class FanoutRun:
    """One fan-out run: a decomposed brief + its N per-subject tasks."""

    run_id: str
    phase: int
    topic: str
    dimensions: list[str]
    synthesis_goal: str
    agent_type: str
    created_utc: str
    status: str = "decomposed"             # decomposed | aggregated
    synthesis_path: str | None = None
    tasks: list[FanoutTask] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "phase": self.phase,
            "topic": self.topic,
            "dimensions": list(self.dimensions),
            "synthesis_goal": self.synthesis_goal,
            "agent_type": self.agent_type,
            "created_utc": self.created_utc,
            "status": self.status,
            "synthesis_path": self.synthesis_path,
            "tasks": [t.to_dict() for t in self.tasks],
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "FanoutRun":
        raw_tasks = d.get("tasks") or []
        tasks = [FanoutTask.from_dict(t) for t in raw_tasks if isinstance(t, dict)]
        return cls(
            run_id=str(d.get("run_id", "")),
            phase=_coerce_int(d.get("phase")) or 0,
            topic=str(d.get("topic", "")),
            dimensions=[str(x) for x in (d.get("dimensions") or [])],
            synthesis_goal=str(d.get("synthesis_goal", "")),
            agent_type=str(d.get("agent_type", DEFAULT_AGENT_TYPE)),
            created_utc=str(d.get("created_utc", "")),
            status=str(d.get("status", "decomposed")),
            synthesis_path=_opt_str(d.get("synthesis_path")),
            tasks=tasks,
        )


@dataclass
class SubjectResult:
    """One spawned sub-agent's structured return for one subject."""

    subject: str
    findings: dict[str, str]               # dimension -> finding text
    notes: str | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "SubjectResult":
        subject = d.get("subject")
        if not subject or not isinstance(subject, str):
            raise ResultsError(
                "A result entry is missing a string `subject`.\n"
                "  Each entry under `results:` needs `subject:` + a `findings:` map.\n"
                f"  See {DESIGN_DOC} § 8 + skills/wb-fanout/SKILL.md for the schema."
            )
        raw_findings = d.get("findings") or {}
        if not isinstance(raw_findings, dict):
            raise ResultsError(
                f"Result for {subject!r} has a non-mapping `findings:` "
                "(expected `dimension: finding` pairs)."
            )
        findings = {str(k): _stringify(v) for k, v in raw_findings.items()}
        return cls(subject=subject, findings=findings, notes=_opt_str(d.get("notes")))


@dataclass
class SynthesisResult:
    """The aggregated synthesis of N sub-agent results. render() = the markdown artifact."""

    run_id: str
    phase: int
    topic: str
    dimensions: list[str]
    results: list[SubjectResult]
    generated_utc: str
    synthesis_goal: str = ""
    gaps: list[str] = field(default_factory=list)

    def render(self) -> str:
        """Produce the synthesis markdown: frontmatter + matrix + per-dimension cross-cut
        + coverage gaps. Deterministic over the structured inputs (so it is testable)."""
        lines: list[str] = []
        # --- frontmatter ---
        lines.append("---")
        lines.append("type: fanout-synthesis")
        lines.append(f"run_id: {self.run_id}")
        lines.append(f"phase: {self.phase}")
        lines.append(f"topic: {_yaml_inline(self.topic)}")
        lines.append(f"generated_utc: {self.generated_utc}")
        lines.append(f"subjects: {len(self.results)}")
        lines.append(f"dimensions: [{', '.join(self.dimensions)}]")
        lines.append("---")
        lines.append("")
        lines.append(f"# Fan-out synthesis — {self.topic or self.run_id}")
        lines.append("")
        lines.append(
            f"> Parallel research aggregated from {len(self.results)} sub-agent(s) "
            f"(phase {self.phase}). Generated by `wb fanout aggregate` from the "
            "structured per-subject results."
        )
        if self.synthesis_goal:
            lines.append(">")
            lines.append(f"> **Synthesis goal:** {self.synthesis_goal}")
        lines.append("")

        # --- comparison matrix (subjects × dimensions) ---
        lines.append("## Comparison matrix")
        lines.append("")
        if self.dimensions:
            header = "| Subject | " + " | ".join(self.dimensions) + " |"
            divider = "|---|" + "|".join(["---"] * len(self.dimensions)) + "|"
            lines.append(header)
            lines.append(divider)
            for r in self.results:
                cells = [_cell(r.findings.get(dim, "")) for dim in self.dimensions]
                lines.append(f"| {_cell(r.subject)} | " + " | ".join(cells) + " |")
        else:
            lines.append("_(no dimensions declared — see per-subject findings below)_")
        lines.append("")

        # --- per-dimension cross-cut (full text, no truncation) ---
        if self.dimensions:
            lines.append("## By dimension")
            lines.append("")
            for dim in self.dimensions:
                lines.append(f"### {dim}")
                lines.append("")
                for r in self.results:
                    finding = r.findings.get(dim)
                    if finding:
                        lines.append(f"- **{r.subject}**: {finding}")
                    else:
                        lines.append(f"- **{r.subject}**: _(no finding)_")
                lines.append("")

        # --- per-subject notes (when any) ---
        notes = [(r.subject, r.notes) for r in self.results if r.notes]
        if notes:
            lines.append("## Cross-cutting notes")
            lines.append("")
            for subject, note in notes:
                lines.append(f"- **{subject}**: {note}")
            lines.append("")

        # --- coverage gaps ---
        lines.append("## Coverage gaps")
        lines.append("")
        if self.gaps:
            for g in self.gaps:
                lines.append(f"- {g}")
        else:
            lines.append("- None — every subject covered every declared dimension.")
        lines.append("")

        return "\n".join(lines).rstrip() + "\n"


# ---------- Small coercion helpers ----------

def _opt_str(v: Any) -> str | None:
    if v is None:
        return None
    s = str(v)
    return s if s else None


def _coerce_int(v: Any) -> int | None:
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v
    try:
        return int(str(v).strip())
    except (ValueError, TypeError):
        return None


def _stringify(v: Any) -> str:
    """Render a finding value as a single clean string (findings are prose)."""
    if v is None:
        return ""
    if isinstance(v, (list, tuple)):
        return "; ".join(_stringify(x) for x in v)
    return str(v).strip()


def _cell(text: str) -> str:
    """Make `text` safe for a one-line markdown table cell (escape pipes, collapse
    newlines, truncate to the soft cap with the full text preserved below the matrix)."""
    flat = " ".join(str(text).split()).replace("|", "\\|")
    if len(flat) > MATRIX_CELL_CAP:
        flat = flat[: MATRIX_CELL_CAP - 1].rstrip() + "…"
    return flat or "—"


def _yaml_inline(text: str) -> str:
    """Quote a scalar for a frontmatter value when it could confuse a YAML parser."""
    s = " ".join(str(text).split())
    if s == "" or any(ch in s for ch in (":", "#", "'", '"', "[", "]", "{", "}")):
        return '"' + s.replace('"', '\\"') + '"'
    return s


# ---------- Brief → FanoutRun (the decompose core; pure, no I/O) ----------


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _compact_ts(dt: datetime) -> str:
    return dt.strftime("%Y%m%dT%H%M%SZ")


def _iso_ts(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _normalize_str_list(raw: Any, *, field_name: str) -> list[str]:
    """Coerce a list-or-comma-string into a clean list of non-empty strings."""
    if raw is None:
        return []
    if isinstance(raw, str):
        items = [p.strip() for p in raw.split(",")]
    elif isinstance(raw, (list, tuple)):
        items = [str(p).strip() for p in raw]
    else:
        raise BriefError(
            f"Brief field `{field_name}` must be a list or comma-separated string, "
            f"got {type(raw).__name__}."
        )
    return [i for i in items if i]


def build_run(brief: dict[str, Any], *, now: datetime | None = None) -> FanoutRun:
    """Decompose a research brief into a FanoutRun with N per-subject task specs.

    Pure: no file I/O, no network. Directly unit-testable (seeded brief → expected
    specs). The CLI `decompose` verb persists the returned run via record_run().

    Brief schema (any of these may come from a `--brief` YAML file or inline flags):
        phase: int                 # the opt-in phase (2/3/5/8); warned-on otherwise
        topic: str                 # the overall research question
        subjects: [str, ...]       # the fan-out axis — one sub-agent per subject
        dimensions: [str, ...]      # facets each sub-agent must cover (comparable results)
        synthesis_goal: str        # optional; what the aggregate should produce
        agent_type: str            # optional; the subagent_type to spawn (default researcher)
    """
    if not isinstance(brief, dict):
        raise BriefError("Brief must be a mapping (YAML object / dict).")

    phase = _coerce_int(brief.get("phase"))
    if phase is None:
        raise BriefError(
            "Brief is missing a numeric `phase`.\n"
            f"  Fan-out is an opt-in at phases {', '.join(map(str, OPT_IN_PHASES))}; "
            "name the current phase so the ledger + recipe are scoped to it."
        )

    subjects = _normalize_str_list(brief.get("subjects"), field_name="subjects")
    if not subjects:
        raise BriefError(
            "Brief has no `subjects` — nothing to fan out over.\n"
            "  `subjects` is the fan-out axis: the N things researched in parallel "
            "(e.g. 5 competitor URLs, 5 voice exemplars, 3 image providers)."
        )

    dimensions = _normalize_str_list(brief.get("dimensions"), field_name="dimensions")
    topic = str(brief.get("topic", "")).strip()
    synthesis_goal = str(brief.get("synthesis_goal", "")).strip()
    agent_type = str(brief.get("agent_type", "") or DEFAULT_AGENT_TYPE).strip()

    dt = now or _now()
    run_id = f"fanout-p{phase}-{_compact_ts(dt)}"

    tasks: list[FanoutTask] = []
    width = max(2, len(str(len(subjects))))
    for idx, subject in enumerate(subjects, start=1):
        task_id = f"{run_id}-{str(idx).zfill(width)}"
        spec = _build_spec(subject=subject, topic=topic, dimensions=dimensions)
        tasks.append(FanoutTask(task_id=task_id, subject=subject, spec=spec))

    return FanoutRun(
        run_id=run_id,
        phase=phase,
        topic=topic,
        dimensions=dimensions,
        synthesis_goal=synthesis_goal,
        agent_type=agent_type,
        created_utc=_iso_ts(dt),
        status="decomposed",
        tasks=tasks,
    )


def _build_spec(*, subject: str, topic: str, dimensions: list[str]) -> str:
    """The self-contained prompt one spawned sub-agent receives for one subject.

    It instructs the sub-agent to research the subject across the declared dimensions
    and return a single structured YAML block in the exact shape `aggregate` consumes —
    so N independent sub-agents produce comparable, mergeable results."""
    lines: list[str] = []
    lines.append(
        f"You are researching ONE subject as part of a parallel fan-out. "
        f"Subject: {subject}."
    )
    if topic:
        lines.append(f"Overall research goal: {topic}")
    if dimensions:
        lines.append(
            "Cover each of these dimensions thoroughly and separately: "
            + "; ".join(dimensions)
            + "."
        )
    else:
        lines.append(
            "Research the subject thoroughly and report the most decision-relevant findings."
        )
    lines.append(
        "Use web search / fetch as needed. Be concrete and source-grounded; flag "
        "uncertainty rather than fabricating."
    )
    lines.append("")
    lines.append(
        "Return ONLY a single YAML block in EXACTLY this shape (one `findings` key per "
        "dimension above), nothing else:"
    )
    lines.append("")
    lines.append("```yaml")
    lines.append(f"subject: {subject}")
    lines.append("findings:")
    if dimensions:
        for dim in dimensions:
            lines.append(f"  {dim}: \"<your concise, concrete finding>\"")
    else:
        lines.append("  summary: \"<your concise, concrete finding>\"")
    lines.append("notes: \"<optional cross-cutting observation, or omit>\"")
    lines.append("```")
    return "\n".join(lines)


# ---------- Spawn-recipe render (pure; the markdown the agent executes) ----------


def render_spawn_recipe(run: FanoutRun) -> str:
    """Render the spawn-recipe block: the markdown the in-session agent reads + executes
    to spawn the N sub-agents + TaskCreate each. This is the part the helper CANNOT do
    itself (a subprocess can't call the Agent / TaskCreate tools — only the agent can)."""
    lines: list[str] = []
    lines.append(f"# Parallel research fan-out — `{run.run_id}` (phase {run.phase})")
    lines.append("")
    lines.append(
        "> The user opted into parallel research. **In-person is the default; this is "
        "the speed path the user asked for.** Each subject below still becomes a real "
        "anchor for the conversation — fan-out gathers the raw material faster, it does "
        "not skip the in-person synthesis."
    )
    lines.append("")
    if run.topic:
        lines.append(f"**Brief:** {run.topic}")
    if run.dimensions:
        lines.append(f"**Dimensions (every sub-agent covers all):** {', '.join(run.dimensions)}")
    lines.append(f"**Subjects ({len(run.tasks)}):** " + ", ".join(t.subject for t in run.tasks))
    lines.append("")
    lines.append("## Step 1 — spawn the sub-agents (one message, in parallel)")
    lines.append("")
    lines.append(
        f"Issue all {len(run.tasks)} `Agent` calls in a SINGLE message so they run "
        "concurrently, and `TaskCreate` one task per subject so the user sees progress. "
        "Record each spawned task's id back into the ledger (`wb fanout` tracks the "
        "specs; you own the live `Agent`/`Task` handles)."
    )
    lines.append("")
    for i, t in enumerate(run.tasks, start=1):
        lines.append(f"### {i}. {t.subject}  (`{t.task_id}`)")
        lines.append("")
        lines.append(
            f'`TaskCreate(subject="fanout: {t.subject}", '
            f'description="Parallel research — {t.subject}")`'
        )
        lines.append("")
        lines.append(
            f'`Agent(subagent_type="{run.agent_type}", '
            f'description="research {t.subject}", prompt=<<<SPEC>>>)`'
        )
        lines.append("")
        lines.append("<<<SPEC>>>:")
        lines.append("")
        lines.append("```text")
        lines.append(t.spec)
        lines.append("```")
        lines.append("")
    lines.append("## Step 2 — collect + aggregate")
    lines.append("")
    lines.append(
        "When ALL sub-agents have returned, assemble their YAML blocks into one results "
        f"file at `.website-builder/fanout-results-{run.run_id}.yaml` with this shape:"
    )
    lines.append("")
    lines.append("```yaml")
    lines.append("results:")
    for t in run.tasks:
        lines.append(f"  - subject: {t.subject}")
        lines.append("    findings:")
        if run.dimensions:
            for dim in run.dimensions:
                lines.append(f"      {dim}: \"...\"")
        else:
            lines.append("      summary: \"...\"")
    lines.append("```")
    lines.append("")
    lines.append("Then run:")
    lines.append("")
    lines.append("```bash")
    lines.append(
        f"wb fanout aggregate --run {run.run_id} "
        f"--results .website-builder/fanout-results-{run.run_id}.yaml"
    )
    lines.append("```")
    lines.append("")
    lines.append(
        "`aggregate` produces a subjects × dimensions comparison matrix + per-dimension "
        "cross-cut + coverage-gap flags, writes it under `.website-builder/library/`, and "
        "marks the run aggregated in the ledger. **Then return to the in-person "
        "conversation** and walk the user through the synthesis — that is where the "
        "decision is made."
    )
    return "\n".join(lines).rstrip() + "\n"


# ---------- Aggregate core (pure; no I/O) ----------


def aggregate_results(
    run: FanoutRun | None,
    results: list[SubjectResult],
    *,
    dimensions: list[str] | None = None,
    now: datetime | None = None,
) -> SynthesisResult:
    """Aggregate N structured sub-agent results into a SynthesisResult.

    Pure: no file I/O. `run` provides topic/phase/dimensions when available; when it is
    None (aggregate called without a prior decompose), dimensions fall back to the
    explicit `dimensions` arg, else the ordered union of keys across all result findings.
    """
    if not results:
        raise ResultsError(
            "No results to aggregate.\n"
            "  The results file needs a non-empty `results:` list — one entry per "
            "subject, each with `subject:` + a `findings:` map."
        )

    # Resolve the dimension set (column order for the matrix + per-dimension sections).
    dims: list[str]
    if run is not None and run.dimensions:
        dims = list(run.dimensions)
    elif dimensions:
        dims = list(dimensions)
    else:
        dims = _union_dimensions(results)

    gaps = _coverage_gaps(results, dims)

    dt = now or _now()
    return SynthesisResult(
        run_id=run.run_id if run else "fanout-adhoc",
        phase=run.phase if run else 0,
        topic=run.topic if run else "",
        dimensions=dims,
        results=results,
        generated_utc=_iso_ts(dt),
        synthesis_goal=run.synthesis_goal if run else "",
        gaps=gaps,
    )


def _union_dimensions(results: list[SubjectResult]) -> list[str]:
    """Ordered union of every findings key across results (first-seen order)."""
    seen: list[str] = []
    for r in results:
        for k in r.findings:
            if k not in seen:
                seen.append(k)
    return seen


def _coverage_gaps(results: list[SubjectResult], dims: list[str]) -> list[str]:
    """Flag (subject, dimension) pairs where a declared dimension has no finding."""
    gaps: list[str] = []
    for r in results:
        missing = [d for d in dims if not r.findings.get(d)]
        if missing:
            gaps.append(f"{r.subject}: missing " + ", ".join(f"`{m}`" for m in missing))
    # Also flag dimensions no subject covered at all.
    for d in dims:
        if all(not r.findings.get(d) for r in results):
            gaps.append(f"dimension `{d}`: no subject reported a finding")
    return gaps


# ---------- Ledger I/O (round-trip-preserving over .website-builder/tasks.yaml) ----------


def _state_dir(project_root: Path) -> Path:
    return project_root / STATE_DIR_NAME


def _tasks_yaml_path(project_root: Path) -> Path:
    return _state_dir(project_root) / TASKS_YAML_NAME


def _load_tasks_doc(project_root: Path) -> dict[str, Any]:
    """Load the whole .website-builder/tasks.yaml document (or {} if absent).

    Round-trip-preserving: we load the ENTIRE doc so non-fanout keys (the agent's
    phase-progress mirror) survive a save. PyYAML is the parse path; if it's absent we
    try json (a prior fallback write) then wb_markdown.parse_yaml (scalar best-effort)."""
    path = _tasks_yaml_path(project_root)
    if not path.is_file():
        return {}
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise LedgerError(f"Could not read the ledger at {path}: {exc}") from exc
    if not text.strip():
        return {}
    if yaml is not None:
        data = yaml.safe_load(text)
        return data if isinstance(data, dict) else {}
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else {}
    except ValueError:
        return wb_markdown.parse_yaml(text)


def _dump_tasks_doc(doc: dict[str, Any]) -> str:
    """Serialize the whole tasks.yaml doc. PyYAML when available; JSON (valid YAML)
    fallback otherwise. block scalars + escaping are PyYAML's job on the supported path."""
    if yaml is not None:
        return yaml.safe_dump(
            doc, sort_keys=False, allow_unicode=True, default_flow_style=False, width=100
        )
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def _save_tasks_doc(project_root: Path, doc: dict[str, Any]) -> Path:
    path = _tasks_yaml_path(project_root)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_dump_tasks_doc(doc), encoding="utf-8")
    except OSError as exc:
        raise LedgerError(f"Could not write the ledger at {path}: {exc}") from exc
    return path


def _load_runs(project_root: Path) -> list[FanoutRun]:
    doc = _load_tasks_doc(project_root)
    ledger = doc.get(LEDGER_KEY)
    if not isinstance(ledger, dict):
        return []
    raw_runs = ledger.get("runs") or []
    return [FanoutRun.from_dict(r) for r in raw_runs if isinstance(r, dict)]


def record_run(project_root: Path, run: FanoutRun) -> Path:
    """Persist a FanoutRun into the `fanout:` subtree of .website-builder/tasks.yaml,
    preserving every other key. A run with the same run_id is replaced (idempotent)."""
    doc = _load_tasks_doc(project_root)
    ledger = doc.get(LEDGER_KEY)
    if not isinstance(ledger, dict):
        ledger = {}
    runs = ledger.get("runs")
    if not isinstance(runs, list):
        runs = []
    runs = [r for r in runs if not (isinstance(r, dict) and r.get("run_id") == run.run_id)]
    runs.append(run.to_dict())
    ledger["runs"] = runs
    doc[LEDGER_KEY] = ledger
    return _save_tasks_doc(project_root, doc)


def update_run(project_root: Path, run: FanoutRun) -> Path:
    """Round-trip alias for record_run — used by aggregate to flip status/synthesis_path."""
    return record_run(project_root, run)


def _find_run(project_root: Path, run_id: str | None) -> FanoutRun | None:
    runs = _load_runs(project_root)
    if not runs:
        return None
    if run_id is None:
        return runs[-1]  # most-recently-recorded run
    for r in runs:
        if r.run_id == run_id:
            return r
    raise LedgerError(
        f"No fan-out run {run_id!r} in the ledger.\n"
        f"  Known runs: {', '.join(r.run_id for r in runs) or '(none)'}.\n"
        "  Run `wb fanout status` to list them, or `wb fanout decompose` to create one."
    )


# ---------- Results loading ----------


def _load_results(path: Path) -> list[SubjectResult]:
    if not path.is_file():
        raise ResultsError(
            f"Results file not found: {path}\n"
            "  Assemble the spawned sub-agents' YAML blocks into a `results:` list first "
            "(see the spawn-recipe Step 2 / skills/wb-fanout/SKILL.md)."
        )
    text = path.read_text(encoding="utf-8")
    data = wb_markdown.parse_yaml(text)
    raw = data.get("results")
    if raw is None and isinstance(data, dict) and "subject" in data:
        raw = [data]  # tolerate a single bare result object
    if not isinstance(raw, list) or not raw:
        raise ResultsError(
            f"Results file {path} has no non-empty `results:` list.\n"
            "  Expected: `results:` → a list of `{subject, findings:{dim: text}, notes}`."
        )
    return [SubjectResult.from_dict(r) for r in raw if isinstance(r, dict)]


# ---------- Verb handlers ----------


def _cmd_decompose(project_root: Path, rest: list[str]) -> int:
    """`wb fanout decompose` — brief → ledger + spawn-recipe (stdout)."""
    parser = argparse.ArgumentParser(prog="wb fanout decompose", add_help=True)
    parser.add_argument("--brief", type=Path, default=None,
                        help="Path to a YAML brief file (phase/topic/subjects/dimensions/...).")
    parser.add_argument("--phase", type=int, default=None, help="The opt-in phase (2/3/5/8).")
    parser.add_argument("--topic", default=None, help="The overall research question.")
    parser.add_argument("--subjects", default=None,
                        help="Comma-separated fan-out subjects (the N things researched).")
    parser.add_argument("--dimensions", default=None,
                        help="Comma-separated facets every sub-agent covers.")
    parser.add_argument("--synthesis-goal", default=None,
                        help="What the aggregate synthesis should produce.")
    parser.add_argument("--agent-type", default=None,
                        help=f"subagent_type to spawn (default {DEFAULT_AGENT_TYPE}).")
    try:
        args = parser.parse_args(rest)
    except SystemExit as exc:
        return int(exc.code or 0)

    brief = _assemble_brief(args)
    run = build_run(brief)

    if run.phase not in OPT_IN_PHASES:
        log_warn(
            f"phase {run.phase} is not a fan-out opt-in phase "
            f"({', '.join(map(str, OPT_IN_PHASES))}). Proceeding, but parallel research "
            "is by-design an opt-in at those phases — confirm the user asked for speed here."
        )
    if len(run.tasks) < 2:
        log_warn(
            "only 1 subject — fanning out over a single subject adds no parallelism. "
            "Consider an in-person pass instead."
        )

    path = record_run(project_root, run)
    log_ok(f"recorded run {run.run_id} ({len(run.tasks)} task(s)) → {path}")
    print(render_spawn_recipe(run))
    return 0


def _assemble_brief(args: argparse.Namespace) -> dict[str, Any]:
    """Build the brief dict from a --brief file and/or inline flags (inline overrides)."""
    brief: dict[str, Any] = {}
    if args.brief is not None:
        if not args.brief.is_file():
            raise BriefError(f"Brief file not found: {args.brief}")
        loaded = wb_markdown.parse_yaml(args.brief.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise BriefError(f"Brief file {args.brief} did not parse to a mapping.")
        brief.update(loaded)
    if args.phase is not None:
        brief["phase"] = args.phase
    if args.topic is not None:
        brief["topic"] = args.topic
    if args.subjects is not None:
        brief["subjects"] = args.subjects
    if args.dimensions is not None:
        brief["dimensions"] = args.dimensions
    if args.synthesis_goal is not None:
        brief["synthesis_goal"] = args.synthesis_goal
    if args.agent_type is not None:
        brief["agent_type"] = args.agent_type
    return brief


def _cmd_aggregate(project_root: Path, rest: list[str]) -> int:
    """`wb fanout aggregate` — N structured results → synthesis artifact (+ ledger update)."""
    parser = argparse.ArgumentParser(prog="wb fanout aggregate", add_help=True)
    parser.add_argument("--results", type=Path, required=True,
                        help="Path to the assembled YAML results file (`results:` list).")
    parser.add_argument("--run", dest="run_id", default=None,
                        help="Run id to aggregate (default: the most-recent recorded run).")
    parser.add_argument("--dimensions", default=None,
                        help="Override the dimension set (comma-separated); else from the "
                             "run, else the union of result findings keys.")
    parser.add_argument("--out", type=Path, default=None,
                        help="Synthesis output path (default .website-builder/library/"
                             "fanout-<run_id>-synthesis.md).")
    try:
        args = parser.parse_args(rest)
    except SystemExit as exc:
        return int(exc.code or 0)

    results = _load_results(args.results)
    run = _find_run(project_root, args.run_id)
    dims_override = (
        _normalize_str_list(args.dimensions, field_name="dimensions")
        if args.dimensions else None
    )

    synthesis = aggregate_results(run, results, dimensions=dims_override)

    # run_id already starts with "fanout-"; don't double the prefix.
    out_path = args.out or (
        _state_dir(project_root) / LIBRARY_DIR_NAME / f"{synthesis.run_id}-synthesis.md"
    )
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(synthesis.render(), encoding="utf-8")
    except OSError as exc:
        raise ResultsError(f"Could not write the synthesis to {out_path}: {exc}") from exc

    # Flip the run's status/synthesis_path + mark every matched task done (round-trip).
    if run is not None:
        run.status = "aggregated"
        run.synthesis_path = str(out_path)
        covered = {r.subject for r in results}
        for t in run.tasks:
            if t.subject in covered:
                t.status = "done"
                if t.result_ref is None:
                    t.result_ref = str(args.results)
        update_run(project_root, run)

    log_ok(f"aggregated {len(results)} result(s) → {out_path}")
    print(synthesis.render())
    return 0


def _cmd_status(project_root: Path, rest: list[str]) -> int:
    """`wb fanout status` — print the fan-out ledger (the round-trip read side)."""
    parser = argparse.ArgumentParser(prog="wb fanout status", add_help=True)
    parser.add_argument("--run", dest="run_id", default=None,
                        help="Show only this run id (default: all runs).")
    try:
        args = parser.parse_args(rest)
    except SystemExit as exc:
        return int(exc.code or 0)

    runs = _load_runs(project_root)
    if args.run_id:
        runs = [r for r in runs if r.run_id == args.run_id]
    if not runs:
        print("No fan-out runs recorded.")
        return 0
    for r in runs:
        done = sum(1 for t in r.tasks if t.status == "done")
        print(f"{r.run_id}  [phase {r.phase}]  status={r.status}  "
              f"tasks={done}/{len(r.tasks)} done")
        if r.topic:
            print(f"    topic: {r.topic}")
        if r.dimensions:
            print(f"    dimensions: {', '.join(r.dimensions)}")
        if r.synthesis_path:
            print(f"    synthesis: {r.synthesis_path}")
        for t in r.tasks:
            print(f"      - {t.task_id}  [{t.status}]  {t.subject}")
    return 0


# ---------- run (the `wb fanout` dispatch entry point) ----------

VERBS = {
    "decompose": _cmd_decompose,
    "aggregate": _cmd_aggregate,
    "status": _cmd_status,
}


def run(argv: list[str], *, project_root: Path) -> int:
    """Dispatch a `wb fanout` sub-verb.

    argv: the args AFTER `wb fanout` (e.g. ["decompose", "--brief", "brief.yaml"]).
    project_root: the user's project dir (contains .website-builder/).
    Returns a process exit code (0 = success).

    Verbs handled: decompose | aggregate | status.
    """
    if not argv:
        log_err(
            "Usage: wb fanout <verb>\n"
            "  decompose   Decompose a research brief into N sub-agent specs + a spawn-recipe\n"
            "  aggregate   Aggregate the N structured sub-agent results into a synthesis\n"
            "  status      Show the fan-out ledger (runs + per-task status)"
        )
        return 2

    verb, rest = argv[0], argv[1:]
    handler = VERBS.get(verb)
    if handler is None:
        log_err(
            f"Unknown `wb fanout` verb: {verb!r}. "
            f"Valid verbs: {', '.join(sorted(VERBS))}."
        )
        return 2

    try:
        return handler(project_root, rest)
    except FanoutError as exc:
        log_err(str(exc))
        return 1


# ---------- Standalone CLI (dispatcher normally calls run()) ----------


def main(argv: list[str] | None = None) -> int:
    """Standalone entry: `python wb_fanout.py <verb>` or `python wb_fanout.py fanout <verb>`.
    The `wb` dispatcher calls run() directly; this exists for isolated debugging.
    project_root = cwd."""
    args = list(argv if argv is not None else sys.argv[1:])
    if args and args[0] == "fanout":
        args = args[1:]
    return run(args, project_root=Path.cwd())


if __name__ == "__main__":
    sys.exit(main())
