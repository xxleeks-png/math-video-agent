import shutil
import subprocess
from pathlib import Path

from .dsl import VideoDocument

def render_mp4(document: VideoDocument, output_path: str = 'output/math_video.mp4') -> str:
    """Render a deterministic vertical MP4 from the Video DSL using FFmpeg."""
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        raise RuntimeError('未检测到 FFmpeg，请先安装 FFmpeg 并加入 PATH')
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    subtitle_file = output.with_suffix('.srt')
    def stamp(seconds: float) -> str:
        ms = int(round(seconds * 1000))
        h, ms = divmod(ms, 3600000)
        m, ms = divmod(ms, 60000)
        s, ms = divmod(ms, 1000)
        return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'
    blocks = []
    for i, scene in enumerate(document.scenes, 1):
        text = scene.subtitle or scene.narration
        blocks.append(f'{i}\n{stamp(scene.start)} --> {stamp(scene.end)}\n{text}\n')
    subtitle_file.write_text('\n'.join(blocks), encoding='utf-8')
    vf = "subtitles=" + str(subtitle_file).replace(':', '\\:') + ":force_style='FontSize=18,Alignment=2,MarginV=120'"
    command = [ffmpeg, '-y', '-f', 'lavfi', '-i', f'color=c=white:s={document.width}x{document.height}:r={document.fps}:d={document.duration}', '-vf', vf, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-an', str(output)]
    subprocess.run(command, check=True, capture_output=True, text=True)
    return str(output)