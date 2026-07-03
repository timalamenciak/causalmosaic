# Causal Mosaic schema reference

This page documents the classes and slots in `camo-0.7.2.yaml` (schema version `0.7.2`). The schema declares slots as inline class attributes rather than in a top-level `slots:` section; each table below is therefore the complete slot contract for that class.

## Reading the tables

- **Range** names the LinkML scalar, enum, or class accepted by the slot. "or" indicates an `any_of` union.
- **Cardinality** is `1` for required single-valued slots, `0..1` for optional single-valued slots, `1..*` for required multivalued slots, and `0..*` for optional multivalued slots.
- **Constraints and metadata** records identifiers, semantic URIs, defaults, numeric bounds, inlining, and schema annotations. `None` means that the schema declares no additional constraint.
- The descriptions and constraints below are taken directly from the schema. Enum permissible values are intentionally not duplicated on this classes-and-slots page.

## Class index

| Class | Role | Slots |
|---|---|---:|
| [CausalGraph](#class-causalgraph) | Tree root | 6 |
| [GraphProvenance](#class-graphprovenance) | Nested class | 8 |
| [CausalNode](#class-causalnode) | Nested class | 10 |
| [TextSpan](#class-textspan) | Nested class | 5 |
| [SourceDocument](#class-sourcedocument) | Nested class | 15 |
| [StudyCoordinates](#class-studycoordinates) | Nested class | 8 |
| [TemporalExtent](#class-temporalextent) | Nested class | 5 |
| [CausalEdge](#class-causaledge) | Nested class | 35 |
| [EvidenceBaseAssessmentEdge](#class-evidencebaseassessmentedge) | Nested class | 41 |
| [DirectionAnnotation](#class-directionannotation) | Nested class | 2 |
| [MediationAnnotation](#class-mediationannotation) | Nested class | 3 |
| [ModerationAnnotation](#class-moderationannotation) | Nested class | 3 |
| [StrengthAnnotation](#class-strengthannotation) | Nested class | 5 |
| [ContextAnnotation](#class-contextannotation) | Nested class | 5 |
| [EvidentialBasis](#class-evidentialbasis) | Nested class | 2 |

## Class: CausalGraph

A labeled property graph of causal claims extracted from scientific literature. The top-level container for nodes and edges.

**Tree root:** yes

**Declared slots:** 6

| Slot | Range | Cardinality | Constraints and metadata | Description |
|---|---|---:|---|---|
| `graph_id` | `string` | `1` | identifier | Unique identifier for this graph or sub-graph. |
| `schema_version` | `string` | `1` | default: `string(0.4.0)` | Schema version for compatibility tracking. |
| `provenance` | `GraphProvenance` | `1` | None | Provenance metadata for the graph. |
| `nodes` | `CausalNode` | `1..*` | inlined as list | All causal entities (causes, effects, mediators, moderators). |
| `edges` | `CausalEdge` | `1..*` | inlined as list | All annotated causal relationships. |
| `evidence_base_assessments` | `EvidenceBaseAssessmentEdge` | `0..*` | inlined as list | Derived evidence-base-level assessments over sets of article-level causal edges. These should be regenerated when new relevant CausalEdge records are added. |

## Class: GraphProvenance

Provenance and metadata for a causal graph.

**Declared slots:** 8

| Slot | Range | Cardinality | Constraints and metadata | Description |
|---|---|---:|---|---|
| `ontology_framework` | `string` | `0..1` | default: `string(ELMO + CAMO)` | Ontology and causal annotation frameworks used by this graph. |
| `elm_version` | `string` | `0..1` | None | Version of the Ecolink Model Ontology entity structure used. |
| `causal_mosaic_version` | `string` | `0..1` | None | Version of the CAMO annotation framework used. |
| `annotation_guide_version` | `string` | `0..1` | None | Version of the annotation guide used to create the graph. |
| `created` | `datetime` | `0..1` | None | Date and time when the graph metadata was created. |
| `source_corpus` | `string` | `0..1` | None | Description of the annotated corpus or literature set. |
| `annotation_protocol` | `uri` | `0..1` | None | DOI or URL of the annotation protocol document. |
| `project` | `string` | `0..1` | None | Project name (e.g., 'EcoWeaver', 'Grassland Systematic Map'). |

## Class: CausalNode

A node in the labeled property graph representing a causally active ecological entity — specifically, a state or change in state of an environmental variable or process. Merges ELMO's entity structure (Alamenciak et al. 2025) with CAMO's annotation requirements. Key design principle: causation in ecology is represented between states or changes in state, not between things alone. A taxon does not cause anything by itself; the causally relevant annotation concerns the state or change of an attribute of a taxon. Therefore each node decomposes into: entity → what thing (taxon, chemical, abiotic factor, process) attribute → what measurable property (abundance, cover, rate) qualifier → whether or how it changed (present, increased, etc.) The human-readable 'name' is the composed form: "Increased abundance of Canis lupus". The structured fields allow decomposed querying: "show me all claims involving Canis lupus" or "all claims about abundance changes" or "all claims where abundance decreased." This pattern corresponds to ELMO's subject/object value + derivative qualifier + state/change qualifier structure.

**Declared slots:** 10

| Slot | Range | Cardinality | Constraints and metadata | Description |
|---|---|---:|---|---|
| `id` | `uriorcurie` | `1` | identifier<br>`loom_role`: auto_generated | Unique node identifier. This field is populated automatically by the annotation tool; annotators do not need to fill it in. If entity_term is provided, Loom uses that CURIE; otherwise, Loom generates causal_mosaic:{slugified_name}_{4-char-hash}. |
| `name` | `string` | `1` | None | Human-readable composed label for the node. Should express the full semantic content: "Increased wolf population abundance" or "Prescribed burning process" or "Elevated soil nitrogen." This is what appears in Rosetta Statements and graph visualizations. |
| `entity_type` | `EntityTypeEnum` | `0..1` | `note`: Recommended but not required; inferred from entity_term when missing. | High-level category of the ecological entity, for semantic disambiguation. |
| `entity_term` | `uriorcurie` or `string` | `1` | `note`: For taxa use Wikidata; for chemicals CHEBI; for environments ENVO; for processes GO or ENVO process terms; for qualities PATO. | The core ecological entity as an ontology CURIE, or free text when no cached ontology term matches yet. This is the "what thing" — the taxon, chemical, abiotic factor, or process class, and is the authoritative ontology grounding for the node's entity. Corresponds to ELMO's subject_value / object_value slot. Examples: WD:18498 (Canis lupus), CHEBI:24279 (glucosinolate), ENVO:01000253 (grassland). Secondary ontology crosswalks, if needed, should be maintained outside article annotations in SSSOM files. |
| `measured_attribute` | `uriorcurie` or `string` | `0..1` | `examples`: PATO:0000070 (abundance), PATO:0000918 (width), PATO:0000574 (density), PATO:0001019 (mass), PATO:0000033 (concentration), PATO:0001708 (1-D extent/cover), GO:0008150 (biological process for rates) | The measurable attribute of the entity that participates in the causal relationship. Corresponds to ELMO's derivative_qualifier slot. Together with entity_term and state_or_change_qualifier, forms the full semantic content: "state or change qualifier of attribute of entity." This is the authoritative ontology grounding for the measured attribute. Use PATO terms for qualities (abundance, density, cover, height), GO terms for process rates, or free text if no ontology term exists. |
| `state_or_change_qualifier` | `StateOrChangeQualifierEnum` | `0..1` | None | Qualifier indicating the state or change in the attribute, including cases where the attribute is present, absent, unchanged, or unspecified. Corresponds to ELMO's direction_qualifier slot. Combined with entity_term and measured_attribute to produce the node's full meaning: e.g., entity=Canis lupus, attribute=abundance, qualifier=increased → "increased abundance of Canis lupus." |
| `source_spans` | `TextSpan` | `0..*` | inlined as list | Text spans grounding this node in the source document. |
| `embedding_text` | `string` | `0..1` | `loom_role`: hidden | Concatenated text used for generating the embedding vector. Typically: name + description + synonym list. |
| `embedding_vector` | `string` | `0..1` | `loom_role`: hidden<br>`note`: Serialized float32 array; decode with numpy/arrow | Pre-computed embedding vector for RAG retrieval. Stored as serialized float array. Generated by the indexing pipeline, not by annotators. |
| `annotator` | `string` | `0..1` | `loom_role`: hidden | Annotator identifier (human ORCID or model ID). |

## Class: TextSpan

A span of text in the source document, for provenance and RAG.

**Declared slots:** 5

| Slot | Range | Cardinality | Constraints and metadata | Description |
|---|---|---:|---|---|
| `text` | `string` | `1` | None | Verbatim text. |
| `start_char` | `integer` | `0..1` | `loom_role`: hidden | Character offset start in source document. |
| `end_char` | `integer` | `0..1` | `loom_role`: hidden | Character offset end. |
| `sentence_id` | `string` | `0..1` | `loom_role`: hidden | Sentence identifier. |
| `paragraph_id` | `string` | `0..1` | `loom_role`: hidden | Paragraph identifier. |

## Class: SourceDocument

Bibliographic metadata and study-level context for the source document. Supports RAG retrieval, evidence gap map construction, and spatiotemporal analysis of the evidence base. Spatial fields enable map-based evidence visualization and proximity-weighted retrieval. Temporal fields enable tracking of when evidence was collected and whether causal relationships vary over time.

**Declared slots:** 15

| Slot | Range | Cardinality | Constraints and metadata | Description |
|---|---|---:|---|---|
| `doi` | `string` | `0..1` | None | Digital Object Identifier for the source document. |
| `pmid` | `string` | `0..1` | None | PubMed identifier for the source document. |
| `title` | `string` | `0..1` | None | Title of the source document. |
| `authors` | `string` | `0..*` | None | Authors of the source document. |
| `year` | `integer` | `0..1` | None | Publication year. |
| `journal` | `string` | `0..1` | None | Journal or publication venue for the source document. |
| `study_coordinates` | `StudyCoordinates` | `0..*` | inlined as list | Coordinate set or sets reported for the study. Use one entry per reported centroid or bounded study area. This supports multi-site studies without requiring site names that the source may not report. Coordinates enable map-based evidence gap maps, proximity-weighted retrieval ("show me evidence from sites near mine"), and spatial analysis of where causal relationships have been tested. |
| `study_country` | `string` | `0..1` | None | Country or countries where the study was conducted. Use country names or ISO 3166-1 alpha-2 codes where practical. If multiple countries are reported, separate them with semicolons. |
| `study_state_or_province` | `string` | `0..1` | None | State, province, territory, or comparable administrative region where the study was conducted. If multiple regions are reported, separate them with semicolons. |
| `study_period_start` | `string` | `0..1` | `format`: ISO 8601 (YYYY, YYYY-MM, or YYYY-MM-DD)<br>`examples`: 2015, 2015-06, 2015-06-15 | Start date of data collection. Not the publication date — when the fieldwork or measurements actually began. ISO 8601 format. Can be year-only (2015), year-month (2015-06), or full date (2015-06-15). For paleontological or historical ecology studies, use negative years or descriptive text in study_temporal_note. |
| `study_period_end` | `string` | `0..1` | `format`: ISO 8601 (YYYY, YYYY-MM, or YYYY-MM-DD) | End date of data collection. Same format as study_period_start. |
| `study_duration_months` | `float` | `0..1` | `loom_role`: calculated | Duration of the study in months. Computed from start/end if both are provided, or entered directly if the paper reports duration without specific dates. Useful for filtering: "show me only studies with at least 24 months of monitoring." |
| `study_temporal_note` | `string` | `0..1` | None | Free-text note for temporal context that doesn't fit structured fields. E.g., "data collected over three growing seasons", "historical records from 1850-1950", "pollen core spanning 6,700 years." |
| `study_design` | `EvidenceTypeEnum` | `0..1` | None | Study design classification for EGM quality assessment. |
| `study_sample_size` | `string` | `0..1` | None | Sample size or replication level reported in the study. Free text: "n = 12 plots per treatment", "47 studies", "182 survey respondents." |

## Class: StudyCoordinates

Structured coordinate representation for a study location. At minimum, provide latitude and longitude as a centroid when coordinates are reported. Optionally provide a bounding box for larger study areas and elevation. Coordinates should be in WGS 84 (EPSG:4326), which is what GPS devices and most ecology papers report.

**Declared slots:** 8

| Slot | Range | Cardinality | Constraints and metadata | Description |
|---|---|---:|---|---|
| `latitude` | `float` | `0..1` | minimum: `-90.0`<br>maximum: `90.0` | Latitude of the study coordinate centroid in decimal degrees (WGS 84). Positive = North, negative = South. E.g., 43.2642 for southern Ontario. |
| `longitude` | `float` | `0..1` | minimum: `-180.0`<br>maximum: `180.0` | Longitude of the study coordinate centroid in decimal degrees (WGS 84). Positive = East, negative = West. E.g., -81.7567 for southern Ontario. |
| `elevation_m` | `float` | `0..1` | None | Elevation of the coordinate location in metres above sea level, if reported. Useful for montane and altitudinal gradient studies. |
| `coordinate_uncertainty_m` | `float` | `0..1` | None | Uncertainty radius in metres around the centroid coordinates. If the paper reports coordinates to the nearest minute (~1850m) vs. second (~30m) vs. high-precision GPS (~5m), this field captures that. Follows Darwin Core dwc:coordinateUncertaintyInMeters. |
| `bbox_north` | `float` | `0..1` | `loom_role`: collapse | Northern boundary of study area bounding box (decimal degrees). |
| `bbox_south` | `float` | `0..1` | `loom_role`: collapse | Southern boundary of study area bounding box (decimal degrees). |
| `bbox_east` | `float` | `0..1` | `loom_role`: collapse | Eastern boundary of study area bounding box (decimal degrees). |
| `bbox_west` | `float` | `0..1` | `loom_role`: collapse | Western boundary of study area bounding box (decimal degrees). |

## Class: TemporalExtent

The temporal window over which a causal effect was observed or measured. Distinct from the study period (when was fieldwork done): this captures the timescale of the causal relationship itself. For example, a study conducted from 2015-2020 might report that invasive removal led to native recovery "within three growing seasons" — the study period is 5 years, but the temporal extent of the causal effect is 3 growing seasons (~18 months). This is important for practitioners who need to know how long to wait for results, and for meta-analysts investigating whether effect sizes vary with observation duration.

**Declared slots:** 5

| Slot | Range | Cardinality | Constraints and metadata | Description |
|---|---|---:|---|---|
| `duration_months` | `float` | `0..1` | None | Duration of the observed causal effect in months. E.g., 36 for "within three years", 6 for "one growing season." |
| `duration_text` | `string` | `0..1` | None | Free-text description of the temporal extent as stated in the source. E.g., "within three growing seasons", "over a 20-year period", "immediately following treatment." |
| `lag_months` | `float` | `0..1` | None | Time lag between the cause and the onset of the effect, in months. E.g., if invasive removal happens in year 0 and native recovery begins in year 2, lag = 24. Null if the effect is immediate or lag is not reported. |
| `observation_grain` | `string` | `0..1` | `examples`: daily, weekly, monthly, seasonal, annual, decadal, centennial | The temporal grain at which the effect was measured. E.g., "daily", "monthly", "seasonal", "annual", "decadal." Affects interpretability — a relationship detected at annual grain may not hold at daily grain. |
| `observation_seasons` | `string` | `0..*` | None | Seasons during which the effect was observed, if seasonally restricted. E.g., ["spring", "summer"] for a growing-season study. Important for context-dependent effects that may not hold year-round. |

## Class: CausalEdge

An edge in the labeled property graph representing a causal relationship. Carries all four annotation layers as properties: Layer 1: Claim strength and linguistic expression Layer 2: Philosophical account classification Layer 3: Fifteen causal features Layer 4: Evidential basis Plus rendering metadata for each downstream target.

**Declared slots:** 35

| Slot | Range | Cardinality | Constraints and metadata | Description |
|---|---|---:|---|---|
| `id` | `string` | `1` | identifier<br>`loom_role`: auto-generated | Unique edge identifier. |
| `subject` | `CausalNode` | `1` | None | Node ID of the cause entity. |
| `predicate` | `CausalPredicateEnum` | `1` | None | Edge type from controlled vocabulary. |
| `object` | `CausalNode` | `1` | None | Node ID of the effect entity. |
| `negated` | `boolean` | `0..1` | default: `boolean(false)` | True if the claim is that the relationship does NOT hold. |
| `claim_strength` | `ClaimStrengthEnum` | `1` | None | How strong is the causal language used? |
| `original_sentence` | `string` | `0..1` | None | The full original sentence(s) from which this edge was extracted. Preserved for RAG retrieval and rendering validation. |
| `ecosystem_context` | `EcosystemFunctionalGroupEnum` | `0..1` | `elm_correspondence`: ecosystem_context_qualifier<br>`examples`: temperate_subhumid_grasslands, seagrass_meadows | The IUCN Global Ecosystem Typology Level 3 ecosystem functional group in which this causal relationship was observed, represented by an ELMO ecosystem type term. Use this edge-level field for the ecosystem setting of the causal claim. |
| `philosophical_accounts` | `PhilosophicalAccountEnum` | `1..*` | None | Which philosophical account(s) of causation does this claim invoke? A claim may invoke multiple accounts simultaneously. |
| `necessity` | `FeatureAssertionEnum` | `0..1` | URI: `camo:necessity`<br>default: `string(not_addressed)` | Whether the cause is characterized as necessary for the effect. |
| `sufficiency` | `FeatureAssertionEnum` | `0..1` | URI: `camo:sufficiency`<br>default: `string(not_addressed)` | Whether the cause is characterized as sufficient for the effect. |
| `direction` | `DirectionAnnotation` | `0..1` | URI: `camo:direction`<br>inlined | Annotation of causal direction and evidence for direction. |
| `temporal_ordering` | `FeatureAssertionEnum` | `0..1` | URI: `camo:temporal_ordering`<br>default: `string(not_addressed)` | Whether temporal ordering between cause and effect is addressed. |
| `mediation` | `MediationAnnotation` | `0..1` | URI: `camo:mediation`<br>inlined | Annotation of any mediating pathway between cause and effect. |
| `moderation` | `ModerationAnnotation` | `0..1` | URI: `camo:moderation`<br>inlined | Annotation of any moderator or effect modifier for the causal relationship. |
| `strength` | `StrengthAnnotation` | `0..1` | URI: `camo:strength`<br>inlined | Annotation of the reported strength or magnitude of the causal relationship. |
| `specificity` | `FeatureAssertionEnum` | `0..1` | URI: `camo:specificity`<br>default: `string(not_addressed)` | Whether the causal relationship is characterized as specific to particular causes or effects. |
| `stability` | `FeatureAssertionEnum` | `0..1` | URI: `camo:stability`<br>default: `string(not_addressed)` | Whether the causal relationship is characterized as stable across contexts or conditions. |
| `token_or_type` | `TokenTypeEnum` | `0..1` | URI: `camo:token_or_type`<br>default: `string(not_addressed)` | Whether the claim concerns a specific causal instance or a general causal type. |
| `determinism` | `DeterminismEnum` | `0..1` | URI: `camo:determinism`<br>default: `string(not_addressed)` | Whether the causal relationship frames the underlying process as deterministic or indeterministic, or uses probability only to express epistemic uncertainty. |
| `proximate_distal` | `ProximateDistalEnum` | `0..1` | URI: `camo:proximate_distal`<br>default: `string(not_addressed)` | Whether the cause is positioned as proximate, distal, or both. |
| `contributing_sole` | `ContributingSoleEnum` | `0..1` | URI: `camo:contributing_sole`<br>default: `string(not_addressed)` | Whether the cause is presented as a sole cause or contributing cause. |
| `reversibility` | `ReversibilityEnum` | `0..1` | URI: `camo:reversibility`<br>default: `string(not_addressed)` | Whether removing the cause is characterized as reversing the effect. |
| `proportionality` | `FeatureAssertionEnum` | `0..1` | URI: `camo:proportionality`<br>default: `string(not_addressed)` | Whether the cause is characterized at a proportional level of specificity. |
| `context_dependence` | `ContextAnnotation` | `0..1` | inlined | Annotation of scope conditions or context dependence for the causal relationship. |
| `evidential_basis` | `EvidentialBasis` | `0..1` | inlined | Annotation of the evidence type and evidence object supporting the claim. |
| `fcm_weight` | `float` | `0..1` | minimum: `-1.0`<br>maximum: `1.0`<br>`loom_role`: hidden | Numeric edge weight for Fuzzy Cognitive Map rendering. Range: -1.0 (strong negative) to +1.0 (strong positive). Derived from predicate sign, claim_strength, and strength annotation. Can be overridden by expert elicitation. |
| `fcm_weight_source` | `string` | `0..1` | `examples`: derived_from_schema, expert_elicitation, meta_analysis_effect_size<br>`loom_role`: hidden | How the FCM weight was determined. |
| `temporal_extent` | `TemporalExtent` | `0..1` | inlined | The temporal window over which this causal effect was observed. Distinct from the study period in source_document (when fieldwork was done): this captures the timescale of the causal relationship itself. E.g., "native recovery occurred within three growing seasons of invasive removal." Enables filtering by effect duration and analysis of whether effect sizes vary with observation window. |
| `source_spans` | `TextSpan` | `1..*` | inlined as list | Text spans grounding this edge. |
| `source_document` | `SourceDocument` | `0..1` | inlined | Bibliographic and study-level metadata for the source document. |
| `annotator` | `string` | `0..1` | None | Annotator identifier (human ORCID or model ID). |
| `annotation_confidence` | `float` | `0..1` | minimum: `0.0`<br>maximum: `1.0` | Annotator confidence in the overall annotation, 0.0-1.0. |
| `annotation_timestamp` | `datetime` | `0..1` | None | Date and time when the edge annotation was created. |
| `annotation_notes` | `string` | `0..1` | None | Free-text notes from the annotator about this edge. |

## Class: EvidenceBaseAssessmentEdge

A derived evidence-base-level assessment for a causal relationship, computed or curated from multiple article-level CausalEdge records that refer to the same or comparable subject-predicate-object relationship. This class is intended for synthesis and graph analysis, not for per-article annotation. It can be regenerated when the evidence base changes, reducing annotator effort by avoiding repeated aggregate judgments such as Russo-Williamson satisfaction on every article-level edge.

**Declared slots:** 41

| Slot | Range | Cardinality | Constraints and metadata | Description |
|---|---|---:|---|---|
| `id` | `string` | `1` | identifier | Unique identifier for this evidence-base assessment edge. |
| `subject` | `CausalNode` | `1` | None | Canonical cause node being assessed. |
| `predicate` | `CausalPredicateEnum` | `1` | None | Aggregate causal predicate being assessed. |
| `object` | `CausalNode` | `1` | None | Canonical effect node being assessed. |
| `included_edge_ids` | `string` | `0..*` | None | Article-level CausalEdge identifiers included in this aggregate assessment. |
| `excluded_edge_ids` | `string` | `0..*` | None | Article-level CausalEdge identifiers reviewed but excluded from this aggregate assessment. |
| `inclusion_criteria` | `string` | `0..1` | None | Criteria used to decide which article-level edges belong in this aggregate assessment. |
| `exclusion_rationale` | `string` | `0..1` | None | Free-text rationale for exclusions, if any. |
| `evidence_types` | `EvidenceTypeEnum` | `0..*` | None | Evidence types represented across the included edges. |
| `evidence_objects` | `EvidenceObjectEnum` | `0..*` | None | Evidence objects represented across the included edges: correlation, mechanism, or both. |
| `has_difference_making_evidence` | `AssessmentStatusEnum` | `0..1` | default: `string(not_assessed)` | Aggregate assessment of whether the evidence base contains difference-making evidence for the relationship. |
| `has_production_evidence` | `AssessmentStatusEnum` | `0..1` | default: `string(not_assessed)` | Aggregate assessment of whether the evidence base contains production or mechanistic evidence for the relationship. |
| `russo_williamson_satisfied` | `AssessmentStatusEnum` | `0..1` | default: `string(not_assessed)` | Aggregate assessment of whether the evidence base satisfies the Russo-Williamson requirement for both difference-making and production evidence. |
| `russo_williamson_rationale` | `string` | `0..1` | None | Rationale for the aggregate Russo-Williamson assessment. |
| `bradford_hill_viewpoints` | `BradfordHillViewpointEnum` | `0..*` | None | Bradford Hill viewpoints supported by the aggregated evidence base. Some viewpoints require qualitative judgment and may not be fully programmatically reassessable each time article-level causal edges change. |
| `bradford_hill_count` | `integer` | `0..1` | minimum: `0`<br>maximum: `9` | Count of Bradford Hill viewpoints supported by the aggregated evidence base. |
| `evidence_balance` | `EvidenceBalanceEnum` | `0..1` | default: `string(not_assessed)` | Overall balance of the included evidence. |
| `aggregate_certainty_grade` | `CertaintyGradeEnum` | `0..1` | default: `string(not_assessed)` | Certainty grade assigned to the aggregate evidence-base assessment. |
| `aggregate_certainty_rationale` | `string` | `0..1` | None | Rationale for the aggregate certainty grade. |
| `conflict_summary` | `string` | `0..1` | None | Summary of important conflicts or heterogeneity across included studies. |
| `context_dependence_summary` | `string` | `0..1` | None | Summary of contexts or scope conditions that affect the aggregate relationship. |
| `number_of_studies` | `integer` | `0..1` | minimum: `0` | Number of distinct source studies represented in the included edges. |
| `number_of_supporting_edges` | `integer` | `0..1` | minimum: `0` | Number of included article-level edges supporting the relationship. |
| `number_of_contradicting_edges` | `integer` | `0..1` | minimum: `0` | Number of included article-level edges contradicting the relationship. |
| `number_of_experimental_studies` | `integer` | `0..1` | minimum: `0` | Number of included studies using randomized, quasi-, or natural experimental designs. |
| `number_of_observational_studies` | `integer` | `0..1` | minimum: `0` | Number of included observational studies. |
| `number_of_mechanistic_studies` | `integer` | `0..1` | minimum: `0` | Number of included studies providing mechanistic or production evidence. |
| `aggregate_effect_sign` | `string` | `0..1` | `examples`: positive, negative, mixed, neutral, unknown | Aggregate direction/sign of the effect, if assessed. |
| `aggregate_effect_size` | `string` | `0..1` | None | Aggregate effect size or summary statistic, if available. |
| `effect_size_metric` | `string` | `0..1` | `examples`: risk ratio, odds ratio, standardized mean difference, correlation coefficient | Metric used for the aggregate effect size. |
| `effect_size_summary_method` | `string` | `0..1` | `examples`: meta_analysis, vote_counting, narrative_synthesis, expert_assessment | Method used to summarize effect sizes across studies. |
| `heterogeneity` | `string` | `0..1` | None | Heterogeneity statistic or qualitative heterogeneity summary. |
| `assessment_method` | `string` | `0..1` | `examples`: automated_rule, narrative_synthesis, systematic_review, meta_analysis, expert_review | Method used to generate the evidence-base assessment. |
| `assessment_version` | `string` | `0..1` | None | Version of the assessment method or ruleset. |
| `assessed_by` | `string` | `0..1` | None | Identifier for the person, model, or workflow that generated the assessment. |
| `assessment_timestamp` | `datetime` | `0..1` | None | Date and time when the aggregate assessment was generated. |
| `last_refreshed_at` | `datetime` | `0..1` | None | Date and time when the aggregate assessment was last refreshed. |
| `needs_refresh` | `boolean` | `0..1` | default: `boolean(false)` | True when new relevant article-level CausalEdge records have been added or changed since this assessment was last generated. |
| `refresh_reason` | `string` | `0..1` | None | Reason the assessment needs to be refreshed, if applicable. |
| `assessment_notes` | `string` | `0..1` | None | Free-text notes about the aggregate assessment. |
| `evidential_basis` | `EvidentialBasis` | `0..1` | inlined | Aggregate evidence type and object characterization across included edges. Computed from the `evidence_types` and `evidence_objects` of member article-level edges. |

## Class: DirectionAnnotation

Direction and asymmetry of the causal relationship.

**Declared slots:** 2

| Slot | Range | Cardinality | Constraints and metadata | Description |
|---|---|---:|---|---|
| `status` | `DirectionStatusEnum` | `0..1` | default: `string(not_addressed)` | Assertion status for the direction annotation. |
| `evidence_for_direction` | `DirectionEvidenceEnum` | `0..1` | None | Evidence used to establish the direction of causation. |

## Class: MediationAnnotation

Whether a mediating pathway is identified between cause and effect.

**Declared slots:** 3

| Slot | Range | Cardinality | Constraints and metadata | Description |
|---|---|---:|---|---|
| `status` | `FeatureAssertionEnum` | `0..1` | default: `string(not_addressed)` | Assertion status for the mediation annotation. |
| `mediator_node_ids` | `uriorcurie` | `0..*` | None | Node IDs of mediating entities. These should also appear as separate nodes in the graph with their own edges. |
| `pathway_description` | `string` | `0..1` | None | Free-text description of the mediating pathway. |

## Class: ModerationAnnotation

Whether effect modification by a third variable is noted.

**Declared slots:** 3

| Slot | Range | Cardinality | Constraints and metadata | Description |
|---|---|---:|---|---|
| `status` | `FeatureAssertionEnum` | `0..1` | default: `string(not_addressed)` | Assertion status for the moderation annotation. |
| `moderator_node_ids` | `uriorcurie` | `0..*` | None | Node IDs of moderating entities. |
| `interaction_type` | `InteractionTypeEnum` | `0..1` | None | Type of interaction or effect modification described. |

## Class: StrengthAnnotation

Effect size, magnitude, or dose-response characterization.

**Declared slots:** 5

| Slot | Range | Cardinality | Constraints and metadata | Description |
|---|---|---:|---|---|
| `status` | `FeatureAssertionEnum` | `0..1` | default: `string(not_addressed)` | Assertion status for the strength annotation. |
| `quantitative_value` | `string` | `0..1` | None | Effect size as reported: 'RR = 2.0', 'd = 0.8', '60% reduction'. |
| `quantitative_numeric` | `float` | `0..1` | None | Numeric value extracted for computation (e.g., FCM weight derivation). Use the primary effect size; specify the metric in quantitative_value. |
| `qualitative_descriptor` | `StrengthQualitativeEnum` | `0..1` | None | Qualitative descriptor of the causal relationship strength. |
| `dose_response` | `boolean` | `0..1` | default: `boolean(false)` | Is a dose-response or gradient relationship described? |

## Class: ContextAnnotation

Scope conditions or enabling conditions for the causal relationship.

**Declared slots:** 5

| Slot | Range | Cardinality | Constraints and metadata | Description |
|---|---|---:|---|---|
| `status` | `FeatureAssertionEnum` | `0..1` | default: `string(not_addressed)` | Assertion status for the context annotation. |
| `scope_conditions` | `uriorcurie` or `string` | `0..*` | None | Named conditions under which the relationship holds. E.g., 'in acidic soils', 'at elevations above 2000m', 'in temperate grasslands'. |
| `geographic_scope` | `string` | `0..1` | None | Geographic scope of the claim. |
| `temporal_scope` | `string` | `0..1` | None | Temporal scope of the claim. |
| `ecosystem_scope` | `string` | `0..1` | None | Ecosystem type scope, ideally mapped to IUCN GET. |

## Class: EvidentialBasis

Operationalizes Illari's type/object distinction and the Russo-Williamson Thesis at the article-annotation level. Tracks what kinds of evidence an individual source provides; aggregate criteria are assessed on EvidenceBaseAssessmentEdge.

**Declared slots:** 2

| Slot | Range | Cardinality | Constraints and metadata | Description |
|---|---|---:|---|---|
| `evidence_types` | `EvidenceTypeEnum` | `0..*` | None | TYPE of evidence: what kind of study or reasoning. |
| `evidence_objects` | `EvidenceObjectEnum` | `0..*` | None | OBJECT of evidence: whether it supports correlation, mechanism, or both. Per the Russo-Williamson Thesis. |

## Coverage

This reference covers all **15 classes** and all **153 inline slots** declared in `camo-0.7.2.yaml`.
