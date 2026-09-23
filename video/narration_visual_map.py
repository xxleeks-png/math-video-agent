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


def build_narration_visual_cues(document) -> list[NarrationVisualCue]:
    """Build a one-to-one narration/action map from the already validated storyboard."""
    cues: list[NarrationVisualCue] = []
    for index, scene in enumerate(document.scenes):
        key = ("hook", "explain", "mistake", "summary")[index] if index < 4 else f"scene_{index+1}"
        elements = [e for e in scene.elements if e.start is not None and e.end is not None]
        if not elements:
            cues.append(
                NarrationVisualCue(
                    scene_key=key,
                    start=scene.start,
                    end=scene.end,
                    narration=scene.narration,
                    action="hold",
                    element_type="text",
                )
            )
            continue

        # Split narration across visual cues so every spoken unit has an explicit action.
        words = max(1, len(scene.narration.split()))
        cursor = scene.start
        for i, element in enumerate(elements):
            remaining = len(elements) - i
            available = scene.end - cursor
            slice_duration = available / remaining
            cue_end = min(scene.end, cursor + slice_duration)
            cues.append(
                NarrationVisualCue(
                    scene_key=key,
                    start=cursor,
                    end=cue_end,
                    narration=scene.narration if i == 0 else "",
                    action=element.animation or "hold",
                    element_type=element.type,
                    text=element.text or element.value or "",
                )
            )
            cursor = cue_end
    return cues
