#!/usr/bin/env python3
"""Render the shared Terms of Use for both apps from docs/terms-content.json.

Outputs terms/index.html (the multilingual hash page, x-default of the route) and one language
page per locale (/<locale>/terms/), with the same page shell, hreflang links and no-JavaScript
fallback as the privacy pages. Billing that differs by store sits in two marked subsections of
section 3 (App Store, Google Play). The medical section reuses the existing localized iOS
disclaimer and urgent-help wording verbatim; validate() keeps them identical.

The Terms have no live version. Their effective date is the monetization release date
(legal_release.NEXT_RELEASE_EFFECTIVE_DATE): while it is None the page shows no date, and
`check_site.py --release` fails until the owner sets it.
"""

from __future__ import annotations

import argparse
import functools
import html
import json
import re
from pathlib import Path

from site_assets import script_path, stylesheet_path
import legal_release
import locale_pages

ROOT = Path(__file__).resolve().parents[1]
SITE_BASE = locale_pages.SITE_BASE
CONTENT_PATH = ROOT / "docs/terms-content.json"
IOS_CONTENT_PATH = ROOT / "docs/ios-content.json"
ROUTE = "terms/"
PAGE_PATH = ROOT / "terms/index.html"
CANONICAL = f"{SITE_BASE}{ROUTE}"
TITLE = "DoseWeek Terms of Use"
DESCRIPTION = (
    "Terms of Use for DoseWeek on iPhone, iPad and Android: the free version with ads, the "
    "optional Plus subscription, billing through the App Store and Google Play, and the app's "
    "medical limits."
)
SOCIAL_IMAGE = f"{SITE_BASE}assets/app-icon.png"
SUPPORT_EMAIL = "wonyoung@wonyoungchoi.dev"
SECTION_IDS = [
    "service", "free-plus", "billing", "ad-free-pass", "medical", "records", "changes", "contact",
]
PARAGRAPH_COUNTS = {
    "service": 1, "free-plus": 3, "billing": 2, "ad-free-pass": 1, "medical": 3, "records": 1,
    "changes": 1, "contact": 1,
}
SUBSECTIONS = {"billing": {"billing-ios": 2, "billing-android": 1}}
MEDICAL_SECTION_ID = "medical"
# Deliberate external link (reviewed 2026-09-29): Apple's standard EULA, which also governs the
# iOS app. check_site.py allows it only on the Terms pages.
EULA_URL = "https://www.apple.com/legal/internet-services/itunes/dev/stdeula/"
LINKED_URLS = (EULA_URL,)
# Final reference prices (superseding owner/spec decision, 2026-10-02). The Store supplies the actual
# localized price, eligible introductory offer and billing period before purchase.
REFERENCE_PRICES = ("USD 1.99", "USD 13.99", "KRW 3,300", "KRW 22,000", "JPY 300", "JPY 1,980")


def escaped(value: object) -> str:
    return html.escape(str(value), quote=True)


def paragraph_blocks(value: str) -> list[str]:
    """Blank-line ("\\n\\n") separated display paragraphs, as in the policy renderers."""
    return value.split("\n\n")


def breakable_url(safe_url: str) -> str:
    scheme, separator, rest = safe_url.partition("://")
    return scheme + separator + re.sub(r"/(?=.)", "/<wbr>", rest)


def terms_paragraph(value: str) -> str:
    """Escaped text; only LINKED_URLS become links (left-to-right in RTL); "\\n" becomes <br>."""
    rendered = escaped(value)
    for url in LINKED_URLS:
        safe_url = escaped(url)
        rendered = rendered.replace(
            safe_url, f'<a href="{safe_url}"><bdi dir="ltr">{breakable_url(safe_url)}</bdi></a>'
        )
    return rendered.replace("\n", "<br>")


def load() -> tuple[dict, dict]:
    content = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
    ios = json.loads(IOS_CONTENT_PATH.read_text(encoding="utf-8"))
    return content, ios


