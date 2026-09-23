from typing import List
from math_engine.models import MathSolution


def generate_teacher_script(solution: MathSolution, style: str = "清晰讲解") -> dict:
    """Generate a parent-oriented teaching structure from a verified math solution."""
    if not solution.verified:
        raise ValueError("数学结果尚未通过验证，禁止生成讲解脚本")

    opening = f"这道题的关键不是急着计算，而是先看懂每个量表示什么。"
    explanation = [
        "先确定单位“1”，再把题目中的条件换算成每小时的变化量。",
        *solution.steps,
    ]
    return {
        "audience": {"primary": "parent", "secondary": "child"},
        "style": style,
        "hook": opening,
        "explanation": explanation,
        "common_mistake": "不要把题目中的“净变化量”直接当成某一种单独变化量。",
        "key_method": solution.knowledge_point,
        "parent_insight": "如果孩子能算出数字却经常列错式，重点应放在数量关系和单位“1”的理解，而不是只增加计算量。",
        "transfer": "建议再练2～3道同类型题，确认孩子能独立建立数量关系。",
        "cta": "需要系统巩固时，可继续配合同类型教辅练习。",
        "duration_seconds": 40,
    }


def generate_variants(solution: MathSolution) -> List[dict]:
    return [
        generate_teacher_script(solution, "清晰讲解"),
        generate_teacher_script(solution, "家长辅导"),
        generate_teacher_script(solution, "短视频错题讲解"),
    ]
