#!/usr/bin/env python3
"""Build the published 1.0.6 legal pages from the base sources and the staged overlays.

Owner decisions 2026-10-03 (release ledger late-decisions.md, entries 17:35 and 19:00 KST):
effective date 2026-10-03; the Android app-managed Google Drive backup stays and is described;
operator Wonyoung Labs, servers on AWS Seoul; retention under Article 6 of the Enforcement Decree
of the Act on the Consumer Protection in Electronic Commerce; the Google Play account-deletion URL is the product site's /account-deletion/.

Inputs stay as they are: docs/*.json are the base sources and the candidates, and
`render_account_sync.integrated_sources` is the staged overlay (kept for its tests). This script
applies the decisions on top, in memory, and writes
- docs/published/*.json: the exact sources of the public pages, and manifest.json;
- the public pages (privacy, support, Android privacy/support/home, Terms, US health, home).
The AI record assistant (Pro) text is NOT part of this build: it is publish 2 (see
docs/publication-decisions-20261003.json, ai.reason).
`--check` rebuilds everything in memory and compares it with the files, so a public page can
only come from this build. Readiness flags in the candidates are NOT set to true here: the
manifest lists every flag that was still open when the owner ordered publication.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path

import account_sync_candidate
import ai_assistant_candidate
import legal_release
import locale_pages
import render_account_sync
import render_android
import render_home
import render_ios
import render_terms
import render_us_health

ROOT = Path(__file__).resolve().parents[1]
PUBLISHED = ROOT / "docs/published"
DECISIONS = json.loads((ROOT / "docs/publication-decisions-20261003.json").read_text(encoding="utf-8"))
EFFECTIVE_DATE = DECISIONS["effectiveDate"]
AI_SWITCHES = (DECISIONS["ai"]["location"], DECISIONS["ai"]["guardrail"])
AI_INCLUDED = DECISIONS["ai"]["included"]
assert AI_INCLUDED is True, "publish 2 carries the approved ai-consent-v3 text"
P2 = json.loads((ROOT / "docs/publication-decisions-20261003-p2.json").read_text(encoding="utf-8"))
# Sentences that carry the business registration number, the street address or the
# representative's name are not published (owner decision relayed 2026-10-03, publish 2).
PRIVATE_IDENTITY = re.compile(r"863-25-02023|Surim|수림로|46281")
REPRESENTATIVE = "Wonyoung Choi"
SENTENCES = re.compile(r"(?<=[.。।])\s+|(?<=。)")
DELETION_URL = DECISIONS["accountDeletionUrl"]
SOURCE_NAMES = ("ios-content.json", "android-content.candidate.json", "terms-content.json",
                "us-health-content.json")
# The localized effective-date line of the live policy names 2026-09-23; only the date changes.
DATE_SWAPS = {
    "ko": ("9월 23일", "10월 3일"), "en": ("September 23", "October 3"),
    "ja": ("9月23日", "10月3日"), "de": ("23. September", "3. Oktober"),
    "fr": ("23 septembre", "3 octobre"), "es": ("23 de septiembre", "3 de octubre"),
    "it": ("23 settembre", "3 ottobre"), "nl": ("23 september", "3 oktober"),
    "pt-PT": ("23 de setembro", "3 de outubro"), "pl": ("23 września", "3 października"),
    "sv": ("23 september", "3 oktober"), "hi": ("23 सितंबर", "3 अक्टूबर"),
    "pt-BR": ("23 de setembro", "3 de outubro"), "ar": ("23 سبتمبر", "3 أكتوبر"),
    "zh-Hans": ("9月23日", "10月3日"), "zh-Hant": ("9月23日", "10月3日"),
    "tr": ("23 Eylül", "3 Ekim"),
}


def sections(entry: dict) -> dict:
    return {section["id"]: section for section in entry["sections"]}


def status(locale: str, family: str) -> str:
    """The version scope sentence. iOS pages name no other platform, Android pages name no
    Apple device, the shared Terms and US policy name both."""
    return DECISIONS["text"]["releaseStatus"][locale].replace("{version}", version(locale, family))


def version(locale: str, family: str) -> str:
    """Android pages say 1.0.6; iOS pages promise no version number (App Store work is on
    hold): 'the next iOS update'; the shared Terms and US policy say both."""
    next_ios = P2["text"]["nextIos"][locale]
    return {"android": "1.0.6", "ios": next_ios, "shared": f"Android 1.0.6; {next_ios}"}[family]


def scrub_identity(sources: dict[str, dict]) -> list[dict]:
    """Drop the sentences with the registration number, address or representative; name the
    operator, the mail-order registration and the e-mail contact instead."""
    log: list[dict] = []

    def walk(value, locale, where, in_changes):
        if isinstance(value, dict):
            return {k: walk(v, locale, f"{where}/{k}", in_changes or value.get("id") in ("changes", "contact"))
                    for k, v in value.items()}
        if isinstance(value, list):
            return [walk(v, locale, f"{where}/{n}", in_changes) for n, v in enumerate(value)]
        if not isinstance(value, str) or not (PRIVATE_IDENTITY.search(value) or REPRESENTATIVE in value):
            return value
        kept, removed = [], []
        for paragraph in value.split("\n\n"):
            parts = [part for part in SENTENCES.split(paragraph) if part and part.strip()]
            out = []
            for part in parts:
                if PRIVATE_IDENTITY.search(part) or (REPRESENTATIVE in part and in_changes):
                    removed.append(part)
                else:
                    out.append(part.replace(REPRESENTATIVE, "Wonyoung Labs"))
            if out:
                kept.append(("" if locale in render_account_sync.CJK else " ").join(out))
        text = "\n\n".join(kept)
        if removed:
            identity = P2["text"]["identity"][locale]
            if identity not in text:
                text = (text + "\n\n" + identity) if text else identity
            log.append({"where": where, "removed": removed})
        return text

    for name, document in sources.items():
        for locale in list(document["locales"]):
            document["locales"][locale] = walk(document["locales"][locale], locale, f"{name}/{locale}", False)
    return log


def decided_candidate() -> dict:
    """The account/sync candidate with the owner's answers in place of its pending sentences."""
    candidate = copy.deepcopy(account_sync_candidate.load())
    text = DECISIONS["text"]
    for locale, entry in candidate["locales"].items():
        # The overlay runs with the Android wording; published_sources swaps the version for
        # the iOS pages and for the shared Terms and US policy.
        entry["releaseStatus"] = status(locale, "android")
        for field, pending, key in (
            ("retention", legal_release.PENDING_TOMBSTONE_RETENTION, "tombstone"),
            ("sync", legal_release.PENDING_DIGEST_BASIS, "digest"),
        ):
            assert entry[field].count(pending[locale]) == 1, (locale, field, "pending sentence")
            entry[field] = entry[field].replace(pending[locale], text[key][locale])
        log = text["noticeLog"][locale]
        assert entry["notice"].count(log["old"]) == 1, (locale, "notice log clause")
        entry["notice"] = entry["notice"].replace(log["old"], log["new"])
        entry["retention"] += ("" if locale in render_account_sync.CJK else " ") + P2["text"]["verifierNature"][locale]
        # 2026-10-03 publish 3: no backup job runs on the host, so the text says what is true
        # now and what applies once scheduled backups are enabled.
        entry["serverBackup"] = P2["text"]["serverBackup"][locale]
    # Owner 2026-10-03 19:00: the purchase-verification server is on AWS Seoul. The flag lives
    # only in this in-memory copy; the candidate file keeps its own state.
    candidate["serverReadiness"]["verifierHostDecided"] = True
    return candidate


