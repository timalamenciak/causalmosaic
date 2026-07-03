# Schema Editing Instructions

These instructions apply to this repository and all files beneath it.

## Active schema

- The active schema is the highest-versioned `causal_mosaic_v*.yaml` file at
  the repository root (currently `causal_mosaic_v0.7.1.yaml`) — check the
  filenames and each file's internal `version:` field rather than trusting a
  hardcoded name here, since this note will otherwise drift out of date again
  as new versions ship.
- Do not modify an earlier or later schema version unless the user explicitly directs you to do so.

## Releasing a new version

When the `version:` field in the root schema file changes:

1. Update `CHANGELOG.md` with the change and its rationale (see Changelog below).
2. `git tag vX.Y.Z && git push --tags`
3. `gh release create vX.Y.Z causal_mosaic_vX.Y.Z.yaml --notes-file <changelog-excerpt>`
   — attaching the schema file itself as a release asset is the important part:
   downstream consumers (e.g. Loom) poll GitHub Releases for this repo and
   download that asset to pick up the new schema.

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
