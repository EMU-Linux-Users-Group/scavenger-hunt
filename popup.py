"""
Shows Stranger Pings popups with whatever the computer has.\n
The game runs this file in the background (`spawn`) so the student's prompt
never waits for anyone to click OK.
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import sys

TITLE = "Stranger Pings"


def popup_methods(style: str, platform: str) -> list[str]:
    """
    Returns the ways to show a popup, best first.\n
    On a Mac, `tk` is the backup a helper can switch to if the normal
    popups misbehave (`stranger-pings popups tk`).
    """

    if platform == "darwin":
        return ["tk", "osascript", "print"] if style == "tk" else ["osascript", "tk", "print"]
    return ["tk", "zenity", "print"]


def _osascript(message: str) -> bool:
    """Shows `message` in a macOS dialog and returns whether it worked"""

    if not shutil.which("osascript"):
        return False
    import subprocess  # pylint: disable=import-outside-toplevel
    result = subprocess.run(["osascript", "-e", "on run argv", "-e",
                             'display dialog (item 1 of argv) with title (item 2 of argv) '
                             'buttons {"OK"} default button 1',
                             "-e", "end run", message, TITLE], check=False)
    return result.returncode == 0


def _tk(message: str) -> bool:
    """Shows `message` in a window that stays on top, and returns whether it worked"""

    try:
        import tkinter  # pylint: disable=import-outside-toplevel
    except ImportError:
        return False
    try:
        window = tkinter.Tk()
        window.title(TITLE)
        window.resizable(False, False)
        window.attributes("-topmost", True)
        tkinter.Label(window, text=message, wraplength=380, justify="left",
                      font=("Helvetica", 16), padx=28, pady=22).pack()
        button = tkinter.Button(window, text="OK", width=10, command=window.destroy)
        button.pack(pady=(0, 18))
        window.bind("<Return>", lambda _event: window.destroy())
        window.update_idletasks()
        x = (window.winfo_screenwidth() - window.winfo_width()) // 2
        y = (window.winfo_screenheight() - window.winfo_height()) // 3
        window.geometry(f"+{x}+{y}")
        window.lift()
        window.focus_force()
        button.focus_set()
        window.mainloop()
    except tkinter.TclError:
        return False
    return True


def _zenity(message: str) -> bool:
    """Shows `message` with zenity (Linux) and returns whether it worked"""

    if not shutil.which("zenity"):
        return False
    import subprocess  # pylint: disable=import-outside-toplevel
    result = subprocess.run(["zenity", "--info", "--no-markup", "--title", TITLE,
                             "--text", message], check=False)
    return result.returncode in (0, 1)


def _print(message: str) -> bool:
    """Prints `message` when nothing else can show it"""

    print(message, flush=True)
    return True


_METHODS = {"osascript": _osascript, "tk": _tk, "zenity": _zenity, "print": _print}


def show(message: str, style: str):
    """
    Shows `message` in a popup and waits for it to be closed.\n
    With `STRANGER_PINGS_POPUP_LOG` set (the tests set it), the message is added
    to that file instead.
    """

    log = os.environ.get("STRANGER_PINGS_POPUP_LOG")
    if log:
        with open(log, "a", encoding="utf-8") as file:
            file.write(message + "\n")
        return
    for method in popup_methods(style, sys.platform):
        if _METHODS[method](message):
            return


def spawn(message: str, style: str):
    """Shows `message` from a separate background process, without waiting for it"""

    import subprocess  # pylint: disable=import-outside-toplevel
    subprocess.Popen(  # pylint: disable=consider-using-with
        [sys.executable, "-E", "-s", str(Path(__file__).resolve()), style, message],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True)


if __name__ == "__main__":
    show(sys.argv[2], sys.argv[1])
