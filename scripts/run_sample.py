from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from generate_video import generate_video
from tts.models import VoiceConfig

PROBLEM = "一个空水池，单独开进水管，6小时可以注满；单独开出水管，8小时可以放完一池水。现在雨天雨水匀速注入池中，同时打开进水管和出水管，12小时刚好注满水池。如果雨天只开出水管，多少小时可以把满池水放完？"

F5_PYTHON = r"C:\Users\38166\.workbuddy\binaries\python\envs\tts-env\Scripts\python.exe"
F5_SCRIPT = r"C:\Users\38166\.workbuddy\skills\mathscene\scripts\tts_clone.py"
AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac", ".m4a"}


def find_reference_audio() -> str:
    voice_dir = PROJECT_ROOT / "assets" / "voice"
    voice_dir.mkdir(parents=True, exist_ok=True)
    candidates = sorted(
        path for path in voice_dir.iterdir()
        if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS
    )
    if not candidates:
        raise RuntimeError(
            "没有找到参考人声。请把一段用于声音克隆的 WAV/MP3/M4A/FLAC 音频放到：\n"
            f"{voice_dir}\n\n"
            "放好后重新双击 scripts\\run_sample.bat。"
        )
    return str(candidates[0])


def build_voice_config() -> VoiceConfig:
    reference_audio = find_reference_audio()
    if not Path(F5_PYTHON).is_file():
        raise RuntimeError(f"找不到本机 F5-TTS Python：{F5_PYTHON}")
    if not Path(F5_SCRIPT).is_file():
        raise RuntimeError(f"找不到本机 F5-TTS 脚本：{F5_SCRIPT}")
    return VoiceConfig(
        provider="f5_tts",
        reference_audio=reference_audio,
        python_executable=F5_PYTHON,
        script_path=F5_SCRIPT,
        nfe_steps=64,
    )


if __name__ == "__main__":
    config = build_voice_config()
    print(f"Reference audio: {config.reference_audio}")
    result = generate_video(PROBLEM, "output/sample_01", voice_config=config)
    print("")
    print("SAMPLE VIDEO GENERATED")
    print(result["video_path"])
