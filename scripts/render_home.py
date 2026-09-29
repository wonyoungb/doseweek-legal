#!/usr/bin/env python3
"""Render the shared home using the same locale set and guide versions as the apps."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from string import Template

from render_android import escaped, language_navigation, skip_links
from site_assets import script_path, stylesheet_path
from help_navigation import COPY as HELP_COPY, task_cards
import locale_pages

ROOT = Path(__file__).resolve().parents[1]
FIELDS = (
    "title", "intro", "choose", "guide", "iosTitle", "iosBody", "androidTitle",
    "androidBody", "openGuide", "transferTitle", "transferBody", "importGuide", "privacyNote",
)


def sources() -> tuple[dict, dict, dict]:
    content = json.loads((ROOT / "docs/home-content.json").read_text())
    ios = json.loads((ROOT / "docs/ios-content.json").read_text())
    android = json.loads((ROOT / "docs/android-content.candidate.json").read_text())
    assert list(content) == ios["localeOrder"] == android["localeOrder"], "Home locale coverage must match both guides"
    return content, ios, android


def home_panel(locale: str, raw: dict, ios: dict, android: dict) -> str:
    assert set(raw) == set(FIELDS), f"{locale}: home fields differ"
    assert all(isinstance(v, str) and v.strip() for v in raw.values()), f"{locale}: empty home copy"
    c = {key: escaped(value) for key, value in raw.items()}
    policy = ios["locales"][locale]["privacy"]
    direction = ios["locales"][locale]["direction"]
    privacy = escaped(android["locales"][locale]["home"]["privacyLinkTitle"])
    medical = policy["medicalDisclaimer"]
    return f'''      <article id="{locale}" class="language-panel" lang="{locale}" dir="{direction}" data-language="{locale}" data-document-title="DoseWeek {c['guide']}" aria-labelledby="{locale}-title">
        <div id="{locale}-content" tabindex="-1" data-skip-target>
          <header class="hero home-hero help-home-hero"><p class="eyebrow">DoseWeek · iPhone / iPad</p><h1 id="{locale}-title">{c['guide']}</h1><p class="hero-copy">{c['iosBody']}</p></header>
          {task_cards(locale, 'support/', 'import/')}
          <a class="help-privacy" href="privacy/#{locale}"><strong>{privacy}</strong><span>{escaped(HELP_COPY[locale]['privacyBody'])}</span></a>
          <a class="help-platform" href="android/#{locale}">{c['androidTitle']} <span aria-hidden="true">{"←" if direction == "rtl" else "→"}</span></a>
          <p class="quiet-note home-note">{escaped(medical['body'])} {escaped(medical['notAMedicalDevice'])}</p>
        </div>
      </article>'''


def rendered() -> str:
    content, ios, android = sources()
    panels = [home_panel(locale, raw, ios, android) for locale, raw in content.items()]
    return Template((ROOT / "templates/home.html").read_text()).substitute(
        stylesheet=stylesheet_path(), skips=skip_links(ios), navigation=language_navigation(ios),
        panels="\n\n".join(panels), alternates=locale_pages.alternate_links(""),
        language_script=script_path("language.js"),
    )


def rendered_locale_pages() -> dict[Path, str]:
    """/<locale>/: the same home panel on its own page (description: the home intro)."""
    content, ios, android = sources()
    names = {locale: entry["languageName"] for locale, entry in ios["locales"].items()}
    return {
        locale_pages.page_path("", locale): locale_pages.locale_page(
            route="", locale=locale, names=names, description=raw["intro"],
            panel=home_panel(locale, raw, ios, android),
            icon="assets/app-icon.png", social_image=f"{locale_pages.SITE_BASE}assets/app-icon.png",
            image_alt="DoseWeek app icon", brand_href="./", brand_aria="DoseWeek",
            brand_label="DoseWeek", skip_label=ios["locales"][locale]["common"]["skipToContent"],
            skip_target=f"{locale}-content", body_attributes=' class="home-simple"',
            footer='<footer class="site-footer site-shell"><span>© 2026 Wonyoung Choi</span>'
                   '<span lang="en">DoseWeek · Private by design</span></footer>',
        )
        for locale, raw in content.items()
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    pages = {ROOT / "index.html": rendered(), **rendered_locale_pages()}
    locale_pages.write_pages(pages, args.check, "run scripts/render_home.py")
    print(f"OK: shared home and {len(pages) - 1} language homes match all 17 guide locales and catalog versions")


if __name__ == "__main__":
    main()
