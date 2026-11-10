# Stranger Pings: slide text

Paste these into the Google Slides deck. The intro slides (what a computer is,
what the terminal is, what Bash is) stay as they are. These replace the two
"Today's Activity: Ready Player Root" slides and the nine command slides.

Every command slide follows the same pattern: the **story**, **what the
command does**, and **what to type** (shown big). Each popup line under
"Success" is the start of the popup students should see. The bulbs are the
Christmas lights at the start of each student's prompt (`●●●○○○○○○`), one lit
per finished slide.

---

## Title slide

**Stranger Pings**

Presented by the EMU Linux Users Group

---

## Today's Activity: Stranger Pings

**The story:** Will Byers has vanished, and the lights all over Hawkins are
acting strange. Your mission: reach Will, survive the Upside Down, and close
the gate.

**How it works:**

- Each slide teaches one command.
- Type it in the Terminal on your computer, then press Return.
- A popup means you got it! Click OK and wait for the next slide.
- A bulb in your Christmas lights (`○○○○○○○○○`) lights up for every slide
  you finish.
- Stuck? A hint appears in your terminal. Still stuck? Raise your hand.

**Speaker notes:**
- Ask: "Who's seen Stranger Things?" Give a 30-second summary: a boy named
  Will disappears into the Upside Down, a dark copy of his town, and his
  friends and Eleven get him back.
- Point at a student's screen and show them the row of empty bulbs.
- Say clearly: "We won't move on until everyone has their popup."

---

## 1. echo

**Story:** Will is trapped somewhere, and the only way he can hear you is
through the Christmas lights. Send him a message!

**What it does:** `echo` prints whatever you type after it.

**Type this:**

```
echo hello Will
```

(Any message works. Stick to letters and spaces.)

**Tips:**
- Press Return to run a command.
- If you see `quote>` or `>` instead of your lights, press Control-C and try
  again.

**Speaker notes:**
- Say: "Everything you type after `echo` comes right back to you. The
  computer is *echoing* you."
- Success: popup "The lights flicker on and off. Will heard you!" and
  **1 bulb** lit.
- Watch for:
  - `echo` with no message. The hint asks for a message.
  - Typos like `ehco`. The hint spells it out: e-c-h-o.
  - An apostrophe (`echo I'm here`) leaves the terminal waiting at `quote>`
    for the closing quote. Press Control-C and type it without the `'`.

---

## 2. ls

**Story:** Take a look around Hawkins.

**What it does:** `ls` lists the files and folders where you are.

**Type this:**

```
ls
```

**Speaker notes:**
- They'll see `byers_house`, `hawkins_lab`, and `walkie_talkie`. Folders are
  places, and files hold things.
- Success: popup "You look around Hawkins..." and **2 bulbs** lit.
- Watch for:
  - Capital letters (`LS`). Commands are all lowercase.
  - `sl`. The hint spells it out.

---

## 3. cat

**Story:** That walkie-talkie is crackling. Dustin left you a message!

**What it does:** `cat` shows what's inside a file.

**Type this:**

```
cat walkie_talkie
```

**Tips:**
- Names use `_` instead of spaces.
- Type `cat wa` and press Tab to finish the name for you.
- If `cat` ever seems stuck, press Control-C.

**Speaker notes:**
- Don't spoil this: after this slide, the game secretly moves everyone into
  the Upside Down. Their prompt still says `hawkins`.
- Success: popup "The walkie-talkie cuts to static..." and **3 bulbs** lit.
- Watch for:
  - `cat walkie talkie` with a space. The hint says to use `_`.
  - `cat` with nothing after it. This waits forever; press Control-C.
  - `cat byers_house`. That's a folder, not a file.

---

## 4. pwd

**Story:** Everything looks the same... but something feels wrong. Where are
you, really?

**What it does:** `pwd` prints the full path of the folder you're in.

**Type this:**

```
pwd
```

