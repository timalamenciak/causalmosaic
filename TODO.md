# TODO: items for human review and decision

Left open after the nine-paper schema-test update (`unit_text`, `composite_variable`, assemblage composition). Nothing here blocks the current state: all three checks pass and the version is still 0.10.0.

## Decisions on the composition design

1. **`basis` is required, but sources often do not state one.** In the five test cases, 2 and 4 only validate because the annotator infers a basis (`cover`, `relative_abundance`). The `other` value says to name the basis in `verbatim`, which is optional, so `other` leaves the basis unrecoverable. Options: add a `not_stated` value to `CompositionBasisEnum`, make `basis` optional, or leave as is and accept inference. Adding an enum value is non-breaking.
2. **`density` basis does not fit the slot name `share`.** With `basis: density`, `share` holds a concentration (a count per area), not a proportion of a whole, and `total_share` has no meaning. Options: drop `density` from the basis enum, or document it as the one basis whose amounts are absolute.
3. **`detection_frequency` and `frequency_of_occurrence` overlap.** Both are a fraction of sampling units; the only difference is the unit (occasions versus plots). `frequency_of_occurrence` was anticipated, not observed in the corpus. Keep both, merge, or drop it until a paper needs it.
4. **Possibly missing basis values:** `importance_value`, `basal_area`, and a raw `count` (unnormalised individuals). None has been seen in the corpus. Add only when a finding needs one.
5. **`components` is not restricted to `management_intervention` nodes.** `composition` is limited by a rule to `composite_variable`, but nothing stops `components` appearing on a `composite_variable` node. Decide whether to add the mirror rule. The `components` description now says what it is for, which is advisory only.
6. **`DominanceEnum` is a small ordinal scale** (dominant, codominant, subdominant, minor, rare). Check it against the corpus before relying on it; for example "common" or "abundant" have no value.

## Known gaps in the design (documented, not solved)

- A group-to-group ratio ("forb-to-grass species ratios 3.5:1 vs 5.4:1") has no home. 2 findings in 2 papers, below the bar for action.
- Nested groups flatten to one member list ("dominated by exotic ruderals including A, B, C, as well as early-seral natives D, E").
- Members are not always taxa (one real case is a fraction of particulate organic matter by biomass). The descriptions now say so, but nothing in the slots enforces or supports non-taxon members beyond `entity_type`.
- `CausalGraph.edges` stays required by decision, so a composition-only finding is not a record. Four findings with fit grade `none` stay outside the graph.

## Data and downstream

- **Existing annotations that labelled an assemblage `environmental_variable`** are still valid but now disagree with the documentation, so the corpus holds two conventions. Re-typing is a data decision. The candidates are `environmental_variable` nodes with `applied_to` set, and each needs a human look because a scalar variable can legitimately carry a taxon scope.
- **loom:** regenerate models. New public names are `EntityTypeEnum.composite_variable`, `CausalNode.composition`, `CompositionAnnotation`, `CompositionMember` and the abstract `EntityReference`. Two enum values now share `meaning: BFO:0000019`, so anything that inverts `meaning` back to a value must key on the value name. See "Note for loom" in `CHANGELOG.md`.
- **`unit_text` is free text.** A quantity with `unit_text` and no `unit` has an unresolved unit. Consider a later pass mapping the common ones (`ramets/m2`, `deer/km2`) to QUDT terms, and whether to make `unit` and `unit_text` mutually exclusive (currently only advised in the description).

## Housekeeping

- **Release decision:** the three changes plus `EntityReference` sit under "Unreleased" in `causalmosaic.yaml` and `CHANGELOG.md`. Decide when to cut a release and what version number. They are additive, but the `EntityReference` parent class changes the generated class hierarchy, so loom should regenerate either way.
- **Stale `## Unreleased` section** near line 787 of `CHANGELOG.md` (the `CoordinateLocationBasisEnum` entry) predates the 0.10.0 changelog and looks like leftover from an earlier release. Check whether it belongs under a released version.
- **Pre-existing non-cp1252 characters** in `causalmosaic.yaml` (an arrow and em dashes in older descriptions) crash generators on Windows consoles, per `AGENTS.md`. Not introduced by this work; worth a separate cleanup.
- **Docs are hand-maintained and were already stale in places** (the schema guide named a `taxonomic_scope` slot that no longer exists; fixed). Worth a read-through of `docs/` against the schema for other drift.
- **Uncommitted work:** all changes, plus the earlier untracked files (`GOVERNANCE.md`, `Makefile`, `vocab/`, `docs/ecoskos/` and others), are not committed.
- **`AGENTS.md` is human-owned.** Candidate convention to fold in: when a class needs another class's slots but not its role, extract an abstract base (as `EntityReference`) rather than using `is_a` on a concrete class, because LinkML ranges accept subclasses.

## Caveats from the source analysis

- Everything rests on one model (`gemma4:31b`). A second arm (DeepSeek-V4-Flash) reached 507 findings before its endpoint failed and is not pooled.
- `study_design` was empty for all nine papers, so the Frequent criterion's "at least two study designs or ecosystems" could not be evaluated for any candidate.
- No reviewer has graded the fits; `agreement.csv` has `reviewer_fit` unfilled.
