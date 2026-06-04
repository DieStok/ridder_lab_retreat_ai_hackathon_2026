"""Parse SLURM `sacct --parsable2` output into typed Job records.

Expected sacct invocation (what Roy would run):

    sacct -X -a \
      --starttime=now-7days \
      --format=JobID,User,JobName,Partition,State,AllocCPUS,ReqMem,Timelimit,\
ElapsedRaw,CPUTimeRaw,MaxRSS,ReqTRES,AllocTRES,ExitCode \
      --parsable2 > dump.txt

We're forgiving about missing columns: if a column is absent, the field is None.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Job:
    job_id: str
    user: str
    job_name: str
    partition: str
    state: str
    alloc_cpus: int
    req_mem_mb: int | None       # parsed from ReqMem (e.g. "16000M", "32G", "4Gn")
    timelimit_sec: int | None    # parsed from Timelimit (DD-HH:MM:SS or HH:MM:SS)
    elapsed_sec: int             # ElapsedRaw is seconds
    cpu_time_sec: int            # CPUTimeRaw is seconds
    max_rss_mb: int | None       # parsed from MaxRSS (e.g. "12345K", "2.3G")
    n_gpus: int                  # parsed out of AllocTRES (gres/gpu=N)
    exit_code: str = ""
    raw: dict[str, str] = field(default_factory=dict)

    @property
    def alloc_cpu_seconds(self) -> int:
        return self.alloc_cpus * self.elapsed_sec

    @property
    def cpu_efficiency(self) -> float:
        """0.0–1.0. Same definition as `seff`."""
        denom = self.alloc_cpu_seconds
        if denom <= 0:
            return 0.0
        return min(1.0, self.cpu_time_sec / denom)

    @property
    def mem_efficiency(self) -> float | None:
        if self.req_mem_mb is None or self.max_rss_mb is None or self.req_mem_mb <= 0:
            return None
        return min(1.0, self.max_rss_mb / self.req_mem_mb)

    @property
    def time_efficiency(self) -> float | None:
        if self.timelimit_sec is None or self.timelimit_sec <= 0:
            return None
        return min(1.0, self.elapsed_sec / self.timelimit_sec)


def _parse_mem(s: str) -> int | None:
    """ReqMem / MaxRSS in SLURM can look like '16000M', '32G', '12345K', '2.3Gn'."""
    if not s:
        return None
    m = re.match(r"^\s*([\d.]+)\s*([KMGTP]?)", s.strip())
    if not m:
        return None
    val = float(m.group(1))
    unit = m.group(2) or "M"
    mult = {"K": 1 / 1024, "M": 1, "G": 1024, "T": 1024 * 1024, "P": 1024**3}[unit]
    return int(val * mult)


def _parse_timelimit(s: str) -> int | None:
    """SLURM time formats: 'DD-HH:MM:SS', 'HH:MM:SS', 'MM:SS', 'UNLIMITED'."""
    if not s or s.upper() in ("UNLIMITED", "NONE", ""):
        return None
    days = 0
    if "-" in s:
        d, s = s.split("-", 1)
        days = int(d)
    parts = s.split(":")
    if len(parts) == 3:
        h, m, sec = (int(p) for p in parts)
    elif len(parts) == 2:
        h = 0
        m, sec = (int(p) for p in parts)
    else:
        return None
    return days * 86400 + h * 3600 + m * 60 + sec


def _parse_gpus(alloc_tres: str) -> int:
    """AllocTRES looks like 'cpu=8,mem=64G,gres/gpu=2,billing=8'."""
    if not alloc_tres:
        return 0
    m = re.search(r"gres/gpu(?::[a-z0-9_]+)?=(\d+)", alloc_tres)
    return int(m.group(1)) if m else 0


def parse_sacct_parsable2(text: str) -> list[Job]:
    """Parse `sacct --parsable2` output. First line is the header."""
    lines = [ln.rstrip("\n") for ln in text.splitlines() if ln.strip()]
    if not lines:
        return []
    header = lines[0].split("|")
    jobs: list[Job] = []
    for line in lines[1:]:
        cells = line.split("|")
        if len(cells) < len(header):
            cells = cells + [""] * (len(header) - len(cells))
        row = dict(zip(header, cells, strict=False))
        # Case-insensitive column access. Real `sacct` normalises some headers
        # to a different case than the field list we request — e.g. we ask for
        # `CPUTimeRaw` but sacct prints `CPUTimeRAW`. A plain `row["CPUTimeRaw"]`
        # then misses, silently zeroing cpu_time (and CPU efficiency) on real
        # data while the mock path — which builds Jobs directly — looks fine.
        lc = {k.lower(): v for k, v in row.items()}

        def col(name: str, default: str = "") -> str:
            return lc.get(name.lower(), default)

        # Skip step entries (we ran with -X but be defensive).
        if "." in col("JobID"):
            continue
        try:
            jobs.append(
                Job(
                    job_id=col("JobID"),
                    user=col("User") or "unknown",
                    job_name=col("JobName"),
                    partition=col("Partition"),
                    state=col("State"),
                    alloc_cpus=int(col("AllocCPUS") or 0),
                    req_mem_mb=_parse_mem(col("ReqMem")),
                    timelimit_sec=_parse_timelimit(col("Timelimit")),
                    elapsed_sec=int(col("ElapsedRaw") or 0),
                    cpu_time_sec=int(col("CPUTimeRaw") or 0),
                    max_rss_mb=_parse_mem(col("MaxRSS")),
                    n_gpus=_parse_gpus(col("AllocTRES")),
                    exit_code=col("ExitCode"),
                    raw=row,
                )
            )
        except (ValueError, KeyError):
            continue
    return jobs


def load_sacct_file(path: str | Path) -> list[Job]:
    return parse_sacct_parsable2(Path(path).read_text())
