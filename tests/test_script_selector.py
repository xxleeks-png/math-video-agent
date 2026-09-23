from agents.script_selector import score_script, select_script
from agents.teacher import generate_variants
from math_engine.solver import solve


def test_script_selection():
    solution = solve("36 ÷ 6")
    variants = generate_variants(solution)
    selected = select_script(variants, solution)
    assert selected["audience"]["primary"] == "parent"
    assert selected["audience"]["secondary"] == "child"
    assert selected["duration_seconds"] <= 60
    assert score_script(selected, solution) > 0
