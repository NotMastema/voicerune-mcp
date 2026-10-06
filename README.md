# VoiceRune MCP: Ruune for Claude

This lets Claude read your Ruune recordings: the list, the full transcripts, and the summaries.

You set it up **once per computer**. It takes about 5 minutes. You don't need a GitHub account, and you don't need to type any commands.

> Unofficial. Not made by or affiliated with Ruune / Internet of Humans. It only reads your own recordings, signed in as you.

---

## What you need

- A Windows computer with **Claude Desktop** installed
- **Google Chrome** (or Microsoft Edge)
- Your Ruune login (the Google account you use for Ruune)

---

## Set it up

1. **Download the setup file:** [setup.bat](https://github.com/NotMastema/voicerune-mcp/raw/main/setup.bat)
   (If your browser asks, choose **Keep**.)
2. **Double-click `setup.bat`** in your Downloads folder.
   - If a blue box says **"Windows protected your PC"**, click **More info**, then **Run anyway**.
3. **Follow the black window.** It does everything by itself:
   - installs Python if you don't have it
   - downloads the latest version
   - opens a browser on the Ruune login page: **sign in with Google**, and the browser closes by itself
   - connects it to Claude Desktop
   - asks to restart Claude: press **Enter** for yes
4. ✅ When it says **"All done!"**, open a chat in Claude and ask: **"List my Ruune recordings."** 🎉

---

## Get the newest version

Double-click `setup.bat` again. It updates the files and keeps your sign-in.

---

## Something went wrong?

| What you see | What to do |
|---|---|
| The black window shows **"!!"** and an error | Take a screenshot and ask Claude for help. |
| Claude says **"sign-in expired"** or **"Not signed in"** | Delete the folder `%USERPROFILE%\.voicerune` (paste that into the File Explorer address bar), then double-click `setup.bat` again. |
| The pop-up browser says Google sign-in is **"not secure"** | Close it and double-click `setup.bat` again. If it keeps happening, ask Claude. |
| **ruune** shows "Server disconnected" in Claude → Settings → Developer | Double-click `setup.bat` again, then restart Claude. |

Every computer signs in on its own. Never copy the `%USERPROFILE%\.voicerune` folder from one computer to another.

---

## Extra: a second Ruune account on the same computer

1. Press **Windows key + R**, paste this, and press **Enter**:
   ```
   %USERPROFILE%\voicerune-mcp\setup.bat work
   ```
2. Sign in with the **other** Google account when the browser opens.

It shows up in Claude as **ruune-work**. (Use any one-word nickname instead of `work`.)

---

## For the curious: what it installs

- The app goes in `%USERPROFILE%\voicerune-mcp` (code + its own Python environment)
- Your Ruune sign-in is saved in `%USERPROFILE%\.voicerune`
- One entry named `ruune` is added to Claude Desktop's config (a backup copy is saved next to it as `.json.bak`)
