"""
The game rules: after every command a student runs, decides whether they
finished the slide, what hint (if any) to give, and where their shell belongs.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from parse import Command, paths, split_line
from progress import Progress
import story
import world

# Names a student might type with a space instead of the underscore
_UNDERSCORE_NAMES = {part for relative in story.FILES for part in relative.split("/")
                     if "_" in part} | {"castle_byers"}
_HELPER_MOVES = {"", "start", "reset", "skip"}


@dataclass(frozen=True)
class Report:
    """What the shell add-on saw: the line typed, its exit status, and the folder before and after"""

    line: str
    status: int
    before: Path
    after: Path


@dataclass
class Outcome:
    """What the game does about one typed line"""

    hint: str | None = None        # a `story.HINTS` key, or `typo:<command>`
    popup: str | None = None       # popup text to show
    move_to: Path | None = None    # folder to move the student's shell into
    finished: bool = False         # the last slide was just finished


def _same(first: Path, second: Path) -> bool:
    """Returns whether two paths are the same place, even if one no longer exists"""

    try:
        return os.path.samefile(first, second)
    except OSError:
        return os.path.normpath(first) == os.path.normpath(second)


def _distance(first: str, second: str) -> int:
    """Returns how many typing mistakes turn `first` into `second` (a swap counts as one)"""

    rows = [[0] * (len(second) + 1) for _ in range(len(first) + 1)]
    for i in range(len(first) + 1):
        rows[i][0] = i
    for j in range(len(second) + 1):
        rows[0][j] = j
    for i in range(1, len(first) + 1):
        for j in range(1, len(second) + 1):
            cost = 0 if first[i - 1] == second[j - 1] else 1
            rows[i][j] = min(rows[i - 1][j] + 1, rows[i][j - 1] + 1, rows[i - 1][j - 1] + cost)
            if i > 1 and j > 1 and first[i - 1] == second[j - 2] and first[i - 2] == second[j - 1]:
                rows[i][j] = min(rows[i][j], rows[i - 2][j - 2] + 1)
    return rows[-1][-1]


def _typo_of(name: str, step: int) -> str | None:
    """Returns which of the nine commands `name` looks like a misspelling of, if any"""

    current = story.COMMANDS[step]
    candidates = []
    for order, command in enumerate(story.COMMANDS):
        distance = _distance(name, command)
        if 0 < distance <= (2 if len(command) >= 4 else 1):
            candidates.append((distance, command != current, order, command))
    return min(candidates)[3] if candidates else None


def _words(command: Command) -> list[str]:
    """Returns the arguments that aren't options like `-r`"""
    return [arg for arg in command.args if not arg.startswith("-")]


def _all_paths(command: Command, report: Report, home: Path) -> list[Path]:
    """Returns every path the command's arguments point to"""
    return [path for word in _words(command) for path in paths(word, report.before, home)]


def _completes(step: int, command: Command, report: Report, progress: Progress,
               home: Path, last: bool) -> bool:
    """
    Returns whether `command` finishes the slide for `step`.\n
    The exit status belongs to the line's last command, so an earlier command
    on the line (`echo hi; oops`) is taken to have worked.
    """

    name = story.COMMANDS[step]
    ok = report.status == 0 or not last
    if command.name.lower() != name:
        return False
    if name == "echo":
        return ok and bool(command.args)
    if name in ("ls", "pwd"):
        return ok
    if name == "cat":
        walkie_talkie = world.hawkins(home) / "walkie_talkie"
        return walkie_talkie.is_file() and any(
            _same(path, walkie_talkie) for path in _all_paths(command, report, home))
    if name == "mkdir":
        return ok and world.castle(home).is_dir()
    if name == "cd":
        return progress.entered_castle and _same(report.after, world.mirror(home))
    if name == "cp":
        eggos = world.mirror(home) / "eggos"
        if not ok or not eggos.is_file() or not world.castle(home).is_dir():
            return False
        contents = eggos.read_bytes()
        return any(path.is_file() and path.read_bytes() == contents
                   for path in world.castle(home).iterdir())
    if name == "rm":
        demogorgon = world.gate(home) / "demogorgon"
        return not (demogorgon.exists() or demogorgon.is_symlink())
    return ok and not world.gate(home).exists()   # rmdir


