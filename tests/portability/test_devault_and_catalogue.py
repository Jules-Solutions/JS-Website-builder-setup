"""Portability guard + ecosystem-catalogue tests.

Two concerns, both landed by the catalogue/de-vault packet (Decision 91,
supersedes Decision 88 — "ship the menu, fetch the meals"):

1. TestPortabilityGuard — the plugin must be vault-independent. A fresh clone
   with no Jules.Life vault must have ZERO `Workstreams/` references in any
   shipped runtime file. This is the regression guard that keeps the plugin
   from silently re-acquiring dead vault paths (the defect this packet fixed:
   ~122 shipped files carried author-vault `Workstreams/website-builder/...`
   refs, some load-bearing runtime read-instructions that dead-ended off-vault).

2. TestEcosystemCatalogue — the curated catalogue (the "menu") must ship as a
   bundled plugin artifact, parse, carry the expected categories, and tag every
   surfacing decision.

Run:
  bash tests/run-tests.sh
  cd tests && uv run --with pyyaml --with pytest pytest portability/ -v
"""

from __future__ import annotations

import re
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent

# Directories that are NOT part of the shipped runtime surface. Mirrors the
# de-vault sweep scope: tests/ and .claude/ are excluded per the packet spec;
# the rest are build/vcs/cache artifacts.
SKIP_DIRS = {
    ".git",
    ".claude",
    ".ruff_cache",
    "__pycache__",
    ".venv",
    "node_modules",
    "tests",
}
TEXT_EXT = {".md", ".py", ".sh", ".json", ".yaml", ".yml", ".toml", ".txt"}
VAULT_REF = re.compile(r"Workstreams/")


def _shipped_text_files():
    for p in PLUGIN_ROOT.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(PLUGIN_ROOT)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if p.suffix.lower() not in TEXT_EXT:
            continue
        yield p


class TestPortabilityGuard:
    """A fresh clone (no vault) must have zero dead vault references."""

    def test_no_vault_refs_in_shipped_files(self):
        offenders: list[str] = []
        for p in _shipped_text_files():
            try:
                text = p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for i, line in enumerate(text.splitlines(), 1):
                if VAULT_REF.search(line):
                    rel = p.relative_to(PLUGIN_ROOT)
                    offenders.append(f"{rel}:{i}: {line.strip()[:120]}")
        assert not offenders, (
            "Plugin must be vault-independent: shipped files must contain no "
            "`Workstreams/` references (a fresh clone has no vault, so those "
            "paths dead-end). Repoint load-bearing refs to "
            "${CLAUDE_PLUGIN_ROOT}/reference-corpus/ECOSYSTEM-CATALOG.md (or a "
            "bundled corpus dir), and convert provenance refs to by-name notes.\n"
            "Offenders:\n" + "\n".join(offenders)
        )

    def test_guard_actually_scans_runtime_files(self):
        # Sanity: the walk must reach real runtime files, else the guard above
        # could pass vacuously.
        names = {p.name for p in _shipped_text_files()}
        assert "02-vision.md" in names, "guard did not reach phase-contracts/"
        assert "ECOSYSTEM-CATALOG.md" in names, "guard did not reach reference-corpus/"


CATALOG = PLUGIN_ROOT / "reference-corpus" / "ECOSYSTEM-CATALOG.md"

SURFACING_TAGS = ("bundled", "clone-into-project", "fetch-on-demand")

# Category headings the catalogue must carry (substring match — headings may
# carry a parenthetical suffix, e.g. "Framework documentation (context7-served)").
EXPECTED_SECTIONS = (
    "Bundled reference corpora",
    "Design-system / artifact-extraction tools",
    "Design-skill flavors",
    "Component libraries",
    "CMS",
    "Commerce platforms",
    "Payment providers",
    "Booking platforms",
    "Stack adapters",
    "Hosting + DNS",
    "Inspiration galleries",
    "Templates + starter sources",
    "Framework documentation",
)

BUNDLED_CORPORA = (
    "brand-examples",
    "voice-archetypes",
    "design-systems",
    "component-patterns",
    "seo-checklists",
    "awesome-design-md-corpus",
)


class TestEcosystemCatalogue:
    """The curated catalogue ships bundled, parses, and is well-formed."""

    def test_catalogue_ships(self):
        assert CATALOG.is_file(), (
            f"the ecosystem catalogue must ship at "
            f"{CATALOG.relative_to(PLUGIN_ROOT)}"
        )

    def test_catalogue_parses(self):
        text = CATALOG.read_text(encoding="utf-8")
        assert text.strip(), "catalogue is empty"
        assert text.lstrip().startswith("# "), "catalogue must open with an H1"

    def test_expected_categories_present(self):
        text = CATALOG.read_text(encoding="utf-8")
        headings = {
            ln.lstrip("#").strip() for ln in text.splitlines() if ln.startswith("## ")
        }
        missing = [
            s for s in EXPECTED_SECTIONS if not any(s in h for h in headings)
        ]
        assert not missing, (
            f"catalogue missing expected categories: {missing}\n"
            f"got: {sorted(headings)}"
        )

    def test_surfacing_tags_present(self):
        text = CATALOG.read_text(encoding="utf-8")
        for tag in SURFACING_TAGS:
            assert f"`{tag}`" in text, (
                f"catalogue must carry the `{tag}` surfacing tag"
            )

    def test_entries_carry_urls(self):
        text = CATALOG.read_text(encoding="utf-8")
        n = text.count("https://")
        assert n >= 60, (
            f"catalogue should be comprehensive (>=60 resource URLs); found {n}"
        )

    def test_bundled_corpora_listed(self):
        text = CATALOG.read_text(encoding="utf-8")
        for d in BUNDLED_CORPORA:
            assert d in text, f"catalogue should list the bundled corpus `{d}`"

    def test_no_vault_path_in_catalogue(self):
        # The catalogue names its authoring SSOT by doc-name, never by vault path.
        text = CATALOG.read_text(encoding="utf-8")
        assert "Workstreams/" not in text, (
            "catalogue must reference its SSOT by name, not by vault path"
        )
