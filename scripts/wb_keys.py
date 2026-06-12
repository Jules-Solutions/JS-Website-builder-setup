#!/usr/bin/env python3
"""
scripts/wb_keys.py — the website-builder plugin's secrets/keys module.

Two public entry points (the locked module-boundary contract in
`scripts/README.md` § "Module boundary"):

    run(argv, *, project_root) -> int
        Dispatch a `wb keys` sub-verb. Verbs: migrate-to-1password | migrate-to-env.

    resolve_keys(project_root) -> dict[str, str]
        Resolve `.website-builder/keys.yaml` -> {env_var_name: value}. Reads `.env`
        (source: env) + `op://` references via the `op` CLI (source: onepassword).
        Called by the SessionStart hook / resolver entry point — NOT a `wb keys`
        sub-verb. Raises KeyResolutionError (with a fix-path message) on unresolved
        required keys.

This module is the resolver-layer + migration-CLI half of
`Workstreams/website-builder/cross-cutting/DESIGN-secrets-and-keys.md` (the hybrid
`.env` / 1Password model, decisions 29 + 44). The `.env` path is the muggle
default; the 1Password CLI path is the opt-in power-user upgrade. Code in the
user's generated project always reads `process.env.<NAME>` — this module ensures
those env vars exist, regardless of source.

Interface rules (locked — `scripts/README.md` § "Interface rules"):
  - IMPORT-SAFE: importing this module has NO side effects (no network, no file
    writes, no `op` calls at import time). All work happens inside the entry
    points. The `op`-CLI verification at module scope is deferred to call time.
  - Does NOT import the dispatcher (no circular dependency). Does NOT import the
    library module (P and Q never import each other).
  - `project_root` is passed in explicitly — this module never reads
    `os.getcwd()` itself (testability; mirrors wb-bootstrap.py's contract).

1Password CLI surface verified 2026-06-12 (per Decision 75 — fresh ID resolution;
the design doc is dated 2026-05-10) against https://www.1password.dev/cli/reference :
  - `op read <op://vault/item/field> -n`   — resolve one secret reference (primary
                                              resolver mechanism; -n = --no-newline)
  - `op item create [<section>.]<field>[[<fieldType>]]=<value> --category --title
        --vault`                             — assignment-statement create syntax
  - `op item get <name|id> --fields label=... --reveal`
  - `op whoami`                              — signed-in probe (non-zero exit = not
                                              signed in)
  - `op --version`                           — availability probe

See also:
  - Workstreams/website-builder/cross-cutting/DESIGN-secrets-and-keys.md
  - skills/wb-bootstrap/SKILL.md (Step 3 — records secrets_backend in project.yaml)
  - scripts/wb-bootstrap.py (sibling runner — YAML emit/parse precedent reused here)
  - scripts/README.md (the module-boundary contract)
  - .claude/rules/secrets-conventions.md (never write a secret to logs/files)
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

# ---------- Constants ----------

MODULE_NAME = "wb_keys"
SECRETS_DESIGN_DOC = (
    "Workstreams/website-builder/cross-cutting/DESIGN-secrets-and-keys.md"
)
STATE_DIR_NAME = ".website-builder"
KEYS_YAML_NAME = "keys.yaml"
ENV_OP_NAME = ".env.op"

# The leaf-entry marker. Any dict in keys.yaml that carries an `env_var` key is a
# "key entry" — the unit the resolver and migrators operate on. `source` defaults
# to "env" when omitted (matches the muggle default).
ENTRY_MARKER = "env_var"

VALID_SOURCES = ("env", "onepassword")

# The 1Password CLI binary name. Overridable via env for testability + non-standard
# installs (mirrors wb-bootstrap.py's WB_BOOTSTRAP_PYTHON override pattern).
OP_BIN = os.environ.get("WB_OP_BIN", "op")


# ---------- Typed errors (the fix-path-carrying contract) ----------

class KeysError(Exception):
    """Base class for keys-module errors. Carries a human fix-path message."""


class KeyResolutionError(KeysError):
    """
    Raised by resolve_keys() when one or more required keys can't be resolved.

    The message names each unresolved key + the concrete fix path (per the design
    doc's "Validation failures surface to user with diagnostic + fix path", lines
    474-488). Never contains a secret value — only key names + sources.
    """

    def __init__(self, unresolved: list["UnresolvedKey"]) -> None:
        self.unresolved = unresolved
        super().__init__(self._render())

    def _render(self) -> str:
        lines = [
            f"{len(self.unresolved)} required key(s) could not be resolved:",
            "",
        ]
        for u in self.unresolved:
            lines.append(f"  - {u.env_var}  (source: {u.source})")
            lines.append(f"      {u.fix_path}")
        lines.append("")
        lines.append(
            f"See {SECRETS_DESIGN_DOC} for the full secrets model, or run "
            "`wb maintain reconfig` to revisit your secrets backend."
        )
        return "\n".join(lines)


class OpCliUnavailableError(KeysError):
    """Raised when a `source: onepassword` key is needed but `op` isn't usable."""


