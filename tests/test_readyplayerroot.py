"""Checks that the real Ready Player Root hunt loads, follows the rules, and can be won"""

from __future__ import annotations

from pathlib import Path
import re
import tempfile
import unittest

from helpers import play_to_the_end, settle
from scavenger_hunt import (FOLDER_STRUCTURE_FILE, HINT_STRUCTURE_FILE, NEXT_ROOM_MESSAGE,
                            TREASURE_MESSAGE, Game, load_hunt)


def _every_folder(folder):
    """Yields `folder` and every folder inside it"""
    yield folder
    for child in folder.folders:
        yield from _every_folder(child)


class ReadyPlayerRootTests(unittest.TestCase):
    """The hunt the students will actually play"""

    def setUp(self):
        self.root = load_hunt(FOLDER_STRUCTURE_FILE, HINT_STRUCTURE_FILE)

    def test_rooms_keys_and_treasure(self):
        race = self.root.correct_folder
        hotel = race.correct_folder
        castle = hotel.correct_folder
        self.assertEqual([room.name for room in (race, hotel, castle)],
                         ["Unbeatable Race", "Overlook Hotel", "Castle Anorak"])
        self.assertEqual([room.correct_file.name for room in (race, hotel, castle)],
                         ["Copper Key", "Jade Key", "Crystal Key"])
        self.assertEqual(castle.treasure.name, "Golden Easter Egg")

    def test_only_key_files_mention_a_key(self):
        keys = set()
        room = self.root
        while room.folders:
            keys.add(room.correct_folder.correct_file.id_)
            room = room.correct_folder
        for folder in _every_folder(self.root):
            for file in folder.files:
                mentions_key = re.search(r"\bkeys?\b", file.contents, re.IGNORECASE)
                self.assertEqual(bool(mentions_key), file.id_ in keys, file.name)

    def test_no_text_gives_away_an_id(self):
        folders = list(_every_folder(self.root))
        ids = {item.id_ for folder in folders for item in folder.files + folder.folders}
        for folder in folders:
            for text in [file.contents for file in folder.files] + [folder.hint or ""]:
                for id_ in ids:
                    self.assertNotIn(id_, text)

    def test_hunt_can_be_won(self):
        with tempfile.TemporaryDirectory() as tmp:
            game_dir = Path(tmp) / "hunt"
            game = Game(self.root, game_dir)
            game.setup()
            settle(game)
            self.assertEqual(play_to_the_end(game, self.root, game_dir),
                             [NEXT_ROOM_MESSAGE, NEXT_ROOM_MESSAGE, TREASURE_MESSAGE])
            self.assertTrue((game_dir / "Unbeatable Race" / "Overlook Hotel" / "Castle Anorak"
                             / "Golden Easter Egg").is_file())
