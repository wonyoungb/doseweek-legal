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
FIELDS = ("account", "sync", "healthSync", "processors", "retention", "notice", "webDeletion", "releaseStatus",
          "analytics", "legacyRights", "deletionTitle", "requestLabel", "manualBackupScope",
          "priorBuyerClaimPrivacy", "priorBuyerClaimHelp")


# Lane LEGAL-STORE (2026-10-02): the account/sync server facts every locale must state before the
# candidate can describe a working service. Operator: the person the current policy already names.
# Region: the deploy receipt's Lightsail address lies in AWS's published ap-northeast-2 (Seoul)
# range. Cloudflare proxies every request (owner decision, deploy receipt owner_decisions[1]) and
# is a processor with a PIPA Art. 28-8 overseas transfer, so the recipient's contact and network
# pages are cited verbatim. Retention (owner decision D8) is 30 days after the last
# server-verified Store end; a Store outage defers deletion by at most 7 days; the approved
# Lightsail daily snapshots keep 7, so deleted data leaves backups within 7 days.
HOSTING_FIELD = "processors"
HOSTING_TOKENS = ("Wonyoung Choi", "Amazon Web Services", "Lightsail", "ap-northeast-2", "Cloudflare")
CLOUDFLARE_TRANSFER_LINKS = (
    "https://www.cloudflare.com/privacypolicy/",
    "https://www.cloudflare.com/network/",
)
RETENTION_NUMBERS = ("30", "7")
# D1: the full record graph crosses both platforms. The sync text reaches the Android pages,
# whose catalog guard (render_android.validate_catalog) refuses the token "iOS", so the scope is
# checked by the record kinds and the "both platforms" wording in the two reviewed languages.
SYNC_SCOPE = {
    "en": ("injection plans", "dose records", "meals", "body measurements", "supplies",
           "import history", "settings", "both platforms"),
    "ko": ("주사 계획", "투여 기록", "식사", "신체 측정값", "재고", "가져오기 기록", "설정", "두 플랫폼"),
}