# ---------- Logging helpers (mirror wb-bootstrap.py) ----------

def _color_supported() -> bool:
    return sys.stdout.isatty()


_USE_COLOR = _color_supported()


def _c(code: str, msg: str) -> str:
    if not _USE_COLOR:
        return msg
    return f"\x1b[{code}m{msg}\x1b[0m"


def log_info(msg: str) -> None:
    print(f"{_c('36', '[wb keys]')} {msg}", flush=True)


def log_ok(msg: str) -> None:
    print(f"{_c('32', '[wb keys]')} {msg}", flush=True)


def log_warn(msg: str) -> None:
    print(f"{_c('33', '[wb keys]')} {msg}", file=sys.stderr, flush=True)


def log_err(msg: str) -> None:
    print(f"{_c('31', '[wb keys]')} {msg}", file=sys.stderr, flush=True)


# ---------- YAML emit / parse (mirror wb-bootstrap.py's pyyaml-with-fallback) ----------
#
# keys.yaml is committed config; project.yaml/.env are read-mostly. We reuse the
# same PyYAML-when-available, hand-rolled-fallback shape as wb-bootstrap.py so the
# module runs both under the test harness (`uv run --with pyyaml`) and under a bare
# interpreter. keys.yaml is nested (image_gen.api_key.source, ...), so the parse
# path must produce nested dicts — the hand-rolled fallback covers the simple
# nesting we generate; PyYAML is the real path in every supported runtime.

try:
    import yaml  # type: ignore
    HAS_PYYAML = True
except ImportError:  # pragma: no cover — exercised only outside the test harness
    HAS_PYYAML = False


def parse_yaml(text: str) -> dict[str, Any]:
    """Parse YAML to a dict. PyYAML when available; minimal nested fallback else."""
    if HAS_PYYAML:
        result = yaml.safe_load(text)
        return result if isinstance(result, dict) else {}
    return _hand_parse_yaml(text)


def _hand_parse_yaml(text: str) -> dict[str, Any]:
    """
    Minimal indentation-based YAML parser for the nested-dict shape keys.yaml uses
    (block mappings, scalar leaves, no flow-style, no lists at the leaves we read).
    Sufficient for keys.yaml resolution when PyYAML is absent; PyYAML is the path
    in every supported runtime (the test harness pins it).
    """
    root: dict[str, Any] = {}
    # stack of (indent, container_dict)
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.split("#", 1)[0].strip() if val else ""
        # Pop to the correct parent for this indent level.
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
    if raw.startswith(("'", '"')) and raw.endswith(("'", '"')) and len(raw) >= 2:
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


def emit_yaml(data: dict[str, Any]) -> str:
    """Emit YAML. PyYAML when available; minimal nested fallback else."""
    if HAS_PYYAML:
        return yaml.safe_dump(  # type: ignore[no-any-return]
            data, sort_keys=False, default_flow_style=False, allow_unicode=True
        )
    return _hand_emit_yaml(data, 0)


