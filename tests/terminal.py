"""A real game shell in a pseudoterminal, typed into the way a student would (tests only)"""

from __future__ import annotations

import fcntl
import os
from pathlib import Path
import pty
import re
import select
import shlex
import signal
import struct
import subprocess
import sys
import termios
import time

REPO_DIR = Path(__file__).resolve().parent.parent
# Colors, cursor moves, window titles, and bracketed-paste switches
_ESCAPES = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)|\x1b[=>]")
_PROMPT = re.compile(r"([●○]{9}) (\S+) % $")


def _take_terminal():
    """Makes the pseudoterminal the new shell's controlling terminal, like a real Terminal window"""
    os.setsid()
    fcntl.ioctl(0, termios.TIOCSCTTY, 0)


class GameTerminal:
    """Starts `stranger-pings` in a pseudoterminal with its own home folder"""

    def __init__(self, home: Path, shell: str, env: dict[str, str] | None = None):
        self.home = home
        if os.environ.get("STRANGER_PINGS_COMMAND"):
            command = shlex.split(os.environ["STRANGER_PINGS_COMMAND"])
        else:
            command = [sys.executable, str(REPO_DIR / "stranger_pings.py")]
        full_env = {key: value for key, value in os.environ.items()
                    if not key.startswith("STRANGER_PINGS_")}
        full_env.update(HOME=str(home), SHELL=shell, TERM="dumb",
                        STRANGER_PINGS_USE_SHELL=shell,
                        STRANGER_PINGS_POPUP_LOG=str(home / "popups.log"))
        full_env.update(env or {})
        self.master, follower = pty.openpty()
        fcntl.ioctl(follower, termios.TIOCSWINSZ, struct.pack("HHHH", 50, 300, 0, 0))
        self.process = subprocess.Popen(  # pylint: disable=consider-using-with
            command, stdin=follower, stdout=follower, stderr=follower, env=full_env,
            cwd=home, preexec_fn=_take_terminal)  # pylint: disable=subprocess-popen-preexec-fn
        os.close(follower)
        self.buffer = ""
        self.prompt = ""

    def send(self, line: str):
        """Types `line` and presses Return"""
        os.write(self.master, (line + "\n").encode("utf-8"))

    def until_prompt(self, timeout: float = 10) -> str:
        """Returns everything printed before the next prompt, with colors removed"""
        end = time.time() + timeout
        while True:
            text = _ESCAPES.sub("", self.buffer).replace("\r", "")
            match = _PROMPT.search(text)
            if match:
                self.buffer = ""
                self.prompt = match.group(0)
                return text[:match.start()]
            remaining = end - time.time()
            if remaining <= 0:
                raise AssertionError(f"no game prompt after {timeout}s; got:\n{text[-2000:]}")
            ready, _, _ = select.select([self.master], [], [], remaining)
            if ready:
                try:
                    data = os.read(self.master, 65536)
                except OSError:   # the shell has exited
                    data = b""
                if not data:
                    raise AssertionError(f"the shell exited; got:\n{text[-2000:]}")
                self.buffer += data.decode("utf-8", errors="replace")

    def interrupt_while_checking(self, timeout: float = 5) -> bool:
        """
        Presses Control-C at the moment the game's checker is running (Linux only:
        it watches /proc for the checker) and returns whether it caught it.
        """
        end = time.time() + timeout
        while time.time() < end:
            for pid in os.listdir("/proc"):
                if not pid.isdigit():
                    continue
                try:
                    command = Path(f"/proc/{pid}/cmdline").read_bytes()
                except OSError:
                    continue
                if b"stranger_pings.py\0check" in command:
                    os.killpg(os.tcgetpgrp(self.master), signal.SIGINT)
                    return True
        return False

    def lit(self) -> int:
        """Returns how many bulbs are lit in the last prompt"""
        return self.prompt.count("●")

    def popups(self, expect: int = 0) -> list[str]:
        """Returns the popups shown so far, waiting up to 5 seconds for at least `expect`"""
        log = self.home / "popups.log"
        end = time.time() + 5
        while True:
            lines = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
            if len(lines) >= expect or time.time() > end:
                return lines
            time.sleep(0.05)

    def close(self):
        """Ends the shell and frees the pseudoterminal (calling it again does nothing)"""
        if self.master < 0:
            return
        if self.process.poll() is None:
            self.process.kill()
        self.process.wait(timeout=5)
        os.close(self.master)
        self.master = -1
