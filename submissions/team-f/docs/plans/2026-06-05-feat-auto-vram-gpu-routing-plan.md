---
title: Auto VRAM/GPU-tier + context-length routing for RoboRoy
type: feat
status: completed
date: 2026-06-05
scope: hackathon/submissions/team-f (roybot)
branch: hackathon submodule `main`
---

# Auto VRAM/GPU-tier + context-length routing for RoboRoy

## Overview

Port geo_harmonizer's GGUF-native VRAM estimation + GPU-tier routing into roboroy
so that **any** Ollama model self-routes to the **smallest GPU slice that fits**,
and so the Ollama context length is resolved automatically from the model's GGUF
instead of being hand-set. New models need zero config: give a tag, the launcher
parses its GGUF, estimates VRAM at the chosen context, picks the `--gres` tier,
and submits.

This is a deliberate rework, done **after** the manual `qwen3.5:9b` run was
committed (commit `a51f58d`), so routing becomes automatic from here on.

## Problem statement / motivation

- `scripts/run_roboroy.sbatch` hardcodes `--gres=gpu:7g.79gb:1` "so a 26B model
  loads without OOM." That 79 GB A100 MIG slice is the **most contended** GPU on
  the cluster (`sinfo`: all `7g.79gb` nodes `mix`; `2g.20gb` has 4 idle).
- The assumption is also **wrong at our context size**: measured with
  `gguf-parser` v0.24.0 at ctx=8192, `gemma4:26b` needs only **14.4 GB** — it
  fits the idle `2g.20gb` (20 GB) tier. We were queuing for a huge GPU we don't
  need.
- For the smaller `qwen3.5:9b` run we picked the GPU tier **by hand**. That
  doesn't scale: each new model means another manual VRAM guess.
- geo_harmonizer already solved this (feature "model max context & auto VRAM
  routing"): a prebuilt `gguf-parser-go` binary reads the GGUF header offline
  (SWA-aware, ~100 MiB accuracy) and a tier table maps VRAM → SLURM `--gres`.
  Reuse it rather than reinvent.

## Proposed solution

Routing is decided at **submit time** (login/submit node), because `#SBATCH
--gres` must be fixed before submission. A thin launcher resolves the model's
GGUF, estimates VRAM at the target context, maps to a GPU tier, and calls
`sbatch --gres=<tier> ... run_roboroy.sbatch`. `run_roboroy.sbatch` keeps working
standalone (its `#SBATCH` defaults remain a safe fallback).

Five pieces, all under `submissions/team-f/`:

1. **Vendored estimator binary** — `gguf-parser-go` v0.24.0
   (`vendor_model_mem_tools/gguf-parser-go/bin/gguf-parser`, gitignored) plus
   `scripts/setup_gguf_parser.sh` to fetch it idempotently (one-time, needs
   internet on the submit node; the binary itself runs fully offline thereafter).
2. **`roybot/model_memory.py`** — port of geo's
   `agent_tools/estimate_model_memory_usage.py` (copied with a one-line
   attribution header). Runs `gguf-parser --path <gguf> --ctx-size <n> --json
   --flash-attention`; returns weights GB, a VRAM curve, and the GGUF's
   `maximumContextLength`.
3. **`roybot/gpu_router.py`** — roboroy glue (the part geo had tangled in its
   sweep CLI):
   - Ollama tag → GGUF blob resolver (manifest `application/vnd.ollama.image.model`
     layer digest → `blobs/sha256-<hex>`).
   - The tier table (ported ceilings 20/24/79) mapped to **this cluster's**
     `--gres` strings.
   - `route(model, ctx)` → `{gres, gpu_tier, context_length, est_vram_gb,
     max_context}` with a documented safety headroom factor.
   - A `__main__` CLI the launcher consumes (`--format sbatch|json`).
4. **`scripts/submit_roboroy.sh`** — the automatic entry point: route, print the
   decision, `sbatch` with the chosen `--gres` and resolved `CTX`.
5. **Docs + tests** — README "Automatic GPU routing" section, `.env.example`
   (`OLLAMA_MODELS`, `ROBOROY_VRAM_HEADROOM`), and pytest cases for the tier
   table, context capping, and the Ollama→GGUF resolver.

## Technical approach

### Dataflow

```
submit_roboroy.sh  (login/submit node)
  │  MODEL=gemma4:26b  CTX=8192  OUT_ROOT=out
  ▼
roybot.gpu_router.route(MODEL, CTX)
  ├─ ollama_gguf_path(MODEL)         manifest -> model-layer digest -> blob
  ├─ model_memory.estimate_memory(gguf, ctx)   gguf-parser --json   (offline)
  │     -> est_vram_gb, max_context (architecture.maximumContextLength)
  ├─ context_length = ctx=='max' ? max_context : min(CTX, max_context)   (cap)
  ├─ effective = ceil(est_vram_gb * HEADROOM)
  └─ gres = tier_for(effective):  <=20 2g.20gb | <=24 quadro_rtx_6000 | <=79 7g.79gb | else error
  ▼
sbatch --gres=<gres>,tmpspace:10G --job-name=roboroy_<model>_claude-code \
       <MODEL/CTX/OUT_ROOT as env>  scripts/run_roboroy.sbatch
  ▼
run_roboroy.sbatch  (unchanged pipeline: serve-local -> roast -> Piper -> stop)
```

### Tier table (ported from geo, mapped to this cluster)

| VRAM ceiling | geo tier name | this cluster `--gres` | physical |
|---|---|---|---|
| ≤ 20 GB | `gpu_small` | `gpu:2g.20gb:1` | A100 MIG 20 GB (4 idle) |
| ≤ 24 GB | `gpu_large` | `gpu:quadro_rtx_6000:1` | RTX 6000 24 GB |
| ≤ 79 GB | `gpu_extra_large` | `gpu:7g.79gb:1` | A100 MIG 79 GB |
| > 79 GB | — | pre-flight error (do not submit) | — |

Constants ported verbatim: `_GPU_SMALL_CEILING_GB=20`, `_GPU_LARGE_CEILING_GB=24`,
`_GPU_EXTRA_LARGE_CEILING_GB=79`.

### Safety headroom (roboroy-specific decision)

geo trusts the raw `gguf-parser` number because it self-heals against *measured*
VRAM curves in a registry we don't have here. Standalone, `gguf-parser`'s device
figure excludes Ollama's compute/graph buffer (observed: it reports 3.85 GB for
`qwen3.5:9b` where Ollama actually uses ~7 GB). The tiers are coarse (20/24/79),
so this rarely changes the routing — but to avoid an OOM on a boundary model we
apply `effective = ceil(est_vram * ROBOROY_VRAM_HEADROOM)` with **default 1.3**,
overridable via env. The safe failure mode (round a borderline model up to the
next, larger, still-cheaper-than-79 GB tier) is preferred. Documented in source.

