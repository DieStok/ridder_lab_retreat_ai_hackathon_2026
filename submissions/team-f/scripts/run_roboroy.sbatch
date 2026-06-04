#!/bin/bash
#SBATCH --job-name=roboroy_claude-code
#SBATCH --account=compgen
#SBATCH --partition=gpu
# Pin a big-VRAM A100 MIG slice (79 GB) so a 26B model loads without OOM —
# a 16 GB V100 would be too small. Override with e.g. --gres=gpu:1 + a smaller
# MODEL if these are busy.
#SBATCH --gres=gpu:7g.79gb:1,tmpspace:10G
#SBATCH --time=02:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err
#
# run_roboroy.sbatch — the full RoboRoy pipeline on the HPC.
#
#   1. dump a week of sacct for dstoker        -> EXAMPLE_DIETER_05_06_2026.txt
#   2. start a per-job Ollama (GPU)            -> OLLAMA_BASE_URL  (ollama_hpc.sh)
#   3. roybot: sacct -> stats -> Ollama roast  -> out/<user>/*.md + stats.json
#   4. Piper TTS                               -> out/<user>/*.wav
#   5. stop Ollama (trap)
#
# Processes Dieter (the headline roast, addressed as "Dieter - Herder of Claude
# Code") plus the other committed example dumps. Empty dumps are skipped.
#
# Submit from submissions/team-f/:  sbatch scripts/run_roboroy.sbatch
#
# Smaller model on an un-contended GPU, in parallel with the big run (writes to
# out_qwen9b/ and reuses the committed dump so the two jobs don't collide):
#   OUT_ROOT=out_qwen9b MODEL=qwen3.5:9b REDUMP=0 \
#     sbatch --job-name=roboroy_qwen9b_claude-code --gres=gpu:2g.20gb:1,tmpspace:10G \
#            --time=01:00:00 --mem=16G scripts/run_roboroy.sbatch

set -euo pipefail

# --- config ---------------------------------------------------------------
MODEL="${MODEL:-gemma4:26b}"          # non-reasoning -> clean spoken text. Override freely.
CTX="${CTX:-8192}"                    # Ollama context window (avoids the ~4096 truncation default)
VOICE_MODEL="${VOICE_MODEL:-models/en_GB-northern_english_male-medium.onnx}"
DIETER_NAME="Dieter - Herder of Claude Code"
# OUT_ROOT lets several model runs coexist (e.g. out/ for gemma4:26b, out_qwen9b/
# for qwen3.5:9b) without clobbering each other. REDUMP=0 reuses the already
# committed EXAMPLE_DIETER dump instead of re-running sacct — use it for a second
# parallel run so the two jobs don't race on the same example file.
OUT_ROOT="${OUT_ROOT:-out}"
REDUMP="${REDUMP:-1}"

# Run from the submission dir regardless of where sbatch was invoked.
cd "$(dirname "$0")/.."
TEAM_DIR="$PWD"
mkdir -p logs "$OUT_ROOT"

# --- venv: puts roybot's deps AND the `piper` binary on PATH --------------
[ -x .venv/bin/python ] || { echo "[roboroy] .venv missing — run: uv venv .venv && uv pip install ollama python-dotenv piper-tts" >&2; exit 1; }
# shellcheck disable=SC1091
source .venv/bin/activate

# Pin thread counts so onnxruntime (Piper) doesn't spam pthread_setaffinity
# warnings on this multi-socket node.
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-4}"

# --- 1. dump a week of sacct for dstoker ----------------------------------
if [ "$REDUMP" = 1 ]; then
    echo "[roboroy] dumping a week of sacct for dstoker ..."
    DUMP="$(SACCT_USERS=dstoker SACCT_DAYS=7 SACCT_OUT_DIR="$TEAM_DIR/.sacct_tmp" bash scripts/collect_sacct.sh | tail -1)"
    cp "$DUMP" EXAMPLE_DIETER_05_06_2026.txt
    rm -rf "$TEAM_DIR/.sacct_tmp"
    echo "[roboroy] wrote EXAMPLE_DIETER_05_06_2026.txt ($(( $(wc -l < EXAMPLE_DIETER_05_06_2026.txt) - 1 )) jobs)"
else
    echo "[roboroy] REDUMP=0 — reusing committed EXAMPLE_DIETER_05_06_2026.txt ($(( $(wc -l < EXAMPLE_DIETER_05_06_2026.txt) - 1 )) jobs)"
fi

# --- 2. per-job Ollama (context length exported BEFORE serve-local) --------
export OLLAMA_CONTEXT_LENGTH="$CTX"
eval "$(scripts/ollama_hpc.sh serve-local --warmup-model "$MODEL" --keep-alive -1)"
trap 'scripts/ollama_hpc.sh stop-local || true' EXIT INT TERM
[ -n "${OLLAMA_BASE_URL:-}" ] || { echo "[roboroy] serve-local failed to export OLLAMA_BASE_URL" >&2; exit 1; }
echo "[roboroy] Ollama at $OLLAMA_BASE_URL, model=$MODEL, ctx=$CTX"

# --- helper: run roybot on one example dump -------------------------------
run_one() {
    local dump="$1" tag="$2"; shift 2   # remaining args -> extra roybot flags (e.g. --rename)
    local rows; rows=$(( $(wc -l < "$dump") - 1 ))
    if [ "$rows" -le 0 ]; then
        echo "[roboroy] $tag: 0 jobs in window — skipping"
        return 0
    fi
    echo "[roboroy] $tag: roasting $rows jobs ..."
    python -m roybot --sacct "$dump" --out "$OUT_ROOT/$tag" \
        --with-llm --no-fallback \
        --with-audio --engine piper --piper-model "$VOICE_MODEL" \
        --model "$MODEL" --num-ctx "$CTX" "$@" \
        || echo "[roboroy] $tag: roybot returned non-zero"
}

# --- 3-4. the headline roast + the rest -----------------------------------
run_one EXAMPLE_DIETER_05_06_2026.txt dieter --rename "dstoker=${DIETER_NAME}"

for f in EXAMPLE_AIRANPOUR_05_06_2026.txt EXAMPLE_CFIORENZANI_05_06_2026.txt \
         EXAMPLE_LBARBADILLAMARTINEZ_05_06_2026.txt EXAMPLE_ATSAKALI_05_06_2026.txt \
         EXAMPLE_RSTRAVER_05_06_2026.txt; do
    [ -f "$f" ] || continue
    tag="$(echo "$f" | sed -E 's/^EXAMPLE_(.*)_05_06_2026\.txt$/\1/' | tr '[:upper:]' '[:lower:]')"
    run_one "$f" "$tag"
done

# --- 5. summary -----------------------------------------------------------
echo "[roboroy] ===== artifacts ($OUT_ROOT) ====="
find "$OUT_ROOT" -maxdepth 2 -type f \( -name '*.md' -o -name '*.wav' -o -name 'standup.txt' \) | sort
echo "[roboroy] done."
