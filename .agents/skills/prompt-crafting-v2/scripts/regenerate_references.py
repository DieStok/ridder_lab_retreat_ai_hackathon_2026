#!/usr/bin/env python3
"""
regenerate_references.py
========================

Refetch the official prompt-engineering documentation pages from Anthropic and
OpenAI and rewrite the cached reference files in ../references/.

Usage
-----
    python scripts/regenerate_references.py             # write/rewrite all files
    python scripts/regenerate_references.py --dry-run   # show diff stats only
    python scripts/regenerate_references.py --check     # CI: exit 1 if drift
    python scripts/regenerate_references.py --only ID   # only one stitched section

Design goals
------------
- **Idempotent**: same input HTML/markdown -> byte-identical output (modulo
  the fetch date in the header).
- **Robust to format drift**: when the source HTML structure shifts, the
  extractor still produces something useful; if extraction completely fails,
  the script falls back to the raw text so the user can inspect the diff.
- **Reproducible audit trail**: every output carries the source URLs, fetch
  date, and SHA-256 of the fetched body so drift can be detected later.

Dependencies
------------
- requests          — HTTP client
- pyyaml            — read sources.yaml
- beautifulsoup4    — HTML structure for extraction
- markdownify       — HTML -> Markdown conversion

Install with:
    pip install requests pyyaml beautifulsoup4 markdownify
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import re
import sys
import textwrap
from pathlib import Path
from typing import Any

# Defer optional imports so --check / --dry-run still print useful errors
# when dependencies are missing.
try:
    import requests
    import yaml
    from bs4 import BeautifulSoup, Tag
    from markdownify import markdownify as _md
except ImportError as exc:  # pragma: no cover
    sys.stderr.write(
        "Missing dependency: {}\n"
        "Install with: pip install requests pyyaml beautifulsoup4 markdownify\n"
        .format(exc.name)
    )
    sys.exit(2)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REFERENCES_DIR = SKILL_ROOT / "references"
SOURCES_YAML = SCRIPT_DIR / "sources.yaml"

USER_AGENT = (
    "prompt-crafting-v2-skill-regenerator/1.0 "
    "(+https://github.com/anthropics/skills) "
    "python-requests/{ver}"
).format(ver=requests.__version__)
REQUEST_TIMEOUT_SECONDS = 30
REQUEST_RETRIES = 3
REQUEST_BACKOFF_SECONDS = 2.0


# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------

def fetch(url: str) -> tuple[str, str]:
    """Fetch a URL and return (raw_body, sha256-hex).

    Retries on transient failures with linear backoff. Sets a polite
    User-Agent. Raises requests.HTTPError on a non-2xx final response.
    """
    last_exc: Exception | None = None
    for attempt in range(1, REQUEST_RETRIES + 1):
        try:
            resp = requests.get(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "text/html,text/markdown,text/plain,*/*;q=0.8",
                },
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            resp.raise_for_status()
        except requests.RequestException as exc:
            last_exc = exc
            if attempt < REQUEST_RETRIES:
                import time
                time.sleep(REQUEST_BACKOFF_SECONDS * attempt)
                continue
            raise
        body = resp.text
        digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
        return body, digest
    # Defensive — should never reach here.
    raise last_exc if last_exc else RuntimeError("fetch failed without exception")


# ---------------------------------------------------------------------------
# Content extraction
# ---------------------------------------------------------------------------

# Anthropic publishes its docs as raw .md, so HTML extraction isn't needed
# when content_type=='markdown'. The body comes through unchanged.

def extract_markdown(html: str, *, extract_markers: list[str] | None = None,
                     section_only: str | None = None) -> str:
    """Convert an OpenAI documentation HTML page to Markdown.

    The OpenAI doc HTML wraps the article body in an `<article>` (or
    sometimes `<main>`) element surrounded by extensive nav/sidebar chrome.
    We:
      1. Try to isolate the `<article>`/`<main>` element.
      2. Strip nav, footer, and aside elements that may live inside it.
      3. Convert what remains to Markdown.
      4. (Optional) when `section_only` is set, find the matching tab
         heading (e.g. "## GPT-5.5 prompting guide") and slice from there
         to the next sibling tab heading.

    `extract_markers` is a list of substrings; if any is found in the result,
    we trust the extraction and return it. Otherwise we fall back to a
    full-page conversion so the caller can still diff against the previous
    cache.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Drop chrome elements that often live inside the main region too.
    for selector in ("nav", "header", "footer", "aside",
                     "[role=navigation]", "[role=banner]"):
        for el in soup.select(selector):
            el.decompose()

    # Try to find the article body.
    main: Tag | None = (
        soup.find("article")
        or soup.find("main")
        or soup.find(attrs={"role": "main"})
    )

    container: Tag = main if isinstance(main, Tag) else soup

    md = _md(str(container), heading_style="ATX", strip=("script", "style"))
    md = _normalize_whitespace(md)

    # If markers are provided and none are present, fall back to converting
    # the entire page. This protects against silent misses when the article
    # selector changes.
    if extract_markers and not any(m in md for m in extract_markers):
        full_md = _md(str(soup), heading_style="ATX", strip=("script", "style"))
        full_md = _normalize_whitespace(full_md)
        # Only use the fallback if it actually contains a marker.
        if any(m in full_md for m in extract_markers):
            md = full_md

    # Optional: slice to a single tab section.
    if section_only:
        md = _slice_section(md, section_only)

    return md


