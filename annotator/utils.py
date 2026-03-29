"""
utils.py — Shared utilities for the Causal Mosaic annotation pipeline.
"""

import sys
from pathlib import Path


def load_text(path: str) -> str:
    """Load plain text from a .txt/.md file or extract text from a PDF.

    For PDFs, tries pdfplumber first, then pymupdf (fitz). If neither is
    installed, prints an install hint and exits.
    """
    p = Path(path)
    if p.suffix.lower() == ".pdf":
        return _extract_pdf(path)
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _extract_pdf(path: str) -> str:
    """Extract full text from a PDF. Tries pdfplumber, then pymupdf."""
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            pages = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
        return "\n".join(pages)
    except ImportError:
        pass

    try:
        import fitz  # pymupdf
        doc = fitz.open(path)
        pages = [page.get_text() for page in doc]
        doc.close()
        return "\n".join(pages)
    except ImportError:
        pass

    print(
        "ERROR: PDF input requires pdfplumber or pymupdf.\n"
        "  pip install pdfplumber\n"
        "  or\n"
        "  pip install pymupdf",
        file=sys.stderr,
    )
    sys.exit(1)


def load_llm_config(config_path: str) -> dict:
    """Load and validate an llm.yaml config file.

    Returns a dict with at minimum the keys:
        provider, model, max_tokens, temperature
    """
    import yaml

    with open(config_path, encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh) or {}

    # Apply defaults
    cfg.setdefault("provider", "openai_compatible")
    cfg.setdefault("base_url", "http://localhost:8000/v1")
    cfg.setdefault("model", "meta-llama/Llama-3.3-70B-Instruct")
    cfg.setdefault("api_key_env", "LLM_API_KEY")
    cfg.setdefault("max_tokens", 8192)
    cfg.setdefault("temperature", 0.1)

    provider = cfg["provider"]
    if provider not in ("anthropic", "openai_compatible"):
        print(
            f"ERROR: llm.yaml provider must be 'anthropic' or 'openai_compatible', "
            f"got {provider!r}",
            file=sys.stderr,
        )
        sys.exit(1)

    return cfg


def make_llm_client(cfg: dict):
    """Return (provider_name, client) based on the llm.yaml config."""
    import os

    provider = cfg["provider"]

    if provider == "anthropic":
        try:
            import anthropic
        except ImportError:
            print("ERROR: anthropic package not installed. Run: pip install anthropic", file=sys.stderr)
            sys.exit(1)
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            print(
                "ERROR: ANTHROPIC_API_KEY environment variable is not set.",
                file=sys.stderr,
            )
            sys.exit(1)
        return "anthropic", anthropic.Anthropic(api_key=api_key)

    else:  # openai_compatible
        try:
            from openai import OpenAI
        except ImportError:
            print("ERROR: openai package not installed. Run: pip install openai", file=sys.stderr)
            sys.exit(1)
        api_key_env = cfg.get("api_key_env", "LLM_API_KEY")
        api_key = os.environ.get(api_key_env, "none")
        base_url = cfg["base_url"]
        return "openai_compatible", OpenAI(base_url=base_url, api_key=api_key)


def call_llm(provider: str, client, cfg: dict,
             system_prompt: str, user_prompt: str) -> str:
    """Send a prompt to the configured LLM and return the response text."""
    model      = cfg["model"]
    max_tokens = int(cfg.get("max_tokens", 8192))
    temperature = float(cfg.get("temperature", 0.1))

    if provider == "anthropic":
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return message.content[0].text

    else:  # openai_compatible
        response = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content
