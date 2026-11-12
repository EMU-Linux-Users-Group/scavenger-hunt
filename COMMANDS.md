`stranger-pings [COMMAND]` (from the repo: `python3 stranger_pings.py [COMMAND]`)

# (no command) or start
- builds the student's world in `~/hawkins` and opens the game in this
  Terminal window
- if the student already made progress, picks up where they left off
- inside the game, it just says the game is already running
- `exit` closes the game; Control-D is ignored, so students can't close it by
  accident

# reset
- deletes `~/hawkins` and `~/upside_down` and the student's progress, then
  starts over from the first slide

# skip COMMAND
- jumps to the slide for COMMAND (`echo`, `ls`, `cat`, `pwd`, `mkdir`, `cd`,
  `cp`, `rm`, or `rmdir`), building the world as if every earlier slide was
  done
- use it for a student whose game got reset

# popups auto | tk
- `tk` switches this account to the backup popup window, in case the normal
  macOS popups misbehave; `auto` switches back
- this setting survives `reset`

# check, status
- used by the game's shell add-on after every command; not for people
