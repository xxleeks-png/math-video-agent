from agents.teacher import generate_teacher_script
from math_engine.models import MathSolution
from .dsl import VideoDocument, VideoScene, VideoElement, validate_video_document


def build_storyboard(solution: MathSolution) -> VideoDocument:
    script = generate_teacher_script(solution)

    scenes = [
        VideoScene(
            start=0, end=4,
            elements=[
                VideoElement(type="title", text="这道题的关键是什么？", x=0.5, y=0.22, emphasis=True),
                VideoElement(type="problem", text=solution.problem, x=0.5, y=0.48),
            ],
            narration=script["hook"],
            subtitle=script["hook"],
        ),
        VideoScene(
            start=4, end=24,
            elements=[
                VideoElement(type="method", text=script["key_method"], x=0.5, y=0.18, emphasis=True),
                *[
                    VideoElement(type="step", text=step, x=0.5, y=0.38 + i * 0.10)
                    for i, step in enumerate(solution.steps[:5])
                ],
            ],
            narration=" ".join(script["explanation"][:6]),
            subtitle=" ".join(script["explanation"][:3]),
        ),
        VideoScene(
            start=24, end=32,
            elements=[
                VideoElement(type="warning", text="常见错误", x=0.5, y=0.25, emphasis=True),
                VideoElement(type="text", text=script["common_mistake"], x=0.5, y=0.48),
            ],
            narration=script["common_mistake"],
            subtitle=script["common_mistake"],
        ),
        VideoScene(
            start=32, end=40,
            elements=[
                VideoElement(type="summary", text=script["key_method"], x=0.5, y=0.28, emphasis=True),
                VideoElement(type="cta", text=script["cta"], x=0.5, y=0.58),
            ],
            narration=script["transfer"] + " " + script["cta"],
            subtitle=script["transfer"],
        ),
    ]

    document = VideoDocument(duration=40, scenes=scenes)
    if not validate_video_document(document):
        raise ValueError("生成的视频 DSL 未通过时间轴校验")
    return document
