from math_engine.models import MathSolution


def score_script(script: dict, solution: MathSolution) -> float:
    """Deterministic pre-LLM scorer; rewards teachability and penalizes unsafe output."""
    if not solution.verified:
        return -1.0
    score = 0.0
    text = " ".join(
        str(script.get(key, ""))
        for key in ("hook", "explanation", "common_mistake", "key_method", "transfer")
    )
    if script.get("audience", {}).get("primary") == "parent":
        score += 2.0
    if script.get("audience", {}).get("secondary") == "child":
        score += 1.0
    if script.get("duration_seconds", 0) <= 60:
        score += 1.0
    if script.get("common_mistake"):
        score += 1.5
    if script.get("transfer"):
        score += 1.0
    if solution.knowledge_point and solution.knowledge_point in text:
        score += 1.5
    if solution.answer in text:
        score += 1.0
    if len(text) > 900:
        score -= 2.0
    return score


def select_script(variants: list[dict], solution: MathSolution) -> dict:
    if not variants:
        raise ValueError("没有可供选择的讲解脚本")
    scored = [(score_script(script, solution), index, script) for index, script in enumerate(variants)]
    _, _, selected = max(scored, key=lambda item: (item[0], -item[1]))
    return selected


def select_teacher_script(solution: MathSolution) -> dict:
    from .teacher import generate_variants
    return select_script(generate_variants(solution), solution)
