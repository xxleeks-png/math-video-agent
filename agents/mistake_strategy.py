from math_engine.models import MathSolution


def build_mistake_strategy(solution: MathSolution) -> dict:
    """Return a deterministic, parent-oriented misconception for the verified problem type."""
    if not solution.verified:
        raise ValueError("未验证的数学结果不能生成错题策略")

    key = solution.knowledge_point
    if "流水问题" in key or "工程问题" in key:
        return {
            "mistake": "把某一种单独变化量，直接当成题目给出的净变化量。",
            "why": "题目中的进水、出水、雨水和净变化代表不同的量，不能混为一谈。",
            "method": "先确定单位“1”，再分别标出每一种变化量，最后建立数量关系。",
        }
    if "面积与周长" in key:
        return {
            "mistake": "把面积公式和周长公式混用。",
            "why": "面积描述覆盖了多大的区域，周长描述边界有多长，单位和数量关系都不同。",
            "method": "先看题目问面积还是周长，再选择对应公式。",
        }
    if "分数运算" in key:
        return {
            "mistake": "分母不同就直接把分子分母分别相加减。",
            "why": "分母表示单位被分成多少份，份数不同就不能直接比较或合并。",
            "method": "先统一分母，也就是统一计量单位，再进行计算。",
        }
    if "四则运算" in key:
        return {
            "mistake": "只看数字顺序，不判断运算关系。",
            "why": "不同运算代表不同的数量关系，不能只按看到的数字机械计算。",
            "method": "先判断运算关系，再按运算规则逐步计算。",
        }
    return {
        "mistake": "看到数字就直接计算，没有先确认数量关系。",
        "why": "数学题真正容易出错的地方通常是条件之间的关系，而不只是计算。",
        "method": "先找单位“1”和数量关系，再列式计算。",
    }


def build_mistake_script(solution: MathSolution) -> dict:
    return build_mistake_strategy(solution)
