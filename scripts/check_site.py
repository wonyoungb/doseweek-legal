#!/usr/bin/env python3
"""Dependency-free structural checks for the DoseWeek static pages."""

from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = [ROOT / "index.html", ROOT / "support/index.html", ROOT / "privacy/index.html"]
LANGUAGES = ["en", "ja", "ko"]
SITE_BASE = "https://wonyoungb.github.io/doseweek-legal/"
SOCIAL_IMAGE = f"{SITE_BASE}assets/app-icon.png"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.panel_languages: list[str] = []
        self.language_links: list[tuple[str, str | None, str | None]] = []
        self.references: list[tuple[str, str]] = []
        self.metadata: dict[str, str] = {}
        self.link_relations: dict[str, str] = {}
        self.summary_markers: list[list[str | None]] = []
        self._summary_marker_values: list[str | None] | None = None
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        element_id = values.get("id")
        if element_id:
            self.ids.append(element_id)

        classes = set((values.get("class") or "").split())
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

        if tag == "summary":
            assert self._summary_marker_values is None, "nested summary elements are invalid"
            self._summary_marker_values = []
        elif self._summary_marker_values is not None and "summary-symbol" in classes:
            self._summary_marker_values.append(values.get("aria-hidden"))

        if "language-panel" in classes:
            language = values.get("data-language")
            if language:
                self.panel_languages.append(language)

        language_link = values.get("data-language-link")
        if language_link:
            self.language_links.append((language_link, values.get("aria-current"), values.get("lang")))

        for attribute in ("href", "src"):
            reference = values.get(attribute)
            if reference:
                self.references.append((attribute, reference))

    def handle_endtag(self, tag: str) -> None:
        if tag == "summary" and self._summary_marker_values is not None:
            self.summary_markers.append(self._summary_marker_values)
            self._summary_marker_values = None

    def handle_data(self, data: str) -> None:
        stripped = " ".join(data.split())
        if stripped:
            self.text.append(stripped)


