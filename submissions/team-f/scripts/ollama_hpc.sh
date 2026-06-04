#!/usr/bin/env bash
# ollama_hpc.sh — per-job detached Ollama for RoboRoy on the HPC.
#
# Adapted (slimmed) from geo_harmonizer's
#   agent_tools/ollama_management/manage_ollama.sh  (serve-local / stop-local)
# at /hpc/compgen/projects/llm_GEO_project/.../geo_harmonizer. Same idea:
# start a detached `ollama serve` for the current SLURM job, point it at the
# shared model cache, and emit `export` lines the caller `eval`s. The caller
# owns teardown via `stop-local` (run it from a trap).
#
# Subcommands:
#   serve-local [--warmup-model TAG] [--keep-alive V]
#                    Start a detached server on a free port. Prints, on STDOUT,
#                    `export OLLAMA_HOST=...` and `export OLLAMA_BASE_URL=...`
#                    so the caller can:  eval "$(ollama_hpc.sh serve-local ...)"
#   stop-local       Kill the server started for this job (reads the env file).
#   status           Report whether this job's server is up.
#   pull TAG...      Start a temp server, pull model(s) into the shared cache,
#                    stop it. (Needs a GPU allocation.)
#
# Context length: export OLLAMA_CONTEXT_LENGTH *before* calling serve-local so
# the spawned `ollama serve` inherits it — otherwise Ollama falls back to its
# ~4096 VRAM default and silently truncates the prompt (geo failure taxonomy).
#
# Everything except the eval-able exports goes to STDERR: leaking anything else
# to STDOUT breaks the caller's `eval`.

set -euo pipefail

# Shared Ollama install (overridable). This is the lab's GPU-built Ollama with
# the model cache; it is a deployment path, not tool source, so it lives here
# rather than in roybot/.
OLLAMA_INSTALL_DIR="${OLLAMA_INSTALL_DIR:-/hpc/compgen/projects/ollama/ollama_run/analysis/dstoker}"
OLLAMA_BIN="${OLLAMA_BIN:-$OLLAMA_INSTALL_DIR/bin/ollama}"
OLLAMA_MODELS_DIR="${OLLAMA_MODELS:-$OLLAMA_INSTALL_DIR/ollama_models}"
JOB_ID="${SLURM_JOB_ID:-local}"
ENV_FILE="${TMPDIR:-/tmp}/roboroy_ollama_${JOB_ID}.env"

info() { echo "[ollama_hpc] $*" >&2; }
die()  { echo "[ollama_hpc] ERROR: $*" >&2; exit 1; }

check_binary() {
    [ -x "$OLLAMA_BIN" ] || OLLAMA_BIN="$(command -v ollama 2>/dev/null || true)"
    [ -n "$OLLAMA_BIN" ] && [ -x "$OLLAMA_BIN" ] || die "ollama binary not found (set OLLAMA_BIN or OLLAMA_INSTALL_DIR)"
}

# A free TCP port via the OS, with a tiny race window we accept for single-job use.
free_port() {
    python3 - <<'PY'
import socket
s = socket.socket()
s.bind(("127.0.0.1", 0))
print(s.getsockname()[1])
s.close()
PY
}

