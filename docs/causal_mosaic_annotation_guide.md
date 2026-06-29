# Causal Mosaic Annotation Guide

## A Practical Handbook for Annotating Ecological Causal Claims

**Schema version:** 0.4.0
**Audience:** Undergraduate annotators with introductory ecology and environmental studies background
**Last updated:** March 2026

---

## Table of Contents

1. [Introduction: Why This Work Matters](#1-introduction-why-this-work-matters)
2. [The Big Picture: What You Are Building](#2-the-big-picture-what-you-are-building)
3. [The Two Grounding Ontologies: ELMO and CAMO](#3-the-two-grounding-ontologies-elmo-and-camo)
4. [Core Concept: Causation Is Between Changes, Not Things](#4-core-concept-causation-is-between-changes-not-things)
5. [Part I — Annotating Nodes (The Ecological Entities)](#5-part-i--annotating-nodes-the-ecological-entities)
6. [Part II — Annotating Edges (The Causal Relationships)](#6-part-ii--annotating-edges-the-causal-relationships)
7. [Layer 1: Claim Strength](#7-layer-1-claim-strength)
8. [Layer 2: Philosophical Account of Causation](#8-layer-2-philosophical-account-of-causation)
9. [Layer 3: The Fifteen Causal Features](#9-layer-3-the-fifteen-causal-features)
10. [Layer 4: Evidential Basis](#10-layer-4-evidential-basis)
11. [Recording Provenance and Source Information](#11-recording-provenance-and-source-information)
12. [Rendering Outputs: FCM Weights and Rosetta Statements](#12-rendering-outputs-fcm-weights-and-rosetta-statements)
13. [Worked Example: Grassland Restoration](#13-worked-example-grassland-restoration)
14. [Common Pitfalls and How to Avoid Them](#14-common-pitfalls-and-how-to-avoid-them)
15. [Decision Flowcharts](#15-decision-flowcharts)
16. [Quick Reference Tables](#16-quick-reference-tables)
17. [Suggesting New Ontology Terms](#17-suggesting-new-ontology-terms)
18. [Glossary](#18-glossary)
19. [Appendix A: LLM-Assisted Extraction — Best Practices and Prompt](#appendix-a-llm-assisted-extraction--best-practices-and-prompt)

---

## 1. Introduction: Why This Work Matters

Ecological science is full of causal claims. A restoration ecologist might write: "Removing invasive buckthorn increased light availability, which promoted native grass recovery." A conservation biologist might report: "Higher wildflower diversity supports more diverse bee communities." These claims are scattered across thousands of journal articles, reports, and field guides — each expressed in different language, at different levels of confidence, and backed by different kinds of evidence.

The **Causal Mosaic** schema gives us a structured, consistent way to capture all of that richness. When you annotate a paper using this schema, you are translating an author's prose into a formal graph — a network of ecological entities (nodes) connected by causal relationships (edges) — where every edge carries detailed metadata about *what kind* of causation is being claimed, *how strong* the evidence is, and *under what conditions* the relationship holds.

Your annotations will be used to build:

- **Causal diagrams** showing how ecological systems work
- **Evidence gap maps** revealing where we have strong evidence and where we need more research
- **Fuzzy Cognitive Maps** for modeling and simulation
- **Searchable databases** so practitioners and researchers can find relevant evidence
- **Plain-language summaries** for land managers making real-world decisions

Every annotation you produce contributes to a growing knowledge base that helps science move faster and helps practitioners make better decisions.

---

## 2. The Big Picture: What You Are Building

A Causal Mosaic annotation is a **labeled property graph**. Think of it as a network diagram where:

- **Nodes** are ecological entities — things like species, environmental variables, processes, or management actions. Each node has structured properties describing exactly what it represents.
- **Edges** are causal relationships connecting one node to another. Each edge carries four layers of annotation that capture everything we need to know about the claim.

Here is a simplified picture of what the graph looks like for a grassland restoration study:

```
[Buckthorn Removal] ──causally_decreases──▶ [Buckthorn Canopy Cover]
                                                      │
                                              causally_decreases
                                                      │
                                                      ▼
                                            [Light Availability]
                                              │              │
                                    causally_increases    causally_decreases
                                              │              │
                                              ▼              ▼
                                    [Native Grass Growth]  [Soil Moisture]
                                      │            │
                            causally_increases   causally_decreases
                                      │            │
                                      ▼            ▼
                            [Big Bluestem     [Native Forb
                              Abundance]       Richness]
                                                   │
                                          causally_increases
                                                   │
                                                   ▼
                                           [Bee Diversity]
```

Your job is to read a scientific paper, identify these nodes and edges, and fill in the structured annotation for each one. The rest of this guide walks you through exactly how to do that.

---

## 3. The Two Grounding Ontologies: ELMO and CAMO

The Causal Mosaic schema is grounded in two purpose-built ontologies. Understanding their roles is essential before you start annotating.

### 3.1 ELMO — The Ecolink Model Ontology

**Repository:** [https://github.com/timalamenciak/elmo](https://github.com/timalamenciak/elmo)
**Documentation:** [https://timalamenciak.github.io/elmo](https://timalamenciak.github.io/elmo)
**Ontology IRI:** `https://w3id.org/elmo`

ELMO is an application ontology that describes ecosystem management processes, ecosystem types, and environmental variables. It provides the **entity layer** — the vocabulary for describing *what* is involved in a causal relationship. ELMO provides three critical things for your annotation work:

**Ecosystem types.** ELMO incorporates two major international classification schemes: the IUCN's Global Ecosystem Typology 2.0 (GET) and NatureServe's International Vegetation Classification (IVC). These have been harmonized with a crosswalk so that a single ELMO identifier (e.g., `ELMO:3620108` for "Temperate pyric humid forest" or `ELMO:3620109` for "Temperate pyric sclerophyll forests and woodlands") can stand for the ecosystem type in both typologies. **All ecosystem context annotations in the Causal Mosaic must be grounded in ELMO ecosystem types.** Do not use free-text ecosystem descriptions or ENVO ecosystem terms when an ELMO term exists.

**Environmental variables and processes.** ELMO contains terms for common environmental variables (state variables like soil moisture, canopy cover, species abundance) and environmental processes (flows like nitrogen deposition, competitive exclusion, prescribed burning). When annotating nodes, look for an ELMO term first. If one exists, use it as the `entity_term`.

**The ELM qualifier pattern.** ELMO implements the Ecolink Model (ELM) pattern for decomposing ecological relationships into entity + measurable attribute + state/change qualifier, with qualifier slots for ecosystem context, process context, and conditioning variables. This is the structural pattern you will use for every node.

### 3.2 CAMO — The Causal Mosaic Ontology

**Repository:** [https://github.com/timalamenciak/camo](https://github.com/timalamenciak/camo)
**Ontology IRI:** `http://purl.obolibrary.org/obo/camo.owl`

CAMO is the ontology that provides the **causal semantics layer** — the vocabulary for describing *how* things are causally related and *how we know*. All causal predicates, philosophical account classifications, causal feature terms, and evidence type terms used in edge annotations are defined in CAMO. When you assign a predicate like `causes`, `contributes_to`, or `prevents`, you are using a CAMO term. When you classify a philosophical account as `mechanistic` or `interventionist`, that is also a CAMO term.

### 3.3 How ELMO and CAMO Work Together

Think of it this way:

| Question | Ontology | Where It Appears |
|---|---|---|
| **What** is involved? (entities, variables, taxa, ecosystem types) | **ELMO** (+ NCBITaxon, PATO, CHEBI, GO for cross-references) | **Nodes**, and ecosystem context on **edges** |
| **How** are they causally related? (predicates, accounts, features, evidence) | **CAMO** | **Edges** (all four annotation layers) |

ELMO asks: "What is related to what, and in what context?"
CAMO asks: "How do we know this is causal, what kind of causation is claimed, and how confident should we be?"

### 3.4 Browsing the Ontologies

As an annotator, you will frequently need to look up terms. Here is how to browse each ontology:

- **ELMO ecosystem types:** Visit the [ELMO ecosystem types page](https://timalamenciak.github.io/elmo/ecosystems/) for an overview, or browse the full ontology in the [HTML documentation](https://timalamenciak.github.io/elmo/elmo.html). You can also open `elmo.owl` in an ontology editor like Protégé.
- **ELMO variables and processes:** Browse the full ontology HTML or OWL file. Terms use the prefix `ELMO:` followed by a numeric identifier (e.g., `ELMO:3620108`).
- **CAMO causal terms:** Browse the CAMO documentation or OWL file at the repository. Terms use the prefix `camo:` (e.g., `camo:causes`, `camo:Mechanistic`).
- **Cross-referenced ontologies** (NCBITaxon, PATO, CHEBI, GO, ENVO): Use the [Ontology Lookup Service (OLS)](https://www.ebi.ac.uk/ols4/) to search these.

---

## 4. Core Concept: Causation Is Between Changes, Not Things

This is the single most important idea in the entire schema. Internalize it before you annotate anything.

**In ecology, causation is always between *changes in state*, not between *things*.**

A wolf does not "cause" an elk. That sentence makes no sense causally. What *does* make sense is:

> "An **increase** in wolf **population abundance** causally **decreases** elk **browsing intensity**."

Notice how three components combine to give the node its full meaning:

| Component | What It Answers | Example |
|---|---|---|
| **Entity** | What thing? | Wolf (*Canis lupus*) |
| **Attribute** | What measurable property of that thing? | Population abundance |
| **Direction** | Which way did it change? | Increased |

We call this the **entity + attribute + direction** decomposition. It comes from the Ecolink Model (ELM), and it is the foundation of every node in the graph.

**Why this matters for you as an annotator:** When you read a sentence like "Wolves reduce elk populations," you need to mentally decompose it into:

- Source node: increased abundance of *Canis lupus*
- Target node: decreased abundance of *Cervus canadensis*
- Predicate: causally decreases

If you find yourself creating a node that is just a bare thing ("wolves," "fire," "nitrogen") without an attribute and direction, stop and rethink. Something is missing.

---

## 5. Part I — Annotating Nodes (The Ecological Entities)

### 5.1 Required Fields for Every Node

Every node must have the following:

| Field | Description | Example |
|---|---|---|
| `id` | A unique identifier. Use ontology CURIEs when possible. | `node:buckthorn_canopy_cover` |
| `name` | A human-readable label expressing the full meaning (entity + attribute + direction). | "Buckthorn Canopy Cover" |
| `description` | A free-text explanation as characterized in the source paper. | "Percentage of ground covered by buckthorn canopy." |

### 5.2 The Entity Decomposition Fields

These are the structured fields that break the node into its component parts:

**entity_type** — What broad category of ecological thing is this? Choose one:

| Value | When to Use | Examples |
|---|---|---|
| `environmental_variable` | A measurable aspect of ecosystem state at a point in time. Think of these as "state variables." | Soil pH, canopy height, water temperature, bare soil cover, light availability |
| `environmental_process` | Something that changes ecosystem state over time. Think of these as "flows" or "dynamics." | Nitrogen deposition, competitive exclusion, trophic cascade, decomposition |
| `management_intervention` | A deliberate human action. A special subtype of process with an implied human agent. | Prescribed burning, invasive species removal, seeding, dam removal |
| `species` | A biological taxon (species, genus, family, or higher group) whose measurable attribute participates in the causal relationship. This is distinct from environmental variables — it is the organism itself. | *Andropogon gerardii* (Big Bluestem), *Rhamnus cathartica* (European buckthorn), native bee communities (Hymenoptera), *Canis lupus* (grey wolf) |

**Important:** Species nodes still follow the entity + attribute + direction decomposition. The entity is the taxon, but you must still specify *what measurable property* of that taxon is changing. A node for "Big Bluestem" is incomplete — you need "Increased percent cover of *Andropogon gerardii*" or "Decreased population abundance of *Rhamnus cathartica*." The species node type just signals that the core entity is a biological organism rather than an abiotic variable or process.

**entity_term** — The core ecological entity, expressed as an ontology identifier (a "CURIE"). This is the "what thing" component. **Look for an ELMO term first** for environmental variables, processes, and ecosystem types. For species, use NCBITaxon. For chemicals, use CHEBI.

Common ontology prefixes you will use:

| Prefix | Ontology | Use For | Example |
|---|---|---|---|
| `ELMO:` | Ecolink Model Ontology | Environmental variables, processes, ecosystem types — **check ELMO first** | `ELMO:3620108` (Temperate pyric humid forest) |
| `NCBITaxon:` | NCBI Taxonomy | Species and higher taxa (required for all species nodes) | `NCBITaxon:9612` (*Canis lupus*) |
| `ENVO:` | Environment Ontology | Environmental features not yet in ELMO | `ENVO:00010483` (canopy) |
| `CHEBI:` | Chemical Entities of Biological Interest | Chemicals, nutrients, pollutants | `CHEBI:24279` (glucosinolate) |
| `GO:` | Gene Ontology | Biological processes not in ELMO | `GO:0009056` (growth) |
| `PATO:` | Phenotype and Trait Ontology | Qualities and measurable attributes | `PATO:0000070` (abundance) |
| `camo:` | Causal Mosaic Ontology | Causal predicates and causal terms (used on edges, not nodes) | `camo:causes` |

*Tip:* Browse the [ELMO documentation](https://timalamenciak.github.io/elmo/elmo.html) first. If no ELMO term exists, check the [Ontology Lookup Service (OLS)](https://www.ebi.ac.uk/ols4/). If no ontology has a suitable term, use a descriptive free-text label and **flag it as a candidate for a new ELMO term** (see Section 17).

**variable_attribute** — The measurable property that participates in causation. This is the "what property" component. Use PATO terms when possible.

Common attributes:

| Attribute | PATO Term | Typical Use |
|---|---|---|
| Abundance | `PATO:0000070` | Population counts, density |
| Concentration | `PATO:0000033` | Chemical concentrations in soil, water |
| Cover | `PATO:0001708` | Percent vegetation cover |
| Mass/Biomass | `PATO:0001019` | Above-ground biomass, body mass |
| Density | `PATO:0000574` | Stem density, population density |

**state_or_change_qualifier** — What state or change qualifies the attribute? Choose one:

| Value | Use When | Rosetta Prefix |
|---|---|---|
| `increased` | The attribute went up | "increased" |
| `decreased` | The attribute went down | "decreased" |
| `present` | The entity or attribute is present (binary) | "presence of" |
| `absent` | The entity or attribute is absent (binary) | "absence of" |
| `introduced` | The entity was introduced to the system | "introduction of" |
| `removed` | The entity was removed from the system | "removal of" |
| `unchanged` | No change (control, baseline) | — |
| `unspecified` | Direction not stated in text | — |

### 5.3 Context Qualifiers on Nodes

Nodes can carry qualifier fields that specify context affecting how the node itself should be interpreted:

- **process_context** — The ecological or management process context (e.g., "restoration management practice"). Use this when the node's meaning is tied to a specific process.
- **conditioned_by** — External variables that condition how the node should be interpreted (e.g., climate season, management timing).

**Where does ecosystem context go?** Ecosystem context is recorded on **edges**, not on nodes. This is because the ecosystem type describes the context of the *causal relationship* — the conditions under which C causes E. The same species or environmental variable can participate in causal relationships across different ecosystem types, but the specific causal claim (e.g., "light increases grass growth") was observed in a particular ecosystem. Therefore, ecosystem context belongs on the edge as part of the statement-level context qualifiers (see Section 6.4) and the context dependence annotation in Layer 3 (see Section 9.2, Feature: Context Dependence). **All ecosystem context annotations must use ELMO ecosystem type terms** (e.g., `ELMO:3620108` for "Temperate pyric humid forest"), not free-text descriptions or generic ENVO terms.

### 5.4 Node Categories

Assign one or more categories from the controlled vocabulary. These are compatible with the Biolink model and help with downstream integration. The most common categories you will use:

| Category | Description |
|---|---|
| `organism_taxon` | A species or higher taxonomic group |
| `biological_process` | A biological or ecological process |
| `environmental_process` | An environmental process |
| `abiotic_factor` | An abiotic environmental variable |
| `management_intervention` | A human management action |
| `ecological_outcome` | A measurable ecological state or change |
| `disturbance_event` | A disturbance (fire, flood, storm) |

### 5.5 Evidence Gap Map Support

Evidence gap map groupings are inferred from ontology terms and node categories rather than entered manually.

If a node represents a **management intervention** or an **ecological outcome**, make sure `entity_term`, `variable_attribute`, `entity_type`, and `categories` are as accurate as possible. Downstream tooling can use these ontology-grounded fields to infer intervention and outcome groupings.

External crosswalks between ontology terms and evidence gap map groupings should be maintained outside article annotations, for example as SSSOM files.

### 5.6 Step-by-Step: How to Annotate a Node

1. **Read the sentence or passage** that introduces the ecological entity.
2. **Identify the entity.** What thing is being discussed? A species? A chemical? An abiotic factor? A management action?
3. **Identify the attribute.** What measurable property is relevant? Abundance? Cover? Concentration? Biomass?
4. **Identify the state/change qualifier.** Did it increase, decrease, appear, disappear, remain unchanged, or is the qualifier unspecified?
5. **Compose the name** using the pattern: "[Direction] [attribute] of [entity]." For example: "Increased abundance of *Andropogon gerardii*."
6. **Look up the ontology terms** for the entity and attribute. Record them as CURIEs.
7. **Fill in context qualifiers** if the passage specifies an ecosystem, process, or conditioning variable.
8. **Write a brief description** in your own words, summarizing what the node represents as described in the source.

---

## 6. Part II — Annotating Edges (The Causal Relationships)

Edges are the heart of the annotation. Each edge represents a causal claim extracted from the text, and each edge carries **four layers** of annotation:

| Layer | What It Captures | Key Question |
|---|---|---|
| **Layer 1: Claim Strength** | How strong is the causal language? | Is the author hedging or asserting directly? |
| **Layer 2: Philosophical Account** | What kind of causation is claimed? | Is this about mechanisms, probabilities, interventions, or something else? |
| **Layer 3: Fifteen Causal Features** | What are the detailed characteristics of the claim? | Is it reversible? Is there a mediator? How strong is the effect? |
| **Layer 4: Evidential Basis** | What evidence supports the claim? | What kind of studies? How certain should we be? |

### 6.1 Basic Edge Structure

Every edge has these required fields:

| Field | Description | Example |
|---|---|---|
| `id` | Unique identifier | `edge:removal_to_cover` |
| `subject` | Node ID of the cause | `node:buckthorn_removal` |
| `object` | Node ID of the effect | `node:buckthorn_canopy_cover` |
| `predicate` | The type of causal relationship | `causally_decreases` |
| `claim_strength` | Layer 1 annotation | `direct_causal` |
| `philosophical_accounts` | Layer 2 annotation(s) | `[interventionist]` |
| `source_spans` | Text from the paper grounding the claim | (see Section 11) |

### 6.2 Choosing the Predicate

The predicate describes the type of relationship. All predicates are defined in **CAMO** (the Causal Mosaic Ontology). Choose from this controlled vocabulary:

| Predicate | Sign | Use When |
|---|---|---|
| `causes` | + | Direct positive causation: C produces E |
| `contributes_to` | + | C is one of several contributing factors to E |
| `enables` | + | C facilitates E but is not sufficient alone |
| `positively_regulates` | + | C upregulates or increases E |
| `associated_with` | ? | Statistical association without causal commitment |
| `correlated_with` | ? | Statistical correlation without direction or causal claim |
| `prevents` | − | C inhibits, blocks, or reduces E |
| `disrupts` | − | C degrades or suppresses E |
| `negatively_regulates` | − | C downregulates or decreases E |
| `regulates` | ± | C modulates E (direction may be positive or negative) |
| `mediates` | path | M is on the causal pathway between C and E |
| `moderates` | mod | Z modifies the strength/direction of the C→E relationship |
| `precedes` | time | Temporal precedence without causal commitment |

**Decision rule:** If the author uses strong, direct causal language ("X causes Y," "X leads to Y"), use `causes`. If the language is hedged ("X contributes to Y," "X is one factor in Y"), use `contributes_to`. If the author only claims a statistical pattern without asserting causation, use `associated_with` or `correlated_with`.

### 6.3 The `negated` Field

If the text explicitly states that a relationship does *not* hold (e.g., "Grazing did not affect soil carbon"), set `negated: true`. The predicate should still reflect the hypothesized relationship that was tested and rejected.

### 6.4 Statement-Level Context Qualifiers (Including Ecosystem Context)

Edges carry context qualifiers that describe the conditions under which the causal relationship was observed. **Ecosystem context is recorded on edges, not on nodes**, because it describes the setting of the causal claim.

- **ecosystem_context** — The ecosystem type in which this causal relationship was studied. **This must be an ELMO ecosystem type term** grounded in the IUCN Global Ecosystem Typology (GET) or NatureServe's International Vegetation Classification (IVC). For example, use `ELMO:3620108` for "Temperate pyric humid forest," not a free-text string like "temperate forest." Browse the [ELMO ecosystem types documentation](https://timalamenciak.github.io/elmo/ecosystems/) to find the correct term. If the paper's ecosystem does not map neatly to an existing ELMO term, use the closest match and flag the gap (see Section 17).
- **process_context** — The management or ecological process during which the relationship was observed. Use ELMO process terms where available.
- **conditioned_by** — Variables that condition (moderate, dampen, or enhance) the relationship but are not on the causal pathway themselves. These can be node IDs from the graph or ontology CURIEs.

---

## 7. Layer 1: Claim Strength

### 7.1 What You Are Coding

Layer 1 captures the **epistemic commitment of the text** — how strongly the author asserts the causal relationship. This is about the *language*, not the actual strength of evidence. An author might use very strong language based on weak evidence (overstatement) or very hedged language despite strong evidence (caution). You code what the text says, not what you think the evidence supports.

### 7.2 The Four Levels

| Level | Description | Example Language |
|---|---|---|
| `no_relationship` | The text explicitly states there is no relationship | "no significant effect"; "did not affect"; "no association was found" |
| `associational` | Correlation or co-occurrence language without a causal verb | "correlated with"; "associated with"; "co-occurred with"; "linked to" |
| `conditional_causal` | Hedged causal language; the author qualifies or softens the causal claim | "may cause"; "could contribute to"; "suggests a causal role"; "possibly leads to" |
| `direct_causal` | Unhedged, direct causal assertion | "causes"; "leads to"; "results in"; "produces"; "drives"; "determines" |

### 7.3 Practical Tips

- **Look at the verbs.** The main verb in the sentence is usually your best guide. "Is associated with" → associational. "Leads to" → direct causal. "May contribute to" → conditional causal.
- **Watch for hedging words.** Words like "may," "might," "could," "possibly," "suggests," "appears to," and "is thought to" all signal conditional causal language.
- **The abstract often has stronger language than the discussion.** If the same claim appears in multiple places with different strength, annotate the strongest version but note the inconsistency.
- **Do not upgrade or downgrade.** If the author says "associated with," code it as associational even if the evidence clearly supports a causal claim. Your job here is to capture the author's language, not your assessment of the evidence.

### 7.4 Recording the Causal Connective

In addition to the claim strength level, record the **causal connective** — the specific word or phrase that signals the causal relationship. This is a text span from the source document. Examples: "because," "leads to," "the mechanism by which," "results in."

---

## 8. Layer 2: Philosophical Account of Causation

### 8.1 Why Philosophical Accounts Matter

Different scientific disciplines and different types of evidence invoke different ideas about what "causation" means. A field ecologist who removes invasive plants and watches native species recover is using a different notion of causation than a statistician who finds a correlation in a large dataset. The Causal Mosaic framework, developed by philosophers Federica Russo and Phyllis Illari, recognizes that these are *complementary perspectives*, not competitors. A single causal claim can invoke multiple accounts simultaneously.

Your task is to identify which account(s) the text invokes for each edge.

### 8.2 The Three Families

The twelve philosophical accounts fall into three families:

**Family 1: Difference-Making** — These accounts ask: "Does C make a *difference* to E?"

| Account | Core Question | Key Linguistic Cues | Common in... |
|---|---|---|---|
| **Counterfactual** | Would E have occurred without C? | "without X"; "in the absence of"; "had X not occurred"; "if X had not..." | Experimental ecology, BACI designs |
| **Probabilistic** | Does C raise the probability of E? | "increases the risk of"; "associated with [+stats]"; "odds ratio"; "relative risk" | Epidemiology, population studies |
| **Interventionist** | Does intervening on C change E? | "experimental manipulation of"; "removal led to"; "treatment resulted in" | Restoration ecology, field experiments |
| **Variation** | Do variations in C track variations in E? | "regression coefficient"; "R²"; "variance explained"; "effect of X on Y" | Statistical ecology, gradient studies |

**Family 2: Production** — These accounts ask: "How does C *bring about* E?"

| Account | Core Question | Key Linguistic Cues | Common in... |
|---|---|---|---|
| **Process** | What conserved quantity is transmitted? | "energy transfer"; "nutrient transport"; "water flow"; "sediment transport" | Hydrology, biogeochemistry |
| **Mechanistic** | What entities and activities produce E from C? | "the mechanism by which"; "pathway from X to Y"; "step-by-step process" | Physiology, community ecology |
| **Information transmission** | What information is transmitted? | "signal"; "gene expression cascade"; "biomarker pathway" | Molecular ecology, chemical ecology |

**Family 3: Complementary** — These accounts provide additional structural perspectives.

| Account | Core Question | Key Linguistic Cues | Common in... |
|---|---|---|---|
| **Regularity** | Does C-type always/usually precede E-type? | "consistently observed"; "invariably accompanies"; "universal pattern" | Long-term monitoring, natural history |
| **INUS component** | Is C a necessary part of a sufficient cause constellation? | "contributing factor"; "one of several causes"; "in combination with" | Multifactorial studies |
| **Capacity** | Does C have the power to produce E? | "capacity to"; "tendency to"; "competitive ability"; "dispersal capacity" | Functional ecology, trait-based approaches |
| **Agency** | Can an agent bring about E by doing C? | "managers can achieve Y by doing X"; "restoration prescription"; "recommended intervention" | Management ecology, adaptive management |

### 8.3 How to Assign Philosophical Accounts

1. **Read the sentence or passage** containing the causal claim.
2. **Identify the linguistic cues.** What verbs, phrases, and framing does the author use? Refer to the tables above.
3. **Ask yourself: Is the author explaining WHETHER C makes a difference (difference-making) or HOW C brings about E (production)?** Often, both will be present in different parts of the text discussing the same relationship.
4. **Assign one or more accounts.** A single edge can invoke multiple accounts. For example, an author might present experimental evidence (interventionist) and then explain the biochemical pathway (mechanistic). In that case, assign both.
5. **Record the account family** (`difference_making`, `production`, or `complementary`) for each assigned account.

### 8.4 Common Combinations

In ecology, you will frequently encounter these combinations:

- **Interventionist + mechanistic:** "We removed buckthorn (intervention) and observed increased light (mechanism: canopy removal → less shading)."
- **Probabilistic + mechanistic:** "Higher forb diversity is associated with higher bee diversity (probabilistic), likely because diverse flowers provide temporally extended pollen resources (mechanism)."
- **Variation + mechanistic:** "Light explains 62% of variance in grass biomass (variation/regression), driven by photosynthetic rate (mechanism)."
- **Agency + interventionist:** "Managers can restore native grasslands by removing invasive shrubs (agency/prescription) — experimental plots confirmed this (interventionist)."

### 8.5 When You Are Unsure

If you genuinely cannot tell which account is invoked:

- Default to `mechanistic` if the text describes *how* C produces E at any level of detail.
- Default to `probabilistic` if the text reports statistical associations.
- Default to `interventionist` if the text describes an experimental manipulation or management action.
- Flag the edge for review and add an annotation note explaining your uncertainty.

---

## 9. Layer 3: The Fifteen Causal Features

Layer 3 is the most detailed part of the annotation. It captures fifteen distinct characteristics of the causal claim. Not every feature will be addressed in every paper — many will be coded as `not_addressed`. That is perfectly fine. Code what the text tells you; do not infer.

### 9.1 Feature Assertion Status

For many features, you will record a four-level assertion status:

| Status | Meaning |
|---|---|
| `explicitly_asserted` | The text directly states this feature |
| `implicitly_assumed` | The feature is strongly implied but not directly stated |
| `explicitly_denied` | The text states this feature does NOT hold |
| `not_addressed` | The text does not discuss this feature |

Use `not_addressed` generously. It is far better to leave a feature as "not addressed" than to guess.

### 9.2 The Fifteen Features, Explained

#### Feature 1: Necessity

**Question:** Is C necessary for E? Would E never occur without C?

- `explicitly_asserted` — Text says C is required/necessary for E.
- `explicitly_denied` — Text says E can occur without C.
- `not_addressed` — Most common. Few ecological papers discuss necessity explicitly.

*Example:* "Light is necessary for photosynthesis" → necessity is explicitly asserted for the light → grass growth edge.

#### Feature 2: Sufficiency

**Question:** Is C sufficient for E? Does C alone guarantee E?

- Rarely asserted in ecology, because ecological outcomes almost always depend on multiple factors.

*Example:* "Buckthorn removal alone does not guarantee native grass recovery; adequate seed sources must also be present" → sufficiency explicitly denied.

#### Feature 3: Direction

This feature has its own sub-structure rather than using the four-level assertion status.

**Direction status:** Is the direction of causation (which causes which) established?

| Status | Meaning |
|---|---|
| `asserted` | The text asserts a clear direction: C causes E, not E causes C |
| `uncertain` | The text acknowledges direction is debated or unclear |
| `bidirectional` | The text describes reciprocal causation (C↔E) |
| `not_addressed` | Direction not discussed |

**Direction evidence:** How was direction established?

| Value | Meaning |
|---|---|
| `experimental` | Experimental manipulation confirmed direction |
| `temporal_precedence` | C was observed to precede E in time |
| `theoretical` | Direction assumed based on theory or prior knowledge |
| `natural_experiment` | Natural experiment or instrumental variable |
| `structural_model` | DAG or structural equation model |

*Example:* A study removes buckthorn and then observes canopy cover decline. Direction status = `asserted`; direction evidence = `experimental`.

#### Feature 4: Temporal Ordering

**Question:** Does the text assert that C precedes E in time?

This is usually `explicitly_asserted` for experimental studies (where the intervention clearly happens before the outcome) and `implicitly_assumed` for observational studies that assume a temporal sequence.

#### Feature 5: Mediation

This feature has its own sub-structure.

**Question:** Does the text identify a mediating variable — something *on the causal pathway* between C and E?

A mediator is a variable through which C exerts its effect on E. In the chain C → M → E, M is the mediator. This is different from a moderator (see Feature 6), which *modifies* the C→E relationship but is not on the pathway.

| Field | Description |
|---|---|
| `status` | Feature assertion status |
| `mediator_node_ids` | Node IDs of the mediating variables |
| `pathway_description` | Free-text description of the mediating pathway |

*Example:* "Light availability increases grass growth" — but the text also discusses that increased light drives evapotranspiration, which reduces soil moisture, partially offsetting the benefit. Here, soil moisture is a mediator on a competing pathway.

**Key distinction: Mediator vs. Moderator**

| | Mediator | Moderator |
|---|---|---|
| Position | On the causal pathway (C → M → E) | Not on the pathway; modifies C → E from the side |
| Example | Light → photosynthesis → grass growth (photosynthesis mediates) | Drought modifies the light → grass growth relationship |
| Question it answers | *How* does C affect E? | *When* or *for whom* is the C→E effect stronger or weaker? |

#### Feature 6: Moderation (Effect Modification)

This feature also has its own sub-structure.

**Question:** Does the text identify a variable that modifies the strength or direction of the C→E relationship?

| Field | Description |
|---|---|
| `status` | Feature assertion status |
| `moderator_node_ids` | Node IDs of the moderating variables |
| `interaction_type` | Type of interaction (see below) |

Interaction types:

| Type | Meaning |
|---|---|
| `synergistic` | Combined effect of C and moderator is greater than the sum of their individual effects |
| `antagonistic` | Combined effect is less than the sum |
| `qualitative` | The *direction* of C→E changes at different levels of the moderator |
| `quantitative` | The *magnitude* (but not direction) changes at different levels |
| `not_specified` | Interaction is noted but type is not characterized |

*Example:* "Grass growth response to light is moderated by water availability. In drought years, the light benefit is diminished." Moderator = soil moisture / drought. Interaction type = `quantitative` (magnitude changes, but light still helps growth — direction does not reverse).

#### Feature 7: Strength

This feature has its own sub-structure for recording effect size information.

| Field | Description | Example |
|---|---|---|
| `status` | Feature assertion status | `explicitly_asserted` |
| `quantitative_value` | Effect size as reported in the text | "R² = 0.62, p < 0.001" |
| `quantitative_numeric` | Numeric value for computation | `0.62` |
| `qualitative_descriptor` | Qualitative label: `strong`, `moderate`, `weak`, `negligible` | `strong` |
| `dose_response` | Is a dose-response / gradient relationship described? | `true` |

**How to choose the qualitative descriptor:**

| Descriptor | Rough Guide |
|---|---|
| `strong` | Large effect sizes (e.g., R² > 0.5, large experimental differences, relative risk > 3) |
| `moderate` | Medium effect sizes (e.g., R² 0.2–0.5, moderate differences) |
| `weak` | Small effect sizes (e.g., R² < 0.2, small or marginal differences) |
| `negligible` | Trivially small effect |

These are rough guides. Use your best judgment and the context of the field. An R² of 0.3 might be "strong" for a field ecology study but "weak" for a lab experiment.

#### Feature 8: Specificity

**Question:** Is the C→E relationship specific — a one-to-one mapping — or does C affect many things (or is E caused by many things)?

- `explicitly_asserted` — The text claims C specifically affects E and not other things (rare in ecology).
- `explicitly_denied` — The text acknowledges C has many effects or E has many causes.
- `not_addressed` — Most common.

#### Feature 9: Stability

**Question:** Is the C→E relationship stable and consistent across different contexts, studies, or populations?

- `explicitly_asserted` — The text cites replication across sites, years, or studies.
- `explicitly_denied` — The text reports that the relationship varies across contexts.

*Example:* "Results align with meta-analysis showing consistent positive correlation between native plant diversity and native bee richness across temperate grasslands" → stability explicitly asserted.

#### Feature 10: Token or Type

**Question:** Is this a claim about a *specific* case (token) or a *general* pattern (type)?

| Value | Meaning | Example |
|---|---|---|
| `token` | A claim about this specific C causing this specific E | "The 2023 buckthorn removal at Pinery Provincial Park increased light by 300%." |
| `type` | A general claim that C-type causes E-type | "Removing invasive shrubs generally increases understory light availability." |
| `ambiguous` | Cannot tell | — |
| `not_addressed` | Not relevant | — |

#### Feature 11: Determinism

**Question:** Does C invariably produce E (deterministic), or does C merely raise the probability of E (probabilistic)?

| Value | Meaning |
|---|---|
| `deterministic` | C always produces E |
| `probabilistic` | C raises the probability of E but does not guarantee it |
| `ambiguous` | Cannot determine |
| `not_addressed` | Not discussed |

Most ecological claims are probabilistic. Reserve `deterministic` for truly invariant relationships (e.g., "Removing 100% of a plant's above-ground biomass reduces its canopy cover to zero" — this is mechanistically certain).

#### Feature 12: Proximate vs. Distal

**Question:** Is C a proximate (immediate, direct) cause or a distal (upstream, root) cause?

| Value | Meaning | Example |
|---|---|---|
| `proximate` | Immediate trigger | Light directly drives photosynthesis |
| `distal` | Upstream or root cause | Buckthorn removal is a distal cause of grass growth (operates through light) |
| `both_specified` | Both positions identified | — |
| `not_addressed` | Not discussed | — |

#### Feature 13: Contributing vs. Sole Cause

**Question:** Is C presented as the only cause of E, or one of several contributing factors?

| Value | Meaning |
|---|---|
| `sole_cause` | C is the only cause mentioned |
| `contributing_cause` | C is one of several factors |
| `not_addressed` | Not discussed |

Most ecological claims involve contributing causes. Use `sole_cause` only when the text explicitly states or strongly implies that C is the only factor.

#### Feature 14: Reversibility

**Question:** If you remove C, does E go back to its original state?

This feature is especially important in restoration ecology, where the question "Will the ecosystem recover if we remove the stressor?" is central.

| Value | Meaning | Ecological Example |
|---|---|---|
| `reversible` | Removing C reverses E | Removing invasive plants allows native recovery |
| `irreversible` | E persists even after C is removed | Soil degradation from overgrazing persists after livestock removal |
| `partially_reversible` | Partial recovery | Some but not all native species return |
| `hysteresis` | Recovery follows a different path than degradation | Degraded grassland takes a different recovery trajectory than degradation trajectory |
| `not_addressed` | Not discussed | — |

#### Feature 15: Proportionality

**Question:** Is the magnitude of the effect proportional to the magnitude of the cause? In other words, do bigger changes in C produce correspondingly bigger changes in E?

Often related to dose-response in the strength feature, but proportionality is more about whether the author explicitly discusses proportional scaling.

### 9.3 Context Dependence

In addition to the fifteen features above, each edge has a **context dependence** annotation with its own sub-structure:

| Field | Description | Example |
|---|---|---|
| `status` | Feature assertion status | `explicitly_asserted` |
| `scope_conditions` | Named conditions under which the relationship holds | "in acidic soils"; "at elevations above 2000m" |
| `geographic_scope` | Where does the claim apply? | "southern Ontario temperate zone" |
| `temporal_scope` | When does the claim apply? | "growing season (May-September)" |
| `ecosystem_scope` | What ecosystem type? | "temperate grassland, mesic sites" |

**This is one of the most important parts of the annotation.** Ecological relationships are almost always context-dependent. Pay close attention to any qualifications the author makes about when, where, and under what conditions the relationship holds.

---

## 10. Layer 4: Evidential Basis

Layer 4 captures the evidence supporting the causal claim. It implements a framework developed by philosophers Federica Russo and Jon Williamson, which distinguishes between the *type* of evidence (what kind of study) and the *object* of evidence (what the evidence is *about*: correlation or mechanism).

### 10.1 Evidence Type

What kind of study or reasoning produced the evidence? Select all that apply:

| Type | Description | Example |
|---|---|---|
| `randomized_experiment` | Randomized controlled trial or field experiment | Randomized block design testing fire effects |
| `natural_experiment` | Natural experiment or exogenous shock | Studying ecosystem changes after a natural fire |
| `quasi_experiment` | BACI, difference-in-differences, etc. | Before-after-control-impact study of restoration |
| `observational_longitudinal` | Longitudinal observational study | 10-year monitoring of vegetation change |
| `observational_cross_sectional` | Cross-sectional survey | Comparing invaded vs. uninvaded plots at one time |
| `mechanistic_study` | Lab or field study of mechanism | Measuring photosynthetic rates under different light |
| `structural_equation_model` | SEM or path analysis | Path model of trophic cascade |
| `meta_analysis` | Quantitative synthesis of multiple studies | Meta-analysis of invasive plant effects |
| `systematic_review` | Qualitative or quantitative systematic review | Cochrane-style systematic review |
| `modeling_simulation` | Computational model or simulation | Agent-based model of dispersal |
| `expert_judgment` | Expert elicitation or professional opinion | Delphi panel on restoration priorities |
| `case_study` | Single case study | Detailed report from one restoration site |
| `theoretical` | Deduction from theory | Applying optimal foraging theory |
| `indigenous_knowledge` | Traditional ecological knowledge | Indigenous fire management practices |
| `practitioner_experience` | Field practitioner experience | Land manager observations over 20 years |

### 10.2 Evidence Object

What does the evidence tell us *about*? This implements the **Russo-Williamson Thesis**, which holds that strong causal claims need *both* difference-making evidence (correlation) *and* production evidence (mechanism).

| Object | Meaning | Example |
|---|---|---|
| `correlation` | Evidence that C and E are statistically associated / C makes a difference to E | "R² = 0.62 between light and grass biomass" |
| `mechanism` | Evidence for a mechanism linking C to E | "Light drives photosynthesis via RuBisCO carboxylation" |
| `both` | Evidence addresses both | A study that both measures the correlation and traces the mechanism |

### 10.3 The Russo-Williamson Thesis

After recording evidence types and objects, answer this yes/no question:

> **`russo_williamson_satisfied`:** Does the evidence base include BOTH difference-making evidence (correlation) AND production evidence (mechanism)?

If the answer is `true`, the claim meets the evidential pluralism criterion — it has support from both statistical patterns and mechanistic understanding. This is a mark of strong evidence.

If the answer is `false`, note which type is missing. This helps identify where the evidence base has gaps.

### 10.4 Bradford Hill Viewpoints

Sir Austin Bradford Hill proposed nine "viewpoints" (not criteria — he was careful to call them viewpoints) for evaluating whether an observed association is causal. Record which viewpoints the evidence addresses:

| Viewpoint | Question | Addressed When... |
|---|---|---|
| `strength` | Is the association strong? | A large effect size is reported |
| `consistency` | Is it replicated across studies/contexts? | Multiple studies show the same pattern |
| `specificity` | Is C specifically associated with E? | One-to-one mapping claimed |
| `temporality` | Does C precede E? | Time ordering established |
| `biological_gradient` | Is there a dose-response? | More C → more E (or less E) |
| `plausibility` | Is a mechanism known? | A plausible mechanism is described |
| `coherence` | Does it fit broader knowledge? | Consistent with established theory |
| `experiment` | Does manipulation change E? | Experimental evidence presented |
| `analogy` | Are similar relationships known? | Analogous examples cited |

Record the count of viewpoints addressed (`bradford_hill_count`). This is a simple numeric summary: how many of the nine viewpoints does the evidence touch on?

### 10.5 Certainty Grade

Assign a GRADE-style certainty grade. This is your **overall assessment** of how certain we should be about this causal claim, considering all the evidence:

| Grade | Meaning | Language in Rosetta Statements |
|---|---|---|
| `high` | Confident the true effect is close to the estimated effect | "X increases Y" |
| `moderate` | Moderately confident; the true effect is likely close | "X probably increases Y" |
| `low` | Limited confidence; the true effect may differ substantially | "X may increase Y" |
| `very_low` | Very little confidence | "X might increase Y" |
| `not_assessed` | Certainty not formally evaluated | — |

**Factors that raise certainty:** Large effect sizes, replication across studies, clear mechanism, experimental design, multiple Bradford Hill viewpoints addressed, Russo-Williamson satisfied.

**Factors that lower certainty:** Small sample sizes, confounding not addressed, mechanism unclear, observational design only, contradictory results, narrow geographic or temporal scope.

Provide a brief `certainty_rationale` — a few sentences explaining why you assigned this grade.

---

## 11. Recording Provenance and Source Information

### 11.1 Source Spans (Text Grounding)

Every edge and node should be grounded in the actual text of the source document. For each, record one or more **text spans**:

| Field | Description | Example |
|---|---|---|
| `text` | The verbatim text from the paper | "Native grass standing crop correlated strongly with growing-season PAR..." |
| `start_char` | Character offset where the span starts | `3100` |
| `end_char` | Character offset where the span ends | `3350` |

If your annotation tool provides character offsets, use them. If not, the verbatim text field alone is sufficient.

### 11.2 Source Document

Record bibliographic metadata for the source paper:

| Field | Description |
|---|---|
| `doi` | Digital object identifier |
| `title` | Paper title |
| `authors` | List of authors |
| `year` | Publication year |
| `journal` | Journal name |
| `section` | Which section of the paper the claim comes from (abstract, results, discussion, etc.) |
| `study_country` | Country or countries where the study was conducted; separate multiple countries with semicolons |
| `study_state_or_province` | State, province, territory, or comparable region; separate multiple regions with semicolons |
| `study_coordinates` | Structured coordinate set or sets; use one entry per reported centroid or bounded study area |
| `study_period_start` / `study_period_end` | When data was collected |
| `study_ecosystem` | Ecosystem type |
| `study_design` | Study design classification |

### 11.3 Annotator Metadata

Every edge should record who annotated it and when:

| Field | Description |
|---|---|
| `annotator` | Your identifier (e.g., ORCID if you have one, or a project-assigned ID) |
| `annotation_confidence` | Your confidence in the overall annotation, 0.0 to 1.0 |
| `annotation_timestamp` | When you created the annotation |
| `annotation_notes` | Free-text notes — anything you want to flag for reviewers |

**Use `annotation_notes` generously.** This is your space to explain difficult judgment calls, flag uncertainties, note ambiguities in the text, or highlight things that puzzled you.

---

## 12. Rendering Outputs: FCM Weights and Rosetta Statements

The annotation includes two computed outputs that you should fill in:

### 12.1 FCM Weight

The **Fuzzy Cognitive Map (FCM) weight** is a number between −1.0 and +1.0 that summarizes the strength and direction of the causal relationship:

| Range | Meaning |
|---|---|
| +0.7 to +1.0 | Strong positive effect |
| +0.4 to +0.69 | Moderate positive effect |
| +0.1 to +0.39 | Weak positive effect |
| 0.0 | No effect or undetermined |
| −0.1 to −0.39 | Weak negative effect |
| −0.4 to −0.69 | Moderate negative effect |
| −0.7 to −1.0 | Strong negative effect |

The FCM weight is derived from the predicate sign, claim strength, and strength annotation. Record the source of the weight in `fcm_weight_source` (e.g., "derived from schema: strong quantitative effect" or "expert elicitation").

### 12.2 Rosetta Statement

A **Rosetta Statement** is a template-based natural language sentence rendering the edge in plain English. It combines the node names, predicate, and certainty grade. Examples:

- Certainty = high: "Removal of European buckthorn **increases** light availability at ground level."
- Certainty = moderate: "Light availability **probably increases** native grass biomass."
- Certainty = low: "Light availability **may increase** native forb species richness."
- Certainty = very low: "Grass biomass **might decrease** native forb richness."

You do not need to compose these from scratch — they are generated from a template. But you should verify that the generated statement reads sensibly and edit the `rosetta_statement` field if needed.

---

## 13. Worked Example: Grassland Restoration

Let us walk through annotating one edge in detail, using the sample data from a study of European buckthorn removal in a southern Ontario temperate grassland.

### 13.1 The Source Sentence

> "Native grass standing crop at peak season correlated strongly with growing-season PAR integration (R² = 0.62, p < 0.001), with graminoids under removed buckthorn achieving 340 ± 45 g m⁻² versus 120 ± 30 g m⁻² under intact canopy."

### 13.2 Identifying the Nodes

**Source node:** Light Availability at Ground Level

- entity_type: `environmental_variable`
- entity_term: `ENVO:00010165` (light)
- variable_attribute: PAR in mol/m²/day
- state_or_change_qualifier: `increased`

**Target node:** Native Grass Growth

- entity_type: `biological_process`
- entity_term: `GO:0009056` (growth)
- variable_attribute: above-ground grass biomass in g/m²
- state_or_change_qualifier: `increased`

### 13.3 Annotating the Edge

**Basic structure:**

| Field | Value |
|---|---|
| id | `edge:light_to_grass_growth` |
| subject | `node:light_availability` |
| object | `node:native_grass_growth` |
| predicate | `causally_increases` |

**Layer 1 — Claim Strength:**

The text says "correlated strongly" — this is associational language ("correlated"), but in the broader context of the paper, the authors describe a clear mechanistic pathway (photosynthesis) and present before-after comparisons. Looking at the full passage, the authors also write: "In experimental gap studies, light exclusion reduced native grass growth by 48%, confirming light limitation." This is direct causal language ("confirming"). Assign: `direct_causal`.

**Layer 2 — Philosophical Account:**

- The R² = 0.62 invokes a **variation** account (systematic covariation).
- The experimental gap study invokes an **interventionist** account.
- The discussion of photosynthetic pathways invokes a **mechanistic** account.
- Assign all three: `[mechanistic, interventionist, variation]`.
- Account families: `[production, difference_making]`.

**Layer 3 — Fifteen Features:**

| Feature | Value | Reasoning |
|---|---|---|
| Necessity | `implicitly_assumed` | Light is implicitly necessary for photosynthesis |
| Sufficiency | `explicitly_denied` | Paper notes water availability also matters |
| Direction | Status: `asserted`; Evidence: `experimental` | Gap study confirms direction |
| Temporal ordering | `explicitly_asserted` | Light increase precedes biomass accumulation |
| Mediation | Status: `partially_characterized`; Mediators: `[node:soil_moisture]`; Pathway: "Light increases ET, which reduces soil moisture, partially offsetting grass growth" | Competing mediating pathway discussed |
| Moderation | Status: `addressed`; Moderators: `[node:soil_moisture]`; Interaction type: `quantitative` | Drought years reduce the light benefit |
| Strength | `explicitly_asserted`; Quantitative: "R² = 0.62"; Numeric: 0.62; Qualitative: `strong`; Dose-response: `true` | Clear quantitative reporting |
| Specificity | `not_addressed` | Not discussed |
| Stability | `not_addressed` | Not discussed for this specific edge |
| Token or type | `type` | General claim about grass response to light |
| Determinism | `probabilistic` | R² < 1.0; variation in response |
| Proximate/distal | `proximate` | Light is the immediate driver of photosynthesis |
| Contributing/sole | `contributing_cause` | Water and nutrients also matter |
| Reversibility | `not_addressed` | Not discussed for this edge |
| Proportionality | `explicitly_asserted` | Dose-response relationship described |

**Context dependence:**
- Scope conditions: "C4 native grass species"; "non-drought years"; "nitrogen not limiting"
- Geographic scope: "southern Ontario temperate grassland"
- Temporal scope: "growing season (May-September); peak effect Aug-Sept"
- Ecosystem scope: "temperate grassland understory"

**Layer 4 — Evidential Basis:**

- Evidence types: `[observational_cross_sectional, randomized_experiment, theoretical]`
- Evidence objects: `[correlation, mechanism]`
- Russo-Williamson satisfied: `true` (both correlation from R² and mechanism from photosynthesis literature)
- Bradford Hill viewpoints: `[strength, consistency, biological_gradient, plausibility, experiment]` → count = 5
- Certainty grade: `high`
- Certainty rationale: "Multiple independent lines of evidence — observational correlation, experimental light manipulation, well-established mechanism from plant physiology. Effect sizes consistent across sites."

**Rendering outputs:**

- Rosetta statement: "Light availability increases native grass biomass."
- FCM weight: 0.75
- FCM weight source: "derived from schema: strong effect size and mechanism"

---

## 14. Common Pitfalls and How to Avoid Them

### Pitfall 1: Creating "bare thing" nodes

**Wrong:** Node name = "Wolves"
**Right:** Node name = "Increased wolf population abundance"

Always decompose into entity + attribute + direction.

### Pitfall 2: Confusing claim strength with evidence quality

Claim strength (Layer 1) codes the *language* the author uses. Evidence quality (Layer 4) codes the actual *strength of the evidence base*. An author might say "X causes Y" (direct causal language → `direct_causal`) based on a single observational study (low evidence quality → certainty grade `low`). These are independent judgments.

### Pitfall 3: Confusing mediators and moderators

A **mediator** is *on the causal pathway* (C → M → E). It answers "how does C affect E?"

A **moderator** is *not on the pathway* — it changes the C→E relationship from the side. It answers "when or under what conditions is the C→E effect stronger or weaker?"

Test: If you block M, does C lose its ability to affect E? If yes, M is a mediator. If blocking M merely changes the *size* of C's effect on E, M is a moderator.

### Pitfall 4: Over-annotating features as "explicitly asserted"

When in doubt, use `not_addressed`. The text must actually *state* or *clearly imply* a feature for it to be coded as explicitly asserted or implicitly assumed. Do not infer features from your own ecological knowledge.

### Pitfall 5: Ignoring competing or offsetting pathways

Ecological systems have feedbacks and competing effects. If the text describes a pathway where C increases E through one route but decreases E through another (e.g., light increases grass growth via photosynthesis but decreases soil moisture via evapotranspiration), these need to be captured as separate edges with appropriate mediation annotations.

### Pitfall 6: Forgetting context dependence

Nearly every ecological relationship is context-dependent. If the author says "in non-drought years" or "in temperate grasslands" or "at elevations above 2000m," that information must go into the context dependence annotation. Pay attention to qualifying clauses.

### Pitfall 7: Assuming Russo-Williamson is satisfied

The Russo-Williamson thesis requires *both* correlation evidence *and* mechanism evidence. If the paper only reports a correlation without discussing mechanism (or vice versa), mark `russo_williamson_satisfied: false`. Many papers address only one side.

### Pitfall 8: Using the wrong ontology prefix

Double-check that you are using the right ontology for each entity type:
- Species → `NCBITaxon:`
- Chemicals → `CHEBI:`
- Environments and habitats → `ENVO:`
- Biological processes → `GO:`
- Qualities and attributes → `PATO:`

---

## 15. Decision Flowcharts

### Flowchart A: Choosing a Predicate

```
Read the causal sentence
        │
        ▼
Does the author assert causation?
        │
   ┌────┴────┐
   No        Yes
   │          │
   ▼          ▼
Is it a      Does C increase E
correlation?  or decrease E?
   │             │
   ▼          ┌──┴──┐
correlated_   │     │
with       Increase  Decrease
              │        │
              ▼        ▼
         Is C the    Is C the
         sole/main   sole/main
         cause?      cause?
          │           │
     ┌────┴───┐  ┌───┴────┐
     Yes      No  Yes     No
     │        │   │       │
     ▼        ▼   ▼       ▼
   causes  contributes prevents disrupts
           _to                  (or negatively
                                _regulates)
```

### Flowchart B: Assigning Certainty Grade

```
Start with "moderate" as your baseline
          │
          ▼
Is there experimental evidence? ──Yes──▶ Move toward "high"
          │ No
          ▼
Is the mechanism well-understood? ──Yes──▶ Move toward "high"
          │ No
          ▼
Are there multiple independent studies? ──Yes──▶ Move toward "high"
          │ No
          ▼
Is there confounding or small sample size? ──Yes──▶ Move toward "low"
          │ No
          ▼
Is the evidence purely observational
with no mechanistic support? ──Yes──▶ Move toward "low" or "very_low"
          │ No
          ▼
Stay at "moderate"
```

---

## 16. Quick Reference Tables

### 16.1 Complete Predicate Reference

| Predicate | Sign | Default FCM Weight | Rosetta Template |
|---|---|---|---|
| causes | + | 0.7 | "{subject} causes {object}" |
| contributes_to | + | 0.4 | "{subject} contributes to {object}" |
| enables | + | 0.5 | "{subject} enables {object}" |
| positively_regulates | + | 0.5 | "{subject} positively regulates {object}" |
| associated_with | ? | 0.3 | "{subject} is associated with {object}" |
| correlated_with | ? | 0.2 | "{subject} is correlated with {object}" |
| prevents | − | −0.6 | "{subject} prevents {object}" |
| disrupts | − | −0.5 | "{subject} disrupts {object}" |
| negatively_regulates | − | −0.5 | "{subject} negatively regulates {object}" |
| regulates | ± | 0.0 | "{subject} regulates {object}" |
| mediates | path | 0.0 | "{subject} mediates the effect on {object}" |
| moderates | mod | 0.0 | "{subject} moderates the relationship with {object}" |
| precedes | time | 0.0 | "{subject} precedes {object}" |

### 16.2 State/Change Qualifier Quick Reference

| Qualifier | Use When | FCM Sign |
|---|---|---|
| increased | Attribute went up | + |
| decreased | Attribute went down | − |
| present | Entity/attribute is present (binary) | + |
| absent | Entity/attribute is absent (binary) | − |
| introduced | Entity introduced to system | + |
| removed | Entity removed from system | − |
| unchanged | No change (control/baseline) | neutral |
| unspecified | State/change qualifier not stated | neutral |

### 16.3 Certainty Grade Summary

| Grade | Verb Modifier | Typical Evidence Profile |
|---|---|---|
| high | (none) | Experimental + mechanistic + replicated |
| moderate | "probably" | Observational + mechanistic, or experimental but limited replication |
| low | "may" | Observational only, or single study with plausible mechanism |
| very_low | "might" | Weak observational evidence, no mechanism, conflicting results |

### 16.4 Bradford Hill Viewpoints Quick Reference

| # | Viewpoint | One-Sentence Test |
|---|---|---|
| 1 | Strength | Is the effect size large? |
| 2 | Consistency | Has it been replicated elsewhere? |
| 3 | Specificity | Is C → E a one-to-one relationship? |
| 4 | Temporality | Does C clearly precede E? |
| 5 | Biological gradient | More C → more (or less) E? |
| 6 | Plausibility | Is there a plausible mechanism? |
| 7 | Coherence | Does it fit with broader knowledge? |
| 8 | Experiment | Does manipulating C change E? |
| 9 | Analogy | Are similar relationships known? |

---

## 17. Suggesting New Ontology Terms

ELMO and CAMO are living ontologies that grow as the community identifies gaps. As an annotator, you are in a unique position to discover these gaps — you encounter the full diversity of ecological language in the papers you read. **We actively encourage you to flag missing terms.**

### 17.1 When to Suggest a New ELMO Term

You should suggest a new term when:

- **An environmental variable or process in the paper has no good match in ELMO.** For example, the paper discusses "mycorrhizal network connectivity" and you cannot find an ELMO term that captures this concept.
- **An ecosystem type in the paper does not map to any existing ELMO ecosystem type.** The IUCN GET and NatureServe IVC are comprehensive but not exhaustive, especially for transitional, novel, or regionally specific ecosystem types.
- **An existing ELMO term is close but not quite right.** For example, ELMO has a general "grassland" term but the paper describes a very specific subtype (e.g., "calcareous fen meadow") that is not distinguished in ELMO.

### 17.2 How to Flag a Gap

When you encounter a missing term during annotation:

1. **Use the best available term** as a placeholder. Record it as the `entity_term` or `ecosystem_context` with a note.
2. **Add a flag in `annotation_notes`** using the prefix `NEW_TERM_NEEDED:` followed by a description:
   ```
   annotation_notes: |
     NEW_TERM_NEEDED: No ELMO term for "mycorrhizal network connectivity."
     Used GO:0009056 (growth) as a rough placeholder. Suggested parent class:
     ELMO environmental_variable. Suggested definition: "The degree of
     hyphal connection between plant root systems via arbuscular or
     ectomycorrhizal fungi."
   ```
3. **File a GitHub issue** on the ELMO repository ([https://github.com/timalamenciak/elmo/issues](https://github.com/timalamenciak/elmo/issues)) if you have a GitHub account. Use the issue template provided in the repository. Include:
   - **Suggested term label** (e.g., "mycorrhizal network connectivity")
   - **Suggested definition** (one sentence, following the genus-differentia pattern: "A [parent class] that [differentia]")
   - **Suggested parent class** in the ELMO hierarchy
   - **Source paper** where you encountered the term (DOI)
   - **Why existing terms are insufficient** (brief explanation)

### 17.3 When to Suggest a New CAMO Term

CAMO gaps are rarer, since the causal vocabulary is more abstract and stable. However, you might encounter:

- A **causal predicate** that doesn't fit any existing option (e.g., "triggers" as distinct from "causes" — implying a threshold effect)
- An **evidence type** not covered by the current list (e.g., "citizen science monitoring" as distinct from observational studies)
- A **philosophical account** that seems to be invoked but doesn't match any of the twelve accounts

Flag these the same way: `NEW_TERM_NEEDED:` in annotation notes, and file a GitHub issue at [https://github.com/timalamenciak/camo/issues](https://github.com/timalamenciak/camo/issues).

### 17.4 Term Suggestion Quality Guidelines

Good term suggestions follow these principles:

- **One concept per term.** Do not bundle multiple ideas into a single term request.
- **Use the genus-differentia definition pattern.** "X is a [broader category] that [distinguishing feature]." For example: "Calcareous fen meadow is a grassland ecosystem that occurs on alkaline, waterlogged peat substrates."
- **Provide at least one source.** Cite the paper where you encountered the concept.
- **Check that the term doesn't already exist** under a different label. Search ELMO, ENVO, and OLS before suggesting.
- **Suggest where the term fits** in the existing hierarchy. What would its parent class be?

---

## 18. Glossary

**BACI design** — Before-After-Control-Impact study design. A quasi-experimental approach that measures an outcome before and after an intervention at both treatment and control sites.

**Bradford Hill viewpoints** — Nine considerations proposed by Sir Austin Bradford Hill (1965) for evaluating whether an observed association is causal. Not criteria (none is required); rather, viewpoints that collectively strengthen or weaken a causal inference.

**CAMO** — Causal Mosaic Ontology ([https://github.com/timalamenciak/camo](https://github.com/timalamenciak/camo)). The causal semantics layer of the schema, implementing Illari and Russo's (2014) causal mosaic framework. CAMO defines all causal predicates (`causes`, `contributes_to`, `prevents`, etc.), philosophical account classifications, and evidence type terms used in edge annotations.

**Causal connective** — The word or phrase in a sentence that signals a causal relationship (e.g., "because," "leads to," "the mechanism by which").

**CURIE** — Compact Uniform Resource Identifier. A shorthand for ontology terms: `prefix:identifier` (e.g., `NCBITaxon:9612` for *Canis lupus*).

**Difference-making** — A family of philosophical accounts of causation that ask whether the cause makes a difference to the effect. Includes counterfactual, probabilistic, interventionist, and variation accounts.

**Dose-response** — A relationship where the magnitude of the effect scales with the magnitude of the cause.

**EGM** — Evidence Gap Map. A matrix visualization showing which intervention-outcome combinations have been studied and what quality of evidence exists.

**ELM** — Ecolink Model. A pattern for decomposing ecological relationships into entity + attribute + direction, with contextual qualifiers.

**ELMO** — Ecolink Model Ontology ([https://github.com/timalamenciak/elmo](https://github.com/timalamenciak/elmo)). An application ontology that describes ecosystem management processes, ecosystem types, and environmental variables. ELMO incorporates the IUCN Global Ecosystem Typology 2.0 (GET) and NatureServe's International Vegetation Classification (IVC). All ecosystem context annotations must use ELMO terms.

**Entity** — The "what thing" component of a node: the species, chemical, abiotic factor, or process at the core of the ecological variable.

**FCM** — Fuzzy Cognitive Map. A weighted directed graph used for qualitative modeling of complex systems.

**GRADE** — Grading of Recommendations, Assessment, Development and Evaluations. A widely used framework for rating certainty of evidence, adapted here for ecological causal claims.

**Hysteresis** — A situation where the recovery trajectory of a system follows a different path than the degradation trajectory. Common in ecosystems with alternative stable states.

**INUS** — An Insufficient but Necessary part of an Unnecessary but Sufficient condition. A philosophical framework for understanding contributing causes.

**Labeled property graph** — A graph data structure where both nodes and edges can carry arbitrary sets of named properties (key-value pairs).

**Mediator** — A variable on the causal pathway between C and E: C → M → E. The mediator transmits or explains the effect of C on E.

**Moderator** — A variable that modifies the strength or direction of the C→E relationship without being on the causal pathway.

**Node** — An ecological entity in the causal graph, representing a change in state of an environmental variable, process, or taxon.

**Ontology** — A formal, structured vocabulary of terms in a domain, with defined relationships between terms. Used for consistent, machine-readable annotation.

**Production** — A family of philosophical accounts of causation that ask how the cause brings about the effect. Includes process, mechanistic, and information transmission accounts.

**Rosetta Statement** — A template-based natural language rendering of a causal edge, designed to be readable by non-specialists.

**Russo-Williamson Thesis** — The thesis that establishing causality requires *both* evidence of difference-making (correlation, statistical association) *and* evidence of production (mechanism). Named after philosophers Federica Russo and Jon Williamson.

**Text span** — A specific passage of text in the source document that grounds a node or edge annotation. Provides provenance and supports retrieval.

---

*This guide is a living document. If you encounter situations not covered here, please document them in your annotation notes and flag them for the project team.*

---
---

# Appendix A: LLM-Assisted Extraction — Best Practices and Prompt

This appendix provides guidance and a ready-to-use prompt for using a large language model (LLM) as a first-pass extraction tool in a **human-in-the-loop** workflow. The LLM generates candidate annotations from source text; a trained human annotator then reviews, corrects, and finalizes every output.

---

## A.1 The Human-in-the-Loop Workflow

The recommended workflow has four stages:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  1. PREPARE  │────▶│  2. EXTRACT  │────▶│  3. REVIEW   │────▶│ 4. FINALIZE  │
│  Source text  │     │  LLM draft   │     │  Human check │     │  Validated   │
│  + metadata  │     │  YAML output │     │  + correct   │     │  YAML record │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
     Human                LLM              Human (critical)         Human
```

**Stage 1 — Prepare:** The human annotator selects the source paper, identifies the relevant sections (usually Results + Discussion), and gathers metadata (DOI, authors, study site coordinates, etc.).

**Stage 2 — Extract:** The LLM processes the text using the prompt below and produces a candidate YAML output conforming to the Causal Mosaic 0.4 schema.

**Stage 3 — Review (Critical):** The human annotator reviews *every* field of *every* node and edge. This is the most important stage. The human must:

- Verify ontology CURIEs are correct (LLMs frequently hallucinate ontology IDs)
- Check that claim strength reflects the *author's language*, not the LLM's interpretation
- Confirm philosophical accounts match the actual framing in the text
- Validate that the fifteen causal features are faithfully coded from the text, not inferred
- Verify source spans are verbatim quotations (LLMs may paraphrase or fabricate)
- Adjust FCM weights and certainty grades using domain expertise
- Add any edges or nodes the LLM missed
- Remove any hallucinated relationships not supported by the text

**Stage 4 — Finalize:** The human produces the validated YAML, records their annotator ID and confidence, and submits for quality assurance.

---

## A.2 Best Practices for LLM-Assisted Extraction

### A.2.1 What LLMs Do Well

- **Sentence-level causal claim detection.** LLMs are good at finding sentences containing causal language and distinguishing them from purely descriptive text.
- **Claim strength classification.** The four-level linguistic scale (no_relationship → associational → conditional_causal → direct_causal) is a surface-language task that LLMs handle reliably.
- **Predicate selection.** Choosing between `causes`, `contributes_to`, `associated_with`, etc. based on verb choice is a pattern-matching strength.
- **Extracting quantitative values.** Pulling out R² values, p-values, effect sizes, and sample sizes from results sections.
- **Drafting free-text fields.** Descriptions, pathway descriptions, mechanism descriptions, and annotation notes.
- **Identifying mediators and moderators from explicit text.** When the paper says "mediated by X" or "moderated by Y," the LLM will usually catch it.

### A.2.2 What LLMs Do Poorly — Known Failure Modes

| Failure Mode | Description | Mitigation |
|---|---|---|
| **Ontology CURIE hallucination** | LLMs invent plausible-looking but non-existent ontology identifiers (e.g., `ENVO:99999999`). | **Always verify every CURIE** against OLS, NCBI Taxonomy, or the relevant ontology browser. See Section A.4 for a grounding tool. |
| **Over-assertion of features** | LLMs tend to fill in features as `explicitly_asserted` when they should be `not_addressed`, drawing on general ecological knowledge rather than what the text actually says. | Instruct the LLM to default to `not_addressed`. During review, ask: "Does the paper *actually say this*, or is the LLM using background knowledge?" |
| **Fabricated source spans** | LLMs may paraphrase or subtly alter quoted text, or generate text that sounds plausible but does not appear in the paper. | **Verify every source span** against the original document. Use string-search (Ctrl+F) to confirm exact match. |
| **Conflating claim strength with evidence quality** | The LLM may assign `direct_causal` claim strength to well-evidenced claims even when the author uses hedged language. | Check the actual verbs and hedging words in the source sentence, not the LLM's assessment. |
| **Missing competing pathways** | LLMs tend to extract the "main story" and miss competing, offsetting, or feedback pathways (e.g., light → grass growth is captured but light → soil moisture reduction → reduced grass growth is missed). | Specifically prompt for competing effects and review the Discussion section for caveats. |
| **Philosophical account misclassification** | LLMs may default to `mechanistic` for everything, or confuse `interventionist` with `counterfactual`. | Cross-check against the linguistic cue tables in Section 8.2 of this guide. |
| **Russo-Williamson over-satisfaction** | LLMs tend to mark `russo_williamson_satisfied: true` too readily, counting general scientific knowledge as "mechanism evidence" even when the paper itself does not discuss mechanism. | Only mark `true` if *this paper* (or cited sources within it) provides both correlation and mechanism evidence. |
| **Temporal extent confusion** | LLMs confuse the study period (when fieldwork happened) with the temporal extent of the causal effect (how long the effect takes to manifest). | Review temporal fields carefully; they answer different questions. |
| **Invented Bradford Hill viewpoints** | LLMs may claim the evidence addresses `experiment` or `consistency` when the paper only provides observational data from a single site. | Count viewpoints conservatively; each must be clearly supported by the text. |

### A.2.3 Prompt Engineering Principles

1. **Supply the complete schema.** The LLM needs the full enum definitions and class structures. Truncated schemas produce inconsistent output.
2. **Include a worked example.** Providing one complete annotated edge (like the grassland example from Section 13 of this guide) dramatically improves output quality.
3. **Enforce YAML output format.** Specify that the LLM must output valid YAML conforming to the schema. Request no additional prose or commentary outside the YAML block.
4. **Instruct conservative defaults.** Tell the LLM to use `not_addressed` as the default for all fifteen causal features, and only change it when the text explicitly supports a different value.
5. **Separate extraction from interpretation.** Tell the LLM to extract what the text says, not what it knows to be true from training data. This reduces over-assertion.
6. **Request self-critique.** Ask the LLM to flag low-confidence annotations so the human reviewer knows where to focus attention.
7. **Chunk long papers.** Process one section at a time (e.g., Results paragraphs individually), then merge. This reduces context window pressure and improves recall.

### A.2.4 Quality Assurance Checklist for Human Reviewers

After receiving LLM output, walk through this checklist for every edge:

- [ ] **Source spans verified.** Every `text` field in `source_spans` is a verbatim quote from the paper (not paraphrased).
- [ ] **Ontology CURIEs verified.** Every `entity_term` and `variable_attribute` has been checked against an ontology browser.
- [ ] **Claim strength matches author language.** Re-read the source sentence and confirm the verb/hedge level matches the assigned `claim_strength`.
- [ ] **Philosophical accounts match text framing.** Cross-check against linguistic cues (Section 8.2).
- [ ] **Causal features are text-grounded.** For every feature coded as anything other than `not_addressed`, confirm the paper explicitly or clearly implicitly supports that coding.
- [ ] **Mediators vs. moderators correctly distinguished.** Apply the "block M" test (Section 9.2, Feature 5).
- [ ] **Competing/offsetting pathways captured.** Check the Discussion for caveats or competing effects that should be separate edges.
- [ ] **Russo-Williamson assessment is conservative.** Only `true` if the paper provides both statistical and mechanistic evidence.
- [ ] **Bradford Hill count is accurate.** Each viewpoint must be supported by specific evidence in the text.
- [ ] **Certainty grade is justified.** The `certainty_rationale` should cite specific evidence characteristics.
- [ ] **FCM weight sign matches predicate.** Positive predicates should have positive weights; negative predicates should have negative weights.
- [ ] **Temporal extent ≠ study period.** Confirm these are distinguished correctly.
- [ ] **No hallucinated edges.** Every edge must be traceable to a specific passage in the paper.

---

## A.3 The Extraction Prompt

Below is the complete prompt for LLM-assisted extraction. Copy the entire block and provide it as a system prompt or initial instruction, together with the source text to be annotated.

> **Note on ontology grounding:** This prompt instructs the LLM to produce *candidate* CURIEs that MUST be verified by a human or an external grounding tool. The LLM does not have reliable access to ontology databases, so every CURIE it produces should be treated as a draft. See Section A.4 for tooling recommendations.

---

````
You are an expert ecological evidence annotator. Your task is to extract causal
claims from scientific text and produce structured annotations conforming to the
Causal Mosaic schema (version 0.4.0). You will output valid YAML and nothing else.

## YOUR ROLE

You are the FIRST PASS in a human-in-the-loop pipeline. A trained human annotator
will review and correct every field you produce. Your goal is to be thorough (high
recall — do not miss claims) and conservative (prefer `not_addressed` over guessing).

## CORE PRINCIPLES

1. CAUSATION IS BETWEEN CHANGES IN STATE, NOT BETWEEN THINGS.
   Every node must decompose into: entity (what thing) + attribute (what measurable
   property) + direction (which way it changed). Never create a bare-entity node
   like "wolves" — always specify "increased/decreased [attribute] of [entity]."

2. EXTRACT WHAT THE TEXT SAYS, NOT WHAT YOU KNOW.
   Your training data contains ecological knowledge. Do NOT use it to fill in
   features the paper does not discuss. If the paper does not mention mechanism,
   do not code mechanism as "well_characterized" just because you know the
   mechanism from your training. Code it as `not_addressed`.

3. DEFAULT TO `not_addressed`.
   For all fifteen causal features, start with `not_addressed` and only change it
   when the text explicitly or clearly implicitly supports a different value.

4. CLAIM STRENGTH TRACKS LANGUAGE, NOT EVIDENCE QUALITY.
   "associated with" → `associational`, even if the evidence is strong.
   "causes" → `direct_causal`, even if the evidence is weak.
   Code the author's words, not your assessment.

5. SOURCE SPANS MUST BE VERBATIM.
   Every `text` field in source_spans must be an exact, character-for-character
   quotation from the provided source text. Do not paraphrase, summarize, or
   fabricate. If you cannot find an exact span, leave the text field empty and
   note this in `annotation_notes`.

6. ONTOLOGY CURIES ARE DRAFTS.
   You do not have access to ontology databases. Provide your best guess for
   CURIEs using the prefixes below, but mark all ontology IDs with a confidence
   flag. The human reviewer will verify every CURIE.
   - Taxa: NCBITaxon:{id}
   - Environments: ENVO:{id}
   - Chemicals: CHEBI:{id}
   - Biological processes: GO:{id}
   - Qualities/attributes: PATO:{id}

7. FLAG UNCERTAINTY.
   Use the `annotation_notes` field on every edge to flag:
   - Any CURIE you are uncertain about (prefix with "VERIFY_CURIE:")
   - Any feature where you were unsure between two values (prefix with "UNCERTAIN:")
   - Any edge where you suspect the text might support an alternative interpretation
     (prefix with "ALT_INTERPRETATION:")

## OUTPUT FORMAT

Produce a single YAML document with the following top-level structure:

```yaml
id: "causal_mosaic:{document_slug}"
title: "{paper title}"
description: "{1-2 sentence summary of what the paper studies}"

nodes:
  - id: "node:{snake_case_label}"
    label: "{Human-readable composed name}"
    description: "{Free-text description from paper}"
    node_type: "{process | environmental_variable | taxa_variable | ecological_state}"
    entity_type: "{environmental_variable | environmental_process | management_intervention}"
    entity_id: "{CURIE — DRAFT, must be verified}"
    entity_label: "{Human label for entity}"
    measurable_attribute: "{short attribute name}"
    attribute_definition: "{How this attribute is measured, from paper}"
    direction: "{increased | decreased | present | absent | introduced | removed | unchanged | unspecified}"
    qualifier_ecosystem_context: "{ecosystem type if stated}"
    # Add more nodes...

edges:
  - id: "edge:{source_slug}_to_{target_slug}"
    source_id: "node:{source_slug}"
    target_id: "node:{target_slug}"
    predicate: "{see predicate vocabulary below}"

    # --- LAYER 1: Claim Strength ---
    claim_strength: "{no_relationship | associational | conditional_causal | direct_causal}"
    claim_strength_basis: "{brief justification}"

    # --- LAYER 2: Philosophical Account ---
    philosophical_account: "{counterfactual | probabilistic | interventionist | variation | process | mechanistic | information_transmission | regularity | inus_component | capacity | agency}"
    philosophical_account_explanation: "{1-3 sentences explaining why you chose this account}"

    # --- LAYER 3: Causal Features (15 features) ---
    # DEFAULT: not_addressed for all. Only change when text supports it.
    direction_annotation:
      status: "{asserted | uncertain | bidirectional | not_addressed}"
      evidence_for_direction: "{experimental | temporal_precedence | theoretical | natural_experiment | structural_model}"
    mechanism_annotation:
      status: "{well_characterized | partially_characterized | not_addressed}"
      mechanism_description: "{from text, not from your training data}"
    mediation_annotation:
      status: "{explicitly_asserted | implicitly_assumed | not_addressed}"
      mediator_node_ids: []
      pathway_description: ""
    moderation_annotation:
      status: "{explicitly_asserted | implicitly_assumed | addressed | not_addressed}"
      moderator_node_ids: []
      interaction_type: "{synergistic | antagonistic | qualitative | quantitative | not_specified}"
    strength_annotation:
      status: "{fully_quantified | partially_quantified | qualitatively_described | not_addressed}"
      quantitative_value: "{effect size as stated in text}"
      quantitative_numeric: null  # numeric value if available
      qualitative_descriptor: "{strong | moderate | weak | negligible | not_specified}"
      dose_response: false
    context_annotation:
      status: "{scope_specified | not_addressed}"
      scope_conditions: []
      geographic_scope: ""
      temporal_scope: ""
      ecosystem_scope: ""
    necessity: "not_addressed"
    sufficiency: "not_addressed"
    temporal_ordering: "not_addressed"
    specificity: "not_addressed"
    stability: "not_addressed"
    token_or_type: "not_addressed"
    determinism: "not_addressed"
    proximate_distal: "not_addressed"
    contributing_sole: "not_addressed"
    reversibility: "not_addressed"
    proportionality: "not_addressed"

    # --- LAYER 4: Evidential Basis ---
    evidence_basis:
      evidence_types: []
      evidence_objects: []    # correlation | mechanism | both
      russo_williamson_satisfied: false
      bradford_hill_viewpoints: []
      bradford_hill_count: 0
      certainty_grade: "not_assessed"
      certainty_rationale: ""
      evidence_count: 0

    # --- Temporal Extent ---
    temporal_extent:
      starts_at: ""
      duration_value: null
      duration_unit: ""
      description: ""

    # --- Provenance ---
    source_spans:
      - id: "span:{n}"
        text: "{VERBATIM quote from paper — do NOT paraphrase}"
        source_document_id: "{doi}"
    source_document:
      id: "{doi}"
      title: "{paper title}"
      authors: []
      publication_year: null
      doi: ""
      publication_type: ""

    annotator: "llm:claude-sonnet-4-20250514"  # or appropriate model ID
    annotation_confidence: 0.0  # SET THIS: your confidence 0.0–1.0
    annotation_notes: |
      {Flag uncertainties here. Use prefixes:
       VERIFY_CURIE: [any CURIE you're unsure about]
       UNCERTAIN: [any feature where you debated between values]
       ALT_INTERPRETATION: [alternative readings of the text]}

    # --- Rendering ---
    rosetta_statement: "{Template: [Subject] [certainty-modified verb] [Object]}"
    fcm_weight: 0.0  # -1.0 to +1.0
    fcm_weight_source: ""

metadata:
  schema_version: "0.4.0"
```

## PREDICATE VOCABULARY (choose one per edge)

| Predicate             | Sign | Use when...                                            |
|-----------------------|------|--------------------------------------------------------|
| causes                | +    | Direct, unhedged positive causation                    |
| contributes_to        | +    | One of several contributing factors                    |
| enables               | +    | Facilitates but not sufficient alone                   |
| positively_regulates  | +    | Upregulates / increases                                |
| associated_with       | ?    | Statistical association, no causal commitment          |
| correlated_with       | ?    | Correlation without direction/causation                |
| prevents              | −    | Inhibits / blocks / reduces                            |
| disrupts              | −    | Degrades / suppresses                                  |
| negatively_regulates  | −    | Downregulates / decreases                              |
| regulates             | ±    | Modulates (direction unclear)                          |
| mediates              | path | On the causal pathway between C and E                  |
| moderates             | mod  | Modifies strength/direction of C→E                     |
| precedes              | time | Temporal precedence only                               |

## PHILOSOPHICAL ACCOUNTS — LINGUISTIC CUE REFERENCE

| Account                 | Family            | Look for these cues in the text                        |
|-------------------------|-------------------|--------------------------------------------------------|
| counterfactual          | difference_making | "without X"; "had X not occurred"; "in the absence of" |
| probabilistic           | difference_making | "risk factor"; "odds ratio"; "P(E|C)"; "associated with [+stats]" |
| interventionist         | difference_making | "removal led to"; "treatment resulted in"; "experiment showed" |
| variation               | difference_making | "R²"; "regression"; "variance explained"; "SEM"       |
| process                 | production        | "energy transfer"; "nutrient flow"; "water transport"  |
| mechanistic             | production        | "mechanism by which"; "pathway"; "step-by-step"        |
| information_transmission| production        | "signal"; "biomarker"; "gene expression cascade"       |
| regularity              | complementary     | "consistently observed"; "invariably"; "universal pattern" |
| inus_component          | complementary     | "contributing factor"; "one of several causes"; "multifactorial" |
| capacity                | complementary     | "capacity to"; "tendency to"; "competitive ability"    |
| agency                  | complementary     | "managers can"; "restoration prescription"; "recommended" |

## EVIDENCE TYPES

randomized_experiment | natural_experiment | quasi_experiment |
observational_longitudinal | observational_cross_sectional | mechanistic_study |
structural_equation_model | meta_analysis | systematic_review |
modeling_simulation | expert_judgment | case_study | theoretical |
indigenous_knowledge | practitioner_experience

## BRADFORD HILL VIEWPOINTS

strength | consistency | specificity | temporality | biological_gradient |
plausibility | coherence | experiment | analogy

## CERTAINTY GRADES

| Grade     | Verb modifier  | Assign when...                                         |
|-----------|----------------|--------------------------------------------------------|
| high      | (none)         | Experimental + mechanistic + replicated                |
| moderate  | "probably"     | Observational + mechanism, or experiment but limited   |
| low       | "may"          | Single study, or observational without mechanism       |
| very_low  | "might"        | Weak evidence, no mechanism, conflicting results       |

## INSTRUCTIONS

1. Read the source text provided below carefully.
2. Identify ALL causal claims, including:
   - Direct causal statements
   - Associational claims with statistical evidence
   - Mechanistic pathway descriptions
   - Competing or offsetting effects
   - Null results (use predicate with negated: true)
3. For each claim, create the necessary nodes (if not already created) and an edge.
4. Fill in all four annotation layers for each edge.
5. Be thorough — extract every causal relationship you can find.
6. Be conservative — default to `not_addressed` and only upgrade when the text supports it.
7. Flag all uncertainties in `annotation_notes`.
8. Output ONLY the YAML. No preamble. No commentary. No markdown fences around the YAML.

## SOURCE TEXT TO ANNOTATE

{PASTE THE SOURCE TEXT HERE}
````

---

## A.4 External Tooling Requirements for Ontology Grounding

The most critical weakness of LLM-assisted extraction is **ontology CURIE accuracy**. LLMs do not have live access to ontology databases and will frequently produce CURIEs that look plausible but are incorrect or non-existent. This problem cannot be solved by prompt engineering alone — it requires external tooling.

### A.4.1 The Problem

When the LLM encounters a species name like *Andropogon gerardii*, it might produce `NCBITaxon:95525`. This might be correct, or it might be a hallucinated number. Similarly, for an environment like "temperate grassland," it might produce `ENVO:01000180` — again, potentially correct or invented. The human reviewer currently has to manually look up every single CURIE in a browser, which is slow and error-prone.

### A.4.2 Recommended Solution: An Ontology Grounding Service

The recommended approach is to build a lightweight validation and lookup service that:

1. **Accepts a list of candidate CURIEs** from the LLM output
2. **Validates each CURIE** against the actual ontology database (OLS API, NCBI Taxonomy API, etc.)
3. **Returns validation results** indicating whether each CURIE exists and what its canonical label is
4. **Suggests corrections** for invalid CURIEs by fuzzy-matching the label text against the ontology

This tool does not exist as a standard component of the Causal Mosaic pipeline yet. **Building it is recommended as a priority infrastructure task.**

### A.4.3 Claude Code Prompts for Building Grounding Tools

The following prompts can be used with Claude Code (Anthropic's command-line coding agent) to build the necessary validation tools. Each prompt describes a self-contained tool.

---

**Tool 1: Ontology CURIE Validator**

```
Build a Python CLI tool called `validate_curies.py` that:

1. Accepts a YAML file (Causal Mosaic 0.4 format) as input.
2. Extracts all ontology CURIEs from the file — specifically from these fields
   in both nodes and edges:
   - entity_id / entity_term
   - variable_attribute (when it's a CURIE, not free text)
   - mediator_node_ids
   - moderator_node_ids
   - ecosystem_context
   - process_context
   - conditioned_by
3. Groups CURIEs by prefix (NCBITaxon, ENVO, CHEBI, GO, PATO, etc.).
4. Validates each CURIE against the appropriate API:
   - NCBITaxon: use NCBI E-utilities (esummary on taxonomy database)
   - ENVO, GO, PATO, CHEBI: use the OLS4 API (https://www.ebi.ac.uk/ols4/api/)
5. Outputs a validation report as JSON with this structure for each CURIE:
   {
     "curie": "NCBITaxon:95525",
     "valid": true|false,
     "canonical_label": "Andropogon gerardii" or null,
     "label_in_yaml": "Big Bluestem",
     "label_match": true|false,
     "suggested_curie": null or "NCBITaxon:XXXXX" (if invalid, try fuzzy match)
   }
6. Prints a summary: total CURIEs checked, valid count, invalid count, with
   details for any invalid CURIEs.

Dependencies: requests, pyyaml, click (for CLI). Rate-limit API calls
(max 3 requests/second for NCBI, 10/second for OLS).
Include a --dry-run flag that lists extracted CURIEs without making API calls.
```

---

**Tool 2: Ontology Label-to-CURIE Lookup**

```
Build a Python CLI tool called `lookup_curie.py` that:

1. Accepts a natural-language label (e.g., "Andropogon gerardii", "grassland",
   "abundance") and an ontology prefix (NCBITaxon, ENVO, PATO, GO, CHEBI).
2. Searches the appropriate API for matching terms:
   - NCBITaxon: use NCBI E-utilities esearch
   - ENVO/GO/PATO/CHEBI: use OLS4 search API
3. Returns the top 5 matches with:
   - CURIE
   - Canonical label
   - Definition (if available)
   - Match score / relevance
4. Supports batch mode: accepts a TSV file with columns (label, prefix) and
   outputs results for all rows.

This tool is used when the LLM leaves a CURIE blank or when the validator
flags a CURIE as invalid and the human needs to find the correct one.

Dependencies: requests, click. Include caching to avoid redundant API calls
during batch processing.
```

---

**Tool 3: Source Span Verifier**

```
Build a Python CLI tool called `verify_spans.py` that:

1. Accepts two inputs:
   - A Causal Mosaic YAML file (with source_spans containing `text` fields)
   - The original source document (as plain text, PDF extracted to text, or
     a text file)
2. For every source_span in the YAML (across both nodes and edges), checks
   whether the `text` field appears VERBATIM in the source document.
3. Uses fuzzy matching (e.g., Levenshtein distance, or difflib.SequenceMatcher)
   to catch near-misses where the LLM subtly altered a few characters.
4. Outputs a report:
   - For exact matches: span_id, status="exact_match", char_offsets in source
   - For near matches (>90% similarity): span_id, status="near_match",
     similarity_score, diff showing what changed
   - For no match (<90%): span_id, status="not_found"
5. Optionally auto-corrects near-matches by replacing the LLM's text with the
   exact text from the source document (with a --fix flag).
6. If char offsets (start_char, end_char) are provided in the YAML, validates
   that the text at those offsets matches the `text` field.

Dependencies: pyyaml, click, difflib (stdlib). Optional: pdfplumber or
pymupdf for PDF text extraction.
```

---

**Tool 4: Causal Mosaic YAML Schema Validator**

```
Build a Python CLI tool called `validate_schema.py` that:

1. Accepts a Causal Mosaic YAML file.
2. Validates it against the Causal Mosaic 0.4 schema by checking:
   a. Required fields are present (id, name for nodes; id, subject, object,
      predicate, claim_strength, philosophical_accounts, source_spans for edges)
   b. Enum values are valid (e.g., claim_strength must be one of:
      no_relationship, associational, conditional_causal, direct_causal)
   c. Node IDs referenced in edges (subject, object, mediator_node_ids,
      moderator_node_ids) actually exist in the nodes list
   d. FCM weights are in range [-1.0, 1.0]
   e. Annotation confidence is in range [0.0, 1.0]
   f. Bradford Hill count matches the length of bradford_hill_viewpoints list
   g. Predicate sign is consistent with FCM weight sign (positive predicate
      should not have negative FCM weight)
   h. No duplicate node or edge IDs
3. Outputs a validation report with errors (must fix) and warnings (should
   review):
   - ERROR: missing required field
   - ERROR: invalid enum value
   - ERROR: dangling node reference
   - WARNING: FCM weight sign inconsistent with predicate
   - WARNING: bradford_hill_count does not match viewpoints list length
   - WARNING: annotation_confidence is 0.0 (likely not set)
4. Exits with code 0 if no errors, code 1 if errors found.

Dependencies: pyyaml, click, jsonschema (optional for more rigorous
validation). Include the complete enum definitions inline in the script
so it is self-contained.
```

---

### A.4.4 Integration Workflow with Tools

Once the tools described above are built, the full pipeline becomes:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  LLM Extract │────▶│ validate_    │────▶│ validate_    │
│  (YAML draft)│     │ schema.py    │     │ curies.py    │
└──────────────┘     │ Fix errors   │     │ Fix CURIEs   │
                     └──────────────┘     └──────────────┘
                                                │
                     ┌──────────────┐           │
                     │  Human       │◀──────────┘
                     │  Review      │
                     │  (Stage 3)   │◀──── verify_spans.py
                     └──────────────┘
                           │
                     ┌──────────────┐
                     │  Finalized   │
                     │  YAML        │
                     └──────────────┘
```

1. **LLM extraction** produces draft YAML.
2. **`validate_schema.py`** catches structural errors (missing fields, bad enums, dangling references).
3. **`validate_curies.py`** checks every ontology ID against live databases and flags invalid ones.
4. **`verify_spans.py`** confirms source spans are verbatim from the paper.
5. **Human review** addresses all remaining issues — feature coding, philosophical accounts, certainty grades, and any flags from the tools or the LLM's own `annotation_notes`.
6. **Finalized YAML** is the validated output.

### A.4.5 A Note on Prompt Iteration

The extraction prompt provided in Section A.3 is a starting point. As you use it across papers, you will discover domain-specific issues. Track these in a "prompt changelog" and update the prompt accordingly. Common iterations include:

- Adding domain-specific predicate examples (e.g., for marine ecology vs. grassland ecology)
- Refining the mechanism description instructions when the LLM consistently over-specifies or under-specifies
- Adding examples of null results to improve extraction of negated edges
- Adjusting the philosophical account cues when the LLM consistently confuses two accounts

Treat the prompt as a living artifact, just like this annotation guide.

---

## A.5 Inter-Annotator Agreement with LLM Drafts

When using LLM-assisted extraction, measure inter-annotator agreement (IAA) between the LLM draft and the human-corrected final version. Track agreement rates per field type:

| Field Category | Expected Agreement | Notes |
|---|---|---|
| Node identification (which entities are nodes) | 70–85% | LLMs tend to over-split or miss implicit nodes |
| Edge identification (which claims are edges) | 75–90% | High recall but some false positives |
| Predicate selection | 80–90% | Generally reliable for clear causal language |
| Claim strength | 85–95% | Surface-language task; LLMs do this well |
| Philosophical account | 60–75% | Most variable; requires human judgment |
| Causal features (15 features) | 70–85% | Driven by over-assertion tendency |
| Evidence types | 80–90% | Usually straightforward from Methods section |
| Certainty grade | 55–70% | Highly subjective; expect significant correction |
| Ontology CURIEs | 50–70% | Hallucination rate varies by ontology |
| Source spans (verbatim accuracy) | 60–80% | Paraphrasing is the main failure mode |

These figures are rough expectations. Track your own project's rates to calibrate how much human effort the LLM is actually saving versus creating.

---

## A.6 When NOT to Use LLM Extraction

LLM-assisted extraction is not always the right choice. Prefer fully manual annotation when:

- **The paper has complex, multi-step causal chains** where getting the graph topology right is critical and errors cascade.
- **The paper reports highly contested or politically sensitive findings** where subtle framing differences in claim strength matter.
- **The paper uses domain-specific jargon or neologisms** that the LLM is unlikely to recognize correctly.
- **The corpus is small** (fewer than ~10 papers). The time spent setting up and validating the LLM pipeline may exceed the time saved.
- **Training new annotators.** Have new annotators do their first 5–10 papers fully manually to build deep familiarity with the schema before using LLM assistance.

---

*End of Appendix A*
