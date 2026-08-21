#!/usr/bin/env python3
"""Dependency-free structural checks for the DoseWeek static pages."""

from __future__ import annotations

import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = [ROOT / "index.html", ROOT / "support/index.html", ROOT / "privacy/index.html"]
LANGUAGES = ["en", "ja", "ko"]


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.panel_languages: list[str] = []
        self.language_links: list[tuple[str, str | None, str | None]] = []
        self.references: list[tuple[str, str]] = []
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        element_id = values.get("id")
        if element_id:
            self.ids.append(element_id)

        classes = set((values.get("class") or "").split())
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
        if split.scheme != "mailto":
            raise AssertionError(f"{source.relative_to(ROOT)}: external reference {reference!r}")
        return None

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


def main() -> None:
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "--catalog",
        type=Path,
        help="optional path to the app's Localizable.xcstrings for verbatim policy comparison",
    )
    arguments = argument_parser.parse_args()

    pages = {path.resolve(): parse(path) for path in HTML_FILES}

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
    support_text = " ".join(pages[(ROOT / "support/index.html").resolve()].text)

    for required in (
        "Effective date: August 21, 2026",
        "施行日: 2026年8月21日",
        "시행일: 2026년 8월 21일",
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

    if arguments.catalog:
        catalog_check(arguments.catalog.resolve(), privacy_text)

    suffix = ", and app-catalog parity" if arguments.catalog else ""
    print(f"OK: {len(HTML_FILES)} pages, local links, locale panels, critical disclosures{suffix}")


if __name__ == "__main__":
    main()
