"""Scavenger hunt for Digital Dudes and Divas"""

import json
from pprint import pprint
from pathlib import Path

class Folder:
    """
    Contains possibly three files and possibly three folders.\n
    If there are three folders, the second and third files must be deleted
    with the the first one remaining in order for the three folders to appear.\n
    If there are not three files, it must be the root/start folder.
    """
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

def read_folder_structure(file_name: str | None = None):
    """Reads a folder structure from a file"""

    if file_name is None:
        file_name = "folder_structure.json"

    with open(file_name, 'r', encoding="utf-8") as folder_structure:
        return json.load(folder_structure)

def print_folder_structure(folder_structure):
    """Prints a JSON `folder_structure` by `list`"""

    root_keys = list(folder_structure.keys())
    print(f"{root_keys = }")
    folder0_0_keys = list(folder_structure[root_keys[1]])
    print(f"{folder0_0_keys = }")
    folder0_1_keys = list(folder_structure[root_keys[3]])
    print(f"{folder0_1_keys = }")
    folder0_2_keys = list(folder_structure[root_keys[5]])
    print(f"{folder0_2_keys = }")
    folder1_0_keys = list(folder_structure[root_keys[1]][folder0_0_keys[4]])
    print(f"{folder1_0_keys = }")
    folder1_1_keys = list(folder_structure[root_keys[1]][folder0_0_keys[6]])
    print(f"{folder1_1_keys = }")
    folder1_2_keys = list(folder_structure[root_keys[1]][folder0_0_keys[8]])
    print(f"{folder1_2_keys = }")
    folder2_0_keys = list(folder_structure[root_keys[1]][folder0_0_keys[4]][folder1_0_keys[4]])
    print(f"{folder2_0_keys = }")
    folder2_1_keys = list(folder_structure[root_keys[1]][folder0_0_keys[4]][folder1_0_keys[6]])
    print(f"{folder2_1_keys = }")
    folder2_2_keys = list(folder_structure[root_keys[1]][folder0_0_keys[4]][folder1_0_keys[8]])
    print(f"{folder2_2_keys = }")

def parse_folder_structure(folder_structure):
    """Converts a JSON `folder_structure` to a `Folder`"""

    root_keys = list(folder_structure.keys())
    folder0_0_keys = list(folder_structure[root_keys[1]])
    folder0_1_keys = list(folder_structure[root_keys[3]])
    folder0_2_keys = list(folder_structure[root_keys[5]])
    folder1_0_keys = list(folder_structure[root_keys[1]][folder0_0_keys[4]])
    folder1_1_keys = list(folder_structure[root_keys[1]][folder0_0_keys[6]])
    folder1_2_keys = list(folder_structure[root_keys[1]][folder0_0_keys[8]])
    folder2_0_keys = list(folder_structure[root_keys[1]][folder0_0_keys[4]][folder1_0_keys[4]])
    folder2_1_keys = list(folder_structure[root_keys[1]][folder0_0_keys[4]][folder1_0_keys[6]])
    folder2_2_keys = list(folder_structure[root_keys[1]][folder0_0_keys[4]][folder1_0_keys[8]])

    root = Folder("start", "start")
    folder0_0 = Folder(root_keys[0], root_keys[1],
                       (folder0_0_keys[0], folder0_0_keys[1], folder0_0_keys[2]))
    folder0_1 = Folder(root_keys[2], root_keys[3],
                       (folder0_1_keys[0], folder0_1_keys[1], folder0_1_keys[2]))
    folder0_2 = Folder(root_keys[4], root_keys[5],
                       (folder0_2_keys[0], folder0_2_keys[1], folder0_2_keys[2]))
    folder1_0 = Folder(folder0_0_keys[3], folder0_0_keys[4],
                       (folder1_0_keys[0], folder1_0_keys[1], folder1_0_keys[2]))
    folder1_1 = Folder(folder0_0_keys[5], folder0_0_keys[6],
                       (folder1_1_keys[0], folder1_1_keys[1], folder1_1_keys[2]))
    folder1_2 = Folder(folder0_0_keys[7], folder0_0_keys[8],
                       (folder1_2_keys[0], folder1_2_keys[1], folder1_2_keys[2]))
    folder2_0 = Folder(folder1_0_keys[3], folder1_0_keys[4],
                       (folder2_0_keys[0], folder2_0_keys[1], folder2_0_keys[2]))
    folder2_1 = Folder(folder1_0_keys[5], folder1_0_keys[6],
                       (folder2_1_keys[0], folder2_1_keys[1], folder2_1_keys[2]))
    folder2_2 = Folder(folder1_0_keys[7], folder1_0_keys[8],
                       (folder2_2_keys[0], folder2_2_keys[1], folder2_2_keys[2]))

    folder1_0.folders = (folder2_0, folder2_1, folder2_2)
    folder0_0.folders = (folder1_0, folder1_1, folder1_2)
    root.folders = (folder0_0, folder0_1, folder0_2)

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

    pprint(folder_structure)

    parse_folder_structure(folder_structure)

    print("folder structure keys")
    pprint(folder_structure.keys())

    root_keys = list(folder_structure.keys())
    folder0_keys = folder_structure[root_keys[1]].keys()
    print("folder0 keys")
    pprint(folder0_keys)

if __name__ == "__main__":
    main()
