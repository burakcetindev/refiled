

import asyncio
from pathlib import Path

undo_stack = []

def add_change_set(changes: list[tuple[Path, Path]]):
    """
    Add a list of (old_path, new_path) tuples to the undo stack.
    """
    if changes:
        undo_stack.append(changes)

async def undo_last_change_set() -> list[tuple[Path, Path]]:
    """
    Undo the last batch of changes by renaming new_path back to old_path asynchronously.
    Returns the list of reverted changes.
    """
    if not undo_stack:
        return []

    last_changes = undo_stack.pop()
    loop = asyncio.get_running_loop()

    async def revert_change(old_path: Path, new_path: Path):
        try:
            await loop.run_in_executor(None, new_path.rename, old_path)
            return (new_path, old_path)
        except Exception as e:
            print(f"⚠️ Failed to undo rename {new_path} -> {old_path}: {e}")
            return None

    tasks = [revert_change(old, new) for old, new in last_changes]
    results = await asyncio.gather(*tasks)
    return [res for res in results if res is not None]