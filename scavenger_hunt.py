"""Scavenger hunt for Digital Dudes and Divas"""

import json
from pprint import pprint
from pathlib import Path

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

if __name__ == "__main__":
    main()
