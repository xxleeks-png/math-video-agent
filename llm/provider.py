from .models import LLMConfig


def generate_local(prompt: str, config: LLMConfig | None = None) -> str:
    config = config or LLMConfig()

    if config.provider != "ollama":
        raise ValueError(f"暂不支持本地 LLM provider：{config.provider}")

    from .ollama import generate

    return generate(prompt, config)
