"""
JSON handoff protocol tests (Phase 6 / Captain R scope).

Asserts three contracts that BUILD-strategy Phase 6 DoD (line 253) names:

  (a) spec/component-request-v1.json is a well-formed JSON Schema.
  (b) Each adapter fixture's sample brief validates against that schema.
  (c) Round-trip ingestion on >=3 of the 6 AI-tool fixtures: feed each
      fixture's sample OUTPUT through the ingestion contract and assert it
      extracts the expected tokens / content / component-shape / code AND
      binds back to the brief `id`.

  DoD line 253: "Handoff protocol round-trips: agent emits brief -> AI tool
  produces output -> agent re-imports cleanly on >=3 of the 6 AI-tool
  fixtures." Fixture-validated, NOT a live-network test — the protocol is
  explicitly manual copy-paste (DESIGN-handoff-protocol.md § "What this
  protocol is NOT": "the user manually copies + pastes"). Mirrors the Phase-5
  Stitch precedent at tests/extraction/stitch/: the test embodies an
  executable reference implementation, the fixtures are stored, no network.

Two executable reference implementations live in this file:

  1. MiniSchemaValidator — a stdlib-only Draft-2020-12 *subset* validator
     covering exactly the keywords spec/component-request-v1.json uses
     (type, required, properties, additionalProperties, patternProperties,
     enum, const, pattern, minimum, minLength, minItems, minProperties,
     items, $ref to #/$defs/*, union type arrays). Mirrors the Stitch
     precedent's stdlib-only reference normalizer: no new test dependency,
     no edit to run-tests.sh / uv.lock / pyproject.toml (the harness ships
     only pytest + pyyaml). It both validates briefs AND self-checks that the
     schema is well-formed.

  2. ingest_output — the executable spec of the phase-6.5 AI-output-parser
     round-trip (handoff-spec/component-output-v1.md § "What the parser does"
     + extraction/ai-output.md). Identifies modality (Form 1 pure-code /
     fenced+prose vs Form 2 metadata-header), strips fences/prose, binds to a
     brief (by Form-2 brief_id or by filename = brief id), extracts the
     component name + props from the JSX, extracts the color tokens used, and
     runs the palette validator (flags any color value not in the brief's
     brand_context.color_palette and not a shadcn CSS-variable token ref).

If either reference drifts from the spec, these tests surface the drift.

Run via:
  ./tests/run-tests.sh          (from plugin root — default 'all' mode)
  cd tests && uv run --with pyyaml --with pytest pytest handoff-protocol -v
"""

from __future__ import annotations

import json
import re
from pathlib import Path

# --- Paths -----------------------------------------------------------------

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = PLUGIN_ROOT / "spec" / "component-request-v1.json"
SAMPLES_DIR = PLUGIN_ROOT / "handoff-spec" / "adapter-fixtures" / "samples"
FIXTURES_DIR = PLUGIN_ROOT / "handoff-spec" / "adapter-fixtures"

# The 7 fixtures (6 AI tools + human-freelancer). Each has a sample brief.
ALL_BRIEFS = [
    "chatgpt-brief.json",
    "claude-ai-brief.json",
    "v0-brief.json",
    "cursor-brief.json",
    "lovable-brief.json",
    "bolt-new-brief.json",
    "human-freelancer-brief.json",
]

# The >=3 AI-tool fixtures exercised for round-trip ingestion (DoD bar).
ROUND_TRIP_PAIRS = [
    # (brief file, output file, modality, binds_by, on_brand)
    ("chatgpt-brief.json", "chatgpt-output.tsx", "form1-fenced", "filename", False),
    ("claude-ai-brief.json", "claude-ai-output.tsx", "form2-metadata", "metadata", True),
    ("v0-brief.json", "v0-output.tsx", "form1-pure", "filename", True),
]


# === Reference implementation 1: stdlib JSON Schema (Draft 2020-12 subset) ===
#
# Covers only the keyword set spec/component-request-v1.json uses. Raises
# SchemaError on a malformed schema; returns a list of validation errors for a
# data instance. No third-party dependency (mirrors Stitch's stdlib normalizer).


class SchemaError(Exception):
    """The schema itself is malformed (well-formedness failure)."""


