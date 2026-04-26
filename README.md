# Ridder Lab AI Hackathon — Spring 2026 Retreat

Welcome. This folder is the playground for the lab retreat. Each team picks an automation idea, hacks on it for the duration of the retreat, and ships their work into `submissions/team_<your_name>/`.

If you've never used a coding agent (Claude Code, Codex, Cursor, Aider, etc.) before, you'll be using one this week. The lab AGENTS.md and the per-tool stubs in this monorepo are written to give an agent enough context to be useful from the first prompt.

> **Note for the retreat:** this is a *submodule* of the larger `lab_ai_automation` monorepo at `/hpc/compgen/projects/lab_ai_automation/` (also at `github.com/DieStok/ridder_lab_ai_automation`). You can clone just this folder if you want, but cloning the parent monorepo gives your coding agent access to the live `slack_paperbot_ridder_lab` as a real-world worked example, plus the `automation_building_blocks/` library.

## 10-minute start

```bash
# 1. Clone the parent monorepo so you also get the building blocks and the
#    live slack paperbot as reference. Skip the --recurse-submodules flag
#    if you only want the hackathon.
git clone --recurse-submodules https://github.com/DieStok/ridder_lab_ai_automation.git
cd ridder_lab_ai_automation/hackathon

# 2. Sync the shared dev environment. This installs every common dependency
#    (Slack, LLM clients, LangGraph, web/PDF parsing, data tools) into a
#    single .venv at hackathon/.venv. uv handles caching so this is fast
#    after the first run.
uv sync

# 3. Pick a problem from automation_ideas.md (or invent your own).

# 4. Make your team's working directory.
git checkout -b team/<your_team>
mkdir submissions/team_<your_team>
cd submissions/team_<your_team>

# 5. (a) If you're building a Slack bot:
cp -r ../../../automation_building_blocks/slack_app_skeleton/* .
cp .env.example .env       # then fill in your tokens
# Note: slack_app_skeleton has its own pyproject.toml. You can either
# `uv sync` inside your submission for an isolated venv, or — for the
# retreat — just use the shared hackathon/.venv at the parent level
# and skip your own pyproject.

# 5. (b) If you're building something else:
uv init                    # fresh pyproject in your team dir
# ... or just write Python files and use the shared hackathon/.venv

# 6. Iterate with your coding agent. Push your branch when you have
#    something to share.
git add .
git commit -m "[team_<your_team>] first cut"
git push origin team/<your_team>
```

## Ground rules

1. **No secrets in commits.** `.env` files are gitignored at every level. If you accidentally commit a token, *immediately* tell `dstoker` so the token can be rotated. (This is non-negotiable; it's not a punishment, it's just the only safe path.)
2. **No force-pushes to `main`.** Work on `team/<your_team>` branches. Open a PR if you want feedback.
3. **Don't touch other teams' folders.** Stay inside `submissions/team_<your_team>/`. The shared hackathon-level files (`README.md`, `pyproject.toml`, `automation_ideas.md`, `AGENTS.md`) are also off-limits for in-place editing during the retreat — open an issue or PR if you want them changed.
4. **Don't install system packages.** The shared `pyproject.toml` is meant to cover most needs. If you need something exotic, add it to your team's own `pyproject.toml` rather than to the shared one. If you really need a system library, ask `dstoker` first.
5. **Be kind to the cluster.** No long-running processes on submit nodes. If you need batch compute, see `../automation_building_blocks/deployment_recipes/hpc_cron_sbatch.md`.
6. **Have fun.** A scrappy demo that works beats a polished design that doesn't.

## What's already in this folder

```
hackathon/
├── README.md                 # this file
├── AGENTS.md                 # short, concrete rules for your coding agent
├── .claude/CLAUDE.md         # symlink → AGENTS.md (for Claude Code)
├── automation_ideas.md       # seed ideas — pick one or invent your own
├── pyproject.toml            # shared dependencies (uv-managed)
├── .env.example              # baseline secrets schema
├── .gitignore
└── submissions/              # one subdir per team
    └── README.md
```

## Starter resources

- **`automation_building_blocks/slack_app_skeleton/`** (in the parent monorepo) — minimal Slack Bolt app with Socket Mode. Easiest start for a Slack bot.
- **`automation_building_blocks/deployment_recipes/`** — how to run a tool locally, on HPC, on a VM.
- **`slack_paperbot_ridder_lab/`** (in the parent monorepo) — the lab's live, working paper-FYI bot. Read its `CLAUDE.md` and `design_decisions_and_rationale.md` if you want to see how a real tool is structured. (Caveat: it is currently HPC-coupled; do not copy its deployment patterns wholesale into a new tool.)
- **`AGENTS.md`** — read this before pointing your coding agent at the repo. It tells the agent how to behave during the retreat.

## Submitting

Your team's work goes in `submissions/team_<your_team>/`. Push your branch:

```bash
git push origin team/<your_team>
```

At the end of the retreat, branches are merged into `main` so everyone's work is preserved in one place. If your work is unfinished, that's fine — push it anyway.

## Help

- Lab Slack: `#ridder-lab` (or wherever the retreat channel is).
- Maintainer for this folder and the wider monorepo: `dstoker`.
- Bug in the shared `pyproject.toml` or `automation_building_blocks/`? File an issue or open a PR against `main`.
