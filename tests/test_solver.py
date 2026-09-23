from math_engine.solver import solve


def test_water_tank_problem():
    problem = "一个空水池，进水管单独6小时装满，出水管单独8小时排空；雨天两管同时开，6小时装满。如果雨天只开出水管，多少小时可以把满池水放完？"
    result = solve(problem)
    assert result.verified is True
    assert result.answer == "无法排空（需要无限长时间）"
    assert "雨水速度=1/8" in result.steps[3]
