from dataclasses import dataclass
import re
from typing import Callable

from math_engine.models import MathSolution
from .dsl import VideoElement
from .semantic_actions import infer_action_from_expression


@dataclass(frozen=True)
class VisualTemplate:
    key: str
    matcher: Callable[[MathSolution], bool]
    builder: Callable[[MathSolution], list[VideoElement]]


def _water(solution: MathSolution) -> list[VideoElement]:
    return [
        VideoElement(type="tank", semantic_key="unit", text="满池水 = 1", x=0.5, y=0.42, start=4, end=9, animation="draw", visual_action="equal", action_target="unit", action_value="1"),
        VideoElement(type="rate", semantic_key="inlet", text="进水：1/6", x=0.30, y=0.62, start=7, end=12, animation="slide", visual_action="add", action_target="tank", action_value="1/6", action_ratio=1/6),
        VideoElement(type="rate", semantic_key="outlet", text="出水：1/8", x=0.70, y=0.62, start=10, end=15, animation="slide", visual_action="subtract", action_target="tank", action_value="1/8", action_ratio=1/8),
        VideoElement(type="relation", semantic_key="net_relation", text="进水 + 雨水 − 出水 = 净变化", x=0.5, y=0.78, scale=0.82, start=12, end=17, animation="fade", visual_action="transform", action_target="net_change", action_from="进水+雨水-出水", action_to="净变化", action_result="1/12"),
        VideoElement(type="rate", semantic_key="net_rate", text="雨天净变化：1/12", x=0.5, y=0.70, start=14, end=18, animation="pop", emphasis=True, visual_action="equal", action_target="net_change", action_value="1/12", action_ratio=1/12),
        VideoElement(type="formula", semantic_key="rain_rate", text="雨水速度 = 1/12 + 1/8 − 1/6 = 1/24", x=0.5, y=0.50, scale=0.82, start=17, end=21, animation="fade", visual_action="add", action_target="rain", action_value="1/24", action_ratio=1/24),
        VideoElement(type="formula", semantic_key="effective_outflow", text="实际排水速度 = 1/8 − 1/24 = 1/12", x=0.5, y=0.62, scale=0.86, start=20, end=24, animation="fade", emphasis=True, visual_action="subtract", action_target="outflow", action_value="1/24", action_ratio=1/24, action_units=24, action_selected=3, action_removed=1, action_remaining=2),
    ]


def _rectangle(solution: MathSolution) -> list[VideoElement]:
    target = solution.goal
    return [
        VideoElement(type="shape", semantic_key="shape", text="长方形", x=0.5, y=0.42, scale=1.3, start=4, end=10, animation="draw", visual_action="transform", action_target="rectangle", action_from="长×宽", action_to="面积"),
        VideoElement(type="dimension", semantic_key="length", text="长", x=0.78, y=0.42, start=6, end=10, animation="draw", visual_action="highlight", action_target="length"),
        VideoElement(type="dimension", semantic_key="width", text="宽", x=0.5, y=0.59, start=7, end=11, animation="draw", visual_action="highlight", action_target="width"),
        VideoElement(type="relation", semantic_key="formula", text="面积 = 长 × 宽" if "面积" in target else "周长 = (长 + 宽) × 2", x=0.5, y=0.58, scale=0.95, start=8, end=13, animation="fade", visual_action="transform", action_target="formula", action_from="长×宽" if "面积" in target else "长+宽", action_to="面积" if "面积" in target else "周长"),
        VideoElement(type="formula", semantic_key="result", text=solution.steps[0], x=0.5, y=0.70, scale=0.88, start=12, end=18, animation="fade", visual_action="equal", action_target="result", action_value=solution.answer),
    ]


def _fraction_parts(expression: str) -> tuple[int, int, str, int, int] | None:
    matches = re.findall(r"(-?\d+)\s*/\s*(-?\d+)", expression or "")
    if len(matches) < 2:
        return None
    n1, d1 = map(int, matches[0])
    n2, d2 = map(int, matches[1])
    if d1 <= 0 or d2 <= 0 or d1 != d2:
        return None
    action = infer_action_from_expression(expression)
    if action not in {"add", "subtract"}:
        return None
    return n1, d1, action, n2, d2


def _fraction(solution: MathSolution) -> list[VideoElement]:
    step = solution.steps[0] if solution.steps else solution.answer
    parts = _fraction_parts(step)
    action_kwargs = {}
    if parts:
        n1, denominator, action, n2, _ = parts
        if action == "subtract":
            action_kwargs.update(
                action_units=denominator,
                action_selected=max(n1, 0),
                action_removed=max(n2, 0),
                action_remaining=max(n1 - n2, 0),
            )
        else:
            action_kwargs.update(
                action_units=denominator,
                action_ratio=min(1.0, max(0.0, n2 / denominator)),
            )
    operation_action = parts[2] if parts else "transform"
    return [
        VideoElement(type="fraction_bar", semantic_key="original", text="分数模型", x=0.5, y=0.45, start=4, end=9, animation="draw", visual_action="split", action_target="unit", action_units=parts[1] if parts else None),
        VideoElement(type="relation", semantic_key="operation", text=step, x=0.5, y=0.68, scale=0.9, start=9, end=15, animation="fade", visual_action=operation_action, action_target="fraction_operation", action_left=f"{n1}/{denominator}" if parts else None, action_right=f"{n2}/{denominator}" if parts else None, action_result=solution.answer, **action_kwargs),
        VideoElement(type="formula", semantic_key="result", text=f"结果：{solution.answer}", x=0.5, y=0.80, scale=0.9, start=14, end=18, animation="pop", visual_action="equal", action_target="result", action_value=solution.answer),
    ]


def _arithmetic(solution: MathSolution) -> list[VideoElement]:
    elements: list[VideoElement] = []
    step = solution.steps[0] if solution.steps else solution.answer
    action = infer_action_from_expression(step) or "transform"
    semantic_keys = ("operand_a", "operator", "result")
    actions = ("highlight", action, "equal")
    for i, current_step in enumerate(solution.steps[:3]):
        start = 5 + i * 4
        end = start + 4
        elements.append(
            VideoElement(
                type="math_step",
                semantic_key=semantic_keys[min(i, len(semantic_keys) - 1)],
                text=current_step,
                x=0.5,
                y=0.45 + i * 0.15,
                scale=1.0,
                start=start,
                end=end,
                animation="pop",
                visual_action=actions[min(i, len(actions) - 1)],
                action_target=semantic_keys[min(i, len(semantic_keys) - 1)],
                action_from=step if action == "transform" else None,
                action_result=solution.answer if action == "transform" else None,
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
