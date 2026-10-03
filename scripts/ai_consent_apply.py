#!/usr/bin/env python3
"""ai-consent-v3: per-locale hashes for the four owner-switch combinations and the apply list.

    python3 scripts/ai_consent_apply.py            # write docs/ai-consent-v3-apply.json
    python3 scripts/ai_consent_apply.py --check    # fail when that file is stale
    python3 scripts/ai_consent_apply.py --export DIR   # also write the resolved copy per combination

    python3 scripts/ai_consent_apply.py --export-selected DIR   # final copy of the owner's combination

The two owner switches are SWITCH_LOCATION (us | global) and SWITCH_AWS_GUARDRAIL (off | on). The
owner chose global and off on 2026-10-03. The app and server lanes take the block of that one
combination: the resolved strings (--export-selected), the Screen A display hashes and the server
registry document.

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
        "status": "candidate-not-applied: the owner chose SWITCH_LOCATION=global and SWITCH_AWS_GUARDRAIL=off "
                  "(2026-10-03 17:35 and 19:00 KST); apply combinations.global-off only; nothing here is "
                  "published or applied to an app or server",
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
    "precondition": "The owner picked SWITCH_LOCATION=global and SWITCH_AWS_GUARDRAIL=off (late-decisions.md, "
                    "2026-10-03 17:35 and 19:00 KST); switches.location.selected and switches.guardrail.selected "
                    "carry that in docs/ai-app-copy.candidate.json and docs/ai-assistant-content.candidate.json. "
                    "Export the final copy: python3 scripts/ai_consent_apply.py --export-selected <dir> (iOS, "
                    "Android, web, server registry). Use combination global-off only. The guardrail-off text "
                    "must not ship before the server stops calling AWS ApplyGuardrail "
                    "(readiness.serverGuardrailCallRemovedReadback).",
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
        "variant keys only; update the header comment to consentVersion 2026-10-03.4.",
        "app/src/main/java/com/wonyoungchoi/doseweek/domain/aiassist/AiConsentPolicy.kt: VERSION = "
        "\"ai-consent-v3\", COPY_VERSION = \"2026-10-03.4\"; canAgree and grant take a third argument "
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
        "The copy changed in review round 3 (consentVersion 2026-10-03.4: the Global wording rule, the sentence "
        "on the recipients' countries, the contracting-entity wording): take the strings again from a fresh "
        "--export-selected; the Screen A hashes of 2026-10-03.2 and 2026-10-03.3 are void.",
        "Selected combination global-off: recipients = {ai-consent-v3: google-vertex-global}, guardrail = "
        "{ai-consent-v3: null}, guardrailLocales = {ai-consent-v3: []}; DOSEWEEK_AI_VERTEX_LOCATION = global. "
        "The release gate needs readiness.serverGuardrailCallRemovedReadback: a readback that the deployed "
        "server makes no ApplyGuardrail call.",
    ],
}


def export_selected(directory: Path, document: dict) -> list[Path]:
    """The final copy of the owner's combination: one file each for iOS, Android, web and the server."""
    chosen = candidate.selection(candidate.load_app_copy())
    assert chosen is not None, "the owner switches are not selected"
    name = combination_name(*chosen)
    block = document["combinations"][name]
    app, web = candidate.resolve(candidate.load_app_copy(), *chosen), candidate.resolve(candidate.load(), *chosen)
    head = {"consentVersion": document["consentVersion"], "wireConsentVersion": document["wireConsentVersion"],
            "location": chosen[0], "guardrail": chosen[1], "combination": name}
    outputs = {}
    for platform, other in (("ios", ".android"), ("android", ".ios")):
        locales = {}
        for locale, entry in app["locales"].items():
            copy = {key: text for key, text in entry["copy"].items() if not key.endswith(other)}
            locales[locale] = {
                "name": entry["name"], "perk": entry["perk"], "whatsNew": entry["whatsNew"], "copy": copy,
                "screenA": {region: {"strings": candidate.screen_a_strings(entry["copy"], platform, region),
                                     "sha256": block["locales"][locale]["screenA"][f"{platform}.{region}"]}
                            for region in ("default", "US")}}
            if platform == "android":
                locales[locale]["androidNames"] = {key: android_name(key) for key in copy}
        outputs[f"{platform}.app-copy.{name}.json"] = {
            **head, "platform": platform,
            "note": "Resolved text, no switch token. Keys ending in the other platform's suffix are left out. "
                    "screenA.sha256 is over these source strings joined with U+000A; an app that ships other "
                    "bytes hashes what it shows.",
            "changedOrNewKeys": [*NEW_KEYS, *CHANGED_KEYS], "retiredKeys": list(V2_APP_KEYS_REMOVED),
            "locales": locales}
    outputs[f"web.ai-assistant-content.{name}.json"] = {
        **head, "note": "Resolved website text per locale: privacy section clauses, processor row, Terms "
                        "paragraphs, US consumer-health sentences, deletion paragraph. {healthExclusion} in "
                        "clause 2 is the platform placeholder that scripts/ai_assistant_candidate.integrate fills.",
        "locales": web["locales"]}
    outputs[f"server.ai-consent-texts.{name}.json"] = {
        **head, "serverVertexLocation": block["serverVertexLocation"],
        "note": "serverRegistry is the complete ai-consent-texts.json document for this combination. Hashes are "
                "source-form; replace them with app-computed display hashes if an app ships other bytes.",
        "serverRegistry": block["serverRegistry"]}
    directory.mkdir(parents=True, exist_ok=True)
    written = []
    for filename, value in outputs.items():
        path = directory / filename
        path.write_text(json.dumps(value, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        written.append(path)
    return written


def main() -> None:
    document = build()
    text = json.dumps(document, ensure_ascii=False, indent=1) + "\n"
    if "--check" in sys.argv:
        assert OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == text, (
            "docs/ai-consent-v3-apply.json is stale: run python3 scripts/ai_consent_apply.py")
    else:
        OUTPUT.write_text(text, encoding="utf-8")
    if "--export-selected" in sys.argv:
        export_selected(Path(sys.argv[sys.argv.index("--export-selected") + 1]), document)
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
