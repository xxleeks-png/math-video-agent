from video.math_visuals import get_visual_template
from math_engine.solver import solve


def test_visual_template_registry_water():
    solution = solve("一个空水池，单独开进水管，6小时可以注满；单独开出水管，8小时可以放完一池水。现在雨天雨水匀速注入池中，同时打开进水管和出水管，12小时刚好注满水池。如果雨天只开出水管，多少小时可以把满池水放完？")
    assert solution.verified is True
    assert get_visual_template(solution).key == "water_tank"


def test_visual_template_registry_arithmetic():
    solution = solve("36 ÷ 6")
    assert get_visual_template(solution).key == "arithmetic"
