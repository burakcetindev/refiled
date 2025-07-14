

import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from refiled.operations.search import filter_files
from refiled.utilities import safe_rename, is_video_file, clean_string

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov"}

def _move_text_in_name(name: str, text: str, position: str) -> str:
    """
    Move the first occurrence of `text` (case-insensitive) in `name` to the given position.
    Returns the modified name. If text not found, returns original.
    """
    # Normalize and split into tokens
    tokens = name.split()
    text_tokens = text.split()

    # Lowercase version for matching
    lower_tokens = [t.lower() for t in tokens]
    lower_text_tokens = [t.lower() for t in text_tokens]
    text_len = len(text_tokens)

    # Search for exact match of the sequence
    for i in range(len(tokens) - text_len + 1):
        if lower_tokens[i:i + text_len] == lower_text_tokens:
            matched = tokens[i:i + text_len]
            rest = tokens[:i] + tokens[i + text_len:]
            if position == "start":
                new_tokens = matched + rest
            elif position == "end":
                new_tokens = rest + matched
            else:
                return name
            return " ".join(new_tokens)
    
    return name  # text not found

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

async def move_text(files, text, position, fuzzy=False, reversed=False, filter_mode="all", filter_term=None):
    files = [f for f in files if is_video_file(f.name)]
    if filter_mode == "specific" and filter_term:
        files = await filter_files(files, filter_term, fuzzy=fuzzy, reversed=reversed)
    results = []
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        tasks = [loop.create_task(_process_file(file, text, position)) for file in files]
        for task in asyncio.as_completed(tasks):
            res = await task
            if res:
                results.append(res)
    return results