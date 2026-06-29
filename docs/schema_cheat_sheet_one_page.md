# Causal Mosaic One-Page Cheat Sheet

## What This Is

The Causal Mosaic schema stores ecological cause-and-effect claims in a structured way.

Think of it like this:

- a **node** is a change
- an **edge** is a claim that one change affected another change
- the rest of the fields explain how strong the claim is and what evidence supports it

## The Core Idea

Instead of storing only a sentence like:

> Removing buckthorn increased light and helped native wildflowers recover.

the schema breaks that into pieces that can be searched, compared, and reused.

## The 5 Questions to Ask

1. What changed?
2. Which way did it change?
3. What did it affect?
4. How strong is the causal claim?
5. What evidence supports it?

If you can answer those questions, you can understand most of the schema.

## The Two Main Parts

### Nodes = changes

Examples:

- increased buckthorn removal
- decreased buckthorn canopy cover
- increased light availability
- increased native forb richness
- increased bee diversity

### Edges = causal links

Examples:

- more buckthorn removal -> less buckthorn canopy cover
- less buckthorn canopy cover -> more light
- more light -> more native forbs
- more native forbs -> more bee diversity

## The Schema in One Picture

```mermaid
graph LR
  A["Node: more buckthorn removal"] --> B["Edge: reduces"]
  B --> C["Node: less buckthorn canopy cover"]
  C --> D["Edge: increases"]
  D --> E["Node: more light at ground level"]
  E --> F["Edge: increases"]
  F --> G["Node: more native forb richness"]
```

## What a Node Usually Contains

| Plain-language question | Schema field |
|---|---|
| What thing or process is this about? | `entity_term` |
| What property is changing? | `variable_attribute` |
| Which way did it change? | `variable_direction` |
| In what setting? | `ecosystem_context`, `process_context`, `conditioned_by` |

## What an Edge Usually Contains

| Plain-language question | Schema field |
|---|---|
| What is causing the change? | `subject` |
| What kind of causal link is claimed? | `predicate` |
| What is being affected? | `object` |
| How strong is the claim? | `claim_strength` |
| What kind of causal reasoning is used? | `philosophical_accounts` |
| How do we know? | `evidential_basis` |

## Plain Language to Schema

| Ordinary language | Schema meaning |
|---|---|
| "buckthorn canopy cover" | the thing being measured |
| "decreased" | `variable_direction` |
| "less buckthorn canopy" | a node |
| "caused" / "led to" | an edge |
| "strong evidence" | strength / certainty fields |
| "shown by experiment" | evidence type |

## Tiny Worked Example

### In plain language

> Removing buckthorn reduced canopy cover.

### In schema language

Node 1:

- increased buckthorn removal

Node 2:

- decreased buckthorn canopy cover

Edge:

- buckthorn removal `negatively_regulates` buckthorn canopy cover

## What the Extra Fields Are For

These fields answer practical questions like:

- Is this a strong causal claim or a tentative one?
- Is direction clearly supported?
- Does the effect depend on context?
- Is the evidence experimental, observational, mechanistic, or mixed?

## Why Ontology IDs Exist

Ontology IDs help keep wording consistent across papers.

For most readers, the key point is:

- labels are for people
- identifiers are for consistency and machine use

You do not need to memorize IDs to understand the schema.

## Best Simple Explanation

> The schema turns a causal sentence from a paper into a chain of changes and links, then adds notes about confidence, context, and evidence.

## Starter Template

Fill this out before looking at YAML:

1. Change 1: `__________`
2. Change 2: `__________`
3. Link: `Change 1 affects Change 2`
4. Evidence: `__________`
5. Confidence: `strong / moderate / weak / uncertain`
