from scripts.generate_video import generate_video
from tts.models import AudioSegment, TTSBatchResult


def test_generate_video_orchestration(monkeypatch, tmp_path):
    def fake_tts(document, config, output_dir):
        segments = []
        cursor = 0.0
        for index, cue in enumerate(document.visual_cues):
            end = cursor + 1.0
            segments.append(
                AudioSegment(
                    text=cue["narration"],
                    start=cursor,
                    end=end,
                    segment_id=cue["segment_id"],
                    audio_path=str(tmp_path / f"step{index + 1}.wav"),
                )
            )
            cursor = end
        return TTSBatchResult(segments=segments, output_dir=output_dir)

    def fake_render(document, output_path, audio_segments=None):
        assert audio_segments
        return output_path

    monkeypatch.setattr("scripts.generate_video.synthesize_voice_timeline", fake_tts)
    monkeypatch.setattr("scripts.generate_video.render_mp4", fake_render)

    result = generate_video("36 ÷ 6", str(tmp_path))
    assert result["solution"]["answer"] == "6"
    assert result["solution"]["verified"] is True
    assert result["resolution"] == "1080x1920"
