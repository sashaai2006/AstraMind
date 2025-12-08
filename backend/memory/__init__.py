"""
Memory module for AstraMind.

Includes:
- db: SQLite database for projects, tasks, events
- vector_store: ChromaDB for semantic search and long-term memory
- knowledge_sources: Curated knowledge base for best practices
"""
from backend.memory.vector_store import (
    get_project_memory,
    get_semantic_cache,
    ProjectMemory,
    SemanticCache,
)
from backend.memory.knowledge_sources import (
    get_knowledge_registry,
    KnowledgeSource,
    KnowledgeSourceRegistry,
)

__all__ = [
    "get_project_memory",
    "get_semantic_cache",
    "ProjectMemory",
    "SemanticCache",
    "get_knowledge_registry",
    "KnowledgeSource",
    "KnowledgeSourceRegistry",
]
