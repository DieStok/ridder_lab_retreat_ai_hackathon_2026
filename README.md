<div align="center">
  <img src="images/Ye_Olde_Hackathonne.png" alt="Brainstorm de Ridder Lab" width="800">
  <figcaption>Fig 1. Obligatory AI-generated diagram to add spirit and vim to this README.
  Motivational quote: 'Hack away'! Hotel: Trivago.</figcaption>
</div>



# Ridder Lab AI Hackathon — Spring 2026 Retreat

Welcome. This folder is the playground for the lab retreat. Each team picks an automation idea, hacks on it for 50 minutes, and ships their work into `submissions/team_<your_name>/`. Refer to the [brainstorm idea doc](./BRAINSTORM_lab_automation_ideas.md) to find ideas that we pre-generated and the ideas that we have just come up with.

The brainstorm document has more details, but TL;DR the hackathon:
1. You clone this repo (ideally the top-level ridder_lab_ai_automation repo if you want context for any AI coding agents; see below)
2. You work with your team in a folder within `submissions`, e.g. `submissions/Spanish_are_best_team_NO_CUBANS` or something similarly innocuous.
3. You produce i) a markdown document detailing exactly: a) the problem you intend to solve; b) why that is a problem and how LLM agents or other automation could solve this (partly); c) a proposed architecture/workflow/idea of how to implement this; d) any references or tool docs that could be useful for further work. [Work by filling out the TEMPLATE.md](./submissions/TEMPLATE.md) ; ii) an initial implementation, in so far as you can get that in ±50 minutes with the help of your teammates and your LLM agent of choice.
4. Starting sources on LLM reviews, scientific agent/AI workflows, tools, etc. can be found in [additional_information_and_resources](./additional_information_and_resources). These are almost certainly relevant, so add them to any LLM chats or agents and ask if there's anything in there.

Note that it's good to check that we're not reinventing the wheel, so if there are tools that we should just start using given the ideas in the [brainstorm idea doc](./BRAINSTORM_lab_automation_ideas.md), this is a valuable find as well: a write-up on what to use, how, and when is the best possible quick win!

Note 2: think about whether the solution is something we would run on our local laptops, is it something we would run on the hpc (e.g. code analysis, but no internet access allowed because that's a security nightmare), or something that would interact with Slack (and should perhaps live as a bot on a cloud VM)? Note this in the document. 

## 10-minute start

```bash
# 1. Clone the parent monorepo so you also get the building blocks and the
#    live slack paperbot as reference. Skip the --recurse-submodules flag
#    if you only want the hackathon.
git clone --recurse-submodules https://github.com/DieStok/ridder_lab_ai_automation.git
cd ridder_lab_ai_automation/hackathon

# 2. Pick a problem from BRAINSTORM_lab_automation_ideas.md

# 3. Make your team's working directory.
git checkout -b team/<your_team>
mkdir submissions/team_<your_team>
cp submissions/TEMPLATE.md submissions/team_<your_team>/PROPOSAL.md
cd submissions/team_<your_team>

# 4. Start filling out the TEMPLATE.md that you just renamed PROPOSAL.md with your team!
#    You can do this by brainstorming, asking LLMs for tips, making svg images, etc.
#    Don't forget to look at hackathon/additional_information_and_resources for some starting information!
#    YOU REALISTICALLY WILL SPEND MOST TIME IN THIS STEP!

# 5. Start hacking something together! Use your favourite LLM agents, either in the browser or on your laptop.
#    You can use the included basic uv virtual environment with the command below this comment block.
#    It installs dependencies for:
#    Slack, LLM clients, LangGraph, web/PDF parsing, and some common data tools into a
#    single .venv at hackathon/.venv. 
#    NOTE: you can of course get started researching without this. This is only for implementation!
uv sync
#activate the venv
source ../hackathon/.venv/bin/activate
# If you don't have uv/don't know what it is:
curl -LsSf https://astral.sh/uv/install.sh | sh # And see: https://docs.astral.sh/uv/getting-started/installation/ 


# 6. Iterate with your coding agent. Push your branch at the end. Tell Dieter whose e-mail to add to allow you to actually commit and push. 
git add .
git commit -m "[team_<your_team>] first cut"
git push origin team/<your_team>
```

## Ground rules

1. **No force-pushes to `main`.** Work on `team/<your_team>` branches. 
2. **Don't touch other teams' folders.** Stay inside `submissions/team_<your_team>/`. The shared hackathon-level files (`README.md`, `pyproject.toml`, `BRAINSTORM_lab_automation_ideas.md`, `AGENTS.md`) are also off-limits for in-place editing during the retreat — open an issue or PR if you want them changed.
3. **Have fun.** OR ELSE!

## What's already in this folder

```
hackathon/
├── README.md                                # this file
├── AGENTS.md                                # short, concrete rules for your coding agent
├── .claude/CLAUDE.md                        # symlink → AGENTS.md (for Claude Code)
├── BRAINSTORM_lab_automation_ideas.md       # seed ideas — pick one or invent your own
├── pyproject.toml                           # shared dependencies (uv-managed)
├── .env.example                             # baseline secrets schema
├── .gitignore
└── submissions/                             # one subdir per team
    └── README.md
```

## Starter resources

- **`automation_building_blocks/slack_app_skeleton/`** (in the parent monorepo) — minimal Slack Bolt app with Socket Mode. Easiest start for a Slack bot.
- **`automation_building_blocks/deployment_recipes/`** — how to run a tool locally, on HPC, on a VM.
- **`slack_paperbot_ridder_lab/`** (in the parent monorepo) — working paper FYI bot concept. Did use internet from the HPC, so decommissioned for now (thanks Roy, and apologies - Dieter) until refactor for running locally or on a cloud VM. 
- **`AGENTS.md`** — read this before pointing your coding agent at the repo. It tells the agent how to behave during the retreat.

## Submitting

Your team's work goes in `submissions/team_<your_team>/`. Push your branch:

```bash
git push origin team/<your_team>
```

At the end of the retreat, branches are merged into `main` so everyone's work is preserved in one place. If your work is unfinished, that's fine — push it anyway.

## Help

<div align="center">
  <img src="images/on_your_own.gif" alt="No help is coming boii" width="800">
  <figcaption>Fig 2. Nope. jk jk, we'll be perambulating and answering your queries with gusto.</figcaption>
</div>

