"""Pydantic schemas for API requests and responses."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID

class FileEntry(BaseModel):
    """File entry in a project."""
    path: str
    is_dir: bool = False
    content: Optional[str] = None

class FileUpdate(BaseModel):
    """File update request."""
    path: str
    content: str

class ProjectCreate(BaseModel):
    """Project creation request."""
    name: str
    description: Optional[str] = None

class ProjectStatusResponse(BaseModel):
    """Project status response."""
    id: str
    status: str
    version: int = 0

class DocumentCreate(BaseModel):
    """Document creation request."""
    name: str
    doc_type: str
    description: Optional[str] = None

class DocumentStatusResponse(BaseModel):
    """Document status response."""
    id: str
    status: str
    name: str
    doc_type: str

class ArtifactInfo(BaseModel):
    """Artifact information."""
    path: str
    content: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

