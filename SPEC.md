# EMU LUG Digital D___s: Stranger Pings Specification

The full design is in
`docs/superpowers/specs/2026-11-10-stranger-pings-design.md`. In short:

# Basic Functionality
- the presentation and the game are the same thing: each slide teaches one
  command and is one step of a Stranger Things story
- the nine slides, in order: `echo`, `ls`, `cat`, `pwd`, `mkdir`, `cd`, `cp`,
  `rm`, `rmdir`
- students type each command in the real Terminal; the class moves to the
  next slide once everyone has their popup

# Feedback
- a popup appears **only** when a student finishes a slide, so anyone in the
  room can see who's done
- a mistake prints a one-line hint in the terminal, in the story's voice
- exploring (running `ls` again, reading other files) gets no response
- the prompt is a string of Christmas lights: one bulb lit per finished slide

# The Story's Folders
- students start in `~/hawkins`
- after the cat slide they're pulled into its mirror, `~/upside_down/hawkins`,
  which looks the same from the prompt; `pwd` reveals it
- anything a student breaks that a later slide needs is quietly put back

# Commands
- `stranger-pings`: open the game (resumes saved progress)
- `stranger-pings reset`: start over
- `stranger-pings skip COMMAND`: jump to a slide
- `stranger-pings popups auto|tk`: switch to the backup popup