SENTENCE_END = re.compile(r"(?<=[.。।؟!?])\s*(?=\S)")
# Draft-only remarks of the staged legal supplement ("blocks release", "this draft", "proof
# pending"). They described the release process, not the processing, and are removed from the
# published text. Statements that a provider detail is "not verified" stay: they are true.
REMOVED: list[dict] = []
IDENTITY_LOG: list[dict] = []


def _drop_tail(text: str, count: int, where: tuple) -> str:
    parts = [part for part in SENTENCE_END.split(text) if part.strip()]
    assert len(parts) > count, where
    kept = text[: text.rindex(parts[-count])].rstrip()
    REMOVED.append({"where": "/".join(where), "removed": text[len(kept):].strip()})
    return kept


def _cut(text: str, markers: tuple[str, ...], where: tuple, end: str = "") -> str:
    positions = [text.rfind(marker) for marker in markers if marker in text]
    assert positions, where
    kept = text[: max(positions)].rstrip() + end
    REMOVED.append({"where": "/".join(where), "removed": text[max(positions):].strip()})
    return kept


def strip_draft_remarks(sources: dict[str, dict]) -> None:
    ios, android, _terms, us_health = (sources[name] for name in SOURCE_NAMES)
    for platform, document in (("ios", ios), ("android", android)):
        for locale, entry in document["locales"].items():
            supplement = sections(entry["privacy"]["legalSupplement"])
            where = (platform, locale)
            rights = supplement["rights"]["paragraphs"]
            rights[3] = _drop_tail(rights[3], 2 if locale == "sv" else 1, (*where, "rights"))
            processing = supplement["processing"]["paragraphs"]
            processing[2] = _drop_tail(processing[2], 1, (*where, "processing"))
            table = supplement["processors"]["table"]
            table["caption"] = _cut(table["caption"], (" — ", "："), (*where, "caption"))
            rows = {row["id"]: row["cells"] for row in table["rows"]}
            rows["cloudflare"]["refusalEffect"] = _drop_tail(
                rows["cloudflare"]["refusalEffect"], 1, (*where, "cloudflare"))
            retention = rows["aws"]["retention"]
            if locale in ("ja", "sv"):
                retention = _drop_tail(retention, 1, (*where, "aws"))
            elif locale == "ko":
                tail = "제거해야 하고, 실제 증명은 아직 없어요."
                assert retention.endswith(tail), where
                REMOVED.append({"where": "/".join((*where, "aws")), "removed": tail})
                retention = retention[: -len(tail)] + "제거해요."
            else:
                end = "。" if locale.startswith("zh") else "।" if locale == "hi" else "."
                retention = _cut(retention, (";", "；", "؛"), (*where, "aws"), end)
            rows["aws"]["retention"] = retention
    for locale, entry in us_health["locales"].items():
        intro = entry["intro"]
        version = intro.rindex("1.0.6")
        start = max(intro.rfind(mark, 0, version) + len(mark)
                    for mark in (". ", "。", "। ") if mark in intro[:version])
        REMOVED.append({"where": f"us-health/{locale}/intro", "removed": intro[start:]})
        entry["intro"] = intro[:start].rstrip()


