"""Ruune MCP server: read your Ruune recordings, transcripts and summaries from Claude.

Talks to Ruune's Supabase backend as you. Sign in once with `login.py`; the session is
saved under %LOCALAPPDATA%\\ruune-mcp\\ and renewed automatically.

Optional env (in claude_desktop_config.json):
  RUUNE_PROFILE         name for a separate Ruune account, e.g. "work" (default: "default")
  RUUNE_APIKEY          override the built-in public Ruune key
  RUUNE_REFRESH_TOKEN   legacy: seed a session without login.py
"""
import base64, json, os, re, time
from pathlib import Path

import httpx

BASE = "https://fqnfgorcssrnpcavhfhd.supabase.co"
WEB = "https://web.ruune.ai"
COOKIE = "sb-fqnfgorcssrnpcavhfhd-auth-token"
# Public "publishable" key shipped in Ruune's web app for every user (not a secret).
DEFAULT_APIKEY = "sb_publishable_SnXowShyuQqCPpaJd9IZsQ_zo90I6oB"
APIKEY = os.environ.get("RUUNE_APIKEY") or DEFAULT_APIKEY
DATA_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "ruune-mcp"


def state_path(profile: str | None = None) -> Path:
    profile = profile or os.environ.get("RUUNE_PROFILE", "default")
    legacy = DATA_DIR / "session.json"
    if profile == "default" and legacy.exists():
        return legacy
    return DATA_DIR / f"session-{profile}.json"


def discover_apikey() -> str | None:
    """Read the current public key out of Ruune's web app, in case it ever changes."""
    try:
        html = httpx.get(f"{WEB}/login", timeout=20, follow_redirects=True).text
        for src in re.findall(r'src="([^"]+\.js)"', html):
            js = httpx.get(src if src.startswith("http") else WEB + src, timeout=20).text
            m = re.search(r"sb_publishable_[A-Za-z0-9_-]+", js)
            if m:
                return m.group(0)
    except Exception:
        pass
    return None


def save_session(path: Path, d: dict) -> dict:
    s = {"refresh_token": d["refresh_token"], "access_token": d["access_token"],
         "expires_at": d.get("expires_at") or time.time() + d.get("expires_in", 3600),
         "email": (d.get("user") or {}).get("email")}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(s))
    return s


def refresh(refresh_token: str, path: Path) -> dict:
    """Trade a refresh token for a new session and save it (tokens are single-use)."""
    global APIKEY
    for attempt in (1, 2):
        r = httpx.post(f"{BASE}/auth/v1/token", params={"grant_type": "refresh_token"},
                       headers={"apikey": APIKEY}, json={"refresh_token": refresh_token}, timeout=30)
        if r.status_code == 200:
            return save_session(path, r.json())
        if attempt == 1 and "api key" in r.text.lower():
            new = discover_apikey()
            if new and new != APIKEY:
                APIKEY = new
                continue
        raise RuntimeError(f"Ruune sign-in expired or failed ({r.status_code}). "
                           "Run login.py again, then restart Claude Desktop.")


def cookie_session(cookie_value: str) -> dict:
    """Decode the Supabase auth cookie (possibly 'base64-' prefixed) into its session dict."""
    from urllib.parse import unquote
    v = unquote(cookie_value)
    if v.startswith("base64-"):
        b = v[7:].replace("-", "+").replace("_", "/")
        v = base64.b64decode(b + "=" * (-len(b) % 4)).decode()
    return json.loads(v)


# ---------------------------------------------------------------- MCP server
_session: dict = {}


def _ensure() -> None:
    global _session
    path = state_path()
    if not _session:
        if path.exists():
            _session = json.loads(path.read_text())
        elif os.environ.get("RUUNE_REFRESH_TOKEN"):
            _session = {"refresh_token": os.environ["RUUNE_REFRESH_TOKEN"], "access_token": None, "expires_at": 0}
        else:
            raise RuntimeError("Not signed in to Ruune yet. Run login.py, then restart Claude Desktop.")
    if not _session.get("access_token") or _session["expires_at"] - time.time() < 60:
        _force_refresh()


