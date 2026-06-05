# tachterberg — weekly HPC report

## At a glance

- Jobs: **146921** (7753 failed, 0 cancelled, 6 timed out)
- CPU-hours: **3529.8**, GPU-hours: **0.0**
- Avg CPU efficiency: **99%**, avg walltime usage: **2%**
- Energy: **49.42 kWh** ≈ **13.34 kg CO₂**

## Serious report

Total usage reached 3529.8 CPU-hours and 13.34 kg CO2. Job 53487402 was killed for exceeding its walltime limit, while many other tasks significantly overprovisioned their requested durations. For these tasks, next time use `--time=00:30:00`.

## Roy says

> You requested 24h of walltime and finished in 0%. It is quite a feat to accumulate 7753 failed jobs while essentially just occupying the queue. Even your 12h requests are only using 4% of their allocated time.
Try checking if your code actually works before booking the cluster for the afternoon.

## Recommendations for next time

- **geo_dl** (job 53487498): asked for 8h walltime, used 1% → `--time=00:30:00`
- **geo_dl** (job 53487986): asked for 8h walltime, used 1% → `--time=00:30:00`
- **cram_timestamps** (job 53630985): asked for 6h walltime, used 2% → `--time=00:30:00`
- **13eb38e7-b9d1-40cf-bf2a-1ce5a78b2eed** (job 53798799): asked for 8h walltime, used 3% → `--time=00:30:00`
- **13eb38e7-b9d1-40cf-bf2a-1ce5a78b2eed** (job 53798800): asked for 2h walltime, used 13% → `--time=00:30:00`
- **13eb38e7-b9d1-40cf-bf2a-1ce5a78b2eed** (job 53798801): asked for 8h walltime, used 10% → `--time=01:15:00`
- **13eb38e7-b9d1-40cf-bf2a-1ce5a78b2eed** (job 53798802): asked for 8h walltime, used 3% → `--time=00:30:00`
- **13eb38e7-b9d1-40cf-bf2a-1ce5a78b2eed** (job 53798803): asked for 12h walltime, used 4% → `--time=01:00:00`
- **13eb38e7-b9d1-40cf-bf2a-1ce5a78b2eed** (job 53800450): asked for 8h walltime, used 3% → `--time=00:30:00`
- **13eb38e7-b9d1-40cf-bf2a-1ce5a78b2eed** (job 53800452): asked for 2h walltime, used 11% → `--time=00:30:00`
- **13eb38e7-b9d1-40cf-bf2a-1ce5a78b2eed** (job 53800454): asked for 8h walltime, used 2% → `--time=00:30:00`
- **b066a161-0a27-4123-b1e0-02754fe0be94** (job 53801180): asked for 8h walltime, used 3% → `--time=00:30:00`
- **b066a161-0a27-4123-b1e0-02754fe0be94** (job 53801181): asked for 2h walltime, used 11% → `--time=00:30:00`
- **b066a161-0a27-4123-b1e0-02754fe0be94** (job 53801183): asked for 8h walltime, used 3% → `--time=00:30:00`
- **b066a161-0a27-4123-b1e0-02754fe0be94** (job 53801184): asked for 12h walltime, used 5% → `--time=01:00:00`
- **rot_chm13_lymphoma** (job 53801517): asked for 24h walltime, used 0% → `--time=00:30:00`
- **b066a161-0a27-4123-b1e0-02754fe0be94** (job 53801542): asked for 2h walltime, used 11% → `--time=00:30:00`
- **e5bf2767-f079-46bf-a23b-387986090014** (job 53814695): asked for 2h walltime, used 11% → `--time=00:30:00`
