from fractions import Fraction
from .models import MathSolution
from .problem import ProblemSpec
from .registry import registry
from .solvers_basic import solve_arithmetic, solve_fraction, solve_rectangle
from . import validator


def solve_water_tank_spec(spec: ProblemSpec) -> MathSolution:
    inlet = Fraction(1, int(spec.known["inlet_hours"]))
    outlet = Fraction(1, int(spec.known["outlet_hours"]))
    both = Fraction(1, int(spec.known["rainy_both_hours"]))
    rain = both + outlet - inlet
    effective = outlet - rain
    answer_time = Fraction(1, 1) / effective
    return MathSolution(problem=spec.raw_text, known_conditions=["进水速度=1/6", "出水速度=1/8", "雨天净速度=1/12"], goal="求雨天只开出水管时的排水时间", steps=["把满池水量看作1", f"雨水速度=1/12+1/8-1/6={rain}", f"实际排水速度=1/8-{rain}={effective}", f"排完一池水需要=1÷{effective}={answer_time}小时"], answer=f"{answer_time}小时", verified=False, knowledge_point="工程问题 / 流水问题")


registry.register("流水问题", solve_water_tank_spec)


def solve(problem: str) -> MathSolution:
    from .parser import parse
    spec = parse(problem)
    solution = registry.get(spec.sub_type)(spec)
    solution.verified = validator.validate(spec, solution)
    return solution
