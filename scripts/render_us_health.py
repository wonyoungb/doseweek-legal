#!/usr/bin/env python3
"""Render the separate US health-data policy and all 17 static language pages.

The source is docs/us-health-content.json. This review draft shares the release-date gate with
Terms, and is generated locally only. Shared privacy pages link to this distinct document.
"""
from __future__ import annotations

import argparse
import functools
import html
import json
from pathlib import Path

from site_assets import script_path, stylesheet_path
import legal_release
import locale_pages

ROOT = Path(__file__).resolve().parents[1]
SITE_BASE = locale_pages.SITE_BASE
CONTENT_PATH = ROOT / 'docs/us-health-content.json'
IOS_CONTENT_PATH = ROOT / 'docs/ios-content.json'
ROUTE = 'us-health/'
PAGE_PATH = ROOT / ROUTE / 'index.html'
CANONICAL = f'{SITE_BASE}{ROUTE}'
TITLE = 'DoseWeek US Consumer Health Data Privacy Policy'
DESCRIPTION = ('A separate consumer health-data privacy notice for DoseWeek users in the United '
               'States: categories, purposes, sources, recipients, consent, deletion and appeals.')
SOCIAL_IMAGE = f'{SITE_BASE}assets/app-icon.png'
SUPPORT_EMAIL = 'wonyoung@wonyoungchoi.dev'
SECTION_IDS = ['categories', 'purposes-sources', 'disclosures', 'consent', 'rights', 'deadlines', 'contact']
PARAGRAPH_COUNTS = dict(zip(SECTION_IDS, (1, 2, 3, 2, 3, 3, 1)))


def escaped(value: object) -> str:
    return html.escape(str(value), quote=True)


def load() -> tuple[dict, dict]:
    return (json.loads(CONTENT_PATH.read_text(encoding='utf-8')),
            json.loads(IOS_CONTENT_PATH.read_text(encoding='utf-8')))


def validate(content: dict, ios: dict) -> None:
    assert set(content) == {'schemaVersion', 'effectiveDate', 'supportEmail', 'localeOrder', 'locales'}
    assert content['schemaVersion'] == 1
    assert content['effectiveDate'] in (legal_release.NEXT_RELEASE_EFFECTIVE_DATE,
                                        legal_release.PUBLISHED_EFFECTIVE_DATE), (
        'US health-data policy effectiveDate must match NEXT_RELEASE_EFFECTIVE_DATE')
    assert content['supportEmail'] == SUPPORT_EMAIL
    assert content['localeOrder'] == list(locale_pages.LOCALES) == ios['localeOrder']
    assert list(content['locales']) == content['localeOrder']
    assert '<' not in json.dumps(content, ensure_ascii=False), 'US health-data copy must be plain text'
    for locale, entry in content['locales'].items():
        assert set(entry) == {'title', 'intro', 'effectiveDateLabel', 'sections', 'links'}, locale
        assert set(entry['links']) == {'privacyIos', 'privacyAndroid'}, locale
        for text in (entry['title'], entry['intro'], entry['effectiveDateLabel'], *entry['links'].values()):
            assert isinstance(text, str) and text.strip(), locale
        assert [section['id'] for section in entry['sections']] == SECTION_IDS, locale
        for number, section in enumerate(entry['sections'], 1):
            assert set(section) == {'id', 'title', 'paragraphs'}, (locale, section['id'])
            assert section['title'].startswith(f'{number}. '), (locale, section['id'])
            assert len(section['paragraphs']) == PARAGRAPH_COUNTS[section['id']], (locale, section['id'])
            assert all(isinstance(p, str) and p.strip() for p in section['paragraphs']), (locale, section['id'])
        by_id = {section['id']: section for section in entry['sections']}
        joined = lambda key: '\n'.join(by_id[key]['paragraphs'])
        assert 'HealthKit' in joined('purposes-sources') and 'Health Connect' in joined('purposes-sources'), locale
        assert 'Cloudflare' in joined('disclosures') and 'AWS' in joined('disclosures'), locale
        assert SUPPORT_EMAIL in joined('rights') and SUPPORT_EMAIL in joined('contact'), locale
        assert '7' in joined('rights'), locale
        for token in ('Washington', 'Nevada', 'Connecticut', '45', '30', '60', '15'):
            assert token in joined('deadlines'), (locale, token)
        assert joined('deadlines').count('45') >= 5, locale


