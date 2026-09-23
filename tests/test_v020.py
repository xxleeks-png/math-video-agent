from math_engine.parser import parse
from math_engine.solver import solve
from math_engine.validator import validate


PROBLEM = (
    "一个空水池，单独开进水管，6小时可以注满；"
    "单独开出水管，8小时可以放完一池水。"
    "现在雨天雨水匀速注入池中，同时打开进水管和出水管，"
    "12小时刚好注满水池。如果雨天只开出水管，多少小时可以把满池水放完？"
)


def test_parse_problem():
    spec = parse(PROBLEM)
    assert spec.sub_type == "流水问题"
    assert spec.known["inlet_hours"] == 6
    assert spec.known["outlet_hours"] == 8
    assert spec.known["rainy_both_hours"] == 12


def test_solve_and_validate():
    spec = parse(PROBLEM)
    solution = solve(PROBLEM)
    assert solution.answer == "12小时"
    assert solution.verified is True
    assert validate(spec, solution) is True
