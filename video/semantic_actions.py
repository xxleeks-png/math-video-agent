"""Reusable semantic math actions shared by the DSL, planners, and renderer.

The action names describe mathematical meaning rather than a concrete drawing.
Renderers are free to choose a visual representation for the same action.
"""

from __future__ import annotations

from typing import Optional


SUPPORTED_VISUAL_ACTIONS = frozenset(
    {
        "add",
        "subtract",
        "split",
        "merge",
        "compare",
        "transform",
        "equal",
        "highlight",
    }
)


def validate_action_fields(
    action: Optional[str],
    ratio: Optional[float] = None,
    units: Optional[int] = None,
    selected: Optional[int] = None,
    removed: Optional[int] = None,
    remaining: Optional[int] = None,
    left: Optional[str] = None,
    right: Optional[str] = None,
    result: Optional[str] = None,
    source: Optional[str] = None,
    target: Optional[str] = None,
) -> bool:
    """Validate an action payload without depending on VideoElement."""
    if action is not None and action not in SUPPORTED_VISUAL_ACTIONS:
        return False
    text_fields = (left, right, result, source, target)
    if any(value is not None and not str(value).strip() for value in text_fields):
        return False
    if ratio is not None and not 0 <= ratio <= 1:
        return False
    counts = (units, selected, removed, remaining)
    if any(v is not None and v < 0 for v in counts):
        return False
    if units is not None:
        if units <= 0:
            return False
        for value in (selected, removed, remaining):
            if value is not None and value > units:
                return False
        if selected is not None and removed is not None and removed > selected:
            return False
        if selected is not None and removed is not None and remaining is not None:
            if selected - removed != remaining:
                return False
    if action == "compare" and (left is None or right is None):
        return False
    if action == "transform" and source is None and target is None and result is None:
        return False
    if action == "split" and source is None and result is None and units is None:
        return False
    if action == "merge" and source is None and result is None and left is None and right is None:
        return False
    return True


def infer_action_from_expression(expression: str) -> Optional[str]:
    """Infer the simplest reusable action from a spoken/displayed math step."""
    text = expression or ""
    if "−" in text or "-" in text:
        return "subtract"
    if "+" in text:
        return "add"
    if "×" in text or "*" in text:
        return "transform"
    if "÷" in text or "/" in text:
        return "transform"
    if "=" in text:
        return "equal"
    return None
