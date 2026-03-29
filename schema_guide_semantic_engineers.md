# Causal Mosaic Schema Guide for Computer Scientists and Semantic Engineers

## Purpose

The Causal Mosaic schema models ecological causal claims as a labeled property graph with ontology-grounded nodes and richly annotated causal edges.

The current schema file is `causal_mosaic_v0.4.0.yaml`.
The main worked example is `sample_data.yaml`.

## Core Model

The top-level object is a `CausalGraph` with:

- `graph_id`
- `schema_version`
- `provenance`
- `nodes`
- `edges`

Nodes encode changes in ecological state using an ELMO-style decomposition:

- `entity_term`: what thing or process is involved
- `variable_attribute`: what property is changing
- `variable_direction`: how it changes
- `ecosystem_context`, `process_context`, `conditioned_by`: qualifiers

Edges encode causal claims using CAMO-style semantics:

- `subject`, `predicate`, `object`
- `claim_strength`
- `philosophical_accounts`, `account_families`
- causal features such as `direction`, `mediation`, `moderation`, `strength`
- evidential layer in `evidential_basis`

## Ontology Grounding

The schema uses:

- `camo:` for philosophical accounts, causal predicates, evidence types, and feature slot URIs
- `elmo:` and `elmo_cas:` for ecological process and intervention grounding
- external ontologies such as `ENVO`, `GO`, `PATO`, `NCBITaxon`, `ECO`, and `RO`

The example identifiers `example:`, `node:`, and `edge:` are declared as prefixes so example data stays CURIE-safe.

## Shared Example

The same example is reused across all documentation:

- Increased buckthorn removal intensity
- Decreased buckthorn canopy cover
- Increased light availability
- Increased native forb species richness
- Increased native bee species richness
- Increased native grass biomass, which partly suppresses forb richness

Core causal chain:

```mermaid
graph LR
  A["Buckthorn removal"] -->|negatively_regulates| B["Buckthorn canopy cover"]
  B -->|negatively_regulates| C["Light availability"]
  C -->|positively_regulates| D["Native forb richness"]
  D -->|positively_regulates| E["Bee diversity"]
  C -->|positively_regulates| F["Native grass biomass"]
  F -->|negatively_regulates| D
```

## Minimal Node Example

```yaml
- id: "node:buckthorn_canopy_cover"
  name: "Decreased buckthorn canopy cover"
  categories:
    - abiotic_factor
    - ecological_outcome
  entity_type: environmental_variable
  entity_term: "ENVO:00010483"
  variable_attribute: "PATO:0001708"
  variable_direction: decreased
  ecosystem_context:
    - "elmo:elmo_3620249"
```

Interpretation:

- The bearer is `ENVO:00010483` canopy.
- The measured property is cover-like extent (`PATO:0001708`).
- The node means a decrease in that attribute in a temperate grassland context.

## Minimal Edge Example

```yaml
- id: "edge:cover_to_light"
  subject: "node:buckthorn_canopy_cover"
  predicate: negatively_regulates
  object: "node:light_availability"
  claim_strength: direct_causal
  philosophical_accounts:
    - mechanistic
  account_families:
    - production
  temporal_ordering: explicitly_asserted
  direction:
    status: asserted
    evidence_for_direction: theoretical
  strength:
    status: explicitly_asserted
    qualitative_descriptor: strong
    dose_response: true
  evidential_basis:
    evidence_types:
      - observational_longitudinal
      - mechanistic_study
    evidence_objects:
      - correlation
      - mechanism
    russo_williamson_satisfied: true
    certainty_grade: high
```

## Modeling Notes

- Use `entity_term` for the main bearer or process class, not for the whole node meaning.
- Use `variable_direction` to encode the state change rather than folding change language into `entity_term`.
- Use `predicate` for the causal relation between nodes, and feature slots for metadata about that claim.
- Use `philosophical_accounts` as a multivalued classifier. A claim may be both `variation` and `mechanistic`.
- Use `source_spans` for provenance, not as a substitute for structured annotation.

## Common Workflow

1. Identify the ecological state changes to become nodes.
2. Ground each node with ontology terms plus ELMO-style qualifiers.
3. Create edges only for actual claims in the source.
4. Classify each edge with one or more CAMO accounts.
5. Fill feature slots only when the source supports them.
6. Capture evidence and provenance explicitly.

## What Changed in 0.4.0

- Schema version increased to `0.4.0`.
- Placeholder local CURIE meanings were replaced by real `camo:` and `elmo:` terms in the key semantic enums and slots.
- `variation` was added to `PhilosophicalAccountEnum`.
- `structural_equation_model` was added to `EvidenceTypeEnum`.
- CAMO feature slot grounding was made explicit with `slot_uri`.
- Node-level `ecosystem_context`, `process_context`, and `conditioned_by` qualifiers were added to match the documented ELMO pattern.
