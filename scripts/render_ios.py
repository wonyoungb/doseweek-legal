#!/usr/bin/env python3
"""Render iOS policy/support from the website-owned docs/ios-content.json.

Apps retain required consent and minimum instructions; full website policies are no longer
copied into app catalogs. --catalog is an explicit legacy comparison for historical inputs,
not the current website release gate.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

from site_assets import script_path, stylesheet_path
from help_navigation import support_start
import locale_pages
import render_terms
import privacy_legal
import render_us_health

import legal_release
from legal_release import (
    CURRENT_IOS_EFFECTIVE_DATE,
    expected_effective_date,
    missing_food_attributions,
)


ROOT = Path(__file__).resolve().parents[1]
SITE_BASE = "https://doseweek-legal.wonyoungchoi.dev/"
CONTENT_PATH = ROOT / "docs/ios-content.json"
PAGE_PATH = ROOT / "privacy/index.html"
SUPPORT_PATH = ROOT / "support/index.html"
SUPPORT_CANONICAL = f"{SITE_BASE}support/"
SUPPORT_TITLE = "DoseWeek Support"
SUPPORT_DESCRIPTION = (
    "Getting started with DoseWeek, and help with records, Apple Health, notifications, "
    "encrypted backups, plaintext exports, App Lock, on-device AI, meals, record import, the "
    "Plus subscription and ads."
)
RELEASED_FAQ = [
    "storage", "health", "notifications", "backup", "exports", "ai", "applock", "deletion",
]
BUGFIX_CANDIDATE_FAQ = ["dates", "edit", "past", "health", "sites"]
SECOND_RELEASE_FAQ = ["meals", "dates", "charts", "calendar", "backup", "devices", "import"]
# Monetization candidate (owner instruction 2026-09-29): free download with ads, Plus subscription.
# Anchors are #<locale>-plus-<key>; each answer has two paragraphs.
PLUS_FAQ = ["free", "features", "manage", "ads", "earlier", "adprivacy"]
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
    "access, user-directed encrypted backups, optional calendar sync, ads in the free version "
    "and Plus purchases."
)
LOCALE_ORDER = [
    "ko", "en", "ja", "de", "fr", "es", "it", "nl", "pt-PT", "pl", "sv", "hi",
    "pt-BR", "ar", "zh-Hans", "zh-Hant", "tr",
]
SECTION_IDS = [
    "storage", "health", "backups", "notifications", "tracking", "deletion", "contact", "ai",
    "calendar", "meals", "ads", "purchases", "next-release",
]
CANDIDATE_SECTION_ID = "next-release"
# Paragraph strings per section (default 1). The monetization candidate (2026-09-29) adds a
# leading analytics-scope paragraph to "tracking" and a Plus/subscription paragraph to
# "deletion" as separate strings, so the existing localized text stays untouched; the 1.0.5
# candidate section keeps its six paragraphs.
SECTION_PARAGRAPHS = {"tracking": 2, "deletion": 2, CANDIDATE_SECTION_ID: 6}
# Tokens every locale keeps in the monetization sections (names are not translated). The ads
# section also lists the overseas-transfer particulars of the ad SDKs as the analytics section does
# (review finding 14, 2026-09-29): recipient, contact, countries and Google's own purposes.
ADS_TRANSFER_TOKENS = (
    "Google LLC", "Google Ireland Limited", "https://policies.google.com/privacy",
    "https://datacenters.google/locations/",
    "https://policies.google.com/technologies/partner-sites",
)
SECTION_TOKENS = {
    "ads": ("AdMob", "UMP", "IDFA", *ADS_TRANSFER_TOKENS),
    "purchases": ("App Store", "Plus"),
}
# Legacy catalog parity compares the pre-monetization paragraph of each section.
LEGACY_PARAGRAPH_INDEX = {"tracking": 1}
# Owner decision IOS-VERSION-104-20260917: the pending 1.0.4 (build 15) review is cancelled and the
# stage-2 release ships as iOS 1.0.5. Owner decision 2026-09-24: these features ship, so the FAQ
# carries no pre-release notice; each of the twelve answers added for 1.0.5 opens with a one-line
# version scope ("available in" / "this applies to" DoseWeek iOS 1.0.5 and later), and the last
# section (13 since the monetization candidate added sections 11 and 12) describes what 1.0.5 adds. The page eyebrow and footer carry the version too. No scope line names
# a build: the store build number is chosen for the final artifact. Build planning and upload state
# live in the map.
CANDIDATE_VERSION = "1.0.5"
PAGE_VERSION = "1.0.5"
CATALOG_KEYS = {
    "storage": 1, "health": 2, "backups": 3, "notifications": 4, "tracking": 5,
    "deletion": 6, "contact": 7, "ai": 8, "calendar": 9, "meals": 10,
}


def escaped(value: object) -> str:
    return html.escape(str(value), quote=True)


def paragraph_blocks(value: str) -> list[str]:
    """Split one source string into its blank-line ("\\n\\n") separated display paragraphs.

    Sources keep one string per policy section or FAQ answer; each block renders as its own <p>.
    A single "\\n" inside a block is left in the block; privacy_paragraph renders it as <br>.
    """
    return value.split("\n\n")


def breakable_url(safe_url: str) -> str:
    """Link text for a long URL: allow a line break after each path "/" (never inside "://")."""
    scheme, separator, rest = safe_url.partition("://")
    return scheme + separator + re.sub(r"/(?=.)", "/<wbr>", rest)


def privacy_paragraph(value: str) -> str:
    """Keep policy text escaped; link only the reviewed processor-source URLs.

    Link text is isolated left-to-right, so a trailing "/" stays at the end of the URL in RTL text.

    A single "\\n" left inside a block is a line break within that paragraph (the contact
    sentence and its email address), so it renders as <br>.
    """
    rendered = escaped(value)
    for url in (
        "https://privacy.google.com/businesses/processorsupport",
        "https://datacenters.google/locations/",
        "https://business.safety.google/adssubprocessors/",
        "https://business.safety.google/adsprocessorterms/",
        "https://policies.google.com/privacy",
        "https://policies.google.com/technologies/partner-sites",
    ):
        safe_url = escaped(url)
        rendered = rendered.replace(
            safe_url,
            f'<a href="{safe_url}"><bdi dir="ltr">{breakable_url(safe_url)}</bdi></a>',
        )
    return rendered.replace("\n", "<br>")


def validate(content: dict) -> None:
    assert set(content) == {
        "schemaVersion", "platform", "bundleVersion", "effectiveDate", "supportEmail",
        "localeOrder", "locales", "legalReadiness", "representatives", "marketAvailability",
    }
    privacy_legal.validate_readiness(content)
    assert content["schemaVersion"] == 1
    assert content["platform"] == "ios"
    assert content["bundleVersion"] in (PAGE_VERSION, *legal_release.NEXT_VERSIONS)
    # An explicit unpublished 1.0.6 render has no invented effective date; the publication
    # build carries the owner's date.
    if content["bundleVersion"] in legal_release.NEXT_VERSIONS:
        assert content["effectiveDate"] in (None, legal_release.PUBLISHED_EFFECTIVE_DATE)
    else:
        # Live label (1.0.5): the base date, or the owner's date in the publication build,
        # which promises no iOS version number while App Store work is on hold.
        assert content["effectiveDate"] in (expected_effective_date(CURRENT_IOS_EFFECTIVE_DATE),
                                            legal_release.PUBLISHED_EFFECTIVE_DATE)
    assert content["supportEmail"] == "wonyoung@wonyoungchoi.dev"
    assert content["localeOrder"] == LOCALE_ORDER
    assert list(content["locales"]) == LOCALE_ORDER

    for locale, entry in content["locales"].items():
        locale_copy = json.dumps(entry, ensure_ascii=False)
        # ASCII letter boundaries catch shortened store names beside CJK text and in
        # hyphenated token names while keeping Google sign-in disclosures available.
        assert not re.search(r'(?<![A-Za-z])(?:Android|Google\s+Play|Play)(?![A-Za-z])',
                             locale_copy, flags=re.IGNORECASE), (
            f'{locale}: iOS policy/help copy must use neutral references to other platforms/stores'
        )
        assert set(entry) == {"languageName", "direction", "common", "privacy", "support"}, locale
        validate_support(locale, entry["support"])
        if content["bundleVersion"] == "1.0.6":
            # 1.0.6 ships the AI record assistant, which a server processes with a third-party
            # model. The 1.0.5 answer ends with "No Private Cloud Compute, server model, or
            # third-party model is used"; in 1.0.6 the answer must also say where the assistant
            # is processed. The served 1.0.5 source keeps its answer until 1.0.6 is published.
            assert "Google Cloud Vertex AI" in entry["support"]["released"]["ai"]["answers"][0], (
                f"{locale}: the 1.0.6 AI answer denies a server or third-party model without "
                "naming the server-processed AI record assistant"
            )
        assert entry["direction"] == ("rtl" if locale == "ar" else "ltr"), locale
        assert set(entry["common"]) == {"skipToContent", "contents", "supportLinkTitle"}, locale
        privacy = entry["privacy"]
        assert set(privacy) == {
            "title", "intro", "effectiveDate", "sections", "medicalDisclaimer", "legalSupplement",
        }, locale
        privacy_legal.validate_supplement(privacy["legalSupplement"], locale)
        assert set(privacy["medicalDisclaimer"]) == {
            "title", "body", "notAMedicalDevice",
        }, locale
        assert [section["id"] for section in privacy["sections"]] == SECTION_IDS, locale
        for number, section in enumerate(privacy["sections"], start=1):
            assert set(section) == {"id", "title", "paragraphs"}, f"{locale}:{section['id']}"
            assert section["title"].startswith(f"{number}. "), (
                f"{locale}:{section['id']} title must start with its number {number}."
            )
            expected = SECTION_PARAGRAPHS.get(section["id"], 1)
            assert len(section["paragraphs"]) == expected, f"{locale}:{section['id']}"
            for paragraph in section["paragraphs"]:
                assert isinstance(paragraph, str) and paragraph.strip(), (
                    f"{locale}:{section['id']}"
                )
        by_id = {section["id"]: section for section in privacy["sections"]}
        for section_id, tokens in SECTION_TOKENS.items():
            for token in tokens:
                assert token in by_id[section_id]["paragraphs"][0], (
                    f"{locale}: section {section_id} is missing {token!r}"
                )
        candidate = by_id[CANDIDATE_SECTION_ID]
        assert candidate is privacy["sections"][-1] and candidate["title"].startswith(
            f"{len(SECTION_IDS)}. "
        ), f"{locale}: candidate section stays last, after the app policy sections"
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
        # the bundled food data ships in this release, so its attribution lines are verbatim
        assert not missing_food_attributions(candidate["paragraphs"][4]), (
            f"{locale}: candidate food data paragraph is missing the attribution "
            f"{missing_food_attributions(candidate['paragraphs'][4])[0]!r}"
        )
        for string in (
            entry["languageName"], entry["common"]["skipToContent"],
            entry["common"]["contents"], entry["common"]["supportLinkTitle"],
            privacy["title"], privacy["intro"], privacy["effectiveDate"],
        ):
            assert isinstance(string, str) and string.strip(), locale


def faq_items(support: dict) -> dict[str, dict]:
    """FAQ items by their anchor suffix: faq-<key>, candidate-<key>, candidate2-<key>, plus-<key>."""
    return {
        **{f"faq-{key}": support["released"][key] for key in RELEASED_FAQ},
        **{f"candidate-{key}": support["candidate"][key] for key in BUGFIX_CANDIDATE_FAQ},
        **{f"candidate2-{key}": support["secondRelease"][key] for key in SECOND_RELEASE_FAQ},
        **{f"plus-{key}": support["plus"][key] for key in PLUS_FAQ},
    }


def guide_steps(locale: str, support: dict) -> list[tuple[str, str, str, str]]:
    """The getting-started steps as (title, body, href, link text); each links to its FAQ answer."""
    items = faq_items(support)
    return [
        (step["title"], step["body"], f"#{locale}-{step['link']}", items[step["link"]]["question"])
        for step in support["guide"]["steps"]
    ]


def validate_support(locale: str, support: dict) -> None:
    assert set(support) == {
        "labels", "guide", "safetyCards", "released", "candidate", "secondRelease", "plus",
    }, locale
    assert set(support["guide"]) == {"steps"} and len(support["guide"]["steps"]) == 6, (
        f"{locale}: the getting-started guide has six steps"
    )
    for index, step in enumerate(support["guide"]["steps"], start=1):
        assert set(step) == {"title", "body", "link"}, f"{locale}: guide step {index}"
        assert all(isinstance(step[key], str) and step[key].strip() for key in step), (
            f"{locale}: guide step {index}"
        )
        assert step["link"] in faq_items(support), f"{locale}: guide step {index} links to no FAQ"
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
        ("plus", PLUS_FAQ, 2),
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
    # every answer added for 1.0.5 opens with a version-scope line that names the version
    for key in BUGFIX_CANDIDATE_FAQ:
        notice = support["candidate"][key]["answers"][0]
        assert f"iOS {CANDIDATE_VERSION}" in notice and "build" not in notice.lower(), (
            f"{locale}: bugfix-candidate {key} must name iOS {CANDIDATE_VERSION}, without a build"
        )
    for key in SECOND_RELEASE_FAQ:
        notice = support["secondRelease"][key]["answers"][0]
        assert f"iOS {PAGE_VERSION}" in notice and "build" not in notice.lower(), (
            f"{locale}: second-release {key} must name iOS {PAGE_VERSION}, without a build"
        )
    ai_answer = support["released"]["ai"]["answers"][0]
    assert ai_answer.count(AI_MODEL_TOKEN) == 1, f"{locale}: AI answer must name the model once"
    assert "Private Cloud Compute" in ai_answer, locale
    assert "AES-256-GCM" in support["released"]["backup"]["answers"][0], locale
    assert "<" not in json.dumps(support, ensure_ascii=False), (
        f"{locale}: support copy is plain text; markup is added by the renderer"
    )


def catalog_parity(content: dict, catalog_path: Path) -> None:
    """Legacy diagnostic for a historical policy and its matching app catalog."""
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
            if section["id"] not in CATALOG_KEYS:
                continue  # the 1.0.5 candidate and the monetization sections have no app key
            number = CATALOG_KEYS[section["id"]]
            assert section["title"] == value(f"privacy.section{number}.title", locale), (
                f"{locale}: privacy.section{number}.title does not match the app catalog"
            )
            legacy = section["paragraphs"][LEGACY_PARAGRAPH_INDEX.get(section["id"], 0)]
            assert legacy == value(f"privacy.section{number}.body", locale), (
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
    toc += privacy_legal.toc(locale, privacy["legalSupplement"])
    toc += (
        f'<li><a href="#{escaped(locale)}-medical">'
        f'{escaped(privacy["medicalDisclaimer"]["title"])}</a></li>'
    )
    sections = "\n".join(
        f'              <section id="{escaped(locale)}-{escaped(section["id"])}" '
        f'class="policy-section"><h2'
        + (f' id="{escaped(locale)}-analytics-overseas-transfer" data-skip-target tabindex="-1"'
           if section["id"] == "tracking" else "")
        + f'>{escaped(section["title"])}</h2><div>'
        + "".join(
            f"<p>{privacy_paragraph(block)}</p>"
            for paragraph in section["paragraphs"]
            for block in paragraph_blocks(paragraph)
        )
        + "</div></section>"
        for section in privacy["sections"]
    )
    sections += "\n" + privacy_legal.sections_html(locale, privacy["legalSupplement"])
    disclaimer = privacy["medicalDisclaimer"]
    date = (
        f'<p class="date"><time datetime="{escaped(effective_date)}">'
        f'{escaped(privacy["effectiveDate"])}</time></p>' if effective_date else ""
    )
    return f"""        <article id="{escaped(locale)}" class="language-panel" lang="{escaped(locale)}" dir="{escaped(direction)}" data-language="{escaped(locale)}" data-document-title="{escaped(document_title)}" aria-labelledby="{escaped(locale)}-content">
          <header class="hero">
            <p class="eyebrow">DoseWeek · iOS {escaped(bundle_version)}</p>
            <h1 id="{escaped(locale)}-content" data-skip-target tabindex="-1">{escaped(privacy['title'])}</h1>
            <p class="hero-copy">{escaped(privacy['intro'])}</p>
            {date}
          </header>

          <div class="policy-layout">
            <nav class="policy-toc" aria-label="{escaped(entry['common']['contents'])}"><h2>{escaped(entry['common']['contents'])}</h2><ol>{toc}</ol></nav>
            <div class="policy-card">
{sections}
              <section id="{escaped(locale)}-medical" class="policy-section medical"><h2>{escaped(disclaimer['title'])}</h2><div><p>{escaped(disclaimer['body'])}</p><p>{escaped(disclaimer['notAMedicalDevice'])}</p></div></section>
            </div>
          </div>
          <a class="page-link" href="../support/#{escaped(locale)}">{escaped(entry['common']['supportLinkTitle'])} <span aria-hidden="true">{arrow}</span></a>
          {render_terms.page_link(locale, '../', direction)}
          {render_us_health.page_link(locale, '../', direction)}
        </article>"""


def faq_answer(text: str, locale: str) -> str:
    """Escape an answer and wrap the on-device model name in <code>, as the published page did."""
    escaped_text = escaped(text)
    escaped_text = escaped_text.replace(AI_MODEL_TOKEN, f"<code>{AI_MODEL_TOKEN}</code>")
    import_guide = "doseweek-legal.wonyoungchoi.dev/import/"
    return escaped_text.replace(
        import_guide,
        f'<a href="../import/#{escaped(locale)}"><bdi dir="ltr">{import_guide}</bdi></a>',
    )


def faq_details(locale: str, identifier: str, item: dict, candidate: bool) -> str:
    # `candidate` marks the twelve answers added for 1.0.5; since they ship, the rendered
    # markup no longer carries a release-status attribute (kept for callers and tests).
    del candidate
    answers = "".join(
        f"<p>{faq_answer(block, locale)}</p>"
        for answer in item["answers"]
        for block in paragraph_blocks(answer)
    )
    return (
        f'              <details id="{escaped(locale)}-{escaped(identifier)}">'
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
    for key in PLUS_FAQ:
        faq.append(faq_details(locale, f"plus-{key}", support["plus"][key], False))
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

          {support_start(locale, '../', '../import/', '../privacy/', privacy_title, guide_steps(locale, support))}

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
          {render_terms.page_link(locale, '../', direction)}
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
{locale_pages.alternate_links(page + "/")}
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
    <link rel="stylesheet" href="{stylesheet_path('../')}">
    <script src="{script_path('language.js', '../')}" defer></script>
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

    <footer class="site-footer site-shell"><span>© 2026 Wonyoung Labs</span><span>DoseWeek · iOS {escaped(content['bundleVersion'])}</span></footer>
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
{locale_pages.alternate_links("privacy/")}
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

    <footer class="site-footer site-shell"><span>© 2026 Wonyoung Labs</span><span>DoseWeek · iOS {escaped(content['bundleVersion'])}</span></footer>
  </body>
</html>
"""


