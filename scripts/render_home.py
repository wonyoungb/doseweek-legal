#!/usr/bin/env python3
"""Render the shared home using the same locale set and guide versions as the apps."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from string import Template

from render_android import escaped, language_navigation, skip_links
from site_assets import stylesheet_path

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
        cards = []
        for platform, version, icon, route in (
            ("ios", ios["bundleVersion"], "app-icon.png", ""),
            ("android", android["versionName"], "android-app-icon.png", "android/"),
        ):
            label = "iOS" if platform == "ios" else "Android"
            cards.append(f'''          <section class="info-card platform-card" aria-labelledby="{locale}-{platform}">
            <div class="platform-heading"><img src="assets/{icon}" alt="" width="48" height="48"><div><p class="platform-version">{label} {escaped(version)} · {c['guide']}</p><h3 id="{locale}-{platform}">{c[platform+'Title']}</h3></div></div>
            <p>{c[platform+'Body']}</p>
            <div class="button-row"><a class="button primary" href="{route}support/#{locale}">{c['openGuide']}</a><a class="button" href="{route}privacy/#{locale}">{privacy}</a></div>
          </section>''')
        panels.append(f'''      <article id="{locale}" class="language-panel" lang="{locale}" dir="{direction}" data-language="{locale}" data-document-title="DoseWeek — {c['title']}" aria-labelledby="{locale}-title">
        <div id="{locale}-content" tabindex="-1" data-skip-target>
          <header class="hero home-hero"><p class="eyebrow">DoseWeek</p><h1 id="{locale}-title">{c['title']}</h1><p class="hero-copy">{c['intro']}</p></header>
          <section class="content-section home-platforms" aria-labelledby="{locale}-choose">
            <h2 id="{locale}-choose">{c['choose']}</h2>
            <div class="card-grid platform-grid">
{chr(10).join(cards)}
            </div>
          </section>
          <section class="home-transfer" aria-labelledby="{locale}-transfer"><div><h2 id="{locale}-transfer">{c['transferTitle']}</h2><p>{c['transferBody']}</p></div><a class="button" href="import/#{locale}">{c['importGuide']}</a></section>
          <p class="quiet-note home-note">{c['privacyNote']}</p>
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
