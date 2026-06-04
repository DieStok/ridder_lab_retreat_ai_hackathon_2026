"""Tests for roybot's sacct parser, schema, and analysis.

Run from submissions/team-f/:

    uv run --python .venv/bin/python pytest -q        # or: .venv/bin/python -m pytest -q

Focus: every field of the Job schema is parsed correctly from real-shaped
`sacct --parsable2` rows, including the case where sacct prints `CPUTimeRAW`
(all-caps) while we request `CPUTimeRaw`. Also format-checks every committed
EXAMPLE_*.txt dump so a malformed real dump fails CI rather than at runtime.
"""
from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest

from roybot.data import (
    Job,
    _parse_gpus,
    _parse_mem,
    _parse_timelimit,
    parse_sacct_parsable2,
)
from roybot.analyze import aggregate, apply_renames

TEAM_DIR = Path(__file__).resolve().parent.parent

# A header with the real-world all-caps CPUTimeRAW (the bug that zeroed CPU
# efficiency on real data) plus a GPU job, a segfault, and an unlimited limit.
HEADER = (
    "JobID|User|JobName|Partition|State|AllocCPUS|ReqMem|Timelimit|"
    "ElapsedRaw|CPUTimeRAW|MaxRSS|ReqTRES|AllocTRES|ExitCode"
)
ROWS = [
    # full CPU job, 50% CPU eff (cpu_time = half of alloc*elapsed)
    "1001|alice|train|cpu|COMPLETED|4|16G|01:00:00|3600|7200|8G|cpu=4,mem=16G|cpu=4,mem=16G|0:0",
    # GPU job, 2 GPUs, day-format timelimit
    "1002|bob|fit|gpu|COMPLETED|8|64G|1-00:00:00|3600|28800|32000M|cpu=8|cpu=8,mem=64G,gres/gpu=2,billing=8|0:0",
    # segfault, unlimited timelimit, MaxRSS in K
    "1003|carol|seg|cpu|FAILED|1|4G|UNLIMITED|120|120|2048000K||cpu=1,mem=4G|139:0",
    # a step entry that must be skipped (JobID contains a dot)
    "1001.batch|alice|batch|cpu|COMPLETED|4|16G|01:00:00|3600|7200|8G||cpu=4|0:0",
]
SAMPLE = HEADER + "\n" + "\n".join(ROWS)

ALL_FIELDS = {f.name for f in dataclasses.fields(Job)}


def test_schema_has_expected_fields():
    expected = {
        "job_id", "user", "job_name", "partition", "state", "alloc_cpus",
        "req_mem_mb", "timelimit_sec", "elapsed_sec", "cpu_time_sec",
        "max_rss_mb", "n_gpus", "exit_code", "raw",
    }
    assert expected <= ALL_FIELDS


def test_parses_all_fields_and_skips_steps():
    jobs = parse_sacct_parsable2(SAMPLE)
    assert len(jobs) == 3  # the .batch step is skipped

    a, b, c = jobs
    # --- every scalar field on the first job ---
    assert a.job_id == "1001"
    assert a.user == "alice"
    assert a.job_name == "train"
    assert a.partition == "cpu"
    assert a.state == "COMPLETED"
    assert a.alloc_cpus == 4
    assert a.req_mem_mb == 16 * 1024
    assert a.timelimit_sec == 3600
    assert a.elapsed_sec == 3600
    assert a.cpu_time_sec == 7200          # <-- proves CPUTimeRAW (all-caps) is read
    assert a.max_rss_mb == 8 * 1024
    assert a.n_gpus == 0
    assert a.exit_code == "0:0"
    assert a.raw  # raw row preserved

    # --- GPU parsing + day-format timelimit ---
    assert b.n_gpus == 2
    assert b.timelimit_sec == 86400

    # --- segfault + unlimited + K-unit MaxRSS ---
    assert c.exit_code.startswith("139")
    assert c.timelimit_sec is None
    assert c.max_rss_mb == 2048000 // 1024


def test_cputime_case_insensitive_equivalence():
    """`CPUTimeRaw` and `CPUTimeRAW` headers must parse identically."""
    lower = SAMPLE.replace("CPUTimeRAW", "CPUTimeRaw")
    assert [j.cpu_time_sec for j in parse_sacct_parsable2(lower)] == \
           [j.cpu_time_sec for j in parse_sacct_parsable2(SAMPLE)]


