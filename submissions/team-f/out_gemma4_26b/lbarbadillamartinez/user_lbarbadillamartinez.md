# lbarbadillamartinez — weekly HPC report

## At a glance

- Jobs: **69** (9 failed, 1 cancelled, 19 timed out)
- CPU-hours: **478.3**, GPU-hours: **217.7**
- Avg CPU efficiency: **97%**, avg walltime usage: **40%**
- Energy: **128.64 kWh** ≈ **34.73 kg CO₂**

## Serious report

Total usage this week was 478.3 CPU-hours and 128.64 kWh, generating 34.73 kg of CO2. Nineteen jobs failed because they ran out of walltime. Job 53430782_0 was heavily overprovisioned, using only 7% of its requested 40-hour allocation. For similar workloads, next time use `--time=05:00:00`.

## Roy says

> You requested 40h of walltime for a job that finished in 0%. With 19 timeouts and 9 failed jobs, you are essentially using the cluster as an expensive way to host a digital void. It is quite an achievement to reserve so much hardware for no reason.
Advice: Try running your script locally before requesting 40h of walltime.

## Recommendations for next time

- **synthetic_all_kozaks_ARRAYS** (job 53430782_0): asked for 40h walltime, used 7% → `--time=05:00:00`
- **synthetic_all_kozaks_ARRAYS** (job 53610647_0): asked for 40h walltime, used 0% → `--time=00:30:00`
