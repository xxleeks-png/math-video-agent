from copy import deepcopy

from tts.models import AudioSegment

from tts.models import AudioSegment
from video.dsl import VideoDocument
from video.narration_visual_map import NarrationVisualCue


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


def align_document_to_sentence_audio(document: VideoDocument, audio_segments: list[AudioSegment]) -> VideoDocument:
    """Build scene and visual-cue timing directly from sentence-level audio."""
    if not audio_segments or not document.visual_cues:
        return document

    updated = deepcopy(document)
    cue_by_id = {cue.get("segment_id"): cue for cue in updated.visual_cues}
    audio_by_id = {segment.segment_id: segment for segment in audio_segments if segment.segment_id}

    for cue in updated.visual_cues:
        audio = audio_by_id.get(cue.get("segment_id"))
        if audio:
            cue["start"] = audio.start
            cue["end"] = audio.end

    for scene in updated.scenes:
        scene_cues = [cue for cue in updated.visual_cues if cue.get("scene_key") == _scene_key(scene, updated)]
        if not scene_cues:
            continue
        scene.start = min(c["start"] for c in scene_cues)
        scene.end = max(c["end"] for c in scene_cues)
        for element in scene.elements:
            if element.start is None or element.end is None:
                continue
            if element.cue_id:
                cue = next((c for c in scene_cues if c.get("segment_id") == element.cue_id), None)
                if cue:
                    element.start, element.end = cue["start"], cue["end"]
                    continue
            old_start, old_end = element.start, element.end
            overlaps = [cue for cue in scene_cues if not (cue["end"] <= old_start or cue["start"] >= old_end)]
            if overlaps:
                element.start = min(c["start"] for c in overlaps)
                element.end = max(c["end"] for c in overlaps)

    updated.duration = max((s.end for s in updated.scenes), default=updated.duration)
    return updated


def _scene_key(scene, document):
    index = document.scenes.index(scene)
    keys = ("hook", "explain", "mistake", "summary")
    return keys[index] if index < len(keys) else f"scene_{index + 1}"
