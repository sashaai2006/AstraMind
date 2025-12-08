from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import FileResponse, PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.agents.refactor import RefactorAgent
from backend.agents.reviewer import ReviewerAgent
from backend.core.orchestrator import orchestrator
from backend.core.ws_manager import ws_manager
from backend.memory import utils as db_utils
from backend.memory.db import get_session_dependency
from backend.memory.models import Project
from backend.memory.vector_store import get_project_memory, get_semantic_cache
from backend.memory.knowledge_sources import get_knowledge_registry, KnowledgeSource
from backend.settings import get_settings
from backend.utils import fileutils
from backend.utils.logging import get_logger
from backend.utils.schemas import (
    FileEntry,
    FileUpdate,
    ProjectCreate,
    ProjectStatusResponse,
)
from pydantic import BaseModel

router = APIRouter(prefix="/api/projects", tags=["projects"])
LOGGER = get_logger(__name__)
refactor_agent = RefactorAgent()
reviewer_agent = ReviewerAgent()


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = None


class DeepReviewRequest(BaseModel):
    """Request for deep code review."""
    paths: List[str]  # List of file paths to review


def _project_path(project_id: UUID) -> Path:
    settings = get_settings()
    return settings.projects_root / str(project_id)


@router.get("")
async def list_projects(
    session: AsyncSession = Depends(get_session_dependency),
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    search: Optional[str] = Query(default=None),
) -> dict:
    """List all projects with optional search and pagination."""
    from sqlalchemy import select, or_, func
    
    query = select(Project)
    
    # Search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                Project.title.ilike(search_pattern),
                Project.description.ilike(search_pattern),
            )
        )
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    result = await session.execute(count_query)
    total = result.scalar() or 0
    
    # Apply pagination and ordering
    query = query.order_by(Project.created_at.desc()).limit(limit).offset(offset)
    
    result = await session.execute(query)
    projects = result.scalars().all()
    
    return {
        "projects": [
            {
                "id": str(p.id),
                "title": p.title,
                "description": p.description,
                "target": p.target,
                "status": p.status,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in projects
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate, session: AsyncSession = Depends(get_session_dependency)
) -> dict:
    project = Project(
        title=payload.title,
        description=payload.description,
        target=payload.target,
        status="creating",
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)

    settings = get_settings()
    fileutils.ensure_project_dir(
        settings.projects_root,
        str(project.id),
        {
            "title": payload.title,
            "description": payload.description,
            "target": payload.target,
        },
    )

    await orchestrator.async_start(
        project.id, payload.title, payload.description, payload.target
    )

    return {"project_id": str(project.id), "status": "created"}


@router.delete("/{project_id}")
async def delete_project(
    project_id: UUID, session: AsyncSession = Depends(get_session_dependency)
) -> dict:
    """Delete a project and all its files."""
    import shutil
    
    # Get project from DB
    project = await db_utils.get_project(session, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Delete project directory
    project_path = _project_path(project_id)
    if project_path.exists():
        try:
            shutil.rmtree(project_path)
            LOGGER.info("Deleted project directory: %s", project_path)
        except Exception as e:
            LOGGER.error("Failed to delete project directory %s: %s", project_path, e)
    
    # Delete from database
    await session.delete(project)
    await session.commit()
    
    LOGGER.info("Deleted project %s from database", project_id)
    
    return {"success": True, "message": f"Project {project.title} deleted"}


@router.get("/{project_id}/status", response_model=ProjectStatusResponse)
async def get_status(
    project_id: UUID, session: AsyncSession = Depends(get_session_dependency)
) -> ProjectStatusResponse:
    project = await db_utils.get_project(session, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    tasks = await db_utils.list_tasks(session, project_id)
    artifacts = await db_utils.list_artifacts(session, project_id)
    return ProjectStatusResponse(
        project_id=str(project.id),
        status=project.status,  # type: ignore[arg-type]
        steps=[
            {
                "id": str(task.id),
                "name": task.name,
                "agent": task.agent,
                "status": task.status,
                "parallel_group": task.parallel_group,
                "payload": task.payload,
            }
            for task in tasks
        ],
        artifacts=[
            {
                "path": artifact.path,
                "size_bytes": artifact.size_bytes,
            }
            for artifact in artifacts
        ],
    )


@router.get("/{project_id}/files", response_model=List[FileEntry])
async def list_files(project_id: UUID) -> List[FileEntry]:
    project_path = _project_path(project_id)
    if not project_path.exists():
        raise HTTPException(status_code=404, detail="Project not found")
    return fileutils.iter_file_entries(project_path)


@router.get("/{project_id}/file")
async def read_file(
    project_id: UUID,
    path: str = Query(...),
    version: Optional[int] = Query(default=None),
) -> Response:
    project_path = _project_path(project_id)
    full_path = project_path / path
    try:
        data, is_text = fileutils.read_project_file(project_path, path)
    except FileNotFoundError as exc:  # noqa: BLE001
        raise HTTPException(status_code=404, detail="File not found") from exc
    if is_text:
        return PlainTextResponse(data.decode("utf-8"))
    return Response(
        content=data, media_type="application/octet-stream", headers={"X-File": path}
    )


@router.post("/{project_id}/chat")
async def chat_with_project(project_id: UUID, payload: ChatRequest) -> dict:
    """Chat with the RefactorAgent to modify the project."""
    response = await refactor_agent.chat(project_id, payload.message, payload.history)
    return {"response": response}


@router.post("/{project_id}/review")
async def deep_review(project_id: UUID, payload: DeepReviewRequest) -> dict:
    """
    Deep review: run ReviewerAgent on specified files.
    Returns review comments and approval status.
    """
    project_path = _project_path(project_id)
    if not project_path.exists():
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Read file contents
    files_to_review = []
    for path in payload.paths:
        try:
            data, is_text = fileutils.read_project_file(project_path, path)
            if is_text:
                files_to_review.append({
                    "path": path,
                    "content": data.decode("utf-8")
                })
        except FileNotFoundError:
            continue
    
    if not files_to_review:
        raise HTTPException(status_code=400, detail="No valid files to review")
    
    # Broadcast that review is starting
    await ws_manager.broadcast(
        str(project_id),
        {
            "type": "event",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "project_id": str(project_id),
            "agent": "reviewer",
            "level": "info",
            "msg": f"Deep review started for {len(files_to_review)} files...",
        },
    )
    
    # Run review (parallel if multiple files)
    if len(files_to_review) == 1:
        result = await reviewer_agent.review(
            f"Review this file: {files_to_review[0]['path']}", 
            files_to_review
        )
    else:
        # Parallel review for multiple files
        tasks = [
            reviewer_agent.review(f"Review file: {f['path']}", [f])
            for f in files_to_review
        ]
        results = await asyncio.gather(*tasks)
        
        # Merge results
        all_comments = []
        all_approved = True
        for r in results:
            all_comments.extend(r.get("comments", []))
            if not r.get("approved", True):
                all_approved = False
        result = {"approved": all_approved, "comments": all_comments}
    
    # Broadcast result
    level = "info" if result.get("approved") else "warning"
    await ws_manager.broadcast(
        str(project_id),
        {
            "type": "event",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "project_id": str(project_id),
            "agent": "reviewer",
            "level": level,
            "msg": f"Review complete. Approved: {result.get('approved')}. Comments: {len(result.get('comments', []))}",
        },
    )
    
    return result


@router.get("/{project_id}/download")
async def download_project(
    project_id: UUID, version: Optional[int] = Query(default=None)
) -> FileResponse:
    project_path = _project_path(project_id)
    if not project_path.exists():
        raise HTTPException(status_code=404, detail="Project not found")
    zip_path = fileutils.build_project_zip(project_path)
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"project_{project_id}.zip",
    )


@router.post("/{project_id}/file")
async def save_file(
    project_id: UUID,
    payload: FileUpdate,
    session: AsyncSession = Depends(get_session_dependency),
) -> dict:
    project_path = _project_path(project_id)
    if not project_path.exists():
        raise HTTPException(status_code=404, detail="Project not found")
    target = project_path / payload.path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(payload.content, encoding="utf-8")
    size = target.stat().st_size
    await db_utils.add_artifacts(session, project_id, [payload.path], [size])
    await db_utils.record_event(
        session,
        project_id,
        f"File {payload.path} saved",
        agent="editor",
    )
    await ws_manager.broadcast(
        str(project_id),
        {
            "type": "event",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "project_id": str(project_id),
            "agent": "editor",
            "level": "info",
            "msg": f"File {payload.path} saved",
            "artifact_path": payload.path,
        },
    )
    return {"path": payload.path, "size_bytes": size}


# ============ Memory / Knowledge API ============

class MemorySearchRequest(BaseModel):
    """Request for memory search."""
    query: str
    n_results: int = 5
    context_type: Optional[str] = None  # file, event, decision


class MemoryAddRequest(BaseModel):
    """Request to add memory."""
    content: str
    context_type: str = "general"
    metadata: Optional[Dict[str, str]] = None


@router.get("/{project_id}/memory/search")
async def search_project_memory(
    project_id: UUID,
    query: str = Query(..., description="Search query"),
    n_results: int = Query(default=5, ge=1, le=20),
    context_type: Optional[str] = Query(default=None),
) -> List[Dict]:
    """
    Поиск в долгосрочной памяти проекта.
    
    Возвращает релевантные документы (файлы, события, решения).
    """
    memory = get_project_memory(str(project_id))
    results = memory.search(query, n_results=n_results, context_type=context_type)
    return results


@router.post("/{project_id}/memory/add")
async def add_to_project_memory(
    project_id: UUID,
    request: MemoryAddRequest,
) -> Dict:
    """
    Добавить информацию в память проекта вручную.
    
    Полезно для добавления контекста, который агенты не знают автоматически.
    """
    memory = get_project_memory(str(project_id))
    success = memory.add_context(
        content=request.content,
        context_type=request.context_type,
        metadata=request.metadata
    )
    return {"success": success}


@router.get("/{project_id}/memory/context")
async def get_relevant_context(
    project_id: UUID,
    task: str = Query(..., description="Task description to find relevant context for"),
    max_chars: int = Query(default=3000, ge=100, le=10000),
) -> Dict:
    """
    Получить релевантный контекст для задачи.
    
    Используется для улучшения качества генерации кода.
    """
    memory = get_project_memory(str(project_id))
    context = memory.get_relevant_context(task, max_chars=max_chars)
    return {"context": context, "length": len(context)}


@router.delete("/cache/clear")
async def clear_semantic_cache() -> Dict:
    """
    Очистить семантический кэш LLM запросов.
    
    Полезно для отладки или принудительного обновления.
    """
    cache = get_semantic_cache()
    success = cache.clear()
    return {"success": success, "message": "Semantic cache cleared" if success else "Failed to clear cache"}


# ============ Knowledge Sources API ============

class KnowledgeAddRequest(BaseModel):
    """Request to add knowledge to a source."""
    content: str
    title: str = ""
    tags: Optional[List[str]] = None


class KnowledgeSearchRequest(BaseModel):
    """Request to search knowledge."""
    query: str
    n_results: int = 5
    source_ids: Optional[List[str]] = None
    tags: Optional[List[str]] = None


@router.get("/knowledge/sources")
async def list_knowledge_sources() -> List[Dict]:
    """
    Список всех источников знаний.
    """
    registry = get_knowledge_registry()
    sources = registry.list_sources()
    return [
        {
            "id": s.id,
            "name": s.name,
            "source_type": s.source_type,
            "description": s.description,
            "enabled": s.enabled,
        }
        for s in sources
    ]


@router.post("/knowledge/sources/{source_id}/add")
async def add_knowledge_to_source(
    source_id: str,
    request: KnowledgeAddRequest,
) -> Dict:
    """
    Добавить знания в источник.
    """
    registry = get_knowledge_registry()
    source = registry.get_source(source_id)
    
    if not source:
        raise HTTPException(status_code=404, detail=f"Source '{source_id}' not found")
    
    success = registry.add_knowledge(
        source_id=source_id,
        content=request.content,
        title=request.title,
        tags=request.tags
    )
    
    return {"success": success}


@router.post("/knowledge/search")
async def search_knowledge(request: KnowledgeSearchRequest) -> List[Dict]:
    """
    Поиск по базе знаний.
    """
    registry = get_knowledge_registry()
    results = registry.search_knowledge(
        query=request.query,
        n_results=request.n_results,
        source_ids=request.source_ids,
        tags=request.tags
    )
    return results


@router.get("/knowledge/context")
async def get_knowledge_context(
    task: str = Query(..., description="Task description"),
    tech_stack: Optional[str] = Query(default=None, description="Technology stack (e.g., python, cpp, react)"),
    max_chars: int = Query(default=2000, ge=100, le=5000),
) -> Dict:
    """
    Получить релевантные знания для задачи.
    
    Используется агентами для улучшения качества генерации.
    """
    registry = get_knowledge_registry()
    context = registry.get_context_for_task(
        task_description=task,
        tech_stack=tech_stack,
        max_chars=max_chars
    )
    return {"context": context, "length": len(context)}
