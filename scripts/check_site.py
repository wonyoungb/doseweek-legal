#!/usr/bin/env python3
"""Dependency-free structural checks for the DoseWeek static pages."""

from __future__ import annotations

import argparse
import copy
import json
import io
import re
import unittest
import xml.etree.ElementTree as ET
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

from site_assets import script_path, stylesheet_path
from urllib.parse import unquote, urlsplit

import korean_tone
import legal_release
import locale_pages
import account_sync_candidate
import render_ios
import render_home
import render_terms
from render_android import rendered_pages, validate_catalog
from render_import import rendered as rendered_import, validate as validate_import


ROOT = Path(__file__).resolve().parents[1]
IOS_HTML_FILES = [ROOT / "index.html", ROOT / "support/index.html", ROOT / "privacy/index.html"]
ANDROID_HTML_FILES = [
    ROOT / "android/index.html",
    ROOT / "android/support/index.html",
    ROOT / "android/privacy/index.html",
]
IMPORT_HTML_FILES = [ROOT / "import/index.html"]
TERMS_HTML_FILES = [ROOT / "terms/index.html"]
HTML_FILES = IOS_HTML_FILES + ANDROID_HTML_FILES + IMPORT_HTML_FILES + TERMS_HTML_FILES
ANDROID_LANGUAGES = [
    "ko", "en", "ja", "de", "fr", "es", "it", "nl", "pt-PT", "pl", "sv", "hi",
    "pt-BR", "ar", "zh-Hans", "zh-Hant", "tr",
]
# The iOS privacy policy is generated for the same seventeen locales the apps ship.
ALL_LANGUAGES = ANDROID_LANGUAGES
SECOND_RELEASE_TOPICS = [
    "meals", "dates", "charts", "calendar", "backup", "devices", "import",
]
SITE_BASE = "https://doseweek-legal.wonyoungchoi.dev/"
SOCIAL_IMAGE = f"{SITE_BASE}assets/app-icon.png"
ANDROID_SOCIAL_IMAGE = f"{SITE_BASE}assets/android-app-icon.png"
POLICY_SOURCE_LINKS = {
    "https://privacy.google.com/businesses/processorsupport",
    "https://datacenters.google/locations/",
    "https://business.safety.google/adssubprocessors/",
    "https://business.safety.google/adsprocessorterms/",
    # ad SDK overseas-transfer particulars (review finding 14, 2026-09-29)
    "https://policies.google.com/privacy",
    "https://policies.google.com/technologies/partner-sites",
}
# The hash pages and the per-language pages of both privacy policies may link the processor sources.
PRIVACY_PAGES = {
    locale_pages.page_path(route, locale).resolve()
    for route in ("privacy/", "android/privacy/") for locale in (None, *locale_pages.LOCALES)
}
# The Terms pages (hash page and language pages) may link Apple's standard EULA, deliberately
# added 2026-09-29 for the iOS subscription terms; no other page may.
TERMS_SOURCE_LINKS = set(render_terms.LINKED_URLS)
TERMS_PAGES = {
    locale_pages.page_path("terms/", locale).resolve() for locale in (None, *locale_pages.LOCALES)
}
# Monetization copy (owner instruction 2026-09-29) must not reuse the 1.0.5 claims or state an
# unapproved price or trial on any page, in any language panel.
MONETIZATION_OVERCLAIMS = (
    "we collect no data", "collects no data", "no data is collected", "show no ads",
    "No ads;", "one-time purchase", "no in-app purchase", "free trial", "KRW", "₩",
    "2,900", "19,900", "광고 없음 ·",
    # release builds verify Plus only through the purchase-verification server (finding 31)
    "checks the signed purchase data",
)
SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
XHTML_NS = "{http://www.w3.org/1999/xhtml}"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.panel_languages: list[str] = []
        self.panel_declared_languages: dict[str, str | None] = {}
        self.panel_directions: dict[str, str | None] = {}
        self.language_links: list[tuple[str, str | None, str | None]] = []
        self.language_skips: list[str] = []
        self.references: list[tuple[str, str]] = []
        self.metadata: dict[str, str] = {}
        self.link_relations: dict[str, str] = {}
        self.summary_markers: list[list[str | None]] = []
        self._summary_marker_values: list[str | None] | None = None
        self.text: list[str] = []
        self.html_attributes: dict[str, str | None] = {}
        self.alternates: list[tuple[str, str]] = []
        self.title = ""
        self._in_title = False
        self.panel_classes: list[set[str]] = []
        self.panel_titles: dict[str, str | None] = {}
        self.navigation: list[dict[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        element_id = values.get("id")
        if element_id:
            self.ids.append(element_id)

        classes = set((values.get("class") or "").split())
        if tag == "html":
            self.html_attributes = values
        elif tag == "title":
            self._in_title = True
        if tag == "a" and "language-link" in classes:
            self.navigation.append(values)
        if tag == "meta":
            key = values.get("property") or values.get("name")
            content = values.get("content")
            if key and content:
                self.metadata[key] = content

        if tag == "link":
            href = values.get("href")
            for relation in (values.get("rel") or "").split():
                if href:
                    self.link_relations[relation] = href
            if "alternate" in (values.get("rel") or "").split() and values.get("hreflang"):
                self.alternates.append((values["hreflang"], href or ""))

        if tag == "summary":
            assert self._summary_marker_values is None, "nested summary elements are invalid"
            self._summary_marker_values = []
        elif self._summary_marker_values is not None and "summary-symbol" in classes:
            self._summary_marker_values.append(values.get("aria-hidden"))

        if "language-panel" in classes:
            language = values.get("data-language")
            if language:
                self.panel_languages.append(language)
                self.panel_declared_languages[language] = values.get("lang")
                self.panel_directions[language] = values.get("dir")
                self.panel_classes.append(classes)
                self.panel_titles[language] = values.get("data-document-title")

        language_link = values.get("data-language-link")
        if language_link:
            self.language_links.append((language_link, values.get("aria-current"), values.get("lang")))
        language_skip = values.get("data-language-skip")
        if language_skip:
            self.language_skips.append(language_skip)

        for attribute in ("href", "src"):
            reference = values.get(attribute)
            if reference:
                self.references.append((attribute, reference))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag == "summary" and self._summary_marker_values is not None:
            self.summary_markers.append(self._summary_marker_values)
            self._summary_marker_values = None

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        stripped = " ".join(data.split())
        if stripped:
            self.text.append(stripped)


def parse(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser


def local_target(source: Path, reference: str, *, attribute: str | None = None) -> tuple[Path, str] | None:
    split = urlsplit(reference)
    if split.scheme or split.netloc:
        if split.scheme == "mailto":
            return None
        if (
            attribute == "href"
            and source.resolve() in PRIVACY_PAGES
            and reference in POLICY_SOURCE_LINKS
        ):
            # Deliberate navigation to reviewed processor evidence, never a remote asset.
            return None
        if (
            attribute == "href"
            and source.resolve() in TERMS_PAGES
            and reference in TERMS_SOURCE_LINKS
        ):
            # Deliberate navigation to Apple's standard EULA from the Terms, never a remote asset.
            return None
        if reference.startswith(SITE_BASE):
            relative_path = unquote(split.path.removeprefix("/doseweek-legal/").lstrip("/"))
            target = (ROOT / relative_path).resolve()
            if target.is_dir() or split.path.endswith("/"):
                target /= "index.html"
            return target, unquote(split.fragment)
        raise AssertionError(f"{source.relative_to(ROOT)}: external reference {reference!r}")

    target = source if not split.path else (source.parent / unquote(split.path)).resolve()
    if target.is_dir() or split.path.endswith("/"):
        target /= "index.html"
    return target, unquote(split.fragment)


def catalog_check(catalog_path: Path, privacy_text: str) -> None:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))["strings"]
    keys = ["privacy.title", "privacy.intro", "privacy.effectiveDate"]
    for number in range(1, 11):
        keys.extend((f"privacy.section{number}.title", f"privacy.section{number}.body"))
    keys.extend(("privacy.medical.title", "privacy.medical.body", "common.notAMedicalDevice"))

    for key in keys:
        assert key in catalog, f"catalog: missing source-of-truth key {key!r}"
        for language in ANDROID_LANGUAGES:
            value = catalog[key]["localizations"][language]["stringUnit"]["value"]
            normalized = " ".join(value.split())
            assert normalized in privacy_text, (
                f"privacy/index.html: {key} ({language}) does not match the app catalog"
            )


def android_claims_text(path: Path) -> str:
    """Exclude only verified navigation to the other platform, not Android feature claims."""
    source = path.read_text(encoding="utf-8")
    if path == ROOT / "android/index.html":
        home = json.loads((ROOT / "docs/home-content.json").read_text(encoding="utf-8"))
        seen: list[str] = []

        def platform_link(match: re.Match[str]) -> str:
            locale, title = match.group(1), unescape(match.group(2))
            assert locale in ALL_LANGUAGES and title == home[locale]["iosTitle"], (
                "Android platform navigation must name the linked iOS home exactly"
            )
            seen.append(locale)
            return ""

        source = re.sub(
            r'<a class="help-platform" href="\.\./#([^"]+)">([^<]+) '
            r'<span aria-hidden="true">[←→]</span></a>',
            platform_link, source,
        )
        assert len(seen) == len(ALL_LANGUAGES) and set(seen) == set(ALL_LANGUAGES), (
            "Android home must keep one verified other-platform link per locale"
        )
    page = PageParser()
    page.feed(source)
    page.close()
    return " ".join(page.text)


def assert_css_minimum(css: str, selector: str, property_name: str, minimum: int) -> None:
    match = re.search(rf"{re.escape(selector)}\s*\{{(?P<body>[^}}]+)\}}", css)
    assert match, f"assets/site.css: missing {selector!r} rule"
    value = re.search(rf"{re.escape(property_name)}:\s*(\d+)px", match.group("body"))
    assert value and int(value.group(1)) >= minimum, (
        f"assets/site.css: {selector} must set {property_name} to at least {minimum}px"
    )


def android_guard_regression_check(catalog: dict[str, object]) -> None:
    def expect_rejected(candidate: dict[str, object], label: str) -> None:
        try:
            validate_catalog(candidate)
        except (AssertionError, KeyError, TypeError):
            return
        raise AssertionError(f"Android catalog guard failed to reject {label}")

    cjk_suffix = copy.deepcopy(catalog)
    cjk_suffix["locales"]["ja"]["home"]["intro"] += " iOS版"
    expect_rejected(cjk_suffix, "a prohibited iOS token with a CJK suffix")

    wrong_type = copy.deepcopy(catalog)
    wrong_type["locales"]["fr"]["privacy"]["sections"][3]["paragraphs"] = "oops"
    expect_rejected(wrong_type, "a string where backup paragraphs must be a list")

    missing_disclosure = copy.deepcopy(catalog)
    missing_disclosure["locales"]["fr"]["privacy"]["sections"][3]["paragraphs"] = [
        "placeholder",
        "placeholder",
        "placeholder",
        "placeholder",
    ]
    expect_rejected(missing_disclosure, "a localized backup section without AES-256-GCM")

    weakened_backup = copy.deepcopy(catalog)
    weakened_answer = weakened_backup["locales"]["fr"]["support"]["faq"][4]["answers"][0]
    weakened_backup["locales"]["fr"]["support"]["faq"][4]["answers"][0] = (
        weakened_answer
        .replace("fichier chiffré avec AES-256-GCM", "fichier AES-256-GCM")
        .replace("code de récupération distinct à haute entropie", "code")
    )
    expect_rejected(weakened_backup, "weakened encrypted/high-entropy backup wording")

    missing_version_scope = copy.deepcopy(catalog)
    scoped_answer = missing_version_scope["locales"]["ja"]["support"]["faq"][2]["answers"][0]
    missing_version_scope["locales"]["ja"]["support"]["faq"][2]["answers"][0] = (
        scoped_answer.replace("DoseWeek 1.0.5", "DoseWeek")
    )
    expect_rejected(missing_version_scope, "a localized AI/Health FAQ without version scope")

    weakened_emergency = copy.deepcopy(catalog)
    disclaimer = weakened_emergency["locales"]["es"]["privacy"]["medicalDisclaimer"]["body"]
    weakened_emergency["locales"]["es"]["privacy"]["medicalDisclaimer"]["body"] = (
        disclaimer.replace("servicios de emergencia locales", "servicios locales")
    )
    expect_rejected(weakened_emergency, "generic Spanish service wording in an emergency notice")

    ambiguous_antecedent = copy.deepcopy(catalog)
    decrypt_answer = ambiguous_antecedent["locales"]["es"]["support"]["faq"][4]["answers"][1]
    ambiguous_antecedent["locales"]["es"]["support"]["faq"][4]["answers"][1] = (
        decrypt_answer.replace("descifrar el archivo", "descifrarlo")
    )
    expect_rejected(ambiguous_antecedent, "an ambiguous Spanish decryption antecedent")

    missing_ad_sdk = copy.deepcopy(catalog)
    ads_section = missing_ad_sdk["locales"]["fr"]["privacy"]["sections"][4]
    assert ads_section["id"] == "ads", "the ads section follows backup at sections[4]"
    ads_section["paragraphs"] = [text.replace("AdMob", "SDK") for text in ads_section["paragraphs"]]
    expect_rejected(missing_ad_sdk, "a localized ads section that no longer names AdMob")

    withdrawn_badge = copy.deepcopy(catalog)
    withdrawn_badge["locales"]["en"]["home"]["featureBadges"][2] = "No ads; usage analytics is optional"
    expect_rejected(withdrawn_badge, "the withdrawn 'No ads' badge")

    unscoped_server = copy.deepcopy(catalog)
    unscoped_server["locales"]["en"]["support"]["intro"] = (
        "DoseWeek works without a DoseWeek account or a developer server, so support cannot "
        "remotely view or recover records on your device."
    )
    expect_rejected(unscoped_server, "an unscoped 'no developer server' support intro")

    spanish_word = copy.deepcopy(catalog)
    spanish_word["locales"]["es"]["home"]["intro"] += " datos propios"
    validate_catalog(spanish_word)
    print(
        "OK: Android catalog guard regressions reject CJK-suffixed iOS copy, wrong nested "
        "types, weakened backup/version/emergency wording, ambiguous Spanish decryption copy, "
        "an ads section without AdMob, the withdrawn 'No ads' badge and an unscoped "
        "'no developer server' claim, without rejecting Spanish propios"
    )


def korean_tone_check() -> str:
    """Run the Korean 해요체 self-tests, then require zero non-allow-listed violations."""
    suite = unittest.defaultTestLoader.loadTestsFromName("test_korean_tone")
    result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
    assert result.wasSuccessful() and result.testsRun, (
        f"scripts/test_korean_tone.py: {len(result.failures)} failures, {len(result.errors)} errors; "
        "run python3 -m unittest discover -s scripts -p test_korean_tone.py"
    )
    entries, files = korean_tone.load_entries()
    report = korean_tone.build_report(entries, files)
    first = report["violations"][:5]
    assert not report["violations"], (
        f"Korean tone: {report['counts']['total']} violations, e.g. "
        + "; ".join(f"{item['file']} {item['key']} [{item['rule']}] {item['sentence']}" for item in first)
        + "; run python3 scripts/korean_tone.py"
    )
    assert not report["allowlist"]["stale"], (
        f"scripts/korean_tone_allowlist.json: stale entries {report['allowlist']['stale']}"
    )
    return (f"Korean tone ({result.testsRun} self-tests, {report['scanned']['sentences']} sentences, "
            f"{report['allowlist']['suppressed']} allow-listed)")


def check_references(path: Path, page: PageParser, known: dict[Path, PageParser]) -> None:
    """Every local href/src resolves, including #fragments, from this page."""
    label = path.relative_to(ROOT)
    for attribute, reference in page.references:
        resolved = local_target(path, reference, attribute=attribute)
        if resolved is None:
            continue
        target, fragment = resolved
        assert target.exists(), f"{label}: broken {attribute}={reference!r}"
        if fragment and target.suffix == ".html":
            target_page = known.get(target.resolve()) or parse(target)
            assert fragment in target_page.ids, f"{label}: missing target for {reference!r}"


def panel_markup(source: str, locale: str, label: object) -> str:
    panels = re.findall(rf'<article id="{re.escape(locale)}"[^>]*>.*?</article>', source, flags=re.DOTALL)
    assert len(panels) == 1, f"{label}: expected one {locale} panel"
    return panels[0]


def check_language_pages(hash_pages: dict[Path, PageParser]) -> dict[Path, PageParser]:
    """/<locale>/<route>: one static panel per URL with its own language, canonical URL,
    alternates and navigation, and exactly the text of the hash page's panel."""
    language_pages: dict[Path, PageParser] = {}
    for route in locale_pages.ROUTES:
        hash_path = locale_pages.page_path(route).resolve()
        hash_source = hash_path.read_text(encoding="utf-8")
        descriptions = set()
        for locale in ALL_LANGUAGES:
            path = locale_pages.page_path(route, locale).resolve()
            label = path.relative_to(ROOT)
            assert path.is_file(), f"{label}: missing language page; rerun the renderers"
            source = path.read_text(encoding="utf-8")
            page = parse(path)
            language_pages[path] = page
            direction = "rtl" if locale == "ar" else "ltr"

            assert (page.html_attributes.get("lang"), page.html_attributes.get("dir")) == (locale, direction), (
                f"{label}: <html> must declare lang={locale} dir={direction}"
            )
            assert "data-locale-page" in page.html_attributes, f"{label}: missing data-locale-page"
            assert page.panel_languages == [locale], f"{label}: one {locale} panel per URL"
            assert page.panel_declared_languages == {locale: locale}, f"{label}: panel lang"
            assert page.panel_directions == {locale: direction}, f"{label}: panel direction"
            assert page.panel_classes == [{"language-panel", "is-active"}], (
                f"{label}: the panel must be visible without JavaScript (is-active)"
            )
            duplicates = sorted({item for item in page.ids if page.ids.count(item) > 1})
            assert not duplicates, f"{label}: duplicate IDs {duplicates}"

            canonical = locale_pages.page_url(route, locale)
            assert page.link_relations.get("canonical") == canonical, f"{label}: wrong canonical URL"
            assert page.metadata.get("og:url") == canonical, f"{label}: wrong og:url"
            assert page.alternates == locale_pages.alternates(route), (
                f"{label}: hreflang must list the 17 language pages and x-default of {route or '/'}"
            )
            title = page.panel_titles[locale]
            assert title and page.title == title, f"{label}: <title> must be the panel's document title"
            assert page.metadata.get("og:title") == title and page.metadata.get("twitter:title") == title, (
                f"{label}: social titles must match <title>"
            )
            description = page.metadata.get("description")
            assert description and description == page.metadata.get("og:description") == (
                page.metadata.get("twitter:description")
            ), f"{label}: descriptions must be present and equal"
            descriptions.add(description)
            for key in ("og:image", "og:image:alt", "twitter:image", "twitter:image:alt"):
                assert page.metadata.get(key), f"{label}: missing {key}"

            assert page.language_links == [] and page.language_skips == [], (
                f"{label}: a language page has no hash switch (data-language-link/skip)"
            )
            navigation = [link.get("hreflang") for link in page.navigation]
            assert navigation == ALL_LANGUAGES, f"{label}: language links must follow {ALL_LANGUAGES}"
            assert [link.get("lang") for link in page.navigation] == ALL_LANGUAGES, f"{label}: link lang"
            targets = [(path.parent / (link.get("href") or "")).resolve() / "index.html" for link in page.navigation]
            assert targets == [locale_pages.page_path(route, other).resolve() for other in ALL_LANGUAGES], (
                f"{label}: each language link must open the same page in that language"
            )
            current = [link.get("hreflang") for link in page.navigation if link.get("aria-current") == "true"]
            assert current == [locale], f"{label}: aria-current must mark {locale} only"
            assert script_path("language.js") in source and stylesheet_path() in source, (
                f"{label}: stale language.js or site.css version"
            )

            # Same localized text as the hash page; only the static class and download paths differ.
            panel = panel_markup(source, locale, label).replace(
                'class="language-panel is-active"', 'class="language-panel"', 1
            )
            panel = re.sub(
                r'href="\.\./\.\./import/((?:prompt|format)\.[^"/]+\.md|draft[^"/]*\.json)"', r'href="\1"', panel
            )
            assert panel == panel_markup(hash_source, locale, hash_path.relative_to(ROOT)), (
                f"{label}: panel differs from the {locale} panel of {hash_path.relative_to(ROOT)}"
            )
        assert len(descriptions) == len(ALL_LANGUAGES), (
            f"{route or '/'}: every language page needs its own localized description"
        )
    known = {**hash_pages, **language_pages}
    for path, page in language_pages.items():
        check_references(path, page, known)
    return language_pages


def check_hreflang_clusters(all_pages: dict[Path, PageParser]) -> int:
    """Each route's 18 pages list the same alternates, including themselves, and x-default."""
    clusters: dict[str, tuple[str, list[tuple[str, str]]]] = {}
    for route in locale_pages.ROUTES:
        for locale in (None, *ALL_LANGUAGES):
            page = all_pages[locale_pages.page_path(route, locale).resolve()]
            clusters[locale_pages.page_url(route, locale)] = (locale or "x-default", page.alternates)
    for url, (code, alternates) in clusters.items():
        codes = [item for item, _ in alternates]
        assert len(codes) == len(set(codes)), f"{url}: duplicate hreflang values"
        assert "x-default" in codes, f"{url}: missing hreflang x-default"
        assert (code, url) in alternates, f"{url}: must list itself as hreflang {code}"
        for other_code, other_url in alternates:
            assert other_url in clusters, f"{url}: hreflang {other_code} points to {other_url}, not a page"
            own, back = clusters[other_url]
            assert own == other_code, f"{url}: hreflang {other_code} points to the {own} page {other_url}"
            assert (code, url) in back, f"{other_url} does not link back to {url} as hreflang {code}"
    return len(clusters)


def check_sitemap(all_pages: dict[Path, PageParser]) -> int:
    """sitemap.xml lists every page once, each with the same alternates as the page itself."""
    text = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    assert text == locale_pages.sitemap_xml(), "sitemap.xml is stale; run scripts/render_sitemap.py"
    root = ET.fromstring(text)
    assert root.tag == f"{SITEMAP_NS}urlset", "sitemap.xml: not a sitemap urlset"
    entries: dict[str, list[tuple[str | None, str | None]]] = {}
    for url in root.findall(f"{SITEMAP_NS}url"):
        loc = url.findtext(f"{SITEMAP_NS}loc")
        assert loc and loc not in entries, f"sitemap.xml: missing or repeated <loc> {loc!r}"
        entries[loc] = [
            (link.get("hreflang"), link.get("href"))
            for link in url.findall(f"{XHTML_NS}link") if link.get("rel") == "alternate"
        ]
    expected = {
        locale_pages.page_url(route, locale): locale_pages.page_path(route, locale).resolve()
        for route in locale_pages.ROUTES for locale in (None, *ALL_LANGUAGES)
    }
    missing, extra = sorted(set(expected) - set(entries)), sorted(set(entries) - set(expected))
    assert not missing and not extra, f"sitemap.xml: missing {missing[:3]}, extra {extra[:3]}"
    for loc, links in entries.items():
        assert links == all_pages[expected[loc]].alternates, (
            f"sitemap.xml: alternates of {loc} differ from the page's hreflang links"
        )
    assert f"Sitemap: {SITE_BASE}sitemap.xml" in (ROOT / "robots.txt").read_text().splitlines(), (
        "robots.txt must name the sitemap"
    )
    return len(entries)


def main() -> None:
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "--catalog",
        type=Path,
        help="legacy diagnostic: compare a matching historical iOS full-policy catalog; not a current website gate",
    )
    argument_parser.add_argument(
        "--android-content",
        type=Path,
        default=ROOT / "docs/android-content.candidate.json",
        help="Android website source (defaults to docs/android-content.candidate.json)",
    )
    argument_parser.add_argument(
        "--release",
        action="store_true",
        help="publish gate: also require the owner to have filled "
        "legal_release.NEXT_RELEASE_EFFECTIVE_DATE and replaced legal_release.RELEASE_PLACEHOLDERS",
    )
    arguments = argument_parser.parse_args()
    if arguments.release:
        legal_release.require_release_date()
        account_sync_candidate.require_release_ready()
        for relative in ("docs/ios-content.json", "docs/android-content.candidate.json",
                         "docs/terms-content.json"):
            left = legal_release.release_placeholders((ROOT / relative).read_text(encoding="utf-8"))
            assert not left, f"{relative}: release placeholder still present: {left[0]!r}"
    # Owner decision 2026-10-01: sign-in is Apple and Google only. No live or candidate
    # sign-in-bearing legal source may name the dropped Kakao login.
    retired = account_sync_candidate.retired_provider_errors()
    assert not retired, (
        f"retired sign-in provider named in {len(retired)} legal source fields, e.g. {retired[:3]}; "
        "sign-in is Apple and Google only (owner decision 2026-10-01)"
    )
    # Lane LEGAL-STORE (2026-10-02): the staged 1.0.6 account/sync candidate must name the
    # operator, the AWS Lightsail ap-northeast-2 server, the Cloudflare overseas transfer and the
    # D8/backup 30/7-day rules in every locale, and its staged privacy sources may not keep a
    # "listed before release" server placeholder.
    hosting = account_sync_candidate.hosting_retention_errors()
    assert not hosting, (
        f"account/sync candidate misses server facts in {len(hosting)} places, e.g. {hosting[:3]}"
    )
    import render_account_sync
    staged_left = account_sync_candidate.staged_placeholder_errors(
        render_account_sync.integrated_sources()
    )
    assert not staged_left, (
        f"staged 1.0.6 privacy sources keep {len(staged_left)} release placeholders, e.g. {staged_left[:2]}"
    )
    # Every locale carries the release placeholders exactly as en does, so a translated
    # placeholder is registered (and caught by --release) and no locale keeps one after en changes.
    for relative in ("docs/ios-content.json", "docs/android-content.candidate.json",
                     "docs/terms-content.json"):
        drift = legal_release.placeholder_parity_errors(
            json.loads((ROOT / relative).read_text(encoding="utf-8"))
        )
        assert not drift, (
            f"{relative}: release placeholders differ from en ({'; '.join(drift)}); register the "
            "translated sentence in legal_release.RELEASE_PLACEHOLDERS or replace it with en"
        )
    # One purchase-verification server: both purchase sections keep the same pending (or written)
    # location, operator and retention sentences in every locale (review finding 26).
    purchase_drift = legal_release.purchase_placeholder_parity_errors(
        json.loads((ROOT / "docs/ios-content.json").read_text(encoding="utf-8")),
        json.loads((ROOT / "docs/android-content.candidate.json").read_text(encoding="utf-8")),
    )
    assert not purchase_drift, (
        "iOS and Android purchase sections describe the same server but differ: "
        + "; ".join(purchase_drift)
    )

    assert (ROOT / "index.html").read_text() == render_home.rendered(), "index.html is stale; rerun render_home.py"
    pages = {path.resolve(): parse(path) for path in HTML_FILES}

    expected_metadata = {
        (ROOT / "index.html").resolve(): (
            SITE_BASE, "assets/app-icon.png", SOCIAL_IMAGE, ALL_LANGUAGES,
            ALL_LANGUAGES,
        ),
        (ROOT / "support/index.html").resolve(): (
            f"{SITE_BASE}support/", "../assets/app-icon.png", SOCIAL_IMAGE,
            ALL_LANGUAGES, ALL_LANGUAGES,
        ),
        (ROOT / "privacy/index.html").resolve(): (
            f"{SITE_BASE}privacy/", "../assets/app-icon.png", SOCIAL_IMAGE,
            ALL_LANGUAGES, ALL_LANGUAGES,
        ),
        (ROOT / "import/index.html").resolve(): (
            f"{SITE_BASE}import/", "../assets/app-icon.png", SOCIAL_IMAGE,
            ANDROID_LANGUAGES, ANDROID_LANGUAGES,
        ),
        (ROOT / "android/index.html").resolve(): (
            f"{SITE_BASE}android/", "../assets/android-app-icon.png", ANDROID_SOCIAL_IMAGE,
            ANDROID_LANGUAGES, ANDROID_LANGUAGES,
        ),
        (ROOT / "android/support/index.html").resolve(): (
            f"{SITE_BASE}android/support/", "../../assets/android-app-icon.png",
            ANDROID_SOCIAL_IMAGE, ANDROID_LANGUAGES, ANDROID_LANGUAGES,
        ),
        (ROOT / "android/privacy/index.html").resolve(): (
            f"{SITE_BASE}android/privacy/", "../../assets/android-app-icon.png",
            ANDROID_SOCIAL_IMAGE, ANDROID_LANGUAGES, ANDROID_LANGUAGES,
        ),
        (ROOT / "terms/index.html").resolve(): (
            f"{SITE_BASE}terms/", "../assets/app-icon.png", SOCIAL_IMAGE,
            ALL_LANGUAGES, ALL_LANGUAGES,
        ),
    }

    for path, page in pages.items():
        label = path.relative_to(ROOT)
        duplicates = sorted({element_id for element_id in page.ids if page.ids.count(element_id) > 1})
        assert not duplicates, f"{label}: duplicate IDs {duplicates}"
        canonical, touch_icon, social_image, panel_languages, link_languages = expected_metadata[path]
        assert page.panel_languages == panel_languages, (
            f"{label}: panels must stay in order {panel_languages}, got {page.panel_languages}"
        )
        assert [language for language, _, _ in page.language_links] == link_languages, (
            f"{label}: expected language links {link_languages}"
        )
        assert [declared for _, _, declared in page.language_links] == link_languages, (
            f"{label}: every language link must declare its own lang"
        )
        current = [language for language, state, _ in page.language_links if state == "true"]
        assert current == [], f"{label}: static markup must not misstate aria-current before JS"

        multilingual = ANDROID_HTML_FILES + IMPORT_HTML_FILES + TERMS_HTML_FILES + [
            ROOT / "privacy/index.html", ROOT / "support/index.html", ROOT / "index.html",
        ]
        if path in {candidate.resolve() for candidate in multilingual}:
            assert page.language_skips == ANDROID_LANGUAGES, (
                f"{label}: Android skip-link locale mismatch"
            )
            assert page.panel_directions == {
                language: "rtl" if language == "ar" else "ltr"
                for language in ANDROID_LANGUAGES
            }, f"{label}: Android panel direction mismatch"
            assert page.panel_declared_languages == {
                language: language for language in ANDROID_LANGUAGES
            }, f"{label}: Android panel language mismatch"

        assert page.link_relations.get("canonical") == canonical, f"{label}: wrong canonical URL"
        # the hash page stays canonical and is the x-default of its route's language pages
        route = canonical.removeprefix(SITE_BASE)
        assert page.alternates == locale_pages.alternates(route), (
            f"{label}: hreflang must list the 17 language pages and x-default"
        )
        assert "data-locale-page" not in page.html_attributes, f"{label}: hash pages keep the switch"
        assert page.link_relations.get("apple-touch-icon") == touch_icon, (
            f"{label}: missing app-icon apple-touch-icon"
        )
        for key in (
            "description",
            "og:title",
            "og:description",
            "og:image:alt",
            "twitter:title",
            "twitter:description",
            "twitter:image:alt",
        ):
            assert page.metadata.get(key), f"{label}: missing {key} metadata"
        assert page.metadata.get("og:type") == "website", f"{label}: wrong og:type"
        assert page.metadata.get("og:site_name") == "DoseWeek", f"{label}: wrong og:site_name"
        assert page.metadata.get("og:url") == canonical, f"{label}: wrong og:url"
        assert page.metadata.get("og:image") == social_image, f"{label}: wrong og:image"
        assert page.metadata.get("twitter:card") == "summary", f"{label}: wrong twitter:card"
        assert page.metadata.get("twitter:image") == social_image, f"{label}: wrong twitter:image"

        check_references(path, page, pages)

    privacy_text = " ".join(pages[(ROOT / "privacy/index.html").resolve()].text)
    support_page = pages[(ROOT / "support/index.html").resolve()]
    support_text = " ".join(support_page.text)
    css = (ROOT / "assets/site.css").read_text(encoding="utf-8")
    for path in pages:
        assert stylesheet_path() in path.read_text(encoding="utf-8"), (
            f"{path.relative_to(ROOT)}: stale stylesheet version; regenerate pages and update index.html"
        )
        assert script_path("language.js") in path.read_text(encoding="utf-8"), (
            f"{path.relative_to(ROOT)}: stale language.js version; regenerate pages"
        )
    javascript = (ROOT / "assets/language.js").read_text(encoding="utf-8")
    assert javascript.find("data-locale-page") != -1 and (
        javascript.find("data-locale-page") < javascript.find("panel.hidden")
    ), "assets/language.js: language pages must return before any panel is hidden"

    policy_dates = json.loads((ROOT / "docs/ios-content.json").read_text(encoding="utf-8"))
    for required in (
        *(entry["privacy"]["effectiveDate"] for entry in policy_dates["locales"].values()),
        "weight, BMI, body fat percentage, lean body mass, and waist circumference",
        "体重、BMI、体脂肪率、除脂肪体重、ウエスト周囲径",
        "체중, BMI, 체지방률, 제지방량, 허리둘레",
        "SystemLanguageModel.default",
        "Private Cloud Compute",
        "AES-256-GCM",
    ):
        assert required in privacy_text, f"privacy/index.html: missing required disclosure {required!r}"

    assert privacy_text.count("SystemLanguageModel.default") == len(ALL_LANGUAGES), (
        "privacy/index.html: SystemLanguageModel.default must appear once per language"
    )
    assert support_text.count("SystemLanguageModel.default") == len(ALL_LANGUAGES), (
        "support/index.html: SystemLanguageModel.default must appear once per language"
    )
    for warning in (
        "Never email health details, a backup file, or a recovery code.",
        "健康情報、バックアップファイル、復旧コードをメールで送らないでください。",
        "건강 정보, 백업 파일, 복구 코드를 절대 이메일로 보내지 마세요.",
    ):
        assert warning in support_text, f"support/index.html: missing safety warning {warning!r}"

    for disclosure in (
        "securely cleans the private database files",
        "If iOS temporarily prevents that cleanup",
        "アプリ専用データベースファイルの安全な消去",
        "iOSによって一時的に消去を完了できない場合",
        "앱 전용 데이터베이스 파일을 안전하게 정리",
        "iOS가 일시적으로 정리를 막으면",
    ):
        assert disclosure in privacy_text, (
            f"privacy/index.html: missing deferred secure-cleanup disclosure {disclosure!r}"
        )

    for support_disclosure in (
        "relaunch DoseWeek",
        "Deleted records are not restored.",
        "DoseWeekを再起動",
        "削除した記録が復元されることはありません。",
        "DoseWeek를 다시 실행",
        "삭제된 기록은 복원되지 않아요.",
    ):
        assert support_disclosure in support_text, (
            f"support/index.html: missing cleanup recovery guidance {support_disclosure!r}"
        )

    for export_disclosure in (
        "PDF and CSV exports are plaintext",
        "the destination you choose in the system share sheet",
        "PDFとCSVの書き出しデータは平文",
        "システム共有シートで選択した送信先",
        "PDF와 CSV 내보내기는 평문",
        "시스템 공유 시트에서 사용자가 선택한 대상",
    ):
        assert export_disclosure in privacy_text and export_disclosure in support_text, (
            f"site: missing sensitive-export disclosure {export_disclosure!r}"
        )

    for overclaim in (
        "immediately deletes every record stored on your device",
        "デバイスに保存されたすべての記録が直ちに削除されます",
        "기기에 저장된 모든 기록이 즉시 삭제됩니다",
        "기기에 저장된 모든 기록이 즉시 삭제돼요",
        "기기에 저장된 모든 기록이 바로 삭제돼요",
    ):
        assert overclaim not in privacy_text and overclaim not in support_text, (
            f"site must not overclaim physical deletion timing: {overclaim!r}"
        )

    for app_lock_guidance in (
        "App Lock cannot be turned off without authentication.",
        "認証せずにアプリロックをオフにすることはできません。",
        "인증 없이는 앱 잠금을 끌 수 없어요.",
    ):
        assert app_lock_guidance in support_text, (
            f"support/index.html: missing App Lock recovery guidance {app_lock_guidance!r}"
        )

    assert "결정적인 진료 준비 화면" not in support_text, (
        "support/index.html: Korean deterministic fallback is mistranslated"
    )
    assert "규칙 기반 진료 준비 화면" in support_text, (
        "support/index.html: missing corrected Korean deterministic fallback"
    )

    assert len(support_page.summary_markers) == 26 * len(ALL_LANGUAGES), (
        "support/index.html: expected eight existing, five bugfix-candidate, seven "
        "second-release and six Plus/ads FAQ disclosures per language"
    )
    assert all(markers == ["true"] for markers in support_page.summary_markers), (
        "support/index.html: every summary needs one aria-hidden summary-symbol"
    )

    android_pages = [pages[path.resolve()] for path in ANDROID_HTML_FILES]
    android_text = " ".join(text for page in android_pages for text in page.text)
    android_feature_claims = " ".join(android_claims_text(path) for path in ANDROID_HTML_FILES)
    android_support = pages[(ROOT / "android/support/index.html").resolve()]
    assert len(android_support.summary_markers) == 25 * len(ANDROID_LANGUAGES), (
        "android/support/index.html: expected seven existing, five bugfix-candidate, seven "
        "second-release and six Plus/ads FAQ disclosures per language"
    )
    assert all(markers == ["true"] for markers in android_support.summary_markers), (
        "android/support/index.html: every summary needs one aria-hidden summary-symbol"
    )

    for path, page, languages, candidate_version in (
        (ROOT / "support/index.html", support_page, ALL_LANGUAGES,
         f"iOS {render_ios.CANDIDATE_VERSION}"),
        (ROOT / "android/support/index.html", android_support, ANDROID_LANGUAGES,
         "Android 1.0.0 (versionCode 12)"),
    ):
        # the five bugfix topics open with a version-scope line naming the release they ship in:
        # iOS 1.0.5 (owner decision IOS-VERSION-104-20260917) or Android code 12. Owner decision
        # 2026-09-24: no pre-release notice; the scope line is not a claim of store availability.
        source = path.read_text(encoding="utf-8")
        for language in languages:
            for topic in ("dates", "edit", "past", "health", "sites"):
                identifier = f"{language}-candidate-{topic}"
                assert identifier in page.ids, f"{path.name}: missing candidate FAQ {identifier}"
                entry = re.search(rf'<details id="{re.escape(identifier)}"[^>]*>(.*?)</details>',
                                  source, flags=re.DOTALL)
                assert entry is not None, identifier
                paragraphs = re.findall(r"<p>(.*?)</p>", entry.group(1), flags=re.DOTALL)
                assert len(paragraphs) == (3 if topic == "sites" else 2), identifier
                assert candidate_version in paragraphs[0], (
                    f"{identifier}: the version-scope line must identify the exact version"
                )

    for path, page, languages, second_release_version, scope_overrides in (
        # iOS: the notice names the marketing version 1.0.5 but no build, because the store build
        # number is chosen at upload
        (ROOT / "support/index.html", support_page, ALL_LANGUAGES,
         f"iOS {render_ios.PAGE_VERSION}", {}),
        # Android: owner decision 2026-09-25, Android 14 is the minimum from versionCode 13
        (ROOT / "android/support/index.html", android_support, ANDROID_LANGUAGES,
         "versionCode 12", {"devices": "versionCode 13"}),
    ):
        source = path.read_text(encoding="utf-8")
        for language in languages:
            for topic in SECOND_RELEASE_TOPICS:
                identifier = f"{language}-candidate2-{topic}"
                assert identifier in page.ids, f"{path.name}: missing {identifier}"
                entry = re.search(rf'<details id="{re.escape(identifier)}"[^>]*>(.*?)</details>',
                                  source, flags=re.DOTALL)
                assert entry is not None, identifier
                paragraphs = re.findall(r"<p>(.*?)</p>", entry.group(1), flags=re.DOTALL)
                assert len(paragraphs) == 2, identifier
                assert scope_overrides.get(topic, second_release_version) in paragraphs[0], (
                    f"{identifier}: the version-scope line must name the version it applies to"
                )
                if path.parent.name == "support" and path.parent.parent == ROOT:
                    assert "build" not in paragraphs[0].lower(), (
                        f"{identifier}: the notice must not name an unreleased build"
                    )

    # Owner decision 2026-09-24: these features ship, so help and policy pages carry no
    # pre-release label, and each support page opens with the six-step getting-started guide.
    pre_release_labels = (
        "출시 전 안내", "Candidate guidance", "公開前のご案内", "Hinweise zur Vorabversion",
        "Guide de la version candidate", "Guía de la versión candidata",
        "Guida alla versione candidata", "Uitleg bij de testversie", "Guia da versão candidata",
        "Wskazówki dotyczące wersji testowej", "Hjälp för testversionen",
        "परीक्षण संस्करण की जानकारी", "إرشادات الإصدار التجريبي", "未发布版本指南", "未發布版本指南",
        "Aday sürüm kılavuzu", "unreleased candidate", "is not released yet",
    )
    for relative in ("support/index.html", "android/support/index.html",
                     "privacy/index.html", "android/privacy/index.html", "terms/index.html"):
        page_text = " ".join(pages[(ROOT / relative).resolve()].text)
        for label in pre_release_labels:
            assert label not in page_text, f"{relative}: pre-release label {label!r} is back"

    # Monetization candidate (owner instruction 2026-09-29, MONETIZATION_POLICY.md): the ads,
    # purchase and Terms disclosures are present, and no page reuses a withdrawn claim or states
    # an unapproved price or trial.
    for path, page in pages.items():
        page_text = " ".join(page.text)
        for claim in MONETIZATION_OVERCLAIMS:
            assert claim not in page_text, f"{path.relative_to(ROOT)}: withdrawn or unapproved claim {claim!r}"
    for required in (
        "Google Mobile Ads SDK (AdMob)",
        "User Messaging Platform (UMP)",
        "App Tracking Transparency",
        "Non-personalized ads still involve processing.",
        "Settings > Privacy choices for ads",
        "In this version the iOS app sends no purchase data to the developer.",
        "It does not cancel a Plus subscription, which you manage in the App Store.",
        "This section covers optional usage analytics only.",
        "개인 맞춤형이 아닌 광고에도 정보 처리가 필요해요.",
        "설정 > 광고 개인정보 선택",
    ):
        assert required in privacy_text, f"privacy/index.html: missing monetization disclosure {required!r}"
    terms_text = " ".join(pages[(ROOT / "terms/index.html").resolve()].text)
    for required in (
        "at least 24 hours before the end of the current period",
        "Payments & subscriptions > Subscriptions",
        "has no cash value",
        "This app is not a medical device.",
        "이 앱은 의료기기가 아니에요.",
        "wonyoung@wonyoungchoi.dev",
    ):
        assert required in terms_text, f"terms/index.html: missing required term {required!r}"
    for relative in ("support/index.html", "android/support/index.html"):
        source = (ROOT / relative).read_text(encoding="utf-8")
        guides = re.findall(r'<section class="help-start" aria-labelledby="([^"]+)-start">(.*?)</section>',
                            source, flags=re.DOTALL)
        assert [language for language, _ in guides] == ANDROID_LANGUAGES, (
            f"{relative}: every locale needs the getting-started guide"
        )
        for language, body in guides:
            assert body.count("<li>") == 6, f"{relative}: {language} guide must have six steps"
            assert source.index(f'id="{language}-start"') < source.index(f'id="{language}-faq"'), (
                f"{relative}: {language} guide must come before the FAQ"
            )

    for prohibited in (
        "iPhone",
        "iPad",
        "iOS",
        "Apple Health",
        "HealthKit",
        "Apple Foundation Models",
        "Apple Intelligence",
        "SystemLanguageModel",
        "Private Cloud Compute",
        "Face ID",
        "PDF",
        "Visit Prep",
    ):
        pattern = (
            rf"(?<![A-Za-z0-9_]){re.escape(prohibited.casefold())}(?![A-Za-z0-9_])"
        )
        assert not re.search(pattern, android_feature_claims.casefold()), (
            f"Android pages contain prohibited iOS-only claim/token {prohibited!r}"
        )

    for required in (
        "only the app's package name, the product and the purchase token",
        "reads the advertising ID as zeros",
        "Google Play Billing",
        "Non-personalized ads still involve processing.",
        "no developer server for health records",
        "system file picker",
        "AES-256-GCM",
        "app-private storage",
        "Health Connect",
        "Tapping a reminder only opens the app",
        "Optional reminders and a home-screen widget are available",
        "There are no wearable apps",
        "stores no biometric data",
        "not a medical device",
        "wonyoung@wonyoungchoi.dev",
        "Android 1.0.0",
    ):
        assert required in android_text, f"Android pages are missing required disclosure {required!r}"
    # "CC0 1.0" is the name of a data licence, not an app version, so it is removed before
    # the version scan; every remaining 1.0 would be an inexact version scope.
    android_version_text = android_text.replace("CC0 1.0", "CC0")
    assert not re.search(r"(?<![\d.])1\.0(?![\d.])", android_version_text), (
        "Android pages must use the binary's exact 1.0.0 version scope"
    )
    for relative_path in ("android/privacy/index.html", "android/support/index.html"):
        source = (ROOT / relative_path).read_text(encoding="utf-8")
        assert re.search(
            r'<article id="ar".*?<a class="page-link"[^>]*>.*?'
            r'<span aria-hidden="true">←</span>',
            source,
            re.DOTALL,
        ), f"{relative_path}: Arabic page link must point left"

    assert ".faq-list summary::after" not in css, (
        "assets/site.css: disclosure state must not pollute the summary accessible name"
    )
    assert 'content: "+"' not in css and 'content: "−"' not in css, (
        "assets/site.css: disclosure icons must be drawn without accessible text"
    )

    assert_css_minimum(css, ".brand", "min-height", 44)
    assert_css_minimum(css, ".brand", "min-width", 44)
    assert_css_minimum(css, ".language-nav.many-languages .language-link", "min-height", 44)
    assert_css_minimum(css, ".policy-toc a", "min-height", 44)
    assert_css_minimum(css, ".page-link", "min-height", 44)
    assert "clip-path: inset(50%)" not in css, (
        "assets/site.css: mobile layout must keep the DoseWeek brand label visible"
    )
    assert "activeLanguageLink.scrollIntoView" in javascript, (
        "assets/language.js: selected Android locale must be scrolled into view"
    )
    assert "data-language-skip" in javascript and "data-skip-target" in javascript, (
        "assets/language.js: localized skip links must preserve the active locale"
    )
    normalized_css = " ".join(css.split())
    for language in ANDROID_LANGUAGES[1:]:
        selector = (
            f'body:has(.language-panel[data-language="{language}"]:target) '
            f'.skip-link[data-language-skip="{language}"]'
        )
        nested_selector = (
            f'body:has(.language-panel[data-language="{language}"] :target) '
            f'.skip-link[data-language-skip="{language}"]'
        )
        assert selector in normalized_css and nested_selector in normalized_css, (
            f"assets/site.css: missing no-JS localized skip-link selectors for {language}"
        )

    for required in (
        "USDA FoodData Central",
        "Open Government Licence v3.0",
        "CC0 1.0",
        "data.go.kr",
        "iOS 26.0",
    ):
        assert required in privacy_text, (
            f"privacy/index.html: missing second-release disclosure {required!r}"
        )

    ios_content = json.loads((ROOT / "docs/ios-content.json").read_text(encoding="utf-8"))
    assert render_ios.rendered(ios_content) == (ROOT / "privacy/index.html").read_text(
        encoding="utf-8"
    ), "privacy/index.html does not match docs/ios-content.json; rerun render_ios.py"
    assert render_ios.rendered_support(ios_content) == (ROOT / "support/index.html").read_text(
        encoding="utf-8"
    ), "support/index.html does not match docs/ios-content.json; rerun render_ios.py"
    for path, expected in {**render_ios.rendered_locale_pages(ios_content),
                           **render_home.rendered_locale_pages()}.items():
        assert path.is_file() and path.read_text(encoding="utf-8") == expected, (
            f"{path.relative_to(ROOT)} does not match its source; rerun render_ios.py and render_home.py"
        )
    for path, expected in render_terms.rendered_pages(*render_terms.load()).items():
        assert path.is_file() and path.read_text(encoding="utf-8") == expected, (
            f"{path.relative_to(ROOT)} does not match docs/terms-content.json; rerun render_terms.py"
        )

    if arguments.catalog:
        catalog_check(arguments.catalog.resolve(), privacy_text)
        render_ios.catalog_parity(ios_content, arguments.catalog.resolve())

    if arguments.android_content:
        android_catalog = json.loads(arguments.android_content.read_text(encoding="utf-8"))
        validate_catalog(android_catalog)
        android_guard_regression_check(android_catalog)
        for path, expected in rendered_pages(android_catalog).items():
            assert path.read_text(encoding="utf-8") == expected, (
                f"{path.relative_to(ROOT)} does not match the Android legal source"
            )

    import_content = json.loads((ROOT / "import/content.json").read_text(encoding="utf-8"))
    validate_import(import_content, require_all=True)
    assert import_content["status"] == "supported", (
        "import/content.json: the published guide must lead to the in-app import "
        "(TRANSFER-20260913-10), not stay preparation_only"
    )
    for relative, expected in rendered_import(import_content).items():
        assert (ROOT / relative).read_text(encoding="utf-8") == expected, (
            f"{relative}: stale generated import guide or download"
        )
    import_source = (ROOT / "import/index.html").read_text(encoding="utf-8")
    assert import_source.count(f'data-import-status="{import_content["status"]}"') == 17
    assert "<form" not in import_source and 'type="file"' not in import_source, (
        "import/index.html: the import guide must not upload records"
    )
    import_page = pages[(ROOT / "import/index.html").resolve()]
    assert len(import_page.summary_markers) == 3 * 17
    assert all(markers == ["true"] for markers in import_page.summary_markers)

    tone = korean_tone_check()

    # Per-language URLs: 17 static pages per route next to the multilingual hash page, one
    # hreflang cluster per route, and a sitemap that lists every page with its alternates.
    language_pages = check_language_pages(pages)
    all_pages = {**pages, **language_pages}
    cluster_pages = check_hreflang_clusters(all_pages)
    sitemap_urls = check_sitemap(all_pages)

    parity = []
    if arguments.catalog:
        parity.append("iOS app-catalog parity")
    if arguments.android_content:
        parity.append("Android legal-catalog parity")
    suffix = f", and {' + '.join(parity)}" if parity else ""
    print(
        f"OK: {len(HTML_FILES)} hash pages and {len(language_pages)} language pages, hreflang "
        f"({cluster_pages} pages, 17 languages + x-default, reciprocal), sitemap ({sitemap_urls} URLs "
        f"with alternates)/robots, local links, locale panels, social metadata, accessible FAQ "
        f"markers, 44px key targets, critical disclosures, {tone}{suffix}"
    )


if __name__ == "__main__":
    main()
