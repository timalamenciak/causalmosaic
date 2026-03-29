"""
lookup_curie.py — Ontology Label-to-CURIE Lookup for Causal Mosaic

Searches ontology APIs for terms matching a natural-language label and returns
the top candidate CURIEs. Used to find correct identifiers when the LLM leaves
a CURIE blank or when validate_curies.py flags one as invalid.
See Annotation Guide Appendix A.4.3, Tool 2.

Usage:
    # Single lookup
    python lookup_curie.py "Andropogon gerardii" NCBITaxon
    python lookup_curie.py "temperate grassland" ENVO
    python lookup_curie.py "abundance" PATO

    # Batch mode (TSV with columns: label<TAB>prefix)
    python lookup_curie.py --batch labels.tsv --output results.tsv

Supported prefixes: NCBITaxon, ENVO, GO, PATO, CHEBI, RO, OBI, ECO, BFO, ELMO
"""

import csv
import io
import json
import os
import sys
import time

import click
import requests

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

OLS4_SEARCH = "https://www.ebi.ac.uk/ols4/api/search"
NCBI_ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
NCBI_ESUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

OLS_ONTOLOGY_MAP = {
    "ENVO":  "envo",
    "GO":    "go",
    "PATO":  "pato",
    "CHEBI": "chebi",
    "RO":    "ro",
    "OBI":   "obi",
    "ECO":   "eco",
    "BFO":   "bfo",
    "SEPIO": "sepio",
    "ELMO":  "elmo",
}

VALID_PREFIXES = {"NCBITaxon"} | set(OLS_ONTOLOGY_MAP.keys())

# Simple in-memory cache: (label, prefix) → results list
_CACHE: dict[tuple[str, str], list[dict]] = {}


# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------

class RateLimiter:
    def __init__(self, calls_per_second: float):
        self.interval = 1.0 / calls_per_second
        self._last = 0.0

    def wait(self):
        elapsed = time.monotonic() - self._last
        sleep_for = self.interval - elapsed
        if sleep_for > 0:
            time.sleep(sleep_for)
        self._last = time.monotonic()


_ncbi_limiter = RateLimiter(3.0 if not os.environ.get("NCBI_API_KEY") else 10.0)
_ols_limiter  = RateLimiter(10.0)


# ---------------------------------------------------------------------------
# Search implementations
# ---------------------------------------------------------------------------

def _ncbi_api_key_params() -> dict:
    key = os.environ.get("NCBI_API_KEY", "")
    return {"api_key": key} if key else {}


def search_ncbi_taxon(label: str, top_n: int, session: requests.Session) -> list[dict]:
    """Search NCBI Taxonomy for a label and return up to top_n results."""
    _ncbi_limiter.wait()
    search_params = {
        "db": "taxonomy",
        "term": label,
        "retmode": "json",
        "retmax": top_n,
        **_ncbi_api_key_params(),
    }
    try:
        resp = session.get(NCBI_ESEARCH, params=search_params, timeout=10)
        resp.raise_for_status()
        search_data = resp.json()
    except (requests.RequestException, json.JSONDecodeError) as exc:
        return [{"error": str(exc)}]

    ids = search_data.get("esearchresult", {}).get("idlist", [])
    if not ids:
        return []

    _ncbi_limiter.wait()
    summary_params = {
        "db": "taxonomy",
        "id": ",".join(ids[:top_n]),
        "retmode": "json",
        **_ncbi_api_key_params(),
    }
    try:
        resp2 = session.get(NCBI_ESUMMARY, params=summary_params, timeout=10)
        resp2.raise_for_status()
        summary_data = resp2.json()
    except (requests.RequestException, json.JSONDecodeError) as exc:
        return [{"error": str(exc)}]

    results = []
    result_dict = summary_data.get("result", {})
    for uid in ids[:top_n]:
        entry = result_dict.get(uid, {})
        if not entry:
            continue
        canonical = entry.get("scientificname") or entry.get("commonname") or "(unknown)"
        results.append({
            "curie": f"NCBITaxon:{uid}",
            "canonical_label": canonical,
            "definition": entry.get("division", ""),
            "match_score": 1.0 if canonical.lower() == label.lower() else 0.5,
        })
    return results


def search_ols(label: str, prefix: str, top_n: int, session: requests.Session) -> list[dict]:
    """Search OLS4 for a label within the specified ontology."""
    ontology_key = OLS_ONTOLOGY_MAP.get(prefix)
    _ols_limiter.wait()

    params: dict = {
        "q": label,
        "rows": top_n,
        "type": "class",
    }
    if ontology_key:
        params["ontology"] = ontology_key

    try:
        resp = session.get(OLS4_SEARCH, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, json.JSONDecodeError) as exc:
        return [{"error": str(exc)}]

    docs = data.get("response", {}).get("docs", [])
    results = []
    for doc in docs[:top_n]:
        obo_id = doc.get("obo_id", "") or doc.get("short_form", "")
        if not obo_id:
            continue
        # Normalise to CURIE form: ENVO_01000335 → ENVO:01000335
        curie = obo_id.replace("_", ":", 1) if "_" in obo_id else obo_id
        canonical = doc.get("label", "")
        definition_list = doc.get("description", [])
        definition = definition_list[0] if definition_list else ""
        score = doc.get("score", 0)
        results.append({
            "curie": curie,
            "canonical_label": canonical,
            "definition": definition[:200] if definition else "",
            "match_score": float(score) if score else 0.0,
        })
    return results


