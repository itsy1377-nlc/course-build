"""Narration. One cue in, one wav out, and the duration it actually took.

The duration is the point. Because the pipeline authors the script, it never
has to recognise speech to find out where a line starts and stops: it measures
the audio it just made. That one number sets how long a slide holds, where a
caption cue begins and ends, and how long the finished video runs. Three things
that would otherwise drift apart all read the same measurement.

That is also what makes the voice swappable. An engine change re-measures and
everything downstream follows. Nothing else in the pipeline knows or cares
which engine spoke.

Default is Kokoro: Apache-2.0 weights, 82M parameters, runs offline on the GPU
of this machine at roughly five times realtime. `say` is a fallback that needs
no install. ElevenLabs is here so that subscribing later is a config line
rather than a rewrite.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import wave
from pathlib import Path
from typing import Protocol

SAMPLE_RATE = 24_000
KOKORO_REPO = "hexgrad/Kokoro-82M"

# espeak-ng keeps its data directory in a fixed char buffer, N_PATH_HOME in
# speech.h, which is 160 bytes. Kokoro reaches espeak-ng through misaki, which
# hands it the copy bundled inside the venv at
# <project>/tools/video/.venv/lib/python3.12/site-packages/espeakng_loader/espeak-ng-data
# That is 100 characters before the project path is even counted, so a project
# living more than about 60 characters deep overflows the buffer. espeak-ng
# does not report this. It silently reverts to the path baked in when the wheel
# was built, fails to find phontab there, prints one line to stderr and calls
# exit(1) from C, which takes the whole build down with no Python traceback and
# no clue. Measured here: the bundled path was 170 characters.
#
# So pick a data directory that fits, preferring the bundled one because it is
# offline and version matched to the bundled library.
ESPEAK_PATH_LIMIT = 160

# Fallbacks, each paired with the library of the same install so the data and
# the code that reads it are the same version.
SYSTEM_ESPEAK = [
    (Path("/opt/homebrew/share/espeak-ng-data"), Path("/opt/homebrew/lib/libespeak-ng.dylib")),
    (Path("/usr/local/share/espeak-ng-data"), Path("/usr/local/lib/libespeak-ng.dylib")),
    (Path("/usr/lib/x86_64-linux-gnu/espeak-ng-data"),
     Path("/usr/lib/x86_64-linux-gnu/libespeak-ng.so.1")),
    (Path("/usr/lib/aarch64-linux-gnu/espeak-ng-data"),
     Path("/usr/lib/aarch64-linux-gnu/libespeak-ng.so.1")),
    (Path("/usr/share/espeak-ng-data"), Path("/usr/lib/libespeak-ng.so.1")),
]


class VoiceError(Exception):
    pass


def _configure_espeak() -> None:
    """Point phonemizer at an espeak-ng data directory short enough to survive.

    Imports misaki.espeak first on purpose: that module sets the data path at
    import time, so anything set before it would be overwritten.
    """
    import espeakng_loader
    import misaki.espeak  # noqa: F401  imported for its module level side effect
    from phonemizer.backend.espeak.wrapper import EspeakWrapper

    bundled_data = Path(espeakng_loader.get_data_path())
    bundled_lib = Path(espeakng_loader.get_library_path())

    tried = []
    for data, library in [(bundled_data, bundled_lib), *SYSTEM_ESPEAK]:
        if not (data / "phontab").is_file():
            continue
        if len(str(data).encode()) >= ESPEAK_PATH_LIMIT:
            tried.append(f"{data} ({len(str(data))} chars, over the {ESPEAK_PATH_LIMIT} limit)")
            continue
        if not library.exists():
            continue
        EspeakWrapper.set_library(str(library))
        EspeakWrapper.set_data_path(str(data))
        return

    raise VoiceError(
        "No usable espeak-ng data directory. Kokoro cannot turn text into "
        "phonemes without one.\n"
        f"  Rejected: {'; '.join(tried) or 'none found'}\n"
        f"  espeak-ng holds this path in a {ESPEAK_PATH_LIMIT} byte buffer and exits "
        "rather than reporting an overflow.\n"
        "  Either move the project somewhere shorter, or install espeak-ng "
        "system wide (brew install espeak-ng, apt install espeak-ng-data).")


class Voice(Protocol):
    name: str
    def speak(self, text: str, out: Path) -> float:
        """Write a wav and return its duration in seconds."""


def wav_duration(path: Path) -> float:
    with wave.open(str(path)) as w:
        return w.getnframes() / w.getframerate()


class KokoroVoice:
    """The default. Local, open weights, offline, no account, no per-word cost."""

    def __init__(self, voice: str = "af_heart", speed: float = 1.0):
        self.name = f"kokoro:{voice}"
        self.voice = voice
        self.speed = speed
        self._pipeline = None

    def _pipe(self):
        if self._pipeline is None:
            # Kokoro falls back to CPU for a couple of ops that MPS lacks. The
            # flag keeps that from raising instead of falling back.
            os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
            # Before kokoro, because this fixes a failure that is an exit(1)
            # from inside a C library rather than an exception.
            _configure_espeak()
            from kokoro import KPipeline
            # repo_id explicitly. Left to itself the pipeline warns
            # "Defaulting repo_id to hexgrad/Kokoro-82M" and resolves whatever
            # is current, which would re-time every caption in the course on a
            # day nobody touched the repository.
            self._pipeline = KPipeline(lang_code="a", repo_id=KOKORO_REPO)
        return self._pipeline

    def speak(self, text: str, out: Path) -> float:
        import numpy as np
        import soundfile as sf
        # No split_pattern: a cue is already the unit we want, and letting the
        # pipeline split it again would produce more audio segments than cues
        # and quietly break the caption mapping.
        parts = [np.asarray(a) for _, _, a in self._pipe()(text, voice=self.voice, speed=self.speed)]
        if not parts:
            raise VoiceError(f"Kokoro produced no audio for: {text[:60]!r}")
        out.parent.mkdir(parents=True, exist_ok=True)
        sf.write(out, np.concatenate(parts), SAMPLE_RATE)
        return wav_duration(out)


class SayVoice:
    """macOS `say`. No install, but proprietary and macOS only, so it is a
    fallback for a machine without the model rather than the shipping default."""

    def __init__(self, voice: str = "Ava (Premium)", wpm: int = 165):
        self.name = f"say:{voice}"
        self.voice = voice
        self.wpm = wpm

    def speak(self, text: str, out: Path) -> float:
        out.parent.mkdir(parents=True, exist_ok=True)
        aiff = out.with_suffix(".aiff")
        subprocess.run(["say", "-v", self.voice, "-r", str(self.wpm), "-o", str(aiff), text],
                       check=True, capture_output=True)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(aiff),
                        "-ar", str(SAMPLE_RATE), "-ac", "1", str(out)], check=True)
        aiff.unlink(missing_ok=True)
        return wav_duration(out)


class ElevenLabsVoice:
    """Present so that subscribing is a config change. Reads the key from the
    environment and never from the repo. Not the default: it is neither local
    nor open source, and the course is both."""

    def __init__(self, voice_id: str, model: str = "eleven_multilingual_v2"):
        self.name = f"elevenlabs:{voice_id}"
        self.voice_id = voice_id
        self.model = model

    def speak(self, text: str, out: Path) -> float:
        import requests
        key = os.environ.get("ELEVENLABS_API_KEY")
        if not key:
            raise VoiceError("ELEVENLABS_API_KEY is not set. Export it, or use the kokoro voice.")
        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}",
            headers={"xi-api-key": key, "accept": "audio/mpeg"},
            json={"text": text, "model_id": self.model,
                  "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}},
            timeout=60)
        response.raise_for_status()
        out.parent.mkdir(parents=True, exist_ok=True)
        mp3 = out.with_suffix(".mp3")
        mp3.write_bytes(response.content)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(mp3),
                        "-ar", str(SAMPLE_RATE), "-ac", "1", str(out)], check=True)
        mp3.unlink(missing_ok=True)
        return wav_duration(out)


def build_voice(spec: str) -> Voice:
    """'kokoro:af_heart' | 'say:Ava (Premium)' | 'elevenlabs:<voice_id>'"""
    engine, _, argument = spec.partition(":")
    if engine == "kokoro":
        return KokoroVoice(argument or "af_heart")
    if engine == "say":
        return SayVoice(argument or "Ava (Premium)")
    if engine == "elevenlabs":
        if not argument:
            raise VoiceError("elevenlabs needs a voice id, as in elevenlabs:21m00Tcm4TlvDq8ikWAM")
        return ElevenLabsVoice(argument)
    raise VoiceError(f"Unknown voice engine {engine!r}. Use kokoro, say, or elevenlabs.")


class NarrationCache:
    """Speak each distinct line once, ever, per (engine, voice, text).

    Synthesis is the slow half of a rebuild, so this is what makes fixing one
    sentence re-speak one sentence.

    There is deliberately no index file. An earlier version kept durations in
    index.json and it had three races the moment two videos built at once: a
    non-atomic write could be read half-finished, two processes each held their
    own copy of the index so the last writer erased the other's entries, and a
    reader could pick up a wav that was still being written.

    The wav already knows how long it is, so the files are the cache. A cue is
    synthesized to a private temporary name and moved into place with
    os.replace, which is atomic: a concurrent reader sees either the complete
    old file or the complete new one, never a partial. A file that cannot be
    read is treated as debris from an interrupted run and rebuilt.
    """

    def __init__(self, root: Path, voice: Voice):
        self.root = root
        self.voice = voice
        self.root.mkdir(parents=True, exist_ok=True)

    def _key(self, text: str) -> str:
        return hashlib.sha256(f"{self.voice.name}\x00{text}".encode()).hexdigest()[:20]

    def speak(self, text: str) -> tuple[Path, float, bool]:
        key = self._key(text)
        path = self.root / f"{key}.wav"
        if path.exists():
            try:
                return path, wav_duration(path), True
            except Exception:
                path.unlink(missing_ok=True)
        # The .wav suffix stays on the temporary name: soundfile picks its
        # output format from the extension and refuses a bare ".part".
        staging = self.root / f"{key}.{os.getpid()}.part.wav"
        try:
            duration = self.voice.speak(text, staging)
            os.replace(staging, path)
        finally:
            staging.unlink(missing_ok=True)
        return path, duration, False
