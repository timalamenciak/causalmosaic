# Changelog

All notable changes to the active LinkML schema and its supporting governance files are recorded here.

## 0.9.0 > 0.10.0 — Seasons as an enum, statistical significance, life stage, dose levels, composite variables

CAMO 0.10.0 contains **one breaking change**, to `TemporalExtent.observation_seasons`. Everything else is additive. `helpers/migrate_0_9_0_to_0_10_0.py` applies the mechanical steps and reports the ones that need a human. The 0.9.0 schema is archived as `old versions/causal_mosaic_v0.9.0.yaml`.

These changes came out of two schema tests that measured where annotated findings lose information: one over three papers (`threepapers_test`), and a later one over nine papers, which prompted `unit_text`, `composite_variable`, assemblage composition and the restored `certainty_grade`. Each entry below names the measurement that prompted it.

### Breaking: `observation_seasons` is now `SeasonEnum`

In 0.9.0 the slot was `range: string`. Three papers produced **twelve distinct spellings for five seasons** — `late spring` (11 uses), `early spring` (10), `autumn` (6), `spring` (4), `summer` (2), then `mid spring`, `early season`, `late season`, `fledging period` and two entries that are not seasons at all (`year 1 autumn to year 2 early spring`). Free text means `spring`, `late spring` and `late season` do not group in a query, and a reasoner has nothing to resolve.

* **`SeasonEnum`**: ten values. The four cardinal seasons carry exact `meaning:` mappings to NCIT (`NCIT:C94730` winter through `NCIT:C94733` autumn), which defines them astronomically rather than clinically. The sub-seasons (`early_spring`, `mid_spring`, `late_spring`, `early_summer`) take their cardinal season as `broad_mappings`, since no ontology checked carries them as terms. `growing_season` and `dormant_season` are included because sources in strongly seasonal systems report by those instead.

**Migration.** `migrate_0_9_0_to_0_10_0.py` converts the recognised spellings, ignoring case and hyphens, so `late spring`, `late-spring` and `Late Spring` all become `late_spring`. Entries that name no season are **left in place and reported**, because they cannot be moved mechanically: a window spanning seasons or years belongs in the new `time_since_intervention_text`, and a life-history period such as `fledging period` belongs in the new `life_stage_term`. Such a record will not validate until a human moves them, which is the intended behaviour — silently dropping them would lose the only record of when the measurement was taken.

### Added: statistical significance, analysis method, variance explained

Of 36 residue items labelled *statistical detail* across all three papers, 16 were dropped entirely — the highest drop count of any gap in the run. Twenty-five of 237 edges are `no_relationship` with `negated: true`, and with no significance field, "tested and found not significant" is indistinguishable from "never tested". That is the distinction an empty evidence-gap-map cell turns on, and the imprecision domain in GRADE.

* **`SignificanceEnum`**: `significant` and `not_significant` map exactly to `STATO:0000734` and `STATO:0000735`. `marginal` is deliberately unmapped (STATO has the two verdicts but no term for a near miss) and exists because `tended to be (non-significant trend)` was dropped outright in the run, so a hedged near miss entered the graph as a clean null. `not_tested` and `not_reported` are informative values, not placeholders.
* **`AnalysisMethodEnum`**: 11 values. `manova` maps to `STATO:0000454` and `mixed_model` to `STATO:0000189` (with `STATO:0000464`, linear mixed model, as a `narrow_mappings`). `anova` is unmapped pending verification of STATO's parent term for analysis of variance; its verified children are `STATO:0000044`, `:0000045` and `:0000048`. `ordination` is unmapped — no verified STATO equivalent.
* **`StrengthAnnotation.significance`, `.p_value`, `.alpha`, `.analysis_method`**. `p_value` carries two `exact_mappings`, `STATO:0000700` and `OBI:0000175`; both are genuine exact matches in different ontologies, and the STATO–OBI equivalence belongs in an SSSOM crosswalk rather than being resolved here.
* **`EffectMetricEnum.variance_explained`**, with `close_mappings: [STATO:0000564]` (coefficient of determination). Close and not exact, because an ordination axis's share of variance is not an R². The test report asked for this by name, having logged `effect_metric only 'other'; no 'variance explained' metric`.

What is **not** added: ordination axis identity. `CCA axis 1 represented a gradient from high field-layer vegetation cover to high conifer cover` is a proposition about a synthetic variable. It stays in prose.

