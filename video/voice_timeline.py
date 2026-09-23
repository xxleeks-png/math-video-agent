from tts.models import AudioSegment, TTSBatchResult, VoiceConfig
from tts.local import synthesize_batch
from .narration_visual_map import _split_sentences
from video.dsl import VideoDocument


def build_voice_timeline(document: VideoDocument) -> list[AudioSegment]:
    """Create one local TTS segment per spoken sentence."""
    segments: list[AudioSegment] = []
    keys = ("hook", "explain", "mistake", "summary")
    for scene_index, scene in enumerate(document.scenes):
        key = keys[scene_index] if scene_index < len(keys) else f"scene_{scene_index + 1}"
        for sentence_index, sentence in enumerate(_split_sentences(scene.narration)):
            if not sentence.strip():
                continue
            segment_id = f"{key}_{sentence_index + 1}"
            segments.append(
                AudioSegment(
                    text=sentence,
                    start=0.0,
                    end=0.0,
                    segment_id=segment_id,
                )
            )
    return segments


def synthesize_voice_timeline(
    document: VideoDocument,
    config: VoiceConfig,
    output_dir: str = "output/audio",
) -> TTSBatchResult:
    """Synthesize the sentence timeline through the configured local TTS provider."""
    segments = build_voice_timeline(document)
    return synthesize_batch(segments, config, output_dir)
