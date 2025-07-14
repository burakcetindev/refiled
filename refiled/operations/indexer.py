import asyncio
from pathlib import Path
from collections import defaultdict
import re

import nltk
from nltk.corpus import stopwords

from better_profanity import profanity
profanity.load_censor_words()

import wordninja
from refiled.utilities import is_probable_name
from refiled.utilities import safe_rename, is_video_file

try:
    STOPWORDS = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords")
    STOPWORDS = set(stopwords.words("english"))


def is_forbidden_phrase(phrase):
    return profanity.contains_profanity(phrase)

def normalize_name(name):
    # Remove extension, lowercase, replace punctuation with space, collapse spaces
    name = Path(name).stem
    name = re.sub(r'[^a-zA-Z0-9\s]', ' ', name)
    name = re.sub(r'\s+', ' ', name)
    return name.strip().lower()

def generate_phrases(tokens):
    phrases = set()
    length = len(tokens)
    # 2-word, 3-word phrases only
    for n in [2, 3]:
        for i in range(length - n + 1):
            phrase = " ".join(tokens[i:i + n])
            phrases.add(phrase)
    return phrases

async def index_repeated_keywords(directory: Path, fuzzy: bool = False):
    """
    Index repeated 2-3 word phrases in filenames under directory,
    move grouped files into [indexed]/phrase_name/ folders asynchronously,
    and return list of (old_path, new_path) tuples for undo.
    """
    path = directory
    files = [f for f in path.iterdir() if f.is_file() and is_video_file(f.name)]

    phrase_map = defaultdict(set)  # phrase -> set of files

    # Build phrase map
    for file in files:
        norm_name = normalize_name(file.name)
        norm_tokens = norm_name.split()
        # Use wordninja to split original stem for probable names
        orig_name = Path(file.name).stem
        orig_tokens = wordninja.split(orig_name)
        phrases_norm = generate_phrases(norm_tokens)
        for phrase in phrases_norm:
            words = phrase.split()
            score = 0
            if len(words) >= 2:
                score += 1
            if all(w.istitle() for w in words):
                score += 1
            if all(w.lower() not in STOPWORDS for w in words):
                score += 1
            if not is_forbidden_phrase(phrase.replace("_", " ")):
                score += 1
            if any(word.isdigit() for word in words):
                continue
            # Use is_probable_name to filter probable phrases
            if not is_probable_name(phrase):
                continue
            if score < 3:
                continue
            phrase_map[phrase].add(file)

    # Merge reversed two-word phrases into one key
    for phrase in list(phrase_map.keys()):
        tokens = phrase.split()
        if len(tokens) == 2:
            rev = f"{tokens[1]} {tokens[0]}"
            if rev in phrase_map:
                phrase_map[phrase] |= phrase_map[rev]
                del phrase_map[rev]

    # Filter phrases that appear in at least two unique files
    valid_phrases = {p: fs for p, fs in phrase_map.items() if len(fs) >= 2 and len({f.name for f in fs}) >= 2}
    if not valid_phrases:
        return []

    # Sort phrases by length descending (prioritize longer phrases)
    sorted_phrases = sorted(valid_phrases.items(), key=lambda x: -len(x[0].split()))

    indexed_dir = path / "[indexed]"
    indexed_dir.mkdir(exist_ok=True)

    changes = []
    assigned_files = set()

    loop = asyncio.get_running_loop()

    async def move_file_async(file: Path, target_dir: Path):
        target_dir.mkdir(exist_ok=True)
        target = target_dir / file.name
        try:
            await safe_rename(file, target)
            return (file, target)
        except Exception as e:
            print(f"[ERROR] Failed to move {file} to {target}: {e}")
            return None

    for phrase, files_set in sorted_phrases:
        unique_files = [f for f in files_set if f not in assigned_files]
        if len(unique_files) < 2:
            continue

        subfolder = indexed_dir / phrase.replace(" ", "_")
        # Schedule moves concurrently
        move_tasks = [move_file_async(file, subfolder) for file in unique_files]
        results = await asyncio.gather(*move_tasks)
        for res in results:
            if res:
                old_file, new_file = res
                assigned_files.add(old_file)
                changes.append((old_file, new_file))

    # Track indexed_dir for deletion if undo is triggered
    if changes:
        changes.append(("__DELETE_IF_UNDONE__", indexed_dir))
    return changes


# Cleanup function to remove [indexed] folder if all subfolders are empty
def cleanup_indexed_folder_if_empty(indexed_dir: Path):
    """
    Recursively check all subdirectories in the indexed folder.
    If they are all empty or contain no files, remove the entire [indexed] folder.
    """
    if not indexed_dir.exists():
        return
    for sub in indexed_dir.rglob("*"):
        if sub.is_file():
            return  # Abort: there's still at least one file
    try:
        for sub in sorted(indexed_dir.glob("**/*"), reverse=True):
            if sub.is_dir():
                sub.rmdir()
        indexed_dir.rmdir()
        print(f"🗑️ Cleaned up empty folder: {indexed_dir}")
    except Exception as e:
        print(f"[ERROR] Failed to clean up {indexed_dir}: {e}")