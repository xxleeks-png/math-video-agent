from math_engine.solver import solve
from video.storyboard import build_storyboard
from video.voice_timeline import build_voice_timeline
from video.subtitles import segments_to_subtitles, subtitles_to_srt


def test_voice_timeline():
    document = build_storyboard(solve("36 ÷ 6"))
    segments = build_voice_timeline(document)
    assert len(segments) == 4
    assert segments[0].start == 0
    assert segments[-1].end == 40


def test_srt_generation():
    document = build_storyboard(solve("27 + 15"))
    segments = build_voice_timeline(document)
    srt = subtitles_to_srt(segments_to_subtitles(segments))
    assert "00:00:00,000 --> 00:00:04,000" in srt
    assert "这道题的关键" in srt
