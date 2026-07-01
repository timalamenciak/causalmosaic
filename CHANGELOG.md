# Changelog

All notable changes to the active LinkML schema and its supporting governance files are recorded here.

## 0.6.0 -> 0.7.0 changes

### Detailed changes
- Standardized `EvidenceTypeEnum` values to use ECO IRIs.
  - Rationale: Ensures interoperability with community ontologies (ECO, SEPIO, RO), eliminates custom IRI drift, and supports semantic validation across tools.
- Changed `variable_attribute` to `measured_attribute` for clarity.
- Removed `conditioned_by` from `CausalEdge` and subsumed under `ContextAnnotation.scope_conditions`
  - Rationale: Removes duplication between CausalEdge.conditioned_by and ContextAnnotation.scope_conditions, while expanding scope_conditions to accept both node IDs and ontology terms — critical for modeling context dependence in ecology.
- Added `evidential_basis` to `EvidenceBaseAssessmentEdge`
    - Rationale: Aligns EvidenceBaseAssessmentEdge with CausalEdge.evidential_basis, ensuring consistent layer 4 modeling and reducing downstream confusion.
- Added process-based terms to `StateOrChangeQualifierEnum` to capture that.
  - Rationale: Maintaining semantic accuracy.
  


## 0.4.2 -> 0.6.0 changes

### New annotation
- `loom_role:` added to several fields. This has the values: 
    - `hidden` - hidden from annotators.
    - `collapsed` - Starts off collapsed in the annotation form but can be revealed and entered.
    - `calculated` - Loom should auto calculate a value to suggest here.
    - `auto_generated` - Loom should auto generate a value and not allow users to edit this field.

### Detailed changes

- Removed `study_taxa` from `SourceDocument`
  - Rationale: This duplicates information contained in the `CausalNode`. Ultimately
    we only care about the species for which causal claims were made, not all species
    in a particular article.
- Removed `study_ecosystem` from `SourceDocument`
  - Rationale: This duplicates information contained in the `CausalEdge`. Again, if 
    we decide this is important, we can roll up information from the edges to the `SourceDocument`.
- Commented out `conditioned_by` slot on `CausalEdge`
  - Rationale: This could be surfaced in mediation analyses but I think is an unspecific
    way of discussing context-specific variables like ecosystem type, time, etc. It also may
    be better to include these as a node in an INUS or probabilistic relationship.
- Removed `account_families` on `CausalEdge` 
  - Rationale: This can be inferred from the `philosophical_accounts` enum. Kept `AccountFamilyEnum` 
    as it may be used to resolve the annotation `family:`
- Removed `description` from `CausalNode`
  - Rationale: Name and text span are sufficient.
- Added `required: true` to `CausalNode` `entity_term`.
  - Rationale: A node needs an entity.
- Removed `synonyms` from `CausalNode`
  - Rationale: Synonyms are handled at the ontology level, and by WikiData content negotiation. 
    It may be sensible to pull those in, but not necessary as a graph attribute.
- Removed `categories` from `CausalNode`
  - Rationale: This is for BioLink interoperability and may interfere with extraction.
    Categories can be inferred from the full causal node and filled in later.
- Removed `entity_type` from `CausalNode`
  - Rationale: Again, handled at the ontology level. Could be classified post-hoc.
- Added `loom_role: hidden` to `start_char`, `end_char`, `sentence_id`, `paragraph_id`
  - Rationale: These fields may be annotated automatically but will not be populated by
    human annotators.
- Removed `document_source` field `section:` 
  - Rationale: One document source should be valid for all edges extracted from document. Section is unhelpful.
- Removed `causal_connective` from `CausalEdge`
  - Rationale: This is covered by `original_sentence` and is redundant.
- Changed Layer 1 name to "Layer 1: Claim Strength & Context"
- Added `annotation: hidden` to `fcm_weight` and `fcm_weight_source`
  - Rationale: These are calculated and/or expert elicited and should be part of a different process.
- Added `annotator:` to `CausalNode` and made it a hidden field to auto-populate with ORCID.
- `EvidenceBaseAssessmentEdge` is introduced as a new edge type that will be calculated in the final reified graph. It should not be annotated at this stage.



## Unreleased

### Changed

- Removed `process_context` from `CausalEdge`.
  - Rationale: ecological and management processes should be represented as
    nodes when they participate in the causal relationship, using the existing
    entity, attribute, and state/change qualifier structure.
- Added `EcosystemFunctionalGroupEnum` from ELMO's IUCN GET Level 3
  ecosystem functional groups and changed edge-level `ecosystem_context` to use
  that enum. Enum values use LinkML-friendly names grounded to ELMO terms and
  include annotations for the ELMO CURIE, GET code, plain ecosystem name, and
  code-prefixed display label.
  - Rationale: EFGs are included to simplify auto-complete.
- Removed `ecosystem_context` from `CausalNode`, leaving ecosystem context on
  `CausalEdge`.
  - Rationale: ecosystem context constrains the causal relationship rather than
    the reusable node meaning; the same node can participate in causal edges
    observed in different ecosystems, so node-level context can be misleading
    or force duplicate context-specific nodes.
- Improved the `CausalNode.description` slot description to distinguish the
  source-text characterization from the composed canonical `name`.
  - Rationale: annotator clarity.
- Clarified `CausalNode.id` as an annotation-tool-generated field and added
  `loom_role: auto_generated`; Loom uses `entity_term` when provided, otherwise
  generates `causal_mosaic:{slugified_name}_{4-char-hash}`.
  - Rationale: annotator simplification.
- Replaced `DeterminismEnum` values `deterministic` and `stochastic` with
  `deterministic_process`, `indeterministic_process`,
  `epistemic_probability_only`, `ambiguous`, and `not_addressed`; updated the
  enum and slot descriptions to distinguish ontic causal process claims from
  epistemic uncertainty.
  - Rationale: Robert noted that Bayesian probabilities may represent
    uncertainty even when the modeled cause is deterministic.
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
