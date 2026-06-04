---
title: RoboRoy HPC Ollama sacct-shaming pipeline
type: feat
status: active
date: 2026-06-04
scope: hackathon/submissions/team-f (roybot)
branch: hackathon submodule `main`
---

# RoboRoy — HPC Ollama sacct-shaming pipeline

## Overview

Wire the existing **roybot** ("RoboRoy") submission so it runs end-to-end **on the
HPC** against a real week of SLURM accounting data and produces a spoken roast.
Today roybot is laptop-shaped: it reads `sacct --parsable2`, talks to whatever
`OLLAMA_BASE_URL` points at, and renders audio with macOS `say` or local `piper`.
This plan adds the HPC plumbing — a per-job detached Ollama server (the
geo_harmonizer pattern), an isolated `uv` venv with the Piper voice model, a real
example data file, and an `sbatch` job that runs the whole pipeline and emits an
audio clip that addresses the user as **"Dieter - Herder of Claude Code"**.

**Key constraint decided by the user:** roybot's code is built around `sacct`
(`roybot/data.py` parses `sacct --parsable2`). The user said *"I said seff, the
code uses sacct — do what the code says."* So this plan uses the **sacct**
pipeline throughout. The example file keeps the requested name
(`EXAMPLE_DIETER_05_06_2026.txt`) but holds `sacct --parsable2` output.

## Problem statement / motivation

- RoboRoy has never been run against real cluster data or the lab's real Ollama
  install. The `PROPOSAL.md` explicitly wants "a roast aimed at the worst
  offender … and an audio clip we can play at the actual stand-up," and notes the
  HPC has **no internet** for LLM calls — so the LLM must be the locally-installed
  Ollama, reached via a GPU `sbatch` job.
- There is no documented, repeatable way to point roybot at the HPC Ollama. The
  geo_harmonizer project already solved "detached Ollama inside an sbatch job"
  with `agent_tools/ollama_management/manage_ollama.sh` (`serve-local` /
  `stop-local`). RoboRoy should mirror that organisation rather than reinvent it.
- The audio path on Linux can only be Piper (`say` is macOS-only), and Piper +
  its voice model are deliberately **not** in the shared `hackathon/pyproject.toml`
  (the README forbids editing it). They need an isolated, untracked venv.

## Proposed solution

Four cohesive pieces, all under `submissions/team-f/`:

1. **Example data (`EXAMPLE_DIETER_05_06_2026.txt`)** — a real `sacct --parsable2`
   dump of user `dstoker`'s last 7 days, committed as the canonical example input
   (alongside the existing 5-row `sample_sacct.txt`).
2. **HPC Ollama wiring** — a slim `scripts/ollama_hpc.sh` adapted from
   geo_harmonizer's `manage_ollama.sh` (`serve-local` / `stop-local` / `status`),
   plus a `--ollama-host` CLI option on roybot for explicit override. roybot's
   `llm.py` already honours `OLLAMA_BASE_URL`, so wiring is thin.
3. **Isolated venv + Piper voice** — an untracked `team-f/.venv` (uv) with
   `ollama`, `python-dotenv`, `piper-tts`, and a downloaded British Piper voice
   `.onnx` (+ `.onnx.json`) under the already-gitignored `models/`.
4. **The sbatch job (`scripts/run_roboroy.sbatch`)** — a GPU job that: dumps the
   week's sacct to `EXAMPLE_DIETER_05_06_2026.txt`, starts Ollama via `serve-local`
   (with a `trap … stop-local`), runs roybot with `--with-llm --with-audio
   --engine piper` and a **display-name override** so the roast addresses
   "Dieter - Herder of Claude Code", saves the text, and renders the `.wav`.

A small, general roybot feature — `--rename USER=NAME` (display name used in
prompts/reports, while output filenames stay keyed on the SLURM username) — is the
clean way to make the roast say "Dieter - Herder of Claude Code" without
contaminating filenames or hardcoding a name in the tool.

## Technical approach

### Architecture / dataflow

