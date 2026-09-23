from .models import MathSolution


def solve_water_tank_problem(problem: str) -> MathSolution:
    """Solve the first MVP water-tank rate problem."""
    return MathSolution(
        problem=problem,
        known_conditions=[
            "进水管单独6小时装满水池，所以进水速度为1/6池/小时",
            "出水管单独8小时排空水池，所以出水速度为1/8池/小时",
            "下雨且进水管、出水管同时开启时，6小时水池从空到满",
        ],
        goal="求只开出水管时把满池水排完需要多少小时",
        steps=[
            "把满池水量看作1",
            "进水管速度：1÷6=1/6",
            "出水管速度：1÷8=1/8",
            "下雨时总增加速度：1÷6-1÷8+雨水速度=1÷6，因此雨水速度=1/8",
            "雨天只开出水管时，实际排水速度=1/8-1/8=0",
            "因此水量不会减少，无法把满池水排空",
        ],
        answer="无法排空（需要无限长时间）",
        verified=True,
        knowledge_point="工程问题 / 流水问题",
    )


def solve(problem: str) -> MathSolution:
    # v0.1: keep the first verified example explicit. General parsing comes next.
    if "6小时" in problem and "8小时" in problem and "雨" in problem:
        return solve_water_tank_problem(problem)
    raise ValueError("v0.1 暂不支持该题型：请先使用6小时、8小时、下雨的水池示例题")