### Added: life stage, out of `measured_attribute`

*subgroup* was the largest gap by finding share — 34 items, all three papers, 28% of fitted findings — and most of it was one thing: the life stage being counted. With nowhere to put it, the fitting stage put `seedlings` and `year 2 rosettes` into `measured_attribute`, which is part of `variable_key`. So *number of A. petiolata seedlings* and *number of A. petiolata year-2 rosettes* received different variable keys for the wrong reason, nodes would not merge across papers, and the PATO grounding `measured_attribute` is meant to carry was corrupted — "seedlings" is not a quality.

* **`LifeStageEnum`**: eight values, deliberately coarse. Developmental-stage vocabularies are kingdom-specific, and a graph like Cardinal 2012 annotates songbirds, deer and plants together, so one enum cannot ground them all. Values carry `close_mappings` and never `meaning:`, because each spans kingdoms while the source terms do not: `seed_or_seed_bank` to `PO:0001170`, `germinant_or_seedling` to `PO:0007131`, `reproductive_adult` to `UBERON:0018241`. `ramet_or_clonal_unit` is unmapped — PO has clonal structures but no clonal-unit stage.
* **`CausalNode.life_stage` and `.life_stage_term`**, and the same pair on **`AppliedToEntity`**. The enum is the cross-taxon facet a query groups on; the term slot takes the precise CURIE (a PO development-stage term under `PO:0009012` for plants, a UBERON life-cycle-stage term under `UBERON:0000105` for animals) or the source's own wording for distinctions neither keeps, such as "year 1 rosette" against "year 2 rosette".

Two slots rather than one `any_of: [uriorcurie, LifeStageEnum]`, because that shape enforces nothing: `uriorcurie` is a plain string in the generated JSON Schema, so every branch matches and a typo validates. Splitting them means the enum is actually checked. This mirrors how `entity_type` and `entity_term` already divide the same labour.

**Watch the structure-versus-stage trap.** `PO:0008037` is *seedling*, a plant structure; `PO:0007131` is *seedling development stage*. The slot wants the stage. Getting it backwards is the same class of error the 0.8.0 ECO fix corrected.

### Added: when the measurement was taken

`TemporalExtent` recorded how long an effect lasted (`duration_months`) and how long it took to begin (`lag_months`), but not the one thing every paper states: at what point after the intervention a reading was taken. So `in year 2`, `by the second growing season` and `after only 4 years` all went to `duration_text`, which in the run was filled on 36 edges and carried **seven different gap types at once**, while `duration_months` was used five times and `lag_months` never.

* **`TemporalExtent.time_since_intervention_months`**, with `close_mappings: [TIME:numericDuration]`. Close and not exact: OWL-Time pairs a numeric duration with a separate unit, whereas this slot fixes the unit to months in its own name.
* **`TemporalExtent.time_since_intervention_text`**, for the epoch as the source states it.
* **`duration_text` is now documented as effect duration only.** The measurement epoch, the observation seasons and the study's fieldwork dates each have their own slot.

Without this, readings from one study cannot be ordered into a trajectory, so any dynamic or state-transition model built from the graph has unordered observations, and GRADE cannot rate follow-up adequacy: a 4-year null is a different claim from a 4-month null.

### Added: the comparison arm's dose

All 25 *comparison between treatments* items went to `comparator_description` as prose — `relative to lower initial densities`, `9 and 11 ramets/m2 tended to be the most effective (compared with 15 and 20 ramets/m2)`. The numbers are in the sentence and there was no number-shaped slot for them. Of 135 comparator entries in the run, 41 were typed `alternative_treatment`, which in a gradient experiment is wrong, and 51 were `not_reported`.

* **`ComparatorAnnotation.comparator_dose`** (`QuantityValue`) and **`.comparator_dose_level`** (`DoseLevelEnum`). Grounding comes for free: `QuantityValue` already constrains `unit` to QUDT or UO by pattern and grounds `counted_entity` through `AppliedToEntity`, so "ramets of *Sanguinaria canadensis* per square metre" becomes a QUDT unit plus an NCBITaxon ID with no new vocabulary.
* **`ComparatorTypeEnum.alternative_dose_level`**: a different level of the same treatment, rather than a different treatment, which `alternative_treatment` was conflating.

### Added: ordinal dose levels

