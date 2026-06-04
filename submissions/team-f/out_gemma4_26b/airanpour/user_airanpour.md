# airanpour — weekly HPC report

## At a glance

- Jobs: **21** (3 failed, 0 cancelled, 2 timed out)
- CPU-hours: **504.2**, GPU-hours: **50.2**
- Avg CPU efficiency: **100%**, avg walltime usage: **23%**
- Energy: **35.16 kWh** ≈ **9.49 kg CO₂**

## Serious report

You used 504.2 CPU-hours and 9.49 kg CO2 this week. High walltime overprovisioning across several jobs resulted in an average time efficiency of only 23%. For `mnm_geo_medullo`, next time use `--time=00:30:00`.

## Roy says

> You requested 96h walltime and finished in only 4%. It is quite a feat to hold the cluster hostage while other jobs use as little as 1% of their allocation. All that for 7381.9 GB hours.
Try checking if your code actually runs before you book a holiday on the scheduler.

## Recommendations for next time

- **mnm_geo_medullo** (job 53608780): asked for 12h walltime, used 1% → `--time=00:30:00`
- **mnm_geo_medullo_v2** (job 53609787): asked for 12h walltime, used 1% → `--time=00:30:00`
- **mnm_hier_bilin_v2** (job 53611871): asked for 24h walltime, used 8% → `--time=03:00:00`
- **mnm_hier_bilin_v3e5** (job 53634746): asked for 24h walltime, used 5% → `--time=02:15:00`
- **mnm_hier_v5_heads** (job 53636380): asked for 24h walltime, used 13% → `--time=05:00:00`
- **mnm_hier_v6_factorized** (job 53796806): asked for 18h walltime, used 11% → `--time=03:15:00`
- **mnm_v5_once** (job 53806128): asked for 24h walltime, used 13% → `--time=05:00:00`
- **mnm_v6_once** (job 53806171): asked for 18h walltime, used 11% → `--time=03:00:00`
- **fig3_complete_v6** (job 53848344): asked for 96h walltime, used 11% → `--time=16:30:00`
- **fig3_complete_v6** (job 53886178): asked for 96h walltime, used 4% → `--time=06:45:00`
- **mnm_domain_shift** (job 53893447): asked for 36h walltime, used 10% → `--time=06:00:00`
- **fig3_sts_v6** (job 53896511): asked for 72h walltime, used 1% → `--time=01:15:00`
