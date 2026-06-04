#!/usr/bin/env python3
"""GGUF-native, SWA-aware model memory estimation.

Ported (gguf-parser path, near-verbatim) from geo_harmonizer's
``agent_tools/estimate_model_memory_usage.py`` at
``/hpc/compgen/projects/llm_GEO_project/harmonia_metadata_agent/analysis/dstoker/
geo_harmonizer``. The hf-mem fallback (for not-yet-downloaded / safetensors-only
models) was dropped: roboroy only ever estimates **local Ollama GGUF blobs**.

Estimator: **gguf-parser-go** (gpustack) — a prebuilt static binary (no Go
toolchain) that reads a local GGUF header offline (no network), is SWA-aware,
models flash-attention, and implements llama.cpp's actual VRAM formulas (~100 MiB
deviation from real serving). Fetch it with ``scripts/setup_gguf_parser.sh``.

CLI::

    python -m roybot.model_memory --gguf-path /path/to/model.gguf --ctx 8192
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path

# Repo root = parent of roybot/. The prebuilt gguf-parser binary lives under
# vendor_model_mem_tools/ (git-excluded; fetched by scripts/setup_gguf_parser.sh).
_REPO_ROOT = Path(__file__).resolve().parents[1]
GGUF_PARSER_BIN = (
    _REPO_ROOT / "vendor_model_mem_tools" / "gguf-parser-go" / "bin" / "gguf-parser"
)

_BYTES_PER_GIB = 1024**3

# gguf-parser treats --ctx-size 0 as "model max", not weights-only, so 0 is
# deliberately absent from any default grid.
DEFAULT_CTX_GRID: tuple[int, ...] = (8192,)


@dataclass
class MemoryPoint:
    """VRAM/RAM footprint at one context size."""

    ctx: int
    total_vram_gb: float  # sum(estimate.items[0].vrams[].nonuma) / 1024**3
    host_ram_gb: float | None = None  # estimate.items[0].ram.nonuma / 1024**3


@dataclass
class MemoryEstimate:
    """A weights footprint plus a VRAM curve over a context grid."""

    model_id: str
    weights_gb: float  # gguf-parser metadata.size / 1024**3 (NOT a ctx=0 run)
    max_context: int | None = None  # architecture.maximumContextLength
    points: list[MemoryPoint] = field(default_factory=list)
    source_tool: str = "gguf-parser-go"

    def vram_at(self, ctx: int) -> float | None:
        """Exact-or-nearest-not-exceeding VRAM lookup for tier routing.

        Returns the ``total_vram_gb`` of the point whose ctx is the largest
        that is ``<= ctx`` (or the smallest point if ``ctx`` is below the whole
        curve). ``None`` only when there are no points.
        """
        if not self.points:
            return None
        at_or_below = [p for p in self.points if p.ctx <= ctx]
        chosen = max(at_or_below, key=lambda p: p.ctx) if at_or_below else min(
            self.points, key=lambda p: p.ctx
        )
        return chosen.total_vram_gb

    def to_dict(self) -> dict:
        return asdict(self)


# --------------------------------------------------------------------------- #
# Pure JSON parsers — operate on a gguf-parser ``--json`` dict.
# --------------------------------------------------------------------------- #
def _weights_gb(data: dict) -> float:
    """Weight footprint from GGUF ``metadata.size`` (raw param bytes)."""
    return data["metadata"]["size"] / _BYTES_PER_GIB


def _vram_gb(data: dict) -> float:
    """Total device VRAM at the requested ctx, summed across GPU shards."""
    item = data["estimate"]["items"][0]
    return sum(v["nonuma"] for v in item["vrams"]) / _BYTES_PER_GIB


def _host_ram_gb(data: dict) -> float | None:
    item = data["estimate"]["items"][0]
    ram = (item.get("ram") or {}).get("nonuma")
    return ram / _BYTES_PER_GIB if ram is not None else None


def _n_ctx_train_from_json(data: dict) -> int | None:
    return (data.get("architecture") or {}).get("maximumContextLength")


# --------------------------------------------------------------------------- #
# Subprocess wrapper.
# --------------------------------------------------------------------------- #
def _run_gguf_parser(
    gguf_path: str | Path, ctx: int, *, flash_attention: bool = True
) -> dict:
    """Run the prebuilt gguf-parser binary at one ctx; return parsed JSON.

    Raises ``CalledProcessError`` on a non-zero exit — never falls back to a
    heuristic.
    """
    if not GGUF_PARSER_BIN.exists():
        raise FileNotFoundError(
            f"gguf-parser binary not found at {GGUF_PARSER_BIN}. "
            "Run scripts/setup_gguf_parser.sh once to fetch it."
        )
    cmd = [
        str(GGUF_PARSER_BIN),
        "--path", str(gguf_path),
        "--ctx-size", str(ctx),
        "--json",
    ]
    if flash_attention:
        cmd.append("--flash-attention")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise subprocess.CalledProcessError(
            proc.returncode, cmd, output=proc.stdout, stderr=proc.stderr
        )
    return json.loads(proc.stdout)


# --------------------------------------------------------------------------- #
# Estimator.
# --------------------------------------------------------------------------- #
def _clamp_grid(ctx_grid: Sequence[int], n_ctx_train: int | None) -> list[int]:
    """Clamp each grid point to ``min(g, n_ctx_train)`` and de-duplicate.

    Above-trained points collapse onto ``n_ctx_train`` (gguf-parser would
    silently extrapolate otherwise). Always yields at least one point.
    """
    if n_ctx_train is None:
        return sorted({int(g) for g in ctx_grid})
    return sorted({min(int(g), int(n_ctx_train)) for g in ctx_grid})


def estimate_memory(
    *,
    gguf_path: str | Path,
    n_ctx_train: int | None = None,
    ctx_grid: Sequence[int] = DEFAULT_CTX_GRID,
    flash_attention: bool = True,
    model_id: str | None = None,
) -> MemoryEstimate:
    """Estimate VRAM over a context grid (clamped to the GGUF's trained ctx).

    Reads ``maximumContextLength`` from the GGUF in a single cheap probe when
    ``n_ctx_train`` is not supplied, then estimates VRAM at each (clamped) grid
    point. On tool failure the underlying ``CalledProcessError`` propagates.
    """
    gguf_path = Path(gguf_path)

    train = n_ctx_train
    probe_max = None
    if train is None:
        probe = _run_gguf_parser(
            gguf_path, min(int(g) for g in ctx_grid), flash_attention=flash_attention
        )
        train = _n_ctx_train_from_json(probe)
        probe_max = train

    points: list[MemoryPoint] = []
    weights_gb: float | None = None
    for ctx in _clamp_grid(ctx_grid, train):
        data = _run_gguf_parser(gguf_path, ctx, flash_attention=flash_attention)
        if weights_gb is None:
            weights_gb = _weights_gb(data)
        if probe_max is None:
            probe_max = _n_ctx_train_from_json(data)
        points.append(
            MemoryPoint(
                ctx=ctx, total_vram_gb=_vram_gb(data), host_ram_gb=_host_ram_gb(data)
            )
        )

    return MemoryEstimate(
        model_id=model_id or gguf_path.name,
        weights_gb=weights_gb if weights_gb is not None else 0.0,
        max_context=train if train is not None else probe_max,
        points=points,
        source_tool="gguf-parser-go",
    )


# --------------------------------------------------------------------------- #
# CLI.
# --------------------------------------------------------------------------- #
def _build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--gguf-path", type=Path, required=True,
                    help="local GGUF blob to estimate")
    ap.add_argument("--ctx", "--ctx-grid", dest="ctx_grid",
                    default=",".join(map(str, DEFAULT_CTX_GRID)),
                    help="context size, or comma-separated grid")
    ap.add_argument("--n-ctx-train", type=int, default=None,
                    help="trained context length (clamps the grid)")
    ap.add_argument("--no-flash-attention", action="store_true",
                    help="disable flash-attention (default: on, matches serving)")
    ap.add_argument("--model-id", default=None)
    return ap


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    grid = tuple(int(x) for x in args.ctx_grid.split(",") if x.strip())
    est = estimate_memory(
        gguf_path=args.gguf_path,
        n_ctx_train=args.n_ctx_train,
        ctx_grid=grid,
        flash_attention=not args.no_flash_attention,
        model_id=args.model_id,
    )
    json.dump(est.to_dict(), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