def _hand_emit_yaml(node: Any, indent: int) -> str:
    pad = " " * indent
    out: list[str] = []
    if isinstance(node, dict):
        if not node:
            return f"{pad}{{}}\n" if indent else "{}\n"
        for k, v in node.items():
            if isinstance(v, dict):
                if not v:
                    out.append(f"{pad}{k}: {{}}")
                else:
                    out.append(f"{pad}{k}:")
                    out.append(_hand_emit_yaml(v, indent + 2).rstrip("\n"))
            else:
                out.append(f"{pad}{k}: {_emit_scalar(v)}")
    return "\n".join(out) + "\n"


def _emit_scalar(v: Any) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    s = str(v)
    specials = (":", "#", "{", "}", "[", "]", ",", "&", "*", "!", "|", ">",
                "'", '"', "%", "@", "`")
    if s == "" or any(c in s for c in specials) or s.lower() in (
        "yes", "no", "true", "false", "null", "~"
    ):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


# ---------- .env parsing (read-side; dotenv subset) ----------

def parse_dotenv(text: str) -> dict[str, str]:
    """
    Parse a .env file body into a {name: value} dict. Standard dotenv subset:
    KEY=VALUE lines, `#` comments, optional `export ` prefix, single/double quotes
    stripped. Blank lines + comments ignored. Does NOT expand ${VAR} interpolation
    (the resolver layer is the single source of truth for env composition).
    """
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].lstrip()
        if "=" not in line:
            continue
        name, _, value = line.partition("=")
        name = name.strip()
        if not name:
            continue
        value = value.strip()
        # Strip a single layer of matching quotes.
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        out[name] = value
    return out


# ---------- keys.yaml entry model ----------

class KeyEntry:
    """
    One resolvable key declared in keys.yaml. A "key entry" is any nested dict that
    carries an `env_var` field. The dotted path (e.g. "image_gen.api_key") is kept
    for diagnostics + for the migrators to flip `source` in place.
    """

    __slots__ = ("path", "env_var", "source", "ref", "required", "_node")

    def __init__(self, path: str, node: dict[str, Any]) -> None:
        self.path = path
        self.env_var: str = str(node[ENTRY_MARKER])
        self.source: str = str(node.get("source", "env"))
        self.ref: str | None = node.get("ref")
        # Every declared entry is required unless explicitly marked optional. The
        # design's validation block ("all keys.yaml entries have a value") treats
        # declared = required; `required: false` is the opt-out (e.g. a key only
        # some deploys need).
        self.required: bool = bool(node.get("required", True))
        self._node = node  # live reference into the parsed tree (migrators mutate)


class UnresolvedKey:
    """A required key that couldn't be resolved, plus its concrete fix path."""

    __slots__ = ("env_var", "source", "fix_path")

    def __init__(self, env_var: str, source: str, fix_path: str) -> None:
        self.env_var = env_var
        self.source = source
        self.fix_path = fix_path


def collect_key_entries(keys_doc: dict[str, Any]) -> list[KeyEntry]:
    """
    Walk keys.yaml recursively and collect every leaf key-entry (dict carrying an
    `env_var` field). The keys.yaml schema is arbitrarily nested
    (image_gen.api_key, hosting.vercel.deploy_token, commerce.stripe.secret_key,
    ...) — see DESIGN-secrets-and-keys.md "Layer 1". `version` and other top-level
    scalars are skipped (only dicts are walked).
    """
    entries: list[KeyEntry] = []

    def _walk(node: Any, prefix: str) -> None:
        if not isinstance(node, dict):
            return
        if ENTRY_MARKER in node and not isinstance(node[ENTRY_MARKER], (dict, list)):
            entries.append(KeyEntry(prefix.rstrip("."), node))
            # A key entry is a leaf for collection purposes; don't descend into
            # its own scalar fields (source/ref/env_var/required).
            return
        for k, v in node.items():
            if isinstance(v, dict):
                _walk(v, f"{prefix}{k}.")

    _walk(keys_doc, "")
    return entries


# ---------- Path helpers ----------

def _state_dir(project_root: Path) -> Path:
    return project_root / STATE_DIR_NAME


def _keys_yaml_path(project_root: Path) -> Path:
    return _state_dir(project_root) / KEYS_YAML_NAME


