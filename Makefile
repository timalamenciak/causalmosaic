# Thin wrapper over the commands in AGENTS.md. Every target is a plain
# `python ...` call, so the Makefile is optional: run the commands directly
# where make is not installed.

PYTHON ?= python
SCHEMA := causalmosaic.yaml

# make terms-report DAYS=30        flag proposed/requested terms older than 30 days
DAYS ?= 90
# make term-request ID=ecoskos:0000001
ID ?=

.PHONY: check schema-check vocab vocab-check vocab-next-id terms-report term-request

# Everything CI runs, plus the vocabulary.
check: schema-check vocab-check

schema-check:
	linkml validate $(SCHEMA)
	linkml lint $(SCHEMA)
	$(PYTHON) ci.py $(SCHEMA)

# Validate vocab/ecoskos_terms.tsv and regenerate docs/ecoskos/ecoskos.ttl and index.html.
vocab:
	$(PYTHON) vocab/build_vocab.py

# Validate, and fail if the committed ttl/html do not match the TSV.
vocab-check:
	$(PYTHON) vocab/build_vocab.py --check

# Print the next unused ecoskos id, for adding a row.
vocab-next-id:
	$(PYTHON) vocab/build_vocab.py --next-id

# Counts by status, terms with no broader term, and proposed/requested terms
# older than DAYS days.
terms-report:
	$(PYTHON) vocab/terms_report.py --days $(DAYS)

# Print one term as a markdown ontology term request, ready to paste into a tracker.
term-request:
	$(if $(ID),,$(error ID is required: make term-request ID=ecoskos:0000001))
	$(PYTHON) vocab/term_request.py $(ID)
