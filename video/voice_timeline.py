from tts.models import AudioSegment, TTSBatchResult, VoiceConfig
from .narration_visual_map import NarrationVisualCue
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


def align_visual_cues_to_audio(cues: list[NarrationVisualCue], audio_segments: list[AudioSegment]) -> list[NarrationVisualCue]:
    """Shift cue boundaries to the actual synthesized segment timings."""
    if not audio_segments:
        return cues
    aligned = []
    for cue in cues:
        match = next(
            (segment for segment in audio_segments
             if segment.text.strip() == cue.narration.strip()
             or (segment.start <= cue.start < segment.end)),
            None,
        )
        if match:
            start = max(match.start, cue.start)
            end = min(match.end, cue.end)
            if end <= start:
                start, end = match.start, match.end
            aligned.append(cue.__class__(
                scene_key=cue.scene_key,
                start=start,
                end=end,
                narration=cue.narration,
                action=cue.action,
                element_type=cue.element_type,
                text=cue.text,
            ))
        else:
            aligned.append(cue)
    return aligned
