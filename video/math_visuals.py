from fractions import Fraction
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
            VideoElement(type="rate", text="雨天净变化：1/12", x=0.5, y=0.74, start=13, end=18, animation="pop"),
            VideoElement(type="formula", text="雨水速度 = 1/12 + 1/8 − 1/6 = 1/24", x=0.5, y=0.50, scale=0.86, start=16, end=21, animation="fade"),
            VideoElement(type="formula", text="实际排水速度 = 1/8 − 1/24 = 1/12", x=0.5, y=0.62, scale=0.90, start=19, end=24, animation="fade"),
        ])
    elif "面积与周长" in knowledge:
        elements.extend([
            VideoElement(type="shape", text="长方形", x=0.5, y=0.42, scale=1.3, start=4, end=10, animation="draw"),
            VideoElement(type="formula", text=solution.steps[0], x=0.5, y=0.62, scale=0.9, start=8, end=16, animation="fade"),
        ])
    elif "分数" in knowledge:
        elements.append(
            VideoElement(type="fraction_bar", text="把单位“1”平均分成相同份数", x=0.5, y=0.45, start=4, end=14, animation="draw")
        )
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
