"""Release-step constants shared by the page renderers and the site checker.

RELEASE STEP FILLS THIS (owner decision LEGAL-EFFECTIVE-DATE-20260917)
-----------------------------------------------------------------------
The second-release effective date is chosen after both builds (iOS 1.0.5 and Android 1.0.0,
versionCode 11) are uploaded for store review, and the candidate pages are merged to `main` and
published only after that. Until then `SECOND_RELEASE_EFFECTIVE_DATE` stays `None` and the
renderers keep requiring the effective dates that are live today.

When the release step sets it to an ISO date (`YYYY-MM-DD`), the same change must also set:

- `docs/ios-content.json` `effectiveDate`, and every locale's `privacy.effectiveDate`, which is
  mirrored verbatim from `privacy.effectiveDate` in the iOS app catalog (the app catalog must carry
  the same date, or `render_ios.py --check --catalog` fails);
- `docs/android-content.candidate.json` `effectiveDate`, with the same bytes adopted by
  `DoseweekPlayStore/docs/legal/android-content.json`;
- the sentence in both candidate policy sections that says the effective date is set when the
  version is released;
- `effectiveDateDecision` for both platforms in `legal-release-map.json`.

`python3 scripts/check_site.py --release` refuses to pass while the date is not filled.
"""

from __future__ import annotations

import datetime

# RELEASE STEP: replace None with the chosen second-release effective date, e.g. "2026-09-30".
SECOND_RELEASE_EFFECTIVE_DATE: str | None = None

# Effective dates of the policies that are live now (main 8a615a1).
CURRENT_IOS_EFFECTIVE_DATE = "2026-08-22"
CURRENT_ANDROID_EFFECTIVE_DATE = "2026-09-08"


def expected_effective_date(current: str) -> str:
    """The effective date a catalog must carry: the filled release date, else the live one."""
    if SECOND_RELEASE_EFFECTIVE_DATE is None:
        return current
    release_date = datetime.date.fromisoformat(SECOND_RELEASE_EFFECTIVE_DATE)
    assert release_date.isoformat() == SECOND_RELEASE_EFFECTIVE_DATE, (
        "SECOND_RELEASE_EFFECTIVE_DATE must be written as YYYY-MM-DD"
    )
    assert SECOND_RELEASE_EFFECTIVE_DATE > current, (
        "SECOND_RELEASE_EFFECTIVE_DATE must be later than the effective date it replaces"
    )
    return SECOND_RELEASE_EFFECTIVE_DATE


def require_release_date() -> str:
    assert SECOND_RELEASE_EFFECTIVE_DATE is not None, (
        "scripts/legal_release.py: SECOND_RELEASE_EFFECTIVE_DATE is not filled; the release step "
        "sets it after the store upload (LEGAL-EFFECTIVE-DATE-20260917) before publishing"
    )
    return expected_effective_date("0000-00-00")