def validate(content: dict, ios: dict) -> None:
    assert set(content) == {
        "schemaVersion", "effectiveDate", "supportEmail", "localeOrder", "locales",
    }, "terms-content.json: unexpected top-level keys"
    assert content["schemaVersion"] == 1
    # The Terms first take effect with the monetization release; no earlier date exists.
    assert content["effectiveDate"] == legal_release.NEXT_RELEASE_EFFECTIVE_DATE, (
        "docs/terms-content.json effectiveDate must equal legal_release.NEXT_RELEASE_EFFECTIVE_DATE "
        "(null until the owner sets the release date)"
    )
    assert content["supportEmail"] == SUPPORT_EMAIL
    assert content["localeOrder"] == list(locale_pages.LOCALES) == ios["localeOrder"]
    assert list(content["locales"]) == content["localeOrder"]
    assert "<" not in json.dumps(content, ensure_ascii=False), (
        "terms copy is plain text; markup is added by the renderer"
    )
    for locale, entry in content["locales"].items():
        assert set(entry) == {"title", "intro", "effectiveDateLabel", "sections", "links"}, locale
        assert set(entry["links"]) == {"privacyIos", "privacyAndroid"}, locale
        for value in (entry["title"], entry["intro"], entry["effectiveDateLabel"],
                      *entry["links"].values()):
            assert isinstance(value, str) and value.strip(), locale
        assert [section["id"] for section in entry["sections"]] == SECTION_IDS, locale
        for number, section in enumerate(entry["sections"], start=1):
            label = f"{locale}:{section['id']}"
            expected_keys = {"id", "title", "paragraphs"} | (
                {"subsections"} if section["id"] in SUBSECTIONS else set()
            )
            assert set(section) == expected_keys, label
            assert section["title"].startswith(f"{number}. "), f"{label}: title must start with {number}."
            assert len(section["paragraphs"]) == PARAGRAPH_COUNTS[section["id"]], label
            if section["id"] in SUBSECTIONS:
                assert [sub["id"] for sub in section["subsections"]] == list(SUBSECTIONS[section["id"]]), label
                for sub in section["subsections"]:
                    assert set(sub) == {"id", "title", "paragraphs"}, f"{label}:{sub['id']}"
                    assert sub["title"].strip(), f"{label}:{sub['id']}"
                    assert len(sub["paragraphs"]) == SUBSECTIONS[section["id"]][sub["id"]], (
                        f"{label}:{sub['id']}"
                    )
            for paragraph in paragraphs(section):
                assert isinstance(paragraph, str) and paragraph.strip(), label
        by_id = {section["id"]: section for section in entry["sections"]}
        # The medical section reuses the existing localized wording, unchanged.
        ios_entry = ios["locales"][locale]
        disclaimer = ios_entry["privacy"]["medicalDisclaimer"]
        medical = by_id[MEDICAL_SECTION_ID]
        assert medical["title"] == f"{SECTION_IDS.index(MEDICAL_SECTION_ID) + 1}. {disclaimer['title']}", (
            f"{locale}: the medical section title must reuse the privacy disclaimer title"
        )
        assert medical["paragraphs"] == [
            disclaimer["body"], disclaimer["notAMedicalDevice"],
            ios_entry["support"]["safetyCards"][1]["body"],
        ], f"{locale}: the medical section must reuse the existing disclaimer wording verbatim"
        # Invariants every translation keeps: store names, the EULA link, the numbers in the
        # renewal and pass terms, and the support address.
        billing = {sub["id"]: sub for sub in by_id["billing"]["subsections"]}
        ios_billing = " ".join(billing["billing-ios"]["paragraphs"])
        android_billing = " ".join(billing["billing-android"]["paragraphs"])
        assert "App Store" in billing["billing-ios"]["title"], f"{locale}: iOS subsection names App Store"
        assert "Google Play" in billing["billing-android"]["title"], (
            f"{locale}: Android subsection names Google Play"
        )
        assert ios_billing.count("24") >= 2, f"{locale}: App Store renewal terms need the 24-hour rule"
        text = json.dumps(entry, ensure_ascii=False)
        assert text.count(EULA_URL) == 1 and EULA_URL in billing["billing-ios"]["paragraphs"][-1], (
            f"{locale}: the iOS subsection links Apple's standard EULA once"
        )
        assert "Google Play" in android_billing, locale
        pass_text = " ".join(by_id["ad-free-pass"]["paragraphs"])
        assert "30" not in pass_text, f"{locale}: stale 30-minute pass"
        assert "24" in pass_text and "48" in pass_text, f"{locale}: rewarded pass limits"
        assert SUPPORT_EMAIL in by_id["contact"]["paragraphs"][0], f"{locale}: contact address"
        offer = by_id["free-plus"]["paragraphs"][2]
        assert all(price in offer for price in REFERENCE_PRICES), (
            f"{locale}: final reference prices and their full billing periods must be disclosed"
        )
        assert "2,900" not in offer and "App Store" in offer and "Google Play" in offer, (
            f"{locale}: offer must use the final Korean price and identify Store eligibility"
        )
        assert not re.search(r"(?<![\d,])30(?![\d,])", offer), (
            f"{locale}: a calendar-month trial cannot be described as 30 days"
        )
        billing_rights = by_id["billing"]["paragraphs"][1]
        assert all(period in billing_rights for period in ("7", "3", "30", "50–20", "15–45", "7–30")), (
            f"{locale}: consumer-rights and applicable notice windows must survive rendering"
        )


