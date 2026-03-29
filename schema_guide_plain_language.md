# Causal Mosaic Guide in Plain Language

## What This Schema Is, in Everyday Terms

This schema is a way to turn a sentence like:

> Removing buckthorn let in more light, which helped native wildflowers recover.

into a set of small, reusable pieces.

Why do that?

- so different papers can be compared more easily
- so the same idea does not have to stay buried in prose
- so people can search for patterns across many studies
- so a computer can help summarize the evidence later

The simplest way to think about it is:

**The schema stores causal stories as building blocks.**

## The Five Questions the Schema Asks

Instead of starting with technical field names, start with these questions:

1. What changed?
2. Which way did it change?
3. What does the paper say caused that change?
4. How strong or certain is the claim?
5. What kind of evidence supports it?

If someone can answer those five questions, they already understand most of the schema.

## The Two Main Building Blocks

### 1. Nodes = Changes

A node is one change the paper talks about.

Examples:

- buckthorn removal increased
- buckthorn canopy cover decreased
- light at ground level increased
- native forb richness increased
- bee diversity increased

The key idea is that the schema stores **changes**, not just things.

So it does not just store "buckthorn" or "bees."
It stores things like:

- less buckthorn canopy
- more bee diversity

### 2. Edges = Causal Links

An edge is the claim that one change helped produce another.

Examples:

- more buckthorn removal caused less buckthorn canopy
- less buckthorn canopy caused more light
- more light caused more native forbs
- more native forbs caused more bee diversity

So if nodes are the building blocks, edges are the arrows between them.

## A Very Simple Mental Model

You can explain the whole schema to a new person like this:

> A node is a change.
> An edge is a claim that one change affected another change.
> The rest of the schema is extra detail about how confident we are and why we believe it.

## One Example, Translated Step by Step

Plain-language claim:

> Removing buckthorn reduced canopy cover, which increased light, which helped native forbs recover.

Broken into nodes:

- increased buckthorn removal
- decreased buckthorn canopy cover
- increased light availability
- increased native forb richness

Broken into edges:

- increased buckthorn removal -> decreased buckthorn canopy cover
- decreased buckthorn canopy cover -> increased light availability
- increased light availability -> increased native forb richness

## Sentence-to-Schema Table

| In ordinary language | In the schema |
|---|---|
| "buckthorn canopy cover" | the thing being measured |
| "decreased" | the direction of change |
| "less buckthorn canopy" | a node |
| "led to" or "caused" | an edge |
| "strong evidence" | claim strength / certainty fields |
| "shown by an experiment" | evidential basis |

## The Extra Fields, Without the Jargon

Some parts of the schema are there so we do not treat every causal claim as equally good or equally clear.

Those fields mostly answer practical questions like:

- Was this a strong causal claim or a cautious one?
- Did the authors really show direction, or only an association?
- Did the effect depend on context?
- Was the evidence observational, experimental, mechanistic, or mixed?

So the extra fields are not a second schema hiding inside the first one.
They are just ways of saying:

- how sure are we?
- what kind of claim is this?
- what supports it?

## Why the Ontology IDs Are There

The IDs are mainly for consistency.

People may use different phrases for similar ideas:

- canopy cover
- shrub cover
- overstory cover

The ontology link helps the computer treat closely related terms in a more organized way.

For most readers, the important point is simple:

- the label is for people
- the identifier is for consistency and reuse

You do not need to memorize the IDs to understand the schema.

## A Better Way to Teach It Than a README Alone

One especially easy way to explain this schema is as a **before-and-after story card**.

For each claim, show:

- the cause change
- the effect change
- an arrow between them
- one line saying what evidence supports the claim

For example:

| Cause change | Effect change | What supports this? |
|---|---|---|
| more buckthorn removal | less buckthorn canopy cover | management intervention + field observation |
| less buckthorn canopy cover | more light at ground level | mechanistic reasoning + measurement |
| more light at ground level | more native forb richness | plot-level ecological evidence |

That format is easier for many readers because it starts with the story, not the YAML.

## If You Want a One-Sentence Summary

This schema is a structured way to store ecological cause-and-effect claims by breaking them into:

- what changed
- what it affected
- how strong the claim is
- what kind of evidence supports it

## If You Want a One-Minute Teaching Script

You could explain it out loud like this:

> The schema takes a causal claim from a paper and breaks it into pieces. Each piece of change becomes a node, like "more light" or "less canopy cover." Each causal link between those changes becomes an edge, like "less canopy cover leads to more light." Then the schema adds notes about how strong the claim is and what evidence supports it.

## A Fill-in-the-Blanks Template

When someone is first learning the schema, this is often easier than showing raw YAML:

1. The thing that changed was: `__________`
2. It changed in this direction: `increased / decreased / other`
3. The paper says it affected: `__________`
4. The claimed effect was: `__________`
5. The evidence came from: `__________`
6. The claim seems: `strong / moderate / weak / uncertain`

If someone can fill that out, the schema can usually be built from it afterward.
