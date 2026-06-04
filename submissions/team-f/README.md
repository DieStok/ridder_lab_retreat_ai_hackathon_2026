# Team F — Roy-bot

The HPC babysitter for the De Ridder Lab. Reads SLURM `sacct` output, computes
per-user efficiency / overprovisioning / CO₂, then asks a local LLM to write
two reports per lab member (one serious, one roast) and a 30-second lab
stand-up monologue. Optionally reads the monologue aloud in a dry British
voice via macOS `say` or Piper.

> Double the Roy, double the fun.

## First run for a labmate (start here if you've never run this)

**What you need, by how far you want to go:**

| You want… | You need |
|---|---|
| just to see it work | Python 3.11+ and `uv`. Nothing else. |
| the real reports + jokes | the above, plus [Ollama](https://ollama.com) running with a model pulled |
| audio (nice voice) | the above, plus a Piper voice model (one download) |
| audio (zero setup) | a Mac — uses the built-in `say` command |

**The 30-second version — proves it works with zero dependencies:**

```bash
# 1. install uv (once, if you don't have it)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. build the environment (once)
cd ridder_lab_ai_automation/hackathon
uv sync

# 3. run it on the built-in fake lab
cd submissions/team-f
uv run python -m roybot --mock

# 4. look at the output
open out/standup.txt out/user_merel.md
```

That's it — no Ollama, no API keys, no internet. `--mock` ships a fake 5-person
lab so you can see the whole pipeline immediately.

**To get the actual LLM reports + roast**, start Ollama and pull the model once:

```bash
ollama serve &                 # if it isn't already running
ollama pull qwen2.5:14b        # ~9 GB, one time
uv run python -m roybot --mock --with-llm
```

**To add the good voice** (one-time, ~60 MB — see the [Piper section](#piper-local-open-source-much-more-natural)
for the download commands):

```bash
uv pip install piper-tts
uv run python -m roybot --mock --with-llm --with-audio \
    --engine piper --piper-model models/en_GB-northern_english_male-medium.onnx
open out/standup.wav
```

**On real lab data** instead of `--mock`, pull a week of `sacct` off the cluster
(see [Getting real sacct data](#getting-real-sacct-data)) and pass `--sacct dump.txt`.

> **Why `uv`?** It's the lab's standard package manager (see the monorepo
> `AGENTS.md`). `uv sync` builds an isolated `.venv/` with the exact pinned
> dependencies — no clashes with your system Python or conda. `uv run …` then
> runs inside that venv automatically, so you never `activate` anything. It also
> finds the shared `hackathon/.venv/` one level up, which is why `uv run` works
> from inside `submissions/team-f/`.
>
> **One gotcha:** Piper is *not* in `uv sync` (we kept it out of the shared
> `pyproject.toml`, which isn't ours to edit). If you use `--engine piper`, run
> `uv pip install piper-tts` once. Using `--engine say` on a Mac needs nothing extra.

## Quick start

Run from this directory (`hackathon/submissions/team-f/`) so `python -m roybot`
can find the package. `uv run` walks up the tree to find the shared
`hackathon/.venv/` automatically.

```bash
cd hackathon/submissions/team-f

# Sanity check with the built-in mock dataset — no Ollama, no audio.
uv run python -m roybot --mock

# Same, but with the real LLM (needs Ollama running at $OLLAMA_BASE_URL).
uv run python -m roybot --mock --with-llm

# Full retreat-demo mode: real LLM + audio.
uv run python -m roybot --mock --with-llm --with-audio --voice Daniel

# On real data:
uv run python -m roybot --sacct /path/to/dump.txt --with-llm --with-audio
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

If you also want the LLM + audio to run on the same schedule, that has to
live somewhere with Ollama — the cluster compute nodes (via `sbatch`) or an
off-cluster box. For the retreat demo we just run that part manually.

## Running the whole thing on the HPC (Ollama on a GPU + sbatch)

The HPC has no internet, so the LLM is the lab's **locally-installed Ollama**
on a GPU node. One sbatch job does everything: dump a week of sacct, start a
per-job Ollama, roast, and render audio with Piper. End-to-end:

```bash
cd hackathon/submissions/team-f

# 1. one-time: isolated venv with the audio model (NOT in the shared toml)
uv venv .venv --python 3.11
uv pip install --python .venv/bin/python ollama python-dotenv piper-tts
.venv/bin/python -m piper.download_voices en_GB-northern_english_male-medium \
    --download-dir models           # ~63 MB .onnx + .json into models/ (gitignored)

# 2. submit the pipeline (defaults to gemma4:26b on a 79 GB A100 MIG slice)
sbatch scripts/run_roboroy.sbatch
#   MODEL=qwen3.5:27b sbatch scripts/run_roboroy.sbatch     # override the model

# 3. outputs land under out/<user>/  (per-user roast .md + .wav, standup, stats.json)
```

### How the Ollama wiring works (`scripts/ollama_hpc.sh`)

Adapted from geo_harmonizer's `manage_ollama.sh`. It runs a **per-job** Ollama
bound to a free port and prints `export` lines the sbatch `eval`s:

```bash
export OLLAMA_CONTEXT_LENGTH=8192          # BEFORE serve-local, so ollama serve inherits it
eval "$(scripts/ollama_hpc.sh serve-local --warmup-model gemma4:26b --keep-alive -1)"
trap 'scripts/ollama_hpc.sh stop-local || true' EXIT INT TERM
# ... now $OLLAMA_BASE_URL points at the per-job server; roybot reads it ...
```

It points Ollama's model cache at the shared install
(`$OLLAMA_INSTALL_DIR/ollama_models`) so pulls are cached across jobs and never
hit the 5 GB home quota. `serve-local` / `stop-local` / `status` / `pull` are
the subcommands; teardown is the caller's job (hence the `trap`).

> **Context length matters.** Ollama otherwise defaults to a ~4096-token window
> and *silently truncates* the prompt. We pin it twice — server-side via
> `OLLAMA_CONTEXT_LENGTH` and per-request via roybot's `--num-ctx` (default
> 8192). This is the belt-and-suspenders fix from geo_harmonizer's failure
> taxonomy.

### Addressing someone by a title (`--rename`)

The roast/standup normally use the SLURM username. To address a person by a
display name in the prose **and the audio** (output filenames stay on the
username), use `--rename`:

```bash
python -m roybot --sacct EXAMPLE_DIETER_05_06_2026.txt --with-llm --with-audio \
    --engine piper --rename 'dstoker=Dieter - Herder of Claude Code'
```

### Example data in the repo

`EXAMPLE_<USER>_05_06_2026.txt` are real one-week `sacct --parsable2` dumps for
six lab members, committed as ready-to-run inputs (e.g.
`EXAMPLE_DIETER_05_06_2026.txt`). Two users (`atsakali`, `rstraver`) had no jobs
in that window, so their dumps are header-only — kept on purpose to exercise the
empty-input path. `run_roboroy.sbatch` skips empty dumps automatically.

### Tests

```bash
.venv/bin/python -m pytest -q        # parser schema + every committed dump format-checks
```

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

## Delivering the reports

RoboRoy writes files to `out/` — it doesn't post them anywhere. To get them to
people, attach `out/user_<name>.md` to a DM/email per person, and drop
`out/standup.txt` (or play `standup.wav`) at the Monday stand-up. Automating
delivery (e.g. a weekly Slack post) is deliberately out of scope — see
`ADOPTION.md` for the open decisions if the lab wants it.

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
    └── tts.py           # `say` + Piper wrappers, acronym normalisation
```

## Known limitations / future fun

- GPU efficiency is approximated from job state. Real GPU utilisation needs
  jobstats (Princeton's tool) or NVIDIA DCGM exporters running cluster-side.
  If Utrecht installs jobstats, swap `data.py` for a jobstats loader.
- Delivery is manual — RoboRoy writes files, you hand them out. No Slack/email
  posting (see `ADOPTION.md` for why and what it would take).
- The roast prompt assumes ≥ a 14B model. Smaller models will write a
  competent serious report but produce flat roasts. If you have to use a 7B
  model, raise the temperature in `llm.py`.

## Credits

- Inspired by [Princeton jobstats](https://princetonuniversity.github.io/jobstats/).
- Roy is a national treasure.