def parse(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser


def local_target(source: Path, reference: str) -> tuple[Path, str] | None:
    split = urlsplit(reference)
    if split.scheme or split.netloc:
        if split.scheme == "mailto":
            return None
        if reference.startswith(SITE_BASE):
            relative_path = unquote(split.path.removeprefix("/doseweek-legal/"))
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
    for number in range(1, 9):
        keys.extend((f"privacy.section{number}.title", f"privacy.section{number}.body"))
    keys.extend(("privacy.medical.title", "privacy.medical.body", "common.notAMedicalDevice"))

    for key in keys:
        assert key in catalog, f"catalog: missing source-of-truth key {key!r}"
        for language in ("en", "ja", "ko"):
            value = catalog[key]["localizations"][language]["stringUnit"]["value"]
            normalized = " ".join(value.split())
            assert normalized in privacy_text, (
                f"privacy/index.html: {key} ({language}) does not match the app catalog"
            )


def assert_css_minimum(css: str, selector: str, property_name: str, minimum: int) -> None:
    match = re.search(rf"{re.escape(selector)}\s*\{{(?P<body>[^}}]+)\}}", css)
    assert match, f"assets/site.css: missing {selector!r} rule"
    value = re.search(rf"{re.escape(property_name)}:\s*(\d+)px", match.group("body"))
    assert value and int(value.group(1)) >= minimum, (
        f"assets/site.css: {selector} must set {property_name} to at least {minimum}px"
    )


def main() -> None:
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "--catalog",
        type=Path,
        help="optional path to the app's Localizable.xcstrings for verbatim policy comparison",
    )
    arguments = argument_parser.parse_args()

    pages = {path.resolve(): parse(path) for path in HTML_FILES}

    expected_metadata = {
        (ROOT / "index.html").resolve(): (SITE_BASE, "assets/app-icon.png"),
        (ROOT / "support/index.html").resolve(): (f"{SITE_BASE}support/", "../assets/app-icon.png"),
        (ROOT / "privacy/index.html").resolve(): (f"{SITE_BASE}privacy/", "../assets/app-icon.png"),
    }

    for path, page in pages.items():
        label = path.relative_to(ROOT)
        duplicates = sorted({element_id for element_id in page.ids if page.ids.count(element_id) > 1})
        assert not duplicates, f"{label}: duplicate IDs {duplicates}"
        assert page.panel_languages == LANGUAGES, (
            f"{label}: panels must stay in no-script order {LANGUAGES}, got {page.panel_languages}"
        )
        assert [language for language, _, _ in page.language_links] == ["ko", "en", "ja"], (
            f"{label}: expected ko/en/ja language links"
        )
        assert [declared for _, _, declared in page.language_links] == ["ko", "en", "ja"], (
            f"{label}: every language link must declare its own lang"
        )
        current = [language for language, state, _ in page.language_links if state == "true"]
        assert current == [], f"{label}: static markup must not misstate aria-current before JS"

        canonical, touch_icon = expected_metadata[path]
        assert page.link_relations.get("canonical") == canonical, f"{label}: wrong canonical URL"
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
        assert page.metadata.get("og:image") == SOCIAL_IMAGE, f"{label}: wrong og:image"
        assert page.metadata.get("twitter:card") == "summary", f"{label}: wrong twitter:card"
        assert page.metadata.get("twitter:image") == SOCIAL_IMAGE, f"{label}: wrong twitter:image"

        for attribute, reference in page.references:
            resolved = local_target(path, reference)
            if resolved is None:
                continue
            target, fragment = resolved
            assert target.exists(), f"{label}: broken {attribute}={reference!r}"
            if fragment and target.suffix == ".html":
                target_page = pages.get(target.resolve()) or parse(target)
                assert fragment in target_page.ids, f"{label}: missing target for {reference!r}"

    privacy_text = " ".join(pages[(ROOT / "privacy/index.html").resolve()].text)
    support_page = pages[(ROOT / "support/index.html").resolve()]
    support_text = " ".join(support_page.text)
    css = (ROOT / "assets/site.css").read_text(encoding="utf-8")

    for required in (
        "Effective date: August 22, 2026",
        "施行日: 2026年8月22日",
        "시행일: 2026년 8월 22일",
        "weight, body fat percentage, lean body mass, and waist circumference",
        "体重、体脂肪率、除脂肪体重、ウエスト周囲径",
        "체중, 체지방률, 제지방량, 허리둘레",
        "SystemLanguageModel.default",
        "Private Cloud Compute",
        "AES-256-GCM",
    ):
        assert required in privacy_text, f"privacy/index.html: missing required disclosure {required!r}"

    assert privacy_text.count("SystemLanguageModel.default") == 3, (
        "privacy/index.html: SystemLanguageModel.default must appear once per language"
    )
    assert support_text.count("SystemLanguageModel.default") == 3, (
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
        "DoseWeek를 재실행",
        "삭제된 기록은 복원되지 않습니다.",
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
    ):
        assert overclaim not in privacy_text and overclaim not in support_text, (
            f"site must not overclaim physical deletion timing: {overclaim!r}"
        )

    for app_lock_guidance in (
        "App Lock cannot be turned off without authentication.",
        "認証せずにアプリロックをオフにすることはできません。",
        "인증 없이는 앱 잠금을 끌 수 없습니다.",
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

    assert len(support_page.summary_markers) == 24, (
        "support/index.html: expected eight FAQ disclosures in each language"
    )
    assert all(markers == ["true"] for markers in support_page.summary_markers), (
        "support/index.html: every summary needs one aria-hidden summary-symbol"
    )
    assert ".faq-list summary::after" not in css, (
        "assets/site.css: disclosure state must not pollute the summary accessible name"
    )
    assert 'content: "+"' not in css and 'content: "−"' not in css, (
        "assets/site.css: disclosure icons must be drawn without accessible text"
    )

    assert_css_minimum(css, ".brand", "min-height", 44)
    assert_css_minimum(css, ".brand", "min-width", 44)
    assert_css_minimum(css, ".policy-toc a", "min-height", 44)
    assert_css_minimum(css, ".page-link", "min-height", 44)
    assert "clip-path: inset(50%)" not in css, (
        "assets/site.css: mobile layout must keep the DoseWeek brand label visible"
    )

    if arguments.catalog:
        catalog_check(arguments.catalog.resolve(), privacy_text)

    suffix = ", and app-catalog parity" if arguments.catalog else ""
    print(
        f"OK: {len(HTML_FILES)} pages, local links, locale panels, social metadata, "
        f"accessible FAQ markers, 44px key targets, critical disclosures{suffix}"
    )


if __name__ == "__main__":
    main()
