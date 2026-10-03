#!/usr/bin/env python3
"""Staged legal copy for the Pro "AI 기록 도우미" (AI record assistant), 1.0.6 candidate.

Sources (lane LEGAL-AI, 2026-10-02; PRO-SPEC section 8, compliance sections 4.5 and 8):

* docs/ai-assistant-content.candidate.json: website text in 17 locales. The privacy section
  "AI 기록 도우미(Pro)", the processor row, the sentences that qualify the existing
  "the server cannot read your records" claims, the Terms section and the US consumer-health
  additions.
* docs/ai-app-copy.candidate.json: text the apps consume. Screen A, Screen B and Settings copy,
  the perk line, the helplines and the neutral What's New line.

ai-consent-v3 (2026-10-03, owner decision: Pro AI ships on Gemini, Google Cloud Vertex AI, with a
cross-border transfer consent). The recipient is Google, the transfer notice is shown on every
storefront, and two owner decisions are single switches whose four combinations are all built and
validated here: location (us | global) and the AWS output Guardrail (off | on). The JSON strings
carry the tokens {aiLocation}, {aiLocationShort}, {aiTransferCountry} and {aiGuardrail};
`resolve(document, location, guardrail)` returns the text a reader sees. v1 and v2 named Amazon
Bedrock in Seoul; that text is in the Git history of both files.

Review round 2 (2026-10-03): the token checks below accepted copy that contradicted the facts.
scripts/ai_legal_guard.py adds exact pinned sentences per locale, the six notice items of the
transfer notice, forbidden claims per locale and per-combination hashes of the pinned fields
(docs/ai-consent-v3-legal-pins.json). `validate_web` and `validate_app` run on an in-memory
document, so a test can replay a wrong edit.

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

import ai_legal_guard

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/ai-assistant-content.candidate.json"
APP_SOURCE = ROOT / "docs/ai-app-copy.candidate.json"
LOCALES = (
    "ko", "en", "ja", "de", "fr", "es", "it", "nl", "pt-PT", "pl", "sv", "hi",
    "pt-BR", "ar", "zh-Hans", "zh-Hant", "tr",
)
CJK = ("ja", "zh-Hans", "zh-Hant")
SECTION_ID = "ai-assistant"
PROCESSOR_ROW_ID = "google-vertex-ai"
PROCESSOR_ROW_PREFIX = "Google Cloud Vertex AI (Google) — "
ROW_CELLS = ("legalBasis", "data", "country", "timingMethod", "recipientContact", "purpose",
             "retention", "refusalEffect")
US_HEALTH_FIELDS = ("categories", "purpose", "processor", "noSale", "consent")
FIELDS = ("name", "perk", "sectionTitle", "clauses", "e2eeException", "healthExclusion",
          "onDeviceScope", "onDeviceOnly", "iosAiFaq", "androidAiFaq", "androidBadge",
          "androidNotUsedItem", "processorRow", "cloudflareTransit", "terms", "usHealth", "deletion",
          "switchText")
# iOS 1.0.5 said "No Private Cloud Compute, server model, or third-party model is used" in the
# on-device AI section and in the support answer "Why is an AI feature unavailable?". That is
# true for AI entry and Visit Prep only: the AI record assistant is processed on a server by a
# third-party model. The staged text scopes the sentence to the two on-device features
# (onDeviceOnly) and the support answer says where the assistant is processed (iosAiFaq).
# Review round 2.
ON_DEVICE_DENIAL_TOKEN = "Private Cloud Compute"
ON_DEVICE_MODEL_TOKEN = "SystemLanguageModel.default"
SENTENCE = re.compile(r"(?<=[。।])|(?<=\.)\s+")
# ai-consent-v2 carried five draft sentences per locale ("not yet verified"). ai-consent-v3 states
# only what Google's published terms say, so it carries none; the open items are the two owner
# switches, the readiness flags and the unresolved list.
PRE_RELEASE_WORDING_FIELDS = 0
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
    "googleContractingEntityVerified", "vertexLocationDecided", "awsGuardrailDecided",
    "vertexCacheSettingReadback", "vertexRequestResponseLoggingOffReadback", "hpkeEnvelopeDeployed",
    "consentRoutesDeployed", "killSwitchVerified", "helplinesRefetched", "legalSelfReviewAccepted",
    "localeReviewReceiptsAccepted", "evalGatePassed", "storeDeclarationsReadBack",
)
INFORMATIONAL_READINESS_KEYS = ('counselReviewed',)
# Review round 2 (F8): two open points used to block publication only through the free-text
# unresolved list. Each is now a flag that require_release_ready demands for the switch value that
# raises the question: (switch, value) -> flag.
# Review round 3 (re-review R1): the two other switch values had no flag, so the likeliest
# combination passed the conditional gate with nothing to prove. Guardrail off needs a readback
# that the server no longer calls AWS ApplyGuardrail (the off text names Google only); location us
# needs the PIPA 28-8(2)2 form for us accepted.
CONDITIONAL_READINESS = {
    ("location", "global"): "pipaCountryItemForGlobalAccepted",
    ("location", "us"): "pipaCountryItemForUsAccepted",
    ("guardrail", "on"): "awsGuardrailEntityAndProcessorRowVerified",
    ("guardrail", "off"): "serverGuardrailCallRemovedReadback",
}
# Owner decisions 2026-10-03 17:35 and 19:00 KST (late-decisions.md): location global, guardrail off.
OWNER_SELECTION = ("global", "off")
# Flags that are true in the committed candidate; each needs its reason in readinessEvidence.
DECIDED_READINESS = ("vertexLocationDecided", "awsGuardrailDecided", "pipaCountryItemForGlobalAccepted")
# Owner wording rule 2026-10-03 19:10 KST: every global text says "Global".
GLOBAL_WORD = "Global"
LEGAL_REVIEW_SOURCE_FIELDS = ('schemaVersion', 'plannedVersion', 'facts', 'switches', 'localeOrder',
                              'preReleaseWording', 'locales')
LEGAL_REVIEW_BASE_SOURCES = (
    'docs/ai-app-copy.candidate.json', 'docs/account-sync-content.candidate.json',
    'docs/ios-content.json', 'docs/android-content.candidate.json',
    'docs/terms-content.json', 'docs/us-health-content.json',
)
# ai-consent-v3 (2026-10-03): the processor is Google (Gemini on Google Cloud Vertex AI). Every
# figure is from Google's published documentation and terms as saved with SHA-256 in the lane
# evidence FACTS.md (release/evidence/1.0.6/.../legal-self-review/claude-20261003).
FACTS = {
    "provider": "Google Cloud Vertex AI", "model": "gemini-3.8-flash", "modelFamily": "Google Gemini",
    "recipient": "Google Cloud Korea LLC; Google Asia Pacific Pte. Ltd. and its affiliates including Google LLC",
    "recipientContact": "https://support.google.com/cloud/contact/dpo",
    "googleRole": "processor", "crossBorderTransfer": True, "locationOptions": ["us", "global"],
    "googleTrainsOnContent": False, "googleInMemoryCacheHours": 24, "googleAbusePromptLogDays": 90,
    "monthlyRequests": 150, "weeklySummaryOutsideQuota": True, "trialDays": 7, "trialRequests": 50,
    "minimumAge": 18, "usageCountRetentionMonths": 2, "reportExcerptRetentionDays": 30,
    "summaryCardsOnDevice": 2, "priorityFirstReplyBusinessDays": 1, "limitReductionNoticeDays": 30,
}
COPY_VERSION = "2026-10-03.4"
WIRE_CONSENT_VERSION = "ai-consent-v3"
# The two owner switches (decided 2026-10-03: OWNER_SELECTION). Both texts of each stay in the
# candidate files and every one of the four combinations is validated by load() and load_app_copy().
LOCATIONS = ("us", "global")
GUARDRAILS = ("off", "on")
SWITCH_TOKENS = ("{aiLocation}", "{aiLocationShort}", "{aiTransferCountry}", "{aiGuardrail}")
# Used ONLY for an unpublished staging render of a document whose selection is null (a test
# fixture); the committed candidate carries the owner's selection and renders with it.
STAGING_PREVIEW_SWITCHES = ("us", "off")
GOOGLE_ENTITIES = ("Google Cloud Korea LLC", "Google Asia Pacific Pte. Ltd.", "Google LLC")
GOOGLE_CONTACT = "https://support.google.com/cloud/contact/dpo"
GOOGLE_LOCATIONS_URL = "https://cloud.google.com/about/locations"
# Google's own sentence about the global endpoint (data-residency page), quoted in every locale.
GOOGLE_GLOBAL_QUOTE = "“may be processed in any Google Cloud location around the world”"
# ai-consent-v1/v2 named these. None may remain; "Amazon Web Services" is allowed only inside the
# guardrail sentence when that switch is on.
RETIRED_PROVIDER_TOKENS = ("Bedrock", "Anthropic", "Claude", "AWS", "Amazon", "ap-northeast-2")
# The United States as each locale writes it, as the stem that survives case endings.
US_STEMS = {
    "ko": "미국", "en": "United States", "ja": "アメリカ合衆国", "de": "Vereinigte", "fr": "États-Unis",
    "es": "Estados Unidos", "it": "Stati Uniti", "nl": "Verenigde Staten", "pt-PT": "Estados Unidos",
    "pl": "Zjednoczon", "sv": "USA", "hi": "संयुक्त राज्य अमेरिका", "pt-BR": "Estados Unidos",
    "ar": "الولايات المتحدة", "zh-Hans": "美国", "zh-Hant": "美國", "tr": "Amerika Birleşik Devletleri",
}
RETIRED_APP_KEYS = ("ai.consent.a.region.jp",)
TRANSFER_KEYS = ("ai.consent.a.transfer.title", "ai.consent.a.transfer.body", "ai.consent.a.check.transfer")
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


def _switch_text(entry: dict, locale: str) -> dict:
    text = entry["switchText"]
    assert tuple(text) == ("aiLocation", "aiLocationShort", "aiTransferCountry", "aiGuardrail"), locale
    for name in ("aiLocation", "aiLocationShort", "aiTransferCountry"):
        assert tuple(text[name]) == LOCATIONS, (locale, name)
    assert tuple(text["aiGuardrail"]) == ("on",), locale
    for value in _strings(text):
        assert value == value.strip() and len(value) >= 2 and not PLACEHOLDER.search(value), locale
    # us names the United States and never quotes the global statement; global quotes Google and
    # links Google's list of locations; the guardrail sentence is the only place that names AWS.
    country = US_STEMS[locale]
    for name in ("aiLocation", "aiLocationShort", "aiTransferCountry"):
        assert country in text[name]["us"], (locale, name)
    for name in ("aiLocation", "aiTransferCountry"):
        assert country in text[name]["us"] and GOOGLE_GLOBAL_QUOTE not in text[name]["us"], (locale, name)
        assert GOOGLE_GLOBAL_QUOTE in text[name]["global"], (locale, name)
    for name in ("aiLocation", "aiLocationShort", "aiTransferCountry"):
        assert GLOBAL_WORD in text[name]["global"], (
            f"{locale}: {name} for location global must say {GLOBAL_WORD} (owner wording rule 2026-10-03)")
        assert GLOBAL_WORD not in text[name]["us"], (locale, name)
    assert GOOGLE_LOCATIONS_URL in text["aiTransferCountry"]["global"], locale
    assert GOOGLE_LOCATIONS_URL not in text["aiTransferCountry"]["us"], locale
    # Both texts describe the systems of the countries where the named recipients are (APPI Rule
    # 17(2), PPC Q12-11): the United States and Singapore, each with its APEC CBPR participation.
    for option in LOCATIONS:
        assert text["aiTransferCountry"][option].count("APEC") >= 2, (
            f"{locale}: the {option} notice describes the United States and Singapore")
        assert "Google Asia Pacific Pte. Ltd." in text["aiTransferCountry"][option], (locale, option)
        assert "Personal Data Protection Act 2012" in text["aiTransferCountry"][option], (locale, option)
    assert "Amazon Web Services" in text["aiGuardrail"]["on"], locale
    assert not [token for token in RETIRED_PROVIDER_TOKENS
                for name in ("aiLocation", "aiLocationShort", "aiTransferCountry")
                for value in text[name].values() if token in value], locale
    return text


def _resolve_entry(value: object, text: dict, location: str, guardrail: str, joiner: str) -> object:
    if isinstance(value, str):
        value = value.replace("{aiGuardrail}", joiner + text["aiGuardrail"]["on"] if guardrail == "on" else "")
        for token in ("aiLocationShort", "aiLocation", "aiTransferCountry"):
            value = value.replace("{" + token + "}", text[token][location])
        return value
    if isinstance(value, list):
        return [_resolve_entry(item, text, location, guardrail, joiner) for item in value]
    if isinstance(value, dict):
        return {key: _resolve_entry(item, text, location, guardrail, joiner) for key, item in value.items()}
    return value


def resolve(document: dict, location: str, guardrail: str) -> dict:
    """The document with the two owner switches applied: no switch token and no switchText left.

    `location` is "us" or "global", `guardrail` is "off" or "on". Works for both candidate files.
    """
    assert location in LOCATIONS and guardrail in GUARDRAILS, (location, guardrail)
    resolved = {key: value for key, value in document.items() if key != "locales"}
    resolved["resolvedSwitches"] = {"location": location, "guardrail": guardrail}
    resolved["locales"] = {}
    for locale, entry in document["locales"].items():
        text = entry["switchText"]
        resolved["locales"][locale] = {
            key: _resolve_entry(value, text, location, guardrail, separator(locale))
            for key, value in entry.items() if key != "switchText"}
    return resolved


def selection(document: dict) -> tuple[str, str] | None:
    """The owner's switch selection, or None while either decision is open."""
    switches = document["switches"]
    chosen = (switches["location"]["selected"], switches["guardrail"]["selected"])
    if None in chosen:
        return None
    assert chosen[0] in LOCATIONS and chosen[1] in GUARDRAILS, chosen
    return chosen


