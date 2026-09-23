from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class NarrationVisualCue:
    scene_key: str
    start: float
    end: float
    narration: str
    action: str
    element_type: str
    text: str = ""
    segment_id: str = ""


def _split_sentences(text: str) -> list[str]:
    import re
    parts = [p.strip() for p in re.split(r"(?<=[。！？；])\\s*", text or "") if p.strip()]
    return parts or [text.strip()] if text.strip() else []


def build_narration_visual_cues(document) -> list[NarrationVisualCue]:
    """Map each spoken sentence to a concrete visual action and time slice."""
    cues: list[NarrationVisualCue] = []
    keys = ("hook", "explain", "mistake", "summary")

    for index, scene in enumerate(document.scenes):
        key = keys[index] if index < len(keys) else f"scene_{index + 1}"
        sentences = _split_sentences(scene.narration)
        elements = [e for e in scene.elements if e.start is not None and e.end is not None]

        if not sentences:
            continue

        # Use the visual elements as the action track; each spoken sentence gets
        # its own cue. If there are more sentences than elements, reuse the last
        # visual action instead of leaving narration visually unsupported.
        total_weight = sum(max(len(s), 1) for s in sentences)
        cursor = scene.start
        for sentence_index, sentence in enumerate(sentences):
            weight = max(len(sentence), 1) / total_weight
            allocated_end = scene.start + (scene.end - scene.start) * (cursor - scene.start + (scene.end - scene.start) * weight) / (scene.end - scene.start) if scene.end > scene.start else scene.end
            cue_start = cursor
            cue_end = scene.end if sentence_index == len(sentences) - 1 else min(scene.end, allocated_end)
            cursor = cue_end
            if elements:
                element = elements[min(sentence_index, len(elements) - 1)]
                action = element.animation or "hold"
                element_type = element.type
                text = element.text or element.value or ""
                start = max(scene.start, element.start)
                end = min(scene.end, element.end)
            else:
                action = "hold"
                element_type = "text"
                text = ""
                start, end = scene.start, scene.end

            if end <= start:
                start, end = scene.start, scene.end

            cues.append(
                NarrationVisualCue(
                    scene_key=key,
                    start=start,
                    end=end,
                    narration=sentence,
                    action=action,
                    element_type=element_type,
                    text=text,
                    segment_id=f"{key}_{sentence_index + 1}",
                )
            )

    return cues
