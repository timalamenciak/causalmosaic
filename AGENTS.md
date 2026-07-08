# AGENTS.md — Causal Mosaic Schema (CAMO)

Instructions for coding agents working in the CAMO repository. Read by Claude
Code (via a `CLAUDE.md` symlink), Codex, and OpenCode. Keep it lean.

## What this repo is

The **source of truth** for the Causal Mosaic schema — a **LinkML data model**
(YAML), grounded in Illari & Russo's causal mosaic framework, used to annotate
restoration-ecology causal evidence. Current version: **v0.7.3**.

This is a **schema, not an ontology and not app code.** The `.yaml` is authored
by hand; everything else (Pydantic, JSON Schema, SHACL, OWL, docs) is
*generated* from it. Downstream repos — notably loom — generate code and
validate data against what is released here, so class and slot **names are a
published contract.**

## The loop (non-negotiable)

```bash
./validate.sh
```

Green means: the schema lints (`linkml-lint`), the example / test data validates
against it (`linkml-validate`), and all generated artifacts regenerate cleanly
with no uncommitted diff. Never hand back a state that fails. Fix the schema, not
the checks.

## Commands

<!-- CONFIRM each; replace guesses -->

| Task                | Command                                       |
| ------------------- | --------------------------------------------- |
| Validate (all)      | `./validate.sh`                               |
| Lint schema         | `linkml-lint camo.yaml`                        |
| Validate data       | `linkml-validate -s camo.yaml «data».yaml`     |
| Regenerate artifacts| `gen-project -d generated/ camo.yaml`          |
| Pydantic models     | `gen-pydantic camo.yaml`                       |
| Tests               | `pytest`                                        |

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

## Hard "do not"

- Do **not** hand-edit any generated artifact. Change the schema and regenerate.
- Do **not** rename/remove a released class, slot, or enum without a deprecation
  path + changelog + migration note for loom.
- Do **not** add a slot without a `range` and `description`.
- Do **not** bump the version without recording the breaking changes.

## Maintaining this file

Human-owned. Do not rewrite it wholesale or append notes mid-task. Propose
durable conventions in your response and let a human fold them in.