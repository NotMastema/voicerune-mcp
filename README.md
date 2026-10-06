# Ruune for Claude

This lets Claude read your Ruune recordings: the list, the full transcripts, and the summaries.

You set it up **once per computer**. It takes about 15 minutes.

---

## Before you start: things you need

- [ ] A Windows computer with **Claude Desktop** installed
- [ ] **Google Chrome** (or Microsoft Edge)
- [ ] Your Ruune login (the Google account you use for Ruune)

---

## Step 1: Install the 3 helper programs

Skip any you already have.

1. **Python**: go to https://www.python.org/downloads/ and click the big yellow button. When the installer opens, check the box **"Add python.exe to PATH"**, then click **Install Now**.
2. **Git**: go to https://git-scm.com/download/win, download it, and click **Next** on every screen.
3. **GitHub CLI**: go to https://cli.github.com, download it, and click **Next** on every screen.

Then **close and reopen PowerShell** so it notices the new programs.

> To open PowerShell, press the **Windows key**, type `powershell`, and press **Enter**.

---

## Step 2: Sign in to GitHub

In PowerShell, type:

```powershell
gh auth login
```

Pick these answers: **GitHub.com** → **HTTPS** → **Yes** → **Login with a web browser**. It shows a code. Press Enter, paste the code in the browser, and approve.

---

## Step 3: Download this project

Copy and paste this whole box into PowerShell and press **Enter**:

```powershell
cd C:\
gh repo clone ruune-mcp
cd C:\ruune-mcp
py -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

Wait until it stops scrolling. ✅ The last line should say **"Successfully installed ..."**.

---

## Step 4: Sign in to Ruune

In the same PowerShell window, type:

```powershell
.\.venv\Scripts\python.exe login.py
```

1. A browser window pops up on the Ruune login page.
2. **Sign in with Google** (use the Ruune account you want Claude to see).
3. The window closes by itself. ✅ PowerShell says **"Signed in as ... All set."**

> Every computer signs in on its own. Never copy the files in `%LOCALAPPDATA%\ruune-mcp` from one computer to another.

---

## Step 5: Tell Claude Desktop about it

1. Open **Claude Desktop** → **Settings** → **Developer** → **Edit Config**. A file opens (or a folder; double-click `claude_desktop_config.json`).
2. Find the line that says `"mcpServers": {`.
3. Paste this **right after** that line:

```json
    "ruune": {
      "command": "C:\\ruune-mcp\\.venv\\Scripts\\python.exe",
      "args": ["C:\\ruune-mcp\\server.py"]
    },
```

4. Save the file (Ctrl + S).

> If `"mcpServers": {` is followed right away by `}` (nothing else in there), delete the comma at the very end of what you pasted.
> If the file has no `"mcpServers"` at all, make the whole file look like this:
> ```json
> {
>   "mcpServers": {
>     "ruune": { ...the block above, without the last comma... }
>   }
> }
> ```

---

## Step 6: Restart Claude and check

1. **Fully quit** Claude Desktop: right-click the Claude icon by the clock (bottom-right) → **Quit**. Then open it again.
2. Go to **Settings** → **Developer**. ✅ You should see **ruune** with a green **running**.
3. Start a chat and ask: **"List my Ruune recordings."** 🎉

---

## Something went wrong?

| What you see | What to do |
|---|---|
| **"Server disconnected"** in Settings → Developer | Open PowerShell and run `cd C:\ruune-mcp` then `.\.venv\Scripts\python.exe server.py`. If an error shows, send it to Claude. If nothing happens, that part works (press Ctrl + C); check the config file for a typo or missing comma. |
| Claude says **"sign-in expired"** or **"Not signed in"** | Do **Step 4** again, then restart Claude (Step 6). |
| The pop-up browser says Google sign-in is **"not secure"** | Close it, run `login.py` again, and try once more. If it keeps happening, tell Claude. |
| `py` is not recognized | Python isn't installed right. Redo Step 1, and make sure you check **"Add python.exe to PATH"**. |
| `gh` or `git` is not recognized | Close and reopen PowerShell. If it still fails, reinstall from Step 1. |

---

## Extra: two Ruune accounts on one computer

1. Sign in the second account with a nickname, like `work`:

```powershell
cd C:\ruune-mcp
.\.venv\Scripts\python.exe login.py --profile work
```

2. Add a second block in Step 5 with a different name and that nickname:

```json
    "ruune-work": {
      "command": "C:\\ruune-mcp\\.venv\\Scripts\\python.exe",
      "args": ["C:\\ruune-mcp\\server.py"],
      "env": { "RUUNE_PROFILE": "work" }
    },
```

## Getting updates on a computer that already has this

```powershell
cd C:\ruune-mcp
git pull
.\.venv\Scripts\pip install -r requirements.txt
```

Then restart Claude Desktop.
