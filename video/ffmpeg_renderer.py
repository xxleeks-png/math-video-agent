import shutil
import subprocess
from pathlib import Path

from .dsl import VideoDocument
from tts.models import AudioSegment
from .text_layout import prepare_display_text, cleanup_render_text_files

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

def _escape_filter_path(path: str) -> str:
    return path.replace("\\", "/").replace(":", "\\:")


def _write_textfile(output: Path, name: str, text: str) -> Path:
    path = output.parent / f".{output.stem}_{name}.txt"
    path.write_text(text, encoding="utf-8")
    return path


def _textfile_drawtext(element, output: Path, fontfile: str | None, index: int) -> str:
    display_text, size = prepare_display_text(element.text or element.value or "", max_chars=18)
    text_path = _write_textfile(output, f"text_{index}", display_text)
    path = _escape_filter_path(str(text_path))
    x = f"(w-text_w)*{element.x:.3f}"
    y = f"h*{element.y:.3f}-text_h/2"
    size = int(size * max(0.7, min(1.8, element.scale)))
    color = "white" if element.emphasis else "0x111827"
    box = "box=1:boxcolor=0xFFFFFF@0.92:boxborderw=18" if not element.emphasis else "box=1:boxcolor=0x111827@0.96:boxborderw=22"
    enable = ""
    if element.start is not None and element.end is not None:
        enable = f":enable=between(t\\,{element.start:g}\\,{element.end:g})"
    font = f":fontfile={fontfile}" if fontfile else ""
    return f"drawtext=textfile={path}:fontsize={size}:fontcolor={color}:x={x}:y={y}:{box}:shadowx=2:shadowy=2{font}{enable}"

def _font_file() -> str | None:
    candidates = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/msyh.ttf",
        "C:/Windows/Fonts/simhei.ttf",
    ]
    return next((p for p in candidates if Path(p).exists()), None)

def _drawtext(element, fontfile: str | None) -> str:
    raise RuntimeError("直接 drawtext 已弃用，请使用 _textfile_drawtext")


