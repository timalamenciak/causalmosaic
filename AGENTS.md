# AGENTS.md — Causal Mosaic Schema (CAMO)

Instructions for coding agents working in the CAMO repository. Read by Claude
Code (via a `CLAUDE.md` symlink), Codex, and OpenCode. Keep it lean.

## What this repo is

The **source of truth** for the Causal Mosaic schema — a **LinkML data model**
(YAML), grounded in Illari & Russo's causal mosaic framework, used to annotate
restoration-ecology causal evidence. The schema lives in `causalmosaic.yaml`;
its current version is the `version:` field there (0.8.0 at time of writing).
Past released versions are archived in `old versions/`. Data-migration scripts
between versions live in `helpers/`; add one with each breaking release.

This is a **schema, not an ontology and not app code.** The `.yaml` is authored
by hand; Pydantic, JSON Schema, SHACL and OWL are *generated* from it on
demand (none are committed here). The pages in `docs/`, `README.md` and
`CHANGELOG.md` are hand-maintained and must be kept in step with the schema.
Downstream repos — notably loom — generate code and validate data against
what is released here, so class and slot **names are a published contract.**

## The loop (non-negotiable)

CI (`.github/workflows/linkml-schema.yml`) runs these three checks with
`linkml==1.11.1`. Run them with that version; older releases (e.g. 1.8.x)
miss errors CI catches.

```bash
linkml validate causalmosaic.yaml
linkml lint causalmosaic.yaml
python ci.py causalmosaic.yaml
```

Green means: the schema is valid against the LinkML metamodel, it lints, and
CAMO's own invariants hold (`ci.py` checks the annotation crosswalks LinkML
treats as opaque strings). Never hand back a state that fails. Fix the schema,
not the checks.

## Commands

| Task                 | Command                                             |
| -------------------- | --------------------------------------------------- |
| Metamodel validation | `linkml validate causalmosaic.yaml`                 |
| Lint schema          | `linkml lint causalmosaic.yaml`                     |
| CAMO invariants      | `python ci.py causalmosaic.yaml`                    |
| Validate data        | `linkml-validate -s causalmosaic.yaml «data».yaml`  |
| JSON Schema          | `gen-json-schema causalmosaic.yaml`                 |
| Pydantic models      | `gen-pydantic causalmosaic.yaml`                    |
| Migrate 0.7.9 data   | `python helpers/migrate_0_7_9_to_0_8_0.py «data».yaml -o «out».yaml` |

## Authoring conventions (this is a LinkML schema)

- **The `.yaml` is the source; generated artifacts are outputs.** Regenerate
  them — never hand-edit Pydantic, JSON Schema, SHACL, OWL, or docs.
- **Class and slot names are the public API.** Downstream code is generated from
  them and existing data keys on them. Do not rename or remove without a
  deprecation path and a changelog entry — a silent rename breaks loom's
  generated models and existing annotations.
- **Every class and slot needs a `description`; every slot needs an explicit
  `range`.** No untyped or undocumented slots.
- **Declare every prefix in the `prefixes` block and set `id_prefixes` on
  identified classes.** Consistent CURIE prefixes are what let identifiers
  resolve — this is the schema-side version of the CURIE hygiene that keeps
  biting annotation runs.
- **Model causal-relation categories as closed enums grounded in the causal
  mosaic framework**, not free-text strings or ad hoc permissible values.
- **Bump the schema `version:` on any breaking change**, with a changelog note.
  Record changes in both the `## CHANGELOG` header of `causalmosaic.yaml` and
  `CHANGELOG.md`; until the bump, log them under "Unreleased". Before the first
  breaking change after a release, archive that release as
  `old versions/causal_mosaic_v«version».yaml`.
- **LinkML rules can't test boolean slots.** `equals_string: "true"` compiles
  to the JSON string `"true"`, not a boolean, so such rules misfire. State
  boolean invariants with `equals_expression` and note that loom enforces them.
- **Rules must name the current slot**, not an alias. JSON Schema output keys on
  slot names, so a rule citing an alias requires a property that can't exist.
- **Keep descriptions encodable in cp1252** (no `→` or similar). Generators
  crash on Windows consoles otherwise.

## Hard "do not"

- Do **not** hand-edit any generated artifact. Change the schema and regenerate.
- Do **not** rename/remove a released class, slot, or enum without a deprecation
  path + changelog + migration note for loom.
- Do **not** add a slot without a `range` and `description`.
- Do **not** bump the version without recording the breaking changes.

## Maintaining this file

Human-owned. Do not rewrite it wholesale or append notes mid-task. Propose
durable conventions in your response and let a human fold them in.