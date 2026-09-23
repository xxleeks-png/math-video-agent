from math_engine.solver import solve
from video.storyboard import build_storyboard
from video.dsl import validate_video_document


def test_storyboard_from_verified_math():
    solution = solve("36 ÷ 6")
    assert solution.verified is True

    document = build_storyboard(solution)
    assert document.version == "0.5.0"
    assert document.width == 1080
    assert document.height == 1920
    assert document.duration == 40
    assert len(document.scenes) == 4
    assert validate_video_document(document) is True


def test_scene_timeline_is_ordered():
    document = build_storyboard(solve("27 + 15"))
    ends = [scene.end for scene in document.scenes]
    starts = [scene.start for scene in document.scenes]
    assert starts == sorted(starts)
    assert ends == sorted(ends)
    assert ends[-1] == document.duration