def _visual_filter(document: VideoDocument, output: Path, subtitle_file: Path) -> str:
    filters = ["format=yuv420p"]
    fontfile = _font_file()
    text_index = 0
    for scene in document.scenes:
        start, end = f"{scene.start:g}", f"{scene.end:g}"
        filters.append(f"drawbox=x=60:y=80:w=960:h=130:color=0x111827@0.96:t=fill:enable=between(t\\,{start}\\,{end})")
        filters.append(f"drawbox=x=60:y=230:w=960:h=5:color=0x2563EB@1:t=fill:enable=between(t\\,{start}\\,{end})")
        for element in scene.elements:
            if element.type in {"title", "method", "answer", "warning", "summary", "cta", "problem", "text", "formula"}:
                filters.append(_textfile_drawtext(element, output, fontfile, text_index))
                text_index += 1
            elif element.type == "math_step":
                filters.append(_textfile_drawtext(element, output, fontfile, text_index))
                text_index += 1
                enable = f":enable=between(t\\,{element.start:g}\\,{element.end:g})"
                # Staged underline gives each calculation step a visual focus.
                filters.append(
                    f"drawbox=x=210:y={int((element.y or 0.5)*1920 + 55)}:w=660:h=6:"
                    f"color=0x2563EB@0.9:t=fill{enable}"
                )
                filters.append(_textfile_drawtext(element, output, fontfile, text_index))
                text_index += 1
            elif element.type == "tank":
                enable = f":enable=between(t\\,{element.start:g}\\,{element.end:g})"
                filters.append(f"drawbox=x=300:y=620:w=480:h=260:color=0x60A5FA@0.25:t=10{enable}")
                duration = max((element.end or 1) - (element.start or 0), 0.1)
                height_expr = f"180*clip((t-{element.start:g})/{duration:g},0,1)"
                y_expr = f"880-({height_expr})"
                filters.append(f"drawbox=x=300:y={y_expr}:w=480:h=180:color=0x60A5FA@0.55:t=fill{enable}")
                tank_path = _write_textfile(output, "tank", "满池水 = 1")
                filters.append(f"drawtext=textfile={_escape_filter_path(str(tank_path))}:fontsize=54:fontcolor=0x111827:x=(w-text_w)/2:y=835{enable}")
            elif element.type == "rate":
                enable = f":enable=between(t\\,{element.start:g}\\,{element.end:g})"
                side = 180 if element.x < 0.5 else 650
                direction = 1 if element.x < 0.5 else -1
                filters.append(f"drawbox=x={side}:y=1080:w=250:h=12:color=0x2563EB@0.85:t=fill{enable}")
                for offset in (0, 70, 140):
                    x_pos = side + offset if direction > 0 else side + 250 - offset - 22
                    filters.append(f"drawbox=x={x_pos}:y=1075:w=22:h=22:color=0x2563EB@1:t=fill{enable}")
            elif element.type == "mistake":
                enable = f":enable=between(t\\,{element.start:g}\\,{element.end:g})"
                filters.append(f"drawbox=x=110:y=1450:w=860:h=150:color=0xFEE2E2@0.96:t=fill{enable}")
                filters.append(f"drawbox=x=110:y=1450:w=860:h=150:color=0xB91C1C@1:t=8{enable}")
                filters.append(_textfile_drawtext(element, output, fontfile, text_index))
                text_index += 1
            elif element.type == "correction":
                enable = f":enable=between(t\\,{element.start:g}\\,{element.end:g})"
                filters.append(f"drawbox=x=100:y=1280:w=880:h=180:color=0xDBEAFE@0.96:t=fill{enable}")
                filters.append(f"drawbox=x=100:y=1280:w=880:h=180:color=0x2563EB@1:t=8{enable}")
                filters.append(_textfile_drawtext(element, output, fontfile, text_index))
                text_index += 1
            elif element.type == "method":
                filters.append(_textfile_drawtext(element, output, fontfile, text_index))
                text_index += 1
            elif element.type == "dimension":
                enable = f":enable=between(t\\,{element.start:g}\\,{element.end:g})"
                label = element.text or "长度"
                label_path = _write_textfile(output, f"dimension_{element.start:g}", label)
                filters.append(f"drawtext=textfile={_escape_filter_path(str(label_path))}:fontsize=42:fontcolor=0x111827:x=820:y=650{enable}")
            elif element.type == "shape":
                enable = f":enable=between(t\\,{element.start:g}\\,{element.end:g})"
                filters.append(f"drawbox=x=250:y=500:w=580:h=320:color=0xDBEAFE@0.7:t=fill{enable}")
                filters.append(f"drawbox=x=250:y=500:w=580:h=320:color=0x2563EB@1:t=8{enable}")
                filters.append(f"drawtext=text=长方形:fontsize=52:fontcolor=0x111827:x=(w-text_w)/2:y=610{enable}")
            elif element.type == "fraction_bar":
                enable = f":enable=between(t\\,{element.start:g}\\,{element.end:g})"
                duration = max((element.end or 1) - (element.start or 0), 0.1)
                fill_expr = f"350*clip((t-{element.start:g})/{duration:g},0,1)"
                filters.append(f"drawbox=x=190:y=560:w=700:h=180:color=0xE5E7EB@1:t=fill{enable}")
                filters.append(f"drawbox=x=190:y=560:w={fill_expr}:h=180:color=0x60A5FA@0.75:t=fill{enable}")
                filters.append(f"drawbox=x=190:y=560:w=700:h=180:color=0x111827@1:t=8{enable}")
                label = element.text or "单位“1”"
                label_path = _write_textfile(output, f"fraction_{element.start:g}", label)
                filters.append(f"drawtext=textfile={_escape_filter_path(str(label_path))}:fontsize=44:fontcolor=0x111827:x=(w-text_w)/2:y=770{enable}")
            elif element.type == "relation":
                enable = f":enable=between(t\\,{element.start:g}\\,{element.end:g})"
                filters.append(f"drawbox=x=150:y=1077:w=780:h=6:color=0x64748B@1:t=fill{enable}")
                filters.append(f"drawbox=x=537:y=980:w=6:h=200:color=0x64748B@1:t=fill{enable}")
                relation_path = _write_textfile(output, f"relation_{text_index}", element.text or "")
                filters.append(f"drawtext=textfile={_escape_filter_path(str(relation_path))}:fontsize=42:fontcolor=0x111827:x=(w-text_w)/2:y=1250{enable}")
                text_index += 1
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
    vf = _visual_filter(document, output, subtitle_file)
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
    cleanup_render_text_files(output.parent)
    return str(output)
