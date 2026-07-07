from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.models.db_models import Team, TeamCourse, TeamMember, User
from app.models.schemas import TeamCreate, TeamMemberAdd, TeamOut
from app.services.audit import log_action

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("", response_model=TeamOut)
async def create_team(
    body: TeamCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    team = Team(name=body.name, owner_id=user.id)
    db.add(team)
    await db.flush()
    db.add(TeamMember(team_id=team.id, user_id=user.id, role="owner"))
    await db.commit()
    await db.refresh(team)
    await log_action(db, user.id, "create", "team", team.id)
    return TeamOut(id=team.id, name=team.name, member_count=1)


@router.get("", response_model=list[TeamOut])
async def list_teams(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Team)
        .join(TeamMember, TeamMember.team_id == Team.id)
        .where(TeamMember.user_id == user.id)
    )
    teams = result.scalars().unique().all()
    out = []
    for team in teams:
        count = await db.scalar(
            select(func.count()).select_from(TeamMember).where(TeamMember.team_id == team.id)
        )
        out.append(TeamOut(id=team.id, name=team.name, member_count=count or 0))
    return out


@router.post("/{team_id}/members")
async def add_team_member(
    team_id: str,
    body: TeamMemberAdd,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    team = await db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    result = await db.execute(select(User).where(User.email == body.user_email.lower()))
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="User not found")
    db.add(TeamMember(team_id=team_id, user_id=member.id, role=body.role))
    await db.commit()
    await log_action(db, user.id, "add_member", "team", team_id, member.email)
    return {"ok": True}


@router.post("/{team_id}/courses/{course_id}")
async def link_course_to_team(
    team_id: str,
    course_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    db.add(TeamCourse(team_id=team_id, course_id=course_id))
    await db.commit()
    await log_action(db, user.id, "link_course", "team", team_id, course_id)
    return {"ok": True}