def paragraphs(section: dict) -> list[str]:
    return [*section["paragraphs"], *(
        paragraph for sub in section.get("subsections", []) for paragraph in sub["paragraphs"]
    )]


def section_markup(locale: str, section: dict) -> str:
    body = "".join(
        f"<p>{terms_paragraph(block)}</p>"
        for paragraph in section["paragraphs"] for block in paragraph_blocks(paragraph)
    )
    for sub in section.get("subsections", []):
        body += f'<h3 id="{escaped(locale)}-{escaped(sub["id"])}">{escaped(sub["title"])}</h3>'
        body += "".join(
            f"<p>{terms_paragraph(block)}</p>"
            for paragraph in sub["paragraphs"] for block in paragraph_blocks(paragraph)
        )
    medical = " medical" if section["id"] == MEDICAL_SECTION_ID else ""
    return (
        f'              <section id="{escaped(locale)}-{escaped(section["id"])}" '
        f'class="policy-section{medical}"><h2>{escaped(section["title"])}</h2><div>{body}</div></section>'
    )


def panel(locale: str, entry: dict, ios_entry: dict, effective_date: str | None) -> str:
    direction = ios_entry["direction"]
    arrow = "←" if direction == "rtl" else "→"
    contents = ios_entry["common"]["contents"]
    document_title = f"{entry['title']} — DoseWeek"
    toc = "".join(
        f'<li><a href="#{escaped(locale)}-{escaped(section["id"])}">{escaped(section["title"])}</a></li>'
        for section in entry["sections"]
    )
    sections = "\n".join(section_markup(locale, section) for section in entry["sections"])
    date = (
        f'\n            <p class="date"><time datetime="{escaped(effective_date)}">'
        f'{escaped(entry["effectiveDateLabel"])}: {escaped(effective_date)}</time></p>'
        if effective_date else ""
    )
    return f"""        <article id="{escaped(locale)}" class="language-panel" lang="{escaped(locale)}" dir="{escaped(direction)}" data-language="{escaped(locale)}" data-document-title="{escaped(document_title)}" aria-labelledby="{escaped(locale)}-content">
          <header class="hero">
            <p class="eyebrow">DoseWeek · iPhone · iPad · Android</p>
            <h1 id="{escaped(locale)}-content" data-skip-target tabindex="-1">{escaped(entry['title'])}</h1>
            <p class="hero-copy">{escaped(entry['intro'])}</p>{date}
          </header>

          <div class="policy-layout">
            <nav class="policy-toc" aria-label="{escaped(contents)}"><h2>{escaped(contents)}</h2><ol>{toc}</ol></nav>
            <div class="policy-card">
{sections}
            </div>
          </div>
          <a class="page-link" href="../privacy/#{escaped(locale)}">{escaped(entry['links']['privacyIos'])} <span aria-hidden="true">{arrow}</span></a>
          <a class="page-link" href="../android/privacy/#{escaped(locale)}">{escaped(entry['links']['privacyAndroid'])} <span aria-hidden="true">{arrow}</span></a>
        </article>"""