# Lane LEGAL-STORE round 2 (reviews of 2026-10-02). Every request to the DoseWeek host passes
# through Cloudflare, including the public announcement check that every user's app makes when it
# opens, signed in or not (Android AnnouncementTransport.FEED_URL, iOS RemoteAnnouncementHTTPClient;
# the deploy receipt's doseweek vhost accepts only Cloudflare ranges). So the PIPA Art. 28-8
# particulars must name that occasion, the refusal method and its effect must be true (not signing
# in does not stop it), and the notice must name Cloudflare. A Google ID token can carry email and
# profile claims (Android GetSignInWithGoogleOption); the server keeps only issuer and subject.
ANNOUNCEMENT_HOST = "doseweek.wonyoungchoi.dev"
ANNOUNCEMENT_TERMS = {
    'ko': '공지',
    'en': 'announcement',
    'ja': 'お知らせ',
    'de': 'Mitteilungen',
    'fr': 'annonces',
    'es': 'avisos',
    'it': 'avvisi',
    'nl': 'mededelingen',
    'pt-PT': 'avisos',
    'pl': 'komunikat',
    'sv': 'meddelanden',
    'hi': 'सूचना',
    'pt-BR': 'avisos',
    'ar': 'الإعلان العام',
    'zh-Hans': '公告',
    'zh-Hant': '公告',
    'tr': 'duyuru',
}
GOOGLE_TOKEN_TERMS = {
    'ko': '이메일 주소',
    'en': 'email address',
    'ja': 'メールアドレス',
    'de': 'E-Mail-Adresse',
    'fr': 'adresse e-mail',
    'es': 'correo electrónico',
    'it': 'indirizzo e-mail',
    'nl': 'e-mailadres',
    'pt-PT': 'endereço de e-mail',
    'pl': 'adres e-mail',
    'sv': 'e-postadress',
    'hi': 'ईमेल पता',
    'pt-BR': 'endereço de e-mail',
    'ar': 'بريدك الإلكتروني',
    'zh-Hans': '电子邮件地址',
    'zh-Hant': '電子郵件地址',
    'tr': 'e-posta adresinizi',
}
# The refusal sentence that was false: not signing in does not stop the announcement check.
RETIRED_TRANSFER_REFUSALS = {
    'ko': '이전을 원하지 않으면 DoseWeek 계정에 로그인하지 마세요.',
    'en': 'If you do not want this transfer, do not sign in to a DoseWeek account.',
    'ja': '移転を望まない場合は、DoseWeekアカウントにログインしないでください。',
    'de': 'Wenn Sie diese Übermittlung nicht wünschen, melden Sie sich nicht bei einem DoseWeek-Konto an.',
    'fr': 'Si vous ne souhaitez pas ce transfert, ne vous connectez pas à un compte DoseWeek.',
    'es': 'Si no desea esta transferencia, no inicie sesión en una cuenta DoseWeek.',
    'it': 'Se non vuoi questo trasferimento, non accedere a un account DoseWeek.',
    'nl': 'Wilt u deze doorgifte niet, meld u dan niet aan bij een DoseWeek-account.',
    'pt-PT': 'Se não quiser esta transferência, não inicie sessão numa conta DoseWeek.',
    'pl': 'Jeśli nie chcesz tego przekazania, nie loguj się do konta DoseWeek.',
    'sv': 'Om du inte vill ha överföringen loggar du inte in på ett DoseWeek-konto.',
    'hi': 'यदि आप यह स्थानांतरण नहीं चाहते, तो DoseWeek खाते में साइन इन न करें।',
    'pt-BR': 'Se não quiser essa transferência, não entre em uma conta DoseWeek.',
    'ar': 'إذا كنت لا تريد هذا النقل، فلا تسجّل الدخول إلى حساب DoseWeek.',
    'zh-Hans': '如不希望进行此转移，请不要登录 DoseWeek 账户。',
    'zh-Hant': '如不希望進行此移轉，請勿登入 DoseWeek 帳戶。',
    'tr': 'Bu aktarımı istemiyorsanız bir DoseWeek hesabında oturum açmayın.',
}
# Every envelope uploads the data key wrapped under the recovery-derived key (PROTOCOL.md), so
# "the key stays on your devices" was imprecise: the recovery code stays there.
RETIRED_KEY_SENTENCES = {
    'ko': '키는 복구 코드로 보호돼 사용자의 기기에만 있어서, 운영자도 건강 기록을 읽을 수 없어요.',
    'en': 'The key stays on your devices, protected by your recovery code, so the operator cannot read your health records.',
    'ja': '鍵は復旧コードで保護されて利用者の端末にだけあるため、運営者も健康記録を読めません。',
    'de': 'Der Schlüssel bleibt, geschützt durch Ihren Wiederherstellungscode, auf Ihren Geräten, sodass auch der Betreiber Ihre Gesundheitsdaten nicht lesen kann.',
    'fr': 'La clé reste sur vos appareils, protégée par votre code de récupération : l’exploitant ne peut donc pas lire vos données de santé.',
    'es': 'La clave permanece en sus dispositivos, protegida por su código de recuperación, por lo que el responsable no puede leer sus registros de salud.',
    'it': 'La chiave resta sui tuoi dispositivi, protetta dal codice di recupero, quindi neanche il gestore può leggere i tuoi dati sanitari.',
    'nl': 'De sleutel blijft op uw apparaten, beschermd door uw herstelcode, zodat ook de beheerder uw gezondheidsgegevens niet kan lezen.',
    'pt-PT': 'A chave fica nos seus dispositivos, protegida pelo código de recuperação, pelo que o responsável não consegue ler os seus registos de saúde.',
    'pl': 'Klucz pozostaje na Twoich urządzeniach, chroniony kodem odzyskiwania, więc administrator nie może odczytać Twoich danych zdrowotnych.',
    'sv': 'Nyckeln stannar på dina enheter, skyddad av återställningskoden, så inte heller den som driver tjänsten kan läsa dina hälsouppgifter.',
    'hi': 'कुंजी आपके रिकवरी कोड से सुरक्षित होकर केवल आपके डिवाइस पर रहती है, इसलिए संचालक भी आपके स्वास्थ्य रिकॉर्ड नहीं पढ़ सकता।',
    'pt-BR': 'A chave fica nos seus aparelhos, protegida pelo código de recuperação, por isso o operador não consegue ler seus registros de saúde.',
    'ar': 'يبقى المفتاح على أجهزتك محميًا برمز الاسترداد، لذلك لا يستطيع المشغّل قراءة سجلاتك الصحية.',
    'zh-Hans': '密钥受恢复码保护，只保存在您的设备上，因此运营者也无法读取您的健康记录。',
    'zh-Hant': '金鑰受復原碼保護，只保存在您的裝置上，因此營運者也無法讀取您的健康紀錄。',
    'tr': 'Anahtar, kurtarma kodunuzla korunarak yalnızca cihazlarınızda kalır; bu nedenle işletmeci de sağlık kayıtlarınızı okuyamaz.',
}
# Imported Apple Health / Health Connect observations are in the sync graph (PROTOCOL.md "Snapshot
# contents"), so the Health Connect "not sent to the developer" sentence is replaced by healthSync.
HEALTH_CONNECT_DENIALS = {
    'ko': '읽은 정보는 앱 전용 저장소에 보관하고 개발자에게 보내지 않아요.',
    'en': 'What it reads is kept in app-private storage and is not sent to the developer.',
    'ja': '読み取った情報はアプリ専用領域に保存され、開発者へは送信されません。',
    'de': 'Gelesene Werte bleiben im privaten App-Speicher und werden nicht an den Entwickler gesendet.',
    'fr': 'Ce qu’il lit reste dans le stockage privé de l’application et n’est pas envoyé au développeur.',
    'es': 'Lo que lee se guarda en el almacenamiento privado de la aplicación y no se envía al desarrollador.',
    'it': 'Ciò che legge resta nell’archiviazione privata dell’app e non viene inviato allo sviluppatore.',
    'nl': 'Wat wordt gelezen, blijft in de privéopslag van de app en wordt niet naar de ontwikkelaar gestuurd.',
    'pt-PT': 'O que lê fica no armazenamento privado da aplicação e não é enviado ao programador.',
    'pl': 'Odczytane dane pozostają w prywatnej pamięci aplikacji i nie są wysyłane do dewelopera.',
    'sv': 'Det som läses stannar i appens privata lagringsutrymme och skickas inte till utvecklaren.',
    'hi': 'पढ़ी गई जानकारी ऐप-निजी स्टोरेज में रहती है और डेवलपर को नहीं भेजी जाती।',
    'pt-BR': 'O que é lido fica no armazenamento privado do aplicativo e não é enviado ao desenvolvedor.',
    'ar': 'وتُحفظ البيانات المقروءة في التخزين الخاص بالتطبيق ولا تُرسل إلى المطوّر.',
    'zh-Hans': '读取到的信息保存在应用专属存储空间，不会发送给开发者。',
    'zh-Hant': '讀取到的資訊保存在應用程式專用儲存空間，不會傳送給開發者。',
    'tr': 'Okuduğu veriler uygulamaya özel depolamada kalır ve geliştiriciye gönderilmez.',
}
# Turkish: the app UI and the base candidate say "eşitleme" for sync.
TURKISH_RETIRED_SYNC_TERM = "eşzamanla"
# ko/ja/zh: the country qualifies the Seoul region, not the AWS legal entity.
COUNTRY_BEFORE_AWS = re.compile(r"(?:대한민국|大韓民国|大韩民国|大韓民國)\s*の?\s*Amazon Web Services")
# Facts the drafted text states that the server and apps do not ship yet. Each stays False until
# the named path lands, every False one keeps its own unresolved item (matched by its token), and
# require_release_ready() refuses any False one.
SERVER_READINESS_TOKENS = {
    "retentionRecheckWired": "recheckPlus",
    "syncResetRoute": "DELETE /v1/sync/snapshot",
    "syncResetUiIos": "iOS reset-sync control",
    "syncResetUiAndroid": "Android reset-sync control",
    "verifierHostDecided": "server/entitlement-verifier",
    "tombstoneRetentionDecided": "tombstone retention",
    "announcementTransferReviewed": "announcement check",
    "cloudflareContactVerified": "Cloudflare privacy contact",
}


