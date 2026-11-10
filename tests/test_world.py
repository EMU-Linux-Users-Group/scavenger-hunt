"""Tests for building and repairing the student's world"""

from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest

import story
import world


class WorldTests(unittest.TestCase):
    """`prepare` makes the world look the way each slide expects"""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = Path(tmp.name)

    def test_hawkins_only_at_the_start(self):
        world.prepare(0, self.home)
        for path, text in story.FILES.items():
            if path.startswith("hawkins/"):
                self.assertEqual((self.home / path).read_text(encoding="utf-8"), text + "\n")
        self.assertFalse((self.home / "upside_down").exists())

    def test_what_exists_at_each_step(self):
        # step: (castle_byers, castle_byers/eggos, gate/demogorgon, gate)
        expected = {0: None, 1: None, 2: None,
                    3: (False, False, True, True), 4: (False, False, True, True),
                    5: (True, False, True, True), 6: (True, False, True, True),
                    7: (True, True, True, True), 8: (True, True, False, True),
                    9: (True, True, False, False)}
        for step, exists in expected.items():
            with self.subTest(step=step):
                world.wipe(self.home)
                world.prepare(step, self.home)
                if exists is None:
                    self.assertFalse((self.home / "upside_down").exists())
                    continue
                self.assertTrue((world.mirror(self.home) / "eggos").is_file())
                self.assertEqual((world.castle(self.home).is_dir(),
                                  (world.castle(self.home) / "eggos").is_file(),
                                  (world.gate(self.home) / "demogorgon").is_file(),
                                  world.gate(self.home).is_dir()), exists)

    def test_going_back_removes_the_upside_down(self):
        world.prepare(6, self.home)
        world.prepare(1, self.home)
        self.assertFalse((self.home / "upside_down").exists())

    def test_castle_made_too_early_is_removed(self):
        world.prepare(3, self.home)
        world.castle(self.home).mkdir()
        world.prepare(4, self.home)
        self.assertFalse(world.castle(self.home).exists())

    def test_gate_is_emptied_of_the_demogorgon_for_rmdir(self):
        world.prepare(7, self.home)
        world.prepare(8, self.home)
        self.assertEqual(list(world.gate(self.home).iterdir()), [])

    def test_repairs_edited_replaced_symlinked_and_locked_things(self):
        world.prepare(3, self.home)
        (world.hawkins(self.home) / "walkie_talkie").write_text("hi", encoding="utf-8")
        eggos = world.mirror(self.home) / "eggos"
        eggos.unlink()
        eggos.mkdir()
        house = world.hawkins(self.home) / "byers_house"
        os.rename(house, self.home / "moved")
        house.symlink_to(self.home)
        (world.mirror(self.home) / "hawkins_lab").chmod(0o000)
        world.prepare(3, self.home)
        self.assertEqual((world.hawkins(self.home) / "walkie_talkie").read_text(encoding="utf-8"),
                         story.FILES["hawkins/walkie_talkie"] + "\n")
        self.assertTrue(eggos.is_file())
        self.assertTrue(house.is_dir() and not house.is_symlink())
        self.assertTrue((self.home / "moved").is_dir())   # the student's moved folder is untouched
        self.assertTrue((world.mirror(self.home) / "hawkins_lab" / "vines").is_file())

    def test_student_files_are_left_alone(self):
        world.prepare(6, self.home)
        (world.hawkins(self.home) / "notes").write_text("mine", encoding="utf-8")
        (world.castle(self.home) / "drawing").write_text("mine", encoding="utf-8")
        world.prepare(7, self.home)
        self.assertTrue((world.hawkins(self.home) / "notes").exists())
        self.assertTrue((world.castle(self.home) / "drawing").exists())

    def test_start_folder(self):
        self.assertEqual([world.start_folder(step, self.home) for step in (0, 2, 3, 9)],
                         [world.hawkins(self.home), world.hawkins(self.home),
                          world.mirror(self.home), world.mirror(self.home)])

    def test_wipe_removes_only_the_world(self):
        world.prepare(5, self.home)
        (self.home / "homework.txt").write_text("keep", encoding="utf-8")
        world.wipe(self.home)
        world.wipe(self.home)   # nothing left to wipe is fine
        self.assertEqual([p.name for p in self.home.iterdir()], ["homework.txt"])


class StoryTests(unittest.TestCase):
    """The text the team edits stays usable"""

    def test_one_popup_per_command(self):
        self.assertEqual(len(story.POPUPS), len(story.COMMANDS))

    def test_every_hint_renders(self):
        for key in story.HINTS:
            if key != "typo":
                self.assertTrue(story.hint_text(key))
        self.assertIn("e-c-h-o", story.hint_text("typo:echo"))

    def test_final_message_names_every_command(self):
        for command in story.COMMANDS:
            self.assertIn(command, story.FINAL_MESSAGE)
