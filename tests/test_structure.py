"""Tests for reading, parsing, and validating hunt structures"""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from helpers import REPO_DIR, TEST_FOLDER_STRUCTURE, TEST_HINT_STRUCTURE
from scavenger_hunt import (File, Folder, parse_folder_structure,
                            read_folder_structure, validate_structure)


class ParseTests(unittest.TestCase):
    """Turning folder_structure + hint_structure JSON into `Folder`s"""

    def setUp(self):
        self.root = parse_folder_structure(read_folder_structure(TEST_FOLDER_STRUCTURE),
                                           read_folder_structure(TEST_HINT_STRUCTURE))

    def test_names_map_to_ids(self):
        red_house = self.root.correct_folder
        self.assertEqual((red_house.name, red_house.id_), ("Red House", "t78sxc"))
        self.assertEqual([folder.name for folder in self.root.folders],
                         ["Red House", "Silver Car", "Orange Building"])
        self.assertEqual([file.id_ for file in red_house.files], ["dgfhuj", "higdf8", "vvsg92"])

    def test_files_get_text_from_hint_structure(self):
        self.assertEqual(self.root.correct_folder.correct_file.contents,
                         "Blue Knife in the Red House")

    def test_only_correct_folders_get_hints(self):
        self.assertEqual(self.root.correct_folder.hint, "Red House hint")
        self.assertIsNone(self.root.folders[1].hint)

    def test_treasure_is_in_the_last_correct_folder(self):
        congress = self.root.correct_folder.correct_folder.correct_folder
        self.assertEqual(congress.name, "Congress Building")
        self.assertEqual(congress.folders, ())
        self.assertEqual(congress.treasure.name, "Golden Deagle")
        self.assertEqual(congress.treasure.contents, "You found the Golden Deagle!")

    def test_example_structure_parses_without_hints(self):
        root = parse_folder_structure(
            read_folder_structure(REPO_DIR / "folder_structure.example.json"))
        last = root.correct_folder.correct_folder.correct_folder
        self.assertEqual(len(root.folders), 3)
        self.assertEqual(len(last.files), 3)
        self.assertEqual(last.treasure.name, "treasure")


class ValidateTests(unittest.TestCase):
    """Catching mistakes in hand-written hunt JSON"""

    def setUp(self):
        self.folders = read_folder_structure(TEST_FOLDER_STRUCTURE)
        self.hints = read_folder_structure(TEST_HINT_STRUCTURE)

    def assert_invalid(self, message: str):
        """Asserts that validating the edited structures fails with `message`"""
        with self.assertRaisesRegex(ValueError, message):
            validate_structure(parse_folder_structure(self.folders, self.hints))

    def test_test_hunt_is_valid(self):
        validate_structure(parse_folder_structure(self.folders, self.hints))

    def test_rejects_file_without_text(self):
        del self.hints["t78sxc"]["higdf8"]
        self.assert_invalid("higdf8")

    def test_rejects_room_without_three_folders(self):
        del self.folders["Orange Building"]
        del self.folders["sdfilj"]
        self.assert_invalid("3 folders")

    def test_rejects_folder_without_three_files(self):
        del self.folders["78tgdf"]["Worn Sock"]
        self.assert_invalid("Silver Car")

    def test_rejects_duplicate_ids_in_a_folder(self):
        self.folders["78tgdf"]["Silver Sword"] = "dsg352"
        self.assert_invalid("twice")

    def test_rejects_missing_treasure(self):
        del self.folders["t78sxc"]["sdfg92"]["fgb939"]["Treasure"]
        self.assert_invalid("treasure")

    def test_rejects_missing_room_hint(self):
        del self.hints["t78sxc"]["hint"]
        self.assert_invalid("hint")

    def test_rejects_file_text_that_is_not_a_string(self):
        self.hints["t78sxc"]["sdfg92"]["fgb939"]["fgdj39"] = 42
        self.assert_invalid("fgdj39")

    def test_rejects_folder_hints_that_are_not_an_object(self):
        self.hints["t78sxc"]["sdfg92"] = "oops"
        self.assert_invalid("sdfg92")

    def test_rejects_room_hint_that_is_not_a_string(self):
        self.hints["t78sxc"]["hint"] = ["Red House hint"]
        self.assert_invalid("hint")

    def test_rejects_slash_in_a_revealed_name(self):
        self.folders = {("Red/House" if key == "Red House" else key): value
                        for key, value in self.folders.items()}
        self.assert_invalid("Red/House")


class CreateTests(unittest.TestCase):
    """Writing one folder and its files to disk"""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "t78sxc"
        self.folder = Folder("Red House", "t78sxc", (File("Blue Knife", "dgfhuj", "knife"),
                                                     File("Gold Heart", "higdf8", "heart")))

    def test_files_are_named_by_id(self):
        self.folder.create(self.path)
        self.assertEqual((self.path / "dgfhuj").read_text(encoding="utf-8"), "knife\n")

    def test_create_again_only_adds_missing_files(self):
        self.folder.create(self.path)
        (self.path / "dgfhuj").write_text("edited", encoding="utf-8")
        (self.path / "higdf8").unlink()
        self.folder.create(self.path)
        self.assertEqual((self.path / "dgfhuj").read_text(encoding="utf-8"), "edited")
        self.assertEqual((self.path / "higdf8").read_text(encoding="utf-8"), "heart\n")
