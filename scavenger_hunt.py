"""Scavenger hunt for Digital Dudes and Divas"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import random
import signal
import stat
import subprocess
import sys
import time

NEXT_ROOM_MESSAGE = "Congratulations! You unlocked the next room!"
TREASURE_MESSAGE = "Congratulations! You unlocked the treasure!"

SCRIPT_DIR = Path(__file__).resolve().parent
GAME_DIR = Path.home() / "ready_player_root"
FOLDER_STRUCTURE_FILE = SCRIPT_DIR / "folder_structure.readyplayerroot.json"
HINT_STRUCTURE_FILE = SCRIPT_DIR / "hint_structure.readyplayerroot.json"
PID_FILE = SCRIPT_DIR / ".monitor.pid"
MONITOR_SCRIPT = SCRIPT_DIR / "monitor.pyw"


def _make_writable(path: Path):
    """Lets the game change the folder at `path` again if a player locked it with `chmod`"""

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


def _make_folder(path: Path):
    """Creates the folder at `path` if it is missing, replacing anything else in its way"""

    if path.is_symlink() or not path.is_dir():
        _clear(path)
    path.mkdir(parents=True, exist_ok=True)
    _make_writable(path)


class File:
    """A file in the hunt, named by its ID until its room is solved"""

    def __init__(self, name: str, id_: str, contents: str = ""):
        self._name = name
        self._id = id_
        self._contents = contents

    @property
    def name(self):
        """Returns the name of the file"""
        return self._name

    @property
    def id_(self):
        """Returns the ID of the file"""
        return self._id

    @property
    def contents(self):
        """Returns the hint text inside the file"""
        return self._contents

    def place(self, path: Path):
        """Writes the file at `path` unless it is already there, replacing anything else in its way"""
        if path.is_symlink() or path.is_dir():
            _clear(path)
        if not path.exists():
            path.write_text(self._contents + "\n", encoding="utf-8")


class Folder:
    """
    Contains three files and possibly three folders.\n
    The 0th file and the 0th folder are always the correct ones.\n
    If there are three folders, the second and third files must be deleted
    with the first one remaining in order for the three folders to appear.\n
    If there are not three files, it must be the root/start folder.
    """

    def __init__(self, name: str, id_: str,
                 files: tuple[File, ...] = (),
                 folders: tuple[Folder, ...] = (),
                 hint: str | None = None,
                 treasure: File | None = None):
        self._name = name
        self._id = id_
        self._files = files
        self._folders = folders
        self._hint = hint
        self._treasure = treasure

    @property
    def name(self):
        """Returns the name of the folder"""
        return self._name

    @property
    def id_(self):
        """Returns the ID of the folder"""
        return self._id

    @property
    def files(self):
        """Returns files contained in the folder"""
        return self._files

    @property
    def folders(self):
        """Returns folders contained in the folder"""
        return self._folders

    @property
    def hint(self):
        """Returns the hint shown when the player destroys this (correct) folder"""
        return self._hint

    @property
    def treasure(self):
        """Returns the treasure file, which only the last correct folder has"""
        return self._treasure

    @property
    def correct_folder(self):
        """Returns the folder the player has to keep"""
        return self._folders[0]

    @property
    def correct_file(self):
        """Returns the file the player has to keep"""
        return self._files[0]

    def create(self, path: Path):
        """
        Creates the folder at `path` with any of its files that are missing,
        named by their IDs.\n
        Its folders are placed later by the monitor, once this room is solved.
        """
        _make_folder(path)
        for file in random.sample(self._files, len(self._files)):
            file.place(path / file.id_)


def read_folder_structure(file_name: str | Path):
    """Reads a folder or hint structure from a JSON file"""

    with open(file_name, 'r', encoding="utf-8") as folder_structure:
        return json.load(folder_structure)


def parse_folder_structure(folder_structure: dict, hint_structure: dict | None = None,
                           name: str = "start", id_: str = "start") -> Folder:
    """
    Converts a JSON `folder_structure` to a `Folder`.\n
    Names map to IDs; an ID that is also a key holding an object is a folder,
    otherwise it is a file. `hint_structure` mirrors the same IDs.
    """

    if not isinstance(folder_structure, dict):
        raise ValueError(f"`{name}` ({id_}) is a folder, so its folder structure entry "
                         "must be an object")
    if not isinstance(hint_structure, (dict, type(None))):
        raise ValueError(f"`{name}` ({id_}) is a folder, so its hint structure entry "
                         "must be an object")
    hints = hint_structure or {}
    files = []
    folders = []
    treasure = None
    for key, value in folder_structure.items():
        if not isinstance(value, str):
            continue
        if key.lower() == "treasure":
            treasure = File(value, value, _hint_text(hints, "treasure", "the treasure"))
        elif isinstance(folder_structure.get(value), dict):
            folders.append(parse_folder_structure(folder_structure[value],
                                                  hints.get(value), key, value))
        else:
            files.append(File(key, value, _hint_text(hints, value, f"`{key}` ({value})")))
    hint = hints.get("hint")
    if hint is not None and not isinstance(hint, str):
        raise ValueError(f"the hint for `{name}` must be text")
    return Folder(name, id_, tuple(files), tuple(folders), hint, treasure)


def _hint_text(hints: dict, id_: str, label: str) -> str:
    """Returns the hint structure's text for `id_`, which must be a string"""

    text = hints.get(id_, "")
    if not isinstance(text, str):
        raise ValueError(f"{label} needs text in the hint structure, "
                         f"not {type(text).__name__}")
    return text


