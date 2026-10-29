"""Tests for starting and stopping the background monitor"""

from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest

from helpers import TEST_FOLDER_STRUCTURE, TEST_HINT_STRUCTURE
from scavenger_hunt import Game, load_hunt, monitor_pid, start_monitor, stop_monitor


class MonitorProcessTests(unittest.TestCase):
    """Runs the real monitor.pyw against a temporary game"""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.pid_file = self.tmp / ".monitor.pid"
        self.addCleanup(stop_monitor, self.pid_file)

    def test_stop_when_nothing_is_running(self):
        self.assertFalse(stop_monitor(self.pid_file))

    def test_stop_never_kills_a_process_that_is_not_the_monitor(self):
        self.pid_file.write_text(str(os.getpid()), encoding="utf-8")
        self.assertIsNone(monitor_pid(self.pid_file))
        self.assertFalse(stop_monitor(self.pid_file))
        self.assertFalse(self.pid_file.exists())

    def test_start_then_stop(self):
        game_dir = self.tmp / "hunt"
        Game(load_hunt(TEST_FOLDER_STRUCTURE, TEST_HINT_STRUCTURE), game_dir).setup()
        pid = start_monitor(game_dir, TEST_FOLDER_STRUCTURE, TEST_HINT_STRUCTURE, self.pid_file)
        self.assertEqual(monitor_pid(self.pid_file), pid)
        self.assertTrue(stop_monitor(self.pid_file))
        self.assertIsNone(monitor_pid(self.pid_file))