def _check_switches(document: dict) -> None:
    switches = document["switches"]
    assert tuple(switches) == ("rule", "location", "guardrail", "tokens"), "switch block"
    assert tuple(switches["location"]["options"]) == LOCATIONS
    assert tuple(switches["guardrail"]["options"]) == GUARDRAILS
    assert tuple(switches["tokens"]) == SWITCH_TOKENS
    for name, options in (("location", LOCATIONS), ("guardrail", GUARDRAILS)):
        assert switches[name]["selected"] in (None, *options), name


def _provider_tokens(text: str, guardrail: str, sentence: str, where: object) -> None:
    """Reject a leftover AWS, Bedrock, Claude or Seoul-Region processing claim."""
    if guardrail == "on":
        text = text.replace(sentence, "")
    found = [token for token in RETIRED_PROVIDER_TOKENS if token in text]
    assert not found, (where, found)


def load() -> dict:
    return validate_web(json.loads(SOURCE.read_text(encoding="utf-8")))


def validate_web(candidate: dict, pins: dict | None = None) -> dict:
    """Validate a website candidate document (the file, or an in-memory copy a test changed)."""
    pins = pins if pins is not None else ai_legal_guard.read_pins()
    assert candidate["schemaVersion"] == 1
    assert candidate["status"] in ("pre-release-candidate-not-published", "integrated-and-verified")
    assert candidate["plannedVersion"] == "1.0.6"
    assert candidate["facts"] == FACTS, "AI facts changed: update the copy in all 17 locales first"
    assert set(candidate["readiness"]) == set(
        READINESS_KEYS + INFORMATIONAL_READINESS_KEYS + tuple(CONDITIONAL_READINESS.values()))
    evidence = candidate.get("legalSelfReviewEvidence")
    assert evidence is None or isinstance(evidence, dict), "AI self-review evidence schema"
    assert all(type(value) is bool for value in candidate["readiness"].values())
    # A flag is true only with a recorded reason (owner decision or readback) next to it.
    reasons = candidate.get("readinessEvidence", {})
    for key, value in candidate["readiness"].items():
        assert not value or (isinstance(reasons.get(key), str) and len(reasons[key]) > 40), (
            f"readiness.{key} is true without a reason in readinessEvidence")
    assert candidate["localeOrder"] == list(LOCALES)
    assert list(candidate["locales"]) == list(LOCALES)
    _check_switches(candidate)
    for locale, entry in candidate["locales"].items():
        assert tuple(entry) == FIELDS, f"{locale}: AI disclosure fields"
        _switch_text(entry, locale)
        template = {key: value for key, value in entry.items() if key != "switchText"}
        tokens = [found for text in _strings(template) for found in PLACEHOLDER.findall(text)]
        assert sorted(set(tokens)) == sorted((HEALTH_PLACEHOLDER, *SWITCH_TOKENS)), (
            f"{locale}: clause 2 carries the platform placeholder; the other tokens are the two owner switches"
        )
        assert tokens.count(HEALTH_PLACEHOLDER) == 1 and HEALTH_PLACEHOLDER in entry["clauses"][1], locale
    for location in LOCATIONS:
        for guardrail in GUARDRAILS:
            _check_web(resolve(candidate, location, guardrail), candidate, location, guardrail, pins)
    korean = "\n".join(_strings(candidate["locales"]["ko"]))
    assert not [term for term in RETIRED_KOREAN_TERMS if term in korean], "Korean AI copy uses a retired term"
    assert "AI 기록 도우미" == candidate["locales"]["ko"]["name"]
    assert "우선 문의 답변" == candidate["locales"]["ko"]["perk"]
    wording = candidate["preReleaseWording"]
    assert list(wording) == list(LOCALES)
    for locale, drafts in wording.items():
        # ai-consent-v3 states facts read from Google's published terms; it carries no "not yet
        # verified" sentence. What is still open is in readiness, switches and unresolved.
        assert len(drafts) == PRE_RELEASE_WORDING_FIELDS, locale
    return candidate


