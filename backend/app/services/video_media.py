import subprocess
from pathlib import Path


class FFmpegNotFoundError(RuntimeError):
    pass


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, check=True)
    except FileNotFoundError as exc:
        raise FFmpegNotFoundError(
            "ffmpeg/ffprobe not found. Install from https://ffmpeg.org/download.html "
            "and add to PATH, then restart the terminal."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(exc.stderr or str(exc)) from exc


def probe_duration(path: Path) -> float:
    result = _run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ]
    )
    return float(result.stdout.strip())


def extract_audio(video_path: Path) -> Path:
    audio_path = video_path.with_suffix(".wav")
    _run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-vn",
            "-acodec",
            "pcm_s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            str(audio_path),
        ]
    )
    return audio_path


def extract_frame_at(video_path: Path, seconds: float, dest: Path) -> Path | None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        _run(
            [
                "ffmpeg",
                "-y",
                "-ss",
                str(max(0, seconds)),
                "-i",
                str(video_path),
                "-frames:v",
                "1",
                "-q:v",
                "2",
                str(dest),
            ]
        )
    except RuntimeError:
        return None
    return dest if dest.exists() else None
