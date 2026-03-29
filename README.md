# Causal Mosaic

A LinkML schema and annotation pipeline for representing ecological causal claims as an ontology-grounded graph. Combines ELMO-style entity decomposition with the Illari–Russo causal mosaic framework (CAMO), so the same curated claims can drive causal diagrams, evidence gap maps, fuzzy cognitive models, and practitioner summaries.

---

## Repository contents

| File / folder | Purpose |
|---|---|
| `causal_mosaic_v0.4.0.yaml` | Versioned LinkML schema |
| `sample_data.yaml` | Full worked example (grassland restoration) |
| `sample_data_grounded.yaml` | Compact ontology-grounded version of the same example |
| `causal_mosaic_annotation_guide.md` | Complete annotator handbook (includes LLM pipeline guidance in Appendix A) |
| `schema_cheat_sheet_one_page.md` | One-page quick reference |
| `schema_guide_ecologists.md` | Audience guide for ecologists |
| `schema_guide_philosophers.md` | Audience guide for philosophers |
| `schema_guide_plain_language.md` | Plain-language guide |
| `schema_guide_semantic_engineers.md` | Audience guide for semantic engineers |
| `sentence_to_schema_infographic.md` | Visual walkthrough of schema decomposition |
| `annotator/` | LLM annotation pipeline scripts |

---

## The schema in one sentence

A Causal Mosaic annotation is a **labeled property graph** where every **node** is a change in an ecological variable (entity + attribute + direction) and every **edge** is a causal claim carrying four annotation layers: claim strength, philosophical account, fifteen causal features, and evidential basis.

The five questions the schema answers for each claim:

1. **What changed?** — `entity_term`, `variable_attribute`
2. **Which way?** — `variable_direction`
3. **What did it affect?** — edge `subject` → `object`
4. **How strong is the claim?** — `claim_strength`, `philosophical_accounts`
5. **What evidence supports it?** — `evidential_basis`

---

## Annotation pipeline (`annotator/`)

The pipeline implements the human-in-the-loop workflow from Annotation Guide Appendix A. An LLM produces a first-pass draft; a trained human reviews and corrects every field.

```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  1. PREPARE  │──▶│  2. EXTRACT  │──▶│  3. VALIDATE │──▶│  4. REVIEW   │
│  Paper + DOI │   │  LLM draft   │   │  Schema,     │   │  Human check │
│  metadata    │   │  YAML output │   │  CURIEs,     │   │  + correct   │
└──────────────┘   └──────────────┘   │  Spans       │   └──────────────┘
     Human              LLM           └──────────────┘    Human (critical)
```

### Quick start

```bash
cd annotator
pip install -r requirements.txt

# 1. Configure the LLM (edit this file before running anything)
#    Defaults to openai_compatible pointing at a local vLLM instance.
nano llm.yaml

# 2. Set your API key (if required by your endpoint)
export LLM_API_KEY="your-key-here"   # or "none" for unauthenticated vLLM

# 3. Run the full pipeline
python pipeline.py --text paper.pdf --doi "10.xxxx/yyyy" --output-dir outputs/

# Or run steps individually:
python extract.py       --text paper.pdf --output draft.yaml
python validate_schema.py draft.yaml
python validate_curies.py draft.yaml --output curie_report.json
python verify_spans.py  draft.yaml paper.pdf
```

### Configuring the LLM — `llm.yaml`

All pipeline scripts read `annotator/llm.yaml` at startup. No model settings are hard-coded. Edit this file to point at any LLM endpoint.

**vLLM (default)**

```yaml
provider: openai_compatible
base_url: "http://localhost:8000/v1"
model: "meta-llama/Llama-3.3-70B-Instruct"
api_key_env: "LLM_API_KEY"
max_tokens: 8192
temperature: 0.1
```

Start vLLM with, e.g.:

```bash
vllm serve meta-llama/Llama-3.3-70B-Instruct --port 8000
export LLM_API_KEY="none"
```

**Ollama (local)**

```yaml
provider: openai_compatible
base_url: "http://localhost:11434/v1"
model: "llama3.3:70b"
api_key_env: "LLM_API_KEY"
```

```bash
ollama pull llama3.3:70b
export LLM_API_KEY="none"
```

**OpenAI**

```yaml
provider: openai_compatible
base_url: "https://api.openai.com/v1"
model: "gpt-4o"
api_key_env: "OPENAI_API_KEY"
```

**Together AI / Groq**

```yaml
provider: openai_compatible
base_url: "https://api.together.xyz/v1"   # or https://api.groq.com/openai/v1
model: "meta-llama/Llama-3.3-70B-Instruct-Turbo"
api_key_env: "TOGETHER_API_KEY"
```

**Anthropic Claude**

```yaml
provider: anthropic
model: "claude-sonnet-4-6"
max_tokens: 8192
temperature: 0.1
```

```bash
export ANTHROPIC_API_KEY="your-key"
pip install anthropic
```

### PDF support

All scripts that accept a source document (`extract.py`, `verify_spans.py`, `pipeline.py`) accept both `.txt`/`.md` and `.pdf` files. PDF text extraction requires one additional package:

