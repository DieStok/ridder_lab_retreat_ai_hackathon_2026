# `.agents/skills/` — agent skill pack for the Ridder Lab AI hackathon

This folder is the single source of truth for agent skills used during the hackathon. It is read by Claude Code, Codex, Cursor, and any other agent that supports the open [Agent Skills](https://agentskills.io/) standard. To make Claude Code find it, create a symlink from `hackathon/`:

```bash
mkdir -p .claude && ln -s ../.agents/skills .claude/skills
```

Codex and Cursor look at `.agents/skills/` directly — for those agents the symlink is unnecessary, but harmless.

## What's in here

| # | Skill | Source | Role |
|---|-------|--------|------|
| 1 | `compound-engineering/` | [EveryInc/compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin) (entire `plugins/compound-engineering/` folder — 38 skills + 49 agents) | Process layer — brainstorm, plan, code-review, debug, commit-push-pr, compound, and 30+ more, with the agent set the skills depend on. |
| 2 | `skill-creator/` | [anthropics/skills](https://github.com/anthropics/skills) | Interactive guide for building new skills. Use it whenever you find yourself re-explaining the same thing to your agent. |
| 3 | `frontend-design/` | [anthropics/skills](https://github.com/anthropics/skills) | Distinctive, production-grade frontend interfaces — for any team building a paper website, dashboard, or interactive demo. |
| 4 | `slack-bolt-app/` | Lab-internal (this repo) | Build Slack bots in Python with `slack_bolt`. Wraps the lab's `automation_building_blocks/slack_app_skeleton/`, encodes the 3-second ack rule and lazy-listener pattern, and ships the relevant Bolt-Python English docs in `references/`. |
| 5 | `paper-lookup/` | [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | One skill that wraps PubMed, PMC, bioRxiv, medRxiv, arXiv, OpenAlex, Crossref, Semantic Scholar, CORE, and Unpaywall via REST APIs. |
| 6 | `literature-review/` | [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | Tiered, citation-aware synthesis across multiple databases. Pairs naturally with `paper-lookup`. |
| 7 | `scientific-writing/` | [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | IMRAD-structured manuscripts, citations (APA/AMA/Vancouver), reporting guidelines (CONSORT/STROBE/PRISMA). Useful when filling in `submissions/team_<name>/PROPOSAL.md` to a publishable standard. |

## Why these and how they fit the 50-minute hackathon

You have ~50 minutes, you'll write a `PROPOSAL.md`, you'll scaffold a small Python tool (probably a Slack bot or an HPC job), and you'll `git push origin team/<your_team>` at the end. The skills above are chosen to compress every one of those steps and to nudge you away from the most common 50-minute hackathon failure mode: jumping to code before the design is clear.

`compound-engineering` is the process spine. The four entry points your team will actually call are `/ce-brainstorm` (one-question-at-a-time interview that produces a brainstorm doc matching `TEMPLATE.md`'s structure), `/ce-plan` (turns the brainstorm into an ID-traceable plan), `/ce-debug` (the safety net for the last fifteen minutes), and `/ce-commit-push-pr` (one command for the submission step). The other 34 skills are there because the four you'll use depend on them — `ce-plan` spawns the research agent, `ce-debug` calls the correctness reviewer, etc. Vendoring the whole plugin keeps those references intact.

`skill-creator` is for the moment you find yourself explaining the same lab convention three times in one session. Stop, run skill-creator, codify it, and the next person on your team starts ahead. This is the "compound" half of compound-engineering applied to the skill layer itself.

`frontend-design` earns its slot because of brainstorm idea #8 (interactive demos and paper websites): coding agents are *good* at one-pass UI work and `frontend-design` is the skill that keeps the output from looking like generic AI slop.

`slack-bolt-app` is the densest skill in the pack and the one most likely to save you real time. It encodes the things you would otherwise discover by trial and error: Socket Mode means no public URL, lazy listeners are mandatory if your handler talks to an LLM (3-second ack rule), and `automation_building_blocks/slack_app_skeleton/` already has the `pyproject.toml` and `.env.example` you need. The vendored Bolt docs in `references/` cover events, slash commands, modals, message sending, the Web API, errors, async, and the AI-specific features (`adding-agent-features.md`, `using-the-assistant-class.md`).

`paper-lookup` and `literature-review` are the two skills that turn brainstorm ideas #1 (personal reading digest) and #4 (LLM-based local reviewer) from "we'd need to glue ten APIs together" into "import the skill". `paper-lookup` is the search backend; `literature-review` is the synthesis layer that knows about journal tiers and preprint servers.

`scientific-writing` is the heaviest of the K-Dense skills, included not for ambitious manuscript writing in 50 minutes but because it gives the agent a coherent template for the prose sections of `PROPOSAL.md` — problem statement, why automation fits, references — at a level appropriate for something the lab will actually read after the retreat.

## Updating

Each subfolder is a vendored copy from its upstream as of the date this pack was assembled. To refresh a skill, sparse-clone the upstream repo and replace the folder. For `compound-engineering` specifically, you can also use the official plugin marketplace install (`/plugin marketplace add EveryInc/compound-engineering-plugin && /plugin install compound-engineering`) for Claude Code; that gives you the same content under `~/.claude/plugins/` instead of the project-local copy here.

## Licenses

Each skill keeps its upstream license file. `compound-engineering/LICENSE`, `skill-creator/LICENSE.txt`, `frontend-design/LICENSE.txt`, and the K-Dense skills (per-skill `license` field in their `SKILL.md` frontmatter) carry the original terms. The `slack-bolt-app/references/` directory is a verbatim copy of selected files from [slackapi/bolt-python](https://github.com/slackapi/bolt-python/tree/main/docs/english) (MIT).
