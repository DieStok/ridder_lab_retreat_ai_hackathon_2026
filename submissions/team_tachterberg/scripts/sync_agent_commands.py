#!/usr/bin/env python3
"""Transpile the canonical Claude Code commands into every major agent's format.

Single source of truth: ``.claude/commands/*.md`` (the slash commands you edit).
Run this script to (re)generate the equivalent invokable command for each other
coding agent. Nothing here installs packages — it is Python standard library only.

    python3 scripts/sync_agent_commands.py          # regenerate everything
    python3 scripts/sync_agent_commands.py --check   # fail if anything is stale

Inspired by the multi-agent layout of github.com/JuliusBrussee/caveman and the
convert.sh idea from github.com/alirezarezvani/claude-skills, but adapted for
*invokable commands* (not always-on rules) so /onboard never fires unprompted.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / ".claude" / "commands"

BANNER_MD = (
    "<!-- GENERATED from {src} by scripts/sync_agent_commands.py. "
    "Edit the source, then re-run the script. -->\n\n"
)
BANNER_TOML = (
    "# GENERATED from {src} by scripts/sync_agent_commands.py.\n"
    "# Edit the source, then re-run the script.\n\n"
)


def parse_command(path: Path) -> tuple[str, str]:
    """Return (description, body) from a Claude command file with YAML frontmatter."""
    text = path.read_text(encoding="utf-8")
    description = ""
    body = text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            frontmatter = text[3:end]
            body = text[end + 4 :].lstrip("\n")
            for line in frontmatter.splitlines():
                if line.strip().lower().startswith("description:"):
                    description = line.split(":", 1)[1].strip().strip("\"'")
    return description, body.rstrip() + "\n"


def yaml_frontmatter_md(src_rel: str, description: str, body: str) -> str:
    # Frontmatter MUST be the first bytes of the file or agents won't parse it,
    # so the "generated" banner goes *after* the closing fence, not before it.
    return (
        "---\n"
        + f"description: {description}\n"
        + "---\n\n"
        + BANNER_MD.format(src=src_rel)
        + body
    )


def plain_md(src_rel: str, body: str) -> str:
    return BANNER_MD.format(src=src_rel) + body


def gemini_toml(src_rel: str, description: str, body: str) -> str:
    if "'''" in body:
        raise ValueError(f"{src_rel}: body contains ''' which breaks the TOML literal string")
    desc = description.replace("\\", "\\\\").replace('"', '\\"')
    return (
        BANNER_TOML.format(src=src_rel)
        + f'description = "{desc}"\n\n'
        + "prompt = '''\n"
        + body.rstrip("\n")
        + "\n'''\n"
    )


# (subdir, extension, renderer) per agent. Renderer takes (src_rel, description, body).
TARGETS = [
    (Path(".cursor") / "commands", ".md", lambda s, d, b: plain_md(s, b)),
    (Path(".opencode") / "commands", ".md", yaml_frontmatter_md),
    (Path(".windsurf") / "workflows", ".md", yaml_frontmatter_md),
    (Path(".codex") / "prompts", ".md", yaml_frontmatter_md),
    (Path(".gemini") / "commands", ".toml", lambda s, d, b: gemini_toml(s, d, b)),
]


def render_all() -> dict[Path, str]:
    out: dict[Path, str] = {}
    sources = sorted(SOURCE_DIR.glob("*.md"))
    if not sources:
        sys.exit(f"No source commands found in {SOURCE_DIR}")
    for src in sources:
        stem = src.stem
        src_rel = src.relative_to(ROOT).as_posix()
        description, body = parse_command(src)
        for subdir, ext, render in TARGETS:
            dest = ROOT / subdir / f"{stem}{ext}"
            out[dest] = render(src_rel, description, body)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="exit non-zero if files are stale")
    args = ap.parse_args()

    rendered = render_all()
    stale = []
    for dest, content in rendered.items():
        current = dest.read_text(encoding="utf-8") if dest.exists() else None
        if current != content:
            stale.append(dest)
        if not args.check:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")

    rel = lambda p: p.relative_to(ROOT).as_posix()
    if args.check:
        if stale:
            print("Stale generated files (run sync_agent_commands.py):")
            for p in stale:
                print(f"  {rel(p)}")
            return 1
        print("All agent command files are up to date.")
        return 0

    print(f"Wrote {len(rendered)} agent command files from {len(list(SOURCE_DIR.glob('*.md')))} sources:")
    for p in sorted(rendered, key=rel):
        print(f"  {rel(p)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
