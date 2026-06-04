# RoboRoy — what we'd automate for the lab, and how

> The "clear overview + small workflow" deliverable for lab-wide adoption.
> One page. Read it before deciding whether to actually run this weekly.

## What it does

Once a week, for each lab member, RoboRoy turns the past week of SLURM job
records into:

1. **A per-person report** (`user_<name>.md`) — CPU/GPU/memory hours, efficiency,
   energy (kWh) and CO₂, plus concrete `sbatch` flags to request less next time.
2. **A 30-second lab stand-up monologue** (text + audio) naming the biggest
   emitter and the efficiency champion — for the Monday work-discussion slide.
3. **A short roast per person** (audio) — the nudge that makes people actually
   read the report.

## What's automated vs. what stays human

| Step | Who / what | Why |
|---|---|---|
| Collect the week's `sacct` data | **automated** — `collect_sacct.sh` on a cron | mechanical |
| Compute efficiency, energy, CO₂, sbatch recommendations | **automated** — deterministic Python | must be exact, not guessed |
| Write the prose reports + roasts + standup | **automated** — local LLM (Ollama) | tone, not numbers |
| Read the room, decide policy, answer "but my job is special" | **Roy** | he's the expert; the bot only nudges |

The split matters: **every number is computed, the LLM only writes the words.**
The model never invents a CPU count or a CO₂ figure — those are passed to it as
facts, and for clean users the roast is skipped entirely so it can't fabricate a
flaw.

## The weekly workflow

```
Monday 08:00, submit node (hpcs05/06), cron:
  collect_sacct.sh  ──►  sacct_YYYY-MM-DD.txt   (last 7 days, compgen account)
        │
        │  (file synced / picked up off-cluster — see note)
        ▼
Off-cluster box with internet + Ollama:
  roybot --sacct <dump> --with-llm --with-audio
        │
        ▼
  out/user_<name>.md     → DM / email to each member  (the personalised tips)
  out/standup.{txt,wav}  → #lab-standup channel slide  (the public summary)
```

**Why two machines?** The lab's HPC policy (parent `AGENTS.md`) forbids
long-lived, internet-facing processes on submit nodes. So: collection runs *on*
the cluster (cheap, no internet); the LLM + audio + posting run *off* the
cluster (a laptop today, a small VM if we want it hands-off). The hand-off is the
one piece still manual — a `scp`/rsync or a shared mount.

## What it costs to adopt

- **Nothing in API spend** — Ollama + a local model, runs on a laptop or a lab GPU node.
- **One-time setup:** cron line on a submit node (`scripts/crontab.example`), and a
  place to run the report (laptop is fine to start).
- **Ongoing:** zero human time once cronned, except Roy glancing at the standup.

## Honest limitations (so we adopt it with eyes open)

- **GPU utilisation is heuristic.** Plain `sacct` shows GPUs *allocated*, not
  *used*. We catch the obvious waste (multi-GPU jobs that die early or starve the
  CPU feeder) but miss "asked for 8, used 1 at 100%". Fixing this properly needs
  Princeton `jobstats` or NVIDIA DCGM installed on the cluster — a request to make
  of the HPC admins, not something we can do from user space.
- **CO₂ is order-of-magnitude**, not metered: NL grid intensity × ballpark TDPs ×
  PUE. Fine for "who's the worst this week", not for a carbon audit.
- **The roast is a social tool, not a manager.** It nudges; it doesn't enforce.
  Real over-use conversations stay between humans.

## Decisions for the lab to make

1. **Do we want the roast, or just the serious reports?** (One flag — the roast is
   the engagement hook, but it's optional.)
2. **Public standup vs. private DMs vs. both?** The standup names names; some may
   prefer the per-user report stay private.
3. **Who hosts the off-cluster run** once we want it fully hands-off — a laptop on a
   calendar reminder, or a small always-on VM?
4. **Worth asking HPC for `jobstats`/DCGM** so GPU numbers become real?

## Next steps if we say yes

- [ ] Install `scripts/crontab.example` on hpcs05/06 (Roy)
- [ ] Decide the hand-off mechanism (shared mount vs. scp)
- [ ] Map HPC usernames → Slack handles / emails for delivery
- [ ] Pick a voice the lab can stand to hear weekly
- [ ] (optional) Request `jobstats` from the HPC admins
