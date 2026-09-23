from math_engine.solver import solve
from agents.teacher import generate_teacher_script, generate_variants
from agents.content_strategy import build_content_plan


PROBLEM = "36 ÷ 6"


def test_teacher_requires_verified_solution():
    solution = solve(PROBLEM)
    assert solution.verified is True
    script = generate_teacher_script(solution)
    assert script["audience"]["primary"] == "parent"
    assert script["audience"]["secondary"] == "child"
    assert script["duration_seconds"] == 40
    assert "key_method" in script
    assert "parent_insight" in script


def test_teacher_variants():
    solution = solve(PROBLEM)
    variants = generate_variants(solution)
    assert len(variants) == 3


def test_content_strategy():
    solution = solve(PROBLEM)
    plan = build_content_plan(solution)
    assert plan["commercial_mode"]["enabled"] is True
    assert plan["commercial_mode"]["hard_sell"] is False
    assert plan["primary_audience"] == "parent"
