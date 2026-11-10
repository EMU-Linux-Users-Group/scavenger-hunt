# Stranger Pings Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Ready Player Root with Stranger Pings. Students type each slide's command into a real Terminal, and a shell add-on reports every command to a checker. The checker shows a popup when the student got it right, prints a themed hint when they didn't, and lights one Christmas bulb in the prompt per finished step.

**Architecture:**
- `stranger-pings` prepares the student's world under `~/hawkins` and `~/upside_down/hawkins`, then replaces itself with the student's normal shell (zsh or bash). It starts that shell with a game-owned startup file.
- After every command, that file's hook runs `stranger_pings.py check` with the command line, exit status, and folders. The checker decides the outcome, repairs the world, saves progress, and starts any popup in the background.
- It prints hints to stderr. On stdout it prints two lines: the prompt's lights, and an optional folder the hook should `cd` into.

**Tech Stack:** Python 3.9+ standard library only, zsh/bash startup files, `unittest`; real-shell tests drive bash/zsh through a pseudoterminal (tests only).

**Spec:** `docs/superpowers/specs/2026-11-10-stranger-pings-design.md`. Read it first. It holds the story, the step table, and the exact popup text.

## Global Constraints

- Python **3.9+** compatible: `from __future__ import annotations` in every module, no `match`, and no runtime `X | Y`. **Standard library only.**
- Linux and macOS. The game runs the user's `$SHELL` if it's zsh or bash. Otherwise it uses zsh when installed, else bash.
- Every name in the world is lowercase with underscores; no spaces.
- Popups appear **only** on success. Hints are one line, in the story's voice, and printed in the terminal before the next prompt.
- The student's own shell startup files (`~/.zshrc`, `~/.bashrc`, `~/.zsh_history`, …) are never read or written. Everything the game writes lives in `~/hawkins`, `~/upside_down`, or the state folder:
  - macOS: `~/Library/Application Support/Stranger Pings`
  - Linux: `~/.local/state/stranger_pings`
- Popup text is copied **verbatim** from the spec's "Popup text (drafts)" list. Banner text is copied verbatim from the spec's "How a session runs" block.
- Repo style:
  - every module, class, and function has a docstring;
  - tests use `unittest` and run with `python3 -m unittest discover -s tests -v` from the repo root;
  - commits use `feat:`/`fix:`/`test:`/`docs:`/`chore:` prefixes and end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- **Never stage** `Digital Dudes Presentation.pptx` or `Links and Brainstorming.docx`. Stage files by name.
- Do not publish a GitHub release. Building one is fine. Nate OK'd *pre-releases* for test builds; a full release needs his explicit go-ahead at that time.

## Review Focus

