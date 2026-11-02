#!/usr/bin/env python3
"""
Compile the EcoSKOS stopgap vocabulary from TSV to SKOS Turtle and HTML.

EcoSKOS holds terms that annotators need for CausalNode.entity_term (and the
other free-text term slots) but that no ontology has yet. It is also the
worklist of terms to request upstream: a term leaves the list when its status
becomes `mapped`, and is kept as a deprecated record if it is withdrawn.

Source of truth:  vocab/ecoskos_terms.tsv   (edit this, in a spreadsheet or by hand)
Generated:        docs/ecoskos/ecoskos.ttl  (SKOS Turtle, committed)
                  docs/ecoskos/index.html   (human-readable page, committed)

Never hand-edit the generated files.

Columns (tab-separated, UTF-8, header row required):
  id            permanent ecoskos:NNNNNNN; never reused, renumbered or deleted
  label         preferred label
  definition    what the term means, in a sentence a curator could act on
  broader       CURIE of an existing ontology term (or an ecoskos id) that
                would be the parent; a hint to the ontology editors on placement
  status        proposed | requested | mapped | deprecated
  proposed_by   who proposed it
  proposed_on   date the term was added, YYYY-MM-DD
  source        where the need arose (paper, DOI, annotation run)
  request_url   (optional) the upstream issue or term request
  requested_on  (optional) date the upstream request was filed, YYYY-MM-DD
  mapped_to     (optional; required when status is mapped) the upstream CURIE
  mapping_type  (optional) exact | close | broad | narrow; default exact
  replaced_by   (optional; deprecated terms) CURIE of the replacing term
  synonyms      (optional) alternative labels, separated by |
  rationale     (optional) why the term is needed; used by term_request.py
  example_usage (optional) an annotation that needs the term; used by
                term_request.py

rationale and example_usage are working notes for upstream requests. They are
not published in the Turtle or the HTML.

CURIE prefixes are resolved from the `prefixes` block of causalmosaic.yaml, so
there is one prefix table. `ecoskos` itself is defined here.

Usage:
    python vocab/build_vocab.py              # validate, then write ttl + html
    python vocab/build_vocab.py --check      # validate; fail if outputs are stale
    python vocab/build_vocab.py --next-id    # print the next free id

Exit codes:
    0  ok
    1  validation failed, or (--check) generated files are out of date
    2  unreadable input or missing dependency
"""

from __future__ import annotations

import argparse
import csv
import datetime
import html
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = ROOT / "vocab" / "ecoskos_terms.tsv"
DEFAULT_SCHEMA = ROOT / "causalmosaic.yaml"
DEFAULT_TTL = ROOT / "docs" / "ecoskos" / "ecoskos.ttl"
DEFAULT_HTML = ROOT / "docs" / "ecoskos" / "index.html"

PREFIX = "ecoskos"
NAMESPACE = "https://w3id.org/ecoskos/"
ID_RE = re.compile(r"ecoskos:(\d{7})")
CURIE_RE = re.compile(r"([A-Za-z][A-Za-z0-9_]*):(\S+)")
SAFE_LOCAL_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_\-]*")

STATUSES = ("proposed", "requested", "mapped", "deprecated")
MAPPING_PREDICATES = {
    "exact": "skos:exactMatch",
    "close": "skos:closeMatch",
    "broad": "skos:broadMatch",
    "narrow": "skos:narrowMatch",
}
REQUIRED_COLUMNS = ["id", "label", "definition", "broader", "status",
                    "proposed_by", "proposed_on", "source"]
OPTIONAL_COLUMNS = ["request_url", "requested_on", "mapped_to", "mapping_type",
                    "replaced_by", "synonyms", "rationale", "example_usage"]
SEPARATOR = "|"

BASE_PREFIXES = {
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "dcterms": "http://purl.org/dc/terms/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
}

SCHEME_IRI = NAMESPACE
SCHEME_TITLE = "EcoSKOS: stopgap vocabulary for ecological evidence annotation"
SCHEME_DESCRIPTION = (
    "Terms that annotators need for ecological causal-evidence annotation "
    "(Causal Mosaic, CAMO) but that no ontology yet defines. Each term is a "
    "placeholder and a request: its broader term says where an ontology "
    "editor would place it, and it is mapped to the ontology term once one "
    "exists."
)

