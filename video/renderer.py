from pathlib import Path
from .dsl import VideoDocument


def render_preview(document: VideoDocument, output_dir: str = "output") -> str:
    """Create a deterministic JSON preview of the Video DSL.

    v0.6 keeps rendering dependency-light. A later renderer can consume the
    same DSL and produce PNG frames/MP4 without changing upstream agents.
    """
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    output = path / "storyboard_preview.json"
    output.write_text(document.model_dump_json(indent=2), encoding="utf-8")
    return str(output)
