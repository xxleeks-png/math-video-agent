from pydantic import BaseModel
from typing import Optional


class VoiceConfig(BaseModel):
    provider: str = "mock"
    voice_id: str = "default"
    speed: float = 1.0
    pitch: float = 0.0


class AudioSegment(BaseModel):
    text: str
    start: float
    end: float
    audio_path: Optional[str] = None
