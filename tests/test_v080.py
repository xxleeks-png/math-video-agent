import shutil
import pytest
from math_engine.solver import solve
from video.ffmpeg_renderer import render_mp4
from video.storyboard import build_storyboard

@pytest.mark.skipif(shutil.which('ffmpeg') is None, reason='FFmpeg not installed')
def test_render_mp4(tmp_path):
    document = build_storyboard(solve('36 ÷ 6'))
    output = render_mp4(document, str(tmp_path / 'math_video.mp4'))
    assert output.endswith('.mp4')
    assert (tmp_path / 'math_video.mp4').exists()