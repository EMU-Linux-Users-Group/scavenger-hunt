# Stranger Pings: Design

*November 10, 2026. Written with Nate Rupard (EMU Linux Users Group).
Replaces Ready Player Root.*

## Why this exists

Ready Player Root ran as "slides first, scavenger hunt after." It didn't
work. The students were complete beginners, and every slide confused them.
The class barely got through the presentation and never really reached the
hunt. Students don't learn a command by looking at a slide; they learn it by
typing it right away.

In Stranger Pings, **the presentation and the game are the same thing.** Each
slide teaches one command and is one step of a single Stranger Things story.
While that slide is on the projector, every student types the command on
their own Mac. When a student gets it right, a popup appears with the next
bit of the story. The popup also tells the presenters at a glance who is
done and who needs help.

## Who it's for

- High school students with **no terminal experience at all**. The next
  group is high school girls. The last group, high school boys, had very
  little attention span.
- It has to work for **any group of beginners**, including a restless one.
  Every step must make sense from the slide alone.
- A presenter drives the slides while one or two helpers walk around. **The
  class does not move to the next slide until everyone has their popup.**

## Goals

1. Each of the nine command slides is a short puzzle that a beginner can
   finish in about a minute with the slide in front of them.
2. A popup appears only on success, so anyone in the room can see who's done.
3. When a student makes a mistake, a short hint in the story's voice appears
   right in their terminal.
4. Students type in the real Terminal and run the real commands.
5. Setting up the classroom Macs needs no admin password.

## Non-goals

- Syncing with the presenter's slides over the network. Students simply
  follow along, and the class moves together.
- Scores, timers, leaderboards, or competition between students.
- Teaching commands beyond the nine, apart from the two small extras the
  story needs: `cd ..` and a `folder/file` path.
- Windows.
- Protecting a student's account from destructive commands typed outside
  the game (for example, `rm -r ~`).

## Anti-goals (it fails if...)

- **The room loses the thread again**, with someone still lost on slide 3
  while the projector shows slide 6.
- **A puzzle is so clever that it hides the command it's meant to teach.**
  The theme is flavor. It must never get in the way of learning.
- **It's a fake terminal.** Students must learn the real one.
- **It scolds a student for exploring**, for example by complaining when
  they run `ls` again.
- **It needs anything installed on the classroom Macs** beyond the one-line
  download, or needs an admin password.

## Constraints

- **Classroom Macs**, Apple Silicon or Intel, where we have only
  student-level permissions. The game installs like Ready Player Root did:
  one `curl` line unpacks it into `/Users/Shared`, with its own bundled
  Python. Reuse `tools/build_release.py` and the `tools/ready-player-root`
  launcher pattern; the reasoning behind both is in `DEVLOG.md` and the
  v1.0.0 release notes.
- **macOS's default shell is zsh.** It must also work with bash, both as a
  fallback on the Mac and because the developer's Linux machine has bash but
  no zsh yet. Running the zsh tests needs `sudo dnf install zsh` there.
- **Linux works too**, so the game can be developed and tested here.
- Use only Python's standard library, since nothing can be pip-installed on
  student machines.
- The repo's existing conventions still apply: docstrings, `unittest`, and
  conventional commit prefixes. Never commit
  `Digital Dudes Presentation.pptx` or `Links and Brainstorming.docx`.

## How a session runs

**Before class.** The game is already installed on each Mac. A helper logs
in, opens Terminal, and starts Stranger Pings with one command. That leaves a
Terminal window showing:

```
  S T R A N G E R   P I N G S
  Watch the slides at the front of the room.
  Type each command here, then press Return.

○○○○○○○○○ hawkins %
```

Students never start anything themselves.

**The prompt is a string of Christmas lights**, one per step, followed by the
name of the current folder. Each finished step lights a bulb, so a student who
has finished four steps sees:

```
●●●●○○○○○ hawkins %
```

