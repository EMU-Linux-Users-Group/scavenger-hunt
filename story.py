"""
Everything Stranger Pings says to students, in one place so the team can edit it.\n
Steps are numbered from 0 in the order of `COMMANDS`: 0 is the echo slide and 8
is the rmdir slide. Step 9 means the student has finished.
"""

from __future__ import annotations

# One slide per command, in the order the slides teach them
COMMANDS = ("echo", "ls", "cat", "pwd", "mkdir", "cd", "cp", "rm", "rmdir")

# The popup for finishing each slide, in the same order as `COMMANDS`
POPUPS = (
    "The lights flicker on and off. Will heard you!",
    "You look around Hawkins. That walkie-talkie is crackling. "
    "Someone is trying to reach you.",
    "The walkie-talkie cuts to static. The lights flicker, and everything goes cold. "
    "Hawkins looks the same... but something feels wrong.",
    "You're in the Upside Down! Will once hid here in Castle Byers. "
    "Build it so you have somewhere safe.",
    "Castle Byers is ready. Get inside, fast!",
    "That was close. The coast is clear, and Eleven is on her way. She'll be hungry...",
    "Eggos delivered! Eleven has her strength back. Now for the Demogorgon.",
    "The Demogorgon is gone! Close the gate before anything else gets through.",
    "The gate is closed. Hawkins is safe! You used all nine commands.",
)

BANNER = """
  S T R A N G E R   P I N G S
  Watch the slides at the front of the room.
  Type each command here, then press Return.
"""

RESUME = "Picking up where you left off: the {command} slide."
DONE_ALREADY = "You already closed the gate! Explore all you like."

FINAL_MESSAGE = """
  * * * * * * * * * * * * * * * * * * * * * * * * * * *
  You closed the gate. Hawkins is safe!
  You used all nine commands: echo, ls, cat, pwd, mkdir, cd, cp, rm, rmdir
  Keep exploring if you like.
  * * * * * * * * * * * * * * * * * * * * * * * * * * *
"""

# The text inside every file in the world, by its path inside the student's home folder
FILES = {
    "hawkins/walkie_talkie":
        "Dustin here. Do you copy? Over.\n"
        "Something weird is happening with the lights all over town.\n"
        "Wait... do you hear that? kkkkhhhhhh...",
    "hawkins/byers_house/christmas_lights":
        "Strings of Christmas lights cover every wall.\n"
        "They blink even when nobody is touching them.",
    "hawkins/byers_house/alphabet_wall":
        "Someone painted the alphabet on the wall,\n"
        "one letter under each light bulb.",
    "hawkins/hawkins_lab/notice":
        "HAWKINS NATIONAL LABORATORY\n"
        "AUTHORIZED PERSONNEL ONLY\n"
        "(Nobody is answering the door.)",
    "upside_down/hawkins/walkie_talkie":
        "kkkkhhhhhh... ssssss... kkkhhh...\n"
        "Nothing but static now.",
    "upside_down/hawkins/byers_house/christmas_lights":
        "The same lights, but dark and wrapped in vines.\n"
        "One bulb flickers, very faintly.",
    "upside_down/hawkins/hawkins_lab/vines":
        "Thick black vines crawl over everything.\n"
        "They seem to move when you look away.",
    "upside_down/hawkins/eggos":
        "A box of frozen waffles.\n"
        "Eleven's favorite food in the whole world.",
    "upside_down/hawkins/gate/demogorgon":
        "A tall creature whose face opens like a flower.\n"
        "It is guarding the gate. Get rid of it!",
}

# One-line hints printed in the terminal. `typo` fills in the spelled-out command,
# and `space` the command that was typed without a space after it.
HINTS = {
    "typo": "The lights stay dark... check the spelling: {letters}",
    "lowercase": "Commands use only small letters. Try it again in lowercase.",
    "later": "That's for a later slide. Watch the screen!",
    "try_again": "Not quite. Look at the slide and try again.",
    "echo_empty": "Will can't hear silence. Type echo, a space, then your message.",
    "echo_letters": "Will can only read letters and spaces. Try just words, like: echo hello Will",
    "space": "Put a space between {command} and the rest, like the slide shows.",
    "spaces": "Names here use _ instead of spaces, like walkie_talkie.",
    "cat_folder": "That's a folder, not a file. cat only reads files.",
    "cat_missing": "There's no file by that name here. Type ls to see what's around.",
    "cat_no_file": "cat needs a file name after it. (If cat ever seems stuck, press Control-C.)",
    "wrong_folder": "You wandered off in the dark! The Upside Down pulls you back. Try again here.",
    "mkdir_name": "Will's fort has a special name: castle_byers",
    "cd_back_out": "You're safe inside Castle Byers. Something is moving outside... "
                   "When it's gone, head back out with: cd ..",
    "cd_lost": "You got lost in the dark! The vines pull you back. Follow the slide.",
    "cp_destination": "cp needs two names: what to copy, then where it goes.",
    "cp_wrong_place": "Eleven is waiting in castle_byers. Copy the eggos there.",
    "rm_folder": "The gate is a folder. The Demogorgon is inside it: rm gate/demogorgon",
    "rm_inside_gate": "The Demogorgon is hiding inside the gate: rm gate/demogorgon",
    "gate_not_empty": "The gate won't close while something is still inside it!",
    "use_rmdir": "That blew the whole gate open! It's back now. Close it the safe way: rmdir gate",
}


def hint_text(key: str) -> str:
    """Returns the hint for `key`; `typo:<command>` spells out that command, and
    `space:<command>` asks for a space after it"""

    if key.startswith("typo:"):
        return HINTS["typo"].format(letters="-".join(key[len("typo:"):]))
    if key.startswith("space:"):
        return HINTS["space"].format(command=key[len("space:"):])
    return HINTS[key]
