#!/usr/bin/env python3
"""Render the iOS public privacy policy from the vendored iOS legal catalog.

`docs/ios-content.json` mirrors the iOS app catalog
(`DoseDay/Resources/Localizable.xcstrings`) verbatim for every policy string, plus the
repository-local second-release candidate section. Pass `--catalog` to prove the mirror,
which is what `check_site.py --catalog` does.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTENT_PATH = ROOT / "docs/ios-content.json"
PAGE_PATH = ROOT / "privacy/index.html"
SITE_BASE = "https://doseweek-legal.wonyoungchoi.dev/"
SOCIAL_IMAGE = f"{SITE_BASE}assets/app-icon.png"
CANONICAL = f"{SITE_BASE}privacy/"
TITLE = "DoseWeek Privacy Policy"
DESCRIPTION = (
    "Privacy policy for DoseWeek on iPhone and iPad: local records, read-only Apple Health "
    "access, user-directed encrypted backups, and optional calendar sync."
)
LOCALE_ORDER = [
    "ko", "en", "ja", "de", "fr", "es", "it", "nl", "pt-PT", "pl", "sv", "hi",
    "pt-BR", "ar", "zh-Hans", "zh-Hant", "tr",
]
SECTION_IDS = [
    "storage", "health", "backups", "notifications", "tracking", "deletion", "contact", "ai",
    "calendar", "next-release",
]
CANDIDATE_SECTION_ID = "next-release"
CANDIDATE_VERSION = "1.0.4 (build 16)"
CATALOG_KEYS = {
    "storage": 1, "health": 2, "backups": 3, "notifications": 4, "tracking": 5,
    "deletion": 6, "contact": 7, "ai": 8, "calendar": 9,
}


def escaped(value: object) -> str:
    return html.escape(str(value), quote=True)


def validate(content: dict) -> None:
    assert set(content) == {
        "schemaVersion", "platform", "bundleVersion", "effectiveDate", "supportEmail",
        "localeOrder", "locales",
    }
    assert content["schemaVersion"] == 1
    assert content["platform"] == "ios"
    assert content["bundleVersion"] == CANDIDATE_VERSION
    assert content["effectiveDate"] == "2026-08-22"
    assert content["supportEmail"] == "wonyoung@wonyoungchoi.dev"
    assert content["localeOrder"] == LOCALE_ORDER
    assert list(content["locales"]) == LOCALE_ORDER

    for locale, entry in content["locales"].items():
        assert set(entry) == {"languageName", "direction", "common", "privacy"}, locale
        assert entry["direction"] == ("rtl" if locale == "ar" else "ltr"), locale
        assert set(entry["common"]) == {"skipToContent", "contents", "supportLinkTitle"}, locale
        privacy = entry["privacy"]
        assert set(privacy) == {
            "title", "intro", "effectiveDate", "sections", "medicalDisclaimer",
        }, locale
        assert set(privacy["medicalDisclaimer"]) == {
            "title", "body", "notAMedicalDevice",
        }, locale
        assert [section["id"] for section in privacy["sections"]] == SECTION_IDS, locale
        for section in privacy["sections"]:
            assert set(section) == {"id", "title", "paragraphs"}, f"{locale}:{section['id']}"
            expected = 6 if section["id"] == CANDIDATE_SECTION_ID else 1
            assert len(section["paragraphs"]) == expected, f"{locale}:{section['id']}"
            for paragraph in section["paragraphs"]:
                assert isinstance(paragraph, str) and paragraph.strip(), (
                    f"{locale}:{section['id']}"
                )
        candidate = privacy["sections"][-1]
        assert CANDIDATE_VERSION in candidate["paragraphs"][0], (
            f"{locale}: the candidate section must name the released version it follows"
        )
        serialized = json.dumps(candidate, ensure_ascii=False)
        # Every food data source keeps its name and its licence basis in every language;
        # Japanese and Chinese name the Japanese provider by its official name instead of MEXT.
        for tokens in (
            ("iOS 26.0",), ("CC0 1.0",), ("Open Government Licence v3.0",),
            ("USDA",), ("CoFID",), ("data.go.kr",), ("MEXT", "文部科学省", "文部科學省"),
        ):
            assert any(token in serialized for token in tokens), (
                f"{locale}: candidate section is missing {tokens[0]!r}"
            )
        for string in (
            entry["languageName"], entry["common"]["skipToContent"],
            entry["common"]["contents"], entry["common"]["supportLinkTitle"],
            privacy["title"], privacy["intro"], privacy["effectiveDate"],
        ):
            assert isinstance(string, str) and string.strip(), locale


def catalog_parity(content: dict, catalog_path: Path) -> None:
    """Every policy string except the repository-local candidate section is verbatim."""
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))["strings"]

    def value(key: str, locale: str) -> str:
        return catalog[key]["localizations"][locale]["stringUnit"]["value"]

    for locale, entry in content["locales"].items():
        privacy = entry["privacy"]
        assert privacy["title"] == value("privacy.title", locale), f"{locale}: privacy.title"
        assert privacy["intro"] == value("privacy.intro", locale), f"{locale}: privacy.intro"
        assert privacy["effectiveDate"] == value("privacy.effectiveDate", locale), (
            f"{locale}: privacy.effectiveDate"
        )
        disclaimer = privacy["medicalDisclaimer"]
        assert disclaimer["title"] == value("privacy.medical.title", locale), locale
        assert disclaimer["body"] == value("privacy.medical.body", locale), locale
        assert disclaimer["notAMedicalDevice"] == value("common.notAMedicalDevice", locale), locale
        for section in privacy["sections"]:
            if section["id"] == CANDIDATE_SECTION_ID:
                continue
            number = CATALOG_KEYS[section["id"]]
            assert section["title"] == value(f"privacy.section{number}.title", locale), (
                f"{locale}: privacy.section{number}.title does not match the app catalog"
            )
            assert section["paragraphs"][0] == value(f"privacy.section{number}.body", locale), (
                f"{locale}: privacy.section{number}.body does not match the app catalog"
            )


def panel(locale: str, entry: dict, bundle_version: str, effective_date: str) -> str:
    privacy = entry["privacy"]
    direction = entry["direction"]
    arrow = "←" if direction == "rtl" else "→"
    document_title = f"{privacy['title']} — DoseWeek"
    toc = "".join(
        f'<li><a href="#{escaped(locale)}-{escaped(section["id"])}">'
        f'{escaped(section["title"])}</a></li>'
        for section in privacy["sections"]
    )
    toc += (
        f'<li><a href="#{escaped(locale)}-medical">'
        f'{escaped(privacy["medicalDisclaimer"]["title"])}</a></li>'
    )
    sections = "\n".join(
        f'              <section id="{escaped(locale)}-{escaped(section["id"])}" '
        f'class="policy-section"'
        + (' data-release-status="candidate"' if section["id"] == CANDIDATE_SECTION_ID else "")
        + f'><h2>{escaped(section["title"])}</h2><div>'
        + "".join(f"<p>{escaped(paragraph)}</p>" for paragraph in section["paragraphs"])
        + "</div></section>"
        for section in privacy["sections"]
    )
    disclaimer = privacy["medicalDisclaimer"]
    return f"""        <article id="{escaped(locale)}" class="language-panel" lang="{escaped(locale)}" dir="{escaped(direction)}" data-language="{escaped(locale)}" data-document-title="{escaped(document_title)}" aria-labelledby="{escaped(locale)}-content">
          <header class="hero">
            <p class="eyebrow">DoseWeek · iOS {escaped(bundle_version)}</p>
            <h1 id="{escaped(locale)}-content" data-skip-target tabindex="-1">{escaped(privacy['title'])}</h1>
            <p class="hero-copy">{escaped(privacy['intro'])}</p>
            <p class="date"><time datetime="{escaped(effective_date)}">{escaped(privacy['effectiveDate'])}</time></p>
          </header>

          <div class="policy-layout">
            <nav class="policy-toc" aria-label="{escaped(entry['common']['contents'])}"><h2>{escaped(entry['common']['contents'])}</h2><ol>{toc}</ol></nav>
            <div class="policy-card">
{sections}
              <section id="{escaped(locale)}-medical" class="policy-section medical"><h2>{escaped(disclaimer['title'])}</h2><div><p>{escaped(disclaimer['body'])}</p><p>{escaped(disclaimer['notAMedicalDevice'])}</p></div></section>
            </div>
          </div>
          <a class="page-link" href="../support/#{escaped(locale if locale in ('ko', 'en', 'ja') else 'en')}">{escaped(entry['common']['supportLinkTitle'])} <span aria-hidden="true">{arrow}</span></a>
        </article>"""


def rendered(content: dict) -> str:
    validate(content)
    locales = content["locales"]
    navigation = "\n".join(
        '          <li><a class="language-link" '
        f'href="#{escaped(locale)}" lang="{escaped(locale)}" hreflang="{escaped(locale)}" '
        f'data-language-link="{escaped(locale)}">{escaped(locales[locale]["languageName"])}</a></li>'
        for locale in content["localeOrder"]
    )
    skips = "\n".join(
        f'    <a class="skip-link" data-language-skip="{escaped(locale)}" '
        f'href="#{escaped(locale)}-content" lang="{escaped(locale)}" '
        f'dir="{escaped(locales[locale]["direction"])}">'
        f'{escaped(locales[locale]["common"]["skipToContent"])}</a>'
        for locale in content["localeOrder"]
    )
    panels = "\n\n".join(
        panel(locale, locales[locale], content["bundleVersion"], content["effectiveDate"])
        for locale in content["localeOrder"]
    )
    return f"""<!doctype html>
