"""Plays the game in real bash and zsh shells, typing like a student"""

from __future__ import annotations

from pathlib import Path
import shutil
import tempfile
import unittest

from helpers import SOLUTION
import story
from terminal import GameTerminal


class ShellMixin:
    """The same student session, run in each shell"""

    SHELL: str | None = None

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = Path(tmp.name)
        self.mirror = str(self.home / "upside_down" / "hawkins")

    def open(self, env: dict[str, str] | None = None) -> GameTerminal:
        """Starts the game and waits for its first prompt"""
        terminal = GameTerminal(self.home, self.SHELL, env)
        self.addCleanup(terminal.close)
        self.startup = terminal.until_prompt()
        return terminal

    @staticmethod
    def type(terminal: GameTerminal, line: str) -> str:
        """Types `line` and returns what was printed before the next prompt"""
        terminal.send(line)
        return terminal.until_prompt()

    def test_play_through(self):
        terminal = self.open()
        outputs, lit = [], []
        for line in SOLUTION:
            outputs.append(self.type(terminal, line))
            lit.append(terminal.lit())
        self.assertEqual(lit, [1, 2, 3, 4, 5, 5, 6, 7, 8, 9])
        self.assertEqual(terminal.popups(expect=9), list(story.POPUPS))
        self.assertIn(self.mirror, outputs[3])
        self.assertIn(story.FINAL_MESSAGE.strip().splitlines()[0], outputs[-1])

    def test_typo_hint_appears_before_the_next_prompt(self):
        terminal = self.open()
        self.assertIn(story.hint_text("typo:echo"), self.type(terminal, "ehco hi"))

    def test_empty_return_checks_nothing(self):
        terminal = self.open()
        self.assertIn(story.hint_text("typo:echo"), self.type(terminal, "ehco hi"))
        self.assertNotIn(story.hint_text("typo:echo"), self.type(terminal, ""))

    def test_same_typo_twice_hints_twice(self):
        terminal = self.open({"HISTCONTROL": "ignoredups:ignorespace"})
        for _ in range(2):
            self.assertIn(story.hint_text("typo:echo"), self.type(terminal, "ehco hi"))

    def test_leading_space_is_still_checked(self):
        terminal = self.open({"HISTCONTROL": "ignoredups:ignorespace"})
        self.assertIn(story.hint_text("typo:echo"), self.type(terminal, " ehco hi"))

    def test_resume_after_closing_the_terminal(self):
        terminal = self.open()
        for line in SOLUTION[:4]:
            self.type(terminal, line)
        self.assertEqual(terminal.lit(), 4)
        terminal.send("exit")
        terminal.close()
        terminal = self.open()
        self.assertEqual(terminal.lit(), 4)
        self.assertIn(self.mirror, self.type(terminal, "pwd"))

    def test_skip_inside_the_game_moves_the_shell(self):
        terminal = self.open()
        self.type(terminal, "stranger-pings skip cp")
        self.assertEqual(terminal.lit(), 6)
        self.assertIn(self.mirror, self.type(terminal, "pwd"))

    def test_students_own_startup_files_are_ignored(self):
        for name in (".bashrc", ".zshrc", ".zshenv"):
            (self.home / name).write_text("echo LEAKED\n", encoding="utf-8")
        terminal = self.open()
        self.assertNotIn("LEAKED", self.startup + self.type(terminal, "echo hi"))


class BashTests(ShellMixin, unittest.TestCase):
    """The game in bash (the fallback, and what Linux machines usually have)"""

    SHELL = shutil.which("bash")


@unittest.skipUnless(shutil.which("zsh"), "install zsh to test the Mac's shell")
class ZshTests(ShellMixin, unittest.TestCase):
    """The game in zsh (what the classroom Macs use)"""

    SHELL = shutil.which("zsh")