The lit bulbs are colored like Christmas lights, and unlit ones are dim. This
is how helpers check a student once the popup has been closed: they compare
the number of lit bulbs with the slide number. It also covers a fast student
who finished a step before its slide came up. (Nate approved this.)

**Each slide.** The slide gives the story beat, says in one sentence what the
command does, and shows what to type. The student types it. When it's right,
a popup tells the next bit of story. They click OK and wait for the next
slide.

**Mistakes.** A typo, an error, or the wrong file prints a one-line hint in
the terminal, in the story's voice, and no popup appears:

```
○○○○○○○○○ hawkins % ehco hello
zsh: command not found: ehco
  The lights stay dark... check the spelling: e-c-h-o
```

**The ending.** After the last step, a final popup says the gate is closed
and Hawkins is safe. The terminal shows a short "you used all nine commands"
message, and the shell stays open for free play.

## The story and the nine steps

The story was approved as is. The exact commands, the folder layout, and the
popup and hint wording below are my drafts, and the team may edit the text.
All story text is original writing in the spirit of the show, not quotes
from it.

| # | Slide | Story beat | What they type | What counts |
|---|---|---|---|---|
| 1 | echo | Will is trapped and can only hear you through the Christmas lights | `echo` and any message, e.g. `echo hello Will` | `echo` with at least one word after it, exit status 0 |
| 2 | ls | Look around Hawkins | `ls` | any `ls` that succeeds |
| 3 | cat | Dustin left a message on the walkie-talkie | `cat walkie_talkie` | `cat` succeeds on Hawkins' `walkie_talkie` file |
| 4 | pwd | Everything looks the same, but something feels wrong | `pwd` | any `pwd` that succeeds |
| 5 | mkdir | Build Castle Byers, Will's hideout | `mkdir castle_byers` | the folder `castle_byers` now exists in the Upside Down's `hawkins` |
| 6 | cd | Hide inside it, then come out once it's safe | `cd castle_byers`, then `cd ..` | the student went into `castle_byers` and then came back out |
| 7 | cp | Bring Eleven her Eggos | `cp eggos castle_byers` | `castle_byers` holds a copy of `eggos`, and the original is still there |
| 8 | rm | Defeat the Demogorgon | `rm gate/demogorgon` | `gate/demogorgon` is gone, removed with `rm` |
| 9 | rmdir | Close the gate | `rmdir gate` | `gate` is gone, removed with `rmdir` |

**Popup text (drafts):**

1. "The lights flicker on and off. Will heard you!"
2. "You look around Hawkins. That walkie-talkie is crackling. Someone is
   trying to reach you."
3. "The walkie-talkie cuts to static. The lights flicker, and everything goes
   cold. Hawkins looks the same... but something feels wrong."
4. "You're in the Upside Down! Will once hid here in Castle Byers. Build it
   so you have somewhere safe."
5. "Castle Byers is ready. Get inside, fast!"
6. "That was close. The coast is clear, and Eleven is on her way. She'll be
   hungry..."
7. "Eggos delivered! Eleven has her strength back. Now for the Demogorgon."
8. "The Demogorgon is gone! Close the gate before anything else gets
   through."
9. "The gate is closed. Hawkins is safe! You used all nine commands."

**Two story mechanics:**

- **Pulled into the Upside Down (after step 3).** Once `cat walkie_talkie`
  succeeds, the game creates the Upside Down and moves the student's shell
  into it. The Upside Down is a mirror of Hawkins at `~/upside_down/hawkins`,
  so the prompt still says `hawkins %` and nothing looks different. On the pwd
  slide, `pwd` prints `/Users/<name>/upside_down/hawkins`. That's the reveal,
  and it's why `pwd` matters. (My call: the approved plan said the world
  lives in `~/hawkins`; the mirror adds a second folder, `~/upside_down`.)
- **The cd slide has two parts.** First the student goes in
  (`cd castle_byers`). The terminal then prints a story line telling them to
  head back out with `cd ..`. The popup comes when they're back out. This
  keeps the cp, rm, and rmdir steps all in one folder, so students never need
  `../` paths. (My call.)

