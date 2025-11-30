from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from sqlmodel import Column, DateTime, Field, JSON, SQLModel


class Project(SQLModel, table=True):
    __tablename__ = "projects"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    title: str
    description: str
    target: str
    status: str = Field(default="creating")
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.utcnow)
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
        )
    )


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    project_id: UUID = Field(foreign_key="projects.id", index=True)
    name: str
    agent: str
    status: str = Field(default="pending")
    parallel_group: Optional[str] = None
    payload: Dict[str, Any] = Field(
        sa_column=Column(JSON, default=dict, nullable=False)
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.utcnow)
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
        )
    )


class Event(SQLModel, table=True):
    __tablename__ = "events"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    project_id: UUID = Field(foreign_key="projects.id", index=True)
    agent: Optional[str] = None
    level: str = Field(default="info")
    message: str
    data: Dict[str, Any] = Field(sa_column=Column(JSON, default=dict, nullable=False))
    timestamp: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.utcnow)
    )


class Artifact(SQLModel, table=True):
    __tablename__ = "artifacts"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    project_id: UUID = Field(foreign_key="projects.id", index=True)
    path: str
    size_bytes: int
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.utcnow)
    )

