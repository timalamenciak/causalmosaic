"""
validate_schema.py — Causal Mosaic YAML Schema Validator

Checks a Causal Mosaic 0.4 YAML file for structural errors and warnings
before human review. See Annotation Guide Appendix A.4.3, Tool 4.

Usage:
    python validate_schema.py draft.yaml
    python validate_schema.py draft.yaml --strict   # treat warnings as errors

Exit codes:
    0 — no errors (warnings may be present)
    1 — one or more errors found
"""

import sys
import click
import yaml

# ---------------------------------------------------------------------------
# Enum definitions (Causal Mosaic 0.4.0)
# ---------------------------------------------------------------------------

CLAIM_STRENGTH = {"no_relationship", "associational", "conditional_causal", "direct_causal"}

PREDICATES = {
    "causes", "contributes_to", "associated_with", "correlated_with",
    "prevents", "disrupts", "negatively_regulates", "positively_regulates",
    "regulates", "mediates", "moderates", "precedes", "enables",
}

# Predicates whose FCM weight should be positive (>0) or negative (<0)
POSITIVE_PREDICATES = {"causes", "contributes_to", "enables", "positively_regulates"}
NEGATIVE_PREDICATES = {"prevents", "disrupts", "negatively_regulates"}

PHILOSOPHICAL_ACCOUNTS = {
    "counterfactual", "probabilistic", "interventionist", "variation",
    "process", "mechanistic", "information_transmission", "regularity",
    "inus_component", "capacity", "agency",
}

ACCOUNT_FAMILIES = {"difference_making", "production", "complementary"}

FEATURE_ASSERTION = {
    "explicitly_asserted", "implicitly_assumed", "explicitly_denied", "not_addressed",
}

DIRECTION_STATUS = {"asserted", "uncertain", "bidirectional", "not_addressed"}

DIRECTION_EVIDENCE = {
    "experimental", "temporal_precedence", "theoretical",
    "natural_experiment", "structural_model",
}

TOKEN_TYPE = {"token", "type", "ambiguous", "not_addressed"}

DETERMINISM = {"deterministic", "probabilistic", "ambiguous", "not_addressed"}

PROXIMATE_DISTAL = {"proximate", "distal", "both_specified", "not_addressed"}

CONTRIBUTING_SOLE = {"sole_cause", "contributing_cause", "not_addressed"}

REVERSIBILITY = {
    "reversible", "irreversible", "partially_reversible", "hysteresis", "not_addressed",
}

INTERACTION_TYPE = {
    "synergistic", "antagonistic", "qualitative", "quantitative", "not_specified",
}

STRENGTH_QUALITATIVE = {"strong", "moderate", "weak", "negligible", "not_specified"}

VARIABLE_DIRECTION = {
    "increased", "decreased", "present", "absent",
    "introduced", "removed", "unchanged", "unspecified",
}

ENTITY_TYPE = {
    "environmental_variable", "environmental_process", "management_intervention",
    "organism_taxon", "community", "ecological_state", "abiotic_factor",
    "biological_process", "ecological_outcome",
}

EVIDENCE_TYPES = {
    "randomized_experiment", "natural_experiment", "quasi_experiment",
    "observational_longitudinal", "observational_cross_sectional",
    "mechanistic_study", "structural_equation_model", "meta_analysis",
    "systematic_review", "modeling_simulation", "expert_judgment",
    "case_study", "theoretical", "indigenous_knowledge", "practitioner_experience",
}

EVIDENCE_OBJECTS = {"correlation", "mechanism", "both"}

BRADFORD_HILL = {
    "strength", "consistency", "specificity", "temporality",
    "biological_gradient", "plausibility", "coherence", "experiment", "analogy",
}

CERTAINTY_GRADES = {"high", "moderate", "low", "very_low", "not_assessed"}

CERTAINTY_ALIASES = {"high_confidence": "high", "medium": "moderate", "medium_confidence": "moderate"}

TEMPORAL_ORDERING = {
    "explicitly_asserted", "implicitly_assumed", "explicitly_denied", "not_addressed",
}

# Fields required on every node
NODE_REQUIRED = {"id", "name"}

# Fields required on every edge
EDGE_REQUIRED = {"id", "subject", "predicate", "object", "claim_strength"}

# ---------------------------------------------------------------------------
# Validation logic
# ---------------------------------------------------------------------------

class Report:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str):
        self.errors.append(f"ERROR: {msg}")

    def warn(self, msg: str):
        self.warnings.append(f"WARNING: {msg}")

    def print_all(self):
        for line in self.errors + self.warnings:
            click.echo(line)

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)


