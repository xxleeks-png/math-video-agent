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
    alpha = ""
    if element.start is not None and element.end is not None:
        start = element.start
        end = element.end
        enable = f":enable=between(t\\,{start:g}\\,{end:g})"
        duration = max(end - start, 0.1)
        # enter: quick fade/scale-in, focus: stable, resolve: slight fade-out.
        phase = element.action_phase or "auto"
        if phase == "enter":
            progress = f"clip((t-{start:g})/{min(duration * 0.25, 0.35):g}\\,0\\,1)"
            alpha = f":alpha={progress}"
        elif phase == "resolve":
            fade_start = start + duration * 0.75
            progress = f"1-0.35*clip((t-{fade_start:g})/{max(duration * 0.25, 0.1):g}\\,0\\,1)"
            alpha = f":alpha={progress}"
        elif phase == "auto":
            progress = f"clip((t-{start:g})/{min(duration * 0.25, 0.35):g}\\,0\\,1)"
            alpha = f":alpha={progress}"
    font = f":fontfile={_escape_filter_path(fontfile)}" if fontfile else ""
    return f"drawtext=textfile={path}:fontsize={size}:fontcolor={color}:x={x}:y={y}:{box}:shadowx=2:shadowy=2{font}{alpha}{enable}"

def _phase_windows(element) -> tuple[str, str, str]:
    """Return FFmpeg enable expressions for enter/focus/resolve."""
    start = element.start if element.start is not None else 0.0
    end = element.end if element.end is not None else start + 1.0
    duration = max(end - start, 0.1)
    enter_end = start + min(duration * 0.25, 0.35)
    resolve_start = start + duration * 0.75
    enter = f":enable=between(t\\,{start:g}\\,{enter_end:g})"
    focus = f":enable=between(t\\,{enter_end:g}\\,{resolve_start:g})"
    resolve = f":enable=between(t\\,{resolve_start:g}\\,{end:g})"
    return enter, focus, resolve


def _phase_enable(element, phase: str) -> str:
    if element.action_phase and element.action_phase not in {"auto", "hold"}:
        return f":enable=between(t\\,{element.start:g}\\,{element.end:g})"
    enter, focus, resolve = _phase_windows(element)
    return {"enter": enter, "focus": focus, "resolve": resolve}.get(phase, f":enable=between(t\\,{element.start:g}\\,{element.end:g})")


