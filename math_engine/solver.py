from fractions import Fraction
from .models import MathSolution
from .problem import ProblemSpec


def solve_water_tank_spec(spec: ProblemSpec) -> MathSolution:
    inlet = Fraction(1, int(spec.known["inlet_hours"]))
    outlet = Fraction(1, int(spec.known["outlet_hours"]))
    both = Fraction(1, int(spec.known["rainy_both_hours"]))
    rain = both + outlet - inlet
    effective_outflow = outlet - rain
    answer_time = Fraction(1, 1) / effective_outflow

    return MathSolution(
        problem=spec.raw_text,
        known_conditions=[
            f"进水管单独{int(spec.known['inlet_hours'])}小时装满，所以进水速度为1/{int(spec.known['inlet_hours'])}池/小时",
            f"出水管单独{int(spec.known['outlet_hours'])}小时排空，所以出水速度为1/{int(spec.known['outlet_hours'])}池/小时",
            f"雨天两管同时开，{int(spec.known['rainy_both_hours'])}小时注满，所以净增加速度为1/{int(spec.known['rainy_both_hours'])}池/小时",
        ],
        goal="求雨天只开出水管时把满池水排完需要多少小时",
        steps=[
            "把满池水量看作1",
            f"进水管速度：1÷{int(spec.known['inlet_hours'])}=1/{int(spec.known['inlet_hours'])}",
            f"出水管速度：1÷{int(spec.known['outlet_hours'])}=1/{int(spec.known['outlet_hours'])}",
            f"雨天两管同时开，水池每小时净增加1÷{int(spec.known['rainy_both_hours'])}=1/{int(spec.known['rainy_both_hours'])}",
            f"雨水速度：1/{int(spec.known['rainy_both_hours'])}+1/{int(spec.known['outlet_hours'])}-1/{int(spec.known['inlet_hours'])}={rain}",
            f"雨天只开出水管时，实际排水速度：1/{int(spec.known['outlet_hours'])}-{rain}={effective_outflow}",
            f"排完一池水需要：1÷{effective_outflow}={answer_time}小时",
        ],
        answer=f"{answer_time}小时",
        verified=False,
        knowledge_point="工程问题 / 流水问题",
    )


def solve(problem: str) -> MathSolution:
    from .parser import parse
    from .validator import validate

    spec = parse(problem)
    solution = solve_water_tank_spec(spec)
    solution.verified = validate(spec, solution)
    return solution
