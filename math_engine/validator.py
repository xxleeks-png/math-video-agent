from fractions import Fraction

from .models import MathSolution
from .problem import ProblemSpec


def validate_water_tank(spec: ProblemSpec, solution: MathSolution) -> bool:
    inlet = Fraction(1, int(spec.known["inlet_hours"]))
    outlet = Fraction(1, int(spec.known["outlet_hours"]))
    both = Fraction(1, int(spec.known["rainy_both_hours"]))

    rain = both + outlet - inlet
    effective_outflow = outlet - rain
    if rain <= 0 or effective_outflow <= 0:
        return False

    expected_time = Fraction(1, 1) / effective_outflow
    return solution.answer == f"{expected_time}小时"


def validate_basic(spec: ProblemSpec, solution: MathSolution) -> bool:
    if spec.sub_type in ("四则运算", "分数运算"):
        a = Fraction(spec.question["a"])
        b = Fraction(spec.question["b"])
        result = {"+": a + b, "-": a - b, "×": a * b, "÷": a / b}[spec.question["op"]]
        return solution.answer == str(result)

    if spec.sub_type == "面积与周长":
        length = Fraction(str(spec.known["length"]))
        width = Fraction(str(spec.known["width"]))
        expected = (
            length * width
            if spec.question["target"] == "area"
            else (length + width) * 2
        )
        return solution.answer == str(expected)

    return False


def validate(spec: ProblemSpec, solution: MathSolution) -> bool:
    if spec.sub_type == "流水问题":
        return validate_water_tank(spec, solution)
    return validate_basic(spec, solution)
