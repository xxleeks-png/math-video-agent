from agents.teacher import generate_teacher_script
from math_engine.models import MathSolution
from .dsl import VideoDocument, VideoScene, VideoElement, validate_video_document

def _math_elements(solution: MathSolution) -> list[VideoElement]:
    elements = []
    for i, step in enumerate(solution.steps[:5]):
        start = 6 + i * 3.2
        end = start + 3.0
        elements.append(VideoElement(
            type="math_step",
            text=step,
            x=0.5,
            y=0.44 + (i % 3) * 0.14,
            scale=1.0 if i == len(solution.steps[:5]) - 1 else 0.88,
            emphasis=i == len(solution.steps[:5]) - 1,
            start=start,
            end=end,
            animation="fade_slide",
        ))
    return elements

def build_storyboard(solution: MathSolution) -> VideoDocument:
    script = generate_teacher_script(solution)
    scenes = [
        VideoScene(
            start=0, end=4,
            elements=[
                VideoElement(type="title", text="这道题的关键是什么？", x=0.5, y=0.22, emphasis=True, start=0, end=4, animation="fade"),
                VideoElement(type="problem", text=solution.problem, x=0.5, y=0.48, start=0.6, end=3.8, animation="fade_slide"),
            ],
            narration=script["hook"], subtitle=script["hook"],
        ),
        VideoScene(
            start=4, end=24,
            elements=[
                VideoElement(type="method", text=script["key_method"], x=0.5, y=0.18, emphasis=True, start=4, end=24, animation="fade"),
                *_math_elements(solution),
            ],
            narration=" ".join(script["explanation"][:6]),
            subtitle=" ".join(script["explanation"][:3]),
        ),
        VideoScene(
            start=24, end=32,
            elements=[
                VideoElement(type="warning", text="常见错误", x=0.5, y=0.25, emphasis=True, start=24, end=32, animation="fade"),
                VideoElement(type="text", text=script["common_mistake"], x=0.5, y=0.48, start=24.6, end=31.5, animation="fade_slide"),
            ],
            narration=script["common_mistake"], subtitle=script["common_mistake"],
        ),
        VideoScene(
            start=32, end=40,
            elements=[
                VideoElement(type="summary", text=script["key_method"], x=0.5, y=0.28, emphasis=True, start=32, end=40, animation="fade"),
                VideoElement(type="answer", text=f"答案：{solution.answer}", x=0.5, y=0.45, emphasis=True, start=33, end=38.5, animation="pop"),
                VideoElement(type="cta", text=script["cta"], x=0.5, y=0.62, start=36, end=40, animation="fade"),
            ],
            narration=script["transfer"] + " " + script["cta"], subtitle=script["transfer"],
        ),
    ]
    document = VideoDocument(duration=40, scenes=scenes)
    if not validate_video_document(document):
        raise ValueError("生成的视频 DSL 未通过时间轴校验")
    return document
