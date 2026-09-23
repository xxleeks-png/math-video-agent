from fractions import Fraction
from .models import MathSolution
from .problem import ProblemSpec
from .registry import registry


def solve_arithmetic(spec: ProblemSpec) -> MathSolution:
    a, op, b = Fraction(spec.question["a"]), spec.question["op"], Fraction(spec.question["b"])
    result = {"+": a+b, "-": a-b, "×": a*b, "÷": a/b}[op]
    return MathSolution(problem=spec.raw_text, known_conditions=[f"已知：{a} {op} {b}"], goal="求计算结果", steps=[f"{a} {op} {b} = {result}"], answer=str(result), verified=False, knowledge_point="四则运算")


def solve_fraction(spec: ProblemSpec) -> MathSolution:
    return solve_arithmetic(spec)


def solve_rectangle(spec: ProblemSpec) -> MathSolution:
    length, width = Fraction(spec.known["length"]), Fraction(spec.known["width"])
    target = spec.question["target"]
    if target == "area":
        result = length * width
        step = f"面积=长×宽={length}×{width}={result}"
    else:
        result = (length + width) * 2
        step = f"周长=(长+宽)×2=({length}+{width})×2={result}"
    return MathSolution(problem=spec.raw_text, known_conditions=[f"长={length}", f"宽={width}"], goal="求长方形" + ("面积" if target == "area" else "周长"), steps=[step], answer=str(result), verified=False, knowledge_point="面积与周长")


registry.register("四则运算", solve_arithmetic)
registry.register("分数运算", solve_fraction)
registry.register("面积与周长", solve_rectangle)
