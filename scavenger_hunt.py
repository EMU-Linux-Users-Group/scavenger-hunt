"""Scavenger hunt for Digital Dudes and Divas"""

import json
from pprint import pprint
from pathlib import Path
import shutil

class Folder:
    """
    Contains possibly three files and possibly three folders.\n
    If there are three folders, the second and third files must be deleted
    with the the first one remaining in order for the three folders to appear.\n
    If there are not three files, it must be the root/start folder.
    """

    NO_ERROR = 0
    CANNOT_MODIFY = 1

    def __init__(self, name: str, id_: str,
                 file_names: tuple[str, str, str] | None = None,
                 folders: tuple[Folder, Folder, Folder] | None = None):
        self._name = name
        self._id = id_
        self._file_names = file_names
        self._folders = folders

    @property
    def name(self):
        """Returns the name of the folder"""
        return self._name

    @property
    def id_(self):
        """Returns the ID of the folder"""
        return self._id

    @property
    def file_names(self):
        """Returns file names contained in the folder"""
        return self._file_names

    @property
    def folders(self):
        """Returns folders contained in the folder"""
        return self._folders

    @folders.setter
    def folders(self, value):
        """Sets `self._folders` to `value`"""
        self._folders = value

    def create(self, path: Path):
        """Creates the folder in an actual directory dictated by `path`"""

        if path.exists():
            choice = input(f"Delete `{path}`? (y/N)\n>")
            if choice in ('y', 'Y'):
                shutil.rmtree(path)
            else:
                return self.CANNOT_MODIFY

        path.mkdir()

        folders = [
            path / self._folders[0].id_,
            path / self._folders[1].id_,
            path / self._folders[2].id_,
            path / Path(self._folders[0].id_) / self._folders[0].folders[0].id_,
            path / Path(self._folders[0].id_) / self._folders[0].folders[1].id_,
            path / Path(self._folders[0].id_) / self._folders[0].folders[2].id_,
            path / Path(self._folders[0].id_) / Path(self._folders[0].folders[0].id_)
                 / self._folders[0].folders[0].folders[0].id_,
            path / Path(self._folders[0].id_) / Path(self._folders[0].folders[0].id_)
                 / self._folders[0].folders[0].folders[1].id_,
            path / Path(self._folders[0].id_) / Path(self._folders[0].folders[0].id_)
                 / self._folders[0].folders[0].folders[2].id_
        ]

        for folder in folders:
            folder.mkdir()

        return self.NO_ERROR

def read_folder_structure(file_name: str | None = None):
    """Reads a folder structure from a file"""

    if file_name is None:
        file_name = "folder_structure.json"

    with open(file_name, 'r', encoding="utf-8") as folder_structure:
        return json.load(folder_structure)

def print_folder_structure(folder_structure):
    """Prints a JSON `folder_structure` by `list`"""

    root_keys = list(folder_structure.keys())
    folder0_0_keys = list(folder_structure[root_keys[1]])
    folder1_0_keys = list(folder_structure[root_keys[1]][folder0_0_keys[4]])
    folder_keys = [
        list(folder_structure[root_keys[3]]),
        list(folder_structure[root_keys[5]]),
        list(folder_structure[root_keys[1]][folder0_0_keys[6]]),
        list(folder_structure[root_keys[1]][folder0_0_keys[8]]),
        list(folder_structure[root_keys[1]][folder0_0_keys[4]][folder1_0_keys[4]]),
        list(folder_structure[root_keys[1]][folder0_0_keys[4]][folder1_0_keys[6]]),
        list(folder_structure[root_keys[1]][folder0_0_keys[4]][folder1_0_keys[8]])
    ]

    print(f"{root_keys      = }")
    print(f"{folder0_0_keys = }")
    for i, folder in enumerate(folder_keys):
        print(f"folder 0{i} keys = {folder}")
        if i == 3:
            print(f"{folder1_0_keys = }")


def parse_folder_structure(folder_structure):
    """Converts a JSON `folder_structure` to a `Folder`"""

    root_keys = list(folder_structure.keys())
    folder0_0_keys = list(folder_structure[root_keys[1]])
    folder1_0_keys = list(folder_structure[root_keys[1]][folder0_0_keys[4]])
    folder_keys = [
        list(folder_structure[root_keys[3]]),
        list(folder_structure[root_keys[5]]),
        list(folder_structure[root_keys[1]][folder0_0_keys[6]]),
        list(folder_structure[root_keys[1]][folder0_0_keys[8]]),
        list(folder_structure[root_keys[1]][folder0_0_keys[4]][folder1_0_keys[4]]),
        list(folder_structure[root_keys[1]][folder0_0_keys[4]][folder1_0_keys[6]]),
        list(folder_structure[root_keys[1]][folder0_0_keys[4]][folder1_0_keys[8]])
    ]

    root = Folder("start", "start")
    folders = [
        Folder(root_keys[0], root_keys[1],
                        (folder0_0_keys[0], folder0_0_keys[1], folder0_0_keys[2])),
        Folder(root_keys[2], root_keys[3],
                        (folder_keys[0][0], folder_keys[0][1], folder_keys[0][2])),
        Folder(root_keys[4], root_keys[5],
                        (folder_keys[1][0], folder_keys[1][1], folder_keys[1][2])),
        Folder(folder0_0_keys[3], folder0_0_keys[4],
                        (folder1_0_keys[0], folder1_0_keys[1], folder1_0_keys[2])),
        Folder(folder0_0_keys[5], folder0_0_keys[6],
                        (folder_keys[2][0], folder_keys[2][1], folder_keys[2][2])),
        Folder(folder0_0_keys[7], folder0_0_keys[8],
                        (folder_keys[3][0], folder_keys[3][1], folder_keys[3][2])),
        Folder(folder1_0_keys[3], folder1_0_keys[4],
                        (folder_keys[4][0], folder_keys[4][1], folder_keys[4][2])),
        Folder(folder1_0_keys[5], folder1_0_keys[6],
                        (folder_keys[5][0], folder_keys[5][1], folder_keys[5][2])),
        Folder(folder1_0_keys[7], folder1_0_keys[8],
                        (folder_keys[6][0], folder_keys[6][1], folder_keys[6][2]))
    ]

    folders[3].folders = (folders[6], folders[7], folders[8])
    folders[0].folders = (folders[3], folders[4], folders[5])
    root.folders = (folders[0], folders[1], folders[2])

    return root

def create_folder(folder, folder_path):
    """Creates the folders and files specified by `folder` into `folder_path`"""
    folder_names = folder.keys()
    for i in len(folder_names):
        i += 1
        folder = Path(f"{folder_path}/{folder_names[i]}")
        folder.mkdir(parents=True, exist_ok=True)

def main():
    """The main function"""

    try:
        folder_structure = read_folder_structure("folder_structure.test.json")
    except json.decoder.JSONDecodeError:
        print("Invalid JSON file")
        return

    print_folder_structure(folder_structure)
    parse_folder_structure(folder_structure)

if __name__ == "__main__":
    main()
