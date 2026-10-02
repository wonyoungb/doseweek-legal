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
FIELDS = ("account", "sync", "healthSync", "healthConsent", "serverBackup", "recordsSync", "mealsSync", "processors", "retention", "notice",
          "webDeletion", "releaseStatus",
          "analytics", "legacyRights", "deletionTitle", "requestLabel", "manualBackupScope",
          "priorBuyerClaimPrivacy", "priorBuyerClaimHelp")


# Lane LEGAL-STORE (2026-10-02): the account/sync server facts every locale must state before the
# candidate can describe a working service. Operator: the person the current policy already names.
# Region: the deploy receipt's Lightsail address lies in AWS's published ap-northeast-2 (Seoul)
# range. Cloudflare proxies every request (owner decision, deploy receipt owner_decisions[1]) and
# is a processor with a PIPA Art. 28-8 overseas transfer, so the recipient's contact and network
# pages are cited verbatim. Retention (owner decision D8) is 30 days after the last
# server-verified Store end; a Store outage defers deletion by at most 7 days; server backups are
# kept for at most 7 days (round 3: mechanism-neutral, since owner decision
# round3_20261002.backup_hybrid replaces the daily-snapshot plan; serverReadiness.backupWindowVerified).
HOSTING_FIELD = "processors"
HOSTING_TOKENS = ("Wonyoung Labs", "Wonyoung Choi", "Amazon Web Services", "Lightsail", "ap-northeast-2", "Cloudflare")
CLOUDFLARE_TRANSFER_LINKS = (
    "https://www.cloudflare.com/privacypolicy/",
    "https://www.cloudflare.com/network/",
)
RETENTION_NUMBERS = ("30", "7")
# D1: the full record graph crosses both platforms. The sync text reaches the Android pages,
# whose catalog guard (render_android.validate_catalog) refuses the token "iOS", so the scope is
# checked by the record kinds, settings and the "both platforms" wording. Round 2 (2026-10-02
# review): every locale, not only en and ko. Lane commit debbd1c had narrowed the first RED
# (702c296), which required "iOS"/"Android" in every locale, to en/ko record kinds.
SYNC_SCOPE = {
    "en": ("injection plans", "dose records", "meals", "body measurements", "supplies",
           "import history", "settings", "both platforms"),
    "ko": ("주사 계획", "투여 기록", "식사", "신체 측정값", "재고", "가져오기 기록", "설정", "두 플랫폼"),
    "ja": ("注射計画", "投与記録", "食事", "身体の測定値", "在庫", "取り込み履歴", "設定", "両プラットフォーム"),
    "de": ("Injektionspläne", "Dosisaufzeichnungen", "Mahlzeiten", "Körpermesswerte", "Vorräte",
           "Importverlauf", "Einstellungen", "beide Plattformen"),
    "fr": ("plans d’injection", "prises", "repas", "mesures corporelles", "stocks",
           "historique d’importation", "réglages", "deux plateformes"),
    "es": ("planes de inyección", "registros de dosis", "comidas", "medidas corporales", "existencias",
           "historial de importación", "ajustes", "ambas plataformas"),
    "it": ("piani di iniezione", "somministrazioni", "pasti", "misure corporee", "scorte",
           "cronologia delle importazioni", "impostazioni", "due piattaforme"),
    "nl": ("injectieplannen", "dosisregistraties", "maaltijden", "lichaamsmetingen", "voorraad",
           "importgeschiedenis", "instellingen", "beide platforms"),
    "pt-PT": ("planos de injeção", "registos de doses", "refeições", "medidas corporais", "stock",
              "histórico de importação", "definições", "duas plataformas"),
    "pl": ("plany wstrzyknięć", "zapisy dawek", "posiłki", "pomiary ciała", "zapasy",
           "historię importu", "ustawieniami", "obiema platformami"),
    "sv": ("injektionsplaner", "dosregistreringar", "måltider", "kroppsmått", "förråd",
           "importhistorik", "inställningar", "båda plattformarna"),
    "hi": ("इंजेक्शन योजनाएँ", "खुराक रिकॉर्ड", "भोजन", "शरीर माप", "स्टॉक", "आयात इतिहास", "सेटिंग",
           "दोनों प्लेटफ़ॉर्म"),
    "pt-BR": ("planos de injeção", "registros de doses", "refeições", "medidas corporais", "estoque",
              "histórico de importação", "configurações", "duas plataformas"),
    "ar": ("خطط الحقن", "سجلات الجرعات", "الوجبات", "قياسات الجسم", "المخزون", "سجل الاستيراد",
           "الإعدادات", "المنصّتين"),
    "zh-Hans": ("注射计划", "用药记录", "饮食", "身体测量", "库存", "导入历史", "设置", "两个平台"),
    "zh-Hant": ("注射計畫", "用藥紀錄", "飲食", "身體測量", "庫存", "匯入歷程", "設定", "兩個平台"),
    "tr": ("enjeksiyon planları", "doz kayıtları", "öğünler", "vücut ölçümleri", "stok",
           "içe aktarma geçmişi", "ayarlarla", "iki platform"),
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
    # Round 3 (2026-10-02 reviews of e3da3bd): the backup window under the hybrid backup decision
    # (owner-decisions round3_20261002.backup_hybrid) and the origin access-log disclosure.
    "backupWindowVerified": "backup window",
    "accessLogDisclosed": "HOST-07",
    "processorInventoryVerified": "processorInventoryVerified",
    "healthConsentVerified": "healthConsentVerified",
    "internationalRepresentativesVerified": "internationalRepresentativesVerified",
    "breachProcedureOperational": "breachProcedureOperational",
    "regionalSubscriptionNoticesVerified": "regionalSubscriptionNoticesVerified",
    "consumerHealthRightsVerified": "consumerHealthRightsVerified",
}

