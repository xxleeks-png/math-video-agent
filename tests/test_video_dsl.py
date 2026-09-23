from video.dsl import VideoDocument, VideoElement, VideoScene, validate_video_document


def test_structured_action_counts_validate():
    element = VideoElement(
        type="formula",
        semantic_key="effective_outflow",
        visual_action="subtract",
        action_units=24,
        action_selected=3,
        action_removed=1,
        action_remaining=2,
        start=20,
        end=24,
    )
    document = VideoDocument(
        duration=24,
        scenes=[VideoScene(start=0, end=24, elements=[element])],
    )
    assert validate_video_document(document) is True


def test_structured_action_counts_reject_inconsistent_remainder():
    element = VideoElement(
        type="formula",
        visual_action="subtract",
        action_units=24,
        action_selected=3,
        action_removed=1,
        action_remaining=3,
        start=20,
        end=24,
    )
    document = VideoDocument(
        duration=24,
        scenes=[VideoScene(start=0, end=24, elements=[element])],
    )
    assert validate_video_document(document) is False
