"""Scavenger hunt for Digital Dudes and Divas"""

from __future__ import annotations

import json
from pathlib import Path
import shutil


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
        """Writes the file at `path` unless it is already there, replacing a folder in its way"""
        if path.is_dir():
            shutil.rmtree(path)
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
        if path.exists() and not path.is_dir():
            path.unlink()
        path.mkdir(parents=True, exist_ok=True)
        for file in self._files:
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

    hints = hint_structure or {}
    files = []
    folders = []
    treasure = None
    for key, value in folder_structure.items():
        if not isinstance(value, str):
            continue
        if key.lower() == "treasure":
            treasure = File(value, value, hints.get("treasure", ""))
        elif isinstance(folder_structure.get(value), dict):
            folders.append(parse_folder_structure(folder_structure[value],
                                                  hints.get(value), key, value))
        else:
            files.append(File(key, value, hints.get(value, "")))
    return Folder(name, id_, tuple(files), tuple(folders), hints.get("hint"), treasure)


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


def main():
    """The main function (temporary until the commands are added)"""

    root = load_hunt(Path("folder_structure.test.json"), Path("hint_structure.test.json"))
    print(f"Loaded the `{root.correct_folder.name}` hunt")

if __name__ == "__main__":
    main()
