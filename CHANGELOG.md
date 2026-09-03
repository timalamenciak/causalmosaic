# Changelog

All notable changes to the active LinkML schema and its supporting governance files are recorded here.

## 0.7.8 > 0.7.9  — Comparators and experimental controls

CAMO 0.7.9 adds a representation for what a causal claim was assessed *relative to*. It is an additive release: existing 0.7.8 records remain valid without migration.

### The problem

Nodes in CAMO represent states and changes in state. An experimental control is neither — no state changed in the control arm — but it is not neutral either. The same reported effect means different things measured against untreated plots, against undisturbed remnant, or against the same plots before treatment, and until now nothing in the schema recorded which was meant.

Modelling a control as a node does not work. A single shared control node becomes a hub asserting equivalence between untreated grassland, untreated peatland and untreated reef; a per-study control node is a singleton that can never merge with another study's, which defeats the type-level synthesis the schema exists for. The comparison basis is a property of the causal inference, so it is annotated on the edge, alongside `mediation`, `moderation` and `context_dependence`.

### Added

#### `ComparatorTypeEnum`

A closed vocabulary for the comparison basis:

* `untreated_control` — concurrent units receiving no manipulation of the tested factor.
* `reference_undisturbed` — an intact system used as a recovery benchmark or restoration target.
* `pre_treatment_baseline` — the same units measured before the intervention.
* `alternative_treatment` — a different active arm.
* `passive_management_arm` — a real do-nothing or cease-disturbance decision a practitioner could take.
* `spatial_or_temporal_control` — an unimpacted site or period in an observational design.
* `not_reported` — no comparator is stated or recoverable. Informative: it downgrades certainty rather than leaving a silent gap.
* `not_applicable` — the claim is mechanistic or definitional and invokes no contrast.

#### `ComparatorAnnotation`

An inlined annotation class with `status`, `comparator_type`, `comparator_description` (the arm as the source names it) and `comparator_node_id`.

`passive_management_arm` is the value that carries the boundary. Where a "control" arm is a decision a land manager could actually make — natural regeneration, withdrawal of grazing — it is a management intervention in its own right, gets an ordinary node, and is referenced by `comparator_node_id`. Where the arm exists only to be measured against, it gets no node.

#### `CausalEdge.comparator`

Optional Layer 1 slot of range `ComparatorAnnotation`. Unlike the Layer 3 feature slots it carries no `camo:` slot URI, since the comparator is not one of the sixteen causal features.

### Changed

* Narrowed the description of the `unchanged` state-or-change qualifier. It previously read "(control, null result, baseline)", collapsing three distinct concepts into one docstring. It now covers null results only; controls and baselines are `ComparatorTypeEnum` values.

### Annotation guidance

Two rules follow from this release and belong in the annotation guide rather than the schema:

* **Node a control arm only when it is a decision.** Three tests, in order: could a practitioner choose it? Does the source report its outcomes as findings in their own right, or only as a yardstick? Would the resulting node ever merge with a node from another paper? A "no" at any point means comparator, not node.
* **A factor held constant across all arms is not a cause of any difference.** Where an intervention was applied to every arm including the control, the study cannot attribute any between-arm outcome to it, and it should not be annotated as a cause in that document's graph.

---

## 0.7.7 > 0.7.8  — TDWG interoperability, evidence aggregation, and BBN support

CAMO 0.7.8 strengthens interoperability with TDWG standards, improves the representation of multi-document evidence bases, and adds schema features needed for fuzzy cognitive maps, Bayesian belief networks, and evidence gap maps.

This release includes several schema changes that require migration of existing CAMO records.

### Added

#### Darwin Core and Humboldt Extension alignment

* Added the `dwc:` and `dwciri:` Darwin Core namespaces.
* Added the `eco:` namespace for the Humboldt Extension.
* Added Darwin Core mappings for study geography:

  * `StudyCoordinates.latitude` → `dwc:decimalLatitude`
  * `StudyCoordinates.longitude` → `dwc:decimalLongitude`
  * `StudyCoordinates.coordinate_uncertainty_m` → `dwc:coordinateUncertaintyInMeters`
  * `StudyCoordinates.elevation_m` → `dwc:verbatimElevation` as a close mapping
  * `SourceDocument.study_country` → `dwc:country`
  * `SourceDocument.study_state_or_province` → `dwc:stateProvince`
  * study-period start and end → `dwc:eventDate` as close mappings
* Added `StudyCoordinates.geodetic_datum`, defaulting to WGS84 and mapped to `dwc:geodeticDatum`.
* Added the canonical `wd:` namespace for Wikidata entity identifiers.

#### Structured sampling effort

Replaced the free-text `SourceDocument.study_sample_size` field with a structured representation:

