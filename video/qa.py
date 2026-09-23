from video.dsl import VideoDocument
from tts.models import AudioSegment


def validate_audio_visual_alignment(document: VideoDocument, audio_segments: list[AudioSegment]) -> bool:
    """Final structural QA for sentence-level audio/visual synchronization."""
    if not audio_segments or not document.visual_cues:
        return False

    cues = {cue.get("segment_id"): cue for cue in document.visual_cues if cue.get("segment_id")}
    if len(cues) != len(document.visual_cues):
        return False

    for segment in audio_segments:
        cue = cues.get(segment.segment_id)
        if cue is None:
            return False
        if segment.end <= segment.start:
            return False
        if cue["start"] < 0 or cue["end"] <= cue["start"]:
            return False
        if abs(cue["start"] - segment.start) > 1e-6 or abs(cue["end"] - segment.end) > 1e-6:
            return False

    for scene in document.scenes:
        if scene.start < 0 or scene.end <= scene.start or scene.end > document.duration:
            return False
        for element in scene.elements:
            if element.start is not None and element.end is not None:
                if element.end <= element.start:
                    return False
                if element.start < scene.start - 1e-6 or element.end > scene.end + 1e-6:
                    return False
                if element.cue_id and element.cue_id not in cues:
                    return False

    return True
