"""
Each student's saved progress and the popup setting.\n
Both live in the student's own home folder, because students can't write to an
app folder someone else installed, and so students can't affect each other.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import sys

import story

POPUP_STYLES = ("auto", "tk")


@dataclass
class Progress:
    """Which slide a student is on (0 = echo, 9 = finished)"""

    step: int = 0
    # On the cd slide: whether the student has gone into Castle Byers yet
    entered_castle: bool = False


def state_dir(home: Path, platform: str = sys.platform) -> Path:
    """Returns the folder where the game keeps a student's progress and settings"""

    if platform == "darwin":
        return home / "Library" / "Application Support" / "Stranger Pings"
    return home / ".local" / "state" / "stranger_pings"


def _read_json(path: Path) -> dict:
    """Returns the JSON object in `path`, or `{}` if it is missing or broken"""

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_json(path: Path, data: dict):
    """Saves `data` to `path` all at once, so a crash never leaves half a file"""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(data), encoding="utf-8")
    os.replace(temporary, path)


def load_progress(state: Path) -> Progress:
    """Returns the saved progress, or a fresh start if there is none or it is broken"""

    data = _read_json(state / "progress.json")
    step = data.get("step")
    if type(step) is not int or not 0 <= step <= len(story.COMMANDS):  # pylint: disable=unidiomatic-typecheck
        return Progress()
    return Progress(step, data.get("entered_castle") is True)


def save_progress(state: Path, progress: Progress):
    """Saves `progress`"""

    _write_json(state / "progress.json", asdict(progress))


def clear_progress(state: Path):
    """Forgets the saved progress (the popup setting stays)"""

    (state / "progress.json").unlink(missing_ok=True)


def load_popup_style(state: Path) -> str:
    """Returns which popups this account uses: `auto` or `tk`"""

    style = _read_json(state / "settings.json").get("popups")
    return style if style in POPUP_STYLES else "auto"


def save_popup_style(state: Path, style: str):
    """Saves which popups this account uses, raising `ValueError` for an unknown style"""

    if style not in POPUP_STYLES:
        raise ValueError(f"popup style must be one of {', '.join(POPUP_STYLES)}")
    _write_json(state / "settings.json", {"popups": style})