def _load_keys_doc(project_root: Path) -> dict[str, Any]:
    path = _keys_yaml_path(project_root)
    if not path.is_file():
        raise KeysError(
            f"No keys.yaml found at {path}. Run `/wb-bootstrap` (or "
            "`wb maintain reconfig`) to initialize the project's secrets registry."
        )
    return parse_yaml(path.read_text(encoding="utf-8"))


def _find_dotenv(project_root: Path) -> Path | None:
    """
    Locate the .env file. Per the design (Layer 2), .env can live at the project
    root OR inside .website-builder/. Project root wins (the common dotenv
    convention every tutorial uses); .website-builder/.env is the documented
    fallback. Returns None if neither exists.
    """
    candidates = [
        project_root / ".env",
        _state_dir(project_root) / ".env",
    ]
    for c in candidates:
        if c.is_file():
            return c
    return None


def _load_dotenv(project_root: Path) -> dict[str, str]:
    path = _find_dotenv(project_root)
    if path is None:
        return {}
    return parse_dotenv(path.read_text(encoding="utf-8"))


# ---------- op CLI helpers (called only inside entry points — import-safe) ----------

def _op_available() -> bool:
    """True if the `op` CLI is on PATH. No side effects beyond a `which` lookup."""
    return shutil.which(OP_BIN) is not None


def _run_op(args: list[str], *, input_text: str | None = None) -> subprocess.CompletedProcess:
    """
    Invoke `op` with the given args. Thin wrapper so tests can monkeypatch a single
    seam. Never logs stdout (it may contain a secret). 30s timeout — op signin /
    network can be slow but shouldn't hang a session.
    """
    return subprocess.run(
        [OP_BIN, *args],
        input=input_text,
        capture_output=True,
        text=True,
        timeout=30,
    )


def _op_read(ref: str) -> str:
    """
    Resolve a single `op://vault/item/field` reference to its value via `op read`.
    Verified 2026-06-12 syntax: `op read <ref> -n` (-n = --no-newline, so the
    returned value has no trailing newline). Raises OpCliUnavailableError with a
    fix path on any failure (not-installed / not-signed-in / bad-ref).
    """
    if not _op_available():
        raise OpCliUnavailableError(_op_install_hint())
    try:
        proc = _run_op(["read", ref, "-n"])
    except FileNotFoundError:  # race: op disappeared between which() and run
        raise OpCliUnavailableError(_op_install_hint())
    except subprocess.TimeoutExpired:
        raise OpCliUnavailableError(
            f"`op read {ref}` timed out. Check your network + that you're signed "
            "in (`op signin`)."
        )
    if proc.returncode != 0:
        # stderr is op's own diagnostic — safe to surface (it names the failure,
        # not the secret). Common cases: not signed in, vault/item/field not found.
        stderr = (proc.stderr or "").strip()
        raise OpCliUnavailableError(
            f"`op read {ref}` failed (exit {proc.returncode}): {stderr or 'unknown error'}. "
            "If you're not signed in, run `op signin`. If the reference is wrong, "
            "check it in your 1Password app (Right-click → Copy Secret Reference)."
        )
    return proc.stdout


def _op_signed_in() -> bool:
    """
    Best-effort signed-in probe via `op whoami` (verified 2026-06-12). Returns False
    if op is missing or whoami exits non-zero. Advisory only — the real signal is
    `op read` succeeding or failing per-reference.
    """
    if not _op_available():
        return False
    try:
        proc = _run_op(["whoami"])
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    return proc.returncode == 0


def _op_install_hint() -> str:
    """Per-platform `op` install path (per DESIGN-secrets-and-keys.md install section)."""
    plat = sys.platform
    if plat == "darwin":
        how = "brew install --cask 1password-cli"
    elif plat.startswith("win"):
        how = "winget install AgileBits.1Password.CLI"
    else:
        how = (
            "see https://www.1password.dev/cli/get-started/ (apt: add the 1Password "
            "apt repo, then `sudo apt install 1password-cli`)"
        )
    return (
        f"The 1Password CLI (`{OP_BIN}`) isn't installed or isn't on PATH. "
        f"Install it: {how}\n"
        "Then enable CLI integration in the 1Password app "
        "(Settings -> Developer) and run `op signin`. "
        "If you'd rather not use 1Password, run `wb keys migrate-to-env` to switch "
        "these keys to a .env file."
    )


