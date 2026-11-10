"""Reads a typed command line the way the shell would, closely enough to judge it"""

from __future__ import annotations

from dataclasses import dataclass
import glob
from pathlib import Path
import re
import shlex

_ASSIGNMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")


@dataclass(frozen=True)
class Command:
    """One command from a typed line: its name and the words after it"""

    name: str
    args: tuple[str, ...] = ()


def _is_separator(token: str) -> bool:
    """Returns whether `token` ends one command and starts the next (`;`, `&&`, `|`, ...)"""
    return set(token) <= set(";&|()")


def _is_redirection(token: str) -> bool:
    """Returns whether `token` sends output to or reads input from a file (`>`, `>>`, `<`, ...)"""
    return set(token) <= set("<>&") and bool(set(token) & set("<>"))


def _commands(tokens: list[str]) -> list[Command]:
    """Groups the tokens of one line into commands"""

    commands = []
    words: list[str] = []
    skip_next = False
    for token in tokens + [";"]:
        if skip_next:
            skip_next = False
        elif _is_redirection(token):
            skip_next = True
        elif _is_separator(token):
            while words and _ASSIGNMENT.match(words[0]):
                words.pop(0)
            if words:
                commands.append(Command(words[0], tuple(words[1:])))
            words = []
        else:
            words.append(token)
    return commands


def split_line(line: str) -> list[Command]:
    """
    Splits what a student typed into commands, with quotes removed and
    redirections dropped.\n
    Lines that can't be read, or that use command substitution, give no commands.
    """

    if "$(" in line or "`" in line:
        return []
    commands = []
    for part in line.split("\n"):
        lexer = shlex.shlex(part, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        try:
            tokens = list(lexer)
        except ValueError:
            return []
        commands += _commands(tokens)
    return commands


def paths(arg: str, cwd: Path, home: Path) -> list[Path]:
    """
    Returns the paths `arg` means when typed in `cwd`: `~` is the home folder,
    and wildcards expand to the sorted matches (or stay as typed if nothing matches).
    """

    if arg == "~" or arg.startswith("~/"):
        path = home / arg[2:]
    else:
        path = cwd / arg
    if any(char in arg for char in "*?["):
        matches = sorted(glob.glob(str(path)))
        if matches:
            return [Path(match) for match in matches]
    return [path]
