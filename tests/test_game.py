"""Tests for the game rules the monitor runs on every poll"""

from __future__ import annotations

from pathlib import Path
import shutil
import tempfile
import unittest

from helpers import (TEST_FOLDER_STRUCTURE, TEST_HINT_STRUCTURE, play_to_the_end,
                     settle, solve_room)
from scavenger_hunt import NEXT_ROOM_MESSAGE, TREASURE_MESSAGE, Game, load_hunt


class GameTests(unittest.TestCase):
    """Plays the test hunt in a temporary folder"""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.game_dir = Path(tmp.name) / "hunt"
        self.root = load_hunt(TEST_FOLDER_STRUCTURE, TEST_HINT_STRUCTURE)
        self.game = Game(self.root, self.game_dir)
        self.game.setup()
        self.assertIsNone(settle(self.game))

    def unlock_first_room(self) -> Path:
        """Solves room 1 and returns the renamed correct folder"""
        solve_room(self.game_dir, self.root)
        self.assertEqual(settle(self.game), NEXT_ROOM_MESSAGE)
        return self.game_dir / "Red House"

    def test_setup_creates_only_the_first_room(self):
        self.assertEqual(sorted(path.name for path in self.game_dir.iterdir()),
                         ["78tgdf", "sdfilj", "t78sxc"])
        self.assertEqual(sorted(path.name for path in (self.game_dir / "t78sxc").iterdir()),
                         ["dgfhuj", "higdf8", "vvsg92"])
        self.assertEqual((self.game_dir / "t78sxc" / "dgfhuj").read_text(encoding="utf-8"),
                         "Blue Knife in the Red House\n")

    def test_setup_deletes_an_old_game(self):
        (self.game_dir / "old.txt").write_text("old", encoding="utf-8")
        self.game.setup()
        self.assertFalse((self.game_dir / "old.txt").exists())

    def test_partial_progress_does_nothing(self):
        shutil.rmtree(self.game_dir / "78tgdf")
        self.assertIsNone(settle(self.game))
        self.assertFalse((self.game_dir / "78tgdf").exists())

    def test_empty_wrong_folder_left_behind_blocks_unlocking(self):
        solve_room(self.game_dir, self.root)
        (self.game_dir / "78tgdf").mkdir()
        self.assertIsNone(settle(self.game))

    def test_waits_until_the_folder_stops_changing(self):
        solve_room(self.game_dir, self.root)
        self.assertIsNone(self.game.poll())
        self.assertEqual(self.game.poll(), NEXT_ROOM_MESSAGE)

    def test_unlocking_renames_and_places_the_next_room(self):
        red_house = self.unlock_first_room()
        self.assertFalse((self.game_dir / "t78sxc").exists())
        self.assertEqual((red_house / "Blue Knife").read_text(encoding="utf-8"),
                         "Blue Knife in the Red House\n")
        self.assertEqual(sorted(path.name for path in red_house.iterdir()),
                         ["Blue Knife", "dssfs9", "sdfg92", "sdfop2"])
        self.assertTrue((red_house / "sdfg92" / "sdg924").is_file())

    def test_own_rename_is_not_a_wrong_deletion(self):
        self.unlock_first_room()
        for _ in range(3):
            self.assertIsNone(settle(self.game))

    def test_deleting_the_key_resets_the_room(self):
        shutil.rmtree(self.game_dir / "78tgdf")
        (self.game_dir / "t78sxc" / "dgfhuj").unlink()
        self.assertEqual(settle(self.game), "Red House hint")
        self.assertTrue((self.game_dir / "t78sxc" / "dgfhuj").is_file())
        self.assertTrue((self.game_dir / "78tgdf" / "dsg352").is_file())

    def test_deleting_everything_resets_the_room_once(self):
        for path in list(self.game_dir.iterdir()):
            shutil.rmtree(path)
        self.assertEqual(settle(self.game), "Red House hint")
        self.assertEqual(len(list(self.game_dir.iterdir())), 3)
        self.assertIsNone(settle(self.game))

    def test_deleting_an_unlocked_room_restores_it(self):
        red_house = self.unlock_first_room()
        shutil.rmtree(self.game_dir)
        self.assertEqual(settle(self.game), "Giant Palace hint")
        self.assertTrue((red_house / "Blue Knife").is_file())
        self.assertTrue((red_house / "sdfg92" / "sdg924").is_file())

    def test_deleting_an_unlocked_key_restores_it(self):
        red_house = self.unlock_first_room()
        (red_house / "Blue Knife").unlink()
        self.assertEqual(settle(self.game), "Giant Palace hint")
        self.assertTrue((red_house / "Blue Knife").is_file())

    def test_player_made_files_are_ignored(self):
        (self.game_dir / "notes").mkdir()
        (self.game_dir / "t78sxc" / "copy.txt").write_text("hi", encoding="utf-8")
        self.unlock_first_room()

    def test_player_made_folder_with_the_real_name_is_replaced(self):
        (self.game_dir / "Red House").mkdir()
        (self.game_dir / "Red House" / "junk").write_text("hi", encoding="utf-8")
        red_house = self.unlock_first_room()
        self.assertFalse((red_house / "junk").exists())

    def test_file_where_a_folder_should_be_is_replaced(self):
        shutil.rmtree(self.game_dir / "t78sxc")
        (self.game_dir / "t78sxc").write_text("copied", encoding="utf-8")
        self.assertEqual(settle(self.game), "Red House hint")
        self.assertTrue((self.game_dir / "t78sxc" / "dgfhuj").is_file())

    # Tricky things students might try

    def test_deleting_the_whole_game_folder_resets_the_room(self):
        shutil.rmtree(self.game_dir)
        self.assertEqual(settle(self.game), "Red House hint")
        self.assertTrue((self.game_dir / "t78sxc" / "dgfhuj").is_file())

    def test_file_where_the_game_folder_should_be_is_replaced(self):
        shutil.rmtree(self.game_dir)
        self.game_dir.write_text("echoed", encoding="utf-8")
        self.assertEqual(settle(self.game), "Red House hint")
        self.assertTrue((self.game_dir / "t78sxc" / "dgfhuj").is_file())

    def test_file_where_an_unlocked_room_should_be_is_replaced(self):
        red_house = self.unlock_first_room()
        shutil.rmtree(red_house)
        red_house.write_text("echoed", encoding="utf-8")
        self.assertEqual(settle(self.game), "Giant Palace hint")
        self.assertTrue((red_house / "Blue Knife").is_file())
        self.assertTrue((red_house / "sdfg92" / "sdg924").is_file())

    def test_folder_where_the_key_should_be_is_replaced(self):
        (self.game_dir / "t78sxc" / "dgfhuj").unlink()
        (self.game_dir / "t78sxc" / "dgfhuj").mkdir()
        self.assertEqual(settle(self.game), "Red House hint")
        self.assertTrue((self.game_dir / "t78sxc" / "dgfhuj").is_file())

    def test_player_made_file_with_the_key_name_is_replaced(self):
        (self.game_dir / "t78sxc" / "Blue Knife").write_text("fake", encoding="utf-8")
        red_house = self.unlock_first_room()
        self.assertEqual((red_house / "Blue Knife").read_text(encoding="utf-8"),
                         "Blue Knife in the Red House\n")

    def test_deleting_wrong_items_and_the_key_together_resets_instead_of_unlocking(self):
        solve_room(self.game_dir, self.root)
        (self.game_dir / "t78sxc" / "dgfhuj").unlink()
        self.assertEqual(settle(self.game), "Red House hint")
        self.assertFalse((self.game_dir / "Red House").exists())
        self.assertTrue((self.game_dir / "78tgdf").is_dir())

    def test_setup_replaces_a_file_where_the_game_folder_should_be(self):
        shutil.rmtree(self.game_dir)
        self.game_dir.write_text("echoed", encoding="utf-8")
        Game(self.root, self.game_dir).setup()
        self.assertTrue((self.game_dir / "t78sxc" / "dgfhuj").is_file())

    def test_setup_replaces_a_symlink_where_the_game_folder_should_be(self):
        elsewhere = self.game_dir.parent / "elsewhere"
        elsewhere.mkdir()
        (elsewhere / "homework.txt").write_text("keep me", encoding="utf-8")
        shutil.rmtree(self.game_dir)
        self.game_dir.symlink_to(elsewhere)
        Game(self.root, self.game_dir).setup()
        self.assertFalse(self.game_dir.is_symlink())
        self.assertTrue((self.game_dir / "t78sxc" / "dgfhuj").is_file())
        self.assertTrue((elsewhere / "homework.txt").is_file())

    def test_setup_deletes_an_old_game_with_locked_folders(self):
        (self.game_dir / "78tgdf").chmod(0o000)
        (self.game_dir / "t78sxc").chmod(0o500)
        Game(self.root, self.game_dir).setup()
        self.assertTrue((self.game_dir / "78tgdf" / "dsg352").is_file())
        self.assertTrue((self.game_dir / "t78sxc" / "dgfhuj").is_file())

    def test_symlink_where_the_key_should_be_is_replaced(self):
        key = self.game_dir / "t78sxc" / "dgfhuj"
        key.unlink()
        key.symlink_to("..")
        self.assertEqual(settle(self.game), "Red House hint")
        self.assertTrue(key.is_file())
        self.assertTrue((self.game_dir / "78tgdf" / "dsg352").is_file())

    def test_broken_symlink_where_a_folder_should_be_is_replaced(self):
        shutil.rmtree(self.game_dir / "t78sxc")
        (self.game_dir / "t78sxc").symlink_to("nowhere")
        self.assertEqual(settle(self.game), "Red House hint")
        self.assertTrue((self.game_dir / "t78sxc" / "dgfhuj").is_file())

    def test_locked_folder_is_still_reset(self):
        (self.game_dir / "t78sxc" / "dgfhuj").unlink()
        (self.game_dir / "t78sxc").chmod(0o500)
        self.assertEqual(settle(self.game), "Red House hint")
        self.assertTrue((self.game_dir / "t78sxc" / "dgfhuj").is_file())

    def test_locked_correct_folder_still_unlocks(self):
        solve_room(self.game_dir, self.root)
        (self.game_dir / "t78sxc").chmod(0o500)
        self.game_dir.chmod(0o500)
        self.assertEqual(settle(self.game), NEXT_ROOM_MESSAGE)
        self.assertTrue((self.game_dir / "Red House" / "Blue Knife").is_file())
        self.assertFalse((self.game_dir / "t78sxc").exists())

    def test_creation_order_does_not_reveal_the_correct_items(self):
        first_folders, first_files = set(), set()
        for _ in range(30):
            Game(self.root, self.game_dir).setup()
            folders = list(self.game_dir.iterdir())
            first_folders.add(min(folders, key=lambda path: path.stat().st_ino).name)
            files = list((self.game_dir / "t78sxc").iterdir())
            first_files.add(min(files, key=lambda path: path.stat().st_ino).name)
        self.assertGreater(len(first_folders), 1)
        self.assertGreater(len(first_files), 1)

    def test_winning_places_the_treasure(self):
        messages = play_to_the_end(self.game, self.root, self.game_dir)
        self.assertEqual(messages, [NEXT_ROOM_MESSAGE, NEXT_ROOM_MESSAGE, TREASURE_MESSAGE])
        congress = self.game_dir / "Red House" / "Giant Palace" / "Congress Building"
        self.assertEqual((congress / "Golden Deagle").read_text(encoding="utf-8"),
                         "You found the Golden Deagle!\n")
        self.assertTrue((congress / "Judge Gavel").is_file())
        self.assertTrue(self.game.finished)
        self.assertIsNone(settle(self.game))
