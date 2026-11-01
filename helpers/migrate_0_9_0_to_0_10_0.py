#!/usr/bin/env python3
"""
Migrate CAMO datasets from schema 0.9.0 to 0.10.0.

Applied automatically:
  - TemporalExtent.observation_seasons entries are converted from free text
    to SeasonEnum values ("late spring" and "late-spring" both become
    late_spring). Matching ignores case, hyphens and surrounding whitespace.
  - CausalGraph.schema_version is set to 0.10.0.

Reported for review, not changed (these need a human decision):
  - observation_seasons entries that name no season. 0.9.0 allowed any
    string, so some hold a window spanning seasons or years ("year 1 autumn
    to year 2 early spring") or a life-history period ("fledging period").
    The first belong in the new temporal_extent.time_since_intervention_text,
    the second in the new CausalNode.life_stage_term. Neither can be placed
    mechanically, so the entry is left as it is and the record will not
    validate until a human moves it.
  - CausalEdge.dose holding a QuantityValue with no numeric_value,
    minimum_value or maximum_value. Those records did not validate under
    0.9.0 either; 0.10.0 gives them somewhere to go, so each is reported with
    the CausalEdge.dose_level value its verbatim text suggests. Not applied
    automatically, because dropping a dose a reader can see in the source is
    a judgement call.

Input can be YAML or JSON holding a CausalGraph, a list of CausalGraphs, a
list of edges, or a single edge. YAML comments are not preserved.

Usage:
    python helpers/migrate_0_9_0_to_0_10_0.py data.yaml -o data_0.10.0.yaml
    python helpers/migrate_0_9_0_to_0_10_0.py data.yaml --in-place
    python helpers/migrate_0_9_0_to_0_10_0.py data.yaml --check

Exit codes:
    0  migrated (or, with --check, already 0.10.0-shaped); nothing to review
    1  error (unreadable input, unexpected schema_version)
    2  migrated, but some entries need review (see the report on stderr)
    3  --check only: the file needs migration
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

FROM_VERSION = "0.9.0"
TO_VERSION = "0.10.0"

# Free-text season spellings seen in 0.9.0 data, mapped to SeasonEnum values.
# Keys are normalised: lower-cased, hyphens and underscores turned into spaces,
# whitespace collapsed.
SEASON_MAP = {
    "early spring": "early_spring",
    "mid spring": "mid_spring",
    "middle spring": "mid_spring",
    "late spring": "late_spring",
    "spring": "spring",
    "early summer": "early_summer",
    "summer": "summer",
    "autumn": "autumn",
    "fall": "autumn",
    "winter": "winter",
    "growing season": "growing_season",
    "dormant season": "dormant_season",
    "non growing season": "dormant_season",
}

# Ordinal dose words, for the dose_level suggestion in the review report.
DOSE_WORDS = [
    (r"\bvery high\b|\bextreme", "very_high"),
    (r"\bhigh\b|\bheavy\b|\bintense", "high"),
    (r"\bintermediate\b|\bmoderate\b|\bmedium\b", "intermediate"),
    (r"\blow\b|\bsparse\b|\blight\b", "low"),
    (r"\bno\b|\bzero\b|\babsent\b|\bunseeded\b|\bnone\b", "absent"),
    (r"\bhigher\b|\bgreater\b|\bmore\b", "higher_than_comparator"),
    (r"\blower\b|\bless\b|\bfewer\b", "lower_than_comparator"),
]


def normalise(text: str) -> str:
    """Lower-case, turn hyphens and underscores into spaces, collapse runs."""
    return re.sub(r"\s+", " ", str(text).replace("-", " ").replace("_", " ")).strip().lower()


def suggest_dose_level(verbatim: str) -> str:
    low = normalise(verbatim)
    for pattern, value in DOSE_WORDS:
        if re.search(pattern, low):
            return value
    return "not_specified"


def iter_graphs(data):
    """Yield every mapping that looks like a CausalGraph."""
    if isinstance(data, dict):
        if "nodes" in data or "edges" in data:
            yield data
    elif isinstance(data, list):
        for item in data:
            yield from iter_graphs(item)


def iter_edges(data):
    """Yield every mapping that looks like a CausalEdge, with a path label."""
    if isinstance(data, dict):
        if {"subject", "predicate", "object"} <= set(data):
            yield data.get("id", "<no id>"), data
        for value in data.values():
            yield from iter_edges(value)
    elif isinstance(data, list):
        for item in data:
            yield from iter_edges(item)


def iter_nodes(data):
    if isinstance(data, dict):
        for graph in iter_graphs(data):
            for node in graph.get("nodes") or []:
                yield node
    elif isinstance(data, list):
        for item in data:
            yield from iter_nodes(item)


def migrate(data) -> tuple[int, list[str]]:
    """Rewrite data in place. Return (changes applied, review notes)."""
    changed = 0
    review: list[str] = []

    for edge_id, edge in iter_edges(data):
        extent = edge.get("temporal_extent")
        if isinstance(extent, dict):
            seasons = extent.get("observation_seasons")
            if isinstance(seasons, list):
                for i, entry in enumerate(seasons):
                    if not isinstance(entry, str):
                        continue
                    mapped = SEASON_MAP.get(normalise(entry))
                    if mapped and mapped != entry:
                        seasons[i] = mapped
                        changed += 1
                    elif not mapped:
                        review.append(
                            f"edge {edge_id}: observation_seasons[{i}] = {entry!r} "
                            "names no season. A window spanning seasons or years "
                            "belongs in temporal_extent.time_since_intervention_text; "
                            "a life-history period belongs in CausalNode.life_stage_term."
                        )

        dose = edge.get("dose")
        if isinstance(dose, dict):
            has_number = any(
                dose.get(k) is not None
                for k in ("numeric_value", "minimum_value", "maximum_value")
            )
            if not has_number:
                verbatim = dose.get("verbatim") or ""
                review.append(
                    f"edge {edge_id}: dose has no numeric_value, minimum_value or "
                    f"maximum_value (verbatim {verbatim!r}), so it does not validate. "
                    f"0.10.0 records a named level as dose_level; suggested value: "
                    f"{suggest_dose_level(verbatim)}. Set dose_level and remove dose, "
                    "or add the quantity if the source gives one."
                )

    for graph in iter_graphs(data):
        if graph.get("schema_version") != TO_VERSION:
            graph["schema_version"] = TO_VERSION
            changed += 1
        provenance = graph.get("provenance")
        if isinstance(provenance, dict) and provenance.get("causal_mosaic_version"):
            if provenance["causal_mosaic_version"] != TO_VERSION:
                provenance["causal_mosaic_version"] = TO_VERSION
                changed += 1

    return changed, review


def needs_migration(data) -> bool:
    for graph in iter_graphs(data):
        if graph.get("schema_version") != TO_VERSION:
            return True
    for _edge_id, edge in iter_edges(data):
        extent = edge.get("temporal_extent")
        if isinstance(extent, dict):
            for entry in extent.get("observation_seasons") or []:
                if isinstance(entry, str) and SEASON_MAP.get(normalise(entry)) != entry:
                    return True
    return False


def load(path: Path):
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text), "json"
    return yaml.safe_load(text), "yaml"


def dump(data, fmt: str) -> str:
    if fmt == "json":
        return json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=f"Migrate CAMO data from {FROM_VERSION} to {TO_VERSION}."
    )
    ap.add_argument("input", type=Path)
    out = ap.add_mutually_exclusive_group()
    out.add_argument("-o", "--output", type=Path, help="write the migrated data here")
    out.add_argument("--in-place", action="store_true", help="overwrite the input file")
    out.add_argument("--check", action="store_true", help="report only; write nothing")
    args = ap.parse_args(argv)

    try:
        data, fmt = load(args.input)
    except Exception as exc:  # noqa: BLE001 - report any read or parse failure
        print(f"error: cannot read {args.input}: {exc}", file=sys.stderr)
        return 1

    if data is None:
        print(f"error: {args.input} is empty", file=sys.stderr)
        return 1

    if args.check:
        if needs_migration(data):
            print(f"{args.input}: needs migration to {TO_VERSION}")
            return 3
        print(f"{args.input}: already {TO_VERSION}-shaped")
        return 0

    changed, review = migrate(data)
    text = dump(data, fmt)

    if args.in_place:
        args.input.write_text(text, encoding="utf-8")
        target = args.input
    elif args.output:
        args.output.write_text(text, encoding="utf-8")
        target = args.output
    else:
        sys.stdout.write(text)
        target = None

    where = f" -> {target}" if target else ""
    print(f"{args.input}: {changed} change(s) applied{where}", file=sys.stderr)

    if review:
        print(f"\n{len(review)} item(s) need review:", file=sys.stderr)
        for note in review:
            print(f"  - {note}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
