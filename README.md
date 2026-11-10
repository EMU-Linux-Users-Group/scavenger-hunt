# scavenger-hunt

**Stranger Pings** is a terminal lesson for the EMU Linux Users Group's
Digital Dudes and Divas activity. Each slide teaches one command and is also
one step of a Stranger Things story. While a slide is up, students type its
command into the real Terminal on their own computer. When they get it right,
a popup tells the next part of the story, and a bulb lights up in the string
of Christmas lights in their prompt. Mistakes get a short hint right in the
terminal.

- Slide text and speaker notes: [`docs/slides.md`](docs/slides.md)
- Before class: [`docs/morning-checklist.md`](docs/morning-checklist.md)
- Design: [`docs/superpowers/specs/2026-11-10-stranger-pings-design.md`](docs/superpowers/specs/2026-11-10-stranger-pings-design.md)

The slides teach nine commands, in this order: `echo`, `ls`, `cat`, `pwd`,
`mkdir`, `cd`, `cp`, `rm`, `rmdir`.

## Requirements

- macOS or Linux, with zsh or bash. There is nothing to install with pip.
- On macOS, use the release download (see below). It brings its own Python.
- Running from this repo instead needs Python 3.9 or newer.
- Popups use `osascript` on macOS, with a tkinter window as the backup. On
  Linux they use tkinter (on Fedora: `sudo dnf install python3-tkinter`) or
  fall back to `zenity`.

## Setting up classroom Macs

Each [release](https://github.com/EMU-Linux-Users-Group/scavenger-hunt/releases)
has a `stranger-pings-macos.tar.gz`. It works on Apple Silicon and Intel Macs
and bundles its own Python, so it needs no admin password and no Xcode tools.
On each Mac, open Terminal and paste:

```bash
curl -fsSL https://github.com/EMU-Linux-Users-Group/scavenger-hunt/releases/latest/download/stranger-pings-macos.tar.gz | tar -xpzf - -C /Users/Shared
```

That puts the game in `/Users/Shared/stranger-pings`, where every account on
the Mac can run it. Then, logged in as the student, either run
`/Users/Shared/stranger-pings/stranger-pings` in Terminal or double-click
`Stranger Pings.command` in that folder. Each student's game and progress live
in their own home folder.

Use `curl` rather than downloading in a browser. macOS blocks programs
downloaded in a browser until whoever downloaded them runs them once. To
update a Mac, run the same `curl` command again.

## Helper commands

Inside a student's game, type these as shown. Outside it, use the full path
`/Users/Shared/stranger-pings/stranger-pings`.

| Command | What it does |
|---|---|
| `stranger-pings` | Opens the game in this Terminal window. If the student already made progress, it picks up where they left off. |
| `stranger-pings reset` | Starts the student over from the first slide. |
| `stranger-pings skip mkdir` | Jumps the student to that slide (any of the nine commands), as if they'd done every slide before it. |
| `stranger-pings popups tk` | Switches this account to the backup popup (`popups auto` switches back). |

## How it works

- `stranger-pings` builds the student's world (`~/hawkins`, and later its
  mirror in the Upside Down, `~/upside_down/hawkins`). Then it opens the
  student's own shell (zsh, or bash) with a small add-on from `shell/`. The
  student's own startup files are never read or changed.
- After every command, the add-on runs `stranger_pings.py check`. It passes
  along what was typed, whether it worked, and the folder before and after.
- The rules in `checker.py` decide whether the slide is finished (popup), was
  attempted the wrong way (hint), or neither. They quietly put back anything
  the student deleted that a slide still needs. The answer comes back as the
  prompt's lights and, sometimes, a folder to move the student into.
- Progress is saved per account in
  `~/Library/Application Support/Stranger Pings/` on macOS or
  `~/.local/state/stranger_pings/` on Linux. If anything ever goes wrong,
  details land in `errors.log` there, never in the student's terminal.

## Editing the story

Everything students read is in `story.py`: the popups, the hints, the banner,
and the text inside every file. Changing the wording there is safe. Renaming a
file or folder also needs changes in `world.py`, `checker.py`, and the tests.

## Running from the repo

```bash
python3 stranger_pings.py          # opens the game in this terminal; `exit` leaves it
python3 stranger_pings.py reset    # start over
```

To clean up afterward: `rm -rf ~/hawkins ~/upside_down` and the progress
folder above.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

`tests/test_shells.py` plays the game in real bash and zsh shells by typing
into them. The zsh tests are skipped unless zsh is installed
(`sudo dnf install zsh`); install it, since the Macs use zsh. To run those
tests against an unpacked release instead of the repo, set
`STRANGER_PINGS_COMMAND` to its `stranger-pings` launcher.

## Building a release

```bash
python3 tools/build_release.py         # dist/stranger-pings-macos.tar.gz
python3 tools/build_release.py linux   # for testing on Linux
```
