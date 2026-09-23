from math_engine.solver import solve
from video.storyboard import build_storyboard


def test_storyboard_has_narration_visual_cues():
    document = build_storyboard(solve("36 ÷ 6"))
    assert document.visual_cues
    assert all(cue["start"] < cue["end"] for cue in document.visual_cues)
    assert any(cue["element_type"] == "math_step" for cue in document.visual_cues)


def test_visual_cues_stay_inside_document():
    document = build_storyboard(solve("3/4 + 1/4"))
    assert all(0 <= cue["start"] < cue["end"] <= document.duration for cue in document.visual_cues)
