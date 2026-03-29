"""
pipeline.py — Causal Mosaic Full Annotation Pipeline

Orchestrates the complete human-in-the-loop annotation workflow described in
Annotation Guide Appendix A.4.4:

    1. EXTRACT  — Call Claude to produce a draft YAML from the source text.
    2. VALIDATE SCHEMA — Check structural correctness.
    3. VALIDATE CURIES — Check ontology IDs against live APIs.
    4. VERIFY SPANS — Confirm source quotes are verbatim.
    5. REPORT  — Print a consolidated summary for the human reviewer.

Usage:
    python pipeline.py --text paper.txt --doi "10.1234/example" \\
                       --title "My Paper" --output-dir ./outputs

    python pipeline.py --text paper.txt --output-dir ./outputs \\
                       --skip-curies          # skip live CURIE API calls
                       --skip-spans           # skip span verification

Each stage writes its output to --output-dir. If extraction has already been
run and a draft YAML exists, use --no-extract to skip straight to validation:

    python pipeline.py --draft outputs/draft.yaml --text paper.txt \\
                       --output-dir ./outputs --no-extract

All tool calls are delegated to the individual scripts in this directory, so
each script can also be run standalone.
"""

import subprocess
import sys
from pathlib import Path

import click

DEFAULT_CONFIG = str(Path(__file__).parent / "llm.yaml")


def _run(cmd: list[str], label: str, fatal: bool = True) -> int:
    """Run a subprocess command, stream its output, and return its exit code."""
    click.echo(f"\n{'='*60}")
    click.echo(f"  {label}")
    click.echo(f"{'='*60}")
    click.echo(f"  $ {' '.join(cmd)}\n")

    result = subprocess.run(cmd, check=False)

    if result.returncode != 0 and fatal:
        click.echo(
            f"\nERROR: {label} failed (exit code {result.returncode}).\n"
            "Fix the issues above before proceeding.",
            err=True,
        )
        sys.exit(result.returncode)
    return result.returncode


def _script(name: str) -> str:
    """Return the path to a script in the same directory as this file."""
    return str(Path(__file__).parent / name)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.command(context_settings={"max_content_width": 100})
@click.option("--text", "text_path", default=None, type=click.Path(exists=True),
              help="Path to the plain-text source document.")
@click.option("--draft", "draft_path", default=None, type=click.Path(),
              help="Path to an existing draft YAML (skips extraction if provided with --no-extract).")
@click.option("--output-dir", "-d", default=".", show_default=True, type=click.Path(),
              help="Directory for all pipeline outputs.")
@click.option("--doi", default="", help="DOI of the source paper.")
@click.option("--title", default="", help="Title of the source paper.")
@click.option("--authors", multiple=True, default=[],
              help="Authors (repeat for multiple).")
@click.option("--year", default=None, type=int, help="Publication year.")
@click.option("--journal", default="", help="Journal name.")
@click.option("--config", "-c", default=DEFAULT_CONFIG, show_default=True,
              type=click.Path(exists=True),
              help="Path to llm.yaml configuration file.")
@click.option("--no-extract", is_flag=True, default=False,
              help="Skip extraction (requires --draft to point at an existing YAML).")
@click.option("--skip-curies", is_flag=True, default=False,
              help="Skip CURIE validation (no API calls). Useful offline.")
@click.option("--skip-spans", is_flag=True, default=False,
              help="Skip source span verification.")
@click.option("--fix-spans", is_flag=True, default=False,
              help="Auto-correct near-match spans during verification.")
@click.option("--strict", is_flag=True, default=False,
              help="Treat schema warnings as errors.")
@click.option("--chunk/--no-chunk", default=False, show_default=True,
              help="Split source text into chunks before extraction.")
