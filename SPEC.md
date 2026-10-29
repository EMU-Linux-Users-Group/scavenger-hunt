# EMU LUG Digital D___s Scavenger Hunt Specification

# Basic Functionality
- in the folder structure, every 0th folder is the correct one
    - in the example, this means every folder named "folder0"
    - files work the same way
- another way you know a folder is correct based on the structure is it will 
  have three folders in it
    - for the players, these three folders will only appear when they have 
      eliminated the two incorrect folders (with their files) and the two incorrect files

# Hints/Hint Functionality
- we need a folder structure format called hint_structure that maps hints to 
  the files/folders they are contained to
- every file will contain a hint based on where it is and what it contains
    - if it is the incorrect folder, the hints contained within the three files 
      will be random from each other
    - if it is the correct folder, the hints will be descriptive of being in 
      the same room
- if the wrong folder gets destroyed, display a unique hint for the correct 
  folder of that folder layer

# Monitor Functionality
- in order for the program to know when the player deletes the correct files 
  and folders, it needs to use a monitor (monitor.pyw) that runs in the 
  background
- the monitor will moniter the folder structure
    - if the student deletes the correct folders and files
        - popup a message saying "Congratulations! You unlocked the next room!"
            - unless the treasure is unlocked, then say, "Congratulations! 
              You unlocked the treasure!"
        - place the next folders and files with their proper contents
    - if the student deletes the wrong folders and files
        - popup a message displaying the aforementioned unique hint 
        - replace the necessary folders and files, but do not delete the 
          student's progress

# Folder Rename Functionality
- if you notice in the folder_structure, names map to ids, and ids map to the 
  actual structure
- by default, folders and files are named their ids
- when a folder layer is solved, the file and folder names should be renamed to
  their names rather than ids
    - make sure the whole program is aware when the rename happens so no glitches happen

# Commands
- `python3 scavenger_hunt.py start`
    - creates/initializes the folder structure
    - starts the monitor
    - if the folder structure already exists
        - delete it
        - start new
- `python3 scavenger_hunt.py stop`
    - stops the monitor