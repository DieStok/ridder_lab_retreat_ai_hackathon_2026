#!/usr/bin/env bash
# submit_roboroy.sh — route a model to the smallest GPU that fits, then submit.
#
# Run from a submit node. Resolves MODEL's GGUF, estimates VRAM at CTX via
# roybot.gpu_router, picks the --gres tier + capped context length, and submits
# scripts/run_roboroy.sbatch with those values. Automatic for any pulled model.
#
#   ./scripts/submit_roboroy.sh                       # MODEL=qwen3.5:9b, CTX=8192
#   MODEL=gemma4:26b ./scripts/submit_roboroy.sh      # routes by size, no guessing
#   MODEL=qwen3.5:27b CTX=max ./scripts/submit_roboroy.sh
#
# First time only:  ./scripts/setup_gguf_parser.sh
#
# See docs/plans/2026-06-05-feat-auto-vram-gpu-routing-plan.md.

set -euo pipefail

cd "$(dirname "$0")/.."

# --- config ---------------------------------------------------------------
MODEL="${MODEL:-qwen3.5:9b}"   # small by default — the task is simple, big GPUs are contended
CTX="${CTX:-8192}"             # target context (or 'max' to use the GGUF's trained max)
REDUMP="${REDUMP:-1}"          # 1: refresh sacct; 0: reuse committed dump (for parallel runs)
SBATCH_TIME="${SBATCH_TIME:-01:00:00}"
SBATCH_MEM="${SBATCH_MEM:-16G}"
SBATCH_TMPSPACE="${SBATCH_TMPSPACE:-10G}"

# Deployment defaults (paths live in scripts, not tool source — monorepo rule #3).
export OLLAMA_INSTALL_DIR="${OLLAMA_INSTALL_DIR:-/hpc/compgen/projects/ollama/ollama_run/analysis/dstoker}"
export OLLAMA_MODELS="${OLLAMA_MODELS:-$OLLAMA_INSTALL_DIR/ollama_models}"

# Per-model output dir so parallel model runs don't clobber each other.
OUT_ROOT="${OUT_ROOT:-out_$(echo "$MODEL" | tr ':/' '__')}"

# --- preflight ------------------------------------------------------------
# logs/ and out/ must exist before sbatch: SLURM opens --output=logs/... before
# the job script's own mkdir runs, so a missing logs/ fails the job in seconds.
mkdir -p logs out
[ -x .venv/bin/python ] || { echo "[submit] .venv missing — see README (uv venv + uv pip install)" >&2; exit 1; }
if [ ! -x vendor_model_mem_tools/gguf-parser-go/bin/gguf-parser ]; then
    echo "[submit] gguf-parser missing — run: ./scripts/setup_gguf_parser.sh" >&2
    exit 1
fi

# --- route ----------------------------------------------------------------
echo "[submit] routing $MODEL @ ctx=$CTX ..."
ROUTE="$(.venv/bin/python -m roybot.gpu_router --model "$MODEL" --ctx "$CTX" --format sbatch)"
# Pull KEY=VALUE lines from the router.
GRES="$(echo "$ROUTE" | sed -n 's/^GRES=//p')"
CONTEXT_LENGTH="$(echo "$ROUTE" | sed -n 's/^CONTEXT_LENGTH=//p')"
GPU_TIER="$(echo "$ROUTE" | sed -n 's/^GPU_TIER=//p')"
[ -n "$GRES" ] && [ -n "$CONTEXT_LENGTH" ] || { echo "[submit] routing failed" >&2; exit 1; }

JOBTAG="$(echo "$MODEL" | tr ':/' '__')"
echo "[submit] $MODEL -> tier=$GPU_TIER gres=$GRES ctx=$CONTEXT_LENGTH out=$OUT_ROOT"

# --- submit ---------------------------------------------------------------
# --gres on the command line overrides the #SBATCH default in the script.
sbatch \
    --job-name="roboroy_${JOBTAG}_claude-code" \
    --gres="${GRES},tmpspace:${SBATCH_TMPSPACE}" \
    --time="$SBATCH_TIME" \
    --mem="$SBATCH_MEM" \
    --export=ALL,ROBOROY_DIR="$PWD",MODEL="$MODEL",CTX="$CONTEXT_LENGTH",OUT_ROOT="$OUT_ROOT",REDUMP="$REDUMP",OLLAMA_INSTALL_DIR="$OLLAMA_INSTALL_DIR",OLLAMA_MODELS="$OLLAMA_MODELS" \
    scripts/run_roboroy.sbatch
