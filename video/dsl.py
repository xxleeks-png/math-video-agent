from pydantic import BaseModel, Field
from typing import List, Optional

from .semantic_actions import validate_action_fields


class VideoElement(BaseModel):
    type: str
    text: Optional[str] = None
    value: Optional[str] = None
    semantic_key: Optional[str] = None
    visual_action: Optional[str] = None
    action_target: Optional[str] = None
    action_value: Optional[str] = None
    action_ratio: Optional[float] = None
    action_units: Optional[int] = None
    action_selected: Optional[int] = None
    action_removed: Optional[int] = None
    action_remaining: Optional[int] = None
    # Optional semantic operands/results used by compare/transform/split/merge.
    action_left: Optional[str] = None
    action_right: Optional[str] = None
    action_result: Optional[str] = None
    action_from: Optional[str] = None
    action_to: Optional[str] = None
    x: float = 0.5
    y: float = 0.5
    scale: float = 1.0
    emphasis: bool = False
    start: Optional[float] = None
    end: Optional[float] = None
    animation: Optional[str] = None
    cue_id: Optional[str] = None
    action_phase: Optional[str] = None


class VideoScene(BaseModel):
    start: float
    end: float
    elements: List[VideoElement] = Field(default_factory=list)
    narration: str = ""
    subtitle: str = ""


class VideoDocument(BaseModel):
    version: str = "0.8.0"
    width: int = 1080
    height: int = 1920
    fps: int = 30
    duration: float
    scenes: List[VideoScene]
    visual_cues: List[dict] = Field(default_factory=list)


def validate_video_document(document: VideoDocument) -> bool:
    if document.width <= 0 or document.height <= 0 or document.fps <= 0:
        return False
    if document.duration <= 0 or not document.scenes:
        return False
    previous_end = 0.0
    for scene in document.scenes:
        if scene.start < 0 or scene.end <= scene.start or scene.start < previous_end:
            return False
        if scene.end > document.duration:
            return False
        for element in scene.elements:
            if element.start is not None and element.start < scene.start:
                return False
            if element.end is not None and element.end > scene.end:
                return False
            if element.end is not None and element.start is not None and element.end <= element.start:
                return False
            if not validate_action_fields(
                element.visual_action,
                element.action_ratio,
                element.action_units,
                element.action_selected,
                element.action_removed,
                element.action_remaining,
                element.action_left,
                element.action_right,
                element.action_result,
                element.action_from,
                element.action_to,
            ):
                return False
        previous_end = scene.end
    for cue in document.visual_cues:
        try:
            if cue["start"] < 0 or cue["end"] <= cue["start"] or cue["end"] > document.duration:
                return False
            if not str(cue.get("narration", "")).strip() or not str(cue.get("action", "")).strip():
                return False
        except (KeyError, TypeError):
            return False
    return True
