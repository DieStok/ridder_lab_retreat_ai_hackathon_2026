#!/usr/bin/env python3
"""Auto GPU-tier + context-length routing for RoboRoy.

Given an Ollama model tag, resolve its GGUF blob, estimate VRAM at the target
context (via roybot.model_memory / gguf-parser), and map that to the smallest
SLURM ``--gres`` GPU slice that fits. Routing is computed at *submit time* so
``sbatch --gres=...`` can be set before the job is queued.

Tier ceilings (20/24/79 GB) are ported from geo_harmonizer's
``src/core/sweep/cli.py`` (``_gpu_tier_for``); the ``--gres`` strings are this
cluster's GPU types (``sinfo``).

CLI::

    python -m roybot.gpu_router --model qwen3.5:9b --ctx 8192
    python -m roybot.gpu_router --model gemma4:26b --ctx max --format json

Store: pass ``--store`` or set ``OLLAMA_MODELS`` (same var ollama_hpc.sh uses).
No absolute path is baked into this module (monorepo rule #3) — the deployment
default lives in scripts/submit_roboroy.sh.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from .model_memory import estimate_memory

# Ported verbatim from geo_harmonizer (_GPU_*_CEILING_GB). The third element is
# this cluster's --gres GPU type for that tier.
GPU_TIERS: tuple[tuple[int, str, str], ...] = (
    (20, "gpu_small", "gpu:2g.20gb:1"),          # A100 MIG 20 GB (usually idle)
    (24, "gpu_large", "gpu:quadro_rtx_6000:1"),  # RTX 6000 24 GB
    (79, "gpu_extra_large", "gpu:7g.79gb:1"),    # A100 MIG 79 GB (contended)
)

# gguf-parser reports device VRAM excluding Ollama's compute/graph buffer, so it
# under-reports real usage. The tiers are coarse, but a multiplier keeps a
# near-boundary model off a too-small slice. Override with ROBOROY_VRAM_HEADROOM.
DEFAULT_HEADROOM = 1.3
_PROBE_CTX = 2048  # cheap probe just to read maximumContextLength


@dataclass
class RouteDecision:
    model: str
    gguf_path: str
    gpu_tier: str
    gres: str
    context_length: int
    max_context: int | None
    est_vram_gb: float        # raw gguf-parser estimate
    effective_vram_gb: int    # ceil(raw * headroom) — what was routed on
    headroom: float

    def to_dict(self) -> dict:
        return asdict(self)


def resolve_store(store: str | Path | None = None) -> Path:
    """The Ollama model store: explicit arg > OLLAMA_MODELS env."""
    if store:
        return Path(store)
    env = os.environ.get("OLLAMA_MODELS")
    if env:
        return Path(env)
    raise ValueError(
        "Ollama model store not set: pass --store or export OLLAMA_MODELS "
        "(scripts/submit_roboroy.sh sets the lab default)."
    )


def _split_tag(model: str) -> tuple[str, str]:
    """'qwen3.5:9b' -> ('qwen3.5', '9b'); 'gemma3' -> ('gemma3', 'latest')."""
    if ":" in model:
        name, ver = model.rsplit(":", 1)
    else:
        name, ver = model, "latest"
    return name, ver


def _find_manifest(store: Path, name: str, ver: str) -> Path:
    """Locate the Ollama manifest file for name:ver under store/manifests."""
    manifests = store / "manifests"
    # Fast paths: library models and host-qualified names.
    candidates = [
        manifests / "registry.ollama.ai" / "library" / Path(name) / ver,
        manifests / Path(name) / ver,
    ]
    for c in candidates:
        if c.is_file():
            return c
    # Fallback: any manifest whose path ends with <name>/<ver>.
    suffix = os.path.join(name, ver)
    if manifests.is_dir():
        for p in manifests.rglob(ver):
            if p.is_file() and str(p).endswith(suffix):
                return p
    raise FileNotFoundError(
        f"No Ollama manifest for {name}:{ver} under {manifests}. "
        f"Is the model pulled? (ollama list)"
    )


def ollama_gguf_path(model: str, store: str | Path | None = None) -> Path:
    """Resolve an Ollama tag to its GGUF blob on disk (offline, no server)."""
    store = resolve_store(store)
    name, ver = _split_tag(model)
    manifest = _find_manifest(store, name, ver)
    data = json.loads(manifest.read_text())
    digest = next(
        (
            layer["digest"]
            for layer in data.get("layers", [])
            if layer.get("mediaType") == "application/vnd.ollama.image.model"
        ),
        None,
    )
    if not digest:
        raise ValueError(f"No model layer in manifest {manifest}")
    blob = store / "blobs" / ("sha256-" + digest.split(":", 1)[1])
    if not blob.is_file():
        raise FileNotFoundError(f"GGUF blob missing: {blob}")
    return blob


def tier_for(vram_gb: float) -> tuple[str, str]:
    """Map an (effective) VRAM figure to (tier_name, --gres). Errors above 79 GB."""
    for ceiling, name, gres in GPU_TIERS:
        if vram_gb <= ceiling:
            return name, gres
    raise ValueError(
        f"Estimated {vram_gb} GB exceeds the largest GPU tier "
        f"({GPU_TIERS[-1][0]} GB) — no slice fits this model/context."
    )


def _resolve_context(ctx: str | int, max_context: int | None) -> int:
    """Resolve the effective context: 'max' -> max_context; else cap at max."""
    if isinstance(ctx, str) and ctx.lower() == "max":
        if not max_context:
            raise ValueError("--ctx max requested but the GGUF reports no maximumContextLength")
        return max_context
    val = int(ctx)
    if max_context and val > max_context:
        return max_context
    return val


def route(
    model: str,
    ctx: str | int = 8192,
    *,
    store: str | Path | None = None,
    headroom: float | None = None,
    flash_attention: bool = True,
) -> RouteDecision:
    """Resolve model -> GGUF -> VRAM@ctx -> GPU tier + capped context length."""
    if headroom is None:
        headroom = float(os.environ.get("ROBOROY_VRAM_HEADROOM", DEFAULT_HEADROOM))
    gguf = ollama_gguf_path(model, store)

    # Cheap probe for the trained context, then estimate VRAM at the resolved ctx.
    probe = estimate_memory(gguf_path=gguf, ctx_grid=(_PROBE_CTX,), model_id=model)
    max_context = probe.max_context
    context_length = _resolve_context(ctx, max_context)

    est = estimate_memory(
        gguf_path=gguf,
        ctx_grid=(context_length,),
        n_ctx_train=max_context,
        flash_attention=flash_attention,
        model_id=model,
    )
    raw_vram = est.vram_at(context_length) or 0.0
    effective = math.ceil(raw_vram * headroom)
    tier_name, gres = tier_for(effective)

    return RouteDecision(
        model=model,
        gguf_path=str(gguf),
        gpu_tier=tier_name,
        gres=gres,
        context_length=context_length,
        max_context=max_context,
        est_vram_gb=round(raw_vram, 2),
        effective_vram_gb=effective,
        headroom=headroom,
    )


# --------------------------------------------------------------------------- #
# CLI.
# --------------------------------------------------------------------------- #
def _build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model", required=True, help="Ollama model tag, e.g. qwen3.5:9b")
    ap.add_argument("--ctx", default="8192", help="target context size, or 'max'")
    ap.add_argument("--store", default=None, help="Ollama model store (else $OLLAMA_MODELS)")
    ap.add_argument("--headroom", type=float, default=None,
                    help="VRAM safety multiplier (else $ROBOROY_VRAM_HEADROOM or 1.3)")
    ap.add_argument("--format", choices=("sbatch", "json"), default="sbatch",
                    help="sbatch: KEY=VALUE lines; json: full decision")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    try:
        d = route(args.model, args.ctx, store=args.store, headroom=args.headroom)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[gpu_router] ERROR: {exc}", file=sys.stderr)
        return 1
    if args.format == "json":
        json.dump(d.to_dict(), sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(
            f"[gpu_router] {d.model}: ~{d.est_vram_gb} GB raw "
            f"(x{d.headroom} -> {d.effective_vram_gb} GB) @ ctx {d.context_length} "
            f"-> {d.gpu_tier} ({d.gres})",
            file=sys.stderr,
        )
        print(f"GRES={d.gres}")
        print(f"CONTEXT_LENGTH={d.context_length}")
        print(f"GPU_TIER={d.gpu_tier}")
        print(f"EST_VRAM_GB={d.effective_vram_gb}")
        print(f"MAX_CONTEXT={d.max_context}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
