"""Text-to-speech for Roy-bot.

Two engines:

  say     — macOS built-in. Robotic on Compact voices, fine on Premium ones.
            Voices: try `say -v '?'`. Suggested: Daniel, Karen, Moira, or any
            "(Premium)" voice you've downloaded from System Settings.

  piper   — https://github.com/rhasspy/piper. Local, free, sounds genuinely
            natural. We invoke it via its CLI (subprocess) so we don't need
            to import onnxruntime in our code.

Install Piper:

    cd hackathon/submissions/team-f
    uv add piper-tts

Then download a voice model (one .onnx + matching .onnx.json):

    mkdir -p models
    BASE=https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB
    curl -L "$BASE/alan/medium/en_GB-alan-medium.onnx"      -o models/en_GB-alan-medium.onnx
    curl -L "$BASE/alan/medium/en_GB-alan-medium.onnx.json" -o models/en_GB-alan-medium.onnx.json

Browse all voices at https://github.com/rhasspy/piper/blob/master/VOICES.md.
Good Roy candidates:
  en_GB-alan-medium                  — dry British male
  en_GB-northern_english_male-medium — Yorkshire deadpan, perfect
  en_GB-southern_english_female-low  — receptionist energy
  en_GB-jenny_dioco-medium           — natural UK female
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_VOICE = "Daniel"


# --- Acronym normalisation ------------------------------------------------
# TTS engines mispronounce acronyms by trying to read them as words ("kuh-poo"
# for CPU, "ram" for RAM is fine but inconsistent). We spell them out so the
# voice reads each letter. Order matters: plurals before singulars.
_ACRONYM_SUBS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bCPUs\b"),  "C P U s"),
    (re.compile(r"\bCPU\b"),   "C P U"),
    (re.compile(r"\bGPUs\b"),  "G P U s"),
    (re.compile(r"\bGPU\b"),   "G P U"),
    (re.compile(r"\bRAM\b"),   "R A M"),
    (re.compile(r"\bHPC\b"),   "H P C"),
    (re.compile(r"\bAPI\b"),   "A P I"),
    # CO2 / CO₂ — say "C O two", explicit so digits don't get read as "number two".
    (re.compile(r"\bCO2\b"),   "C O two"),
    (re.compile(r"CO₂"),       "C O two"),
    # Units: read as full words. "k W h" sounds dumb spelled out.
    (re.compile(r"\bkWh\b"),   "kilowatt hours"),
    (re.compile(r"\bkW\b"),    "kilowatts"),
    (re.compile(r"\bkg\b"),    "kilograms"),
    (re.compile(r"\bGB\b"),    "gigabytes"),
    (re.compile(r"\bMB\b"),    "megabytes"),
    (re.compile(r"\bTB\b"),    "terabytes"),
    # Tool names the TTS gets wrong. `\b` boundaries don't apply because
    # these often appear inside underscored job names (e.g. `jupyter_zombie`).
    (re.compile(r"jupyter", re.IGNORECASE), "jupiter"),
    # `sbatch`, `seff`, etc. — read literally is fine; leave them.
]


def normalize_for_tts(text: str) -> str:
    """Pre-TTS pass: spell out acronyms, expand units."""
    for pat, repl in _ACRONYM_SUBS:
        text = pat.sub(repl, text)
    return text


# ---------------------------------------------------------------- macOS `say`

def say_available() -> bool:
    return sys.platform == "darwin" and shutil.which("say") is not None


def speak_with_say(text: str, out_path: str | Path, voice: str = DEFAULT_VOICE, rate: int | None = None) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["say", "-v", voice, "-o", str(out_path)]
    if rate is not None:
        cmd += ["-r", str(rate)]
    cmd += ["--", text]
    subprocess.run(cmd, check=True)
    return out_path


def list_say_voices() -> list[str]:
    if not say_available():
        return []
    out = subprocess.run(["say", "-v", "?"], capture_output=True, text=True, check=True).stdout
    return [line.split()[0] for line in out.splitlines() if line.strip()]


# ----------------------------------------------------------------- piper-tts

def piper_available() -> bool:
    return shutil.which("piper") is not None


def _resolve_piper_model(model: str | Path | None) -> Path:
    """Find the .onnx model file. Order: explicit arg, $PIPER_VOICE_MODEL, ./models/*.onnx."""
    if model:
        p = Path(model)
        if p.suffix != ".onnx":
            p = p.with_suffix(".onnx")
        if not p.exists():
            raise FileNotFoundError(f"piper model not found: {p}")
        return p
    env = os.environ.get("PIPER_VOICE_MODEL")
    if env:
        p = Path(env)
        if not p.exists():
            raise FileNotFoundError(f"PIPER_VOICE_MODEL points to a missing file: {p}")
        return p
    for candidate in Path("models").glob("*.onnx"):
        return candidate
    raise FileNotFoundError(
        "No piper voice model found. Pass --piper-model PATH, set "
        "PIPER_VOICE_MODEL, or drop a *.onnx into ./models/. See "
        "roybot/tts.py for download commands."
    )


def speak_with_piper(text: str, out_path: str | Path, model: str | Path | None = None) -> Path:
    if not piper_available():
        raise RuntimeError(
            "`piper` binary not on PATH. Install with: uv add piper-tts"
        )
    model_path = _resolve_piper_model(model)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["piper", "--model", str(model_path), "-f", str(out_path)]
    subprocess.run(cmd, input=text, text=True, check=True)
    return out_path


# ------------------------------------------------------------------ dispatch

def speak(
    text: str,
    out_path: str | Path,
    engine: str = "say",
    voice: str = DEFAULT_VOICE,
    rate: int | None = None,
    piper_model: str | Path | None = None,
) -> Path | None:
    """Render `text` to audio. Returns the output path, or None if the chosen engine isn't available.

    Output extension is inferred from the engine: `.aiff` for `say`, `.wav` for piper.
    """
    out_path = Path(out_path)
    spoken = normalize_for_tts(text)
    if engine == "say":
        if not say_available():
            return None
        if out_path.suffix.lower() not in (".aiff", ".aif"):
            out_path = out_path.with_suffix(".aiff")
        return speak_with_say(spoken, out_path, voice=voice, rate=rate)
    if engine == "piper":
        if out_path.suffix.lower() != ".wav":
            out_path = out_path.with_suffix(".wav")
        return speak_with_piper(spoken, out_path, model=piper_model)
    raise ValueError(f"unknown TTS engine: {engine!r} (try 'say' or 'piper')")


# --- legacy aliases so older callers keep working --------------------------
is_available = say_available
speak_to_file = speak_with_say
list_voices = list_say_voices
