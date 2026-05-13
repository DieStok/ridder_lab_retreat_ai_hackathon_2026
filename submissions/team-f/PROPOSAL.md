---
team_name: "Team F"
team_members:
  - "Roy"
  - "Merel"
  - "Claudio"
problem:
  number:                 6
  short_description: "we probably overprovision or overuse both sbatch and srun jobs, and the current infrastructure requires that everyone check their own jobs' actual usage versus what was requested. Can we use automated tools to surface a daily/weekly report to members on how their jobs did and give recommendations on what to change"
running_environment: "Local"   # one of: local | HPC | cloud_VM | other
                          # HPC implies NO internet access for LLM/agent calls
running_environment_other: ""   # fill only if "other" above
notes_and_caveats: "We don't think running an LLM for monthly / biweekly reporting is useful, because we have Roy, command master. But wouldn't it be cool to bash lab members every week based on what they did on the HPC? Bonus points for generating an audio for the work discussion. CO2 calculations included."
---

# Team F — Double the Roy, double the fun

## 1. The problem

The numbers Roy needs to give the lab are already in SLURM (`sacct`, `seff`,
`sstat`). What's missing is the social layer: nobody reads a wall of job
stats unless they have to, and Roy shouldn't have to babysit five people's
overprovisioned jobs every Monday. We want the dry-but-fun weekly
"here's how the lab spent its CPU-hours" segment, automatically.

## 2. Why it matters & where automation fits

Roy stays the admin and the source of truth — he still owns `sacct`, still
gives the real recommendations, still knows the cluster. Roy-bot is a layer
on top of Roy's data, not a replacement for him: it turns this week's job
records into a per-person markdown report, a roast aimed at the worst
offender, a 30-second lab stand-up monologue, and an audio clip we can play
at the actual stand-up. The goal is behaviour nudging via humour, not advice
generation — when someone reserves 500 GB of RAM and uses 9 GB, hearing it
read out loud in a Northern English deadpan is more motivating than another
Slack DM. CO₂ numbers fall out of the same pipeline, mostly so we can all
feel guilty about it.

## 3. Architecture / workflow

```
sacct --parsable2 dump        (or built-in mock dataset)
        │
        ▼
roybot.data         — parse rows into typed Jobs
        │
        ▼
roybot.analyze      — per-user stats: CPU/GPU/RAM hours,
                      efficiency, overprovision flags, kWh, CO₂
        │
        ▼
roybot.llm          — local Ollama (qwen2.5:14b by default)
                      ├── serious per-user report  (LLM)
                      ├── Roy-style roast          (LLM, skipped for clean users)
                      └── lab-wide stand-up        (LLM)
        │
        ▼
roybot.tts          — engine = say | piper
                      • acronym spelling: CPU → "C P U", CO₂ → "C O two", kWh → "kilowatt hours"
                      • voices: Daniel (say), en_GB-northern_english_male (piper, recommended)
        │
        ▼
out/                — markdown reports, stats.json,
                      standup.txt, standup_spoken.txt, standup.{aiff,wav}
        │
        ▼
(optional) Slack post: text + audio attachment for the stand-up slide
```

Tools we reuse:
- [`ollama`](https://ollama.com) for local LLM inference
- [`piper-tts`](https://github.com/rhasspy/piper) for natural-sounding local TTS
- macOS `say` for the zero-install TTS fallback
- [Princeton `jobstats`](https://princetonuniversity.github.io/jobstats/) — inspiration only. We use plain `sacct` so it works on Utrecht's cluster today. If jobstats gets installed there later, swap `roybot/data.py` for a jobstats loader.
- `slack-sdk` for optional posting

## 4. References

- SLURM `sacct` docs — https://slurm.schedmd.com/sacct.html
- `seff` (efficiency report) — https://github.com/SchedMD/slurm/blob/master/contribs/seff/seff
- Princeton jobstats — https://princetonuniversity.github.io/jobstats/
- Piper TTS voices — https://github.com/rhasspy/piper/blob/master/VOICES.md
- Netherlands grid carbon intensity — ~0.27 kg CO₂/kWh (2024, Ember)

---

## (Bonus) Initial implementation notes

Code lives in `submissions/team-f/roybot/`. Run with:

```bash
# from hackathon/, populate the shared venv once:
uv sync

# everything else runs from inside the team dir:
cd submissions/team-f
uv run python -m roybot --mock                                       # built-in fake data
uv run python -m roybot --mock --with-llm                            # adds the LLM (needs Ollama)
uv run python -m roybot --mock --with-llm --with-audio               # macOS `say` voice
uv run python -m roybot --mock --with-llm --with-audio \             # natural Piper voice
    --engine piper --piper-model models/en_GB-northern_english_male-medium.onnx
uv run python -m roybot --sacct dump.txt --with-llm --with-audio     # on real sacct data
```

### What works
- sacct `--parsable2` parser + mock dataset (5 users, varied behaviour)
- per-user efficiency stats (CPU / mem / walltime, seff-style)
- kWh + kg CO₂ estimates using NL grid intensity
- overprovision flags + "worst offender" selection
- two-prompt LLM pipeline (serious + roast) on local Ollama
- lab-wide stand-up monologue
- two TTS engines (`say` and Piper), with acronym normalisation so the voice doesn't say "kuh-poo"
- optional Slack post + audio upload
- `scripts/collect_sacct.sh`: a small shell script Roy can drop in a submit-node crontab to produce a weekly sacct dump (atomic write, timestamped output, env-configurable account / users / lookback window). One-line crontab example included.

### What's stubbed / still TODO
- **End-to-end scheduling.** `collect_sacct.sh` produces the dump on schedule; the LLM + audio + Slack-post side still has to run somewhere with internet access (per the parent `AGENTS.md`, that's not the submit node). Likely a small cloud VM or systemd timer — recipes are in `automation_building_blocks/deployment_recipes/`. For the retreat demo we just run that part by hand from a laptop.
- **Cron line not yet installed.** `scripts/crontab.example` is ready to paste but nobody has put it on `hpcs05` / `hpcs06` yet — Roy needs to do that on his cluster account.
- **GPU efficiency.** Approximated from job state today (e.g. "1 GPU allocated, 1 hour of walltime → 1 GPU-hour"). True GPU utilisation needs `jobstats` or DCGM exporters server-side.
- **Slack posting.** Code works but never tested with real tokens — needs a Slack app installed in the lab workspace.
