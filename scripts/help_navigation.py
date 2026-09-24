"""Shared, localized entry points for DoseWeek's two help sites."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COPY = json.loads((ROOT / "docs/help-navigation.json").read_text())
HOME = json.loads((ROOT / "docs/home-content.json").read_text())
COPY_KEYS = {"startTitle", "startBody", "solveTitle", "solveBody", "backHome", "privacyBody"}
assert list(COPY) == list(HOME), "Help navigation must cover the same 17 locales as home"
assert all(set(item) == COPY_KEYS and all(isinstance(v, str) and v.strip() for v in item.values()) for item in COPY.values())


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


def support_start(locale: str, home: str, import_path: str, privacy: str, privacy_title: str,
                  steps: list[tuple[str, str, str, str]]) -> str:
    """Shortcut links, then the six-step getting-started guide (anchor #<locale>-start).

    Each step is (title, body, href, link text); the link points to the FAQ answer or policy
    section that explains the step in detail.
    """
    c = COPY[locale]
    h = HOME[locale]
    arrow = "←" if locale == "ar" else "→"
    links = ((home + f"#{locale}", c["backHome"]), (f"#{locale}-faq", c["solveTitle"]),
             (import_path + f"#{locale}", h["importGuide"]), (privacy + f"#{locale}", privacy_title))
    nav = '<nav class="help-shortcuts">' + ''.join(
        f'<a href="{html.escape(href)}">{html.escape(title)}</a>' for href, title in links
    ) + '</nav>'
    assert len(steps) == 6, f"{locale}: the guide has six steps"
    items = ''.join(
        f'<li><strong>{html.escape(title)}</strong><p>{html.escape(body)}</p>'
        f'<a href="{html.escape(href)}">{html.escape(link_text)} <span aria-hidden="true">{arrow}</span></a></li>'
        for title, body, href, link_text in steps
    )
    return (
        nav + f'<section class="help-start" aria-labelledby="{locale}-start">'
        f'<h2 id="{locale}-start">{html.escape(c["startTitle"])}</h2>'
        f'<p>{html.escape(c["startBody"])}</p><ol>{items}</ol></section>'
    )
