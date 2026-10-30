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

## 10/27/26 - 4:29 PM - Nate Rupard
- Removed FolderStructure class
- Integrated FolderStructure functionality into Folder
- Fixed folder_structure.example.json
- Added `parse_folder_structure`
- Added `folders` setter to `Folder`
- Added `print_folder_structure` for easier debugging
- Added TODO.md
- Changed `create_folders_and_files_from_folder_structure` to `create_folder`

## 10/27/26 - 4:34 PM - Nate Rupard
- Fixed (but dnf) folder_structure.readyplayerroot.json

## 10/27/26 - 4:45 PM - Nate Rupard
- Updated TODO.md
- After several minutes of contemplation, I decided to revert the merge 
  between the 4:34 and 4:29 logs

## 10/27/26 - 6:21 PM - Nate Rupard
- Updated TODO.md
- Added COMMANDS.md
- Added monitor.pyw
- Deleted TXT files

## 10/27/26 - 8:06 PM - Nate Rupard
- Updated TODO.md
- Changed `create_folder` to `Folder.create`
- Imported `shutil`
- Finished but did not test `Folder.create`
    - This **hopefully** achieved checks 2 and 3* for today's TODO (*Update 10:58 PM: checks 2 and 3 are now 1 and 2)
- Cleaned up `parse_folder_structure` and made it pylint-compliant
- Cleaned up `print_folder_structure` and it now prints different variable 
  names
- `main` now only prints with `print_folder_structure`

## 10/27/26 - 11:02 PM - Nate Rupard
- Formally removed `create_folder`
- Removed `pprint`
- Fixed `Folder.create`
- As a test, the main function now creates a folder in "./test_folder"
- Updated TODO.md
    - Moved monitor functionality to the end of Wednesday
- Notes for the next couple days
    - We need a separate JSON file that mirrors the folder structure that gives
      hints and correct and incorrect information

## 10/28/26 - 9:23 PM - Isaac Mullison (filled in 10/29/26, 4:46 PM, by Nate Rupard)
- Completed correct and incorrect file names

## 10/29/26 - 5:01 PM - Nate Rupard
- Added the draft for Isaac's work to be translated into a JSON file
- Added a SPEC.md file meant for any collaborators, but mainly my good friend
  Albert Iverson
## 10/29/26 - 5:33 PM - Nate Rupard (with Claude)
- Rewrote `Folder` parsing to be recursive and added a `File` class
- Added the hint_structure format (`hint_structure.*.json`) and validation
  for hand-written hunt JSON
- Added `Game`, which reveals one room at a time, renames solved folders and
  keys to their real names, and resets the room after a wrong deletion
- Added the `start`/`stop` commands and filled in `monitor.pyw` (popups via
  osascript, tkinter, or zenity)
- Translated Isaac's draft into `folder_structure.readyplayerroot.json` and
  drafted all hint/treasure text in `hint_structure.readyplayerroot.json`
    - Rooms 2 and 3 keys are now named Jade Key and Crystal Key
- Added tests (`python3 -m unittest discover -s tests -v`), including tricky
  things students might try
- Filled in README.md with how to run and how to play (slide text)

## 10/29/26 - 10:20 PM - Nate Rupard (with Claude)
- Key files no longer say "key". Each one describes the secret way through
  its room, and the other two files in the right folder are obstacles
    - Room 3's "24" and "42" are now Orb of Osuvox and Mechagodzilla
    - Room hints now also say how to spot the key
- Fixed crashes from symlinks and `chmod`-locked folders found in review
- Moved the monitor's PID and log files into each user's home folder, so
  every account on a Mac can run one shared install
- Added `tools/build_release.py`, which builds a macOS download that bundles
  its own Python (no admin password or Xcode tools needed)
