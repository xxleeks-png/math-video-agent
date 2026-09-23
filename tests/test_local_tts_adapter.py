from pathlib import Path

from tts.local import _find_reference_audio
from tts.models import VoiceConfig


def test_reference_audio_directory(tmp_path, monkeypatch):
    audio = tmp_path / "teacher.wav"
    audio.write_bytes(b"RIFF")
    monkeypatch.setenv("F5_TTS_REF_AUDIO_DIR", str(tmp_path))

    assert _find_reference_audio(VoiceConfig()) == str(audio)
