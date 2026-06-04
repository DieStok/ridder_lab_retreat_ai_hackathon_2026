# cfiorenzani — weekly HPC report

## At a glance

- Jobs: **35** (12 failed, 0 cancelled, 0 timed out)
- CPU-hours: **67.0**, GPU-hours: **1.8**
- Avg CPU efficiency: **100%**, avg walltime usage: **9%**
- Energy: **1.94 kWh** ≈ **0.52 kg CO₂**

## Serious report

Your workload consumed 67.0 CPU-hours and 1.94 kWh of energy. Twelve of your 35 submitted jobs failed during this window. Job 53400595 was significantly overprovisioned, using only 8% of its requested walltime. Next time use `--time=01:30:00`.

## Roy says

> You requested 10h of walltime and finished in 2% of it. It is quite an achievement to rack up 12 failed jobs while barely using your allocated time. Try checking if your code actually works before you reserve the cluster for nothing.

## Recommendations for next time

- **bash** (job 53400595): asked for 10h walltime, used 8% → `--time=01:30:00`
- **bash** (job 53401918): asked for 10h walltime, used 2% → `--time=00:30:00`
- **parm_mutagenesis** (job 53609966): asked for 12h walltime, used 11% → `--time=02:15:00`
