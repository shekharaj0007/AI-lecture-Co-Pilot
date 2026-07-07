"""Simple speaker labeling when full diarization isn't configured."""


def assign_speakers(segments: list[dict]) -> list[dict]:
    """Heuristic: group consecutive segments; alternate label on long pauses."""
    if not segments:
        return segments

    labeled = []
    speaker_idx = 0
    prev_end = 0.0

    for segment in segments:
        gap = segment["start"] - prev_end
        if gap > 3.0 and labeled:
            speaker_idx = 1 - speaker_idx
        labeled.append({**segment, "speaker": f"Speaker {speaker_idx + 1}"})
        prev_end = segment["end"]

    return labeled
