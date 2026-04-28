<div align="center">
  <img src="images/Ye_Olde_Hackathonne.png" alt="Brainstorm de Ridder Lab" width="800">
  <figcaption>Fig 1. Obligatory AI-generated diagram to add spirit and vim to this README.
  Motivational quote: 'Hack away'! Hotel: Trivago.</figcaption>
</div>



# Ridder Lab AI Hackathon — Spring 2026 Retreat

Welcome. This folder is the playground for the lab retreat. Each team picks an automation idea, hacks on it for the duration of the retreat, and ships their work into `submissions/team_<your_name>/`. Refer to the [brainstorm idea doc](hackathon/BRAINSTORM_lab_automation_ideas.md) to find ideas that we pre-generated and the ideas that we have just come up with.

The brainstorm document has more details, but TL;DR the hackathon:
1. You clone this repo (ideally the top-level ridder_lab_ai_automation repo if you want context for any AI coding agents)
2. You work with your team in a folder within `submissions`, e.g. `submissions/Spanish_are_best_team_NO_CUBANS` or something similarly innocuous.
3. You produce i) a markdown document detailing exactly: a) the problem you intend to solve; b) why that is a problem and how LLM agents or other automation could help; c) a proposed architecture/workflow/idea of how to implement this. ; ii) an initial implementation, in so far as you can get that in ±50 minutes with the help of your teammates and your LLM bot of choice.

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

1. **No force-pushes to `main`.** Work on `team/<your_team>` branches. Open a PR if you want feedback.
2. **Don't touch other teams' folders.** Stay inside `submissions/team_<your_team>/`. The shared hackathon-level files (`README.md`, `pyproject.toml`, `automation_ideas.md`, `AGENTS.md`) are also off-limits for in-place editing during the retreat — open an issue or PR if you want them changed.
3. **Have fun.** OR ELSE!

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
