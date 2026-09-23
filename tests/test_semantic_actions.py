from math_engine.solver import solve
from video.dsl import VideoDocument, VideoElement, VideoScene, validate_video_document
from video.math_visuals import build_math_visuals
from video.semantic_actions import SUPPORTED_VISUAL_ACTIONS, infer_action_from_expression


def test_shared_action_registry_contains_core_primitives():
    assert {"add", "subtract", "split", "merge", "compare", "transform", "equal", "highlight"} <= SUPPORTED_VISUAL_ACTIONS


def test_expression_action_inference():
    assert infer_action_from_expression("3/4 + 1/4 = 1") == "add"
    assert infer_action_from_expression("2/3 - 1/3 = 1/3") == "subtract"
    assert infer_action_from_expression("6 × 4 = 24") == "transform"
    assert infer_action_from_expression("24 ÷ 6 = 4") == "transform"


def test_arithmetic_visuals_use_operation_action():
    add = build_math_visuals(solve("36 + 6"))
    sub = build_math_visuals(solve("36 - 6"))
    assert any(e.visual_action == "add" for e in add)
    assert any(e.visual_action == "subtract" for e in sub)


def test_fraction_subtraction_carries_structured_counts():
    elements = build_math_visuals(solve("2/3 - 1/3"))
    operation = next(e for e in elements if e.semantic_key == "operation")
    assert operation.visual_action == "subtract"
    assert operation.action_units == 3
    assert operation.action_selected == 2
    assert operation.action_removed == 1
    assert operation.action_remaining == 1


def test_dsl_rejects_invalid_action_payload():
    document = VideoDocument(
        duration=2,
        scenes=[
            VideoScene(
                start=0,
                end=2,
                elements=[
                    VideoElement(
                        type="formula",
                        visual_action="not-a-real-action",
                        start=0.2,
                        end=1.5,
                    )
                ],
            )
        ],
    )
    assert not validate_video_document(document)


def test_dsl_rejects_inconsistent_counts():
    document = VideoDocument(
        duration=2,
        scenes=[
            VideoScene(
                start=0,
                end=2,
                elements=[
                    VideoElement(
                        type="formula",
                        visual_action="subtract",
                        action_units=8,
                        action_selected=3,
                        action_removed=4,
                        action_remaining=0,
                        start=0.2,
                        end=1.5,
                    )
                ],
            )
        ],
    )
    assert not validate_video_document(document)
