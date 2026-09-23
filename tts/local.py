import json
import os
import subprocess
from pathlib import Path
from typing import Iterable

from .models import AudioSegment, TTSBatchResult, VoiceConfig


AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac", ".m4a"}


def _env_or(value: str | None, name: str, default: str = "") -> str:
    return value or os.getenv(name, default)


def _find_reference_audio(config: VoiceConfig) -> str:
    if config.reference_audio:
        path = Path(config.reference_audio)
        if path.is_file():
            return str(path)

    directory = os.getenv("F5_TTS_REF_AUDIO_DIR", "").strip()
    if not directory:
        raise RuntimeError(
            "未配置 F5_TTS_REF_AUDIO_DIR，也没有提供 VoiceConfig.reference_audio。"
        )

    candidates = sorted(
        p for p in Path(directory).iterdir()
        if p.is_file() and p.suffix.lower() in AUDIO_EXTENSIONS
    )
    if not candidates:
        raise RuntimeError(f"参考音频目录中没有找到音频文件：{directory}")
    return str(candidates[0])


def _paths(config: VoiceConfig) -> tuple[str, str]:
    python_executable = _env_or(
        config.python_executable,
        "F5_TTS_PYTHON",
        "python",
    )
    script_path = _env_or(config.script_path, "F5_TTS_SCRIPT")
    if not script_path:
        raise RuntimeError("未配置 F5_TTS_SCRIPT。")
    return python_executable, script_path


def synthesize_batch(
    segments: Iterable[AudioSegment],
    config: VoiceConfig,
    output_dir: str = "output/audio",
) -> TTSBatchResult:
    """Call the user's real local tts_clone.py once for a whole scene timeline.

    Expected CLI:
        python tts_clone.py <ref_audio> <script.json> <output_dir>

    Expected script.json:
        [{"id": "step1", "text": "..."}]
    """
    items = list(segments)
    if not items:
        return TTSBatchResult(segments=[], output_dir=output_dir)

    reference_audio = _find_reference_audio(config)
    python_executable, script_path = _paths(config)

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    script_json = output / "script.json"
    payload = []
    for index, segment in enumerate(items, 1):
        payload.append({
            "id": segment.segment_id or f"step{index}",
            "text": segment.text,
            **({"ref_text": config.reference_text} if config.reference_text else {}),
        })
    script_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    command = [
        python_executable,
        script_path,
        reference_audio,
        str(script_json),
        str(output),
    ]
    completed = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    generated = {
        p.stem: p for p in output.rglob("*.wav") if p.is_file()
    }
    result_segments = []
    missing = []
    for index, segment in enumerate(items, 1):
        segment_id = segment.segment_id or f"step{index}"
        audio = generated.get(segment_id)
        if audio is None:
            # Fallback for scripts that rename outputs but preserve generation order.
            ordered = sorted(
                p for p in output.rglob("*.wav")
                if p.is_file() and p.name != script_json.name
            )
            if index <= len(ordered):
                audio = ordered[index - 1]
        if audio is None:
            missing.append(segment_id)
            continue

        result_segments.append(
            segment.model_copy(update={
                "segment_id": segment_id,
                "audio_path": str(audio),
            })
        )

    if missing:
        stdout = completed.stdout[-2000:]
        stderr = completed.stderr[-2000:]
        raise RuntimeError(
            "F5-TTS 已执行，但没有找到全部 WAV 输出。"
            f"缺少：{missing}。\nstdout:\n{stdout}\nstderr:\n{stderr}"
        )

    return TTSBatchResult(segments=result_segments, output_dir=str(output))


def synthesize(
    text: str,
    start: float,
    duration: float,
    config: VoiceConfig,
    output_dir: str = "output/audio",
) -> AudioSegment:
    segment = AudioSegment(
        text=text,
        start=start,
        end=start + duration,
        segment_id=f"step_{int(start * 1000):08d}",
    )
    return synthesize_batch([segment], config, output_dir).segments[0]
