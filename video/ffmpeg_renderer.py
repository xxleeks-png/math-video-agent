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
        blocks.append(f"{i}\n{_stamp(scene.start)} --> {_stamp(scene.end)}\n{text}\n")
    subtitle_file.write_text("\n".join(blocks), encoding="utf-8")
    return subtitle_file


def _visual_filter(document: VideoDocument, subtitle_file: Path) -> str:
    """Build a dependency-light animated card layout from the Video DSL."""
    filters = [
        "format=yuv420p",
        "drawbox=x=70:y=90:w=940:h=120:h=fill:color=0x111827@0.94",
        "drawbox=x=70:y=230:w=940:h=4:h=fill:color=0x2563EB@1",
    ]
    accents = ["0x2563EB", "0x7C3AED", "0x059669", "0xEA580C"]
    for i, scene in enumerate(document.scenes):
        accent = accents[i % len(accents)]
        start = f"{scene.start:g}"
        end = f"{scene.end:g}"
        filters.append(
            f"drawbox=x=70:y=90:w=940:h=120:h=fill:color={accent}@0.96:enable=between(t\\,{start}\\,{end})"
        )
        filters.append(
            f"drawbox=x=70:y=260:w=940:h=4:h=fill:color={accent}@1:enable=between(t\\,{start}\\,{end})"
        )
        filters.append(
            f"drawbox=x=70:y=300:w=940:h=520:h=fill:color=0xF8FAFC@0.92:enable=between(t\\,{start}\\,{end})"
        )
    subtitle_path = str(subtitle_file).replace("\\", "/").replace(":", "\\:")
    filters.append(
        "subtitles=" + subtitle_path + ":force_style="
        "'FontName=Microsoft YaHei,FontSize=20,PrimaryColour=&H00111111&,OutlineColour=&H00FFFFFF&,Outline=2,Alignment=2,MarginV=150'"
    )
    return ",".join(filters)


def render_mp4(document: VideoDocument, output_path: str = "output/math_video.mp4", audio_segments: list[AudioSegment] | None = None) -> str:
    """Render a vertical MP4 with scene cards, subtitles and optional local TTS audio."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("未检测到 FFmpeg，请先安装 FFmpeg 并加入 PATH")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    subtitle_file = _subtitle_file(document, output)
    vf = _visual_filter(document, subtitle_file)

    command = [ffmpeg, "-y", "-f", "lavfi", "-i",
               f"color=c=0xF3F4F6:s={document.width}x{document.height}:r={document.fps}:d={document.duration}"]

    valid_audio = [s for s in (audio_segments or []) if s.audio_path and Path(s.audio_path).exists()]
    if valid_audio:
        for segment in valid_audio:
            command += ["-i", segment.audio_path]
        filters = []
        mix_inputs = []
        for i, segment in enumerate(valid_audio):
            delay_ms = max(0, int(round(segment.start * 1000)))
            filters.append(f"[{i + 1}:a]adelay={delay_ms}:all=1[a{i}]")
            mix_inputs.append(f"[a{i}]")
        filters.append("".join(mix_inputs) + f"amix=inputs={len(valid_audio)}:duration=longest:dropout_transition=0,atrim=duration={document.duration},asetpts=N/SR/TB[aout]")
        command += ["-filter_complex", ";".join(filters), "-map", "0:v", "-map", "[aout]", "-vf", vf,
                    "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", "-shortest", str(output)]
    else:
        command += ["-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(output)]

    try:
        subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "")[-4000:]
        raise RuntimeError(f"FFmpeg 渲染失败：\n{detail}") from exc
    return str(output)
