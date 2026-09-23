"""Release-step constants shared by the page renderers and the site checker.

Owner decision 2026-09-22: align the effective date in both app catalogs BEFORE
final builds/signing. Upload those immutable artifacts to both stores, then publish
the site after both uploads are accepted. A policy date is not proof of app availability.
This supersedes the 2026-09-17 after-upload date order and avoids duplicate signing.

Owner instruction 2026-09-23 makes the website the full-policy source. App consent notices and
minimum instructions remain native, but full-policy app-catalog parity is retired. Setting an
ISO date (`YYYY-MM-DD`) must align these website fields:

- `docs/ios-content.json` `effectiveDate` and every locale's `privacy.effectiveDate`;
- `docs/android-content.candidate.json` `effectiveDate`;
- the sentence in both candidate policy sections that says the effective date is set when the
  version is released;
- `effectiveDateDecision` for both platforms in `legal-release-map.json`.

`python3 scripts/check_site.py --release` refuses to pass while the date is not filled.
"""

from __future__ import annotations

import datetime

# Owner-approved order: fix the policy date before final build and signing.
SECOND_RELEASE_EFFECTIVE_DATE: str | None = "2026-09-23"

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
        "sets it before final builds/signing (owner decision 2026-09-22)"
    )
    return expected_effective_date("0000-00-00")


# Food data bundled with the second release (owner decision NUTRITION-CATALOG-RELEASE-20260917):
# Integrated candidate food release (reviewed alias update; attribution text unchanged):
# 7df0320bb6f46a59392e5669621ce9da1d48122d84aac2790dd5bedb84ecdcb6, notices/NOTICE.txt. The
# attribution lines (and the MEXT change statement that MEXT requires for edited data) are legal
# notices, so both candidate policy sections carry them verbatim, in their source language, in
# every locale.
FOOD_DATA_RELEASE_ID = "7df0320bb6f46a59392e5669621ce9da1d48122d84aac2790dd5bedb84ecdcb6"
FOOD_DATA_ATTRIBUTIONS = (
    "U.S. Department of Agriculture, Agricultural Research Service. FoodData Central: "
    "Foundation Foods, April 2026 bulk release. https://fdc.nal.usda.gov/",
    "PHE (Public Health England) (2021). Composition of foods integrated dataset (CoFID). "
    "© Crown copyright 2021. Contains public sector information licensed under the Open "
    "Government Licence v3.0.",
    "出典：日本食品標準成分表（八訂）増補2023年（文部科学省）",
    "「日本食品標準成分表（八訂）増補2023年」（文部科学省）を基にDoseWeekが編集・加工"
    "（文部科学省が作成したものではありません）。",
    "출처: 식품의약품안전처, 전국통합식품영양성분정보(음식)표준데이터 (공공데이터포털 data.go.kr, "
    "데이터기준일자 2026-08-28). 일부 항목 원출처: 농촌진흥청 국가표준식품성분표.",
)


def missing_food_attributions(text: str) -> list[str]:
    return [line for line in FOOD_DATA_ATTRIBUTIONS if line not in text]
