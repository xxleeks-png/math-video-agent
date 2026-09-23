from pathlib import Path
from .models import AudioSegment, VoiceConfig


def synthesize(text: str, start: float, duration: float, config: VoiceConfig, output_dir: str = "output") -> AudioSegment:
    """Dependency-free TTS placeholder.

    It creates a manifest segment now; a real provider can implement the same
    interface later without changing storyboard or subtitle code.
    """
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return AudioSegment(text=text, start=start, end=start + duration, audio_path=None)
