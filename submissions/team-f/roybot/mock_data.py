"""A built-in fake sacct dump with realistic over/underprovision patterns.

Characters (fictional usage patterns, real lab names):
  - roy:     the admin. Modest, efficient. He knows what he's doing.
  - merel:   asks for 8 GPUs, uses 1. Multiple times.
  - claudio: gigantic memory requests, 2% used. Also leaves jobs idle.
  - dieter:  fine, mostly. Has one runaway segfault though.
  - huub:    timelimit hoarder — 7-day walltime, finishes in 20 min.
"""
from __future__ import annotations

from .data import Job

# These are NOT runtime-derived — they're hand-crafted to give the LLM something
# concrete to roast. Keep the numbers realistic-ish for the lab's HPC partition.
MOCK_JOBS: list[Job] = [
    # roy — fine across the board
    Job(
        job_id="100001", user="roy", job_name="sacct_audit", partition="cpu",
        state="COMPLETED", alloc_cpus=2, req_mem_mb=8000, timelimit_sec=3600,
        elapsed_sec=2700, cpu_time_sec=2 * 2400, max_rss_mb=6200, n_gpus=0,
        exit_code="0:0",
    ),
    Job(
        job_id="100002", user="roy", job_name="cluster_health", partition="cpu",
        state="COMPLETED", alloc_cpus=1, req_mem_mb=4000, timelimit_sec=1800,
        elapsed_sec=1500, cpu_time_sec=1400, max_rss_mb=3100, n_gpus=0,
        exit_code="0:0",
    ),
    # merel — GPU hoarder
    Job(
        job_id="100003", user="merel", job_name="train_diffusion", partition="gpu",
        state="COMPLETED", alloc_cpus=16, req_mem_mb=128000, timelimit_sec=86400,
        elapsed_sec=43200, cpu_time_sec=16 * 5000, max_rss_mb=42000, n_gpus=8,
        exit_code="0:0",
    ),
    Job(
        job_id="100004", user="merel", job_name="train_diffusion", partition="gpu",
        state="COMPLETED", alloc_cpus=16, req_mem_mb=128000, timelimit_sec=86400,
        elapsed_sec=21600, cpu_time_sec=16 * 2400, max_rss_mb=38000, n_gpus=8,
        exit_code="0:0",
    ),
    Job(
        job_id="100005", user="merel", job_name="debug_run", partition="gpu",
        state="CANCELLED", alloc_cpus=16, req_mem_mb=128000, timelimit_sec=86400,
        elapsed_sec=600, cpu_time_sec=16 * 30, max_rss_mb=12000, n_gpus=8,
        exit_code="0:15",
    ),
    # claudio — memory dragon, leaves jobs idle
    Job(
        job_id="100006", user="claudio", job_name="rna_pipeline", partition="cpu",
        state="COMPLETED", alloc_cpus=8, req_mem_mb=500000, timelimit_sec=172800,
        elapsed_sec=86400, cpu_time_sec=8 * 18000, max_rss_mb=9500, n_gpus=0,
        exit_code="0:0",
    ),
    Job(
        job_id="100007", user="claudio", job_name="rna_pipeline", partition="cpu",
        state="COMPLETED", alloc_cpus=8, req_mem_mb=500000, timelimit_sec=172800,
        elapsed_sec=72000, cpu_time_sec=8 * 16000, max_rss_mb=11000, n_gpus=0,
        exit_code="0:0",
    ),
    Job(
        job_id="100008", user="claudio", job_name="jupyter_zombie", partition="gpu",
        state="TIMEOUT", alloc_cpus=4, req_mem_mb=64000, timelimit_sec=86400,
        elapsed_sec=86400, cpu_time_sec=4 * 4000, max_rss_mb=8000, n_gpus=1,
        exit_code="0:0",
    ),
    # dieter — mostly fine
    Job(
        job_id="100009", user="dieter", job_name="fit_glm", partition="cpu",
        state="COMPLETED", alloc_cpus=4, req_mem_mb=16000, timelimit_sec=7200,
        elapsed_sec=6300, cpu_time_sec=4 * 5800, max_rss_mb=13000, n_gpus=0,
        exit_code="0:0",
    ),
    Job(
        job_id="100010", user="dieter", job_name="fit_glm", partition="cpu",
        state="FAILED", alloc_cpus=4, req_mem_mb=16000, timelimit_sec=7200,
        elapsed_sec=120, cpu_time_sec=4 * 60, max_rss_mb=2000, n_gpus=0,
        exit_code="139:0",  # segfault
    ),
    # huub — wall-time padder
    Job(
        job_id="100011", user="huub", job_name="quick_qc", partition="cpu",
        state="COMPLETED", alloc_cpus=2, req_mem_mb=8000, timelimit_sec=604800,
        elapsed_sec=1200, cpu_time_sec=2 * 1100, max_rss_mb=7000, n_gpus=0,
        exit_code="0:0",
    ),
    Job(
        job_id="100012", user="huub", job_name="quick_qc", partition="cpu",
        state="COMPLETED", alloc_cpus=2, req_mem_mb=8000, timelimit_sec=604800,
        elapsed_sec=900, cpu_time_sec=2 * 850, max_rss_mb=6800, n_gpus=0,
        exit_code="0:0",
    ),
]


def load_mock() -> list[Job]:
    return list(MOCK_JOBS)
