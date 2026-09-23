from .models import MathSolution


def solve_water_tank_problem(problem: str) -> MathSolution:
    """Solve the verified MVP water-tank rate problem."""
    return MathSolution(
        problem=problem,
        known_conditions=[
            "进水管单独6小时装满水池，所以进水速度为1/6池/小时",
            "出水管单独8小时排空水池，所以出水速度为1/8池/小时",
            "雨天雨水匀速注入，同时打开进水管和出水管，12小时刚好注满水池",
        ],
        goal="求雨天只开出水管时把满池水排完需要多少小时",
        steps=[
            "把满池水量看作1",
            "进水管速度：1÷6=1/6池/小时",
            "出水管速度：1÷8=1/8池/小时",
            "雨天两管同时开，水池每小时净增加1÷12=1/12池",
            "雨水速度：1/12+1/8-1/6=1/24池/小时",
            "雨天只开出水管时，每小时实际减少1/8-1/24=1/12池",
            "排完一池水需要：1÷1/12=12小时",
        ],
        answer="12小时",
        verified=True,
        knowledge_point="工程问题 / 流水问题",
    )


def solve(problem: str) -> MathSolution:
    # v0.1.1: keep the first verified example explicit.
    if "6小时" in problem and "8小时" in problem and "12小时" in problem and "雨" in problem:
        return solve_water_tank_problem(problem)
    raise ValueError(
        "v0.1.1 暂不支持该题型：请先使用6小时、8小时、12小时、下雨的水池示例题"
    )
