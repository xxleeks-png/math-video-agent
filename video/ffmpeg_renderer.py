import shutil
import subprocess
from pathlib import Path

from .dsl import VideoDocument
from tts.models import AudioSegment


def _stamp(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _subtitle_file(document: VideoDocument, output: Path) -> Path:
    subtitle_file = output.with_suffix(".srt")
    blocks = []
    for i, scene in enumerate(document.scenes, 1):
        text = scene.subtitle or scene.narration
        blocks.append(
            f"{i}\n{_stamp(scene.start)} --> {_stamp(scene.end)}\n{text}\n"
        )
    subtitle_file.write_text("\n".join(blocks), encoding="utf-8")
    return subtitle_file


def render_mp4(
    document: VideoDocument,
    output_path: str = "output/math_video.mp4",
    audio_segments: list[AudioSegment] | None = None,
) -> str:
    """Render vertical MP4 and optionally mux real local TTS audio."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("未检测到 FFmpeg，请先安装 FFmpeg 并加入 PATH")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    subtitle_file = _subtitle_file(document, output)

    vf = (
        "subtitles="
        + str(subtitle_file).replace("\\", "/").replace(":", "\\:")
        + ":force_style='FontSize=18,Alignment=2,MarginV=120'"
    )

    command = [
        ffmpeg,
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"color=c=white:s={document.width}x{document.height}:r={document.fps}:d={document.duration}",
    ]

    valid_audio = [
        segment for segment in (audio_segments or [])
        if segment.audio_path and Path(segment.audio_path).exists()
    ]

    if valid_audio:
        for segment in valid_audio:
            command += ["-i", segment.audio_path]

        filters = []
        mix_inputs = []
        for i, segment in enumerate(valid_audio):
            delay_ms = max(0, int(round(segment.start * 1000)))
            filters.append(
                f"[{i + 1}:a]adelay={delay_ms}:all=1[a{i}]"
            )
            mix_inputs.append(f"[a{i}]")

        filters.append(
            "".join(mix_inputs)
            + f"amix=inputs={len(valid_audio)}:duration=longest:dropout_transition=0,"
            + f"atrim=duration={document.duration},asetpts=N/SR/TB[aout]"
        )
        command += [
            "-filter_complex",
            ";".join(filters),
            "-map",
            "0:v",
            "-map",
            "[aout]",
            "-vf",
            vf,
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            "-shortest",
            str(output),
        ]
    else:
        command += [
            "-vf",
            vf,
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            "-an",
            str(output),
        ]

    subprocess.run(command, check=True, capture_output=True, text=True)
    return str(output)