# Keywords this subset validator understands. A schema node using anything
# outside this set is flagged by the well-formedness check, so the validator
# can never silently under-enforce.
_KNOWN_KEYWORDS = {
    "$schema", "$id", "$ref", "$defs", "title", "description",
    "type", "required", "properties", "additionalProperties",
    "patternProperties", "enum", "const", "pattern", "format",
    "minimum", "minLength", "minItems", "minProperties", "items",
    "default",
}

_TYPE_PY = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
}


class MiniSchemaValidator:
    """A deterministic Draft-2020-12 *subset* validator for the request schema."""

    def __init__(self, schema: dict):
        self.schema = schema
        self.defs = schema.get("$defs", {})

    # --- well-formedness -------------------------------------------------
    def check_schema(self) -> None:
        """Raise SchemaError unless the schema is structurally well-formed.

        Satisfies DoD (a): 'spec/component-request-v1.json is a well-formed
        JSON Schema.' Checks the $schema dialect, that every node uses only
        known keywords, that $refs resolve, and that enums/required are
        well-typed.
        """
        dialect = self.schema.get("$schema")
        if dialect != "https://json-schema.org/draft/2020-12/schema":
            raise SchemaError(f"unexpected $schema dialect: {dialect!r}")
        self._walk_schema_node(self.schema, "#")

    def _walk_schema_node(self, node: dict, path: str) -> None:
        if not isinstance(node, dict):
            raise SchemaError(f"{path}: schema node must be an object, got {type(node).__name__}")
        for kw in node:
            if kw not in _KNOWN_KEYWORDS:
                raise SchemaError(f"{path}: unknown/unsupported keyword {kw!r}")
        # $ref must resolve into #/$defs/<name>
        ref = node.get("$ref")
        if ref is not None:
            self._resolve_ref(ref, path)
        # type must name a known type (or a list thereof)
        t = node.get("type")
        if t is not None:
            for tt in ([t] if isinstance(t, str) else t):
                if tt not in _TYPE_PY:
                    raise SchemaError(f"{path}: unknown type {tt!r}")
        # required must be a list of strings
        req = node.get("required")
        if req is not None and not (isinstance(req, list) and all(isinstance(x, str) for x in req)):
            raise SchemaError(f"{path}: 'required' must be a list of strings")
        # enum / const sanity
        if "enum" in node and not isinstance(node["enum"], list):
            raise SchemaError(f"{path}: 'enum' must be a list")
        # recurse into subschema-bearing keywords
        for key in ("properties", "patternProperties", "$defs"):
            sub = node.get(key)
            if sub is not None:
                if not isinstance(sub, dict):
                    raise SchemaError(f"{path}/{key}: must be an object")
                for name, child in sub.items():
                    self._walk_schema_node(child, f"{path}/{key}/{name}")
        ap = node.get("additionalProperties")
        if isinstance(ap, dict):
            self._walk_schema_node(ap, f"{path}/additionalProperties")
        items = node.get("items")
        if isinstance(items, dict):
            self._walk_schema_node(items, f"{path}/items")
        # pattern must compile
        if "pattern" in node:
            try:
                re.compile(node["pattern"])
            except re.error as e:
                raise SchemaError(f"{path}: invalid regex pattern: {e}")
        for pk in node.get("patternProperties", {}):
            try:
                re.compile(pk)
            except re.error as e:
                raise SchemaError(f"{path}: invalid patternProperties key regex {pk!r}: {e}")

    def _resolve_ref(self, ref: str, path: str) -> dict:
        if not ref.startswith("#/$defs/"):
            raise SchemaError(f"{path}: only local #/$defs/* refs supported, got {ref!r}")
        name = ref[len("#/$defs/"):]
        if name not in self.defs:
            raise SchemaError(f"{path}: $ref {ref!r} does not resolve")
        return self.defs[name]

    # --- instance validation --------------------------------------------
    def validate(self, instance) -> list[str]:
        """Return a list of human-readable validation errors (empty == valid)."""
        errors: list[str] = []
        self._validate_node(self.schema, instance, "$", errors)
        return errors

    def _validate_node(self, schema: dict, value, path: str, errors: list[str]) -> None:
        # resolve $ref first
        if "$ref" in schema:
            schema = self._resolve_ref(schema["$ref"], path)

        # type
        t = schema.get("type")
        if t is not None:
            types = [t] if isinstance(t, str) else t
            # bool is a subclass of int in Python — guard integer/number
            ok = False
            for tt in types:
                py = _TYPE_PY[tt]
                if tt in ("integer", "number"):
                    if isinstance(value, bool):
                        continue
                    if isinstance(value, py):
                        ok = True
                elif tt == "boolean":
                    if isinstance(value, bool):
                        ok = True
                elif isinstance(value, py) and not (py is dict and isinstance(value, bool)):
                    ok = True
            if not ok:
                errors.append(f"{path}: expected type {t}, got {type(value).__name__}")
                return  # further checks meaningless on wrong type

        # const
        if "const" in schema and value != schema["const"]:
            errors.append(f"{path}: expected const {schema['const']!r}, got {value!r}")

        # enum
        if "enum" in schema and value not in schema["enum"]:
            errors.append(f"{path}: {value!r} not in enum {schema['enum']}")

        # string facets
        if isinstance(value, str):
            if "minLength" in schema and len(value) < schema["minLength"]:
                errors.append(f"{path}: string shorter than minLength {schema['minLength']}")
            if "pattern" in schema and not re.search(schema["pattern"], value):
                errors.append(f"{path}: {value!r} does not match pattern {schema['pattern']!r}")

        # number facets
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if "minimum" in schema and value < schema["minimum"]:
                errors.append(f"{path}: {value} < minimum {schema['minimum']}")

        # array facets
        if isinstance(value, list):
            if "minItems" in schema and len(value) < schema["minItems"]:
                errors.append(f"{path}: array shorter than minItems {schema['minItems']}")
            item_schema = schema.get("items")
            if isinstance(item_schema, dict):
                for i, item in enumerate(value):
                    self._validate_node(item_schema, item, f"{path}[{i}]", errors)

        # object facets
        if isinstance(value, dict):
            props = schema.get("properties", {})
            pattern_props = schema.get("patternProperties", {})
            additional = schema.get("additionalProperties", True)
            if "minProperties" in schema and len(value) < schema["minProperties"]:
                errors.append(f"{path}: fewer than minProperties {schema['minProperties']}")
            for req in schema.get("required", []):
                if req not in value:
                    errors.append(f"{path}: missing required property {req!r}")
            for key, sub_value in value.items():
                if key in props:
                    self._validate_node(props[key], sub_value, f"{path}.{key}", errors)
                    continue
                matched = False
                for pat, pat_schema in pattern_props.items():
                    if re.search(pat, key):
                        matched = True
                        self._validate_node(pat_schema, sub_value, f"{path}.{key}", errors)
                if matched:
                    continue
                if additional is False:
                    errors.append(f"{path}: additional property {key!r} not allowed")
                elif isinstance(additional, dict):
                    self._validate_node(additional, sub_value, f"{path}.{key}", errors)


