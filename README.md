# scavenger-hunt

**Ready Player Root** is a terminal scavenger hunt for the EMU Linux Users
Group's Digital Dudes and Divas activity. Players use `ls`, `cd`, `cat`, `rm`,
and `rmdir` to work through three rooms of folders, collect the Copper, Jade,
and Crystal Keys, and unlock the Golden Easter Egg. A background monitor
watches what they delete, reveals each room once the previous one is solved,
and shows popups along the way.

## Requirements

- Python 3.9 or newer (the `python3` that comes with macOS works)
- Linux or macOS. There is nothing to install with pip.
- Popups use `osascript` on macOS. On Linux they use tkinter (on Fedora:
  `sudo dnf install python3-tkinter`) or fall back to `zenity`.

## Running it

```bash
python3 scavenger_hunt.py start   # wipe and create the game, start the monitor
python3 scavenger_hunt.py stop    # stop the monitor
```

- The game is created in `~/ready_player_root`. Players start with
  `cd ~/ready_player_root`.
- `start` always deletes the old game and starts fresh. If a monitor is
  already running, it is stopped first, so there is only ever one.
- `start` checks both JSON files before touching anything. If something is
  wrong with them, it prints the problem and changes nothing.
- The monitor exits on its own once the treasure is unlocked.
- If the monitor ever misbehaves, its output is in `.monitor.log` next to this
  README.

## How to play

*(This section doubles as the slide text for the presentation.)*

1. **There are three rooms.** Each room has three folders, and each folder has
   three files. Their names are scrambled, like `gf4fh4`.
2. **Read everything.** `cd` into each folder and `cat` every file. Each file
   describes an object and where it is.
3. **Find the right folder.** Only one folder has three files that all
   describe the *same place*. In the other two folders, the files describe
   objects scattered all over the place.
4. **Find the key.** Inside the right folder, only one file describes a key.
5. **Clear away everything else.** `rm` the two files that aren't the key.
   Then empty the two wrong folders with `rm` and remove them with `rmdir`
   (or use `rm -r`).
6. **Unlock the next room.** When only the right folder and its key are left,
   a popup congratulates you. The folder and key get their real names (like
   `Unbeatable Race` and `Copper Key`), and the next room appears inside it.
7. **Careful!** If you delete the right folder or the key, the room resets and
   a popup gives you a hint.
8. Collect all three keys to find the **Golden Easter Egg**.

Tips:

- Names with spaces need quotes or Tab completion: `cd "Unbeatable Race"`.
- If `ls` looks empty after a room resets, run `cd ..` and go back in.
- `pwd` tells you where you are.

## Writing a hunt

A hunt is two JSON files.

**`folder_structure.<name>.json`** maps names to IDs. When an ID is also a key
whose value is an object, it is a folder; otherwise it is a file. The first
folder and the first file in each folder are the correct ones. The last
correct folder holds `"treasure": "<file name>"`.

```json
{
    "Unbeatable Race": "gf4fh4",
    "gf4fh4": {
        "Copper Key": "cfd4ys",
        "Backwards Ramps": "k3m9xp",
        "King Kong": "dr66tk",
        "Overlook Hotel": "ghfn6g",
        "ghfn6g": { "...": "..." }
    }
}
```

**`hint_structure.<name>.json`** mirrors the same nesting using **IDs only**.
A file ID maps to the text inside that file. `"hint"` inside a correct folder
is the popup shown when a player wrecks that room. `"treasure"` holds the
treasure text.

```json
{
    "gf4fh4": {
        "hint": "Oops! That was part of the real path...",
        "cfd4ys": "A small key made of copper...",
        "k3m9xp": "A row of ramps...",
        "dr66tk": "A giant ape...",
        "ghfn6g": { "...": "..." }
    }
}
```

The hunt `start` uses is set by `FOLDER_STRUCTURE_FILE` and
`HINT_STRUCTURE_FILE` at the top of `scavenger_hunt.py`.

## For facilitators: known ways to cheat

The answers live in this repo's JSON files. Because the monitor runs as the
student's own user, a student who finds the repo, or who spots the JSON paths
in `ps` output, can read them. Keep the repo somewhere students won't go
looking, and treat it as part of the honor system.

## Tests

```bash
python3 -m unittest discover -s tests -v
```
