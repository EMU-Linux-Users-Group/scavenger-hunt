"""Scavenger hunt for Digital Dudes and Divas"""
# NOTE: the `_` prefix in the `_folder_structure` and `_folder_path` variables
#       shall be removed once they are actually used

def read_folder_structure(file_name: str | None = None):
    """Reads a folder structure from a file"""

    if file_name is None:
        file_name = "folder_structure.txt"

    with open(file_name, 'r', encoding="UTF-8") as folder_structure:
        return folder_structure.readlines()

def parse_folder_structure(_folder_structure):
    """Parses the raw folder structure contents returned by `read_folder_structure`"""

def create_folders_and_files_from_folder_structure(_folder_structure, _folder_path):
    """Creates the folders and files specified by `folder_structure` into `folder_path`"""

def main():
    """The main function"""

    raw_folder_structure = read_folder_structure("folder_structure.example.txt")
    print(raw_folder_structure)

if __name__ == "__main__":
    main()
