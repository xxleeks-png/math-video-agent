from math_engine.solver import solve
from video.storyboard import build_storyboard
from llm.models import LLMConfig
from tts.models import VoiceConfig


def test_local_configs():
    assert LLMConfig().base_url.startswith("http://127.0.0.1")
    assert VoiceConfig().provider == "mock"


def test_pipeline_stays_local_before_external_services():
    solution = solve("1/2 + 1/3")
    assert solution.answer == "5/6"
    assert solution.verified is True

    document = build_storyboard(solution)
    assert document.duration == 40