def published_sources() -> dict[str, dict]:
    candidate = decided_candidate()
    base_android = json.loads((ROOT / "docs/android-content.candidate.json").read_text(encoding="utf-8"))
    base_ios = json.loads((ROOT / "docs/ios-content.json").read_text(encoding="utf-8"))
    sources = render_account_sync.integrated_sources(candidate)
    ios, android, terms, us_health = (sources[name] for name in SOURCE_NAMES)
    # The iOS pages promise no version number: the label stays the live version.
    ios["bundleVersion"] = base_ios["bundleVersion"]
    # One status sentence per page family: the iOS pages name no other platform, the Android
    # pages name no Apple device, the shared Terms and US policy name both.
    for name, key in zip(SOURCE_NAMES, ("ios", "android", "shared", "shared")):
        flat = json.dumps(sources[name], ensure_ascii=False)
        for locale in candidate["localeOrder"]:
            staged = json.dumps(status(locale, "android"), ensure_ascii=False)[1:-1]
            assert staged in flat, (name, locale, "status sentence")
            flat = flat.replace(staged, json.dumps(status(locale, key), ensure_ascii=False)[1:-1])
        sources[name] = json.loads(flat)
    ios, android, terms, us_health = (sources[name] for name in SOURCE_NAMES)
    for document in sources.values():
        document["effectiveDate"] = EFFECTIVE_DATE
    REMOVED.clear()
    text = DECISIONS["text"]
    for locale in candidate["localeOrder"]:
        entry = candidate["locales"][locale]
        old, new = DATE_SWAPS[locale]
        line = base_ios["locales"][locale]["privacy"]["effectiveDate"]
        assert line.count(old) == 1, (locale, "effective date line")
        ios["locales"][locale]["privacy"]["effectiveDate"] = line.replace(old, new)
        # Android app-managed Google Drive backup (OQ-L2-1): it stays in 1.0.6, so its three
        # paragraphs of the live policy (what Drive holds and sees, encryption, deletion) come
        # back between the manual file backup and the Plus/OS paths.
        base = sections(base_android["locales"][locale]["privacy"])["backup"]["paragraphs"]
        assert len(base) == 7, (locale, "Android backup paragraphs changed")
        backup = sections(android["locales"][locale]["privacy"])["backup"]
        staged = backup["paragraphs"]
        assert len(staged) == 7, (locale, "staged Android backup paragraphs changed")
        backup["paragraphs"] = staged[:4] + base[4:7] + staged[4:]
        faq = {item["id"]: item for item in android["locales"][locale]["support"]["faq"]}
        faq["backup"]["answers"].append(base[4])
        # "The current version is 1.0.6" is not true until 1.0.6 is in the store: the scope
        # sentences keep the live version; the status sentence above them covers 1.0.6.
        # Release day: set "androidInStore": true in docs/publication-decisions-20261003-p2.json
        # and rerun this script; the overlay's "current version, 1.0.6" lines then stay.
        base_entry = base_android["locales"][locale]
        scope = android["locales"][locale]["privacy"]["scope"]
        assert scope.endswith(base_entry["privacy"]["scope"].replace("1.0.5", "1.0.6")), locale
        if P2["androidInStore"] is not True:
            android["locales"][locale]["privacy"]["scope"] = (
                status(locale, "android") + "\n\n" + base_entry["privacy"]["scope"])
            android["locales"][locale]["home"]["versionScope"] = base_entry["home"]["versionScope"]
        # AI record assistant (approved ai-consent-v3, Global / guardrail off). It arrives with
        # Android 1.0.6 and the next iOS update, so every place that describes it opens with
        # the scope sentence: not released yet, nothing is sent to Google until then.
        p2 = P2["text"]
        scope_of = lambda family: p2["aiScope"][locale].replace("{version}", version(locale, family))
        for document, family in ((ios, "ios"), (android, "android")):
            supplement = sections(document["locales"][locale]["privacy"]["legalSupplement"])
            ai = supplement[ai_assistant_candidate.SECTION_ID]["paragraphs"]
            ai[0] = scope_of(family) + "\n\n" + ai[0]
            vertex = {row["id"]: row["cells"] for row in supplement["processors"]["table"]["rows"]}[
                ai_assistant_candidate.PROCESSOR_ROW_ID]
            vertex["timingMethod"] = scope_of(family) + " " + vertex["timingMethod"]
            supplement["rights"]["paragraphs"][0] += "\n\n" + p2["children"][locale]
        faq["ai-health"]["answers"][0] = scope_of("android") + "\n\n" + faq["ai-health"]["answers"][0]
        ios_ai = ios["locales"][locale]["support"]["released"]["ai"]["answers"]
        ios_ai[0] = ios_ai[0] + "\n\n" + scope_of("ios")
        badges = android["locales"][locale]["home"]["featureBadges"]
        badges[ai_assistant_candidate.ANDROID_BADGE_INDEX] = (
            "DoseWeek 1.0.6: " + badges[ai_assistant_candidate.ANDROID_BADGE_INDEX])
        terms_sections = sections(terms["locales"][locale])
        terms_ai = terms_sections[ai_assistant_candidate.SECTION_ID]["paragraphs"]
        terms_ai[0] = scope_of("shared") + "\n\n" + terms_ai[0]
        terms_sections["contact"]["paragraphs"][-1] += "\n\n" + p2["noOrders"][locale] + "\n\n" + p2["identity"][locale]
        # Destruction procedure and method (PIPA Art. 30(1)3-2), from the server code and config.
        sections(android["locales"][locale]["privacy"])["retention"]["paragraphs"][-1] += "\n\n" + p2["destruction"][locale]
        sections(ios["locales"][locale]["privacy"])["deletion"]["paragraphs"][-1] += "\n\n" + p2["destruction"][locale]
        # Processor table: provider facts from each provider's published documents.
        for document in (ios, android):
            table = sections(document["locales"][locale]["privacy"]["legalSupplement"])["processors"]["table"]
            rows = {row["id"]: row["cells"] for row in table["rows"]}
            # The table no longer marks unverified particulars: drop the sentence that says so.
            processors = sections(document["locales"][locale]["privacy"]["legalSupplement"])["processors"]
            parts = [part for part in SENTENCES.split(processors["paragraphs"][0]) if part]
            if len(parts) in (4, 5) and not processors.get("_trimmed"):
                REMOVED.append({"where": f"{document['platform']}/{locale}/processors-intro", "removed": parts[1]})
                processors["paragraphs"][0] = ("" if locale in render_account_sync.CJK else " ").join(
                    parts[:1] + parts[2:])
            rows["aws"]["timingMethod"] = P2["text"]["awsTiming"][locale]
            for row_id, cells in P2["processorCells"].items():
                for cell_id, by_locale in cells.items():
                    assert cell_id in rows[row_id], (row_id, cell_id)
                    rows[row_id][cell_id] = by_locale[locale]
        purchases = sections(android["locales"][locale]["privacy"])["purchases"]["paragraphs"]
        purchases[2] += "\n\n" + text["verifier"][locale]
    strip_draft_remarks(sources)
    IDENTITY_LOG.clear()
    IDENTITY_LOG.extend(scrub_identity(sources))
    for name, document in sources.items():
        flat = json.dumps(document, ensure_ascii=False)
        left = legal_release.release_placeholders(flat) + legal_release.pending_release_markers(flat)
        assert not left, f"{name}: pending sentence left in the published source: {left[0]!r}"
        assert "{version}" not in flat, f"{name}: unresolved version token"
        assert not PRIVATE_IDENTITY.search(flat) and REPRESENTATIVE not in flat, f"{name}: identity left"
        assert "1.0.7" not in flat, f"{name}: an iOS version number is promised"
    return sources