# === Reference implementation 2: phase-6.5 round-trip ingestion ============
#
# The executable spec of handoff-spec/component-output-v1.md § "What the
# parser does with the output (Flow B inputs)". Pure, deterministic, no I/O
# beyond reading the fixture text passed in.

_FENCE_RE = re.compile(r"```[a-zA-Z0-9]*\n(.*?)```", re.DOTALL)
_METADATA_RE = re.compile(r"^/\*\s*(\{.*?\})\s*\*/", re.DOTALL)
# A Tailwind utility referencing a raw palette family (drift candidate):
# bg-indigo-600 / text-slate-500 / border-zinc-200 / hover:bg-rose-700 ...
_RAW_PALETTE_RE = re.compile(
    r"\b(?:bg|text|border|ring|from|to|via|fill|stroke|outline|decoration|"
    r"divide|accent|caret|shadow|placeholder)-"
    r"(slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|"
    r"emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-"
    r"\d{2,3}\b"
)
# An OKLCH literal used inside a Tailwind arbitrary value: bg-[oklch(...)].
_OKLCH_LITERAL_RE = re.compile(r"oklch\([^)]*\)")


def _normalize_oklch(value: str) -> str:
    """Normalize an OKLCH literal for brand-token comparison.

    Tailwind arbitrary values replace spaces with underscores
    (bg-[oklch(64%_0.18_30)]); brand palette tokens use spaces
    (oklch(64% 0.18 30)). Collapse both to a single canonical form so the
    palette validator compares like with like.
    """
    return re.sub(r"[\s_]+", " ", value).strip()
