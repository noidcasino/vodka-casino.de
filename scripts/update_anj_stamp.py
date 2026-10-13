import re
import ssl
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
ANJ_JS = "https://af84fdbb-4457-4ce1-85e4-18782f98b79b.snippet.anjcdn.org/anj-seal.js"
STAMP_RE = re.compile(r"[a-f0-9]{32}")


def fetch_stamp() -> str:
    url = f"{ANJ_JS}?t={int(time.time())}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    raw = urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=60).read()
    text = raw.decode("utf-8", "replace")
    text = re.sub(r"\\x([0-9a-fA-F]{2})", lambda m: chr(int(m.group(1), 16)), text)
    m = re.search(r"sealassets/([a-f0-9]{32})-", text)
    if m:
        return m.group(1)
    m = re.search(r"stamp=([a-f0-9]{32})", text)
    if m:
        return m.group(1)
    raise RuntimeError("stamp not found in anj-seal.js")


def current_stamp(html: str) -> str | None:
    m = re.search(
        r"verification\.anjouangamingboard\.org/validate\?[^\"']*stamp=([a-f0-9]{32})",
        html,
    )
    if m:
        return m.group(1)
    m = re.search(r"sealassets/([a-f0-9]{32})-vodka\.bet-", html)
    if m:
        return m.group(1)
    return None


def apply_stamp(html: str, old: str, new: str) -> str:
    if old == new:
        return html
    if not STAMP_RE.fullmatch(old) or not STAMP_RE.fullmatch(new):
        raise RuntimeError("invalid stamp format")
    out = html
    out = out.replace(f"stamp={old}", f"stamp={new}")
    out = out.replace(f"sealassets/{old}-vodka.bet-", f"sealassets/{new}-vodka.bet-")
    if out.count(new) < 1:
        raise RuntimeError("stamp replacement produced no matches")
    if old in out and f"stamp={old}" in out:
        raise RuntimeError("old stamp still present in validate url")
    return out


def main() -> int:
    html = INDEX.read_text(encoding="utf-8")
    old = current_stamp(html)
    new = fetch_stamp()
    print(f"old={old}")
    print(f"new={new}")
    if not old:
        print("no existing stamp in index.html", file=sys.stderr)
        return 2
    if old == new:
        print("unchanged")
        return 0
    updated = apply_stamp(html, old, new)
    if updated == html:
        print("no file changes")
        return 0
    INDEX.write_text(updated, encoding="utf-8")
    print("updated index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())