# Changelog

All notable changes to the active LinkML schema and its supporting governance files are recorded here.

## 0.7.4 Changed filename

Renamed camo-0.7.3.yaml to causalmosaic.yaml so that CI doesn't keep breaking.

## 0.7.3 Taxon-scope two-path model (2026-07-07)

### Machine-readable summary

```yaml
added_slots:
  - slot: taxonomic_scope
    class: CausalNode
    range: any_of [uriorcurie, string]
    multivalued: true
updated_descriptions:
  - class: CausalNode
    note: two-path model for taxon-specific measurements added to class description
  - enum: EntityTypeEnum
    value: taxon
    note: two-path model documented in permissible value description
updated_metadata:
  - version: 0.7.2 -> 0.7.3
```

### Detailed changes

- Added `taxonomic_scope` (multivalued, `any_of [uriorcurie, string]`) to
  `CausalNode`.
  - Rationale: An audit of extraction outputs revealed that taxon-specific
    measurements were being emitted as compound unresolved terms
    (e.g., "abundance of Yellow-breasted Chats") rather than decomposed
    graph structures, because the schema had no slot for scoping an
    environmental_variable node to one or more taxa without a non-causal
    edge. `taxonomic_scope` provides that slot. It accepts Wikidata QIDs
    so that higher-rank identifiers (e.g., Q30019 for genus *Sphagnum*)
    enable downstream traversal to all taxon nodes sharing that QID
    without requiring a structural edge. Free-text values are accepted for
    functional groups and guilds that have no Wikidata resolution
    ("native species", "shade-tolerant species") — these should be tracked
    in the project NAO list with a note that they are relational terms
    requiring geographic or jurisdictional context. The slot is annotated
    as applicable only to `environmental_variable` nodes; `taxon` nodes
    should continue to carry their identity in `entity_term`.
  - This slot preserves the invariant that all edges in the graph are
    purely causal — `taxonomic_scope` is a queryable annotation field,
    not a structural link.

- Documented the two-path model for taxon-specific measurements in both
  the `CausalNode` class description and the `EntityTypeEnum.taxon`
  permissible value description.
  - Path 1 (single taxon as subject): use `entity_type: taxon` with the
    Wikidata QID in `entity_term` and the measured property in
    `measured_attribute`. The taxon node is both organism and measurement
    and participates directly in causal edges.
  - Path 2 (multi-taxon aggregate or ecological guild): use
    `entity_type: environmental_variable` with one or more Wikidata QIDs
    or free-text guild names in `taxonomic_scope`.
  - Rationale: Tim Alamenciak confirmed this design in review: edges must
    remain purely causal; the shared Wikidata QID is the implicit link
    between taxon nodes and `taxonomic_scope` entries on variable nodes,
    enabling queries like "everything involving *Sphagnum*" across both
    paths without non-causal edges.

## 0.7.2 LinkML compatibility fix (2026-07-03)

- Changed `CausalPredicateEnum.precedes.notes` from a scalar string to a
  one-item list, as required by the LinkML metamodel.
  - Rationale: LinkML compatibility.

## Supporting documentation and CI (2026-07-03)

- Added a GitHub Actions workflow that validates the active schema against the
  LinkML metamodel and runs the LinkML linter on pushes and pull requests.
  - Rationale: continuously lint and validate the LinkML schema in GitHub CI.
- Added a single-page schema reference covering every class and inline slot in
  the active schema.
  - Rationale: provide one documentation page detailing the schema's classes
    and slots.
- Expanded `README.md` with a high-level explanation of `CausalNode`,
  `CausalEdge`, and `EvidenceBaseAssessmentEdge`.
  - Rationale: explain the schema's three core graph objects at a conceptual
    level.
- Added README badges for the latest version tag and LinkML schema CI status.
  - Rationale: make the current release version and CI result visible from the
    repository landing page. The version badge uses tags because the repository
    does not yet have a published GitHub Release.
- These changes affect only supporting documentation and CI configuration; they
  do not change the schema.

## 0.7.0 -> 0.7.1 changes

This entry was reconstructed from a file diff (`old versions/causal_mosaic_v0.7.0.yaml`
vs `causal_mosaic_v0.7.1.yaml`) rather than logged at the time, so several
items are missing the rationale the schema owner would normally supply here —
marked below where that's the case.

### Machine-readable summary

