from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Sequence
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Artifact, Event, Project, Task


async def get_project(session: AsyncSession, project_id: UUID) -> Optional[Project]:
    result = await session.execute(select(Project).where(Project.id == project_id))
    return result.scalar_one_or_none()


async def list_projects(session: AsyncSession) -> Sequence[Project]:
    result = await session.execute(select(Project))
    return result.scalars().all()


async def record_event(
    session: AsyncSession,
    project_id: UUID,
    message: str,
    *,
    agent: Optional[str] = None,
    level: str = "info",
    data: Optional[Dict[str, Any]] = None,
) -> Event:
    event = Event(
        project_id=project_id,
        agent=agent,
        level=level,
        message=message,
        data=data or {},
    )
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event


async def upsert_task(
    session: AsyncSession,
    *,
    project_id: UUID,
    task_id: UUID,
    name: str,
    agent: str,
    status: str,
    parallel_group: Optional[str],
    payload: Dict[str, Any],
) -> Task:
    result = await session.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if task:
        task.status = status
        task.payload = payload
        await session.commit()
        await session.refresh(task)
        return task
    task = Task(
        id=task_id,
        project_id=project_id,
        name=name,
        agent=agent,
        status=status,
        parallel_group=parallel_group,
        payload=payload,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def list_tasks(session: AsyncSession, project_id: UUID) -> List[Task]:
    result = await session.execute(select(Task).where(Task.project_id == project_id))
    return list(result.scalars().all())


async def add_artifacts(
    session: AsyncSession, project_id: UUID, paths: Iterable[str], sizes: Iterable[int]
) -> None:
    for path, size in zip(paths, sizes):
        artifact = Artifact(project_id=project_id, path=path, size_bytes=size)
        session.add(artifact)
    await session.commit()


async def list_artifacts(session: AsyncSession, project_id: UUID) -> List[Artifact]:
    result = await session.execute(
        select(Artifact).where(Artifact.project_id == project_id)
    )
    return list(result.scalars().all())


async def update_project_status(
    session: AsyncSession, project_id: UUID, status: str
) -> Project:
    await session.execute(
        update(Project).where(Project.id == project_id).values(status=status)
    )
    await session.commit()
    result = await session.execute(select(Project).where(Project.id == project_id))
    return result.scalar_one()

