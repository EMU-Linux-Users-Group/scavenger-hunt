"""
The folders and files of each student's game.\n
Hawkins (`~/hawkins`) is there from the start. After the cat slide, the student
is pulled into its mirror in the Upside Down (`~/upside_down/hawkins`), which
looks the same from the prompt.
"""

from __future__ import annotations

from pathlib import Path
import stat

import story

PULLED_IN = story.COMMANDS.index("pwd")         # first step spent in the Upside Down
CASTLE_BUILT = story.COMMANDS.index("cd")       # first step after mkdir
EGGOS_DELIVERED = story.COMMANDS.index("rm")    # first step after cp
DEMOGORGON_GONE = story.COMMANDS.index("rmdir")  # first step after rm
FINISHED = len(story.COMMANDS)
DEMOGORGON = "upside_down/hawkins/gate/demogorgon"
EGGOS = "upside_down/hawkins/eggos"


def hawkins(home: Path) -> Path:
    """Returns where Hawkins is"""
    return home / "hawkins"


def mirror(home: Path) -> Path:
    """Returns where the Upside Down's copy of Hawkins is"""
    return home / "upside_down" / "hawkins"


def castle(home: Path) -> Path:
    """Returns where the student builds Castle Byers"""
    return mirror(home) / "castle_byers"


def gate(home: Path) -> Path:
    """Returns where the gate is"""
    return mirror(home) / "gate"


def start_folder(step: int, home: Path) -> Path:
    """Returns the folder a student at `step` belongs in"""
    return hawkins(home) if step < PULLED_IN else mirror(home)


def _make_writable(path: Path):
    """Lets the game change the folder at `path` again if a student locked it with `chmod`"""

    path.chmod(stat.S_IMODE(path.stat().st_mode) | stat.S_IRWXU)


def _clear(path: Path):
    """
    Deletes whatever is at `path`, even folders locked with `chmod`.\n
    Symlinks are deleted without touching what they point to.
    """

    if path.is_dir() and not path.is_symlink():
        _make_writable(path)
        for child in path.iterdir():
            _clear(child)
        path.rmdir()
    elif path.is_symlink() or path.exists():
        path.unlink()


def _folder(path: Path):
    """Makes sure a real, usable folder is at `path`, replacing anything else in its way"""

    if path.is_symlink() or not path.is_dir():
        _clear(path)
    path.mkdir(exist_ok=True)
    _make_writable(path)


def _file(path: Path, text: str):
    """Makes sure the file at `path` holds `text`, replacing anything else in its way"""

    contents = text + "\n"
    if path.is_symlink() or path.exists():
        try:
            unchanged = path.is_file() and path.read_text(encoding="utf-8") == contents
        except (OSError, UnicodeDecodeError):
            unchanged = False
        if unchanged:
            return
        _clear(path)
    path.write_text(contents, encoding="utf-8")


def _place(home: Path, relative: str, text: str):
    """Puts the game file at `relative` (inside `home`) back the way the story has it"""

    *folders, name = relative.split("/")
    folder = home
    for part in folders:
        folder = folder / part
        _folder(folder)
    _file(folder / name, text)


def prepare(step: int, home: Path):
    """
    Builds or repairs the world so it looks the way the slide for `step` expects,
    as if the student had done every earlier step.\n
    Only the game's own files and folders are touched.
    """

    for relative, text in story.FILES.items():
        if relative.startswith("hawkins/"):
            _place(home, relative, text)
    upside_down = home / "upside_down"
    if step < PULLED_IN:
        _clear(upside_down)
        return

    for relative, text in story.FILES.items():
        if relative.startswith("upside_down/") and relative != DEMOGORGON:
            _place(home, relative, text)
    if step < DEMOGORGON_GONE:
        _place(home, DEMOGORGON, story.FILES[DEMOGORGON])
    elif step < FINISHED:
        _folder(gate(home))
        _clear(gate(home) / "demogorgon")

    if step < CASTLE_BUILT:
        _clear(castle(home))
    else:
        _folder(castle(home))
        if step >= EGGOS_DELIVERED and not (castle(home) / "eggos").exists():
            _file(castle(home) / "eggos", story.FILES[EGGOS])


def wipe(home: Path):
    """Deletes the whole world, leaving the rest of the home folder alone"""

    _clear(hawkins(home))
    _clear(home / "upside_down")
