#!/usr/bin/env python3
"""Spec for the per-language help URLs (/<locale>/<route>), read from the generated files.

This test is self-contained on purpose: it defines the expected locales and routes itself and
inspects the pages on disk, so it checks what the renderers wrote instead of reusing their code.
The hash pages (/support/#ko) stay the multilingual entry points and the x-default of each
route; every locale also gets one static page per route that shows only its own language.
"""

from __future__ import annotations

import json
import re
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://doseweek-legal.wonyoungchoi.dev/"
LOCALES = [
    "ko", "en", "ja", "de", "fr", "es", "it", "nl", "pt-PT", "pl", "sv", "hi",
    "pt-BR", "ar", "zh-Hans", "zh-Hant", "tr",
]
ROUTES = [
    "", "support/", "privacy/", "android/", "android/support/", "android/privacy/", "import/",
    "terms/",
]
SITEMAP = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
XHTML = "{http://www.w3.org/1999/xhtml}"


def page_url(route: str, locale: str | None = None) -> str:
    return BASE + (f"{locale}/" if locale else "") + route


def page_path(route: str, locale: str | None = None) -> Path:
    return ROOT / (locale or "") / route / "index.html"


def expected_alternates(route: str) -> list[tuple[str, str]]:
    return [(locale, page_url(route, locale)) for locale in LOCALES] + [("x-default", page_url(route))]


def words(value: str) -> str:
    return " ".join(value.split())


class Page(HTMLParser):
    """What the spec needs from one generated page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.html: dict[str, str | None] = {}
        self.title = ""
        self._in_title = False
        self.meta: dict[str, str] = {}
        self.canonical: list[str] = []
        self.alternates: list[tuple[str, str]] = []
        self.panels: list[dict[str, str | None]] = []
        self.nav_links: list[dict[str, str | None]] = []
        self.hash_switch_links: list[str] = []
        self.references: list[str] = []
        self.ids: list[str] = []
        self.scripts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        classes = (values.get("class") or "").split()
        if values.get("id"):
            self.ids.append(values["id"])
        if tag == "html":
            self.html = values
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            key = values.get("name") or values.get("property")
            if key and values.get("content") is not None:
                self.meta[key] = values["content"]
        elif tag == "link":
            relations = (values.get("rel") or "").split()
            if "canonical" in relations:
                self.canonical.append(values.get("href") or "")
            if "alternate" in relations and values.get("hreflang"):
                self.alternates.append((values["hreflang"], values.get("href") or ""))
        elif tag == "script" and values.get("src"):
            self.scripts.append(values["src"])
        if "language-panel" in classes:
            self.panels.append(values)
        if tag == "a" and "language-link" in classes:
            self.nav_links.append(values)
        if values.get("data-language-link"):
            self.hash_switch_links.append(values["data-language-link"])
        if tag in {"a", "link", "img", "script"}:
            reference = values.get("href") or values.get("src")
            if reference:
                self.references.append(reference)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data


_PAGES: dict[Path, Page] = {}


def load(route: str, locale: str | None = None) -> Page:
    path = page_path(route, locale)
    assert path.is_file(), f"missing generated page {path.relative_to(ROOT)}"
    if path not in _PAGES:
        parser = Page()
        parser.feed(path.read_text(encoding="utf-8"))
        parser.close()
        _PAGES[path] = parser
    return _PAGES[path]


def sources() -> dict[str, dict]:
    read = lambda relative: json.loads((ROOT / relative).read_text(encoding="utf-8"))
    return {
        "home": read("docs/home-content.json"),
        "ios": read("docs/ios-content.json")["locales"],
        "android": read("docs/android-content.candidate.json")["locales"],
        "import": read("import/content.json")["locales"],
        "terms": read("docs/terms-content.json")["locales"],
    }


def expected_description(route: str, locale: str, data: dict[str, dict]) -> str:
    """Existing localized copy only: each route's description comes from its own source."""
    return words({
        "": data["home"][locale]["intro"],
        "support/": data["ios"][locale]["support"]["labels"]["lead"],
        "privacy/": data["ios"][locale]["privacy"]["intro"],
        "android/": data["home"][locale]["androidBody"],
        "android/support/": data["android"][locale]["home"]["supportLinkBody"],
        "android/privacy/": data["android"][locale]["home"]["privacyLinkBody"],
        "import/": data["import"][locale]["lead"],
        "terms/": data["terms"][locale]["intro"],
    }[route])


