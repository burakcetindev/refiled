

import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from refiled.operations.search import filter_files
from refiled.utilities import safe_rename, is_video_file, clean_string

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov"}

def _move_text_in_name(name: str, text: str, position: str) -> str:
    """
    Move the first occurrence of text in name to start or end.
    Returns the modified name. If text not found, returns original.
    """
    lower_name = name.lower()
    lower_text = text.lower()
    idx = lower_name.find(lower_text)
    if idx == -1:
        return name  # text not found

    # Extract the matched substring respecting original casing
    matched_substring = name[idx : idx + len(text)]

    # Remove matched substring
    new_name = name[:idx] + name[idx + len(text):]

    # Clean spaces around removed text
    new_name = " ".join(new_name.split())

    if position == "start":
        return matched_substring + " " + new_name
    elif position == "end":
        return new_name + " " + matched_substring
    else:
        return name

async def _process_file(file: Path, text: str, position: str) -> tuple[Path, Path]:
    stem = file.stem
    ext = file.suffix
    new_stem = _move_text_in_name(stem, text, position)
    new_stem = clean_string(new_stem)
    new_name = new_stem + ext
    new_path = file.with_name(new_name)
    if new_path.exists() or new_name == file.name:
        return None
    success = await safe_rename(file, new_path)
    if success:
        return (file, new_path)
    return None

async def move_text(files, text, position, fuzzy=False, reversed=False):
    files = [f for f in files if is_video_file(f.name)]
    files = await filter_files(files, text, fuzzy=fuzzy, reversed=reversed)
    results = []
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        tasks = [loop.create_task(_process_file(file, text, position)) for file in files]
        for task in asyncio.as_completed(tasks):
            res = await task
            if res:
                results.append(res)
    return results