def _check_web(resolved: dict, candidate: dict, location: str, guardrail: str, pins: dict) -> None:
    for locale, entry in resolved["locales"].items():
        where = (locale, location, guardrail)
        switch = candidate["locales"][locale]["switchText"]
        sentence, country = switch["aiGuardrail"]["on"], US_STEMS[locale]
        # Exact pinned sentences, forbidden claims and field hashes (review round 2, F1).
        ai_legal_guard.check_web(locale, entry, location, guardrail, {"guardrailSentence": sentence}, pins)
        clauses = entry["clauses"]
        assert len(clauses) == CLAUSES and len(entry["terms"]) == TERMS_PARAGRAPHS, where
        assert tuple(entry["processorRow"]) == ROW_CELLS, where
        assert tuple(entry["usHealth"]) == US_HEALTH_FIELDS, where
        assert tuple(entry["healthExclusion"]) == ("ios", "android"), where
        texts = _strings(entry)
        assert all(text == text.strip() and len(text) > 2 for text in texts), where
        assert "<" not in "".join(texts), f"{where}: plain text only"
        placeholders = [found for text in texts for found in PLACEHOLDER.findall(text)]
        assert placeholders == [HEALTH_PLACEHOLDER], f"{where}: a switch token is left in the resolved text"
        name = entry["name"]
        assert name in entry["sectionTitle"] or name.casefold() in entry["sectionTitle"].casefold(), where
        assert "Pro" in entry["sectionTitle"], where
        for text in texts:
            _provider_tokens(text, guardrail, sentence, where)
        row = entry["processorRow"]
        # Recipient, model, role and contact (FACTS.md section 3; PIPA 28-8(2)3).
        for token in ("Google", "Gemini", "Vertex AI", "Gemini Enterprise Agent Platform", *GOOGLE_ENTITIES,
                      GOOGLE_CONTACT, "Cloud Data Processing Addendum"):
            assert token in clauses[4], f"{where}: clause 5 names the processor ({token})"
        for token in (*GOOGLE_ENTITIES, GOOGLE_CONTACT):
            assert token in row["recipientContact"], (where, token)
        # Location (PIPA 28-8(2)2): the country, or Google's own statement that there is none.
        for text in (clauses[4], clauses[5], row["country"]):
            if location == "us":
                assert country in text and GOOGLE_GLOBAL_QUOTE not in text, where
            else:
                assert GOOGLE_GLOBAL_QUOTE in text, where
        assert all((GOOGLE_GLOBAL_QUOTE in text) == (location == "global")
                   for text in texts if GOOGLE_GLOBAL_QUOTE in text), where
        if location == "us":
            assert GOOGLE_GLOBAL_QUOTE not in "".join(texts), where
        # The guardrail sentence appears only when the switch is on.
        guarded = [text for text in texts if sentence in text]
        assert (len(guarded) == 2 and sentence in clauses[4] and sentence in row["purpose"]) \
            if guardrail == "on" else not guarded, where
        assert "Cloudflare" in clauses[5] and "DoseWeek" in clauses[5], where
        # Retention (FACTS.md section 2): the DoseWeek figures, and for Google exactly 24 hours in
        # memory and 90 days for a flagged prompt; never "deleted at once" for Google.
        assert number(2, clauses[3]) and number(30, clauses[3]), f"{where}: clause 4 retention"
        for text in (clauses[3], row["retention"], entry["deletion"]):
            assert "Google" in text and number(24, text) and number(90, text), f"{where}: Google retention"
        assert number(18, clauses[10]), f"{where}: clause 11 age"
        for token in HELPLINE_TOKENS:
            assert token in clauses[11], f"{where}: clause 12 helpline {token}"
        assert "Google" in entry["e2eeException"] and "DoseWeek" in entry["e2eeException"], where
        assert "Google" in clauses[7] and "DoseWeek" in clauses[7], where
        assert row["legalBasis"].startswith(PROCESSOR_ROW_PREFIX), where
        assert "28" in row["legalBasis"] and "Cloud Data Processing Addendum" in row["legalBasis"], where
        assert "Google" in row["timingMethod"] and "DoseWeek" in row["timingMethod"], where
        assert "Gemini" in row["purpose"], where
        terms = entry["terms"]
        assert "Plus" in terms[0] and "Pro" in terms[0] and number(7, terms[0]) and number(3, terms[0]), where
        assert number(18, terms[1]), where
        assert "119" in terms[3] and "911" in terms[3], where
        assert all(number(value, terms[4]) for value in (150, 50, 30, 1)) and "UTC" in terms[4], where
        assert entry["perk"].casefold() in terms[0].casefold(), f"{where}: perk named in the Pro paragraph"
        assert entry["perk"].casefold() in terms[7].casefold() and number(1, terms[7]), where
        us_health = entry["usHealth"]
        assert "HealthKit" in us_health["categories"] and "Health Connect" in us_health["categories"], where
        assert "Google" in us_health["categories"] and "DoseWeek" in us_health["categories"], where
        assert "Google" in us_health["processor"] and "Vertex AI" in us_health["processor"], where
        assert number(30, entry["deletion"]), where
        assert "1.0.6" in entry["androidAiFaq"] and "Google Cloud Vertex AI" in entry["androidAiFaq"], where
        scoped, pointer = entry["onDeviceOnly"], entry["iosAiFaq"]
        assert ON_DEVICE_DENIAL_TOKEN in scoped and ON_DEVICE_DENIAL_TOKEN not in pointer, where
        assert ON_DEVICE_MODEL_TOKEN not in scoped + pointer, f"{where}: the model is named once, by the page"
        for token in ("Google Cloud Vertex AI", "Gemini", "DoseWeek"):
            assert token in pointer, f"{where}: the iOS AI answer names the server path ({token})"
        assert name.casefold() in pointer.casefold() and "Pro" in pointer, where
        assert "\n" not in scoped + pointer, where
        ios_only = [entry["healthExclusion"]["ios"], entry["onDeviceScope"], scoped, pointer]
        android_only = [entry["healthExclusion"]["android"], entry["androidAiFaq"],
                        entry["androidBadge"], entry["androidNotUsedItem"]]
        assert "\n" not in entry["androidBadge"] + entry["androidNotUsedItem"], where
        assert not [token for token in IOS_ONLY_FORBIDDEN for text in ios_only if token in text], where
        assert not [token for token in ANDROID_ONLY_FORBIDDEN for text in android_only if token in text], where
        shared = [text for text in texts if text not in ios_only + android_only]
        # The privacy section reaches both platform policies, so its shared text names neither
        # platform; the Terms and the US policy are single pages for both and may.
        both_platforms = [*entry["terms"], *entry["usHealth"].values()]
        for text in shared:
            if text in both_platforms:
                continue
            assert not [token for token in ("Android", "iOS", "Google Play", "App Store") if token in text], (
                f"{where}: shared privacy text names a platform"
            )
    english = resolved["locales"]["en"]
    passage = "\n".join(english["clauses"][4:6] + [english["processorRow"]["timingMethod"]])
    assert "end-to-end" not in passage, "the AI transit is app-layer encryption to the server key, not end-to-end"


