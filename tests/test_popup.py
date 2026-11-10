"""Tests for choosing and showing popups"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from popup import popup_methods

POPUP_SCRIPT = Path(__file__).resolve().parent.parent / "popup.py"


class PopupTests(unittest.TestCase):
    """Popups use what each computer has, and can be switched to tk on a Mac"""

    def test_methods_per_platform_and_style(self):
        self.assertEqual(popup_methods("auto", "darwin"), ["osascript", "tk", "print"])
        self.assertEqual(popup_methods("tk", "darwin"), ["tk", "osascript", "print"])
        self.assertEqual(popup_methods("auto", "linux"), ["tk", "zenity", "print"])
        self.assertEqual(popup_methods("tk", "linux"), ["tk", "zenity", "print"])

    def test_popup_log_records_the_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "popups.log"
            subprocess.run([sys.executable, str(POPUP_SCRIPT), "auto", "hi there"],
                           env={**os.environ, "STRANGER_PINGS_POPUP_LOG": str(log)},
                           check=True, timeout=10)
            self.assertEqual(log.read_text(encoding="utf-8"), "hi there\n")