def _semantic_motion_filters(element, fontfile: str | None, output: Path, text_index: int) -> list[str]:
    """Render meaning-bearing motion for semantic math elements."""
    if element.start is None or element.end is None:
        return []
    key = element.semantic_key or ""
    filters: list[str] = []
    enter = _phase_enable(element, "enter")
    focus = _phase_enable(element, "focus")
    resolve = _phase_enable(element, "resolve")
    start = element.start
    end = element.end
    duration = max(end - start, 0.1)
    # FFmpeg filter expressions require commas to be escaped inside option values.
    progress = f"clip((t-{start:g})/{duration:g}\\,0\\,1)"

    if element.type == "tank":
        filters.append(f"drawbox=x=300:y=620:w=480:h=260:color=0x2563EB@0.9:t=10{enter}")
        fill_h = f"180*{progress}"
        fill_y = f"880-({fill_h})"
        filters.append(f"drawbox=x=300:y={fill_y}:w=480:h={fill_h}:color=0x60A5FA@0.58:t=fill{focus}")
        filters.append(f"drawbox=x=300:y=620:w=480:h=260:color=0x2563EB@1:t=14{resolve}")
    elif element.type == "rate":
        side = 180 if element.x < 0.5 else 650
        direction = 1 if element.x < 0.5 else -1
        # A moving line plus three arrow-head blocks makes flow direction explicit.
        travel = f"140*{progress}"
        if direction > 0:
            line_x = f"{side}+{travel}"
            head_x = f"{side}+{travel}+120"
        else:
            line_x = f"{side}-{travel}"
            head_x = f"{side}-{travel}"
        filters.append(f"drawbox=x={line_x}:y=1068:w=120:h=10:color=0x2563EB@0.75:t=fill{focus}")
        if direction > 0:
            filters.append(f"drawbox=x={head_x}:y=1052:w=10:h=42:color=0x2563EB@1:t=fill{focus}")
        else:
            filters.append(f"drawbox=x={head_x}:y=1052:w=10:h=42:color=0x2563EB@1:t=fill{focus}")
        if key == "inlet":
            filters.append(f"drawbox=x=300:y=1015:w=16:h=55:color=0x2563EB@1:t=fill{enter}")
        elif key == "outlet":
            filters.append(f"drawbox=x=765:y=1015:w=16:h=55:color=0x2563EB@1:t=fill{enter}")
        elif key in {"net_rate", "effective_outflow"}:
            filters.append(f"drawbox=x=300:y=1030:w=480:h=70:color=0x2563EB@0.18:t=fill{resolve}")
    elif element.type == "fraction_bar":
        filters.append(f"drawbox=x=190:y=560:w=700:h=180:color=0x111827@1:t=8{enter}")
        fill_w = f"700*{progress}"
        filters.append(f"drawbox=x=190:y=560:w={fill_w}:h=180:color=0x60A5FA@0.75:t=fill{focus}")
        if key == "original":
            for i in range(1, 4):
                x = 190 + i * 175
                filters.append(f"drawbox=x={x}:y=560:w=4:h=180:color=0x94A3B8@1:t=fill{focus}")
        elif key == "result":
            filters.append(f"drawbox=x=190:y=550:w=700:h=200:color=0x2563EB@1:t=8{resolve}")
    elif element.type == "shape":
        filters.append(f"drawbox=x=250:y=500:w=580:h=320:color=0x2563EB@1:t=8{enter}")
        draw_w = f"580*{progress}"
        filters.append(f"drawbox=x=250:y=500:w={draw_w}:h=320:color=0xDBEAFE@0.72:t=fill{focus}")
        filters.append(f"drawbox=x=250:y=500:w=580:h=320:color=0x2563EB@1:t=14{resolve}")
    elif element.type == "dimension":
        if key == "length":
            filters.append(f"drawbox=x=250:y=455:w=580:h=8:color=0x2563EB@1:t=fill{focus}")
            filters.append(f"drawbox=x=250:y=440:w=8:h=38:color=0x2563EB@1:t=fill{enter}")
            filters.append(f"drawbox=x=822:y=440:w=8:h=38:color=0x2563EB@1:t=fill{resolve}")
        elif key == "width":
            filters.append(f"drawbox=x=220:y=500:w=8:h=320:color=0x2563EB@1:t=fill{focus}")
            filters.append(f"drawbox=x=205:y=500:w=38:h=8:color=0x2563EB@1:t=fill{enter}")
            filters.append(f"drawbox=x=205:y=812:w=38:h=8:color=0x2563EB@1:t=fill{resolve}")
    elif key in {"rain_rate"}:
        for x in (380, 540, 700):
            drop_y = f"420+180*{progress}"
            filters.append(f"drawbox=x={x}:y={drop_y}:w=10:h=34:color=0x60A5FA@0.9:t=fill{focus}")
    elif key in {"net_relation", "formula", "operation"}:
        filters.append(f"drawbox=x=160:y=1050:w=760:h=8:color=0x94A3B8@0.65:t=fill{enter}")
        filters.append(f"drawbox=x=500:y=1010:w=8:h=88:color=0x2563EB@0.85:t=fill{focus}")
        filters.append(f"drawbox=x=150:y=1040:w=780:h=28:color=0x2563EB@0.12:t=fill{resolve}")
    elif key in {"effective_outflow", "result"}:
        filters.append(f"drawbox=x=120:y=1180:w=840:h=12:color=0x2563EB@0.9:t=fill{focus}")
        filters.append(f"drawbox=x=110:y=1160:w=860:h=52:color=0x2563EB@0.14:t=fill{resolve}")
    return filters


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
                filters.extend(_semantic_motion_filters(element, fontfile, output, text_index))
                filters.append(_textfile_drawtext(element, output, fontfile, text_index))
                text_index += 1
            elif element.type == "math_step":
                filters.append(_textfile_drawtext(element, output, fontfile, text_index))
                text_index += 1
                enable = f":enable=between(t\\,{element.start:g}\\,{element.end:g})"
                # Staged underline gives each calculation step a visual focus.
                phase = element.action_phase or "hold"
                if phase == "focus":
                    underline = enable
                elif phase == "enter":
                    underline = f":enable=between(t\\,{element.start:g}\\,{min(element.end or element.start, element.start + 0.35):g})"
                else:
                    underline = enable
                filters.append(
                    f"drawbox=x=210:y={int((element.y or 0.5)*1920 + 55)}:w=660:h=6:"
                    f"color=0x2563EB@0.9:t=fill{underline}"
                )
            elif element.type == "tank":
                filters.extend(_semantic_motion_filters(element, fontfile, output, text_index))
                enable = _phase_enable(element, "focus")
                filters.append(f"drawbox=x=300:y=620:w=480:h=260:color=0x60A5FA@0.25:t=10{enable}")
                duration = max((element.end or 1) - (element.start or 0), 0.1)
                height_expr = f"180*clip((t-{element.start:g})/{duration:g}\\,0\\,1)"
                y_expr = f"880-({height_expr})"
                filters.append(f"drawbox=x=300:y={y_expr}:w=480:h=180:color=0x60A5FA@0.55:t=fill{enable}")
                tank_path = _write_textfile(output, "tank", "满池水 = 1")
                font = f":fontfile={_escape_filter_path(fontfile)}" if fontfile else ""
                filters.append(f"drawtext=textfile={_escape_filter_path(str(tank_path))}:fontsize=54:fontcolor=0x111827:x=(w-text_w)/2:y=835{font}{enable}")
            elif element.type == "rate":
                filters.extend(_semantic_motion_filters(element, fontfile, output, text_index))
                enable = _phase_enable(element, "focus")
                side = 180 if element.x < 0.5 else 650
                direction = 1 if element.x < 0.5 else -1
                filters.append(f"drawbox=x={side}:y=1080:w=250:h=12:color=0x2563EB@0.85:t=fill{enable}")
                for offset in (0, 70, 140):
                    x_pos = side + offset if direction > 0 else side + 250 - offset - 22
                    filters.append(f"drawbox=x={x_pos}:y=1075:w=22:h=22:color=0x2563EB@1:t=fill{enable}")
                rate_path = _write_textfile(output, f"rate_{text_index}", element.text or "")
                font = f":fontfile={_escape_filter_path(fontfile)}" if fontfile else ""
                filters.append(
                    f"drawtext=textfile={_escape_filter_path(str(rate_path))}:fontsize=42:"
                    f"fontcolor=0x111827:x=(w-text_w)/2:y=1135{font}{enable}"
                )
                text_index += 1
            elif element.type == "mistake":
                enable = _phase_enable(element, "focus")
                filters.append(f"drawbox=x=110:y=1450:w=860:h=150:color=0xFEE2E2@0.96:t=fill{enable}")
                filters.append(f"drawbox=x=110:y=1450:w=860:h=150:color=0xB91C1C@1:t=8{enable}")
                filters.append(_textfile_drawtext(element, output, fontfile, text_index))
                text_index += 1
            elif element.type == "correction":
                enable = _phase_enable(element, "focus")
                filters.append(f"drawbox=x=100:y=1280:w=880:h=180:color=0xDBEAFE@0.96:t=fill{enable}")
                filters.append(f"drawbox=x=100:y=1280:w=880:h=180:color=0x2563EB@1:t=8{enable}")
                filters.append(_textfile_drawtext(element, output, fontfile, text_index))
                text_index += 1
            elif element.type == "method":
                filters.append(_textfile_drawtext(element, output, fontfile, text_index))
                text_index += 1
            elif element.type == "dimension":
                filters.extend(_semantic_motion_filters(element, fontfile, output, text_index))
                enable = _phase_enable(element, "focus")
                label = element.text or "长度"
                label_path = _write_textfile(output, f"dimension_{element.start:g}", label)
                font = f":fontfile={_escape_filter_path(fontfile)}" if fontfile else ""
                filters.append(f"drawtext=textfile={_escape_filter_path(str(label_path))}:fontsize=42:fontcolor=0x111827:x=820:y=650{font}{enable}")
            elif element.type == "shape":
                filters.extend(_semantic_motion_filters(element, fontfile, output, text_index))
                enable = _phase_enable(element, "focus")
                filters.append(f"drawbox=x=250:y=500:w=580:h=320:color=0xDBEAFE@0.7:t=fill{enable}")
                filters.append(f"drawbox=x=250:y=500:w=580:h=320:color=0x2563EB@1:t=8{enable}")
                shape_path = _write_textfile(output, "shape", "长方形")
                font = f":fontfile={_escape_filter_path(fontfile)}" if fontfile else ""
                filters.append(f"drawtext=textfile={_escape_filter_path(str(shape_path))}:fontsize=52:fontcolor=0x111827:x=(w-text_w)/2:y=610{font}{enable}")
            elif element.type == "fraction_bar":
                filters.extend(_semantic_motion_filters(element, fontfile, output, text_index))
                enable = _phase_enable(element, "focus")
                duration = max((element.end or 1) - (element.start or 0), 0.1)
                fill_expr = f"350*clip((t-{element.start:g})/{duration:g}\\,0\\,1)"
                filters.append(f"drawbox=x=190:y=560:w=700:h=180:color=0xE5E7EB@1:t=fill{enable}")
                filters.append(f"drawbox=x=190:y=560:w={fill_expr}:h=180:color=0x60A5FA@0.75:t=fill{enable}")
                filters.append(f"drawbox=x=190:y=560:w=700:h=180:color=0x111827@1:t=8{enable}")
                label = element.text or "单位“1”"
                label_path = _write_textfile(output, f"fraction_{element.start:g}", label)
                font = f":fontfile={_escape_filter_path(fontfile)}" if fontfile else ""
                filters.append(f"drawtext=textfile={_escape_filter_path(str(label_path))}:fontsize=44:fontcolor=0x111827:x=(w-text_w)/2:y=770{font}{enable}")
            elif element.type == "relation":
                filters.extend(_semantic_motion_filters(element, fontfile, output, text_index))
                enable = _phase_enable(element, "focus")
                filters.append(f"drawbox=x=150:y=1077:w=780:h=6:color=0x64748B@1:t=fill{enable}")
                filters.append(f"drawbox=x=537:y=980:w=6:h=200:color=0x64748B@1:t=fill{enable}")
                relation_path = _write_textfile(output, f"relation_{text_index}", element.text or "")
                font = f":fontfile={_escape_filter_path(fontfile)}" if fontfile else ""
                filters.append(f"drawtext=textfile={_escape_filter_path(str(relation_path))}:fontsize=42:fontcolor=0x111827:x=(w-text_w)/2:y=1250{font}{enable}")
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
