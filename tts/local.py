import os
import shlex
import subprocess
from pathlib import Path

from .models import AudioSegment, VoiceConfig


def synthesize(
    text: str,
    start: float,
    duration: float,
    config: VoiceConfig,
    output_dir: str = "output/audio",
) -> AudioSegment:
    """Run a local TTS command without requiring a cloud API.

    The command is configured through F5_TTS_COMMAND. Supported placeholders:
    {text}, {output}, {voice}, {speed}, {pitch}.

    The adapter intentionally does not assume the CLI syntax of tts_clone.py;
    configure the exact command used by the user's local installation.
    """
    command_template = os.getenv("F5_TTS_COMMAND", "").strip()
    if not command_template:
        raise RuntimeError(
            "未配置 F5_TTS_COMMAND。请在 .env 中填写本地 tts_clone.py 的实际调用命令。"
        )

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    audio_path = output / f"segment_{start:.3f}.wav"

    values = {
        "text": text,
        "output": str(audio_path),
        "voice": config.voice_id,
        "speed": str(config.speed),
        "pitch": str(config.pitch),
    }
    command = command_template.format(**values)
    subprocess.run(
        shlex.split(command, posix=False),
        check=True,
        capture_output=True,
        text=True,
    )

    if not audio_path.exists():
        raise RuntimeError(f"本地 TTS 未生成音频文件：{audio_path}")

    return AudioSegment(
        text=text,
        start=start,
        end=start + duration,
        audio_path=str(audio_path),
    )
