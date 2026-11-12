# Morning-of-class checklist

Nobody could test on the classroom Macs ahead of time, so run this on **one
Mac** before students arrive. It takes about five minutes. If everything
passes, set up the rest of the Macs the same way (steps 1–2 on each).

## Steps

1. **Install.** Log in to the account you'll use for setup (a helper's or
   the teacher's), open Terminal, and paste:

   ```bash
   curl -fsSL https://github.com/EMU-Linux-Users-Group/scavenger-hunt/releases/latest/download/stranger-pings-macos.tar.gz | tar -xpzf - -C /Users/Shared
   ```

   This only needs doing once per Mac. Every account on the Mac can use it.
   To update to a newer version later, run the same command again **from
   this same account**. The game's folder belongs to it, so from other
   accounts the update fails with a long list of `Permission denied` errors.
   Updating keeps students' saved progress.

2. **Start the game as a student.** Log in to a student account. Either:
   - open Terminal and run `/Users/Shared/stranger-pings/stranger-pings`, or
   - in Finder, open `/Users/Shared/stranger-pings` and double-click
     **Stranger Pings.command**.

   You should see the **S T R A N G E R   P I N G S** title and a prompt
   starting with nine empty bulbs: `○○○○○○○○○ hawkins %`.

3. **Type `echo hi`** and press Return. Check all four:
   - [ ] A popup appears **in front of** Terminal: "The lights flicker on
     and off. Will heard you!"
   - [ ] After clicking OK, you can type in Terminal **without clicking it
     first**.
   - [ ] One bulb is lit: `●○○○○○○○○ hawkins %`.
   - [ ] The prompt came back quickly (well under a second). The very first
     command in each account can take a moment longer while the game gets
     ready; after that, the prompt should come back right away.

4. **Type `ehco hi`.** A yellow hint appears: "The lights stay dark... check
   the spelling: e-c-h-o". No popup.

5. **Type `stranger-pings reset`.** The bulbs go back to empty. The Mac is
   ready for a student.

## If something's wrong

| What happened | What to do |
|---|---|
| No popup, or it hid **behind** Terminal | In **each student account**, run `/Users/Shared/stranger-pings/stranger-pings popups tk`, then repeat step 3. This switches to the backup popup. `popups auto` switches back. |
| After clicking OK, typing doesn't go into Terminal | Tell students: "After the popup, click back into Terminal." Add it to the Today's Activity slide. |
| `Permission denied` while installing or updating | Log in to the account that first installed the game and run the command there. `ls -ld /Users/Shared/stranger-pings` shows which account that is (the third column). |
| The prompt is still slow after the first few commands | Note how slow and carry on; the game still works. |
| A student's prompt has no bulbs | They left the game (closed the window or typed `exit`). Start it again as in step 2; it picks up where they left off. |
| Double-clicking the `.command` file shows a security warning | Use the Terminal command in step 2 instead. |
| "Stranger Pings needs zsh or bash" | Shouldn't happen on a Mac. Tell Nate. |
| Anything else odd | Look in `~/Library/Application Support/Stranger Pings/errors.log` in that student's account. |
