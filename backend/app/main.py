import shutil

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.init_db import init_db
from app.core.storage import ensure_bucket
from app.routers import (
    analytics,
    annotations,
    auth,
    chat,
    courses,
    events,
    export,
    flashcards,
    lms,
    notes,
    quizzes,
    slides,
    teams,
    transcript,
    videos,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    ensure_bucket()
    yield


app = FastAPI(title="Lecture Copilot API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(videos.router)
app.include_router(chat.router)
app.include_router(notes.router)
app.include_router(flashcards.router)
app.include_router(transcript.router)
app.include_router(courses.router)
app.include_router(teams.router)
app.include_router(annotations.router)
app.include_router(quizzes.router)
app.include_router(export.router)
app.include_router(events.router)
app.include_router(analytics.router)
app.include_router(lms.router)
app.include_router(slides.router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "ffmpeg": shutil.which("ffmpeg") is not None,
        "ffprobe": shutil.which("ffprobe") is not None,
        "features": [
            "auth",
            "courses",
            "teams",
            "hybrid_search",
            "quizzes",
            "annotations",
            "export",
            "sse",
            "slides",
            "analytics",
            "lms",
            "translation",
        ],
    }
