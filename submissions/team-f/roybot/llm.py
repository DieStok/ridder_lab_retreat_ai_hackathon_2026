"""Thin Ollama wrapper with graceful skip if Ollama isn't reachable.

We use the official `ollama` python client (in the shared pyproject). It talks
to whatever endpoint `OLLAMA_BASE_URL` points at — laptop, GPU node, or remote.
"""
from __future__ import annotations

import os
import re

from . import prompts
from .analyze import UserStats


DEFAULT_MODEL = "qwen2.5:14b"
# Ollama otherwise falls back to a small VRAM-based default (~4096 tokens) and
# silently truncates the prompt. We pin num_ctx per request AND the sbatch
# prelude exports OLLAMA_CONTEXT_LENGTH before `ollama serve` — the belt-and-
# suspenders fix from geo_harmonizer's failure taxonomy (truncated-prompt
# confounder). 8192 comfortably holds the aggregated-stats JSON + reports.
DEFAULT_NUM_CTX = 8192

# Reasoning models (qwen3.x, olmo-3-think, gpt-oss, …) prefix the answer with a
# <think>…</think> block. Strip it so the roast/standup text — and the TTS that
# reads it aloud — never contains the model's internal monologue.
_THINK_RE = re.compile(r"<think>.*?</think>\s*", re.DOTALL | re.IGNORECASE)


class LLM:
    def __init__(
        self,
        model: str | None = None,
        host: str | None = None,
        fallback: bool = True,
        num_ctx: int | None = None,
    ):
        self.model = model or os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL)
        self.host = host or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self.fallback = fallback
        # Precedence: explicit arg > OLLAMA_NUM_CTX > OLLAMA_CONTEXT_LENGTH > default.
        self.num_ctx = num_ctx or int(
            os.environ.get("OLLAMA_NUM_CTX")
            or os.environ.get("OLLAMA_CONTEXT_LENGTH")
            or DEFAULT_NUM_CTX
        )
        self._client = None
        self._unavailable_reason: str | None = None

    def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            from ollama import Client  # type: ignore
            self._client = Client(host=self.host)
            return self._client
        except Exception as e:
            self._unavailable_reason = f"ollama import failed: {e}"
            return None

    def _chat(self, system: str, user: str) -> str:
        client = self._get_client()
        if client is None:
            raise RuntimeError(self._unavailable_reason or "no ollama client")
        resp = client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            # num_ctx pins the context window (see DEFAULT_NUM_CTX). temperature
            # is high for snappy, varied roasts.
            options={"temperature": 0.8, "num_ctx": self.num_ctx},
        )
        # ollama-python returns a ChatResponse with .message.content
        content = resp["message"]["content"]  # type: ignore[index]
        return _THINK_RE.sub("", content).strip()

    def serious(self, stats: UserStats) -> str:
        try:
            return self._chat(prompts.SERIOUS_SYSTEM, prompts.serious_user_prompt(stats))
        except Exception as e:
            if self.fallback:
                return f"[LLM fallback — {e}]\n" + prompts.fallback_serious(stats)
            raise

    def roast(self, stats: UserStats) -> str:
        # No flags = no material. The LLM will hallucinate one if we ask anyway,
        # so just use the canned line. The joke is the same.
        if not stats.flags and stats.worst_offender is None:
            return prompts.fallback_roast(stats)
        try:
            return self._chat(prompts.ROAST_SYSTEM, prompts.roast_user_prompt(stats))
        except Exception as e:
            if self.fallback:
                return f"[LLM fallback — {e}]\n" + prompts.fallback_roast(stats)
            raise

    def standup(self, stats_by_user: dict[str, UserStats]) -> str:
        try:
            return self._chat(prompts.STANDUP_SYSTEM, prompts.standup_prompt(stats_by_user))
        except Exception as e:
            if self.fallback:
                return f"[LLM fallback — {e}]\n" + prompts.fallback_standup(stats_by_user)
            raise
