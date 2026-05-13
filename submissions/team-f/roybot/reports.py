"""Glue: stats -> per-user reports + standup -> files on disk."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .analyze import UserStats, lab_totals
from .llm import LLM


@dataclass
class GeneratedReports:
    per_user_serious: dict[str, str]
    per_user_roast: dict[str, str]
    standup: str
    stats_by_user: dict[str, UserStats]

    def write(self, out_dir: str | Path) -> dict[str, Path]:
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        paths: dict[str, Path] = {}

        # Per-user markdown
        for user, serious in self.per_user_serious.items():
            roast = self.per_user_roast.get(user, "")
            stats = self.stats_by_user[user]
            p = out / f"user_{user}.md"
            p.write_text(_user_md(user, stats, serious, roast))
            paths[f"user_{user}"] = p

        # Stand-up transcript (this is what the TTS reads)
        p = out / "standup.txt"
        p.write_text(self.standup)
        paths["standup"] = p

        # JSON dump of raw stats for downstream tools
        p = out / "stats.json"
        p.write_text(json.dumps(
            {
                "lab_totals": lab_totals(self.stats_by_user),
                "per_user": {u: s.to_dict() for u, s in self.stats_by_user.items()},
            },
            indent=2,
        ))
        paths["stats"] = p

        return paths


def _user_md(user: str, stats: UserStats, serious: str, roast: str) -> str:
    recs_section = "_Nothing to fix — efficient as it gets._"
    if stats.recommendations:
        recs_section = "\n".join(
            f"- **{r.job_name}** (job {r.job_id}): {r.issue} → `{r.suggested_flag}`"
            for r in stats.recommendations
        )

    return (
        f"# {user} — weekly HPC report\n\n"
        f"## At a glance\n\n"
        f"- Jobs: **{stats.n_jobs}** "
        f"({stats.n_failed} failed, {stats.n_cancelled} cancelled, {stats.n_timeout} timed out)\n"
        f"- CPU-hours: **{stats.cpu_hours:.1f}**, GPU-hours: **{stats.gpu_hours:.1f}**\n"
        f"- Avg CPU efficiency: **{int(stats.avg_cpu_eff * 100)}%**"
        + (f", avg mem efficiency: **{int(stats.avg_mem_eff * 100)}%**" if stats.avg_mem_eff is not None else "")
        + (f", avg walltime usage: **{int(stats.avg_time_eff * 100)}%**" if stats.avg_time_eff is not None else "")
        + f"\n- Energy: **{stats.kwh:.2f} kWh** ≈ **{stats.kg_co2:.2f} kg CO₂**\n\n"
        f"## Serious report\n\n{serious}\n\n"
        f"## Roy says\n\n> {roast}\n\n"
        f"## Recommendations for next time\n\n"
        f"{recs_section}\n"
    )


def generate(stats_by_user: dict[str, UserStats], llm: LLM) -> GeneratedReports:
    serious = {u: llm.serious(s) for u, s in stats_by_user.items()}
    roast = {u: llm.roast(s) for u, s in stats_by_user.items()}
    standup = llm.standup(stats_by_user)
    return GeneratedReports(serious, roast, standup, stats_by_user)
