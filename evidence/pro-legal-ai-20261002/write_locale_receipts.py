#!/usr/bin/env python3
"""Write the per-locale review receipts of critic C23 (lane LEGAL-AI, 2026-10-02).

    python3 evidence/pro-legal-ai-20261002/write_locale_receipts.py          # write
    python3 evidence/pro-legal-ai-20261002/write_locale_receipts.py --check  # compare only

Inputs: docs/ai-app-copy.candidate.json (Screen A, Screen B, the settings copy and the perk
line), con-pro-ai-copy.snapshot.json (the shipped labels and refusal templates) and
back-translation/<locale>.txt. A line that starts with "! " is a finding or review note;
"key = text" is the English back-translation of one string, where key is the full copy key or
one of the SHORT aliases; a line that starts with "# " is a comment, and the comment
"# round: <name>" names the session that recorded the lines after it. The receipts pin the
SHA-256 of the exact text that was read, so a later copy change makes
scripts/test_ai_assistant_legal.py fail until the locale is reviewed again.

Coverage (review round 1, PRO-SPEC section 8): every one of the 50 app keys and the 15 CON-PRO
keys has a recorded back-translation in each of the 14 locales. A locale with a missing key
gets flag.recommended=false and names the keys.

Current refresh: Codex checked the changed scope in ko/en/ja and recorded same-model
back-translations for the four changed app strings in the other 14 locales. The unchanged
46 app and 15 shared strings are reused only for matching pinned inputs. No native speaker
or counsel review is claimed, and these source receipts do not set release-readiness flags.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LOCALES = ("ko", "en", "ja", "de", "fr", "es", "it", "nl", "pt-PT", "pl", "sv", "hi",
           "pt-BR", "ar", "zh-Hans", "zh-Hant", "tr")
SHORT = {
    "lead": "ai.consent.a.lead", "sent": "ai.consent.a.sent.body",
    "notSent": "ai.consent.a.notSent.body", "where": "ai.consent.a.where.body",
    "retention": "ai.consent.a.retention.body", "e2ee": "ai.consent.a.e2ee.body",
    "optional": "ai.consent.a.optional.body", "checkHealth": "ai.consent.a.check.health",
    "checkDetail": "ai.consent.a.check.health.detail", "checkAge": "ai.consent.a.check.age",
    "processing": "ai.consent.b.processing",
    "r.dose": "ai.refuse.dose", "r.sideEffect": "ai.refuse.sideEffect",
    "r.diagnosis": "ai.refuse.diagnosis", "r.drugInfo": "ai.refuse.drugInfo",
    "r.diet": "ai.refuse.diet", "r.pregnancy": "ai.refuse.pregnancy", "r.minor": "ai.refuse.minor",
    "r.other": "ai.refuse.other", "emergency": "ai.emergency",
    "emergencyGeneric": "ai.emergency.generic", "crisis": "ai.crisis",
    "crisisGeneric": "ai.crisis.generic", "header": "ai.label.header", "output": "ai.label.output",
    "export": "ai.label.export",
}
AGENT = "Codex AI source reviewer; not a human, native speaker or legal counsel"
STATUS = {
    locale: ("codex-changed-scope-self-review", AGENT,
             "Codex checked the four changed consent strings against actual source facts on "
             "2026-10-03; unchanged strings retain matching pinned prior source evidence. "
             "Source self-review only, not runtime verification or release acceptance.")
    for locale in ("ko", "en", "ja")
}
BACK_TRANSLATION_METHOD = (
    "same-model back-translation: the four changed app strings were translated back in the "
    "Codex refresh on 2026-10-03 using the retained per-row English evidence. The unchanged "
    "46 app strings and 15 CON-PRO strings retain their prior recordings only because the "
    "pinned source values match. Not blind, not independent; no native speaker or counsel "
    "review is claimed. This source receipt does not set factual or runtime readiness flags."
)
ROUNDS = ("writing-session", "review-fix-1", "codex-refresh-2026-10-03")

def canonical_sha256(value):
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def notes(locale, allowed):
    findings, translation, rounds = [], {}, {name: [] for name in ROUNDS}
    current = ROUNDS[0]
    for number, line in enumerate((HERE / "back-translation" / f"{locale}.txt").read_text(encoding="utf-8").splitlines(), 1):
        if line.startswith("# round: "):
            current = line[len("# round: "):].strip()
            assert current in ROUNDS, (locale, number, current)
            continue
        if line.startswith("# "):
            continue
        if line.startswith("! "):
            findings.append(line[2:].strip())
            continue
        key, separator, text = line.partition(" = ")
        key = SHORT.get(key, key)
        assert separator and key in allowed and text.strip(), (locale, number)
        assert key not in translation, (locale, key)
        translation[key] = text.strip()
        rounds[current].append(key)
    return findings, translation, rounds


def build():
    app = json.loads((ROOT / "docs/ai-app-copy.candidate.json").read_text(encoding="utf-8"))
    snapshot = json.loads((HERE / "con-pro-ai-copy.snapshot.json").read_text(encoding="utf-8"))
    app_keys = list(app["keys"])
    scope = {
        "screenA": [key for key in app_keys if key.startswith("ai.consent.a.")],
        "screenB": [key for key in app_keys if key.startswith("ai.consent.b.")],
        "settingsAndPerk": [key for key in app_keys if not key.startswith("ai.consent.")],
        "labels": [key for key in snapshot["keys"] if key.startswith("ai.label.")],
        "refusalTemplates": [key for key in snapshot["keys"] if not key.startswith("ai.label.")],
    }
    order = [*app_keys, *snapshot["keys"]]
    assert len(order) == len(set(order)) == sum(len(keys) for keys in scope.values())
    receipts, coverage_missing = {}, {}
    for locale in LOCALES:
        findings, translation, rounds = notes(locale, set(order))
        copy = app["locales"][locale]["copy"]
        status, reviewer, method = STATUS.get(
            locale, ("back-translation-only", AGENT, BACK_TRANSLATION_METHOD))
        receipt = {
            "schemaVersion": 1,
            "lane": "LEGAL-AI",
            "date": "2026-10-03",
            "locale": locale,
            "consentVersion": app["consentVersion"],
            "scope": scope,
            "sources": {
                "appCopy": {
                    "path": "docs/ai-app-copy.candidate.json",
                    "keys": "all 50 keys: ai.consent.a.*, ai.consent.b.*, ai.help.inputNote, "
                            "ai.settings.* and pro.support.priority",
                    "sha256": canonical_sha256({key: copy[key] for key in app_keys}),
                },
                "conProSharedCopy": {
                    "path": "evidence/pro-legal-ai-20261002/con-pro-ai-copy.snapshot.json",
                    "origin": snapshot["origin"],
                    "keys": snapshot["keys"],
                    "sha256": canonical_sha256(snapshot["locales"][locale]),
                },
            },
            "status": status,
            "reviewer": reviewer,
            "method": method,
            "nativeSpeakerReview": False,
            "counselReview": False,
            "flag": {
                "key": f"locales.{locale}",
                "recommended": locale not in ("ko", "ja"),
                "condition": {
                    "ko": "source-only Codex review recorded; recommendation remains false while "
                          "factual consent/publication prerequisites are unverified; no counsel "
                          "or native-speaker prerequisite is asserted",
                    "ja": "source-only Codex review recorded; recommendation remains false until "
                          "actual foreign-recipient/country/assent facts are completed; no counsel "
                          "or native-speaker prerequisite is asserted",
                    "en": "source-only Codex review recommendation; acceptance does not set "
                          "factual or runtime release flags",
                }.get(locale, "source-only same-model back-translation recommendation; acceptance "
                              "does not set factual or runtime release flags"),
            },
            "findings": findings,
        }
        if status == "back-translation-only":
            missing = [key for key in order if key not in translation]
            receipt["backTranslation"] = {key: translation[key] for key in order if key in translation}
            receipt["backTranslationRecord"] = {
                "recorded": len(receipt["backTranslation"]), "total": len(order),
                "byRound": {name: len(keys) for name, keys in rounds.items()},
                "missing": missing,
            }
            if missing:
                # PRO-SPEC section 8: a locale without its complete receipt keeps its flag off.
                coverage_missing[locale] = missing
                receipt["flag"]["recommended"] = False
                receipt["flag"]["condition"] = (
                    "stays false: no recorded back-translation for " + ", ".join(missing))
        else:
            assert not translation, locale
        receipts[locale] = receipt
    summary = {
        "schemaVersion": 1,
        "lane": "LEGAL-AI",
        "date": "2026-10-03",
        "consentVersion": app["consentVersion"],
        "statuses": {locale: receipt["status"] for locale, receipt in receipts.items()},
        "backTranslationOnly": [l for l, r in receipts.items() if r["status"] == "back-translation-only"],
        "nativeSpeakerReviewed": [],
        "counselReviewed": [],
        "flagsOff": [l for l, r in receipts.items() if not r["flag"]["recommended"]],
        "backTranslationKeyCoverage": {
            "locales": [l for l, r in receipts.items() if r["status"] == "back-translation-only"],
            "perLocale": {
                group: {
                    "recorded": min(
                        sum(key in r["backTranslation"] for key in keys)
                        for r in receipts.values() if r["status"] == "back-translation-only"),
                    "total": len(keys),
                } for group, keys in scope.items()
            },
            "appKeys": {
                "recorded": min(
                    sum(key in r["backTranslation"] for key in app_keys)
                    for r in receipts.values() if r["status"] == "back-translation-only"),
                "total": len(app_keys),
            },
            "missing": coverage_missing,
            "recordedIn": {
                "writing-session": "7 unchanged long consent strings and 15 unchanged CON-PRO strings",
                "review-fix-1": "39 unchanged app strings; prior recordings reused for matching inputs",
                "codex-refresh-2026-10-03": "4 changed app strings with current recorded English back-translations",
            },
        },
        "honesty": "Current changed-scope review is by Codex. ko/en/ja have source self-review; "
                   "14 locales have recorded same-model back-translations, not blind or independent. "
                   "No native-speaker or counsel review is claimed. Unchanged recordings are reused "
                   "only for matching source values. Factual/runtime release flags remain false; "
                   "KO/JA recommendations stay false for unresolved factual consent disclosures.",
    }
    return receipts, summary


def main():
    receipts, summary = build()
    outputs = {HERE / "locale-review" / f"{locale}.json": receipt for locale, receipt in receipts.items()}
    outputs[HERE / "locale-review" / "summary.json"] = summary
    stale = []
    for path, value in outputs.items():
        text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
        if "--check" in sys.argv:
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                stale.append(path.name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    assert not stale, f"receipts differ from their inputs: {stale}"
    print(f"OK: {len(receipts)} locale receipts; flags off: {summary['flagsOff']}; "
          f"back-translation only: {len(summary['backTranslationOnly'])}")


if __name__ == "__main__":
    main()
