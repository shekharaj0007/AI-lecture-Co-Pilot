from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, get_optional_user
from app.core.db import get_db
from app.models.db_models import Course, CourseVideo, User, Video
from app.models.schemas import CourseCreate, CourseOut, CourseVideoAdd
from app.services.audit import log_action

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("", response_model=CourseOut)
async def create_course(
    body: CourseCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    course = Course(owner_id=user.id, name=body.name, description=body.description)
    db.add(course)
    await db.commit()
    await db.refresh(course)
    await log_action(db, user.id, "create", "course", course.id)
    return CourseOut(id=course.id, name=course.name, description=course.description, video_count=0)


@router.get("", response_model=list[CourseOut])
async def list_courses(
    user: User | None = Depends(get_optional_user),
    owner_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    uid = user.id if user else owner_id
    if not uid:
        return []
    result = await db.execute(select(Course).where(Course.owner_id == uid))
    courses = result.scalars().all()
    out = []
    for course in courses:
        count = await db.scalar(
            select(func.count()).select_from(CourseVideo).where(CourseVideo.course_id == course.id)
        )
        out.append(
            CourseOut(
                id=course.id,
                name=course.name,
                description=course.description,
                video_count=count or 0,
            )
        )
    return out


@router.get("/{course_id}", response_model=CourseOut)
async def get_course(course_id: str, db: AsyncSession = Depends(get_db)):
    course = await db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    count = await db.scalar(
        select(func.count()).select_from(CourseVideo).where(CourseVideo.course_id == course_id)
    )
    return CourseOut(
        id=course.id,
        name=course.name,
        description=course.description,
        video_count=count or 0,
    )


@router.get("/{course_id}/videos", response_model=list[dict])
async def list_course_videos(course_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Video)
        .join(CourseVideo, CourseVideo.video_id == Video.id)
        .where(CourseVideo.course_id == course_id)
    )
    videos = result.scalars().all()
    return [
        {
            "id": v.id,
            "title": v.title,
            "status": v.status,
            "duration_seconds": v.duration_seconds,
        }
        for v in videos
    ]


@router.post("/{course_id}/videos")
async def add_video_to_course(
    course_id: str,
    body: CourseVideoAdd,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    course = await db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    video = await db.get(Video, body.video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    existing = await db.execute(
        select(CourseVideo).where(
            CourseVideo.course_id == course_id,
            CourseVideo.video_id == body.video_id,
        )
    )
    if existing.scalar_one_or_none():
        return {"ok": True}
    db.add(CourseVideo(course_id=course_id, video_id=body.video_id))
    await db.commit()
    await log_action(db, user.id, "add_video", "course", course_id, body.video_id)
    return {"ok": True}


@router.delete("/{course_id}/videos/{video_id}")
async def remove_video_from_course(
    course_id: str,
    video_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CourseVideo).where(
            CourseVideo.course_id == course_id,
            CourseVideo.video_id == video_id,
        )
    )
    link = result.scalar_one_or_none()
    if link:
        await db.delete(link)
        await db.commit()
    await log_action(db, user.id, "remove_video", "course", course_id, video_id)
    return {"ok": True}
