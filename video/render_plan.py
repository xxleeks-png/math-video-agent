from typing import Dict, List
from .dsl import VideoDocument


def build_render_plan(document: VideoDocument) -> Dict:
    scenes: List[Dict] = []
    for index, scene in enumerate(document.scenes):
        scenes.append({
            "index": index,
            "start": scene.start,
            "end": scene.end,
            "duration": scene.end - scene.start,
            "elements": [element.model_dump() for element in scene.elements],
            "narration": scene.narration,
            "subtitle": scene.subtitle,
        })
    return {
        "version": "0.6.0",
        "canvas": {"width": document.width, "height": document.height, "fps": document.fps},
        "duration": document.duration,
        "scenes": scenes,
    }
