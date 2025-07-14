

from pathlib import Path

def validate_path(path_str: str) -> Path | None:
    """
    Validates and returns a cleaned Path object if the path exists and is a directory.
    Otherwise, returns None.
    """
    path = Path(path_str).expanduser().resolve()
    if path.exists() and path.is_dir():
        return path
    return None

def is_video_file(path: Path) -> bool:
    """
    Returns True if the file is a recognized video format.
    """
    return path.suffix.lower() in {".mp4", ".mkv", ".avi", ".mov"}