def _force_refresh() -> None:
    global _session
    path = state_path()
    if path.exists():  # file is the source of truth (login.py may have replaced it)
        disk = json.loads(path.read_text())
        if disk.get("refresh_token") != _session.get("refresh_token") and disk.get("expires_at", 0) - time.time() > 60:
            _session = disk
            return
        _session = disk if disk.get("refresh_token") else _session
    _session = refresh(_session["refresh_token"], path)


def _get(path: str, params: dict):
    _ensure()
    for attempt in (1, 2):
        r = httpx.get(f"{BASE}/rest/v1/{path}", params=params, timeout=60,
                      headers={"apikey": APIKEY, "Authorization": f"Bearer {_session['access_token']}"})
        if r.status_code == 401 and attempt == 1:
            _force_refresh()
            continue
        r.raise_for_status()
        return r.json()


def _row(n: dict) -> dict:
    return {"id": n["id"], "title": n.get("title"), "recorded_at": n.get("recorded_at"),
            "status": n.get("status"), "transcript_chars": len(n.get("transcript") or "")}


def build_server():
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("ruune")

    @mcp.tool()
    def list_recordings(limit: int = 20, offset: int = 0, title_contains: str | None = None) -> list[dict]:
        """List Ruune recordings, newest first. Optionally filter by words in the title."""
        p = {"select": "id,title,recorded_at,status,transcript", "archived_at": "is.null",
             "order": "recorded_at.desc.nullslast,created_at.desc", "limit": limit, "offset": offset}
        if title_contains:
            p["title"] = f"ilike.*{title_contains}*"
        return [_row(n) for n in _get("notes", p)]

    @mcp.tool()
    def search_transcripts(query: str, limit: int = 10) -> list[dict]:
        """Find recordings whose transcript contains the phrase; returns a snippet around the first match."""
        rows = _get("notes", {"select": "id,title,recorded_at,status,transcript", "archived_at": "is.null",
                              "transcript": f"ilike.*{query}*", "order": "recorded_at.desc", "limit": limit})
        out = []
        for n in rows:
            t = n.get("transcript") or ""
            i = t.lower().find(query.lower())
            out.append({**_row(n), "snippet": t[max(0, i - 200): i + 200] if i >= 0 else ""})
        return out

    @mcp.tool()
    def get_transcript(recording_id: str, with_speakers: bool = True) -> str:
        """Full transcript of one recording. with_speakers=True gives timestamped speaker turns."""
        rows = _get("notes", {"select": "title,recorded_at,transcript,transcript_json,speaker_labels",
                              "id": f"eq.{recording_id}"})
        if not rows:
            return "Recording not found."
        n = rows[0]
        head = f"# {n.get('title')}\nRecorded: {n.get('recorded_at')}\n\n"
        tj = n.get("transcript_json")
        utts = tj.get("utterances") if isinstance(tj, dict) else None
        if not with_speakers or not utts:
            return head + (n.get("transcript") or "(no transcript yet)")
        labels = n.get("speaker_labels") if isinstance(n.get("speaker_labels"), dict) else {}
        lines = []
        for u in utts:
            s = int(u.get("start") or 0)
            sp = str(u.get("speaker"))
            who = labels.get(sp) or (sp.replace("SPEAKER_", "Speaker ") if sp.startswith("SPEAKER_") else f"Speaker {sp}")
            lines.append(f"[{s // 60:02d}:{s % 60:02d}] {who}: {u.get('text', '').strip()}")
        return head + "\n".join(lines)

    @mcp.tool()
    def get_summary(recording_id: str) -> str:
        """Ruune's AI summaries for one recording (all templates)."""
        rows = _get("note_summaries", {"select": "title,content,created_at,summary_templates(name)",
                                       "note_id": f"eq.{recording_id}", "order": "created_at.asc"})
        if not rows:
            return "No summaries for this recording."
        return "\n\n---\n\n".join(
            f"## {(r.get('summary_templates') or {}).get('name', 'Summary')}\n\n{r.get('content') or ''}" for r in rows)

    return mcp


if __name__ == "__main__":
    build_server().run()