def load_app_copy() -> dict:
    return validate_app(json.loads(APP_SOURCE.read_text(encoding="utf-8")))


def validate_app(document: dict, web: dict | None = None, pins: dict | None = None) -> dict:
    """Validate an app copy document (the file, or an in-memory copy a test changed)."""
    pins = pins if pins is not None else ai_legal_guard.read_pins()
    assert document["schemaVersion"] == 1
    assert document["status"] == "pre-release-candidate-not-published"
    assert document["plannedVersion"] == "1.0.6"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}\.\d+", document["consentVersion"])
    assert document["consentVersion"] == COPY_VERSION and document["wireConsentVersion"] == WIRE_CONSENT_VERSION
    assert document["localeOrder"] == list(LOCALES) and list(document["locales"]) == list(LOCALES)
    _check_switches(document)
    keys = document["keys"]
    assert len(keys) == len(set(keys)) and all(key.startswith(("ai.", "pro.")) for key in keys)
    assert not [key for key in RETIRED_APP_KEYS if key in keys], "a retired key is back"
    assert all(key in keys for key in TRANSFER_KEYS), "the transfer notice and its consent box are missing"
    regions = document["helplines"]["regions"]
    assert {code: (item["emergency"], item["crisis"]) for code, item in regions.items()} == {
        "KR": ("119", "109"), "JP": ("119", "0120-279-338"), "US": ("911", "988"),
    }
    assert document["helplines"]["default"]["link"] == "https://findahelpline.com"
    assert document["helplines"]["verification"]["refetchFromOfficialSources"] == "NOT_RUN" or (
        document["helplines"]["verification"]["status"] == "refetched"
    )
    web = web if web is not None else json.loads(SOURCE.read_text(encoding="utf-8"))
    assert document["switches"] == web["switches"], "the two candidate files disagree on the switches"
    for locale, entry in document["locales"].items():
        assert tuple(entry) == ("name", "perk", "copy", "switchText", "whatsNew"), locale
        assert _switch_text(entry, locale) == web["locales"][locale]["switchText"], (
            f"{locale}: the app copy and the website copy must use the same switch sentences")
        found = sorted({token for text in entry["copy"].values() for token in PLACEHOLDER.findall(text)
                        if token in SWITCH_TOKENS})
        assert found == sorted(SWITCH_TOKENS), f"{locale}: every switch token is used by the app copy"
    for location in LOCATIONS:
        for guardrail in GUARDRAILS:
            _check_app(resolve(document, location, guardrail), document, location, guardrail, pins)
    korean = "\n".join(_strings(document["locales"]["ko"]))
    assert not [term for term in RETIRED_KOREAN_TERMS if term in korean], "Korean app copy uses a retired term"
    return document


