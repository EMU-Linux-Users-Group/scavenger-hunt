"""
Stranger Pings: a terminal lesson where every slide is one step of a Stranger
Things story.\n
Helpers run `stranger-pings` to open the game in a Terminal window. The game's
shell add-on runs `stranger_pings.py check` after every command a student types.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
import traceback

from checker import Report, check
from progress import (POPUP_STYLES, Progress, clear_progress, load_popup_style, load_progress,
                      save_popup_style, save_progress, state_dir)
import story
import world

APP_DIR = Path(__file__).resolve().parent
_ZSH_COLORS = ("red", "yellow", "green", "blue", "magenta")
_BASH_COLORS = (31, 33, 32, 34, 35)
_YELLOW, _GREEN, _PLAIN = "\033[33m", "\033[32m", "\033[0m"


def lights(step: int, shell: str) -> str:
    """Returns the prompt's string of Christmas lights: one lit bulb per finished slide"""

    bulbs = []
    for index in range(len(story.COMMANDS)):
        lit = index < step
        bulb = "●" if lit else "○"
        if shell == "zsh":
            color = _ZSH_COLORS[index % len(_ZSH_COLORS)] if lit else "8"
            bulbs.append(f"%F{{{color}}}{bulb}%f")
        else:
            code = _BASH_COLORS[index % len(_BASH_COLORS)] if lit else 90
            bulbs.append(f"\\[\\e[{code}m\\]{bulb}\\[\\e[0m\\]")
    return "".join(bulbs)


def choose_shell(env_shell: str) -> str | None:
    """
    Returns the shell to play in: zsh whenever the computer has it (the student's
    own zsh first), otherwise bash.\n
    zsh comes first because it's what the classroom Macs are tested with; a Mac's
    own bash is very old.
    """

    if Path(env_shell).name == "zsh":
        return env_shell
    import shutil  # pylint: disable=import-outside-toplevel
    return shutil.which("zsh") or (env_shell if Path(env_shell).name == "bash" else None) \
        or shutil.which("bash")


def shell_command(shell_path: str, state: Path) -> tuple[list[str], dict[str, str]]:
    """
    Returns how to start the student's shell with the game's add-on: its
    arguments and the extra environment it needs.\n
    The student's own startup files are never read, and zsh keeps its files in
    the student's state folder, because the app folder is read-only for them.
    """

    env = {"STRANGER_PINGS_SHELL": "1", "STRANGER_PINGS_PYTHON": sys.executable,
           "STRANGER_PINGS_APP": str(APP_DIR), "STRANGER_PINGS_PYCACHE": str(state / "pycache")}
    if "zsh" in Path(shell_path).name:
        zdotdir = state / "zsh"
        zdotdir.mkdir(parents=True, exist_ok=True)
        (zdotdir / ".zshrc").write_bytes((APP_DIR / "shell" / "zshrc").read_bytes())
        env.update(ZDOTDIR=str(zdotdir), SHELL_SESSIONS_DISABLE="1")
        return [shell_path], env
    env["BASH_SILENCE_DEPRECATION_WARNING"] = "1"
    return [shell_path, "--rcfile", str(APP_DIR / "shell" / "bashrc"), "-i"], env


def _in_game() -> bool:
    """Returns whether this is running inside the game's own shell"""
    return bool(os.environ.get("STRANGER_PINGS_SHELL"))


def _start(home: Path, state: Path) -> int:
    """Opens the game in this Terminal window, picking up where the student left off"""

    if _in_game():
        print("Stranger Pings is already running in this window.")
        return 0
    progress = load_progress(state)
    world.prepare(progress.step, home)
    print(story.BANNER)
    if 0 < progress.step < world.FINISHED:
        print("  " + story.RESUME.format(command=story.COMMANDS[progress.step]) + "\n")
    elif progress.step == world.FINISHED:
        print("  " + story.DONE_ALREADY + "\n")
    # STRANGER_PINGS_USE_SHELL picks a shell outright (the tests use it to play in bash)
    shell = os.environ.get("STRANGER_PINGS_USE_SHELL") or choose_shell(os.environ.get("SHELL", ""))
    if shell is None:
        print("Stranger Pings needs zsh or bash, and this computer has neither.", file=sys.stderr)
        return 1
    argv, env = shell_command(shell, state)
    os.chdir(world.start_folder(progress.step, home))
    sys.stdout.flush()
    os.execvpe(argv[0], argv, {**os.environ, **env})
    return 0   # not reached: the shell replaces this process