def section_markup(locale: str, section: dict) -> str:
    body = ''.join(f'<p>{escaped(block).replace(chr(10), "<br>")}</p>'
                   for paragraph in section['paragraphs'] for block in paragraph.split('\n\n'))
    return (f'              <section id="{escaped(locale)}-{escaped(section["id"])}" '
            f'class="policy-section"><h2>{escaped(section["title"])}</h2><div>{body}</div></section>')


def panel(locale: str, entry: dict, ios_entry: dict, effective_date: str | None) -> str:
    direction = ios_entry['direction']
    arrow = '←' if direction == 'rtl' else '→'
    contents = ios_entry['common']['contents']
    document_title = f'{entry["title"]} — DoseWeek'
    toc = ''.join(f'<li><a href="#{escaped(locale)}-{escaped(section["id"])}">'
                  f'{escaped(section["title"])}</a></li>' for section in entry['sections'])
    sections = '\n'.join(section_markup(locale, section) for section in entry['sections'])
    date = (f'\n            <p class="date"><time datetime="{escaped(effective_date)}">'
            f'{escaped(entry["effectiveDateLabel"])}: {escaped(effective_date)}</time></p>'
            if effective_date else '')
    return f'''        <article id="{escaped(locale)}" class="language-panel" lang="{escaped(locale)}" dir="{escaped(direction)}" data-language="{escaped(locale)}" data-document-title="{escaped(document_title)}" aria-labelledby="{escaped(locale)}-content">
          <header class="hero">
            <p class="eyebrow">DoseWeek</p>
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
        </article>'''


FOOTER = ('<footer class="site-footer site-shell"><span>© 2026 Wonyoung Choi</span>'
          '<span>DoseWeek</span></footer>')


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
  <body data-page="us-health">
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
    validate(content, ios)
    names = {locale: entry['languageName'] for locale, entry in ios['locales'].items()}
    pages = {}
    for locale in content['localeOrder']:
        entry, ios_entry = content['locales'][locale], ios['locales'][locale]
        pages[locale_pages.page_path(ROUTE, locale)] = locale_pages.locale_page(
            route=ROUTE, locale=locale, names=names, description=entry['intro'],
            panel=panel(locale, entry, ios_entry, content['effectiveDate']),
            icon='assets/app-icon.png', social_image=SOCIAL_IMAGE, image_alt='DoseWeek app icon',
            brand_href='../', brand_aria='DoseWeek', brand_label='DoseWeek',
            skip_label=ios_entry['common']['skipToContent'], skip_target=f'{locale}-content',
            body_attributes=' data-page="us-health"', footer=FOOTER,
        )
    return pages


def rendered_pages(content: dict, ios: dict) -> dict[Path, str]:
    return {PAGE_PATH: rendered(content, ios), **rendered_locale_pages(content, ios)}


@functools.lru_cache(maxsize=None)
def link_titles() -> dict[str, str]:
    content = json.loads(CONTENT_PATH.read_text(encoding='utf-8'))
    return {locale: entry['title'] for locale, entry in content['locales'].items()}


def page_link(locale: str, prefix: str, direction: str) -> str:
    arrow = '←' if direction == 'rtl' else '→'
    return (f'<a class="page-link" href="{prefix}us-health/#{escaped(locale)}">'
            f'{escaped(link_titles()[locale])} <span aria-hidden="true">{arrow}</span></a>')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    content, ios = load()
    pages = rendered_pages(content, ios)
    locale_pages.write_pages(pages, args.check, 'rerun render_us_health.py')
    date = content['effectiveDate'] or 'not set (release date BLOCKED)'
    action = 'OK' if args.check else 'Rendered'
    print(f'{action}: US Consumer Health Data policy, {len(pages)} pages / '
          f'{len(content["locales"])} locales; effective date {date}')


if __name__ == '__main__':
    main()
