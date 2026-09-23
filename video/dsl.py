from pydantic import BaseModel, Field
from typing import List, Optional

class VideoElement(BaseModel):
    type: str
    text: Optional[str] = None
    value: Optional[str] = None
    semantic_key: Optional[str] = None
    visual_action: Optional[str] = None
    action_target: Optional[str] = None
    action_value: Optional[str] = None
    action_ratio: Optional[float] = None
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
            if element.action_ratio is not None and not 0 <= element.action_ratio <= 1:
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