`QuantityValue` requires one of `numeric_value`, `minimum_value` or `maximum_value`. Sources routinely name a driver level without quantifying it — "under heavy *Odocoileus virginianus* browsing pressure", "at intermediate densities", "higher densities" — and the only place to put those was `dose.verbatim`, producing a `QuantityValue` with no number. Those records do not validate. In a three-paper schema test they were the largest single cause of a 82% validation rate.

* **`DoseLevelEnum`**: eight values. Five ordinal (`absent`, `low`, `intermediate`, `high`, `very_high`), two relative for sources that compare against an arm they do not state (`higher_than_comparator`, `lower_than_comparator`), and `not_specified`.
* **`CausalEdge.dose_level`**: the subject driver's level on that scale. Use alongside `dose` where the source gives both a name and a quantity, and alone where it gives only the name. Like `dose` it is a condition of the claim rather than part of the node, so it does not enter `variable_key`.

`QuantityValue` is **unchanged**: a quantity with only `verbatim` still fails validation, and that is intentional. `QuantityValue` is also used by `CausalNode.components` and `spatial_grain`, where a missing number is a defect rather than a faithful record. A named level belongs in `dose_level`.

The enum is deliberately unmapped. No OBO ontology carries an ordinal driver-intensity scale, and PATO magnitude qualities describe an *outcome* rather than a *driver's* level, so mapping to them would assert something false.

### Added: prefixes for planned ontology grounding

Eight prefixes, none referenced yet, so that planned mappings pass `ci.py` check A2 (which fails on any CURIE whose prefix is undeclared, since it would not expand in the JSON-LD context):

`STATO` (statistics), `OBI`, `IAO` (information artifacts), `SEPIO` (evidence and assertions), `PO` (plant development stages), `UBERON` (animal life-cycle stages), `NCIT` (seasons) and `TIME` (OWL-Time). `TIME` rather than `time` because `linkml lint` enforces the canonical prefix.

### Added: `QuantityValue.unit_text`

A nine-paper schema test against the 0.10.0 draft lost **19 records** to the `QuantityValue.unit` pattern (`^(unit|UO):\S+$`): 14 on `ramets/m2`, 2 on `deer/km2`, and 3 where the whole `QuantityValue` failed because the unit could not be set. Ecological density units frequently have no QUDT or UO term, so an annotator who read the unit correctly had nowhere to put it.

* **`unit_text`** (string): the unit as the source words it, used only when no CURIE exists. `unit` keeps its pattern and stays an identifier.

Why a sibling slot rather than a wider pattern: widening `unit` to admit literal strings would make one slot hold two kinds of thing (a resolvable identifier and free text), and a consumer would have to sniff which. With `unit_text` the fallback is visible in the data, so a downstream query can count how many quantities lack a resolvable unit and a later release can map the common ones to terms.

### Added: `EntityTypeEnum.composite_variable`

The two-path model under `EntityTypeEnum.taxon` said a multi-taxon aggregate or guild should use `environmental_variable` with `applied_to` listing the members, so the schema described a composite variable in prose and then labelled it with the value used for soil pH. Assemblage-level claims appeared in 8 of 9 papers in the nine-paper test, and `taxon list` rose to third by volume among gap types (267 words, 50 items, 6 papers).

* **`composite_variable`**: a measurable aspect of ecosystem state whose entity is an aggregate of several members (assemblage, community, guild). `meaning: BFO:0000019` (quality), the same as `environmental_variable`, since it is still a state variable, only an aggregated one.
* **Changed, documentation only**: path (2) of the two-path model now says `composite_variable`, in `EntityTypeEnum.taxon` and the `CausalNode` description; the `applied_to` and `AppliedToEntity` descriptions follow. No value, slot or range changed.

Existing annotations that labelled an assemblage `environmental_variable` stay valid but now disagree with the documentation; see the migration note for loom.

### Added: assemblage composition

A `CausalNode` carries one `entity_term`, so an observed assemblage of several taxa with a share each had nowhere to go. In the nine-paper test, 28 of 366 findings (8 of 9 papers, four systems: lake zooplankton, prairie plants, forest understory, boreal mammals) state a composition, and 4 of the 7 findings CAMO could not represent at all (fit grade `none`) were composition statements. Members were being concatenated into a node label or dropped. Sixteen of the 28 rank members without giving any number, so a design carrying only numeric shares would miss the majority.

