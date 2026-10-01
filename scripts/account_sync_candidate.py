"""Pre-release account/sync disclosure source guard.

The candidate is deliberately separate from the generated live policy. Its contents describe
planned behavior, not a deployed service. The release check fails until the implementation,
operational facts and publication sources are reconciled and verified.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/account-sync-content.candidate.json"
# Owner decision 2026-10-01: DoseWeek sign-in uses Apple and Google only; Kakao login was
# dropped. The sign-in-bearing legal sources must not name it as a provider or data recipient.
# import/content.json is deliberately out of scope: record-import examples may name foods,
# and 카카오/カカオ also mean cacao.
SIGN_IN_PROVIDERS = ("Apple", "Google")
RETIRED_PROVIDER = re.compile(r"kakao|카카오|カカオ", re.IGNORECASE)
PROVIDER_SCOPED_SOURCES = (
    "docs/account-sync-content.candidate.json",
    "docs/ios-content.json",
    "docs/android-content.candidate.json",
    "docs/terms-content.json",
    "docs/home-content.json",
    "docs/help-navigation.json",
)
LOCALES = (
    "ko", "en", "ja", "de", "fr", "es", "it", "nl", "pt-PT", "pl", "sv", "hi",
    "pt-BR", "ar", "zh-Hans", "zh-Hant", "tr",
)
FIELDS = ("account", "sync", "retention", "notice", "webDeletion", "releaseStatus",
          "analytics", "legacyRights", "deletionTitle", "requestLabel", "manualBackupScope",
          "priorBuyerClaimPrivacy", "priorBuyerClaimHelp")


def retired_provider_mentions(value: object, where: str = "$") -> list[str]:
    """JSON paths whose key or string value names a retired sign-in provider."""
    if isinstance(value, str):
        return [where] if RETIRED_PROVIDER.search(value) else []
    if isinstance(value, dict):
        hits = []
        for key, item in value.items():
            path = f"{where}.{key}"
            if RETIRED_PROVIDER.search(str(key)):
                hits.append(path)
            hits.extend(retired_provider_mentions(item, path))
        return hits
    if isinstance(value, list):
        return [hit for index, item in enumerate(value)
                for hit in retired_provider_mentions(item, f"{where}[{index}]")]
    return []


def retired_provider_errors(root: Path = ROOT) -> list[str]:
    """Every retired-provider mention in the sign-in-bearing legal sources, as file:path."""
    errors = []
    for relative in PROVIDER_SCOPED_SOURCES:
        source = json.loads((root / relative).read_text(encoding="utf-8"))
        errors.extend(f"{relative}:{hit}" for hit in retired_provider_mentions(source))
    return errors


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
    deletion = candidate["deletionRequest"]
    assert deletion["method"] == "support-email"
    assert deletion["supportEmail"] == "wonyoung@wonyoungchoi.dev"
    assert deletion["requiresPlus"] is False and deletion["requiresReinstall"] is False
    assert deletion["published"] is False
    assert candidate["legacyDecision"]["ownerDecision"] == "resolved"
    assert candidate["legacyDecision"]["perpetualAdFreeGuaranteed"] is False
    assert candidate["legacyDecision"]["promoAcquisitionProvesPaidPurchase"] is False
    retired = retired_provider_mentions(candidate)
    assert not retired, (
        f"{SOURCE.name}: retired sign-in provider named at {retired[:3]}; "
        f"sign-in is {' and '.join(SIGN_IN_PROVIDERS)} only"
    )
    for locale, entry in candidate["locales"].items():
        assert set(entry) == set(FIELDS), f"{locale}: missing disclosure field"
        for field in FIELDS:
            minimum = 2 if field in ("deletionTitle", "requestLabel") else 20
            assert isinstance(entry[field], str) and len(entry[field].strip()) > minimum, (
                f"{locale}.{field}: missing substantial localized copy"
            )
        assert all(provider in entry["account"] for provider in SIGN_IN_PROVIDERS), locale
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
    retired = retired_provider_errors()
    assert not retired, (
        f"retired sign-in provider named in {len(retired)} legal source fields, e.g. {retired[:3]}; "
        f"sign-in is {' and '.join(SIGN_IN_PROVIDERS)} only"
    )
    candidate = load()
    print(f"OK: {len(candidate['locales'])} account/sync draft locales; status={candidate['status']}")
