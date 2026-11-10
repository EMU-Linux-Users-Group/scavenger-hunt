"""Plays the game in real bash and zsh shells, typing like a student"""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import tempfile
import time
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

    def test_echo_with_punctuation_counts(self):
        terminal = self.open()
        self.assertIn("Will!! where are you?", self.type(terminal, "echo Will!! where are you?"))
        self.assertEqual(terminal.lit(), 1)

    @unittest.skipUnless(Path("/proc").is_dir(), "needs /proc to catch the checker running")
    def test_control_c_while_checking_shows_no_traceback(self):
        terminal = self.open()
        for _ in range(3):
            terminal.send("ehco hi")
            self.assertTrue(terminal.interrupt_while_checking())
            self.assertNotIn("Traceback", terminal.until_prompt())
        self.assertIn(story.hint_text("typo:echo"), self.type(terminal, "ehco hi"))

    def test_control_c_still_stops_a_stuck_cat(self):
        terminal = self.open()
        self.type(terminal, "stranger-pings skip cat")
        terminal.send("cat")
        time.sleep(0.5)
        os.write(terminal.master, b"\x03")
        self.assertIn(story.hint_text("cat_no_file"), terminal.until_prompt())
        self.type(terminal, "cat walkie_talkie")
        self.assertEqual(terminal.lit(), 3)

    def test_students_own_startup_files_are_ignored(self):
        for name in (".bashrc", ".zshrc", ".zshenv"):
            (self.home / name).write_text("echo LEAKED\n", encoding="utf-8")
        terminal = self.open()
        self.assertNotIn("LEAKED", self.startup + self.type(terminal, "echo hi"))


class BashTests(ShellMixin, unittest.TestCase):
    """The game in bash (the fallback, and what Linux machines usually have)"""

    SHELL = shutil.which("bash")

    def test_bash_when_asked_even_if_zsh_is_around(self):
        fake_bin = self.home / "fake_bin"
        fake_bin.mkdir()
        (fake_bin / "zsh").write_text("#!/bin/sh\necho FAKE ZSH\n", encoding="utf-8")
        (fake_bin / "zsh").chmod(0o755)
        terminal = self.open({"PATH": f"{fake_bin}{os.pathsep}{os.environ['PATH']}"})
        self.assertIn("bash", self.type(terminal, "echo ${BASH_VERSION:+bash}"))


@unittest.skipUnless(shutil.which("zsh"), "install zsh to test the Mac's shell")
class ZshTests(ShellMixin, unittest.TestCase):
    """The game in zsh (what the classroom Macs use)"""

    SHELL = shutil.which("zsh")
