import json

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.models.db_models import AuditLog, LmsConnection, User
from app.models.schemas import LmsConnectRequest
from app.services.audit import log_action

router = APIRouter(prefix="/lms", tags=["lms"])

PROVIDERS = [
    {
        "id": "canvas",
        "name": "Canvas LMS",
        "description": "Sync courses and assignments from Instructure Canvas.",
    },
    {
        "id": "moodle",
        "name": "Moodle",
        "description": "Import Moodle courses and lecture recordings.",
    },
    {
        "id": "google_classroom",
        "name": "Google Classroom",
        "description": "Connect Google Classroom for shared lecture libraries.",
    },
]


@router.get("/providers")
async def list_providers():
    return PROVIDERS


@router.post("/connect")
async def connect_lms(
    body: LmsConnectRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conn = LmsConnection(
        user_id=user.id,
        provider=body.provider,
        config_json=json.dumps({"api_url": body.api_url, "api_key": "***"}),
    )
    db.add(conn)
    await db.commit()
    await log_action(db, user.id, "connect", "lms", body.provider)
    return {"ok": True, "provider": body.provider, "status": "connected"}


@router.get("/audit")
async def audit_logs(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AuditLog).where(AuditLog.user_id == user.id).order_by(AuditLog.created_at.desc()).limit(50)
    )
    logs = result.scalars().all()
    return [
        {
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "details": log.details,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]


@router.post("/webhook/{provider}")
async def lms_webhook(provider: str, payload: dict):
    return {"ok": True, "provider": provider, "received": True}
