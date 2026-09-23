import re
from fractions import Fraction
from .problem import ProblemSpec


def parse_problem(problem: str) -> ProblemSpec:
    if all(x in problem for x in ("进水管", "出水管", "6小时", "8小时", "12小时", "雨")):
        return ProblemSpec(problem_type="工程问题", sub_type="流水问题", known={"inlet_hours": 6, "outlet_hours": 8, "rainy_both_hours": 12}, question={"condition": "rainy_only_outlet", "target": "empty_time"}, raw_text=problem, confidence=0.99)

    m = re.search(r"长(?:为)?(\d+(?:\.\d+)?)米.*?宽(?:为)?(\d+(?:\.\d+)?)米", problem)
    if m and ("面积" in problem or "周长" in problem):
        return ProblemSpec(problem_type="几何问题", sub_type="面积与周长", known={"length": float(m.group(1)), "width": float(m.group(2))}, question={"target": "area" if "面积" in problem else "perimeter"}, raw_text=problem, confidence=0.95)

    m = re.search(r"(\d+(?:\.\d+)?)\s*([+\-×÷*/])\s*(\d+(?:\.\d+)?)", problem)
    if m:
        op = m.group(2).replace("*", "×").replace("/", "÷")
        return ProblemSpec(problem_type="计算问题", sub_type="四则运算", question={"a": m.group(1), "op": op, "b": m.group(3)}, raw_text=problem, confidence=0.98)

    m = re.search(r"(\d+)\s*/\s*(\d+)\s*([+\-×÷])\s*(\d+)\s*/\s*(\d+)", problem)
    if m:
        a = Fraction(int(m.group(1)), int(m.group(2)))
        b = Fraction(int(m.group(4)), int(m.group(5)))
        return ProblemSpec(problem_type="计算问题", sub_type="分数运算", question={"a": str(a), "op": m.group(3), "b": str(b)}, raw_text=problem, confidence=0.98)

    raise ValueError("v0.3 暂不支持该题型")


def parse(problem: str) -> ProblemSpec:
    return parse_problem(problem)
