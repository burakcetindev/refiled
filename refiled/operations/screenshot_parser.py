import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from refiled.utilities import safe_rename

IMAGE_EXTS = {".png", ".jpg", ".jpeg"}
VIDEO_EXTS = {".mp4", ".mkv", ".avi", ".mov"}

def _is_image(file: Path) -> bool:
    return file.suffix.lower() in IMAGE_EXTS and file.is_file()

def _is_video(file: Path) -> bool:
    return file.suffix.lower() in VIDEO_EXTS and file.is_file()

async def match_and_rename(video_folder: Path, screenshot_folder: Path) -> list[tuple[Path, Path]]:
    videos = sorted([f for f in video_folder.iterdir() if _is_video(f)], key=lambda f: f.name.lower())
    screenshots = sorted([f for f in screenshot_folder.iterdir() if _is_image(f)], key=lambda f: f.name.lower())

    pair_count = min(len(videos), len(screenshots))
    pairs = zip(screenshots[:pair_count], videos[:pair_count])

    loop = asyncio.get_running_loop()
    results = []

    async def rename_pair(screenshot: Path, video: Path):
        new_name = video.stem + screenshot.suffix.lower()
        target = screenshot.with_name(new_name)
        if target.exists():
            return None
        success = await safe_rename(screenshot, target)
        if success:
            return (screenshot, target)
        return None

    with ThreadPoolExecutor() as executor:
        tasks = [loop.create_task(rename_pair(s, v)) for s, v in pairs]
        for task in asyncio.as_completed(tasks):
            result = await task
            if result:
                results.append(result)

    return results