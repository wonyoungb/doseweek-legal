#!/usr/bin/env python3
"""Semantic guards for the ai-consent-v3 legal copy (review round 2, finding F1).

The validators in ai_assistant_candidate.py used to check that tokens are present (Google, 24, 90,
the section titles). Copy that contradicts the facts still passed: an added "Google never stores
it", a dropped negation, a deleted notice item, a retired provider written in Hangul. This module
adds four guards, all driven by docs/ai-consent-v3-legal-pins.json:

1. requiredSentences: the exact sentence, per locale, for every legally relevant statement
   (no training, the 24-hour cache and the 90-day abuse log with staff review, what Google uses
   the content for, who does not save conversations, how long Google can read the content, the
   scope of the United States commitment, the systems of the United States and Singapore). Each
   must appear verbatim in the fields listed in APP_REQUIRED and WEB_REQUIRED.
2. pipaItemLabels: the six item labels of the transfer notice (PIPA 28-8(2)) per locale, in
   order, and a content rule for each item.
3. forbiddenClaims: per locale, phrases that state something the sources do not support
   (deleted at once, never stored, processed only in Seoul or Korea, not sent abroad, used for
   training), plus the retired provider names in non-Latin scripts for every locale.
4. combinationSha256 / templateFieldSha256: SHA-256 of the pinned fields per locale and switch
   combination, so any other change to a pinned field fails until someone re-pins.

Sections 1 to 3 are written by hand and are never regenerated. `--repin` rewrites only section 4;
it is a deliberate step after the changed text was read against the sources, not part of any
build. Guards 1 to 3 hold even after a re-pin: scripts/test_ai_assistant_legal.py replays the
reviewer's mutations with freshly computed hashes and each one still fails.

    python3 scripts/ai_legal_guard.py --check    # pins match the candidate files
    python3 scripts/ai_legal_guard.py --repin    # rewrite section 4 only
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINS = ROOT / "docs/ai-consent-v3-legal-pins.json"
CJK = ("ja", "zh-Hans", "zh-Hant")
SENTENCE_NAMES = ("doseweekServerKeepsNothing", "googleNoTraining", "googleCacheAndAbuse", "googleUse",
                  "doseweekNoConversations", "googleReadsWhileHeld", "usProcessing", "usCommitment",
                  "usSystem", "singapore")
PIPA_ITEMS = ("recipient", "country", "items", "timeAndMethod", "purposeAndRetention", "refusal")
RETENTION = ("doseweekServerKeepsNothing", "googleNoTraining", "googleCacheAndAbuse", "doseweekNoConversations")
GOOGLE_RETENTION = ("googleNoTraining", "googleCacheAndAbuse")
# name -> sentences required always, with location us, with location global.
APP_REQUIRED = {
    "ai.consent.a.retention.body": (RETENTION, (), ()),
    "ai.consent.a.e2ee.body": (("googleReadsWhileHeld",), (), ()),
    "ai.consent.a.where.body": ((), ("usProcessing",), ()),
    "ai.consent.a.transfer.body": (("googleUse", "googleCacheAndAbuse", "usSystem", "singapore"),
                                   ("usCommitment",), ()),
}
WEB_REQUIRED = {
    "clauses.3": (RETENTION, (), ()),
    "clauses.4": ((), ("usProcessing",), ()),
    "clauses.5": (("usSystem", "singapore"), ("usCommitment",), ()),
    "clauses.7": (("googleReadsWhileHeld",), (), ()),
    "e2eeException": (("googleReadsWhileHeld",), (), ()),
    "usHealth.categories": (("googleReadsWhileHeld",), (), ()),
    "processorRow.country": (("usSystem", "singapore"), ("usCommitment",), ()),
    "processorRow.purpose": (("googleCacheAndAbuse",), (), ()),
    "processorRow.retention": (GOOGLE_RETENTION, (), ()),
    "deletion": (GOOGLE_RETENTION, (), ()),
}
# Fields whose whole text is hashed (section 4).
APP_PINNED_PREFIXES = ("ai.consent.a.",)
APP_PINNED_KEYS = ("ai.consent.b.processing", "ai.help.inputNote")
WEB_PINNED_FIELDS = ("clauses", "e2eeException", "healthExclusion", "processorRow", "cloudflareTransit",
                     "usHealth", "deletion", "iosAiFaq", "androidAiFaq")


def separator(locale: str) -> str:
    return "" if locale in CJK else " "


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def digest(fields: dict) -> str:
    return sha256(json.dumps(fields, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def flatten(value: object, prefix: str = "") -> dict:
    """{"clauses.3": text, "processorRow.purpose": text, ...} for nested lists and dicts."""
    if isinstance(value, str):
        return {prefix: value}
    items = value.items() if isinstance(value, dict) else enumerate(value)
    found = {}
    for key, item in items:
        found.update(flatten(item, f"{prefix}.{key}" if prefix else str(key)))
    return found


def app_fields(copy: dict) -> dict:
    return {key: text for key, text in copy.items()
            if key.startswith(APP_PINNED_PREFIXES) or key in APP_PINNED_KEYS}


def web_fields(entry: dict) -> dict:
    return flatten({name: entry[name] for name in WEB_PINNED_FIELDS})


def read_pins() -> dict:
    return check_pin_file(json.loads(PINS.read_text(encoding="utf-8")))


def check_pin_file(pins: dict) -> dict:
    assert pins["schemaVersion"] == 1
    locales = list(pins["requiredSentences"])
    for locale in locales:
        sentences = pins["requiredSentences"][locale]
        assert tuple(sentences) == SENTENCE_NAMES, (locale, "required sentences")
        assert all(text == text.strip() and len(text) >= 8 for text in sentences.values()), locale
        assert len(set(sentences.values())) == len(sentences), (locale, "two statements share one sentence")
        labels = pins["pipaItemLabels"][locale]
        assert len(labels) == len(PIPA_ITEMS) and len(set(labels)) == len(labels), (locale, "labels")
        assert all(label.endswith((":", "：")) for label in labels), (locale, "labels")
        assert isinstance(pins["forbiddenClaims"][locale], list) and pins["forbiddenClaims"][locale], locale
        for pattern in pins["forbiddenClaims"][locale]:
            re.compile(pattern)
    assert list(pins["pipaItemLabels"]) == locales, "labels for every locale"
    assert list(pins["forbiddenClaims"]) == ["everyLocale", *locales], "forbidden claims for every locale"
    assert pins["forbiddenClaims"]["everyLocale"], "retired provider names in non-Latin scripts"
    return pins


def _forbidden(locale: str, texts: dict, pins: dict, where: object) -> None:
    claims = pins["forbiddenClaims"]
    for name, text in texts.items():
        found = [word for word in claims["everyLocale"] if word.casefold() in text.casefold()]
        found += [pattern for pattern in claims[locale] if re.search(pattern, text, re.IGNORECASE)]
        assert not found, f"{where}: {name} carries a forbidden claim or retired name: {found}"


def _required(locale: str, texts: dict, table: dict, location: str, pins: dict, where: object) -> None:
    sentences = pins["requiredSentences"][locale]
    for name, (always, us, global_) in table.items():
        for sentence in (*always, *(us if location == "us" else global_)):
            assert sentences[sentence] in texts[name], (
                f"{where}: {name} must carry the pinned sentence {sentence!r}: {sentences[sentence]}")


def _pinned(locale: str, kind: str, fields: dict, pins: dict, location: str, guardrail: str, where: object) -> None:
    expected = pins["combinationSha256"][f"{location}-{guardrail}"][locale][kind]
    assert digest(fields) == expected, (
        f"{where}: the {kind} legal text differs from docs/ai-consent-v3-legal-pins.json. Read the changed "
        f"text against the sources, then run python3 scripts/ai_legal_guard.py --repin")


def pipa_items(locale: str, transfer: str, pins: dict, where: object) -> dict:
    """The six items of the transfer notice, split at this locale's labels (PIPA 28-8(2))."""
    labels = pins["pipaItemLabels"][locale]
    positions = [transfer.find(label) for label in labels]
    missing = [PIPA_ITEMS[index] for index, position in enumerate(positions) if position < 0]
    assert not missing, f"{where}: the transfer notice lost the item(s) {missing}"
    assert positions == sorted(positions) and all(transfer.count(label) == 1 for label in labels), (
        f"{where}: the transfer notice items are out of order or repeated")
    ends = positions[1:] + [len(transfer)]
    return {name: transfer[position + len(label):end].strip()
            for name, label, position, end in zip(PIPA_ITEMS, labels, positions, ends)}