**Speaker notes:**
- They'll see something like `/Users/student/upside_down/hawkins`. Read it
  left to right: each `/` goes one folder deeper. They're in the Upside
  Down's copy of Hawkins! That's the reveal.
- Success: popup "You're in the Upside Down!..." and **4 bulbs** lit.
- Watch for: very little goes wrong here. Capital letters (`PWD`) are the
  main one.

---

## 5. mkdir

**Story:** Build Castle Byers, Will's secret hideout, so you have somewhere
safe.

**What it does:** `mkdir` makes a new folder.

**Type this:**

```
mkdir castle_byers
```

**Tip:** Use `_` instead of spaces.

**Speaker notes:**
- Afterward, `ls` shows `castle_byers` next to everything else.
- Success: popup "Castle Byers is ready. Get inside, fast!" and **5 bulbs**
  lit.
- Watch for:
  - `mkdir castle byers`, which makes *two* folders, `castle` and `byers`.
    The hint says to use `_`.
  - A different name. The hint gives the right one.

---

## 6. cd

**Story:** Hide inside Castle Byers! Then, once it's safe, come back out.

**What it does:** `cd` moves you into a folder. `cd ..` moves you back out
to the folder above.

**Type this:**

```
cd castle_byers
cd ..
```

**Tip:** `..` means "the folder above this one."

**Speaker notes:**
- After the first line, their prompt changes to `castle_byers` and the
  terminal says something is moving outside. The popup comes after `cd ..`.
- Success: popup "That was close. The coast is clear..." and **6 bulbs** lit.
- Watch for:
  - Stopping after the first line.
  - `cd..` with no space. It has to be `cd ..`; the hint asks for the space.

---

## 7. cp

**Story:** Eleven is on her way, and she'll be hungry. Bring her some Eggos!

**What it does:** `cp` copies a file. First comes what to copy, then where
the copy goes.

**Type this:**

```
cp eggos castle_byers
```

**Speaker notes:**
- The original `eggos` stays where it was; `ls castle_byers` shows the copy.
- Success: popup "Eggos delivered!..." and **7 bulbs** lit.
- Watch for:
  - `cp eggos` with no destination.
  - Copying into the wrong folder.

---

## 8. rm

**Story:** The Demogorgon is guarding the gate. Get rid of it!

**What it does:** `rm` deletes a file. Careful: there's no trash can to get
it back from!

**Type this:**

```
rm gate/demogorgon
```

**Tip:** The `/` means *inside*: `gate/demogorgon` is the Demogorgon inside
the gate.

**Speaker notes:**
- Success: popup "The Demogorgon is gone!..." and **8 bulbs** lit.
- Watch for:
  - `rm gate`. The gate is a folder.
  - `rm demogorgon`. It's inside the gate, so it needs `gate/`.

---

## 9. rmdir

**Story:** Close the gate before anything else gets through!

**What it does:** `rmdir` removes a folder, but only if it's empty.

**Type this:**

```
rmdir gate
```

**Tip:** That's why the Demogorgon had to go first: `rmdir` won't remove a
folder with something still inside.

**Speaker notes:**
- Success: popup "The gate is closed. Hawkins is safe!", **all 9 bulbs** lit,
  and a "you used all nine commands" message in the terminal.
- Watch for: `rm -r gate`. The hint says to close it the safe way, with
  `rmdir`.
- Wrap up: ask who can name all nine commands. Then let everyone explore
  freely; the game stays open.

---

## Helper cheat sheet (not a slide)

- **Bulbs lit = slides finished.** Compare with the slide number on screen.
- Inside a student's game, these work as typed:
  - `stranger-pings skip mkdir` jumps that student to the mkdir slide (use
    any command name). Use it if their game got reset.
  - `stranger-pings reset` starts that student over from the first slide.
- If a student closed Terminal, open the game again (see
  `docs/morning-checklist.md`). It picks up where they left off.
