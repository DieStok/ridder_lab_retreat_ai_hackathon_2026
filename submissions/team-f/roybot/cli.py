"""CLI entry point for roybot.

Examples:
    uv run python -m roybot --mock                       # no Ollama, deterministic fallback text
    uv run python -m roybot --mock --with-llm            # real reports via local Ollama
    uv run python -m roybot --sacct dump.txt --with-llm
    uv run python -m roybot --mock --with-llm --with-audio --voice Daniel
    uv run python -m roybot --mock --with-llm --with-audio --slack
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .analyze import aggregate, lab_totals
from .data import load_sacct_file
from .llm import LLM
from .mock_data import load_mock
from .reports import generate
from . import tts


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="roybot", description="HPC babysitter, with extra snark.")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--mock", action="store_true", help="Use built-in fake sacct data.")
    src.add_argument("--sacct", type=Path, help="Path to `sacct --parsable2` dump.")
    p.add_argument("--out", type=Path, default=Path("out"), help="Output directory (default: ./out)")
    p.add_argument("--with-llm", action="store_true", help="Call Ollama (falls back to deterministic text on failure).")
    p.add_argument("--model", default=None, help="Override Ollama model (defaults to qwen2.5:14b or $OLLAMA_MODEL).")
    p.add_argument("--with-audio", action="store_true", help="Generate audio for the stand-up monologue.")
    p.add_argument("--engine", choices=["say", "piper"], default="say",
                   help="TTS engine. 'say' is built-in on macOS; 'piper' is local + much more natural (see README).")
    p.add_argument("--voice", default=tts.DEFAULT_VOICE,
                   help=f"Voice name for the `say` engine (default: {tts.DEFAULT_VOICE}). Ignored for piper.")
    p.add_argument("--rate", type=int, default=None, help="Words per minute (say engine only).")
    p.add_argument("--piper-model", default=None,
                   help="Path to a Piper .onnx voice model. Falls back to $PIPER_VOICE_MODEL or ./models/*.onnx.")
    p.add_argument("--skip-per-user-audio", action="store_true",
                   help="With --with-audio, generate only the lab stand-up; skip per-user roast clips.")
    p.add_argument("--slack", action="store_true", help="Post the stand-up to Slack (needs SLACK_BOT_TOKEN + SLACK_CHANNEL_ID).")
    p.add_argument("--no-fallback", action="store_true", help="Fail loudly if the LLM is unreachable.")
    return p


def main(argv: list[str] | None = None) -> int:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # python-dotenv only required if user has a .env
    args = _parser().parse_args(argv)

    # 1. Load jobs.
    if args.mock:
        jobs = load_mock()
        print(f"[roybot] loaded {len(jobs)} mock jobs", file=sys.stderr)
    else:
        jobs = load_sacct_file(args.sacct)
        print(f"[roybot] loaded {len(jobs)} jobs from {args.sacct}", file=sys.stderr)
    if not jobs:
        print("[roybot] no jobs to report on — exiting", file=sys.stderr)
        return 1

    # 2. Stats.
    stats = aggregate(jobs)
    totals = lab_totals(stats)
    print(
        f"[roybot] {len(stats)} users, "
        f"{totals['total_cpu_hours']} CPU-h, "
        f"{totals['total_kg_co2']} kg CO2, "
        f"biggest emitter: {totals['biggest_emitter']}",
        file=sys.stderr,
    )

    # 3. LLM (or fallback).
    llm = LLM(model=args.model, fallback=not args.no_fallback)
    if not args.with_llm:
        # Force fallback mode by swapping the client to None — uses the deterministic text.
        llm._unavailable_reason = "--with-llm not passed; using deterministic fallback"
        llm._get_client = lambda: None  # type: ignore[assignment]
    print(f"[roybot] generating reports via {llm.model if args.with_llm else 'fallback (no LLM)'} ...", file=sys.stderr)
    reports = generate(stats, llm)

    # 4. Write files.
    paths = reports.write(args.out)
    print(f"[roybot] wrote {len(paths)} files under {args.out}/", file=sys.stderr)

    # 5. Audio.
    audio_path = None
    if args.with_audio:
        # Show what the TTS actually heard (post acronym-spelling pass).
        spoken_path = args.out / "standup_spoken.txt"
        spoken_path.write_text(tts.normalize_for_tts(reports.standup))
        try:
            audio_path = tts.speak(
                reports.standup,
                args.out / "standup",
                engine=args.engine,
                voice=args.voice,
                rate=args.rate,
                piper_model=args.piper_model,
            )
        except (FileNotFoundError, RuntimeError) as e:
            print(f"[roybot] TTS ({args.engine}) failed: {e}", file=sys.stderr)
            audio_path = None
        if audio_path is None:
            print(f"[roybot] {args.engine} engine not available — skipping audio", file=sys.stderr)
        else:
            print(f"[roybot] wrote audio: {audio_path}", file=sys.stderr)

        # 5b. Per-user roast + spoken recommendations (one clip per lab member).
        if audio_path is not None and not args.skip_per_user_audio:
            for user, roast in reports.per_user_roast.items():
                # Drop any "[LLM fallback — ...]" debug header so the voice doesn't read it.
                spoken = roast
                if spoken.startswith("[LLM fallback —"):
                    spoken = spoken.split("\n", 1)[-1]
                # Append the deterministic recommendations so the clip is also actionable.
                recs_spoken = tts.recommendations_to_spoken(stats[user].recommendations)
                if recs_spoken:
                    spoken = spoken.rstrip() + "\n\n" + recs_spoken
                try:
                    user_audio = tts.speak(
                        spoken,
                        args.out / f"user_{user}",
                        engine=args.engine,
                        voice=args.voice,
                        rate=args.rate,
                        piper_model=args.piper_model,
                    )
                except (FileNotFoundError, RuntimeError) as e:
                    print(f"[roybot] per-user audio for {user} failed: {e}", file=sys.stderr)
                    continue
                if user_audio is not None:
                    print(f"[roybot] wrote audio: {user_audio}", file=sys.stderr)

    # 6. Slack.
    if args.slack:
        try:
            from .slack_post import post_standup
            r = post_standup(reports.standup, audio_path)
            print(f"[roybot] posted to Slack: ts={r.get('ts')}", file=sys.stderr)
        except Exception as e:
            print(f"[roybot] Slack post failed: {e}", file=sys.stderr)
            return 2

    # Final friendly summary on stdout (not stderr) for piping.
    print(str(args.out.resolve()))
    return 0