def _check_name(value: str):
    """Raises `ValueError` if `value` cannot be used as a file or folder name"""

    if value in ("", ".", "..") or "/" in value or "\0" in value:
        raise ValueError(f"`{value}` cannot be used as a file or folder name")


def _validate_folder(folder: Folder):
    """Checks the files and IDs of one of the three folders in a room"""

    if len(folder.files) != 3:
        raise ValueError(f"`{folder.name}` must contain exactly 3 files")
    items = folder.files + folder.folders
    if len({item.id_ for item in items}) != len(items):
        raise ValueError(f"an ID is used twice inside `{folder.name}`")
    for item in items:
        _check_name(item.id_)
    for file in folder.files:
        if not file.contents:
            raise ValueError(f"`{file.name}` ({file.id_}) has no text in the hint structure")


def validate_structure(root: Folder):
    """Raises `ValueError` if `root` is not a playable hunt"""

    room = root
    while room.folders:
        if len(room.folders) != 3 or len({folder.id_ for folder in room.folders}) != 3:
            raise ValueError(f"`{room.name}` must contain exactly 3 folders with different IDs")
        for folder in room.folders:
            _validate_folder(folder)
        for folder in room.folders[1:]:
            if folder.folders or folder.treasure:
                raise ValueError(f"`{folder.name}` is a wrong folder, so it cannot hold "
                                 "folders or treasure")
        correct = room.correct_folder
        if not correct.hint:
            raise ValueError(f"`{correct.name}` needs a hint in the hint structure")
        _check_name(correct.name)
        _check_name(correct.correct_file.name)
        room = correct
    if room is root:
        raise ValueError("the start folder must contain 3 folders")
    if room.treasure is None or not room.treasure.contents:
        raise ValueError(f"`{room.name}` must contain the treasure and its text")
    _check_name(room.treasure.name)


def load_hunt(folder_structure_file: Path, hint_structure_file: Path) -> Folder:
    """Reads, parses, and validates a hunt from its folder and hint structure files"""

    root = parse_folder_structure(read_folder_structure(folder_structure_file),
                                  read_folder_structure(hint_structure_file))
    validate_structure(root)
    return root


def _rename(source: Path, target: Path) -> Path:
    """Renames `source` to `target`, replacing anything the player made at `target`"""

    if source == target:
        return target
    _clear(target)
    return source.rename(target)