# ---------- resolve_keys (the SessionStart resolver entry point) ----------

def resolve_keys(project_root: Path) -> dict[str, str]:
    """
    Resolve `.website-builder/keys.yaml` to a {env_var_name: value} dict.

    For each key entry:
      - source: env         -> read from .env, then fall back to the process env
                               (the design's ".env <-> system env vars" path: a
                               user with a shell-exported var works without a .env
                               line).
      - source: onepassword -> resolve the `ref` (op://...) via the `op` CLI.

    Validation (per DESIGN-secrets-and-keys.md lines 173-185 + 474-488): every
    REQUIRED entry must produce a value. Unresolved required keys are collected and
    raised together as a single KeyResolutionError carrying per-key fix paths —
    so the user sees ALL missing keys at once, not one-at-a-time.

    Returns {env_var: value} for every entry that resolved (required + optional).
    Never logs a value. project_root is passed in explicitly (no os.getcwd()).
    """
    keys_doc = _load_keys_doc(project_root)
    entries = collect_key_entries(keys_doc)
    dotenv = _load_dotenv(project_root)

    resolved: dict[str, str] = {}
    unresolved: list[UnresolvedKey] = []

    # Resolve 1Password-sourced keys lazily: only probe op-availability if at least
    # one entry needs it (so a pure-.env project never touches `op`).
    op_entries = [e for e in entries if e.source == "onepassword"]
    op_ready = True
    if op_entries:
        if not _op_available():
            op_ready = False
        elif not _op_signed_in():
            # Not a hard stop here — let each op_read attempt produce its own
            # precise error; but record the advisory for the fix path.
            op_ready = True  # attempt anyway; op read will give the real signal

    for entry in entries:
        if entry.source == "env":
            value = dotenv.get(entry.env_var)
            if value is None:
                value = os.environ.get(entry.env_var)
            if value is not None and value != "":
                resolved[entry.env_var] = value
            elif entry.required:
                unresolved.append(UnresolvedKey(
                    entry.env_var, "env",
                    _env_fix_path(entry, project_root),
                ))
        elif entry.source == "onepassword":
            if not entry.ref:
                if entry.required:
                    unresolved.append(UnresolvedKey(
                        entry.env_var, "onepassword",
                        f"keys.yaml entry '{entry.path}' has source: onepassword but "
                        "no `ref:` (op://vault/item/field). Add the reference, or "
                        "switch it to source: env.",
                    ))
                continue
            if not op_ready:
                if entry.required:
                    unresolved.append(UnresolvedKey(
                        entry.env_var, "onepassword", _op_install_hint(),
                    ))
                continue
            try:
                value = _op_read(entry.ref)
            except OpCliUnavailableError as exc:
                if entry.required:
                    unresolved.append(UnresolvedKey(
                        entry.env_var, "onepassword", str(exc),
                    ))
                continue
            if value != "":
                resolved[entry.env_var] = value
            elif entry.required:
                unresolved.append(UnresolvedKey(
                    entry.env_var, "onepassword",
                    f"`op read {entry.ref}` returned an empty value. Check the "
                    "field exists + is non-empty in 1Password.",
                ))
        else:
            # Unknown source — schema violation. Treat as a fix-path item.
            if entry.required:
                unresolved.append(UnresolvedKey(
                    entry.env_var, entry.source,
                    f"keys.yaml entry '{entry.path}' has unknown source "
                    f"'{entry.source}'. Valid sources: {', '.join(VALID_SOURCES)}.",
                ))

    if unresolved:
        raise KeyResolutionError(unresolved)
    return resolved


