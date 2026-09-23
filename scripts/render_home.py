#!/usr/bin/env python3
"""Render the shared home using the same locale set and guide versions as the apps."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from string import Template

from render_android import escaped, language_navigation, skip_links
from site_assets import stylesheet_path
from help_navigation import COPY as HELP_COPY, task_cards

ROOT = Path(__file__).resolve().parents[1]
FIELDS = (
    "title", "intro", "choose", "guide", "iosTitle", "iosBody", "androidTitle",
    "androidBody", "openGuide", "transferTitle", "transferBody", "importGuide", "privacyNote",
)


def rendered() -> str:
    content = json.loads((ROOT / "docs/home-content.json").read_text())
    ios = json.loads((ROOT / "docs/ios-content.json").read_text())
    android = json.loads((ROOT / "docs/android-content.candidate.json").read_text())
    assert list(content) == ios["localeOrder"] == android["localeOrder"], "Home locale coverage must match both guides"
    panels = []
    for locale, raw in content.items():
        assert set(raw) == set(FIELDS), f"{locale}: home fields differ"
        assert all(isinstance(v, str) and v.strip() for v in raw.values()), f"{locale}: empty home copy"
        c = {key: escaped(value) for key, value in raw.items()}
        policy = ios["locales"][locale]["privacy"]
        direction = ios["locales"][locale]["direction"]
        privacy = escaped(android["locales"][locale]["home"]["privacyLinkTitle"])
        medical = policy["medicalDisclaimer"]
        panels.append(f'''      <article id="{locale}" class="language-panel" lang="{locale}" dir="{direction}" data-language="{locale}" data-document-title="DoseWeek — {c['title']}" aria-labelledby="{locale}-title">
        <div id="{locale}-content" tabindex="-1" data-skip-target>
          <header class="hero home-hero help-home-hero"><p class="eyebrow">DoseWeek · iPhone / iPad</p><h1 id="{locale}-title">{c['guide']}</h1><p class="hero-copy">{c['iosBody']}</p></header>
          {task_cards(locale, 'support/', 'import/')}
          <a class="help-privacy" href="privacy/#{locale}"><strong>{privacy}</strong><span>{escaped(HELP_COPY[locale]['privacyBody'])}</span></a>
          <a class="help-platform" href="android/#{locale}">{c['androidTitle']} <span aria-hidden="true">{"←" if direction == "rtl" else "→"}</span></a>
          <p class="quiet-note home-note">{escaped(medical['body'])} {escaped(medical['notAMedicalDevice'])}</p>
        </div>
      </article>''')
    return Template((ROOT / "templates/home.html").read_text()).substitute(
        stylesheet=stylesheet_path(), skips=skip_links(ios), navigation=language_navigation(ios),
        panels="\n\n".join(panels),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = rendered()
    target = ROOT / "index.html"
    if args.check:
        assert target.read_text() == output, "index.html is stale; run scripts/render_home.py"
    else:
        target.write_text(output)
    print("OK: shared home matches all 17 guide locales and catalog versions")


if __name__ == "__main__":
    main()