def validate(doc: dict, report: Report):
    if not isinstance(doc, dict):
        report.error("Top-level document is not a YAML mapping.")
        return

    nodes = doc.get("nodes", [])
    edges = doc.get("edges", [])

    if not isinstance(nodes, list):
        report.error("`nodes` is not a list.")
        nodes = []
    if not isinstance(edges, list):
        report.error("`edges` is not a list.")
        edges = []

    # Collect node IDs
    node_ids: set[str] = set()
    for node in nodes:
        nid = node.get("id", "")
        if nid:
            if nid in node_ids:
                report.error(f"Duplicate node id: {nid!r}")
            node_ids.add(nid)

    # Validate nodes
    for node in nodes:
        _validate_node(node, report)

    # Validate edges
    edge_ids: set[str] = set()
    for edge in edges:
        eid = edge.get("id", "")
        if eid:
            if eid in edge_ids:
                report.error(f"Duplicate edge id: {eid!r}")
            edge_ids.add(eid)
        _validate_edge(edge, node_ids, report)


def _validate_node(node: dict, report: Report):
    eid = node.get("id", "(no id)")
    ctx = f"node {eid!r}"

    for field in NODE_REQUIRED:
        if not node.get(field):
            report.error(f"{ctx}: missing required field {field!r}")

    vd = node.get("variable_direction")
    if vd and vd not in VARIABLE_DIRECTION:
        report.error(f"{ctx}: invalid variable_direction {vd!r}. "
                     f"Must be one of: {sorted(VARIABLE_DIRECTION)}")

    et = node.get("entity_type")
    if et and et not in ENTITY_TYPE:
        report.warn(f"{ctx}: unrecognised entity_type {et!r}. "
                    f"Known values: {sorted(ENTITY_TYPE)}")