def test_efficiency_properties():
    a, b, c = parse_sacct_parsable2(SAMPLE)
    assert a.cpu_efficiency == pytest.approx(0.5)      # 7200 / (4 * 3600)
    assert a.mem_efficiency == pytest.approx(0.5)      # 8G / 16G
    assert a.time_efficiency == pytest.approx(1.0)     # 3600 / 3600
    assert c.time_efficiency is None                   # unlimited -> None
    assert c.mem_efficiency == pytest.approx(2000 / 4096)  # 2048000K=2000M vs 4G req
    assert a.alloc_cpu_seconds == 4 * 3600


@pytest.mark.parametrize("text,expected_mb", [
    ("16G", 16 * 1024), ("16000M", 16000), ("12345K", 12345 // 1024),
    ("2.3G", int(2.3 * 1024)), ("4Gn", 4 * 1024), ("", None), ("none", None),
])
def test_parse_mem(text, expected_mb):
    assert _parse_mem(text) == expected_mb


@pytest.mark.parametrize("text,expected_sec", [
    ("01:00:00", 3600), ("1-00:00:00", 86400), ("00:30", 30),
    ("2-12:30:00", 2 * 86400 + 12 * 3600 + 30 * 60), ("UNLIMITED", None), ("", None),
])
def test_parse_timelimit(text, expected_sec):
    assert _parse_timelimit(text) == expected_sec


@pytest.mark.parametrize("tres,n", [
    ("cpu=8,mem=64G,gres/gpu=2,billing=8", 2),
    ("cpu=8,mem=64G,gres/gpu:a100=4", 4),
    ("cpu=8,mem=64G", 0),
    ("", 0),
])
def test_parse_gpus(tres, n):
    assert _parse_gpus(tres) == n


def test_aggregate_and_rename():
    stats = aggregate(parse_sacct_parsable2(SAMPLE))
    assert set(stats) == {"alice", "bob", "carol"}
    apply_renames(stats, {"alice": "Alice the Allocator"})
    assert stats["alice"].name == "Alice the Allocator"
    assert stats["bob"].name == "bob"                 # untouched -> falls back to username
    assert stats["carol"].n_jobs == 1
    # rename of a user not present is a silent no-op
    apply_renames(stats, {"nobody": "Ghost"})
    assert "nobody" not in stats


# --- format-check the committed real dumps --------------------------------
EXAMPLE_FILES = sorted(TEAM_DIR.glob("EXAMPLE_*.txt"))


def test_example_files_present():
    # dstoker + the five requested labmates (lbarbadilla -> lbarbadillamartinez)
    names = {p.name for p in EXAMPLE_FILES}
    for needed in ["EXAMPLE_DIETER_05_06_2026.txt", "EXAMPLE_AIRANPOUR_05_06_2026.txt",
                   "EXAMPLE_CFIORENZANI_05_06_2026.txt", "EXAMPLE_LBARBADILLAMARTINEZ_05_06_2026.txt",
                   "EXAMPLE_ATSAKALI_05_06_2026.txt", "EXAMPLE_RSTRAVER_05_06_2026.txt"]:
        assert needed in names, f"missing example dump: {needed}"


@pytest.mark.parametrize("path", EXAMPLE_FILES, ids=lambda p: p.name)
def test_example_dump_format_checks_out(path):
    """Every committed dump parses without exception and every Job is well-typed."""
    jobs = parse_sacct_parsable2(path.read_text())
    for j in jobs:
        assert isinstance(j.job_id, str) and j.job_id
        assert isinstance(j.user, str) and j.user
        assert isinstance(j.alloc_cpus, int)
        assert isinstance(j.elapsed_sec, int)
        assert isinstance(j.cpu_time_sec, int)
        assert isinstance(j.n_gpus, int)
        assert j.req_mem_mb is None or isinstance(j.req_mem_mb, int)
        assert j.timelimit_sec is None or isinstance(j.timelimit_sec, int)
        # computed properties must never raise
        _ = (j.cpu_efficiency, j.mem_efficiency, j.time_efficiency, j.alloc_cpu_seconds)
    # aggregation over the real dump must not raise either
    aggregate(jobs)