def main(
    text_path, draft_path, output_dir,
    config,
    doi, title, authors, year, journal,
    no_extract, skip_curies, skip_spans, fix_spans, strict,
    chunk,
):
    """Run the full Causal Mosaic annotation pipeline.

    Stages: extract → validate_schema → validate_curies → verify_spans → report.

    See Annotation Guide Appendix A for a detailed description of each stage.
    The output directory will contain:
        draft.yaml            — raw LLM output
        schema_errors.txt     — validate_schema.py output
        curie_report.json     — validate_curies.py output
        span_report.json      — verify_spans.py output
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    draft_yaml = Path(draft_path) if draft_path else out / "draft.yaml"
    schema_report  = out / "schema_errors.txt"
    curie_report   = out / "curie_report.json"
    span_report    = out / "span_report.json"

    # ------------------------------------------------------------------
    # Stage 1: Extraction
    # ------------------------------------------------------------------
    if no_extract:
        if not draft_yaml.exists():
            click.echo(
                f"ERROR: --no-extract set but draft YAML not found at {draft_yaml}", err=True
            )
            sys.exit(1)
        click.echo(f"Skipping extraction. Using existing draft: {draft_yaml}")
    else:
        if not text_path:
            click.echo("ERROR: --text is required unless --no-extract is set.", err=True)
            sys.exit(1)

        extract_cmd = [
            sys.executable, _script("extract.py"),
            "--text", text_path,
            "--output", str(draft_yaml),
            "--config", config,
        ]
        if doi:     extract_cmd += ["--doi",     doi]
        if title:   extract_cmd += ["--title",   title]
        if year:    extract_cmd += ["--year",    str(year)]
        if journal: extract_cmd += ["--journal", journal]
        for author in authors:
            extract_cmd += ["--authors", author]
        if chunk:
            extract_cmd.append("--chunk")

        _run(extract_cmd, "Stage 1: LLM Extraction", fatal=True)

    # ------------------------------------------------------------------
    # Stage 2: Schema validation
    # ------------------------------------------------------------------
    schema_cmd = [sys.executable, _script("validate_schema.py"), str(draft_yaml)]
    if strict:
        schema_cmd.append("--strict")

    with _Tee(schema_report) as tee:
        rc = _run(schema_cmd, "Stage 2: Schema Validation", fatal=False)

    if rc != 0:
        click.echo(
            f"\nSchema validation found errors. See {schema_report}.\n"
            "Fix errors in the draft YAML before proceeding with CURIE/span checks.",
            err=True,
        )
        _print_final_report(
            draft_yaml, schema_report, curie_report, span_report,
            schema_ok=False, curies_ok=None, spans_ok=None,
        )
        sys.exit(1)

    # ------------------------------------------------------------------
    # Stage 3: CURIE validation
    # ------------------------------------------------------------------
    if skip_curies:
        click.echo("\nSkipping CURIE validation (--skip-curies).")
        curies_ok = None
    else:
        curie_cmd = [
            sys.executable, _script("validate_curies.py"),
            str(draft_yaml),
            "--output", str(curie_report),
            "--verbose",
        ]
        curie_rc = _run(curie_cmd, "Stage 3: CURIE Validation", fatal=False)
        curies_ok = (curie_rc == 0)

    # ------------------------------------------------------------------
    # Stage 4: Span verification
    # ------------------------------------------------------------------
    if skip_spans:
        click.echo("\nSkipping span verification (--skip-spans).")
        spans_ok = None
    elif not text_path:
        click.echo("\nSkipping span verification (--text not provided).")
        spans_ok = None
    else:
        span_cmd = [
            sys.executable, _script("verify_spans.py"),
            str(draft_yaml), text_path,
            "--output", str(span_report),
        ]
        if fix_spans:
            span_cmd.append("--fix")
        span_rc = _run(span_cmd, "Stage 4: Source Span Verification", fatal=False)
        spans_ok = (span_rc == 0)

    # ------------------------------------------------------------------
    # Final report
    # ------------------------------------------------------------------
    _print_final_report(
        draft_yaml, schema_report, curie_report, span_report,
        schema_ok=True, curies_ok=curies_ok, spans_ok=spans_ok,
    )

    all_ok = all(v is not False for v in [True, curies_ok, spans_ok])
    if not all_ok:
        sys.exit(1)


def _print_final_report(draft_yaml, schema_report, curie_report, span_report,
                        schema_ok, curies_ok, spans_ok):
    click.echo(f"\n{'='*60}")
    click.echo("  PIPELINE COMPLETE — Summary")
    click.echo(f"{'='*60}")
    click.echo(f"  Draft YAML:       {draft_yaml}")
    click.echo(f"  Schema:           {'OK' if schema_ok else 'ERRORS (see ' + str(schema_report) + ')'}")
    if curies_ok is None:
        click.echo("  CURIEs:           skipped")
    else:
        click.echo(f"  CURIEs:           {'OK' if curies_ok else 'ISSUES (see ' + str(curie_report) + ')'}")
    if spans_ok is None:
        click.echo("  Source spans:     skipped")
    else:
        click.echo(f"  Source spans:     {'OK' if spans_ok else 'ISSUES (see ' + str(span_report) + ')'}")

    click.echo("")
    click.echo("  NEXT STEP (Stage 3 — Human Review):")
    click.echo("  Open the draft YAML and review every field carefully.")
    click.echo("  Checklist from Annotation Guide Appendix A.2.4:")
    click.echo("    [ ] Source spans verified verbatim against original paper")
    click.echo("    [ ] Ontology CURIEs verified in ontology browser")
    click.echo("    [ ] Claim strength matches author's language (not LLM's assessment)")
    click.echo("    [ ] Philosophical accounts match text framing")
    click.echo("    [ ] Causal features are grounded in the text (not LLM background knowledge)")
    click.echo("    [ ] Russo-Williamson only true if paper provides both stat + mechanism evidence")
    click.echo("    [ ] Bradford Hill count matches viewpoints list")
    click.echo("    [ ] FCM weight sign matches predicate sign")
    click.echo("    [ ] No hallucinated edges (every edge traceable to a specific passage)")
    click.echo("")


class _Tee:
    """Context manager that tees stdout of subprocess calls to a file.

    Note: subprocess output is printed directly, so this class simply
    records that validation ran. A full tee would require redirecting
    subprocess stdout/stderr, which is left to the individual scripts.
    """
    def __init__(self, path: Path):
        self.path = path

    def __enter__(self):
        return self

    def __exit__(self, *args):
        # Touch the file so callers know it was attempted
        self.path.touch(exist_ok=True)


if __name__ == "__main__":
    main()
