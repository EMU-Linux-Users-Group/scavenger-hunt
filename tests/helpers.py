"""A pretend student for the game-rule tests"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile

from checker import Outcome, Report, check
from progress import Progress
import world

SOLUTION = ("echo hello Will", "ls", "cat walkie_talkie", "pwd", "mkdir castle_byers",
            "cd castle_byers", "cd ..", "cp eggos castle_byers", "rm gate/demogorgon",
            "rmdir gate")


def run_in_bash(line: str, cwd: Path, home: Path) -> Report:
    """Runs `line` in a real bash in `cwd` and reports it the way the shell add-on would"""
    read, write = os.pipe()
    script = f'{line}\n__s=$?\nprintf %s "$PWD" >&{write}\nexit $__s'
    result = subprocess.run(["bash", "--noprofile", "--norc", "-c", script], cwd=cwd,
                            env={**os.environ, "HOME": str(home), "PWD": str(cwd)},
                            pass_fds=(write,), capture_output=True, check=False)
    os.close(write)
    with os.fdopen(read) as pipe:
        after = pipe.read() or str(cwd)
    return Report(line, result.returncode, cwd, Path(after))


class Session:
    """A student with their own temporary home, starting at `step` as if a helper had skipped there"""

    def __init__(self, test_case, step: int = 0):
        tmp = tempfile.TemporaryDirectory()
        test_case.addCleanup(tmp.cleanup)
        self.home = Path(tmp.name)
        self.progress = Progress(step)
        world.prepare(step, self.home)
        self.cwd = world.start_folder(step, self.home)

    def type(self, line: str) -> Outcome:
        """Types `line`, lets the game react, and follows any move it asks for"""
        report = run_in_bash(line, self.cwd, self.home)
        outcome = check(report, self.progress, self.home)
        self.cwd = outcome.move_to or report.after
        return outcome

    def play_to(self, step: int):
        """Types the solution lines until the student reaches `step`"""
        for line in SOLUTION:
            if self.progress.step >= step:
                return
            self.type(line)