**The world:**

```
~/hawkins/                      from the start
    byers_house/                scenery, with a file or two to explore
    hawkins_lab/                scenery
    walkie_talkie               Dustin's message (read in step 3)

~/upside_down/hawkins/          appears after step 3
    byers_house/  hawkins_lab/  darker versions of the same places
    walkie_talkie               nothing but static now
    eggos                       copied in step 7
    gate/
        demogorgon              removed in step 8; then gate is removed in step 9
    castle_byers/               made by the student in step 5
```

Every name uses lowercase and underscores, with no spaces. The text inside
each file is a few short lines at most.

## How the game reacts

- **Steps count only in order.** The current step is the first one not done.
- **Popups only ever mean success**: one per step, plus the final one. If one
  command line finishes more than one step (`echo hi; ls`), only the last
  step's popup appears. (My call.)
- **Hints** are one line, in the story's voice, and printed in the terminal
  right before the next prompt. A hint appears when:
  - the command fails or isn't found, and the student was trying the
    current step (for example, the typo `ehco` is close to `echo`);
  - the current step's command was used the wrong way (`echo` with nothing
    after it, `cat byers_house`, `rm gate`, `rmdir gate` while the Demogorgon
    is still inside);
  - a name was typed with spaces instead of underscores
    (`cat walkie talkie`, `mkdir castle byers`);
  - the command belongs to a **later** slide. The command still runs, and the
    hint says "That's for a later slide. Watch the screen!"
- **No hint for exploring.** A command that succeeds and isn't the current
  step's command (running `ls` again, `cat` on a scenery file) gets no
  response.
- **Quiet repair.** When a step becomes current, the game makes the world
  look the way that slide expects. It does the same after a failed attempt
  if the student's own commands broke something. Examples:
  - `walkie_talkie`, `eggos`, `gate`, or the Demogorgon comes back if it
    was deleted early;
  - a `castle_byers` made too early is removed before the mkdir slide;
  - an empty `gate` comes back if `rm -r gate` took the whole thing on the
    rm slide.
  
  Repair only touches the game's own names, never anything else the student
  made.
- **Wrong folder.** If the current step's command is run in the wrong folder
  (for example, `mkdir castle_byers` after wandering off with `cd`), the hint
  says where it needs to happen and the game moves the student back.
  (My call.)

## Helpers' tools

These are typed by helpers, never by students, and work from inside or
outside the game's shell:

- **`stranger-pings`**: starts the game in this Terminal window. If the
  account already has progress, it **resumes**. The world is put back the
  way the current step expects, and the shell opens in the right folder
  (`~/hawkins` for steps 1–3, `~/upside_down/hawkins` after that). So a
  student who closes Terminal by accident loses nothing.
- **`stranger-pings reset`**: wipes the world and the progress, then starts
  fresh. Use it for the next group.
- **`stranger-pings skip <command>`**: jumps a student to that slide, for
  example `stranger-pings skip mkdir`. The world is built as if every
  earlier step had been done. It's only for a student whose game got reset.

Progress is saved per account (as with Ready Player Root:
`~/Library/Application Support/Stranger Pings/` on macOS, and
`~/.local/state/stranger_pings/` on Linux), so students can't affect each
other's games.

## How it's built

The shell add-on with no pseudoterminal was approved. The details below are
my calls.

- **No pseudoterminal.** Reading keystrokes through a pseudoterminal would
  mean rebuilding line editing, Tab completion, and arrow keys. Instead,
  `stranger-pings` starts the student's normal shell with a small add-on
  that runs after every command.
  - zsh is used if it's available; otherwise bash.
  - The add-on is loaded through the game's own startup file (zsh through
    `ZDOTDIR`, bash through `--rcfile`), so the student's own shell setup is
    never edited.
  - It also sets the short prompt and makes `stranger-pings` available as a
    command inside the game.
