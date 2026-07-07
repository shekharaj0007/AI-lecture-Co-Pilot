"""Download videos from URLs (YouTube, Vimeo, direct .mp4 links, etc.)."""

import re
import shutil
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, urlparse, urlunparse

import httpx


class VideoDownloadError(Exception):
    pass


def _safe_filename(title: str) -> str:
    cleaned = re.sub(r"[^\w\s\-().]", "", title).strip()
    return (cleaned[:80] or "lecture").replace(" ", "_")


def download_video_url(url: str) -> tuple[Path, str, Path]:
    """
    Download a video to a temp directory.
    Returns (video_path, title, temp_dir) — caller must clean up temp_dir.
    """
    url = url.strip()
    if not url:
        raise VideoDownloadError("URL is empty")

    url = _normalize_url(url)

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise VideoDownloadError("URL must start with http:// or https://")

    tmp = Path(tempfile.mkdtemp(prefix="lecture-import-"))

    if _is_direct_video_url(url):
        title, path = _download_direct(url, tmp)
        return path, title, tmp

    return _download_ytdlp(url, tmp)


def _normalize_url(url: str) -> str:
    """Keep only the video ID for YouTube watch URLs (ignore playlist params)."""
    parsed = urlparse(url)
    if parsed.netloc in ("www.youtube.com", "youtube.com", "m.youtube.com"):
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]
            if video_id:
                return f"https://www.youtube.com/watch?v={video_id}"
    return url


def _is_direct_video_url(url: str) -> bool:
    lower = url.lower().split("?")[0]
    return lower.endswith((".mp4", ".webm", ".mkv", ".mov", ".m4v"))


def _download_direct(url: str, tmp: Path) -> tuple[str, Path]:
    ext = Path(urlparse(url).path).suffix or ".mp4"
    dest = tmp / f"video{ext}"

    with httpx.stream("GET", url, follow_redirects=True, timeout=600) as response:
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if "text/html" in content_type and not _is_direct_video_url(url):
            raise VideoDownloadError("Link returned a web page, not a video file. Try a direct video URL or YouTube link.")

        with open(dest, "wb") as out:
            for chunk in response.iter_bytes(1024 * 1024):
                out.write(chunk)

    if dest.stat().st_size < 1024:
        raise VideoDownloadError("Downloaded file is too small — may not be a valid video.")

    title = Path(urlparse(url).path).stem or "Imported lecture"
    return title, dest


def _download_ytdlp(url: str, tmp: Path) -> tuple[Path, str, Path]:
    try:
        import yt_dlp
    except ImportError as exc:
        raise VideoDownloadError(
            "Install yt-dlp for YouTube and link imports: pip install yt-dlp"
        ) from exc

    outtmpl = str(tmp / "%(title).100s.%(ext)s")
    has_ffmpeg = shutil.which("ffmpeg") is not None

    # YouTube often splits video + audio; merging requires ffmpeg.
    if has_ffmpeg:
        format_str = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
    else:
        format_str = "best[ext=mp4][acodec!=none][vcodec!=none]/best[height<=720]/best"

    ydl_opts = {
        "format": format_str,
        "outtmpl": outtmpl,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }
    if has_ffmpeg:
        ydl_opts["merge_output_format"] = "mp4"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info is None:
                raise VideoDownloadError("Could not fetch video info from that link.")
            title = info.get("title") or "Imported lecture"
            prepared = Path(ydl.prepare_filename(info))
            if prepared.exists():
                return prepared, title, tmp
            # merged file may differ
            candidates = sorted(tmp.iterdir(), key=lambda p: p.stat().st_size, reverse=True)
            if not candidates:
                raise VideoDownloadError("Download finished but no video file was found.")
            return candidates[0], title, tmp
    except VideoDownloadError:
        raise
    except Exception as exc:
        msg = str(exc)
        if "ffmpeg" in msg.lower():
            raise VideoDownloadError(
                "ffmpeg is required for YouTube downloads. "
                "Install from https://ffmpeg.org/download.html and add to PATH, then restart the backend."
            ) from exc
        raise VideoDownloadError(f"Could not download video: {exc}") from exc
