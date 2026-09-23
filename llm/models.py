from pydantic import BaseModel


class LLMConfig(BaseModel):
    provider: str = "ollama"
    model: str = "qwen3.5:9b"
    base_url: str = "http://127.0.0.1:11434"
    temperature: float = 0.2
    timeout_seconds: int = 120
