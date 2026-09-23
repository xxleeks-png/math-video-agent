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
        for sentence_index, sentence in enumerate(sentences):
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
                )
            )

    return cues
