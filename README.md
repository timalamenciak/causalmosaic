# Causal Mosaic

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

## What goes in?

- Ecological causal claims extracted from papers, reports, or synthesis products
- Ontology terms from CAMO, ELMO, ENVO, GO, PATO, NCBITaxon, ECO, and related vocabularies
- Source-document provenance: quoted spans, study metadata, annotator judgments

## What comes out?

- Versioned, validated YAML records conforming to `causal_mosaic_v0.7.1.yaml`
- Causal graphs suitable for Fuzzy Cognitive Maps, Evidence Gap Maps, and RAG pipelines
- Structured evidence for practitioner summaries and systematic reviews

---