cmd_serve_local() {
    local warmup_model="" keep_alive=""
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --warmup-model) warmup_model="$2"; shift 2 ;;
            --keep-alive)   keep_alive="$2";   shift 2 ;;
            *) die "unknown serve-local flag: $1" ;;
        esac
    done
    [[ -n "$warmup_model" && -z "$keep_alive" ]] && keep_alive="-1"

    check_binary
    mkdir -p "$OLLAMA_MODELS_DIR"
    local port host_bind host_client home
    port="$(free_port)"
    host_bind="0.0.0.0:${port}"        # server listens on all interfaces
    host_client="127.0.0.1:${port}"    # clients connect on loopback
    home="${TMPDIR:-/tmp}/roboroy_ollama_home_${JOB_ID}_$$"
    mkdir -p "$home"

    info "starting ollama: bind=$host_bind client=$host_client models=$OLLAMA_MODELS_DIR ctx=${OLLAMA_CONTEXT_LENGTH:-default} warmup=${warmup_model:-none}"
    # nohup + setsid so the server outlives this script returning to the caller.
    # OLLAMA_CONTEXT_LENGTH (if exported by the caller) is inherited here.
    OLLAMA_HOME="$home" OLLAMA_HOST="$host_bind" OLLAMA_MODELS="$OLLAMA_MODELS_DIR" \
        ${keep_alive:+OLLAMA_KEEP_ALIVE="$keep_alive"} \
        nohup setsid "$OLLAMA_BIN" serve >"$home/server.log" 2>&1 </dev/null &
    local serve_pid=$!
    disown "$serve_pid" 2>/dev/null || true

    # Wait for the HTTP listener to bind.
    local up=0
    for _ in $(seq 1 60); do
        if curl -sf "http://${host_client}/api/tags" >/dev/null 2>&1; then up=1; break; fi
        kill -0 "$serve_pid" 2>/dev/null || die "ollama serve died on startup — see $home/server.log"
        sleep 1
    done
    [ "$up" = 1 ] || die "ollama serve did not bind within 60s — see $home/server.log"
    info "ollama up (pid=$serve_pid)"

    # Optional synchronous warmup: load the model into VRAM before returning so
    # the first real request doesn't race the lazy load.
    if [[ -n "$warmup_model" ]]; then
        info "warming up $warmup_model (this can take 30-300s for a cold load)..."
        curl -sf "http://${host_client}/api/generate" \
            -d "{\"model\":\"${warmup_model}\",\"prompt\":\"\",\"keep_alive\":${keep_alive:-\"-1\"}}" \
            >/dev/null 2>&1 || info "warmup request returned non-zero (model may still load on first use)"
    fi

    cat >"$ENV_FILE" <<EOF
export OLLAMA_HOME='$home'
export OLLAMA_HOST='$host_client'
export OLLAMA_BASE_URL='http://${host_client}'
export OLLAMA_MODELS='$OLLAMA_MODELS_DIR'
export OLLAMA_PID='$serve_pid'
EOF
    # The eval-able exports — STDOUT only.
    echo "export OLLAMA_HOST='$host_client'"
    echo "export OLLAMA_BASE_URL='http://${host_client}'"
}

cmd_stop_local() {
    [ -f "$ENV_FILE" ] || { info "no env file at $ENV_FILE — nothing to stop"; return 0; }
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    if [[ -n "${OLLAMA_PID:-}" ]] && kill -0 "$OLLAMA_PID" 2>/dev/null; then
        kill "$OLLAMA_PID" 2>/dev/null || true
        sleep 1
        kill -9 "$OLLAMA_PID" 2>/dev/null || true
        info "stopped ollama (pid=$OLLAMA_PID)"
    else
        info "ollama pid ${OLLAMA_PID:-?} not running"
    fi
    rm -f "$ENV_FILE"
}

cmd_status() {
    if [ -f "$ENV_FILE" ]; then
        # shellcheck disable=SC1090
        source "$ENV_FILE"
        if curl -sf "${OLLAMA_BASE_URL}/api/tags" >/dev/null 2>&1; then
            echo "up: ${OLLAMA_BASE_URL} (pid=${OLLAMA_PID:-?})"
        else
            echo "env file present but server not responding: ${OLLAMA_BASE_URL}"
        fi
    else
        echo "no per-job server (no $ENV_FILE)"
    fi
}

cmd_pull() {
    [ $# -ge 1 ] || die "usage: $0 pull <model> [model2 ...]"
    check_binary
    mkdir -p "$OLLAMA_MODELS_DIR"
    local port; port="$(free_port)"
    local home="${TMPDIR:-/tmp}/roboroy_ollama_pull_$$"
    mkdir -p "$home"
    OLLAMA_HOME="$home" OLLAMA_HOST="127.0.0.1:${port}" OLLAMA_MODELS="$OLLAMA_MODELS_DIR" \
        "$OLLAMA_BIN" serve >"$home/server.log" 2>&1 &
    local pid=$!
    sleep 5
    kill -0 "$pid" 2>/dev/null || { rm -rf "$home"; die "server failed to start (need a GPU srun?) — see $home/server.log"; }
    local rc=0
    for m in "$@"; do
        info "pulling $m ..."
        OLLAMA_HOST="127.0.0.1:${port}" OLLAMA_MODELS="$OLLAMA_MODELS_DIR" "$OLLAMA_BIN" pull "$m" || rc=1
    done
    kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; rm -rf "$home"
    return $rc
}

case "${1:-}" in
    serve-local) shift; cmd_serve_local "$@" ;;
    stop-local)  cmd_stop_local ;;
    status)      cmd_status ;;
    pull)        shift; cmd_pull "$@" ;;
    *) die "usage: $0 {serve-local [--warmup-model TAG] [--keep-alive V] | stop-local | status | pull TAG...}" ;;
esac
