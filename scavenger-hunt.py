def read_folder_structure(file_name: str | None = None):
    if file_name is None:
        file_name = "folder_structure.txt"

    with open(file_name, 'r') as folder_structure:
        return folder_structure.readlines()

def parse_folder_structure(folder_structure):
    ...

def create_folders_and_files_from_folder_structure(folder_structure, folder_path):
    ...

def main():
    raw_folder_structure = read_folder_structure("folder_structure.example.txt")
    print(raw_folder_structure)

if __name__ == "__main__":
    main()
