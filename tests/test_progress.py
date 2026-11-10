"""Tests for saving each student's progress and the popup setting"""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from progress import (Progress, clear_progress, load_popup_style, load_progress,
                      save_popup_style, save_progress, state_dir)


class ProgressTests(unittest.TestCase):
    """Progress lives in each student's own home folder"""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.state = Path(tmp.name) / "state"

    def test_state_dir_per_platform(self):
        home = Path("/home/student")
        self.assertEqual(state_dir(home, "darwin"),
                         home / "Library" / "Application Support" / "Stranger Pings")
        self.assertEqual(state_dir(home, "linux"), home / ".local" / "state" / "stranger_pings")

    def test_missing_or_corrupt_progress_starts_fresh(self):
        self.assertEqual(load_progress(self.state), Progress())
        self.state.mkdir()
        for text in ("{not json", "[1, 2]", '{"step": 42}', '{"step": "3"}', '{"step": true}'):
            with self.subTest(text=text):
                (self.state / "progress.json").write_text(text, encoding="utf-8")
                self.assertEqual(load_progress(self.state), Progress())

    def test_progress_round_trip(self):
        save_progress(self.state, Progress(5, True))
        self.assertEqual(load_progress(self.state), Progress(5, True))
        save_progress(self.state, Progress(6))
        self.assertEqual(load_progress(self.state), Progress(6, False))

    def test_popup_style_defaults_to_auto_and_survives_clear_progress(self):
        self.assertEqual(load_popup_style(self.state), "auto")
        save_popup_style(self.state, "tk")
        save_progress(self.state, Progress(4))
        clear_progress(self.state)
        clear_progress(self.state)   # clearing twice is fine
        self.assertEqual(load_progress(self.state), Progress())
        self.assertEqual(load_popup_style(self.state), "tk")

    def test_bad_popup_style_is_rejected(self):
        with self.assertRaises(ValueError):
            save_popup_style(self.state, "banana")
