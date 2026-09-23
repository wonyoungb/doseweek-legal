"""Shared, localized entry points for DoseWeek's two help sites."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COPY = json.loads((ROOT / "docs/help-navigation.json").read_text())
HOME = json.loads((ROOT / "docs/home-content.json").read_text())
assert list(COPY) == list(HOME), "Help navigation must cover the same 17 locales as home"
assert all(len(item) == 9 and all(isinstance(v, str) and v.strip() for v in item.values()) for item in COPY.values())


def task_cards(locale: str, support: str, import_path: str) -> str:
    c = COPY[locale]
    h = HOME[locale]
    items = (
        (support + f"#{locale}-start", c["startTitle"], c["startBody"]),
        (import_path + f"#{locale}", h["importGuide"], h["transferBody"]),
        (support + f"#{locale}-faq", c["solveTitle"], c["solveBody"]),
    )
    return '<div class="help-tasks">' + "".join(
        f'<a class="help-task" href="{html.escape(href)}"><h2>{html.escape(title)}</h2>'
        f'<p>{html.escape(body)}</p><span aria-hidden="true">{"←" if locale == "ar" else "→"}</span></a>'
        for href, title, body in items
    ) + '</div>'


def support_start(locale: str, home: str, import_path: str, privacy: str, privacy_title: str) -> str:
    c = COPY[locale]
    h = HOME[locale]
    links = ((home + f"#{locale}", c["backHome"]), (f"#{locale}-faq", c["solveTitle"]),
             (import_path + f"#{locale}", h["importGuide"]), (privacy + f"#{locale}", privacy_title))
    nav = '<nav class="help-shortcuts">' + ''.join(
        f'<a href="{html.escape(href)}">{html.escape(title)}</a>' for href, title in links
    ) + '</nav>'
    steps = ''.join(f'<li>{html.escape(c[key])}</li>' for key in ("step1", "step2", "step3"))
    return nav + f'<section class="help-start" aria-labelledby="{locale}-start"><h2 id="{locale}-start">{html.escape(c["startTitle"])}</h2><ol>{steps}</ol></section>'
