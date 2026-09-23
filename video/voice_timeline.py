from tts.models import AudioSegment, TTSBatchResult, VoiceConfig
from video.dsl import VideoDocument


def build_voice_timeline(document: VideoDocument) -> list[AudioSegment]:
    segments = []
    for index, scene in enumerate(document.scenes, 1):
        if scene.narration.strip():
            segments.append(
                AudioSegment(
                    text=scene.narration,
                    start=scene.start,
                    end=scene.end,
                    segment_id=f"step{index}",
                )
            )
    return segments


def synthesize_voice_timeline(
    document: VideoDocument,
    config: VoiceConfig | None = None,
    output_dir: str = "output/audio",
) -> TTSBatchResult:
    from tts.local import synthesize_batch

    config = config or VoiceConfig()
    return synthesize_batch(
        build_voice_timeline(document),
        config,
        output_dir,
    )