def _reset(home: Path, state: Path) -> int:
    """Throws away the student's world and progress and starts fresh"""

    world.wipe(home)
    clear_progress(state)
    if _in_game():
        world.prepare(0, home)
        print("Fresh start! Back to the first slide.")
        return 0
    return _start(home, state)


def _skip(command: str, home: Path, state: Path) -> int:
    """Jumps the student to the slide for `command`, as if they'd done every slide before it"""

    step = story.COMMANDS.index(command)
    save_progress(state, Progress(step))
    world.prepare(step, home)
    if _in_game():
        print(f"Skipped to the {command} slide.")
        return 0
    return _start(home, state)


def _write_protocol(step: int, shell: str, move_to: Path | None):
    """Writes the two lines the shell add-on reads: the lights, then where to `cd` (if anywhere)"""

    text = lights(step, shell) + "\n" + (str(move_to) if move_to else "") + "\n"
    sys.stdout.buffer.write(text.encode("utf-8"))
    sys.stdout.flush()


def _log_error(state: Path):
    """Keeps the current error's traceback out of the student's terminal, in errors.log if possible"""

    try:
        state.mkdir(parents=True, exist_ok=True)
        with open(state / "errors.log", "a", encoding="utf-8") as log:
            log.write(traceback.format_exc() + "\n")
    except OSError:
        pass


def _say(text: str, color: str):
    """Prints a line for the student, in color, where the shell add-on doesn't read it"""
    print(f"{color}{text}{_PLAIN}", file=sys.stderr, flush=True)


def _check(args: argparse.Namespace, home: Path, state: Path) -> int:
    """Judges one typed line for the shell add-on; never fails in a way the student sees"""

    progress = Progress()
    try:
        progress = load_progress(state)
        report = Report(args.line, args.status, Path(args.before), Path(args.after))
        outcome = check(report, progress, home)
        try:
            save_progress(state, progress)
        except OSError:
            _log_error(state)
        if outcome.hint:
            _say("  " + story.hint_text(outcome.hint), _YELLOW)
        if outcome.finished:
            _say(story.FINAL_MESSAGE, _GREEN)
        if outcome.popup:
            from popup import spawn  # pylint: disable=import-outside-toplevel
            spawn(outcome.popup, load_popup_style(state))
        _write_protocol(progress.step, args.shell, outcome.move_to)
    except Exception:  # pylint: disable=broad-except
        _log_error(state)
        _write_protocol(progress.step, args.shell, None)
    return 0


def main(argv: list[str] | None = None) -> int:
    """Runs a `stranger-pings` command"""

    parser = argparse.ArgumentParser(prog="stranger-pings",
                                     description="Stranger Pings terminal lesson")
    commands = parser.add_subparsers(dest="command")
    commands.add_parser("start", help="open the game in this window (the default)")
    commands.add_parser("reset", help="start over from the first slide")
    skip = commands.add_parser("skip", help="jump to a slide, e.g. `skip mkdir`")
    skip.add_argument("slide", choices=story.COMMANDS)
    popups = commands.add_parser("popups", help="which popups to use on this account")
    popups.add_argument("style", choices=POPUP_STYLES)
    for name in ("check", "status"):
        hook = commands.add_parser(name, help="used by the game's shell add-on")
        hook.add_argument("--shell", choices=("zsh", "bash"), required=True)
        if name == "check":
            hook.add_argument("--status", type=int, required=True)
            hook.add_argument("--before", required=True)
            hook.add_argument("--after", required=True)
            hook.add_argument("line", nargs="?", default="")
    args = parser.parse_args(argv)

    home = Path.home()
    state = state_dir(home)
    if args.command == "check":
        return _check(args, home, state)
    if args.command == "status":
        _write_protocol(load_progress(state).step, args.shell, None)
        return 0
    if args.command == "reset":
        return _reset(home, state)
    if args.command == "skip":
        return _skip(args.slide, home, state)
    if args.command == "popups":
        save_popup_style(state, args.style)
        print(f"Popups on this account now use: {args.style}")
        return 0
    return _start(home, state)


if __name__ == "__main__":
    sys.exit(main())
