

import asyncio
from pathlib import Path
from refiled.utilities import is_video_file, safe_rename


def _transform_name(name: str, mode: str) -> str:
    """
    Transform the stem of the filename to upper or lower, preserving extension and special characters.
    """
    if "." not in name:
        # No extension
        stem = name
        ext = ""
    else:
        stem, ext = name.rsplit(".", 1)
        ext = "." + ext
    if mode == "upper":
        new_stem = stem.upper()
    elif mode == "lower":
        new_stem = stem.lower()
    else:
        new_stem = stem
    return f"{new_stem}{ext}"


async def convert_to_all_caps(files: list[Path]) -> list[tuple[Path, Path]]:
    """
    Converts filenames to full uppercase (excluding extension), preserving special characters.
    Only operates on video files.
    Returns a list of (old_path, new_path) pairs for successful renames.
    """
    results = []
    for file in files:
        if not is_video_file(file.name):
            continue
        new_name = _transform_name(file.name, mode="upper")
        target = file.with_name(new_name)
        if target == file:
            continue
        success = await safe_rename(file, target)
        if success:
            results.append((file, target))
    return results


async def convert_to_all_lower(files: list[Path]) -> list[tuple[Path, Path]]:
    """
    Converts filenames to lowercase (excluding extension), preserving extension casing and special characters.
    Only operates on video files.
    Returns a list of (old_path, new_path) pairs for successful renames.
    """
    results = []
    for file in files:
        if not is_video_file(file.name):
            continue
        new_name = _transform_name(file.name, mode="lower")
        target = file.with_name(new_name)
        if target == file:
            continue
        success = await safe_rename(file, target)
        if success:
            results.append((file, target))
    return results