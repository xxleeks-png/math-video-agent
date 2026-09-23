from math_engine.models import MathSolution


def build_content_plan(solution: MathSolution) -> dict:
    if not solution.verified:
        raise ValueError("未验证的数学结果不能进入内容生产")

    return {
        "primary_audience": "parent",
        "secondary_audience": "child",
        "content_goal": ["explain", "identify_common_error", "teach_transferable_method"],
        "commercial_mode": {"enabled": True, "hard_sell": False, "product_type": "teaching_material"},
        "conversion_path": [
            "展示高频错误",
            "解释错误原因",
            "给出可迁移方法",
            "提示同类训练需求",
            "自然引导配套教辅",
        ],
        "selling_point": "围绕具体知识点提供系统化同类练习",
    }
