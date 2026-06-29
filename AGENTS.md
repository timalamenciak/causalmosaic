# Schema Editing Instructions

These instructions apply to this repository and all files beneath it.

## Active schema

- The schema currently under development is `causal_mosaic_v0.4.2.yaml`.
- Do not modify an earlier or later schema version unless the user explicitly directs you to do so.

## Change control

- Only make changes explicitly requested by the user.
- Do not make opportunistic fixes, cleanups, formatting changes, renames, refactors, or inferred improvements.
- Ask the user for clarification whenever a requested change is ambiguous, incomplete, or could reasonably be implemented in materially different ways.
- Do not modify unrelated files or overwrite existing user changes.
- Familiarization, review, and validation do not authorize changes to the schema.

## Changelog

- Record every requested change in `CHANGELOG.md`.
- For each change, identify what changed and include the rationale supplied by the user.
- Do not invent a rationale. If the rationale is required but has not been supplied, ask the user for it before finalizing the change log entry.
- Explicitly note when an action changes only supporting documentation and does not change the schema.

## Validation and reporting

- After an authorized schema edit, validate the edited schema when suitable validation tooling is available.
- Report validation results separately from the requested changes; do not silently fix unrelated validation findings.
- In the final response, list the files changed and confirm whether `causal_mosaic_v0.4.2.yaml` was modified.
