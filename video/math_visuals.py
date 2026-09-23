from dataclasses import dataclass
from typing import Callable

from math_engine.models import MathSolution
from .dsl import VideoElement


@dataclass(frozen=True)
class VisualTemplate:
    key: str
    matcher: Callable[[MathSolution], bool]
    builder: Callable[[MathSolution], list[VideoElement]]


def _water(solution: MathSolution) -> list[VideoElement]:
    return [
        VideoElement(type="tank", text="满池水 = 1", x=0.5, y=0.42, start=4, end=9, animation="draw"),
        VideoElement(type="rate", text="进水：1/6", x=0.30, y=0.62, start=7, end=12, animation="slide"),
        VideoElement(type="rate", text="出水：1/8", x=0.70, y=0.62, start=10, end=15, animation="slide"),
        VideoElement(type="relation", text="进水 + 雨水 − 出水 = 净变化", x=0.5, y=0.78, scale=0.82, start=12, end=17, animation="fade"),
        VideoElement(type="mistake", text="常见错误：把 1/8 直接当成雨水速度", x=0.5, y=0.86, scale=0.78, start=24, end=28, animation="shake"),
        VideoElement(type="correction", text="为什么错？1/8 是出水速度，不是雨水速度", x=0.5, y=0.78, scale=0.78, start=27, end=32, animation="slide"),
        VideoElement(type="method", text="先分清：进水、出水、雨水、净变化", x=0.5, y=0.64, scale=0.86, start=31, end=36, animation="pop"),
        VideoElement(type="rate", text="雨天净变化：1/12", x=0.5, y=0.70, start=14, end=18, animation="pop"),
        VideoElement(type="formula", text="雨水速度 = 1/12 + 1/8 − 1/6 = 1/24", x=0.5, y=0.50, scale=0.82, start=17, end=21, animation="fade"),
        VideoElement(type="formula", text="实际排水速度 = 1/8 − 1/24 = 1/12", x=0.5, y=0.62, scale=0.86, start=20, end=24, animation="fade"),
    ]


def _rectangle(solution: MathSolution) -> list[VideoElement]:
    return [
        VideoElement(type="shape", text="长方形", x=0.5, y=0.42, scale=1.3, start=4, end=10, animation="draw"),
        VideoElement(type="dimension", text="长", x=0.78, y=0.42, start=6, end=10, animation="draw"),
        VideoElement(type="dimension", text="宽", x=0.5, y=0.59, start=7, end=11, animation="draw"),
        VideoElement(type="relation", text="面积 = 长 × 宽", x=0.5, y=0.58, scale=0.95, start=8, end=13, animation="fade"),
        VideoElement(type="formula", text=solution.steps[0], x=0.5, y=0.70, scale=0.88, start=12, end=18, animation="fade"),
    ]


def _fraction(solution: MathSolution) -> list[VideoElement]:
    return [
        VideoElement(type="fraction_bar", text="单位“1”平均分成相同份数", x=0.5, y=0.45, start=4, end=11, animation="draw"),
        VideoElement(type="relation", text="先统一单位，再计算", x=0.5, y=0.68, start=10, end=15, animation="fade"),
    ]


def _arithmetic(solution: MathSolution) -> list[VideoElement]:
    elements: list[VideoElement] = []
    for i, step in enumerate(solution.steps[:3]):
        start = 5 + i * 4
        end = start + 4
        elements.append(
            VideoElement(
                type="math_step",
                text=step,
                x=0.5,
                y=0.45 + i * 0.15,
                scale=1.0,
                start=start,
                end=end,
                animation="pop",
            )
        )
    return elements


VISUAL_TEMPLATES = [
    VisualTemplate("water_tank", lambda s: "流水问题" in s.knowledge_point, _water),
    VisualTemplate("rectangle", lambda s: "面积与周长" in s.knowledge_point, _rectangle),
    VisualTemplate("fraction", lambda s: "分数" in s.knowledge_point, _fraction),
    VisualTemplate("arithmetic", lambda s: "四则运算" in s.knowledge_point, _arithmetic),
]


def get_visual_template(solution: MathSolution) -> VisualTemplate:
    for template in VISUAL_TEMPLATES:
        if template.matcher(solution):
            return template
    raise ValueError(f"暂未找到视觉模板：{solution.knowledge_point}")


def build_math_visuals(solution: MathSolution) -> list[VideoElement]:
    return get_visual_template(solution).builder(solution)
