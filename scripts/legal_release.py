"""Release-step constants shared by the page renderers and the site checker.

Owner decision 2026-09-22: align the effective date in both app catalogs BEFORE
final builds/signing. Upload those immutable artifacts to both stores, then publish
the site after both uploads are accepted. A policy date is not proof of app availability.
This supersedes the 2026-09-17 after-upload date order and avoids duplicate signing.

Owner instruction 2026-09-23 makes the website the full-policy source. App consent notices and
minimum instructions remain native, but full-policy app-catalog parity is retired.

Monetization release (owner instruction 2026-09-29, docs/MONETIZATION_POLICY.md in both app
repositories): the free download with ads and the Plus subscription add the "ads" and
"purchases" policy sections, new FAQ answers and the Terms of Use page (/terms/). Their
publication date is not decided, so NEXT_RELEASE_EFFECTIVE_DATE stays None: the policy pages keep
the live effective date (CURRENT_*), the Terms page shows no date, and
`python3 scripts/check_site.py --release` fails. Setting an ISO date (`YYYY-MM-DD`) must align:

- `docs/ios-content.json` `effectiveDate` and every locale's `privacy.effectiveDate`;
- `docs/android-content.candidate.json` `effectiveDate`;
- `docs/terms-content.json` `effectiveDate`;
- `effectiveDateDecision` for both platforms in `legal-release-map.json`.

`--release` then also refuses RELEASE_PLACEHOLDERS: the purchase-verification server's
location, operator and retention must be written into the sources first.
"""

from __future__ import annotations

import datetime

# The owner sets the monetization release date. None: not decided (BLOCKED for --release).
NEXT_RELEASE_EFFECTIVE_DATE: str | None = None

# Effective dates of the policies that are live now: main 8b53cf0, whose pages matched the live
# site on 2026-09-29 (the 1.0.5 policy date, formerly SECOND_RELEASE_EFFECTIVE_DATE).
CURRENT_IOS_EFFECTIVE_DATE = "2026-09-23"
CURRENT_ANDROID_EFFECTIVE_DATE = "2026-09-23"

# Candidate sentences that must be replaced with facts before release (en and ko sources; the
# translations of the same paths are replaced in the same step).
RELEASE_PLACEHOLDERS = (
    "The server location and operator details are listed here before this version is released.",
    "How long the server keeps these records is also listed here before this version is released.",
    "서버 위치와 운영자 정보는 이 버전을 출시하기 전에 여기에 공개해요.",
    "서버가 이 기록을 얼마나 보관하는지도 이 버전을 출시하기 전에 여기에 공개해요.",
)


def expected_effective_date(current: str) -> str:
    """The effective date a catalog must carry: the filled release date, else the live one."""
    if NEXT_RELEASE_EFFECTIVE_DATE is None:
        return current
    release_date = datetime.date.fromisoformat(NEXT_RELEASE_EFFECTIVE_DATE)
    assert release_date.isoformat() == NEXT_RELEASE_EFFECTIVE_DATE, (
        "NEXT_RELEASE_EFFECTIVE_DATE must be written as YYYY-MM-DD"
    )
    assert NEXT_RELEASE_EFFECTIVE_DATE > current, (
        "NEXT_RELEASE_EFFECTIVE_DATE must be later than the effective date it replaces"
    )
    return NEXT_RELEASE_EFFECTIVE_DATE


def require_release_date() -> str:
    assert NEXT_RELEASE_EFFECTIVE_DATE is not None, (
        "scripts/legal_release.py: NEXT_RELEASE_EFFECTIVE_DATE is not filled; the owner sets the "
        "monetization release date before final builds/signing (BLOCKED)"
    )
    return expected_effective_date("0000-00-00")


def release_placeholders(text: str) -> list[str]:
    """Candidate placeholder sentences still present in text."""
    return [sentence for sentence in RELEASE_PLACEHOLDERS if sentence in text]


# Food data bundled with the second release (owner decision NUTRITION-CATALOG-RELEASE-20260917):
# Integrated candidate food release (200 foods with 17-language names; attribution unchanged):
# 291c3210df94d6f9f6f470122b2ffefcfd40d04e23051948c9e4874d35b53697, notices/NOTICE.txt. The
# attribution lines (and the MEXT change statement that MEXT requires for edited data) are legal
# notices, so both candidate policy sections carry them verbatim, in their source language, in
# every locale.
FOOD_DATA_RELEASE_ID = "291c3210df94d6f9f6f470122b2ffefcfd40d04e23051948c9e4874d35b53697"
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
