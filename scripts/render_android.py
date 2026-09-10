#!/usr/bin/env python3
"""Render the Android public pages from the Android app repository's legal catalog."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE_BASE = "https://doseweek-legal.wonyoungchoi.dev/"
SOCIAL_IMAGE = f"{SITE_BASE}assets/android-app-icon.png"
ANDROID_ICON_PATH = ROOT / "assets/android-app-icon.png"
ANDROID_ICON_SOURCE = Path("marketing/GooglePlay/play-icon-512.png")
REQUIRED_BACKUP_SECURITY_PHRASES = {
    "ko": ("AES-256-GCM으로 암호화된 파일", "별도의 고엔트로피 복구 코드"),
    "en": ("AES-256-GCM encrypted file", "separate high-entropy recovery code"),
    "ja": ("AES-256-GCM暗号化ファイル", "別の高エントロピー復旧コード"),
    "de": ("AES-256-GCM-verschlüsselte", "getrennter Wiederherstellungscode mit hoher Entropie"),
    "fr": ("fichier chiffré avec AES-256-GCM", "code de récupération distinct à haute entropie"),
    "es": ("archivo cifrado con AES-256-GCM", "código de recuperación independiente de alta entropía"),
    "it": ("file crittografato con AES-256-GCM", "codice di ripristino separato ad alta entropia"),
    "nl": ("met AES-256-GCM versleuteld bestand", "aparte herstelcode met hoge entropie"),
    "pt-PT": ("ficheiro encriptado com AES-256-GCM", "código de recuperação separado de alta entropia"),
    "pl": ("pliku zaszyfrowanym AES-256-GCM", "osobny kod odzyskiwania o wysokiej entropii"),
    "sv": ("AES-256-GCM-krypterad fil", "separat återställningskod med hög entropi"),
    "hi": ("AES-256-GCM से एन्क्रिप्ट की गई फ़ाइल", "अलग उच्च-एंट्रॉपी रिकवरी कोड"),
    "pt-BR": ("arquivo criptografado com AES-256-GCM", "código de recuperação separado e de alta entropia"),
    "ar": ("ملف مشفّر باستخدام AES-256-GCM", "رمز استرداد منفصل عالي العشوائية"),
    "zh-Hans": ("AES-256-GCM 加密文件", "单独的高熵恢复码"),
    "zh-Hant": ("AES-256-GCM 加密檔案", "獨立的高熵復原碼"),
    "tr": ("AES-256-GCM ile şifrelenmiş bir dosyaya", "Ayrı, yüksek entropili bir kurtarma kodu"),
}
REQUIRED_EMERGENCY_SERVICE_PHRASES = {
    "es": "servicios de emergencia locales",
    "it": "servizi di emergenza locali",
    "pt-BR": "serviço de emergência local",
}


def escaped(value: object) -> str:
    return html.escape(str(value), quote=True)


def language_navigation(catalog: dict[str, object]) -> str:
    links = []
    locales = catalog["locales"]
    for locale in catalog["localeOrder"]:
        entry = locales[locale]
        links.append(
            "          <li><a class=\"language-link\" "
            f"href=\"#{escaped(locale)}\" lang=\"{escaped(locale)}\" "
            f"hreflang=\"{escaped(locale)}\" data-language-link=\"{escaped(locale)}\">"
            f"{escaped(entry['languageName'])}</a></li>"
        )
    return "\n".join(links)


def skip_links(catalog: dict[str, object]) -> str:
    links = []
    for locale in catalog["localeOrder"]:
        entry = catalog["locales"][locale]
        links.append(
            f'    <a class="skip-link" data-language-skip="{escaped(locale)}" '
            f'href="#{escaped(locale)}-content" lang="{escaped(locale)}" '
            f'dir="{escaped(entry["direction"])}">'
            f'{escaped(entry["common"]["skipToContent"])}</a>'
        )
    return "\n".join(links)


def page_shell(
    *,
    catalog: dict[str, object],
    page: str,
    canonical_path: str,
    asset_prefix: str,
    home_prefix: str,
    title: str,
    description: str,
    panels: str,
) -> str:
    canonical = f"{SITE_BASE}{canonical_path}"
    navigation = language_navigation(catalog)
    skips = skip_links(catalog)
    version = escaped(catalog["versionName"])
    return f"""<!doctype html>