# shadcn CSS-variable theme tokens (on-brand by reference, not raw palette).
_SHADCN_TOKEN_RE = re.compile(
    r"\b(?:bg|text|border|ring|fill|stroke)-"
    r"(primary|secondary|foreground|background|card|muted|accent|destructive|"
    r"popover|border|input|ring|muted-foreground|card-foreground|"
    r"primary-foreground|secondary-foreground|accent-foreground)\b"
)


class IngestError(Exception):
    pass


def ingest_output(output_text: str, output_filename: str, briefs_by_id: dict[str, dict]) -> dict:
    """Phase-6.5 reference ingestion of an external-tool output.

    Returns a normalized ingestion result:
        {
          modality, bound_brief_id, code, component_name, props,
          colors_used, palette_drift, on_brand
        }
    Raises IngestError if the output cannot be bound to a brief.
    """
    # --- 1. Identify modality + extract code -----------------------------
    metadata = None
    md_match = _METADATA_RE.match(output_text.lstrip())
    if md_match:
        modality = "form2-metadata"
        metadata = json.loads(md_match.group(1))
        code = output_text[output_text.index("*/") + 2:].strip()
    elif "```" in output_text:
        modality = "form1-fenced"
        fence = _FENCE_RE.search(output_text)
        if not fence:
            raise IngestError("fenced output but no complete code fence found")
        code = fence.group(1).strip()
    else:
        modality = "form1-pure"
        code = output_text.strip()

    # --- 2. Bind to a brief ---------------------------------------------
    bound_brief_id = None
    if metadata is not None and metadata.get("brief_id"):
        bound_brief_id = metadata["brief_id"]
    else:
        # filename = brief id (strip extension)
        stem = Path(output_filename).stem
        if stem in briefs_by_id:
            bound_brief_id = stem
    if bound_brief_id is None or bound_brief_id not in briefs_by_id:
        raise IngestError(
            f"could not bind output {output_filename!r} to any brief "
            f"(metadata={metadata}, stem={Path(output_filename).stem!r})"
        )
    brief = briefs_by_id[bound_brief_id]

    # --- 3. Extract component name --------------------------------------
    name_match = re.search(r"export\s+function\s+([A-Za-z0-9_]+)", code) or \
        re.search(r"export\s+(?:default\s+)?(?:const|class)\s+([A-Za-z0-9_]+)", code)
    component_name = name_match.group(1) if name_match else None

    # --- 4. Extract props (from the destructured TS prop type) ----------
    props: list[str] = []
    type_match = re.search(r"type\s+\w+Props\s*=\s*\{(.*?)\}", code, re.DOTALL)
    if type_match:
        for line in type_match.group(1).splitlines():
            m = re.match(r"\s*([A-Za-z0-9_]+)\??\s*:", line)
            if m:
                props.append(m.group(1))
    else:
        # fall back to the destructuring in the function signature
        destr = re.search(r"function\s+\w+\(\s*\{([^}]*)\}", code)
        if destr:
            for raw in destr.group(1).split(","):
                token = raw.strip().split(":")[0].strip()
                if re.fullmatch(r"[A-Za-z0-9_]+", token):
                    props.append(token)

    # --- 5. Extract colors used + run the palette validator -------------
    brand_colors = {_normalize_oklch(v) for v in brief["brand_context"]["color_palette"].values()}
    oklch_raw = set(_OKLCH_LITERAL_RE.findall(code))
    oklch_used = {_normalize_oklch(c) for c in oklch_raw}
    shadcn_tokens = set(_SHADCN_TOKEN_RE.findall(code))
    raw_palette_drift = sorted(set(m.group(0) for m in _RAW_PALETTE_RE.finditer(code)))

    # On-brand iff: no raw Tailwind palette utilities, AND every OKLCH literal
    # used (whitespace-normalized) is one of the brand palette values (shadcn
    # token refs are on-brand by definition — they resolve through the
    # project's theme).
    off_brand_oklch = sorted(c for c in oklch_used if c not in brand_colors)
    palette_drift = raw_palette_drift + off_brand_oklch
    on_brand = len(palette_drift) == 0

    return {
        "modality": modality,
        "bound_brief_id": bound_brief_id,
        "code": code,
        "component_name": component_name,
        "props": props,
        "colors_used": sorted(oklch_used),
        "shadcn_tokens": sorted(shadcn_tokens),
        "palette_drift": palette_drift,
        "on_brand": on_brand,
    }