def _current_hint(step: int, command: Command, report: Report, progress: Progress,
                  home: Path) -> tuple[str | None, Path | None]:
    """Returns the hint (and any move) for using this slide's own command the wrong way"""

    name = story.COMMANDS[step]
    words = _words(command)
    failed = report.status != 0
    mirror = world.mirror(home)
    if name == "echo" and not command.args:
        return "echo_empty", None
    if name == "echo" and failed:
        return "echo_letters", None
    if any(f"{first}_{second}" in _UNDERSCORE_NAMES for first, second in zip(words, words[1:])):
        return "spaces", None
    if name == "cat":
        if not words:
            return "cat_no_file", None
        if failed:
            folder = any(path.is_dir() for path in _all_paths(command, report, home))
            return ("cat_folder" if folder else "cat_missing"), None
        return None, None
    if name in ("mkdir", "cp", "rm", "rmdir") and not _same(report.before, mirror):
        return "wrong_folder", mirror
    if name == "mkdir" and not failed:
        return "mkdir_name", None
    if name == "cd" and not (_same(report.after, mirror) or _same(report.after, world.castle(home))):
        return "cd_lost", world.castle(home) if progress.entered_castle else mirror
    if name == "cp":
        if len(words) < 2:
            return "cp_destination", None
        destination = paths(words[-1], report.before, home)[0]
        if not (_same(destination, world.castle(home))
                or _same(destination.parent, world.castle(home))):
            return "cp_wrong_place", None
    if name == "rm":
        targets = _all_paths(command, report, home)
        if any(_same(path, world.gate(home)) for path in targets):
            return "rm_folder", None
        if any(path.name == "demogorgon" and not _same(path.parent, world.gate(home))
               for path in targets):
            return "rm_inside_gate", None
    if name == "rmdir" and world.gate(home).is_dir() and any(world.gate(home).iterdir()):
        return "gate_not_empty", None
    return ("try_again" if failed else None), None


def _hint(step: int, command: Command, report: Report, progress: Progress,
          home: Path) -> tuple[str | None, Path | None]:
    """Returns the hint (and any move) for a command that didn't finish the slide"""

    name = command.name.lower()
    if report.status == 127 and name in story.COMMANDS and command.name != name:
        return "lowercase", None
    if report.status == 127:
        for known in sorted(story.COMMANDS, key=len, reverse=True):
            if name.startswith(known) and name[len(known):len(known) + 1] in ("-", ".", "/", "~"):
                return f"space:{known}", None
        typo = _typo_of(command.name, step)
        if typo:
            return f"typo:{typo}", None
    if (story.COMMANDS[step] == "rmdir" and name == "rm"
            and not world.gate(home).exists()):
        return "use_rmdir", None
    if name in story.COMMANDS[step + 1:]:
        # A `cd` before its slide would leave the student lost, so bring them back
        start = world.start_folder(step, home)
        return "later", (start if name == "cd" and not _same(report.after, start) else None)
    if name == story.COMMANDS[step]:
        return _current_hint(step, command, report, progress, home)
    return None, None


def check(report: Report, progress: Progress, home: Path) -> Outcome:
    """
    Judges one typed line, updates `progress`, and quietly repairs anything the
    student broke that the current slide needs.
    """

    outcome = Outcome()
    if progress.step >= world.FINISHED:
        return outcome
    commands = split_line(report.line)
    if commands and Path(commands[0].name).name == "stranger-pings":
        # A helper's command; it has already updated the progress and the world
        if (commands[0].args[:1] or ("",))[0] in _HELPER_MOVES:
            outcome.move_to = world.start_folder(progress.step, home)
        return outcome

    after_existed = report.after.is_dir()
    for index, command in enumerate(commands):
        if progress.step >= world.FINISHED:
            break
        step = progress.step
        if _completes(step, command, report, progress, home, index == len(commands) - 1):
            progress.step += 1
            progress.entered_castle = False
            outcome.popup = story.POPUPS[step]
            if progress.step == world.PULLED_IN:
                outcome.move_to = world.mirror(home)
            outcome.finished = progress.step == world.FINISHED
        elif (story.COMMANDS[step] == "cd" and command.name.lower() == "cd"
              and _same(report.after, world.castle(home))):
            progress.entered_castle = True
            outcome.hint = outcome.hint or "cd_back_out"
        elif outcome.hint is None:
            outcome.hint, move = _hint(step, command, report, progress, home)
            outcome.move_to = outcome.move_to or move

    world.prepare(progress.step, home)
    if outcome.move_to is None:
        if not report.after.is_dir():
            # The repair took away the folder the shell is in; never leave it there
            outcome.move_to = world.start_folder(progress.step, home)
        elif not after_existed:
            # The repair rebuilt the folder the shell is in; step back into the new one
            outcome.move_to = report.after
    return outcome
