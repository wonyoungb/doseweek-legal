"""Monetization privacy copy guards (review findings 14, 15, 26 and 31, 2026-09-29).

- 14: both ads sections list the overseas-transfer particulars of the Google Mobile Ads SDK and
  UMP (recipient, contact, countries, Google's own purposes) in every locale, as the analytics
  section does for Firebase.
- 15: the Android ads section names the app set ID next to the SDK-created identifiers.
- 26: the iOS and Android purchase sections describe the same purchase-verification server, so
  they carry the same release placeholders (location, operator and retention).
- 31: the Android purchase copy describes the server verification that release builds use, not an
  on-device signature check.
"""

import copy
import json
import unittest
from pathlib import Path

import legal_release
import render_android
import render_ios


ROOT = Path(__file__).resolve().parents[1]
TRANSFER_TOKENS = (
    "Google LLC",
    "Google Ireland Limited",
    "https://policies.google.com/privacy",
    "https://datacenters.google/locations/",
    "https://policies.google.com/technologies/partner-sites",
)


def load(name: str) -> dict:
    return json.loads((ROOT / "docs" / name).read_text(encoding="utf-8"))


def section(catalog: dict, locale: str, section_id: str) -> dict:
    return next(
        item for item in catalog["locales"][locale]["privacy"]["sections"]
        if item["id"] == section_id
    )


def section_text(catalog: dict, locale: str, section_id: str) -> str:
    return "\n".join(section(catalog, locale, section_id)["paragraphs"])


def purchases_catalog(text: str) -> dict:
    return {"locales": {"en": {"privacy": {"sections": [
        {"id": "purchases", "paragraphs": [text]},
    ]}}}}


class AdsTransferParticularsTest(unittest.TestCase):
    def test_every_ios_ads_section_lists_the_transfer_particulars(self):
        ios = load("ios-content.json")
        for locale in ios["localeOrder"]:
            text = section_text(ios, locale, "ads")
            for token in TRANSFER_TOKENS:
                self.assertIn(token, text, f"iOS {locale}: ads section is missing {token!r}")

    def test_every_android_ads_section_lists_the_particulars_and_the_app_set_id(self):
        android = load("android-content.candidate.json")
        for locale in android["localeOrder"]:
            text = section_text(android, locale, "ads")
            for token in (*TRANSFER_TOKENS, "app set ID"):
                self.assertIn(token, text, f"Android {locale}: ads section is missing {token!r}")
            # the identifier list itself (paragraph 2) names the app set ID, not only the
            # transfer particulars at the end
            self.assertIn("app set ID", section(android, locale, "ads")["paragraphs"][2], locale)

    def test_renderers_reject_an_ads_section_without_the_particulars(self):
        ios = load("ios-content.json")
        render_ios.validate(ios)
        broken = copy.deepcopy(ios)
        ads = section(broken, "fr", "ads")
        ads["paragraphs"] = [
            text.replace("Google Ireland Limited", "Google") for text in ads["paragraphs"]
        ]
        with self.assertRaises(AssertionError):
            render_ios.validate(broken)

        android = load("android-content.candidate.json")
        render_android.validate_catalog(android)
        broken = copy.deepcopy(android)
        ads = section(broken, "ja", "ads")
        ads["paragraphs"] = [text.replace("app set ID", "ID") for text in ads["paragraphs"]]
        with self.assertRaises(AssertionError):
            render_android.validate_catalog(broken)


class AndroidPurchaseVerificationCopyTest(unittest.TestCase):
    def test_english_purchase_copy_names_server_verification_only(self):
        text = section_text(load("android-content.candidate.json"), "en", "purchases")
        self.assertNotIn("signed purchase data", text)
        self.assertIn(
            "the app has the developer's purchase-verification server confirm the purchase with "
            "Google Play",
            text,
        )


class PurchaseServerPlaceholderTest(unittest.TestCase):
    def test_ios_and_android_purchase_sections_carry_the_same_placeholders(self):
        self.assertEqual(
            legal_release.purchase_placeholder_parity_errors(
                load("ios-content.json"), load("android-content.candidate.json")
            ),
            [],
        )

    def test_parity_guard_rejects_an_ios_section_without_the_retention_sentence(self):
        location, retention = legal_release.RELEASE_PLACEHOLDERS[:2]
        both = purchases_catalog(f"Records. {location} {retention}")
        errors = legal_release.purchase_placeholder_parity_errors(
            purchases_catalog(f"Records. {location}"), both
        )
        self.assertEqual(len(errors), 1)
        self.assertTrue(errors[0].startswith("en: "), errors)
        self.assertIn(retention, errors[0])
        self.assertEqual(legal_release.purchase_placeholder_parity_errors(both, both), [])
        written = purchases_catalog("The server is operated in Seoul and keeps records for a year.")
        self.assertEqual(legal_release.purchase_placeholder_parity_errors(written, written), [])

    def test_release_gate_finds_every_pending_ios_server_sentence(self):
        # --release refuses any registered placeholder; each locale's iOS purchases section still
        # carries as many as its Android one, so no platform can go live without a retention period.
        ios, android = load("ios-content.json"), load("android-content.candidate.json")
        for locale in ios["localeOrder"]:
            self.assertEqual(
                legal_release.release_placeholders(section_text(ios, locale, "purchases")),
                legal_release.release_placeholders(section_text(android, locale, "purchases")),
                locale,
            )


class RewardPassCopyTest(unittest.TestCase):
    def test_every_locale_describes_the_24_hour_reward_and_48_hour_cap(self):
        ios = load("ios-content.json")
        android = load("android-content.candidate.json")
        terms = load("terms-content.json")
        self.assertEqual(ios["localeOrder"], android["localeOrder"])
        self.assertEqual(ios["localeOrder"], terms["localeOrder"])
        for locale in ios["localeOrder"]:
            ios_entry = ios["locales"][locale]
            android_entry = android["locales"][locale]
            terms_entry = terms["locales"][locale]
            ios_support = ios_entry["support"]["plus"]["ads"]
            android_support = next(
                item for item in android_entry["support"]["faq"]
                if item["id"] == "plus-ads"
            )
            terms_pass = next(
                item for item in terms_entry["sections"]
                if item["id"] == "ad-free-pass"
            )
            for label, value in (
                ("iOS support question", ios_support["question"]),
                ("iOS support answer", " ".join(ios_support["answers"])),
                ("Android support answer", " ".join(android_support["answers"])),
                ("Terms", " ".join(terms_pass["paragraphs"])),
            ):
                self.assertNotIn("30", value, f"{locale}: stale 30-minute {label}")
                if label != "iOS support question":
                    self.assertIn("24", value, f"{locale}: missing 24-hour {label}")
                    self.assertIn("48", value, f"{locale}: missing 48-hour {label}")
            for label, value in (
                ("iOS ads privacy", section_text(ios, locale, "ads")),
                ("iOS purchases privacy", section_text(ios, locale, "purchases")),
                ("Android purchases privacy", section_text(android, locale, "purchases")),
            ):
                self.assertNotIn("30", value, f"{locale}: stale 30-minute {label}")


if __name__ == "__main__":
    unittest.main()