def transfer_disclosure_errors(candidate: dict | None = None) -> list[str]:
    """Locales whose transfer, notice, key, health-sync or retention text is still false or
    incomplete after the round-2 reviews, plus readiness flags without their unresolved item."""
    import legal_release  # local import: legal_release has no dependency on this module
    if candidate is None:
        candidate = json.loads(SOURCE.read_text(encoding="utf-8"))
    errors = []
    for locale in LOCALES:
        entry = candidate["locales"].get(locale, {})
        processors = entry.get(HOSTING_FIELD, "")
        for token, why in ((ANNOUNCEMENT_HOST, "the host every request goes to"),
                           (ANNOUNCEMENT_TERMS[locale], "the announcement check as a transfer occasion"),
                           (GOOGLE_TOKEN_TERMS[locale], "the email claim in a Google sign-in token")):
            if token not in processors:
                errors.append(f"{locale}.{HOSTING_FIELD}: missing {token!r} ({why})")
        if RETIRED_TRANSFER_REFUSALS[locale] in processors:
            errors.append(f"{locale}.{HOSTING_FIELD}: false refusal (not signing in does not stop the announcement check)")
        if COUNTRY_BEFORE_AWS.search(processors):
            errors.append(f"{locale}.{HOSTING_FIELD}: the country qualifies AWS instead of the Seoul region")
        if "Cloudflare" not in entry.get("notice", ""):
            errors.append(f"{locale}.notice: does not say the announcement request passes through Cloudflare")
        if RETIRED_KEY_SENTENCES[locale] in entry.get("sync", ""):
            errors.append(f"{locale}.sync: says the key stays on the devices (the recovery code does)")
        if not entry.get("healthSync", "").strip():
            errors.append(f"{locale}.healthSync: missing (imported health measurements are in the sync graph)")
        retention = entry.get("retention", "")
        if legal_release.PENDING_TOMBSTONE_RETENTION[locale] not in retention:
            errors.append(f"{locale}.retention: does not list the keyed purchase tombstone kept after deletion")
        if not re.search(r"(?<!\d)90(?!\d)", retention):
            errors.append(f"{locale}.retention: does not list the verifier's 90-day purchase records")
    turkish = json.dumps(candidate["locales"].get("tr", {}), ensure_ascii=False)
    if TURKISH_RETIRED_SYNC_TERM in turkish:
        errors.append("tr: uses 'eşzamanlama' for sync; the app and the base candidate say 'eşitleme'")
    readiness = candidate.get("serverReadiness")
    if not isinstance(readiness, dict) or set(readiness) != set(SERVER_READINESS_TOKENS):
        errors.append(f"serverReadiness: must list exactly {sorted(SERVER_READINESS_TOKENS)}")
    else:
        unresolved = "\n".join(candidate.get("unresolvedBeforePublication", []))
        for key, token in SERVER_READINESS_TOKENS.items():
            if readiness[key] is not True and token not in unresolved:
                errors.append(f"serverReadiness.{key} is open but no unresolved item names {token!r}")
    return errors


