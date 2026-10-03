#!/usr/bin/env python3
"""Staged legal copy for the Pro "AI 기록 도우미" (AI record assistant), 1.0.6 candidate.

Sources (lane LEGAL-AI, 2026-10-02; PRO-SPEC section 8, compliance sections 4.5 and 8):

* docs/ai-assistant-content.candidate.json: website text in 17 locales. The privacy section
  "AI 기록 도우미(Pro)", the processor row, the sentences that qualify the existing
  "the server cannot read your records" claims, the Terms section and the US consumer-health
  additions.
* docs/ai-app-copy.candidate.json: text the apps consume. Screen A, Screen B and Settings copy,
  the perk line, the helplines and the neutral What's New line.

Nothing here is published. `integrate` changes only the in-memory staged 1.0.6 sources that
scripts/render_account_sync.py builds; the served pages and their sources stay as they are.
`require_release_ready` keeps `check_site.py --release` closed until every required readiness flag is
true and the unresolved list is empty.

    python3 scripts/ai_assistant_candidate.py   # validate both sources
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/ai-assistant-content.candidate.json"
APP_SOURCE = ROOT / "docs/ai-app-copy.candidate.json"
LOCALES = (
    "ko", "en", "ja", "de", "fr", "es", "it", "nl", "pt-PT", "pl", "sv", "hi",
    "pt-BR", "ar", "zh-Hans", "zh-Hant", "tr",
)
CJK = ("ja", "zh-Hans", "zh-Hant")
SECTION_ID = "ai-assistant"
PROCESSOR_ROW_ID = "aws-bedrock"
ROW_CELLS = ("legalBasis", "data", "country", "timingMethod", "recipientContact", "purpose",
             "retention", "refusalEffect")
US_HEALTH_FIELDS = ("categories", "purpose", "processor", "noSale", "consent")
FIELDS = ("name", "perk", "sectionTitle", "clauses", "e2eeException", "healthExclusion",
          "onDeviceScope", "onDeviceOnly", "iosAiFaq", "androidAiFaq", "androidBadge",
          "androidNotUsedItem", "processorRow", "cloudflareTransit", "terms", "usHealth", "deletion")
# iOS 1.0.5 said "No Private Cloud Compute, server model, or third-party model is used" in the
# on-device AI section and in the support answer "Why is an AI feature unavailable?". That is
# true for AI entry and Visit Prep only: the AI record assistant is processed on a server by a
# third-party model. The staged text scopes the sentence to the two on-device features
# (onDeviceOnly) and the support answer says where the assistant is processed (iosAiFaq).
# Review round 2.
ON_DEVICE_DENIAL_TOKEN = "Private Cloud Compute"
ON_DEVICE_MODEL_TOKEN = "SystemLanguageModel.default"
SENTENCE = re.compile(r"(?<=[。।])|(?<=\.)\s+")
# Draft sentences that say a fact is not verified yet or will be recorded before release:
# clause 5, and the processor-row cells legalBasis, country, recipientContact and retention.
PRE_RELEASE_WORDING_FIELDS = 5
# Android 1.0.5 said "No generative AI" as a home badge and listed "Generative AI" among the
# things DoseWeek does not use. Both are false once the assistant ships in 1.0.6, so the staged
# text replaces them at these positions (review round 1).
ANDROID_BADGE_INDEX = 3
ANDROID_NOT_USED_ITEM_INDEX = 4
CLAUSES = 12
TERMS_PARAGRAPHS = 8
HEALTH_PLACEHOLDER = "{healthExclusion}"
# Account/sync candidate fields that say the developer or server cannot read the records.
# With the AI record assistant that is true only for sync and backup, so the staged text adds
# the exception right after each of them (PRO-SPEC section 8; never claim that end-to-end
# encryption covers AI content).
SERVER_CANNOT_READ_FIELDS = ("recordsSync", "mealsSync", "sync")
READINESS_KEYS = (
    "awsContractingEntityVerified", "bedrockRetentionNoneReadback",
    "bedrockInvocationLoggingOffReadback", "hpkeEnvelopeDeployed", "consentRoutesDeployed",
    "killSwitchVerified", "helplinesRefetched", "legalSelfReviewAccepted",
    "localeReviewReceiptsAccepted", "evalGatePassed", "storeDeclarationsReadBack",
)
INFORMATIONAL_READINESS_KEYS = ('counselReviewed',)
LEGAL_REVIEW_SOURCE_FIELDS = ('schemaVersion', 'plannedVersion', 'facts', 'localeOrder',
                              'preReleaseWording', 'locales')
LEGAL_REVIEW_BASE_SOURCES = (
    'docs/ai-app-copy.candidate.json', 'docs/account-sync-content.candidate.json',
    'docs/ios-content.json', 'docs/android-content.candidate.json',
    'docs/terms-content.json', 'docs/us-health-content.json',
)
FACTS = {
    "provider": "Amazon Bedrock", "region": "ap-northeast-2", "inRegionOnly": True,
    "bedrockRetention": "none", "modelFamily": "Anthropic Claude", "monthlyRequests": 150,
    "weeklySummaryOutsideQuota": True, "trialDays": 7, "trialRequests": 50, "minimumAge": 18,
    "usageCountRetentionMonths": 2, "reportExcerptRetentionDays": 30, "summaryCardsOnDevice": 2,
    "priorityFirstReplyBusinessDays": 1, "limitReductionNoticeDays": 30,
}
HELPLINE_TOKENS = ("119", "109", "911", "988", "0120-279-338", "findahelpline.com")
# Owner second round (2026-10-02): the product is "AI 기록 도우미" and the perk "우선 문의 답변";
# "상담" is never used. compliance 4.1 lists the other names that must not appear.
RETIRED_KOREAN_TERMS = ("상담", "AI 코치", "AI 영양사", "AI 닥터", "주치의", "무제한", "부작용 관리")
IOS_ONLY_FORBIDDEN = ("Android", "Google Play", "Health Connect")
ANDROID_ONLY_FORBIDDEN = ("Apple", "iOS", "App Store")
PLACEHOLDER = re.compile(r"\{[A-Za-z0-9]+\}")
APP_PLACEHOLDERS = ("{count}", "{count2}", "{text}")
SCREEN_A_PREFIX = "ai.consent.a."
SCREEN_B_PREFIX = "ai.consent.b."


def separator(locale: str) -> str:
    return "" if locale in CJK else " "


def number(value: int, text: str) -> bool:
    """True when the integer appears as its own number in text (not inside a longer number)."""
    return re.search(rf"(?<![\d.,]){value}(?![\d])", text) is not None


def _strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in value.values() for text in _strings(item)]
    if isinstance(value, list):
        return [text for item in value for text in _strings(item)]
    return []


def load() -> dict:
    candidate = json.loads(SOURCE.read_text(encoding="utf-8"))
    assert candidate["schemaVersion"] == 1
    assert candidate["status"] in ("pre-release-candidate-not-published", "integrated-and-verified")
    assert candidate["plannedVersion"] == "1.0.6"
    assert candidate["facts"] == FACTS, "AI facts changed: update the copy in all 17 locales first"
    assert set(candidate["readiness"]) == set(READINESS_KEYS + INFORMATIONAL_READINESS_KEYS)
    evidence = candidate.get("legalSelfReviewEvidence")
    assert evidence is None or isinstance(evidence, dict), "AI self-review evidence schema"
    assert all(type(value) is bool for value in candidate["readiness"].values())
    assert candidate["localeOrder"] == list(LOCALES)
    assert list(candidate["locales"]) == list(LOCALES)
    for locale, entry in candidate["locales"].items():
        assert tuple(entry) == FIELDS, f"{locale}: AI disclosure fields"
        clauses = entry["clauses"]
        assert len(clauses) == CLAUSES and len(entry["terms"]) == TERMS_PARAGRAPHS, locale
        assert tuple(entry["processorRow"]) == ROW_CELLS, locale
        assert tuple(entry["usHealth"]) == US_HEALTH_FIELDS, locale
        assert tuple(entry["healthExclusion"]) == ("ios", "android"), locale
        texts = _strings(entry)
        assert all(text == text.strip() and len(text) > 2 for text in texts), locale
        assert "<" not in "".join(texts), f"{locale}: plain text only"
        placeholders = [found for text in texts for found in PLACEHOLDER.findall(text)]
        assert placeholders == [HEALTH_PLACEHOLDER] and HEALTH_PLACEHOLDER in clauses[1], (
            f"{locale}: clause 2 carries the one platform placeholder"
        )
        name = entry["name"]
        assert name in entry["sectionTitle"] or name.casefold() in entry["sectionTitle"].casefold(), locale
        assert "Pro" in entry["sectionTitle"], locale
        for token in ("Amazon Bedrock", "ap-northeast-2", "Anthropic", "Claude"):
            assert token in clauses[4], f"{locale}: clause 5 names the processor ({token})"
        assert "Cloudflare" in clauses[5] and "DoseWeek" in clauses[5], locale
        assert number(2, clauses[3]) and number(30, clauses[3]), f"{locale}: clause 4 retention"
        assert number(18, clauses[10]), f"{locale}: clause 11 age"
        for token in HELPLINE_TOKENS:
            assert token in clauses[11], f"{locale}: clause 12 helpline {token}"
        assert "Amazon Bedrock" in entry["e2eeException"] and "DoseWeek" in entry["e2eeException"], locale
        row = entry["processorRow"]
        assert row["legalBasis"].startswith("Amazon Bedrock (AWS) — "), locale
        assert "ap-northeast-2" in row["country"], locale
        assert "https://aws.amazon.com/privacy/" in row["recipientContact"], locale
        assert "Amazon Bedrock" in row["retention"], locale
        terms = entry["terms"]
        assert "Plus" in terms[0] and "Pro" in terms[0] and number(7, terms[0]) and number(3, terms[0]), locale
        assert number(18, terms[1]), locale
        assert "119" in terms[3] and "911" in terms[3], locale
        assert all(number(value, terms[4]) for value in (150, 50, 30, 1)) and "UTC" in terms[4], locale
        assert entry["perk"].casefold() in terms[0].casefold(), f"{locale}: perk named in the Pro paragraph"
        assert entry["perk"].casefold() in terms[7].casefold() and number(1, terms[7]), locale
        us_health = entry["usHealth"]
        assert "HealthKit" in us_health["categories"] and "Health Connect" in us_health["categories"], locale
        assert "Amazon Bedrock" in us_health["processor"] and "AWS" in us_health["processor"], locale
        assert number(30, entry["deletion"]), locale
        assert "1.0.6" in entry["androidAiFaq"] and "Amazon Bedrock" in entry["androidAiFaq"], locale
        scoped, pointer = entry["onDeviceOnly"], entry["iosAiFaq"]
        assert ON_DEVICE_DENIAL_TOKEN in scoped and ON_DEVICE_DENIAL_TOKEN not in pointer, locale
        assert ON_DEVICE_MODEL_TOKEN not in scoped + pointer, f"{locale}: the model is named once, by the page"
        for token in ("Amazon Bedrock", "Anthropic", "Claude", "DoseWeek"):
            assert token in pointer, f"{locale}: the iOS AI answer names the server path ({token})"
        assert name.casefold() in pointer.casefold() and "Pro" in pointer, locale
        assert "\n" not in scoped + pointer, locale
        ios_only = [entry["healthExclusion"]["ios"], entry["onDeviceScope"], scoped, pointer]
        android_only = [entry["healthExclusion"]["android"], entry["androidAiFaq"],
                        entry["androidBadge"], entry["androidNotUsedItem"]]
        assert "\n" not in entry["androidBadge"] + entry["androidNotUsedItem"], locale
        assert not [token for token in IOS_ONLY_FORBIDDEN for text in ios_only if token in text], locale
        assert not [token for token in ANDROID_ONLY_FORBIDDEN for text in android_only if token in text], locale
        shared = [text for text in texts if text not in ios_only + android_only]
        # The privacy section reaches both platform policies, so its shared text names neither
        # platform; the Terms and the US policy are single pages for both and may.
        both_platforms = [*entry["terms"], *entry["usHealth"].values()]
        for text in shared:
            if text in both_platforms:
                continue
            assert not [token for token in ("Android", "iOS", "Google Play", "App Store") if token in text], (
                f"{locale}: shared privacy text names a platform"
            )
    korean = "\n".join(_strings(candidate["locales"]["ko"]))
    assert not [term for term in RETIRED_KOREAN_TERMS if term in korean], "Korean AI copy uses a retired term"
    assert "AI 기록 도우미" == candidate["locales"]["ko"]["name"]
    assert "우선 문의 답변" == candidate["locales"]["ko"]["perk"]
    english = "\n".join(candidate["locales"]["en"]["clauses"][4:6] + [candidate["locales"]["en"]["processorRow"]["timingMethod"]])
    assert "end-to-end" not in english, "the AI transit is app-layer encryption to the server key, not end-to-end"
    wording = candidate["preReleaseWording"]
    assert list(wording) == list(LOCALES)
    for locale, drafts in wording.items():
        assert len(drafts) == PRE_RELEASE_WORDING_FIELDS and all(len(text) > 8 for text in drafts), locale
        if candidate["status"] == "pre-release-candidate-not-published":
            # The list follows the text: a draft sentence that is reworded is listed again.
            entry = candidate["locales"][locale]
            row = entry["processorRow"]
            fields = (entry["clauses"][4], row["legalBasis"], row["country"], row["recipientContact"],
                      row["retention"])
            assert all(text in field for text, field in zip(drafts, fields)), (
                f"{locale}: preReleaseWording no longer matches clause 5 and the processor row"
            )
    return candidate


def load_app_copy() -> dict:
    document = json.loads(APP_SOURCE.read_text(encoding="utf-8"))
    assert document["schemaVersion"] == 1
    assert document["status"] == "pre-release-candidate-not-published"
    assert document["plannedVersion"] == "1.0.6"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}\.\d+", document["consentVersion"])
    assert document["localeOrder"] == list(LOCALES) and list(document["locales"]) == list(LOCALES)
    keys = document["keys"]
    assert len(keys) == len(set(keys)) and all(key.startswith(("ai.", "pro.")) for key in keys)
    regions = document["helplines"]["regions"]
    assert {code: (item["emergency"], item["crisis"]) for code, item in regions.items()} == {
        "KR": ("119", "109"), "JP": ("119", "0120-279-338"), "US": ("911", "988"),
    }
    assert document["helplines"]["default"]["link"] == "https://findahelpline.com"
    assert document["helplines"]["verification"]["refetchFromOfficialSources"] == "NOT_RUN" or (
        document["helplines"]["verification"]["status"] == "refetched"
    )
    reference = document["locales"]["ko"]["copy"]
    for locale, entry in document["locales"].items():
        assert tuple(entry) == ("name", "perk", "copy", "whatsNew"), locale
        copy = entry["copy"]
        assert list(copy) == keys, f"{locale}: app copy keys"
        for key, text in copy.items():
            assert isinstance(text, str) and text == text.strip() and text, (locale, key)
            found = sorted(PLACEHOLDER.findall(text))
            assert found == sorted(PLACEHOLDER.findall(reference[key])), (locale, key, "placeholders")
            assert all(item in APP_PLACEHOLDERS for item in found), (locale, key)
            if key.endswith(".ios"):
                assert not [token for token in IOS_ONLY_FORBIDDEN if token in text], (locale, key)
            elif key.endswith(".android"):
                assert not [token for token in ANDROID_ONLY_FORBIDDEN if token in text], (locale, key)
            else:
                assert not [token for token in ("Android", "iOS", "Google Play", "App Store",
                                                "Health Connect", "Apple") if token in text], (locale, key)
        for token in ("Amazon Bedrock", "Anthropic", "Claude", "DoseWeek"):
            assert token in copy["ai.consent.a.where.body"], (locale, token)
        assert number(2, copy["ai.consent.a.retention.body"]) and number(30, copy["ai.consent.a.retention.body"]), locale
        assert number(30, copy["ai.consent.a.check.health.detail"]), locale
        assert number(18, copy["ai.consent.a.check.age"]), locale
        assert "Amazon Bedrock" in copy["ai.consent.a.e2ee.body"], locale
        assert "Amazon Bedrock" in copy["ai.consent.b.processing"], locale
        assert number(7, copy["ai.consent.b.purpose.weekly"]), locale
        assert "PIPA" in copy["ai.consent.a.region.jp"] and "Amazon Bedrock" in copy["ai.consent.a.region.jp"], locale
        assert copy["pro.support.priority"].startswith(entry["perk"]) and number(1, copy["pro.support.priority"]), locale
        assert entry["name"].casefold() in entry["whatsNew"].casefold(), f"{locale}: What's New names the feature"
    korean = "\n".join(_strings(document["locales"]["ko"]))
    assert not [term for term in RETIRED_KOREAN_TERMS if term in korean], "Korean app copy uses a retired term"
    return document


def _qualified(value: object, claims: list[str], exception: str, joiner: str) -> object:
    if isinstance(value, str):
        for claim in claims:
            if claim in value:
                value = value.replace(claim, claim + joiner + exception)
        return value
    if isinstance(value, list):
        return [_qualified(item, claims, exception, joiner) for item in value]
    if isinstance(value, dict):
        return {key: _qualified(item, claims, exception, joiner) for key, item in value.items()}
    return value


def _sections(entries: list[dict]) -> dict:
    return {section["id"]: section for section in entries}


def _scoped_denial(text: str, replacement: str, locale: str) -> str:
    """Replace the one 1.0.5 sentence that denies any server or third-party model."""
    found = [part.strip() for block in text.split("\n\n") for part in SENTENCE.split(block)
             if ON_DEVICE_DENIAL_TOKEN in part]
    assert len(found) == 1 and text.count(found[0]) == 1, (locale, "on-device AI denial changed")
    return text.replace(found[0], replacement)


def _supplement(privacy: dict, text: dict, platform: str) -> None:
    supplement = privacy["legalSupplement"]
    clauses = [clause.replace(HEALTH_PLACEHOLDER, text["healthExclusion"][platform])
               for clause in text["clauses"]]
    supplement["sections"].append({"id": SECTION_ID, "title": text["sectionTitle"], "paragraphs": clauses})
    rows = _sections(supplement["sections"])["processors"]["table"]["rows"]
    position = [row["id"] for row in rows].index("aws") + 1
    rows.insert(position, {"id": PROCESSOR_ROW_ID, "role": "processor",
                           "cells": dict(text["processorRow"])})
    return None


def integrate(ios: dict, android: dict, terms: dict, us_health: dict, account: dict,
              candidate: dict | None = None) -> None:
    """Add the AI record assistant disclosures to the staged 1.0.6 sources, in place."""
    import render_account_sync
    candidate = candidate or load()
    for locale in LOCALES:
        text = candidate["locales"][locale]
        joiner = separator(locale)
        claims = [account["locales"][locale][field] for field in SERVER_CANNOT_READ_FIELDS]
        for document in (ios, android, terms):
            document["locales"][locale] = _qualified(
                document["locales"][locale], claims, text["e2eeException"], joiner)
        i, a, t = ios["locales"][locale], android["locales"][locale], terms["locales"][locale]
        ip, ap = _sections(i["privacy"]["sections"]), _sections(a["privacy"]["sections"])

        # Privacy: the section, the processor row and the Cloudflare ciphertext sentence.
        for privacy, platform in ((i["privacy"], "ios"), (a["privacy"], "android")):
            _supplement(privacy, text, platform)
            table = _sections(privacy["legalSupplement"]["sections"])["processors"]["table"]
            cloudflare = _sections(table["rows"])["cloudflare"]["cells"]
            cloudflare["data"] += joiner + text["cloudflareTransit"]
        # Health-platform data is never used for AI (Apple 5.1.3; PRO-SPEC 5.4 provenance filter).
        ip["health"]["paragraphs"][0] += joiner + text["healthExclusion"]["ios"]
        ap["no-collection"]["paragraphs"][2] += joiner + text["healthExclusion"]["android"]
        # "No server model" is true only for on-device AI entry and Visit Prep. The privacy
        # section scopes that sentence and says where the assistant is; the support answer
        # scopes it too and says that the assistant is processed on a server by Amazon Bedrock.
        ip["ai"]["paragraphs"][0] = (
            _scoped_denial(ip["ai"]["paragraphs"][0], text["onDeviceOnly"], locale)
            + "\n\n" + text["onDeviceScope"])
        answers = i["support"]["released"]["ai"]["answers"]
        answers[0] = _scoped_denial(answers[0], text["onDeviceOnly"] + joiner + text["iosAiFaq"], locale)
        # 1.0.5 said "no generative AI"; the staged build only bumped the version in that
        # sentence, which is false once the assistant ships in 1.0.6.
        faq = _sections(a["support"]["faq"])["ai-health"]
        faq["answers"][0] = render_account_sync.replace_backup_sentence(
            faq["answers"][0], 0, text["androidAiFaq"], locale)
        # The same denial as a home badge and as an item of the "not used by default" list:
        # generative AI is used, but only in the assistant and only after separate consent.
        a["home"]["featureBadges"][ANDROID_BADGE_INDEX] = text["androidBadge"]
        ap["no-collection"]["items"][ANDROID_NOT_USED_ITEM_INDEX] = text["androidNotUsedItem"]

        # Terms: a new section right after the medical notice; later titles move up by one.
        sections = t["sections"]
        index = [section["id"] for section in sections].index("medical") + 1
        for section in sections[index:]:
            old, separator_, rest = section["title"].partition(". ")
            assert separator_ and old.isdigit(), (locale, section["id"], "numbered title")
            section["title"] = f"{int(old) + 1}. {rest}"
        sections.insert(index, {"id": SECTION_ID, "title": f"{index + 1}. {text['sectionTitle']}",
                                "paragraphs": list(text["terms"])})

        # US consumer-health policy: sentences inside the existing paragraphs.
        us = _sections(us_health["locales"][locale]["sections"])
        additions = text["usHealth"]
        us["categories"]["paragraphs"][0] += joiner + additions["categories"]
        us["purposes-sources"]["paragraphs"][1] += joiner + additions["purpose"]
        us["disclosures"]["paragraphs"][0] += joiner + additions["processor"]
        us["disclosures"]["paragraphs"][2] += joiner + additions["noSale"]
        us["consent"]["paragraphs"][1] += joiner + additions["consent"]


def deletion_paragraph(locale: str, candidate: dict | None = None) -> str:
    return (candidate or load())["locales"][locale]["deletion"]


def _legal_review_source_fingerprint(candidate: dict) -> str:
    payload = {
        'aiCandidate': {key: candidate[key] for key in LEGAL_REVIEW_SOURCE_FIELDS},
        'stagedSources': {path: json.loads((ROOT / path).read_text(encoding='utf-8'))
                          for path in LEGAL_REVIEW_BASE_SOURCES},
    }
    data = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def _require_legal_self_review(candidate: dict, *, allow_synthetic_fixture: bool) -> None:
    evidence = candidate.get('legalSelfReviewEvidence')
    assert isinstance(evidence, dict), 'AI legal self-review evidence is missing'
    assert set(evidence) == {'receiptPath', 'receiptSha256', 'sourceFingerprintSha256'}, (
        'AI legal self-review evidence fields'
    )
    assert isinstance(evidence['receiptPath'], str) and evidence['receiptPath'].strip(), (
        'AI legal self-review receipt path is empty'
    )
    for key in ('receiptSha256', 'sourceFingerprintSha256'):
        assert isinstance(evidence[key], str) and re.fullmatch(r'[0-9a-f]{64}', evidence[key]), (
            f'AI legal self-review {key} is invalid'
        )
    path = Path(evidence['receiptPath'])
    path = path if path.is_absolute() else ROOT / path
    assert path.is_file(), 'AI legal self-review receipt is missing'
    data = path.read_bytes()
    assert data and hashlib.sha256(data).hexdigest() == evidence['receiptSha256'], (
        'AI legal self-review receipt bytes do not match'
    )
    receipt = json.loads(data.decode('utf-8'))
    assert isinstance(receipt, dict), 'AI legal self-review receipt must be an object'
    assert receipt.get('status') == 'accepted', 'AI legal self-review receipt is not accepted'
    assert receipt.get('reviewType') == 'codex-source-self-review', (
        'AI legal self-review receipt has an unrecognized review type'
    )
    scope = receipt.get('scope')
    assert isinstance(scope, str) and scope.strip(), 'AI legal self-review scope is empty'
    assert type(receipt.get('synthetic')) is bool, 'AI legal self-review synthetic marker is missing'
    if not allow_synthetic_fixture:
        assert receipt['synthetic'] is False and 'synthetic' not in scope.casefold(), (
            'Synthetic self-review evidence cannot authorize production release'
        )
    assert receipt.get('counselReviewed') is False and receipt.get('nativeSpeakerReview') is False, (
        'Codex self-review evidence must not claim counsel or native-speaker review'
    )
    current = _legal_review_source_fingerprint(candidate)
    assert evidence['sourceFingerprintSha256'] == receipt.get('sourceFingerprintSha256') == current, (
        'AI legal self-review does not match the current reviewed sources'
    )


def require_release_ready(candidate: dict | None = None, *,
                          allow_synthetic_fixture: bool = False) -> None:
    # Synthetic opt-in is restricted to explicit in-memory fixtures, never the loaded candidate.
    assert type(allow_synthetic_fixture) is bool, "AI synthetic fixture option must be Boolean"
    assert not allow_synthetic_fixture or candidate is not None, (
        "Synthetic self-review opt-in requires an explicit test fixture"
    )
    candidate = candidate if candidate is not None else load()
    assert candidate["status"] == "integrated-and-verified", (
        "AI record assistant disclosure is a pre-release candidate: verify the provider facts, "
        "the consent flow, the helplines and the locale reviews first"
    )
    assert not candidate["unresolvedBeforePublication"], (
        "AI release blockers remain in docs/ai-assistant-content.candidate.json"
    )
    open_flags = [key for key in READINESS_KEYS if candidate["readiness"].get(key) is not True]
    assert not open_flags, f"AI readiness flags still open: {open_flags}"
    _require_legal_self_review(candidate, allow_synthetic_fixture=allow_synthetic_fixture)
    # The flags alone do not change the text: the sentences that say a fact is unverified or will
    # be recorded before release must be replaced with the verified facts.
    drafts = [(locale, text) for locale, sentences in candidate["preReleaseWording"].items()
              for text in sentences if any(text in value for value in _strings(candidate["locales"][locale]))]
    assert not drafts, (
        f"AI policy still carries {len(drafts)} draft sentence(s) (not yet verified / before "
        f"release), first: {drafts[0]}"
    )


if __name__ == "__main__":
    web, app = load(), load_app_copy()
    print(f"OK: {len(web['locales'])} AI disclosure locales, {len(app['keys'])} app copy keys; "
          f"status={web['status']}; consentVersion={app['consentVersion']}")
