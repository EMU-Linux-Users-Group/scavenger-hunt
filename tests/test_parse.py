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
