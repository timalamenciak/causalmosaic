"""
validate_curies.py — Ontology CURIE Validator for Causal Mosaic YAML

Extracts every ontology CURIE from a Causal Mosaic 0.4 YAML file, validates
each against the appropriate external API, and reports which are valid,
invalid, or mismatched. See Annotation Guide Appendix A.4.3, Tool 1.

Usage:
    python validate_curies.py draft.yaml
    python validate_curies.py draft.yaml --output report.json
    python validate_curies.py draft.yaml --dry-run   # list CURIEs without API calls

Supported ontology prefixes:
    NCBITaxon  — NCBI E-utilities (Taxonomy database)
    ENVO       — OLS4 API
    GO         — OLS4 API
    PATO       — OLS4 API
    CHEBI      — OLS4 API
    ELMO       — OLS4 API (best-effort; namespace may not be in OLS)
    RO         — OLS4 API
    OBI        — OLS4 API
    ECO        — OLS4 API
    BFO        — OLS4 API

Rate limits:
    NCBI: max 3 requests/second (10/s with an API key set in NCBI_API_KEY env var)
    OLS4: max 10 requests/second
"""

import json
import os
import re
import sys
import time
from typing import Optional

import click
import requests
import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

OLS4_BASE = "https://www.ebi.ac.uk/ols4/api"
NCBI_ESUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
NCBI_ESEARCH  = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

# OLS4 ontology short names keyed by CURIE prefix
OLS_ONTOLOGY_MAP = {
    "ENVO":      "envo",
    "GO":        "go",
    "PATO":      "pato",
    "CHEBI":     "chebi",
    "RO":        "ro",
    "OBI":       "obi",
    "ECO":       "eco",
    "BFO":       "bfo",
    "SEPIO":     "sepio",
    "ELMO":      "elmo",      # may not be in OLS; will fall through gracefully
    "elmo":      "elmo",
    "elmo_cas":  "elmo",
}

# CURIE fields to extract from nodes (list of dot-path strings or plain keys)
NODE_CURIE_FIELDS = [
    "entity_term",
    "variable_attribute",
    "ecosystem_context",   # list
    "process_context",     # list
    "conditioned_by",      # list
]

# CURIE fields to extract from edges
EDGE_CURIE_FIELDS = [
    "ecosystem_context",   # single or list
    "process_context",
    "conditioned_by",      # list
]

CURIE_PATTERN = re.compile(r"^([A-Za-z][A-Za-z0-9_]*):\S+$")


# ---------------------------------------------------------------------------
# CURIE extraction
# ---------------------------------------------------------------------------

def _is_curie(value: str) -> bool:
    """Return True if value looks like an ontology CURIE (prefix:localpart)."""
    return bool(CURIE_PATTERN.match(str(value)))


def _collect_curies_from_value(value, source_path: str, curies: dict):
    """Recursively walk a value and collect CURIEs keyed by source path."""
    if isinstance(value, str) and _is_curie(value):
        curies.setdefault(value, []).append(source_path)
    elif isinstance(value, list):
        for i, item in enumerate(value):
            _collect_curies_from_value(item, f"{source_path}[{i}]", curies)
    elif isinstance(value, dict):
        for k, v in value.items():
            _collect_curies_from_value(v, f"{source_path}.{k}", curies)


def extract_curies(doc: dict) -> dict[str, list[str]]:
    """Return {curie: [source_path, ...]} for every ontology CURIE in the doc."""
    curies: dict[str, list[str]] = {}

    for i, node in enumerate(doc.get("nodes", [])):
        nid = node.get("id", f"nodes[{i}]")
        for field in NODE_CURIE_FIELDS:
            if field in node:
                _collect_curies_from_value(node[field], f"{nid}.{field}", curies)
        # ontology_mappings list
        for j, mapping in enumerate(node.get("ontology_mappings", [])):
            if isinstance(mapping, dict) and "curie" in mapping:
                _collect_curies_from_value(
                    mapping["curie"], f"{nid}.ontology_mappings[{j}].curie", curies
                )

    for i, edge in enumerate(doc.get("edges", [])):
        eid = edge.get("id", f"edges[{i}]")
        for field in EDGE_CURIE_FIELDS:
            if field in edge:
                _collect_curies_from_value(edge[field], f"{eid}.{field}", curies)
        # mediator / moderator node_ids — these are node IDs, not CURIEs, skip them
        # but check mediation/moderation sub-objects for any ontology fields
        for sub in ("mediation", "moderation"):
            if sub in edge and isinstance(edge[sub], dict):
                for k, v in edge[sub].items():
                    if k not in ("mediator_node_ids", "moderator_node_ids"):
                        _collect_curies_from_value(v, f"{eid}.{sub}.{k}", curies)

    return curies


