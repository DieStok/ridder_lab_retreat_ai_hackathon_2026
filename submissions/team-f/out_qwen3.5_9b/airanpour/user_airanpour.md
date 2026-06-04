# airanpour — weekly HPC report

## At a glance

- Jobs: **21** (3 failed, 0 cancelled, 2 timed out)
- CPU-hours: **504.2**, GPU-hours: **50.2**
- Avg CPU efficiency: **100%**, avg walltime usage: **23%**
- Energy: **35.16 kWh** ≈ **9.49 kg CO₂**

## Serious report

You consumed 504.2 CPU-hours this week while generating 9.49 kg of CO2 across twenty-one jobs including three that failed due to walltime limits. Several submissions like job_id=53848344 requested ninety-six hours but finished in a fraction of the time, wasting significant queue availability for others. Next time run your long-running tasks with adjusted limits such as this suggestion to use `--time=05:00:00`.

## Roy says

> You reserved ninety-six hours of walltime for a figure job that finished in one percent while twenty-one jobs queued behind you waiting like patients at a doctor’s surgery where everyone else gets their actual work done on GPUs instead of bash timeouts killing them off, airanpour. Your requests are so bloated I’m surprised your `bash` scripts didn’t finish before they could even ask to be killed by running out of their own allocated time and wasting ninety-six hours when the system only used one percent like it did there for another job in that list. Stop treating the HPC like a personal vacation rental where you book an entire suite just to stand in front of the minibar while everyone else gets their actual work done on GPUs instead of bash timeouts killing them off. Next time check your walltime limits against reality before asking for ninety-six hours when something shorter would suffice, mate.

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