* **`CausalNode.composition`** (`CompositionAnnotation`), restricted by a rule to `entity_type: composite_variable` nodes. The rule tests an enum value, not a boolean.
* **`CompositionAnnotation`**: required `basis` and `members` (at least one member); optional `total_share` and `verbatim`.
* **`CompositionMember`**, `is_a: EntityReference`: adds `share` (`QuantityValue`), `dominance` and `rank`, with an `any_of` requiring at least one of the three.
* **`CompositionBasisEnum`**: `relative_abundance`, `cover`, `biomass`, `density`, `detection_frequency`, `frequency_of_occurrence`, `other`.
* **`DominanceEnum`**: `dominant`, `codominant`, `subdominant`, `minor`, `rare`. Ordinal only.

A bare membership list with no share, ranking or dominance is **not** a composition: list the members in `applied_to` and carry presence or disappearance in `state_or_change_qualifier`. `CausalNode.components` is unchanged and still records what a management intervention applied; `composition` records what was observed.

Not changed, by decision: `CausalGraph.edges` stays required, so a composition-only finding is not a record and the four `none` fits above stay outside the graph. Composition rides along on a node that already participates in an edge, which covers the other 24 findings.

Known limits of this design, documented rather than solved: a group-to-group ratio ("forb-to-grass species ratios 3.5:1 vs 5.4:1") has no home (2 findings in 2 papers, below the bar for action); nested groups ("dominated by exotic ruderals including A, B, C, as well as early-seral natives D, E") flatten to one member list; and members are not always taxa (one real case is a fraction of particulate organic matter by biomass), though the descriptions lean taxon-centric.

### Added: `CausalEdge.certainty_grade` (restored)

`CausalEdge.certainty_grade` (`CertaintyGradeEnum`, default `not_assessed`) is back with its earlier definition unchanged. It was removed in an earlier rework, but a per-claim GRADE-style certainty gives each individual claim context that the evidence-base-level `aggregate_certainty_grade` does not. Additive; records written without it validate and default to `not_assessed`.

### Changed: documentation

* The `docs/` guides now describe `composite_variable`, `composition` and the revised two-path model. `docs/camo_schema_guide.html` still named a `taxonomic_scope` slot that no longer exists in the schema; it now says `applied_to`.
* Entity-type counts in the guides and in `docs/camo-rendering-targets.md` now say five.
* New page `docs/camo_annotation_essentials.html`: a simplified annotation guide for 0.10.0 that sorts fields into three tiers (always, when the paper says so, leave alone) and works through Murphy (2005) from the gold-set extraction. It adds to the full annotation guide and replaces nothing. Linked from `docs/index.html` and the README.

### Changed: explicit `class_uri` on every class

All 21 classes now declare `class_uri: causal_mosaic:<Name>`. That is the IRI each class already resolved to through `default_prefix`, so **no class IRI changes** — the value is pinned rather than inherited, which keeps generated OWL and JSON-LD stable if `default_prefix` is ever changed, and gives WARP a fixed target.

### Fixed: stale `schema_version` default

The `ifabsent` default on `CausalGraph.schema_version` and `ParameterOptionCatalog.schema_version` still said `0.8.0` — it was not bumped for the 0.9.0 release. Both now say `0.10.0`.

**Note for loom:** regenerate models. `dose_level`, `life_stage`, `significance` and `analysis_method` are all annotator-filled, not calculated. Two behaviours to add: prefer `dose_level` over constructing a `QuantityValue` whose only populated field is `verbatim`; and decide whether `life_stage` joins `variable_key`. It arguably should, since two stages of one taxon are genuinely different variables in a stage-structured model — but that changes node identity, so it is left as a deliberate decision rather than taken as a side effect of this release.

**Generator caveat worth knowing:** `gen-owl` ignores `slot_uri` on attribute-style (inline) slots — `camo:dose_level`, `camo:significance` and the sixteen Layer 3 feature slots all emit as `causal_mosaic:<name>` in the OWL output. `gen-jsonld-context` honours them correctly (`dose_level` maps to `camo:dose_level`). This is a generator limitation rather than a schema error, but it means OWL exports do not carry the `camo:` feature IRIs that `ci.py` check C6a enforces. Promoting those slots from `attributes:` to top-level `slots:` is the likely fix.

### Note for loom: composite variables, composition, `unit_text`

These additions rename or remove nothing, so they need no migration beyond the seasons step above. Five new public names enter the contract; regenerate models to pick them up:

