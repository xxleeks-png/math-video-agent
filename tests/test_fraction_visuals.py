from fractions import Fraction

from math_engine.models import MathSolution
from video.math_visuals import build_math_visuals
from math_engine.solver import solve


def test_fraction_visual_has_bar():
    solution = solve("3/4 + 1/4")
    elements = build_math_visuals(solution)
    bar = next(e for e in elements if e.type == "fraction_bar")
    assert bar.start < bar.end
    assert bar.text


def test_fraction_visuals_are_deterministic():
    solution = solve("2/3 - 1/3")
    first = build_math_visuals(solution)
    second = build_math_visuals(solution)
    assert [e.model_dump() for e in first] == [e.model_dump() for e in second]