def _check_app(resolved: dict, document: dict, location: str, guardrail: str, pins: dict) -> None:
    keys = document["keys"]
    reference = resolved["locales"]["ko"]["copy"]
    for locale, entry in resolved["locales"].items():
        where = (locale, location, guardrail)
        switch = document["locales"][locale]["switchText"]
        sentence, country = switch["aiGuardrail"]["on"], US_STEMS[locale]
        copy = entry["copy"]
        assert list(copy) == keys, f"{where}: app copy keys"
        for key, text in copy.items():
            assert isinstance(text, str) and text == text.strip() and text, (where, key)
            found = sorted(PLACEHOLDER.findall(text))
            assert found == sorted(PLACEHOLDER.findall(reference[key])), (where, key, "placeholders")
            assert all(item in APP_PLACEHOLDERS for item in found), (where, key)
            _provider_tokens(text, guardrail, sentence, (where, key))
            if key.endswith(".ios"):
                assert not [token for token in IOS_ONLY_FORBIDDEN if token in text], (where, key)
            elif key.endswith(".android"):
                assert not [token for token in ANDROID_ONLY_FORBIDDEN if token in text], (where, key)
            else:
                assert not [token for token in ("Android", "iOS", "Google Play", "App Store",
                                                "Health Connect", "Apple") if token in text], (where, key)
        body, transfer = copy["ai.consent.a.where.body"], copy["ai.consent.a.transfer.body"]
        for token in ("Google", "Gemini", "Vertex AI", "DoseWeek"):
            assert token in body, (where, token)
        # PIPA 28-8(2): recipient and contact, country, items, time and method, purpose and
        # retention, how to refuse and the effect. ai_legal_guard checks every item on its own:
        # its label, its content and, for purpose and retention, the exact pinned sentences.
        for token in (*GOOGLE_ENTITIES, GOOGLE_CONTACT, "Cloud Data Processing Addendum", "PIPA",
                      copy["ai.consent.a.sent.title"], copy["ai.consent.b.send"]):
            assert token in transfer, (where, "transfer notice", token)
        ai_legal_guard.check_app(locale, copy, location, guardrail, {
            "guardrailSentence": sentence, "recipient": (*GOOGLE_ENTITIES, GOOGLE_CONTACT), "country": country,
            "global": (GOOGLE_GLOBAL_QUOTE, GOOGLE_LOCATIONS_URL), "sentTitle": copy["ai.consent.a.sent.title"],
            "send": copy["ai.consent.b.send"]}, pins)
        for text in (body, transfer):
            if location == "us":
                assert country in text and GOOGLE_GLOBAL_QUOTE not in text, where
            else:
                assert GOOGLE_GLOBAL_QUOTE in text, where
        assert (GOOGLE_LOCATIONS_URL in transfer) == (location == "global"), where
        for key in ("ai.consent.b.processing", "ai.help.inputNote"):
            assert "Google" in copy[key] and "Gemini" in copy[key], (where, key)
            assert switch["aiLocationShort"][location] in copy[key], (where, key)
        guarded = [key for key, text in copy.items() if sentence in text]
        assert guarded == (["ai.consent.a.where.body"] if guardrail == "on" else []), where
        retention = copy["ai.consent.a.retention.body"]
        assert number(2, retention) and number(30, retention), where
        assert "Google" in retention and number(24, retention) and number(90, retention), (
            f"{where}: Screen A states Google's 24-hour memory cache and 90-day abuse log")
        detail = copy["ai.consent.a.check.health.detail"]
        assert number(30, detail) and number(24, detail) and number(90, detail) and "Google" in detail, where
        assert number(18, copy["ai.consent.a.check.age"]), where
        assert "Google" in copy["ai.consent.a.e2ee.body"], where
        assert "Google" in copy["ai.consent.a.check.transfer"], where
        assert number(7, copy["ai.consent.b.purpose.weekly"]), where
        assert copy["pro.support.priority"].startswith(entry["perk"]) and number(1, copy["pro.support.priority"]), where
        assert entry["name"].casefold() in entry["whatsNew"].casefold(), f"{where}: What's New names the feature"


