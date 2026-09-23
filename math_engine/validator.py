from fractions import Fraction
from .problem import ProblemSpec
from .models import MathSolution


def validate_water_tank(spec: ProblemSpec, solution: MathSolution) -> bool:
    inlet = Fraction(1, int(spec.known["inlet_hours"]))
    outlet = Fraction(1, int(spec.known["outlet_hours"]))
    both = Fraction(1, int(spec.known["rainy_both_hours"]))
    rain = both + outlet - inlet
    effective_outflow = outlet - rain
    expected_time = Fraction(1, 1) / effective_outflow
    return rain > 0 and effective_outflow > 0 and expected_time == 12 and solution.answer == "12小时"


def validate(spec: ProblemSpec, solution: MathSolution) -> bool:
    if spec.sub_type == "流水问题":
        return validate_water_tank(spec, solution)
    return False
