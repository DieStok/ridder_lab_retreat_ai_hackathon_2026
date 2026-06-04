# RoboRoy — 5-minute showcase run sheet

> Lab meeting, 5 June 2026. Target: 5 minutes. Driver: Claudio.
> Goal: show the lab a working weekly HPC usage report + roast, and make them laugh once.

## Before you stand up (do this in the 10 min before the meeting)

```bash
cd ridder_lab_ai_automation/hackathon

# 1. make sure Ollama is up with the model pulled
ollama serve >/dev/null 2>&1 &        # if not already running
ollama list | grep qwen2.5:14b || ollama pull qwen2.5:14b

# 2. pre-generate everything so the live run is a re-run (fast, can't fail on stage)
cd submissions/team-f
uv run python -m roybot --mock --with-llm --with-audio \
    --engine piper --piper-model models/en_GB-northern_english_male-medium.onnx

# 3. confirm the audio plays through the room's speakers NOW, not on stage
open out/standup.wav
open out/user_merel.wav
```

If Ollama or Piper misbehaves on the day, the fallback still demos fine:
`uv run python -m roybot --mock --with-audio` (deterministic text + macOS `say`).

## The 5 minutes

**[0:00–0:45] The problem.** One sentence each:
- Everyone over-requests CPUs/RAM/GPUs "to be safe"; nobody checks `seff` afterward.
- When one person reserves 8 GPUs and uses 1, everyone else queues.
- Roy *could* nag us every week. Roy has better things to do. So we built RoboRoy.

**[0:45–1:45] One live run.** From `submissions/team-f/`:
```bash
uv run python -m roybot --mock --with-llm --with-audio \
    --engine piper --piper-model models/en_GB-northern_english_male-medium.onnx
```
Talk over the ~30s while it runs: "Reads a week of `sacct` data — real or, today, a
mock lab — computes per-user efficiency, energy and CO₂, then a local LLM writes the
reports. No data leaves the machine."

**[1:45–3:00] Play the standup audio.** `open out/standup.wav`. Let it run (~25s). It
opens with the lab total — *"749 CPU-hours, 28.43 kg of CO₂"* — names the biggest
emitter (Merel) and the efficiency champion (Lisa). This is the "work-discussion slide"
deliverable.

**[3:00–4:00] Show one report on screen.** Open `out/user_claudio.md`. Scroll to
**Recommendations for next time** — the concrete, deterministic part:
```
rna_pipeline: asked for 488 GB RAM, peaked at 9 GB (1%) → --mem=13G
jupyter_zombie: asked for 4 CPUs, used 4% → --cpus-per-task=1
```
Say it plainly: "The numbers are computed, not hallucinated — the LLM only does the
prose and the jokes. The sbatch flags are math."

**[4:00–4:40] The roast.** `open out/user_merel.wav` (~6s). This is the fun beat —
the Northern-English deadpan calling out the 8-GPU job. Then Roy's clip: *"Roy did
absolutely nothing wrong. Disappointing, really."* (~2s). Laugh, move on.

**[4:40–5:00] How it'd actually run.** One line: "`scripts/collect_sacct.sh` on a
submit node via cron dumps the week; the report + audio run off-cluster. See
ADOPTION.md." Hand back.

## If asked (likely Q&A)

- **"Is it reading our real jobs?"** Not today — mock dataset. The `sacct` parser is
  real; swap `--mock` for `--sacct dump.txt`. Collection script is written, not yet
  cronned on hpcs05/06.
- **"GPU efficiency?"** Heuristic only — plain `sacct` can't see per-GPU utilisation.
  We flag multi-GPU jobs that died early or starved their CPU feeder. Real numbers need
  Princeton `jobstats` or DCGM server-side. Honest limitation, noted in the README.
- **"Where does the LLM run / does data leave?"** Local Ollama. Nothing leaves the box.
- **"CO₂ numbers real?"** Order-of-magnitude: NL grid 0.27 kg/kWh, PUE 1.4, ballpark
  TDPs. Constants at the top of `analyze.py`, easy to argue about.

## Files to have open in tabs beforehand
1. terminal in `submissions/team-f/`
2. `out/user_claudio.md`
3. Finder on `out/` (to click the `.wav`s)
