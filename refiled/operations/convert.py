

import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from refiled.utilities import safe_rename

VIDEO_EXTENSIONS = {".mp4", ".mkv"}

def _convert_extension(file: Path, to_ext: str) -> Path:
    new_name = file.stem + to_ext
    return file.with_name(new_name)

async def _process_file(file: Path, to_ext: str) -> tuple[Path, Path]:
    new_path = _convert_extension(file, to_ext)
    if new_path.exists():
        return None
    success = await safe_rename(file, new_path)
    if success:
        return (file, new_path)
    return None

async def convert_files(files, to_ext: str):
    """
    Convert files with .mp4 or .mkv extension to the other format.
    """
    to_ext = to_ext.lower()
    if to_ext not in VIDEO_EXTENSIONS:
        raise ValueError(f"Unsupported target extension: {to_ext}")

    from_ext = ".mkv" if to_ext == ".mp4" else ".mp4"

    filtered_files = [f for f in files if f.suffix.lower() == from_ext]

    results = []
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        tasks = [loop.create_task(_process_file(file, to_ext)) for file in filtered_files]
        for task in asyncio.as_completed(tasks):
            res = await task
            if res:
                results.append(res)
    return results