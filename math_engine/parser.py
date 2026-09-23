from .problem import ProblemSpec


def parse_problem(problem: str) -> ProblemSpec:
    if all(x in problem for x in ("进水管", "出水管", "6小时", "8小时", "12小时", "雨")):
        return ProblemSpec(
            grade="小学",
            problem_type="工程问题",
            sub_type="流水问题",
            known={"inlet_hours": 6, "outlet_hours": 8, "rainy_both_hours": 12},
            question={"condition": "rainy_only_outlet", "target": "empty_time"},
            raw_text=problem,
            confidence=0.99,
        )
    raise ValueError("v0.2 暂不支持该题型：当前支持6小时、8小时、12小时的水池流水题")


def parse(problem: str) -> ProblemSpec:
    return parse_problem(problem)
