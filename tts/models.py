from pydantic import BaseModel, Field
from typing import Optional


class VoiceConfig(BaseModel):
    provider: str = "f5_tts"
    voice_id: str = "default"
    speed: float = 1.0
    pitch: float = 0.0
    reference_audio: Optional[str] = None
    reference_text: Optional[str] = None
    python_executable: Optional[str] = None
    script_path: Optional[str] = None
    nfe_steps: int = 64


class AudioSegment(BaseModel):
    text: str
    start: float
    end: float
    audio_path: Optional[str] = None
    segment_id: Optional[str] = None


class TTSBatchResult(BaseModel):
    segments: list[AudioSegment] = Field(default_factory=list)
    output_dir: str
