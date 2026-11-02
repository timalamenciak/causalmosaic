#!/usr/bin/env python3
"""
Print a status report for the EcoSKOS vocabulary.

Shows how many terms are in each status, which terms still lack a broader
term, and which proposed or requested terms have been waiting longer than a
threshold, so stalled upstream requests get chased.

A term's age counts from requested_on when it is requested and that date is
set, otherwise from proposed_on.

Usage:
    python vocab/terms_report.py                 # stale after 90 days
    python vocab/terms_report.py --days 30
    python vocab/terms_report.py --today 2026-12-01   # fix the date, for testing

Exit codes:
    0  report printed (stale terms are reported, not an error)
    1  the source could not be read
"""

from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

from build_vocab import DEFAULT_SCHEMA, DEFAULT_SOURCE, STATUSES, load_prefixes, read_terms, validate

DEFAULT_DAYS = 90
WAITING = ("proposed", "requested")


def age_basis(term) -> tuple[str, str]:
    """The date a term's waiting time counts from, and which field it came from."""
    if term.status == "requested" and term.requested_on:
        return term.requested_on, "requested_on"
    return term.proposed_on, "proposed_on"


def parse_date(value: str) -> datetime.date | None:
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        return None


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS,
                        help=f"list proposed/requested terms older than this (default {DEFAULT_DAYS})")
    parser.add_argument("--today", type=datetime.date.fromisoformat, default=None,
                        help="treat this YYYY-MM-DD as today")
    args = parser.parse_args(argv[1:])

    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(errors="replace")

    try:
        terms, header_errors = read_terms(args.source)
    except (OSError, UnicodeDecodeError) as exc:
        print(f"cannot read {args.source}: {exc}", file=sys.stderr)
        return 1
    if header_errors:
        for message in header_errors:
            print(f"  FAIL  {message}", file=sys.stderr)
        return 1

    today = args.today or datetime.date.today()
    print(f"EcoSKOS terms report, {today.isoformat()}")
    print(f"{len(terms)} term(s) in {args.source.name}\n")

    print("By status")
    counts = {s: 0 for s in STATUSES}
    other = 0
    for term in terms:
        if term.status in counts:
            counts[term.status] += 1
        else:
            other += 1
    for status in STATUSES:
        print(f"  {status:<11} {counts[status]:>3}")
    if other:
        print(f"  {'other':<11} {other:>3}  (status not recognised)")

    no_parent = [t for t in terms if not t.broader and t.status != "deprecated"]
    print("\nWithout a broader term")
    if no_parent:
        for term in no_parent:
            print(f"  {term.id}  {term.label}")
    else:
        print("  none")

    stale, undated = [], []
    for term in terms:
        if term.status not in WAITING:
            continue
        value, field_name = age_basis(term)
        since = parse_date(value)
        if since is None:
            undated.append(term)
        elif (today - since).days > args.days:
            stale.append(((today - since).days, term, field_name, value))
    stale.sort(key=lambda item: (-item[0], item[1].id))

    print(f"\nProposed or requested for more than {args.days} days")
    if stale:
        for days, term, field_name, value in stale:
            line = f"  {term.id}  {days:>4} d  {term.status:<9}  {term.label}  ({field_name} {value})"
            print(line)
            if term.request_url:
                print(f"{'':>16}{term.request_url}")
    else:
        print("  none")
    for term in undated:
        print(f"  {term.id}  no valid date; cannot age  ({term.label})")

    problems, _ = validate(terms, load_prefixes(args.schema))
    if problems:
        print(f"\nNote: the source has {len(problems)} validation error(s); "
              "run `make vocab-check` for details.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
