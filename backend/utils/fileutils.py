"""File utilities for project operations."""
import asyncio
from pathlib import Path
from typing import Dict, List, Tuple, Any
import os

class FileEntry:
    """Represents a file entry in a project."""
    def __init__(self, path: str, is_dir: bool = False):
        self.path = path
        self.is_dir = is_dir

def iter_file_entries(project_path: Path) -> List[FileEntry]:
    """Iterate over all files in a project directory."""
    entries = []
    if not project_path.exists():
        return entries
    
    for root, dirs, files in os.walk(project_path):
        root_path = Path(root)
        rel_root = root_path.relative_to(project_path)
        
        for d in dirs:
            entries.append(FileEntry(str(rel_root / d), is_dir=True))
        
        for f in files:
            entries.append(FileEntry(str(rel_root / f), is_dir=False))
    
    return entries

def read_project_file(project_path: Path, file_path: str) -> Tuple[bytes, bool]:
    """Read a file from a project. Returns (data, is_text)."""
    full_path = project_path / file_path
    if not full_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        data = full_path.read_bytes()
        # Simple text detection
        try:
            data.decode('utf-8')
            is_text = True
        except UnicodeDecodeError:
            is_text = False
        return data, is_text
    except Exception as e:
        raise IOError(f"Error reading file {file_path}: {e}")

def write_files(project_path: Path, files: Dict[str, str]) -> None:
    """Write multiple files to a project directory."""
    for file_path, content in files.items():
        full_path = project_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding='utf-8')

async def write_files_async(project_path: Path, files: Dict[str, str]) -> None:
    """Write multiple files to a project directory asynchronously."""
    await asyncio.to_thread(write_files, project_path, files)

