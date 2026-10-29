"""Shared paths and player actions for the scavenger hunt tests"""

from __future__ import annotations

from pathlib import Path
import shutil

from scavenger_hunt import Folder

REPO_DIR = Path(__file__).resolve().parent.parent
TEST_FOLDER_STRUCTURE = REPO_DIR / "folder_structure.test.json"
TEST_HINT_STRUCTURE = REPO_DIR / "hint_structure.test.json"


def solve_room(room_dir: Path, room: Folder):
    """Deletes the wrong folders and wrong files of `room` like a player would"""
    for folder in room.folders[1:]:
        shutil.rmtree(room_dir / folder.id_)
    for file in room.correct_folder.files[1:]:
        (room_dir / room.correct_folder.id_ / file.id_).unlink()


def settle(game):
    """Polls until the game has seen the same folders twice and returns what it said"""
    return game.poll() or game.poll()


def play_to_the_end(game, root: Folder, game_dir: Path) -> list[str | None]:
    """Solves every room in order and returns each popup message"""
    messages = []
    room, room_dir = root, game_dir
    while not game.finished and len(messages) < 10:
        solve_room(room_dir, room)
        messages.append(settle(game))
        room_dir = room_dir / room.correct_folder.name
        room = room.correct_folder
    return messages
