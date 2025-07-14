from pathlib import Path
from InquirerPy import inquirer

def list_subfolders(path: Path) -> list:
    try:
        return sorted(
            [f for f in path.iterdir() if f.is_dir() and (not f.name.startswith(".") or f.name in {"Downloads", "Desktop", "Documents"})],
            key=lambda x: (not x.name[0].isdigit(), x.name.lower())
        )
    except Exception:
        return []

def build_folder_choices(current_path: Path) -> list:
    home = Path.home()
    common_folders = [home / "Downloads", home / "Desktop", home / "Movies", home / "Documents"]
    subfolders = list_subfolders(current_path)
    choices = []

    choices.append({"name": "⬆️ Go Up", "value": current_path.parent})
    choices.append({"name": f"🗂️ Select This Folder [{current_path.name}]", "value": current_path})

    if current_path == home:
        for folder in [f for f in common_folders if f.exists()]:
            choices.append({"name": f"📂 {folder.name}", "value": folder})
        choices.append({"name": "📁 Enter Custom Path", "value": "custom"})
        choices.append({"name": "🚧 Exit to Main Menu", "value": "__BACK__"})

    if current_path != home:
        for folder in sorted(subfolders, key=lambda x: (not x.name[0].isdigit(), x.name.lower())):
            choices.append({"name": f"📂 {folder.name}", "value": folder})

    return choices

async def choose_folder(start_path: Path = None) -> Path | str:
    current_path = start_path or Path.home()

    while True:
        choices = build_folder_choices(current_path)

        selected = await inquirer.select(
            message=f"? Current folder: {current_path}",
            choices=choices,
            cycle=True,
            qmark="📁"
        ).execute_async()

        if selected == "custom":
            new_path_str = await inquirer.text(message="Enter custom path:").execute_async()
            if not new_path_str.strip():
                continue
            new_path = Path(new_path_str).expanduser().resolve()
            if new_path.exists() and new_path.is_dir():
                current_path = new_path
            else:
                print("⚠️ Invalid path, please try again.")
        elif selected == "__BACK__":
            return "__BACK__"
        elif isinstance(selected, Path):
            if selected == current_path:
                return selected
            else:
                current_path = selected

# ✅ support for dual-folder flows like screenshot parser
async def choose_two_folders(label1: str, label2: str) -> tuple[Path, Path] | str:
    print(f"📁 {label1}")
    folder1 = await choose_folder()
    if folder1 == "__BACK__":
        return "__BACK__"

    print(f"📁 {label2}")
    folder2 = await choose_folder()
    if folder2 == "__BACK__":
        return "__BACK__"

    return folder1, folder2