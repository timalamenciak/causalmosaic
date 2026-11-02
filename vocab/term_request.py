#!/usr/bin/env python3
"""
Export one EcoSKOS term as a ready-to-paste ontology term request.

The output is markdown laid out like a new-term-request issue on an OBO
Foundry tracker (ENVO, GO, PATO, ECO and others): label, synonyms, definition,
proposed parent, rationale, example usage, sources. Paste it into the
tracker's issue form, trimming to whatever that tracker's template asks for.

Markdown goes to stdout, so it can be piped to a clipboard tool; anything that
needs your attention goes to stderr.

Usage:
    python vocab/term_request.py ecoskos:0000001
    python vocab/term_request.py 0000001 -o request.md

Exit codes:
    0  exported (check stderr for fields that were empty)
    1  the term was not found, or the source could not be read
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from build_vocab import (CURIE_RE, DEFAULT_SCHEMA, DEFAULT_SOURCE, ID_RE, PREFIX,
                         expand, load_prefixes, read_terms)

PROJECT = "Causal Mosaic (CAMO) schema, https://github.com/timalamenciak/causalmosaic"


def normalise_id(raw: str) -> str:
    raw = raw.strip()
    return f"{PREFIX}:{raw}" if re.fullmatch(r"\d{7}", raw) else raw


def bullet(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def render(term, prefixes: dict[str, str]) -> tuple[str, list[str]]:
    notes: list[str] = []

    if term.broader and CURIE_RE.fullmatch(term.broader) and term.broader.split(":")[0] in prefixes:
        parent = f"`{term.broader}` ({expand(term.broader, prefixes)})"
    else:
        parent = "_Not yet identified. Suggestions from the ontology editors are welcome._"
        notes.append("broader is empty or not resolvable: the request has no proposed parent")

    if term.rationale:
        rationale = term.rationale
    else:
        rationale = ("Needed to annotate ecological causal-evidence claims with the "
                     f"{PROJECT}. First encountered in: {term.source}")
        notes.append("rationale is empty: generic text used. Say why existing terms do not "
                     "serve, and which ontologies you searched")

    sections = [
        f"**Title:** New term request: {term.label}",
        "---",
        f"**Preferred term label**\n\n{term.label}",
    ]
    if term.synonyms:
        sections.append(f"**Synonyms**\n\n{bullet(term.synonyms)}")
    sections += [
        f"**Definition**\n\n{term.definition}",
        f"**Proposed parent term**\n\n{parent}",
        f"**Rationale / use case**\n\n{rationale}",
    ]
    if term.example_usage:
        sections.append(f"**Example usage**\n\n> {term.example_usage}")
    else:
        notes.append("example_usage is empty: the request has no example")
    sections.append(f"**Sources**\n\n{bullet([term.source])}")
    sections.append(f"**Requested by**\n\n{term.proposed_by}")
    sections.append(
        "**Cross-reference**\n\n"
        f"We hold this concept as a placeholder, `{term.id}`, in the EcoSKOS stopgap "
        "vocabulary of the project above. Once a term exists, please comment here with "
        "its ID so we can map our placeholder to it."
    )

    if term.status not in ("proposed", "requested"):
        notes.append(f"status is {term.status!r}, so a request may not be needed"
                     + (f" (mapped_to {term.mapped_to})" if term.mapped_to else ""))
    if term.status == "requested" and term.request_url:
        notes.append(f"a request is already open: {term.request_url}")
    return "\n\n".join(sections) + "\n", notes


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("term", help="term id, with or without the ecoskos: prefix")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("-o", "--output", type=Path, help="write to a file instead of stdout")
    args = parser.parse_args(argv[1:])

    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(errors="replace")

    term_id = normalise_id(args.term)
    if not ID_RE.fullmatch(term_id):
        print(f"{args.term!r} is not an EcoSKOS id (expected ecoskos:0000001 or 0000001)",
              file=sys.stderr)
        return 1
    try:
        terms, header_errors = read_terms(args.source)
        prefixes = load_prefixes(args.schema)
    except (OSError, UnicodeDecodeError) as exc:
        print(f"cannot read input: {exc}", file=sys.stderr)
        return 1
    if header_errors:
        for message in header_errors:
            print(f"  FAIL  {message}", file=sys.stderr)
        return 1

    match = next((t for t in terms if t.id == term_id), None)
    if match is None:
        print(f"{term_id} is not in {args.source.name}", file=sys.stderr)
        return 1

    text, notes = render(match, prefixes)
    for note in notes:
        print(f"  NOTE  {note}", file=sys.stderr)
    if args.output:
        args.output.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