def local_file(page: Path, reference: str) -> tuple[Path, str] | None:
    split = urlsplit(reference)
    if split.scheme in {"mailto"}:
        return None
    if split.scheme or split.netloc:
        if not reference.startswith(BASE):
            return None
        target = ROOT / unquote(split.path).lstrip("/")
    else:
        target = page if not split.path else (page.parent / unquote(split.path)).resolve()
    if target.is_dir() or split.path.endswith("/"):
        target /= "index.html"
    return target, unquote(split.fragment)


class LocalePageTests(unittest.TestCase):
    def test_every_route_has_a_page_for_every_locale(self):
        missing = [
            page_path(route, locale).relative_to(ROOT).as_posix()
            for route in ROUTES for locale in LOCALES if not page_path(route, locale).is_file()
        ]
        self.assertEqual(missing, [], f"{len(missing)} per-language pages are missing")

    def test_locale_pages_declare_their_language_and_direction(self):
        for route in ROUTES:
            for locale in LOCALES:
                with self.subTest(route=route, locale=locale):
                    page = load(route, locale)
                    direction = "rtl" if locale == "ar" else "ltr"
                    self.assertEqual(page.html.get("lang"), locale)
                    self.assertEqual(page.html.get("dir"), direction)
                    self.assertIn("data-locale-page", page.html)
                    self.assertEqual(len(page.panels), 1, "one language per URL")
                    panel = page.panels[0]
                    self.assertEqual(
                        (panel.get("data-language"), panel.get("lang"), panel.get("dir")),
                        (locale, locale, direction),
                    )
                    # visible without JavaScript: the existing .is-active rule shows the panel
                    self.assertIn("is-active", (panel.get("class") or "").split())

    def test_locale_pages_are_canonical_and_list_every_alternate(self):
        for route in ROUTES:
            for locale in LOCALES:
                with self.subTest(route=route, locale=locale):
                    page = load(route, locale)
                    self.assertEqual(page.canonical, [page_url(route, locale)])
                    self.assertEqual(page.meta.get("og:url"), page_url(route, locale))
                    self.assertEqual(page.alternates, expected_alternates(route))

    def test_hash_pages_stay_multilingual_and_become_x_default(self):
        for route in ROUTES:
            with self.subTest(route=route):
                page = load(route)
                self.assertEqual(page.canonical, [page_url(route)])
                self.assertEqual(page.alternates, expected_alternates(route))
                self.assertEqual([panel.get("data-language") for panel in page.panels], LOCALES)
                self.assertEqual(page.hash_switch_links, LOCALES, "hash switching stays")
                self.assertEqual(
                    [link.get("href") for link in page.nav_links], [f"#{locale}" for locale in LOCALES]
                )
                self.assertNotIn("data-locale-page", page.html)
                self.assertEqual(page.html.get("lang"), "ko", "Korean stays the no-JavaScript default")

    def test_hreflang_links_are_reciprocal(self):
        clusters: dict[str, tuple[str, list[tuple[str, str]]]] = {}
        for route in ROUTES:
            clusters[page_url(route)] = ("x-default", load(route).alternates)
            for locale in LOCALES:
                clusters[page_url(route, locale)] = (locale, load(route, locale).alternates)
        for url, (code, alternates) in clusters.items():
            self.assertIn((code, url), alternates, f"{url} must list itself")
            for other_code, other_url in alternates:
                self.assertIn(other_url, clusters, f"{url}: alternate {other_url} is not a page")
                own, back = clusters[other_url]
                self.assertEqual(own, other_code, f"{url}: {other_url} is not the {other_code} page")
                self.assertIn((code, url), back, f"{other_url} does not link back to {url}")

    def test_titles_and_descriptions_are_localized(self):
        data = sources()
        for route in ROUTES:
            titles = set()
            for locale in LOCALES:
                with self.subTest(route=route, locale=locale):
                    page = load(route, locale)
                    title = page.panels[0].get("data-document-title")
                    self.assertTrue(title)
                    self.assertEqual(page.title, title, "static title = the title the hash page sets")
                    self.assertEqual(page.meta.get("og:title"), title)
                    self.assertEqual(page.meta.get("twitter:title"), title)
                    description = expected_description(route, locale, data)
                    self.assertEqual(page.meta.get("description"), description)
                    self.assertEqual(page.meta.get("og:description"), description)
                    self.assertEqual(page.meta.get("twitter:description"), description)
                    titles.add(title)
            self.assertGreater(len(titles), len(LOCALES) // 2, f"{route}: titles look untranslated")

    def test_language_navigation_links_the_same_route_in_every_locale(self):
        for route in ROUTES:
            for locale in LOCALES:
                with self.subTest(route=route, locale=locale):
                    page = load(route, locale)
                    self.assertEqual(page.hash_switch_links, [], "static pages have no hash switch")
                    self.assertEqual([link.get("hreflang") for link in page.nav_links], LOCALES)
                    self.assertEqual([link.get("lang") for link in page.nav_links], LOCALES)
                    resolved = [urljoin(page_url(route, locale), link.get("href") or "") for link in page.nav_links]
                    self.assertEqual(resolved, [page_url(route, other) for other in LOCALES])
                    current = [link.get("hreflang") for link in page.nav_links if link.get("aria-current") == "true"]
                    self.assertEqual(current, [locale])

    def test_local_links_resolve_from_locale_pages(self):
        for route in ROUTES:
            for locale in LOCALES:
                path = page_path(route, locale)
                page = load(route, locale)
                for reference in page.references:
                    resolved = local_file(path, reference)
                    if resolved is None:
                        continue
                    target, fragment = resolved
                    with self.subTest(page=path.relative_to(ROOT).as_posix(), reference=reference):
                        self.assertTrue(target.is_file(), f"broken link {reference!r}")
                        if fragment and target.suffix == ".html":
                            other = page if target == path else None
                            ids = other.ids if other else re.findall(r'\sid="([^"]+)"', target.read_text(encoding="utf-8"))
                            self.assertIn(fragment, ids, f"missing anchor for {reference!r}")

    def test_locale_panel_is_the_hash_page_panel(self):
        """Same localized text as the hash page: only the static-visibility class differs."""
        for route in ROUTES:
            root_text = page_path(route).read_text(encoding="utf-8")
            for locale in LOCALES:
                with self.subTest(route=route, locale=locale):
                    self.assertTrue(page_path(route, locale).is_file(), "missing per-language page")
                    text = page_path(route, locale).read_text(encoding="utf-8")
                    pattern = rf'<article id="{re.escape(locale)}"[^>]*>.*?</article>'
                    panel = re.search(pattern, text, flags=re.DOTALL)
                    original = re.search(pattern, root_text, flags=re.DOTALL)
                    self.assertIsNotNone(panel)
                    self.assertIsNotNone(original)
                    normalized = panel.group(0).replace(
                        'class="language-panel is-active"', 'class="language-panel"', 1
                    )
                    # the import downloads live once, in /import/
                    normalized = re.sub(
                        r'href="\.\./\.\./import/((?:prompt|format)\.[^"/]+\.md|draft[^"/]*\.json)"',
                        r'href="\1"', normalized,
                    )
                    self.assertEqual(normalized, original.group(0))

    def test_sitemap_lists_every_page_with_its_alternates(self):
        tree = ET.parse(ROOT / "sitemap.xml")
        entries = {}
        for url in tree.getroot().findall(f"{SITEMAP}url"):
            loc = url.findtext(f"{SITEMAP}loc")
            links = [
                (link.get("hreflang"), link.get("href"))
                for link in url.findall(f"{XHTML}link") if link.get("rel") == "alternate"
            ]
            self.assertNotIn(loc, entries, f"sitemap lists {loc} twice")
            entries[loc] = links
        expected = {page_url(route, locale) for route in ROUTES for locale in [None, *LOCALES]}
        self.assertEqual(set(entries), expected)
        for route in ROUTES:
            for locale in [None, *LOCALES]:
                self.assertEqual(entries[page_url(route, locale)], expected_alternates(route))
        robots = (ROOT / "robots.txt").read_text(encoding="utf-8").splitlines()
        self.assertIn(f"Sitemap: {BASE}sitemap.xml", robots)

    def test_language_script_leaves_static_pages_alone(self):
        script = (ROOT / "assets/language.js").read_text(encoding="utf-8")
        branch = script.find("data-locale-page")
        self.assertNotEqual(branch, -1, "language.js must recognise per-language pages")
        # the static-page branch returns before any panel is hidden or the hash is rewritten
        self.assertLess(branch, script.find("panel.hidden"))
        self.assertLess(branch, script.find("history.replaceState"))
        for route in ROUTES:
            for locale in [None, *LOCALES]:
                with self.subTest(route=route, locale=locale):
                    scripts = [src for src in load(route, locale).scripts if "language.js" in src]
                    self.assertEqual(len(scripts), 1)
                    # a new file name per version keeps a cached old script off the new pages
                    self.assertRegex(scripts[0], r"assets/language\.js\?v=[0-9a-f]{12}$")


if __name__ == "__main__":
    unittest.main()
