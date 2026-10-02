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
location, operator and retention must be written into the sources first. Both purchase sections
(iOS privacy section 12, Android privacy section 6) describe the same server, so they carry the
same placeholders and are replaced together (review finding 26, 2026-09-29: iOS section 12 had no
retention placeholder, so `--release` could pass without a retention period for the server's
Apple records). `purchase_placeholder_parity_errors` keeps them aligned.
"""

from __future__ import annotations

import datetime

# The owner sets the monetization release date. None: not decided (BLOCKED for --release).
NEXT_RELEASE_EFFECTIVE_DATE: str | None = None

# Effective dates of the policies that are live now: main 8b53cf0, whose pages matched the live
# site on 2026-09-29 (the 1.0.5 policy date, formerly SECOND_RELEASE_EFFECTIVE_DATE).
CURRENT_IOS_EFFECTIVE_DATE = "2026-09-23"
CURRENT_ANDROID_EFFECTIVE_DATE = "2026-09-23"

# Candidate sentences that must be replaced with facts before release: the en and ko sources and
# the translations of the same sentences (Android privacy section 6 and iOS privacy section 12 both
# carry both: the iOS app sends the server nothing, but Apple sends it subscription notices whose
# records it keeps). Replace every locale in the same step; `check_site.py` requires each locale to
# carry as many registered placeholders as en, and each locale's two purchase sections to carry the
# same ones, so an edited translation must be registered here again.
RELEASE_PLACEHOLDERS = (
    "The server location and operator details are listed here before this version is released.",
    "How long the server keeps these records is also listed here before this version is released.",
    "서버 위치와 운영자 정보는 이 버전을 출시하기 전에 여기에 공개해요.",
    "서버가 이 기록을 얼마나 보관하는지도 이 버전을 출시하기 전에 여기에 공개해요.",
    # translations (monetization candidate, 2026-09-29; no native-speaker review claimed)
    "サーバーの所在地と運営者の情報は、このバージョンの公開前にここに記載します。",
    "サーバーがこれらの記録を保管する期間も、このバージョンの公開前にここに記載します。",
    "Standort und Betreiber des Servers werden hier vor der Veröffentlichung dieser Version angegeben.",
    "Wie lange der Server diese Datensätze aufbewahrt, wird hier ebenfalls vor der "
    "Veröffentlichung dieser Version angegeben.",
    "L’emplacement du serveur et les coordonnées de son exploitant sont indiqués ici avant la "
    "sortie de cette version.",
    "La durée pendant laquelle le serveur conserve ces enregistrements est également indiquée ici "
    "avant la sortie de cette version.",
    "La ubicación del servidor y los datos de su operador se indican aquí antes de publicar esta versión.",
    "El tiempo durante el que el servidor conserva estos datos también se indica aquí antes de "
    "publicar esta versión.",
    "L’ubicazione del server e i dati del gestore vengono indicati qui prima del rilascio di "
    "questa versione.",
    "Anche per quanto tempo il server conserva questi dati viene indicato qui prima del rilascio "
    "di questa versione.",
    "De locatie van de server en de gegevens van de beheerder worden hier vermeld voordat deze "
    "versie wordt uitgebracht.",
    "Hoe lang de server deze gegevens bewaart, wordt hier eveneens vermeld voordat deze versie "
    "wordt uitgebracht.",
    "A localização do servidor e os dados do operador são indicados aqui antes do lançamento "
    "desta versão.",
    "O tempo durante o qual o servidor conserva estes registos também é indicado aqui antes do "
    "lançamento desta versão.",
    "Lokalizacja serwera i dane operatora zostaną podane tutaj przed wydaniem tej wersji.",
    "Przed wydaniem tej wersji zostanie tu też podane, jak długo serwer przechowuje te rekordy.",
    "Serverns plats och uppgifter om operatören anges här innan den här versionen släpps.",
    "Hur länge servern sparar dessa poster anges också här innan den här versionen släpps.",
    "सर्वर के स्थान और संचालक का विवरण इस संस्करण के रिलीज़ होने से पहले यहाँ दिया जाएगा।",
    "सर्वर ये रिकॉर्ड कितने समय तक रखता है, यह भी इस संस्करण के रिलीज़ होने से पहले यहाँ दिया जाएगा।",
    "A localização do servidor e os dados do operador serão informados aqui antes do lançamento "
    "desta versão.",
    "Por quanto tempo o servidor mantém esses registros também será informado aqui antes do "
    "lançamento desta versão.",
    "وستُدرج هنا تفاصيل موقع الخادم والجهة المشغّلة له قبل إطلاق هذا الإصدار.",
    "كما ستُدرج هنا مدة احتفاظ الخادم بهذه السجلات قبل إطلاق هذا الإصدار.",
    "服务器所在地和运营方信息将在此版本发布前在此列出。",
    "服务器保存这些记录的期限也将在此版本发布前在此列出。",
    "伺服器所在地與營運者資訊會在此版本發布前列於此處。",
    "伺服器保存這些紀錄的期限，也會在此版本發布前列於此處。",
    "Sunucunun konumu ve işletmeci bilgileri bu sürüm yayımlanmadan önce burada belirtilir.",
    "Sunucunun bu kayıtları ne kadar süre sakladığı da bu sürüm yayımlanmadan önce burada belirtilir.",
)


# Lane LEGAL-STORE round 2 (2026-10-02 reviews): facts the owner has not decided yet stay in the
# staged 1.0.6 sources as registered pending sentences, one per locale, instead of disappearing.
# check_site.py requires them in the staged sources while the candidate says the fact is open,
# and `check_site.py --release` refuses them in the effective sources, so applying the staged
# sources cannot hide an undecided fact. They are deliberately not RELEASE_PLACEHOLDERS: the
# staged sources must hold none of those.
# Where the standalone Android purchase-verification server (server/entitlement-verifier) runs.
PENDING_VERIFIER_LOCATION = {
    'ko': '별도의 Google Play 구매 확인 서버의 위치는 출시 전에 여기에 공개해요.',
    'en': 'The location of the separate Google Play purchase-verification server is stated here before release.',
    'ja': '別のGoogle Play購入確認サーバーの所在地は、公開前にここに記載します。',
    'de': 'Der Standort des separaten Google-Play-Kaufprüfungsservers wird hier vor der Veröffentlichung angegeben.',
    'fr': 'L’emplacement du serveur distinct de vérification des achats Google Play est indiqué ici avant la sortie.',
    'es': 'La ubicación del servidor independiente de verificación de compras de Google Play se indica aquí antes del lanzamiento.',
    'it': 'L’ubicazione del server separato di verifica degli acquisti Google Play viene indicata qui prima del rilascio.',
    'nl': 'De locatie van de afzonderlijke Google Play-server voor aankoopverificatie wordt hier vóór de release vermeld.',
    'pt-PT': 'A localização do servidor separado de verificação de compras do Google Play é indicada aqui antes do lançamento.',
    'pl': 'Lokalizacja osobnego serwera weryfikacji zakupów Google Play zostanie podana tutaj przed wydaniem.',
    'sv': 'Platsen för den separata servern för köpverifiering i Google Play anges här före lanseringen.',
    'hi': 'अलग Google Play खरीद-सत्यापन सर्वर का स्थान रिलीज़ से पहले यहाँ बताया जाएगा।',
    'pt-BR': 'A localização do servidor separado de verificação de compras do Google Play será informada aqui antes do lançamento.',
    'ar': 'وسيُذكر هنا موقع خادم التحقق من مشتريات Google Play المنفصل قبل الإصدار.',
    'zh-Hans': '独立的 Google Play 购买核验服务器所在地将在发布前在此列出。',
    'zh-Hant': '獨立的 Google Play 購買驗證伺服器所在地會在發布前列於此處。',
    'tr': 'Ayrı Google Play satın alma doğrulama sunucusunun konumu yayımdan önce burada belirtilir.',
}

# How long the keyed purchase tombstone kept after account deletion stays (store.js deleteAccount).
PENDING_TOMBSTONE_RETENTION = {
    'ko': '이 표식의 보관 기간은 출시 전에 여기에 공개해요.',
    'en': 'How long this marker is kept is stated here before release.',
    'ja': 'この標識の保管期間は公開前にここに記載します。',
    'de': 'Wie lange diese Markierung aufbewahrt wird, wird hier vor der Veröffentlichung angegeben.',
    'fr': 'La durée de conservation de ce marqueur est indiquée ici avant la sortie.',
    'es': 'El plazo de conservación de este marcador se indica aquí antes del lanzamiento.',
    'it': 'Il periodo di conservazione di questo marcatore viene indicato qui prima del rilascio.',
    'nl': 'Hoe lang deze markering wordt bewaard, wordt hier vóór de release vermeld.',
    'pt-PT': 'O prazo de conservação deste marcador é indicado aqui antes do lançamento.',
    'pl': 'Okres przechowywania tego znacznika zostanie podany tutaj przed wydaniem.',
    'sv': 'Hur länge markören sparas anges här före lanseringen.',
    'hi': 'यह चिह्न कितने समय तक रखा जाता है, यह रिलीज़ से पहले यहाँ बताया जाएगा।',
    'pt-BR': 'O prazo de retenção desse marcador será informado aqui antes do lançamento.',
    'ar': 'وستُذكر هنا مدة الاحتفاظ بهذه العلامة قبل الإصدار.',
    'zh-Hans': '该标记的保存期限将在发布前在此列出。',
    'zh-Hant': '此標記的保存期限會在發布前列於此處。',
    'tr': 'Bu işaretin ne kadar süre saklanacağı yayımdan önce burada belirtilir.',
}
# Round 3 (2026-10-02 review): the sync text's last sentence says the basis and duration of the
# keyed digest markers are settled before launch; it belongs to the same undecided tombstone fact
# (serverReadiness.tombstoneRetentionDecided), so it is registered and refused by --release too.
PENDING_DIGEST_BASIS = {
    'ko': '중복 구매 연결을 막기 위한 키 기반 다이제스트 표식의 보관 근거와 기간은 출시 전에 확정해요.',
    'en': 'The basis and duration for retaining keyed digest markers to prevent duplicate purchase linking must be settled before launch.',
    'ja': '購入の重複連携を防ぐダイジェスト標識の保持根拠と期間は公開前に確定します。',
    'de': 'Grundlage und Dauer der Aufbewahrung von Digest-Markierungen gegen doppelte Kaufverknüpfungen müssen vor der Veröffentlichung feststehen.',
    'fr': 'La base et la durée de conservation des marqueurs d’empreinte contre les liaisons d’achat en double restent à fixer avant publication.',
    'es': 'Antes del lanzamiento se definirán la base y el plazo de conservación de los marcadores que evitan vincular una compra varias veces.',
    'it': 'Base e durata di conservazione dei marcatori che impediscono associazioni duplicate degli acquisti saranno definite prima del lancio.',
    'nl': 'Grondslag en bewaartermijn van digestmarkeringen tegen dubbele aankoopkoppelingen worden voor publicatie vastgesteld.',
    'pt-PT': 'A base e o prazo de conservação dos marcadores que impedem ligações duplicadas de compras serão definidos antes do lançamento.',
    'pl': 'Podstawa i okres przechowywania znaczników skrótów zapobiegających powtórnemu powiązaniu zakupu zostaną ustalone przed publikacją.',
    'sv': 'Grund och lagringstid för avtrycksmarkörer som förhindrar dubbla köpkopplingar ska fastställas före lansering.',
    'hi': 'एक खरीद को दो बार जोड़ने से रोकने वाले डाइजेस्ट चिह्नों को रखने का आधार और अवधि लॉन्च से पहले तय होंगे।',
    'pt-BR': 'A base e o prazo de retenção dos marcadores que impedem vínculos duplicados de compras serão definidos antes do lançamento.',
    'ar': 'يُحدّد قبل الإطلاق أساس ومدة الاحتفاظ بعلامات الملخص لمنع ربط الشراء أكثر من مرة.',
    'zh-Hans': '防止重复关联购买的摘要标记，其保留依据和期限须在发布前确定。',
    'zh-Hant': '防止重複連結購買的摘要標記，其保留依據和期限須在發布前確定。',
    'tr': 'Yinelenen satın alma bağlantılarını önleyen özet işaretlerinin saklama dayanağı ve süresi yayımdan önce belirlenmelidir.',
}
PENDING_RELEASE_MARKERS = (*PENDING_VERIFIER_LOCATION.values(), *PENDING_TOMBSTONE_RETENTION.values(),
                           *PENDING_DIGEST_BASIS.values())


def pending_release_markers(text: str) -> list[str]:
    """Registered pending sentences still present in text."""
    return [sentence for sentence in PENDING_RELEASE_MARKERS if sentence in text]

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


def _strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in value.values() for text in _strings(item)]
    if isinstance(value, list):
        return [text for item in value for text in _strings(item)]
    return []


def placeholder_parity_errors(catalog: dict[str, object]) -> list[str]:
    """Locales whose registered placeholder count differs from en (translation drift or a
    locale left behind when en was replaced)."""
    locales = catalog["locales"]
    assert isinstance(locales, dict)
    expected = len(release_placeholders("\n".join(_strings(locales["en"]))))
    errors = []
    for locale, entry in locales.items():
        found = len(release_placeholders("\n".join(_strings(entry))))
        if found != expected:
            errors.append(f"{locale}: {found} registered release placeholders, en has {expected}")
    return errors


def purchase_placeholder_parity_errors(
    ios_catalog: dict[str, object], android_catalog: dict[str, object]
) -> list[str]:
    """Locales whose iOS and Android purchase sections carry different release placeholders.

    Both sections describe the one purchase-verification server, so its location, operator and
    retention stay pending, or are written, on both platforms together.
    """
    def placeholders(catalog: dict[str, object], locale: str) -> list[str]:
        locales = catalog["locales"]
        assert isinstance(locales, dict)
        sections = locales[locale]["privacy"]["sections"]
        purchases = next(section for section in sections if section["id"] == "purchases")
        return release_placeholders("\n".join(_strings(purchases["paragraphs"])))

    ios_locales = ios_catalog["locales"]
    assert isinstance(ios_locales, dict)
    errors = []
    for locale in ios_locales:
        ios, android = placeholders(ios_catalog, locale), placeholders(android_catalog, locale)
        if ios != android:
            errors.append(
                f"{locale}: iOS purchases carries {len(ios)} release placeholders, Android "
                f"purchases {len(android)} (missing on iOS: "
                f"{[sentence for sentence in android if sentence not in ios]})"
            )
    return errors


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