def _env_fix_path(entry: KeyEntry, project_root: Path) -> str:
    dotenv_path = _find_dotenv(project_root) or (project_root / ".env")
    return (
        f"{entry.env_var} is not set. Add a line to {dotenv_path}:\n"
        f"        {entry.env_var}=<your-value-here>\n"
        "      (or export it in your shell). The .env file is gitignored — your "
        "secret won't be committed."
    )


# ---------- migrate-to-1password ----------

def _migrate_to_1password(project_root: Path, argv: list[str]) -> int:
    """
    `.env` -> 1Password (DESIGN-secrets-and-keys.md lines 445-455).

    For each `source: env` key currently resolvable from .env:
      - prompt for an op:// destination (vault/item/field)
      - create the item via `op item create`
      - flip the keys.yaml entry to source: onepassword + record the ref
      - optionally remove the value from .env (with confirmation)
      - verify resolution still works

    Non-interactive support: `--vault <name>` + `--yes` drive a scripted migration
    (each key -> op://<vault>/<env_var>/credential) so the flow is testable without
    a TTY. `--keep-env` retains the .env values (default removes after confirm).
    """
    parser = argparse.ArgumentParser(prog="wb keys migrate-to-1password", add_help=True)
    parser.add_argument("--vault", default=None,
                        help="Destination 1Password vault for created items "
                             "(non-interactive). Item title defaults to the env-var name.")
    parser.add_argument("--field", default="credential",
                        help="1Password field name to store the value in (default: credential).")
    parser.add_argument("--keep-env", action="store_true",
                        help="Keep the migrated values in .env (default: leave .env untouched "
                             "for now; removal of .env values is a separate confirmed step).")
    parser.add_argument("--yes", action="store_true",
                        help="Assume yes to confirmations (non-interactive).")
    args = parser.parse_args(argv)

    if not _op_available():
        log_err(_op_install_hint())
        return 4

    keys_doc = _load_keys_doc(project_root)
    entries = collect_key_entries(keys_doc)
    dotenv = _load_dotenv(project_root)

    env_entries = [e for e in entries if e.source == "env"]
    if not env_entries:
        log_ok("No source: env keys to migrate — keys.yaml has nothing on the .env path.")
        return 0

    migrated = 0
    for entry in env_entries:
        value = dotenv.get(entry.env_var) or os.environ.get(entry.env_var)
        if not value:
            log_warn(
                f"Skipping {entry.env_var}: no value found in .env or process env. "
                "Nothing to migrate for this key."
            )
            continue

        vault, item, field = _resolve_op_destination(entry, args)
        if vault is None:
            log_warn(f"Skipping {entry.env_var}: no destination provided.")
            continue

        ref = f"op://{vault}/{item}/{field}"
        # op item create with assignment statement: `<field>=<value>`. The value is
        # passed as an arg to op — never echoed by us (op masks it; we never log it).
        create_args = [
            "item", "create",
            "--category", "API Credential",
            "--title", item,
            "--vault", vault,
            f"{field}={value}",
        ]
        try:
            proc = _run_op(create_args)
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            log_err(f"Failed to create 1Password item for {entry.env_var}: {exc}")
            continue
        if proc.returncode != 0:
            log_err(
                f"`op item create` for {entry.env_var} failed (exit {proc.returncode}): "
                f"{(proc.stderr or '').strip()}"
            )
            continue

        # Flip keys.yaml entry in place: source -> onepassword, add ref.
        entry._node["source"] = "onepassword"
        entry._node["ref"] = ref
        log_ok(f"{entry.env_var} -> {ref} (created in 1Password; keys.yaml updated).")
        migrated += 1

    if migrated == 0:
        log_warn("Nothing migrated.")
        return 0

    # Persist the updated keys.yaml (references only — never the secret values).
    _write_keys_doc(project_root, keys_doc)

    # Verify resolution still works for the migrated set.
    _verify_after_migration(project_root, expect_sources={"onepassword"})

    if not args.keep_env:
        log_info(
            "Your .env still holds the original values. Once you've confirmed "
            "1Password resolution works, remove the migrated lines from .env "
            "(they're now duplicated in 1Password). I left .env untouched to be safe."
        )
    log_ok(f"Migrated {migrated} key(s) to 1Password. keys.yaml now references op://...")
    return 0


