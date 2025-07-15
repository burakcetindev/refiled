import asyncio
import time
from pathlib import Path
from InquirerPy import inquirer
from refiled.utilities import is_video_file
from rich.console import Console

from refiled.filesystem.navigator import choose_folder, choose_two_folders
from refiled.operations import (
    add_remove,
    move,
    pirate,
    prefix,
    remove_brackets,
    convert,
    indexer,
    undo,
)

console = Console()

async def run_cli():
    undo_stack = []

    console.print("Starting...", style="bold white")
    console.print(
        "The people who are crazy enough to think they can change the world are the ones who do!",
        style="bold blue",
    )
    console.print("Started", style="purple")

    while True:
        choice = await inquirer.select(
            message="? Choose an action:",
            choices=[
                "👉 Text Editing",
                "👉 Screenshot Parser",
                "👉 Index Repeated Files",
                "👉 Convert Files (.mp4 <-> .mkv)",
                "👉 Exit",
            ],
        ).execute_async()

        if choice == "👉 Exit":
            console.print("Exiting gracefully...", style="yellow")
            console.print("Exited", style="red")
            console.print("Every End Is a New Beginning!", style="yellow")
            return

        if choice == "👉 Text Editing":
            text_choice = await inquirer.select(
                message="? Choose a text editing menu:",
                choices=[
                    "👉 Add or Remove Text",
                    "👉 Move Text",
                    "👉 Add/remove prefix on filenames",
                    "👉 Remove brackets from filenames",
                    "👉 Formatting Pirate/Normalize",
                    "👉 Formatting All Caps / Lowered",
                    "👉 Back to main menu",
                ],
            ).execute_async()

            if text_choice == "👉 Back to main menu":
                continue

            folder = await choose_folder()
            if folder == "__BACK__":
                continue
            files = [f for f in folder.iterdir() if is_video_file(f)]

            await handle_text_edit_menu(files, undo_stack, preselected_choice=text_choice)

        elif choice == "👉 Index Repeated Files":
            folder = await choose_folder()
            if folder == "__BACK__":
                continue
            start = time.perf_counter()
            changes = await indexer.index_repeated_keywords(folder)
            duration_ms = (time.perf_counter() - start) * 1000
            if changes:
                undo.add_change_set(changes)
                undo_stack.append(changes)
                console.print(f"✅ Indexed and moved {len(changes)} files.")
                console.print(f"✅ Operation completed in {duration_ms:.2f}ms", style="cyan")
                undo_prompt = await inquirer.select(
                    message="Do you want to undo the changes?",
                    choices=["Y", "N"],
                    default="Y"
                ).execute_async()
                undo_prompt = undo_prompt == "Y"
                if undo_prompt:
                    changes = await undo.undo_last_change_set()
                    console.print(f"↩️ Undid {len(changes)} changes.")
            else:
                console.print("⚠️ No repeated keywords found.")

        elif choice == "👉 Screenshot Parser":
            from refiled.operations import screenshot_parser

            console.print("Step [1/2]: Choose video folder", style="cyan")
            video_folder = await choose_folder()
            if video_folder == "__BACK__":
                continue
            console.print("✅ Step 1 completed", style="green")

            console.print("Step [2/2]: Choose screenshot folder", style="cyan")
            screenshot_folder = await choose_folder()
            if screenshot_folder == "__BACK__":
                continue
            console.print("✅ Step 2 completed", style="green")

            confirm = await inquirer.select(
                message="Do you want to proceed?",
                choices=["Y", "N"],
                default="Y"
            ).execute_async()
            if confirm != "Y":
                continue

            start = time.perf_counter()
            changes = await screenshot_parser.match_and_rename(video_folder, screenshot_folder)
            duration_ms = (time.perf_counter() - start) * 1000

            if changes:
                undo.add_change_set(changes)
                undo_stack.append(changes)
                console.print(f"✅ Renamed {len(changes)} screenshot files.")
                console.print(f"✅ Operation completed in {duration_ms:.2f}ms", style="cyan")

                undo_prompt = await inquirer.select(
                    message="Do you want to undo the changes?",
                    choices=["Y", "N"],
                    default="Y"
                ).execute_async()
                undo_prompt = undo_prompt == "Y"
                if undo_prompt:
                    changes = await undo.undo_last_change_set()
                    console.print(f"↩️ Undid {len(changes)} changes.")
            else:
                console.print("⚠️ No matching screenshots found.")

        elif choice == "👉 Convert Files (.mp4 <-> .mkv)":
            folder = await choose_folder()
            if folder == "__BACK__":
                continue
            files = [f for f in folder.iterdir() if is_video_file(f)]

            convert_ext = await inquirer.select(
                message="Choose conversion format:",
                choices=[".mp4 to .mkv", ".mkv to .mp4"],
            ).execute_async()

            to_ext = ".mkv" if convert_ext == ".mp4 to .mkv" else ".mp4"
            start = time.perf_counter()
            changes = await convert.convert_files(files, to_ext)
            duration_ms = (time.perf_counter() - start) * 1000
            if changes:
                undo.add_change_set(changes)
                undo_stack.append(changes)
                console.print(f"✅ Converted {len(changes)} files to {to_ext}.")
                console.print(f"✅ Operation completed in {duration_ms:.2f}ms", style="cyan")
                undo_prompt = await inquirer.select(
                    message="Do you want to undo the changes?",
                    choices=["Y", "N"],
                    default="Y"
                ).execute_async()
                undo_prompt = undo_prompt == "Y"
                if undo_prompt:
                    changes = await undo.undo_last_change_set()
                    console.print(f"↩️ Undid {len(changes)} changes.")
            else:
                console.print(f"⚠️ No {to_ext} conversion candidates found.")