<html lang="ko" dir="ltr">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
    <meta name="description" content="{escaped(description)}">
    <meta name="color-scheme" content="light dark">
    <meta name="theme-color" media="(prefers-color-scheme: light)" content="#f4f4f8">
    <meta name="theme-color" media="(prefers-color-scheme: dark)" content="#0d0d11">
    <title>{escaped(title)}</title>
    <link rel="canonical" href="{canonical}">
    <link rel="icon" type="image/png" href="{asset_prefix}assets/android-app-icon.png">
    <link rel="apple-touch-icon" href="{asset_prefix}assets/android-app-icon.png">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="DoseWeek">
    <meta property="og:title" content="{escaped(title)}">
    <meta property="og:description" content="{escaped(description)}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:image" content="{SOCIAL_IMAGE}">
    <meta property="og:image:alt" content="DoseWeek Android app icon">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{escaped(title)}">
    <meta name="twitter:description" content="{escaped(description)}">
    <meta name="twitter:image" content="{SOCIAL_IMAGE}">
    <meta name="twitter:image:alt" content="DoseWeek Android app icon">
    <link rel="stylesheet" href="{asset_prefix}assets/site.css">
    <script src="{asset_prefix}assets/language.js" defer></script>
  </head>
  <body data-platform="android" data-page="{escaped(page)}">
{skips}

    <header class="site-header site-shell">
      <a class="brand" href="{home_prefix}" aria-label="DoseWeek for Android" data-language-path="{home_prefix}">
        <img class="brand-mark" src="{asset_prefix}assets/android-app-icon.png" alt="" width="36" height="36">
        <span class="brand-label">DoseWeek <span class="platform-label">Android</span></span>
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

    <footer class="site-footer site-shell"><span>© 2026 Wonyoung Choi</span><span>DoseWeek · Android {version}</span></footer>
  </body>
