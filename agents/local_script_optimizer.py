import json
from copy import deepcopy

from llm.models import LLMConfig
from llm.provider import generate_local
from math_engine.models import MathSolution

from .script_selector import score_script, select_script
from .teacher import generate_variants


def _prompt(solution: MathSolution, variants: list[dict], target_duration: int) -> str:
    payload = {
        "task": "从候选讲解脚本中选择一个，并只优化表达，不得修改数学事实。",
        "rules": [
            "不得修改 solution.answer。",
            "不得修改 solution.steps。",
            "不得新增未经 solution 证明的数学结论。",
            "面向家长，孩子也能听懂。",
            "教学价值优先，CTA 必须软，不得硬卖。",
            "目标时长约为指定秒数。",
            "只返回 JSON：candidate_index、hook、common_mistake、transfer、cta、reason。",
        ],
        "target_duration_seconds": target_duration,
        "solution": {
            "problem": solution.problem,
            "knowledge_point": solution.knowledge_point,
            "answer": solution.answer,
            "steps": solution.steps,
        },
        "candidates": variants,
    }
    return json.dumps(payload, ensure_ascii=False)


def _apply_safe_edit(original: dict, proposal: dict, solution: MathSolution) -> dict:
    allowed = ("hook", "common_mistake", "transfer", "cta")
    result = deepcopy(original)
    for key in allowed:
        value = proposal.get(key)
        if isinstance(value, str) and value.strip():
            result[key] = value.strip()
    # These fields remain deterministic and mathematically authoritative.
    result["explanation"] = original["explanation"]
    result["key_method"] = original["key_method"]
    result["duration_seconds"] = original.get("duration_seconds", 40)
    result["audience"] = original["audience"]
    return result


def select_teacher_script_with_local_llm(
    solution: MathSolution,
    target_duration: int = 40,
    config: LLMConfig | None = None,
) -> dict:
    if not solution.verified:
        raise ValueError("数学结果尚未验证，禁止进入 LLM 脚本优化")

    variants = generate_variants(solution)
    deterministic = select_script(variants, solution)

    config = config or LLMConfig()
    prompt = _prompt(solution, variants, target_duration)
    try:
        raw = generate_local(prompt, config)
        proposal = json.loads(raw)
        index = int(proposal.get("candidate_index", variants.index(deterministic)))
        if index < 0 or index >= len(variants):
            index = variants.index(deterministic)
        selected = _apply_safe_edit(variants[index], proposal, solution)
        if score_script(selected, solution) < 0:
            return deterministic
        return selected
    except Exception:
        # Local LLM is an optional optimization layer; deterministic selection remains the fallback.
        return deterministic
