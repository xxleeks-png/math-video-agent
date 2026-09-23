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

def _escape_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace(",", "\\,").replace(";", "\\;")

def _font_file() -> str | None:
    candidates = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/msyh.ttf",
        "C:/Windows/Fonts/simhei.ttf",
    ]
    return next((p for p in candidates if Path(p).exists()), None)

def _drawtext(element, fontfile: str | None) -> str:
    text = _escape_text(element.text or element.value or "")
    x = f"(w-text_w)*{element.x:.3f}"
    y = f"h*{element.y:.3f}-text_h/2"
    size = int(48 * max(0.7, min(1.8, element.scale)))
    color = "white" if element.emphasis else "0x111827"
    box = "box=1:boxcolor=0xFFFFFF@0.92:boxborderw=18" if not element.emphasis else "box=1:boxcolor=0x111827@0.96:boxborderw=22"
    enable = ""
    if element.start is not None and element.end is not None:
        enable = f":enable=between(t\\,{element.start:g}\\,{element.end:g})"
    font = f":fontfile={fontfile}" if fontfile else ""
    return f"drawtext=text={text}:fontsize={size}:fontcolor={color}:x={x}:y={y}:{box}:shadowx=2:shadowy=2{font}{enable}"

def _visual_filter(document: VideoDocument, subtitle_file: Path) -> str:
    filters = ["format=yuv420p"]
    fontfile = _font_file()
    for scene in document.scenes:
        start, end = f"{scene.start:g}", f"{scene.end:g}"
        filters.append(f"drawbox=x=60:y=80:w=960:h=130:color=0x111827@0.96:t=fill:enable=between(t\\,{start}\\,{end})")
        filters.append(f"drawbox=x=60:y=230:w=960:h=5:color=0x2563EB@1:t=fill:enable=between(t\\,{start}\\,{end})")
        for element in scene.elements:
            if element.type in {"title", "method", "math_step", "answer", "warning", "summary", "cta", "problem", "text", "rate", "formula"}:
                filters.append(_drawtext(element, fontfile))
            elif element.type == "tank":
                enable = f":enable=between(t\\,{element.start:g}\\,{element.end:g})"
                filters.append(f"drawbox=x=300:y=620:w=480:h=260:color=0x60A5FA@0.25:t=10{enable}")
                filters.append(f"drawbox=x=300:y=700:w=480:h=180:color=0x60A5FA@0.55:t=fill{enable}")
                filters.append(f"drawtext=text=满池水\\ =\\ 1:fontsize=54:fontcolor=0x111827:x=(w-text_w)/2:y=835{enable}")
            elif element.type == "shape":
                enable = f":enable=between(t\\,{element.start:g}\\,{element.end:g})"
                filters.append(f"drawbox=x=250:y=500:w=580:h=320:color=0xDBEAFE@0.7:t=fill{enable}")
                filters.append(f"drawbox=x=250:y=500:w=580:h=320:color=0x2563EB@1:t=8{enable}")
                filters.append(f"drawtext=text=长方形:fontsize=52:fontcolor=0x111827:x=(w-text_w)/2:y=610{enable}")
            elif element.type == "fraction_bar":
                enable = f":enable=between(t\\,{element.start:g}\\,{element.end:g})"
                filters.append(f"drawbox=x=190:y=560:w=700:h=180:color=0xE5E7EB@1:t=fill{enable}")
                filters.append(f"drawbox=x=190:y=560:w=350:h=180:color=0x60A5FA@0.75:t=fill{enable}")
                filters.append(f"drawbox=x=190:y=560:w=700:h=180:color=0x111827@1:t=8{enable}")
            elif element.type == "relation":
                enable = f":enable=between(t\\,{element.start:g}\\,{element.end:g})"
                filters.append(f"drawbox=x=150:y=1077:w=780:h=6:color=0x64748B@1:t=fill{enable}")
                filters.append(f"drawbox=x=537:y=980:w=6:h=200:color=0x64748B@1:t=fill{enable}")
                filters.append(f"drawtext=text={_escape_text(element.text or '')}:fontsize=42:fontcolor=0x111827:x=(w-text_w)/2:y=1250{enable}")
    subtitle_path = str(subtitle_file).replace("\\", "/").replace(":", "\\:")
    filters.append("subtitles=" + subtitle_path + ":force_style='FontName=Microsoft YaHei,FontSize=20,PrimaryColour=&H00111111&,OutlineColour=&H00FFFFFF&,Outline=2,Alignment=2,MarginV=150'")
    return ",".join(filters)

def render_mp4(document: VideoDocument, output_path: str = "output/math_video.mp4", audio_segments: list[AudioSegment] | None = None) -> str:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("未检测到 FFmpeg，请先安装 FFmpeg 并加入 PATH")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    subtitle_file = _subtitle_file(document, output)
    vf = _visual_filter(document, subtitle_file)
    command = [ffmpeg, "-y", "-f", "lavfi", "-i", f"color=c=0xF3F4F6:s={document.width}x{document.height}:r={document.fps}:d={document.duration}"]
    valid_audio = [s for s in (audio_segments or []) if s.audio_path and Path(s.audio_path).exists()]
    if valid_audio:
        for segment in valid_audio:
            command += ["-i", segment.audio_path]
        filters, mix_inputs = [], []
        for i, segment in enumerate(valid_audio):
            delay_ms = max(0, int(round(segment.start * 1000)))
            filters.append(f"[{i + 1}:a]adelay={delay_ms}:all=1[a{i}]")
            mix_inputs.append(f"[a{i}]")
        filters.append("".join(mix_inputs) + f"amix=inputs={len(valid_audio)}:duration=longest:dropout_transition=0,atrim=duration={document.duration},asetpts=N/SR/TB[aout]")
        command += ["-filter_complex", ";".join(filters), "-map", "0:v", "-map", "[aout]", "-vf", vf, "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-shortest", str(output)]
    else:
        command += ["-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(output)]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "")[-4000:]
        raise RuntimeError(f"FFmpeg 渲染失败：\n{detail}") from exc
    return str(output)
