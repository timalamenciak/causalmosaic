"""
verify_spans.py — Source Span Verifier for Causal Mosaic YAML

For every source_span in a Causal Mosaic YAML file, checks whether the quoted
`text` field appears verbatim in the source document. Uses fuzzy matching to
catch near-misses where the LLM subtly altered a few characters.
See Annotation Guide Appendix A.4.3, Tool 3.

Usage:
    python verify_spans.py draft.yaml paper.txt
    python verify_spans.py draft.yaml paper.pdf    # PDF support via pdfplumber
    python verify_spans.py draft.yaml paper.txt --fix   # auto-correct near-matches
    python verify_spans.py draft.yaml paper.txt --threshold 0.85

Exit codes:
    0 — all spans matched (exact or near)
    1 — one or more spans not found
"""

import difflib
import json
import re
import sys
from pathlib import Path
from typing import Optional

import click
import yaml

# Shared text loading (handles .txt and .pdf)
sys.path.insert(0, str(Path(__file__).parent))
from utils import load_text as load_source_text


# ---------------------------------------------------------------------------
# Span extraction from YAML
# ---------------------------------------------------------------------------

def extract_spans(doc: dict) -> list[dict]:
    """Return a flat list of {span_id, text, source, edge_id} for all source_spans."""
    spans = []

    def _gather(item, edge_id: str):
        if not isinstance(item, dict):
            return
        for sub_span in item.get("source_spans", []):
            if not isinstance(sub_span, dict):
                continue
            text = sub_span.get("text", "")
            span_id = sub_span.get("id", f"{edge_id}.span")
            start_char = sub_span.get("start_char")
            end_char   = sub_span.get("end_char")
            spans.append({
                "span_id":    span_id,
                "text":       text,
                "source":     edge_id,
                "start_char": start_char,
                "end_char":   end_char,
            })

    for edge in doc.get("edges", []):
        eid = edge.get("id", "unknown_edge")
        _gather(edge, eid)

    for node in doc.get("nodes", []):
        nid = node.get("id", "unknown_node")
        _gather(node, nid)

    return spans


# ---------------------------------------------------------------------------
# Matching logic
# ---------------------------------------------------------------------------

def _normalise(text: str) -> str:
    """Normalise whitespace for fuzzy comparison."""
    return re.sub(r"\s+", " ", text).strip()


