#!/usr/bin/env bash
# collect_sacct.sh — dump last N days of SLURM accounting data to a file.
#
# Designed to live on an HPC submit node and run from cron. Writes a
# timestamped, atomic `.txt` file that roybot can ingest with `--sacct PATH`.
#
# Configure via env vars (all optional):
#   SACCT_DAYS        lookback window in days  (default: 7)
#   SACCT_ACCOUNT     SLURM account to filter  (default: compgen)
#   SACCT_OUT_DIR     directory for dumps      (default: $PWD/sacct_dumps)
#   SACCT_USERS       comma-separated user list (default: all users on account)
#
# Output: prints the absolute path of the dump to stdout. Exits non-zero
# if `sacct` is missing or fails.

set -euo pipefail

DAYS="${SACCT_DAYS:-7}"
ACCOUNT="${SACCT_ACCOUNT:-compgen}"
OUT_DIR="${SACCT_OUT_DIR:-$PWD/sacct_dumps}"
USERS="${SACCT_USERS:-}"

# Fail loudly on submit nodes that don't have sacct (i.e. anything but HPC).
if ! command -v sacct >/dev/null 2>&1; then
    echo "[collect_sacct] sacct not on PATH — this script must run on a SLURM submit node" >&2
    exit 1
fi

mkdir -p "$OUT_DIR"
STAMP="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
OUT_FILE="$OUT_DIR/sacct_${STAMP}.txt"
TMP_FILE="${OUT_FILE}.partial"

# Field list mirrors what roybot/data.py expects. Keep these in sync.
FIELDS="JobID,User,JobName,Partition,State,AllocCPUS,ReqMem,Timelimit,ElapsedRaw,CPUTimeRaw,MaxRSS,ReqTRES,AllocTRES,ExitCode"

SACCT_ARGS=(
    -X                              # one row per job, not per step
    --starttime="now-${DAYS}days"
    --format="$FIELDS"
    --parsable2
    --noconvert                     # keep raw bytes/seconds, no auto-humanise
)

if [ -n "$USERS" ]; then
    # Explicit user list wins over account filter.
    SACCT_ARGS+=(--user="$USERS")
elif [ -n "$ACCOUNT" ]; then
    SACCT_ARGS+=(--accounts="$ACCOUNT")
else
    # Whole cluster — almost never what you want, but allowed.
    SACCT_ARGS+=(-a)
fi

sacct "${SACCT_ARGS[@]}" > "$TMP_FILE"
mv "$TMP_FILE" "$OUT_FILE"

echo "$OUT_FILE"