def check_app(locale: str, copy: dict, location: str, guardrail: str, facts: dict, pins: dict) -> None:
    """One locale's RESOLVED app copy. `facts` carries the tokens the items must contain."""
    where = (locale, location, guardrail, "app")
    fields = app_fields(copy)
    scan = dict(fields)
    if guardrail == "on":
        scan = {name: text.replace(facts["guardrailSentence"], "") for name, text in scan.items()}
    _forbidden(locale, scan, pins, where)
    _required(locale, copy, APP_REQUIRED, location, pins, where)
    sentences = pins["requiredSentences"][locale]
    items = pipa_items(locale, copy["ai.consent.a.transfer.body"], pins, where)
    short = [name for name, text in items.items() if len(text) < 10]
    assert not short, f"{where}: transfer notice item(s) without content: {short}"
    for token in facts["recipient"]:
        assert token in items["recipient"], f"{where}: recipient item lacks {token}"
    if location == "us":
        assert facts["country"] in items["country"] and sentences["usCommitment"] in items["country"], (
            f"{where}: country item")
    else:
        assert all(token in items["country"] for token in facts["global"]), f"{where}: country item"
    assert sentences["usSystem"] in items["country"] and sentences["singapore"] in items["country"], (
        f"{where}: the country item describes the United States and Singapore")
    assert facts["sentTitle"] in items["items"], f"{where}: items item points to the sent section"
    assert facts["send"] in items["timeAndMethod"] and "DoseWeek" in items["timeAndMethod"], (
        f"{where}: time and method item")
    purpose = sentences["googleUse"] + separator(locale) + sentences["googleCacheAndAbuse"]
    assert items["purposeAndRetention"] == purpose, (
        f"{where}: the purpose and retention item must be exactly the two pinned sentences")
    _pinned(locale, "app", fields, pins, location, guardrail, where)


