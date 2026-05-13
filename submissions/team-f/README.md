# Team F — Roy-bot

The HPC babysitter for the De Ridder Lab. Reads SLURM `sacct` output, computes
per-user efficiency / overprovisioning / CO₂, then asks a local LLM to write
two reports per lab member (one serious, one roast) and a 30-second lab
stand-up monologue. Optionally reads the monologue aloud in a dry British
voice via macOS `say` and posts it to Slack.

> Double the Roy, double the fun.

## Quick start

Run from this directory (`hackathon/submissions/team-f/`) so `python -m roybot`
can find the package. `uv run` walks up the tree to find the shared
`hackathon/.venv/` automatically.

```bash
cd hackathon/submissions/team-f

# Sanity check with the built-in mock dataset — no Ollama, no audio, no Slack.
uv run python -m roybot --mock

# Same, but with the real LLM (needs Ollama running at $OLLAMA_BASE_URL).
uv run python -m roybot --mock --with-llm

# Full retreat-demo mode: real LLM + audio.
uv run python -m roybot --mock --with-llm --with-audio --voice Daniel

# On real data:
uv run python -m roybot --sacct /path/to/dump.txt --with-llm --with-audio

# Post the stand-up + audio to Slack (needs .env with bot token + channel id).
uv run python -m roybot --mock --with-llm --with-audio --slack
```

> If you'd rather invoke it from anywhere, run
> `PYTHONPATH=/abs/path/to/submissions/team-f uv run python -m roybot ...`.

Outputs land in `./out/`:

```
out/
├── user_<name>.md          per-user markdown report  (one per lab member)
├── user_<name>.wav         per-user roast clip       (with --with-audio)
├── standup.txt             lab stand-up monologue (text)
├── standup_spoken.txt      same, post acronym normalisation (what the TTS heard)
├── standup.wav             lab stand-up monologue (audio)
└── stats.json              raw per-user numbers
```

`say` produces `.aiff`; Piper produces `.wav`. Each per-user clip contains
just the roast — the actionable `--cpus-per-task=…`, `--mem=…`, etc.
recommendations live in the per-user markdown report (`user_<name>.md`),
which is the personalised message you can send to each lab member.
Pass `--skip-per-user-audio` if you only want the lab stand-up clip.

## Getting real sacct data

Use `scripts/collect_sacct.sh` — it runs the right `sacct` invocation and
writes a timestamped, atomic dump file. It must run on a SLURM submit node
(it'll exit with a clear error if `sacct` isn't on `$PATH`).

```bash
# one-shot, last 7 days of the compgen account into ./sacct_dumps/:
./scripts/collect_sacct.sh

# everything is env-configurable:
SACCT_DAYS=14 SACCT_ACCOUNT=compgen SACCT_OUT_DIR=/tmp/dumps \
    ./scripts/collect_sacct.sh

# explicit user list (overrides account filter):
SACCT_USERS=roy,merel,claudio ./scripts/collect_sacct.sh
```

The script prints the absolute path of the dump to stdout. Pipe that into
roybot:

```bash
DUMP=$(./scripts/collect_sacct.sh)
uv run python -m roybot --sacct "$DUMP" --with-llm --with-audio
```

### Schedule it weekly

`scripts/crontab.example` is a one-line crontab entry that runs the dump
every Monday at 08:00. Edit the paths and `crontab -e` it onto the submit
node (`hpcs05` / `hpcs06`). The cron line is tagged `# roybot-collect` for
easy lookup (`crontab -l | grep roybot-collect`).

If you also want the LLM + audio + Slack post to run on the same schedule,
that has to live somewhere with internet access — the parent `AGENTS.md`
forbids long-lived internet-facing processes on submit nodes. See
`automation_building_blocks/deployment_recipes/` for cloud-VM and systemd
patterns. For the retreat demo we just run that part manually.

## What's actually computed

Per job (using the same definitions as `seff`):