```bash
pip install pdfplumber    # recommended
# or
pip install pymupdf
```

---

### Pipeline scripts reference

| Script | Purpose |
|---|---|
| `extract.py` | Call the LLM with the Appendix A.3 extraction prompt; write draft YAML |
| `validate_schema.py` | Check required fields, enum values, node references, FCM weight sign consistency |
| `validate_curies.py` | Validate every ontology CURIE against NCBI E-utilities and OLS4 |
| `lookup_curie.py` | Find the correct CURIE for a label when the LLM guessed wrong |
| `verify_spans.py` | Confirm every `source_spans.text` is a verbatim quote from the paper |
| `pipeline.py` | Run all stages in sequence with a single command |
| `llm.yaml` | LLM provider, endpoint, model, and generation settings |
| `utils.py` | Shared text loading (`.txt`/`.pdf`) and LLM client construction |

#### `extract.py`

```
python extract.py --text paper.pdf [options]

  --text PATH         Source document (.txt, .md, or .pdf)  [required]
  --output PATH       Draft YAML output  [default: draft.yaml]
  --config PATH       llm.yaml path  [default: annotator/llm.yaml]
  --doi TEXT          DOI of the paper
  --title TEXT        Paper title
  --authors TEXT      Author name (repeat for multiple)
  --year INT          Publication year
  --journal TEXT      Journal name
  --chunk             Split into ~3000-word chunks (for long papers)
  --words-per-chunk   Words per chunk  [default: 3000]
```

#### `validate_schema.py`

```
python validate_schema.py draft.yaml [--strict]
```

Exits 0 if no errors; 1 if errors found. `--strict` treats warnings as errors.

#### `validate_curies.py`

```
python validate_curies.py draft.yaml [--output report.json] [--dry-run] [--verbose]
```

Set `NCBI_API_KEY` to raise the NCBI rate limit from 3 to 10 requests/second.

#### `lookup_curie.py`

```
# Single lookup
python lookup_curie.py "Andropogon gerardii" NCBITaxon
python lookup_curie.py "temperate grassland" ENVO

# Batch (TSV: label<TAB>prefix)
python lookup_curie.py --batch labels.tsv --output results.tsv
```

#### `verify_spans.py`

```
python verify_spans.py draft.yaml paper.pdf [options]

  --threshold FLOAT   Fuzzy similarity cutoff  [default: 0.90]
  --fix               Auto-correct near-matches in the YAML
  --output PATH       Write JSON report to file
  --show-diff         Print diff for near-matches
```

#### `pipeline.py`

```
python pipeline.py --text paper.pdf [options]

  --text PATH         Source document  [required unless --no-extract]
  --draft PATH        Existing draft YAML (use with --no-extract)
  --output-dir DIR    Directory for all outputs  [default: .]
  --config PATH       llm.yaml path
  --doi / --title / --authors / --year / --journal
                      Paper metadata passed to extract.py
  --no-extract        Skip extraction; validate an existing draft
  --skip-curies       Skip CURIE API validation (useful offline)
  --skip-spans        Skip source span verification
  --fix-spans         Auto-correct near-match spans
  --strict            Treat schema warnings as errors
  --chunk             Enable chunked extraction
```

---

## Human review checklist

After every LLM extraction, a human annotator must verify (from Annotation Guide §A.2.4):

- [ ] Source spans are verbatim quotes (use `verify_spans.py`, then Ctrl+F)
- [ ] Every ontology CURIE is correct (use `validate_curies.py` + ontology browser)
- [ ] Claim strength matches the author's actual language, not the LLM's interpretation
- [ ] Philosophical accounts match the text framing (check linguistic cues in §8.2)
- [ ] All fifteen causal features are grounded in the text (`not_addressed` by default)
- [ ] `russo_williamson_satisfied: true` only if the paper itself provides both statistical and mechanistic evidence
- [ ] `bradford_hill_count` equals the length of `bradford_hill_viewpoints`
- [ ] FCM weight sign matches the predicate sign
- [ ] No hallucinated edges — every edge traces to a specific passage in the paper
- [ ] Competing or offsetting effects are captured (check the Discussion section)

---

## What goes in?

- Ecological causal claims extracted from papers, reports, or synthesis products
- Ontology terms from CAMO, ELMO, ENVO, GO, PATO, NCBITaxon, ECO, and related vocabularies
- Source-document provenance: quoted spans, study metadata, annotator judgments

## What comes out?

- Versioned, validated YAML records conforming to `causal_mosaic_v0.4.0.yaml`
- Causal graphs suitable for Fuzzy Cognitive Maps, Evidence Gap Maps, and RAG pipelines
- Structured evidence for practitioner summaries and systematic reviews

---

## Open questions

- Which node categories should be grounded directly to stable external ontology terms rather than local placeholders?
- How strict should validation be for partially grounded claims when no exact ontology term exists?
- Should the project maintain one canonical sample dataset or both a compact grounded sample and a fuller narrative sample?
- What downstream renderers should be treated as first-class targets in the next iteration?
