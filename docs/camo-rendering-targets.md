# CAMO Rendering Target Guide

**Causal Mosaic Schema (CAMO)** — companion document to `causalmosaic.yaml`
Schema version: 0.7.8 · Licence: CC0 · `https://w3id.org/causal-mosaic`
A CAMO graph is not itself a deliverable. It is an annotation substrate that
projects into several deliverables and decision products, each consuming a different subset of the
annotation layers. This guide specifies those projections: what each target
reads, which external inputs it requires, how to derive it, and where the derivation is lossy or ambiguous.
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
- [6. Spatial Prioritization (`prioritizr`)](#6-spatial-prioritization-prioritizr)
- [7. Practitioner Summary](#7-practitioner-summary)
- [8. RAG Retrieval](#8-rag-retrieval)
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

**Rule: use the aggregate edge for synthesis and model targets wherever one exists.**
An article-level edge is the annotation unit; the aggregate edge is the synthesized
relationship. A renderer that projects several `CausalEdge` records directly into an FCM,
EGM, BBN assistant, or spatial prioritization can show the same relationship several times
with no indication that they belong to one evidence base. Fall back to `CausalEdge` when no
assessment covers the relationship and say so in the output.

Source-grounded targets are the deliberate exception: RAG retrieval and article-specific
Rosetta statements should retain the article-level edge because that is where citable text
provenance lives.

### The `not_addressed` convention

Most feature slots default to `not_addressed` via `ifabsent`. This means *the
source did not speak to this*, not **the answer is no**. Renderers must not
collapse `not_addressed` into a negative — an edge with
`reversibility: not_addressed` is not an edge with `reversibility: irreversible`.
Where a feature is unaddressed, omit the corresponding clause rather than
rendering a default.

### `negated`

`CausalEdge.negated` (default `false`) inverts the claim: the source asserted
that the relationship does **not** hold. It is the canonical null-result
encoding and always pairs with `causal_language: no_relationship`: one is set
if and only if the other is. A null result is never encoded as an object node
with the qualifier `unchanged`, which means a reported stable state instead.
Every renderer must handle `negated` explicitly; ignoring it inverts meaning.

### Model-building targets need external inputs

BBNs and spatial prioritizations are not literal graph exports. CAMO can supply structure,
state spaces, evidence-derived responses, and uncertainty, but it does not contain every
parameter or normative choice required to build those models. Renderers must distinguish
CAMO-derived values from modeller, stakeholder, or external spatial inputs.

### `loom_role: hidden`

Slots annotated `loom_role: hidden` (`embedding_text`, `embedding_vector`,
`fcm_weight`, character offsets) are machine-facing. They belong in machine-facing targets such as the FCM, spatial prioritization, and
RAG retrieval, and should never surface in a human-readable rendering.

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
| `CausalEdge.causal_language` | hedging (article-level) |
| `CertaintyGradeEnum` → `rosetta_verb_modifier` | hedging (aggregate) |
| `CausalEdge.negated` | negation |
| `mediation`, `context_dependence`, `strength` | optional trailing clauses |

### Procedure

**Step 1 — render each node label.** Concatenate the `rosetta_prefix`
annotation on the node's `state_or_change_qualifier`, the `measured_attribute`,
and the label for `entity_term`:

```
qualifier=increased  →  rosetta_prefix "increased"
measured_attribute   →  "cover"
entity_term          →  wikidata:Q...  →  "Sphagnum"
                     →  "increased Sphagnum cover"

```
**Step 2 — apply the predicate template.** Each `CausalPredicateEnum` value
carries `rosetta_template` with `{subject}` and `{object}` placeholders.
Substitute the rendered labels.
**Step 3 — hedge.** Use exactly one hedging source:

- **Aggregate edges** use `rosetta_verb_modifier` from
  `aggregate_certainty_grade`: `high` → no modifier, `moderate` → **probably**,
  `low` → **may**, `very_low` → **might**.

- **Article-level edges** use `causal_language`, which reflects the source's own
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
subject   entity_term=ELMO:\<ditch blocking>, qualifier=occurred
predicate contributes_to
object    entity_term=wikidata:Q..., measured_attribute=cover,
          qualifier=increased
aggregate_certainty_grade  moderate
mediation.pathway_description  "raised water table"
ecosystem_context  palustrine_wetlands (T7.x)

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
| `EvidenceBaseAssessmentEdge.aggregate_fcm_weight`, `_source` | preferred aggregate weight |
| `CausalEdge.fcm_weight`, `fcm_weight_source` | article-level fallback |
| `CausalPredicateEnum` → `fcm_default_weight`, `sign` | final fallback weight |
| `StateOrChangeQualifierEnum` → `fcm_sign` | node polarity (conditional — see below) |
| `CausalEdge.causal_language` | article-level inclusion filter |
| `direction.status` | edge orientation |
| `aggregate_certainty_grade` | uncertainty metadata / optional explicit down-weighting rule |

### Procedure

**Step 1 — select edges.** An FCM models causal influence, so filter on
`causal_language`. Including `associational` and `no_relationship` edges puts
non-causal claims into a causal model. A reasonable default is
`causal_language IN (uncertain_causal, direct_causal)`.
**Step 2 — drop structural predicates.** `mediates`, `moderates`, and
`precedes` carry `fcm_default_weight: 0.0` and signs `pathway`, `modifier`,
`temporal`. These are **not zero-weight edges** — they are not edges of this
graph at all. Emitting them as zero-weight arcs pollutes the adjacency matrix.
Handle mediators by path expansion and moderators as edge-weight modifiers, or
omit them.
**Step 3 — resolve the weight.**

For an `EvidenceBaseAssessmentEdge`:

1. use `aggregate_fcm_weight` if present;
2. otherwise derive a weight from an explicitly documented synthesis rule over the member
   edges or from a compatible aggregate effect estimate; and
3. record that rule in `aggregate_fcm_weight_source`.

For an article-level fallback:

1. use `CausalEdge.fcm_weight` if present;
2. otherwise use `fcm_default_weight` from the predicate; and
3. note that `regulates` carries `sign: variable` and weight `0.0`, so it cannot be
   resolved from the predicate alone. Use `strength.quantitative_numeric` or
   `qualitative_descriptor`, or exclude the edge.
**Step 4 — decide the sign convention, once, and document it.** This is the
single most common way to build a wrong FCM from CAMO.
CAMO nodes are **already signed states** — "decreased water table depth" is a
node, not a variable with a negative value. So:

- **If FCM concepts are CAMO nodes as-is** (signed states), use the **predicate
  sign only**. The node's `fcm_sign` is already baked into the concept's
  identity.

- **If you have first collapsed signed nodes into variables** (as the BBN
  target does — see §5), apply `subject fcm_sign × predicate sign × object
  fcm_sign`, with positive = +1 and negative = −1. A node with no qualifier,
  or with `occurred` or `ongoing`, counts as +1. Leave out edges with an
  `unchanged` node on either end; they have no variable-level sign.

Doing both double-counts polarity and silently flips the sign of every edge
whose object is a `decreased` or `absent` state. Using only the object sign
flips every edge whose subject is `decreased`, `absent`, `removed` or
`terminated`.

| Annotation | State-level sign | Variable-level sign |
|---|---|---|
| increased X `prevents` Y | − | (+1)(−1)(+1) = − |
| decreased X `causes` Y | + | (−1)(+1)(+1) = − |
| decreased X `causes` decreased Y | + | (−1)(+1)(−1) = + |
| removed X `disrupts` increased Y | − | (−1)(−1)(+1) = + |

`CausalEdge.fcm_weight` is stored at the state level. The full rule is in the
`CausalPredicateEnum` description.
**Step 5 — orient.** `direction.status: asserted` → single arc.
`bidirectional` → two arcs; FCMs tolerate this. `uncertain` or `not_addressed`
→ include with a flag, or exclude, but be consistent.
**Step 6 — handle certainty explicitly.** If the FCM design intentionally
down-weights causal influence by `aggregate_certainty_grade`, record the multiplier and
rule in `aggregate_fcm_weight_source`. Do not silently treat certainty as effect magnitude;
an alternative is to preserve the central weight and run sensitivity scenarios over
uncertainty.

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

4. **Moderators** — `moderation.moderator_node_ids` attach **to the edge**, not
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
Intervention and outcome are **positions in an edge**, not kinds of thing: the
same node is an outcome in one edge and a mediator in another. Role is derived
from edge position, never from node type.

### Column zoom comes free

Every `EcosystemFunctionalGroupEnum` value carries an `iucn_get_code`
annotation. Truncating it gives the IUCN GET hierarchy without a crosswalk:

```
T1.1  →  T1  (biome)  →  T  (realm)

```
Render at realm level for an overview, drill to Level 3 on demand. Use
`display_label` (which already includes the code) for column headers.

### Row rollup does not

`EntityTypeEnum` has four values; "seeding" is not one of them, it is an
`entity_term`. One row per distinct term is unreadable, so rows must roll up
through ELMO's subsumption hierarchy at query time. This requires:

- ELMO to carry `is-a` axioms for management interventions at usable depth
- a traversal step in the query layer, by reasoner or materialized closure
Verify both before building the renderer. Rollup is deliberately **not**
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

- **`applied_to.entity_term` may be free text.** **Sphagnum**, **sphagnum moss**,
  and **peat moss** are three different filter targets, so a facet query
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

CAMO nodes are states: "increased **Sphagnum** cover" and "decreased **Sphagnum**
cover" are two different nodes. A BBN needs one **variable** (**Sphagnum**
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
tells the modeller that a noisy-OR CPT is **inappropriate** and an interaction
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
  under-represents no-change. Show the cell as **thin**, not absent.

- **A thin `unchanged` cell is not a missing one.** `unchanged` means the
  source measured no change; a null `state_or_change_qualifier` means it did not
  say. Distinguish them in the state-space display — the first is evidence.

- **Priors and CPTs come from the modeller**, not from the graph. Keep them in
  separate storage referencing `EvidenceBaseAssessmentEdge` ids, so the
  literature layer stays uncontaminated by elicited judgement.

---

## 6. Spatial Prioritization (`prioritizr`)

**This target is an optimization-input compiler, not a priority map generated from CAMO alone.**
CAMO supplies evidence about the expected ecological consequences of management actions.
A spatial prioritization additionally requires planning units, baseline spatial feature data,
action-specific costs, feasibility, targets, and optimization choices.

The intended question is:

> Given what the evidence says is likely to happen if we take action *A*, where should we
> allocate that action to meet ecological targets at acceptable cost?

[`prioritizr`](https://prioritizr.net/) is a particularly good fit because it supports
problems with multiple **management zones**. A zone can represent a management action,
and zone-specific feature data can represent the expected amount, occurrence probability,
or abundance of each feature in each planning unit if that action is allocated there.

### Why management zones fit CAMO

| `prioritizr` concept | CAMO contribution | External contribution |
|---|---|---|
| Planning unit | none | polygon/raster planning units |
| Management zone | `management_intervention` node, grouped by `entity_term` | optional baseline / no-action zone |
| Conservation feature | outcome `CausalNode.variable_key` or linked ecological feature | baseline spatial distribution |
| Action → feature response | preferably `EvidenceBaseAssessmentEdge` | response-model transformation |
| Zone-specific feature amount | derived from CAMO response × spatial baseline × context match | baseline value for each planning unit |
| Cost | none | cost by planning unit × action |
| Feasibility | contextual evidence may inform it, but does not define it | feasibility / eligibility layer |
| Target | none | policy, stakeholder, regulatory, or ecological target |
| Connectivity / locking / other constraints | none | spatial planning rules |

The important boundary is deliberate: **CAMO tells the prioritization what an action is
expected to do; it does not tell the optimizer what society should value, what an action
costs, or where that action is physically possible.**

### Consumes from CAMO

Prefer `EvidenceBaseAssessmentEdge` wherever one exists.

| Source | Used for |
|---|---|
| `CausalNode.entity_type` | identify candidate management interventions |
| `CausalNode.entity_term` | define / roll up management actions |
| `CausalNode.variable_key` | define stable ecological outcome features |
| `CausalNode.applied_to` | retain taxonomic or target scope |
| `EvidenceBaseAssessmentEdge.subject` / `object` | identify action → outcome relationships |
| `predicate`, `aggregate_effect_sign` | direction of expected response |
| `aggregate_effect_size`, `effect_size_metric` | quantitative response where comparable |
| `aggregate_fcm_weight` | relative response strength only when no calibrated effect is available |
| `aggregate_certainty_grade`, `evidence_balance` | uncertainty / scenario metadata |
| `context_dependence_summary` | transferability and scope-condition checks |
| member-edge `ecosystem_context` | ecological context in which the response was observed |
| `number_of_studies`, `number_of_contradicting_edges` | evidence diagnostics |
| `temporal_extent` on member edges | lag and duration of response where relevant |

`aggregate_fcm_weight` is **not** an effect size. A weight of `0.7` must never be
interpreted as a 70% increase in the ecological feature. If it is used, the result is a
relative suitability / response score rather than a predicted ecological amount.

### Requires external inputs

A `prioritizr` renderer must declare these inputs explicitly rather than fabricating them:

- **planning units** — raster cells, polygons, parcels, or other decision units;
- **baseline feature layers** — current abundance, area, occurrence probability,
  condition, or another feature metric in each planning unit;
- **action-specific cost layers** — cost of allocating each planning unit to each
  management action;
- **feasibility or eligibility layers** — where each intervention can actually be applied;
- **targets** — the required amount or proportion of each feature;
- **objective** — e.g. minimum-set or maximum-utility formulation;
- **constraints and penalties** — locked-in/out areas, connectivity, budgets, etc.; and
- **solver configuration**.

These are part of the spatial decision problem, not the literature evidence graph.

### Procedure

**Step 1 — define candidate management zones.**

Select subject nodes where `entity_type == management_intervention`. Group equivalent or
more-specific interventions through the ELMO hierarchy at query time, exactly as for EGM
rows.

Each selected intervention becomes a candidate `prioritizr` zone:

```text
no_action
ditch_blocking
native_seeding
prescribed_burn
```

`no_action` or `baseline` is normally an external reference zone; do not invent a CAMO
management-intervention node solely to satisfy the renderer.

**Step 2 — define conservation features.**

Use the outcome side of intervention → outcome relationships. Collapse state-specific CAMO
nodes to `CausalNode.variable_key` so that:

```text
increased native forb cover
decreased native forb cover
unchanged native forb cover
```

refer to one optimization feature:

```text
native forb cover
```

The state/change qualifier describes the **response**, not three separate spatial features.

If an outcome does not resolve to a stable `variable_key`, do not silently create a feature.
Flag it for reconciliation.

**Step 3 — select evidence-backed action → outcome relationships.**

For each candidate management zone and feature:

1. prefer the corresponding `EvidenceBaseAssessmentEdge`;
2. exclude relationships that are only associational unless the prioritization explicitly
   permits non-causal predictors;
3. handle `negated` explicitly;
4. surface `evidence_balance`, `conflict_summary`, and contradicting-edge counts; and
5. retain the assessment id as provenance for every derived response.

Do not combine several article-level edges as if they were independent action effects when
an aggregate assessment exists.

**Step 4 — convert evidence into an action-response function.**

For planning unit \(p\), feature \(f\), and management zone \(z\), the renderer needs an
expected feature amount:

\[
R_{pfz} = h(B_{pf}, E_{fz}, C_{pfz})
\]

where:

- \(B_{pf}\) = baseline amount / occurrence / abundance of feature \(f\) in planning unit \(p\);
- \(E_{fz}\) = evidence-derived response to action \(z\); and
- \(C_{pfz}\) = match between the planning unit and the contexts in which the response is
  supported.

The function \(h\) must be declared by the renderer.

Examples:

- a risk ratio may multiply a baseline probability;
- a mean difference may add to a baseline continuous value;
- a percent change may transform a baseline abundance;
- a sign-only relationship may produce only a relative suitability score.

Do **not** combine effect metrics that are not commensurable. `aggregate_effect_size` is a
string because CAMO preserves the reported synthesis; the renderer must know the
`effect_size_metric` before using it numerically.

**Step 5 — check spatial transferability.**

Compare planning-unit context with the contexts represented by the evidence:

- `ecosystem_context`;
- `context_dependence_summary`;
- geographic scope on member edges;
- `applied_to`; and
- temporal scope where relevant.

A relationship observed in one ecosystem should not automatically be projected into every
planning unit.

When context does not match, choose and record one of three behaviours:

1. **exclude** the action-feature response from that planning unit;
2. **flag** it as extrapolation while retaining the estimate; or
3. **attenuate / scenario-test** it using an explicitly documented transferability model.

Never hide the extrapolation inside the feature layer.

**Step 6 — represent uncertainty as scenarios, not fake precision.**

`aggregate_certainty_grade` is confidence in the evidence, not ecological effect magnitude.
Do not automatically calculate:

```text
effect × certainty score
```

unless that transformation is an explicit modelling decision.

Prefer generating response scenarios such as:

```text
conservative_response
central_response
optimistic_response
```

or otherwise carrying lower / central / upper estimates into sensitivity analyses.
A planning unit that remains selected across scenarios is much more informative than a
single priority based on an arbitrary certainty multiplier.

**Step 7 — construct the `prioritizr` feature data.**

For tabular problems, the natural interchange is an `rij` table:

| `pu` | `species` | `zone` | `amount` |
|---:|---:|---:|---:|
| 1 | 1 | 1 | 0.20 |
| 1 | 1 | 2 | 0.42 |
| 1 | 1 | 3 | 0.51 |
| 2 | 1 | 1 | 0.36 |
| 2 | 1 | 2 | 0.48 |

Here:

- `pu` = planning-unit identifier;
- `species` = `prioritizr` feature identifier;
- `zone` = management-action identifier; and
- `amount` = expected amount of the feature if that planning unit is allocated to that
  action.

The numeric values above are illustrative. A renderer must derive them from an explicit
response model; it must never manufacture plausible-looking amounts from signs or
certainty grades.

For raster or spatial-feature workflows, the same information can instead be organized as
zone-specific feature layers using `prioritizr::zones()` or the corresponding zone-aware
input format.

**Step 8 — attach costs, targets, and constraints externally.**

A CAMO-derived response matrix is only one input to the optimization.

For a tabular multi-zone problem, the resulting workflow is conceptually:

```r
p <- problem(
  planning_units,
  features,
  rij = rij,
  zones = zones,
  cost_column = c("cost_no_action", "cost_seeding", "cost_burn")
) |>
  add_min_set_objective() |>
  add_manual_targets(targets) |>
  add_binary_decisions() |>
  add_default_solver()

solution <- solve(p)
```

The exact `problem()` input format depends on whether planning units and feature data are
represented as rasters, `sf` objects, or tables. The renderer contract is the **semantic
mapping**, not one mandatory R serialization.

**Step 9 — preserve a provenance sidecar.**

The solved priority map alone is not an adequate rendering.

For every feature × zone response, retain:

```text
CAMO variable_key
management-intervention entity_term
EvidenceBaseAssessmentEdge id
effect-size metric / transformation
context-match rule
uncertainty scenario
baseline spatial layer version
cost-layer version
```

Also record the `prioritizr` objective, targets, constraints, package version, solver, and
solver settings. Two maps generated from the same CAMO evidence can differ because of
different societal targets or costs; that difference must remain visible.

### Output contract

The renderer should produce a **`prioritizr`-ready decision bundle**, optionally followed by
a solved prioritization:

```text
planning_units
features
zones
rij or zone-specific feature layers
cost matrix / cost columns
targets
constraints / penalties
CAMO provenance sidecar
uncertainty scenario metadata
```

The primary CAMO-derived product is the **action × feature response layer**, not the
optimization solution itself.

### Worked example

Suppose CAMO contains evidence that ditch blocking increases Sphagnum cover in palustrine
wetlands, with context-dependent response magnitude.

External spatial data provide:

```text
planning unit 104
baseline Sphagnum cover = 0.18
ecosystem = palustrine wetland
ditch-blocking cost = $12,400
ditch blocking feasible = true
```

The renderer applies a declared response model and generates:

```text
feature: Sphagnum cover
zone: ditch blocking
planning_unit: 104
expected_amount: 0.37
evidence_base_assessment: eba_042
scenario: central_response
```

`prioritizr` then considers that expected benefit together with costs, targets, and all other
features and actions. CAMO supplied the **evidence-backed consequence of the action**;
`prioritizr` decides whether that action belongs in the optimal spatial portfolio.

### `prioritizr` references for the spatial renderer

The spatial target above follows the current `prioritizr` interfaces for conservation
problems, management zones, and zone-specific expected feature amounts:

- [`problem()`](https://prioritizr.net/reference/problem.html)
- [`zones()`](https://prioritizr.net/reference/zones.html)
- [Management zones tutorial](https://prioritizr.net/articles/management_zones_tutorial.html)
- [Targets](https://prioritizr.net/reference/targets.html)

### Gotchas

- **CAMO is not a spatial distribution model.** It does not provide planning units or the
  baseline distribution of features. Those must come from an observation or spatial-data
  layer.

- **FCM weight is not ecological amount.** `aggregate_fcm_weight` can rank relative
  responses when no calibrated effect is available, but it cannot populate an abundance or
  area target without an additional model.

- **Change is not level.** CAMO often represents *increased cover* or *decreased
  abundance*, while `prioritizr` expects the amount / occurrence / abundance of a feature
  expected under each zone. The renderer must transform a change estimate against a
  baseline; it cannot write the delta directly into `amount` unless the optimization
  feature itself is explicitly a change metric.

- **Do not double-count qualifier states.** `increased`, `decreased`, and `unchanged`
  versions of one `variable_key` are response states, not three independent conservation
  features.

- **Context is part of the effect.** Applying one evidence-base effect uniformly across a
  province silently assumes perfect transportability. Use `ecosystem_context` and
  context-dependence information to restrict or scenario-test extrapolation.

- **Indirect pathways are not automatically additive.** Do not multiply or sum effects
  along CAMO paths to manufacture an intervention → endpoint effect unless the response
  model explicitly supports that operation.

- **Targets are normative inputs.** CAMO evidence can help estimate what an action does;
  it does not determine how much habitat, abundance, or probability of occurrence should
  be secured. Keep targets attributable to the policy or stakeholder process.

- **Costs and feasibility remain external.** A prioritization without action-specific
  costs or eligibility is not a complete `prioritizr` problem, even if the ecological
  response layer is excellent.

- **A priority map is conditional.** Always label the output with its response scenario,
  targets, costs, constraints, and solver configuration. The map is a solution to one
  declared decision problem, not a direct property of the CAMO graph.


---

## 7. Practitioner Summary

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

## 8. RAG Retrieval

Source-text retrieval for question answering over the corpus.

### Consumes

`CausalNode.embedding_text` / `embedding_vector`,
`CausalEdge.original_sentence`, `source_spans` (`text`, `start_char`,
`end_char`, `sentence_id`, `paragraph_id`, `section`), `SourceDocument` (`document_id`,
`doi`, `title`, `authors`, `year`, `journal`).

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

| Field | Rosetta | FCM | Diagram | EGM | BBN | Spatial | Practitioner | RAG |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `entity_term` / `measured_attribute` | ● | ● | ● | ● | ● | ● | ● | ● |
| `variable_key` | | | ○ | | ● | ● | | |
| `state_or_change_qualifier` | ● | ○ | ● | | ● | ○ | ● | |
| `applied_to` | | | | ● | ● | ○ | | |
| `entity_type` | | | ● | ● | | ● | | |
| `predicate` | ● | ● | ● | | ● | ● | ● | |
| `causal_language` | ● | ● | | | | ○ | | |
| `negated` | ● | ● | ● | ● | ● | ● | ● | |
| `ecosystem_context` | ○ | | | ● | | ● | ● | |
| `direction` | | ● | ● | | ● | ○ | | |
| `mediation` | ○ | ○ | ● | | ● | ○ | | |
| `moderation` | | ○ | ● | | ● | ○ | | |
| `strength` | ○ | ● | | | | ○ | | |
| `reversibility` | | | | | | ○ | ● | |
| `contributing_sole` | | | | | ● | ○ | ● | |
| `context_dependence` | ○ | | | | | ● | ● | |
| `temporal_extent` | | | | | | ○ | ● | |
| `philosophical_accounts` | | | | | | | ○ | |
| `fcm_weight` | | ● | | | | ○ | | |
| `aggregate_fcm_weight` | | ● | | | | ○ | | |
| `aggregate_effect_sign` / `_size` / `effect_size_metric` | | ○ | | | ○ | ● | ○ | |
| `aggregate_certainty_grade` | ● | ● | | ● | ● | ● | ● | |
| `evidence_balance` / `conflict_summary` | | ○ | | ○ | ● | ● | ● | |
| `russo_williamson_satisfied` | | | | ○ | ● | ○ | | |
| `number_of_studies` / `_contradicting_` | | | | ● | ● | ● | ● | |
| `source_spans` / `SourceDocument` | | | | ● | ● | ○ | ○ | ● |
| `embedding_text` / `_vector` | | | | | | | | ● |

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
| `entity_term` accepts free text | EGM facets, BBN grouping, Spatial feature/action matching | Silent undercounting or duplicate concepts |
| Empty EGM cell has three meanings | EGM | "No evidence" read as "no effect" |
| Node signs plus predicate signs | FCM | Double-counted polarity if both applied |
| Rollup depends on ELMO `is-a` | EGM rows, Spatial zones | Unreadable or fragmented action categories if hierarchy is shallow |
| `aggregate_fcm_weight` is not an effect size | Spatial | Relative causal weight misread as predicted ecological amount |
| CAMO stores response evidence, not baseline distributions | Spatial | `prioritizr` feature amounts cannot be constructed without external spatial data |
| Effect context may not match planning-unit context | Spatial | Unsupported spatial extrapolation appears as precise benefit |
| Targets, costs, and feasibility are external | Spatial | Optimization choices can be mistaken for evidence-derived facts |
| Qualifier states are not independent features | BBN, Spatial | One ecological variable is duplicated into incompatible states/features |