def staged_disclosure_errors(sources: dict, candidate: dict | None = None) -> list[str]:
    """Staged 1.0.6 sources that keep the Health Connect denial, lack the health-sync sentence
    on either platform, or drop the pending verifier location from the Android purchase section."""
    import legal_release
    if candidate is None:
        candidate = json.loads(SOURCE.read_text(encoding="utf-8"))
    errors = []
    for locale in LOCALES:
        health_sync = candidate["locales"][locale].get("healthSync", "")
        ios = sections_by_id(sources["ios-content.json"]["locales"][locale]["privacy"])
        android = sections_by_id(sources["android-content.candidate.json"]["locales"][locale]["privacy"])
        ios_health = "\n\n".join(ios["health"]["paragraphs"])
        health_connect = android["no-collection"]["paragraphs"][2]
        if not health_sync or health_sync not in ios_health:
            errors.append(f"ios-content.json:{locale}: Apple Health section lacks the health-sync sentence")
        if not health_sync or health_sync not in health_connect:
            errors.append(f"android-content.candidate.json:{locale}: Health Connect paragraph lacks the health-sync sentence")
        if HEALTH_CONNECT_DENIALS[locale] in health_connect:
            errors.append(f"android-content.candidate.json:{locale}: Health Connect paragraph still says nothing is sent")
        purchases = "\n\n".join(android["purchases"]["paragraphs"])
        if (candidate.get("serverReadiness") or {}).get("verifierHostDecided") is not True and \
                legal_release.PENDING_VERIFIER_LOCATION[locale] not in purchases:
            errors.append(f"android-content.candidate.json:{locale}: purchases lost the pending verifier location")
    return errors