def _normalize_whitespace(text: str) -> str:
    """Collapse triple+ blank lines, strip trailing whitespace per line."""
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


# Map sources.yaml `section_only` values to the H2 heading that opens
# each tab on the OpenAI prompt-guidance page.
SECTION_HEADING_FOR = {
    "gpt-5.5":      r"##\s+GPT-?5\.5\s+prompting\s+guide",
    "gpt-5.4":      r"##\s+GPT-?5\.4\s+prompting\s+guide",
    "gpt-5.3-codex": r"##\s+GPT-?5\.3\s+Codex\s+prompting\s+guide",
}

def _slice_section(md: str, section_id: str) -> str:
    """Slice the markdown to a single tab section.

    Looks for the matching heading and returns from that heading to the next
    sibling-level heading that opens a different tab. Falls back to returning
    the whole markdown if the heading can't be found.
    """
    pattern = SECTION_HEADING_FOR.get(section_id)
    if not pattern:
        return md
    start_match = re.search(pattern, md, flags=re.IGNORECASE)
    if not start_match:
        return md  # fall back to full extract
    start = start_match.start()

    # Find the next "## <other model> prompting guide" heading.
    end = len(md)
    for other_id, other_pattern in SECTION_HEADING_FOR.items():
        if other_id == section_id:
            continue
        m = re.search(other_pattern, md[start_match.end():], flags=re.IGNORECASE)
        if m:
            candidate_end = start_match.end() + m.start()
            if candidate_end < end:
                end = candidate_end

    return md[start:end].strip() + "\n"


# ---------------------------------------------------------------------------
# Writing reference files
# ---------------------------------------------------------------------------

def _make_attribution_header(
    *,
    output_filename: str,
    applies_to: str,
    fetch_date: str,
    sources: list[dict[str, Any]],
) -> str:
    """Return the HTML-comment block that opens every reference file."""
    src_lines: list[str] = []
    for src in sources:
        url = src["url"]
        digest = src.get("sha256", "?")
        src_lines.append(f"  - {url}  (sha256: {digest[:16]}…)")
    src_block = "\n".join(src_lines)
    body = textwrap.dedent(f"""\
        <!--
        ================================================================================
        CACHED REFERENCE FILE - DO NOT EDIT BY HAND

        Sources:
        {src_block}

        Fetched:       {fetch_date}
        Applies to:    {applies_to}
        Regenerated by: scripts/regenerate_references.py

        This file is a verbatim cache of the source pages above, kept inside the
        prompt-crafting-v2 skill so the LLM has a stable reference even when offline
        and so the user can diff against the live page when it changes. Do NOT edit
        this file by hand. To refresh, re-run the regenerator script.
        ================================================================================
        -->
    """)
    return body


