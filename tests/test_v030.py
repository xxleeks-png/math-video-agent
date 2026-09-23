from math_engine.parser import parse
from math_engine.solver import solve


def test_water_tank():
    p = "一个空水池，单独开进水管，6小时可以注满；单独开出水管，8小时可以放完一池水。现在雨天雨水匀速注入池中，同时打开进水管和出水管，12小时刚好注满水池。如果雨天只开出水管，多少小时可以把满池水放完？"
    result = solve(p)
    assert result.answer == "12小时"
    assert result.verified is True


def test_arithmetic():
    assert solve("36 ÷ 6").answer == "6"
    assert solve("27 + 15").answer == "42"


def test_fraction():
    assert solve("1/2 + 1/3").answer == "5/6"


def test_rectangle():
    assert solve("一个长8米、宽5米的长方形，面积是多少？").answer == "40"
    assert solve("一个长8米、宽5米的长方形，周长是多少？").answer == "26"
