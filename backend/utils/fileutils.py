import json
import os
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
from zipfile import ZIP_DEFLATED, ZipFile

from .schemas import FileEntry


def ensure_project_dir(projects_root: Path, project_id: str, meta: Dict[str, str]) -> Path:
    project_path = projects_root / project_id
    project_path.mkdir(parents=True, exist_ok=True)
    manifest_path = project_path / "meta.json"
    manifest_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return project_path


def iter_file_entries(project_path: Path) -> List[FileEntry]:
    entries: List[FileEntry] = []
    for root, dirs, files in os.walk(project_path):
        rel_root = Path(root).relative_to(project_path)
        for directory in dirs:
            dir_path = (rel_root / directory).as_posix()
            full = Path(root) / directory
            entries.append(
                FileEntry(
                    path=dir_path if dir_path != "." else directory,
                    is_dir=True,
                    size_bytes=0,
                )
            )
        for file in files:
            full = Path(root) / file
            rel = (rel_root / file).as_posix()
            entries.append(
                FileEntry(
                    path=rel if rel != "." else file,
                    is_dir=False,
                    size_bytes=full.stat().st_size,
                )
            )
    return entries


def read_project_file(project_path: Path, relative_path: str) -> Tuple[bytes, bool]:
    full_path = (project_path / relative_path).resolve()
    if not str(full_path).startswith(str(project_path.resolve())) or not full_path.exists():
        raise FileNotFoundError(relative_path)
    data = full_path.read_bytes()
    is_text = False
    try:
        data.decode("utf-8")
        is_text = True
    except UnicodeDecodeError:
        is_text = False
    return data, is_text


def build_project_zip(project_path: Path) -> Path:
    zip_path = project_path / "project.zip"
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zip_file:
        for file in project_path.rglob("*"):
            if file.is_file() and file.name != "project.zip":
                zip_file.write(file, arcname=file.relative_to(project_path))
    return zip_path


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def write_files(project_path: Path, files: Iterable[Dict[str, str]]) -> List[Path]:
    saved: List[Path] = []
    root = project_path.resolve()
    for file in files:
        relative = file["path"].lstrip("/")
        content = file.get("content", "")
        dest = (project_path / relative).resolve()
        if not _is_within(dest, root):
            # Skip attempts to write outside the project directory
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        saved.append(dest)
    return saved

