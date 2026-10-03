#!/usr/bin/env python3
"""ai-consent-v3: per-locale hashes for the four owner-switch combinations and the apply list.

    python3 scripts/ai_consent_apply.py            # write docs/ai-consent-v3-apply.json
    python3 scripts/ai_consent_apply.py --check    # fail when that file is stale
    python3 scripts/ai_consent_apply.py --export DIR   # also write the resolved copy per combination

The two open owner decisions are SWITCH_LOCATION (us | global) and SWITCH_AWS_GUARDRAIL (off | on).
Once the owner picks, the app and server lanes take the block of that one combination: the
resolved strings (--export), the Screen A display hashes and the server registry document.

Hash rule (AIAssistConsent.swift `textHash`): SHA-256, lowercase hex, of the Screen A strings in
screen order joined with U+000A. Screen order: ai_assistant_candidate.screen_a_strings.
The hashes here are taken over the strings of docs/ai-app-copy.candidate.json as written
("source form"). An app that changes the bytes it shows (for example the no-break spaces the
Android XML and the iOS catalog insert into Korean) must hash what it shows: run
`display_hash(strings)` from this module over the shipped strings and publish those values.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import ai_assistant_candidate as candidate
import ai_legal_guard

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/ai-consent-v3-apply.json"
V2_APP_KEYS_REMOVED = ("ai.consent.a.region.jp",)
NEW_KEYS = ("ai.consent.a.transfer.title", "ai.consent.a.transfer.body", "ai.consent.a.check.transfer")
CHANGED_KEYS = ("ai.consent.a.where.body", "ai.consent.a.retention.body", "ai.consent.a.e2ee.body",
                "ai.consent.a.check.health.detail", "ai.consent.b.processing", "ai.help.inputNote")
DISPLAY_VARIANTS = (("ios", "default"), ("ios", "US"), ("android", "default"), ("android", "US"))
# Server AI_CONSENT_RECIPIENTS (PRO-SRV-AI src/aiConsent.js): only google-vertex-global exists at
# cfc906f46 / e14e5ae97. The us token is this lane's proposal; the server lane adds it.
RECIPIENT_TOKENS = {"global": "google-vertex-global", "us": "google-vertex-us"}
# Review round 2 (F8): the guardrail switch is bound in data, not only in an instruction. The server
# checks answer text with the Seoul Guardrail in exactly these locales; with the switch off the list
# is empty and no ApplyGuardrail call may be made, because the off text does not name AWS.
GUARDRAIL_LOCALES = {"off": [], "on": ["en", "es", "fr"]}
GUARDRAIL_TOKENS = {"off": None, "on": "aws-guardrail-seoul"}


def canonical_sha256(value: object) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def display_hash(strings: list[str]) -> str:
    return hashlib.sha256("\n".join(strings).encode("utf-8")).hexdigest()


def android_name(key: str) -> str:
    """The Android string resource name of an app copy key (values*/ai_assistant_screens.xml)."""
    key = re.sub(r"\.(android)$", "", key)
    return re.sub(r"(?<=[a-z])(?=[A-Z])", "_", key).replace(".", "_").lower()


def combination_name(location: str, guardrail: str) -> str:
    return f"{location}-{guardrail}"


def build() -> dict:
    document = candidate.load_app_copy()
    pins = ai_legal_guard.read_pins()
    combinations = {}
    for location in candidate.LOCATIONS:
        for guardrail in candidate.GUARDRAILS:
            resolved = candidate.resolve(document, location, guardrail)
            locales, registry = {}, {}
            for locale, entry in resolved["locales"].items():
                copy = entry["copy"]
                screen = {f"{platform}.{region}": candidate.screen_a_hash(copy, platform, region)
                          for platform, region in DISPLAY_VARIANTS}
                assert len(set(screen.values())) == len(screen), (locale, "display variants must differ")
                locales[locale] = {"appCopySha256": canonical_sha256(copy), "screenA": screen,
                                   "legalPinSha256": pins["combinationSha256"][
                                       combination_name(location, guardrail)][locale]["app"]}
                registry[locale] = list(screen.values())
            combinations[combination_name(location, guardrail)] = {
                "location": location, "guardrail": guardrail,
                "serverVertexLocation": location,
                "locales": locales,
                "serverRegistry": {
                    "current": {locale: candidate.WIRE_CONSENT_VERSION for locale in candidate.LOCALES},
                    "recipients": {candidate.WIRE_CONSENT_VERSION: RECIPIENT_TOKENS[location]},
                    "guardrail": {candidate.WIRE_CONSENT_VERSION: GUARDRAIL_TOKENS[guardrail]},
                    "guardrailLocales": {candidate.WIRE_CONSENT_VERSION: GUARDRAIL_LOCALES[guardrail]},
                    "texts": {candidate.WIRE_CONSENT_VERSION: registry},
                },
            }
    hashes = [value["locales"][locale]["appCopySha256"] for value in combinations.values()
              for locale in candidate.LOCALES]
    assert len(set(hashes)) == len(hashes), "every combination and locale has its own text"
    return {
        "schemaVersion": 1,
        "status": "candidate-not-applied: the owner has not chosen the switches; nothing here is published",
        "consentVersion": document["consentVersion"],
        "wireConsentVersion": document["wireConsentVersion"],
        "ownerSwitches": {"SWITCH_LOCATION": list(candidate.LOCATIONS),
                          "SWITCH_AWS_GUARDRAIL": list(candidate.GUARDRAILS),
                          "selected": candidate.selection(document)},
        "hashRule": "screenA: SHA-256 lowercase hex of the Screen A strings in screen order joined with U+000A "
                    "(AIAssistConsent.swift textHash). appCopySha256: SHA-256 of the canonical JSON (sorted "
                    "keys, no spaces, UTF-8) of all resolved app copy keys of the locale.",
        "hashInput": "source form: the strings of docs/ai-app-copy.candidate.json after resolving the switch "
                     "tokens. If an app ships different bytes (no-break spaces, escapes), the registry must "
                     "carry display_hash() of the shipped strings instead.",
        "screenAOrder": {"keys": ["title", "lead", "sent.title", "sent.body", "notSent.body",
                                  "notSent.health.<platform>", "where.title", "where.body", "retention.title",
                                  "retention.body", "e2ee.title", "e2ee.body", "optional.title", "optional.body",
                                  "transfer.title", "transfer.body", "region.us (US storefront only)",
                                  "check.health", "check.health.detail", "check.transfer", "check.age", "later",
                                  "agree"],
                         "displayVariants": [f"{platform}.{region}" for platform, region in DISPLAY_VARIANTS],
                         "serverLimit": "MAX_DISPLAY_VARIANTS = 6 in src/aiConsent.js; v3 publishes 4 per locale"},
        "keys": {"new": list(NEW_KEYS), "changed": list(CHANGED_KEYS), "retired": list(V2_APP_KEYS_REMOVED),
                 "androidNames": {key: android_name(key) for key in (*NEW_KEYS, *CHANGED_KEYS)}},
        "apply": APPLY,
        "combinations": combinations,
    }


APPLY = {
    "precondition": "The owner picks SWITCH_LOCATION and SWITCH_AWS_GUARDRAIL. Set switches.location.selected and "
                    "switches.guardrail.selected in docs/ai-app-copy.candidate.json and "
                    "docs/ai-assistant-content.candidate.json, then export: python3 scripts/ai_consent_apply.py "
                    "--export <dir>. Use the file of the chosen combination only.",
    "ios": [
        "DoseDay/Resources/Localizable.xcstrings: for each of the 17 locales replace the 6 changed keys "
        "(ai.consent.a.where.body, ai.consent.a.retention.body, ai.consent.a.e2ee.body, "
        "ai.consent.a.check.health.detail, ai.consent.b.processing, ai.help.inputNote), add the 3 new keys "
        "(ai.consent.a.transfer.title, ai.consent.a.transfer.body, ai.consent.a.check.transfer) and delete "
        "ai.consent.a.region.jp. Text = the exported resolved copy, iOS variant keys only.",
        "Packages/DoseDayCore/Sources/DoseDayCore/AIAssist/AIAssistWire.swift:19 consentVersion = "
        "\"ai-consent-v3\".",
        "DoseDay/Features/AIAssistant/AIConsentSheet.swift shownStrings(region:): after ai.consent.a.optional.body "
        "append ai.consent.a.transfer.title and ai.consent.a.transfer.body for EVERY region; regionalKey returns "
        "only ai.consent.a.region.us for US (remove the JP case); after ai.consent.a.check.health.detail append "
        "ai.consent.a.check.transfer; then check.age, later, agree. The body shows the same order: a section "
        "(transfer.title, [transfer.body]) for every region, the US link, then three boxes.",
        "AIConsentSheet.swift: add @State transferConsent = false and a third checkBox(titleKey: "
        "ai.consent.a.check.transfer, detailKey: nil, identifier: ai.consentA.transfer) between the health box and "
        "the age box; the agree button is enabled only when all three are ticked. View-only mode shows the "
        "transfer section without the box.",
        "Tests that pin the v2 literals (AIAssistConsentTests, AIAssistTestSupport, AIAssistUITestStub, "
        "scripts/korean_tone_allowlist.json rows for the changed keys) follow the new strings and version.",
        "After the catalog edit compute display_hash() over AIConsentSheet.shownStrings for region default and US "
        "in each locale; if the catalog adds no-break spaces these differ from the source-form hashes here and "
        "the computed values go to the server registry.",
        "Do not edit a consent string in the catalog by hand: docs/ai-consent-v3-legal-pins.json pins the exact "
        "legal sentences per locale and scripts/ai_legal_guard.py rejects a changed, added or dropped sentence.",
    ],
    "android": [
        "app/src/main/res/values*/ai_assistant_screens.xml (17 files): replace ai_consent_a_where_body, "
        "ai_consent_a_retention_body, ai_consent_a_e2ee_body, ai_consent_a_check_health_detail, "
        "ai_consent_b_processing, ai_help_input_note; add ai_consent_a_transfer_title, ai_consent_a_transfer_body, "
        "ai_consent_a_check_transfer; delete ai_consent_a_region_jp. Text = the exported resolved copy, Android "
        "variant keys only; update the header comment to consentVersion 2026-10-03.3.",
        "app/src/main/java/com/wonyoungchoi/doseweek/domain/aiassist/AiConsentPolicy.kt: VERSION = "
        "\"ai-consent-v3\", COPY_VERSION = \"2026-10-03.3\"; canAgree and grant take a third argument "
        "transferTicked and require all three.",
        "app/src/main/java/com/wonyoungchoi/doseweek/features/aiassist/AiAssistScreens.kt (Screen A, about lines "
        "414-441): remove the `storefrontRegion == \"JP\"` block; after the optional block add ConsentBlock("
        "ai_consent_a_transfer_title, ai_consent_a_transfer_body) for every storefront, then the US link; add a "
        "third ConsentCheck (ai_consent_a_check_transfer, tag ai.consent.transfer) between health and age; "
        "enabled = health && transfer && age.",
        "The Android consent text hash is injected (AiAssistController consentTextHash) and has no production "
        "implementation yet: implement it as SHA-256 hex of the shown strings in the screen order of this file "
        "joined with U+000A, over the exact resource strings. The Android XML writes literal \\u00A0 in Korean; "
        "hash the resolved resource values and publish those hashes.",
        "Tests that pin v2 (AiConsentPolicyTest, AiAssistControllerTest, AiAssistClientTest, AiAssistUiTest) follow.",
    ],
    "server": [
        "ai-consent-texts.json on the host = combinations.<chosen>.serverRegistry, with the hashes replaced by the "
        "app-computed display hashes when the apps ship different bytes. current: all 17 locales on ai-consent-v3.",
        "DOSEWEEK_AI_VERTEX_LOCATION must equal the chosen location. For us the request host is "
        "aiplatform.us.rep.googleapis.com (Google multi-region endpoint) and the non-global price applies "
        "(+10%: USD 0.825 / 4.125 per 1M through 2026-12-31, then 1.65 / 8.25).",
        "src/aiConsent.js AI_CONSENT_RECIPIENTS has only vertex: google-vertex-global. For location us the server "
        "lane adds a recipient token (proposed: google-vertex-us) and binds it to the configured location, so a "
        "receipt for the us text never authorizes a global send and the reverse.",
        "Guardrail off: guardrailLocales must be [] and no ApplyGuardrail call may be made, because the off text "
        "does not name Amazon Web Services. Guardrail on: keep the pinned Seoul Guardrail for en, es, fr.",
        "Bind the guardrail like the location (review round 2, F8): serverRegistry.guardrail and "
        "serverRegistry.guardrailLocales of the chosen combination are data. The server lane loads them with the "
        "registry and refuses to start, or to accept a receipt, when its configured guardrail locales differ from "
        "serverRegistry.guardrailLocales[ai-consent-v3]. Until the server enforces this, the off text must not ship "
        "while the server still calls ApplyGuardrail (server report: guardrailDecision stays pinned).",
        "The copy changed in review round 2 (consentVersion 2026-10-03.3): take the strings again from a fresh "
        "--export; the Screen A hashes of 2026-10-03.2 are void.",
    ],
}


def main() -> None:
    document = build()
    text = json.dumps(document, ensure_ascii=False, indent=1) + "\n"
    if "--check" in sys.argv:
        assert OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == text, (
            "docs/ai-consent-v3-apply.json is stale: run python3 scripts/ai_consent_apply.py")
    else:
        OUTPUT.write_text(text, encoding="utf-8")
    if "--export" in sys.argv:
        directory = Path(sys.argv[sys.argv.index("--export") + 1])
        directory.mkdir(parents=True, exist_ok=True)
        app = candidate.load_app_copy()
        for location in candidate.LOCATIONS:
            for guardrail in candidate.GUARDRAILS:
                resolved = candidate.resolve(app, location, guardrail)
                export = {"consentVersion": app["consentVersion"], "wireConsentVersion": app["wireConsentVersion"],
                          "location": location, "guardrail": guardrail,
                          "locales": {locale: {key: entry["copy"][key] for key in (*NEW_KEYS, *CHANGED_KEYS)}
                                      for locale, entry in resolved["locales"].items()}}
                path = directory / f"ai-app-copy.{combination_name(location, guardrail)}.changed-keys.json"
                path.write_text(json.dumps(export, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"OK: {len(document['combinations'])} combinations x {len(candidate.LOCALES)} locales; "
          f"selected={document['ownerSwitches']['selected']}")


if __name__ == "__main__":
    main()