<html lang="ko" dir="ltr">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
    <meta name="description" content="{escaped(DESCRIPTION)}">
    <meta name="color-scheme" content="light dark">
    <meta name="theme-color" media="(prefers-color-scheme: light)" content="#f4f4f8">
    <meta name="theme-color" media="(prefers-color-scheme: dark)" content="#0d0d11">
    <title>{escaped(locales['ko']['privacy']['title'])}</title>
    <link rel="canonical" href="{CANONICAL}">
    <link rel="icon" type="image/png" href="../assets/app-icon.png">
    <link rel="apple-touch-icon" href="../assets/app-icon.png">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="DoseWeek">
    <meta property="og:title" content="{escaped(TITLE)}">
    <meta property="og:description" content="{escaped(DESCRIPTION)}">
    <meta property="og:url" content="{CANONICAL}">
    <meta property="og:image" content="{SOCIAL_IMAGE}">
    <meta property="og:image:alt" content="DoseWeek app icon">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{escaped(TITLE)}">
    <meta name="twitter:description" content="{escaped(DESCRIPTION)}">
    <meta name="twitter:image" content="{SOCIAL_IMAGE}">
    <meta name="twitter:image:alt" content="DoseWeek app icon">
    <link rel="stylesheet" href="../assets/site.css">
    <script src="../assets/language.js" defer></script>
  </head>
  <body data-platform="ios" data-page="privacy">
{skips}

    <header class="site-header site-shell">
      <a class="brand" href="../" aria-label="DoseWeek" data-language-path="../">
        <img class="brand-mark" src="../assets/app-icon.png" alt="" width="36" height="36">
        <span class="brand-label">DoseWeek</span>
      </a>
      <nav class="language-nav many-languages" aria-label="Language">
        <ul class="language-list">
{navigation}
        </ul>
      </nav>
    </header>

    <main id="main" class="site-shell" tabindex="-1">
      <div class="language-stack">
{panels}
      </div>
    </main>

    <footer class="site-footer site-shell"><span>© 2026 Wonyoung Choi</span><span>DoseWeek · iOS {escaped(content['bundleVersion'])}</span></footer>
  </body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--catalog",
        type=Path,
        help="optional path to DoseDay/Resources/Localizable.xcstrings for verbatim parity",
    )
    arguments = parser.parse_args()

    content = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
    page = rendered(content)
    if arguments.catalog:
        catalog_parity(content, arguments.catalog.resolve())

    if arguments.check:
        assert PAGE_PATH.is_file(), "missing generated iOS privacy page"
        assert PAGE_PATH.read_text(encoding="utf-8") == page, (
            "stale privacy/index.html; rerun render_ios.py"
        )
        suffix = " and app-catalog parity" if arguments.catalog else ""
        print(f"OK: iOS privacy page ({len(content['locales'])} locales){suffix}")
        return

    PAGE_PATH.write_text(page, encoding="utf-8")
    print(f"Rendered privacy/index.html from {CONTENT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
