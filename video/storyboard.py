from agents.script_selector import select_teacher_script
from agents.local_script_optimizer import select_teacher_script_with_local_llm
from llm.models import LLMConfig
from .short_video_plan import plan_short_video
import os
from math_engine.models import MathSolution
from .dsl import VideoDocument, VideoScene, VideoElement, validate_video_document
from .math_visuals import build_math_visuals
from .narration_visual_map import build_narration_visual_cues
from agents.mistake_strategy import build_mistake_strategy

def build_storyboard(solution: MathSolution) -> VideoDocument:
    use_local_llm = os.getenv("USE_LOCAL_LLM_SCRIPT_OPTIMIZER", "0").strip().lower() in {"1", "true", "yes", "on"}
    if use_local_llm:
        script = select_teacher_script_with_local_llm(solution, target_duration=40, config=LLMConfig())
    else:
        script = select_teacher_script(solution)
    visual_elements = build_math_visuals(solution)
    mistake = build_mistake_strategy(solution)
    explain_end = timing["explain"].end
    mistake_start = timing["mistake"].start
    mistake_end = timing["mistake"].end
    explain_visuals = [e for e in visual_elements if (e.end or 0) <= explain_end]
    mistake_visuals = [
        VideoElement(type="mistake", text=mistake["mistake"], x=0.5, y=0.48, scale=0.78, start=mistake_start + 0.2, end=mistake_start + 1.8, animation="shake"),
        VideoElement(type="correction", text=mistake["why"], x=0.5, y=0.68, scale=0.76, start=mistake_start + 1.5, end=mistake_start + 3.5, animation="slide"),
        VideoElement(type="method", text=mistake["method"], x=0.5, y=0.84, scale=0.76, start=mistake_start + 3.0, end=mistake_end - 0.2, animation="pop"),
    ]
    plan = plan_short_video(solution.knowledge_point.split(" / ")[0], target_duration=40)
    timing = {segment.key: segment for segment in plan.segments}
    scenes = [
        VideoScene(
            start=timing["hook"].start, end=timing["hook"].end,
            elements=[
                VideoElement(type="title", text="这道题的关键是什么？", x=0.5, y=0.22, emphasis=True, start=0, end=4, animation="fade"),
                VideoElement(type="problem", text=solution.problem, x=0.5, y=0.48, start=timing["hook"].start + 0.5, end=timing["hook"].end - 0.2, animation="fade_slide"),
            ],
            narration=script["hook"], subtitle=script["hook"],
        ),
        VideoScene(
            start=timing["explain"].start, end=timing["explain"].end,
            elements=[
                VideoElement(type="method", text=script["key_method"], x=0.5, y=0.18, emphasis=True, start=timing["explain"].start, end=timing["explain"].end, animation="fade"),
                *explain_visuals,
            ],
            narration=" ".join(script["explanation"][:6]),
            subtitle=" ".join(script["explanation"][:3]),
        ),
        VideoScene(
            start=timing["mistake"].start, end=timing["mistake"].end,
            elements=[
                VideoElement(type="warning", text="常见错误", x=0.5, y=0.25, emphasis=True, start=timing["mistake"].start, end=timing["mistake"].start + 1.0, animation="fade"),
                *mistake_visuals,
                VideoElement(type="text", text=mistake["why"], x=0.5, y=0.40, start=timing["mistake"].start + 0.3, end=timing["mistake"].end - 0.4, animation="fade_slide"),
            ],
            narration=mistake["mistake"] + " " + mistake["why"] + " " + mistake["method"], subtitle=mistake["mistake"],
        ),
        VideoScene(
            start=timing["summary"].start, end=timing["summary"].end,
            elements=[
                VideoElement(type="summary", text=script["key_method"], x=0.5, y=0.28, emphasis=True, start=timing["summary"].start, end=timing["summary"].end, animation="fade"),
                VideoElement(type="answer", text=f"答案：{solution.answer}", x=0.5, y=0.45, emphasis=True, start=timing["summary"].start + 1.0, end=timing["summary"].end - 1.5, animation="pop"),
                VideoElement(type="cta", text=script["cta"], x=0.5, y=0.62, start=timing["summary"].start + 4.0, end=timing["summary"].end, animation="fade"),
            ],
            narration=script["transfer"] + " " + script["cta"], subtitle=script["transfer"],
        ),
    ]
    document = VideoDocument(duration=plan.duration, scenes=scenes)
    if not validate_video_document(document):
        raise ValueError("生成的视频 DSL 未通过时间轴校验")
    cues = build_narration_visual_cues(document)
    document = document.model_copy(update={"visual_cues": [cue.__dict__ for cue in cues]})
    return document
