# Causal Mosaic Schema

<p align="center">
  <img src="mosaic_icon.png" />
</p>

[![Latest release](https://img.shields.io/github/v/tag/timalamenciak/causalmosaic?label=release)](https://github.com/timalamenciak/causalmosaic/tags)
[![LinkML schema](https://github.com/timalamenciak/causalmosaic/actions/workflows/linkml-schema.yml/badge.svg)](https://github.com/timalamenciak/causalmosaic/actions/workflows/linkml-schema.yml)

The Causal Mosaic Schema (CAMO) is a LinkML schema for representing ecological causal claims as an ontology-grounded labeled property graph. This schema implements the [Illari–Russo causal mosaic framework](https://global.oup.com/academic/product/causality-9780199662678). Curated claims made using the schema can drive causal diagrams, evidence gap maps, fuzzy cognitive models, and practitioner summaries.

---

## Repository contents

| File / folder | Purpose |
|---|---|
| `causalmosaic.yaml` | Current versioned LinkML schema |
| `CHANGELOG.md` | Schema change history with rationale |
| `docs/camo_annotation_guide.html` | A guide to using the Causal Mosaic Schema to annotate a scholarly journal article. |
| `docs/camo_schema_guide.html` | A detailed guide in plain language to the Causal Mosaic Schema. |
| `old versions/` | Archived prior schema versions |

---

## The schema in one sentence

The Causal Mosaic Schema is a plan for a **labeled property graph** where every **node** is a change in an ecological variable (entity + attribute + state/change qualifier) and every **edge** is a causal claim carrying four annotation layers: claim strength, philosophical account, causal features, and evidential basis.

The five questions the schema answers for each claim:

1. **What changed?** — `entity_term`, `measured_attribute`
2. **Which way?** — `state_or_change_qualifier`
3. **What did it affect?** — edge `subject` → `object`
4. **How strong is the claim?** — `claim_strength`, `philosophical_accounts`
5. **What evidence supports it?** — `evidential_basis`

---

## Core graph objects

### `CausalNode`

A `CausalNode` represents something ecologically relevant in a particular state or undergoing a particular change. It does not represent a species, chemical, environment, or process in isolation. Instead, it combines the entity, the measurable attribute of interest, and a state-or-change qualifier. For example, *increased abundance of wolves* combines the entity *wolf*, the attribute *abundance*, and the qualifier *increased*. Keeping these components structured makes it possible to search and compare claims by entity, attribute, or kind of change while retaining a readable name for displays and summaries.

### `CausalEdge`

A `CausalEdge` represents an article-level causal claim connecting a cause node to an effect node through a controlled predicate. Beyond the basic subject-predicate-object relationship, it records how strongly the source makes the claim, which philosophical accounts of causation it invokes, the causal features it exhibits, and the evidence supporting it. It can also retain the original sentence, ecosystem context, and rendering metadata. In other words, the edge captures both *what causal relationship was claimed* and *how that claim was expressed and supported in its source*.

### `EvidenceBaseAssessmentEdge` *Future feature*

An `EvidenceBaseAssessmentEdge` represents a synthesis-level judgment across multiple article-level `CausalEdge` records concerning the same or comparable causal relationship. It records which edges were included or excluded and summarizes properties of the combined evidence, such as the evidence types, effect direction, consistency, and the presence of difference-making or mechanistic evidence. It is intended for systematic synthesis and graph analysis rather than direct annotation of an individual article, and it can be regenerated when the underlying evidence base changes.

---

Mosaic by Andrejs Kirma from <a href="https://thenounproject.com/browse/icons/term/mosaic/" target="_blank" title="Mosaic Icons">Noun Project</a> (CC BY 3.0)