from typing import List
from tts.models import AudioSegment


def segments_to_subtitles(segments: List[AudioSegment]) -> List[dict]:
    subtitles = []
    for segment in segments:
        subtitles.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text,
        })
    return subtitles


def subtitles_to_srt(subtitles: List[dict]) -> str:
    def stamp(seconds: float) -> str:
        ms = int(round(seconds * 1000))
        h, ms = divmod(ms, 3600000)
        m, ms = divmod(ms, 60000)
        s, ms = divmod(ms, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    blocks = []
    for i, item in enumerate(subtitles, 1):
        blocks.append(
            f"{i}\n{stamp(item['start'])} --> {stamp(item['end'])}\n{item['text']}\n"
        )
    return "\n".join(blocks)
