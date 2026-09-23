import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from math_engine.solver import solve
from video.ffmpeg_renderer import render_mp4
from video.storyboard import build_storyboard
from video.voice_timeline import synthesize_voice_timeline
from tts.models import VoiceConfig


def _load_config() -> VoiceConfig:
    load_dotenv()
    return VoiceConfig(
        provider="f5_tts",
        reference_audio=os.getenv("F5_TTS_REFERENCE_AUDIO") or None,
        reference_text=os.getenv("F5_TTS_REF_TEXT") or None,
        python_executable=os.getenv("F5_TTS_PYTHON") or None,
        script_path=os.getenv("F5_TTS_SCRIPT") or None,
        nfe_steps=int(os.getenv("F5_TTS_NFE_STEP", "64")),
    )


def generate_video(
    problem: str,
    output_dir: str = "output",
    voice_config: VoiceConfig | None = None,
) -> dict:
    solution = solve(problem)
    if not solution.verified:
        raise ValueError("数学结果未通过验证，已停止视频生产。")

    document = build_storyboard(solution)
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    voice_config = voice_config or _load_config()
    audio_result = synthesize_voice_timeline(
        document,
        voice_config,
        str(output_root / "audio"),
    )

    video_path = render_mp4(
        document,
        str(output_root / "math_video.mp4"),
        audio_segments=audio_result.segments,
    )

    result = {
        "video_path": video_path,
        "solution": solution.model_dump(),
        "audio": [segment.model_dump() for segment in audio_result.segments],
        "duration": document.duration,
        "resolution": f"{document.width}x{document.height}",
    }
    (output_root / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="本地小学数学讲题视频一键生成器")
    parser.add_argument("problem", help="数学题目文本")
    parser.add_argument("--output-dir", default="output", help="输出目录")
    args = parser.parse_args()

    result = generate_video(args.problem, args.output_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
