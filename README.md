# 📁 refiled

![refiled demo](./rfld_image.png)

**refiled** is a modular, asynchronous CLI-based file management and renaming tool designed for power users working with large media collections (e.g., `.mp4`, `.mkv`). It supports advanced text editing, batch renaming, pirate-style formatting, prefixing, undo, and intelligent indexing—all with an interactive CLI interface.

---

## ✨ Features

- 🔍 **Interactive Folder Selection**: Navigate with arrow keys through Downloads, Desktop, Documents, and custom paths. Uses a clean, recursive folder browser with emoji-labeled directories.
- 📝 **Add/Remove Text**: Append or strip any string to/from the start or end of filenames. Supports fuzzy and reversed matching.
- 🔁 **Move Text (Experimental)**: Move a chosen phrase or word within a filename from start to end or vice versa. Still under refinement—may yield edge case issues.
- ☠️ **Pirate/Normalize Formatting**: Convert space-based titles to dot-separated lowercase (`my.movie.title`) and reverse back into capitalized titles (`My Movie Title`).
- ➕ **Add/Remove Prefix**: Insert or delete consistent prefixes from a batch of filenames for better grouping or classification.
- 🧽 **Bracket Cleaner**: Removes unnecessary brackets like `[`, `(`, `{` while preserving enclosed content.
- 🔄 **Undo System**: Every rename operation can be reverted instantly via tracked history. Even index-based group moves are reversible.
- 📂 **Index Repeated Files**: Detects and groups files with repeated phrases (like `Part 1`, `Part 2`) into `[indexed]/Phrase/` folders.
- 🖼️ **Screenshot Parser**: Matches screenshots (`.png`, `.jpg`) to video files alphabetically, renaming screenshots to match corresponding video names.
- 🔁 **MP4/MKV Extension Converter**: Converts file extensions from `.mp4` to `.mkv` (or vice versa) for batches of media with consistent structure.
- 🧠 **Fuzzy + Reversed Matching**: All operations support intelligent fuzzy and reversed matching to broaden match flexibility.
- ⚡ **Async & Parallel Execution**: Uses `asyncio` and `ThreadPoolExecutor` for lightning-fast batch processing even on large file sets.

---

## 📦 Installation

1. **Clone the repo**
```bash
git clone https://github.com/burakcetindev/refiled.git
cd refiled
```

2. **Set up virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt

#(First time only) Download NLTK stopwords:
python -m nltk.downloader stopwords
```


---

## 🚀 Usage

Run the CLI:

```bash
python main.py
```

Use arrow keys to navigate folders, select operations, and interact with prompts.

---

## 🧱 Folder Structure

```
refiled/
├── main.py                 # CLI entry point
├── requirements.txt
├── README.md
├── refiled/
│   ├── cli.py              # Full CLI logic and menu interactions
│   ├── utilities.py        # Shared async helpers
│   ├── filesystem/
│   │   ├── navigator.py    # Folder selection UI
│   │   ├── validator.py    # Path validation
│   ├── operations/
│   │   ├── add_remove.py
│   │   ├── move.py
│   │   ├── pirate.py
│   │   ├── prefix.py
│   │   ├── remove_brackets.py
│   │   ├── convert.py
│   │   ├── indexer.py
│   │   ├── search.py
│   │   ├── undo.py
```

---

## 🧪 Examples

**Pirate format:**
```
Original: My Movie Trailer.mp4
Pirated : my.movie.trailer.mp4
```

**Normalize format:**
```
Original: my.movie.trailer.mp4
Cleaned : My Movie Trailer.mp4
```

**Indexing:**
- Detects common repeated 2-3 word phrases
- Groups files under `[indexed]/Phrase_Name/`

---

## ⚠️ Notes

- The **Move Text** function is experimental and may not always behave as expected.
- Bracket remover only affects brackets, not content.
- Operations work only on common video formats: `.mp4`, `.mkv`, `.avi`, `.mov`.

---

## 📋 License

MIT License
