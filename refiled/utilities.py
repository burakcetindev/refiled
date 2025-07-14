

import asyncio
from pathlib import Path

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov"}

def is_video_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in VIDEO_EXTENSIONS

def clean_string(text: str) -> str:
    # Normalize spaces and strip leading/trailing whitespace
    return " ".join(text.strip().split())

def capwords(text: str) -> str:
    # Capitalizes each word properly
    return " ".join(word.capitalize() for word in text.split())

async def safe_rename(old_path: Path, new_path: Path) -> bool:
    """
    Rename a file asynchronously and safely.
    Returns True if rename succeeded, False otherwise.
    """
    loop = asyncio.get_running_loop()
    try:
        await loop.run_in_executor(None, old_path.rename, new_path)
        return True
    except Exception as e:
        print(f"⚠️ Failed to rename {old_path} -> {new_path}: {e}")
        return False


# Utility to check if a string is a probable "natural" name (not a slug/hash/etc)
def is_probable_name(text: str) -> bool:
    """
    Determines if a phrase looks like a natural name (e.g., Movie Title or Word Group).
    Filters out gibberish, slugs, hashes, and all-uppercase codes.
    """
    if not text or len(text) < 3:
        return False
    if text.isupper():
        return False
    if any(char.isdigit() for char in text) and "_" in text:
        return False
    if len(text.split()) == 1 and text.islower():
        return False
    return True