- **CPU efficiency** = `CPUTimeRaw / (AllocCPUS × ElapsedRaw)`
- **Memory efficiency** = `MaxRSS / ReqMem`
- **Time efficiency** = `ElapsedRaw / Timelimit`
- **Energy** = `(CPU_cores × 10 W + GPUs × 400 W) × elapsed × PUE(1.4)`
- **CO₂** = `kWh × 0.27 kg/kWh` (Netherlands grid, 2024)

Per user we sum these and flag any job below the efficiency thresholds in
`analyze.py` (CPU < 30%, mem < 25%, walltime < 20%). The "worst offender" of
each user is what the roast prompt is told to focus on.

### Next-time recommendations

For every flagged job we compute a concrete `sbatch` flag to use next time,
sized at ~1.3× the actual usage:

| Issue | Suggested flag |
|---|---|
| CPU efficiency < 30% | `--cpus-per-task=<ceil(used_cpus × 1.3)>` |
| Memory peak < 25% of request | `--mem=<ceil(peak_GB × 1.3)>G` |
| Walltime usage < 20% | `--time=<ceil(elapsed × 1.5 to nearest 15 min)>` |
| Multi-GPU job died early (cancelled / failed < 30 min) | `--gres=gpu:1` ("test small first") |
| Multi-GPU job with CPU eff < 30% | `--gres=gpu:<n_gpus // 2>` ("data loader is starving them") |
| Segfault (exit 139) | "reproduce on a small input, then `valgrind`" |

> ⚠️ **GPU recommendations are heuristic.** Plain `sacct` doesn't expose
> per-job GPU utilisation — we can only see how many GPUs were allocated,
> not whether they were busy. The rules above use circumstantial evidence
> (early death, CPU-starved feeders) which catches the obvious waste but
> misses the "asked for 8 GPUs, used 1 of them at 100%" case. If Utrecht
> installs Princeton's [`jobstats`](https://princetonuniversity.github.io/jobstats/)
> or NVIDIA DCGM exporters, the rules in `analyze.py:_recommend_for_job`
> can be tightened to use real numbers.

These appear in a dedicated **"Recommendations for next time"** section of
each user's markdown report. They are also passed to the LLM in JSON so the
spoken serious report quotes the exact flag (rather than the model inventing
its own number).

> The power numbers are ballparks — pick your fight with the team on Slack.
> CPU/GPU TDP and Netherlands grid intensity are constants at the top of
> `analyze.py`; tweak them if Utrecht publishes real numbers.

## Voices — two engines

### `say` (macOS built-in, instant)

```bash
say -v '?'                                                              # list voices
uv run python -m roybot --mock --with-llm --with-audio --voice Daniel   # British dry
uv run python -m roybot --mock --with-llm --with-audio --voice Karen    # Australian sassy
uv run python -m roybot --mock --with-llm --with-audio --voice Moira    # Irish
```

`Daniel` is the default. If it sounds robotic, that's because you have the
**Compact** variant. Download the **Premium** version once (free):

> System Settings → Accessibility → Spoken Content → System Voice → Manage Voices…

then pass the exact name, parens included:

```bash
uv run python -m roybot --mock --with-llm --with-audio --voice "Jamie (Premium)"
```

Good UK Premium voices: `Jamie`, `Oliver`, `Serena`, `Joelle`.

### `piper` (local, open source, much more natural)

