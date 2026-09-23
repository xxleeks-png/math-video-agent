from math_engine.solver import solve
from video.math_visuals import build_math_visuals


def test_water_tank_visuals():
    solution = solve("一个空水池，单独开进水管，6小时可以注满；单独开出水管，8小时可以放完一池水。现在雨天雨水匀速注入池中，同时打开进水管和出水管，12小时刚好注满水池。如果雨天只开出水管，多少小时可以把满池水放完？")
    assert solution.verified is True
    elements = build_math_visuals(solution)
    assert any(e.type == "tank" for e in elements)
    assert any(e.type == "formula" for e in elements)


def test_semantic_visual_keys_drive_concrete_actions():
    solution = solve("一个空水池，单独开进水管，6小时可以注满；单独开出水管，8小时可以放完一池水。现在雨天雨水匀速注入池中，同时打开进水管和出水管，12小时刚好注满水池。如果雨天只开出水管，多少小时可以把满池水放完？")
    elements = build_math_visuals(solution)
    keys = {e.semantic_key for e in elements}
    assert {"inlet", "outlet", "rain_rate", "effective_outflow"} <= keys


def test_visual_elements_declare_reusable_actions():
    solution = solve("一个空水池，单独开进水管，6小时可以注满；单独开出水管，8小时可以放完一池水。现在雨天雨水匀速注入池中，同时打开进水管和出水管，12小时刚好注满水池。如果雨天只开出水管，多少小时可以把满池水放完？")
    elements = build_math_visuals(solution)
    actions = {e.visual_action for e in elements}
    assert {"add", "subtract", "equal", "transform"} <= actions
    subtraction = next(e for e in elements if e.semantic_key == "effective_outflow")
    assert subtraction.action_value == "1/24"
    assert subtraction.action_ratio == 1 / 24
