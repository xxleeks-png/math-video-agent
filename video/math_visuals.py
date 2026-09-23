from math_engine.models import MathSolution
from .dsl import VideoElement


def build_math_visuals(solution: MathSolution) -> list[VideoElement]:
    """Map verified solution semantics to reusable elementary-math visual components."""
    elements: list[VideoElement] = []
    knowledge = solution.knowledge_point

    if "流水问题" in knowledge:
        elements.extend([
            VideoElement(type="tank", text="满池水 = 1", x=0.5, y=0.42, start=4, end=9, animation="draw"),
            VideoElement(type="rate", text="进水：1/6", x=0.30, y=0.62, start=7, end=12, animation="slide"),
            VideoElement(type="rate", text="出水：1/8", x=0.70, y=0.62, start=10, end=15, animation="slide"),
            VideoElement(type="relation", text="进水 + 雨水 − 出水 = 净变化", x=0.5, y=0.78, scale=0.82, start=12, end=17, animation="fade"),
            VideoElement(type="rate", text="雨天净变化：1/12", x=0.5, y=0.70, start=14, end=18, animation="pop"),
            VideoElement(type="formula", text="雨水速度 = 1/12 + 1/8 − 1/6 = 1/24", x=0.5, y=0.50, scale=0.82, start=17, end=21, animation="fade"),
            VideoElement(type="formula", text="实际排水速度 = 1/8 − 1/24 = 1/12", x=0.5, y=0.62, scale=0.86, start=20, end=24, animation="fade"),
        ])
    elif "面积与周长" in knowledge:
        elements.extend([
            VideoElement(type="shape", text="长方形", x=0.5, y=0.42, scale=1.3, start=4, end=10, animation="draw"),
            VideoElement(type="relation", text="面积 = 长 × 宽", x=0.5, y=0.58, scale=0.95, start=8, end=13, animation="fade"),
            VideoElement(type="formula", text=solution.steps[0], x=0.5, y=0.70, scale=0.88, start=12, end=18, animation="fade"),
        ])
    elif "分数" in knowledge:
        elements.extend([
            VideoElement(type="fraction_bar", text="单位“1”平均分成相同份数", x=0.5, y=0.45, start=4, end=11, animation="draw"),
            VideoElement(type="relation", text="先统一单位，再计算", x=0.5, y=0.68, start=10, end=15, animation="fade"),
        ])
    else:
        for i, step in enumerate(solution.steps[:3]):
            elements.append(
                VideoElement(
                    type="formula",
                    text=step,
                    x=0.5,
                    y=0.44 + i * 0.14,
                    scale=0.95,
                    start=5 + i * 3,
                    end=11 + i * 3,
                    animation="fade",
                )
            )
    return elements