def check_web(locale: str, entry: dict, location: str, guardrail: str, facts: dict, pins: dict) -> None:
    """One locale's RESOLVED website entry."""
    where = (locale, location, guardrail, "web")
    fields = web_fields(entry)
    scan = flatten({key: value for key, value in entry.items()})
    if guardrail == "on":
        scan = {name: text.replace(facts["guardrailSentence"], "") for name, text in scan.items()}
    _forbidden(locale, scan, pins, where)
    _required(locale, fields, WEB_REQUIRED, location, pins, where)
    sentences = pins["requiredSentences"][locale]
    block = sentences["googleNoTraining"] + separator(locale) + sentences["googleCacheAndAbuse"]
    assert fields["processorRow.retention"] == block, f"{where}: the retention cell is the two pinned sentences"
    _pinned(locale, "web", fields, pins, location, guardrail, where)


def build_hashes(web: dict, app: dict, resolve, locations, guardrails) -> tuple[dict, dict]:
    combinations = {}
    for location in locations:
        for guardrail in guardrails:
            resolved_web, resolved_app = resolve(web, location, guardrail), resolve(app, location, guardrail)
            combinations[f"{location}-{guardrail}"] = {
                locale: {"app": digest(app_fields(resolved_app["locales"][locale]["copy"])),
                         "web": digest(web_fields(resolved_web["locales"][locale]))}
                for locale in app["locales"]}
    template = {}
    for locale in app["locales"]:
        fields = {f"app:{name}": text for name, text in app_fields(app["locales"][locale]["copy"]).items()}
        fields.update({f"web:{name}": text for name, text in web_fields(web["locales"][locale]).items()})
        fields.update({f"switch:{name}": text
                       for name, text in flatten(app["locales"][locale]["switchText"]).items()})
        template[locale] = {name: sha256(text) for name, text in fields.items()}
    return combinations, template


def with_hashes(pins: dict, web: dict, app: dict) -> dict:
    """A copy of `pins` whose section 4 is computed from the given documents."""
    import ai_assistant_candidate as candidate
    combinations, template = build_hashes(web, app, candidate.resolve, candidate.LOCATIONS, candidate.GUARDRAILS)
    return {**pins, "consentVersion": app["consentVersion"], "combinationSha256": combinations,
            "templateFieldSha256": template}


def changed_fields(pins: dict, web: dict, app: dict) -> list[str]:
    current = with_hashes(pins, web, app)["templateFieldSha256"]
    return sorted(f"{locale}:{name}" for locale, fields in current.items()
                  for name in set(fields) | set(pins["templateFieldSha256"].get(locale, {}))
                  if fields.get(name) != pins["templateFieldSha256"].get(locale, {}).get(name))


def main() -> None:
    import ai_assistant_candidate as candidate
    web = json.loads(candidate.SOURCE.read_text(encoding="utf-8"))
    app = json.loads(candidate.APP_SOURCE.read_text(encoding="utf-8"))
    pins = json.loads(PINS.read_text(encoding="utf-8"))
    if "--repin" in sys.argv:
        changed = changed_fields(pins, web, app) if "templateFieldSha256" in pins else ["(first pin)"]
        pins = with_hashes(pins, web, app)
        PINS.write_text(json.dumps(pins, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"re-pinned {len(changed)} changed field(s)")
        for name in changed[:40]:
            print(" ", name)
    changed = changed_fields(read_pins(), web, app)
    assert not changed, f"pinned legal text changed without a re-pin: {changed[:12]}"
    candidate.validate_web(web)
    candidate.validate_app(app, web)
    print(f"OK: legal pins hold for {len(pins['requiredSentences'])} locales x "
          f"{len(pins['combinationSha256'])} switch combinations; {len(SENTENCE_NAMES)} pinned sentences, "
          f"{len(PIPA_ITEMS)} notice items, forbidden-claim lists for every locale")


if __name__ == "__main__":
    main()