### Validated routing (gguf-parser v0.24.0, ctx=8192, this store)

```
qwen3.5:4b    2.84 GB  -> gpu_small      gpt-oss:20b   13.17 GB -> gpu_small
qwen3.5:9b    3.85 GB  -> gpu_small      qwen3.5:27b   11.51 GB -> gpu_small
gemma4:26b   14.43 GB  -> gpu_small      gemma4:31b    17.77 GB -> gpu_small
```
All fit `gpu_small` at 8k ctx — i.e. routing keeps roboroy off the contended
79 GB GPUs entirely for our workload, which is the whole point.

### No hardcoded paths (repo rule #3)

`gpu_router` reads the model store from `OLLAMA_MODELS` (the same var
`ollama_hpc.sh` uses), falling back to the documented lab default
`$OLLAMA_INSTALL_DIR/ollama_models`. The vendored binary path is derived from the
module location. No absolute paths in `roybot/*.py`.

### Files to add / change

| File | Action |
|---|---|
| `vendor_model_mem_tools/gguf-parser-go/bin/gguf-parser` | **add** (vendored, gitignored) |
| `scripts/setup_gguf_parser.sh` | **add** (idempotent fetch of the binary) |
| `roybot/model_memory.py` | **add** (port of geo estimator + attribution) |
| `roybot/gpu_router.py` | **add** (resolver + tier table + route() + CLI) |
| `scripts/submit_roboroy.sh` | **add** (routing launcher) |
| `scripts/run_roboroy.sbatch` | **edit** (header note: prefer the launcher; defaults stay as fallback) |
| `tests/test_roybot.py` | **edit** (tier/cap/resolver cases) |
| `.gitignore` | **edit** (`vendor_model_mem_tools/`) |
| `README.md` | **edit** ("Automatic GPU routing" section) |
| `.env.example` | **edit** (`OLLAMA_MODELS`, `ROBOROY_VRAM_HEADROOM`) |

## System-wide impact

- **Interaction graph:** routing is pure submit-time computation feeding one
  `sbatch` call. The in-job pipeline (`ollama_hpc.sh serve-local` → roybot →
  Piper → `trap stop-local`) is untouched. `CTX` already flows to both
  `OLLAMA_CONTEXT_LENGTH` and `--num-ctx`; the launcher just sets it from the
  GGUF max instead of a constant.
- **Error propagation / pre-flight:** binary missing → point at
  `setup_gguf_parser.sh`; model not pulled / blob absent → error listing
  available tags from the store; estimate > 79 GB → **refuse to submit** (no
  silent OOM). All before any GPU is requested.
- **State lifecycle:** no new persistent state. Standalone `sbatch
  run_roboroy.sbatch` still works (defaults unchanged) — launcher is additive.
