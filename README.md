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

## Ways to use it

### 1. Just ask (on the computer)

Open a chat in Claude Desktop and ask things like:

- "List my Ruune recordings from this week."
- "Summarize my call from this morning and list the action items."
- "Search my recordings for anything about pricing."
- "Give me the full transcript of the pipeline sync, with timestamps."

### 2. From your phone or iPad (your computer does the work)

The recordings are fetched **by your computer**. Your phone or iPad is just where you ask.

1. On the computer, start a **Cowork** task in Claude Desktop with **this computer selected**. If a task isn't linked yet, open it in Claude Desktop and choose **"Link to this computer"**.
2. Later, open that same task in the Claude app on your phone or iPad and ask away.

✅ This works as long as the computer is **on, awake, online, and Claude Desktop is open**. (See "Keep your computer ready" below.)

### 3. Automatic daily or weekly summaries (scheduled tasks)

Cowork can run a task for you on a schedule. In a Cowork task that's **linked to your computer**, paste something like this and change the time and details:

> Create a scheduled task that runs every weekday at 6:00 PM my time and needs this computer. It should use the ruune tools to find every Ruune recording from today, read each transcript, and send me one short digest: for each recording, the title, 3–5 bullet points, any action items with who owns them, and any dates or numbers mentioned. If there were no recordings today, just say so.

Other ideas you can schedule the same way:

| Schedule | What to ask for |
|---|---|
| Every weekday evening | Daily digest of today's recordings (the example above) |
| Friday afternoon | Weekly recap: themes across all the week's recordings, open action items, people mentioned |
| Every morning | "Anything from yesterday's recordings I promised to do today?" |
| After sales calls | Draft a follow-up email for each customer call (saved as a draft, not sent) |
| Weekly | Save each new transcript as a text file in a folder on your computer, as a personal backup |

Good to know:

- The computer must be ready when the schedule fires (next section). If it's asleep, that run can't reach your recordings.
- A scheduled run happens with nobody watching. If it stops to ask for approval, open the task's settings and turn on **"Automatically approve"** (if your account allows it).
- To change or stop it, just ask Claude: "Show my scheduled tasks" or "Pause the Ruune digest."

### Keep your computer ready

For options 2 and 3, the computer has to be on and reachable:

1. **Don't let it sleep when plugged in:** **Settings** → **System** → **Power & battery** (or **Power**) → **Screen and sleep** → set **"When plugged in, put my device to sleep after"** to **Never**. Turning the *screen* off is fine.
2. **Laptop lid:** press **Windows key**, type `lid`, open **"Change what closing the lid does"**, and set **When plugged in** to **Do nothing**. Now you can close the lid while it's plugged in.
3. **Open Claude Desktop automatically:** press **Windows key + R**, type `shell:startup`, press **Enter**, then drag a **Claude** shortcut from the Start menu into that folder. Claude now opens every time you sign in to Windows.
4. **Watch out for restarts:** Windows Update can restart the computer overnight. With step 3 done, Claude comes back by itself after you sign in.

### Without your computer at all?

Not possible with this version. It runs on your computer. Making it work when the computer is off would mean hosting it online (for example on Cloudflare) and adding it to Claude as a custom connector. That's a future upgrade.

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
