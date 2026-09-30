"""Pre-release account/sync disclosure source guard.

The candidate is deliberately separate from the generated live policy. Its contents describe
planned behavior, not a deployed service. The release check fails until the implementation,
operational facts and publication sources are reconciled and verified.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/account-sync-content.candidate.json"
LOCALES = (
    "ko", "en", "ja", "de", "fr", "es", "it", "nl", "pt-PT", "pl", "sv", "hi",
    "pt-BR", "ar", "zh-Hans", "zh-Hant", "tr",
)
FIELDS = ("account", "sync", "retention", "notice", "webDeletion")
KAKAO_NAME = {"ko": "카카오", "ja": "カカオ"}


def load() -> dict:
    candidate = json.loads(SOURCE.read_text(encoding="utf-8"))
    assert candidate["schemaVersion"] == 1
    assert candidate["localeOrder"] == list(LOCALES)
    assert list(candidate["locales"]) == list(LOCALES)
    assert candidate["plannedVersion"] == "1.0.6"
    assert candidate["plannedApiBase"] == "https://doseweek.wonyoungchoi.dev/v1"
    assert candidate["plannedAnnouncementFeed"] == (
        "https://doseweek.wonyoungchoi.dev/announcements/v1.json"
    )
    assert candidate["plannedDeletionPage"] == (
        "https://doseweek-legal.wonyoungchoi.dev/account/delete/"
    )
    assert candidate["unresolvedBeforePublication"]
    for locale, entry in candidate["locales"].items():
        assert set(entry) == set(FIELDS), f"{locale}: missing disclosure field"
        for field in FIELDS:
            assert isinstance(entry[field], str) and len(entry[field].strip()) > 40, (
                f"{locale}.{field}: missing substantial localized copy"
            )
        assert "Apple" in entry["account"] and "Google" in entry["account"], locale
        assert KAKAO_NAME.get(locale, "Kakao") in entry["account"], locale
        assert "Plus" in entry["account"] and "Plus" in entry["retention"], locale
        assert "30" in entry["retention"], f"{locale}: missing 30-day expiry"
    return candidate


def require_release_ready() -> None:
    candidate = load()
    assert candidate["status"] == "integrated-and-verified", (
        "account/sync disclosure is a pre-release candidate: reconcile 17-locale privacy, "
        "terms, help, deletion page and store declarations with verified native/server behavior"
    )
    assert not candidate["unresolvedBeforePublication"], (
        "account/sync release blockers remain in docs/account-sync-content.candidate.json"
    )


if __name__ == "__main__":
    candidate = load()
    print(f"OK: {len(candidate['locales'])} account/sync draft locales; status={candidate['status']}")
