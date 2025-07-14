

import asyncio
from pathlib import Path
from rapidfuzz import fuzz

async def filter_files(files, search_term, fuzzy=False, reversed=False):
    """
    Asynchronously filter a list of Path objects by matching their names against search_term.
    Supports fuzzy matching and reversed string matching.
    Returns a list of matching Path objects.
    """
    if not search_term:
        return files

    loop = asyncio.get_running_loop()

    def match(file):
        name = file.stem.lower()
        term = search_term.lower()
        to_match = name[::-1] if reversed else name

        if fuzzy:
            score = fuzz.partial_ratio(term, to_match)
            return score >= 70  # threshold can be tuned
        else:
            return term in to_match

    tasks = [loop.run_in_executor(None, match, f) for f in files]
    results = await asyncio.gather(*tasks)

    return [file for file, matched in zip(files, results) if matched]