def _resolve_op_destination(entry: KeyEntry, args: argparse.Namespace) -> tuple[str | None, str, str]:
    """
    Decide the op://vault/item/field destination for a key.

    Non-interactive (`--vault` given): op://<vault>/<env_var>/<field>.
    Interactive (TTY, no --vault): prompt for a full op:// reference or vault.
    Returns (vault, item, field); vault is None if the user declined / no input.
    """
    field = args.field
    if args.vault:
        return args.vault, entry.env_var, field
    # Interactive prompt — only when attached to a TTY (never in tests/CI).
    if not sys.stdin.isatty():
        return None, entry.env_var, field
    log_info(
        f"Where in 1Password should {entry.env_var} go?\n"
        "  Enter a reference  op://<vault>/<item>/<field>  (e.g. op://Personal/Gemini/credential)\n"
        "  or just a vault name (item defaults to the env-var name, field to "
        f"'{field}'), or blank to skip:"
    )
    try:
        raw = input("  > ").strip()
    except EOFError:
        return None, entry.env_var, field
    if not raw:
        return None, entry.env_var, field
    if raw.startswith("op://"):
        parts = raw[len("op://"):].split("/")
        if len(parts) >= 3:
            return parts[0], parts[1], "/".join(parts[2:])
        if len(parts) == 2:
            return parts[0], parts[1], field
        return parts[0], entry.env_var, field
    return raw, entry.env_var, field


# ---------- migrate-to-env ----------

def _migrate_to_env(project_root: Path, argv: list[str]) -> int:
    """
    1Password -> `.env` (DESIGN-secrets-and-keys.md lines 457-468; the downgrade
    path).

    For each `source: onepassword` key:
      - resolve the op:// reference to its actual value via `op read`
      - write the value to .env
      - flip the keys.yaml entry to source: env
      - verify resolution still works
      - remind the user that .env now holds live secrets (.gitignore must be correct)
    """
    parser = argparse.ArgumentParser(prog="wb keys migrate-to-env", add_help=True)
    parser.add_argument("--env-file", default=None,
                        help="Target .env path (default: project-root .env, or the existing "
                             ".env if one is found).")
    args = parser.parse_args(argv)

    keys_doc = _load_keys_doc(project_root)
    entries = collect_key_entries(keys_doc)
    op_entries = [e for e in entries if e.source == "onepassword"]
    if not op_entries:
        log_ok("No source: onepassword keys to migrate — nothing on the 1Password path.")
        return 0

    if not _op_available():
        log_err(_op_install_hint())
        return 4

    # Resolve all op refs first; only write .env if every required one resolves
    # (avoid a half-migrated state).
    resolved_values: dict[str, str] = {}
    failures: list[str] = []
    for entry in op_entries:
        if not entry.ref:
            failures.append(
                f"{entry.env_var}: source: onepassword but no `ref:` in keys.yaml."
            )
            continue
        try:
            value = _op_read(entry.ref)
        except OpCliUnavailableError as exc:
            failures.append(f"{entry.env_var}: {exc}")
            continue
        resolved_values[entry.env_var] = value

    if failures:
        log_err("Cannot migrate to .env — some references didn't resolve:")
        for f in failures:
            log_err(f"  - {f}")
        log_err("No changes made. Fix the references (or sign in to op) and retry.")
        return 5

    # Determine target .env path.
    if args.env_file:
        env_path = Path(args.env_file)
        if not env_path.is_absolute():
            env_path = project_root / env_path
    else:
        env_path = _find_dotenv(project_root) or (project_root / ".env")

    # Merge into existing .env content (preserve unrelated lines).
    existing = parse_dotenv(env_path.read_text(encoding="utf-8")) if env_path.is_file() else {}
    existing.update(resolved_values)
    _write_dotenv(env_path, existing)

    # Flip keys.yaml entries to source: env, drop the ref.
    for entry in op_entries:
        if entry.env_var in resolved_values:
            entry._node["source"] = "env"
            entry._node.pop("ref", None)

    _write_keys_doc(project_root, keys_doc)

    # Verify resolution works on the .env path now.
    _verify_after_migration(project_root, expect_sources={"env"})

    log_ok(f"Migrated {len(resolved_values)} key(s) to {env_path}. keys.yaml now uses source: env.")
    log_warn(
        f"{env_path} now holds LIVE secret values. Make sure your .gitignore ignores it "
        "(.env / .env.* lines) so it's never committed. The website-builder bootstrap "
        "adds those lines by default; double-check if you customized .gitignore."
    )
    return 0


