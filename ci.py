#!/usr/bin/env python3
"""
CAMO schema consistency checks.

`linkml validate` and `linkml lint` verify that causalmosaic.yaml is well-formed
LinkML. They cannot check CAMO's own invariants, because several of the
mappings that drive rendering live in *annotations* — untyped strings that
LinkML does not resolve. A typo in one silently changes an evidence assessment
or flips the sign of an FCM edge.

This script checks those invariants. Each check is keyed to a section of
docs/recommendations.md so a failure points at the rationale.

Usage:
    python ci.py [path/to/causalmosaic.yaml]

Exit codes:
    0  all checks passed (skips allowed)
    1  one or more checks failed

Checks that depend on a construct not yet present in the schema report SKIP
rather than FAIL, so this file can be committed ahead of the schema edits and
activates automatically once they land.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

DEFAULT_SCHEMA = "causalmosaic.yaml"

# Enums intentionally not referenced by any slot range. These are wired to the
# schema through annotation crosswalks (checked below) rather than through a
# slot, so the orphan check must not flag them.
ANNOTATION_ONLY_ENUMS = {
    "AccountFamilyEnum",       # via PhilosophicalAccountEnum.family
}

# The Layer 3 causal feature slots on CausalEdge. Every one must carry a
# slot_uri. See A4 and C6a.
LAYER3_SLOTS = [
    "necessity", "sufficiency", "direction", "temporal_ordering", "mediation",
    "moderation", "strength", "specificity", "stability", "token_or_type",
    "determinism", "proximate_distal", "contributing_sole", "reversibility",
    "proportionality", "context_dependence",
]

VALID_FCM_SIGNS = {"positive", "negative", "neutral"}
IUCN_GET_CODE = re.compile(r"[A-Z]{1,3}\d+\.\d+")
SEPARATOR = "|"


# --------------------------------------------------------------------------
# harness
# --------------------------------------------------------------------------

class Report:
    def __init__(self) -> None:
        self.failures: list[tuple[str, str]] = []
        self.skips: list[tuple[str, str]] = []
        self.passes: list[str] = []
        self._current = ""

    def check(self, ref: str, name: str):
        self._current = f"{ref}  {name}"
        return self

    def __enter__(self):
        self._failed_here = False
        return self

    def __exit__(self, *exc):
        if not self._failed_here and self._current not in [s[0] for s in self.skips]:
            self.passes.append(self._current)
        return False

    def fail(self, message: str) -> None:
        self._failed_here = True
        self.failures.append((self._current, message))

    def skip(self, message: str) -> None:
        self._failed_here = True
        self.skips.append((self._current, message))

    def summary(self) -> int:
        for name in self.passes:
            print(f"  PASS  {name}")
        for name, msg in self.skips:
            print(f"  SKIP  {name}\n          {msg}")
        for name, msg in self.failures:
            print(f"  FAIL  {name}\n          {msg}")
        print()
        print(f"{len(self.passes)} passed, {len(self.skips)} skipped, "
              f"{len(self.failures)} failed")
        return 1 if self.failures else 0


def annotations_of(pv: dict) -> dict:
    return (pv or {}).get("annotations") or {}


def tokens(value: str) -> set[str]:
    """Split a pipe-delimited annotation value, per the Darwin Core convention."""
    return {t.strip() for t in str(value).split(SEPARATOR) if t.strip()}


def all_slot_names(schema: dict) -> set[str]:
    names = set(schema.get("slots") or {})
    for cls in (schema.get("classes") or {}).values():
        names |= set(cls.get("attributes") or {})
    return names


def slot_ranges(schema: dict) -> set[str]:
    """Every range referenced by any slot, including inside any_of branches."""
    found = set()
    for cls in (schema.get("classes") or {}).values():
        for slot in (cls.get("attributes") or {}).values():
            if slot.get("range"):
                found.add(slot["range"])
            for branch in slot.get("any_of") or []:
                if branch.get("range"):
                    found.add(branch["range"])
    return found


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------

def check_bradford_hill_accounts(schema: dict, r: Report) -> None:
    """A5 — every maps_to_account token names a real philosophical account,
    and temporality lists all of them."""
    with r.check("A5 ", "BradfordHillViewpointEnum.maps_to_account"):
        enums = schema["enums"]
        accounts = set(enums["PhilosophicalAccountEnum"]["permissible_values"])
        problems = []
        for name, pv in enums["BradfordHillViewpointEnum"]["permissible_values"].items():
            raw = annotations_of(pv).get("maps_to_account")
            if raw is None:
                problems.append(f"{name}: missing maps_to_account")
                continue
            unknown = tokens(raw) - accounts
            if unknown:
                problems.append(
                    f"{name}: {sorted(unknown)} not in PhilosophicalAccountEnum"
                )
            elif name == "temporality" and tokens(raw) != accounts:
                missing = sorted(accounts - tokens(raw))
                problems.append(
                    "temporality has drifted from PhilosophicalAccountEnum; "
                    f"missing {missing}. It is a precondition of every account, "
                    "so the list must be exhaustive."
                )
        if problems:
            r.fail("\n          ".join(problems))


def check_bradford_hill_features(schema: dict, r: Report) -> None:
    """maps_to_feature must name a real slot."""
    with r.check("A5 ", "BradfordHillViewpointEnum.maps_to_feature"):
        names = all_slot_names(schema)
        problems = [
            f"{name}: maps_to_feature {feature!r} is not a slot"
            for name, pv in schema["enums"]["BradfordHillViewpointEnum"]["permissible_values"].items()
            if (feature := annotations_of(pv).get("maps_to_feature")) and feature not in names
        ]
        if problems:
            r.fail("\n          ".join(problems))


def check_account_families(schema: dict, r: Report) -> None:
    """C2a — every PhilosophicalAccountEnum.family names a real account family.

    This crosswalk computes has_difference_making_evidence and
    has_production_evidence, so a typo produces a wrong Russo-Williamson
    assessment.
    """
    with r.check("C2a", "PhilosophicalAccountEnum.family"):
        enums = schema["enums"]
        families = set(enums["AccountFamilyEnum"]["permissible_values"])
        problems = [
            f"{name}: family {fam!r} not in AccountFamilyEnum"
            for name, pv in enums["PhilosophicalAccountEnum"]["permissible_values"].items()
            if (fam := annotations_of(pv).get("family")) not in families
        ]
        if problems:
            r.fail("\n          ".join(problems))


def check_qualifier_families(schema: dict, r: Report) -> None:
    """B7b — every qualifier carries a family, and the family is declared."""
    with r.check("B7b", "StateOrChangeQualifierEnum.qualifier_family"):
        enums = schema["enums"]
        if "QualifierFamilyEnum" not in enums:
            r.skip("QualifierFamilyEnum not declared yet — see B7b")
            return
        families = set(enums["QualifierFamilyEnum"]["permissible_values"])
        problems = [
            f"{name}: qualifier_family {fam!r} not in QualifierFamilyEnum"
            for name, pv in enums["StateOrChangeQualifierEnum"]["permissible_values"].items()
            if (fam := annotations_of(pv).get("qualifier_family")) not in families
        ]
        if problems:
            r.fail("\n          ".join(problems))


def check_value_type_families(schema: dict, r: Report) -> None:
    """Loom matches parameter options to nodes by these families; a typo drops matches."""
    with r.check("   ", "ValueTypeEnum.compatible_qualifier_families"):
        enums = schema["enums"]
        if "ValueTypeEnum" not in enums:
            r.skip("ValueTypeEnum not declared")
            return
        families = set(enums["QualifierFamilyEnum"]["permissible_values"])
        problems = []
        for name, pv in enums["ValueTypeEnum"]["permissible_values"].items():
            raw = annotations_of(pv).get("compatible_qualifier_families")
            if not raw:
                problems.append(f"{name}: missing compatible_qualifier_families")
                continue
            unknown = sorted(tokens(raw) - families)
            if unknown:
                problems.append(f"{name}: {unknown} not in QualifierFamilyEnum")
        if problems:
            r.fail("\n          ".join(problems))


def check_qualifier_signs(schema: dict, r: Report) -> None:
    """fcm_sign drives FCM polarity; an unrecognized value flips an edge."""
    with r.check("   ", "StateOrChangeQualifierEnum.fcm_sign"):
        problems = [
            f"{name}: fcm_sign {sign!r} not in {sorted(VALID_FCM_SIGNS)}"
            for name, pv in schema["enums"]["StateOrChangeQualifierEnum"]["permissible_values"].items()
            if (sign := annotations_of(pv).get("fcm_sign")) not in VALID_FCM_SIGNS
        ]
        if problems:
            r.fail("\n          ".join(problems))


def check_predicate_weights(schema: dict, r: Report) -> None:
    """C6d — fcm_default_weight is a string; every consumer parses it."""
    with r.check("C6d", "CausalPredicateEnum.fcm_default_weight"):
        problems = []
        for name, pv in schema["enums"]["CausalPredicateEnum"]["permissible_values"].items():
            raw = annotations_of(pv).get("fcm_default_weight")
            if raw is None:
                problems.append(f"{name}: missing fcm_default_weight")
                continue
            try:
                weight = float(raw)
            except (TypeError, ValueError):
                problems.append(f"{name}: fcm_default_weight {raw!r} does not parse as a float")
                continue
            if not -1.0 <= weight <= 1.0:
                problems.append(f"{name}: fcm_default_weight {weight} outside [-1.0, 1.0]")
            if not annotations_of(pv).get("sign"):
                problems.append(f"{name}: missing sign")
        if problems:
            r.fail("\n          ".join(problems))


def check_rosetta_templates(schema: dict, r: Report) -> None:
    """Every predicate template must have both substitution points."""
    with r.check("   ", "CausalPredicateEnum.rosetta_template"):
        problems = []
        for name, pv in schema["enums"]["CausalPredicateEnum"]["permissible_values"].items():
            template = annotations_of(pv).get("rosetta_template")
            if not template:
                problems.append(f"{name}: missing rosetta_template")
                continue
            for placeholder in ("{subject}", "{object}"):
                if placeholder not in template:
                    problems.append(f"{name}: template is missing {placeholder}")
        if problems:
            r.fail("\n          ".join(problems))


def check_certainty_modifiers(schema: dict, r: Report) -> None:
    """Every graded certainty needs a hedging modifier; empty string is valid."""
    with r.check("   ", "CertaintyGradeEnum.rosetta_verb_modifier"):
        problems = [
            f"{name}: missing rosetta_verb_modifier"
            for name, pv in schema["enums"]["CertaintyGradeEnum"]["permissible_values"].items()
            if name != "not_assessed" and annotations_of(pv).get("rosetta_verb_modifier") is None
        ]
        if problems:
            r.fail("\n          ".join(problems))


def check_ecosystem_codes(schema: dict, r: Report) -> None:
    """EGM column rollup truncates iucn_get_code, so the codes must be well-formed."""
    with r.check("   ", "EcosystemFunctionalGroupEnum codes and grounding"):
        problems = []
        for name, pv in schema["enums"]["EcosystemFunctionalGroupEnum"]["permissible_values"].items():
            ann = annotations_of(pv)
            code = ann.get("iucn_get_code")
            if not code or not IUCN_GET_CODE.fullmatch(str(code)):
                problems.append(f"{name}: iucn_get_code {code!r} is not a GET code (e.g. T1.1)")
            meaning = pv.get("meaning")
            curie = ann.get("ontology_curie")
            if not meaning:
                problems.append(f"{name}: no meaning")
            elif curie and meaning.split(":")[-1] != str(curie).split(":")[-1]:
                problems.append(f"{name}: meaning {meaning} and ontology_curie {curie} disagree")
        if problems:
            r.fail("\n          ".join(problems))


def check_no_orphan_enums(schema: dict, r: Report) -> None:
    """C1 — an enum referenced by no slot has no value space."""
    with r.check("C1 ", "no orphaned enums"):
        used = slot_ranges(schema)
        orphans = sorted(
            set(schema["enums"]) - used - ANNOTATION_ONLY_ENUMS
        )
        if orphans:
            r.fail(
                f"referenced by no slot: {orphans}. Either wire to a slot, add to "
                "ANNOTATION_ONLY_ENUMS with the crosswalk check that covers it, "
                "or delete."
            )


def check_ifabsent_defaults(schema: dict, r: Report) -> None:
    """An ifabsent naming a non-existent permissible value fails at runtime."""
    with r.check("   ", "ifabsent defaults name real values"):
        pattern = re.compile(r"\w+\((.*)\)")
        problems = []
        for cname, cls in (schema.get("classes") or {}).items():
            for sname, slot in (cls.get("attributes") or {}).items():
                raw = slot.get("ifabsent")
                rng = slot.get("range")
                if not raw or rng not in schema["enums"]:
                    continue
                match = pattern.fullmatch(str(raw))
                if not match:
                    problems.append(f"{cname}.{sname}: cannot parse ifabsent {raw!r}")
                    continue
                if match.group(1) not in schema["enums"][rng]["permissible_values"]:
                    problems.append(
                        f"{cname}.{sname}: ifabsent {match.group(1)!r} is not a value of {rng}"
                    )
        if problems:
            r.fail("\n          ".join(problems))


def check_prefixes_declared(schema: dict, r: Report) -> None:
    """A CURIE with an undeclared prefix will not expand in the JSON-LD context."""
    with r.check("A2 ", "all CURIEs use declared prefixes"):
        declared = set(schema.get("prefixes") or {})
        fields = {"meaning", "slot_uri", "class_uri",
                  "exact_mappings", "close_mappings", "broad_mappings",
                  "narrow_mappings", "related_mappings"}
        problems = set()

        def walk(node):
            if isinstance(node, dict):
                for key, value in node.items():
                    if key in fields:
                        for item in (value if isinstance(value, list) else [value]):
                            if isinstance(item, str) and ":" in item and not item.startswith("http"):
                                prefix = item.split(":")[0]
                                if prefix not in declared:
                                    problems.add(f"{item} uses undeclared prefix {prefix!r}")
                    walk(value)
            elif isinstance(node, list):
                for item in node:
                    walk(item)

        walk(schema)
        if problems:
            r.fail("\n          ".join(sorted(problems)))


def check_layer3_slot_uris(schema: dict, r: Report) -> None:
    """C6a — every causal feature slot needs a stable URI."""
    with r.check("C6a", "Layer 3 feature slots carry slot_uri"):
        edge = (schema["classes"]["CausalEdge"].get("attributes") or {})
        missing = [name for name in LAYER3_SLOTS
                   if name in edge and not edge[name].get("slot_uri")]
        absent = [name for name in LAYER3_SLOTS if name not in edge]
        problems = []
        if missing:
            problems.append(f"no slot_uri: {missing}")
        if absent:
            problems.append(f"not found on CausalEdge (update LAYER3_SLOTS?): {absent}")
        if problems:
            r.fail("\n          ".join(problems))


def check_renderer_manifest(schema: dict, r: Report, root: Path) -> None:
    """C1b — every field a renderer claims to consume must exist.

    Expects renderers.yaml of the form:
        targets:
          evidence_gap_map:
            consumes: [entity_type, ecosystem_context, ...]
    """
    with r.check("C1b", "renderer manifest fields resolve"):
        manifest = root / "renderers.yaml"
        if not manifest.exists():
            r.skip("renderers.yaml not present — see C1b")
            return
        data = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
        names = all_slot_names(schema)
        problems = [
            f"{target}: consumes {field!r}, which is not a slot"
            for target, spec in (data.get("targets") or {}).items()
            for field in (spec or {}).get("consumes") or []
            if field not in names
        ]
        if problems:
            r.fail("\n          ".join(problems))


# --------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else Path(DEFAULT_SCHEMA)
    if not path.exists():
        print(f"schema not found: {path}", file=sys.stderr)
        return 1

    schema = yaml.safe_load(path.read_text(encoding="utf-8"))
    print(f"CAMO consistency checks — {path} "
          f"(schema version {schema.get('version', 'unknown')})\n")

    r = Report()
    check_bradford_hill_accounts(schema, r)
    check_bradford_hill_features(schema, r)
    check_account_families(schema, r)
    check_qualifier_families(schema, r)
    check_qualifier_signs(schema, r)
    check_value_type_families(schema, r)
    check_predicate_weights(schema, r)
    check_rosetta_templates(schema, r)
    check_certainty_modifiers(schema, r)
    check_ecosystem_codes(schema, r)
    check_no_orphan_enums(schema, r)
    check_ifabsent_defaults(schema, r)
    check_prefixes_declared(schema, r)
    check_layer3_slot_uris(schema, r)
    check_renderer_manifest(schema, r, path.parent)
    return r.summary()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
