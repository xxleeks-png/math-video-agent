from scripts.generate_video import generate_video
from tts.models import AudioSegment, TTSBatchResult


def test_generate_video_orchestration(monkeypatch, tmp_path):
    def fake_tts(document, config, output_dir):
        return TTSBatchResult(
            segments=[
                AudioSegment(
                    text=document.scenes[0].narration,
                    start=0,
                    end=4,
                    segment_id="step1",
                    audio_path=str(tmp_path / "step1.wav"),
                )
            ],
            output_dir=output_dir,
        )

    def fake_render(document, output_path, audio_segments=None):
        assert audio_segments
        return output_path

    monkeypatch.setattr("scripts.generate_video.synthesize_voice_timeline", fake_tts)
    monkeypatch.setattr("scripts.generate_video.render_mp4", fake_render)

    result = generate_video("36 ÷ 6", str(tmp_path))
    assert result["solution"]["answer"] == "6"
    assert result["solution"]["verified"] is True
    assert result["resolution"] == "1080x1920"