def rendered_locale_pages(content: dict) -> dict[Path, str]:
    """/<locale>/privacy/ and /<locale>/support/: the hash pages' panels, one language each.

    Descriptions reuse existing copy: the policy intro and the support lead.
    """
    validate(content)
    names = {locale: entry["languageName"] for locale, entry in content["locales"].items()}
    footer = (
        '<footer class="site-footer site-shell"><span>© 2026 Wonyoung Labs</span>'
        f'<span>DoseWeek · iOS {escaped(content["bundleVersion"])}</span></footer>'
    )
    pages = {}
    for locale in content["localeOrder"]:
        entry = content["locales"][locale]
        shared = dict(
            locale=locale, names=names, icon="assets/app-icon.png", social_image=SOCIAL_IMAGE,
            image_alt="DoseWeek app icon", brand_href="../", brand_aria="DoseWeek",
            brand_label="DoseWeek", skip_label=entry["common"]["skipToContent"],
            skip_target=f"{locale}-content", footer=footer,
        )
        pages[locale_pages.page_path("privacy/", locale)] = locale_pages.locale_page(
            route="privacy/", description=entry["privacy"]["intro"],
            panel=panel(locale, entry, content["bundleVersion"], content["effectiveDate"]),
            body_attributes=' data-platform="ios" data-page="privacy"', **shared,
        )
        pages[locale_pages.page_path("support/", locale)] = locale_pages.locale_page(
            route="support/", description=entry["support"]["labels"]["lead"],
            panel=support_panel(locale, entry, content["bundleVersion"], content["supportEmail"]),
            body_attributes=' data-platform="ios" data-page="support"', **shared,
        )
    return pages


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--catalog",
        type=Path,
        help="legacy diagnostic: compare a matching historical app policy; not a current website gate",
    )
    arguments = parser.parse_args()

    content = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
    pages = {PAGE_PATH: rendered(content), SUPPORT_PATH: rendered_support(content),
             **rendered_locale_pages(content)}
    if arguments.catalog:
        catalog_parity(content, arguments.catalog.resolve())

    locale_pages.write_pages(pages, arguments.check, "rerun render_ios.py")
    if arguments.check:
        suffix = " and app-catalog parity" if arguments.catalog else ""
        print(f"OK: iOS privacy and support pages ({len(content['locales'])} locales) "
              f"and {len(pages) - 2} language pages{suffix}")
        return
    print(f"Rendered privacy/index.html, support/index.html and {len(pages) - 2} language pages "
          f"from {CONTENT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