* `sample_size_value`
* `sample_size_unit`
* `sampling_effort_protocol`
* `is_sampling_effort_reported`

The new fields carry close mappings to Darwin Core and the Humboldt Extension where appropriate. This distinguishes numeric effort, its unit, its reporting protocol, and explicit non-reporting.

#### Source-document normalization

* Added required `SourceDocument.document_id` as the identifier for source records.
* Added multivalued `CausalGraph.source_documents` for graphs assembled from multiple publications.
* Added a document-reference representation for `CausalEdge.source_document`, allowing edges to refer to centrally defined source metadata rather than duplicating bibliographic records.

This establishes the basis for multi-paper evidence graphs and evidence-base-level synthesis without repeatedly embedding the same publication metadata.

#### Evidence-base aggregation

Added the following fields to `EvidenceBaseAssessmentEdge`:

* `aggregate_fcm_weight` — aggregate fuzzy-cognitive-map edge weight constrained to `[-1, 1]`.
* `aggregate_fcm_weight_source` — records how the aggregate weight was derived, such as meta-analysis, weighted member edges, expert elicitation, or certainty down-weighting.
* `account_coverage` — records the philosophical accounts represented across the supporting evidence base.

These fields allow aggregate evidence edges, rather than individual article-level claims, to serve directly as inputs to downstream causal models.

#### Qualifier families

Added `QualifierFamilyEnum` with four mutually exclusive state-space families:

* `directional_change`
* `presence`
* `membership_change`
* `process_phase`

`StateOrChangeQualifierEnum` values are assigned to these families so that downstream systems can determine which qualifier sets constitute coherent variable state spaces.

This is particularly important for Bayesian-network construction, where, for example, `{increased, decreased, unchanged}` represents a different variable type from `{present, absent}`.

#### BBN variable grouping

Added calculated `CausalNode.variable_key`, composed from:

* `entity_term`
* `measured_attribute`
* `applied_to`

The field provides a stable grouping key for projecting CAMO nodes into Bayesian-network variables.

#### Source-text context

Added `TextSpan.section`, using the existing `DocumentSectionEnum`, so evidence can retain whether a claim was extracted from the methods, results, discussion, conclusion, or another document section.

#### Agent identifiers

* Added the `camo_agent:` namespace for model and pipeline identifiers.
* `CausalNode.annotator` now supports resolvable ORCID and CAMO-agent identifiers and validates their identifier form.
* `CausalEdge.annotator` was widened to accept either a URI/CURIE or string identifier.

### Changed

#### Bradford Hill crosswalk

Replaced the special `maps_to_account: all` sentinel on the Bradford Hill `temporality` viewpoint with an explicit list of all current philosophical accounts:

`counterfactual | probabilistic | interventionist | transmission | mechanistic | regularity | inus_component | agency`

Consumers of `maps_to_account` should therefore treat the annotation as a pipe-delimited list, including when only one account is present.

#### Explicit null-result semantics

`StateOrChangeQualifierEnum.unchanged` now renders explicitly as:

`no change in`

This distinguishes a measured null result from an absent annotation.

#### Ecosystem scope

`ContextAnnotation.ecosystem_scope` is now constrained to `EcosystemFunctionalGroupEnum` rather than unrestricted text, aligning it with the IUCN Global Ecosystem Typology vocabulary already used elsewhere in CAMO.

#### Causal-feature metadata

* Corrected the Layer 3 feature count from 15 to 16.
* Added `slot_uri: camo:context_dependence` to `CausalEdge.context_dependence`.

#### Schema versioning

Updated the `CausalGraph.schema_version` default from the stale `0.4.0` value to `0.7.8`.

### Removed

#### `StateOrChangeQualifierEnum.unspecified`

Removed the `unspecified` qualifier.

An absent `state_or_change_qualifier` now represents information that was not specified, while `unchanged` explicitly represents a measured null or baseline result.

#### `NodeCategoryEnum`

Removed the unused `NodeCategoryEnum`.

Intervention, outcome, mediator, and similar roles are contextual positions within causal relationships rather than intrinsic categories of nodes. Downstream evidence-gap-map axes should instead be derived from graph structure and existing CAMO fields.

#### `RenderingTargetEnum`

Removed `RenderingTargetEnum` from the core CAMO schema.

Rendering targets such as fuzzy cognitive maps, evidence gap maps, Bayesian networks, causal diagrams, and RAG indices are properties of downstream consumers rather than instance data represented by CAMO.

#### Duplicate evidence-base fields

Removed the direct:

* `EvidenceBaseAssessmentEdge.evidence_types`
* `EvidenceBaseAssessmentEdge.evidence_objects`

Aggregate records now use the existing inlined `evidential_basis` structure, giving article-level and evidence-base-level edges a consistent representation of evidential basis.

