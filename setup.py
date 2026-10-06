"""Sets everything up after setup.bat has downloaded the files:
Python environment -> Ruune sign-in -> Claude Desktop config -> restart Claude.

    setup.py            # your main Ruune account
    setup.py work       # a second Ruune account, shown in Claude as "ruune-work"
"""
import json, os, shutil, subprocess, sys, time
from pathlib import Path

APP = Path(__file__).resolve().parent
VENV_PY = APP / ".venv" / "Scripts" / "python.exe"
DATA = Path(os.environ["LOCALAPPDATA"]) / "ruune-mcp"


def step(n, text):
    print(f"\n[{n}/4] {text}")


def run(cmd):
    r = subprocess.run(cmd)
    if r.returncode != 0:
        fail(f"This step failed: {' '.join(map(str, cmd))}")


def fail(msg):
    print(f"\n!! {msg}\n   Take a screenshot of this window and ask Claude for help.")
    input("\nPress Enter to close...")
    sys.exit(1)


def session_exists(profile):
    if profile == "default":
        return (DATA / "session.json").exists() or (DATA / "session-default.json").exists()
    return (DATA / f"session-{profile}.json").exists()


def config_path():
    std = Path(os.environ["APPDATA"]) / "Claude" / "claude_desktop_config.json"
    if std.exists() or std.parent.exists():
        return std
    pkgs = Path(os.environ["LOCALAPPDATA"]) / "Packages"
    for p in pkgs.glob("Claude_*"):
        alt = p / "LocalCache" / "Roaming" / "Claude"
        if alt.exists():
            return alt / "claude_desktop_config.json"
    return std


def update_config(profile):
    path = config_path()
    cfg = {}
    if path.exists():
        try:
            cfg = json.loads(path.read_text(encoding="utf-8") or "{}")
        except json.JSONDecodeError:
            fail(f"Your Claude config file has a typo, so I didn't touch it:\n   {path}")
        shutil.copy2(path, path.with_suffix(".json.bak"))
    name = "ruune" if profile == "default" else f"ruune-{profile}"
    entry = cfg.setdefault("mcpServers", {}).get(name, {})
    entry["command"] = str(VENV_PY)
    entry["args"] = [str(APP / "server.py")]
    if profile != "default":
        entry.setdefault("env", {})["RUUNE_PROFILE"] = profile
    cfg["mcpServers"][name] = entry
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    print(f"    Added \"{name}\" to {path}")


def restart_claude():
    subprocess.run(["taskkill", "/IM", "claude.exe", "/F"], capture_output=True)
    time.sleep(3)
    app_id = subprocess.run(
        ["powershell", "-NoProfile", "-Command", "(Get-StartApps | ? Name -eq 'Claude' | select -First 1).AppID"],
        capture_output=True, text=True).stdout.strip()
    if app_id:
        subprocess.Popen(["explorer.exe", f"shell:AppsFolder\\{app_id}"])
        return True
    return False


def main():
    profile = (sys.argv[1] if len(sys.argv) > 1 else "default").strip().lower() or "default"

    step(1, "Installing the pieces it needs (about a minute)...")
    if not VENV_PY.exists():
        run([sys.executable, "-m", "venv", str(APP / ".venv")])
    run([str(VENV_PY), "-m", "pip", "install", "-q", "--disable-pip-version-check", "-r", str(APP / "requirements.txt")])

    step(2, "Signing in to Ruune...")
    if session_exists(profile):
        print("    Already signed in. Skipping.")
    else:
        print("    A browser window will open. Sign in with Google; it closes by itself.")
        run([str(VENV_PY), str(APP / "login.py"), "--profile", profile])

    step(3, "Connecting it to Claude Desktop...")
    update_config(profile)

    step(4, "Restarting Claude Desktop...")
    ans = input("    Claude Desktop needs a restart. Restart it now? (Y/n) ").strip().lower()
    if ans in ("", "y", "yes"):
        if not restart_claude():
            print("    Couldn't reopen it automatically. Open Claude Desktop yourself.")
    else:
        print("    OK. Quit Claude from the tray icon (bottom-right, by the clock) and reopen it later.")

    print("\nAll done! In Claude, ask: \"List my Ruune recordings.\"")
    input("\nPress Enter to close...")


if __name__ == "__main__":
    main()
