# AGENTS.md — `/onboard` & `/create-guide` (cross-agent)

This project ships two **interactive commands** for onboarding new De Ridder Lab
members onto a research project, and authoring the guides that power them:

| Command | For | What it does |
| --- | --- | --- |
| `/onboard` | a new member | Reads a project's numbered notebooks and walks them through it interactively, running read-only checks and driving a first real task. |
| `/create-guide` | a project owner | Interviews you and writes the onboarding notebooks for your project. |

The **single source of truth** is `.claude/commands/*.md`. Every other agent's copy
is generated from it by `scripts/sync_agent_commands.py` — edit the source, then
re-run the script. Do not hand-edit the generated files.

## Where each agent reads these commands

| Agent | Invoke as | File (generated unless noted) |
| --- | --- | --- |
| Claude Code | `/onboard`, `/create-guide` | `.claude/commands/*.md` (**source**) |
| Cursor | `/onboard`, `/create-guide` | `.cursor/commands/*.md` |
| Gemini CLI | `/onboard`, `/create-guide` | `.gemini/commands/*.toml` |
| opencode | `/onboard`, `/create-guide` | `.opencode/commands/*.md` |
| Windsurf (Cascade) | `/onboard`, `/create-guide` | `.windsurf/workflows/*.md` |
| OpenAI Codex | copy to `~/.codex/prompts/`, then `/onboard` | `.codex/prompts/*.md` |
| Any AGENTS.md agent (Codex, Aider, Jules, …) | ask in plain language (see below) | this file + the source command |

## For agents without a slash-command mechanism

If you are an agent that reads this `AGENTS.md` but has no per-command invocation
(e.g. Aider, or Codex reading project instructions), **do not run these workflows
automatically.** They are explicit, user-triggered tasks. Only when the user asks
to "onboard onto a project" or "create an onboarding guide" should you open and
follow the matching file:

- onboarding a member → follow `.claude/commands/onboard.md`
- authoring a guide → follow `.claude/commands/create-guide.md`

Both are self-contained prompts. Honour their rules — in particular `/onboard` is
**read-only**: never submit jobs or modify files, and always use absolute paths on HPC.

## Regenerating after an edit

```bash
python3 scripts/sync_agent_commands.py          # rewrite all agent copies
python3 scripts/sync_agent_commands.py --check  # CI: fail if any copy is stale
```