def published_pages(sources: dict[str, dict]) -> dict[Path, str]:
    ios, android, terms, us_health = (sources[name] for name in SOURCE_NAMES)
    candidate = account_sync_candidate.load()
    pages = {render_ios.PAGE_PATH: render_ios.rendered(ios),
             render_ios.SUPPORT_PATH: render_ios.rendered_support(ios),
             **render_ios.rendered_locale_pages(ios)}
    pages.update(render_android.rendered_pages(android))
    pages.update(render_android.rendered_locale_pages(android))
    pages.update(render_terms.rendered_pages(terms, ios))
    pages.update(render_us_health.rendered_pages(us_health, ios))
    linked = {"privacy/index.html", "support/index.html", "terms/index.html", "us-health/index.html"}
    for path, markup in list(pages.items()):
        relative = path.relative_to(ROOT)
        if not relative.as_posix().endswith(tuple(linked)):
            continue
        locale = relative.parts[0] if relative.parts[0] in candidate["localeOrder"] else None

        def link(loc: str) -> str:
            title = render_account_sync.html.escape(candidate["locales"][loc]["deletionTitle"])
            return f'<a class="page-link" href="{DELETION_URL}#{loc}">{title}</a>'
        if locale:
            assert markup.count("</article>") == 1, relative
            markup = markup.replace("</article>", link(locale) + "</article>")
        else:
            for loc in candidate["localeOrder"]:
                pattern = rf'(<article id="{loc}".*?)(</article>)'
                markup, count = re.subn(pattern, lambda m: m[1] + link(loc) + m[2], markup,
                                        count=1, flags=re.S)
                assert count == 1, (relative, loc)
        pages[path] = markup
    # The home pages read the Android home copy and the iOS medical notice from the sources.
    original = render_home.sources
    home_content = json.loads((ROOT / "docs/home-content.json").read_text(encoding="utf-8"))
    render_home.sources = lambda: (home_content, ios, android)
    try:
        pages[ROOT / "index.html"] = render_home.rendered()
        pages.update(render_home.rendered_locale_pages())
    finally:
        render_home.sources = original
    for path, markup in pages.items():
        assert markup.lstrip().startswith("<!doctype html>"), path
        assert "noindex" not in markup, path
    return pages


