"""Path normalization utilities."""
from pathlib import Path
from typing import Union

def normalize_artifact_path(path: Union[str, Path]) -> str:
    """Normalize an artifact path to a consistent format."""
    if isinstance(path, Path):
        path = str(path)
    
    # Normalize separators
    path = path.replace('\\', '/')
    
    # Remove leading slashes
    path = path.lstrip('/')
    
    # Remove . and .. components
    parts = []
    for part in path.split('/'):
        if part == '.':
            continue
        elif part == '..':
            if parts:
                parts.pop()
        else:
            parts.append(part)
    
    return '/'.join(parts)

