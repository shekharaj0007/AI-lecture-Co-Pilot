"""Scene/chapter detection from sampled video frames."""

from pathlib import Path

import cv2
import numpy as np

from app.core.config import settings


def detect_scenes(video_path: Path, duration: float) -> list[dict]:
    """Detect scene boundaries using frame histogram similarity (fast, no GPU)."""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return _fallback_chapters(duration)

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    sample_every = max(1, int(fps / settings.frame_sample_fps))

    cuts: list[float] = [0.0]
    prev_hist = None
    frame_idx = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        if frame_idx % sample_every != 0:
            frame_idx += 1
            continue

        timestamp = frame_idx / fps
        small = cv2.resize(frame, (160, 90))
        hist = cv2.calcHist([small], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        hist = cv2.normalize(hist, hist).flatten()

        if prev_hist is not None:
            similarity = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
            if similarity < settings.scene_threshold and timestamp - cuts[-1] > 15:
                cuts.append(timestamp)

        prev_hist = hist
        frame_idx += 1

    cap.release()

    if len(cuts) == 1:
        return _fallback_chapters(duration)

    cuts.append(duration)
    chapters = []
    for i in range(len(cuts) - 1):
        chapters.append(
            {
                "start": cuts[i],
                "end": cuts[i + 1],
                "title": f"Scene {i + 1}",
            }
        )
    return chapters


def _fallback_chapters(duration: float) -> list[dict]:
    chapter_count = max(1, int(duration // 600) + 1)
    window = duration / chapter_count
    return [
        {
            "start": i * window,
            "end": min((i + 1) * window, duration),
            "title": f"Chapter {i + 1}",
        }
        for i in range(chapter_count)
    ]


def describe_frame(frame_path: Path) -> str:
    """Lightweight visual summary: brightness + edge density as a proxy for slides vs talking head."""
    image = cv2.imread(str(frame_path))
    if image is None:
        return ""

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brightness = float(np.mean(gray))
    edges = cv2.Canny(gray, 80, 160)
    edge_density = float(np.mean(edges > 0))

    if edge_density > 0.08 and brightness > 120:
        return "slide or whiteboard with text"
    if edge_density > 0.05:
        return "diagram or written content on screen"
    return "speaker or general scene"