def check_span(span_text: str, source_text: str,
               threshold: float) -> tuple[str, float, Optional[tuple[int, int]], Optional[str]]:
    """Check a single span against the source text.

    Returns:
        (status, similarity, char_offsets, corrected_text)
        status: "exact_match" | "near_match" | "not_found"
        similarity: 0.0–1.0
        char_offsets: (start, end) in source_text, or None
        corrected_text: best-match text from source, or None
    """
    if not span_text.strip():
        return ("empty", 0.0, None, None)

    # Exact check (fastest path)
    idx = source_text.find(span_text)
    if idx != -1:
        return ("exact_match", 1.0, (idx, idx + len(span_text)), None)

    # Try normalised whitespace exact match
    norm_span = _normalise(span_text)
    norm_source = _normalise(source_text)
    idx2 = norm_source.find(norm_span)
    if idx2 != -1:
        # Map back to approximate offsets in original source
        return ("exact_match", 1.0, (idx2, idx2 + len(norm_span)), None)

    # Sliding-window fuzzy match
    span_len = len(span_text)
    best_ratio = 0.0
    best_start = -1

    # Use a window slightly larger than the span to account for small deletions/insertions
    window = span_len + max(20, span_len // 5)
    step   = max(1, span_len // 4)

    for start in range(0, max(1, len(source_text) - span_len + 1), step):
        candidate = source_text[start : start + window]
        ratio = difflib.SequenceMatcher(None, span_text, candidate, autojunk=False).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_start = start

    # Refine around best start
    if best_start >= 0:
        refine_start = max(0, best_start - step)
        refine_end   = min(len(source_text), best_start + window + step)
        for start in range(refine_start, refine_end, 1):
            candidate = source_text[start : start + span_len + 20]
            ratio = difflib.SequenceMatcher(None, span_text, candidate, autojunk=False).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_start = start

    if best_ratio >= threshold:
        corrected = source_text[best_start : best_start + span_len]
        return ("near_match", best_ratio, (best_start, best_start + span_len), corrected)

    return ("not_found", best_ratio, None, None)


def verify_char_offsets(span_text: str, source_text: str,
                        start_char: int, end_char: int) -> bool:
    """Return True if the text at [start_char:end_char] matches span_text."""
    if start_char is None or end_char is None:
        return True  # no offsets to verify
    return source_text[start_char:end_char] == span_text


# ---------------------------------------------------------------------------
# Diff display
# ---------------------------------------------------------------------------

def _show_diff(original: str, corrected: str, max_lines: int = 10) -> str:
    orig_lines = original.splitlines(keepends=True)
    corr_lines = corrected.splitlines(keepends=True)
    diff = list(difflib.unified_diff(orig_lines, corr_lines,
                                     fromfile="yaml_text", tofile="source_text", n=0))
    if not diff:
        return "(no diff)"
    if len(diff) > max_lines:
        diff = diff[:max_lines] + [f"... ({len(diff) - max_lines} more lines)\n"]
    return "".join(diff)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.command()
@click.argument("yaml_file",   type=click.Path(exists=True))
@click.argument("source_file", type=click.Path(exists=True))
@click.option("--threshold", "-t", default=0.90, show_default=True,
              help="Fuzzy similarity threshold for near-match (0.0–1.0).")
@click.option("--fix", is_flag=True, default=False,
              help="Auto-correct near-matches: replace the YAML span text with the exact source text.")
@click.option("--output", "-o", default=None,
              help="Write JSON report to this file (default: print to stdout).")
@click.option("--show-diff", "show_diff", is_flag=True, default=False,
              help="Print a diff for near-matches.")
def main(yaml_file, source_file, threshold, fix, output, show_diff):
    """Verify that source_spans in a Causal Mosaic YAML appear verbatim in the source text.

    Uses exact string matching first, then fuzzy matching for near-misses.
    The --fix flag auto-corrects near-matches by replacing the YAML text with
    the exact text from the source document.

    Exit code 1 if any spans are not found (below threshold).
    """
    with open(yaml_file, encoding="utf-8") as fh:
        try:
            doc = yaml.safe_load(fh)
        except yaml.YAMLError as exc:
            click.echo(f"ERROR: Could not parse YAML: {exc}", err=True)
            sys.exit(1)

    source_text = load_source_text(source_file)
    spans = extract_spans(doc)

    if not spans:
        click.echo("No source_spans found in the YAML file.")
        return

    click.echo(f"Checking {len(spans)} span(s) against {source_file}...")

    results = []
    fixes: list[tuple[str, str]] = []  # (old_text, new_text) pairs for --fix

    exact_count = near_count = not_found_count = empty_count = 0

    for span in spans:
        span_text = span.get("text", "")
        span_id   = span.get("span_id", "?")
        source    = span.get("source", "?")

        if not span_text.strip():
            results.append({
                "span_id": span_id, "source": source,
                "status": "empty", "similarity": 0.0,
                "char_offsets": None, "corrected_text": None,
                "offset_valid": None,
            })
            empty_count += 1
            continue

        status, similarity, offsets, corrected = check_span(span_text, source_text, threshold)

        # Verify explicitly supplied offsets
        offset_valid = None
        if span.get("start_char") is not None:
            offset_valid = verify_char_offsets(
                span_text, source_text,
                span["start_char"], span["end_char"]
            )

        result = {
            "span_id":       span_id,
            "source":        source,
            "status":        status,
            "similarity":    round(similarity, 4),
            "char_offsets":  list(offsets) if offsets else None,
            "corrected_text": corrected,
            "offset_valid":  offset_valid,
        }
        results.append(result)

        if status == "exact_match":
            exact_count += 1
        elif status == "near_match":
            near_count += 1
            if show_diff and corrected:
                click.echo(f"\n  Diff for {span_id!r} (score={similarity:.2f}):")
                click.echo(_show_diff(span_text, corrected))
            if fix and corrected:
                fixes.append((span_text, corrected))
        else:
            not_found_count += 1
            click.echo(
                f"  NOT FOUND  [{span_id}] from {source!r}\n"
                f"    Text: {span_text[:80]!r}{'...' if len(span_text) > 80 else ''}\n"
                f"    Best similarity: {similarity:.2f}"
            )

    # Apply fixes
    if fix and fixes:
        click.echo(f"\nApplying {len(fixes)} fix(es) to {yaml_file}...")
        with open(yaml_file, encoding="utf-8") as fh:
            yaml_content = fh.read()
        for old_text, new_text in fixes:
            # Replace within YAML string carefully — escape is not needed since
            # we're doing a raw text replacement of the quoted value
            yaml_content = yaml_content.replace(old_text, new_text, 1)
        with open(yaml_file, "w", encoding="utf-8") as fh:
            fh.write(yaml_content)
        click.echo("Fixes applied. Re-run verify_spans.py to confirm.")

    # Report
    report = {
        "summary": {
            "total":     len(spans),
            "exact_match":   exact_count,
            "near_match":    near_count,
            "not_found":     not_found_count,
            "empty":         empty_count,
            "threshold":     threshold,
        },
        "results": results,
    }

    json_output = json.dumps(report, indent=2, ensure_ascii=False)
    if output:
        with open(output, "w", encoding="utf-8") as fh:
            fh.write(json_output)
        click.echo(f"Report written to: {output}")
    else:
        click.echo(json_output)

    click.echo(
        f"\nSummary: {exact_count} exact, {near_count} near-match, "
        f"{not_found_count} not found, {empty_count} empty."
    )
    if not_found_count:
        click.echo(
            "Review not-found spans manually. The LLM may have paraphrased "
            "or fabricated these quotes."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