1. **The checker crashes** (for example, the state folder can't be written). The student's shell must keep working, the prompt keeps its lights, and no traceback reaches the terminal. *Task 4: `test_check_never_breaks_the_shell`.*
2. **The student deletes the folder they're standing in** (`rm -r ~/hawkins` while inside it). The world comes back, and the shell is moved into the recreated folder instead of being left in a deleted one. *Task 3: `test_deleting_the_folder_you_are_in_moves_you_back_in`.*
3. **A popup blocks the prompt.** The hook reads the checker's stdout through `$(…)`. If the popup process inherits that stdout, the prompt waits until OK is clicked. *Task 4: `test_check_does_not_wait_for_the_popup`.*
4. **Odd input**: unbalanced quotes, `$(`, a lone backslash, emoji, a 10,000-character line. There's no crash, no hint, and no step change. *Task 2: `test_unparseable_lines_give_no_commands`; Task 3: `test_odd_input_is_ignored`.*
5. **Bash history quirks.** Some distros set `HISTCONTROL=ignoredups:ignorespace`, which drops a repeated typo or a line starting with a space from history. Each must still be checked; an empty Return must not re-check the last line. *Task 5: `test_same_typo_twice_hints_twice`, `test_leading_space_is_still_checked`, `test_empty_return_checks_nothing`.*

---

## File Structure

| File | Responsibility |
|---|---|
| `story.py` (new) | All student-facing text: the nine commands, popups, banner, final message, hints, and the world's file contents. The team edits this file. |
| `world.py` (new) | Folder layout; `prepare(step)` builds or repairs the world for a step; `wipe`. |
| `parse.py` (new) | Splits a typed command line into commands, and expands `~`, relative paths, and wildcards. |
| `progress.py` (new) | State folder, per-account progress, popup-style setting. |
| `checker.py` (new) | `check(report, progress, home) -> Outcome`: the game rules. |
| `popup.py` (new) | Shows a popup (osascript / tk / zenity / print). It's also a script, run detached by `spawn`. |
| `stranger_pings.py` (new) | CLI: `start` (default), `reset`, `skip`, `popups`, plus the hook's `check` and `status`; prompt lights; starting the shell. |
| `shell/zshrc`, `shell/bashrc` (new) | The add-on: prompt, the per-command hook, and the `stranger-pings` helper function. |
| `tools/stranger-pings`, `tools/Stranger Pings.command` (new) | Launcher that runs the bundled Python; double-click shortcut. |
| `tools/build_release.py` (modify) | Packages Stranger Pings instead of Ready Player Root. |
| `tests/helpers.py`, `tests/terminal.py` (new) | `Session` (a student in a temp home) and `GameTerminal` (a real shell in a pseudoterminal). |
| `docs/slides.md`, `docs/morning-checklist.md` (new) | Slide text with speaker notes, and the morning-of-class checklist. |
| Removed | `scavenger_hunt.py`, `monitor.pyw`, `folder_structure.*`, `hint_structure.*`, `tools/ready-player-root`, the old `tests/*.py` |

---

### Task 1: Branch, clear out Ready Player Root, story and world

**Files:**
- Create: `story.py`, `world.py`, `tests/test_world.py`
- Delete: `scavenger_hunt.py`, `monitor.pyw`, `folder_structure.example.json`, `folder_structure.readyplayerroot.draft`, `folder_structure.readyplayerroot.json`, `folder_structure.test.json`, `hint_structure.readyplayerroot.json`, `hint_structure.test.json`, `tests/helpers.py`, `tests/test_game.py`, `tests/test_monitor.py`, `tests/test_readyplayerroot.py`, `tests/test_structure.py`
- Modify: `.gitignore` (add `.superpowers/`)

**Interfaces:**
- Produces, in `story.py`:
  - `COMMANDS: tuple[str, ...] = ("echo", "ls", "cat", "pwd", "mkdir", "cd", "cp", "rm", "rmdir")`.
  - `POPUPS: tuple[str, ...]`: the spec's 9 popup texts, verbatim, same order.
  - `BANNER: str`: the spec's three banner lines.
  - `RESUME: str`, with `{command}`: "Picking up where you left off: the {command} slide.".
  - `DONE_ALREADY: str`.
  - `FINAL_MESSAGE: str`: names all nine commands.
  - `FILES: dict[str, str]`: path relative to home → file text, for exactly these paths:
    - `hawkins/walkie_talkie`
    - `hawkins/byers_house/christmas_lights`
    - `hawkins/byers_house/alphabet_wall`
    - `hawkins/hawkins_lab/notice`
    - `upside_down/hawkins/walkie_talkie`
    - `upside_down/hawkins/byers_house/christmas_lights`
    - `upside_down/hawkins/hawkins_lab/vines`
    - `upside_down/hawkins/eggos`
    - `upside_down/hawkins/gate/demogorgon`
  - `HINTS: dict[str, str]`, with these exact keys:
    - `typo` (uses `{letters}`), `lowercase`, `later`, `try_again`;
    - `echo_empty`, `spaces`;
    - `cat_folder`, `cat_missing`, `cat_no_file`;
    - `wrong_folder`, `mkdir_name`;
    - `cd_back_out`, `cd_lost`;
    - `cp_destination`, `cp_wrong_place`;
    - `rm_folder`, `rm_inside_gate`;
    - `gate_not_empty`, `use_rmdir`.
  - `hint_text(key: str) -> str`. `"typo:echo"` gives `HINTS["typo"]` with `letters="e-c-h-o"`; other keys are looked up directly.
- Produces, in `world.py`:
  - `hawkins(home: Path) -> Path` → `home/"hawkins"`.
  - `mirror(home: Path) -> Path` → `home/"upside_down"/"hawkins"`.
  - `castle(home: Path) -> Path` → `mirror(home)/"castle_byers"`.
  - `gate(home: Path) -> Path` → `mirror(home)/"gate"`.
  - `start_folder(step: int, home: Path) -> Path`.
  - `prepare(step: int, home: Path) -> None`.
  - `wipe(home: Path) -> None`.
  - Step numbers are **0-based indexes into `COMMANDS`**: 0 = echo … 8 = rmdir, and 9 = finished.

- [ ] **Step 1: Create the branch and commit the design docs.**
  ```bash
  git checkout -b stranger-pings
  git add docs/superpowers/specs/2026-11-10-stranger-pings-design.md docs/superpowers/plans/2026-11-10-stranger-pings.md
  git commit -m "docs: Stranger Pings design and plan"
  ```
- [ ] **Step 2: Delete the old game.** `git rm` every file in the Delete list. Add `.superpowers/` to `.gitignore`.
- [ ] **Step 3: Write `tests/test_world.py`**

```python
"""Tests for building and repairing the student's world"""

from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest

import story
import world


class WorldTests(unittest.TestCase):
    """`prepare` makes the world look the way each slide expects"""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = Path(tmp.name)

    def test_hawkins_only_at_the_start(self):
        world.prepare(0, self.home)
        for path, text in story.FILES.items():
            if path.startswith("hawkins/"):
                self.assertEqual((self.home / path).read_text(encoding="utf-8"), text + "\n")
        self.assertFalse((self.home / "upside_down").exists())

    def test_what_exists_at_each_step(self):
        # step: (castle_byers, castle_byers/eggos, gate/demogorgon, gate)
        expected = {0: None, 1: None, 2: None,
                    3: (False, False, True, True), 4: (False, False, True, True),
                    5: (True, False, True, True), 6: (True, False, True, True),
                    7: (True, True, True, True), 8: (True, True, False, True),
                    9: (True, True, False, False)}
        for step, exists in expected.items():
            with self.subTest(step=step):
                world.wipe(self.home)
                world.prepare(step, self.home)
                if exists is None:
                    self.assertFalse((self.home / "upside_down").exists())
                    continue
                self.assertTrue((world.mirror(self.home) / "eggos").is_file())
                self.assertEqual((world.castle(self.home).is_dir(),
                                  (world.castle(self.home) / "eggos").is_file(),
                                  (world.gate(self.home) / "demogorgon").is_file(),
                                  world.gate(self.home).is_dir()), exists)

    def test_going_back_removes_the_upside_down(self):
        world.prepare(6, self.home)
        world.prepare(1, self.home)
        self.assertFalse((self.home / "upside_down").exists())

    def test_castle_made_too_early_is_removed(self):
        world.prepare(3, self.home)
        world.castle(self.home).mkdir()
        world.prepare(4, self.home)
        self.assertFalse(world.castle(self.home).exists())

    def test_gate_is_emptied_of_the_demogorgon_for_rmdir(self):
        world.prepare(7, self.home)
        world.prepare(8, self.home)
        self.assertEqual(list(world.gate(self.home).iterdir()), [])

    def test_repairs_edited_replaced_symlinked_and_locked_things(self):
        world.prepare(3, self.home)
        (world.hawkins(self.home) / "walkie_talkie").write_text("hi", encoding="utf-8")
        eggos = world.mirror(self.home) / "eggos"
        eggos.unlink()
        eggos.mkdir()
        house = world.hawkins(self.home) / "byers_house"
        os.rename(house, self.home / "moved")
        house.symlink_to(self.home)
        (world.mirror(self.home) / "hawkins_lab").chmod(0o000)
        world.prepare(3, self.home)
        self.assertEqual((world.hawkins(self.home) / "walkie_talkie").read_text(encoding="utf-8"),
                         story.FILES["hawkins/walkie_talkie"] + "\n")
        self.assertTrue(eggos.is_file())
        self.assertTrue(house.is_dir() and not house.is_symlink())
        self.assertTrue((self.home / "moved").is_dir())   # the student's moved folder is untouched
        self.assertTrue((world.mirror(self.home) / "hawkins_lab" / "vines").is_file())

    def test_student_files_are_left_alone(self):
        world.prepare(6, self.home)
        (world.hawkins(self.home) / "notes").write_text("mine", encoding="utf-8")
        (world.castle(self.home) / "drawing").write_text("mine", encoding="utf-8")
        world.prepare(7, self.home)
        self.assertTrue((world.hawkins(self.home) / "notes").exists())
        self.assertTrue((world.castle(self.home) / "drawing").exists())

    def test_start_folder(self):
        self.assertEqual([world.start_folder(step, self.home) for step in (0, 2, 3, 9)],
                         [world.hawkins(self.home), world.hawkins(self.home),
                          world.mirror(self.home), world.mirror(self.home)])

    def test_wipe_removes_only_the_world(self):
        world.prepare(5, self.home)
        (self.home / "homework.txt").write_text("keep", encoding="utf-8")
        world.wipe(self.home)
        world.wipe(self.home)   # nothing left to wipe is fine
        self.assertEqual([p.name for p in self.home.iterdir()], ["homework.txt"])


class StoryTests(unittest.TestCase):
    """The text the team edits stays usable"""

    def test_one_popup_per_command(self):
        self.assertEqual(len(story.POPUPS), len(story.COMMANDS))

    def test_every_hint_renders(self):
        for key in story.HINTS:
            if key != "typo":
                self.assertTrue(story.hint_text(key))
        self.assertIn("e-c-h-o", story.hint_text("typo:echo"))

    def test_final_message_names_every_command(self):
        for command in story.COMMANDS:
            self.assertIn(command, story.FINAL_MESSAGE)
```

- [ ] **Step 4: Run the tests and confirm they fail.** Run `python3 -m unittest discover -s tests -v`. Expected: `ModuleNotFoundError: No module named 'story'`.
- [ ] **Step 5: Implement `story.py`.**
  - Copy the popups and banner verbatim from the spec.
  - Write the file texts and hints yourself, following the spec's rules: original text (not quotes from the show), a few short lines at most, plain ASCII.
  - `cat_no_file` also tells the student that Control-C gets them out if `cat` seems stuck.
  - `cd_back_out` is the story line printed once the student is inside Castle Byers. It tells them to come back out with `cd ..`.
- [ ] **Step 6: Implement `world.py`.**
  - Copy `_make_writable` and `_clear` from `scavenger_hunt.py` at commit `39f5bdd` (`git show 39f5bdd:scavenger_hunt.py`). They handle `chmod`-locked folders and never follow symlinks.
  - `prepare(step)` always repairs Hawkins (every `hawkins/…` path in `FILES`):
    - a file is rewritten if it's missing or its text differs;
    - anything in the way of a game file or game folder (a folder, a file, or a symlink) is cleared.
  - For `step < 3`, it removes `~/upside_down`.
  - For `step >= 3`, it repairs every `upside_down/…` path in `FILES` except `gate/demogorgon`. Then:
    - `gate/demogorgon`: present for steps 3–7, removed for step 8, left alone at step 9;
    - `gate`: created for steps 3–8; for step 9 it is neither created nor removed;
    - `castle_byers`: removed for steps 3–4, created for step ≥ 5;
    - `castle_byers/eggos`: a copy of `FILES["upside_down/hawkins/eggos"]`, created if missing for step ≥ 7.
  - `start_folder(step)` is `hawkins` for steps 0–2 and `mirror` after that.
  - `wipe(home)` clears `~/hawkins` and `~/upside_down`.
- [ ] **Step 7: Run the tests and confirm they pass.** Run `python3 -m unittest discover -s tests -v`. Expected: all `test_world` tests pass.
- [ ] **Step 8: Commit**
  ```bash
  git add .gitignore story.py world.py tests/test_world.py
  git commit -m "feat: Stranger Pings story text and world, replacing Ready Player Root"
  ```
  (`git rm` already staged the deletions.)

---

### Task 2: Reading a command line

**Files:**
- Create: `parse.py`, `tests/test_parse.py`

**Interfaces:**
- Produces:
  - `@dataclass(frozen=True) class Command`, with `name: str` (the first word, case kept) and `args: tuple[str, ...]` (quotes removed, redirections dropped, no wildcard expansion).
  - `split_line(line: str) -> list[Command]`.
  - `paths(arg: str, cwd: Path, home: Path) -> list[Path]`: expands `~`, resolves relative paths from `cwd`, and expands wildcards into sorted matches. With no match, it returns `[cwd / arg]`. Paths are made absolute but **not** resolved (no symlink following).

- [ ] **Step 1: Write `tests/test_parse.py`**

```python
"""Tests for reading what a student typed"""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from parse import Command, paths, split_line


class SplitLineTests(unittest.TestCase):
    """Turning one typed line into commands"""

    def test_one_command(self):
        self.assertEqual(split_line("  echo   hello Will  "),
                         [Command("echo", ("hello", "Will"))])

    def test_quotes(self):
        self.assertEqual(split_line("echo 'hello Will'"), [Command("echo", ("hello Will",))])

    def test_several_commands(self):
        self.assertEqual([c.name for c in split_line("echo hi; ls && pwd || cat x | cat &")],
                         ["echo", "ls", "pwd", "cat", "cat"])

    def test_redirections_are_dropped(self):
        self.assertEqual(split_line("echo hi > note"), [Command("echo", ("hi",))])
        self.assertEqual(split_line("cat < walkie_talkie"), [Command("cat", ())])

    def test_variable_assignments_are_skipped(self):
        self.assertEqual(split_line("FOO=1 ls"), [Command("ls", ())])

    def test_unparseable_lines_give_no_commands(self):
        for line in ("", "   ", "echo 'unclosed", "echo \"unclosed", "\\", ";;", "|",
                     "echo $(", "echo $(pwd)", "echo `pwd`"):
            with self.subTest(line=line):
                self.assertEqual(split_line(line), [])
        self.assertEqual(split_line("echo " + "x" * 10000)[0].name, "echo")
        self.assertEqual(split_line("echo 🙂")[0].args, ("🙂",))


class PathsTests(unittest.TestCase):
    """Working out which files an argument means"""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = Path(tmp.name)
        self.cwd = self.home / "hawkins"
        self.cwd.mkdir()
        for name in ("walkie_talkie", "eggos"):
            (self.cwd / name).write_text("x", encoding="utf-8")

    def test_relative_home_and_absolute(self):
        target = self.cwd / "walkie_talkie"
        for arg in ("walkie_talkie", "./walkie_talkie", "~/hawkins/walkie_talkie", str(target)):
            with self.subTest(arg=arg):
                self.assertEqual(paths(arg, self.cwd, self.home), [target])

    def test_wildcards(self):
        self.assertEqual(paths("*", self.cwd, self.home),
                         [self.cwd / "eggos", self.cwd / "walkie_talkie"])
        self.assertEqual(paths("nothing*", self.cwd, self.home), [self.cwd / "nothing*"])
```

- [ ] **Step 2: Run the tests and confirm they fail.** Run `python3 -m unittest discover -s tests -p test_parse.py -v`. Expected: `ModuleNotFoundError: No module named 'parse'`.
- [ ] **Step 3: Implement `parse.py`.**
  - Use `shlex.shlex(line, posix=True, punctuation_chars=True)` with `whitespace_split=True`.
  - Separators: tokens made only of `;&|()` characters, plus newlines.
  - Redirections: a token made only of `<>&` characters is dropped together with the word after it.
  - `ValueError` (from unbalanced quotes) gives `[]`.
  - A line containing `$(` or a backtick gives `[]`. Command substitution is beyond these lessons, and without this rule `echo $(` would look like a real echo.
  - Leading `NAME=value` words are skipped.
  - `paths` uses `os.path.expanduser` with `home`, and `glob.glob` only when the arg contains `*?[`.
- [ ] **Step 4: Run the tests and confirm they pass.** Run `python3 -m unittest discover -s tests -v`. Expected: all pass.
- [ ] **Step 5: Commit**
  ```bash
  git add parse.py tests/test_parse.py
  git commit -m "feat: read typed command lines the way the shell does"
  ```

---

### Task 3: Progress and the game rules

**Files:**
- Create: `progress.py`, `checker.py`, `tests/helpers.py`, `tests/test_progress.py`, `tests/test_checker.py`

**Interfaces:**
- Consumes: `story` and `world` (Task 1); `split_line` and `paths` (Task 2).
- Produces, in `progress.py`:
  - `state_dir(home: Path, platform: str = sys.platform) -> Path`.
  - `@dataclass class Progress`, with `step: int = 0` and `entered_castle: bool = False`.
  - `load_progress(state: Path) -> Progress`. A missing or corrupt file, or one with an out-of-range step, gives `Progress()`.
  - `save_progress(state: Path, progress: Progress) -> None`: atomic (write a temp file, then `os.replace`), creating `state`. The file is `progress.json`.
  - `clear_progress(state: Path) -> None`.
  - `load_popup_style(state: Path) -> str`: `"auto"` by default.
  - `save_popup_style(state: Path, style: str) -> None`. The file is `settings.json`, which `clear_progress` never touches. `style` is `"auto"` or `"tk"`, else `ValueError`.
- Produces, in `checker.py`:
  - `@dataclass(frozen=True) class Report`, with `line: str`, `status: int`, `before: Path`, `after: Path`.
  - `@dataclass class Outcome`, with `hint: str | None = None` (a `story.HINTS` key, or `"typo:<command>"`), `popup: str | None = None`, `move_to: Path | None = None`, and `finished: bool = False`.
  - `check(report: Report, progress: Progress, home: Path) -> Outcome`, which updates `progress` in place.
- Produces, in `tests/helpers.py`:
  - `SOLUTION: tuple[str, ...] = ("echo hello Will", "ls", "cat walkie_talkie", "pwd", "mkdir castle_byers", "cd castle_byers", "cd ..", "cp eggos castle_byers", "rm gate/demogorgon", "rmdir gate")`.
  - `run_in_bash(line, cwd, home) -> Report`.
  - `class Session`, with `.home`, `.progress`, `.cwd`, `.type(line) -> Outcome`, and `.play_to(step)`.

**The rules `check` implements** (spec: "How the game reacts" and the step table):
1. At step 9, return `Outcome()` and change nothing (free play).
2. If the line's first command is `stranger-pings`:
   - for its `start`, `reset`, or `skip` subcommands, return `Outcome(move_to=world.start_folder(progress.step, home))`;
   - otherwise return `Outcome()`.
   (The helper command has already updated the progress and the world.)
3. Walk the commands in order, each against the *current* step. When one completes the step:
   - the step goes up by 1 and `entered_castle` resets;
   - `popup` becomes that step's `POPUPS` entry, so only the last completed step's popup survives;
   - finishing cat sets `move_to = mirror`, and finishing rmdir sets `finished`.
   A command that doesn't complete the step can set the hint, but only if none is set yet; at most one hint per line.
4. What completes each step, where `ok` means `report.status == 0`, `cmd.name.lower()` is compared, and paths are compared with `os.path.samefile` when both exist:
   - **echo:** `ok` and at least one arg.
   - **ls:** `ok`.
   - **pwd:** `ok`.
   - **cat:** some arg's `paths` include `hawkins/walkie_talkie` as an existing file. The status is ignored because `cat *` also fails on folders.
   - **mkdir:** `ok` and `castle` is a folder.
   - **cd:** first `after` is `castle`. That sets `entered_castle` and the hint `cd_back_out`. Then, with `entered_castle` set, `after` is `mirror`.
   - **cp:** `ok`, `mirror/eggos` exists, and some file directly inside `castle` has the same text as `mirror/eggos`.
   - **rm:** `gate/demogorgon` no longer exists. The status is ignored, so `rm -rf *` counts.
   - **rmdir:** `ok` and `gate` no longer exists.
5. Hints, checked in this order for a command that didn't complete the step:
   1. `status == 127` and the name lowercased is one of `COMMANDS` → `lowercase`.
   2. `status == 127` and the name is close to a `COMMANDS` entry → `typo:<that command>`. "Close" is measured with optimal-string-alignment distance, where swapping two neighboring letters counts as 1. The limit is 1, or 2 when the command has 4 or more letters. The closest command wins; ties go to the current step's command, then to `COMMANDS` order. So `sl`, `cta`, `ehco`, `mdkir`, and `rmdri` get the hint, but a stray `hi` doesn't.
   3. At step 8, an `rm` that left `gate` gone → `use_rmdir`. (`rm` is an earlier step's command at that point, so this rule comes before rule 6.)
   4. The name is a later step's command → `later`.
   5. The name is the current step's command, with step-specific hints:
      - **echo:** no args → `echo_empty`.
      - **Any step:** two args that joined with `_` equal a game name (`walkie_talkie`, `castle_byers`) → `spaces`.
      - **cat:** no args → `cat_no_file`; an arg that's a folder → `cat_folder`; otherwise `cat_missing`.
      - **mkdir, cp, rm, rmdir** run with `before` not `mirror` → `wrong_folder`, plus `move_to = mirror`.
      - **mkdir:** a different name → `mkdir_name`.
      - **cd:** `after` is neither `mirror` nor `castle` → `cd_lost`, plus `move_to = castle if entered_castle else mirror`.
      - **cp:** fewer than 2 args → `cp_destination`; the destination isn't `castle` → `cp_wrong_place`.
      - **rm:** an arg that is `gate` → `rm_folder`; an arg named `demogorgon` outside `gate` → `rm_inside_gate`.
      - **rmdir** on a non-empty `gate` → `gate_not_empty`.
      - Any other failure of the current command → `try_again`.
   6. Anything else (an earlier step's command, an untaught command, success while exploring) → no hint.
6. After the walk, call `world.prepare(progress.step, home)` (quiet repair). If `report.after` didn't exist before the repair and does now, and `move_to` is still unset, set `move_to = report.after`.

- [ ] **Step 1: Write `tests/helpers.py`**

```python
"""A pretend student for the game-rule tests"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile

from checker import Outcome, Report, check
from progress import Progress
import world

SOLUTION = ("echo hello Will", "ls", "cat walkie_talkie", "pwd", "mkdir castle_byers",
            "cd castle_byers", "cd ..", "cp eggos castle_byers", "rm gate/demogorgon",
            "rmdir gate")


def run_in_bash(line: str, cwd: Path, home: Path) -> Report:
    """Runs `line` in a real bash in `cwd` and reports it the way the shell add-on would"""
    read, write = os.pipe()
    script = f'{line}\n__s=$?\nprintf %s "$PWD" >&{write}\nexit $__s'
    result = subprocess.run(["bash", "--noprofile", "--norc", "-c", script], cwd=cwd,
                            env={**os.environ, "HOME": str(home), "PWD": str(cwd)},
                            pass_fds=(write,), capture_output=True, check=False)
    os.close(write)
    with os.fdopen(read) as pipe:
        after = pipe.read() or str(cwd)
    return Report(line, result.returncode, cwd, Path(after))


class Session:
    """A student with their own temporary home, starting at `step` as if a helper had skipped there"""

    def __init__(self, test_case, step: int = 0):
        tmp = tempfile.TemporaryDirectory()
        test_case.addCleanup(tmp.cleanup)
        self.home = Path(tmp.name)
        self.progress = Progress(step)
        world.prepare(step, self.home)
        self.cwd = world.start_folder(step, self.home)

    def type(self, line: str) -> Outcome:
        """Types `line`, lets the game react, and follows any move it asks for"""
        report = run_in_bash(line, self.cwd, self.home)
        outcome = check(report, self.progress, self.home)
        self.cwd = outcome.move_to or report.after
        return outcome

    def play_to(self, step: int):
        """Types the solution lines until the student reaches `step`"""
        for line in SOLUTION:
            if self.progress.step >= step:
                return
            self.type(line)
```

- [ ] **Step 2: Write `tests/test_progress.py`** with these tests:
  - `test_state_dir_per_platform`: the darwin path ends in `Library/Application Support/Stranger Pings`, and the linux path ends in `.local/state/stranger_pings`.
  - `test_missing_or_corrupt_progress_starts_fresh`: no file, `{not json`, a JSON list, and `{"step": 42}` all give `Progress()`.
  - `test_progress_round_trip`.
  - `test_popup_style_defaults_to_auto_and_survives_clear_progress`.
  - `test_bad_popup_style_is_rejected`: `save_popup_style(state, "banana")` raises `ValueError`.

- [ ] **Step 3: Write `tests/test_checker.py`.** Every row is one test method that uses `Session`. Names and assertions:

```python
"""Tests for the game rules, using real bash to run what a student types"""

from __future__ import annotations

import sys
import unittest

from helpers import SOLUTION, Session
import story
import world


class HappyPathTests(unittest.TestCase):
    """A student who follows the slides"""

    def test_each_slide_in_order(self):
        s = Session(self)
        popups = [s.type(line).popup for line in SOLUTION]
        self.assertEqual(popups, [story.POPUPS[0], story.POPUPS[1], story.POPUPS[2],
                                  story.POPUPS[3], story.POPUPS[4], None, story.POPUPS[5],
                                  story.POPUPS[6], story.POPUPS[7], story.POPUPS[8]])
        self.assertEqual(s.progress.step, 9)

    def test_cat_pulls_the_student_into_the_upside_down(self):
        s = Session(self, 2)
        self.assertEqual(s.type("cat walkie_talkie").move_to, world.mirror(s.home))
        self.assertTrue((world.gate(s.home) / "demogorgon").is_file())

    def test_inside_the_castle_says_to_come_back_out(self):
        s = Session(self, 5)
        outcome = s.type("cd castle_byers")
        self.assertEqual((outcome.hint, outcome.popup, s.progress.step), ("cd_back_out", None, 5))

    def test_last_slide_finishes_and_then_anything_goes(self):
        s = Session(self, 8)
        self.assertTrue(s.type("rmdir gate").finished)
        self.assertEqual(s.type("ehco hi").hint, None)
        self.assertEqual(s.type("rm -rf *").popup, None)
```

  `MistakeTests`. Each case is `(start step, line typed, expected hint, step afterwards)`, and each becomes its own `test_…` method:

  | Test | Step | Line | Hint | Step after |
  |---|---|---|---|---|
  | `test_typo` | 0 | `ehco hello` | `typo:echo` | 0 |
  | `test_typo_of_another_command` | 4 | `mdkir castle_byers` | `typo:mkdir` | 4 |
  | `test_capital_letters` (skip on darwin) | 0 | `ECHO hi` | `lowercase` | 0 |
  | `test_echo_with_nothing` | 0 | `echo` | `echo_empty` | 0 |
  | `test_later_slide` | 0 | `ls` | `later` | 0 |
  | `test_cat_a_folder` | 2 | `cat byers_house` | `cat_folder` | 2 |
  | `test_cat_with_spaces` | 2 | `cat walkie talkie` | `spaces` | 2 |
  | `test_cat_misspelled_file` | 2 | `cat walky_talky` | `cat_missing` | 2 |
  | `test_mkdir_with_spaces` | 4 | `mkdir castle byers` | `spaces` | 4 |
  | `test_mkdir_other_name` | 4 | `mkdir fort` | `mkdir_name` | 4 |
  | `test_cp_without_destination` | 6 | `cp eggos` | `cp_destination` | 6 |
  | `test_cp_into_wrong_folder` | 6 | `cp eggos byers_house` | `cp_wrong_place` | 6 |
  | `test_rm_the_gate` | 7 | `rm gate` | `rm_folder` | 7 |
  | `test_rm_demogorgon_outside_gate` | 7 | `rm demogorgon` | `rm_inside_gate` | 7 |
  | `test_rm_r_gate_on_rmdir_slide` | 8 | `rm -r gate` | `use_rmdir` | 8 (`gate` is back, empty) |
  | `test_rmdir_full_gate` | 8 | `echo boo > gate/note; rmdir gate` | `gate_not_empty` | 8 |

  `ExploringTests`. Each of these gives no hint and no step change:
  - `test_ls_again_on_cat_slide`: step 2, `ls`.
  - `test_cat_a_scenery_file`: step 2, `cat byers_house/christmas_lights`.
  - `test_untaught_commands`: step 2, `touch notes`, then `mv walkie_talkie radio`. Afterwards `walkie_talkie` exists again.
  - `test_earlier_command_failing`: step 5, `mkdir castle_byers`, which fails because the castle already exists.

  `TrickyTests`:
  - `test_two_steps_on_one_line_show_only_the_last_popup`: step 0, `echo hi; ls` → popup `POPUPS[1]`, step 2.
  - `test_cat_star_counts`: step 2, `cat *` → popup `POPUPS[2]`.
  - `test_other_paths_to_the_walkie_talkie_count`: `./walkie_talkie`, `~/hawkins/walkie_talkie`, and the absolute path, each in a fresh `Session(self, 2)` → popup.
  - `test_mkdir_p_counts`: step 4, `mkdir -p castle_byers` → popup.
  - `test_cp_with_a_new_name_counts`: step 6, `cp eggos castle_byers/waffles` → popup.
  - `test_rm_rf_star_counts_and_the_world_comes_back`: step 7, `rm -rf *` → popup `POPUPS[7]`, step 8, `eggos` exists, `gate` exists and is empty.
  - `test_early_rm_is_undone`: step 3, `rm gate/demogorgon` → hint `later`, and the demogorgon exists.
  - `test_early_mkdir_is_undone`: step 3, `mkdir castle_byers` → hint `later`, and the castle doesn't exist.
  - `test_wrong_folder_moves_the_student_back`: `Session(self, 4)` with `s.cwd = world.hawkins(s.home)`, then `mkdir castle_byers` → hint `wrong_folder`, `move_to == world.mirror(s.home)`.
  - `test_cd_somewhere_else_moves_the_student_back`: step 5, `cd castle_byers`, then `cd` → hint `cd_lost`, `move_to == world.castle(s.home)`.
  - `test_deleting_the_folder_you_are_in_moves_you_back_in` *(Review Focus 2)*: step 1, `rm -r ~/hawkins` → hawkins is rebuilt, and `move_to == world.hawkins(s.home)`.
  - `test_odd_input_is_ignored` *(Review Focus 4)*: step 0. Lines: `echo 'unclosed`, `echo $(`, `\`, `🙂`, and `"x" * 10000`. Each gives `Outcome()` with step 0.
  - `test_helper_commands_are_not_judged`: step 3, `stranger-pings skip mkdir` → `move_to == world.start_folder(3, s.home)`, and no hint. (No `stranger-pings` exists in that bash, so the status is 127; the rule must not treat that as a typo.)

- [ ] **Step 4: Run the tests and confirm they fail.** Run `python3 -m unittest discover -s tests -v`. Expected: `ModuleNotFoundError: No module named 'progress'`.
- [ ] **Step 5: Implement `progress.py`, then `check` in `checker.py`,** following the rules above. The typo distance is a short optimal-string-alignment function, so there's nothing to import.
- [ ] **Step 6: Run the tests and confirm they pass.** Run `python3 -m unittest discover -s tests -v`. Expected: all pass. (`test_capital_letters` is skipped on macOS only.)
- [ ] **Step 7: Commit**
  ```bash
  git add progress.py checker.py tests/helpers.py tests/test_progress.py tests/test_checker.py
  git commit -m "feat: game rules for all nine slides, with hints and quiet repair"
  ```

---

### Task 4: Popups and the `stranger-pings` command

**Files:**
- Create: `popup.py`, `stranger_pings.py`, `tests/test_popup.py`, `tests/test_cli.py`, and `shell/zshrc` + `shell/bashrc` holding only their header comment (Task 5 fills them in)

**Interfaces:**
- Consumes: `check`, `Report`, `Outcome` (Task 3); `progress.*` (Task 3); `world.*` and `story.*` (Task 1).
- Produces, in `popup.py`:
  - `TITLE = "Stranger Pings"`.
  - `popup_methods(style: str, platform: str) -> list[str]`:
    - `("auto", "darwin")` → `["osascript", "tk", "print"]`;
    - `("tk", "darwin")` → `["tk", "osascript", "print"]`;
    - `("auto", "linux")` and `("tk", "linux")` → `["tk", "zenity", "print"]`.
  - `show(message: str, style: str) -> None`. It tries each method until one works. If the environment variable `STRANGER_PINGS_POPUP_LOG` is set, it appends `message + "\n"` to that file instead of showing anything. The tests use this, and it needs no code in production paths beyond that one branch.
  - `spawn(message: str, style: str) -> None`: runs `[sys.executable, "-E", "-s", <popup.py>, style, message]` with stdin, stdout, and stderr all set to `subprocess.DEVNULL` and `start_new_session=True`.
  - Running `popup.py STYLE MESSAGE` calls `show`.
  - The osascript call reuses Ready Player Root's `display dialog` invocation (`git show 39f5bdd:monitor.pyw`).
  - The tk method makes a small topmost window with the message and an OK button, then calls `lift()` and `focus_force()`.
- Produces, in `stranger_pings.py`:
  - `APP_DIR = Path(__file__).resolve().parent`.
  - `lights(step: int, shell: str) -> str`. It returns 9 bulbs: `step` lit `●`, the rest unlit `○`.
    - Lit bulbs cycle red, yellow, green, blue, magenta.
    - For zsh, each bulb is wrapped in `%F{<color>}…%f`, and unlit ones in `%F{8}…%f`.
    - For bash, each is wrapped in `\[\e[3Nm\]…\[\e[0m\]`, and unlit ones in `\[\e[90m\]…\[\e[0m\]`.
  - `shell_command(shell_path: str, state: Path) -> tuple[list[str], dict[str, str]]` returns the argv and the extra environment for the student's shell.
    - zsh: `[shell_path]`, with `ZDOTDIR=<state>/zsh` and `SHELL_SESSIONS_DISABLE=1`. It first writes `<state>/zsh/.zshrc` as a copy of `APP_DIR/shell/zshrc`, every time.
    - bash: `[shell_path, "--rcfile", str(APP_DIR/"shell"/"bashrc"), "-i"]`, with `BASH_SILENCE_DEPRECATION_WARNING=1`.
    - Both also set `STRANGER_PINGS_SHELL=1`, `STRANGER_PINGS_PYTHON=sys.executable`, and `STRANGER_PINGS_APP=str(APP_DIR)`.
  - `choose_shell(env_shell: str) -> str`: the `$SHELL` path if its basename is `zsh` or `bash`; otherwise `shutil.which("zsh")`, then `shutil.which("bash")`.
  - `main(argv: list[str] | None = None) -> int`.

**The `main` subcommands:**
- **`start`** (also the default when no subcommand is given):
  - If `STRANGER_PINGS_SHELL` is set, print "Stranger Pings is already running in this window." and return 0.
  - Otherwise `prepare` for the saved step and print `BANNER`, plus `RESUME` (step 1–8) or `DONE_ALREADY` (step 9).
  - Then `os.chdir(start_folder)` and `os.execvpe` the shell from `shell_command(choose_shell($SHELL), state)`.
- **`reset`:** `world.wipe`, then `clear_progress`, then the same as `start`. Inside the game it instead runs `prepare(0)`, prints a one-line confirmation, and returns 0.
- **`skip COMMAND`:** `COMMAND` must be in `COMMANDS`; otherwise print the valid ones to stderr and exit 2. It saves `Progress(step=COMMANDS.index(COMMAND))` and runs `prepare` for that step. Inside the game it prints "Skipped to the COMMAND slide." and returns 0; outside the game it's the same as `start`.
- **`popups {auto,tk}`:** calls `save_popup_style` and prints a confirmation. argparse rejects anything else with exit 2.
- **`check --shell {zsh,bash} --status N --before DIR --after DIR -- LINE`** (the hook):
  - load the progress, run `check`, and save the progress;
  - print the hint (`story.hint_text`) in yellow to **stderr**, and `FINAL_MESSAGE` if finished;
  - `spawn` the popup with the saved style;
  - write `lights(step, shell) + "\n" + (str(move_to) if move_to else "") + "\n"` to stdout as UTF-8 bytes, whatever the locale.
  - Any exception gives exit 0 and the best lights line available, and the traceback is appended to `<state>/errors.log` if that's writable. The terminal never sees a traceback.
- **`status --shell {zsh,bash}`:** the same two stdout lines, using the current progress, with an empty move line.

- [ ] **Step 1: Write `tests/test_popup.py`:**
  - `test_methods_per_platform_and_style`: the four `popup_methods` cases above.
  - `test_popup_log_records_the_message`: runs `popup.py auto "hi there"` as a subprocess with `STRANGER_PINGS_POPUP_LOG` set, and finds `hi there\n` in the log.
- [ ] **Step 2: Write `tests/test_cli.py`.** Each test runs `[sys.executable, "stranger_pings.py", …]` as a subprocess with `cwd=REPO_DIR`, `HOME=<tmp>`, `STRANGER_PINGS_SHELL=1`, and `STRANGER_PINGS_POPUP_LOG=<tmp>/popups.log`. Define a `cli(*args)` helper in the test class that returns the `CompletedProcess`, and a `check_line(line, status, before, after)` helper that calls `cli("check", "--shell", "bash", "--status", …, "--", line)`.
  - `test_lights_for_each_shell`: `lights(3, "zsh")` contains `%F{` and 3 `●` and 6 `○`; `lights(3, "bash")` contains `\[` and the same counts.
  - `test_check_success_prints_lights_and_shows_popup`: `skip echo`, then `check_line("echo hi", 0, H, H)`. stdout line 1 has 1 `●`; line 2 is empty. Within 5 s the popup log contains `POPUPS[0]`.
  - `test_check_hint_goes_to_stderr`: `check_line("ehco hi", 127, H, H)`. stderr contains `hint_text("typo:echo")`, and stdout line 1 has 0 `●`.
  - `test_check_after_cat_moves_into_upside_down`: `skip cat`, then `check_line("cat walkie_talkie", 0, H, H)`. stdout line 2 is `str(mirror)`.
  - `test_skip_inside_the_game`: `skip mkdir` → exit 0, and the saved step is 4. Then `check_line("stranger-pings skip mkdir", 0, H, H)` → line 2 is `str(mirror)`.
  - `test_skip_rejects_unknown_command`: `skip dance` → exit 2, and stderr names `rmdir`.
  - `test_reset_keeps_popup_style`: `popups tk`, `skip cp`, `reset` → the step is 0, `~/upside_down` is gone, and the style is still `tk`.
  - `test_bad_popup_style`: `popups banana` → exit 2.
  - `test_start_inside_the_game_does_not_nest`: `start` → exit 0 and stdout says "already running".
  - `test_check_never_breaks_the_shell` *(Review Focus 1)*: create the state folder's parent path as a regular **file**, so the state can't be saved. `check_line("echo hi", 0, H, H)` → exit 0, stdout line 1 has 9 bulb characters, and stderr has no `Traceback`.
  - `test_check_does_not_wait_for_the_popup` *(Review Focus 3)*: make `STRANGER_PINGS_POPUP_LOG` a FIFO (`os.mkfifo`) with no reader, so the popup process blocks opening it. `skip echo`, then run `check_line("echo hi", …)` via `subprocess.run(…, capture_output=True, timeout=10)`. It must return. Afterwards open the FIFO with `O_RDONLY | O_NONBLOCK` to release the popup process.
  - `test_shell_command_zsh`: `shell_command("/bin/zsh", state)`. argv is `["/bin/zsh"]`, `env["ZDOTDIR"] == str(state/"zsh")`, `env["SHELL_SESSIONS_DISABLE"] == "1"`, and `(state/"zsh"/".zshrc")` matches `shell/zshrc`.
  - `test_shell_command_bash`: argv ends with `["--rcfile", str(APP_DIR/"shell"/"bashrc"), "-i"]`.
  - `test_choose_shell`: `/bin/zsh` → `/bin/zsh`; `/usr/bin/bash` → `/usr/bin/bash`; `/usr/bin/fish` → whichever of zsh or bash `shutil.which` finds first.
- [ ] **Step 3: Run the tests and confirm they fail.** Run `python3 -m unittest discover -s tests -v`. Expected: `ModuleNotFoundError: No module named 'popup'`.
- [ ] **Step 4: Implement `popup.py`, then `stranger_pings.py`,** as specified above. Keep `check` fast: import `subprocess` only inside `popup.spawn`, and import no tkinter in the `check` path.
- [ ] **Step 5: Run the tests and confirm they pass.** Run `python3 -m unittest discover -s tests -v`. Expected: all pass.
- [ ] **Step 6: Commit**
  ```bash
  git add popup.py stranger_pings.py shell/zshrc shell/bashrc tests/test_popup.py tests/test_cli.py
  git commit -m "feat: stranger-pings command, hook protocol, and popups"
  ```

---

### Task 5: The shell add-on, tested in real shells

**Files:**
- Modify: `shell/zshrc`, `shell/bashrc` (placeholders from Task 4)
- Create: `tests/terminal.py`, `tests/test_shells.py`

**Interfaces:**
- Consumes: the `check`/`status` stdout protocol and the environment variables from `shell_command` (Task 4).
- Produces: `tests/terminal.py`, with:
  - `class GameTerminal(home: Path, shell: str, env: dict[str, str] | None = None)`. It starts the game command in a pseudoterminal with `HOME=home`, `SHELL=shell`, `TERM=dumb`, and `STRANGER_PINGS_POPUP_LOG=home/"popups.log"`.
  - The game command is `STRANGER_PINGS_COMMAND` split with `shlex` if that variable is set; otherwise `[sys.executable, REPO_DIR/"stranger_pings.py"]`.
  - `.send(line: str)` types a line and presses Return.
  - `.until_prompt(timeout: float = 10) -> str` returns everything printed up to the next prompt, with ANSI codes stripped. A prompt is 9 bulb characters, a space, a folder name, and `% `.
  - `.lit() -> int` gives the number of `●` in the last prompt.
  - `.popups() -> list[str]` reads the popup log, waiting up to 5 s for it to grow when asked to via `.popups(expect=n)`.
  - `.close()`.

**What both startup files do:**
- They define `stranger-pings` as a shell function that runs `"$STRANGER_PINGS_PYTHON" -E -s "$STRANGER_PINGS_APP/stranger_pings.py" "$@"`.
- They define one function that runs the checker (`check` or `status`) and splits its stdout into the lights and the move line. It sets the prompt to `<lights> <folder> % `: zsh uses `PROMPT="$lights %1~ %# "` and bash uses `PS1="$lights \W % "`. If the move line is non-empty, it runs `cd -- "$move"`. Empty output (a crash) leaves the prompt alone.
- They call `status` once at startup.
- **zsh:**
  - `unset HISTFILE`.
  - A `preexec` hook saves `$1` and `$PWD`.
  - A `precmd` hook reads `$?` as its very first statement. It must be **prepended** to `precmd_functions`, because macOS's `/etc/zshrc` registers its own precmd functions first. If no command was saved (an empty Return), it does nothing. Otherwise it clears the saved line and runs `check`.
- **bash:**
  - `HISTFILE=`, `HISTCONTROL=`, `HISTIGNORE=`.
  - A `PROMPT_COMMAND` function reads `$?` first, then parses `HISTTIMEFORMAT= history 1` into a number and a line. It runs `check` only when the number differs from the last one seen, then stores `$PWD` as the next command's `before`.

- [ ] **Step 1: Write `tests/test_shells.py`.** A mixin with the tests below runs once per shell, through two classes:
  - `BashTests(ShellMixin, unittest.TestCase)` with `SHELL = shutil.which("bash")`;
  - `ZshTests(…)` with `SHELL = shutil.which("zsh")`, using `skipUnless(shutil.which("zsh"), "install zsh to test the Mac's shell")`.

  Tests:
  - `test_play_through`: start the game, then `send` each `SOLUTION` line and wait for the prompt. After each line, `lit()` follows `[1,2,3,4,5,5,6,7,8,9]`. `popups(expect=9)` equals `list(story.POPUPS)`. The output after `pwd` contains `str(home/"upside_down"/"hawkins")`. The output after `rmdir gate` contains the first line of `FINAL_MESSAGE`.
  - `test_typo_hint_appears_before_the_next_prompt`: `ehco hi` → the text before the prompt contains `hint_text("typo:echo")`.
  - `test_empty_return_checks_nothing` *(Review Focus 5)*: `ehco hi`, then `""` → the second output has no hint.
  - `test_same_typo_twice_hints_twice` *(Review Focus 5)*: start the game with `HISTCONTROL=ignoredups:ignorespace` in the environment, then send `ehco hi` twice → both outputs have the hint.
  - `test_leading_space_is_still_checked` *(Review Focus 5)*: start with the same environment, then send ` ehco hi` → hint.
  - `test_resume_after_closing_the_terminal`: play to `lit() == 4`, send `exit`, then start a new `GameTerminal` with the same home → `lit() == 4`, and `pwd` prints the Upside Down path.
  - `test_skip_inside_the_game_moves_the_shell`: `stranger-pings skip cp` → the next prompt has `lit() == 6`, and `pwd` prints the Upside Down path.
  - `test_students_own_startup_files_are_ignored`: write `~/.zshrc` and `~/.bashrc` with `echo LEAKED`. Starting the game → `LEAKED` doesn't appear.

- [ ] **Step 2: Run the tests and confirm they fail.** Run `python3 -m unittest discover -s tests -p test_shells.py -v`. Expected: the bash tests fail because no prompt with lights appears before the timeout. The zsh tests are skipped if zsh is missing.
- [ ] **Step 3: Write `shell/zshrc` and `shell/bashrc`** as described above. Each has a comment header saying what it is and that the student's own files are never read.
- [ ] **Step 4: Run the tests and confirm they pass.** Run `python3 -m unittest discover -s tests -v`. Expected: all pass. **The zsh tests must run, not be skipped:** if `zsh` is missing, stop and ask Nate to run `! sudo dnf install zsh`.
- [ ] **Step 5: Commit**
  ```bash
  git add shell/zshrc shell/bashrc tests/terminal.py tests/test_shells.py
  git commit -m "feat: zsh and bash add-on that checks every command"
  ```

---

### Task 6: Launcher, shortcut, and release build

**Files:**
- Create: `tools/stranger-pings` (mode 755), `tools/Stranger Pings.command` (mode 755)
- Delete: `tools/ready-player-root`
- Modify: `tools/build_release.py`

**Interfaces:**
- Consumes: `stranger_pings.py`, every module from Tasks 1–4, and `shell/` (Task 5).
- Produces: `dist/stranger-pings-<platform>.tar.gz`, whose top folder `stranger-pings/` holds the modules, `shell/zshrc`, `shell/bashrc`, `README.md`, `stranger-pings`, `Stranger Pings.command`, and `python/<arch>/`.

- [ ] **Step 1: Write `tools/stranger-pings`.** Copy `tools/ready-player-root`; the only change is the last line, `exec "$PYTHON" -E -s "$DIR/stranger_pings.py" "$@"`. Write `tools/Stranger Pings.command` as `#!/bin/sh` plus `exec "$(dirname "$0")/stranger-pings"`. Run `chmod 755` on both, then `git rm tools/ready-player-root`.
- [ ] **Step 2: Update `tools/build_release.py`:**
  - `TOP = "stranger-pings"`;
  - `APP_FILES` is the six modules plus `README.md`;
  - `SHELL_FILES = ("shell/zshrc", "shell/bashrc")`, added after a `shell` folder entry;
  - `LAUNCHERS = (tools/stranger-pings, tools/Stranger Pings.command)`, each added at mode `0o755`;
  - the output is named `stranger-pings-<platform>.tar.gz`;
  - the module docstring names Stranger Pings.
- [ ] **Step 3: Build the Linux bundle and run the real-shell tests against it.**
  ```bash
  python3 tools/build_release.py linux
  B=$(mktemp -d) && tar -xpzf dist/stranger-pings-linux.tar.gz -C "$B"
  STRANGER_PINGS_COMMAND="$B/stranger-pings/stranger-pings" python3 -m unittest discover -s tests -p test_shells.py -v
  ```
  Expected: all pass, with the bundled Python running the game. Then run `python3 tools/build_release.py` (macOS). Expected: it prints `dist/stranger-pings-macos.tar.gz`. Check with `tar -tzf` that it contains `stranger-pings/python/arm64/bin/python3`, `stranger-pings/python/x86_64/bin/python3`, `stranger-pings/shell/zshrc`, and `stranger-pings/Stranger Pings.command`.
- [ ] **Step 4: Commit**
  ```bash
  git add "tools/stranger-pings" "tools/Stranger Pings.command" tools/build_release.py
  git commit -m "feat: Stranger Pings launcher, double-click shortcut, and release build"
  ```

---

### Task 7: Slide text, morning checklist, and docs

**Files:**
- Create: `docs/slides.md`, `docs/morning-checklist.md`
- Modify: `README.md`, `COMMANDS.md`, `SPEC.md`, `TODO.md`, `DEVLOG.md`

- [ ] **Step 1: Write `docs/slides.md`** (spec: "The slide text"). It has a title slide, a "Today's Activity" slide covering the story setup and how the activity works, then nine command slides in `COMMANDS` order. Each command slide has:
  - **Story**: the beat from the spec's step table;
  - **What it does**: one sentence;
  - **Type this**: the exact `SOLUTION` line(s). The cd slide shows both lines, and the echo slide says "any message";
  - **Tip**, where it helps:
    - echo: "press Return to run it";
    - cat: "Control-C gets you out if it seems stuck";
    - mkdir: "use `_` instead of spaces";
    - rm: "a `/` means *inside*";
    - rmdir: "only works on an empty folder";
  - **Speaker notes**:
    - what to say;
    - what success looks like: the popup's first words, and "N bulbs lit";
    - the 1–2 mistakes to watch for, taken from Task 3's hint table.

  The intro slides on what a computer, the terminal, and Bash are aren't touched; note that at the top.
- [ ] **Step 2: Write `docs/morning-checklist.md`** (spec: "Must check on a real Mac before class"). It's numbered steps for one Mac:
  - install with the `curl` line;
  - log in as a student account, then start the game with the full path or by double-clicking `Stranger Pings.command`;
  - type `echo hi` and confirm:
    - the popup appears in front;
    - clicking OK puts typing back in Terminal;
    - one bulb lights;
    - the prompt comes back quickly;
  - type `ehco hi` and confirm the hint;
  - run `stranger-pings reset`.

  An "If something's wrong" section maps each failure to its fix:
  - popup behind Terminal or missing → `stranger-pings popups tk` in each student account;
  - typing doesn't return → add "click back into Terminal" to the slides;
  - slow prompt → note it and carry on.
- [ ] **Step 3: Rewrite `README.md` for Stranger Pings.** It covers:
  - what it is;
  - requirements;
  - setting up classroom Macs (the `curl` line with `stranger-pings-macos.tar.gz`, `/Users/Shared/stranger-pings/stranger-pings`, the `.command` shortcut, and why `curl` instead of a browser);
  - running from the repo (`python3 stranger_pings.py`);
  - helper commands;
  - how checking works, in 3–4 sentences;
  - editing the story text (`story.py`);
  - tests (`python3 -m unittest discover -s tests -v`; zsh tests need zsh);
  - building a release.
- [ ] **Step 4: Update the rest.**
  - `COMMANDS.md`: the four helper commands.
  - `SPEC.md`: a short Stranger Pings summary that points to the design doc.
  - `TODO.md`: paste `docs/slides.md` into Google Slides; run `docs/morning-checklist.md` on class day; team review of `story.py` text.
  - `DEVLOG.md`: a new entry in the existing format, "11/10/26 - Nate Rupard (with Claude)", summarizing Tasks 1–7.
- [ ] **Step 5: Run the whole suite.** Run `python3 -m unittest discover -s tests -v`. Expected: all pass, with zsh tests running.
- [ ] **Step 6: Commit**
  ```bash
  git add docs/slides.md docs/morning-checklist.md README.md COMMANDS.md SPEC.md TODO.md DEVLOG.md
  git commit -m "docs: slide text, morning checklist, and README for Stranger Pings"
  ```

---

## Verification

1. **Full suite:** `python3 -m unittest discover -s tests -v`. Everything passes, with **no zsh skips**.
2. **Python 3.9 floor:** run `uv run --no-project --python 3.9 python -m unittest discover -s tests -v` and the same with `--python 3.12`. (uv is at `~/.local/bin/uv`.)
3. **Bundle:** rerun Task 6, Step 3 against a fresh Linux build.
4. **By hand, in a real terminal on this machine:**
   - Run `python3 stranger_pings.py` and play all nine slides.
   - Watch for each real popup (tkinter or zenity), the bulbs lighting, the `pwd` reveal, and the final message.
   - Then run `stranger-pings reset`.
   - Run `exit`, then `rm -rf ~/hawkins ~/upside_down ~/.local/state/stranger_pings` to clean up.
5. **Not verifiable here:** the Mac-only items in `docs/morning-checklist.md`. Tell Nate plainly that these are untested.
