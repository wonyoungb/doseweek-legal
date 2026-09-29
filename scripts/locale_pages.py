"""Per-language URLs for the help site: /<locale>/<route>, hreflang links and the sitemap.

The hash pages (/support/#ko) stay the multilingual entry points: the apps and store listings
link to them, they keep their JavaScript switch and no-JavaScript fallback, and they are the
x-default of their route. Every locale also gets one static page per route, rendered from the
same panel as the hash page, so a search engine sees one language per URL. Every page of a
route (the hash page and the 17 language pages) lists the same 18 alternates.

URL folders use the exact locale tags of the hash links (pt-PT, zh-Hans). GitHub Pages is
case-sensitive, so /pt-pt/ is not an alias.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

from site_assets import script_path, stylesheet_path

ROOT = Path(__file__).resolve().parents[1]
SITE_BASE = "https://doseweek-legal.wonyoungchoi.dev/"
LOCALES = (
    "ko", "en", "ja", "de", "fr", "es", "it", "nl", "pt-PT", "pl", "sv", "hi",
    "pt-BR", "ar", "zh-Hans", "zh-Hant", "tr",
)
ROUTES = ("", "support/", "privacy/", "android/", "android/support/", "android/privacy/", "import/")
PANEL_CLASS = 'class="language-panel"'


def direction(locale: str) -> str:
    return "rtl" if locale == "ar" else "ltr"


def page_url(route: str, locale: str | None = None) -> str:
    """Absolute URL of a route's hash page (locale None, the x-default) or language page."""
    assert route in ROUTES, route
    return SITE_BASE + (f"{locale}/" if locale else "") + route


def page_path(route: str, locale: str | None = None) -> Path:
    assert route in ROUTES, route
    return ROOT / (locale or "") / route / "index.html"


def root_prefix(route: str, locale: str | None = None) -> str:
    """Relative path from the page's folder back to the site root."""
    return "../" * (route.count("/") + (1 if locale else 0))


def alternates(route: str) -> list[tuple[str, str]]:
    """(hreflang, URL) for every page of the route: the 17 languages, then x-default."""
    return [(locale, page_url(route, locale)) for locale in LOCALES] + [("x-default", page_url(route))]


def alternate_links(route: str, indent: str = "    ") -> str:
    return "\n".join(
        f'{indent}<link rel="alternate" hreflang="{code}" href="{href}">'
        for code, href in alternates(route)
    )


def words(value: str) -> str:
    """One-line metadata text."""
    return " ".join(value.split())


def activated(panel: str) -> str:
    """The hash page's panel, shown without JavaScript by the existing .is-active rule."""
    assert panel.count(PANEL_CLASS) == 1, "a language page holds exactly one panel"
    return panel.replace(PANEL_CLASS, 'class="language-panel is-active"', 1)


def panel_title(panel: str) -> str:
    """The title the hash page's script sets for this panel; the language page uses it too."""
    titles = re.findall(r'data-document-title="([^"]*)"', panel)
    assert len(titles) == 1, "a panel names one document title"
    return html.unescape(titles[0])


def language_navigation(route: str, locale: str, names: dict[str, str], indent: str) -> str:
    """Links to the same route in every language; the current one is marked, never switched."""
    prefix = root_prefix(route, locale)
    items = []
    for other in LOCALES:
        current = ' aria-current="true"' if other == locale else ""
        items.append(
            f'{indent}<li><a class="language-link" href="{prefix}{other}/{route}" lang="{other}" '
            f'hreflang="{other}"{current}>{html.escape(names[other])}</a></li>'
        )
    return "\n".join(items)


def locale_page(
    *,
    route: str,
    locale: str,
    names: dict[str, str],
    description: str,
    panel: str,
    icon: str,
    social_image: str,
    image_alt: str,
    brand_href: str,
    brand_aria: str,
    brand_label: str,
    skip_label: str,
    skip_target: str,
    body_attributes: str = "",
    footer: str = "",
    styles: tuple[str, ...] = (),
    scripts: tuple[str, ...] = (),
) -> str:
    """One static page: this locale's panel with its own lang, canonical URL and alternates.

    `brand_label` and `footer` are markup from the renderer; other text is escaped here.
    `icon`, `styles` and `scripts` are site-root-relative asset paths.
    """
    prefix = root_prefix(route, locale)
    canonical = page_url(route, locale)
    title = html.escape(panel_title(panel))
    summary = html.escape(words(description))
    assert summary, f"{locale}/{route}: empty description"
    extra_styles = "".join(f'\n    <link rel="stylesheet" href="{prefix}{style}">' for style in styles)
    extra_scripts = "".join(f'\n    <script src="{prefix}{script}" defer></script>' for script in scripts)
    footer_line = f"\n\n    {footer}" if footer else ""
    return f"""<!doctype html>
<html lang="{locale}" dir="{direction(locale)}" data-locale-page>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
    <meta name="description" content="{summary}">
    <meta name="color-scheme" content="light dark">
    <meta name="theme-color" media="(prefers-color-scheme: light)" content="#f4f4f8">
    <meta name="theme-color" media="(prefers-color-scheme: dark)" content="#0d0d11">
    <title>{title}</title>
    <link rel="canonical" href="{canonical}">
{alternate_links(route)}
    <link rel="icon" type="image/png" href="{prefix}{icon}">
    <link rel="apple-touch-icon" href="{prefix}{icon}">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="DoseWeek">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{summary}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:image" content="{social_image}">
    <meta property="og:image:alt" content="{html.escape(image_alt)}">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{summary}">
    <meta name="twitter:image" content="{social_image}">
    <meta name="twitter:image:alt" content="{html.escape(image_alt)}">
    <link rel="stylesheet" href="{stylesheet_path(prefix)}">{extra_styles}
    <script src="{script_path('language.js', prefix)}" defer></script>{extra_scripts}
  </head>
  <body{body_attributes}>
    <a class="skip-link" href="#{html.escape(skip_target)}" lang="{locale}" dir="{direction(locale)}">{html.escape(skip_label)}</a>

    <header class="site-header site-shell">
      <a class="brand" href="{brand_href}" aria-label="{html.escape(brand_aria)}">
        <img class="brand-mark" src="{prefix}{icon}" alt="" width="36" height="36">
        <span class="brand-label">{brand_label}</span>
      </a>
      <nav class="language-nav many-languages" aria-label="Language">
        <ul class="language-list">
{language_navigation(route, locale, names, "          ")}
        </ul>
      </nav>
    </header>

    <main id="main" class="site-shell" tabindex="-1">
      <div class="language-stack">
{activated(panel)}
      </div>
    </main>{footer_line}
  </body>
</html>
"""


def sitemap_xml() -> str:
    """Every page of every route, each with the route's hreflang alternates."""
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    ]
    for route in ROUTES:
        links = [
            f'    <xhtml:link rel="alternate" hreflang="{code}" href="{href}"/>'
            for code, href in alternates(route)
        ]
        for locale in (None, *LOCALES):
            lines += ["  <url>", f"    <loc>{page_url(route, locale)}</loc>", *links, "  </url>"]
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def write_pages(pages: dict[Path, str], check: bool, stale_hint: str) -> None:
    """Write generated pages (creating language folders), or assert that they are current."""
    for path, text in pages.items():
        if check:
            assert path.is_file(), f"missing generated page {path.relative_to(ROOT)}; {stale_hint}"
            assert path.read_text(encoding="utf-8") == text, (
                f"stale generated page {path.relative_to(ROOT)}; {stale_hint}"
            )
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