def regenerate_single(spec: dict[str, Any], fetch_date: str) -> str:
    """Build the full content for a single-source output (e.g., Claude doc)."""
    src = spec["single_source"]
    body, digest = fetch(src["url"])
    if src.get("content_type") == "markdown":
        content = body
    else:
        content = extract_markdown(
            body,
            extract_markers=src.get("extract_markers"),
        )
    header = _make_attribution_header(
        output_filename=spec["output"],
        applies_to=spec["applies_to"],
        fetch_date=fetch_date,
        sources=[{"url": src["url"], "sha256": digest}],
    )
    # Anthropic markdown already starts with "# Prompting best practices" —
    # don't add a redundant title.
    return header + "\n" + content.lstrip()


def regenerate_stitched(spec: dict[str, Any], fetch_date: str,
                        only: str | None = None) -> str:
    """Build a stitched output (e.g., the OpenAI combined ref).

    The output structure is:
        <attribution-header>
        # <output title>
        ## How to use this file (routing preamble) -- generated
        # §1. <first section title>
        ...source content...
        ---
        # §2. <next section title>
        ...
    """
    sources_meta: list[dict[str, Any]] = []
    sections_md: list[str] = []

    for src in spec["stitched_sources"]:
        if only and src["id"] != only:
            continue
        body, digest = fetch(src["url"])
        sources_meta.append({"url": src["url"], "sha256": digest})
        if src.get("content_type") == "markdown":
            extracted = body
        else:
            extracted = extract_markdown(
                body,
                extract_markers=src.get("extract_markers"),
                section_only=src.get("section_only"),
            )
        section_block = (
            f"# {src['title']}\n\n"
            f"> **Source:** {src['url']}\n\n"
            f"{extracted.strip()}\n"
        )
        sections_md.append(section_block)

    title = spec.get("title", "OpenAI / ChatGPT / Codex prompting best practices — combined reference")
    routing_preamble = _build_openai_routing_preamble(spec)

    header = _make_attribution_header(
        output_filename=spec["output"],
        applies_to=spec["applies_to"],
        fetch_date=fetch_date,
        sources=sources_meta,
    )

    return (
        header
        + "\n"
        + f"# {title}\n\n"
        + routing_preamble
        + "\n\n---\n\n"
        + "\n\n---\n\n".join(sections_md)
        + "\n\n## End of cached reference\n\n"
        "To refresh: run `python scripts/regenerate_references.py` from the skill root.\n"
    )


def _build_openai_routing_preamble(spec: dict[str, Any]) -> str:
    """Return the static routing preamble for the OpenAI combined ref.

    This is generated rather than fetched, since it's our own scaffolding
    explaining how the stitched sections relate.
    """
    return textwrap.dedent("""\
        ## How to use this file (routing preamble)

        This document combines five OpenAI prompting guides into one reference. Use the table below to jump to the right section based on **which model the prompt is for**:

        | If the target model is… | Use section… | Source URL |
        |---|---|---|
        | **GPT-5.5** (and any future "latest" mainline model) | §2 GPT-5.5 prompting guide | `prompt-guidance?model=gpt-5.5` |
        | **GPT-5.4**, `gpt-5.4-mini`, `gpt-5.4-nano` | §3 GPT-5.4 prompting guide | `prompt-guidance?model=gpt-5.4` |
        | **GPT-5.3-codex** (agentic coding model used by Codex CLI / Codex API) | §4 GPT-5.3 Codex prompting guide | `prompt-guidance?model=gpt-5.3-codex` |
        | **Any OpenAI model**, or for cross-model foundational guidance | §1 General prompt engineering | `guides/prompt-engineering` |
        | **Migration / API-level concerns when moving onto GPT-5.5** | §5 Using GPT-5.5 (supplementary) | `guides/latest-model` |

        **Rules of thumb when routing inside this file:**

        1. Always start with §1 for the absolute basics (message roles, Markdown+XML formatting, few-shot, context windows).
        2. For any model in the GPT-5.x family, also read the matching model-specific section (§2/§3/§4).
        3. The **GPT-5.5** guide deliberately advises **shorter, outcome-first** prompts than the older GPT-5.x stacks — do not blindly carry over GPT-5.4 prompt blocks into a GPT-5.5 system prompt.
        4. The **GPT-5.3-codex** guide is opinionated about *removing* upfront-plan / preamble prompting that helps GPT-5-series models — Codex rollouts can stop early if you keep them.
        5. When in doubt about an exact API parameter or capability, refer back to the source URL — the live page is canonical and may have been updated since this cache was generated.
    """).strip()