ANNOTATION_PROPERTIES = [
    ("status", "status",
     "Lifecycle of the term: proposed, requested (an upstream request is "
     "open), mapped (an ontology term now exists) or deprecated."),
    ("requestUrl", "request URL",
     "The upstream issue or term request for this concept."),
    ("proposedBy", "proposed by", "Who proposed the term."),
    ("requestedOn", "requested on",
     "The date the upstream request for this concept was filed."),
]


@dataclass
class Term:
    id: str
    label: str
    definition: str
    broader: str
    status: str
    proposed_by: str
    proposed_on: str
    source: str
    request_url: str = ""
    requested_on: str = ""
    mapped_to: str = ""
    mapping_type: str = ""
    replaced_by: str = ""
    synonyms: list[str] = field(default_factory=list)
    rationale: str = ""
    example_usage: str = ""
    row: int = 0

    @property
    def where(self) -> str:
        return f"row {self.row} ({self.id or 'no id'})"


# --------------------------------------------------------------------------
# prefixes and CURIEs
# --------------------------------------------------------------------------

def load_prefixes(schema_path: Path) -> dict[str, str]:
    import yaml

    schema = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
    prefixes = dict(schema.get("prefixes") or {})
    prefixes[PREFIX] = NAMESPACE
    return prefixes


def expand(curie: str, prefixes: dict[str, str]) -> str:
    prefix, local = curie.split(":", 1)
    return prefixes[prefix] + local


def turtle_name(curie: str, prefixes: dict[str, str], used: set[str]) -> str:
    """A prefixed name when the local part is safe in Turtle, else a full IRI."""
    prefix, local = curie.split(":", 1)
    if SAFE_LOCAL_RE.fullmatch(local):
        used.add(prefix)
        return curie
    return f"<{expand(curie, prefixes)}>"


# --------------------------------------------------------------------------
# reading and validating the source
# --------------------------------------------------------------------------

def read_terms(path: Path) -> tuple[list[Term], list[str]]:
    errors: list[str] = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        header = reader.fieldnames or []
        missing = [c for c in REQUIRED_COLUMNS if c not in header]
        unknown = [c for c in header if c not in REQUIRED_COLUMNS + OPTIONAL_COLUMNS]
        if missing:
            errors.append(f"header is missing columns: {missing}")
        if unknown:
            errors.append(f"header has unknown columns: {unknown}")
        if errors:
            return [], errors
        terms = []
        for number, record in enumerate(reader, start=1):
            if None in record:
                errors.append(f"row {number}: more cells than header columns")
                continue
            cells = {k: (v or "").strip() for k, v in record.items()}
            if not any(cells.values()):
                continue
            terms.append(Term(
                row=number,
                synonyms=[s.strip() for s in cells.get("synonyms", "").split(SEPARATOR)
                          if s.strip()],
                **{k: cells.get(k, "") for k in REQUIRED_COLUMNS + OPTIONAL_COLUMNS
                   if k != "synonyms"},
            ))
    return terms, errors