# ---------- shared migration helpers ----------

def _write_keys_doc(project_root: Path, keys_doc: dict[str, Any]) -> None:
    path = _keys_yaml_path(project_root)
    _write_text(path, emit_yaml(keys_doc))


def _write_dotenv(path: Path, values: dict[str, str]) -> None:
    """Write a .env file from a {name: value} dict. Values are not quoted unless they
    contain whitespace/# (kept simple + dotenv-portable)."""
    lines = []
    for name, value in values.items():
        if value == "" or any(c in value for c in (" ", "#", "\t", "\n")):
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'{name}="{escaped}"')
        else:
            lines.append(f"{name}={value}")
    _write_text(path, "\n".join(lines) + "\n")


def _write_text(path: Path, content: str) -> None:
    """Write LF-normalized UTF-8 (byte-identical cross-platform; mirrors wb-bootstrap.py)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode("utf-8"))


def _verify_after_migration(project_root: Path, *, expect_sources: set[str]) -> None:
    """
    Best-effort post-migration verification: re-resolve and report. Does NOT raise
    on failure (the migration already happened + persisted); it surfaces a warning
    so the user knows to investigate. Never logs values.
    """
    try:
        resolved = resolve_keys(project_root)
        log_ok(f"Verified: {len(resolved)} key(s) resolve after migration.")
    except KeyResolutionError as exc:
        log_warn(
            "Post-migration verification found unresolved keys (the migration "
            "itself completed). Details:\n" + str(exc)
        )
    except KeysError as exc:
        log_warn(f"Post-migration verification could not run: {exc}")


# ---------- run (the `wb keys` dispatch entry point) ----------

VERBS = {
    "migrate-to-1password": _migrate_to_1password,
    "migrate-to-env": _migrate_to_env,
}


def run(argv: list[str], *, project_root: Path) -> int:
    """
    Dispatch a `wb keys` sub-verb.

    argv: the args AFTER `wb keys` (e.g. ["migrate-to-1password", "--vault", "Personal"]).
    project_root: the user's project dir (contains .website-builder/).
    Returns a process exit code (0 = success).

    Verbs handled: migrate-to-1password | migrate-to-env. (No list/status — not in
    the locked decision-48 surface; the resolver is resolve_keys(), not a verb.)
    """
    if not argv:
        log_err(
            "Usage: wb keys <verb>\n"
            "  migrate-to-1password   Move .env keys into 1Password (op:// refs)\n"
            "  migrate-to-env         Resolve op:// refs back into a .env file"
        )
        return 2

    verb, rest = argv[0], argv[1:]
    handler = VERBS.get(verb)
    if handler is None:
        log_err(
            f"Unknown `wb keys` verb: {verb!r}. "
            f"Valid verbs: {', '.join(sorted(VERBS))}."
        )
        return 2

    try:
        return handler(project_root, rest)
    except KeysError as exc:
        log_err(str(exc))
        return 1


# ---------- Standalone CLI (convenience; dispatcher normally calls run()) ----------

def main(argv: list[str] | None = None) -> int:
    """
    Standalone entry: `python wb_keys.py keys <verb>` or `python wb_keys.py <verb>`.
    The `wb` dispatcher (Captain O) calls run() directly; this main() exists so the
    module is runnable in isolation for debugging. project_root = cwd.
    """
    args = list(argv if argv is not None else sys.argv[1:])
    # Tolerate a leading `keys` token (so `wb_keys.py keys migrate-to-env` works).
    if args and args[0] == "keys":
        args = args[1:]
    return run(args, project_root=Path.cwd())


if __name__ == "__main__":
    sys.exit(main())
