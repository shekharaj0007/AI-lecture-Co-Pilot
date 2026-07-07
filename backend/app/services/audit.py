"""Audit logging for compliance."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import AuditLog


async def log_action(
    db: AsyncSession,
    user_id: str | None,
    action: str,
    resource_type: str,
    resource_id: str,
    details: str = "",
) -> None:
    db.add(
        AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
        )
    )
    await db.commit()
