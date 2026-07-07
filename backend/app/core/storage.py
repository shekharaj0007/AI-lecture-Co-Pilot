import shutil
from pathlib import Path
from typing import BinaryIO, Iterator

import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException

from app.core.config import settings


def _local_path(key: str) -> Path:
    return settings.uploads_dir / key.replace("/", "_")


def save_upload(key: str, file_obj: BinaryIO) -> str:
    if settings.storage_backend == "local":
        dest = _local_path(key)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as out:
            shutil.copyfileobj(file_obj, out)
        return key

    s3 = get_s3_client()
    s3.upload_fileobj(file_obj, settings.s3_bucket, key)
    return key


def save_file_from_path(key: str, source: Path) -> str:
    if settings.storage_backend == "local":
        dest = _local_path(key)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        return key

    s3 = get_s3_client()
    s3.upload_file(source, settings.s3_bucket, key)
    return key


def download_to_path(key: str, dest: Path) -> Path:
    if settings.storage_backend == "local":
        src = _local_path(key)
        if not src.exists():
            raise FileNotFoundError(f"Missing local file: {src}")
        shutil.copy2(src, dest)
        return dest

    s3 = get_s3_client()
    s3.download_file(settings.s3_bucket, key, str(dest))
    return dest


def open_stream(key: str) -> tuple[Iterator[bytes], str]:
    if settings.storage_backend == "local":
        path = _local_path(key)
        if not path.exists():
            raise HTTPException(status_code=404, detail="Video file not found")

        def _iter_file() -> Iterator[bytes]:
            with open(path, "rb") as handle:
                while chunk := handle.read(1024 * 1024):
                    yield chunk

        suffix = path.suffix.lower()
        media = "video/mp4" if suffix == ".mp4" else "application/octet-stream"
        return _iter_file(), media

    s3 = get_s3_client()
    try:
        obj = s3.get_object(Bucket=settings.s3_bucket, Key=key)
    except ClientError as exc:
        raise HTTPException(status_code=404, detail="Video file not found") from exc

    return obj["Body"].iter_chunks(), obj.get("ContentType", "video/mp4")


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url or None,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
    )


def ensure_bucket() -> None:
    if settings.storage_backend == "local":
        settings.uploads_dir.mkdir(parents=True, exist_ok=True)
        settings.frames_dir.mkdir(parents=True, exist_ok=True)
        return

    s3 = get_s3_client()
    try:
        s3.head_bucket(Bucket=settings.s3_bucket)
    except ClientError:
        s3.create_bucket(Bucket=settings.s3_bucket)
