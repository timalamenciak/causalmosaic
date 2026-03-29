"""
extract.py — Causal Mosaic LLM Extraction Tool

Stage 2 of the human-in-the-loop pipeline (see Annotation Guide Appendix A).
Sends source text to a configured LLM and returns a draft Causal Mosaic 0.4
YAML file for human review.

Usage:
    python extract.py --text paper.txt --output draft.yaml
    python extract.py --text paper.pdf --output draft.yaml   # PDF supported
    python extract.py --text paper.txt \\
        --doi "10.1234/example" --title "My Paper" \\
        --authors "Smith, J." --authors "Patel, K." --year 2024 \\
        --journal "Journal of Restoration Ecology" --output draft.yaml

LLM settings (model, endpoint URL, API key env var) are read from llm.yaml in
the same directory as this script. Edit llm.yaml before running.

IMPORTANT: The draft output MUST be reviewed by a human annotator.
Run validate_schema.py, validate_curies.py, and verify_spans.py first, then
manually check every field against the source paper.
"""

import sys
import textwrap
from pathlib import Path

import click
import yaml

# Local utilities (same directory)
sys.path.insert(0, str(Path(__file__).parent))
from utils import load_text, load_llm_config, make_llm_client, call_llm

# ---------------------------------------------------------------------------
# Default config path
# ---------------------------------------------------------------------------

DEFAULT_CONFIG = str(Path(__file__).parent / "llm.yaml")

