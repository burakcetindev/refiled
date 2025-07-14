import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from refiled.operations.search import filter_files
from refiled.utilities import safe_rename, is_video_file, clean_string

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov"}

def _add_prefix(name: str, prefix: str, position: str = "start") -> str:
    if not prefix.endswith(" "):
        prefix += " "
    if position == "start":
        return prefix + name
    elif position == "end":
        return name + " " + prefix.strip()
    else:
        return name

def _remove_prefix(name: str, prefix: str, position: str = "start") -> str:
    if not prefix.endswith(" "):
        prefix += " "
    if position == "start":
        if name.startswith(prefix):
            return name[len(prefix):]
    elif position == "end":
        if name.endswith(prefix.strip()):
            # Remove prefix at end, including preceding space if any
            if name.endswith(" " + prefix.strip()):
                return name[:-(len(prefix) + 1)]
            return name[:-len(prefix)]
    return name

async def _process_add_prefix(file: Path, prefix: str, position: str = "start") -> tuple[Path, Path]:
    stem = file.stem
    ext = file.suffix
    new_stem = _add_prefix(stem, prefix, position)
    new_name = clean_string(new_stem) + ext
    new_path = file.with_name(new_name)
    if new_path.exists():
        return None
    success = await safe_rename(file, new_path)
    if success:
        return (file, new_path)
    return None

async def _process_remove_prefix(file: Path, prefix: str, position: str = "start") -> tuple[Path, Path]:
    stem = file.stem
    ext = file.suffix
    new_stem = _remove_prefix(stem, prefix, position)
    new_name = clean_string(new_stem) + ext
    new_path = file.with_name(new_name)
    if new_path.exists():
        return None
    success = await safe_rename(file, new_path)
    if success:
        return (file, new_path)
    return None

async def add_prefix(files, prefix, position: str = "start", filter_mode="all", filter_term=None):
    if filter_mode == "specific" and filter_term:
        files = await filter_files(files, filter_term, fuzzy=True, reversed=False)
    else:
        files = [f for f in files if is_video_file(f.name)]
    results = []
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        tasks = [loop.create_task(_process_add_prefix(file, prefix, position)) for file in files]
        for task in asyncio.as_completed(tasks):
            res = await task
            if res:
                results.append(res)
    return results

async def remove_prefix(files, prefix, position: str = "start", filter_mode="all", filter_term=None):
    if filter_mode == "specific" and filter_term:
        files = await filter_files(files, filter_term, fuzzy=True, reversed=False)
    else:
        files = [f for f in files if is_video_file(f.name)]
    results = []
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        tasks = [loop.create_task(_process_remove_prefix(file, prefix, position)) for file in files]
        for task in asyncio.as_completed(tasks):
            res = await task
            if res:
                results.append(res)
    return results