def validate(terms: list[Term], prefixes: dict[str, str]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    ids = {t.id for t in terms}

    def check_curie(term: Term, column: str, value: str) -> None:
        match = CURIE_RE.fullmatch(value)
        if not match or value.startswith(("http:", "https:")):
            errors.append(f"{term.where}: {column} {value!r} is not a CURIE (use prefix:id)")
            return
        prefix = match.group(1)
        if prefix not in prefixes:
            errors.append(
                f"{term.where}: {column} {value!r} uses prefix {prefix!r}, which is "
                "not declared in the prefixes block of causalmosaic.yaml"
            )
        elif prefix == PREFIX:
            if not ID_RE.fullmatch(value):
                errors.append(f"{term.where}: {column} {value!r} is not a valid ecoskos id")
            elif value not in ids:
                errors.append(f"{term.where}: {column} {value!r} is not a term in this file")

    seen: dict[str, Term] = {}
    for term in terms:
        for column in REQUIRED_COLUMNS:
            if not getattr(term, column):
                errors.append(f"{term.where}: {column} is empty")

        if term.id:
            if not ID_RE.fullmatch(term.id):
                errors.append(f"{term.where}: id must look like ecoskos:0000001")
            if term.id in seen:
                errors.append(
                    f"{term.where}: duplicate id (also row {seen[term.id].row})"
                )
            seen.setdefault(term.id, term)

        if term.status and term.status not in STATUSES:
            errors.append(
                f"{term.where}: status {term.status!r} not in {list(STATUSES)}"
            )
        if term.broader:
            check_curie(term, "broader", term.broader)
            if term.broader == term.id:
                errors.append(f"{term.where}: broader is the term itself")

        if term.status == "mapped" and not term.mapped_to:
            errors.append(f"{term.where}: status is mapped but mapped_to is empty")
        if term.mapped_to:
            check_curie(term, "mapped_to", term.mapped_to)
            if term.status != "mapped":
                warnings.append(
                    f"{term.where}: mapped_to is set but status is {term.status!r}; "
                    "no mapping is emitted until status is mapped"
                )
        if term.mapping_type and term.mapping_type not in MAPPING_PREDICATES:
            errors.append(
                f"{term.where}: mapping_type {term.mapping_type!r} not in "
                f"{list(MAPPING_PREDICATES)}"
            )
        if term.mapping_type and not term.mapped_to:
            warnings.append(f"{term.where}: mapping_type is set without mapped_to")
        if term.replaced_by:
            check_curie(term, "replaced_by", term.replaced_by)
            if term.status != "deprecated":
                warnings.append(
                    f"{term.where}: replaced_by is set but status is {term.status!r}; "
                    "it is only emitted for deprecated terms"
                )
        if term.status == "requested" and not term.request_url:
            warnings.append(f"{term.where}: status is requested but request_url is empty")
        if term.request_url and not term.request_url.startswith(("http://", "https://")):
            errors.append(f"{term.where}: request_url {term.request_url!r} is not a URL")

        dates = {}
        for column in ("proposed_on", "requested_on"):
            value = getattr(term, column)
            if not value:
                continue
            try:
                dates[column] = datetime.date.fromisoformat(value)
            except ValueError:
                errors.append(f"{term.where}: {column} {value!r} is not a YYYY-MM-DD date")
                continue
            if dates[column] > datetime.date.today():
                warnings.append(f"{term.where}: {column} {value} is in the future")
        if "proposed_on" in dates and "requested_on" in dates \
                and dates["requested_on"] < dates["proposed_on"]:
            warnings.append(f"{term.where}: requested_on is before proposed_on")
        if term.requested_on and not term.request_url:
            warnings.append(f"{term.where}: requested_on is set but request_url is empty")

    # parent chains among ecoskos terms must not loop
    by_id = {t.id: t for t in terms if t.id}
    for term in terms:
        chain, current = [], term
        while current and current.broader in by_id:
            if current.id in chain:
                errors.append(f"{term.where}: broader chain loops ({' > '.join(chain)})")
                break
            chain.append(current.id)
            current = by_id[current.broader]

    # labels and synonyms should not collide among live terms
    live = [t for t in terms if t.status != "deprecated"]
    labels: dict[str, Term] = {}
    for term in live:
        key = term.label.casefold()
        if key in labels:
            warnings.append(
                f"{term.where}: label {term.label!r} duplicates {labels[key].id}; "
                "if they mean the same thing, make one a synonym"
            )
        labels.setdefault(key, term)
    for term in live:
        for synonym in term.synonyms:
            other = labels.get(synonym.casefold())
            if other and other is not term:
                warnings.append(
                    f"{term.where}: synonym {synonym!r} is the label of {other.id}"
                )
    return errors, warnings


def existing_ids(ttl_path: Path) -> set[str]:
    if not ttl_path.exists():
        return set()
    text = ttl_path.read_text(encoding="utf-8")
    return {f"ecoskos:{m}" for m in re.findall(r"^ecoskos:(\d{7}) a skos:Concept", text, re.M)}


def next_id(terms: list[Term], ttl_path: Path) -> str:
    numbers = [int(i.split(":")[1]) for i in existing_ids(ttl_path)]
    numbers += [int(m.group(1)) for t in terms if (m := ID_RE.fullmatch(t.id))]
    return f"ecoskos:{max(numbers, default=0) + 1:07d}"


# --------------------------------------------------------------------------
# Turtle
# --------------------------------------------------------------------------

def literal(text: str, lang: str | None = "en") -> str:
    escaped = (text.replace("\\", "\\\\").replace('"', '\\"')
               .replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t"))
    return f'"{escaped}"' + (f"@{lang}" if lang else "")


def render_ttl(terms: list[Term], prefixes: dict[str, str]) -> str:
    used: set[str] = set()
    blocks = []

    for term in sorted(terms, key=lambda t: t.id):
        lines = [
            f"{term.id} a skos:Concept ;",
            f"    skos:inScheme <{SCHEME_IRI}> ;",
            f"    skos:prefLabel {literal(term.label)} ;",
        ]
        if term.synonyms:
            alt = " , ".join(literal(s) for s in term.synonyms)
            lines.append(f"    skos:altLabel {alt} ;")
        lines += [
            f"    skos:definition {literal(term.definition)} ;",
            f"    skos:broader {turtle_name(term.broader, prefixes, used)} ;",
            f"    {PREFIX}:status {literal(term.status, None)} ;",
            f"    {PREFIX}:proposedBy {literal(term.proposed_by, None)} ;",
            f'    dcterms:created "{term.proposed_on}"^^xsd:date ;',
            f"    dcterms:source {literal(term.source, None)} ;",
        ]
        if term.request_url:
            lines.append(f"    {PREFIX}:requestUrl {literal(term.request_url, None)}^^xsd:anyURI ;")
        if term.requested_on:
            lines.append(f'    {PREFIX}:requestedOn "{term.requested_on}"^^xsd:date ;')
        if term.status == "mapped":
            predicate = MAPPING_PREDICATES[term.mapping_type or "exact"]
            lines.append(f"    {predicate} {turtle_name(term.mapped_to, prefixes, used)} ;")
        if term.status == "deprecated":
            lines.append('    owl:deprecated "true"^^xsd:boolean ;')
            if term.replaced_by:
                lines.append(
                    f"    dcterms:isReplacedBy {turtle_name(term.replaced_by, prefixes, used)} ;"
                )
        lines[-1] = lines[-1][:-2] + " ."
        blocks.append("\n".join(lines))

    header = [f"@prefix {PREFIX}: <{NAMESPACE}> ."]
    header += [f"@prefix {p}: <{u}> ." for p, u in sorted(BASE_PREFIXES.items())]
    header += [f"@prefix {p}: <{prefixes[p]}> ."
               for p in sorted(used - {PREFIX} - set(BASE_PREFIXES))]

    scheme = "\n".join([
        f"<{SCHEME_IRI}> a skos:ConceptScheme ;",
        f"    dcterms:title {literal(SCHEME_TITLE)} ;",
        f"    dcterms:description {literal(SCHEME_DESCRIPTION)} ;",
        "    dcterms:license <https://creativecommons.org/publicdomain/zero/1.0/> .",
    ])

    props = []
    for local, label, comment in ANNOTATION_PROPERTIES:
        props.append("\n".join([
            f"{PREFIX}:{local} a owl:AnnotationProperty ;",
            f"    rdfs:label {literal(label)} ;",
            f"    rdfs:comment {literal(comment)} .",
        ]))

    banner = ("# Generated by vocab/build_vocab.py from vocab/ecoskos_terms.tsv. "
              "Do not edit by hand.")
    parts = [banner, "\n".join(header), scheme, "\n\n".join(props)]
    parts += blocks
    return "\n\n".join(parts) + "\n"


# --------------------------------------------------------------------------
# HTML
# --------------------------------------------------------------------------

STATUS_NOTES = {
    "proposed": "Needed, but no upstream request has been filed yet.",
    "requested": "An upstream request is open.",
    "mapped": "An ontology term now exists; use that instead.",
    "deprecated": "Withdrawn. Kept so existing annotations still resolve.",
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EcoSKOS vocabulary</title>
<style>
:root {
  --forest:#243F32; --sage:#8BAD8C; --mint:#8FBF9F; --cream:#E8DDD0;
  --tan:#D4C4A0; --charcoal:#373535; --burgundy:#7A2D3A;
  --bg:#F6F1EA; --card:#FFFFFF; --text:#373535; --muted:#6B6663;
  --line:#D9CFC1; --link:#243F32; --accent:#243F32;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg:#1B2B23; --card:#243F32; --text:#E8DDD0; --muted:#A9B9AC;
    --line:#3A5A49; --link:#8FBF9F; --accent:#8FBF9F;
  }
}
:root[data-theme="dark"] {
  --bg:#1B2B23; --card:#243F32; --text:#E8DDD0; --muted:#A9B9AC;
  --line:#3A5A49; --link:#8FBF9F; --accent:#8FBF9F;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font:16px/1.5 system-ui,-apple-system,sans-serif}
main{max-width:860px;margin:0 auto;padding:2rem 16px 4rem}
h1{font-size:1.7rem;margin:0 0 .25rem}
a{color:var(--link)}
.lede{color:var(--muted);margin:0 0 1.5rem}
.meta{font-size:.9rem;color:var(--muted);margin:0 0 1.5rem}
.legend{display:grid;gap:.4rem;margin:0 0 1.5rem;padding:0;list-style:none;font-size:.9rem}
.controls{display:flex;flex-wrap:wrap;gap:.5rem;margin:0 0 1rem}
input,select{font:inherit;padding:.45rem .6rem;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--text)}
input{flex:1 1 220px}
.count{color:var(--muted);font-size:.9rem;margin:0 0 .75rem}
article{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:1rem 1.1rem;margin:0 0 .75rem}
article h2{font-size:1.1rem;margin:0 0 .15rem;display:flex;flex-wrap:wrap;gap:.5rem;align-items:baseline}
article.deprecated h2 .label{text-decoration:line-through}
.id{font:.8rem ui-monospace,Consolas,monospace;color:var(--muted)}
.badge{font-size:.72rem;font-weight:700;letter-spacing:.03em;text-transform:uppercase;padding:.1rem .45rem;border-radius:99px;border:1px solid currentColor}
.badge.proposed{color:#8A6D1F}.badge.requested{color:#2F6B8F}.badge.mapped{color:#2E7D4F}.badge.deprecated{color:var(--burgundy)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .badge.proposed{color:#E0C264}:root:not([data-theme="light"]) .badge.requested{color:#7DB8DB}:root:not([data-theme="light"]) .badge.mapped{color:#8FD1A8}:root:not([data-theme="light"]) .badge.deprecated{color:#E59AA6}}
.syn{color:var(--muted);font-size:.9rem;margin:0 0 .5rem}
.def{margin:.5rem 0}
dl{display:grid;grid-template-columns:max-content 1fr;gap:.2rem .9rem;margin:.5rem 0 0;font-size:.9rem}
dt{color:var(--muted)}dd{margin:0;overflow-wrap:anywhere}
footer{margin-top:2rem;color:var(--muted);font-size:.85rem}
</style>
</head>
<body>
<main>
<h1>EcoSKOS</h1>
<p class="lede">Stopgap terms for ecological evidence annotation, for use where no ontology term exists yet.</p>
<p class="meta">Scheme <code>@@NAMESPACE@@</code> &middot; @@TOTAL@@ terms &middot; <a href="ecoskos.ttl">Turtle</a> &middot; CC0 &middot; part of the <a href="https://github.com/timalamenciak/causalmosaic">Causal Mosaic schema</a></p>
<p>Use <code>entity_term: ecoskos:NNNNNNN</code> when you cannot find the concept in an ontology. Each term records where an ontology editor would place it (its broader term) and is mapped to the ontology term once one exists.</p>
<ul class="legend">
@@LEGEND@@
</ul>
<div class="controls">
<input id="q" type="search" placeholder="Search labels, synonyms, definitions" aria-label="Search terms">
<select id="s" aria-label="Filter by status"><option value="">All statuses</option>@@OPTIONS@@</select>
</div>
<p class="count" id="count"></p>
<section id="terms">
@@TERMS@@
</section>
<footer>Generated from <code>vocab/ecoskos_terms.tsv</code> by <code>vocab/build_vocab.py</code>. Do not edit by hand.</footer>
</main>
<script>
(function () {
  var q = document.getElementById('q'), s = document.getElementById('s');
  var items = Array.prototype.slice.call(document.querySelectorAll('#terms article'));
  var count = document.getElementById('count');
  function apply() {
    var needle = q.value.trim().toLowerCase(), status = s.value, shown = 0;
    items.forEach(function (el) {
      var ok = (!status || el.dataset.status === status) &&
               (!needle || el.dataset.text.indexOf(needle) !== -1);
      el.hidden = !ok;
      if (ok) shown++;
    });
    count.textContent = shown + ' of ' + items.length + ' terms shown';
  }
  q.addEventListener('input', apply);
  s.addEventListener('change', apply);
  apply();
})();
</script>
</body>
</html>
"""


def render_html(ttl_text: str) -> str:
    """Render the page from the Turtle, so the page can only show what was published."""
    from rdflib import Graph, Literal, URIRef
    from rdflib.namespace import DCTERMS, OWL, SKOS

    graph = Graph()
    graph.parse(data=ttl_text, format="turtle")
    eco = lambda name: URIRef(NAMESPACE + name)  # noqa: E731
    namespaces = sorted(
        ((str(ns), p) for p, ns in graph.namespaces() if str(ns)),
        key=lambda pair: -len(pair[0]),
    )

    def curie(iri) -> str:
        for ns, prefix in namespaces:
            if str(iri).startswith(ns) and prefix:
                return f"{prefix}:{str(iri)[len(ns):]}"
        return str(iri)

    def link(iri) -> str:
        return f'<a href="{html.escape(str(iri))}">{html.escape(curie(iri))}</a>'

    def one(subject, predicate) -> str:
        value = graph.value(subject, predicate)
        return str(value) if value is not None else ""

    concepts = sorted(graph.subjects(None, SKOS.Concept), key=str)
    cards, counts = [], {s: 0 for s in STATUSES}
    for concept in concepts:
        local = str(concept)[len(NAMESPACE):]
        label = one(concept, SKOS.prefLabel)
        synonyms = sorted(str(o) for o in graph.objects(concept, SKOS.altLabel))
        definition = one(concept, SKOS.definition)
        status = one(concept, eco("status"))
        counts[status] = counts.get(status, 0) + 1

        rows = []
        for parent in graph.objects(concept, SKOS.broader):
            rows.append(("Broader", link(parent)))
        for name, predicate in (("Exact match", SKOS.exactMatch), ("Close match", SKOS.closeMatch),
                                ("Broad match", SKOS.broadMatch), ("Narrow match", SKOS.narrowMatch)):
            for target in graph.objects(concept, predicate):
                rows.append((name, link(target)))
        for target in graph.objects(concept, DCTERMS.isReplacedBy):
            rows.append(("Replaced by", link(target)))
        request = one(concept, eco("requestUrl"))
        if request:
            rows.append(("Upstream request", f'<a href="{html.escape(request)}">{html.escape(request)}</a>'))
        proposed = html.escape(one(concept, eco("proposedBy")))
        created = one(concept, DCTERMS.created)
        rows.append(("Proposed", f"{proposed}, {html.escape(created)}" if created else proposed))
        source = one(concept, DCTERMS.source)
        source_html = html.escape(source)
        if source.startswith(("http://", "https://")):
            source_html = f'<a href="{source_html}">{source_html}</a>'
        rows.append(("Source", source_html))

        search = " ".join([local, label, definition, *synonyms]).lower()
        deprecated = (concept, OWL.deprecated, Literal(True)) in graph
        classes = " deprecated" if deprecated else ""
        syn_html = (f'<p class="syn">Also: {html.escape(", ".join(synonyms))}</p>'
                    if synonyms else "")
        details = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows)
        cards.append(
            f'<article id="{local}" class="{classes.strip()}" data-status="{html.escape(status)}" '
            f'data-text="{html.escape(search, quote=True)}">\n'
            f'<h2><span class="label">{html.escape(label)}</span>'
            f'<span class="badge {html.escape(status)}">{html.escape(status)}</span>'
            f'<a class="id" href="#{local}">ecoskos:{local}</a></h2>\n'
            f'{syn_html}<p class="def">{html.escape(definition)}</p>\n'
            f'<dl>{details}</dl>\n</article>'
        )

    legend = "\n".join(
        f'<li><span class="badge {s}">{s}</span> {html.escape(STATUS_NOTES[s])} ({counts.get(s, 0)})</li>'
        for s in STATUSES
    )
    options = "".join(f'<option value="{s}">{s}</option>' for s in STATUSES)
    empty = '<p class="count">No terms yet.</p>' if not cards else ""
    return (HTML_TEMPLATE
            .replace("@@NAMESPACE@@", html.escape(NAMESPACE))
            .replace("@@TOTAL@@", str(len(concepts)))
            .replace("@@LEGEND@@", legend)
            .replace("@@OPTIONS@@", options)
            .replace("@@TERMS@@", "\n".join(cards) + empty))


# --------------------------------------------------------------------------

def say(message: str = "", stream=None) -> None:
    print(message, file=stream or sys.stdout)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA,
                        help="schema whose prefixes block resolves CURIEs")
    parser.add_argument("--ttl", type=Path, default=DEFAULT_TTL)
    parser.add_argument("--html", type=Path, default=DEFAULT_HTML)
    parser.add_argument("--check", action="store_true",
                        help="validate and fail if the generated files are stale; write nothing")
    parser.add_argument("--next-id", action="store_true",
                        help="print the next unused id and exit")
    args = parser.parse_args(argv[1:])

    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(errors="replace")

    try:
        import rdflib  # noqa: F401
        import yaml  # noqa: F401
    except ImportError as exc:
        say(f"missing dependency: {exc.name} (pip install pyyaml rdflib)", sys.stderr)
        return 2

    try:
        prefixes = load_prefixes(args.schema)
        terms, errors = read_terms(args.source)
    except (OSError, UnicodeDecodeError) as exc:
        say(f"cannot read input: {exc}", sys.stderr)
        return 2

    if args.next_id:
        say(next_id(terms, args.ttl))
        return 0

    if not errors:
        more_errors, warnings = validate(terms, prefixes)
        errors += more_errors
    else:
        warnings = []

    # An id that was ever published must stay in the source, deprecated if need be.
    vanished = sorted(existing_ids(args.ttl) - {t.id for t in terms})
    for term_id in vanished:
        errors.append(
            f"{term_id} is in {args.ttl.name} but not in the source. Ids are never "
            "reused or removed: restore the row, or set its status to deprecated."
        )

    for message in warnings:
        say(f"  WARN  {message}", sys.stderr)
    if errors:
        for message in errors:
            say(f"  FAIL  {message}", sys.stderr)
        say(f"\n{len(errors)} error(s), {len(warnings)} warning(s); nothing written.", sys.stderr)
        return 1

    ttl_text = render_ttl(terms, prefixes)
    try:
        html_text = render_html(ttl_text)
    except Exception as exc:  # rdflib raises several parse error types
        say(f"generated Turtle does not parse: {exc}", sys.stderr)
        return 1

    outputs = [(args.ttl, ttl_text), (args.html, html_text)]
    if args.check:
        stale = [p for p, text in outputs
                 if not p.exists() or p.read_text(encoding="utf-8") != text]
        if stale:
            for p in stale:
                say(f"  FAIL  {p} is out of date; run: python vocab/build_vocab.py", sys.stderr)
            return 1
        say(f"ok: {len(terms)} terms, generated files current ({len(warnings)} warning(s))")
        return 0

    for path, text in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        say(f"wrote {path}")
    say(f"{len(terms)} terms ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