[Piper](https://github.com/rhasspy/piper) is the current state of the art for
free local TTS. Install + grab a voice model (one-time, ~60 MB per voice):

```bash
cd hackathon/submissions/team-f
uv pip install piper-tts                  # add to the shared venv (not the toml)

mkdir -p models
BASE=https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB

# Two voices we've found good for Roy energy:
curl -L "$BASE/alan/medium/en_GB-alan-medium.onnx"      -o models/en_GB-alan-medium.onnx
curl -L "$BASE/alan/medium/en_GB-alan-medium.onnx.json" -o models/en_GB-alan-medium.onnx.json

curl -L "$BASE/northern_english_male/medium/en_GB-northern_english_male-medium.onnx"      -o models/en_GB-northern_english_male-medium.onnx
curl -L "$BASE/northern_english_male/medium/en_GB-northern_english_male-medium.onnx.json" -o models/en_GB-northern_english_male-medium.onnx.json

# Yorkshire deadpan — closest thing to Roy on a Monday morning:
uv run python -m roybot --mock --with-llm --with-audio \
    --engine piper --piper-model models/en_GB-northern_english_male-medium.onnx
```

Then `open out/standup.wav`. Other good UK voices to swap in:

```
en_GB/alan/medium                      — dry British male
en_GB/northern_english_male/medium     — Yorkshire deadpan (recommended)
en_GB/southern_english_female/low      — receptionist energy
en_GB/jenny_dioco/medium               — natural UK female
```

### Acronym spelling

Both engines mispronounce acronyms (`CPU` → "kuh-poo", `CO2` → "co two"
read as a phrase). Roy-bot rewrites the transcript before sending it to
the TTS:

```
CPU  -> C P U                  CO2  -> C O two
GPU  -> G P U                  kWh  -> kilowatt hours
RAM  -> R A M                  kg   -> kilograms
HPC  -> H P C                  GB   -> gigabytes
```

The original `standup.txt` keeps the readable form ("CPU", "CO₂"); the
post-normalisation version (what the TTS actually receives) is written
to `standup_spoken.txt` so you can see exactly what the voice heard.
Mappings live in `roybot/tts.py:_ACRONYM_SUBS` if you want to add more.

Full catalogue: https://github.com/rhasspy/piper/blob/master/VOICES.md.

> Why `uv pip install` and not `uv add`? `uv add` would write piper-tts into
> the shared `hackathon/pyproject.toml`, which the hackathon AGENTS.md keeps
> off-limits. `uv pip install` adds it to the venv without touching the toml.
> Next `uv sync` from `hackathon/` removes it; re-run `uv pip install
> piper-tts` if that happens.

## Slack setup (optional)

Create a Slack app, add `chat:write` and `files:write` bot scopes, install to
the workspace, and copy the bot token. Then:

```bash
cp .env.example .env
# fill in SLACK_BOT_TOKEN and SLACK_CHANNEL_ID
uv run python -m roybot --mock --with-llm --with-audio --slack
```

## Layout

```
team-f/
├── PROPOSAL.md          # the submission template
├── README.md            # this file
├── .env.example
├── .gitignore
├── sample_sacct.txt     # 5-row example in parsable2 format
├── scripts/
│   ├── collect_sacct.sh # cron-friendly sacct dumper (runs on submit nodes)
│   └── crontab.example  # one-line weekly schedule
└── roybot/
    ├── __init__.py
    ├── __main__.py      # python -m roybot
    ├── cli.py           # argparse + orchestration
    ├── data.py          # sacct parser
    ├── mock_data.py     # baked-in fake data
    ├── analyze.py       # stats + CO2 + flags
    ├── llm.py           # Ollama wrapper with fallback
    ├── prompts.py       # serious / roast / standup prompts + fallbacks
    ├── reports.py       # markdown generation
    ├── tts.py           # `say` + Piper wrappers, acronym normalisation
    └── slack_post.py    # one-shot post to Slack
```

## Known limitations / future fun

- GPU efficiency is approximated from job state. Real GPU utilisation needs
  jobstats (Princeton's tool) or NVIDIA DCGM exporters running cluster-side.
  If Utrecht installs jobstats, swap `data.py` for a jobstats loader.
- The Slack poster is one-shot, not a long-running listener. Wrap it in a
  cron / SLURM cron recipe from `automation_building_blocks/deployment_recipes/`
  to run it weekly.
- The roast prompt assumes ≥ a 14B model. Smaller models will write a
  competent serious report but produce flat roasts. If you have to use a 7B
  model, raise the temperature in `llm.py`.

## Credits

- Slack scaffolding pattern from `automation_building_blocks/slack_app_skeleton/`.
- Inspired by [Princeton jobstats](https://princetonuniversity.github.io/jobstats/).
- Roy is a national treasure.
