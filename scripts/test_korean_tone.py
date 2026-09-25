"""Self-tests for scripts/korean_tone.py (Toss-style 해요체 voice check).

The engine tests are identical in the iOS, Android and website repositories; the loader tests
at the end cover this repository's string sources.

    python3 -m unittest discover -s scripts -p test_korean_tone.py
"""

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import korean_tone  # noqa: E402

RULES = korean_tone.load_rules()


def rules_of(text):
    return [finding["rule"] for finding in korean_tone.check_text(text, RULES)]


def suggestion(text):
    return korean_tone.check_text(text, RULES)[0]["suggestion"]


class EngineIdentityTests(unittest.TestCase):
    def test_engine_matches_pinned_hash_in_shared_rule_data(self):
        data = json.loads(korean_tone.RULES_PATH.read_text(encoding="utf-8"))
        digest = hashlib.sha256(korean_tone.engine_source().encode("utf-8")).hexdigest()
        self.assertEqual(digest, data["engine_sha256"],
                         "engine changed: update all three repositories and the pinned hash")


class EndingRuleTests(unittest.TestCase):
    def test_formal_endings_are_flagged(self):
        for text in ("기록을 저장했습니다.", "백업이 필요합니다", "기록이 삭제됩니다.",
                     "이 앱은 의료기기가 아닙니다.", "설정을 확인하십시오.", "기록을 삭제하시겠습니까?",
                     "저장되었습니다.", "앱을 다시 여십시오", "파일이 있습니까?"):
            with self.subTest(text=text):
                self.assertEqual(rules_of(text), ["ending"])

    def test_plain_endings_are_flagged(self):
        for text in ("기록을 저장한다.", "기록이 삭제된다.", "이 값은 추정치이다.", "알림을 끈다"):
            with self.subTest(text=text):
                self.assertEqual(rules_of(text), ["ending"])

    def test_haeyo_sentences_and_questions_pass(self):
        for text in ("기록을 저장했어요.", "이 기록을 삭제할까요?", "알림을 받을까요?",
                     "설정에서 바꿀 수 있어요.", "다시 시도해 주세요.", "어떤 기록을 볼까요?"):
            with self.subTest(text=text):
                self.assertEqual(rules_of(text), [])

    def test_labels_ending_in_a_noun_or_stem_pass(self):
        for text in ("저장", "취소", "기록 추가", "다음 주사 예정일", "입력하지 않음", "완료",
                     "비교 기준보다", "모든 로컬 기록 삭제", "%lld개 날짜 선택됨"):
            with self.subTest(text=text):
                self.assertEqual(rules_of(text), [])

    def test_only_the_sentence_end_counts(self):
        self.assertEqual(rules_of("저장했습니다만 동기화는 나중에 해요."), [])
        self.assertEqual(rules_of("기록은 기기에 있어요. 개발자에게 보내지 않습니다."), ["ending"])

    def test_quoted_term_is_not_the_sentence_ending(self):
        self.assertEqual(rules_of("버튼 이름을 ‘확인했습니다’로 바꾸지 않아요."), [])
        self.assertEqual(rules_of("화면에 “저장합니다”가 보여요"), [])
        self.assertEqual(rules_of("‘저장’을 누르면 기록이 저장됩니다."), ["ending"])

    def test_placeholders_inside_sentences(self):
        for text in ("%@ 기록을 저장했습니다.", "%lld개 기록이 삭제됩니다.", "%1$s의 %2$d번째 기록입니다.",
                     "%d개를 가져왔습니다"):
            with self.subTest(text=text):
                self.assertEqual(rules_of(text), ["ending"])
        self.assertEqual(rules_of("%1$s에 %2$d개 저장했어요."), [])
        self.assertEqual(rules_of("남은 횟수 %1$d"), [])
        self.assertEqual(suggestion("%1$s의 %2$d번째 기록입니다."), "%1$s의 %2$d번째 기록이에요.")

    def test_formal_rewrites(self):
        cases = {
            "기록을 저장했습니다.": "기록을 저장했어요.",
            "기록이 삭제됩니다.": "기록이 삭제돼요.",
            "이 앱은 의료기기가 아닙니다.": "이 앱은 의료기기가 아니에요.",
            "설정을 확인하십시오.": "설정을 확인하세요.",
            "기록을 삭제하시겠습니까?": "기록을 삭제할까요?",
            "값이 서로 다릅니다.": "값이 서로 달라요.",
            "파일을 보냅니다.": "파일을 보내요.",
            "그대로입니다.": "그대로예요.",
            "개인 기록 도구입니다.": "개인 기록 도구예요.",
            "기록이 없습니다.": "기록이 없어요.",
            "알림을 끕니다.": "알림을 꺼요.",
            "기록을 저장한다.": "기록을 저장해요.",
            "알림을 끈다": "알림을 꺼요.",
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(suggestion(text), expected)


class HonorificRuleTests(unittest.TestCase):
    def test_stacked_and_filler_honorifics_are_flagged(self):
        self.assertIn("honorific", rules_of("설정에서 바꾸실 수 있으십니다."))
        self.assertIn("honorific", rules_of("백업 파일을 확인하시기 바랍니다."))
        self.assertIn("honorific", rules_of("새 기능을 안내드립니다."))
        self.assertIn("honorific", rules_of("변경 내용을 알려 드립니다."))

    def test_plain_polite_requests_pass(self):
        for text in ("설정에서 바꿀 수 있어요.", "백업 파일을 확인해 주세요.", "새 기능을 알려 드려요.",
                     "필요하면 도와드릴게요."):
            with self.subTest(text=text):
                self.assertEqual(rules_of(text), [])

    def test_honorific_rewrites(self):
        self.assertEqual(suggestion("설정에서 바꾸실 수 있으십니다."), "설정에서 바꿀 수 있어요.")
        self.assertEqual(suggestion("백업 파일을 확인하시기 바랍니다."), "백업 파일을 확인해 주세요.")
        self.assertEqual(suggestion("새 기능을 안내드립니다."), "새 기능을 알려 드려요.")


class JargonRuleTests(unittest.TestCase):
    def test_jargon_is_flagged_with_its_plain_word(self):
        cases = {
            "체중을 기입하세요.": "기입 -> 입력",
            "금일 기록을 확인하세요.": "금일 -> 오늘",
            "익일 알림을 보내요.": "익일 -> 다음 날",
            "상기 내용을 확인하세요.": "상기 -> 위",
            "해당 기록을 삭제할까요?": "해당 -> 이/그",
            "미입력 항목이 있어요.": "미입력 -> 입력하지 않음",
            "백업을 진행할까요?": "진행하다 -> (name the real action)",
        }
        for text, detail in cases.items():
            with self.subTest(text=text):
                findings = korean_tone.check_text(text, RULES)
                self.assertEqual([(item["rule"], item["detail"]) for item in findings], [("jargon", detail)])

    def test_plain_words_and_lookalikes_pass(self):
        for text in ("체중을 입력하세요.", "오늘 기록을 확인하세요.", "지금 일정을 확인하세요.",
                     "이 기록을 삭제할까요?", "진행 중", "‘해당’ 대신 ‘이’를 써요."):
            with self.subTest(text=text):
                self.assertEqual(rules_of(text), [])

    def test_jargon_rewrites(self):
        self.assertEqual(suggestion("해당 기록을 삭제할까요?"), "이 기록을 삭제할까요?")
        self.assertEqual(suggestion("금일 기록을 기입하세요."), "오늘 기록을 입력하세요.")

    def test_jargon_list_lives_in_the_shared_rule_data(self):
        data = json.loads(korean_tone.RULES_PATH.read_text(encoding="utf-8"))
        terms = {item["term"] for item in data["jargon"]}
        self.assertEqual(terms, {"기입", "금일", "익일", "상기", "해당", "미입력", "진행하다"})


class GlossaryRuleTests(unittest.TestCase):
    def test_feature_names_are_flagged(self):
        self.assertEqual(rules_of("부작용 기록"), ["glossary"])
        self.assertEqual(rules_of("증상 기록을 저장했어요."), ["glossary"])
        self.assertEqual(suggestion("부작용 모아보기"), "컨디션 모아보기")

    def test_feature_name_and_quoted_old_name_pass(self):
        self.assertEqual(rules_of("컨디션 기록을 저장했어요."), [])
        self.assertEqual(rules_of("‘부작용’ 메뉴는 ‘컨디션’으로 바뀌었어요."), [])

    def test_reviewed_allow_list_suppresses_a_legitimate_use(self):
        violation = {"file": "a.json", "key": "safety", "rule": "glossary", "sentence": "증상이 심하면 상담하세요."}
        entry = {"key": "safety", "rule": "glossary", "reason": "clinical advice", "match": "증상이 심하면"}
        self.assertTrue(korean_tone.allowed(violation, entry))
        self.assertFalse(korean_tone.allowed(dict(violation, key="other"), entry))
        self.assertFalse(korean_tone.allowed(dict(violation, rule="jargon"), entry))


class NounStatusRuleTests(unittest.TestCase):
    def test_whole_status_messages_ending_in_a_noun_are_flagged(self):
        cases = {
            "백업 완료": "백업했어요.",
            "내보내기 준비 완료.": "내보내기 준비했어요.",
            "업데이트 실패": "업데이트하지 못했어요.",
            "저장 불가": "저장할 수 없어요.",
            "%@ 가져오기 완료": "%@ 가져오기를 마쳤어요.",
            "가져오기 실패": "가져오지 못했어요.",
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(rules_of(text), ["noun-status"])
                self.assertEqual(suggestion(text), expected)

    def test_short_labels_and_noun_phrases_pass(self):
        for text in ("완료", "실패", "완료된 기록", "저장 불가능한 항목", "가능"):
            with self.subTest(text=text):
                self.assertEqual(rules_of(text), [])

    def test_noun_heading_inside_a_longer_message_passes(self):
        self.assertEqual(rules_of("백업 완료\n파일을 안전한 곳에 보관하세요."), [])


class AuditTests(unittest.TestCase):
    def test_audit_counts_and_stale_allow_list_entries(self):
        entries = [("a.json", "one", "기록을 저장했습니다."), ("a.json", "two", "저장했어요."),
                   ("a.json", "three", "증상이 심하면 상담하세요.")]
        allowlist = [{"key": "three", "rule": "glossary", "reason": "clinical advice"},
                     {"key": "gone", "rule": "ending", "reason": "old"}]
        violations, suppressed, stale, sentences = korean_tone.audit(entries, RULES, allowlist)
        self.assertEqual([(item["key"], item["rule"]) for item in violations], [("one", "ending")])
        self.assertEqual(len(suppressed), 1)
        self.assertEqual(stale, [allowlist[1]])
        self.assertEqual(sentences, 3)

    def test_allow_list_entries_need_a_reason(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "allow.json"
            path.write_text(json.dumps({"entries": [{"key": "k", "rule": "glossary", "reason": ""}]}))
            with self.assertRaises(ValueError):
                korean_tone.load_allowlist(path)

    def test_repository_allow_list_is_valid(self):
        for entry in korean_tone.load_allowlist():
            self.assertIn(entry["rule"], korean_tone.RULE_IDS)


class WebsiteLoaderTests(unittest.TestCase):
    def test_loads_only_the_ko_locale_with_json_paths(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "docs").mkdir()
            (root / "import").mkdir()
            (root / "docs/ios-content.json").write_text(json.dumps({"locales": {
                "ko": {"privacy": {"sections": [{"title": "보관", "paragraphs": ["기록은 기기에 남습니다."]}]}},
                "en": {"privacy": {"sections": [{"title": "Storage", "paragraphs": ["Records stay."]}]}},
            }}, ensure_ascii=False))
            (root / "docs/home-content.json").write_text(json.dumps(
                {"ko": {"title": "나의 기록", "intro": "‘해당’ 없이 써요."}, "en": {"title": "Mine"}},
                ensure_ascii=False))
            (root / "import/content.json").write_text(json.dumps(
                {"locales": {"ko": {"steps": [{"body": "증상 행은 저장할 수 없습니다."}]}}}, ensure_ascii=False))
            entries, files = korean_tone.load_entries(root)
        self.assertEqual(files, ["docs/home-content.json", "docs/ios-content.json", "import/content.json"])
        keys = [key for _, key, _ in entries]
        self.assertIn("locales.ko.privacy.sections[0].paragraphs[0]", keys)
        self.assertIn("ko.intro", keys)
        self.assertNotIn("locales.en.privacy.sections[0].paragraphs[0]", keys)
        violations, _, _, _ = korean_tone.audit(entries, RULES, [])
        found = sorted((item["key"], item["rule"]) for item in violations)
        self.assertEqual(found, [("locales.ko.privacy.sections[0].paragraphs[0]", "ending"),
                                 ("locales.ko.steps[0].body", "ending"),
                                 ("locales.ko.steps[0].body", "glossary")])

    def test_generator_label_tables_and_templates(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "scripts").mkdir()
            (root / "templates").mkdir()
            (root / "scripts/render_demo.py").write_text(
                "LABELS = {'ko': ('파일 선택', '기록을 추가합니다'), 'en': ('Choose', 'Add')}\n", encoding="utf-8")
            (root / "templates/home.html").write_text(
                '<html><head><title>나의 기록</title></head><body><p lang="ko">저장됩니다.</p></body></html>',
                encoding="utf-8")
            entries, _ = korean_tone.load_entries(root)
        texts = sorted(text for _, _, text in entries)
        self.assertEqual(texts, ["기록을 추가합니다", "나의 기록", "저장됩니다.", "파일 선택"])

    def test_repository_sources_exclude_generated_pages(self):
        _, files = korean_tone.load_entries()
        self.assertIn("docs/ios-content.json", files)
        self.assertIn("docs/android-content.candidate.json", files)
        self.assertIn("docs/help-navigation.json", files)
        self.assertIn("import/content.json", files)
        self.assertFalse([file for file in files if file.endswith(".md") or file.startswith(("privacy/", "support/"))])


if __name__ == "__main__":
    unittest.main()
