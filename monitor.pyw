"""
Background monitor for the scavenger hunt.\n
Started by `python3 scavenger_hunt.py start`; it watches the game folder and
shows popups until the treasure is unlocked.
"""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
import time

from scavenger_hunt import Game, load_hunt

TITLE = "Ready Player Root"
POLL_SECONDS = 0.5


def _show_tkinter_popup(message: str) -> bool:
    """Shows `message` with tkinter and returns whether it worked"""
    try:
        import tkinter  # pylint: disable=import-outside-toplevel
        from tkinter import messagebox  # pylint: disable=import-outside-toplevel
    except ImportError:
        return False
    try:
        window = tkinter.Tk()
        window.withdraw()
        window.attributes("-topmost", True)
        messagebox.showinfo(TITLE, message, parent=window)
        window.destroy()
    except tkinter.TclError:
        return False
    return True


def show_popup(message: str):
    """Shows `message` in a popup using whatever this computer has"""
    if shutil.which("osascript"):
        subprocess.run(["osascript", "-e", "on run argv", "-e",
                        'display dialog (item 1 of argv) with title (item 2 of argv) '
                        'buttons {"OK"} default button 1',
                        "-e", "end run", message, TITLE], check=False)
    elif not _show_tkinter_popup(message):
        if shutil.which("zenity"):
            subprocess.run(["zenity", "--info", "--no-markup", "--title", TITLE,
                            "--text", message], check=False)
        else:
            print(message, flush=True)


def main():
    """Polls the game folder until the treasure is unlocked"""
    game_dir, folder_structure_file, hint_structure_file = (Path(arg) for arg in sys.argv[1:4])
    game = Game(load_hunt(folder_structure_file, hint_structure_file), game_dir)
    while not game.finished:
        message = game.poll()
        if message:
            show_popup(message)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
