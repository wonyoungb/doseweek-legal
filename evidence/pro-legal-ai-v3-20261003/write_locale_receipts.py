#!/usr/bin/env python3
"""Per-locale receipts for the ai-consent-v3 candidate copy (lane LEGAL-AI, 2026-10-03).

    python3 evidence/pro-legal-ai-v3-20261003/write_locale_receipts.py          # write
    python3 evidence/pro-legal-ai-v3-20261003/write_locale_receipts.py --check  # compare only

What these receipts say, and nothing more: which text was written, by whom, and what was not done.
The 9 changed or new app keys and the switch sentences were written from the English reference by
the lane agent (an AI model) in one session, in all 17 locales. For them there is no native-speaker
review, no counsel review and no back-translation. The other 43 keys are byte-identical to
ai-consent-v2 (checked per key against v2-app-copy-key-hashes.json); their earlier same-model
back-translations are in evidence/pro-legal-ai-20261002 (historical, v2 text).
Every flag stays not recommended. The receipts pin the SHA-256 of the exact template and of each
of the four switch combinations, so a later copy change makes scripts/test_ai_assistant_legal.py
fail until this script is run again.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import ai_assistant_candidate as candidate  # noqa: E402
import ai_consent_apply  # noqa: E402

AGENT = "Claude lane agent (AI model); not a human, native speaker or legal counsel"
STATUS = "same-model-authoring-no-review"
METHOD = ("The changed and new strings were written from the English reference by the same AI model in one "
          "session on 2026-10-03, using the facts in the lane evidence FACTS.md. No back-translation, no blind "
          "or independent check, no native speaker and no counsel. Unchanged strings are byte-identical to "
          "ai-consent-v2 and keep only their v2 same-model back-translation.")


def canonical_sha256(value):
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def build():
    app = candidate.load_app_copy()
    v2 = json.loads((HERE / "v2-app-copy-key-hashes.json").read_text(encoding="utf-8"))
    keys = list(app["keys"])
    apply = ai_consent_apply.build()
    receipts = {}
    for locale in candidate.LOCALES:
        entry = app["locales"][locale]
        copy = entry["copy"]
        old = v2["locales"][locale]
        unchanged = [key for key in keys
                     if old.get(key) == hashlib.sha256(copy[key].encode("utf-8")).hexdigest()]
        changed = [key for key in keys if key not in unchanged]
        receipts[locale] = {
            "schemaVersion": 2,
            "lane": "LEGAL-AI",
            "date": "2026-10-03",
            "locale": locale,
            "consentVersion": app["consentVersion"],
            "wireConsentVersion": app["wireConsentVersion"],
            "sources": {
                "appCopyTemplate": {
                    "path": "docs/ai-app-copy.candidate.json",
                    "keys": f"all {len(keys)} keys with the switch tokens unresolved, plus switchText",
                    "sha256": canonical_sha256({"copy": {key: copy[key] for key in keys},
                                                "switchText": entry["switchText"]}),
                },
                "combinations": {name: block["locales"][locale] for name, block in apply["combinations"].items()},
            },
            "changedOrNewKeys": changed,
            "unchangedFromV2": {"count": len(unchanged),
                                "comparedWith": "evidence/pro-legal-ai-v3-20261003/v2-app-copy-key-hashes.json",
                                "retiredV2Keys": [key for key in old if key not in keys]},
            "status": STATUS,
            "reviewer": AGENT,
            "method": METHOD,
            "backTranslation": "NOT_RUN for the changed and new keys",
            "nativeSpeakerReview": False,
            "counselReview": False,
            "flag": {"key": f"locales.{locale}", "recommended": False,
                     "condition": "stays false: candidate copy (owner selection global and off), unverified "
                                  "Google account facts and no review of the v3 strings by anyone but their "
                                  "author"},
        }
    summary = {
        "schemaVersion": 2,
        "lane": "LEGAL-AI",
        "date": "2026-10-03",
        "consentVersion": app["consentVersion"],
        "wireConsentVersion": app["wireConsentVersion"],
        "statuses": {locale: STATUS for locale in candidate.LOCALES},
        "changedOrNewKeys": receipts["ko"]["changedOrNewKeys"],
        "unchangedFromV2": {locale: receipts[locale]["unchangedFromV2"]["count"] for locale in candidate.LOCALES},
        "backTranslated": [],
        "nativeSpeakerReviewed": [],
        "counselReviewed": [],
        "flagsOff": list(candidate.LOCALES),
        "honesty": "ai-consent-v3 is a candidate written by one AI model. Nobody else has read the changed "
                   "strings in any locale. Recommendation flags are off for all 17 locales.",
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
    print(f"OK: {len(receipts)} locale receipts; changed or new keys: {len(summary['changedOrNewKeys'])}; "
          f"flags off: {len(summary['flagsOff'])}")


if __name__ == "__main__":
    main()
