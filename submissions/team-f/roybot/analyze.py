"""Aggregate Jobs into per-user stats Roy would actually mention in stand-up.

Efficiency thresholds and power numbers are intentionally tunable so the team
can argue about them on Slack later.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean

from .data import Job

# --- Power / CO2 assumptions (Netherlands grid, 2024) ---------------------
# Sources cited in PROPOSAL.md. Order of magnitude is what matters here.
GRID_KGCO2_PER_KWH = 0.27
PUE = 1.4                    # datacenter overhead factor
CPU_TDP_W_PER_CORE = 10.0    # Roughly per-core slice of a modern Xeon/EPYC
GPU_TDP_W = 400.0            # A100-ish ballpark; adjust if Utrecht runs different cards

# --- Overprovision thresholds ---------------------------------------------
LOW_CPU_EFF = 0.30
LOW_MEM_EFF = 0.25
LOW_TIME_EFF = 0.20          # asked for 5x what you needed
MIN_JOB_SEC_FOR_FLAG = 300   # ignore tiny jobs for flag purposes


@dataclass
class Flag:
    job_id: str
    job_name: str
    kind: str        # 'cpu_overprov', 'mem_overprov', 'time_overprov', 'killed', 'segfault'
    detail: str      # short human string


@dataclass
class UserStats:
    user: str
    n_jobs: int = 0
    n_failed: int = 0
    n_cancelled: int = 0
    n_timeout: int = 0
    cpu_hours: float = 0.0
    gpu_hours: float = 0.0
    mem_gb_hours: float = 0.0
    avg_cpu_eff: float = 0.0
    avg_mem_eff: float | None = None
    avg_time_eff: float | None = None
    kwh: float = 0.0
    kg_co2: float = 0.0
    flags: list[Flag] = field(default_factory=list)
    worst_offender: Flag | None = None

    def to_dict(self) -> dict:
        return {
            "user": self.user,
            "n_jobs": self.n_jobs,
            "n_failed": self.n_failed,
            "n_cancelled": self.n_cancelled,
            "n_timeout": self.n_timeout,
            "cpu_hours": round(self.cpu_hours, 1),
            "gpu_hours": round(self.gpu_hours, 1),
            "mem_gb_hours": round(self.mem_gb_hours, 1),
            "avg_cpu_eff": round(self.avg_cpu_eff, 2),
            "avg_mem_eff": round(self.avg_mem_eff, 2) if self.avg_mem_eff is not None else None,
            "avg_time_eff": round(self.avg_time_eff, 2) if self.avg_time_eff is not None else None,
            "kwh": round(self.kwh, 2),
            "kg_co2": round(self.kg_co2, 2),
            "flags": [f.__dict__ for f in self.flags],
            "worst_offender": self.worst_offender.__dict__ if self.worst_offender else None,
        }


def _job_kwh(job: Job) -> float:
    hours = job.elapsed_sec / 3600.0
    cpu_w = job.alloc_cpus * CPU_TDP_W_PER_CORE
    gpu_w = job.n_gpus * GPU_TDP_W
    return (cpu_w + gpu_w) * hours * PUE / 1000.0


def _flag_job(job: Job) -> list[Flag]:
    flags: list[Flag] = []
    if job.elapsed_sec >= MIN_JOB_SEC_FOR_FLAG:
        if job.cpu_efficiency < LOW_CPU_EFF and job.alloc_cpus > 1:
            flags.append(Flag(
                job.job_id, job.job_name, "cpu_overprov",
                f"asked for {job.alloc_cpus} CPUs, used {int(job.cpu_efficiency * 100)}%"
            ))
        mem_eff = job.mem_efficiency
        if mem_eff is not None and mem_eff < LOW_MEM_EFF and job.req_mem_mb and job.req_mem_mb > 1000:
            flags.append(Flag(
                job.job_id, job.job_name, "mem_overprov",
                f"asked for {job.req_mem_mb // 1024} GB RAM, peaked at {int(mem_eff * 100)}%"
            ))
        time_eff = job.time_efficiency
        if time_eff is not None and time_eff < LOW_TIME_EFF and job.timelimit_sec and job.timelimit_sec > 3600:
            flags.append(Flag(
                job.job_id, job.job_name, "time_overprov",
                f"asked for {job.timelimit_sec // 3600}h walltime, finished in {int(time_eff * 100)}%"
            ))
    if job.state == "TIMEOUT":
        flags.append(Flag(job.job_id, job.job_name, "killed", "ran out of walltime"))
    if job.exit_code.startswith("139"):
        flags.append(Flag(job.job_id, job.job_name, "segfault", "SIGSEGV — exit 139"))
    if job.state == "CANCELLED":
        flags.append(Flag(job.job_id, job.job_name, "killed", "cancelled before completion"))
    return flags


def aggregate(jobs: list[Job]) -> dict[str, UserStats]:
    by_user: dict[str, list[Job]] = {}
    for j in jobs:
        by_user.setdefault(j.user, []).append(j)

    out: dict[str, UserStats] = {}
    for user, ujobs in by_user.items():
        s = UserStats(user=user, n_jobs=len(ujobs))
        cpu_effs: list[float] = []
        mem_effs: list[float] = []
        time_effs: list[float] = []
        for j in ujobs:
            s.cpu_hours += j.alloc_cpu_seconds / 3600.0
            s.gpu_hours += j.n_gpus * (j.elapsed_sec / 3600.0)
            if j.req_mem_mb:
                s.mem_gb_hours += (j.req_mem_mb / 1024.0) * (j.elapsed_sec / 3600.0)
            s.kwh += _job_kwh(j)
            if j.state == "FAILED":
                s.n_failed += 1
            elif j.state == "CANCELLED":
                s.n_cancelled += 1
            elif j.state == "TIMEOUT":
                s.n_timeout += 1
            cpu_effs.append(j.cpu_efficiency)
            if j.mem_efficiency is not None:
                mem_effs.append(j.mem_efficiency)
            if j.time_efficiency is not None:
                time_effs.append(j.time_efficiency)
            s.flags.extend(_flag_job(j))

        s.avg_cpu_eff = mean(cpu_effs) if cpu_effs else 0.0
        s.avg_mem_eff = mean(mem_effs) if mem_effs else None
        s.avg_time_eff = mean(time_effs) if time_effs else None
        s.kg_co2 = s.kwh * GRID_KGCO2_PER_KWH

        # "Worst offender" = most egregious flag, used to focus the roast.
        ranked = {"segfault": 4, "killed": 3, "mem_overprov": 2, "cpu_overprov": 1, "time_overprov": 1}
        if s.flags:
            s.worst_offender = max(s.flags, key=lambda f: ranked.get(f.kind, 0))

        out[user] = s
    return out


def lab_totals(stats: dict[str, UserStats]) -> dict:
    return {
        "n_users": len(stats),
        "total_cpu_hours": round(sum(s.cpu_hours for s in stats.values()), 1),
        "total_gpu_hours": round(sum(s.gpu_hours for s in stats.values()), 1),
        "total_kwh": round(sum(s.kwh for s in stats.values()), 2),
        "total_kg_co2": round(sum(s.kg_co2 for s in stats.values()), 2),
        "biggest_emitter": max(stats.values(), key=lambda s: s.kg_co2).user if stats else None,
    }