# ---------------------------------------------------------------------------
# Extraction system prompt (Annotation Guide Appendix A.3)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = textwrap.dedent("""\
    You are an expert ecological evidence annotator. Your task is to extract causal
    claims from scientific text and produce structured annotations conforming to the
    Causal Mosaic schema (version 0.4.0). You will output valid YAML and nothing else.

    ## YOUR ROLE

    You are the FIRST PASS in a human-in-the-loop pipeline. A trained human annotator
    will review and correct every field you produce. Your goal is to be thorough (high
    recall — do not miss claims) and conservative (prefer `not_addressed` over guessing).

    ## CORE PRINCIPLES

    1. CAUSATION IS BETWEEN CHANGES IN STATE, NOT BETWEEN THINGS.
       Every node must decompose into: entity (what thing) + attribute (what measurable
       property) + direction (which way it changed). Never create a bare-entity node
       like "wolves" — always specify "increased/decreased [attribute] of [entity]."

    2. EXTRACT WHAT THE TEXT SAYS, NOT WHAT YOU KNOW.
       Your training data contains ecological knowledge. Do NOT use it to fill in
       features the paper does not discuss. If the paper does not mention mechanism,
       do not code mechanism as "well_characterized" just because you know the
       mechanism from your training. Code it as `not_addressed`.

    3. DEFAULT TO `not_addressed`.
       For all fifteen causal features, start with `not_addressed` and only change it
       when the text explicitly or clearly implicitly supports a different value.

    4. CLAIM STRENGTH TRACKS LANGUAGE, NOT EVIDENCE QUALITY.
       "associated with" → `associational`, even if the evidence is strong.
       "causes" → `direct_causal`, even if the evidence is weak.
       Code the author's words, not your assessment.

    5. SOURCE SPANS MUST BE VERBATIM.
       Every `text` field in source_spans must be an exact, character-for-character
       quotation from the provided source text. Do not paraphrase, summarize, or
       fabricate. If you cannot find an exact span, leave the text field empty and
       note this in `annotation_notes`.

    6. ONTOLOGY CURIES ARE DRAFTS.
       You do not have access to ontology databases. Provide your best guess for
       CURIEs using the prefixes below, but mark all ontology IDs with a confidence
       flag. The human reviewer will verify every CURIE.
       - Taxa: NCBITaxon:{id}
       - Environments: ENVO:{id}
       - Chemicals: CHEBI:{id}
       - Biological processes: GO:{id}
       - Qualities/attributes: PATO:{id}
       - ELMO terms: elmo:{id}

    7. FLAG UNCERTAINTY.
       Use the `annotation_notes` field on every edge to flag:
       - Any CURIE you are uncertain about (prefix with "VERIFY_CURIE:")
       - Any feature where you were unsure between two values (prefix with "UNCERTAIN:")
       - Any edge where you suspect the text might support an alternative interpretation
         (prefix with "ALT_INTERPRETATION:")

    ## OUTPUT FORMAT

    Produce a single YAML document with the following top-level structure.
    Output ONLY the YAML. No preamble. No commentary. No markdown fences.

    graph_id: "example:{document_slug}"
    schema_version: "0.4.0"
    provenance:
      source_corpus: "{1-2 sentence summary of what the paper studies}"
      project: "Causal Mosaic annotation"

    nodes:
      - id: "node:{snake_case_label}"
        name: "{Human-readable composed name, e.g. 'Increased light availability'}"
        description: "{Free-text description from paper}"
        entity_type: "{environmental_variable | environmental_process | management_intervention}"
        entity_term: "{CURIE — DRAFT, must be verified}"
        variable_attribute: "{PATO or similar CURIE for the measurable property — DRAFT}"
        variable_direction: "{increased | decreased | present | absent | introduced | removed | unchanged | unspecified}"
        ecosystem_context:
          - "{ENVO or ELMO CURIE for ecosystem type}"

    edges:
      - id: "edge:{source_slug}_to_{target_slug}"
        subject: "node:{source_slug}"
        predicate: "{see predicate vocabulary below}"
        object: "node:{target_slug}"

        claim_strength: "{no_relationship | associational | conditional_causal | direct_causal}"

        philosophical_accounts:
          - "{counterfactual | probabilistic | interventionist | variation | process | mechanistic | information_transmission | regularity | inus_component | capacity | agency}"
        account_families:
          - "{difference_making | production | complementary}"

        temporal_ordering: "not_addressed"
        direction:
          status: "{asserted | uncertain | bidirectional | not_addressed}"
          evidence_for_direction: "{experimental | temporal_precedence | theoretical | natural_experiment | structural_model}"
        mechanism:
          status: "{well_characterized | partially_characterized | not_addressed}"
          mechanism_description: ""
        mediation:
          status: "not_addressed"
          pathway_description: ""
        moderation:
          status: "not_addressed"
          interaction_type: "not_specified"
          notes: ""
        strength:
          status: "{explicitly_asserted | implicitly_assumed | not_addressed}"
          quantitative_value: ""
          quantitative_numeric: null
          qualitative_descriptor: "{strong | moderate | weak | negligible | not_specified}"
          dose_response: false
        context_dependence:
          status: "{explicitly_asserted | implicitly_assumed | not_addressed}"
          scope_conditions: []
          geographic_scope: ""
          temporal_scope: ""
          ecosystem_scope: ""
        necessity: "not_addressed"
        sufficiency: "not_addressed"
        specificity: "not_addressed"
        stability: "not_addressed"
        token_or_type: "not_addressed"
        determinism: "not_addressed"
        proximate_distal: "not_addressed"
        contributing_sole: "not_addressed"
        reversibility: "not_addressed"
        proportionality: "not_addressed"

        evidential_basis:
          evidence_types: []
          evidence_objects: []
          russo_williamson_satisfied: false
          bradford_hill_viewpoints: []
          bradford_hill_count: 0
          certainty_grade: "not_assessed"
          certainty_rationale: ""
          evidence_count: 0

        temporal_extent:
          duration_months: null
          duration_text: ""
          lag_months: null
          observation_grain: ""

        source_spans:
          - text: "{VERBATIM quote from paper — do NOT paraphrase}"
        source_document:
          doi: "{doi}"
          title: "{paper title}"
          authors: []
          year: null
          journal: ""
          section: ""

        annotator: "llm:{model}"
        annotation_confidence: 0.0
        annotation_notes: |
          {Flag uncertainties here. Use prefixes:
           VERIFY_CURIE: [any CURIE you're unsure about]
           UNCERTAIN: [any feature where you debated between values]
           ALT_INTERPRETATION: [alternative readings of the text]}

        fcm_weight: 0.0
        fcm_weight_source: "derived_from_schema"

    ## PREDICATE VOCABULARY (choose one per edge)

    | Predicate             | Sign | Use when...                                            |
    |-----------------------|------|--------------------------------------------------------|
    | causes                | +    | Direct, unhedged positive causation                    |
    | contributes_to        | +    | One of several contributing factors                    |
    | enables               | +    | Facilitates but not sufficient alone                   |
    | positively_regulates  | +    | Upregulates / increases                                |
    | associated_with       | ?    | Statistical association, no causal commitment          |
    | correlated_with       | ?    | Correlation without direction/causation                |
    | prevents              | −    | Inhibits / blocks / reduces                            |
    | disrupts              | −    | Degrades / suppresses                                  |
    | negatively_regulates  | −    | Downregulates / decreases                              |
    | regulates             | ±    | Modulates (direction unclear)                          |
    | mediates              | path | On the causal pathway between C and E                  |
    | moderates             | mod  | Modifies strength/direction of C→E                     |
    | precedes              | time | Temporal precedence only                               |

    ## PHILOSOPHICAL ACCOUNTS — LINGUISTIC CUE REFERENCE

    | Account                 | Family            | Look for these cues in the text                        |
    |-------------------------|-------------------|--------------------------------------------------------|
    | counterfactual          | difference_making | "without X"; "had X not occurred"; "in the absence of" |
    | probabilistic           | difference_making | "risk factor"; "odds ratio"; "associated with [+stats]" |
    | interventionist         | difference_making | "removal led to"; "treatment resulted in"; "experiment showed" |
    | variation               | difference_making | "R²"; "regression"; "variance explained"; "SEM"       |
    | process                 | production        | "energy transfer"; "nutrient flow"; "water transport"  |
    | mechanistic             | production        | "mechanism by which"; "pathway"; "step-by-step"        |
    | information_transmission| production        | "signal"; "biomarker"; "gene expression cascade"       |
    | regularity              | complementary     | "consistently observed"; "invariably"; "universal pattern" |
    | inus_component          | complementary     | "contributing factor"; "one of several causes"; "multifactorial" |
    | capacity                | complementary     | "capacity to"; "tendency to"; "competitive ability"    |
    | agency                  | complementary     | "managers can"; "restoration prescription"; "recommended" |

    ## EVIDENCE TYPES

    randomized_experiment | natural_experiment | quasi_experiment |
    observational_longitudinal | observational_cross_sectional | mechanistic_study |
    structural_equation_model | meta_analysis | systematic_review |
    modeling_simulation | expert_judgment | case_study | theoretical |
    indigenous_knowledge | practitioner_experience

    ## BRADFORD HILL VIEWPOINTS

    strength | consistency | specificity | temporality | biological_gradient |
    plausibility | coherence | experiment | analogy

    ## CERTAINTY GRADES

    high (experimental + mechanistic + replicated) |
    moderate (observational + mechanism, or experiment but limited) |
    low (single study or observational without mechanism) |
    very_low (weak evidence, no mechanism, conflicting results)
""")

USER_PROMPT_TEMPLATE = textwrap.dedent("""\
    ## SOURCE DOCUMENT METADATA

    DOI: {doi}
    Title: {title}
    Authors: {authors}
    Year: {year}
    Journal: {journal}

    ## INSTRUCTIONS

    1. Read the source text provided below carefully.
    2. Identify ALL causal claims, including direct causal statements, associational
       claims with statistical evidence, mechanistic pathway descriptions, competing
       or offsetting effects, and null results.
    3. For each claim, create the necessary nodes and an edge.
    4. Fill in all four annotation layers for each edge.
    5. Be thorough — extract every causal relationship you can find.
    6. Be conservative — default to `not_addressed` and only upgrade when the text supports it.
    7. Flag all uncertainties in `annotation_notes`.
    8. Output ONLY the YAML. No preamble. No commentary. No markdown fences.

    ## SOURCE TEXT TO ANNOTATE

    {text}
""")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.command()
@click.option("--text", "text_path", required=True, type=click.Path(exists=True),
              help="Path to the source document (.txt, .md, or .pdf).")
@click.option("--output", "-o", default="draft.yaml", show_default=True,
              help="Path to write the draft YAML output.")
@click.option("--config", "-c", default=DEFAULT_CONFIG, show_default=True,
              type=click.Path(exists=True),
              help="Path to llm.yaml configuration file.")
@click.option("--doi", default="", help="DOI of the source paper.")
@click.option("--title", default="", help="Title of the source paper.")
@click.option("--authors", multiple=True, default=[],
              help="Authors (repeat flag for multiple).")
@click.option("--year", default=None, type=int, help="Publication year.")
@click.option("--journal", default="", help="Journal name.")
@click.option("--chunk/--no-chunk", default=False, show_default=True,
              help="Split the text into ~3000-word chunks and merge outputs (for long papers).")
@click.option("--words-per-chunk", default=3000, show_default=True,
              help="Words per chunk when --chunk is set.")
def main(text_path, output, config, doi, title, authors, year, journal, chunk, words_per_chunk):
    """Extract Causal Mosaic annotations from a source document using an LLM.

    Accepts .txt, .md, or .pdf files. LLM settings are read from llm.yaml.

    Produces a draft YAML that MUST be reviewed by a human annotator.
    Next steps after running this script:

    \b
        python validate_schema.py draft.yaml
        python validate_curies.py draft.yaml
        python verify_spans.py   draft.yaml paper.txt
    """
    cfg = load_llm_config(config)
    provider, client = make_llm_client(cfg)

    click.echo(f"Provider : {cfg['provider']}")
    click.echo(f"Model    : {cfg['model']}")
    if cfg["provider"] == "openai_compatible":
        click.echo(f"Endpoint : {cfg['base_url']}")

    source_text = load_text(text_path)
    click.echo(f"Loaded   : {text_path}  ({len(source_text):,} characters)")

    if chunk:
        chunks = _split_into_chunks(source_text, words_per_chunk)
        click.echo(f"Chunked into {len(chunks)} part(s) of ~{words_per_chunk} words each.")
    else:
        chunks = [source_text]

    # Embed model name in the annotator field
    system = SYSTEM_PROMPT.replace("{model}", cfg["model"])

    all_outputs = []
    for i, chunk_text in enumerate(chunks, start=1):
        if len(chunks) > 1:
            click.echo(f"Processing chunk {i}/{len(chunks)}...")

        user_prompt = USER_PROMPT_TEMPLATE.format(
            doi=doi or "(not provided)",
            title=title or "(not provided)",
            authors=", ".join(authors) if authors else "(not provided)",
            year=year or "(not provided)",
            journal=journal or "(not provided)",
            text=chunk_text,
        )

        raw = call_llm(provider, client, cfg, system, user_prompt)
        raw = _strip_fences(raw)
        all_outputs.append(raw)

    final_yaml = all_outputs[0] if len(all_outputs) == 1 else _merge_chunks(all_outputs)

    with open(output, "w", encoding="utf-8") as fh:
        fh.write(final_yaml)

    click.echo(f"\nDraft YAML written to: {output}")
    click.echo("\nNEXT STEPS (human-in-the-loop review required):")
    click.echo(f"  1. python validate_schema.py {output}")
    click.echo(f"  2. python validate_curies.py {output}")
    click.echo(f"  3. python verify_spans.py    {output} {text_path}")
    click.echo("  4. Open the YAML and manually review every field.")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strip_fences(text: str) -> str:
    """Remove accidental markdown code fences from LLM output."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        end = len(lines) - 1 if lines[-1].strip() == "```" else len(lines)
        text = "\n".join(lines[1:end])
    return text


def _split_into_chunks(text: str, words_per_chunk: int) -> list[str]:
    words = text.split()
    return [
        " ".join(words[i : i + words_per_chunk])
        for i in range(0, len(words), words_per_chunk)
    ]


def _merge_chunks(yaml_outputs: list[str]) -> str:
    """Merge YAML chunks by combining nodes and edges lists."""
    import yaml as _yaml

    merged = {
        "graph_id": "",
        "schema_version": "0.4.0",
        "provenance": {},
        "nodes": [],
        "edges": [],
    }
    seen_node_ids: set[str] = set()
    seen_edge_ids: set[str] = set()

    for i, chunk_yaml in enumerate(yaml_outputs, start=1):
        try:
            doc = _yaml.safe_load(chunk_yaml)
        except _yaml.YAMLError as exc:
            click.echo(f"WARNING: chunk {i} could not be parsed as YAML: {exc}", err=True)
            continue
        if not isinstance(doc, dict):
            continue
        if not merged["graph_id"] and doc.get("graph_id"):
            merged["graph_id"] = doc["graph_id"]
        if not merged["provenance"] and doc.get("provenance"):
            merged["provenance"] = doc["provenance"]
        for node in doc.get("nodes", []):
            nid = node.get("id", "")
            if nid not in seen_node_ids:
                merged["nodes"].append(node)
                seen_node_ids.add(nid)
        for edge in doc.get("edges", []):
            eid = edge.get("id", "")
            if eid not in seen_edge_ids:
                merged["edges"].append(edge)
                seen_edge_ids.add(eid)

    return _yaml.dump(merged, allow_unicode=True, sort_keys=False, default_flow_style=False)


if __name__ == "__main__":
    main()
