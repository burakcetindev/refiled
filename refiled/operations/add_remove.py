import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from refiled.operations.search import filter_files
from refiled.utilities import safe_rename, clean_string

# Supported video extensions for rename
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov"}

def _should_process(file: Path) -> bool:
    return file.is_file() and file.suffix.lower() in VIDEO_EXTENSIONS

def _add_text_to_name(name: str, text: str, position: str) -> str:
    if position == "start":
        if not text.endswith(" "):
            text += " "
        return text + name
    elif position == "end":
        if not text.startswith(" "):
            text = " " + text
        return name + text
    return name

def _remove_text_from_name(name: str, text: str) -> str:
    # Remove all occurrences of text (case-insensitive)
    return name.replace(text, "").replace(text.lower(), "").replace(text.upper(), "")

async def _process_file_add(file: Path, text: str, position: str) -> tuple[Path, Path]:
    stem = file.stem
    ext = file.suffix
    new_stem = _add_text_to_name(stem, text, position)
    new_name = clean_string(new_stem) + ext
    new_path = file.with_name(new_name)
    if new_path.exists():
        return None
    success = await safe_rename(file, new_path)
    if success:
        return (file, new_path)
    return None

async def _process_file_remove(file: Path, text: str) -> tuple[Path, Path]:
    stem = file.stem
    ext = file.suffix
    new_stem = _remove_text_from_name(stem, text)
    new_name = clean_string(new_stem) + ext
    new_path = file.with_name(new_name)
    if new_path.exists():
        return None
    success = await safe_rename(file, new_path)
    if success:
        return (file, new_path)
    return None

async def add_text(files, text, position, fuzzy=False, reversed=False, filter_mode="all", filter_term=None):
    if filter_mode == "specific" and filter_term:
        files = await filter_files(files, filter_term, fuzzy=fuzzy, reversed=reversed)
    else:
        files = [f for f in files if _should_process(f)]
    results = []
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        tasks = [
            loop.create_task(_process_file_add(file, text, position))
            for file in files if _should_process(file)
        ]
        for task in asyncio.as_completed(tasks):
            res = await task
            if res:
                results.append(res)
    return results

async def remove_text(files, text, fuzzy=False, reversed=False, filter_mode="all", filter_term=None):
    if filter_mode == "specific" and filter_term:
        files = await filter_files(files, filter_term, fuzzy=fuzzy, reversed=reversed)
    else:
        files = [f for f in files if _should_process(f)]
    results = []
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        tasks = [
            loop.create_task(_process_file_remove(file, text))
            for file in files if _should_process(file)
        ]
        for task in asyncio.as_completed(tasks):
            res = await task
            if res:
                results.append(res)
    return results