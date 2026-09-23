from dataclasses import dataclass


@dataclass(frozen=True)
class SegmentPlan:
    key: str
    start: float
    end: float


@dataclass(frozen=True)
class ShortVideoPlan:
    duration: float
    segments: tuple[SegmentPlan, ...]


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def plan_short_video(
    problem_type: str,
    target_duration: float = 40.0,
    explanation_complexity: int = 1,
) -> ShortVideoPlan:
    """Create a deterministic short-video rhythm before any LLM rewriting.

    The plan is intentionally independent from the final wording so the LLM
    cannot accidentally control the mathematical timeline.
    """
    duration = _clamp(float(target_duration), 25.0, 60.0)

    # More complex word problems get more explanation time; arithmetic stays fast.
    if problem_type in ("四则运算", "分数运算"):
        weights = (0.12, 0.46, 0.18, 0.24)
    elif problem_type in ("工程问题", "流水问题", "面积与周长"):
        weights = (0.10, 0.52, 0.18, 0.20)
    else:
        weights = (0.12, 0.48, 0.18, 0.22)

    if explanation_complexity >= 2:
        weights = (weights[0], min(0.58, weights[1] + 0.06), weights[2], 1.0 - weights[0] - min(0.58, weights[1] + 0.06) - weights[2])

    keys = ("hook", "explain", "mistake", "summary")
    segments = []
    cursor = 0.0
    for key, weight in zip(keys, weights):
        end = duration if key == keys[-1] else round(cursor + duration * weight, 2)
        segments.append(SegmentPlan(key=key, start=round(cursor, 2), end=end))
        cursor = end

    return ShortVideoPlan(duration=duration, segments=tuple(segments))