def sections_by_id(privacy: dict) -> dict:
    return {section["id"]: section for section in privacy["sections"]}


def hosting_retention_errors(candidate: dict | None = None) -> list[str]:
    """Locales whose candidate omits the operator/region/Cloudflare transfer, the D8 and backup
    numbers or the cross-platform sync scope. Reads the raw source unless a candidate is given,
    so the check does not depend on load() accepting it."""
    if candidate is None:
        candidate = json.loads(SOURCE.read_text(encoding="utf-8"))
    errors = []
    for locale in LOCALES:
        entry = candidate["locales"].get(locale, {})
        hosting = entry.get(HOSTING_FIELD, "")
        errors.extend(f"{locale}.{HOSTING_FIELD}: missing {token!r}"
                      for token in (*HOSTING_TOKENS, *CLOUDFLARE_TRANSFER_LINKS) if token not in hosting)
        retention = entry.get("retention", "")
        errors.extend(f"{locale}.retention: missing the {number}-day figure"
                      for number in RETENTION_NUMBERS if not re.search(rf"(?<!\d){number}(?!\d)", retention))
        sync = entry.get("sync", "")
        errors.extend(f"{locale}.sync: missing {term!r} (full cross-platform scope)"
                      for term in SYNC_SCOPE.get(locale, ()) if term not in sync)
    return errors


def staged_placeholder_errors(sources: dict) -> list[str]:
    """Release placeholder sentences (server location/operator/retention still 'listed before
    release') left in the staged 1.0.6 privacy sources built by render_account_sync."""
    import legal_release  # local import: legal_release has no dependency on this module
    errors = []
    for name, source in sources.items():
        for locale, entry in source["locales"].items():
            left = legal_release.release_placeholders(json.dumps(entry, ensure_ascii=False))
            errors.extend(f"{name}:{locale}: {sentence!r}" for sentence in left)
    return errors


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
    hosting = hosting_retention_errors(candidate)
    assert not hosting, f"{SOURCE.name}: missing account/sync server facts, e.g. {hosting[:3]}"
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


def require_release_ready(candidate: dict | None = None) -> None:
    candidate = candidate if candidate is not None else load()
    assert candidate["status"] == "integrated-and-verified", (
        "account/sync disclosure is a pre-release candidate: reconcile 17-locale privacy, "
        "terms, help, deletion page and store declarations with verified native/server behavior"
    )
    assert not candidate["unresolvedBeforePublication"], (
        "account/sync release blockers remain in docs/account-sync-content.candidate.json"
    )
    # Lane LEGAL-STORE round 2: the drafted D8, reset-sync, verifier and tombstone text describes
    # paths that are not shipped or decided; emptying the unresolved list alone does not release it.
    readiness = candidate.get("serverReadiness") or {}
    open_flags = [key for key in SERVER_READINESS_TOKENS if readiness.get(key) is not True]
    assert not open_flags, (
        f"account/sync serverReadiness flags still open: {open_flags}; ship or decide each path first"
    )


if __name__ == "__main__":
    retired = retired_provider_errors()
    assert not retired, (
        f"retired sign-in provider named in {len(retired)} legal source fields, e.g. {retired[:3]}; "
        f"sign-in is {' and '.join(SIGN_IN_PROVIDERS)} only"
    )
    hosting = hosting_retention_errors()
    assert not hosting, (
        f"account/sync candidate misses server facts in {len(hosting)} places, e.g. {hosting[:3]}; "
        "state the operator, AWS Lightsail ap-northeast-2, the Cloudflare transfer and the 30/7-day rules"
    )
    candidate = load()
    print(f"OK: {len(candidate['locales'])} account/sync draft locales; status={candidate['status']}")
