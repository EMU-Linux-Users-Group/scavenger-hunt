# Scavenger Hunt Devlog

## 10/22/26 - 1:35 AM - Nate Rupard
- Got the repo up and running
- Got the script started
- Got a format going for the folder/file parsing
- Started a test folder structure for future testing

## 10/22/26 - 1:57 AM - Nate Rupard
- Continued the test folder structure
- Started the folder structure for Ready Player Root
- Continued the skeleton for the script
- Fixed an issue in the example

## 10/22/26 - 9:51 PM - Nate Rupard
- Renamed scavenger-hunt.py to scavenger_hunt.py according to pylint
- Added docstrings to all the functions
- Temporarily gave certain variables an `_` because they are not used yet

## 10/22/26 - 10:52 PM - Nate Rupard
- Changed custom folder structure format to JSON
- Added JSON versions of the .txt files for the previous format
    - Kept previous format .txt files for future reference
- Updated the `read_folder_structure` function to use JSON
- Started work on the `create_folders_and_files_from_folder_structure` function
- Imported the `json`, `pprint`, and `pathlib` libraries
    - `json`
    - `pprint` from `pprint`
    - `Path` from `pathlib`

## 10/22/26 - 10:56 PM - Nate Rupard
- Updated devlog entries to include time

## 10/22/26 - 11:45 PM - Nate Rupard
- Created the `Folder` and `FolderStructure` classes with future intentions to 
  use them to map out the JSON dict returned from the JSON files
