from pathlib import Path
from math_engine.solver import solve
from video.storyboard import build_storyboard
from video.render_plan import build_render_plan
from video.renderer import render_preview


def test_render_plan():
    document = build_storyboard(solve("36 ÷ 6"))
    plan = build_render_plan(document)
    assert plan["version"] == "0.6.0"
    assert plan["canvas"] == {"width": 1080, "height": 1920, "fps": 30}
    assert len(plan["scenes"]) == 4
    assert plan["scenes"][0]["start"] == 0


def test_render_preview(tmp_path: Path):
    document = build_storyboard(solve("27 + 15"))
    output = Path(render_preview(document, str(tmp_path)))
    assert output.exists()
    assert output.read_text(encoding="utf-8").find('"version": "0.5.0"') >= 0