# ---------------------------------------------------------------------------
# Diff helpers
# ---------------------------------------------------------------------------

def _normalize_for_diff(text: str) -> str:
    """Strip the parts of a reference file that always change between runs.

    Specifically: the attribution header (which contains the fetch date and
    sha256). What remains is the substantive content — useful to compare
    runs and to power --check.
    """
    return re.sub(
        r"<!--\s*=+\s*CACHED REFERENCE FILE.*?=+\s*-->\s*",
        "",
        text,
        count=1,
        flags=re.DOTALL,
    ).strip()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change but do not write files.")
    parser.add_argument("--check", action="store_true",
                        help="CI mode: regenerate, compare against on-disk file, "
                             "exit 1 if substantive content differs. Does not write.")
    parser.add_argument("--only", metavar="ID",
                        help="Only regenerate one stitched section by id "
                             "(see sources.yaml). Does not affect single-source outputs.")
    parser.add_argument("--sources", default=str(SOURCES_YAML),
                        help="Path to sources.yaml (default: %(default)s)")
    args = parser.parse_args(argv)

    if args.dry_run and args.check:
        parser.error("--dry-run and --check are mutually exclusive")

    sources_path = Path(args.sources)
    if not sources_path.exists():
        sys.stderr.write(f"sources.yaml not found at {sources_path}\n")
        return 2

    with open(sources_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    fetch_date = _dt.date.today().isoformat()
    REFERENCES_DIR.mkdir(parents=True, exist_ok=True)

    drift_detected = False

    for spec in config["outputs"]:
        out_path = REFERENCES_DIR / spec["output"]
        print(f"=> {spec['output']}")

        try:
            if "single_source" in spec:
                content = regenerate_single(spec, fetch_date)
            elif "stitched_sources" in spec:
                content = regenerate_stitched(spec, fetch_date, only=args.only)
            else:
                sys.stderr.write(
                    f"  ERROR: spec for {spec['output']} has neither "
                    "`single_source` nor `stitched_sources`.\n"
                )
                drift_detected = True
                continue
        except Exception as exc:
            sys.stderr.write(f"  ERROR while regenerating: {exc}\n")
            drift_detected = True
            continue

        if args.dry_run:
            existing = out_path.read_text(encoding="utf-8") if out_path.exists() else ""
            new_norm = _normalize_for_diff(content)
            old_norm = _normalize_for_diff(existing)
            if new_norm != old_norm:
                print(f"   would change (substantive): "
                      f"{len(old_norm)} -> {len(new_norm)} chars")
            else:
                print("   no substantive change")
            continue

        if args.check:
            if not out_path.exists():
                print("   MISSING (would be created)")
                drift_detected = True
                continue
            existing = out_path.read_text(encoding="utf-8")
            if _normalize_for_diff(existing) != _normalize_for_diff(content):
                print("   DRIFT (substantive content differs from live source)")
                drift_detected = True
            else:
                print("   ok")
            continue

        # Default: write.
        out_path.write_text(content, encoding="utf-8")
        print(f"   wrote {out_path.relative_to(SKILL_ROOT)}  ({len(content)} chars)")

    if drift_detected:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