- **Parity:** the manual path (`MODEL=… sbatch --gres=… run_roboroy.sbatch`) and
  the routed path share the same sbatch; the launcher only computes the flags.
- **Integration scenarios unit tests miss:** (1) GGUF present but Ollama not
  running — routing must not need a live server (it reads the blob offline ✓).
  (2) context capped below `--num-ctx` request — verify roybot still runs. (3)
  headroom pushes a near-boundary model up a tier — verify it submits, doesn't
  error.

## Acceptance criteria

### Functional
- [x] `scripts/setup_gguf_parser.sh` fetches `gguf-parser` v0.24.0 to the vendor
      dir and is a no-op when already present; binary is gitignored.
- [x] `python -m roybot.gpu_router --model qwen3.5:9b --ctx 8192` prints
      `--gres=gpu:2g.20gb:1` and `CTX=8192` (sbatch format) / valid JSON.
- [x] `gemma4:26b --ctx 8192` routes to `gpu_small` (proves the contention win).
- [x] Requesting `--ctx max` resolves to the GGUF's `maximumContextLength`; a
      `--ctx` above the max is **capped** to the max.
- [x] An impossibly large model/context (> 79 GB) exits non-zero **without**
      submitting.
- [x] `scripts/submit_roboroy.sh` submits `run_roboroy.sbatch` with the routed
      `--gres` and resolved `CTX`, printing the routing decision.
- [x] `run_roboroy.sbatch` still runs standalone (regression).

### Non-functional / quality
- [x] No hardcoded absolute paths in `roybot/*.py` (store via `OLLAMA_MODELS` +
      documented default).
- [x] geo_harmonizer attribution comment present in `model_memory.py`.
- [x] No new Python package deps (stdlib only); the only new dependency is the
      vendored binary, documented in README + `.env.example`.
- [x] Shared `hackathon/pyproject.toml` untouched.
- [x] `tests/test_roybot.py` covers tier mapping, context cap, and Ollama→GGUF
      resolution; full suite passes.
- [x] README + `.env.example` updated in the same change set (repo rule #5).

## Dependencies & risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Submit node has no internet to fetch the binary | Low | `setup_gguf_parser.sh` is one-time; binary runs offline after. Document the URL; can be fetched on a transfer node and copied. |
| gguf-parser undercounts real Ollama VRAM near a tier boundary → OOM | Med | `ROBOROY_VRAM_HEADROOM` (default 1.3) + coarse tiers; safe failure rounds up. |
| Ollama store path differs per deployment | Low | `OLLAMA_MODELS` env override; default mirrors `ollama_hpc.sh`. |
| `gguf-parser` JSON schema changes across versions | Low | Pin v0.24.0 in the setup script; parser reads documented fields. |
| Non-`library/` model tags (hf.co/…, batiai/…) have different manifest paths | Low | Resolver walks `manifests/**/<name>/<tag>`; fall back to a clear error. |

## Verification plan
1. `setup_gguf_parser.sh`; confirm `gguf-parser --version` = v0.24.0.
2. `python -m roybot.gpu_router` for qwen3.5:9b, gemma4:26b, and a `--ctx max`
   case; confirm tiers + capping match the table above.
3. `pytest` green.
4. `submit_roboroy.sh MODEL=qwen3.5:9b` (REDUMP=0, OUT_ROOT=out_route_test) —
   confirm it lands on a `2g.20gb` slice and produces a roast + `.wav`.

## Sources & references

### Internal
- geo estimator: `…/geo_harmonizer/agent_tools/estimate_model_memory_usage.py`
- geo tier router: `…/geo_harmonizer/src/core/sweep/cli.py` (`_gpu_tier_for`,
  ceilings) and `src/core/sweep/model_memory.py` (`expected_vram_gb`)
- geo context resolution: `…/geo_harmonizer/src/core/inference/ollama.py`
- roboroy pipeline: `scripts/run_roboroy.sbatch`, `scripts/ollama_hpc.sh`
- prior plan: `docs/plans/2026-06-04-feat-roboroy-hpc-ollama-shaming-pipeline-plan.md`
- monorepo rules: `lab_ai_automation/.claude/CLAUDE.md` (rule #3 paths, copy-with-attribution)

### External
- gguf-parser-go (gpustack), v0.24.0:
  https://github.com/gpustack/gguf-parser-go/releases/tag/v0.24.0

### Environment facts (verified this session)
- gguf-parser v0.24.0 linux-amd64 fetched & working on `n0073`; reads Ollama
  blobs at `/hpc/compgen/projects/ollama/ollama_run/analysis/dstoker/ollama_models`.
- Cluster GPU gres: `2g.20gb` (20 GB, 4 idle), `quadro_rtx_6000` (24 GB),
  `7g.79gb` (79 GB, contended), `tesla_v100-pcie-16gb` (16 GB).
- System `python3` is pre-3.7; use `.venv/bin/python` (3.11).