FOOTER = (
    '<footer class="site-footer site-shell"><span>© 2026 Wonyoung Choi</span>'
    '<span>DoseWeek</span></footer>'
)


def rendered(content: dict, ios: dict) -> str:
    validate(content, ios)
    locales = ios["locales"]
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
        panel(locale, content["locales"][locale], locales[locale], content["effectiveDate"])
        for locale in content["localeOrder"]
    )
    document_title = f"{content['locales']['ko']['title']} — DoseWeek"
    return f"""<!doctype html>
<html lang="ko" dir="ltr">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
    <meta name="description" content="{escaped(DESCRIPTION)}">
    <meta name="color-scheme" content="light dark">
    <meta name="theme-color" media="(prefers-color-scheme: light)" content="#f4f4f8">
    <meta name="theme-color" media="(prefers-color-scheme: dark)" content="#0d0d11">
    <title>{escaped(document_title)}</title>
    <link rel="canonical" href="{CANONICAL}">
{locale_pages.alternate_links(ROUTE)}
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
    <link rel="stylesheet" href="{stylesheet_path('../')}">
    <script src="{script_path('language.js', '../')}" defer></script>
  </head>
  <body data-page="terms">
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

    {FOOTER}
  </body>
</html>
"""


def rendered_locale_pages(content: dict, ios: dict) -> dict[Path, str]:
    """/<locale>/terms/: the hash page's panel, one language each (description: the intro)."""
    validate(content, ios)
    names = {locale: entry["languageName"] for locale, entry in ios["locales"].items()}
    pages = {}
    for locale in content["localeOrder"]:
        entry, ios_entry = content["locales"][locale], ios["locales"][locale]
        pages[locale_pages.page_path(ROUTE, locale)] = locale_pages.locale_page(
            route=ROUTE, locale=locale, names=names, description=entry["intro"],
            panel=panel(locale, entry, ios_entry, content["effectiveDate"]),
            icon="assets/app-icon.png", social_image=SOCIAL_IMAGE, image_alt="DoseWeek app icon",
            brand_href="../", brand_aria="DoseWeek", brand_label="DoseWeek",
            skip_label=ios_entry["common"]["skipToContent"], skip_target=f"{locale}-content",
            body_attributes=' data-page="terms"', footer=FOOTER,
        )
    return pages


def rendered_pages(content: dict, ios: dict) -> dict[Path, str]:
    return {PAGE_PATH: rendered(content, ios), **rendered_locale_pages(content, ios)}


@functools.lru_cache(maxsize=None)
def link_titles() -> dict[str, str]:
    """Localized Terms titles by locale: the privacy and support pages link here with them."""
    content = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
    return {locale: entry["title"] for locale, entry in content["locales"].items()}


def page_link(locale: str, prefix: str, direction: str) -> str:
    """The Terms link placed after a privacy or support panel's own page link."""
    arrow = "←" if direction == "rtl" else "→"
    return (
        f'<a class="page-link" href="{prefix}terms/#{escaped(locale)}">'
        f'{escaped(link_titles()[locale])} <span aria-hidden="true">{arrow}</span></a>'
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    content, ios = load()
    pages = rendered_pages(content, ios)
    locale_pages.write_pages(pages, arguments.check, "rerun render_terms.py")
    date = content["effectiveDate"] or "not set (release date BLOCKED)"
    if arguments.check:
        print(f"OK: Terms of Use page ({len(content['locales'])} locales) and {len(pages) - 1} "
              f"language pages; effective date {date}")
        return
    print(f"Rendered terms/index.html and {len(pages) - 1} language pages from "
          f"{CONTENT_PATH.relative_to(ROOT)}; effective date {date}")


if __name__ == "__main__":
    main()
