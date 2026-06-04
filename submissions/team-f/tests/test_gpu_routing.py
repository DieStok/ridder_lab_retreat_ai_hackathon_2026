"""Tests for roybot's auto GPU-tier + context routing (roybot.gpu_router).

Pure logic + an Ollama→GGUF resolver test against a fake on-disk store. None of
these need the gguf-parser binary or a GPU — the VRAM estimate itself is geo's
validated tool, exercised live in the launcher, not unit-mocked here.

Run from submissions/team-f/:  .venv/bin/python -m pytest -q tests/test_gpu_routing.py
"""
from __future__ import annotations

import json

import pytest

from roybot.gpu_router import (
    GPU_TIERS,
    _resolve_context,
    _split_tag,
    ollama_gguf_path,
    resolve_store,
    tier_for,
)


@pytest.mark.parametrize("vram,tier,gres", [
    (0, "gpu_small", "gpu:2g.20gb:1"),
    (6, "gpu_small", "gpu:2g.20gb:1"),
    (20, "gpu_small", "gpu:2g.20gb:1"),       # ceiling is inclusive
    (20.5, "gpu_large", "gpu:quadro_rtx_6000:1"),
    (24, "gpu_large", "gpu:quadro_rtx_6000:1"),
    (25, "gpu_extra_large", "gpu:7g.79gb:1"),
    (79, "gpu_extra_large", "gpu:7g.79gb:1"),
])
def test_tier_for(vram, tier, gres):
    assert tier_for(vram) == (tier, gres)


def test_tier_for_above_largest_raises():
    with pytest.raises(ValueError):
        tier_for(80)


def test_tiers_are_monotonic():
    ceilings = [c for c, _, _ in GPU_TIERS]
    assert ceilings == sorted(ceilings)


@pytest.mark.parametrize("ctx,maxc,expected", [
    ("max", 262144, 262144),
    (8192, 262144, 8192),          # under max -> unchanged
    (300000, 262144, 262144),      # over max -> capped
    ("8192", 262144, 8192),        # string int accepted
    (8192, None, 8192),            # unknown max -> use as given
    ("MAX", 131072, 131072),       # case-insensitive
])
def test_resolve_context(ctx, maxc, expected):
    assert _resolve_context(ctx, maxc) == expected


def test_resolve_context_max_without_maxctx_raises():
    with pytest.raises(ValueError):
        _resolve_context("max", None)


@pytest.mark.parametrize("tag,name,ver", [
    ("qwen3.5:9b", "qwen3.5", "9b"),
    ("gemma3", "gemma3", "latest"),
    ("hf.co/unsloth/gemma-4-31B-it-GGUF:UD-Q8_K_XL",
     "hf.co/unsloth/gemma-4-31B-it-GGUF", "UD-Q8_K_XL"),
])
def test_split_tag(tag, name, ver):
    assert _split_tag(tag) == (name, ver)


def _make_fake_store(tmp_path, name="foo", ver="1b", digest_hex="abc123"):
    """Build a minimal Ollama store: one library manifest + its model blob."""
    man = tmp_path / "manifests" / "registry.ollama.ai" / "library" / name / ver
    man.parent.mkdir(parents=True)
    man.write_text(json.dumps({
        "layers": [
            {"mediaType": "application/vnd.ollama.image.license", "digest": "sha256:lic"},
            {"mediaType": "application/vnd.ollama.image.model", "digest": f"sha256:{digest_hex}"},
        ],
    }))
    blob = tmp_path / "blobs" / f"sha256-{digest_hex}"
    blob.parent.mkdir(parents=True)
    blob.write_bytes(b"GGUF-fake")
    return blob


def test_ollama_gguf_path_resolves_library_model(tmp_path):
    blob = _make_fake_store(tmp_path)
    assert ollama_gguf_path("foo:1b", store=tmp_path) == blob


def test_ollama_gguf_path_missing_model_raises(tmp_path):
    (tmp_path / "manifests").mkdir()
    with pytest.raises(FileNotFoundError):
        ollama_gguf_path("nope:1b", store=tmp_path)


def test_resolve_store_requires_source(monkeypatch):
    monkeypatch.delenv("OLLAMA_MODELS", raising=False)
    with pytest.raises(ValueError):
        resolve_store(None)
    # explicit arg wins
    assert str(resolve_store("/some/store")) == "/some/store"
