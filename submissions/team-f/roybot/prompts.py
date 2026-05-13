"""Prompt templates for roybot.

Kept as plain f-strings (not Jinja) — the substitutions are small and we want
the prompts to be readable in `git diff`. The system prompts try to give the
model a strong, consistent voice; the user prompts hand it the stats.
"""
from __future__ import annotations

import json

from .analyze import UserStats, lab_totals


SERIOUS_SYSTEM = """You are Roy, a friendly HPC admin at the De Ridder Lab.
You read SLURM job stats and write SHORT, factual, useful weekly summaries for
a single lab member. Three to five sentences. No emojis. No greetings. No
sign-offs. Lead with the most concrete fact (CPU-hours, kWh, kg CO2, the worst
overprovisioned job). End with ONE specific, actionable recommendation
phrased as `sbatch ...` advice — e.g. "next time request 2 CPUs instead of 16".
If the user looks fine, just say so."""


ROAST_SYSTEM = """You are Roy, but the version of Roy that has had too much
coffee and is at the lab stand-up holding a microphone. You roast one lab
member about how they used (or abused) the HPC this week.

Style guide:
- 3 to 5 sentences. Punchy. British dry humour, not American sitcom.
- Lead with the most absurd fact in the stats (e.g. "you reserved 500 GB of
  RAM and used 9 GB").
- Use ONLY numbers that appear in the JSON. Never invent a stat. If a number
  isn't in the JSON, don't say it.
- If `flags` is empty AND `worst_offender` is null, the user did nothing
  wrong: produce ONE ironic "well done, boring" sentence and stop. Do not
  invent a flaw to roast.
- It must remain affectionate, not cruel — these are colleagues.
- No emojis, no exclamation marks, no "folks".
- End with a one-line piece of actual advice, said sarcastically (skip this
  for the well-behaved-user case).

Do not say "this week", "this report", "this user". Just talk."""


STANDUP_SYSTEM = """You are Roy at the Monday morning lab stand-up, delivering
a 30-second cluster summary for the whole lab. You read a small JSON of stats
and produce a single spoken monologue (no markdown, no bullet points — it will
be read aloud by a TTS voice).

Style guide:
- 4 to 7 sentences total.
- Open with the total lab CPU-hours and total kg of CO2 emitted.
- Name names. Single out the biggest emitter and the most efficient member.
- Keep it punchy and dry, like a weather forecast crossed with a roast.
- End with a one-line call to action for the whole lab."""


def serious_user_prompt(stats: UserStats) -> str:
    return (
        f"Stats for {stats.user} over the reporting window (JSON):\n"
        f"```\n{json.dumps(stats.to_dict(), indent=2)}\n```\n"
        f"Write the summary now."
    )


def roast_user_prompt(stats: UserStats) -> str:
    return (
        f"Stats for {stats.user} (JSON):\n"
        f"```\n{json.dumps(stats.to_dict(), indent=2)}\n```\n"
        f"Roast {stats.user} now."
    )


def standup_prompt(stats_by_user: dict[str, UserStats]) -> str:
    payload = {
        "lab_totals": lab_totals(stats_by_user),
        "per_user": {u: s.to_dict() for u, s in stats_by_user.items()},
    }
    return (
        f"Lab stats this week (JSON):\n"
        f"```\n{json.dumps(payload, indent=2)}\n```\n"
        f"Deliver the stand-up monologue now."
    )


# Deterministic fallbacks for --skip-llm / no Ollama. They are intentionally
# boring so it's obvious the LLM didn't run.
def fallback_serious(stats: UserStats) -> str:
    if not stats.flags:
        return (
            f"{stats.user}: {stats.n_jobs} jobs, {stats.cpu_hours:.1f} CPU-hours, "
            f"{stats.kg_co2:.2f} kg CO2. No overprovisioning flagged. Nothing to change."
        )
    w = stats.worst_offender
    return (
        f"{stats.user}: {stats.n_jobs} jobs, avg CPU eff "
        f"{int(stats.avg_cpu_eff * 100)}%, {stats.kg_co2:.2f} kg CO2. "
        f"Worst job: {w.job_name} ({w.detail}). "
        f"Recommendation: tighten the next sbatch for {w.job_name}."
    )


def fallback_roast(stats: UserStats) -> str:
    if not stats.flags:
        return f"{stats.user} did absolutely nothing wrong. Disappointing, really. Keep it up."
    w = stats.worst_offender
    return (
        f"{stats.user}, mate. {w.detail}. {stats.kg_co2:.2f} kilograms of CO2, "
        f"for what was effectively a long lunch. Try `sbatch --help` sometime."
    )


def fallback_standup(stats_by_user: dict[str, UserStats]) -> str:
    t = lab_totals(stats_by_user)
    return (
        f"Right. This week the lab burned {t['total_cpu_hours']} CPU-hours and "
        f"{t['total_kwh']} kilowatt-hours, which works out to {t['total_kg_co2']} "
        f"kilograms of CO2. The biggest emitter was {t['biggest_emitter']}. "
        f"Be more like Roy. Tighter sbatch scripts. That's the memo."
    )
