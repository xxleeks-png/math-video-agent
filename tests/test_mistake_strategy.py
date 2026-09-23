from math_engine.solver import solve
from agents.mistake_strategy import build_mistake_strategy
from video.storyboard import build_storyboard


def test_mistake_strategy_changes_by_problem_type():
    arithmetic = build_mistake_strategy(solve("36 ÷ 6"))
    fraction = build_mistake_strategy(solve("3/4 + 1/4"))
    assert arithmetic["mistake"] != fraction["mistake"]
    assert arithmetic["method"]
    assert fraction["why"]


def test_water_storyboard_keeps_visuals_inside_scenes():
    problem = "一个空水池，单独开进水管，6小时可以注满；单独开出水管，8小时可以放完一池水。现在雨天雨水匀速注入池中，同时打开进水管和出水管，12小时刚好注满水池。如果雨天只开出水管，多少小时可以把满池水放完？"
    document = build_storyboard(solve(problem))
    assert document.scenes
    for scene in document.scenes:
        for element in scene.elements:
            if element.start is not None:
                assert element.start >= scene.start
            if element.end is not None:
                assert element.end <= scene.end
