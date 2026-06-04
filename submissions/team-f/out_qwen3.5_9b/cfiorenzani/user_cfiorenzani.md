# cfiorenzani — weekly HPC report

## At a glance

- Jobs: **35** (12 failed, 0 cancelled, 0 timed out)
- CPU-hours: **67.0**, GPU-hours: **1.8**
- Avg CPU efficiency: **100%**, avg walltime usage: **9%**
- Energy: **1.94 kWh** ≈ **0.52 kg CO₂**

## Serious report

You consumed 67 CPU-hours across 35 jobs this week, generating 0.52 kg CO2 while running three instances where requested walltime exceeded actual usage by a large margin. The worst offender was job `bash` (ID 53400595) which utilized only 8% of its allocated ten-hour window before completion. To reduce future waste, next time use `--time=01:30:00`.

## Roy says

> You reserved 10 hours of walltime while that bash script finished in only 8 per cent efficiency alongside 67.0 CPU hours and 337.8 gigabytes memory usage which suggests you are treating the cluster like a waiting room rather than a compute farm despite 12 failed jobs recorded for your session. It seems your patience with queueing times is lower than caffeine tolerance next to recommendations suggesting --time=01:30:00 so please stop burning through carbon dioxide emissions calculated at 0.52 kilograms unless you really need that walltime again? If the recommendation flags suggest setting the request down next run or we will all have to watch your queue sit idle for even longer than necessary while wasting one point nine four kilowatts of electricity, try reducing it accordingly before someone else suggests a flag change themselves instead.

## Recommendations for next time

- **bash** (job 53400595): asked for 10h walltime, used 8% → `--time=01:30:00`
- **bash** (job 53401918): asked for 10h walltime, used 2% → `--time=00:30:00`
- **parm_mutagenesis** (job 53609966): asked for 12h walltime, used 11% → `--time=02:15:00`
