#!/usr/bin/env python3
"""
Migrate CAMO datasets from schema 0.7.9 to 0.8.0.

Applied automatically:
  - CausalEdge.claim_strength is renamed to causal_language (key order kept).
  - CausalEdge.comparator, a single object in 0.7.9, is wrapped in a list.
  - Edges with causal_language: no_relationship get negated: true, the
    canonical null-result encoding.
  - CausalGraph.schema_version is set to 0.8.0.

Reported for review, not changed (these need a human decision):
  - negated: true with causal_language other than no_relationship. The
    negation may have been of hedged language.
  - Edges whose object node has the qualifier "unchanged". In 0.7.9 that
    could encode a null result; in 0.8.0 it means a reported stable state.
  - Edges that break the new predicate rules (associated_with,
    correlated_with and precedes must be associational or no_relationship;
    causes must not be associational).

Input can be YAML or JSON holding a CausalGraph, a list of CausalGraphs, a
list of edges, or a single edge. YAML comments are not preserved.

Usage:
    python helpers/migrate_0_7_9_to_0_8_0.py data.yaml -o data_0.8.0.yaml
    python helpers/migrate_0_7_9_to_0_8_0.py data.yaml --in-place
    python helpers/migrate_0_7_9_to_0_8_0.py data.yaml --check

Exit codes:
    0  migrated (or, with --check, already 0.8.0-shaped); nothing to review
    1  error (unreadable input, conflicting keys, unexpected schema_version)
    2  migrated, but some edges need review (see the report on stderr)
    3  --check only: the file needs migration
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

FROM_VERSION = "0.7.9"
TO_VERSION = "0.8.0"

NON_CAUSAL_PREDICATES = {"associated_with", "correlated_with", "precedes"}
NON_CAUSAL_LANGUAGE = {"associational", "no_relationship"}


class Report:
    def __init__(self) -> None:
        self.changes: list[str] = []
        self.review: list[str] = []
        self.errors: list[str] = []


def rename_key(d: dict, old: str, new: str) -> dict:
    """Return a copy of d with key old renamed to new, in the same position."""
    return {(new if k == old else k): v for k, v in d.items()}


def edge_label(edge: dict, index: int) -> str:
    return str(edge.get("id") or f"<edge #{index}>")


def migrate_edge(edge: dict, index: int, nodes: dict, r: Report) -> dict:
    eid = edge_label(edge, index)

    if "claim_strength" in edge:
        if "causal_language" in edge and edge["causal_language"] != edge["claim_strength"]:
            r.errors.append(
                f"{eid}: has both claim_strength ({edge['claim_strength']}) and "
                f"causal_language ({edge['causal_language']}) with different values")
            return edge
        if "causal_language" in edge:
            edge = {k: v for k, v in edge.items() if k != "claim_strength"}
        else:
            edge = rename_key(edge, "claim_strength", "causal_language")
        r.changes.append(f"{eid}: renamed claim_strength to causal_language")

    if isinstance(edge.get("comparator"), dict):
        edge["comparator"] = [edge["comparator"]]
        r.changes.append(f"{eid}: wrapped comparator in a list")

    language = edge.get("causal_language")
    negated = edge.get("negated", False) is True

    if language == "no_relationship" and not negated:
        edge["negated"] = True
        r.changes.append(f"{eid}: set negated: true (causal_language is no_relationship)")
    elif negated and language != "no_relationship":
        r.review.append(
            f"{eid}: negated: true but causal_language is {language!r}. Canonical "
            f"null results use no_relationship; decide whether this is a null "
            f"result or a negated hedged claim.")

    obj = nodes.get(edge.get("object"))
    if obj and obj.get("state_or_change_qualifier") == "unchanged" and not negated:
        r.review.append(
            f"{eid}: object node {edge.get('object')} is 'unchanged'. If this edge "
            f"reports a null result, set negated: true and causal_language: "
            f"no_relationship, and point object at the node a positive finding "
            f"would use. Leave it if the paper reports a stable state.")

    predicate = edge.get("predicate")
    if predicate in NON_CAUSAL_PREDICATES and language not in NON_CAUSAL_LANGUAGE:
        r.review.append(
            f"{eid}: predicate {predicate} with causal_language {language!r} breaks "
            f"a 0.8.0 rule (must be associational or no_relationship).")
    if predicate == "causes" and language == "associational":
        r.review.append(
            f"{eid}: predicate causes with causal_language associational breaks a "
            f"0.8.0 rule.")

    return edge


def migrate_edges(edges: list, nodes: dict, r: Report) -> list:
    return [migrate_edge(e, i, nodes, r) if isinstance(e, dict) else e
            for i, e in enumerate(edges)]


def migrate_graph(graph: dict, r: Report) -> dict:
    version = graph.get("schema_version")
    if version not in (None, FROM_VERSION, TO_VERSION):
        r.errors.append(
            f"graph {graph.get('graph_id', '')}: schema_version is {version}; this "
            f"helper only migrates {FROM_VERSION}. Migrate to {FROM_VERSION} first.")
        return graph
    nodes = {n.get("id"): n for n in graph.get("nodes") or [] if isinstance(n, dict)}
    graph["edges"] = migrate_edges(graph.get("edges") or [], nodes, r)
    if version != TO_VERSION:
        graph["schema_version"] = TO_VERSION
        r.changes.append(f"graph {graph.get('graph_id', '')}: schema_version set to {TO_VERSION}")
    return graph


def is_edge(d: object) -> bool:
    return isinstance(d, dict) and "subject" in d and "predicate" in d


def migrate_document(doc: object, r: Report) -> object:
    if isinstance(doc, dict) and "edges" in doc:
        return migrate_graph(doc, r)
    if is_edge(doc):
        return migrate_edge(doc, 0, {}, r)
    if isinstance(doc, list) and all(isinstance(d, dict) and "edges" in d for d in doc):
        return [migrate_graph(d, r) for d in doc]
    if isinstance(doc, list) and all(is_edge(d) for d in doc):
        return migrate_edges(doc, {}, r)
    r.errors.append("input is not a CausalGraph, a list of graphs, or a list of edges")
    return doc


def load(path: Path) -> tuple[object, str]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text), "json"
    return yaml.safe_load(text), "yaml"


def dump(doc: object, fmt: str) -> str:
    if fmt == "json":
        return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
    return yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=88)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=f"Migrate CAMO data from {FROM_VERSION} to {TO_VERSION}.")
    ap.add_argument("input", type=Path)
    out = ap.add_mutually_exclusive_group()
    out.add_argument("-o", "--output", type=Path, help="write the migrated data here")
    out.add_argument("--in-place", action="store_true", help="overwrite the input file")
    out.add_argument("--check", action="store_true", help="report only; write nothing")
    args = ap.parse_args(argv)

    try:
        doc, fmt = load(args.input)
    except (OSError, ValueError, yaml.YAMLError) as e:
        print(f"error: cannot read {args.input}: {e}", file=sys.stderr)
        return 1

    r = Report()
    migrated = migrate_document(doc, r)

    for line in r.changes:
        print(f"  changed  {line}", file=sys.stderr)
    for line in r.review:
        print(f"  REVIEW   {line}", file=sys.stderr)
    for line in r.errors:
        print(f"  ERROR    {line}", file=sys.stderr)
    print(f"{len(r.changes)} changed, {len(r.review)} to review, {len(r.errors)} errors",
          file=sys.stderr)

    if r.errors:
        return 1
    if args.check:
        return 3 if r.changes else (2 if r.review else 0)

    text = dump(migrated, fmt)
    if args.in_place:
        args.input.write_text(text, encoding="utf-8")
    elif args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 2 if r.review else 0


if __name__ == "__main__":
    sys.exit(main())