def split_curie(curie: str) -> tuple[str, str]:
    """Split 'PREFIX:localpart' into (PREFIX, localpart)."""
    parts = curie.split(":", 1)
    return (parts[0], parts[1]) if len(parts) == 2 else (curie, "")


# ---------------------------------------------------------------------------
# API validation
# ---------------------------------------------------------------------------

def _ncbi_api_key_params() -> dict:
    key = os.environ.get("NCBI_API_KEY", "")
    return {"api_key": key} if key else {}


def validate_ncbi_taxon(local_id: str, label_hint: str, session: requests.Session) -> dict:
    """Validate an NCBITaxon CURIE via NCBI E-utilities."""
    params = {
        "db": "taxonomy",
        "id": local_id,
        "retmode": "json",
        **_ncbi_api_key_params(),
    }
    try:
        resp = session.get(NCBI_ESUMMARY, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, json.JSONDecodeError) as exc:
        return {"valid": False, "canonical_label": None, "error": str(exc)}

    result_dict = data.get("result", {})
    uid_list = result_dict.get("uids", [])
    if not uid_list or local_id not in uid_list:
        return {"valid": False, "canonical_label": None, "error": "ID not found in NCBI Taxonomy"}

    entry = result_dict.get(local_id, {})
    canonical_label = entry.get("scientificname") or entry.get("commonname") or None
    return {"valid": True, "canonical_label": canonical_label, "error": None}


def validate_ols(prefix: str, local_id: str, ontology_key: str,
                 label_hint: str, session: requests.Session) -> dict:
    """Validate an OLS4 CURIE by looking up the OBO-format IRI."""
    # Build the IRI: e.g., ENVO:01000335 → http://purl.obolibrary.org/obo/ENVO_01000335
    obo_id = f"{prefix}_{local_id}"
    iri = f"http://purl.obolibrary.org/obo/{obo_id}"
    encoded_iri = requests.utils.quote(iri, safe="")
    url = f"{OLS4_BASE}/ontologies/{ontology_key}/terms/{encoded_iri}"

    try:
        resp = session.get(url, timeout=10)
        if resp.status_code == 404:
            # Try without restricting to a specific ontology
            url_any = f"{OLS4_BASE}/terms/{encoded_iri}"
            resp = session.get(url_any, timeout=10)
        if resp.status_code == 404:
            return {"valid": False, "canonical_label": None,
                    "error": f"IRI {iri!r} not found in OLS4"}
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, json.JSONDecodeError) as exc:
        return {"valid": False, "canonical_label": None, "error": str(exc)}

    # OLS4 may return a list under _embedded.terms or a single term
    if "_embedded" in data:
        terms = data["_embedded"].get("terms", [])
        canonical_label = terms[0].get("label") if terms else None
    else:
        canonical_label = data.get("label")

    return {"valid": True, "canonical_label": canonical_label, "error": None}


