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

from legal_release import CURRENT_IOS_EFFECTIVE_DATE, expected_effective_date


ROOT = Path(__file__).resolve().parents[1]
SITE_BASE = "https://doseweek-legal.wonyoungchoi.dev/"
CONTENT_PATH = ROOT / "docs/ios-content.json"
PAGE_PATH = ROOT / "privacy/index.html"
SUPPORT_PATH = ROOT / "support/index.html"
SUPPORT_CANONICAL = f"{SITE_BASE}support/"
SUPPORT_TITLE = "DoseWeek Support"
SUPPORT_DESCRIPTION = (
    "Help with records, Apple Health, notifications, encrypted backups, plaintext exports, "
    "App Lock, on-device AI, and the unreleased candidate features."
)
RELEASED_FAQ = [
    "storage", "health", "notifications", "backup", "exports", "ai", "applock", "deletion",
]
BUGFIX_CANDIDATE_FAQ = ["dates", "edit", "past", "health", "sites"]
SECOND_RELEASE_FAQ = ["meals", "dates", "charts", "calendar", "backup", "devices", "import"]
SUPPORT_LABELS = [
    "title", "lead", "beforeEmailKicker", "beforeEmailTitle", "noticeStrong", "noticeBody",
    "faqKicker", "faqTitle", "faqDescription", "safetyKicker", "safetyTitle",
    "contactKicker", "contactTitle", "contactBody",
]
AI_MODEL_TOKEN = "SystemLanguageModel.default"
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
# Owner decision IOS-VERSION-104-20260917: the pending 1.0.4 (build 15) review is cancelled and the
# stage-2 release ships as iOS 1.0.5. Every candidate notice (five bugfix-candidate answers, seven
# second-release answers and the candidate policy section) names that marketing version, and the
# page eyebrow and footer carry it too. No notice names a build: the store build number is chosen
# at upload, and build 16 has never been uploaded.
CANDIDATE_VERSION = "1.0.5"
PAGE_VERSION = "1.0.5"
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
    assert content["bundleVersion"] == PAGE_VERSION
    assert content["effectiveDate"] == expected_effective_date(CURRENT_IOS_EFFECTIVE_DATE)
    assert content["supportEmail"] == "wonyoung@wonyoungchoi.dev"
    assert content["localeOrder"] == LOCALE_ORDER
    assert list(content["locales"]) == LOCALE_ORDER

    for locale, entry in content["locales"].items():
        assert set(entry) == {"languageName", "direction", "common", "privacy", "support"}, locale
        validate_support(locale, entry["support"])
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
        # The candidate section names the version it belongs to, never a build: the store build
        # number is chosen at upload.
        assert "build" not in candidate["paragraphs"][0].lower(), (
            f"{locale}: the candidate section must not name a build number"
        )
        assert f"iOS {PAGE_VERSION}" in candidate["paragraphs"][0], (
            f"{locale}: the candidate section must name iOS {PAGE_VERSION}"
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


def validate_support(locale: str, support: dict) -> None:
    assert set(support) == {
        "labels", "safetyCards", "released", "candidate", "secondRelease",
    }, locale
    assert set(support["labels"]) == set(SUPPORT_LABELS), locale
    for key, value in support["labels"].items():
        assert isinstance(value, str) and value.strip(), f"{locale}: labels.{key}"
    assert len(support["safetyCards"]) == 2, locale
    for card in support["safetyCards"]:
        assert set(card) == {"title", "body"} and card["title"].strip() and card["body"].strip(), (
            locale
        )
    groups = (
        ("released", RELEASED_FAQ, None),
        ("candidate", BUGFIX_CANDIDATE_FAQ, 2),
        ("secondRelease", SECOND_RELEASE_FAQ, 2),
    )
    for group, keys, answer_count in groups:
        assert list(support[group]) == keys, f"{locale}: {group}"
        for key, item in support[group].items():
            assert set(item) == {"question", "answers"}, f"{locale}: {group}.{key}"
            assert item["question"].strip(), f"{locale}: {group}.{key}"
            expected = answer_count
            if group == "candidate" and key == "sites":
                expected = 3
            if expected is not None:
                assert len(item["answers"]) == expected, f"{locale}: {group}.{key}"
            assert item["answers"] and all(a.strip() for a in item["answers"]), (
                f"{locale}: {group}.{key}"
            )
    # every candidate answer opens with the notice that names the version it belongs to
    for key in BUGFIX_CANDIDATE_FAQ:
        notice = support["candidate"][key]["answers"][0]
        assert f"iOS {CANDIDATE_VERSION}" in notice and "build" not in notice.lower(), (
            f"{locale}: bugfix-candidate {key} must name iOS {CANDIDATE_VERSION}, without a build"
        )
    for key in SECOND_RELEASE_FAQ:
        notice = support["secondRelease"][key]["answers"][0]
        assert f"iOS {PAGE_VERSION}" in notice and "build" not in notice.lower(), (
            f"{locale}: second-release {key} must name unreleased iOS {PAGE_VERSION}, without a build"
        )
    ai_answer = support["released"]["ai"]["answers"][0]
    assert ai_answer.count(AI_MODEL_TOKEN) == 1, f"{locale}: AI answer must name the model once"
    assert "Private Cloud Compute" in ai_answer, locale
    assert "AES-256-GCM" in support["released"]["backup"]["answers"][0], locale
    assert "<" not in json.dumps(support, ensure_ascii=False), (
        f"{locale}: support copy is plain text; markup is added by the renderer"
    )


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
          <a class="page-link" href="../support/#{escaped(locale)}">{escaped(entry['common']['supportLinkTitle'])} <span aria-hidden="true">{arrow}</span></a>
        </article>"""


def faq_answer(text: str) -> str:
    """Escape an answer and wrap the on-device model name in <code>, as the published page did."""
    escaped_text = escaped(text)
    return escaped_text.replace(AI_MODEL_TOKEN, f"<code>{AI_MODEL_TOKEN}</code>")


def faq_details(locale: str, identifier: str, item: dict, candidate: bool) -> str:
    status = ' data-release-status="candidate"' if candidate else ""
    answers = "".join(f"<p>{faq_answer(answer)}</p>" for answer in item["answers"])
    return (
        f'              <details id="{escaped(locale)}-{escaped(identifier)}"{status}>'
        f'<summary><span>{escaped(item["question"])}</span>'
        '<span class="summary-symbol" aria-hidden="true"></span></summary>'
        f'<div class="faq-answer">{answers}</div></details>'
    )


def support_panel(locale: str, entry: dict, bundle_version: str, email: str) -> str:
    support = entry["support"]
    labels = support["labels"]
    direction = entry["direction"]
    arrow = "←" if direction == "rtl" else "→"
    document_title = f"DoseWeek — {labels['title']}"
    faq = []
    for key in RELEASED_FAQ:
        faq.append(faq_details(locale, f"faq-{key}", support["released"][key], False))
    for key in BUGFIX_CANDIDATE_FAQ:
        faq.append(faq_details(locale, f"candidate-{key}", support["candidate"][key], True))
    for key in SECOND_RELEASE_FAQ:
        faq.append(faq_details(locale, f"candidate2-{key}", support["secondRelease"][key], True))
    cards = "".join(
        f'<div class="info-card"><h3>{escaped(card["title"])}</h3><p>{escaped(card["body"])}</p></div>'
        for card in support["safetyCards"]
    )
    mailto = f"mailto:{email}?subject=DoseWeek%20Support"
    privacy_title = entry["privacy"]["title"]
    return f"""        <article id="{escaped(locale)}" class="language-panel" lang="{escaped(locale)}" dir="{escaped(direction)}" data-language="{escaped(locale)}" data-document-title="{escaped(document_title)}" aria-labelledby="{escaped(locale)}-content">
          <header class="hero">
            <p class="eyebrow">DoseWeek · iOS {escaped(bundle_version)}</p>
            <h1 id="{escaped(locale)}-content" data-skip-target tabindex="-1">{escaped(labels['title'])}</h1>
            <p class="hero-copy">{escaped(labels['lead'])}</p>
          </header>

          <section class="content-section" aria-labelledby="{escaped(locale)}-before-email">
            <div class="section-heading"><p class="section-kicker">{escaped(labels['beforeEmailKicker'])}</p><h2 id="{escaped(locale)}-before-email">{escaped(labels['beforeEmailTitle'])}</h2></div>
            <div class="notice" role="note"><span class="notice-symbol" aria-hidden="true">!</span><div><strong>{escaped(labels['noticeStrong'])}</strong><p>{escaped(labels['noticeBody'])}</p></div></div>
          </section>

          <section class="content-section" aria-labelledby="{escaped(locale)}-faq">
            <div class="section-heading"><p class="section-kicker">{escaped(labels['faqKicker'])}</p><h2 id="{escaped(locale)}-faq">{escaped(labels['faqTitle'])}</h2><p class="section-description">{escaped(labels['faqDescription'])}</p></div>
            <div class="faq-list">
{chr(10).join(faq)}
            </div>
          </section>

          <section class="content-section" aria-labelledby="{escaped(locale)}-safety">
            <div class="section-heading"><p class="section-kicker">{escaped(labels['safetyKicker'])}</p><h2 id="{escaped(locale)}-safety">{escaped(labels['safetyTitle'])}</h2></div>
            <div class="card-grid">{cards}</div>
          </section>

          <section class="content-section" aria-labelledby="{escaped(locale)}-contact">
            <div class="contact-card"><div><p class="section-kicker">{escaped(labels['contactKicker'])}</p><h2 id="{escaped(locale)}-contact">{escaped(labels['contactTitle'])}</h2><p>{escaped(labels['contactBody'])}</p></div><a class="button primary" href="{escaped(mailto)}">{escaped(email)}</a></div>
          </section>
          <a class="page-link" href="../privacy/#{escaped(locale)}">{escaped(privacy_title)} <span aria-hidden="true">{arrow}</span></a>
        </article>"""


def page_shell(content: dict, *, page: str, canonical: str, title: str, description: str,
               document_title: str, panels: str) -> str:
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
    return f"""<!doctype html>
<html lang="ko" dir="ltr">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
    <meta name="description" content="{escaped(description)}">
    <meta name="color-scheme" content="light dark">
    <meta name="theme-color" media="(prefers-color-scheme: light)" content="#f4f4f8">
    <meta name="theme-color" media="(prefers-color-scheme: dark)" content="#0d0d11">
    <title>{escaped(document_title)}</title>
    <link rel="canonical" href="{canonical}">
    <link rel="icon" type="image/png" href="../assets/app-icon.png">
    <link rel="apple-touch-icon" href="../assets/app-icon.png">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="DoseWeek">
    <meta property="og:title" content="{escaped(title)}">
    <meta property="og:description" content="{escaped(description)}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:image" content="{SOCIAL_IMAGE}">
    <meta property="og:image:alt" content="DoseWeek app icon">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{escaped(title)}">
    <meta name="twitter:description" content="{escaped(description)}">
    <meta name="twitter:image" content="{SOCIAL_IMAGE}">
    <meta name="twitter:image:alt" content="DoseWeek app icon">
    <link rel="stylesheet" href="../assets/site.css">
    <script src="../assets/language.js" defer></script>
  </head>
  <body data-platform="ios" data-page="{escaped(page)}">
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


def rendered_support(content: dict) -> str:
    validate(content)
    panels = "\n\n".join(
        support_panel(locale, content["locales"][locale], content["bundleVersion"],
                      content["supportEmail"])
        for locale in content["localeOrder"]
    )
    return page_shell(
        content, page="support", canonical=SUPPORT_CANONICAL, title=SUPPORT_TITLE,
        description=SUPPORT_DESCRIPTION,
        document_title=f"DoseWeek — {content['locales']['ko']['support']['labels']['title']}",
        panels=panels,
    )


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
    pages = {PAGE_PATH: rendered(content), SUPPORT_PATH: rendered_support(content)}
    if arguments.catalog:
        catalog_parity(content, arguments.catalog.resolve())

    if arguments.check:
        for path, page in pages.items():
            assert path.is_file(), f"missing generated page {path.relative_to(ROOT)}"
            assert path.read_text(encoding="utf-8") == page, (
                f"stale {path.relative_to(ROOT)}; rerun render_ios.py"
            )
        suffix = " and app-catalog parity" if arguments.catalog else ""
        print(f"OK: iOS privacy and support pages ({len(content['locales'])} locales){suffix}")
        return

    for path, page in pages.items():
        path.write_text(page, encoding="utf-8")
    print(f"Rendered privacy/index.html and support/index.html from {CONTENT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
