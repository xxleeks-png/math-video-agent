from tts.models import AudioSegment
from video.dsl import VideoDocument


def build_voice_timeline(document: VideoDocument) -> list[AudioSegment]:
    segments = []
    for scene in document.scenes:
        if scene.narration.strip():
            segments.append(
                AudioSegment(
                    text=scene.narration,
                    start=scene.start,
                    end=scene.end,
                )
            )
    return segments
