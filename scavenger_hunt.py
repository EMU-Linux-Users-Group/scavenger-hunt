"""Scavenger hunt for Digital Dudes and Divas"""

import json
from pprint import pprint
from pathlib import Path

class Folder:
    """
    Contains three files and possibly three folders.
    If there are three folders, the second and third files must be deleted
    with the the first one remaining in order for the three folders to appear
    """
    def __init__(self, name: str, id_: str,
                 file_names: tuple[str, str, str],
                 folder_names: tuple[str, str, str] | None = None):
        self._name = name
        self._id = id_
        self._file_names = file_names
        self._folder_names = folder_names

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
    def folder_names(self):
        """Returns folder names contained in the folder"""
        return self._folder_names

class FolderStructure:
    """Contains folders to fully map out a folder structure"""
    def __init__(self, folder_structure: dict):
        root_keys = list(folder_structure.keys())
        root_id_key_indexes = [1, 3, 5]

        self._folders = []

        for i in range(3):
            folder_keys = list(folder_structure[root_keys[root_id_key_indexes[i]]].keys())
            self._folders[i] = Folder(root_keys[root_id_key_indexes[i] - 1],
                                      root_keys[root_id_key_indexes[i]],
                                      (folder_keys[0], folder_keys[1], folder_keys[2]))

    @property
    def folders(self):
        """Returns the folders within the structure"""
        return self._folders

    def folder(self, _id):
        """Retrieves a folder by its ID"""
        raise NotImplementedError

def read_folder_structure(file_name: str | None = None):
    """Reads a folder structure from a file"""

    if file_name is None:
        file_name = "folder_structure.json"

    with open(file_name, 'r', encoding="utf-8") as folder_structure:
        return json.load(folder_structure)

def create_folders_and_files_from_folder_structure(folder_structure, folder_path):
    """Creates the folders and files specified by `folder_structure` into `folder_path`"""
    folder_names = folder_structure.keys()
    for i in len(folder_names):
        i += 1
        folder = Path(f"{folder_path}/{folder_names[i]}")
        folder.mkdir(parents=True, exist_ok=True)

def main():
    """The main function"""

    try:
        folder_structure = read_folder_structure("folder_structure.example.json")
    except json.decoder.JSONDecodeError:
        print("Invalid JSON file")
        return

    pprint(folder_structure)

    print("folder structure keys")
    pprint(folder_structure.keys())

    root_keys = list(folder_structure.keys())
    folder0_keys = folder_structure[root_keys[1]].keys()
    print("folder0 keys")
    pprint(folder0_keys)

if __name__ == "__main__":
    main()
