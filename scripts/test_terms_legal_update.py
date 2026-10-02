"""1.0.6 subscription/consumer-rights guards; these assertions fail on the old copy.

The latest owner/spec decision overrides earlier price examples. The candidate
integration must carry every original billing paragraph rather than silently replace it.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALES = ("ko", "en", "ja", "de", "fr", "es", "it", "nl", "pt-PT", "pl", "sv", "hi", "pt-BR", "ar", "zh-Hans", "zh-Hant", "tr")

# Independent semantic anchors prevent numeric-only translations from passing.
ANCHORS = {
    "ko": ("첫 구독", "명시적 동의", "법률", "영업일", "계정"),
    "en": ("first-time subscribers", "affirmative consent", "statutory", "business days", "account"),
    "ja": ("初回", "明示的な同意", "法定", "営業日", "アカウント"),
    "de": ("Erstabonnenten", "ausdrückliche Zustimmung", "gesetzlichen", "Werktagen", "Konto"),
    "fr": ("premier abonnement", "consentement exprès", "légaux", "jours ouvrables", "compte"),
    "es": ("primera suscripción", "consentimiento expreso", "legales", "días hábiles", "cuenta"),
    "it": ("primo abbonamento", "consenso esplicito", "legali", "giorni lavorativi", "account"),
    "nl": ("eerste abonnement", "uitdrukkelijke toestemming", "wettelijke", "werkdagen", "account"),
    "pt-PT": ("primeira subscrição", "consentimento expresso", "legais", "dias úteis", "conta"),
    "pl": ("pierwszej subskrypcji", "wyraźna zgoda", "ustawowych", "dni roboczych", "konto"),
    "sv": ("första prenumeration", "uttryckligt samtycke", "lagstadgade", "arbetsdagar", "konto"),
    "hi": ("पहली सदस्यता", "स्पष्ट सहमति", "कानूनी", "कार्यदिवस", "खाता"),
    "pt-BR": ("primeira assinatura", "consentimento expresso", "legais", "dias úteis", "conta"),
    "ar": ("المشتركين لأول مرة", "موافقة صريحة", "القانونية", "أيام عمل", "حساب"),
    "zh-Hans": ("首次订阅", "明确同意", "法定", "工作日", "账号"),
    "zh-Hant": ("首次訂閱", "明確同意", "法定", "工作日", "帳號"),
    "tr": ("ilk kez abone", "açık onay", "yasal", "iş günü", "hesap"),
}


def content():
    return json.loads((ROOT / "docs/terms-content.json").read_text(encoding="utf-8"))


def sections(entry):
    return {item["id"]: item for item in entry["sections"]}


class TermsLegalUpdateTest(unittest.TestCase):
    def test_all_17_locales_keep_final_prices_and_store_localization(self):
        source = content()
        self.assertEqual(tuple(source["localeOrder"]), LOCALES)
        for loc, entry in source["locales"].items():
            with self.subTest(locale=loc):
                prices = sections(entry)["free-plus"]["paragraphs"][2]
                for token in ("USD 1.99", "USD 13.99", "KRW 3,300", "KRW 19,900", "JPY 300", "JPY 1,980"):
                    self.assertIn(token, prices, "superseding owner/spec price is missing")
                self.assertNotIn("2,900", prices)
                self.assertNotIn("22,000", prices)

    def test_calendar_month_trial_uses_store_eligibility_for_first_time_subscribers(self):
        for loc, entry in content()["locales"].items():
            with self.subTest(locale=loc):
                offer = sections(entry)["free-plus"]["paragraphs"][2]
                self.assertIn(ANCHORS[loc][0], offer)
                self.assertIn("1", offer)
                self.assertNotRegex(offer, r"(?<![\d,])30(?![\d,])", "calendar month trial must not become 30 days")
                self.assertTrue("App Store" in offer and "Google Play" in offer, "Store decides eligibility and offer")

    def test_korean_conversion_and_increase_need_affirmative_preceding_30_day_consent(self):
        for loc, entry in content()["locales"].items():
            with self.subTest(locale=loc):
                billing = sections(entry)["billing"]["paragraphs"][1]
                self.assertIn(ANCHORS[loc][1], billing)
                self.assertIn("30", billing)
        ko = sections(content()["locales"]["ko"])["billing"]["paragraphs"][1]
        for token in ("전환·인상 전 30일 이내", "이전·새 가격", "결제방법", "취소 조건·방법·효과", "묵시적"):
            self.assertIn(token, ko)

    def test_store_refund_policy_preserves_statutory_rights_and_korean_time_limits(self):
        for loc, entry in content()["locales"].items():
            with self.subTest(locale=loc):
                billing = sections(entry)["billing"]["paragraphs"][1]
                self.assertIn(ANCHORS[loc][2], billing)
                self.assertIn(ANCHORS[loc][3], billing)
                for number in ("7", "3", "30"):
                    self.assertIn(number, billing)
        en = sections(content()["locales"]["en"])["billing"]["paragraphs"][1]
        for token in ("3 months", "30 days", "3 business days", "unprovided", "do not limit"):
            self.assertIn(token, en)

    def test_app_store_trial_is_not_described_as_immediate_payment(self):
        for loc, entry in content()["locales"].items():
            with self.subTest(locale=loc):
                sub = sections(entry)["billing"]["subsections"][0]
                text = " ".join(sub["paragraphs"])
                self.assertIn(ANCHORS[loc][0], text)
                self.assertIn("1", text)
                self.assertGreaterEqual(text.count("24"), 2)
                self.assertNotIn("Android", text)
                self.assertNotIn("Google Play", text)

    def test_annual_and_us_renewal_notice_windows_are_not_assumed_covered(self):
        for loc, entry in content()["locales"].items():
            with self.subTest(locale=loc):
                billing = sections(entry)["billing"]["paragraphs"][1]
                for interval in ("50–20", "15–45", "7–30"):
                    self.assertIn(interval, billing)

    def test_current_operator_and_optional_account_replace_retired_claims(self):
        for loc, entry in content()["locales"].items():
            with self.subTest(locale=loc):
                by_id = sections(entry)
                self.assertIn("Wonyoung Labs", by_id["service"]["paragraphs"][0])
                self.assertIn(ANCHORS[loc][4], by_id["records"]["paragraphs"][0])
        en = json.dumps(content()["locales"]["en"])
        for stale in ("an individual developer", "there is no DoseWeek account", "DoseWeek has no account", "Plus does not change where"):
            self.assertNotIn(stale, en)

    def test_integration_preserves_every_billing_paragraph_and_appends_retention(self):
        import render_account_sync
        staged = render_account_sync.integrated_sources()["terms-content.json"]
        for loc, entry in content()["locales"].items():
            with self.subTest(locale=loc):
                original = sections(entry)["billing"]["paragraphs"]
                integrated = sections(staged["locales"][loc])["billing"]["paragraphs"]
                self.assertEqual(len(integrated), len(original))
                for before, after in zip(original, integrated):
                    self.assertIn(before, after, "integration erased refund/price-change rights")
                self.assertGreater(len(integrated[-1]), len(original[-1]), "account retention belongs after billing rights")


if __name__ == "__main__":
    unittest.main()
