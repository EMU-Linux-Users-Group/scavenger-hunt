"""Tests for the game rules, using real bash to run what a student types"""

from __future__ import annotations

import sys
import unittest

from checker import Outcome
from helpers import SOLUTION, Session
import story
import world


class HappyPathTests(unittest.TestCase):
    """A student who follows the slides"""

    def test_each_slide_in_order(self):
        s = Session(self)
        popups = [s.type(line).popup for line in SOLUTION]
        self.assertEqual(popups, [story.POPUPS[0], story.POPUPS[1], story.POPUPS[2],
                                  story.POPUPS[3], story.POPUPS[4], None, story.POPUPS[5],
                                  story.POPUPS[6], story.POPUPS[7], story.POPUPS[8]])
        self.assertEqual(s.progress.step, 9)

    def test_cat_pulls_the_student_into_the_upside_down(self):
        s = Session(self, 2)
        self.assertEqual(s.type("cat walkie_talkie").move_to, world.mirror(s.home))
        self.assertTrue((world.gate(s.home) / "demogorgon").is_file())

    def test_inside_the_castle_says_to_come_back_out(self):
        s = Session(self, 5)
        outcome = s.type("cd castle_byers")
        self.assertEqual((outcome.hint, outcome.popup, s.progress.step), ("cd_back_out", None, 5))

    def test_last_slide_finishes_and_then_anything_goes(self):
        s = Session(self, 8)
        self.assertTrue(s.type("rmdir gate").finished)
        self.assertEqual(s.type("ehco hi").hint, None)
        self.assertEqual(s.type("rm -rf *").popup, None)


class MistakeTests(unittest.TestCase):
    """Each mistake gets its own hint, and the step stays put"""

    def assert_hint(self, step: int, line: str, hint: str) -> Session:
        """Types `line` at `step` and checks the hint and that the step didn't change"""
        s = Session(self, step)
        outcome = s.type(line)
        self.assertEqual((outcome.hint, outcome.popup, s.progress.step), (hint, None, step))
        return s

    def test_typo(self):
        self.assert_hint(0, "ehco hello", "typo:echo")

    def test_typo_of_another_command(self):
        self.assert_hint(4, "mdkir castle_byers", "typo:mkdir")

    @unittest.skipIf(sys.platform == "darwin", "macOS finds ECHO because its disk ignores case")
    def test_capital_letters(self):
        self.assert_hint(0, "ECHO hi", "lowercase")

    def test_echo_with_nothing(self):
        self.assert_hint(0, "echo", "echo_empty")

    def test_later_slide(self):
        self.assert_hint(0, "ls", "later")

    def test_cat_a_folder(self):
        self.assert_hint(2, "cat byers_house", "cat_folder")

    def test_cat_with_spaces(self):
        self.assert_hint(2, "cat walkie talkie", "spaces")

    def test_cat_misspelled_file(self):
        self.assert_hint(2, "cat walky_talky", "cat_missing")

    def test_mkdir_with_spaces(self):
        self.assert_hint(4, "mkdir castle byers", "spaces")

    def test_mkdir_other_name(self):
        self.assert_hint(4, "mkdir fort", "mkdir_name")

    def test_cp_without_destination(self):
        self.assert_hint(6, "cp eggos", "cp_destination")

    def test_cp_into_wrong_folder(self):
        self.assert_hint(6, "cp eggos byers_house", "cp_wrong_place")

    def test_rm_the_gate(self):
        self.assert_hint(7, "rm gate", "rm_folder")

    def test_rm_demogorgon_outside_gate(self):
        self.assert_hint(7, "rm demogorgon", "rm_inside_gate")

    def test_rm_r_gate_on_rmdir_slide(self):
        s = self.assert_hint(8, "rm -r gate", "use_rmdir")
        self.assertEqual(list(world.gate(s.home).iterdir()), [])

    def test_rmdir_full_gate(self):
        self.assert_hint(8, "echo boo > gate/note; rmdir gate", "gate_not_empty")


