# Causal Mosaic Guide for Philosophers

## What This Is

This project turns causal claims from ecology papers into a structured, inspectable format.

If a paper says something like:

> Removing buckthorn reduced canopy cover, which increased light, which helped native plants recover.

the schema lets us represent that claim in a form that a computer can store, search, compare, and analyze without throwing away the philosophical distinctions that matter.

## The Main Idea

The schema separates two questions:

1. What ecological change is being talked about?
2. What kind of causal claim is being made about that change?

That is why the model has:

- nodes: the ecological changes
- edges: the causal claims linking those changes

## The Shared Example

All three documentation guides use the same example:

- managers remove invasive buckthorn
- buckthorn canopy cover goes down
- light at ground level goes up
- native forb richness goes up
- bee diversity goes up
- at the same time, recovering native grasses can suppress some forbs

So the point is not just "restoration worked." The point is that several distinct causal claims are being separated and annotated.

## What a Node Means

A node is not just a thing like "buckthorn" or "bees."

It is a change in a thing or process, such as:

- increased buckthorn removal intensity
- decreased buckthorn canopy cover
- increased light availability
- increased native forb richness

This matters philosophically because causes and effects are usually not bare objects. They are changes, states, or processes.

## What an Edge Means

An edge is a causal claim connecting two nodes.

For example:

```yaml
- subject: "node:buckthorn_canopy_cover"
  predicate: negatively_regulates
  object: "node:light_availability"
```

This says that more buckthorn canopy tends to reduce light at ground level.

## Why the Extra Annotations Exist

Philosophers often care that causal claims are not all of one kind.

The schema therefore asks:

- Is the claim interventionist?
- Is it mechanistic?
- Is it probabilistic?
- Is it a variation claim?
- Is the direction explicit?
- Is there a mediating pathway?
- Is the evidence merely correlational, mechanistic, or both?

So instead of flattening everything into one generic "causes" relation, the schema preserves distinctions that matter in causal analysis.

## Example: One Claim, Several Philosophical Readings

Consider the claim that less buckthorn canopy increases light.

In this schema, that same claim can be:

- mechanistic, because shading and light interception provide a production story
- variation-based, if measured with a structural model across plots
- interventionist indirectly, if the canopy changed because of deliberate removal

The model is pluralist on purpose. A single ecological claim can legitimately be characterized by more than one account of causation.

## What the Ontologies Are Doing

You do not need prior ontology knowledge to understand the role they play here.

An ontology in this context is just a controlled vocabulary with identifiers.

Instead of writing only "canopy" or "light" as loose text, the schema can point to stable references such as:

- an environment term for canopy
- a process term for growth
- a taxon identifier for Andropogon gerardii

That makes it easier to compare claims across papers that use different wording for the same thing.

## Why This Helps Philosophy

This format makes several familiar philosophical tasks easier:

- comparing difference-making and production evidence
- distinguishing strong and weak causal claims
- asking whether a mechanism is explicit or only assumed
- checking whether the claim is token-level or type-level
- seeing where claims rely on intervention, regularity, or probabilistic support

In short: the schema does not replace causal analysis. It makes causal analysis legible, repeatable, and queryable.

## The Example Chain

Here is the same example in compact form:

```mermaid
graph LR
  A["Buckthorn removal"] -->|reduces| B["Buckthorn canopy cover"]
  B -->|reduces| C["Light limitation"]
  C -->|increases| D["Native forb richness"]
  D -->|increases| E["Bee diversity"]
  C -->|increases| F["Native grass biomass"]
  F -->|suppresses| D
```

The important philosophical point is that the chain is not treated as one undifferentiated fact. Each link can have a different causal profile, strength, and evidential basis.
