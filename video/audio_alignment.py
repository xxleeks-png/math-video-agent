from copy import deepcopy

from tts.models import AudioSegment
from video.dsl import VideoDocument


def align_document_to_audio(document: VideoDocument, audio_segments: list[AudioSegment]) -> VideoDocument:
    """Retarget scene visual elements to actual TTS segment durations when possible."""
    if not audio_segments:
        return document

    updated = deepcopy(document)
    for scene_index, scene in enumerate(updated.scenes):
        if scene_index >= len(audio_segments):
            continue
        audio = audio_segments[scene_index]
        duration = max(audio.end - audio.start, 0.1)
        scene_start = audio.start
        scene_end = audio.end
        old_duration = max(scene.end - scene.start, 0.1)

        for element in scene.elements:
            if element.start is None or element.end is None:
                continue
            relative_start = max(0.0, (element.start - scene.start) / old_duration)
            relative_end = min(1.0, (element.end - scene.start) / old_duration)
            element.start = scene_start + relative_start * duration
            element.end = scene_start + relative_end * duration

        scene.start = scene_start
        scene.end = scene_end

    updated.duration = max(
        updated.duration,
        max((segment.end for segment in audio_segments), default=updated.duration),
    )
    return updated