- **What the add-on does.** After each command, it hands the checker four
  things: the command line exactly as typed, its exit status, the folder
  before it ran, and the folder after.
  - zsh: the command line comes from `preexec` and the status from `precmd`.
  - bash: `PROMPT_COMMAND` gets the line from `history 1`. It must not
    re-check an old command when the student presses Return on an empty
    line, so it compares history numbers.
- **The checker** is Python, run right then (not as a background monitor),
  so hints print in the right place, before the next prompt.
  - It reads the command line the way the shell would: quotes, `;` / `&&` /
    `|`, `~`, and wildcards like `cat *`.
  - Where the step depends on the result, it checks the files on disk.
  - It prints hints, saves progress, does the quiet repair, and starts popups
    in the background so the prompt never waits for one.
  - When the student needs moving (pulled into the Upside Down, sent back to
    the right folder, a `skip`), the add-on runs the `cd` itself, because a
    separate process can't change the shell's folder.
  - It has to start quickly. Aim for well under a quarter of a second per
    command, so avoid heavy imports.
- **Popups** reuse Ready Player Root's approach: `osascript` on macOS, and
  tkinter or else `zenity` on Linux. They run in a separate background
  process.
- **Release**: like Ready Player Root. A tarball bundles Python for both
  kinds of Mac and is installed with `curl … | tar … -C /Users/Shared`, so
  the game lives at `/Users/Shared/stranger-pings/stranger-pings`. A
  double-clickable `Stranger Pings.command` file next to it would also open
  a Terminal window straight into the game. That's optional, and it's the
  builder's call.

## The slide text (a deliverable)

Draft text that the team pastes into the Google Slides deck:

