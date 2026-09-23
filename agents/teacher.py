from typing import List
from math_engine.models import MathSolution


def _base_script(solution: MathSolution, style: str) -> dict:
    if not solution.verified:
        raise ValueError("数学结果尚未通过验证，禁止生成讲解脚本")
    return {
        "audience": {"primary": "parent", "secondary": "child"},
        "style": style,
        "hook": "这道题先别急着算，先把每个量到底表示什么看清楚。",
        "explanation": [
            "先确定单位“1”，再把题目中的条件换算成每小时的变化量。",
            *solution.steps,
        ],
        "common_mistake": "不要把题目里的净变化量，直接当成某一种单独的变化量。",
        "key_method": solution.knowledge_point,
        "parent_insight": "如果孩子会算却经常列错式，重点通常是数量关系和单位“1”，而不只是计算熟练度。",
        "transfer": "再练2～3道同类型题，确认孩子能独立建立数量关系。",
        "cta": "需要系统巩固时，可以配合同类型教辅练习。",
        "duration_seconds": 40,
    }


def generate_teacher_script(solution: MathSolution, style: str = "清晰讲解") -> dict:
    return _base_script(solution, style)


def generate_variants(solution: MathSolution) -> List[dict]:
    styles = [
        ("清晰讲解", "直接拆解题目，重点突出数量关系。"),
        ("家长辅导", "告诉家长应该提醒孩子先找单位“1”和数量关系。"),
        ("错题讲解", "先指出最容易错的地方，再重新建立正确关系。"),
    ]
    variants = []
    for name, angle in styles:
        script = _base_script(solution, name)
        script["hook"] = angle + " " + script["hook"]
        variants.append(script)
    return variants
