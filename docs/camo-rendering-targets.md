# CAMO Rendering Target Guide

**Causal Mosaic Schema (CAMO)** — companion document to `causalmosaic.yaml`
Schema version: 0.7.7 · Licence: CC0 · `https://w3id.org/causal-mosaic`

A CAMO graph is not itself a deliverable. It is an annotation substrate that
projects into several deliverables, each consuming a different subset of the
annotation layers. This guide specifies those projections: what each target
reads, how to derive it, and where the derivation is lossy or ambiguous.

This document is **not part of the schema**. It is versioned alongside the
renderers rather than with `causalmosaic.yaml`, because renderer contracts
change faster than a schema should.

---

## Contents

- [Before you render](#before-you-render)
- [1. Rosetta Statement](#1-rosetta-statement)
- [2. Fuzzy Cognitive Map](#2-fuzzy-cognitive-map)
- [3. Causal Diagram](#3-causal-diagram)
- [4. Evidence Gap Map](#4-evidence-gap-map)
- [5. Bayesian Belief Network](#5-bayesian-belief-network)
- [6. Practitioner Summary](#6-practitioner-summary)
- [7. RAG Retrieval](#7-rag-retrieval)
- [Appendix A: consumption matrix](#appendix-a-consumption-matrix)
- [Appendix B: validating a renderer](#appendix-b-validating-a-renderer)

---

## Before you render

### Two kinds of edge

Everything downstream depends on getting this distinction right.

| | `CausalEdge` | `EvidenceBaseAssessmentEdge` |
|---|---|---|
| Represents | one claim in one paper | one relationship across many papers |
| Carries | claim strength, accounts, 16 features, evidential basis | Russo-Williamson assessment, Bradford Hill, study counts, aggregate certainty |
| Provenance | `source_spans`, `source_document` | `included_edge_ids`, `assessment_method` |

**Rule: render the aggregate edge wherever one exists.** An article-level edge
is the annotation unit; the aggregate edge is the claim. A renderer that
projects `CausalEdge` records directly will show the same relationship several
times with different weights and no indication that they are the same claim.

Fall back to `CausalEdge` only when no assessment covers the relationship, and
say so in the output.

### The `not_addressed` convention

Most feature slots default to `not_addressed` via `ifabsent`. This means *the
source did not speak to this*, not *the answer is no*. Renderers must not
collapse `not_addressed` into a negative — an edge with
`reversibility: not_addressed` is not an edge with `reversibility: irreversible`.

Where a feature is unaddressed, omit the corresponding clause rather than
rendering a default.

### `negated`

`CausalEdge.negated` (default `false`) inverts the claim: the source asserted
that the relationship does *not* hold. This is not the same as
`claim_strength: no_relationship`, which is a positive finding of absence.
Every renderer must handle `negated` explicitly; ignoring it inverts meaning.

### `loom_role: hidden`

Slots annotated `loom_role: hidden` (`embedding_text`, `embedding_vector`,
`fcm_weight`, character offsets) are machine-facing. They belong in the FCM and
RAG targets and should never surface in a human-readable rendering.

---

## 1. Rosetta Statement

Template-generated natural language. The base rendering that most other
human-readable targets build on.

### Consumes

| Source | Used for |
|---|---|
| `CausalNode.state_or_change_qualifier` → `rosetta_prefix` | node label prefix |
| `CausalNode.measured_attribute`, `entity_term` | node label body |
| `CausalPredicateEnum` → `rosetta_template` | sentence frame |
| `CausalEdge.claim_strength` | hedging (article-level) |
| `CertaintyGradeEnum` → `rosetta_verb_modifier` | hedging (aggregate) |
| `CausalEdge.negated` | negation |
| `mediation`, `context_dependence`, `strength` | optional trailing clauses |

### Procedure

**Step 1 — render each node label.** Concatenate the `rosetta_prefix`
annotation on the node's `state_or_change_qualifier`, the `measured_attribute`,
and the label for `entity_term`:

```
qualifier=increased  →  rosetta_prefix "increased"
measured_attribute   →  "cover"
entity_term          →  wikidata:Q...  →  "Sphagnum"
                     →  "increased Sphagnum cover"
```

**Step 2 — apply the predicate template.** Each `CausalPredicateEnum` value
carries `rosetta_template` with `{subject}` and `{object}` placeholders.
Substitute the rendered labels.

**Step 3 — hedge.** Use exactly one hedging source:

- **Aggregate edges** use `rosetta_verb_modifier` from
  `aggregate_certainty_grade`: `high` → no modifier, `moderate` → *probably*,
  `low` → *may*, `very_low` → *might*.
- **Article-level edges** use `claim_strength`, which reflects the source's own
  language rather than an assessment of it.

Do not apply both. A statement hedged twice ("may probably contribute to")
misrepresents the annotation.

**Step 4 — negate if `negated: true`.**

**Step 5 — append feature clauses**, skipping any whose `status` is
`not_addressed`:

- `mediation.pathway_description` → "…via {pathway}"
- `context_dependence` → "…in {ecosystem_context display_label}" and/or
  `geographic_scope`
- `strength.qualitative_descriptor` or `quantitative_value` → magnitude

### Worked example

```
subject   entity_term=ELMO:<ditch blocking>, qualifier=occurred
predicate contributes_to
object    entity_term=wikidata:<Sphagnum>, measured_attribute=cover,
          qualifier=increased
aggregate_certainty_grade  moderate
mediation.pathway_description  "raised water table"
ecosystem_context  palustrine_wetlands (T7.x)
```

→ *Ditch blocking probably contributes to increased Sphagnum cover, via a
raised water table, in palustrine wetlands.*

### Gotchas

- **Empty prefixes.** `unchanged` and `occurred` both carry
  `rosetta_prefix: ""`. Emit "no change in …" for `unchanged` — a measured null
  is a positive finding and should not render as silence. `occurred` renders
  correctly with no prefix ("ditch blocking", not "occurrence of ditch
  blocking").
- **An absent qualifier is not a state.** If `state_or_change_qualifier` is
  null, the source did not specify one. Render the node without a prefix and
  flag it; do not treat it as equivalent to `unchanged`.
- **`entity_term` may be free text.** It is `any_of: [uriorcurie, string]`.
  Resolve CURIEs to labels; pass free text through verbatim and flag it, since
  it will not resolve in any other target either.
- **Predicates without a natural sentence.** `mediates`, `moderates`, and
  `precedes` have templates but describe edge structure rather than causal
  influence. They read poorly in isolation and are usually better rendered as
  clauses on the edge they modify.

---

## 2. Fuzzy Cognitive Map

Weighted directed graph for causal modelling. Cycles are permitted and
expected.

### Consumes

| Source | Used for |
|---|---|
| `CausalEdge.fcm_weight`, `fcm_weight_source` | explicit weight |
| `CausalPredicateEnum` → `fcm_default_weight`, `sign` | fallback weight |
| `StateOrChangeQualifierEnum` → `fcm_sign` | node polarity (conditional — see below) |
| `CausalEdge.claim_strength` | inclusion filter |
| `direction.status` | edge orientation |
| `aggregate_certainty_grade` | weight down-weighting |

### Procedure

**Step 1 — select edges.** An FCM models causal influence, so filter on
`claim_strength`. Including `associational` and `no_relationship` edges puts
non-causal claims into a causal model. A reasonable default is
`claim_strength IN (uncertain_causal, direct_causal)`.

**Step 2 — drop structural predicates.** `mediates`, `moderates`, and
`precedes` carry `fcm_default_weight: 0.0` and signs `pathway`, `modifier`,
`temporal`. These are **not zero-weight edges** — they are not edges of this
graph at all. Emitting them as zero-weight arcs pollutes the adjacency matrix.
Handle mediators by path expansion and moderators as edge-weight modifiers, or
omit them.

**Step 3 — resolve the weight.**

1. `fcm_weight` if present.
2. Otherwise `fcm_default_weight` from the predicate.
3. `regulates` carries `sign: variable` and weight `0.0`; it cannot be resolved
   from the predicate alone. Use `strength.quantitative_numeric` or
   `qualitative_descriptor`, or exclude the edge.

**Step 4 — decide the sign convention, once, and document it.** This is the
single most common way to build a wrong FCM from CAMO.

CAMO nodes are *already signed states* — "decreased water table depth" is a
node, not a variable with a negative value. So:

- **If FCM concepts are CAMO nodes as-is** (signed states), use the **predicate
  sign only**. The node's `fcm_sign` is already baked into the concept's
  identity.
- **If you have first collapsed signed nodes into variables** (as the BBN
  target does — see §5), apply `predicate sign × object fcm_sign`.

Doing both double-counts polarity and silently flips the sign of every edge
whose object is a `decreased` or `absent` state.

**Step 5 — orient.** `direction.status: asserted` → single arc.
`bidirectional` → two arcs; FCMs tolerate this. `uncertain` or `not_addressed`
→ include with a flag, or exclude, but be consistent.

**Step 6 — down-weight by certainty.** Multiply by a factor derived from
`aggregate_certainty_grade`. Record the multiplier in
`aggregate_fcm_weight_source` so the transformation is inspectable rather than
buried in renderer code.

### Gotchas

- **Weights are strings.** `fcm_default_weight` is `"0.7"`, not `0.7` — LinkML
  annotations are untyped. Parse and fail loudly on malformed values.
- **Build from aggregate edges.** Five article-level edges for one relationship
  produce five parallel arcs. Collapse to the `EvidenceBaseAssessmentEdge`
  first.

---

## 3. Causal Diagram

Visual rendering of graph structure. Unlike the FCM, this is for reading rather
than simulation.

### Consumes

`CausalNode` (all), `CausalEdge.subject`/`object`/`predicate`,
`direction` (`status`, `evidence_for_direction`), `mediation.mediator_node_ids`,
`moderation.moderator_node_ids` and `interaction_type`, predicate `sign`.

### Procedure

1. **Nodes** — label via the Rosetta node rendering (§1, step 1). Shape or
   colour by `entity_type`: `management_intervention`, `environmental_variable`,
   `environmental_process`, `taxon`.
2. **Edges** — colour by predicate `sign` (positive / negative / unspecified),
   style by `direction.status`: `asserted` solid, `uncertain` dashed,
   `not_addressed` dotted, `bidirectional` double-headed.
3. **Mediators** — `mediation.mediator_node_ids` references existing
   `CausalNode` ids. Render the expanded path A → M → B alongside or instead of
   the direct arc; do not invent a node.
4. **Moderators** — `moderation.moderator_node_ids` attach *to the edge*, not
   to a node. Render as an annotation on the arc, tagged with
   `interaction_type` (`synergistic`, `antagonistic`, …). Drawing a moderator
   as an ordinary arrow into the object node asserts a causal claim the source
   did not make.

### Gotchas

- **This is not necessarily a DAG.** `direction.status: bidirectional` and
  genuine feedback loops both occur. If your consumer requires acyclicity, say
  which edges you dropped — do not silently orient them.
- **Node identity.** `CausalNode.id` is auto-generated. Two annotators
  describing the same state may produce two nodes. Deduplicate on
  `(entity_term, measured_attribute, state_or_change_qualifier, applied_to)`
  before laying out.

---

## 4. Evidence Gap Map

Intervention × ecosystem matrix with evidence counts, for identifying where
evidence is missing.

### Axes

| Axis | Derivation |
|---|---|
| **Rows** | Subject nodes where `entity_type == management_intervention`, grouped by `entity_term`, rolled up at query time through the ELMO `is-a` hierarchy |
| **Columns** | `CausalEdge.ecosystem_context` (`EcosystemFunctionalGroupEnum`) |
| **Cells** | Count of `EvidenceBaseAssessmentEdge` records, shaded by `aggregate_certainty_grade` |
| **Facet** | `CausalNode.applied_to` — e.g. restrict counts to edges where a taxon of interest appears |

Note there is no `egm_role` annotation and no node-level category slot.
Intervention and outcome are *positions in an edge*, not kinds of thing: the
same node is an outcome in one edge and a mediator in another. Role is derived
from edge position, never from node type.

### Column zoom comes free

Every `EcosystemFunctionalGroupEnum` value carries an `iucn_get_code`
annotation. Truncating it gives the IUCN GET hierarchy without a crosswalk:

```
T1.1  →  T1  (biome)  →  T  (realm)
```

Render at realm level for an overview, drill to Level 3 on demand. Use
`display_label` (which already includes the code) for column headers.

### Row rollup does not

`EntityTypeEnum` has four values; "seeding" is not one of them, it is an
`entity_term`. One row per distinct term is unreadable, so rows must roll up
through ELMO's subsumption hierarchy at query time. This requires:

- ELMO to carry `is-a` axioms for management interventions at usable depth
- a traversal step in the query layer, by reasoner or materialized closure

Verify both before building the renderer. Rollup is deliberately *not*
materialized in the schema — freezing one grouping into the data would force
re-annotation whenever the grouping changed.

### Cell contents

Shade by `aggregate_certainty_grade`. Consider a second visual channel for
`evidence_balance` — a cell with five supporting studies and one contradicting
is not the same as six supporting, and `number_of_contradicting_edges` is
already there.

### Gotchas

- **An empty cell has three meanings** and CAMO can currently distinguish only
  one of them: nobody studied it, someone studied it and found nothing, or it
  was deliberately out of scope. Absence of an edge conflates all three. Label
  empty cells "no evidence retrieved," not "no effect."
- **`applied_to.entity_term` may be free text.** *Sphagnum*, *sphagnum moss*,
  and *peat moss* are three different filter targets, so a facet query
  undercounts silently. Normalize before faceting, and report how many values
  failed to resolve.
- **Taxon facets want their own rollup.** Filtering by genus and catching member
  species requires a traversable taxon hierarchy — Wikidata `P171` or the GBIF
  backbone.

---

## 5. Bayesian Belief Network

**This target is a model-building assistant, not an export.** The distinction
is load-bearing and should be stated wherever the output appears.

### Why not an export

CAMO nodes are states: "increased *Sphagnum* cover" and "decreased *Sphagnum*
cover" are two different nodes. A BBN needs one **variable** (*Sphagnum*
cover) with a mutually exclusive state space and a CPT over parent states.
Those shapes do not convert automatically, and a renderer that pretends
otherwise produces a network the evidence does not support.

With a modeller in the loop, the graph does two things nothing else currently
does.

### Function 1 — recommend the structure

Propose variables, candidate edges, and parent sets, ranked by:

- `aggregate_certainty_grade`
- `number_of_studies`
- `russo_williamson_satisfied`

The modeller accepts or rejects each. Surface `conflict_summary` and
`number_of_contradicting_edges` alongside each proposal so rejection is
informed.

**Parent-set semantics are partly encoded already.** `contributing_sole:
contributing_cause` combined with `moderation.interaction_type: synergistic`
tells the modeller that a noisy-OR CPT is *inappropriate* and an interaction
term is required. Surface this; it is one of the most directly useful things
the feature layer produces.

### Function 2 — supply the state space, with references

Group nodes by:

```
(entity_term, measured_attribute, applied_to)
```

The set of `state_or_change_qualifier` values that the literature has actually
reported for that group **is** the empirically attested state space, and each
state carries its citations through `source_spans` and `source_document`.

**Restrict to one qualifier family.** The enum mixes incompatible families:

| Family | Values | Usable as a state space? |
|---|---|---|
| `directional_change` | `increased`, `decreased`, `unchanged` | Yes — but yields a **delta** variable ("change in cover"), not a level |
| `presence` | `present`, `absent` | Yes — a **level** variable |
| `membership_change` | `introduced`, `removed` | Transitions in presence; not a clean space alongside it |
| `process_phase` | `occurred`, `initiated`, `terminated`, `ongoing`, `interrupted`, `aborted` | No |

A network mixing delta and level variables is legitimate but needs the modeller
to know which is which. Surface the family alongside each proposed variable.

A candidate variable drawing from more than one family is a grouping error, not
a rich state space.

### Cycles

Surface reciprocal evidence; do not resolve it. `direction.status:
bidirectional` and genuine feedback loops are real findings. The modeller
decides what the DAG requires — that is the point of the assistant framing.

### Caveats to state in the output

- **Publication bias.** `unchanged` covers null results, but nulls are
  under-published. A corpus-derived state space systematically
  under-represents no-change. Show the cell as *thin*, not absent.
- **A thin `unchanged` cell is not a missing one.** `unchanged` means the
  source measured no change; a null `state_or_change_qualifier` means it did not
  say. Distinguish them in the state-space display — the first is evidence.
- **Priors and CPTs come from the modeller**, not from the graph. Keep them in
  separate storage referencing `EvidenceBaseAssessmentEdge` ids, so the
  literature layer stays uncontaminated by elicited judgement.

---

## 6. Practitioner Summary

Plain-language output for land managers. The target where the annotation layers
pay off most visibly, because the fields a practitioner needs are exactly the
ones a naive triple discards.

### Consumes

`CausalNode` labels, `predicate`, `aggregate_certainty_grade`,
`reversibility`, `context_dependence`, `contributing_sole`, `temporal_extent`
(`duration_months`, `lag_months`), and edges carrying the `agency` account.

### Procedure

Start from the Rosetta statement (§1), then add what a manager acting on the
claim needs:

1. **Hedge honestly** — `rosetta_verb_modifier` from the aggregate certainty.
2. **Say whether it is the only cause.** `contributing_sole:
   contributing_cause` means the intervention alone will not produce the
   outcome. Practitioners routinely read a bare causal claim as sufficiency.
3. **Say how long.** `temporal_extent.duration_months` and `lag_months` carry
   the difference between an effect next season and an effect in a decade.
4. **Say whether it reverses.** `reversibility: hysteresis` means the system
   does not return along the path it left by — the single most consequential
   field for restoration decisions, and one with no equivalent in any triple
   store.
5. **Say where it holds.** `ecosystem_context.display_label` plus
   `context_dependence.geographic_scope`.

### Worked example

> Blocking drainage ditches probably increases Sphagnum cover in palustrine
> wetlands, but it is one contributing factor among several, and recovery took
> around eleven years in the studies assessed. The effect shows hysteresis:
> re-draining does not return the system along the same path. Assessed as
> moderate certainty from five studies, one of which disagreed.

Every clause traces to a field: `rosetta_verb_modifier`, `contributing_sole`,
`temporal_extent.duration_months`, `reversibility`, `aggregate_certainty_grade`,
`number_of_studies`, `number_of_contradicting_edges`.

### Gotchas

- **Do not omit the contradicting study.** `number_of_contradicting_edges` and
  `conflict_summary` exist so that disagreement survives summarization.
- **Prefer the `agency` account edges** where several exist for one
  relationship: agency-account claims are framed in terms of manipulability,
  which is what a manager can act on.

---

## 7. RAG Retrieval

Source-text retrieval for question answering over the corpus.

### Consumes

`CausalNode.embedding_text` / `embedding_vector`,
`CausalEdge.original_sentence`, `source_spans` (`text`, `start_char`,
`end_char`, `sentence_id`, `paragraph_id`), `SourceDocument` (`doi`, `title`,
`authors`, `year`, `journal`).

### Chunking

Index one chunk per `CausalEdge`, containing:

- `original_sentence` — the verbatim claim
- the rendered Rosetta statement — a normalized paraphrase, which retrieves on
  vocabulary the source did not use
- surrounding `source_spans` for context
- full `SourceDocument` metadata for citation

Indexing both the verbatim and rendered forms is the point: a query phrased as
"does rewetting help peat moss" matches the rendered statement where it would
miss the source's own phrasing.

### Gotchas

- **Character offsets are document-specific.** `start_char` and `end_char` index
  into the source text as ingested. Store the ingestion version, or the offsets
  will drift against a re-fetched PDF.
- **Never surface `embedding_vector`.** It is `loom_role: hidden` and is a
  machine artifact.
- **Attribute to the article-level edge**, not the aggregate. RAG answers need
  a citable source; aggregate edges are assessments and cite via
  `included_edge_ids`.

---

## Appendix A: consumption matrix

| Field | Rosetta | FCM | Diagram | EGM | BBN | Practitioner | RAG |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `entity_term` / `measured_attribute` | ● | ● | ● | ● | ● | ● | ● |
| `state_or_change_qualifier` | ● | ○ | ● | | ● | ● | |
| `applied_to` | | | | ● | ● | | |
| `entity_type` | | | ● | ● | | | |
| `predicate` | ● | ● | ● | | ● | ● | |
| `claim_strength` | ● | ● | | | | | |
| `negated` | ● | ● | ● | ● | ● | ● | |
| `ecosystem_context` | ○ | | | ● | | ● | |
| `direction` | | ● | ● | | ● | | |
| `mediation` | ○ | ○ | ● | | ● | | |
| `moderation` | | ○ | ● | | ● | | |
| `strength` | ○ | ● | | | | | |
| `reversibility` | | | | | | ● | |
| `contributing_sole` | | | | | ● | ● | |
| `context_dependence` | ○ | | | | | ● | |
| `temporal_extent` | | | | | | ● | |
| `philosophical_accounts` | | | | | | ○ | |
| `fcm_weight` | | ● | | | | | |
| `aggregate_certainty_grade` | ● | ● | | ● | ● | ● | |
| `russo_williamson_satisfied` | | | | ○ | ● | | |
| `number_of_studies` / `_contradicting_` | | | | ● | ● | ● | |
| `source_spans` / `SourceDocument` | | | | ● | ● | ○ | ● |
| `embedding_text` / `_vector` | | | | | | | ● |

● required · ○ optional or enriching

---

## Appendix B: validating a renderer

Three checks worth automating.

**1. Every consumed field exists.** Parse the consumption matrix above and
assert each field name resolves to a real slot in `causalmosaic.yaml`. This
guide has previously drifted against the schema — a target once claimed to
consume "nodes with `egm_role` annotations" from an enum that no slot
referenced, and nothing caught it.

**2. Annotation values parse.** `fcm_default_weight` is a string; so is
`fcm_sign`, `rosetta_prefix`, and `rosetta_verb_modifier`. Assert every value
parses to its expected type before shipping a renderer.

**3. Round-trip on a fixture graph.** Keep one small annotated graph in the
repository and assert each renderer produces expected output from it. This
catches sign-convention regressions in the FCM target, which are otherwise
invisible — a flipped sign produces a plausible-looking map that is wrong.

### Known lossy points

Renderers should surface these rather than absorb them:

| Issue | Affects | Effect |
|---|---|---|
| `unchanged` renders with an empty prefix | Rosetta | Measured nulls render as silence unless special-cased |
| `entity_term` accepts free text | EGM facets, BBN grouping | Silent undercounting |
| Empty EGM cell has three meanings | EGM | "No evidence" read as "no effect" |
| Node signs plus predicate signs | FCM | Double-counted polarity if both applied |
| Rollup depends on ELMO `is-a` | EGM rows | Unreadable row count if hierarchy is shallow |