- **Title slide and "Today's Activity" slides**: Stranger Pings, the setup of
  the story (Will is missing; the class has to reach him, get through the
  Upside Down, and close the gate), and how the activity works ("each slide
  is one command; type it on your computer; a popup means you got it; wait
  for the next slide").
- **The nine command slides**, each with:
  - the story beat;
  - one plain sentence on what the command does;
  - exactly what to type, shown big;
  - when needed, one tip (for example, "use `_` instead of spaces" or "a `/`
    means *inside*").
- **Speaker notes for each slide**: what to say, what a correct popup looks
  like, and the one or two mistakes to watch for on that slide.

The intro slides on what a computer, the terminal, and Bash are stay as they
are; the team owns them. Save the drafts in the repo as a Markdown file.

## Testing

Use the real thing wherever possible.

- **Checker tests for each step.** Feed in command lines and exit statuses
  and check the result. Include the tricky and clever things students try:
  - typos: `ehco`, `sl`, `cta`, `mdkir`, `rmdri`;
  - extra spaces, capital letters, and names with spaces;
  - other ways to write a path: `./walkie_talkie`, `~/hawkins/walkie_talkie`,
    full paths, and `cat *`;
  - several commands on one line: `echo hi; ls`, `echo hi && ls`, `ls | cat`;
  - doing things early: `rm gate/demogorgon` on the echo slide, `mkdir
    castle_byers` before the mkdir slide;
  - destructive commands: `rm -r gate`, `rm -rf *`, deleting `eggos` or
    `walkie_talkie`, and `rmdir castle_byers`;
  - doing a step twice: `mkdir castle_byers` again, and `mkdir -p`;
  - cp variants: `cp eggos castle_byers/waffles`, `cp eggos` with no
    destination, and copying into the wrong folder;
  - leaving the world: `cd`, `cd /`, `cd ~`;
  - untaught commands: `mv`, `touch`;
  - shell oddities: an empty Return, Ctrl+C, unbalanced quotes, and a very
    long line.
- **Real-shell tests.** Drive real interactive bash and zsh sessions (the
  tests themselves may use a pseudoterminal to type into them). Check that:
  - the add-on reports every command exactly once;
  - hints show up before the next prompt;
  - the student really gets moved into the Upside Down;
  - an empty Return checks nothing;
  - resume and `skip` land in the right folder.
- **A full play-through** from the first step to the last, plus `reset`.

## Must check on a real Mac before class

**Nobody can test on the classroom Macs before the day of class.** Linux is
available for all testing until then. Nate expects the game to work the same
on both. The core of it should (the shell add-on, the checker, and the
world), but the items below are Mac-only. They have to be checked on the
morning of class, and the backups have to be ready before that:

- **The backup popup is built up front, not just in case.** Popups use
  `osascript` by default. A helper can switch a Mac to the tkinter popup with
  one command (for example, `stranger-pings popups tk`; the name is the
  builder's choice). That window is kept on top, using the Tk that ships with
  the bundled Python.
- **A morning-of-class checklist** is a deliverable: a short, numbered list a
  helper runs on one Mac before students arrive. It covers:
  - installing the game;
  - starting it as a student account;
  - doing the echo step;
  - confirming the popup appears in front;
  - confirming that typing goes back to Terminal;
  - checking that the prompt feels quick;
  - running `reset`;
  - what to do if any of those fail (switch popups, or tell students to
    click back into Terminal).
- **Test the zsh path on Linux too**, with zsh installed
  (`sudo dnf install zsh`), since zsh is what the Macs will use.
- **Test builds** may be posted as GitHub pre-releases (Nate OK'd this).

These are the things that can't be checked from Linux. Ready Player Root never
got to test any of them.

1. The `osascript` popup appears **in front of** Terminal.
2. After clicking OK, typing goes back into Terminal without an extra click.
   If not, the slides need to say "click back into Terminal."
3. The zsh add-on works with the Mac's own zsh and Terminal.app, including
   `/etc/zshrc` and Terminal's session restore.
4. The bundled Python starts fast enough that the prompt doesn't feel slow.
5. A double-clicked `.command` file opens the game without a Gatekeeper
   warning, if that option is built.

If the popups turn out unreliable, the fallback is a tkinter window from the
bundled Python, kept on top. Don't use anything that needs macOS
"Automation" or notification permissions.

## What happens to Ready Player Root

Stranger Pings replaces it in this repo. The old game's code, JSON, and tests
are removed. They stay available in the git history and in the v1.0.0
release. Update `README.md`, `COMMANDS.md`, `SPEC.md`, `TODO.md`, and
`DEVLOG.md` for the new game. Publishing a new release is outward-facing, so
do it only when Nate says so.

## Left to the builder

- The file and module layout, and the names of internal functions.
- How the checker tells the add-on to change folder (a file the add-on reads,
  a separate output channel, or something else).
- Exactly how close a typo has to be to count as "trying the current step."
- The scenery files' names and text, and the walkie-talkie, Eggos, and
  Demogorgon file text, all within the story above.
- The wording of the hints, following the rules above.
- Whether to build the `.command` shortcut.

## My calls, for Nate to check

These are decisions I made that Nate didn't explicitly approve:

1. The Upside Down is a mirror folder, `~/upside_down/hawkins`, so the prompt
   doesn't give it away and `pwd` is the reveal.
2. The cd slide has a second part, `cd ..`, so students never need `../`.
3. The rm slide uses a path, `rm gate/demogorgon`.
4. If one command line finishes two steps, only the last popup shows.
5. A student who runs a step's command in the wrong folder gets moved back
   automatically.
6. Helpers get `reset` and `skip`, and starting the game again resumes saved
   progress.
7. The checker runs right after each command instead of as a long-running
   background monitor; only the popups run in the background. (Nate approved
   the shell add-on with no pseudoterminal when it was played back. This
   item is only about how the checker runs.)
8. `rm -r gate` on the rm slide counts as defeating the Demogorgon, and an
   empty `gate` comes back for the rmdir slide. `cat *` counts on the cat
   slide, because it reads the walkie-talkie.
9. Ready Player Root's files are removed from the repo but stay in git
   history.