| Name | Kind | Notes |
| --- | --- | --- |
| `EntityTypeEnum.composite_variable` | enum value | `meaning: BFO:0000019`, shared with `environmental_variable` |
| `CausalNode.composition` | slot | range `CompositionAnnotation`, inlined |
| `CompositionAnnotation` | class | required `basis`, required `members` |
| `CompositionMember` | class | `is_a EntityReference`; at least one of `share`, `dominance`, `rank` |
| `EntityReference` | class | abstract; holds `entity_type`, `entity_term`, `life_stage`, `life_stage_term`. `AppliedToEntity` now extends it |

Also new, but not slots on existing classes: `CompositionBasisEnum`, `DominanceEnum`, and the optional `QuantityValue.unit_text`.

Things loom should know:

* `AppliedToEntity` is now `is_a: EntityReference` (its slots are unchanged, only inherited). This keeps `CompositionMember` out of `applied_to`: with `CompositionMember is_a AppliedToEntity`, an `applied_to` entry carrying `share` validated. Generated models gain one abstract parent class; no field of `AppliedToEntity` moved or changed.

* A rule on `CausalNode` makes `composition` valid only when `entity_type` is `composite_variable`. It tests an enum, so it compiles correctly to JSON Schema.
* Two permissible values of `EntityTypeEnum` now share one `meaning` (`BFO:0000019`). Code that inverts `meaning` back to a value will find two; key on the value name.
* Annotations that labelled an assemblage `environmental_variable` are still valid but now disagree with the documentation, so the corpus will hold two conventions until they are re-typed. Re-typing is a data decision, not a schema one, and this release does not require it. The candidates are `environmental_variable` nodes with `applied_to` set (the scope role); each needs a human look, because a scalar variable can legitimately carry a taxon scope.
* `unit_text` is free text. Do not feed it to a unit converter; treat a quantity with `unit_text` and no `unit` as having an unresolved unit.

## 0.8.0 > 0.9.0 — Parameter options

Additive. Existing 0.8.0 records remain valid and need no migration. (This section was previously filed under "Unreleased"; it is the 0.9.0 release, as the `## CHANGELOG` header in `causalmosaic.yaml` records.)

### Added: parameter options

A node describes a change in the world. To use CAMO graphs with digital twins (e.g. SMOL) and to build causal models, you also need to know how each node could be measured. Parameter options record that: the sensor, survey, assay, record and model types that could supply a value for a node.

* **`ParameterOptionCatalog`**: a separate, versioned registry of options, kept in its own file and shared by all graphs. It has its own `catalog_version`, independent of the schema version. Validate a catalog with `linkml-validate -s causalmosaic.yaml -C ParameterOptionCatalog catalog.yaml`.
* **`ParameterOption`**: one option, identified in the new `camo_param:` namespace. Required: `label`, `acquisition_method`, `measurement_relation`, `value_type`. Optional: `observable_property`, `sensor_or_instrument`, `protocol`, `unit` (QUDT or UO), `typical_temporal_resolution` (ISO 8601 duration), `typical_spatial_resolution_m`, `option_description` and `scope`. A rule requires `observable_property` when `measurement_relation` is `proxy` or `derived`.
* **`ApplicabilityScope`**: which nodes an option can apply to (entity types, entity terms, measured attributes, qualifier families). Used to narrow candidates when matching options to nodes.
* **`CausalNode.parameter_options`**: ids of the options that could measure the node. Filled from the catalog, not by annotators. It lists possibilities and does not record what any study measured; the DOI conveys that.
* **New enums:** `AcquisitionMethodEnum` (11 values, from `in_situ_sensor` to `expert_elicitation`), `MeasurementRelationEnum` (`direct`, `proxy`, `derived`) and `ValueTypeEnum`. Each `ValueTypeEnum` value lists its `compatible_qualifier_families`; a new `ci.py` check validates them.
* **New prefixes:** `camo_param`, `sosa`, `iop` (I-ADOPT), `ECSO`, `EnvThes`, `nvs_p01`, `nvs_l05`, `nvs_l22`, `unit` (QUDT units) and `UO`.
* **Docs:** new "Parameter options" section in the annotation guide.

This change is additive. Existing 0.8.0 records remain valid and need no migration.

