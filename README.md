# Causal Mosaic Schema readme

The Causal Mosaic prototype is a LinkML schema plus shared example set for representing ecological causal claims as an ontology-grounded graph. It combines ELMO-style decomposition of ecological changes into entity, attribute, direction, and context with CAMO-style annotation of causal accounts, features, and evidence, so the same curated claims can support ingestion, graph construction, evidence synthesis, and downstream interfaces.

Ecological causal knowledge is usually stored as prose, tables, or informal diagrams, which makes it difficult to compare claims across studies, preserve distinctions between different kinds of causal reasoning, and reuse evidence in tools such as causal graphs, evidence gap maps, or user-facing summaries. The project aims to create a common representation that is both philosophically expressive and computationally tractable.

A LinkML schema is being built to encode ecological causal claims as a labeled property graph. Nodes represent changes in ecological variables or processes using ELMO-style decomposition. Edges represent causal claims using CAMO-grounded predicates, philosophical accounts, causal features, and evidential annotations. A migrated grassland restoration sample is being used as the shared worked example for schema testing and documentation.

## What goes in?

- Ecological causal claims extracted from papers, reports, or synthesis products
- Ontology terms from CAMO, ELMO, ENVO, GO, PATO, NCBITaxon, ECO, and related vocabularies
- Source-document provenance such as quoted spans, study metadata, and annotator judgments

## What comes out?

- A versioned LinkML schema in `causal_mosaic_v0.4.0.yaml`
- A migrated example dataset in `sample_data.yaml`
- A smaller grounded example in `sample_data_grounded.yaml`
- Audience-specific Markdown documentation for semantic engineers, philosophers, and ecologists

## Open questions

- Which remaining node categories should be grounded directly to stable external ontology terms instead of the current local placeholders?
- How strict should validation be for partially grounded claims when no exact ontology term exists?
- Should the project maintain one canonical sample dataset or both a compact grounded sample and a fuller narrative sample?
- What downstream renderers should be treated as first-class targets in the next iteration?

## What is the immediate next action?

Run formal LinkML and YAML validation for `causal_mosaic_v0.4.0.yaml` and `sample_data.yaml`, then resolve any schema-sample mismatches that appear in validator output.