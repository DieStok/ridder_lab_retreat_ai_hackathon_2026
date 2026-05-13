"""Post the lab stand-up transcript + audio to Slack.

We only need WebClient (not socket-mode), since this runs as a one-shot from
the CLI. Reads SLACK_BOT_TOKEN and SLACK_CHANNEL_ID from env.

Required bot scopes: chat:write, files:write
"""
# Adapted from automation_building_blocks/slack_app_skeleton (env loading + token names).
from __future__ import annotations

import os
from pathlib import Path


def post_standup(transcript: str, audio_path: str | Path | None = None) -> dict:
    """Post text to the lab channel, optionally with an audio file attached.

    Returns the Slack API response for the chat.postMessage call.
    Raises RuntimeError if env isn't configured (so the CLI can skip gracefully).
    """
    token = os.environ.get("SLACK_BOT_TOKEN")
    channel = os.environ.get("SLACK_CHANNEL_ID")
    if not token or not channel:
        raise RuntimeError("SLACK_BOT_TOKEN and SLACK_CHANNEL_ID must be set in .env")

    from slack_sdk import WebClient  # local import so the CLI works without slack-sdk

    client = WebClient(token=token)
    resp = client.chat_postMessage(
        channel=channel,
        text=":microphone: *Roy-bot's weekly HPC stand-up*\n\n" + transcript,
        mrkdwn=True,
    )
    if audio_path:
        p = Path(audio_path)
        if p.exists():
            client.files_upload_v2(
                channel=channel,
                file=str(p),
                title="Roy-bot stand-up audio",
                initial_comment="Audio version, for the standup slide.",
            )
    return resp.data  # type: ignore[return-value]
