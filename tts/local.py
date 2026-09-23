import json
import os
import subprocess
import wave
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


def _wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        frames = wav.getnframes()
        rate = wav.getframerate()
        return frames / rate if rate else 0.0


def _retime_segments(segments: list[AudioSegment], pause: float = 0.08) -> list[AudioSegment]:
    cursor = 0.0
    result = []
    for segment in segments:
        duration = _wav_duration(Path(segment.audio_path)) if segment.audio_path else 0.0
        if duration <= 0:
            duration = max(segment.end - segment.start, 0.1)
        start = cursor
        end = start + duration
        result.append(segment.model_copy(update={"start": start, "end": end}))
        cursor = end + pause
    return result


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
    # Stream F5-TTS output so a local inference failure is visible immediately.
    # Keep a log file as well, because the launcher may close before the traceback
    # can be copied from the console.
    log_path = output / "f5_tts.log"
    # The project is designed to run fully locally. Prevent inherited proxy
    # settings from making Hugging Face / httpx attempt a network request.
    # If a required model is genuinely missing from the local cache, F5-TTS
    # will now report that directly instead of failing on a SOCKS dependency.
    child_env = os.environ.copy()
    for proxy_name in (
        "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY",
        "http_proxy", "https_proxy", "all_proxy",
    ):
        child_env.pop(proxy_name, None)
    child_env["HF_HUB_OFFLINE"] = "1"
    child_env["TRANSFORMERS_OFFLINE"] = "1"

    with log_path.open("w", encoding="utf-8", errors="replace") as log_file:
        completed = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=child_env,
        )
        log_file.write(completed.stdout or "")
        if completed.stdout:
            print(completed.stdout, end="", flush=True)

    if completed.returncode != 0:
        tail = (completed.stdout or "")[-6000:]
        raise RuntimeError(
            "F5-TTS 本地推理失败，退出码 "
            f"{completed.returncode}。详细日志：{log_path}\n\n{tail}"
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

    result_segments = _retime_segments(result_segments)
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