class ExploringTests(unittest.TestCase):
    """Commands that aren't wrong get no hint and don't change the step"""

    def assert_quiet(self, step: int, *lines: str) -> Session:
        """Types each of `lines` at `step` and checks nothing was said"""
        s = Session(self, step)
        for line in lines:
            outcome = s.type(line)
            self.assertEqual((outcome.hint, outcome.popup, s.progress.step), (None, None, step))
        return s

    def test_ls_again_on_cat_slide(self):
        self.assert_quiet(2, "ls")

    def test_cat_a_scenery_file(self):
        self.assert_quiet(2, "cat byers_house/christmas_lights")

    def test_untaught_commands(self):
        s = self.assert_quiet(2, "touch notes", "mv walkie_talkie radio")
        self.assertTrue((world.hawkins(s.home) / "walkie_talkie").is_file())

    def test_earlier_command_failing(self):
        self.assert_quiet(5, "mkdir castle_byers")


class TrickyTests(unittest.TestCase):
    """Clever, sneaky, or accidental things students try"""

    def test_two_steps_on_one_line_show_only_the_last_popup(self):
        s = Session(self, 0)
        self.assertEqual(s.type("echo hi; ls").popup, story.POPUPS[1])
        self.assertEqual(s.progress.step, 2)

    def test_cat_star_counts(self):
        self.assertEqual(Session(self, 2).type("cat *").popup, story.POPUPS[2])

    def test_other_paths_to_the_walkie_talkie_count(self):
        for line in ("cat ./walkie_talkie", "cat ~/hawkins/walkie_talkie", None):
            with self.subTest(line=line):
                s = Session(self, 2)
                line = line or f"cat {world.hawkins(s.home) / 'walkie_talkie'}"
                self.assertEqual(s.type(line).popup, story.POPUPS[2])

    def test_mkdir_p_counts(self):
        self.assertEqual(Session(self, 4).type("mkdir -p castle_byers").popup, story.POPUPS[4])

    def test_cp_with_a_new_name_counts(self):
        self.assertEqual(Session(self, 6).type("cp eggos castle_byers/waffles").popup,
                         story.POPUPS[6])

    def test_rm_rf_star_counts_and_the_world_comes_back(self):
        s = Session(self, 7)
        self.assertEqual(s.type("rm -rf *").popup, story.POPUPS[7])
        self.assertEqual(s.progress.step, 8)
        self.assertTrue((world.mirror(s.home) / "eggos").is_file())
        self.assertEqual(list(world.gate(s.home).iterdir()), [])

    def test_early_rm_is_undone(self):
        s = Session(self, 3)
        self.assertEqual(s.type("rm gate/demogorgon").hint, "later")
        self.assertTrue((world.gate(s.home) / "demogorgon").is_file())

    def test_early_mkdir_is_undone(self):
        s = Session(self, 3)
        self.assertEqual(s.type("mkdir castle_byers").hint, "later")
        self.assertFalse(world.castle(s.home).exists())

    def test_wrong_folder_moves_the_student_back(self):
        s = Session(self, 4)
        s.cwd = world.hawkins(s.home)
        outcome = s.type("mkdir castle_byers")
        self.assertEqual((outcome.hint, outcome.move_to), ("wrong_folder", world.mirror(s.home)))

    def test_cd_somewhere_else_moves_the_student_back(self):
        s = Session(self, 5)
        s.type("cd castle_byers")
        outcome = s.type("cd")
        self.assertEqual((outcome.hint, outcome.move_to), ("cd_lost", world.castle(s.home)))

    def test_deleting_the_folder_you_are_in_moves_you_back_in(self):
        s = Session(self, 1)
        outcome = s.type("rm -r ~/hawkins")
        self.assertTrue((world.hawkins(s.home) / "walkie_talkie").is_file())
        self.assertEqual(outcome.move_to, world.hawkins(s.home))

    def test_odd_input_is_ignored(self):
        for line in ("echo 'unclosed", "echo $(", "\\", "🙂", "x" * 10000):
            with self.subTest(line=line[:20]):
                s = Session(self, 0)
                self.assertEqual(s.type(line), Outcome())
                self.assertEqual(s.progress.step, 0)

    def test_helper_commands_are_not_judged(self):
        s = Session(self, 3)
        outcome = s.type("stranger-pings skip mkdir")
        self.assertEqual((outcome.hint, outcome.move_to),
                         (None, world.start_folder(3, s.home)))
