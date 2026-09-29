"""Content-versioned local assets prevent mixed old/new page layouts and scripts."""
from hashlib import sha256
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / "assets"


def stylesheet_path(prefix: str = "") -> str:
    return script_path("site.css", prefix)


def script_path(name: str, prefix: str = "") -> str:
    """`assets/<name>?v=<content hash>`: a changed file gets a new URL, so no cached copy runs."""
    version = sha256((ASSETS / name).read_bytes()).hexdigest()[:12]
    return f"{prefix}assets/{name}?v={version}"