**Note for loom:** regenerate models. `parameter_options` is a calculated field (`loom_role: calculated`) holding references by id. Loom must check that each id exists in the catalog; LinkML does not check references across files. Options apply per `variable_key`: nodes sharing a key should carry the same options, filtered to those whose `value_type` is compatible with the node's qualifier family.

## 0.7.9 > 0.8.0 — Multiple comparators, canonical null results, `causal_language`

CAMO 0.8.0 contains **breaking changes**. 0.7.9 records need migration (see the notes under each change). `helpers/migrate_0_7_9_to_0_8_0.py` applies the mechanical steps and reports the ones that need a human. The 0.7.9 schema is archived as `old versions/causal_mosaic_v0.7.9.yaml`.

### Breaking: `comparator` is now a list

In 0.7.9, `CausalEdge.comparator` held a single `ComparatorAnnotation`, so an edge could name only one comparison basis. Before-after-control-impact (BACI) designs, which are common in restoration, contrast against both a pre-treatment baseline and a control site. The worked example (Kramer et al. 1995) has both, and 0.7.9 could not represent it.

`comparator` is now `multivalued: true, inlined_as_list: true`, with one `ComparatorAnnotation` per comparison arm. Each arm keeps its own `comparator_type`, `comparator_description` and `comparator_node_id`. That is why the list sits on `comparator` rather than making `comparator_type` multivalued: a list of types would lose which description and node belong to which arm.

**Migration note for loom:** wrap each existing `comparator` object in a one-item list, and regenerate models. For BACI studies, add a second entry for the arm that could not be recorded before.

### Breaking: `claim_strength` renamed to `causal_language`

`CausalEdge.claim_strength` is now `CausalEdge.causal_language`. The slot still ranges over `ClaimStrengthEnum`, and `claim_strength` is kept as an alias. Generated JSON Schema and Pydantic models key on the new name, so existing records fail validation until the key is renamed.

**Migration note for loom:** rename `claim_strength` to `causal_language` in every edge record, and regenerate models from the schema.

### Breaking: canonical null-result encoding

A null result could previously be recorded three ways: `negated: true`, `claim_strength: no_relationship`, or an object node with the qualifier `unchanged`. Two annotators could encode the same finding differently, which broke node merging and evidence counts.

* **Canonical encoding.** A null result ("X had no effect on Y") is an edge with `negated: true` **and** `causal_language: no_relationship`. The two always occur together: `negated` is true if and only if `causal_language` is `no_relationship`. The object node keeps the qualifier a positive finding would use (the tested direction if stated, otherwise none), so null and positive findings about the same variables land on the same nodes.
* **`unchanged` narrowed.** The qualifier now means a reported stable state of the outcome variable itself (e.g. "water table remained at 30 cm"), used on a positive, non-negated claim. It is never used to encode a null result.
* The invariant is declared as `equals_expression` on `CausalEdge.negated`. LinkML rules cannot test a boolean slot (the JSON Schema generator emits `const: "true"` as a string), so generated JSON Schema and Pydantic models do **not** enforce it. Loom must check it at validation time.

**Migration note for loom:**

* Edges with `claim_strength`/`causal_language: no_relationship` and `negated: false` → set `negated: true`.
* Edges with `negated: true` and any other claim strength → set `causal_language: no_relationship` (the helper reports these for review rather than changing them, since the negation may have been of hedged language).
* Edges whose object node is `unchanged` and that report a null result → set `negated: true`, `causal_language: no_relationship`, and repoint the object to the node a positive finding would use. The helper reports these; they need a human to decide.

### Added: predicate and causal-language consistency rules

* `associated_with`, `correlated_with` and `precedes` may only carry `causal_language` of `associational` or `no_relationship`.
* `causes` may not carry `associational`.

These rules are enforced by generated JSON Schema. Records that break them now fail validation; the migration helper lists them.

### Changed: `associated_with` and `correlated_with`

* `correlated_with` is now `is_a: associated_with`, and is reserved for sources that report a correlation statistic (e.g. Pearson or Spearman r, R², regression slope). Otherwise use `associated_with`.
* Both carry `exact_mappings` to `biolink:associated_with` and `biolink:correlated_with`.

### Documented: FCM sign composition

Predicates carry a `sign` annotation and qualifiers carry `fcm_sign`, but nothing said how they combine, so two renderers could build opposite FCMs from the same graph. The rule is now stated in the `CausalPredicateEnum` and `CausalEdge.fcm_weight` descriptions, and in the rendering guide:

