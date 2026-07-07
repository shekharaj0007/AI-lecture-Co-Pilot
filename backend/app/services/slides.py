"""Extract slide-like frames from lecture video."""

import shutil
from pathlib import Path

import cv2
import numpy as np

from app.core.config import settings


def extract_slides(video_path: Path, video_id: str, chapters: list[dict]) -> list[dict]:
    """Save frames that look like slides (high brightness + edge density)."""
    slides_dir = settings.uploads_dir / "slides" / video_id
    slides_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return []

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    slides: list[dict] = []
    seen_hashes: set[str] = set()

    for chapter in chapters:
        timestamp = chapter["start"] + 2.0
        cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
        ok, frame = cap.read()
        if not ok:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = float(np.mean(gray))
        edges = cv2.Canny(gray, 80, 160)
        edge_density = float(np.mean(edges > 0))

        if not (edge_density > 0.06 and brightness > 100):
            continue

        small = cv2.resize(gray, (32, 18))
        frame_hash = str(int(np.sum(small)))
        if frame_hash in seen_hashes:
            continue
        seen_hashes.add(frame_hash)

        filename = f"slide_{int(timestamp)}.jpg"
        out_path = slides_dir / filename
        cv2.imwrite(str(out_path), frame)
        slides.append(
            {
                "start_seconds": timestamp,
                "title": chapter.get("title", f"Slide at {int(timestamp)}s"),
                "image_path": str(out_path.relative_to(settings.uploads_dir.parent)),
                "ocr_text": "",
            }
        )

    cap.release()
    return slides
