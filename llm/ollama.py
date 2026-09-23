import json
from urllib import request

from .models import LLMConfig


def generate(prompt: str, config: LLMConfig) -> str:
    payload = json.dumps(
        {
            "model": config.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": config.temperature},
        }
    ).encode("utf-8")

    req = request.Request(
        f"{config.base_url.rstrip('/')}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with request.urlopen(req, timeout=config.timeout_seconds) as response:
        data = json.loads(response.read().decode("utf-8"))

    result = data.get("response")
    if not result:
        raise RuntimeError("本地 Ollama 未返回有效文本")
    return result
