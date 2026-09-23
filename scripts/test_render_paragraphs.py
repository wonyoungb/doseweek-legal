"""Blank-line blocks in policy paragraphs and FAQ answers render as separate <p> elements."""

import html
import json
import re
import unittest

import render_android
import render_ios


PARAGRAPH = re.compile(r"<p>(.*?)</p>", flags=re.DOTALL)
TAG = re.compile(r"<[^>]+>")


def paragraph_texts(fragment: str) -> list[str]:
    """Plain text of each <p>, with the renderer's inline markup removed and entities decoded."""
    return [html.unescape(TAG.sub("", body)) for body in PARAGRAPH.findall(fragment)]


def element(source: str, tag: str, identifier: str) -> str:
    match = re.search(
        rf'<{tag} id="{re.escape(identifier)}"[^>]*>(.*?)</{tag}>', source, flags=re.DOTALL
    )
    assert match is not None, identifier
    return match.group(1)


class ParagraphBlockTests(unittest.TestCase):
    def test_split_is_on_blank_lines_only(self):
        for module in (render_ios, render_android):
            self.assertEqual(module.paragraph_blocks("A\n\nB\n\nC"), ["A", "B", "C"])
            self.assertEqual(module.paragraph_blocks("one line"), ["one line"])
            self.assertEqual(module.paragraph_blocks("line\nnext"), ["line\nnext"])

    def test_android_policy_section_blocks_are_separate_escaped_paragraphs(self):
        section = {
            "id": "retention",
            "title": "T",
            "paragraphs": ["x < y\n\nhttps://datacenters.google/locations/", "single\nline"],
        }
        rendered = render_android.render_policy_section("en", section)
        url = "https://datacenters.google/locations/"
        self.assertIn(
            f'<div><p>x &lt; y</p><p><a href="{url}">{url}</a></p><p>single\nline</p></div>',
            rendered,
        )

    def test_android_list_items_and_skip_target_are_unchanged(self):
        section = {"id": "no-collection", "title": "T", "paragraphs": ["A\n\nB"], "items": ["i"]}
        rendered = render_android.render_policy_section("ko", section)
        self.assertIn(
            '<h2 id="ko-analytics-overseas-transfer" data-skip-target tabindex="-1">T</h2>'
            "<div><p>A</p><p>B</p><ul><li>i</li></ul></div>",
            rendered,
        )

    def test_ios_faq_blocks_keep_inline_markup_per_block(self):
        item = {
            "question": "Q",
            "answers": [
                f"Uses {render_ios.AI_MODEL_TOKEN}.\n\nSee doseweek-legal.wonyoungchoi.dev/import/",
                "Second & last",
            ],
        }
        rendered = render_ios.faq_details("ar", "faq-ai", item, False)
        self.assertIn(
            '<div class="faq-answer">'
            f"<p>Uses <code>{render_ios.AI_MODEL_TOKEN}</code>.</p>"
            '<p>See <a href="../import/#ar"><bdi dir="ltr">doseweek-legal.wonyoungchoi.dev/import/'
            "</bdi></a></p>"
            "<p>Second &amp; last</p></div>",
            rendered,
        )

    def test_single_block_answers_keep_one_paragraph(self):
        item = {"question": "Q", "answers": ["iOS 1.0.5 notice", "Body"]}
        rendered = render_ios.faq_details("en", "candidate-dates", item, True)
        self.assertEqual(len(PARAGRAPH.findall(rendered)), 2)


class GeneratedContentTests(unittest.TestCase):
    """Round-trip the real website sources: every block becomes one <p>, text preserved."""

    @classmethod
    def setUpClass(cls):
        cls.ios = json.loads(render_ios.CONTENT_PATH.read_text(encoding="utf-8"))
        cls.android = json.loads(
            render_android.CANDIDATE_CONTENT_PATH.read_text(encoding="utf-8")
        )
        cls.ios_privacy = render_ios.rendered(cls.ios)
        cls.ios_support = render_ios.rendered_support(cls.ios)
        pages = render_android.rendered_pages(cls.android)
        cls.android_privacy = pages[render_android.ROOT / "android/privacy/index.html"]
        cls.android_support = pages[render_android.ROOT / "android/support/index.html"]

    def assert_blocks(self, fragment: str, strings: list[str], label: str) -> None:
        expected = [block for text in strings for block in text.split("\n\n")]
        texts = paragraph_texts(fragment)
        self.assertEqual(texts, expected, label)
        for text in texts:
            self.assertNotIn("\n\n", text, label)

    def test_ios_privacy_sections(self):
        split_sections = 0
        for locale, entry in self.ios["locales"].items():
            for section in entry["privacy"]["sections"]:
                identifier = f"{locale}-{section['id']}"
                fragment = element(self.ios_privacy, "section", identifier)
                self.assert_blocks(fragment, section["paragraphs"], identifier)
                split_sections += any("\n\n" in text for text in section["paragraphs"])
        self.assertGreater(split_sections, 0)

    def test_ios_support_answers(self):
        split_answers = 0
        for locale, entry in self.ios["locales"].items():
            support = entry["support"]
            groups = (("released", "faq"), ("candidate", "candidate"),
                      ("secondRelease", "candidate2"))
            for group, prefix in groups:
                for key, item in support[group].items():
                    identifier = f"{locale}-{prefix}-{key}"
                    fragment = element(self.ios_support, "details", identifier)
                    answer = fragment.split('<div class="faq-answer">', 1)[1]
                    self.assert_blocks(answer, item["answers"], identifier)
                    split_answers += any("\n\n" in text for text in item["answers"])
        self.assertGreater(split_answers, 0)

    def test_android_privacy_sections(self):
        split_sections = 0
        for locale, entry in self.android["locales"].items():
            for section in entry["privacy"]["sections"]:
                identifier = f"{locale}-{section['id']}"
                fragment = element(self.android_privacy, "section", identifier)
                self.assert_blocks(fragment, section["paragraphs"], identifier)
                split_sections += any("\n\n" in text for text in section["paragraphs"])
        self.assertGreater(split_sections, 0)

    def test_android_support_answers(self):
        for locale, entry in self.android["locales"].items():
            for item in entry["support"]["faq"]:
                identifier = f"{locale}-{item['id']}"
                fragment = element(self.android_support, "details", identifier)
                answer = fragment.split('<div class="faq-answer">', 1)[1]
                self.assert_blocks(answer, item["answers"], identifier)


if __name__ == "__main__":
    unittest.main()
