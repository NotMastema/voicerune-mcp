"""Sign in to Ruune once so Claude can read your recordings.

    .venv\\Scripts\\python.exe login.py               # your main Ruune account
    .venv\\Scripts\\python.exe login.py --profile work  # a second account

Opens Chrome (or Edge) in a fresh, private profile at the Ruune login page.
Sign in with Google; this window closes by itself and the session is saved.
"""
import argparse, json, os, shutil, socket, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path

from websockets.sync.client import connect

import server

CANDIDATES = [
    r"%ProgramFiles%\Google\Chrome\Application\chrome.exe",
    r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe",
    r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe",
    r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe",
    r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe",
]


def find_browser() -> str:
    for c in CANDIDATES:
        p = os.path.expandvars(c)
        if os.path.exists(p):
            return p
    sys.exit("Couldn't find Chrome or Edge. Install Google Chrome and try again.")


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="default", help="name for this Ruune account (default: default)")
    args = ap.parse_args()

    port, tmp = free_port(), tempfile.mkdtemp(prefix="ruune-login-")
    proc = subprocess.Popen([find_browser(), f"--remote-debugging-port={port}", f"--user-data-dir={tmp}",
                             "--no-first-run", "--no-default-browser-check", "--new-window",
                             f"{server.WEB}/login"])
    print("\nA browser window opened. Sign in to Ruune with Google there.")
    print("Waiting for you to finish (up to 5 minutes)...\n")

    # Chrome writes its debugging port to DevToolsActivePort once it's ready.
    ws_url, active = None, Path(tmp) / "DevToolsActivePort"
    for _ in range(120):  # up to 60 seconds; first launch of a fresh profile can be slow
        if proc.poll() is not None:
            break
        try:
            if active.exists():
                port = int(active.read_text().split()[0])
            ws_url = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=2))["webSocketDebuggerUrl"]
            break
        except Exception:
            time.sleep(0.5)
    if not ws_url:
        code = proc.poll()
        proc.kill()
        sys.exit(f"The browser didn't start properly (exit code {code}). Close any windows it opened and try again.")

    session = None
    with connect(ws_url, max_size=None) as ws:
        deadline, msg_id = time.time() + 300, 0
        while time.time() < deadline and session is None:
            msg_id += 1
            ws.send(json.dumps({"id": msg_id, "method": "Storage.getCookies"}))
            while True:
                reply = json.loads(ws.recv(timeout=10))
                if reply.get("id") == msg_id:
                    break
            parts = sorted((c for c in reply.get("result", {}).get("cookies", [])
                            if c["name"].startswith(server.COOKIE)), key=lambda c: c["name"])
            if parts:
                try:
                    s = server.cookie_session("".join(c["value"] for c in parts))
                    if s.get("refresh_token"):
                        session = s
                        break
                except Exception:
                    pass  # cookie still being written
            time.sleep(2)
        try:  # close the browser right away so it can't use the token first
            ws.send(json.dumps({"id": msg_id + 1, "method": "Browser.close"}))
        except Exception:
            pass

    try:
        proc.wait(timeout=10)
    except Exception:
        proc.kill()
    shutil.rmtree(tmp, ignore_errors=True)

    if not session:
        sys.exit("Didn't see a sign-in within 5 minutes. Run login.py again.")

    # Trade the browser's token for one that belongs only to Claude.
    path = server.state_path(args.profile)
    saved = server.refresh(session["refresh_token"], path)
    print(f"Signed in as {saved.get('email') or 'your Ruune account'}  (profile: {args.profile})")
    print("All set. Restart Claude Desktop if it's open.")


if __name__ == "__main__":
    main()