def _validate_edge(edge: dict, node_ids: set[str], report: Report):
    eid = edge.get("id", "(no id)")
    ctx = f"edge {eid!r}"

    for field in EDGE_REQUIRED:
        if not edge.get(field):
            report.error(f"{ctx}: missing required field {field!r}")

    # Predicate
    pred = edge.get("predicate")
    if pred and pred not in PREDICATES:
        report.error(f"{ctx}: invalid predicate {pred!r}. "
                     f"Must be one of: {sorted(PREDICATES)}")

    # Claim strength
    cs = edge.get("claim_strength")
    if cs and cs not in CLAIM_STRENGTH:
        report.error(f"{ctx}: invalid claim_strength {cs!r}. "
                     f"Must be one of: {sorted(CLAIM_STRENGTH)}")

    # Source_spans required
    spans = edge.get("source_spans", [])
    if not spans:
        report.error(f"{ctx}: missing source_spans (at least one required)")

    # Node references
    for ref_field in ("subject", "object"):
        ref = edge.get(ref_field)
        if ref and ref not in node_ids:
            report.error(f"{ctx}: {ref_field} {ref!r} does not match any node id")

    # Philosophical accounts
    accounts = edge.get("philosophical_accounts", [])
    if isinstance(accounts, list):
        for acct in accounts:
            if acct not in PHILOSOPHICAL_ACCOUNTS:
                report.error(f"{ctx}: invalid philosophical_account {acct!r}. "
                             f"Must be one of: {sorted(PHILOSOPHICAL_ACCOUNTS)}")
    elif accounts:
        report.error(f"{ctx}: philosophical_accounts must be a list")

    # Account families
    families = edge.get("account_families", [])
    if isinstance(families, list):
        for fam in families:
            if fam not in ACCOUNT_FAMILIES:
                report.error(f"{ctx}: invalid account_family {fam!r}. "
                             f"Must be one of: {sorted(ACCOUNT_FAMILIES)}")

    # FCM weight range
    fcm = edge.get("fcm_weight")
    if fcm is not None:
        try:
            fcm_f = float(fcm)
        except (TypeError, ValueError):
            report.error(f"{ctx}: fcm_weight {fcm!r} is not a number")
            fcm_f = None
        if fcm_f is not None:
            if not (-1.0 <= fcm_f <= 1.0):
                report.error(f"{ctx}: fcm_weight {fcm_f} is outside [-1.0, 1.0]")
            # Sign consistency with predicate
            if pred in POSITIVE_PREDICATES and fcm_f < 0:
                report.warn(f"{ctx}: positive predicate {pred!r} but fcm_weight is negative ({fcm_f})")
            elif pred in NEGATIVE_PREDICATES and fcm_f > 0:
                report.warn(f"{ctx}: negative predicate {pred!r} but fcm_weight is positive ({fcm_f})")

    # Annotation confidence range
    conf = edge.get("annotation_confidence")
    if conf is not None:
        try:
            conf_f = float(conf)
        except (TypeError, ValueError):
            report.error(f"{ctx}: annotation_confidence {conf!r} is not a number")
            conf_f = None
        if conf_f is not None:
            if not (0.0 <= conf_f <= 1.0):
                report.error(f"{ctx}: annotation_confidence {conf_f} is outside [0.0, 1.0]")
            if conf_f == 0.0:
                report.warn(f"{ctx}: annotation_confidence is 0.0 — likely not set")

    # Evidential basis
    eb = edge.get("evidential_basis", {})
    if isinstance(eb, dict):
        # Evidence types
        for et in eb.get("evidence_types", []):
            if et not in EVIDENCE_TYPES:
                report.warn(f"{ctx}: unrecognised evidence_type {et!r}")

        # Evidence objects
        for eo in eb.get("evidence_objects", []):
            if eo not in EVIDENCE_OBJECTS:
                report.warn(f"{ctx}: unrecognised evidence_object {eo!r}. "
                            f"Expected: {sorted(EVIDENCE_OBJECTS)}")

        # Bradford Hill viewpoints
        bh_views = eb.get("bradford_hill_viewpoints", [])
        bh_count = eb.get("bradford_hill_count", 0)
        for bh in bh_views:
            if bh not in BRADFORD_HILL:
                report.warn(f"{ctx}: unrecognised bradford_hill_viewpoint {bh!r}")
        if isinstance(bh_views, list) and isinstance(bh_count, int):
            if len(bh_views) != bh_count:
                report.warn(
                    f"{ctx}: bradford_hill_count ({bh_count}) does not match "
                    f"length of bradford_hill_viewpoints ({len(bh_views)})"
                )

        # Certainty grade
        cg = eb.get("certainty_grade")
        if cg:
            normalized = CERTAINTY_ALIASES.get(cg, cg)
            if normalized not in CERTAINTY_GRADES:
                report.error(f"{ctx}: invalid certainty_grade {cg!r}. "
                             f"Must be one of: {sorted(CERTAINTY_GRADES)}")

    # Temporal ordering
    to = edge.get("temporal_ordering")
    if to and to not in TEMPORAL_ORDERING:
        report.warn(f"{ctx}: unrecognised temporal_ordering {to!r}")

    # Direction sub-object
    direction = edge.get("direction", {})
    if isinstance(direction, dict):
        ds = direction.get("status")
        if ds and ds not in DIRECTION_STATUS:
            report.error(f"{ctx}: invalid direction.status {ds!r}. "
                        f"Must be one of: {sorted(DIRECTION_STATUS)}")
        de = direction.get("evidence_for_direction")
        if de and de not in DIRECTION_EVIDENCE:
            report.warn(f"{ctx}: unrecognised direction.evidence_for_direction {de!r}")

    # Strength sub-object
    strength = edge.get("strength", {})
    if isinstance(strength, dict):
        sq = strength.get("qualitative_descriptor")
        if sq and sq not in STRENGTH_QUALITATIVE:
            report.warn(f"{ctx}: unrecognised strength.qualitative_descriptor {sq!r}")
        qn = strength.get("quantitative_numeric")
        if qn is not None:
            try:
                float(qn)
            except (TypeError, ValueError):
                report.error(f"{ctx}: strength.quantitative_numeric {qn!r} is not a number")

    # Moderation sub-object
    moderation = edge.get("moderation", {})
    if isinstance(moderation, dict):
        it = moderation.get("interaction_type")
        if it and it not in INTERACTION_TYPE:
            report.warn(f"{ctx}: unrecognised moderation.interaction_type {it!r}")

    # Dangling mediator / moderator references
    for list_field in ("mediator_node_ids", "moderator_node_ids"):
        mediation_block = edge.get("mediation", {})
        moderation_block = edge.get("moderation", {})
        block = mediation_block if list_field == "mediator_node_ids" else moderation_block
        if isinstance(block, dict):
            for ref in block.get(list_field, []):
                if ref and ref not in node_ids:
                    report.warn(f"{ctx}: {list_field} contains reference to unknown node {ref!r}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.command()
@click.argument("yaml_file", type=click.Path(exists=True))
@click.option("--strict", is_flag=True, default=False,
              help="Treat warnings as errors (exit code 1 if any warnings).")
def main(yaml_file, strict):
    """Validate a Causal Mosaic 0.4 YAML file for structural correctness.

    Checks required fields, enum values, node references, FCM weight ranges,
    Bradford Hill count consistency, and predicate/weight sign agreement.

    Exits with code 0 if no errors, code 1 if errors found.
    """
    with open(yaml_file, encoding="utf-8") as fh:
        try:
            doc = yaml.safe_load(fh)
        except yaml.YAMLError as exc:
            click.echo(f"ERROR: Could not parse YAML: {exc}", err=True)
            sys.exit(1)

    report = Report()
    validate(doc, report)
    report.print_all()

    n_nodes = len(doc.get("nodes", [])) if isinstance(doc, dict) else 0
    n_edges = len(doc.get("edges", [])) if isinstance(doc, dict) else 0
    click.echo(
        f"\nValidated {n_nodes} node(s), {n_edges} edge(s). "
        f"{len(report.errors)} error(s), {len(report.warnings)} warning(s)."
    )

    if report.has_errors or (strict and report.warnings):
        sys.exit(1)


if __name__ == "__main__":
    main()
