# AGENTS.md — Ridder Lab AI Hackathon (Spring 2026)

> Source of truth for coding-agent behavior during the lab retreat. `.claude/CLAUDE.md` symlinks here. Tools that read `AGENTS.md` (Codex, Cursor, Aider) and `CLAUDE.md` (Claude Code) see the same rules.
>
> Concrete and concise. If a rule isn't relevant to your team's work, ignore it; if you need a rule that isn't here, ask the human.

## Context for the agent

You are working inside one team's submission directory at the De Ridder Lab's spring retreat. The team is hacking on a small AI-automation project for the lab. They are likely on a laptop, possibly behind UMC Utrecht's network. They have ~1–3 days. They want a scrappy working demo, not a polished system.

The parent monorepo (`lab_ai_automation`) has its own `AGENTS.md` with the lab's general conventions. **This file overrides the parent within the `hackathon/` subtree.**

## Where you can write

- **Inside `submissions/team_<name>/`** — yes, freely. This is your team's working directory.
- **Outside that directory** — no, unless the human explicitly asks. Don't modify `README.md`, `automation_ideas.md`, `pyproject.toml`, the shared `.env.example`, or another team's submissions. If you need a change to a shared file, propose it and let the human commit it.

## Environment

- Python 3.11+, `uv` is the package manager. The shared dev environment is at `hackathon/.venv/` (run `uv sync` from `hackathon/` to populate).
- The shared `pyproject.toml` covers the common kit: `slack_bolt`, `python-dotenv`, `pyyaml`, `requests`, `httpx`, `beautifulsoup4`, `lxml`, `pydantic`, `tenacity`, `diskcache`, `jinja2`, `ollama`, `litellm`, `langchain`, `langgraph` and provider integrations, `pypdf`, `tavily-python`, `arxiv`, `pandas`, `duckdb`, `ipython`, `jupyterlab`, `pytest`. **Prefer adding to the team's own `pyproject.toml`** over modifying the shared one.
- Ollama may be running on `localhost`, on a GPU compute node, or not at all. Always read `OLLAMA_BASE_URL` from env (`http://localhost:11434` is the safe default). Don't hardcode it.

## Hard rules

1. **No secrets in commits.** Read tokens from `.env` via `python-dotenv`. `.env` is gitignored. If you find yourself wanting to write a token into a file that isn't `.env`, stop and ask the human.
2. **No system-package installs.** Don't `apt`, `dnf`, `brew`, or `module load`. If a Python dep needs system libs (e.g. `crawl4ai` needs Playwright system deps), tell the human and stop.
3. **No long-running processes on HPC submit nodes.** If the team is on the cluster, batch work goes through `sbatch`. Read `../automation_building_blocks/deployment_recipes/hpc_cron_sbatch.md`.
4. **No force-pushes, no rewriting history**, on `main` or on team branches. Make new commits.
5. **Don't delete or modify other teams' work.** `submissions/team_*/` directories that aren't yours are read-only.

## Soft rules (the spirit)

- A working scrappy demo is the goal. Skip tests for prototypes; add them when something becomes real.
- Don't over-engineer. The retreat is hours-to-days, not weeks.
- Prefer copying from `../automation_building_blocks/` over inventing new patterns. If you copy a block, leave a one-line attribution comment at the top of the file noting which block it came from.
- When uncertain about a lab convention or what the team actually wants, **ask the human**. The human is in the room.

## Common starting points

- **Slack bot:** `cp -r ../../../automation_building_blocks/slack_app_skeleton/* .` — gives you a working Socket-Mode app to extend.
- **CLI tool:** `uv init` in the team dir and add deps to `pyproject.toml`.
- **Notebook / exploratory:** `uv run jupyter lab` from `hackathon/` (the shared venv has it).

## What "done" looks like for a retreat submission

- A `README.md` in your team dir explaining what you built and how to run it.
- An entry-point command (`uv run python -m mything.run`, `uv run python app.py`, etc.).
- An `.env.example` if your code reads tokens.
- One commit at minimum, pushed to your `team/<name>` branch.

That's enough. Ship it.