```yaml
renamed_enums:
  - {from: NodeEntityTypeEnum, to: EntityTypeEnum}
added_enum_values:
  - {enum: EntityTypeEnum, value: taxon}
removed_enum_values:
  - {enum: StateOrChangeQualifierEnum, values: [introduced, removed]}
added_slots:
  - {slot: entity_type, class: CausalNode, range: EntityTypeEnum}
bug_fixes:
  - {issue: "annotation: (singular) is not a valid LinkML key and was silently ignored",
     fix: "corrected to annotations: on embedding_text, start_char, end_char, sentence_id, paragraph_id, study_duration_months",
     effect: "these fields' loom_role: hidden annotation (declared in 0.4.2->0.6.0) now actually takes effect"}
  - {issue: "loom_role: collapsed does not match the value Loom's schema_engine.py checks for (\"collapse\")",
     fix: "corrected loom_role: collapsed -> collapse on bbox_north, bbox_south, bbox_east, bbox_west",
     effect: "these StudyCoordinates bounding-box fields now actually start collapsed in the annotation form"}
```

### Detailed changes

- Fixed `annotation:` (singular) to `annotations:` (plural — the correct LinkML
  key) on `embedding_text`, `start_char`, `end_char`, `sentence_id`,
  `paragraph_id`, and `study_duration_months`.
  - Rationale: not recorded. This looks like an unintentional typo in 0.7.0
    rather than a deliberate design decision — the singular key silently
    failed to register as a LinkML annotation, so these fields' intended
    `loom_role: hidden` (declared back in the 0.4.2 -> 0.6.0 entry) never
    actually took effect until this fix.
- Fixed `loom_role: collapsed` to `loom_role: collapse` on the `StudyCoordinates`
  bounding-box fields `bbox_north`, `bbox_south`, `bbox_east`, `bbox_west`.
  - Rationale: not recorded. Same pattern as above — Loom's schema-engine code
    only recognizes the value `collapse`, so these fields never actually
    started collapsed in the annotation form until this fix.
- Renamed `NodeEntityTypeEnum` to `EntityTypeEnum` and added a `taxon`
  permissible value.
  - Rationale: not recorded — ask Tim Alamenciak if this should be documented
    further.
- Added `entity_type` to `CausalNode` (range `EntityTypeEnum`), annotated as
  "Recommended but not required; inferred from entity_term when missing."
  - Rationale: not recorded — ask Tim Alamenciak if this should be documented
    further.
- Removed the `introduced` and `removed` permissible values from
  `StateOrChangeQualifierEnum` (both had been added in the 0.6.0 -> 0.7.0
  process-based-terms expansion).
  - Rationale: not recorded — ask Tim Alamenciak if this should be documented
    further.

## 0.6.0 -> 0.7.0 changes

### Machine-readable summary

```yaml
renamed_slots:
  - {from: variable_attribute, to: measured_attribute}
removed_slots:
  - {slot: conditioned_by, class: CausalEdge, note: "subsumed into ContextAnnotation.scope_conditions"}
added_slots:
  - {slot: evidential_basis, class: EvidenceBaseAssessmentEdge}
enum_changes:
  - {enum: EvidenceTypeEnum, change: "values standardized to ECO IRIs"}
  - {enum: StateOrChangeQualifierEnum, change: "added process-based terms"}
```

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

### Machine-readable summary

```yaml
removed_slots:
  - {slot: study_taxa, class: SourceDocument}
  - {slot: study_ecosystem, class: SourceDocument}
  - {slot: conditioned_by, class: CausalEdge, note: "commented out, not deleted"}
  - {slot: account_families, class: CausalEdge}
  - {slot: description, class: CausalNode}
  - {slot: synonyms, class: CausalNode}
  - {slot: categories, class: CausalNode}
  - {slot: entity_type, class: CausalNode}
  - {slot: causal_connective, class: CausalEdge}
  - {slot: section, class: document_source}
added_slots:
  - {slot: annotator, class: CausalNode, note: "loom_role: hidden, auto-populated with ORCID"}
added_classes:
  - EvidenceBaseAssessmentEdge
new_schema_annotations:
  - {annotation: loom_role, values: [hidden, collapsed, calculated, auto_generated]}
```

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

- Added `CoordinateLocationBasisEnum` and multivalued
  `StudyCoordinates.coordinate_location_basis` so coordinate records can note
  whether they identify the `exact_site` or use the `nearest_municipality` as
  an approximate proxy.
  - Rationale: coordinate annotations need to distinguish exact study-site
    coordinates from coordinates of the nearest municipality.
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