</html>
"""


def panel_attributes(locale: str, entry: dict[str, object], document_title: str) -> str:
    return (
        f'id="{escaped(locale)}" class="language-panel" lang="{escaped(locale)}" '
        f'dir="{escaped(entry["direction"])}" data-language="{escaped(locale)}" '
        f'data-document-title="{escaped(document_title)}" '
        f'aria-labelledby="{escaped(locale)}-content"'
    )


def home_panels(catalog: dict[str, object]) -> str:
    rendered = []
    for locale in catalog["localeOrder"]:
        entry = catalog["locales"][locale]
        content = entry["home"]
        title = f"{content['title']} — DoseWeek Android"
        badges = "".join(f"<li>{escaped(value)}</li>" for value in content["featureBadges"])
        rendered.append(
            f"""        <article {panel_attributes(locale, entry, title)}>
          <header class="hero home-hero">
            <div>
              <p class="eyebrow">DoseWeek · Android {escaped(catalog['versionName'])}</p>
              <h1 id="{escaped(locale)}-content" data-skip-target tabindex="-1">{escaped(content['title'])}</h1>
              <p class="hero-copy">{escaped(content['intro'])}</p>
              <ul class="hero-meta">{badges}</ul>
              <p class="quiet-note">{escaped(content['versionScope'])}</p>
            </div>
            <img class="hero-app-icon" src="../assets/android-app-icon.png" alt="" width="512" height="512">
          </header>

          <section class="content-section">
            <div class="card-grid">
              <a class="link-card" href="privacy/#{escaped(locale)}"><h2>{escaped(content['privacyLinkTitle'])}</h2><p>{escaped(content['privacyLinkBody'])}</p></a>
              <a class="link-card" href="support/#{escaped(locale)}"><h2>{escaped(content['supportLinkTitle'])}</h2><p>{escaped(content['supportLinkBody'])}</p></a>
            </div>
          </section>

          <section class="content-section">
            <div class="info-card medical-notice"><h2>{escaped(content['medicalNoticeTitle'])}</h2><p>{escaped(content['medicalNoticeBody'])}</p></div>
          </section>
        </article>"""
        )
    return "\n\n".join(rendered)


def render_policy_section(locale: str, section: dict[str, object]) -> str:
    body = []
    for paragraph in section["paragraphs"]:
        body.append(f"<p>{escaped(paragraph)}</p>")
    if section.get("items"):
        items = "".join(f"<li>{escaped(item)}</li>" for item in section["items"])
        body.append(f"<ul>{items}</ul>")
    return (
        f'              <section id="{escaped(locale)}-{escaped(section["id"])}" class="policy-section">'
        f"<h2>{escaped(section['title'])}</h2><div>{''.join(body)}</div></section>"
    )


def privacy_panels(catalog: dict[str, object]) -> str:
    rendered = []
    for locale in catalog["localeOrder"]:
        entry = catalog["locales"][locale]
        content = entry["privacy"]
        title = f"{content['title']} — DoseWeek Android"
        toc = "".join(
            f'<li><a href="#{escaped(locale)}-{escaped(section["id"])}">{escaped(section["title"])}</a></li>'
            for section in content["sections"]
        )
        sections = "\n".join(render_policy_section(locale, section) for section in content["sections"])
        medical = content["medicalDisclaimer"]
        arrow = "←" if entry["direction"] == "rtl" else "→"
        rendered.append(
            f"""        <article {panel_attributes(locale, entry, title)}>
          <header class="hero">
            <p class="eyebrow">DoseWeek · Android {escaped(catalog['versionName'])}</p>
            <h1 id="{escaped(locale)}-content" data-skip-target tabindex="-1">{escaped(content['title'])}</h1>
            <p class="hero-copy">{escaped(content['scope'])}</p>
            <p class="date"><time datetime="{escaped(catalog['effectiveDate'])}">{escaped(catalog['effectiveDate'])}</time></p>
          </header>

          <div class="policy-layout">
            <nav class="policy-toc" aria-label="{escaped(entry['common']['contents'])}"><h2>{escaped(entry['common']['contents'])}</h2><ol>{toc}<li><a href="#{escaped(locale)}-medical">{escaped(medical['title'])}</a></li></ol></nav>
            <div class="policy-card">
{sections}
              <section id="{escaped(locale)}-medical" class="policy-section medical"><h2>{escaped(medical['title'])}</h2><div><p>{escaped(medical['body'])}</p></div></section>
            </div>
          </div>
          <a class="page-link" href="../support/#{escaped(locale)}">{escaped(entry['home']['supportLinkTitle'])} <span aria-hidden="true">{arrow}</span></a>
        </article>"""
        )
    return "\n\n".join(rendered)


def support_panels(catalog: dict[str, object]) -> str:
    rendered = []
    email = escaped(catalog["supportEmail"])
    for locale in catalog["localeOrder"]:
        entry = catalog["locales"][locale]
        content = entry["support"]
        title = f"{content['title']} — DoseWeek Android"
        arrow = "←" if entry["direction"] == "rtl" else "→"
        faq = []
        for item in content["faq"]:
            answers = "".join(f"<p>{escaped(answer)}</p>" for answer in item["answers"])
            faq.append(
                f'<details id="{escaped(locale)}-{escaped(item["id"])}"><summary><span>{escaped(item["question"])}</span>'
                '<span class="summary-symbol" aria-hidden="true"></span></summary>'
                f'<div class="faq-answer">{answers}</div></details>'
            )
        rendered.append(
            f"""        <article {panel_attributes(locale, entry, title)}>
          <header class="hero">
            <p class="eyebrow">DoseWeek · Android {escaped(catalog['versionName'])}</p>
            <h1 id="{escaped(locale)}-content" data-skip-target tabindex="-1">{escaped(content['title'])}</h1>
            <p class="hero-copy">{escaped(content['intro'])}</p>
          </header>

          <div class="notice"><span class="notice-symbol" aria-hidden="true">!</span><div><strong>{escaped(content['privacyWarning'])}</strong></div></div>

          <section class="content-section"><div class="faq-list">{''.join(faq)}</div></section>

          <section class="content-section">
            <div class="contact-card"><div><h2>{escaped(content['contact']['title'])}</h2><p>{escaped(content['contact']['body'])}</p></div><a class="button primary" href="mailto:{email}?subject=DoseWeek%20Android%20Support">{email}</a></div>
            <div class="info-card medical-notice"><h2>{escaped(content['emergency']['title'])}</h2><p>{escaped(content['emergency']['body'])}</p></div>
          </section>
          <a class="page-link" href="../privacy/#{escaped(locale)}">{escaped(entry['home']['privacyLinkTitle'])} <span aria-hidden="true">{arrow}</span></a>
        </article>"""
        )
    return "\n\n".join(rendered)


def validate_catalog(catalog: dict[str, object]) -> None:
    def require_string(value: object, path: str) -> None:
        assert isinstance(value, str) and value.strip(), f"expected non-empty string at {path}"

    def require_string_list(
        value: object,
        path: str,
        *,
        expected_length: int | None = None,
    ) -> None:
        assert isinstance(value, list), f"expected list at {path}"
        if expected_length is not None:
            assert len(value) == expected_length, (
                f"expected {expected_length} entries at {path}, got {len(value)}"
            )
        else:
            assert value, f"empty list at {path}"
        for index, item in enumerate(value):
            require_string(item, f"{path}[{index}]")

    def require_nonempty(value: object, path: str) -> None:
        if isinstance(value, str):
            assert value.strip(), f"empty string at {path}"
        elif isinstance(value, list):
            assert value, f"empty list at {path}"
            for index, item in enumerate(value):
                require_nonempty(item, f"{path}[{index}]")
        elif isinstance(value, dict):
            assert value, f"empty object at {path}"
            for key, item in value.items():
                require_nonempty(item, f"{path}.{key}")

    expected_order = [
        "ko", "en", "ja", "de", "fr", "es", "it", "nl", "pt-PT", "pl", "sv",
        "hi", "pt-BR", "ar", "zh-Hans", "zh-Hant", "tr",
    ]
    assert isinstance(catalog, dict), "catalog must be an object"
    assert set(catalog) == {
        "schemaVersion", "platform", "applicationId", "versionName", "effectiveDate",
        "supportEmail", "localeOrder", "locales",
    }
    assert catalog["schemaVersion"] == 1
    assert catalog["platform"] == "android"
    assert catalog["applicationId"] == "com.wonyoungchoi.doseweek"
    assert catalog["versionName"] == "1.0.0"
    assert catalog["effectiveDate"] == "2026-09-08"
    assert catalog["supportEmail"] == "wonyoung@wonyoungchoi.dev"
    assert isinstance(catalog["localeOrder"], list)
    assert isinstance(catalog["locales"], dict)
    assert catalog["localeOrder"] == expected_order
    assert list(catalog["locales"]) == expected_order
    assert catalog["locales"]["ar"]["direction"] == "rtl"
    assert all(
        entry["direction"] == ("rtl" if locale == "ar" else "ltr")
        for locale, entry in catalog["locales"].items()
    )
    require_nonempty(catalog["locales"], "locales")

    expected_home_keys = {
        "title", "versionScope", "intro", "featureBadges", "privacyLinkTitle",
        "privacyLinkBody", "supportLinkTitle", "supportLinkBody", "medicalNoticeTitle",
        "medicalNoticeBody",
    }
    expected_section_ids = [
        "scope", "stored-data", "no-collection", "backup", "retention", "security", "changes",
    ]
    expected_faq_ids = [
        "storage", "accounts", "ai-health", "notifications", "backup", "deletion", "recovery",
    ]
    expected_policy_lengths = {
        "scope": (2, None),
        "stored-data": (1, 7),
        "no-collection": (4, 7),
        "backup": (7, None),
        "retention": (3, None),
        "security": (3, None),
        "changes": (1, None),
    }
    expected_faq_answer_lengths = {
        "storage": 1,
        "accounts": 1,
        "ai-health": 1,
        "notifications": 1,
        "backup": 2,
        "deletion": 1,
        "recovery": 1,
    }
    for locale, entry in catalog["locales"].items():
        assert isinstance(entry, dict), f"{locale}: locale entry must be an object"
        assert set(entry) == {
            "languageName", "direction", "common", "home", "privacy", "support",
        }, locale
        require_string(entry["languageName"], f"{locale}.languageName")
        require_string(entry["direction"], f"{locale}.direction")
        assert isinstance(entry["common"], dict), f"{locale}.common must be an object"
        assert isinstance(entry["home"], dict), f"{locale}.home must be an object"
        assert isinstance(entry["privacy"], dict), f"{locale}.privacy must be an object"
        assert isinstance(entry["support"], dict), f"{locale}.support must be an object"
        assert set(entry["common"]) == {"skipToContent", "contents"}, locale
        assert set(entry["home"]) == expected_home_keys, locale
        for key, value in entry["common"].items():
            require_string(value, f"{locale}.common.{key}")
        for key, value in entry["home"].items():
            if key != "featureBadges":
                require_string(value, f"{locale}.home.{key}")
        require_string_list(
            entry["home"]["featureBadges"],
            f"{locale}.home.featureBadges",
            expected_length=4,
        )
        assert set(entry["privacy"]) == {
            "title", "scope", "sections", "medicalDisclaimer",
        }, locale
        assert set(entry["support"]) == {
            "title", "intro", "privacyWarning", "faq", "contact", "emergency",
        }, locale
        require_string(entry["privacy"]["title"], f"{locale}.privacy.title")
        require_string(entry["privacy"]["scope"], f"{locale}.privacy.scope")
        assert isinstance(entry["privacy"]["sections"], list), (
            f"{locale}.privacy.sections must be a list"
        )
        assert isinstance(entry["privacy"]["medicalDisclaimer"], dict), (
            f"{locale}.privacy.medicalDisclaimer must be an object"
        )
        require_string(entry["support"]["title"], f"{locale}.support.title")
        require_string(entry["support"]["intro"], f"{locale}.support.intro")
        require_string(entry["support"]["privacyWarning"], f"{locale}.support.privacyWarning")
        assert isinstance(entry["support"]["faq"], list), f"{locale}.support.faq must be a list"
        assert isinstance(entry["support"]["contact"], dict), (
            f"{locale}.support.contact must be an object"
        )
        assert isinstance(entry["support"]["emergency"], dict), (
            f"{locale}.support.emergency must be an object"
        )
        assert all(isinstance(section, dict) for section in entry["privacy"]["sections"]), locale
        assert all(isinstance(item, dict) for item in entry["support"]["faq"]), locale
        assert [section.get("id") for section in entry["privacy"]["sections"]] == expected_section_ids, locale
        assert [item.get("id") for item in entry["support"]["faq"]] == expected_faq_ids, locale
        assert set(entry["privacy"]["medicalDisclaimer"]) == {"title", "body"}, locale
        assert set(entry["support"]["contact"]) == {"title", "body"}, locale
        assert set(entry["support"]["emergency"]) == {"title", "body"}, locale
        for key, value in entry["privacy"]["medicalDisclaimer"].items():
            require_string(value, f"{locale}.privacy.medicalDisclaimer.{key}")
        for group in ("contact", "emergency"):
            for key, value in entry["support"][group].items():
                require_string(value, f"{locale}.support.{group}.{key}")
        for section in entry["privacy"]["sections"]:
            expected_keys = {"id", "title", "paragraphs"}
            if section["id"] in {"stored-data", "no-collection"}:
                expected_keys.add("items")
            assert set(section) == expected_keys, f"{locale}:{section['id']}"
            require_string(section["id"], f"{locale}.privacy.{section['id']}.id")
            require_string(section["title"], f"{locale}.privacy.{section['id']}.title")
            paragraph_count, item_count = expected_policy_lengths[section["id"]]
            require_string_list(
                section["paragraphs"],
                f"{locale}.privacy.{section['id']}.paragraphs",
                expected_length=paragraph_count,
            )
            if item_count is not None:
                require_string_list(
                    section["items"],
                    f"{locale}.privacy.{section['id']}.items",
                    expected_length=item_count,
                )
        for item in entry["support"]["faq"]:
            assert set(item) == {"id", "question", "answers"}, f"{locale}:{item['id']}"
            require_string(item["id"], f"{locale}.support.{item['id']}.id")
            require_string(item["question"], f"{locale}.support.{item['id']}.question")
            require_string_list(
                item["answers"],
                f"{locale}.support.{item['id']}.answers",
                expected_length=expected_faq_answer_lengths[item["id"]],
            )

        locale_text = json.dumps(entry, ensure_ascii=False)
        for invariant in (
            "DoseWeek", "Android", "AES-256-GCM", "Health Connect",
            catalog["supportEmail"],
        ):
            assert invariant in locale_text, f"{locale}: missing invariant term {invariant!r}"

        policy_by_id = {section["id"]: section for section in entry["privacy"]["sections"]}
        faq_by_id = {item["id"]: item for item in entry["support"]["faq"]}
        critical_locations = {
            "AES-256-GCM": (policy_by_id["backup"], faq_by_id["backup"]),
            "Health Connect": (policy_by_id["no-collection"], faq_by_id["ai-health"]),
            catalog["supportEmail"]: (policy_by_id["changes"], entry["support"]["contact"]),
            catalog["versionName"]: (
                entry["home"]["versionScope"],
                entry["privacy"]["scope"],
                faq_by_id["accounts"],
                faq_by_id["ai-health"],
                faq_by_id["notifications"],
            ),
        }
        for token, locations in critical_locations.items():
            for location in locations:
                assert token in json.dumps(location, ensure_ascii=False), (
                    f"{locale}: critical location is missing {token!r}"
                )

        backup_answer = faq_by_id["backup"]["answers"][0]
        for phrase in REQUIRED_BACKUP_SECURITY_PHRASES[locale]:
            assert phrase in backup_answer, (
                f"{locale}: backup FAQ lost required security phrase {phrase!r}"
            )
        if locale in REQUIRED_EMERGENCY_SERVICE_PHRASES:
            phrase = REQUIRED_EMERGENCY_SERVICE_PHRASES[locale]
            assert phrase in entry["privacy"]["medicalDisclaimer"]["body"], (
                f"{locale}: privacy disclaimer lost precise emergency-service wording"
            )
            assert phrase in entry["support"]["emergency"]["body"], (
                f"{locale}: support guidance lost precise emergency-service wording"
            )
        if locale == "es":
            assert "descifrar el archivo" in faq_by_id["backup"]["answers"][1], (
                "es: backup FAQ must identify the file as the object that cannot be decrypted"
            )

    serialized = json.dumps(catalog["locales"], ensure_ascii=False).casefold()
    for prohibited in (
        "iphone", "ipad", "ios", "apple health", "healthkit", "apple foundation models",
        "apple intelligence", "systemlanguagemodel", "private cloud compute", "face id",
        "pdf", "visit prep",
    ):
        pattern = rf"(?<![A-Za-z0-9_]){re.escape(prohibited)}(?![A-Za-z0-9_])"
        assert not re.search(pattern, serialized), (
            f"Android catalog contains prohibited token {prohibited!r}"
        )


def rendered_pages(catalog: dict[str, object]) -> dict[Path, str]:
    return {
        ROOT / "android/index.html": page_shell(
            catalog=catalog,
            page="home",
            canonical_path="android/",
            asset_prefix="../",
            home_prefix="./",
            title="DoseWeek for Android",
            description="DoseWeek for Android is a private, local-first record for weekly injection therapy.",
            panels=home_panels(catalog),
        ),
        ROOT / "android/privacy/index.html": page_shell(
            catalog=catalog,
            page="privacy",
            canonical_path="android/privacy/",
            asset_prefix="../../",
            home_prefix="../",
            title="DoseWeek Android Privacy Policy",
            description="Privacy policy for DoseWeek on Android: local records and user-directed encrypted backups.",
            panels=privacy_panels(catalog),
        ),
        ROOT / "android/support/index.html": page_shell(
            catalog=catalog,
            page="support",
            canonical_path="android/support/",
            asset_prefix="../../",
            home_prefix="../",
            title="DoseWeek Android Support",
            description="Support for DoseWeek on Android, including local records and encrypted backup and restore.",
            panels=support_panels(catalog),
        ),
    }


def source_icon(content_path: Path) -> Path:
    resolved = content_path.resolve()
    assert resolved.parent.name == "legal" and resolved.parent.parent.name == "docs", (
        "Android content must be DoseweekPlayStore/docs/legal/android-content.json"
    )
    icon = resolved.parents[2] / ANDROID_ICON_SOURCE
    assert icon.is_file(), f"missing canonical Android icon: {icon}"
    return icon


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--content", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()

    catalog = json.loads(arguments.content.read_text(encoding="utf-8"))
    validate_catalog(catalog)
    pages = rendered_pages(catalog)
    canonical_icon = source_icon(arguments.content)
    if arguments.check:
        for path, expected in pages.items():
            assert path.is_file(), f"missing generated page: {path.relative_to(ROOT)}"
            assert path.read_text(encoding="utf-8") == expected, (
                f"stale generated page: {path.relative_to(ROOT)}; rerun render_android.py"
            )
        assert ANDROID_ICON_PATH.is_file(), "missing generated Android web icon"
        assert ANDROID_ICON_PATH.read_bytes() == canonical_icon.read_bytes(), (
            "assets/android-app-icon.png does not match the Android Google Play icon"
        )
        print(f"OK: {len(pages)} Android pages and icon match {arguments.content}")
        return

    ANDROID_ICON_PATH.write_bytes(canonical_icon.read_bytes())
    for path, content in pages.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    print(f"Rendered {len(pages)} Android pages from {arguments.content}")


if __name__ == "__main__":
    main()