def manifest(sources: dict[str, dict], pages: dict[Path, str]) -> dict:
    digest = lambda text: hashlib.sha256(text.encode("utf-8")).hexdigest()
    account = account_sync_candidate.load()
    inputs = ["docs/ios-content.json", "docs/android-content.candidate.json", "docs/terms-content.json",
              "docs/us-health-content.json", "docs/home-content.json",
              "docs/account-sync-content.candidate.json", "docs/ai-assistant-content.candidate.json",
              "docs/publication-decisions-20261003-p2.json",
              "docs/publication-decisions-20261003.json"]
    return {
        "status": "published by owner decision",
        "effectiveDate": EFFECTIVE_DATE,
        "decisions": DECISIONS["source"],
        "ai": {"included": True, "location": AI_SWITCHES[0], "guardrail": AI_SWITCHES[1],
               "lane": DECISIONS["ai"]["lane"],
               "selectedInLaneFile": ai_assistant_candidate.selection(ai_assistant_candidate.load())},
        "accountDeletionUrl": DELETION_URL,
        "inputs": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in inputs},
        "sources": {name: digest(serialized(source)) for name, source in sources.items()},
        "pages": len(pages),
        "notVerifiedAtPublication": {
            "accountServerReadiness": sorted(k for k, v in account["serverReadiness"].items() if v is not True),
            "accountUnresolved": len(account["unresolvedBeforePublication"]),
            "aiReadiness": sorted(k for k, v in ai_assistant_candidate.load()["readiness"].items() if v is not True),
            "aiUnresolved": len(ai_assistant_candidate.load()["unresolvedBeforePublication"]),
            "note": "The candidates' open flags and lists are unchanged. The owner ordered publication "
                    "on 2026-10-03 with these items open; they remain release conditions of the apps "
                    "and the server, not facts this build verified.",
        },
    }


def serialized(document: object) -> str:
    return json.dumps(document, ensure_ascii=False, indent=2) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    sources = published_sources()
    pages = published_pages(sources)
    files = {PUBLISHED / name: serialized(source) for name, source in sources.items()}
    files[PUBLISHED / "manifest.json"] = serialized(manifest(sources, pages))
    files[PUBLISHED / "removed-draft-remarks.json"] = serialized(REMOVED)
    files[PUBLISHED / "removed-identity-sentences.json"] = serialized(IDENTITY_LOG)
    locale_pages.write_pages({**files, **pages}, arguments.check, "rerun publish_release.py")
    print(f"{'OK' if arguments.check else 'Published'}: {len(pages)} public pages and "
          f"{len(files)} files in docs/published; effective date {EFFECTIVE_DATE}; "
          f"AI text included ({AI_SWITCHES[0]}, guardrail {AI_SWITCHES[1]})")


if __name__ == "__main__":
    main()
