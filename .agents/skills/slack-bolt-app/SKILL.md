---
name: slack-bolt-app
description: >
  Build a Slack bot in Python using slack_bolt (the official Bolt framework). Use this skill
  whenever the task involves a Slack app, Slack bot, slash command, message listener,
  reaction handler, modal, Block Kit UI, App Home, slack_bolt, Bolt Socket Mode, or any
  app that posts to or reads from Slack. Also use when the user mentions chat:write,
  app_mentions:read, slash commands, lazy listeners, the 3-second ack rule, slack-sdk,
  Block Kit, or refers to the lab's `automation_building_blocks/slack_app_skeleton/`,
  the Ridder Lab paperbot, or building any "FYI" / digest / summary / agent bot for Slack.
  Trigger even on casual phrasing like "wire this up to Slack", "make it a Slack bot",
  "post this to a channel", or "react to messages in #fyi-papers".
license: MIT
---

# Slack Bolt App (Python) — for the Ridder Lab AI hackathon

This skill helps you build a working Slack bot **fast** using the [Bolt for Python](https://github.com/slackapi/bolt-python) framework. It is tuned to the lab's environment: Socket Mode by default (no public URL needed), `uv` for dependencies, `.env` for secrets, and the three running-environment options the hackathon supports: laptop, cloud VM, or HPC (with a hard rule: **no internet-facing bots on HPC**).

## Hard rules — read first

1. **Slack requires you to acknowledge most events within 3 seconds.** If your handler talks to an LLM, scrapes a paper, or does anything that might take longer, use a **lazy listener** (`process_before_response=True` + a `lazy=[fn]` callback) — see `references/lazy-listeners.md`. Calling an LLM synchronously inside a slash command handler will time out.
2. **No internet-facing bots on the HPC cluster.** This is a lab policy from `hackathon/AGENTS.md` and the `hpc-cluster` skill. If the bot needs to receive Slack events, it runs on a laptop, a cloud VM, or the lab's existing bot host — not on `hpcs05/06`. HPC is fine for *batch jobs* triggered by the bot (e.g. an `sbatch` submission for code review), but the bot's event loop lives elsewhere.
3. **Never commit tokens.** Read `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN` from `.env` via `python-dotenv`. `.env` is gitignored. Add an `.env.example` with the schema (no values).
4. **Don't use deprecated Slack APIs.** Avoid the legacy `steps-from-apps` (in `references/legacy/`); they are off-spec for new apps.

## Where to start

If the team is building a Slack bot, the fastest path is to copy the lab's skeleton and edit it:

```bash
# from inside submissions/team_<your_team>/
cp -r ../../../automation_building_blocks/slack_app_skeleton/* .
cp .env.example .env   # then fill in SLACK_BOT_TOKEN and SLACK_APP_TOKEN
```

The skeleton is a working Socket Mode app with the right `pyproject.toml`, `.env` schema, and a minimal `app.py`. **Edit it. Don't rewrite it.** The shared `hackathon/.venv` already has `slack_bolt`, so `uv run python app.py` should work without further setup.

If for some reason the skeleton is unavailable, the minimal Socket Mode app is below — but copy from the skeleton first.

## Minimal Socket Mode bot (fallback only)

```python
# app.py
import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])

@app.event("app_mention")
def handle_mention(event, say):
    say(f"Hi <@{event['user']}>! What can I do for you?")

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
```

```bash
# .env (gitignored — never commit this)
SLACK_BOT_TOKEN=xoxb-...     # bot OAuth token, from app config → OAuth & Permissions
SLACK_APP_TOKEN=xapp-...     # app-level token, scope: connections:write
```

Required scopes for a typical FYI / digest / paperbot: `app_mentions:read`, `chat:write`, `channels:history`, `channels:read`, `reactions:read`, `reactions:write`, `users:read`. Add scopes only as you actually need them.

## The 3-second rule, expanded

For slash commands, actions, shortcuts, and view submissions, your handler must call `ack()` within 3 seconds. For events (like `message` or `app_mention`), the framework acks for you, but the handler still must return within 3 seconds **unless** you offload work.

For anything LLM-shaped, do this:

```python
def respond_within_3_seconds(body, ack):
    ack(f"Got it — working on `{body['text']}`...")

def do_the_slow_thing(body, say):
    # call the LLM, fetch the paper, run the deep research...
    answer = expensive_llm_call(body["text"])
    say(answer)

app.command("/summarize")(
    ack=respond_within_3_seconds,
    lazy=[do_the_slow_thing],
)
```

Full details and AWS Lambda / FaaS variants in `references/lazy-listeners.md`.

## Common hackathon recipes

**Paper-FYI bot** — react to messages in a channel that contain arXiv/bioRxiv/DOI links, fetch metadata, post a thread reply with a summary. The trigger is `app.event("message")` filtered by URL regex. The work goes in a lazy listener. See `references/event-listening.md` and `references/message-sending.md`.

**Slash-command digest bot** — `/digest` returns a personalized reading list. Slash command + lazy listener for the LLM call. See `references/commands.md` and `references/lazy-listeners.md`.

**Powerpoint summarizer** — listen for `file_shared` events with `.pptx` files, download via the Web API, summarize, post back. See `references/event-listening.md` and `references/web-api.md`.

**Adversarial reviewer in a thread** — `app.event("app_mention")` triggers a response that critiques the parent message. Long answers should use lazy listeners. See `references/event-listening.md`.

**AI-side-panel agent (newer)** — Slack's `Assistant` class gives you a side panel UX designed for AI. See `references/using-the-assistant-class.md` and `references/adding-agent-features.md` (this includes text streaming, feedback buttons, and Slack MCP server integration).

## Where things go in the hackathon repo

```
hackathon/submissions/team_<your_team>/
├── app.py                  # Bolt app — copied from slack_app_skeleton
├── pyproject.toml          # team's deps — or use the shared hackathon/.venv
├── .env.example            # schema only, committed
├── .env                    # filled in, gitignored
└── README.md               # how to run it
```

## Deployment recipes

For local dev: `uv run python app.py` from your team folder. Socket Mode means no port forwarding needed.

For the lab cloud VM (recommended target for anything past the hackathon): see `automation_building_blocks/deployment_recipes/` in the parent monorepo. There is a recipe for systemd-managed bots.

For HPC: **you cannot run an event-loop bot here** (lab policy). What you *can* do is have the bot (running elsewhere) submit `sbatch` jobs to HPC and post the results back to Slack when they finish — see `automation_building_blocks/deployment_recipes/hpc_cron_sbatch.md`. The `hpc-cluster` skill has the SLURM specifics.

## What this skill does NOT cover

- OAuth multi-tenant installs (`authenticating-oauth.md`) — internal lab use is single-workspace, so skip this.
- Token rotation, custom adapters, custom workflow steps — too advanced for a 50-min hackathon.
- The TypeScript/JS Bolt SDK — Python only here.

## Reference reading order

When the team needs more depth, consult `references/` in this order:

1. `getting-started.md` — full quickstart end-to-end
2. `socket-mode.md` — the connection model
3. `event-listening.md` + `message-listening.md` — what to react to
4. `message-sending.md` — `say()`, `respond()`, `client.chat_postMessage`
5. `commands.md` — slash commands
6. `actions.md` — buttons and interactive elements
7. `lazy-listeners.md` — **read this if any handler does LLM work**
8. `acknowledge.md` — the 3-second rule in detail
9. `opening-modals.md` + `view-submissions.md` — modal forms
10. `web-api.md` — calling Slack methods directly (e.g. `client.files_info`)
11. `errors.md` — error handling patterns
12. `async.md` + `listener-middleware.md` — for asyncio apps and middleware chains
13. `adding-agent-features.md` + `using-the-assistant-class.md` — AI-specific Slack features (streaming, feedback, side-panel agent UX)

These files are copied verbatim from the [slackapi/bolt-python](https://github.com/slackapi/bolt-python/tree/main/docs/english) repository (MIT license). Originals live at `bolt-python/docs/english/`.
