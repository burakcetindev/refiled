

import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from refiled.operations.search import filter_files
from refiled.utilities import safe_rename, is_video_file, clean_string

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov"}

def _add_prefix(name: str, prefix: str) -> str:
    return prefix + name

def _remove_prefix(name: str, prefix: str) -> str:
    if name.startswith(prefix):
        return name[len(prefix):]
    return name

async def _process_add_prefix(file: Path, prefix: str) -> tuple[Path, Path]:
    stem = file.stem
    ext = file.suffix
    new_stem = _add_prefix(stem, prefix)
    new_name = clean_string(new_stem) + ext
    new_path = file.with_name(new_name)
    if new_path.exists():
        return None
    success = await safe_rename(file, new_path)
    if success:
        return (file, new_path)
    return None

async def _process_remove_prefix(file: Path, prefix: str) -> tuple[Path, Path]:
    stem = file.stem
    ext = file.suffix
    new_stem = _remove_prefix(stem, prefix)
    new_name = clean_string(new_stem) + ext
    new_path = file.with_name(new_name)
    if new_path.exists():
        return None
    success = await safe_rename(file, new_path)
    if success:
        return (file, new_path)
    return None

async def add_prefix(files, prefix):
    files = [f for f in files if is_video_file(f.name)]
    results = []
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        tasks = [loop.create_task(_process_add_prefix(file, prefix)) for file in files]
        for task in asyncio.as_completed(tasks):
            res = await task
            if res:
                results.append(res)
    return results

async def remove_prefix(files, prefix):
    files = [f for f in files if is_video_file(f.name)]
    results = []
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        tasks = [loop.create_task(_process_remove_prefix(file, prefix)) for file in files]
        for task in asyncio.as_completed(tasks):
            res = await task
            if res:
                results.append(res)
    return results