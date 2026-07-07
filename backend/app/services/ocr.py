"""OCR for slide/whiteboard text. Uses pytesseract when available."""

from pathlib import Path

import cv2


def ocr_frame(frame_path: Path) -> str:
    if not frame_path.exists():
        return ""

    image = cv2.imread(str(frame_path))
    if image is None:
        return ""

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    try:
        import pytesseract

        text = pytesseract.image_to_string(gray, config="--psm 6")
        return " ".join(text.split())
    except Exception:
        return _opencv_text_hint(gray)


def ocr_for_chapters(video_path: Path, chapters: list[dict], video_id: str) -> list[dict]:
    from app.core.config import settings
    from app.services.video_media import extract_frame_at

    results: list[dict] = []
    frames_root = settings.frames_dir / video_id
    frames_root.mkdir(parents=True, exist_ok=True)

    for chapter in chapters:
        midpoint = (chapter["start"] + chapter["end"]) / 2
        frame_path = frames_root / f"scene_{int(midpoint)}.jpg"
        extract_frame_at(video_path, midpoint, frame_path)
        text = ocr_frame(frame_path)
        if text:
            results.append({"start": chapter["start"], "text": text, "end": chapter["end"]})
    return results


def _opencv_text_hint(gray) -> str:
    """Fallback when Tesseract isn't installed: detect high-contrast text regions."""
    edges = cv2.Canny(gray, 50, 150)
    ratio = float((edges > 0).sum()) / edges.size
    if ratio > 0.04:
        return "[on-screen text detected — install Tesseract for full OCR]"
    return ""
