# tachterberg — weekly HPC report

## At a glance

- Jobs: **146921** (7753 failed, 0 cancelled, 6 timed out)
- CPU-hours: **3529.8**, GPU-hours: **0.0**
- Avg CPU efficiency: **99%**, avg walltime usage: **2%**
- Energy: **49.42 kWh** ≈ **13.34 kg CO₂**

## Serious report

You consumed 3529.8 CPU-hours and emitted 13.34 kg CO2 during your recent computing sessions this week. Your average time efficiency remains low at 0.03, indicating that many jobs like job 53798799 requested eight hours of walltime while completing in only a fraction of the allowed duration. This pattern suggests you are allocating more queue resources than necessary for fast-running batch tasks or utilities within your workflow pipeline. Next time use `--time=00:30:00` to align requests with actual runtime requirements and free up capacity for other users.

## Roy says

> You submitted 146921 jobs while asking for 24 hours on your rot_chm13_lymphoma task that finished in 0 percent of its requested time without generating any GPU usage whatsoever. Your average CPU efficiency was perfect at one point zero yet you continue to request walltimes longer than the lifespan of a standard lab session only to finish less than five per cent while consuming thirteen point three four kilograms of carbon dioxide emissions for every single exit code failure. If you are going to run scripts that ask for eight hours and finished in three percent, please just set reasonable limits like thirty minutes before we charge you for this energy output calculated at forty nine point four two kilowatt-hours per job batch.

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
