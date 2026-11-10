"""Tests for the `stranger-pings` command and the hook's `check`/`status` protocol"""

from __future__ import annotations

import os
from pathlib import Path
import select
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

from progress import load_popup_style, load_progress, state_dir
import story
from stranger_pings import APP_DIR, choose_shell, lights, shell_command
import world

REPO_DIR = Path(__file__).resolve().parent.parent


def bulbs(text: str) -> tuple[int, int]:
    """Returns how many lit and unlit bulbs `text` has"""
    return text.count("●"), text.count("○")


class CommandTests(unittest.TestCase):
    """Runs `stranger_pings.py` the way helpers and the shell add-on do"""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = Path(tmp.name)
        self.state = state_dir(self.home)
        self.log = self.home / "popups.log"
        self.hawkins = world.hawkins(self.home)

    def cli(self, *args: str, timeout: float = 20) -> subprocess.CompletedProcess:
        """Runs `stranger_pings.py` with `args` as if inside the game's shell"""
        env = {**os.environ, "HOME": str(self.home), "STRANGER_PINGS_SHELL": "1",
               "STRANGER_PINGS_POPUP_LOG": str(self.log)}
        return subprocess.run([sys.executable, "stranger_pings.py", *args], cwd=REPO_DIR,
                              env=env, capture_output=True, text=True, timeout=timeout,
                              check=False)

    def check_line(self, line: str, status: int, before: Path, after: Path,
                   timeout: float = 20) -> subprocess.CompletedProcess:
        """Runs the hook's `check` for one typed line"""
        return self.cli("check", "--shell", "bash", "--status", str(status), "--before",
                        str(before), "--after", str(after), "--", line, timeout=timeout)

    def popups(self, count: int) -> list[str]:
        """Waits up to 5 seconds for `count` popups and returns them"""
        end = time.time() + 5
        while time.time() < end:
            if self.log.exists() and len(self.log.read_text(encoding="utf-8").splitlines()) >= count:
                break
            time.sleep(0.05)
        return self.log.read_text(encoding="utf-8").splitlines() if self.log.exists() else []

    def test_lights_for_each_shell(self):
        self.assertIn("%F{", lights(3, "zsh"))
        self.assertEqual(bulbs(lights(3, "zsh")), (3, 6))
        self.assertIn("\\[", lights(3, "bash"))
        self.assertEqual(bulbs(lights(3, "bash")), (3, 6))

    def test_check_success_prints_lights_and_shows_popup(self):
        self.cli("skip", "echo")
        result = self.check_line("echo hi", 0, self.hawkins, self.hawkins)
        lit, move = result.stdout.split("\n")[:2]
        self.assertEqual((bulbs(lit), move), ((1, 8), ""))
        self.assertEqual(self.popups(1), [story.POPUPS[0]])

    def test_check_hint_goes_to_stderr(self):
        self.cli("skip", "echo")
        result = self.check_line("ehco hi", 127, self.hawkins, self.hawkins)
        self.assertIn(story.hint_text("typo:echo"), result.stderr)
        self.assertEqual(bulbs(result.stdout.split("\n")[0]), (0, 9))

    def test_check_after_cat_moves_into_upside_down(self):
        self.cli("skip", "cat")
        result = self.check_line("cat walkie_talkie", 0, self.hawkins, self.hawkins)
        self.assertEqual(result.stdout.split("\n")[1], str(world.mirror(self.home)))

    def test_skip_inside_the_game(self):
        self.assertEqual(self.cli("skip", "mkdir").returncode, 0)
        self.assertEqual(load_progress(self.state).step, 4)
        result = self.check_line("stranger-pings skip mkdir", 0, self.hawkins, self.hawkins)
        self.assertEqual(result.stdout.split("\n")[1], str(world.mirror(self.home)))

    def test_skip_rejects_unknown_command(self):
        result = self.cli("skip", "dance")
        self.assertEqual(result.returncode, 2)
        self.assertIn("rmdir", result.stderr)

    def test_reset_keeps_popup_style(self):
        self.cli("popups", "tk")
        self.cli("skip", "cp")
        self.assertEqual(self.cli("reset").returncode, 0)
        self.assertEqual(load_progress(self.state).step, 0)
        self.assertFalse((self.home / "upside_down").exists())
        self.assertEqual(load_popup_style(self.state), "tk")

    def test_bad_popup_style(self):
        self.assertEqual(self.cli("popups", "banana").returncode, 2)

    def test_start_inside_the_game_does_not_nest(self):
        result = self.cli("start")
        self.assertEqual(result.returncode, 0)
        self.assertIn("already running", result.stdout)

    def test_check_never_breaks_the_shell(self):
        (self.home / ".local").write_text("not a folder", encoding="utf-8")
        result = self.check_line("echo hi", 0, self.hawkins, self.hawkins)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(sum(bulbs(result.stdout.split("\n")[0])), 9)
        self.assertNotIn("Traceback", result.stderr)

    def test_check_does_not_wait_for_the_popup(self):
        self.cli("skip", "echo")
        os.mkfifo(self.log)
        result = self.check_line("echo hi", 0, self.hawkins, self.hawkins, timeout=10)
        self.assertEqual(bulbs(result.stdout.split("\n")[0]), (1, 8))
        # Let the waiting popup process finish
        reader = os.open(self.log, os.O_RDONLY | os.O_NONBLOCK)
        try:
            ready, _, _ = select.select([reader], [], [], 5)
            self.assertTrue(ready)
            self.assertIn(story.POPUPS[0].encode(), os.read(reader, 4096))
        finally:
            os.close(reader)


class ShellCommandTests(unittest.TestCase):
    """How the student's own shell is started with the game's add-on"""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.state = Path(tmp.name) / "state"

    def test_shell_command_zsh(self):
        argv, env = shell_command("/bin/zsh", self.state)
        self.assertEqual(argv, ["/bin/zsh"])
        self.assertEqual(env["ZDOTDIR"], str(self.state / "zsh"))
        self.assertEqual(env["SHELL_SESSIONS_DISABLE"], "1")
        self.assertEqual(env["STRANGER_PINGS_SHELL"], "1")
        self.assertEqual(env["STRANGER_PINGS_APP"], str(APP_DIR))
        self.assertEqual((self.state / "zsh" / ".zshrc").read_bytes(),
                         (APP_DIR / "shell" / "zshrc").read_bytes())

    def test_shell_command_bash(self):
        argv, env = shell_command("/usr/bin/bash", self.state)
        self.assertEqual(argv[1:], ["--rcfile", str(APP_DIR / "shell" / "bashrc"), "-i"])
        self.assertEqual(env["STRANGER_PINGS_PYTHON"], sys.executable)

    def test_choose_shell(self):
        self.assertEqual(choose_shell("/bin/zsh"), "/bin/zsh")
        self.assertEqual(choose_shell("/usr/bin/bash"), "/usr/bin/bash")
        self.assertEqual(choose_shell("/usr/bin/fish"),
                         shutil.which("zsh") or shutil.which("bash"))
