from typing import Callable

from .models import AudioSegment, VoiceConfig


TTSFunction = Callable[
    [str, float, float, VoiceConfig, str],
    AudioSegment,
]


def synthesize_local(
    text: str,
    start: float,
    duration: float,
    config: VoiceConfig,
    output_dir: str = "output/audio",
) -> AudioSegment:
    from .local import synthesize

    return synthesize(text, start, duration, config, output_dir)
