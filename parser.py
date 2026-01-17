import srt
from dataclasses import dataclass
from typing import List
from datetime import timedelta

@dataclass
class SubtitleSegment:
    index: int
    start_time: float  # Seconds
    end_time: float    # Seconds
    text: str

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time

def parse_srt(file_path: str) -> List[SubtitleSegment]:
    """
    Parses an SRT file and returns a list of SubtitleSegment objects.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    subs = list(srt.parse(content))
    segments = []

    for sub in subs:
        if not sub.content.strip():
            continue
            
        start = sub.start.total_seconds()
        end = sub.end.total_seconds()
        
        # basic validation
        if end <= start:
            # Skip invalid timestamps or zero duration
            continue

        segments.append(SubtitleSegment(
            index=sub.index,
            start_time=start,
            end_time=end,
            text=sub.content.strip()
        ))

    return segments