#### Unused prefixes and deprecated material

Removed unused namespace declarations for:

* `edge`
* `schema`
* `skos`
* `dcterms`
* `prov`
* `RO`
* `SEPIO`
* `OBI`

Also removed the commented-out `capacity` philosophical-account block.

## Migration notes

### `SourceDocument` now requires an identifier

Existing source-document records must gain a `document_id`.

Where possible, use the DOI as the document identifier. Otherwise, assign a stable local identifier.

### Replace `study_sample_size`

Existing:

```yaml
study_sample_size: "12 plots per treatment"
```

should be migrated, where unambiguous, to:

```yaml
sample_size_value: 12
sample_size_unit: plots
is_sampling_effort_reported: true
```

Do not infer units that are not stated by the source. Ambiguous descriptions should be retained through `sampling_effort_protocol` rather than converted into invented numeric values.

### Remove `unspecified` qualifiers

Existing:

```yaml
state_or_change_qualifier: unspecified
```

should become an absent/null `state_or_change_qualifier`.

`unchanged` should only be used when no change was actually measured or reported.

### Update aggregate evidence records

Move direct aggregate `evidence_types` and `evidence_objects` values into the record's `evidential_basis`.

Consumers producing FCMs may now read `aggregate_fcm_weight` directly from `EvidenceBaseAssessmentEdge`.

### Update Bradford Hill consumers

Code consuming `BradfordHillViewpointEnum.maps_to_account` should split values on `|` and trim whitespace.

The `temporality` mapping is no longer represented by the special value `all`.

### Update rendering consumers

Code referring directly to `NodeCategoryEnum` or `RenderingTargetEnum` must be updated. These enums are no longer part of the CAMO schema.

## Summary

CAMO 0.7.8 moves the schema toward a clearer separation between:

1. **article-level causal claims,**
2. **source-document and study metadata,**
3. **derived evidence-base assessments,** and
4. **downstream model/rendering concerns.**

The release also improves TDWG interoperability and introduces the structured state-space and aggregation metadata needed to project CAMO evidence into fuzzy cognitive maps, Bayesian belief networks, and evidence gap maps.


## 0.7.7 Merge taxonomic_scope into applied_to (2026-07-16)

### Machine-readable summary

```yaml
removed_slots:
  - slot: taxonomic_scope
    class: CausalNode
updated_slots:
  - slot: applied_to
    class: CausalNode
    change: >-
      Extended from environmental_process / management_intervention nodes only
      to all node types. Description updated to document dual scope/target roles.
updated_descriptions:
  - class: CausalNode
    note: two-path model updated to reference applied_to instead of taxonomic_scope
  - enum: EntityTypeEnum
    value: taxon
    note: path 2 updated to reference applied_to instead of taxonomic_scope
  - class: AppliedToEntity
    note: description updated to document scope vs. target roles
updated_metadata:
  - version: 0.7.6 -> 0.7.7
```

### Detailed changes

- Removed `taxonomic_scope` from `CausalNode`.
  - Rationale: `taxonomic_scope` and `applied_to` captured structurally
    similar information — both record what entity or entities a node relates
    to — but through different fields routed by node type. There is no case
    where `taxonomic_scope` is appropriate but `applied_to` is not, since
    the distinction between "scoping a measurement" and "targeting a process"
    is already fully carried by the node's own `entity_type`. Maintaining two
    separate fields imposed a routing rule ("use taxonomic_scope on variables,
    applied_to on processes") that added annotator overhead without adding
    information. Additionally, `taxonomic_scope` was a flat `any_of [uriorcurie,
    string]` while `AppliedToEntity` (the range of `applied_to`) provides the
    richer `entity_type + entity_term` structure and can reference any entity
    type, not just taxa.

- Extended `applied_to` to all `CausalNode` types (previously restricted to
  `environmental_process` and `management_intervention` nodes).
  - `applied_to` now serves two roles, documented in the slot description:
    - **Scope role** (environmental_variable nodes): lists the taxa or
      ecological guilds whose measurements are aggregated. Accepts Wikidata
      QIDs (preferred) or free-text guild names for groups with no Wikidata
      resolution (tracked in the project NAO list). Does not apply to
      single-taxon nodes, which continue to use `entity_type: taxon` with the
      QID in `entity_term`.
    - **Target role** (environmental_process and management_intervention
      nodes): names the directional target entity. Behaviour is unchanged
      from 0.7.6.

- Updated the `CausalNode` class description and `EntityTypeEnum.taxon`
  permissible value description to reference `applied_to` in the two-path
  model (path 2) instead of `taxonomic_scope`.

- Updated the `AppliedToEntity` class description to document the scope vs.
  target dual roles.

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