class Game:
    """
    Tracks which room the player is solving and reacts to what they delete.\n
    The monitor is the only thing that renames or creates game folders, so
    after it does, it forgets what it last saw and watches the new room fresh.
    """

    def __init__(self, root: Folder, game_dir: Path):
        self._game_dir = game_dir
        self._room = root
        self._room_dir = game_dir
        self._unlocked: list[tuple[Path, File]] = []
        self._last_snapshot: frozenset[Path] | None = None
        self._finished = False

    @property
    def finished(self):
        """Returns whether the treasure has been unlocked"""
        return self._finished

    def setup(self):
        """Deletes any old game and creates the first room"""
        _clear(self._room_dir)
        _make_folder(self._room_dir)
        self._create_room()

    def poll(self) -> str | None:
        """
        Checks the game folder once and returns a popup message if something
        happened, otherwise `None`.\n
        Nothing happens until the folders look the same on two polls in a row,
        so the monitor never reacts in the middle of an `rm -r`.
        """
        if self._finished:
            return None
        snapshot = self._snapshot()
        if snapshot != self._last_snapshot:
            self._last_snapshot = snapshot
            return None
        message = self._check()
        if message is not None:
            self._last_snapshot = None
        return message

    def _create_room(self):
        """
        Creates the current room's three folders and any of their missing files.\n
        They are made in a random order so `ls -t` can't give away the answer.
        """
        for folder in random.sample(self._room.folders, len(self._room.folders)):
            folder.create(self._room_dir / folder.id_)

    def _snapshot(self) -> frozenset[Path]:
        """Returns every path the game cares about that currently exists"""
        paths = [self._room_dir]
        for directory, key in self._unlocked:
            paths += [directory, directory / key.name]
        for folder in self._room.folders:
            folder_dir = self._room_dir / folder.id_
            paths.append(folder_dir)
            paths += [folder_dir / file.id_ for file in folder.files]
        return frozenset(path for path in paths if path.exists())

    def _check(self) -> str | None:
        """Resets the room after a wrong deletion, or unlocks it once it is solved"""
        correct = self._room.correct_folder
        correct_dir = self._room_dir / correct.id_
        progress_intact = self._room_dir.is_dir() and all(
            (directory / key.name).is_file() for directory, key in self._unlocked)
        if not progress_intact or not (correct_dir / correct.correct_file.id_).is_file():
            self._restore()
            return correct.hint
        wrong_paths = [self._room_dir / folder.id_ for folder in self._room.folders[1:]]
        wrong_paths += [correct_dir / file.id_ for file in correct.files[1:]]
        if any(path.exists() for path in wrong_paths):
            return None
        return self._unlock()

    def _restore(self):
        """Puts back the rooms and keys already unlocked, then resets the current room"""
        _make_folder(self._game_dir)
        for directory, key in self._unlocked:
            _make_folder(directory)
            key.place(directory / key.name)
        self._create_room()

    def _unlock(self) -> str:
        """Renames the solved folder and key to their real names and places what comes next"""
        correct = self._room.correct_folder
        key = correct.correct_file
        _make_writable(self._room_dir)
        _make_writable(self._room_dir / correct.id_)
        folder_dir = _rename(self._room_dir / correct.id_, self._room_dir / correct.name)
        _rename(folder_dir / key.id_, folder_dir / key.name)
        self._unlocked.append((folder_dir, key))
        self._room = correct
        self._room_dir = folder_dir
        if correct.folders:
            self._create_room()
            return NEXT_ROOM_MESSAGE
        correct.treasure.place(folder_dir / correct.treasure.name)
        self._finished = True
        return TREASURE_MESSAGE


def _is_monitor(pid: int) -> bool:
    """Returns whether process `pid` is this project's running `monitor.pyw`"""

    result = subprocess.run(["ps", "-ww", "-p", str(pid), "-o", "command="],
                            capture_output=True, text=True, check=False)
    return str(MONITOR_SCRIPT) in result.stdout


def monitor_pid(pid_file: Path = PID_FILE) -> int | None:
    """Returns the PID of the running monitor, or `None` if it is not running"""

    try:
        pid = int(pid_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return pid if _is_monitor(pid) else None


def start_monitor(game_dir: Path, folder_structure_file: Path = FOLDER_STRUCTURE_FILE,
                  hint_structure_file: Path = HINT_STRUCTURE_FILE,
                  pid_file: Path = PID_FILE) -> int:
    """Starts `monitor.pyw` in the background, saves its PID, and returns it"""

    with open(pid_file.with_suffix(".log"), "a", encoding="utf-8") as log:
        process = subprocess.Popen(  # pylint: disable=consider-using-with
            [sys.executable, str(MONITOR_SCRIPT), str(game_dir),
             str(folder_structure_file), str(hint_structure_file)],
            stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
    pid_file.write_text(str(process.pid), encoding="utf-8")
    return process.pid


def stop_monitor(pid_file: Path = PID_FILE) -> bool:
    """Stops the monitor if it is running and returns whether it was"""

    pid = monitor_pid(pid_file)
    pid_file.unlink(missing_ok=True)
    if pid is None:
        return False
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return False
    for _ in range(50):
        if not _is_monitor(pid):
            break
        time.sleep(0.1)
    return True


def main(argv: list[str] | None = None) -> int:
    """Runs the `start` or `stop` command"""

    parser = argparse.ArgumentParser(description="Ready Player Root scavenger hunt")
    parser.add_argument("command", choices=("start", "stop"))
    args = parser.parse_args(argv)

    if args.command == "stop":
        print("Stopped the monitor" if stop_monitor() else "The monitor is not running")
        return 0

    try:
        root = load_hunt(FOLDER_STRUCTURE_FILE, HINT_STRUCTURE_FILE)
    except (OSError, ValueError) as error:
        print(f"Could not load the hunt: {error}")
        return 1
    stop_monitor()
    Game(root, GAME_DIR).setup()
    start_monitor(GAME_DIR)
    print(f"Ready Player Root is ready! Players start with: cd {GAME_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
