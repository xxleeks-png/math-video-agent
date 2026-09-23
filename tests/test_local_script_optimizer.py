from agents.local_script_optimizer import select_teacher_script_with_local_llm
from math_engine.solver import solve


def test_local_llm_optimizer_falls_back_without_call(monkeypatch):
    solution = solve("36 ÷ 6")

    def fail(*args, **kwargs):
        raise RuntimeError("ollama unavailable")

    monkeypatch.setattr("agents.local_script_optimizer.generate_local", fail)
    script = select_teacher_script_with_local_llm(solution)
    assert script["audience"]["primary"] == "parent"
    assert script["explanation"] == ["先确定单位“1”，再把题目中的条件换算成每小时的变化量。",
                                     "36 ÷ 6 = 6"]


def test_local_llm_cannot_change_math(monkeypatch):
    solution = solve("36 ÷ 6")

    def fake_generate(*args, **kwargs):
        return '{"candidate_index": 0, "hook": "优化后的开场", "common_mistake": "注意单位", "transfer": "再练两题", "cta": "可以继续练习"}'

    monkeypatch.setattr("agents.local_script_optimizer.generate_local", fake_generate)
    script = select_teacher_script_with_local_llm(solution)
    assert script["explanation"][1] == "36 ÷ 6 = 6"
    assert script["key_method"] == "四则运算"
    assert script["hook"] == "优化后的开场"
