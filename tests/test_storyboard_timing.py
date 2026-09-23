from math_engine.solver import solve
from video.storyboard import build_storyboard
from video.dsl import validate_video_document


def test_storyboard_visuals_stay_inside_explain_scene():
    solution = solve(
        "一个空水池，单独开进水管，6小时可以注满；单独开出水管，8小时可以放完一池水。"
        "现在雨天雨水匀速注入池中，同时打开进水管和出水管，12小时刚好注满水池。"
        "如果雨天只开出水管，多少小时可以把满池水放完？"
    )
    document = build_storyboard(solution)

    assert validate_video_document(document)
    explain = document.scenes[1]
    assert all(
        element.start is None
        or element.end is None
        or (explain.start <= element.start < element.end <= explain.end)
        for element in explain.elements
    )


def test_explanation_elements_use_automatic_action_phases():
    solution = solve(
        "一个空水池，单独开进水管，6小时可以注满；单独开出水管，8小时可以放完一池水。"
        "现在雨天雨水匀速注入池中，同时打开进水管和出水管，12小时刚好注满水池。"
        "如果雨天只开出水管，多少小时可以把满池水放完？"
    )
    document = build_storyboard(solution)
    explain = document.scenes[1]
    bound = [element for element in explain.elements if element.cue_id]
    assert bound
    assert all(element.action_phase == "auto" for element in bound)