```
sbatch (partition=gpu, 1 GPU)
  │
  ├─ 1. collect_sacct.sh  (SACCT_USERS=dstoker, 7 days)
  │        └─► EXAMPLE_DIETER_05_06_2026.txt   [sacct --parsable2]
  │
  ├─ 2. eval "$(scripts/ollama_hpc.sh serve-local --warmup-model $MODEL)"
  │        └─► detached `ollama serve` on this node
  │            exports OLLAMA_BASE_URL=http://<host:port>
  │        trap 'scripts/ollama_hpc.sh stop-local' EXIT INT TERM
  │
  ├─ 3. uv run python -m roybot \
  │        --sacct EXAMPLE_DIETER_05_06_2026.txt \
  │        --with-llm --with-audio --engine piper \
  │        --piper-model models/<voice>.onnx \
  │        --rename 'dstoker=Dieter - Herder of Claude Code' \
  │        --out out/
  │     roybot:  data.py → analyze.py → llm.py (Ollama) → reports.py → tts.py
  │        └─► out/user_dstoker.md      (roast + serious text)   [TEXT captured]
  │        └─► out/user_dstoker.wav     (Piper roast clip)       [AUDIO exists]
  │        └─► out/standup.txt / standup.wav / stats.json
  │
  └─ 4. stop-local (via trap)
```

### Component details

#### A. Example data file — `EXAMPLE_DIETER_05_06_2026.txt`
- Reuse the existing `scripts/collect_sacct.sh` with `SACCT_USERS=dstoker
  SACCT_DAYS=7`, then copy/rename its output to `EXAMPLE_DIETER_05_06_2026.txt`
  in the team-f root.
- Format = `sacct --parsable2` with the field list `data.py` expects
  (`JobID,User,JobName,Partition,State,AllocCPUS,ReqMem,Timelimit,ElapsedRaw,
  CPUTimeRaw,MaxRSS,ReqTRES,AllocTRES,ExitCode`). `--noconvert` keeps raw units.
- **Edge case:** if `dstoker` has zero jobs in the last 7 days, widen the window
  (e.g. 30 days) so the example is non-empty, and note the actual window in a
  one-line header comment is NOT possible (sacct header must stay parseable) — so
  instead record the window in the commit message / README, not the file.
- Committed to the repo (user explicitly asked). It contains only the user's own
  job metadata.

#### B. HPC Ollama wiring — `scripts/ollama_hpc.sh`
- Adapted from `…/geo_harmonizer/agent_tools/ollama_management/manage_ollama.sh`
  (leave a one-line attribution comment at the top, per monorepo convention).
- Subcommands needed:
  - `serve-local [--warmup-model M] [--keep-alive N]` — pick a free port, start a
    **detached** `ollama serve` bound to `127.0.0.1:<port>` on the current node,
    poll `/api/tags` until the listener binds, optionally warm the model, then
    print `export OLLAMA_BASE_URL=http://127.0.0.1:<port>` (and `OLLAMA_HOST`) on
    stdout for the caller to `eval`. Write a small env/pid file under `$TMPDIR`.
  - `stop-local` — kill the server started for this job (read pid file).
  - `status` — report whether a server is up.
- Finds the ollama binary already on PATH at
  `/hpc/compgen/projects/ollama/ollama_run/analysis/dstoker/bin/ollama`.
- roybot change: add `--ollama-host URL` to `cli.py`, passed to `LLM(host=…)`
  (constructor already accepts `host`). Default remains `$OLLAMA_BASE_URL`.