async def handle_text_edit_menu(files, undo_stack, preselected_choice=None):
    if preselected_choice is None:
        text_choice = await inquirer.select(
            message="? Choose a text editing menu:",
            choices=[
                "👉 Add or Remove Text",
                "👉 Move Text",
                "👉 Add/remove prefix on filenames",
                "👉 Remove brackets from filenames",
                "👉 Formatting Pirate/Normalize",
                "👉 Formatting All Caps / Lowered",
                "👉 Back to main menu",
            ],
        ).execute_async()
        if text_choice == "👉 Back to main menu":
            return
    else:
        text_choice = preselected_choice

    if text_choice == "👉 Add or Remove Text":
        mode = await inquirer.select(message="Add or remove?", choices=["add", "remove"]).execute_async()
        text = await inquirer.text(message=f"Enter text to {mode}:").execute_async()

        filter_mode = await inquirer.select(message="Apply to?", choices=["all", "specific"]).execute_async()
        filter_term = None
        if filter_mode == "specific":
            filter_term = await inquirer.text(message="Enter search term to filter files:").execute_async()

        if mode == "add":
            position = await inquirer.select(message="Position?", choices=["start", "end"]).execute_async()
        else:
            position = None

        reversed_match = await inquirer.confirm(message="Also match reversed order?").execute_async()
        fuzzy = await inquirer.confirm(message="Enable fuzzy matching?").execute_async()

        start = time.perf_counter()
        if mode == "add":
            changes = await add_remove.add_text(files, text, position, fuzzy, reversed_match, filter_mode, filter_term)
        else:
            changes = await add_remove.remove_text(files, text, fuzzy, reversed_match, filter_mode, filter_term)
        duration_ms = (time.perf_counter() - start) * 1000

        if changes:
            undo.add_change_set(changes)
            undo_stack.append(changes)
            console.print(f"✅ Renamed {len(changes)} files.")
            console.print(f"✅ Operation completed in {duration_ms:.2f}ms", style="cyan")
            undo_prompt = await inquirer.select(
                message="Do you want to undo the changes?",
                choices=["Y", "N"],
                default="Y"
            ).execute_async()
            undo_prompt = undo_prompt == "Y"
            if undo_prompt:
                changes = await undo.undo_last_change_set()
                console.print(f"↩️ Undid {len(changes)} changes.")
        else:
            console.print("⚠️ No changes made.")

    elif text_choice == "👉 Move Text":
        console.print("⚠️ Experimental: This operation may not always behave as expected.")
        text = await inquirer.text(message="Enter text to move:").execute_async()
        position = await inquirer.select(message="Position?", choices=["start", "end"]).execute_async()

        filter_mode = await inquirer.select(message="Apply to?", choices=["all", "specific"]).execute_async()
        filter_term = None
        if filter_mode == "specific":
            filter_term = await inquirer.text(message="Enter search term to filter files:").execute_async()

        reversed_match = await inquirer.confirm(message="Also match reversed order?").execute_async()
        fuzzy = await inquirer.confirm(message="Enable fuzzy matching?").execute_async()

        start = time.perf_counter()
        changes = await move.move_text(files, text, position, fuzzy, reversed_match, filter_mode, filter_term)
        duration_ms = (time.perf_counter() - start) * 1000

        if changes:
            undo.add_change_set(changes)
            undo_stack.append(changes)
            console.print(f"✅ Moved text in {len(changes)} files.")
            console.print(f"✅ Operation completed in {duration_ms:.2f}ms", style="cyan")
            undo_prompt = await inquirer.select(
                message="Do you want to undo the changes?",
                choices=["Y", "N"],
                default="Y"
            ).execute_async()
            undo_prompt = undo_prompt == "Y"
            if undo_prompt:
                changes = await undo.undo_last_change_set()
                console.print(f"↩️ Undid {len(changes)} changes.")
        else:
            console.print("⚠️ No changes made.")

    elif text_choice == "👉 Formatting Pirate/Normalize":
        action = await inquirer.select(message="Choose formatting:", choices=["pirate", "normalize"]).execute_async()
        reversed_match = await inquirer.confirm(message="Also match reversed order?").execute_async()
        fuzzy = await inquirer.confirm(message="Enable fuzzy matching?").execute_async()

        start = time.perf_counter()
        if action == "pirate":
            changes = await pirate.pirate_format(files, fuzzy, reversed_match)
        else:
            changes = await pirate.normalize_format(files, fuzzy, reversed_match)
        duration_ms = (time.perf_counter() - start) * 1000

        if changes:
            undo.add_change_set(changes)
            undo_stack.append(changes)
            console.print(f"✅ Renamed {len(changes)} files.")
            console.print(f"✅ Operation completed in {duration_ms:.2f}ms", style="cyan")
            undo_prompt = await inquirer.select(
                message="Do you want to undo the changes?",
                choices=["Y", "N"],
                default="Y"
            ).execute_async()
            undo_prompt = undo_prompt == "Y"
            if undo_prompt:
                changes = await undo.undo_last_change_set()
                console.print(f"↩️ Undid {len(changes)} changes.")
        else:
            console.print("⚠️ No changes made.")

    elif text_choice == "👉 Add/remove prefix on filenames":
        mode = await inquirer.select(message="Add or remove prefix?", choices=["add", "remove"]).execute_async()
        prefix_value = await inquirer.text(message="Enter prefix:").execute_async()

        filter_mode = await inquirer.select(message="Apply to?", choices=["all", "specific"]).execute_async()
        filter_term = None
        if filter_mode == "specific":
            filter_term = await inquirer.text(message="Enter search term to filter files:").execute_async()

        start = time.perf_counter()
        if mode == "add":
            position = await inquirer.select(message="Position?", choices=["start", "end"]).execute_async()
            changes = await prefix.add_prefix(files, prefix_value, position=position, filter_mode=filter_mode, filter_term=filter_term)
        else:
            changes = await prefix.remove_prefix(files, prefix_value, filter_mode=filter_mode, filter_term=filter_term)
        duration_ms = (time.perf_counter() - start) * 1000

        if changes:
            undo.add_change_set(changes)
            undo_stack.append(changes)
            console.print(f"✅ Renamed {len(changes)} files.")
            console.print(f"✅ Operation completed in {duration_ms:.2f}ms", style="cyan")
            undo_prompt = await inquirer.select(
                message="Do you want to undo the changes?",
                choices=["Y", "N"],
                default="Y"
            ).execute_async()
            undo_prompt = undo_prompt == "Y"
            if undo_prompt:
                changes = await undo.undo_last_change_set()
                console.print(f"↩️ Undid {len(changes)} changes.")
        else:
            console.print("⚠️ No changes made.")

    elif text_choice == "👉 Remove brackets from filenames":
        start = time.perf_counter()
        changes = await remove_brackets.remove_brackets(files)
        duration_ms = (time.perf_counter() - start) * 1000
        if changes:
            undo.add_change_set(changes)
            undo_stack.append(changes)
            console.print(f"✅ Renamed {len(changes)} files.")
            console.print(f"✅ Operation completed in {duration_ms:.2f}ms", style="cyan")
            undo_prompt = await inquirer.select(
                message="Do you want to undo the changes?",
                choices=["Y", "N"],
                default="Y"
            ).execute_async()
            undo_prompt = undo_prompt == "Y"
            if undo_prompt:
                changes = await undo.undo_last_change_set()
                console.print(f"↩️ Undid {len(changes)} changes.")
        else:
            console.print("⚠️ No changes made.")

    elif text_choice == "👉 Formatting All Caps / Lowered":
        from refiled.operations import low_caps
        transformation = await inquirer.select(
            message="Choose transformation:",
            choices=["ALL CAPS", "all lowered"]
        ).execute_async()

        start = time.perf_counter()
        if transformation == "ALL CAPS":
            changes = await low_caps.convert_to_all_caps(files)
        else:
            changes = await low_caps.convert_to_all_lower(files)
        duration_ms = (time.perf_counter() - start) * 1000

        if changes:
            undo.add_change_set(changes)
            undo_stack.append(changes)
            console.print(f"✅ Renamed {len(changes)} files.")
            console.print(f"✅ Operation completed in {duration_ms:.2f}ms", style="cyan")
            undo_prompt = await inquirer.select(
                message="Do you want to undo the changes?",
                choices=["Y", "N"],
                default="Y"
            ).execute_async()
            if undo_prompt == "Y":
                changes = await undo.undo_last_change_set()
                console.print(f"↩️ Undid {len(changes)} changes.")
        else:
            console.print("⚠️ No changes made.")

    elif text_choice == "👉 Back to main menu":
        return