# --- Loaders ---------------------------------------------------------------

def _load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _load_brief(filename: str) -> dict:
    return json.loads((SAMPLES_DIR / filename).read_text(encoding="utf-8"))


def _briefs_by_id() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for fn in ALL_BRIEFS:
        brief = _load_brief(fn)
        out[brief["id"]] = brief
    return out


def _validator() -> MiniSchemaValidator:
    return MiniSchemaValidator(_load_schema())


# === Tier 1 — schema well-formedness =======================================

class TestSchemaWellFormed:
    """DoD (a): spec/component-request-v1.json is a well-formed JSON Schema."""

    def test_schema_file_exists(self):
        assert SCHEMA_PATH.is_file(), f"missing schema at {SCHEMA_PATH}"

    def test_schema_parses_as_json(self):
        schema = _load_schema()
        assert isinstance(schema, dict)

    def test_schema_declares_draft_2020_12(self):
        schema = _load_schema()
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"

    def test_schema_is_well_formed(self):
        # The reference validator raises SchemaError on any malformed node,
        # unknown keyword, unresolved $ref, or invalid regex.
        _validator().check_schema()

    def test_schema_required_top_level_keys_match_contract(self):
        # Block-by-block SSOT: handoff-spec/component-request-v1.md line 38.
        schema = _load_schema()
        expected = {
            "$schema", "$version", "type", "id", "created", "iteration",
            "subject", "brand_context", "request", "output_format",
            "iteration_history", "instructions_for_external_tool",
        }
        assert set(schema["required"]) == expected

    def test_schema_enums_present(self):
        # subject.kind + output_format.{framework,library,style_system,language}
        defs = _load_schema()["$defs"]
        assert defs["subject"]["properties"]["kind"]["enum"]
        of = defs["output_format"]["properties"]
        for k in ("framework", "library", "style_system", "language"):
            assert of[k]["enum"], f"output_format.{k} missing enum"

    def test_every_ref_resolves(self):
        # Walk schema; check_schema already enforces this, but assert the
        # concrete $defs the top level points at all exist.
        schema = _load_schema()
        for name in ("subject", "brand_context", "request", "output_format"):
            assert name in schema["$defs"], f"$defs missing {name}"


# === Tier 1 — each fixture's sample brief validates =========================

class TestSampleBriefsValidate:
    """DoD (b): each adapter fixture's sample brief validates against the schema."""

    def test_all_brief_files_present(self):
        for fn in ALL_BRIEFS:
            assert (SAMPLES_DIR / fn).is_file(), f"missing sample brief {fn}"

    def test_chatgpt_brief_validates(self):
        self._assert_valid("chatgpt-brief.json")

    def test_claude_ai_brief_validates(self):
        self._assert_valid("claude-ai-brief.json")

    def test_v0_brief_validates(self):
        self._assert_valid("v0-brief.json")

    def test_cursor_brief_validates(self):
        self._assert_valid("cursor-brief.json")

    def test_lovable_brief_validates(self):
        self._assert_valid("lovable-brief.json")

    def test_bolt_new_brief_validates(self):
        self._assert_valid("bolt-new-brief.json")

    def test_human_freelancer_brief_validates(self):
        # This brief is iteration 1 with a populated iteration_history —
        # exercises the iteration_entry $ref path.
        self._assert_valid("human-freelancer-brief.json")

    def test_iteration_matches_history_length(self):
        # Doctrine invariant from the schema description: iteration ==
        # len(iteration_history). Not a schema keyword (cross-field), so it is
        # asserted here over every brief.
        for fn in ALL_BRIEFS:
            brief = _load_brief(fn)
            assert brief["iteration"] == len(brief["iteration_history"]), (
                f"{fn}: iteration {brief['iteration']} != "
                f"len(iteration_history) {len(brief['iteration_history'])}"
            )

    def test_id_pattern_is_filename_safe(self):
        # ids must have no colons (filename-safe) + Z suffix.
        for fn in ALL_BRIEFS:
            brief = _load_brief(fn)
            assert ":" not in brief["id"], f"{fn}: id has a colon"
            assert brief["id"].endswith("Z"), f"{fn}: id not Z-suffixed"

    def _assert_valid(self, fn: str):
        errors = _validator().validate(_load_brief(fn))
        assert errors == [], f"{fn} failed validation:\n  " + "\n  ".join(errors)