#### C. Isolated venv + Piper voice
```bash
cd submissions/team-f
uv venv .venv --python 3.11            # untracked (.gitignore already ignores .venv/)
source .venv/bin/activate              # or use `uv run`
uv pip install ollama python-dotenv piper-tts
mkdir -p models
BASE=https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB
curl -L "$BASE/northern_english_male/medium/en_GB-northern_english_male-medium.onnx"      -o models/en_GB-northern_english_male-medium.onnx
curl -L "$BASE/northern_english_male/medium/en_GB-northern_english_male-medium.onnx.json" -o models/en_GB-northern_english_male-medium.onnx.json
```
- Voice = `en_GB-northern_english_male-medium` (the README's recommended "Yorkshire
  deadpan, perfect for Roy"). `models/` is already gitignored → untracked. The
  voice is the requested "audio model".
- `tts.py:speak_with_piper` shells out to the `piper` binary; the `piper-tts`
  pip package provides that console script inside `.venv/bin`. The sbatch job must
  run inside this venv (so `shutil.which("piper")` resolves).

#### D. roybot display-name feature (minimal, general)
- `analyze.py`: add `display_name: str = ""` to `UserStats`; default to `user` if
  empty (set in `aggregate`). Used only in prompt text + the markdown `# heading`,
  **not** in the output-file key (`user_<slurm_username>.md/.wav`).
- `prompts.py`: `serious_user_prompt` / `roast_user_prompt` / `standup_prompt` use
  `stats.display_name`. When `display_name != user`, add a single line to the roast
  user prompt: `Address them as "<display_name>" at least once.` (keeps the shared
  system prompts untouched).
- `cli.py`: add `--rename OLD=NEW` (repeatable). After `aggregate`, apply renames
  to matching `UserStats.display_name`.
- `reports.py`: `_user_md` heading uses `display_name`; dict key stays `user`.
- This is the wiring that makes the audio say "Dieter - Herder of Claude Code".

#### E. The sbatch job — `scripts/run_roboroy.sbatch`
- SLURM headers per lab template: `--job-name=roboroy_claude-code
  --account=compgen --partition=gpu --gpus-per-node=1 --time=01:00:00 --mem=16G
  --gres=tmpspace:5G --output=logs/%x_%j.out --error=logs/%x_%j.err`.
- Steps: dump sacct → `eval serve-local` + `trap stop-local` → ensure model
  present (pull if missing) → `uv run python -m roybot …` (as in dataflow) → done.
- `MODEL` defaults to `qwen2.5:14b` (README default; fits one GPU). Overridable
  via env. Smaller fallback `qwen2.5:7b` noted in comments.

### Files to add / change

| File | Action |
|---|---|
| `submissions/team-f/EXAMPLE_DIETER_05_06_2026.txt` | **add** (committed sacct dump) |
| `submissions/team-f/scripts/ollama_hpc.sh` | **add** (serve-local/stop-local, from geo) |
| `submissions/team-f/scripts/run_roboroy.sbatch` | **add** (the GPU pipeline job) |
| `submissions/team-f/roybot/analyze.py` | **edit** (`display_name` field + apply) |
| `submissions/team-f/roybot/prompts.py` | **edit** (use display_name in prompts) |
| `submissions/team-f/roybot/reports.py` | **edit** (heading uses display_name) |
| `submissions/team-f/roybot/cli.py` | **edit** (`--rename`, `--ollama-host`) |
| `submissions/team-f/README.md` | **edit** (HPC run section + new flags) |
| `submissions/team-f/.env.example` | **edit** (note HPC ollama / model) |
| `submissions/team-f/.venv/` | **create** (untracked) |
| `submissions/team-f/models/*.onnx(.json)` | **create** (untracked) |
| `submissions/team-f/out/` | runtime outputs (untracked) |
| `submissions/team-f/logs/` | sbatch logs (untracked) |

## System-wide impact

- **Interaction graph:** `cli.main` → `load_sacct_file` → `aggregate` →
  `LLM.serious/roast/standup` (HTTP to Ollama) → `GeneratedReports.write` →
  `tts.speak` (subprocess → `piper`). New `--rename` mutates `UserStats` between
  `aggregate` and `generate`. New `serve-local` lifecycle is owned by the sbatch
  trap, not by Python.
- **Error propagation:** `llm.py` already falls back to deterministic text on any
  Ollama error (unless `--no-fallback`). For this deliverable we want a *real*
  roast, so the sbatch will warm the model first and we will verify the text is
  not an `[LLM fallback — …]` line before declaring success. TTS failures are
  caught in `cli.py` and logged (audio simply skipped) — the sbatch must check the
  `.wav` actually exists, not just that the job exited 0.
- **State lifecycle risks:** an orphaned `ollama serve` if the job dies before the
  trap fires → mitigated by `trap … EXIT INT TERM` and a pid file; `stop-local`
  is idempotent (`|| true`).
- **API surface parity:** `--rename` should work in `--mock` mode too (so the demo
  path and the real path share the code). Verify with a mock run.
- **Integration scenarios that unit tests miss:** (1) Ollama reachable but model
  not pulled → first request 404/slow; warmup catches it. (2) `piper` binary not
  on PATH because the job didn't activate `.venv` → `say`-less Linux yields no
  audio; guard by running under the venv. (3) single-user dump → `standup`
  monologue degenerates to one name; acceptable, the per-user roast is the
  primary artifact.

## Acceptance criteria

### Functional
- [ ] `EXAMPLE_DIETER_05_06_2026.txt` exists in `submissions/team-f/`, is valid
      `sacct --parsable2` (header + ≥1 dstoker job row), and is committed.
- [ ] `scripts/ollama_hpc.sh serve-local` starts a reachable Ollama and prints an
      `export OLLAMA_BASE_URL=…` line; `stop-local` tears it down.
- [ ] `submissions/team-f/.venv` exists (untracked) with `ollama`,
      `python-dotenv`, `piper-tts` importable and `piper` on the venv PATH.
- [ ] A Piper voice `.onnx` (+ `.onnx.json`) exists under `models/` (untracked).
- [ ] roybot processes `EXAMPLE_DIETER_05_06_2026.txt` through the **real** Ollama
      LLM (output is not the deterministic fallback).
- [ ] `--rename 'dstoker=Dieter - Herder of Claude Code'` makes the roast text
      address the user by that exact phrase.
- [ ] `scripts/run_roboroy.sbatch` runs the full pipeline under SLURM and exits 0.
- [ ] **Done-when:** the roast **text is captured** on disk (`out/user_dstoker.md`,
      containing "Dieter - Herder of Claude Code") **AND** the **audio recording
      exists** (`out/user_dstoker.wav` and/or `out/standup.wav`, non-empty).

### Non-functional / quality
- [ ] No hardcoded absolute Ollama URL in roybot source (use `OLLAMA_BASE_URL` /
      `--ollama-host`).
- [ ] Shared `hackathon/pyproject.toml` untouched; Piper installed only in venv.
- [ ] README + `.env.example` updated in the same change set (repo rule #5).
- [ ] `--mock` path still works (regression check).
- [ ] geo_harmonizer attribution comment present in `ollama_hpc.sh`.

## Dependencies & risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Compute node has no internet → can't `pip install` / `curl` the voice | Med | Do venv build + model download on a node with internet (submit/transfer) or current node if reachable; verify with a connectivity probe before committing to a path. |
| `piper-tts` console-script / wheel issues on HPC Linux | Med | Verify `piper --help` after install; if the pip CLI is broken, fall back to the `python -m piper` invocation or a pinned version. |
| Ollama model not pulled in the shared install | Med | `ollama list` (needs server); pull `qwen2.5:14b` via a GPU srun before the run; fall back to `qwen2.5:7b` if VRAM/time constrained. |
| GPU queue wait for sbatch | Low | `--time=01:00:00`, single GPU; can also verify the LLM step interactively on a GPU srun first. |
| LLM omits the exact honorific | Low | Prompt instructs "address them as '<name>' at least once"; verify by grepping `out/user_dstoker.md`; re-run if missing. |
| sacct dump for dstoker empty in 7 days | Low | Widen window; note window in commit/README. |
| Orphaned `ollama serve` | Low | pid file + `trap stop-local` on EXIT/INT/TERM. |

## Verification plan (maps to "execute it")

1. **Build venv + voice**, confirm `piper` resolves and `import ollama` works.
2. **Generate the example file** from real sacct; sanity-check it parses
   (`uv run python -c "from roybot.data import load_sacct_file; print(len(load_sacct_file('EXAMPLE_DIETER_05_06_2026.txt')))"`).
3. **Smoke test offline:** `uv run python -m roybot --sacct EXAMPLE_… --rename
   'dstoker=Dieter - Herder of Claude Code'` (no LLM) → confirms parsing + rename.
4. **Verify LLM:** start Ollama (`ollama_hpc.sh serve-local` on a GPU srun or in
   the sbatch), run with `--with-llm`, confirm output is a real roast (not
   fallback) that contains the honorific.
5. **Full sbatch run:** submit `run_roboroy.sbatch`; on completion verify the two
   done-when artifacts exist and are non-empty, and the text contains
   "Dieter - Herder of Claude Code".

## Sources & references

### Internal
- roybot source: `submissions/team-f/roybot/{cli,data,analyze,llm,prompts,reports,tts}.py`
- existing collector: `submissions/team-f/scripts/collect_sacct.sh`
- submission intent: `submissions/team-f/PROPOSAL.md`, `README.md`
- HPC Ollama pattern: `/hpc/compgen/projects/llm_GEO_project/harmonia_metadata_agent/analysis/dstoker/geo_harmonizer/agent_tools/ollama_management/{README.md,manage_ollama.sh}`
- monorepo conventions: `lab_ai_automation/.claude/CLAUDE.md` (env vars, deployment recipes, copy-with-attribution)

### Environment facts (verified this session)
- Host `n0073.manage.hpc`; `seff`, `sacct`, `uv 0.9.9` present.
- Ollama binary: `/hpc/compgen/projects/ollama/ollama_run/analysis/dstoker/bin/ollama`.
- `tts.py` Linux audio = Piper only (`say` is macOS-only).
- `.gitignore` already excludes `.venv/`, `models/`, `out/`, `*.wav`.
