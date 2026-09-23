from math_engine.solver import solve
from video.math_visuals import build_math_visuals


def test_arithmetic_uses_staged_math_steps():
    solution = solve("36 ÷ 6")
    elements = build_math_visuals(solution)
    steps = [e for e in elements if e.type == "math_step"]
    assert steps
    assert all(e.animation == "pop" for e in steps)
    assert all(e.end > e.start for e in steps)
    assert steps[0].start < steps[-1].start