* **State level** (FCM concepts are CAMO nodes as annotated): edge sign = predicate sign. Node qualifiers are part of each concept's identity and are not applied. `fcm_weight` is stored at this level.
* **Variable level** (nodes collapsed to entity + attribute): edge sign = subject `fcm_sign` × predicate sign × object `fcm_sign`. A node with no qualifier, `occurred` or `ongoing` counts as +1; edges with an `unchanged` node are left out.
* Worked examples: "increased X prevents Y" and "decreased X causes Y" both come out negative at the variable level.

This also fixes the rendering guide, which gave the variable-level rule as `predicate sign × object fcm_sign`, leaving out the subject. That would have flipped every edge whose subject is a `decreased`, `absent`, `removed` or `terminated` state.

No schema structure changed; this is documentation only.

### Fixed: `EvidenceTypeEnum` ECO grounding

Six values used ECO terms as `meaning`. Checked against ECO via OLS, five were unrelated molecular-biology terms and the sixth was a parent term:

| Value | Old `meaning` | What that ECO ID actually is |
|---|---|---|
| `randomized_experiment` | ECO:0000006 | experimental evidence (a parent, not an equivalent) |
| `mechanistic_study` | ECO:0000231 | quantitative polymerase chain reaction evidence |
| `structural_equation_model` | ECO:0000222 | Illumina sequencing evidence |
| `meta_analysis` | ECO:0006153 | self-reported individual's statement evidence |
| `case_study` | ECO:0000066 | yeast one-hybrid evidence |
| `practitioner_experience` | ECO:0000182 | obsolete (in vitro culture assay evidence) |

ECO has no exact equivalent for any of the 15 study designs, so every `meaning` is removed. Where ECO has a parent term, it is now a `broad_mapping`:

| Value | `broad_mappings` |
|---|---|
| `randomized_experiment`, `quasi_experiment` | ECO:0000006 experimental evidence |
| `meta_analysis`, `systematic_review` | ECO:0000212 combinatorial evidence |
| `modeling_simulation` | ECO:0007672 computational evidence |
| `expert_judgment`, `practitioner_experience` | ECO:0006151 documented statement evidence |
| `theoretical` | ECO:0000361 inferential evidence |

`natural_experiment`, `observational_longitudinal`, `observational_cross_sectional`, `mechanistic_study`, `structural_equation_model`, `case_study` and `indigenous_knowledge` have no ECO parent and are left unmapped.

Permissible value names are unchanged, so annotation data is unaffected. The value IRIs in generated OWL/RDF change, because they no longer resolve to the ECO IDs.

### Housekeeping

* Renamed `claim_strength` to `causal_language` throughout `docs/` (rendering guide, annotation guide, schema guide), and aligned their null-result wording with the canonical encoding.
* Removed a stale mention of the `unspecified` qualifier (dropped in 0.7.8) from the `state_or_change_qualifier` description, and listed the `process_phase` values (`occurred`, `initiated`, `terminated`, `ongoing`, `interrupted`, `aborted`) in `QualifierFamilyEnum`, as the other families already do.
* Brought `docs/camo_annotation_guide.html` in line with 0.8.0. Predicate section: removed the defunct `positively_regulates` / `negatively_regulates`, added `correlated_with`, and added a predicate table with signs and the allowed `causal_language` for each, a selection procedure, and guidance on reading predicate and node qualifier together. Corrected the Murphy example's `fcm_weight` to the state-level sign (+0.75, not -0.75). Also documented `comparator` and `ecosystem_context`, the 16 causal features, the sampling-effort fields, `applied_to` in place of the nonexistent `taxonomic_scope`, and the `wd:` prefix.
* Added `helpers/migrate_0_7_9_to_0_8_0.py`, which migrates 0.7.9 datasets to 0.8.0.
* Archived the pre-breaking 0.7.9 schema as `old versions/causal_mosaic_v0.7.9.yaml`.
* Replaced the `→` characters in schema descriptions and comments. `gen-pydantic` crashed with a `UnicodeEncodeError` on Windows consoles.
* Updated `AGENTS.md` with the real schema file name, the checks CI runs, the LinkML version it pins (1.11.1), and authoring notes: LinkML rules can't test boolean slots, rules must name the current slot rather than an alias, and descriptions must stay cp1252-encodable.

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
