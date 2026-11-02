# Adding a Term to EcoSKOS

**EcoSKOS** — the stopgap vocabulary for the Causal Mosaic Schema (CAMO)
Source: `vocab/ecoskos_terms.tsv` · Licence: CC0 · `https://w3id.org/ecoskos/`

When an annotator needs an `entity_term` and no ontology has the concept yet,
the choices are free text, which cannot be grouped or resolved, or a local term
with a permanent ID, which can. EcoSKOS holds those local terms. It is also a
worklist: every term records where an ontology editor would put it, so each one
is a request waiting to be filed, and each one is retired by mapping it to the
ontology term once that exists.

This guide covers adding a term, moving it through its lifecycle, and what to do
when an ontology adopts it. It is about the vocabulary, not the schema, and is
not versioned with `causalmosaic.yaml`.

---

## Contents

- [1. When to add a local term](#1-when-to-add-a-local-term)
- [2. Check the ontologies first](#2-check-the-ontologies-first)
- [3. Adding the row](#3-adding-the-row)
- [4. The fields](#4-the-fields)
- [5. The status lifecycle](#5-the-status-lifecycle)
- [6. When a term lands upstream](#6-when-a-term-lands-upstream)
- [7. Why IDs are permanent](#7-why-ids-are-permanent)
- [8. Commands](#8-commands)
- [9. Current limits](#9-current-limits)

---

## 1. When to add a local term

Add a term only when **all three** hold:

1. You searched the ontologies (section 2) and found no term that means what the
   source means.
2. You need a stable identifier now, because the concept will appear in more than
   one annotation, paper or project.
3. You can say where an ontology editor would put it: an existing term it is a
   kind of.

Do **not** add a term when:

| Situation | Do this instead |
|---|---|
| The concept is a taxon | Use NCBITaxon or Wikidata, which have their own identifiers for taxa. If one is truly missing, ask them, not EcoSKOS. |
| An ontology term exists but the label differs | Use the ontology term and record the source's wording as a synonym there, not here. |
| An existing term plus a qualifier says it | `entity_term` is the entity; the change goes in `measured_attribute` and `state_or_change_qualifier`. |
| It would appear once, in free text, and nowhere else | Free text is allowed. Loom flags it for curation. |

---

## 2. Check the ontologies first

Where to look depends on what kind of thing it is:

| Kind of entity | Look in |
|---|---|
| Taxon | Wikidata, NCBITaxon |
| Environment, habitat | ENVO |
| Quality, attribute | PATO |
| Biological process | GO, ENVO process terms |
| Management action or intervention | ELMO (`https://w3id.org/elmo/`) |
| Chemical | CHEBI |
| A term already proposed here | `docs/ecoskos/index.html`, or search `vocab/ecoskos_terms.tsv` |

Then, in this order:

1. **Search the EBI Ontology Lookup Service** (`https://www.ebi.ac.uk/ols4`) for the
   label, then for each synonym, then for the broader concept. Restrict the search to
   the ontologies in the table; an unrestricted search returns many unrelated
   hits from medicine and molecular biology.
2. **Search Wikidata** (`https://www.wikidata.org`) for the same words.
3. **Browse ELMO** if the concept is a management action. ELMO labels end in
   *process*: *translocation process*, *transplanting process*.
4. **Search EcoSKOS** so you do not add a duplicate.

### Gotchas

- **Search is noisy.** Searching "plant translocation" returns proteins and phloem
  cells, and says nothing about whether a restoration term exists. Search for the
  verb on its own and for the parent concept, and read the hits.
- **A near miss is not a miss.** If an existing term is close, use it, or propose a
  change to it upstream. A local term is for concepts that genuinely have no home.
- **Open every ID before you use it.** An ID that looks right can name something
  else entirely: `wd:Q30055` is a car company, not *Alliaria petiolata*. Read the
  label and definition at the ID itself. Never copy an ID from memory, from another
  document, or from a model.
- **Write down what you searched.** It goes in `rationale`, and the editors you
  eventually ask will want to know.

---

## 3. Adding the row

You can add a term in either of two ways.

**With git.** Edit `vocab/ecoskos_terms.tsv` in a spreadsheet or a text editor.
It is tab-separated UTF-8.

1. Get the next free ID: `make vocab-next-id`
2. Add a row and fill the fields (section 4).
3. Run `make vocab`. It validates the file and regenerates
   `docs/ecoskos/ecoskos.ttl` and `docs/ecoskos/index.html`.
4. Commit the TSV **and** both generated files together.

Never edit the generated files by hand; the next build overwrites them, and
`make vocab-check` fails if they do not match the TSV.

**Without git.** Open a *Propose a vocabulary term* issue. A maintainer checks the
proposal and adds the row.

Annotators then write the CURIE, for example `entity_term: ecoskos:0000001`.

---

## 4. The fields

| Column | Required | What goes in it |
|---|---|---|
| `id` | yes | `ecoskos:` and seven digits. Take it from `make vocab-next-id`. Never chosen by hand, never reused. |
| `label` | yes | The preferred name, lowercase unless a proper noun, in the form an ontology would use. |
| `definition` | yes | One or two sentences: what kind of thing it is (the broader term), then what sets it apart. |
| `broader` | yes | A CURIE for an existing ontology term this is a kind of. It tells the editors where it belongs. The prefix must be declared in the `prefixes` block of `causalmosaic.yaml`. May be another `ecoskos:` term. |
| `status` | yes | `proposed`, `requested`, `mapped` or `deprecated` (section 5). |
| `proposed_by` | yes | Who proposed it. |
| `proposed_on` | yes | `YYYY-MM-DD`. Starts the clock for `make terms-report`. |
| `source` | yes | Where the need arose: a paper, a DOI, a page of the annotation guide. |
| `request_url` | when requested | The issue or term request upstream. |
| `requested_on` | when requested | `YYYY-MM-DD`. The report counts a requested term's age from this date. |
| `mapped_to` | when mapped | The upstream CURIE. |
| `mapping_type` | no | `exact`, `close`, `broad` or `narrow`; blank means `exact`. |
| `replaced_by` | no | For a deprecated term: the CURIE of its replacement. |
| `synonyms` | no | Other labels, separated by `\|`. Add every spelling you have seen; synonyms are how people find the term. |
| `rationale` | no | Why the term is needed, and what you searched. Used by `make term-request`. |
| `example_usage` | no | An annotation that needs the term. Used by `make term-request`. |

`rationale` and `example_usage` are working notes. They are not published in the
Turtle or the HTML.

### Gotchas

- **`broader` may only be empty for a moment.** The build fails on an empty
  `broader`, so a draft with none will not build. That is intended: it keeps
  unplaced terms from being published.
- **Prefer a parent you have opened.** Check that the ID exists and that its label
  and definition fit, before you enter it.
- **Dates are `YYYY-MM-DD`.** `01/02/2026` is rejected, because it is ambiguous.

---

## 5. The status lifecycle

```
proposed  ──►  requested  ──►  mapped
    │              │
    └──────────────┴────────►  deprecated
```

| Status | Meaning | To move on |
|---|---|---|
| `proposed` | Needed, but nobody has asked an ontology for it. | File the request: `make term-request ID=ecoskos:NNNNNNN` prints it ready to paste. Then set `request_url`, `requested_on` and `status: requested`. |
| `requested` | An upstream request is open. | When the term exists, follow section 6. |
| `mapped` | An ontology term now exists. Annotators should use that. | Nothing. A mapped term stays mapped. |
| `deprecated` | Withdrawn: wrong, duplicate or no longer needed. | Nothing. Set `replaced_by` if there is a replacement. |

`make terms-report` shows how many terms are in each status and which proposed or
requested terms have waited more than `DAYS` days (default 90). Use it to decide
which requests to chase.

---

## 6. When a term lands upstream

1. **Open the new term** and read its label and definition. Confirm it means what
   ours means.
2. **Set `mapped_to`** to its CURIE. If the prefix is not in `causalmosaic.yaml`
   yet, add it there first.
3. **Set `mapping_type`** to how the two compare:

   | `mapping_type` | Use when |
   |---|---|
   | `exact` | They mean the same thing. |
   | `close` | They are nearly the same, but not interchangeable. |
   | `broad` | The upstream term is **broader** than ours. |
   | `narrow` | The upstream term is **narrower** than ours. |

4. **Set `status` to `mapped`.**
5. **Run `make vocab`**, and commit the TSV and the generated files.

**Do not delete the row, and do not renumber it.** The concept stays in the
vocabulary with its match, so every annotation that uses `ecoskos:NNNNNNN` still
resolves, and anything downstream can follow the match to the ontology term.

New annotations should use the upstream CURIE. Rewriting `entity_term` in existing
data is a separate step that this repository has no tool for. Do it deliberately:
a node's `id` is built from its `entity_term`, so changing the term changes the
node's ID.

If the upstream term turns out to mean something different, map it as `close`,
`broad` or `narrow`, or set our term to `deprecated` with `replaced_by`.

---

## 7. Why IDs are permanent

An `ecoskos:` ID is written into annotation data and into the IDs of the nodes
built from it. Once it is published, other people's graphs depend on it.

- **Reusing an ID changes what old annotations mean**, silently, with nothing to
  tell you it happened. So an ID is never given to a second concept.
- **Renumbering breaks every reference at once.** So IDs are never renumbered.
- **Deleting a row leaves references that point at nothing.** So rows are never
  deleted. Deprecation is the removal mechanism: the row stays, marked
  `owl:deprecated`, and a successor is named if there is one.
- **The ID carries no meaning.** It is a number, not a slug, so correcting a label,
  adding a synonym or reshaping the hierarchy never forces an ID to change.

The build enforces the rule: if an ID is in the published `ecoskos.ttl` and missing
from the TSV, `make vocab` fails and tells you to restore the row or deprecate it.

---

## 8. Commands

`make` is optional. Each target is one `python` command, shown here.

| Target | Command | What it does |
|---|---|---|
| `make vocab` | `python vocab/build_vocab.py` | Validate the TSV and regenerate the Turtle and HTML. |
| `make vocab-check` | `python vocab/build_vocab.py --check` | Validate, and fail if the generated files are stale. |
| `make vocab-next-id` | `python vocab/build_vocab.py --next-id` | Print the next free ID. |
| `make terms-report DAYS=60` | `python vocab/terms_report.py --days 60` | Counts by status, terms with no parent, and terms waiting too long. |
| `make term-request ID=ecoskos:0000001` | `python vocab/term_request.py ecoskos:0000001` | Print one term as a markdown term request for an ontology tracker. |

`term-request` writes the request to standard output and prints warnings to
standard error for anything missing, such as an empty `rationale`. Read those
before you post it, and trim the request to whatever the tracker's own template
asks for.

---

## 9. Current limits

These are true now and will go out of date as they are fixed.

- `https://w3id.org/ecoskos/` is **not registered yet**, so term IRIs do not
  resolve. Until it is, cite terms by their CURIE.
- The `ecoskos` prefix is **not yet declared** in `causalmosaic.yaml`, and nothing
  yet checks that an annotation's `entity_term` is either an ontology CURIE or an
  EcoSKOS term.
- CI does not yet run `make vocab-check`, so a stale generated file will not fail a
  pull request.
