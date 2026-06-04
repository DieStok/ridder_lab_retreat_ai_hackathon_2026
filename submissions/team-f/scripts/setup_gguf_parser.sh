#!/usr/bin/env bash
# setup_gguf_parser.sh — fetch the gguf-parser-go binary used for VRAM routing.
#
# One-time setup (needs internet on the node you run it on — a submit/transfer
# node is fine). The binary itself runs fully offline afterwards. Idempotent:
# a no-op if the pinned version is already present.
#
# Used by roybot.model_memory / roybot.gpu_router. See
# docs/plans/2026-06-05-feat-auto-vram-gpu-routing-plan.md.

set -euo pipefail

VERSION="${GGUF_PARSER_VERSION:-v0.24.0}"
ARCH="${GGUF_PARSER_ARCH:-linux-amd64}"
URL="https://github.com/gpustack/gguf-parser-go/releases/download/${VERSION}/gguf-parser-${ARCH}"

cd "$(dirname "$0")/.."
DEST_DIR="vendor_model_mem_tools/gguf-parser-go/bin"
DEST="$DEST_DIR/gguf-parser"

if [ -x "$DEST" ] && "$DEST" --version 2>/dev/null | grep -q "$VERSION"; then
    echo "[setup_gguf_parser] $VERSION already present at $DEST"
    exit 0
fi

mkdir -p "$DEST_DIR"
echo "[setup_gguf_parser] fetching $URL"
curl -fsSL -o "$DEST" "$URL"
chmod +x "$DEST"
echo "[setup_gguf_parser] installed: $("$DEST" --version 2>&1 | head -1) -> $DEST"