def screen_a_strings(copy: dict, platform: str, region: str) -> list[str]:
    """Screen A strings in screen order for the consent receipt's textHash (ai-consent-v3).

    Same order on both platforms: the transfer block sits after "You don't have to agree" and
    right above the boxes; the US storefront adds the US policy link after it. `copy` is one
    locale's RESOLVED copy. The hash is SHA-256 over the strings joined with U+000A
    (AIAssistConsent.swift textHash).
    """
    assert platform in ("ios", "android") and region in ("default", "US"), (platform, region)
    keys = ["title", "lead", "sent.title", "sent.body", "notSent.body", f"notSent.health.{platform}",
            "where.title", "where.body", "retention.title", "retention.body", "e2ee.title", "e2ee.body",
            "optional.title", "optional.body", "transfer.title", "transfer.body"]
    if region == "US":
        keys.append("region.us")
    keys += ["check.health", "check.health.detail", "check.transfer", "check.age", "later", "agree"]
    return [copy[SCREEN_A_PREFIX + key] for key in keys]


def screen_a_hash(copy: dict, platform: str, region: str) -> str:
    text = "\n".join(screen_a_strings(copy, platform, region))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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
    if "resolvedSwitches" not in candidate:
        candidate = resolve(candidate, *(selection(candidate) or STAGING_PREVIEW_SWITCHES))
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
    candidate = candidate or load()
    if "resolvedSwitches" not in candidate:
        candidate = resolve(candidate, *(selection(candidate) or STAGING_PREVIEW_SWITCHES))
    return candidate["locales"][locale]["deletion"]


def resolve_app_copy(location: str, guardrail: str) -> dict:
    """The app copy the apps ship for one switch combination (no token, no switchText)."""
    return resolve(load_app_copy(), location, guardrail)


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
    chosen = selection(candidate)
    assert chosen is not None, (
        "AI owner switches are not decided: set switches.location.selected (us or global) and "
        "switches.guardrail.selected (off or on) in both candidate files"
    )
    # A switch value that raises an open legal point needs its own flag (review round 2, F8).
    for (switch, value), flag in CONDITIONAL_READINESS.items():
        if dict(zip(("location", "guardrail"), chosen))[switch] == value:
            assert candidate["readiness"].get(flag) is True, (
                f"AI switch {switch}={value} is selected but readiness.{flag} is not true"
            )
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
          f"status={web['status']}; consentVersion={app['consentVersion']}; wire={app['wireConsentVersion']}; "
          f"validated {len(LOCATIONS) * len(GUARDRAILS)} switch combinations; selected={selection(app)}")
