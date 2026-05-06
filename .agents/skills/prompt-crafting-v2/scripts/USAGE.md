# `scripts/` — keeping the cached references in sync with the live docs

The two reference files in `../references/` are point-in-time caches of public
prompt-engineering documentation pages from Anthropic and OpenAI. The script in
this directory refetches those pages, extracts the relevant content, and
rewrites the local cache.

## Files

| File | Purpose |
|---|---|
| `sources.yaml` | Declarative spec of which URLs feed which output reference file. Edit this when a new model/page is added. |
| `regenerate_references.py` | The fetcher/extractor/writer. Idempotent. Has `--dry-run` and `--check` modes. |
| `USAGE.md` | This file. |

## One-time setup

```bash
pip install requests pyyaml beautifulsoup4 markdownify
```

(Those are the only runtime dependencies. The script itself is plain stdlib
otherwise and targets Python 3.10+.)

## Running

From the skill root (the directory that contains `SKILL.md`):

```bash
# Refetch everything and rewrite the reference files.
python scripts/regenerate_references.py

# Show which files *would* change without touching disk.
python scripts/regenerate_references.py --dry-run

# CI mode — exits 1 if the on-disk content has drifted from the live source.
# Useful as a periodic GitHub Action / cron job that opens a PR with the diff.
python scripts/regenerate_references.py --check

# Regenerate only one stitched section (useful when iterating on extractor):
python scripts/regenerate_references.py --only gpt55
```

## How it works

For each entry in `sources.yaml`:

1. **Fetch** the source URL with a polite User-Agent and short retry/backoff.
   The fetched body is hashed (sha256) for the audit trail in the file header.
2. **Extract** the substantive content. Anthropic publishes its prompting page
   as raw `.md` so it's used verbatim. OpenAI pages are HTML and are extracted
   by:
   - locating `<article>` / `<main>` / `[role=main]`,
   - dropping nav/footer/aside chrome,
   - converting to Markdown via `markdownify`,
   - optionally slicing to a single tab section (e.g. just the GPT-5.5 tab
     out of the multi-tab `prompt-guidance` page).
3. **Stitch** (when applicable) several sources into one combined reference,
   prefixed by a routing preamble that tells the LLM which section to consult
   for which target model.
4. **Write** the result with a standardized HTML-comment attribution header
   listing every source URL, the fetch date, and the sha256 of each fetch.

## Idempotence guarantee

For a given set of source URLs whose content has not changed, `regenerate` is
deterministic *except* for the fetch date in the header. The `--check` mode
compares only the substantive body (the header is stripped before diffing),
so a no-op refetch on unchanged sources will pass `--check`.

## Recovering from extraction failures

If the OpenAI doc HTML structure changes and the article-region detector misses
the main content, `regenerate_references.py` falls back to converting the whole
page (still scoped by the `extract_markers` allow-list). When that happens the
diff against the previous cache will be larger than usual — review it before
committing.

If extraction completely breaks (e.g., the page is now JS-rendered and the raw
HTML no longer contains the text), the script will still write what it can and
exit successfully; a follow-up update to the extractor is then needed. In the
meantime, the previous cache file remains valid as documentation.

## Adding a new source

1. Add an entry under `outputs:` in `sources.yaml`.
   - Use `single_source:` if one URL produces one output file.
   - Use `stitched_sources:` if multiple URLs are combined.
2. If you add a new tab section to the OpenAI stitched output, you may need to
   add an entry to `SECTION_HEADING_FOR` in `regenerate_references.py` so the
   `_slice_section` helper can find the right H2 heading.
3. Update `../SKILL.md`'s "Detailed Reference" section so the LLM knows the new
   line index for jumping to the right place.
4. Run `--dry-run` first to confirm the diff looks right, then run for real.