# Lane LEGAL-STORE round 3 (2026-10-02 reviews of e3da3bd).
# The round-2 healthSync sentence said imported Health Connect / Apple Health data leaves the
# device only if account sync is on. Both apps' encrypted backups carry it too (Android
# DoseWeekRepository backup snapshot incl. external_body_measurement, manual SAF file and Drive
# backup; iOS backup payload with origin .healthKit), so the exclusive form is retired.
RETIRED_HEALTH_SYNC = {
    'ko': '읽은 정보는 앱 전용 저장소에 보관하고, 계정 동기화를 켤 때만 기기 밖으로 나가요. 이때도 출처와 숨김 선택과 함께 개발자가 읽을 수 없는 종단간 암호화 사본에만 담겨요.',
    'en': 'What it reads is kept in app-private storage and leaves the device only if you turn on account sync: it is then included, with its source and your hide choices, in the end-to-end encrypted copy, which the developer cannot read.',
    'ja': '読み取った情報はアプリ専用領域に保存され、アカウント同期をオンにした場合にだけ端末の外に出ます。その場合も、取得元と非表示の選択とともに、開発者が読めないエンドツーエンド暗号化されたコピーにだけ含まれます。',
    'de': 'Gelesene Werte bleiben im privaten App-Speicher und verlassen das Gerät nur, wenn Sie die Kontosynchronisierung einschalten; dann sind sie mit ihrer Quelle und Ihren Ausblende-Einstellungen nur in der Ende-zu-Ende-verschlüsselten Kopie enthalten, die der Entwickler nicht lesen kann.',
    'fr': 'Ce qu’il lit reste dans le stockage privé de l’application et ne quitte l’appareil que si vous activez la synchronisation du compte : ces données sont alors incluses, avec leur source et vos choix de masquage, dans la copie chiffrée de bout en bout, que le développeur ne peut pas lire.',
    'es': 'Lo que lee se guarda en el almacenamiento privado de la aplicación y solo sale del dispositivo si activa la sincronización de la cuenta: entonces se incluye, con su origen y sus opciones de ocultación, en la copia cifrada de extremo a extremo, que el desarrollador no puede leer.',
    'it': 'Ciò che legge resta nell’archiviazione privata dell’app ed esce dal dispositivo solo se attivi la sincronizzazione dell’account: in quel caso è incluso, con la sua origine e le tue scelte di occultamento, nella copia crittografata end-to-end, che lo sviluppatore non può leggere.',
    'nl': 'Wat wordt gelezen, blijft in de privéopslag van de app en verlaat het apparaat alleen als u accountsynchronisatie inschakelt: het zit dan, met de bron en uw verbergkeuzes, in de end-to-end versleutelde kopie, die de ontwikkelaar niet kan lezen.',
    'pt-PT': 'O que lê fica no armazenamento privado da aplicação e só sai do dispositivo se ativar a sincronização da conta: nesse caso é incluído, com a origem e as suas escolhas de ocultação, na cópia encriptada ponto a ponto, que o programador não consegue ler.',
    'pl': 'Odczytane dane pozostają w prywatnej pamięci aplikacji i opuszczają urządzenie tylko wtedy, gdy włączysz synchronizację konta: trafiają wtedy, wraz ze źródłem i Twoimi wyborami ukrycia, do kopii zaszyfrowanej end-to-end, której deweloper nie może odczytać.',
    'sv': 'Det som läses stannar i appens privata lagringsutrymme och lämnar enheten bara om du slår på kontosynkronisering: då ingår det, med sin källa och dina val att dölja, i den end-to-end-krypterade kopian, som utvecklaren inte kan läsa.',
    'hi': 'पढ़ी गई जानकारी ऐप-निजी स्टोरेज में रहती है और केवल तब डिवाइस से बाहर जाती है जब आप खाता सिंक चालू करते हैं: तब वह अपने स्रोत और आपके छिपाने के विकल्पों के साथ एंड-टू-एंड एन्क्रिप्टेड प्रति में शामिल होती है, जिसे डेवलपर पढ़ नहीं सकता।',
    'pt-BR': 'O que é lido fica no armazenamento privado do aplicativo e só sai do aparelho se você ativar a sincronização da conta: nesse caso, é incluído, com a origem e suas escolhas de ocultação, na cópia criptografada de ponta a ponta, que o desenvolvedor não consegue ler.',
    'ar': 'تُحفظ البيانات المقروءة في التخزين الخاص بالتطبيق ولا تغادر الجهاز إلا إذا فعّلت مزامنة الحساب، وعندها تُضمَّن مع مصدرها وخيارات الإخفاء التي اخترتها في النسخة المشفّرة تشفيرًا شاملًا التي لا يستطيع المطوّر قراءتها.',
    'zh-Hans': '读取到的信息保存在应用专属存储空间，只有在您开启账户同步时才会离开设备：此时它会连同来源和您的隐藏选择一起，仅包含在开发者无法读取的端到端加密副本中。',
    'zh-Hant': '讀取到的資訊保存在應用程式專用儲存空間，只有在您開啟帳戶同步時才會離開裝置：此時它會連同來源與您的隱藏選擇一起，僅包含在開發者無法讀取的端對端加密副本中。',
    'tr': 'Okuduğu veriler uygulamaya özel depolamada kalır ve yalnızca hesap eşitlemesini açarsanız cihazdan çıkar: o zaman kaynağı ve gizleme seçimlerinizle birlikte, geliştiricinin okuyamadığı uçtan uca şifreli kopyaya dahil edilir.',
}
# The exclusive "skipped only when offline" clause that 212c91b removed from the refusal; a revert
# must fail (it was present at d89d227).
RETIRED_OFFLINE_CLAUSES = {
    'ko': '기기가 인터넷에 연결되지 않았을 때만 건너뛰어요.',
    'en': 'it is skipped only when the device has no internet connection.',
    'ja': '端末がインターネットに接続していないときだけ行われません。',
    'de': 'sie entfällt nur, wenn das Gerät keine Internetverbindung hat.',
    'fr': 'elle n’est omise que lorsque l’appareil n’a pas de connexion Internet.',
    'es': 'solo se omite cuando el dispositivo no tiene conexión a internet.',
    'it': 'viene saltato solo quando il dispositivo non ha una connessione a Internet.',
    'nl': 'ze wordt alleen overgeslagen als het apparaat geen internetverbinding heeft.',
    'pt-PT': 'só é omitida quando o dispositivo não tem ligação à Internet.',
    'pl': 'jest pomijane tylko wtedy, gdy urządzenie nie ma połączenia z internetem.',
    'sv': 'den hoppas bara över när enheten saknar internetanslutning.',
    'hi': 'यह केवल तब नहीं होती जब डिवाइस इंटरनेट से जुड़ा न हो।',
    'pt-BR': 'ela só é pulada quando o aparelho está sem conexão com a internet.',
    'ar': 'ولا يُتخطّى إلا عندما لا يكون الجهاز متصلًا بالإنترنت.',
    'zh-Hans': '只有在设备未连接互联网时才会跳过。',
    'zh-Hant': '只有在裝置未連上網際網路時才會略過。',
    'tr': 'yalnızca cihazın internet bağlantısı olmadığında atlanır.',
}
# Owner decision round3_20261002.backup_hybrid (daily S3 app-data backups with a 7-day lifecycle
# plus a reduced Lightsail snapshot cadence; exact settings pending) replaces the "automatic daily
# snapshots kept for 7 days" mechanism, so the text states only the window and
# serverReadiness.backupWindowVerified gates it.
RETIRED_BACKUP_MECHANISM = {
    'ko': '서버는 매일 자동 스냅샷으로 백업하고 스냅샷은 7일 동안 보관해요.',
    'en': 'The server is backed up by automatic daily snapshots kept for 7 days',
    'ja': 'サーバーは毎日自動スナップショットでバックアップし、スナップショットは7日間保管します。',
    'de': 'Der Server wird durch tägliche automatische Snapshots gesichert, die 7 Tage aufbewahrt werden',
    'fr': 'Le serveur est sauvegardé par des instantanés automatiques quotidiens conservés 7 jours',
    'es': 'El servidor se respalda con instantáneas automáticas diarias que se conservan 7 días',
    'it': 'Il server viene salvato con snapshot automatici giornalieri conservati per 7 giorni',
    'nl': 'De server wordt geback-upt met dagelijkse automatische momentopnamen die 7 dagen worden bewaard',
    'pt-PT': 'O servidor é salvaguardado por instantâneos automáticos diários mantidos durante 7 dias',
    'pl': 'Serwer jest zabezpieczany codziennymi automatycznymi migawkami przechowywanymi przez 7 dni',
    'sv': 'Servern säkerhetskopieras med dagliga automatiska ögonblicksbilder som sparas i 7 dagar',
    'hi': 'सर्वर का बैकअप रोज़ाना स्वचालित स्नैपशॉट से होता है, जो 7 दिन रखे जाते हैं',
    'pt-BR': 'O servidor tem backup por instantâneos automáticos diários guardados por 7 dias',
    'ar': 'يُنسخ الخادم احتياطيًا بلقطات تلقائية يومية تُحفظ 7 أيام',
    'zh-Hans': '服务器每天通过自动快照备份，快照保留 7 天',
    'zh-Hant': '伺服器每天以自動快照備份，快照保留 7 天',
    'tr': 'Sunucu, 7 gün saklanan günlük otomatik anlık görüntülerle yedeklenir',
}
BACKUP_WINDOW_SENTENCES = {
    'ko': '서버 백업은 최대 7일까지 보관해요.',
    'en': 'Server backups are kept for at most 7 days',
    'ja': 'サーバーのバックアップは最長7日間保管します。',
    'de': 'Serversicherungen werden höchstens 7 Tage aufbewahrt',
    'fr': 'Les sauvegardes du serveur sont conservées 7 jours au maximum',
    'es': 'Las copias de seguridad del servidor se conservan como máximo 7 días',
    'it': 'I backup del server sono conservati per non più di 7 giorni',
    'nl': 'Back-ups van de server worden hoogstens 7 dagen bewaard',
    'pt-PT': 'As cópias de segurança do servidor são mantidas durante 7 dias no máximo',
    'pl': 'Kopie zapasowe serwera są przechowywane najwyżej przez 7 dni',
    'sv': 'Serverns säkerhetskopior sparas i högst 7 dagar',
    'hi': 'सर्वर के बैकअप अधिकतम 7 दिन रखे जाते हैं',
    'pt-BR': 'Os backups do servidor são guardados por no máximo 7 dias',
    'ar': 'تُحفظ النسخ الاحتياطية للخادم 7 أيام كحدّ أقصى',
    'zh-Hans': '服务器备份最多保留 7 天',
    'zh-Hant': '伺服器備份最多保留 7 天',
    'tr': 'Sunucu yedekleri en fazla 7 gün saklanır',
}
# Unqualified denials the staged 1.0.6 sources keep from the live 1.0.5 text (iOS support answer
# "Where are my records", iOS and Android meals paragraphs). With account sync these records reach
# the server end-to-end encrypted, so the staged text uses the candidate's recordsSync/mealsSync.
RECORD_DENIALS = {
    'ko': '개발자는 이 기록을 받지 않아요.',
    'en': 'The developer does not receive these records.',
    'ja': '開発者はこれらの記録を受け取りません。',
    'de': 'Der Entwickler erhält diese Einträge nicht.',
    'fr': 'Le développeur ne reçoit pas ces données.',
    'es': 'El desarrollador no recibe estos registros.',
    'it': 'Lo sviluppatore non riceve questi dati.',
    'nl': 'De ontwikkelaar ontvangt deze gegevens niet.',
    'pt-PT': 'O programador não recebe estes registos.',
    'pl': 'Deweloper nie otrzymuje tych danych.',
    'sv': 'Utvecklaren får inte dessa uppgifter.',
    'hi': 'डेवलपर को ये रिकॉर्ड नहीं मिलते।',
    'pt-BR': 'O desenvolvedor não recebe esses registros.',
    'ar': 'لا يتلقى المطوّر هذه السجلات.',
    'zh-Hans': '开发者不会收到这些记录。',
    'zh-Hant': '開發者不會收到這些紀錄。',
    'tr': 'Geliştirici bu kayıtları almaz.',
}
MEAL_DENIALS = {
    'ko': '개발자는 식사 정보를 받지 않아요.',
    'en': 'The developer receives no meal information.',
    'ja': '開発者は食事の情報を受け取りません。',
    'de': 'Der Entwickler erhält keine Angaben zu Mahlzeiten.',
    'fr': 'Le développeur ne reçoit aucune information sur les repas.',
    'es': 'El desarrollador no recibe información de comidas.',
    'it': 'Lo sviluppatore non riceve informazioni sui pasti.',
    'nl': 'De ontwikkelaar ontvangt geen maaltijdgegevens.',
    'pt-PT': 'O programador não recebe informação sobre refeições.',
    'pl': 'Deweloper nie otrzymuje informacji o posiłkach.',
    'sv': 'Utvecklaren får inga måltidsuppgifter.',
    'hi': 'डेवलपर को भोजन की कोई जानकारी नहीं मिलती।',
    'pt-BR': 'O desenvolvedor não recebe informações de refeições.',
    'ar': 'ولا يتلقى المطوّر أي معلومات عن الوجبات.',
    'zh-Hans': '开发者不会收到任何用餐信息。',
    'zh-Hant': '開發者不會取得任何用餐資訊。',
    'tr': 'Geliştirici öğün bilgisi almaz.',
}
# ja/zh sentences are joined without an ASCII space after "。" (render_account_sync joins
# healthSync the same way).
CJK_LOCALES = ("ja", "zh-Hans", "zh-Hant")


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
        if RETIRED_HEALTH_SYNC[locale] in entry.get("healthSync", ""):
            errors.append(f"{locale}.healthSync: says imported health data leaves the device only through "
                          "account sync (the encrypted backups carry it too)")
        if RETIRED_OFFLINE_CLAUSES[locale] in processors:
            errors.append(f"{locale}.{HOSTING_FIELD}: exclusive 'skipped only when offline' clause")
        for field in ("recordsSync", "mealsSync"):
            if not entry.get(field, "").strip():
                errors.append(f"{locale}.{field}: missing (qualifies the staged 'developer does not receive' denial)")
        if locale in CJK_LOCALES:
            spaced = sorted(field for field, value in entry.items() if isinstance(value, str) and "。 " in value)
            if spaced:
                errors.append(f"{locale}: ASCII space after '。' in {spaced}")
        sync = entry.get("sync", "")
        tombstone_open = (candidate.get("serverReadiness") or {}).get("tombstoneRetentionDecided") is not True
        digest = legal_release.PENDING_DIGEST_BASIS[locale]
        if tombstone_open and digest not in sync:
            errors.append(f"{locale}.sync: lost the pending digest-marker basis sentence")
        if not tombstone_open and digest in sync:
            errors.append(f"{locale}.sync: tombstone retention is decided but the pending digest sentence remains")
        retention = entry.get("retention", "")
        if RETIRED_BACKUP_MECHANISM[locale] in retention:
            errors.append(f"{locale}.retention: names the daily-snapshot backup mechanism the hybrid backup "
                          "decision replaces")
        if BACKUP_WINDOW_SENTENCES[locale] not in retention:
            errors.append(f"{locale}.retention: lacks the mechanism-neutral 7-day backup window sentence")
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
    on either platform, keep an unqualified records/meals denial (round 3) or drop the pending
    verifier location from the Android purchase section."""
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
        ios_entry = sources["ios-content.json"]["locales"][locale]
        android_entry = sources["android-content.candidate.json"]["locales"][locale]
        for name, entry in (("ios-content.json", ios_entry), ("android-content.candidate.json", android_entry)):
            text = json.dumps(entry, ensure_ascii=False)
            for kind, denials in (("records", RECORD_DENIALS), ("meals", MEAL_DENIALS)):
                if denials[locale] in text:
                    errors.append(f"{name}:{locale}: keeps the unqualified {kind} denial {denials[locale]!r}")
        records_sync = candidate["locales"][locale].get("recordsSync", "")
        meals_sync = candidate["locales"][locale].get("mealsSync", "")
        qualified = (
            ("ios-content.json", "support storage answer", records_sync,
             "\n\n".join(ios_entry["support"]["released"]["storage"]["answers"])),
            ("ios-content.json", "meals section", meals_sync, "\n\n".join(ios["meals"]["paragraphs"])),
            ("ios-content.json", "next-release meals paragraph", meals_sync,
             "\n\n".join(ios["next-release"]["paragraphs"])),
            ("android-content.candidate.json", "next-release meals paragraph", meals_sync,
             "\n\n".join(android["next-release"]["paragraphs"])),
        )
        for name, where, sentence, text in qualified:
            if not sentence or sentence not in text:
                errors.append(f"{name}:{locale}: {where} lacks the qualified sync sentence")
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
    transfer = transfer_disclosure_errors()
    assert not transfer, (
        f"account/sync candidate states {len(transfer)} false or incomplete facts, e.g. {transfer[:3]}"
    )
    candidate = load()
    print(f"OK: {len(candidate['locales'])} account/sync draft locales; status={candidate['status']}")
