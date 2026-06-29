# Changelog

All notable changes to the active LinkML schema and its supporting governance files are recorded here.

## Unreleased

### Changed

- Removed `ontology_mappings` from `CausalNode`, removed the `OntologyMapping`
  class, and removed manual `egm_intervention_category` and
  `egm_outcome_category` fields. Ontology grounding is now centralized in
  `entity_term` and `variable_attribute`; node synonyms and evidence-gap-map
  groupings can be inferred downstream from ontology labels, synonyms, classes,
  `entity_type`, and `categories` where possible. External ontology crosswalks,
  if needed, should be maintained outside article annotations in SSSOM files.
  - Rationale: Ontology terms can and should be used directly as values in
    `CausalNode.entity_term` and `CausalNode.variable_attribute`, reducing
    annotator confusion, supporting auto-population of synonyms from ontology
    labels/synonyms, and enabling downstream inference of intervention/outcome
    categories for evidence gap maps.
- Removed `part_qualifiers` from `CausalNode`.
  - Rationale: annotation simplification; the original niche use case is better
    handled through ontology terms.
- Removed aggregate assessment fields from article-level `EvidentialBasis`
  used by `CausalEdge`: `russo_williamson_satisfied`,
  `bradford_hill_viewpoints`, `bradford_hill_count`, `certainty_grade`,
  `certainty_rationale`, and `evidence_count`. These judgments remain on
  `EvidenceBaseAssessmentEdge`, with a note that some Bradford Hill viewpoints
  require qualitative judgment and may not be fully programmatically reassessed
  whenever article-level causal edges change.
  - Rationale: Tim Alamenciak approved this change because these criteria better
    represent aggregate assessments.
- Added `EvidenceBaseAssessmentEdge` as a derived evidence-base-level synthesis
  class for aggregating multiple article-level `CausalEdge` records that refer
  to the same causal relationship. The new class captures evidence set
  membership, aggregate evidence objects/types, Russo-Williamson satisfaction,
  Bradford Hill viewpoints, certainty, evidence balance, study counts, effect
  summaries, and refresh/provenance metadata. Added optional
  `evidence_base_assessments` to `CausalGraph` to store these derived
  assessment edges.
  - Rationale: Based on discussion, aggregate criteria such as
    Russo-Williamson satisfaction are often determined across several studies
    rather than in a single article annotation. Moving these judgments to a
    derived evidence-base assessment layer can reduce annotator effort, for
    example by avoiding repeated Russo-Williamson judgments on every
    article-level causal edge.
- Commented out the Layer 2 `capacity` philosophical account while preserving
  its full definition in comments so the change can be reversed if needed.
  - Rationale: Tim Alamenciak decided to disable this account after conversations
    with Dr. Phyllis Illari suggested it may be too nuanced to be useful.
- Replaced redundant source-document spatial fields `study_location`,
  `study_site`, and `study_sites` with document-level `study_country`,
  `study_state_or_province`, and multivalued `study_coordinates`; renamed
  `StudySite` to `StudyCoordinates` and removed coordinate-level `site_name`,
  `country`, and `admin_region` fields.
  - Rationale: ease of annotation.
- Renamed `variable_direction` to `state_or_change_qualifier` throughout the
  active schema and annotation guide, and renamed the corresponding enum from
  `VariableDirectionEnum` to `StateOrChangeQualifierEnum` while preserving the
  existing permissible values.
  - Rationale: Dr. Phyllis Illari flagged that `variable_direction` is
    inconsistent with variables that do not change, which can still be causally
    relevant.
- Addressed LinkML linter warnings with cosmetic schema metadata cleanup:
  added missing descriptions for existing slots and enums, and removed an unused
  `example` prefix declaration.
  - Rationale: Cosmetic lint cleanup only; this does not affect how the schema
    works.
- Renamed the merged Layer 2 `probabilistic/variation` philosophical account to
  `probabilistic` while retaining the description's distinction between
  probabilistic and variation accounts; updated related Bradford Hill account
  mappings to use `probabilistic`.
  - Rationale: Interoperability.
- Merged the Layer 2 `process` and `information_transmission` philosophical
  accounts into `transmission`, combining their descriptions, canonical
  questions, linguistic cues, and evidence affinities.
  - Rationale: Dr. Phyllis Illari suggested this change to simplify annotation
    of articles.
- Merged the Layer 2 `probabilistic` and `variation` philosophical accounts into
  `probabilistic/variation`, combining both accounts' descriptions, canonical
  questions, linguistic cues, evidence affinities, and related Bradford Hill
  account mappings.
  - Rationale: Dr. Phyllis Illari suggested this change to simplify annotation
    of articles.

### Added

- Initialized `AGENTS.md` with explicit instructions for future agents to work only on `causal_mosaic_v0.4.2.yaml`, make only user-requested changes, seek clarification where required, preserve unrelated work, and record every change with the user-supplied rationale.
  - Rationale: The schema owner requested that these working constraints be made explicit for subsequent agents reviewing or editing the schema.
- Initialized this changelog to provide the requested audit trail for future schema changes.
  - Rationale: The schema owner requested that all changes be logged together with the rationale they provide.
