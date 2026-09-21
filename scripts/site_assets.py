"""Content-versioned local styles prevent mixed old/new page layouts."""
from hashlib import sha256
from pathlib import Path


def stylesheet_path(prefix: str = "") -> str:
    css = Path(__file__).resolve().parents[1] / "assets/site.css"
    version = sha256(css.read_bytes()).hexdigest()[:12]
    return f"{prefix}assets/site.css?v={version}"
