

import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import re

from refiled.utilities import safe_rename, is_video_file, clean_string

BRACKETS_PATTERN = re.compile(r'[\[\]\{\}\(\)]')

def _remove_brackets_from_name(name: str) -> str:
    # Remove brackets [] {} () but keep the content inside intact
    # Also fix multiple spaces
    cleaned = BRACKETS_PATTERN.sub("", name)
    # Normalize spaces
    cleaned = " ".join(cleaned.split())
    return cleaned

async def _process_file(file: Path) -> tuple[Path, Path]:
    stem = file.stem
    ext = file.suffix
    new_stem = _remove_brackets_from_name(stem)
    new_name = clean_string(new_stem) + ext
    new_path = file.with_name(new_name)
    if new_path.exists():
        return None
    if new_name == file.name:
        # No change needed
        return None
    success = await safe_rename(file, new_path)
    if success:
        return (file, new_path)
    return None

async def remove_brackets(files):
    files = [f for f in files if is_video_file(f.name)]
    results = []
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        tasks = [loop.create_task(_process_file(file)) for file in files]
        for task in asyncio.as_completed(tasks):
            res = await task
            if res:
                results.append(res)
    return results