def lookup(label: str, prefix: str, top_n: int,
           session: requests.Session) -> list[dict]:
    """Look up a label in the appropriate ontology API.

    Returns a list of up to top_n result dicts with keys:
        curie, canonical_label, definition, match_score
    Results are cached for the session.
    """
    cache_key = (label.lower(), prefix.upper())
    if cache_key in _CACHE:
        return _CACHE[cache_key]

    prefix_upper = prefix.upper() if prefix != "NCBITaxon" else prefix
    if prefix_upper == "NCBITaxon" or prefix == "NCBITaxon":
        results = search_ncbi_taxon(label, top_n, session)
    elif prefix_upper in OLS_ONTOLOGY_MAP:
        results = search_ols(label, prefix_upper, top_n, session)
    else:
        results = [{"error": f"Unsupported prefix: {prefix!r}. "
                              f"Supported: {sorted(VALID_PREFIXES)}"}]

    _CACHE[cache_key] = results
    return results


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def format_results_text(label: str, prefix: str, results: list[dict]) -> str:
    """Format results as a human-readable text block."""
    lines = [f"Results for: {label!r}  (prefix: {prefix})"]
    if not results:
        lines.append("  (no results found)")
        return "\n".join(lines)
    for i, r in enumerate(results, start=1):
        if "error" in r:
            lines.append(f"  {i}. ERROR: {r['error']}")
            continue
        score_str = f"  score={r['match_score']:.2f}" if r.get("match_score") else ""
        lines.append(f"  {i}. {r['curie']}")
        lines.append(f"     Label: {r['canonical_label']}{score_str}")
        if r.get("definition"):
            defn = r["definition"]
            if len(defn) > 100:
                defn = defn[:97] + "..."
            lines.append(f"     Def:   {defn}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.command()
@click.argument("label", required=False)
@click.argument("prefix", required=False)
@click.option("--batch", "batch_file", default=None, type=click.Path(exists=True),
              help="TSV file with columns: label<TAB>prefix. Overrides LABEL and PREFIX arguments.")
@click.option("--output", "-o", default=None,
              help="Write TSV results to this file (batch mode) or JSON (single mode).")
@click.option("--top-n", "-n", default=5, show_default=True,
              help="Number of top results to return per query.")
@click.option("--json", "as_json", is_flag=True, default=False,
              help="Output in JSON format (single-lookup mode).")
def main(label, prefix, batch_file, output, top_n, as_json):
    """Look up an ontology term by natural-language label.

    Single mode:  python lookup_curie.py "label text" PREFIX
    Batch mode:   python lookup_curie.py --batch labels.tsv --output results.tsv

    Supported prefixes: NCBITaxon, ENVO, GO, PATO, CHEBI, RO, OBI, ECO, BFO, ELMO

    Set NCBI_API_KEY environment variable to raise NCBI rate limit to 10/s.
    """
    session = requests.Session()
    session.headers["User-Agent"] = "causal-mosaic-lookup/0.4.0 (ecology annotation tool)"

    if batch_file:
        _run_batch(batch_file, output, top_n, session)
    else:
        if not label or not prefix:
            click.echo("ERROR: Provide both LABEL and PREFIX, or use --batch.", err=True)
            sys.exit(1)
        results = lookup(label, prefix, top_n, session)
        if as_json:
            out = json.dumps(results, indent=2, ensure_ascii=False)
            if output:
                with open(output, "w", encoding="utf-8") as fh:
                    fh.write(out)
            else:
                click.echo(out)
        else:
            click.echo(format_results_text(label, prefix, results))


def _run_batch(batch_file: str, output: Optional[str], top_n: int,
               session: requests.Session):
    """Process a TSV file of (label, prefix) rows."""
    rows = []
    with open(batch_file, encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh, delimiter="\t")
        for line_no, row in enumerate(reader, start=1):
            if not row or row[0].startswith("#"):
                continue
            if len(row) < 2:
                click.echo(f"WARNING: line {line_no} has fewer than 2 columns — skipped", err=True)
                continue
            rows.append((row[0].strip(), row[1].strip()))

    click.echo(f"Processing {len(rows)} row(s) from {batch_file}...")

    all_results = []
    for label, prefix in rows:
        results = lookup(label, prefix, top_n, session)
        all_results.append((label, prefix, results))

    # Format output
    output_lines = ["label\tprefix\trank\tcurie\tcanonical_label\tmatch_score\tdefinition"]
    for label, prefix, results in all_results:
        if not results:
            output_lines.append(f"{label}\t{prefix}\t\t(no results)\t\t\t")
            continue
        for rank, r in enumerate(results, start=1):
            if "error" in r:
                output_lines.append(f"{label}\t{prefix}\t{rank}\tERROR\t{r['error']}\t\t")
            else:
                defn = (r.get("definition") or "").replace("\t", " ")[:150]
                output_lines.append(
                    f"{label}\t{prefix}\t{rank}\t{r['curie']}\t"
                    f"{r['canonical_label']}\t{r.get('match_score', '')}\t{defn}"
                )

    tsv_output = "\n".join(output_lines) + "\n"
    if output:
        with open(output, "w", encoding="utf-8", newline="") as fh:
            fh.write(tsv_output)
        click.echo(f"Results written to: {output}")
    else:
        click.echo(tsv_output)


# Allow Optional to be imported for type hints used in helpers
from typing import Optional

if __name__ == "__main__":
    main()
