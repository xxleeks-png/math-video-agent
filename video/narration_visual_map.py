from dataclasses import dataclass
import re


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
    sentence_index: int = 0
    action_phase: str = "hold"
    emphasis_token: str = ""


def _split_sentences(text: str) -> list[str]:
    parts = [p.strip() for p in re.split(r"(?<=[。！？；])\s*", text or "") if p.strip()]
    return parts or ([text.strip()] if text.strip() else [])


def build_narration_visual_cues(document) -> list[NarrationVisualCue]:
    """Map each spoken sentence to one concrete visual action."""
    cues: list[NarrationVisualCue] = []
    keys = ("hook", "explain", "mistake", "summary")

    for index, scene in enumerate(document.scenes):
        key = keys[index] if index < len(keys) else f"scene_{index + 1}"
        sentences = _split_sentences(scene.narration)
        elements = [e for e in scene.elements if e.start is not None and e.end is not None]
        if not sentences:
            continue

        total_weight = sum(max(len(s), 1) for s in sentences)
        scene_duration = max(scene.end - scene.start, 0.0)
        cursor = scene.start
        cumulative_weight = 0.0

        for sentence_index, sentence in enumerate(sentences):
            cumulative_weight += max(len(sentence), 1) / total_weight
            cue_start = cursor
            cue_end = scene.end if sentence_index == len(sentences) - 1 else scene.start + scene_duration * cumulative_weight
            cue_end = max(cue_start + 0.05, min(scene.end, cue_end))
            cursor = cue_end

            element = elements[min(sentence_index, len(elements) - 1)] if elements else None
            action = element.animation if element and element.animation else "hold"
            element_type = element.type if element else "text"
            text = (element.text or element.value or "") if element else ""

            cues.append(NarrationVisualCue(
                scene_key=key,
                start=cue_start,
                end=cue_end,
                narration=sentence,
                action=action,
                element_type=element_type,
                text=text,
                segment_id=f"{key}_{sentence_index + 1}",
                sentence_index=sentence_index,
            ))

    return cues


def build_sentence_action_cues(document) -> list[NarrationVisualCue]:
    """Expand each sentence into enter/focus/resolve phases."""
    expanded: list[NarrationVisualCue] = []
    for cue in build_narration_visual_cues(document):
        duration = max(cue.end - cue.start, 0.1)
        phases = (
            ("enter", cue.start, cue.start + duration * 0.25),
            ("focus", cue.start + duration * 0.25, cue.start + duration * 0.75),
            ("resolve", cue.start + duration * 0.75, cue.end),
        )
        for phase, start, end in phases:
            if end <= start:
                continue
            expanded.append(NarrationVisualCue(
                scene_key=cue.scene_key,
                start=start,
                end=end,
                narration=cue.narration,
                action=cue.action,
                element_type=cue.element_type,
                text=cue.text,
                segment_id=cue.segment_id,
                sentence_index=cue.sentence_index,
                action_phase=phase,
                emphasis_token=cue.text if phase == "focus" else "",
            ))
    return expanded