# === Tier 1 — round-trip ingestion (>=3 of 6 AI-tool fixtures) =============

class TestRoundTripIngestion:
    """DoD (c): round-trip ingestion on >=3 of the 6 AI-tool fixtures.

    For each pair: feed the sample OUTPUT through the ingestion reference and
    assert it (1) identifies the right modality, (2) binds back to the brief
    `id`, (3) extracts the component name + props, (4) runs the palette
    validator with the expected on-brand / drift verdict.
    """

    def test_at_least_three_pairs(self):
        assert len(ROUND_TRIP_PAIRS) >= 3, "DoD requires >=3 round-trip fixtures"

    def test_all_pair_files_present(self):
        for brief_fn, output_fn, *_ in ROUND_TRIP_PAIRS:
            assert (SAMPLES_DIR / brief_fn).is_file(), f"missing {brief_fn}"
            assert (SAMPLES_DIR / output_fn).is_file(), f"missing {output_fn}"

    # ---- ChatGPT: Form 1, fenced + prose, brand drift caught -----------
    def test_chatgpt_round_trip(self):
        result = self._ingest("chatgpt-brief.json", "chatgpt-output.tsx")
        assert result["modality"] == "form1-fenced"
        assert result["bound_brief_id"] == "hero-block-2026-06-14T16-32-00Z"
        assert result["component_name"] == "HeroBlock"
        assert set(result["props"]) == {"headline", "sub", "cta_text", "background_image"}
        # The deliberate drift: bg-indigo-600 is NOT a brand token.
        assert result["on_brand"] is False
        assert any("indigo" in d for d in result["palette_drift"]), (
            f"palette validator should flag indigo drift; got {result['palette_drift']}"
        )
        # The fence + prose wrapper must be stripped (no backticks / no
        # 'Here's your' prose survives into the bound code).
        assert "```" not in result["code"]
        assert "Here's your" not in result["code"]
        assert result["code"].startswith("import")

    # ---- Claude.ai: Form 2, metadata-header bind, on-brand --------------
    def test_claude_ai_round_trip(self):
        result = self._ingest("claude-ai-brief.json", "claude-ai-output.tsx")
        assert result["modality"] == "form2-metadata"
        # Binds via the Form-2 metadata header brief_id, NOT filename.
        assert result["bound_brief_id"] == "subscribe-card-2026-06-14T17-05-00Z"
        assert result["component_name"] == "SubscribeCard"
        assert set(result["props"]) == {"heading", "blurb", "cta_text", "on_submit"}
        # All colors are brand OKLCH literals — no drift.
        assert result["palette_drift"] == [], (
            f"claude-ai output should be on-brand; drift: {result['palette_drift']}"
        )
        assert result["on_brand"] is True
        # Every OKLCH literal used is a brand palette value.
        brief = _load_brief("claude-ai-brief.json")
        brand_colors = set(brief["brand_context"]["color_palette"].values())
        for c in result["colors_used"]:
            assert c in brand_colors, f"unexpected non-brand oklch {c}"
        # The metadata header must NOT survive into the bound code.
        assert result["code"].startswith("import")

    # ---- v0: Form 1 pure code, shadcn token refs, on-brand --------------
    def test_v0_round_trip(self):
        result = self._ingest("v0-brief.json", "v0-output.tsx")
        assert result["modality"] == "form1-pure"
        assert result["bound_brief_id"] == "feature-card-2026-06-14T18-12-00Z"
        assert result["component_name"] == "FeatureCard"
        assert set(result["props"]) == {"icon", "title", "body", "href"}
        # v0 uses shadcn CSS-variable theme tokens (bg-card / text-primary /
        # text-foreground) — on-brand by reference, NOT raw palette drift.
        assert result["on_brand"] is True
        assert result["palette_drift"] == []
        assert "primary" in result["shadcn_tokens"], (
            f"expected shadcn token refs; got {result['shadcn_tokens']}"
        )

    def test_each_round_trip_binds_to_its_brief(self):
        # Cross-check: every round-trip output binds to a brief that actually
        # exists in the sample set (the binding invariant).
        briefs = _briefs_by_id()
        for brief_fn, output_fn, _modality, _binds, _on_brand in ROUND_TRIP_PAIRS:
            result = self._ingest(brief_fn, output_fn)
            assert result["bound_brief_id"] in briefs
            assert result["bound_brief_id"] == _load_brief(brief_fn)["id"]

    def test_on_brand_verdict_matches_fixture_intent(self):
        # The (..., on_brand) column of ROUND_TRIP_PAIRS is the documented
        # intent; the ingestion verdict must agree.
        for brief_fn, output_fn, _modality, _binds, expected_on_brand in ROUND_TRIP_PAIRS:
            result = self._ingest(brief_fn, output_fn)
            assert result["on_brand"] is expected_on_brand, (
                f"{output_fn}: on_brand {result['on_brand']} != intent {expected_on_brand}"
            )

    def _ingest(self, brief_fn: str, output_fn: str) -> dict:
        briefs = _briefs_by_id()
        output_text = (SAMPLES_DIR / output_fn).read_text(encoding="utf-8")
        # The sample output files are named by tool for repo organization
        # (chatgpt-output.tsx). At runtime the user saves the output under the
        # protocol's RECOMMENDED filename = the brief id ({brief-id}.{ext}, per
        # component-output-v1.md § "File naming + storage"). Simulate that here
        # so the filename-binding path (Form 1, no metadata header) resolves —
        # the metadata-bound path (Form 2) ignores the filename and binds via
        # the header brief_id regardless.
        brief_id = _load_brief(brief_fn)["id"]
        ext = Path(output_fn).suffix
        saved_as = f"{brief_id}{ext}"
        return ingest_output(output_text, saved_as, briefs)