def validate_curie(curie: str, label_hint: str,
                   session: requests.Session) -> dict:
    """Validate a single CURIE and return a result dict."""
    prefix, local_id = split_curie(curie)

    if prefix == "NCBITaxon":
        result = validate_ncbi_taxon(local_id, label_hint, session)
    elif prefix in OLS_ONTOLOGY_MAP:
        ontology_key = OLS_ONTOLOGY_MAP[prefix]
        result = validate_ols(prefix, local_id, ontology_key, label_hint, session)
    elif prefix in {"node", "edge", "example", "causal_mosaic",
                    "elmo_cas", "orcid", "doi", "llm"}:
        # Internal / non-ontology prefixes — skip silently
        return {
            "curie": curie,
            "valid": True,
            "canonical_label": None,
            "label_in_yaml": label_hint,
            "label_match": None,
            "error": None,
            "note": "internal prefix — not validated against external API",
        }
    else:
        return {
            "curie": curie,
            "valid": None,
            "canonical_label": None,
            "label_in_yaml": label_hint,
            "label_match": None,
            "error": None,
            "note": f"prefix {prefix!r} not supported — skipped",
        }

    canonical_label = result.get("canonical_label")
    label_match: Optional[bool] = None
    if canonical_label and label_hint:
        label_match = label_hint.lower() in canonical_label.lower() or \
                      canonical_label.lower() in label_hint.lower()

    return {
        "curie": curie,
        "valid": result["valid"],
        "canonical_label": canonical_label,
        "label_in_yaml": label_hint,
        "label_match": label_match,
        "error": result.get("error"),
        "suggested_curie": None,
    }


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


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.command()
@click.argument("yaml_file", type=click.Path(exists=True))
@click.option("--output", "-o", default=None,
              help="Write JSON report to this file (default: print to stdout).")
@click.option("--dry-run", is_flag=True, default=False,
              help="List extracted CURIEs without making API calls.")
@click.option("--verbose", "-v", is_flag=True, default=False,
              help="Print each CURIE as it is validated.")
def main(yaml_file, output, dry_run, verbose):
    """Validate all ontology CURIEs in a Causal Mosaic YAML file.

    Checks NCBITaxon CURIEs via NCBI E-utilities and ENVO/GO/PATO/CHEBI/etc.
    CURIEs via the OLS4 API. Outputs a JSON validation report.

    Set NCBI_API_KEY environment variable to raise NCBI rate limit to 10/s.
    """
    with open(yaml_file, encoding="utf-8") as fh:
        try:
            doc = yaml.safe_load(fh)
        except yaml.YAMLError as exc:
            click.echo(f"ERROR: Could not parse YAML: {exc}", err=True)
            sys.exit(1)

    if not isinstance(doc, dict):
        click.echo("ERROR: Top-level document is not a YAML mapping.", err=True)
        sys.exit(1)

    curies = extract_curies(doc)

    if dry_run:
        click.echo(f"Found {len(curies)} unique CURIE(s):")
        for curie, paths in sorted(curies.items()):
            click.echo(f"  {curie}  (used in: {', '.join(paths[:3])}{'...' if len(paths) > 3 else ''})")
        return

    has_ncbi = any(split_curie(c)[0] == "NCBITaxon" for c in curies)
    has_ols  = any(split_curie(c)[0] in OLS_ONTOLOGY_MAP for c in curies)

    ncbi_limiter = RateLimiter(3.0 if not os.environ.get("NCBI_API_KEY") else 10.0)
    ols_limiter  = RateLimiter(10.0)

    results = []
    session = requests.Session()
    session.headers["User-Agent"] = "causal-mosaic-validator/0.4.0 (ecology annotation tool)"

    click.echo(f"Validating {len(curies)} unique CURIE(s)...")

    for curie, paths in sorted(curies.items()):
        prefix, _ = split_curie(curie)
        if prefix == "NCBITaxon":
            ncbi_limiter.wait()
        elif prefix in OLS_ONTOLOGY_MAP:
            ols_limiter.wait()

        # Use the first source path as a label hint (field name or nearby text)
        label_hint = paths[0].split(".")[-1] if paths else ""

        if verbose:
            click.echo(f"  Checking {curie} ... ", nl=False)

        result = validate_curie(curie, label_hint, session)
        result["source_paths"] = paths
        results.append(result)

        if verbose:
            status = "OK" if result["valid"] else ("SKIP" if result["valid"] is None else "FAIL")
            click.echo(status)

    # Summary
    valid_count   = sum(1 for r in results if r["valid"] is True)
    invalid_count = sum(1 for r in results if r["valid"] is False)
    skipped_count = sum(1 for r in results if r["valid"] is None)

    report = {
        "summary": {
            "total": len(results),
            "valid": valid_count,
            "invalid": invalid_count,
            "skipped": skipped_count,
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
        f"\nSummary: {valid_count} valid, {invalid_count} invalid, {skipped_count} skipped."
    )
    if invalid_count:
        click.echo("Review invalid CURIEs with lookup_curie.py to find correct identifiers.")
        sys.exit(1)


if __name__ == "__main__":
    main()
