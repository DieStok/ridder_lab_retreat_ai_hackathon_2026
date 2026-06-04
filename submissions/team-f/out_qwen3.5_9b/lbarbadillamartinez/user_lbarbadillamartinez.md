# lbarbadillamartinez — weekly HPC report

## At a glance

- Jobs: **69** (9 failed, 1 cancelled, 19 timed out)
- CPU-hours: **478.3**, GPU-hours: **217.7**
- Avg CPU efficiency: **97%**, avg walltime usage: **40%**
- Energy: **128.64 kWh** ≈ **34.73 kg CO₂**

## Serious report

You consumed 478 CPU hours and generated 34 kg CO2 across your sixty-nine jobs this week, though average time efficiency was only 0.4 due to frequent walltime kills on synthetic_all_kozaks_ARRAYS tasks that finished in less than ten percent of their requested duration. Several specific runs allocated forty-hour slots while only consuming zero or seven percent capacity before hitting the timeout limit enforced by your batch scheduler system during this reporting window. To prevent these wasted allocations and improve queue availability for others using similar code paths, next time use `--time=05:00:00` to better align walltime requests with actual processing needs.

## Roy says

> You asked for forty hours of walltime yet finished in seven percent, effectively wasting 478.3 CPU hours on tasks that vanish faster than your patience after a long day at the lab bench. Nineteen jobs timed out while you pushed sixty-nine instances into our queue without checking if they were actually ready to handle that amount of reserved space before getting killed by limits too early for us to care about them any further. Your scripts clearly have no idea what time efficiency means, yet somehow you keep managing to generate enough flags until we reach a breaking point where even the GPU hours stop making sense in your favour anyway. Next time try setting smaller walltime limits so we can save some electricity because clearly you enjoy being told about cancelled jobs before it's too late for anyone else involved here at all.

## Recommendations for next time

- **synthetic_all_kozaks_ARRAYS** (job 53430782_0): asked for 40h walltime, used 7% → `--time=05:00:00`
- **synthetic_all_kozaks_ARRAYS** (job 53610647_0): asked for 40h walltime, used 0% → `--time=00:30:00`
