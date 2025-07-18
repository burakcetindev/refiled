

import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from refiled.operations.search import filter_files
from refiled.utilities import safe_rename, is_video_file, clean_string, capwords

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov"}

def _pirate_format(name: str) -> str:
    # Convert spaces to dots and lowercase
    return name.lower().replace(" ", ".")

def _pirate_capitalized_format(name: str) -> str:
    # Replace dots with spaces, capitalize each word, then restore dots
    parts = name.replace(".", " ").split()
    return ".".join(word.capitalize() for word in parts)

def _normalize_format(name: str) -> str:
    # Convert dots to spaces and capitalize words
    return capwords(name.replace(".", " "))

async def _process_pirate(file: Path, capitalized: bool = False) -> tuple[Path, Path] | None:
    stem = file.stem
    ext = file.suffix
    new_stem = _pirate_capitalized_format(stem) if capitalized else _pirate_format(stem)
    new_name = clean_string(new_stem) + ext
    new_path = file.with_name(new_name)
    # Only skip renaming if the full path matches the original (including case), allowing case-only renames
    if new_path.exists() and new_path.resolve() == file.resolve():
        if new_path.name == file.name:
            return None
    success = await safe_rename(file, new_path)
    return (file, new_path) if success else None

async def _process_normalize(file: Path) -> tuple[Path, Path]:
    stem = file.stem
    ext = file.suffix
    new_stem = _normalize_format(stem)
    new_name = clean_string(new_stem) + ext
    new_path = file.with_name(new_name)
    if new_path.exists():
        return None
    success = await safe_rename(file, new_path)
    if success:
        return (file, new_path)
    return None

async def pirate_format(files, fuzzy=False, reversed=False, capitalized=False):
    files = [f for f in files if is_video_file(f.name)]
    files = await filter_files(files, "", fuzzy=fuzzy, reversed=reversed)
    results = []
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        tasks = [loop.create_task(_process_pirate(file, capitalized=capitalized)) for file in files]
        for task in asyncio.as_completed(tasks):
            res = await task
            if res:
                results.append(res)
    return results

async def normalize_format(files, fuzzy=False, reversed=False):
    files = [f for f in files if is_video_file(f.name)]
    files = await filter_files(files, "", fuzzy=fuzzy, reversed=reversed)
    results = []
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        tasks = [loop.create_task(_process_normalize(file)) for file in files]
        for task in asyncio.as_completed(tasks):
            res = await task
            if res:
                results.append(res)
    return results