# === Tier 1 — fixture completeness (mirrors Stitch convention) =============

class TestFixtureCompleteness:
    """The 7 fixtures + samples form a complete, self-describing contract."""

    SEVEN_FIXTURES = [
        "chatgpt.md", "claude-ai.md", "v0.md", "cursor.md",
        "lovable.md", "bolt-new.md", "human-freelancer.md",
    ]

    def test_all_seven_fixtures_present(self):
        for fn in self.SEVEN_FIXTURES:
            assert (FIXTURES_DIR / fn).is_file(), f"missing fixture {fn}"

    def test_six_ai_tool_fixtures_have_a_brief_each(self):
        # 6 AI tools + human-freelancer each ship a sample brief.
        assert len(ALL_BRIEFS) == 7

    def test_round_trip_outputs_present_for_three_ai_fixtures(self):
        for _brief, output_fn, *_ in ROUND_TRIP_PAIRS:
            assert (SAMPLES_DIR / output_fn).is_file()

    def test_no_real_secrets_in_samples(self):
        # Synthetic-only discipline (secrets-conventions.md).
        for p in SAMPLES_DIR.glob("*"):
            text = p.read_text(encoding="utf-8")
            assert "sk-" not in text, f"{p.name}: looks like a real API key"
            assert "API_KEY=" not in text, f"{p.name}: looks like a real secret"

    def test_fixtures_cross_link_the_schema(self):
        # The request contract must point at the concrete JSON Schema.
        contract = (PLUGIN_ROOT / "handoff-spec" / "component-request-v1.md").read_text(encoding="utf-8")
        assert "spec/component-request-v1.json" in contract
