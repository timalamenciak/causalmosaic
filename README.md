# Causal Mosaic

[![Latest release](https://img.shields.io/github/v/tag/timalamenciak/causalmosaic?label=release)](https://github.com/timalamenciak/causalmosaic/tags)
[![LinkML schema](https://github.com/timalamenciak/causalmosaic/actions/workflows/linkml-schema.yml/badge.svg)](https://github.com/timalamenciak/causalmosaic/actions/workflows/linkml-schema.yml)

A LinkML schema for representing ecological causal claims as an ontology-grounded graph. Combines ELMO-style entity decomposition with the Illari–Russo causal mosaic framework (CAMO), so the same curated claims can drive causal diagrams, evidence gap maps, fuzzy cognitive models, and practitioner summaries.

---

## Repository contents

| File / folder | Purpose |
|---|---|
| `causal_mosaic_v0.7.1.yaml` | Current versioned LinkML schema |
| `CHANGELOG.md` | Schema change history with rationale |
| `docs/sample_data.yaml` | Full worked example (grassland restoration) |
| `docs/sample_data_grounded.yaml` | Compact ontology-grounded version of the same example |
| `docs/causal_mosaic_annotation_guide.md` | Complete annotator handbook |
| `docs/schema_cheat_sheet_one_page.md` | One-page quick reference |
| `docs/schema_guide_ecologists.md` | Audience guide for ecologists |
| `docs/schema_guide_philosophers.md` | Audience guide for philosophers |
| `docs/schema_guide_plain_language.md` | Plain-language guide |
| `docs/schema_guide_semantic_engineers.md` | Audience guide for semantic engineers |
| `docs/sentence_to_schema_infographic.md` | Visual walkthrough of schema decomposition |
| `old versions/` | Archived prior schema versions |

---

## The schema in one sentence

A Causal Mosaic annotation is a **labeled property graph** where every **node** is a change in an ecological variable (entity + attribute + state/change qualifier) and every **edge** is a causal claim carrying four annotation layers: claim strength, philosophical account, fifteen causal features, and evidential basis.

The five questions the schema answers for each claim:

1. **What changed?** — `entity_term`, `measured_attribute`
2. **Which way?** — `state_or_change_qualifier`
3. **What did it affect?** — edge `subject` → `object`
4. **How strong is the claim?** — `claim_strength`, `philosophical_accounts`
5. **What evidence supports it?** — `evidential_basis`

---

## Core graph objects

### `CausalNode`

A `CausalNode` represents something ecologically relevant in a particular state
or undergoing a particular change. It does not represent a species, chemical,
environment, or process in isolation. Instead, it combines the entity, the
measurable attribute of interest, and a state-or-change qualifier. For example,
*increased abundance of wolves* combines the entity *wolf*, the attribute
*abundance*, and the qualifier *increased*. Keeping these components structured
makes it possible to search and compare claims by entity, attribute, or kind of
change while retaining a readable name for displays and summaries.

### `CausalEdge`

A `CausalEdge` represents an article-level causal claim connecting a cause node
to an effect node through a controlled predicate. Beyond the basic
subject-predicate-object relationship, it records how strongly the source makes
the claim, which philosophical accounts of causation it invokes, the causal
features it exhibits, and the evidence supporting it. It can also retain the
original sentence, ecosystem context, and rendering metadata. In other words,
the edge captures both *what causal relationship was claimed* and *how that
claim was expressed and supported in its source*.

### `EvidenceBaseAssessmentEdge`

An `EvidenceBaseAssessmentEdge` represents a synthesis-level judgment across
multiple article-level `CausalEdge` records concerning the same or comparable
causal relationship. It records which edges were included or excluded and
summarizes properties of the combined evidence, such as the evidence types,
effect direction, consistency, and the presence of difference-making or
mechanistic evidence. It is intended for systematic synthesis and graph
analysis rather than direct annotation of an individual article, and it can be
regenerated when the underlying evidence base changes.

---

## What goes in?

- Ecological causal claims extracted from papers, reports, or synthesis products
- Ontology terms from CAMO, ELMO, ENVO, GO, PATO, NCBITaxon, ECO, and related vocabularies
- Source-document provenance: quoted spans, study metadata, annotator judgments

## What comes out?

- Versioned, validated YAML records conforming to `causal_mosaic_v0.7.1.yaml`
- Causal graphs suitable for Fuzzy Cognitive Maps, Evidence Gap Maps, and RAG pipelines
- Structured evidence for practitioner summaries and systematic reviews

---
