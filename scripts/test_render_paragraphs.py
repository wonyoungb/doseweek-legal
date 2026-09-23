"""Blank-line blocks in policy paragraphs and FAQ answers render as separate <p> elements.

Also covers the readability rules: a single "\n" in a policy block renders as <br>, reviewed
processor URLs may wrap after a path "/" and stay left-to-right in RTL text, an Android policy
list follows the paragraph that introduces it, and the iOS deletion FAQ names the delete action
once.
"""

import html
import json
import re
import unittest

import render_android
import render_ios


PARAGRAPH = re.compile(r"<p>(.*?)</p>", flags=re.DOTALL)
TAG = re.compile(r"<[^>]+>")
POLICY_URLS = (
    "https://privacy.google.com/businesses/processorsupport",
    "https://datacenters.google/locations/",
    "https://business.safety.google/adssubprocessors/",
    "https://business.safety.google/adsprocessorterms/",
)
# settings.deleteAll in the iOS app catalog (apps/ios DoseDay/Resources/Localizable.xcstrings)
IOS_DELETE_ALL_LABELS = {
    "ko": "모든 로컬 기록 삭제",
    "en": "Delete all local records",
    "ja": "すべてのローカル記録を削除",
    "de": "Alle lokalen Einträge löschen",
    "fr": "Supprimer tous les enregistrements locaux",
    "es": "Eliminar todos los registros locales",
    "it": "Elimina tutte le registrazioni locali",
    "nl": "Alle lokale registraties verwijderen",
    "pt-PT": "Eliminar todos os registos locais",
    "pl": "Usuń wszystkie lokalne wpisy",
    "sv": "Radera alla lokala registreringar",
    "hi": "सभी लोकल रिकॉर्ड हटाएँ",
    "pt-BR": "Excluir todos os registros locais",
    "ar": "حذف جميع السجلات المحلية",
    "zh-Hans": "删除所有本地记录",
    "zh-Hant": "刪除所有本機紀錄",
    "tr": "Tüm yerel kayıtları sil",
}


def paragraph_texts(fragment: str) -> list[str]:
    """Plain text of each <p>: <br> becomes the source "\\n", other inline markup is removed."""
    return [
        html.unescape(TAG.sub("", body.replace("<br>", "\n")))
        for body in PARAGRAPH.findall(fragment)
    ]


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
            f'<div><p>x &lt; y</p><p><a href="{url}"><bdi dir="ltr">'
            "https://datacenters.google/<wbr>locations/</bdi></a></p><p>single<br>line</p></div>",
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

    def test_android_list_follows_the_paragraph_that_introduces_it(self):
        section = {
            "id": "no-collection", "title": "T",
            "paragraphs": ["Lead:", "Detail\n\nMore", "Last"], "items": ["i", "j"],
        }
        rendered = render_android.render_policy_section("en", section)
        self.assertIn(
            "<div><p>Lead:</p><ul><li>i</li><li>j</li></ul>"
            "<p>Detail</p><p>More</p><p>Last</p></div>",
            rendered,
        )
        without_items = {"id": "changes", "title": "T", "paragraphs": ["A", "B"]}
        self.assertNotIn("<ul>", render_android.render_policy_section("en", without_items))

    def test_single_newline_in_a_policy_block_is_a_line_break(self):
        for module in (render_ios, render_android):
            self.assertEqual(
                module.privacy_paragraph("Contact us below.\nwonyoung@wonyoungchoi.dev"),
                "Contact us below.<br>wonyoung@wonyoungchoi.dev",
            )
            self.assertEqual(module.privacy_paragraph("a < b"), "a &lt; b")

    def test_reviewed_urls_wrap_only_after_path_slashes(self):
        for module in (render_ios, render_android):
            self.assertEqual(
                module.breakable_url("https://privacy.google.com/businesses/processorsupport"),
                "https://privacy.google.com/<wbr>businesses/<wbr>processorsupport",
            )
            self.assertEqual(
                module.breakable_url("https://datacenters.google/locations/"),
                "https://datacenters.google/<wbr>locations/",
            )
            for url in POLICY_URLS:
                rendered = module.privacy_paragraph(f"See {url}")
                self.assertEqual(rendered.count(f'<a href="{url}">'), 1, url)
                link_text = re.search(r'<a [^>]*><bdi dir="ltr">(.*?)</bdi></a>', rendered).group(1)
                self.assertEqual(link_text.replace("<wbr>", ""), url)
                self.assertNotIn("://<wbr>", link_text)
                self.assertFalse(link_text.endswith("<wbr>"), url)

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

    def test_ios_contact_email_is_on_its_own_line(self):
        email = self.ios["supportEmail"]
        for locale in self.ios["localeOrder"]:
            fragment = element(self.ios_privacy, "section", f"{locale}-contact")
            self.assertEqual(fragment.count(f"<br>{email}</p>"), 1, locale)

    def test_policy_urls_render_with_wrap_points_and_exact_text(self):
        for page in (self.ios_privacy, self.android_privacy):
            links = re.findall(r'<a href="(https://[^"]+)">(.*?)</a>', page)
            policy_links = [(href, text) for href, text in links if href in POLICY_URLS]
            self.assertEqual(len(policy_links), 4 * 17)
            for href, text in policy_links:
                self.assertTrue(text.startswith('<bdi dir="ltr">'), href)
                self.assertIn("<wbr>", text)
                self.assertEqual(TAG.sub("", text), href)

    def test_android_lists_follow_their_lead_in_paragraph(self):
        for locale, entry in self.android["locales"].items():
            for section in entry["privacy"]["sections"]:
                if not section.get("items"):
                    continue
                identifier = f"{locale}-{section['id']}"
                body = element(self.android_privacy, "section", identifier).split("<div>", 1)[1]
                lead = "".join(
                    f"<p>{render_android.privacy_paragraph(block)}</p>"
                    for block in render_android.paragraph_blocks(section["paragraphs"][0])
                )
                self.assertTrue(body.startswith(lead + "<ul>"), identifier)
                self.assertEqual(body.count("<ul>"), 1, identifier)
                self.assertEqual(body.count("<li>"), len(section["items"]), identifier)

    def test_ios_deletion_faq_names_the_delete_action_once(self):
        self.assertEqual(list(IOS_DELETE_ALL_LABELS), self.ios["localeOrder"])
        for locale, label in IOS_DELETE_ALL_LABELS.items():
            answers = self.ios["locales"][locale]["support"]["released"]["deletion"]["answers"]
            self.assertEqual(len(answers), 2, locale)
            text = " ".join(answers).casefold()
            self.assertEqual(text.count(label.casefold()), 1, locale)
            self.assertIn(label.casefold(), answers[0].casefold(), locale)
            self.assertIn("iOS", answers[1].split("\n\n", 1)[0], locale)

    def test_android_support_answers(self):
        for locale, entry in self.android["locales"].items():
            for item in entry["support"]["faq"]:
                identifier = f"{locale}-{item['id']}"
                fragment = element(self.android_support, "details", identifier)
                answer = fragment.split('<div class="faq-answer">', 1)[1]
                self.assert_blocks(answer, item["answers"], identifier)


if __name__ == "__main__":
    unittest.main()
