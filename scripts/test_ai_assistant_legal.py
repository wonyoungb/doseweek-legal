"""Legal copy contract for the Pro "AI 기록 도우미" (lane LEGAL-AI, 2026-10-02).

PRO-SPEC section 8 (critic C18, C20, C23), sections 4.4 and 5.1-5.5, compliance sections 4.5
and 8, and the owner's second round: 150 requests a month, a 7-day trial with 50, the names
"AI 기록 도우미" and "우선 문의 답변" (never "상담").

The staged 1.0.6 pages must carry the privacy section "AI 기록 도우미(Pro)", the Amazon Bedrock
processor row, the exception after every "the server cannot read your records" claim, the Terms
section and the US consumer-health additions in all 17 locales. The app-consumed consent copy,
the neutral What's New line, the per-locale review receipts and the store declaration drafts
are checked here too.

Assertion REDs: only APIs that exist on the parent commit are imported at module level.
Run from the repository root: python3 -m unittest discover -s scripts -p 'test_*.py'
"""
import hashlib
import html
import importlib
import importlib.util
import json
import re
import unittest
from pathlib import Path

import render_account_sync

ROOT = Path(__file__).resolve().parents[1]
WEB_SOURCE = 'docs/ai-assistant-content.candidate.json'
APP_SOURCE = 'docs/ai-app-copy.candidate.json'
STORE_DOC = 'docs/AI_STORE_DECLARATIONS_1_0_6.md'
RECEIPTS = 'evidence/pro-legal-ai-20261002/locale-review'
LOCALES = ('ko', 'en', 'ja', 'de', 'fr', 'es', 'it', 'nl', 'pt-PT', 'pl', 'sv', 'hi',
           'pt-BR', 'ar', 'zh-Hans', 'zh-Hant', 'tr')
CJK = ('ja', 'zh-Hans', 'zh-Hant')
SECTION = 'ai-assistant'
BEDROCK_ROW = 'aws-bedrock'
# The feature name each locale's shipped ai.* copy uses (CON-PRO shared_copy.json, 6186a662),
# as the stem that survives case endings.
NAME_STEMS = {
    'ko': 'AI 기록 도우미', 'en': 'AI record assistant', 'ja': 'AI記録アシスタント',
    'de': 'KI-Aufzeichnungsassistent', 'fr': 'assistant de suivi IA',
    'es': 'asistente de registros con IA', 'it': 'assistente IA per le registrazioni',
    'nl': 'AI-registratieassistent', 'pt-PT': 'assistente de registos com IA',
    'pl': 'wpisów AI', 'sv': 'AI-loggassistent', 'hi': 'AI रिकॉर्ड असिस्टेंट',
    'pt-BR': 'assistente de registros com IA', 'ar': 'مساعد السجلات بالذكاء الاصطناعي',
    'zh-Hans': 'AI 记录助手', 'zh-Hant': 'AI 紀錄助手', 'tr': 'yapay zeka kayıt asistan',
}
HELPLINES = ('119', '109', '911', '988', '0120-279-338', 'findahelpline.com')
# Review round 2: DoseWeek has two kinds of AI. AI entry and Visit Prep run on the device (iOS);
# the AI record assistant (Pro) is processed on a server by a third-party model. Text that
# describes one must not deny the other. These stems mark "server" and "on the device" in each
# locale, and the phrases of the 1.0.5 sentence "No Private Cloud Compute, server model, or
# third-party model is used", which is false for the app as a whole once the assistant ships.
SERVER_STEMS = {
    'ko': '서버', 'en': 'server', 'ja': 'サーバー', 'de': 'Server', 'fr': 'serveur', 'es': 'servidor',
    'it': 'server', 'nl': 'server', 'pt-PT': 'servidor', 'pl': 'serwer', 'sv': 'server',
    'hi': 'सर्वर', 'pt-BR': 'servidor', 'ar': 'خادم', 'zh-Hans': '服务器', 'zh-Hant': '伺服器',
    'tr': 'sunucu',
}
ON_DEVICE_STEMS = {
    'ko': '기기', 'en': 'device', 'ja': '端末', 'de': 'Gerät', 'fr': 'appareil', 'es': 'dispositivo',
    'it': 'dispositivo', 'nl': 'apparaat', 'pt-PT': 'dispositivo', 'pl': 'urządzeni',
    'sv': 'enheten', 'hi': 'डिवाइस', 'pt-BR': 'dispositivo', 'ar': 'الجهاز', 'zh-Hans': '设备',
    'zh-Hant': '裝置', 'tr': 'cihaz',
}
DENIAL_STEMS = {
    'ko': ('서버 모델', '제3자 모델'),
    'en': ('server model', 'third-party model'),
    'ja': ('サーバーモデル', '第三者モデル'),
    'de': ('Servermodell', 'Modell Dritter', 'Modelle Dritter'),
    'fr': ('modèle serveur', 'modèle tiers'),
    'es': ('modelos de servidor', 'modelo en servidor', 'modelos de terceros', 'modelo de terceros'),
    'it': ('modelli su server', 'modelli di terze parti'),
    'nl': ('servermodel', 'model van derden'),
    'pt-PT': ('modelo em servidor', 'modelos em servidor', 'modelo de terceiros', 'modelos de terceiros'),
    'pl': ('model serwerowy', 'modele serwerowe', 'model innej firmy', 'modele podmiotów zewnętrznych'),
    'sv': ('servermodell', 'tredjepartsmodell', 'modell från tredje part'),
    'hi': ('सर्वर मॉडल', 'तीसरे पक्ष के मॉडल', 'थर्ड-पार्टी मॉडल'),
    'pt-BR': ('modelo em servidor', 'modelo de terceiros'),
    'ar': ('نموذج خادم', 'نموذج على خادم', 'نموذج من طرف ثالث', 'نموذج من طرف خارجي'),
    'zh-Hans': ('服务器模型', '第三方模型'),
    'zh-Hant': ('伺服器模型', '第三方模型'),
    'tr': ('sunucu modeli', 'üçüncü taraf model'),
}
ON_DEVICE_MODEL = 'SystemLanguageModel.default'
SERVER_CANNOT_READ_FIELDS = ('recordsSync', 'mealsSync', 'sync')
SENTENCE = re.compile(r'(?<=[。।])|(?<=\.)\s+')
RETIRED_KOREAN = ('상담', 'AI 코치', 'AI 영양사', 'AI 닥터', '주치의', '무제한', '부작용 관리')
SCREEN_A = (
    'title', 'lead', 'sent.title', 'sent.body', 'notSent.body', 'notSent.health.ios',
    'notSent.health.android', 'where.title', 'where.body', 'retention.title', 'retention.body',
    'e2ee.title', 'e2ee.body', 'optional.title', 'optional.body', 'check.health',
    'check.health.detail', 'check.age', 'later', 'agree', 'region.jp', 'region.us',
)
SCREEN_B = (
    'title', 'purpose.weekly', 'purpose.meal', 'row.doses', 'row.weight', 'row.symptoms',
    'row.meals', 'weight.excluded.ios', 'weight.excluded.android', 'preview', 'processing',
    'quota.weekly', 'quota.regenerate', 'quota.remaining', 'cancel', 'send',
)
SETTINGS = (
    'ai.help.inputNote', 'ai.settings.title', 'ai.settings.state.on', 'ai.settings.viewConsent',
    'ai.settings.usage', 'ai.settings.deleteSummaries', 'ai.settings.withdraw',
    'ai.settings.withdraw.note', 'ai.settings.withdraw.store.ios',
    'ai.settings.withdraw.store.android', 'ai.settings.supportInquiry', 'pro.support.priority',
)
APP_KEYS = (*(f'ai.consent.a.{key}' for key in SCREEN_A), *(f'ai.consent.b.{key}' for key in SCREEN_B),
            *SETTINGS)
PLACEHOLDER = re.compile(r'\{[A-Za-z0-9]+\}')
# Critic C23 (PRO-SPEC section 8): "a recorded back-translation check of Screen A, Screen B, the
# labels and the refusal templates". Every app key is recorded, short labels and buttons too:
# the first receipts recorded only 11 of the 50 app keys and still recommended the flag.
BACK_TRANSLATED_APP_KEYS = APP_KEYS
RECEIPT_SCOPE = {
    'screenA': tuple(f'ai.consent.a.{key}' for key in SCREEN_A),
    'screenB': tuple(f'ai.consent.b.{key}' for key in SCREEN_B),
    'settingsAndPerk': SETTINGS,
}
CON_PRO_KEYS = (
    'ai.refuse.dose', 'ai.refuse.sideEffect', 'ai.refuse.diagnosis', 'ai.refuse.drugInfo',
    'ai.refuse.diet', 'ai.refuse.pregnancy', 'ai.refuse.minor', 'ai.refuse.other', 'ai.emergency',
    'ai.emergency.generic', 'ai.crisis', 'ai.crisis.generic', 'ai.label.header', 'ai.label.output',
    'ai.label.export',
)
# Owner rule 2026-10-02 15:3x: release notes never mention ads, Plus/Pro or any paid tier,
# subscriptions, prices or trials. Substrings are matched on the casefolded line; the
# Latin-script tier names are matched as whole words.
RELEASE_NOTE_TERMS = {
    'ko': ('구독', '가격', '요금', '무료', '체험', '광고', '유료', '결제'),
    'en': ('subscri', 'price', 'trial', 'free', 'advert', 'paid', 'premium', 'purchase'),
    'ja': ('サブスク', '定期購入', '価格', '料金', '無料', 'トライアル', '体験', '広告', '有料', '購入'),
    'de': ('abo', 'preis', 'kostenlos', 'testphase', 'probe', 'werbung', 'kauf', 'bezahl'),
    'fr': ('abonnement', 'prix', 'gratuit', 'essai', 'publicité', 'payant', 'achat'),
    'es': ('suscripción', 'precio', 'gratis', 'gratuit', 'prueba', 'anuncio', 'publicidad', 'pago', 'compra'),
    'it': ('abbonamento', 'prezzo', 'gratis', 'gratuit', 'prova', 'pubblicità', 'pagamento', 'acquisto'),
    'nl': ('abonnement', 'prijs', 'gratis', 'proef', 'advertentie', 'reclame', 'betaald', 'aankoop'),
    'pt-PT': ('subscrição', 'preço', 'grátis', 'gratuit', 'experimental', 'anúncio', 'publicidade', 'pago', 'compra'),
    'pl': ('subskrypc', 'cena', 'cen ', 'bezpłat', 'próbn', 'reklam', 'płatn', 'zakup'),
    'sv': ('prenumeration', 'pris', 'gratis', 'kostnadsfri', 'provperiod', 'annons', 'reklam', 'betal', 'köp'),
    'hi': ('सब्सक्रिप्शन', 'कीमत', 'मुफ़्त', 'ट्रायल', 'विज्ञापन', 'भुगतान', 'खरीद'),
    'pt-BR': ('assinatura', 'preço', 'grátis', 'gratuit', 'teste', 'anúncio', 'publicidade', 'pago', 'compra'),
    'ar': ('اشتراك', 'سعر', 'مجان', 'تجريب', 'إعلان', 'مدفوع', 'شراء'),
    'zh-Hans': ('订阅', '价格', '免费', '试用', '广告', '付费', '购买'),
    'zh-Hant': ('訂閱', '價格', '免費', '試用', '廣告', '付費', '購買'),
    'tr': ('abonelik', 'fiyat', 'ücretsiz', 'deneme', 'reklam', 'ücretli', 'satın'),
}
TIER_WORDS = re.compile(r'\b(pro|plus)\b', re.IGNORECASE)
GERMAN_DU = re.compile(r'\b(du|dich|dir|dein|deine|deinen|deinem|deiner|deines)\b', re.IGNORECASE)
DUTCH_JE = re.compile(r'\b(je|jij|jou|jouw)\b', re.IGNORECASE)


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def sections(entries):
    return {section['id']: section for section in entries}


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)


def plain(markup):
    """A rendered page as the text a reader sees: tags removed, entities decoded."""
    return html.unescape(re.sub(r'<[^>]+>', '', markup))


def sentences(text):
    return [part.strip() for part in SENTENCE.split(text) if part.strip()]


def number(value, text):
    return re.search(rf'(?<![\d.,]){value}(?![\d])', text) is not None


def canonical_sha256(value):
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


class AiAssistantLegalCopyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.account = load('docs/account-sync-content.candidate.json')
        cls.staged = render_account_sync.integrated_sources()
        cls.pages = {path.relative_to(ROOT).as_posix(): markup
                     for path, markup in render_account_sync.rendered_pages(cls.staged).items()}
        cls.ios = cls.staged['ios-content.json']
        cls.android = cls.staged['android-content.candidate.json']
        cls.terms = cls.staged['terms-content.json']
        cls.us_health = cls.staged['us-health-content.json']

    # -- helpers ------------------------------------------------------------------------------

    def source(self, path):
        self.assertTrue((ROOT / path).is_file(),
                        f'{path} is missing: the AI record assistant copy is not written')
        return load(path)

    def supplement(self, document, locale):
        return document['locales'][locale]['privacy']['legalSupplement']

    def ai_section(self, document, locale):
        found = sections(self.supplement(document, locale)['sections'])
        self.assertIn(SECTION, found, f'{locale}: privacy policy has no AI record assistant section')
        return found[SECTION]

    def terms_section(self, locale):
        found = sections(self.terms['locales'][locale]['sections'])
        self.assertIn(SECTION, found, f'{locale}: Terms have no AI record assistant section')
        return found[SECTION]

    def assert_names_feature(self, locale, text, where):
        self.assertIn(NAME_STEMS[locale].casefold(), text.casefold(),
                      f'{locale}: {where} does not name the AI record assistant')

    # -- privacy policy -----------------------------------------------------------------------

    def test_privacy_policies_carry_the_ai_record_assistant_section_in_17_locales(self):
        for platform, document in (('ios', self.ios), ('android', self.android)):
            for locale in LOCALES:
                with self.subTest(platform=platform, locale=locale):
                    section = self.ai_section(document, locale)
                    self.assertEqual([item['id'] for item in self.supplement(document, locale)['sections']][-1],
                                     SECTION)
                    self.assert_names_feature(locale, section['title'], 'section title')
                    self.assertIn('Pro', section['title'])
                    clauses = section['paragraphs']
                    self.assertEqual(len(clauses), 12, 'ten compliance 8.1 clauses, age and safety')
                    for token in ('Amazon Bedrock', 'ap-northeast-2', 'Anthropic', 'Claude'):
                        self.assertIn(token, clauses[4], f'processor clause lacks {token}')
                    self.assertIn('Cloudflare', clauses[5], 'HPKE transit sentence names the relay')
                    self.assertTrue(number(18, clauses[10]), 'AI is 18+')
                    for token in HELPLINES:
                        self.assertIn(token, clauses[11], f'safety clause lacks {token}')
                    self.assertNotIn('{', ''.join(clauses), 'no unresolved placeholder')

    def test_ai_section_names_only_its_own_platform_health_source(self):
        for locale in LOCALES:
            with self.subTest(locale=locale):
                ios = '\n'.join(self.ai_section(self.ios, locale)['paragraphs'])
                android = '\n'.join(self.ai_section(self.android, locale)['paragraphs'])
                self.assertIn('Apple', ios)
                self.assertEqual([t for t in ('Health Connect', 'Android', 'Google Play') if t in ios], [])
                self.assertIn('Health Connect', android)
                self.assertEqual([t for t in ('Apple', 'iOS', 'App Store') if t in android], [])

    def test_ai_section_items_and_retention_follow_screen_a_not_the_first_draft(self):
        # Critic C18: no memo is ever sent (R-7); no chat history, at most two cards outside
        # every backup (R-8); counts up to 2 months, report excerpts 30 days (R-9), never 90.
        for locale in LOCALES:
            with self.subTest(locale=locale):
                clauses = self.ai_section(self.ios, locale)['paragraphs']
                self.assertTrue(number(2, clauses[3]) and number(30, clauses[3]), clauses[3])
                self.assertFalse(number(90, clauses[3]), 'compliance draft retention (90 days) is retired')
        korean = self.ai_section(self.ios, 'ko')['paragraphs']
        self.assertNotIn('내가 고른 경우의 메모', korean[1])
        for item in ('증상 종류별 기록 횟수', '단백질 평균·목표', '연속 기록 주 수', '알레르기', '싫어하는 음식',
                     '언어·지역', '앱 버전'):
            self.assertIn(item, korean[1], f'clause 2 names {item} as Screen A does')
        for fact in ('대화 내용은 저장하지 않아요', '최대 2개', '최대 2개월', '계정이 있는 동안', '30일'):
            self.assertIn(fact, korean[3])

    def test_processor_table_lists_bedrock_seoul_in_region_without_retention(self):
        for platform, document in (('ios', self.ios), ('android', self.android)):
            live = load('docs/ios-content.json' if platform == 'ios' else 'docs/android-content.candidate.json')
            for locale in LOCALES:
                with self.subTest(platform=platform, locale=locale):
                    table = sections(self.supplement(document, locale)['sections'])['processors']['table']
                    ids = [row['id'] for row in table['rows']]
                    self.assertIn(BEDROCK_ROW, ids, 'processor table has no Amazon Bedrock row')
                    self.assertEqual(ids.index(BEDROCK_ROW), ids.index('aws') + 1)
                    row = sections(table['rows'])[BEDROCK_ROW]
                    self.assertEqual(row['role'], 'processor')
                    cells = row['cells']
                    self.assertTrue(cells['legalBasis'].startswith('Amazon Bedrock (AWS) — '))
                    self.assertIn('ap-northeast-2', cells['country'])
                    self.assertIn('https://aws.amazon.com/privacy/', cells['recipientContact'])
                    self.assertIn('Amazon Bedrock', cells['retention'])
                    self.assertIn('Anthropic', cells['purpose'])
                    live_table = sections(self.supplement(live, locale)['sections'])['processors']['table']
                    before = sections(live_table['rows'])['cloudflare']['cells']['data']
                    after = sections(table['rows'])['cloudflare']['cells']['data']
                    self.assertTrue(after.startswith(before) and len(after) > len(before),
                                    'Cloudflare row must add the ciphertext-only transit of AI requests')

    def test_every_server_cannot_read_claim_is_followed_by_the_ai_exception(self):
        for name, document, minimum in (('ios', self.ios, 3), ('android', self.android, 3),
                                        ('terms', self.terms, 1)):
            for locale in LOCALES:
                claims = [self.account['locales'][locale][field] for field in SERVER_CANNOT_READ_FIELDS]
                found = 0
                unqualified = []
                for text in strings(document['locales'][locale]):
                    for claim in claims:
                        start = text.find(claim)
                        while start != -1:
                            found += 1
                            following = text[start + len(claim):start + len(claim) + 700]
                            first_block = following.split('\n\n')[0]
                            if 'Amazon Bedrock' not in first_block:
                                unqualified.append(claim[:60])
                            start = text.find(claim, start + len(claim))
                with self.subTest(source=name, locale=locale):
                    self.assertGreaterEqual(found, minimum, 'the staged text lost its sync claims')
                    self.assertEqual(unqualified, [],
                                     f'{len(unqualified)} of {found} "server cannot read" claims lack the '
                                     'AI record assistant exception (end-to-end encryption covers sync '
                                     'and backup only)')

    def test_the_exception_is_the_candidate_sentence_and_names_the_feature(self):
        candidate = self.source(WEB_SOURCE)
        for locale in LOCALES:
            with self.subTest(locale=locale):
                exception = candidate['locales'][locale]['e2eeException']
                self.assert_names_feature(locale, exception, 'the end-to-end exception')
                self.assertIn('DoseWeek', exception)
                joiner = '' if locale in CJK else ' '
                claim = self.account['locales'][locale]['recordsSync']
                staged = '\n'.join(strings(self.ios['locales'][locale]))
                self.assertIn(claim + joiner + exception, staged)

    def test_health_platform_paragraphs_say_the_data_is_not_used_for_ai(self):
        for locale in LOCALES:
            with self.subTest(locale=locale):
                health = sections(self.ios['locales'][locale]['privacy']['sections'])['health']
                self.assert_names_feature(locale, health['paragraphs'][0], 'the Apple Health paragraph')
                connect = sections(self.android['locales'][locale]['privacy']['sections'])['no-collection']
                self.assertIn('Health Connect', connect['paragraphs'][2])
                self.assert_names_feature(locale, connect['paragraphs'][2], 'the Health Connect paragraph')

    def test_on_device_ai_section_points_to_the_server_assistant(self):
        for locale in LOCALES:
            with self.subTest(locale=locale):
                on_device = sections(self.ios['locales'][locale]['privacy']['sections'])['ai']
                self.assert_names_feature(locale, on_device['paragraphs'][0].split('\n\n')[-1],
                                          'the on-device AI section')

    def test_android_faq_no_longer_says_1_0_6_has_no_generative_ai(self):
        live = load('docs/android-content.candidate.json')
        for locale in LOCALES:
            with self.subTest(locale=locale):
                answer = sections(live['locales'][locale]['support']['faq'])['ai-health']['answers'][0]
                denial = [part.strip() for part in SENTENCE.split(answer) if part.strip()][0]
                self.assertIn('1.0.5', denial)
                staged = sections(self.android['locales'][locale]['support']['faq'])['ai-health']['answers'][0]
                self.assertNotIn(denial.replace('1.0.5', '1.0.6'), staged,
                                 '1.0.6 ships the AI record assistant: "no generative AI" is false')
                self.assertIn('Amazon Bedrock', staged)
                self.assert_names_feature(locale, staged, 'the Android AI answer')

    def test_android_badge_and_not_used_list_no_longer_deny_generative_ai(self):
        # The 1.0.5 badge "No generative AI" and the item "Generative AI" in the list of things
        # DoseWeek does not use are false once the assistant ships in 1.0.6. The same page
        # carries the "AI 기록 도우미(Pro)" section and the Amazon Bedrock row.
        live = load('docs/android-content.candidate.json')
        root_page = self.pages['android/privacy/index.html']
        for locale in LOCALES:
            before = live['locales'][locale]
            badge = before['home']['featureBadges'][3]
            item = sections(before['privacy']['sections'])['no-collection']['items'][4]
            after = self.android['locales'][locale]
            badges = after['home']['featureBadges']
            items = sections(after['privacy']['sections'])['no-collection']['items']
            with self.subTest(locale=locale):
                self.assertEqual((len(badges), len(items)), (4, 7))
                self.assertNotIn(badge, badges, 'the staged badge still says there is no generative AI')
                self.assertNotIn(item, items, 'the staged not-used list still names generative AI outright')
                self.assert_names_feature(locale, badges[3], 'the generative AI badge')
                self.assert_names_feature(locale, items[4], 'the generative AI item of the not-used list')
                self.assertEqual([t for t in ('Apple', 'iOS', 'App Store') if t in badges[3] + items[4]], [])
                bare = f'<li>{html.escape(item)}</li>'
                self.assertNotIn(bare, self.pages[f'{locale}/android/privacy/index.html'],
                                 'the staged Android privacy page lists generative AI as not used')
                self.assertNotIn(bare, root_page, 'the staged root Android privacy page lists generative AI as not used')
                self.assertIn(f'<li>{html.escape(items[4])}</li>',
                              self.pages[f'{locale}/android/privacy/index.html'])
        korean = self.android['locales']['ko']
        self.assertEqual(korean['home']['featureBadges'][3], '생성형 AI는 따로 동의한 AI 기록 도우미에서만 써요')
        self.assertEqual(sections(korean['privacy']['sections'])['no-collection']['items'][4],
                         '따로 동의하기 전에 생성형 AI(AI 기록 도우미) 사용')
        english = self.android['locales']['en']
        self.assertEqual(english['home']['featureBadges'][3],
                         'Generative AI only in the AI record assistant, after separate consent')
        self.assertEqual(sections(english['privacy']['sections'])['no-collection']['items'][4],
                         'Using generative AI (the AI record assistant) without your separate consent')

    def test_android_renderer_rejects_the_bare_generative_ai_denial_for_1_0_6(self):
        import copy
        import render_android
        for field, value in (('badge', 'No generative AI'), ('item', 'Generative AI')):
            catalog = copy.deepcopy(self.android)
            english = catalog['locales']['en']
            if field == 'badge':
                english['home']['featureBadges'][3] = value
            else:
                sections(english['privacy']['sections'])['no-collection']['items'][4] = value
            with self.subTest(field=field):
                self.assertEqual(catalog['versionName'], '1.0.6')
                with self.assertRaises(AssertionError, msg=f'validate_catalog accepts the 1.0.6 {field} {value!r}'):
                    render_android.validate_catalog(catalog)
        # The served 1.0.5 source keeps its badge until 1.0.6 is published.
        render_android.validate_catalog(live := load('docs/android-content.candidate.json'))
        self.assertEqual(live['versionName'], '1.0.5')

    # -- review round 2: on-device AI and the server assistant are different features ----------

    def test_ios_ai_answer_says_which_ai_runs_on_the_device_and_which_on_a_server(self):
        # The staged iOS 1.0.6 support FAQ "Why is an AI feature unavailable?" ended with "No
        # Private Cloud Compute, server model, or third-party model is used." That is true for AI
        # entry and Visit Prep only: the AI record assistant (Pro) is processed on a server by
        # Amazon Bedrock. PRO-SPEC 4.4 `ai.paused` links to this answer.
        live = load('docs/ios-content.json')
        candidate = self.source(WEB_SOURCE)
        root = plain(self.pages['support/index.html'])
        for locale in LOCALES:
            before = live['locales'][locale]['support']['released']['ai']['answers']
            parts = sentences(before[0])
            denial = parts[-1]
            after = self.ios['locales'][locale]['support']['released']['ai']['answers']
            text = candidate['locales'][locale]
            scoped, pointer = text.get('onDeviceOnly', ''), text.get('iosAiFaq', '')
            joiner = '' if locale in CJK else ' '
            with self.subTest(locale=locale):
                self.assertEqual(len(parts), 3, 'the 1.0.5 answer changed: review the replacement')
                self.assertIn('Private Cloud Compute', denial)
                self.assertEqual(after[1:], before[1:], 'the fallback answer is kept')
                answer = after[0]
                self.assertNotIn(denial, answer,
                                 'the staged iOS AI answer still says no server or third-party model '
                                 'is used, without saying that this covers only the on-device features')
                self.assert_names_feature(locale, answer, 'the iOS AI answer')
                for token in ('Amazon Bedrock', 'Anthropic', 'Claude', 'DoseWeek', 'Private Cloud Compute'):
                    self.assertIn(token, answer, f'the iOS AI answer lacks {token}')
                self.assertEqual(answer.count(ON_DEVICE_MODEL), 1)
                self.assertTrue(scoped and pointer,
                                'the candidate has no onDeviceOnly / iosAiFaq text for this locale')
                self.assertEqual(answer, before[0][:before[0].rindex(denial)] + scoped + joiner + pointer)
                self.assertNotIn(denial, scoped, 'the scoped sentence repeats the bare denial')
                self.assertIn('Private Cloud Compute', scoped)
                self.assertIn(ON_DEVICE_STEMS[locale].casefold(), scoped.casefold(),
                              'the denial is not scoped to the on-device features')
                self.assert_names_feature(locale, pointer, 'the pointer to the server assistant')
                self.assertIn(SERVER_STEMS[locale].casefold(), pointer.casefold(),
                              'the pointer does not say the assistant is processed on a server')
                self.assertEqual([t for t in ('Android', 'Google Play', 'Health Connect')
                                  if t in scoped + pointer], [])
                self.assertNotIn(ON_DEVICE_MODEL, scoped + pointer)
                page = plain(self.pages[f'{locale}/support/index.html'])
                for rendered, name in ((page, 'locale'), (root, 'root')):
                    self.assertIn(scoped + joiner + pointer, rendered, f'{name} support page')
                    self.assertNotIn(denial, rendered, f'{name} support page keeps the bare denial')
        korean = self.ios['locales']['ko']['support']['released']['ai']['answers'][0]
        self.assertTrue(korean.endswith(
            '기기 안에서 처리하는 이 두 기능에는 Private Cloud Compute, 서버 모델, 제3자 모델을 쓰지 않아요. '
            'AI 기록 도우미(Pro)는 이와 다른 기능이에요. 서버에서 제3자 모델로 처리해요. 따로 동의한 뒤에만, '
            '확인하고 보낸 내용이 DoseWeek 서버를 거쳐 Amazon Bedrock(대한민국 서울 리전)으로 가고, '
            'Anthropic의 Claude 모델이 답을 만들어요. 인터넷에 연결되어 있어야 하고, 잠시 쉬어 갈 때는 '
            '앱에서 알려 드려요. 자세한 내용은 개인정보 처리방침의 ‘AI 기록 도우미(Pro)’ 항목에 있어요.'), korean)
        english = self.ios['locales']['en']['support']['released']['ai']['answers'][0]
        self.assertTrue(english.endswith(
            'These two on-device features use no Private Cloud Compute, server model, or third-party '
            'model. The AI record assistant (Pro) is a different feature: it is processed on a server, '
            'with a third-party model. Only after your separate consent, what you confirm and send '
            'goes through the DoseWeek server to Amazon Bedrock (Seoul Region, Republic of Korea), '
            'where the Claude model by Anthropic creates the answer. It needs an internet connection '
            'and can be paused for a while; the app tells you when that happens. The Privacy Policy '
            'describes it under “AI record assistant (Pro)”.'), english)

    def test_on_device_ai_section_scopes_its_denial_to_the_on_device_features(self):
        live = load('docs/ios-content.json')
        candidate = self.source(WEB_SOURCE)
        root = plain(self.pages['privacy/index.html'])
        for locale in LOCALES:
            before = sections(live['locales'][locale]['privacy']['sections'])['ai']['paragraphs'][0]
            found = [part for part in sentences(before.split('\n\n')[0]) if 'Private Cloud Compute' in part]
            after = sections(self.ios['locales'][locale]['privacy']['sections'])['ai']['paragraphs'][0]
            text = candidate['locales'][locale]
            scoped = text.get('onDeviceOnly', '')
            with self.subTest(locale=locale):
                self.assertEqual(len(found), 1, 'the 1.0.5 section changed: review the replacement')
                denial = found[0]
                self.assertEqual(before.count(denial), 1)
                self.assertNotIn(denial, after,
                                 'the staged on-device AI section still says no server or third-party '
                                 'model is used, without scope')
                self.assertTrue(scoped, 'the candidate has no onDeviceOnly text for this locale')
                self.assertNotIn(denial, scoped)
                self.assertEqual(after, before.replace(denial, scoped) + '\n\n' + text['onDeviceScope'])
                self.assertEqual(after.count(ON_DEVICE_MODEL), 1)
                page = plain(self.pages[f'{locale}/privacy/index.html'])
                for rendered, name in ((page, 'locale'), (root, 'root')):
                    self.assertIn(scoped, rendered, f'{name} privacy page')
                    self.assertNotIn(denial, rendered, f'{name} privacy page keeps the bare denial')

    def test_no_staged_text_denies_a_server_or_third_party_model_outside_the_scoped_sentences(self):
        # Sweep: the staged policies, help pages, Terms and US policy, and both candidate files.
        # The phrases may appear only inside the candidate sentences that scope them to the
        # on-device features or attribute them to the assistant.
        candidate = self.source(WEB_SOURCE)
        app = self.source(APP_SOURCE)
        documents = (('ios', self.ios), ('android', self.android), ('terms', self.terms),
                     ('us-health', self.us_health), ('web candidate', candidate), ('app copy', app))
        for locale in LOCALES:
            text = candidate['locales'][locale]
            allowed = [part for part in (text.get('onDeviceOnly', ''), text.get('iosAiFaq', '')) if part]
            for name, document in documents:
                found = []
                for value in strings(document['locales'][locale]):
                    for part in allowed:
                        value = value.replace(part, '')
                    folded = value.casefold()
                    found += [stem for stem in DENIAL_STEMS[locale] if stem.casefold() in folded]
                with self.subTest(source=name, locale=locale):
                    self.assertEqual(found, [],
                                     f'{name} denies a server or third-party model without scope')
        for path, markup in self.pages.items():
            locale = path.split('/')[0]
            if locale not in LOCALES:
                continue
            text = candidate['locales'][locale]
            rendered = plain(markup)
            for part in (text.get('onDeviceOnly', ''), text.get('iosAiFaq', '')):
                if part:
                    rendered = rendered.replace(part, '')
            folded = rendered.casefold()
            with self.subTest(page=path):
                self.assertEqual([stem for stem in DENIAL_STEMS[locale] if stem.casefold() in folded], [])

    def test_ios_renderer_rejects_the_unscoped_ai_denial_for_1_0_6(self):
        import copy
        import render_ios
        live = load('docs/ios-content.json')
        catalog = copy.deepcopy(self.ios)
        self.assertEqual(catalog['bundleVersion'], '1.0.6')
        render_ios.validate(catalog)
        catalog['locales']['en']['support']['released']['ai']['answers'][0] = (
            live['locales']['en']['support']['released']['ai']['answers'][0])
        with self.assertRaises(AssertionError,
                               msg='render_ios.validate accepts the 1.0.5 AI answer in a 1.0.6 catalog'):
            render_ios.validate(catalog)
        # The served 1.0.5 source keeps its answer until 1.0.6 is published.
        render_ios.validate(live)
        self.assertEqual(live['bundleVersion'], '1.0.5')

    def test_android_ai_answer_says_the_assistant_is_processed_on_a_server(self):
        candidate = self.source(WEB_SOURCE)
        for locale in LOCALES:
            answer = candidate['locales'][locale]['androidAiFaq']
            staged = sections(self.android['locales'][locale]['support']['faq'])['ai-health']['answers'][0]
            with self.subTest(locale=locale):
                self.assertIn(SERVER_STEMS[locale].casefold(), answer.casefold(),
                              'the Android AI answer does not say the assistant is processed on a server')
                self.assertTrue(staged.startswith(answer))
                self.assertEqual(len(sentences(answer)), 4)
                self.assertIn(ON_DEVICE_STEMS[locale].casefold(), sentences(answer)[1].casefold(),
                              'the Android AI answer does not say it is not processed on the device')
        self.assertIn('이 기능은 기기가 아니라 서버에서 처리해요.', candidate['locales']['ko']['androidAiFaq'])
        self.assertIn('It is processed on a server, not on the device.',
                      candidate['locales']['en']['androidAiFaq'])

    # -- Terms and the US policy --------------------------------------------------------------

    def test_terms_have_the_ai_section_right_after_the_medical_notice(self):
        for locale in LOCALES:
            with self.subTest(locale=locale):
                entries = self.terms['locales'][locale]['sections']
                self.assertEqual([item['id'] for item in entries],
                                 ['service', 'free-plus', 'billing', 'ad-free-pass', 'medical', SECTION,
                                  'records', 'changes', 'contact'])
                for position, item in enumerate(entries, 1):
                    self.assertTrue(item['title'].startswith(f'{position}. '), item['title'])
                section = self.terms_section(locale)
                self.assert_names_feature(locale, section['title'], 'Terms section title')
                paragraphs = section['paragraphs']
                self.assertEqual(len(paragraphs), 8)
                self.assertTrue('Plus' in paragraphs[0] and 'Pro' in paragraphs[0] and number(7, paragraphs[0]))
                self.assertTrue(number(18, paragraphs[1]), 'the Terms state the AI age of 18')
                self.assertTrue('119' in paragraphs[3] and '911' in paragraphs[3])
                for value in (150, 50, 30):
                    self.assertTrue(number(value, paragraphs[4]), f'usage clause lacks {value}')
                self.assertIn('UTC', paragraphs[4])
                self.assertTrue(number(1, paragraphs[7]), 'first reply within 1 business day')
                self.assertIsNone(re.search(r'(?:USD|KRW|JPY|[$₩¥])\s*\d', '\n'.join(paragraphs)))

    def test_terms_ai_section_keeps_statutory_rights_and_uses_the_decided_names(self):
        korean = '\n'.join(self.terms_section('ko')['paragraphs'])
        for required in ('AI 기록 도우미', '우선 문의 답변', '1영업일', '의료 질문에는 답하지 않', '의료기기가 아니',
                         '청약철회·환불 권리는 그대로 보장', '적용 30일 전에 알리', '무료 체험 중에는 50회',
                         '한 달에 150회', '만 18세 이상'):
            self.assertIn(required, korean)
        self.assertEqual([term for term in RETIRED_KOREAN if term in korean], [])
        self.assertNotIn('책임을 지지 않', korean, 'no blanket liability exclusion (compliance 8.3)')
        english = '\n'.join(self.terms_section('en')['paragraphs']).casefold()
        self.assertEqual([term for term in ('not liable', 'no liability', 'disclaim', 'counsel', 'coach')
                          if term in english], [])

    def test_us_consumer_health_policy_covers_the_assistant(self):
        live = load('docs/us-health-content.json')
        for locale in LOCALES:
            with self.subTest(locale=locale):
                found = sections(self.us_health['locales'][locale]['sections'])
                before = sections(live['locales'][locale]['sections'])['purposes-sources']['paragraphs'][1]
                after = found['purposes-sources']['paragraphs'][1]
                self.assertTrue(after.startswith(before) and len(after) > len(before),
                                'purposes must add AI summaries and general nutrition ideas on request')
                categories = found['categories']['paragraphs'][0]
                self.assert_names_feature(locale, categories, 'health-data categories')
                self.assertIn('HealthKit', categories)
                self.assertIn('Amazon Bedrock', found['disclosures']['paragraphs'][0])
                self.assert_names_feature(locale, found['disclosures']['paragraphs'][2], 'no-sale paragraph')
                self.assert_names_feature(locale, found['consent']['paragraphs'][1], 'consent paragraph')
        korean = sections(self.us_health['locales']['ko']['sections'])['categories']['paragraphs'][0]
        for item in ('정해진 목록에서 고른 식사 종류·선호', '알레르기', '싫어하는 음식', '종단간 암호화 대상이 아니'):
            self.assertIn(item, korean, 'critic C18: preferences, allergies and dislikes are categories')

    # -- rendered staged pages ----------------------------------------------------------------

    def test_staged_pages_render_the_section_the_row_and_the_deletion_paragraph(self):
        for locale in LOCALES:
            with self.subTest(locale=locale):
                for route in ('privacy/', 'android/privacy/', 'terms/'):
                    page = self.pages[f'{locale}/{route}index.html']
                    self.assertIn(f'id="{locale}-{SECTION}"', page, f'{route}: AI section not rendered')
                for route in ('privacy/', 'android/privacy/'):
                    self.assertIn('Amazon Bedrock (AWS)', self.pages[f'{locale}/{route}index.html'])
                deletion = self.pages[f'{locale}/account/delete/index.html']
                self.assert_names_feature(locale, deletion, 'the account-deletion page')
        for route in ('privacy/', 'android/privacy/', 'terms/', 'account/delete/', 'us-health/'):
            self.assertIn('name="robots" content="noindex,nofollow"', self.pages[f'{route}index.html'])

    def test_served_sources_stay_without_the_unreleased_assistant(self):
        for path in ('docs/ios-content.json', 'docs/android-content.candidate.json',
                     'docs/terms-content.json', 'docs/us-health-content.json'):
            with self.subTest(path=path):
                text = (ROOT / path).read_text(encoding='utf-8')
                self.assertNotIn('Amazon Bedrock', text)
                self.assertNotIn(SECTION, text)

    # -- candidate sources ----------------------------------------------------------------------

    def test_candidate_states_the_decided_facts_and_stays_unpublished(self):
        candidate = self.source(WEB_SOURCE)
        self.assertEqual(candidate['status'], 'pre-release-candidate-not-published')
        facts = candidate['facts']
        self.assertEqual((facts['monthlyRequests'], facts['trialDays'], facts['trialRequests'],
                          facts['minimumAge'], facts['region'], facts['bedrockRetention']),
                         (150, 7, 50, 18, 'ap-northeast-2', 'none'))
        self.assertTrue(candidate['unresolvedBeforePublication'])
        self.assertFalse(any(candidate['readiness'].values()), 'nothing is verified in this lane')
        self.assertEqual(list(candidate['locales']), list(LOCALES))

    def test_release_gate_stays_closed_until_the_assistant_is_verified(self):
        self.assertIsNotNone(importlib.util.find_spec('ai_assistant_candidate'),
                             'scripts/ai_assistant_candidate.py is missing: nothing blocks publication')
        module = importlib.import_module('ai_assistant_candidate')
        module.load()
        module.load_app_copy()
        with self.assertRaises(AssertionError):
            module.require_release_ready()
        self.assertIn('ai_assistant_candidate.require_release_ready()',
                      (ROOT / 'scripts/check_site.py').read_text(encoding='utf-8'))

    def test_release_gate_refuses_the_draft_sentences_even_when_every_flag_is_true(self):
        # Clause 5 and the processor row say the AWS entity "is not yet verified and will be stated
        # before release". Flipping the flags without replacing those sentences must not publish.
        import copy
        import tempfile
        module = importlib.import_module('ai_assistant_candidate')
        candidate = copy.deepcopy(module.load())
        candidate['status'] = 'integrated-and-verified'
        candidate['unresolvedBeforePublication'] = []
        candidate['readiness'] = {key: True for key in candidate['readiness']}
        with tempfile.TemporaryDirectory(prefix='doseweek-legal-gate-') as directory:
            candidate['legalSelfReviewEvidence'] = self._synthetic_legal_self_review_evidence(
                candidate, directory)
            with self.assertRaises(AssertionError,
                                   msg='the release gate opens while the policy still carries draft sentences') as failure:
                module.require_release_ready(candidate, allow_synthetic_fixture=True)
            self.assertIn('AI policy still carries', str(failure.exception))
        draft = candidate.get('preReleaseWording', {})
        self.assertEqual(list(draft), list(LOCALES))

        def without(value, retired):
            if isinstance(value, str):
                for sentence in retired:
                    value = value.replace(sentence, 'Verified.')
                return value
            if isinstance(value, list):
                return [without(item, retired) for item in value]
            if isinstance(value, dict):
                return {key: without(item, retired) for key, item in value.items()}
            return value

        for locale in LOCALES:
            entry = candidate['locales'][locale]
            cells = entry['processorRow']
            with self.subTest(locale=locale):
                self.assertEqual(len(draft[locale]), 5)
                for sentence, field in zip(draft[locale], (entry['clauses'][4], cells['legalBasis'],
                                                           cells['country'], cells['recipientContact'],
                                                           cells['retention'])):
                    self.assertIn(sentence, field)
            candidate['locales'][locale] = without(entry, draft[locale])
        with tempfile.TemporaryDirectory(prefix='doseweek-legal-gate-') as directory:
            candidate['legalSelfReviewEvidence'] = self._synthetic_legal_self_review_evidence(
                candidate, directory)
            module.require_release_ready(candidate, allow_synthetic_fixture=True)

    def _synthetic_legal_self_review_evidence(self, candidate, directory):
        # A test receipt is never evidence of counsel/native review or product readiness.
        scope = ('schemaVersion', 'plannedVersion', 'facts', 'localeOrder',
                 'preReleaseWording', 'locales')
        payload = {
            'aiCandidate': {key: candidate[key] for key in scope},
            'stagedSources': {path: self.source(path) for path in (
                APP_SOURCE, 'docs/account-sync-content.candidate.json',
                'docs/ios-content.json', 'docs/android-content.candidate.json',
                'docs/terms-content.json', 'docs/us-health-content.json')},
        }
        fingerprint = canonical_sha256(payload)
        receipt = {
            'status': 'accepted', 'reviewType': 'codex-source-self-review',
            'scope': 'synthetic regression fixture only; no real approval',
            'synthetic': True,
            'sourceFingerprintSha256': fingerprint,
            'counselReviewed': False, 'nativeSpeakerReview': False,
        }
        path = Path(directory) / 'synthetic-self-review-receipt.json'
        path.write_text(json.dumps(receipt, sort_keys=True) + '\n', encoding='utf-8')
        return {'receiptPath': str(path),
                'receiptSha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'sourceFingerprintSha256': fingerprint}

    def test_release_gate_accepts_current_source_self_review_without_counsel(self):
        import copy
        import tempfile
        from unittest.mock import patch
        module = importlib.import_module('ai_assistant_candidate')
        with patch.object(module, 'require_release_ready',
                          wraps=module.require_release_ready) as baseline_gate:
            self.test_release_gate_refuses_the_draft_sentences_even_when_every_flag_is_true()
        self.assertEqual(baseline_gate.call_count, 2)
        candidate = copy.deepcopy(baseline_gate.call_args.args[0])
        self.assertTrue(all(candidate['readiness'].values()))
        candidate['readiness']['counselReviewed'] = False
        candidate['readiness']['legalSelfReviewAccepted'] = True
        with tempfile.TemporaryDirectory(prefix='doseweek-legal-gate-') as directory:
            candidate['legalSelfReviewEvidence'] = self._synthetic_legal_self_review_evidence(
                candidate, directory)
            self.assertIs(candidate['readiness']['counselReviewed'], False)
            self.assertTrue(all(value for key, value in candidate['readiness'].items()
                                if key != 'counselReviewed'))
            # Every factual flag and draft replacement is valid in this fixture, so
            # the default call must fail specifically at the synthetic evidence boundary.
            with self.assertRaisesRegex(
                    AssertionError, 'Synthetic self-review evidence cannot authorize production release'):
                module.require_release_ready(candidate)
            module.require_release_ready(candidate, allow_synthetic_fixture=True)

            # A current-fingerprint accepted-format receipt passes the default guard.
            # This isolated test control is not real owner acceptance or product readiness.
            control = json.loads(Path(candidate['legalSelfReviewEvidence']['receiptPath']).read_text(
                encoding='utf-8'))
            control['synthetic'] = False
            control['scope'] = 'Current-source fingerprint acceptance control; no product authorization'
            control['testOnly'] = True
            control_path = Path(directory) / 'current-source-acceptance-control.json'
            control_path.write_text(json.dumps(control, sort_keys=True) + '\n', encoding='utf-8')
            candidate['legalSelfReviewEvidence']['receiptPath'] = str(control_path)
            candidate['legalSelfReviewEvidence']['receiptSha256'] = hashlib.sha256(
                control_path.read_bytes()).hexdigest()
            module.require_release_ready(candidate)

    def test_gate_6_and_counsel_items_of_review_round_2_are_recorded_as_blockers(self):
        unresolved = self.source(WEB_SOURCE)['unresolvedBeforePublication']
        for tokens in (('APPI', 'clause 6', 'locales.ja'),
                       ('ai.consent.a.retention.body', 'clause 4', 'gate 6'),
                       ('zh-Hans', 'zh-Hant', 'meal ideas', 'CON-PRO')):
            with self.subTest(tokens=tokens):
                self.assertEqual(len([item for item in unresolved if all(token in item for token in tokens)]), 1)

    def test_korean_copy_never_says_sangdam_and_uses_the_decided_names(self):
        for path in (WEB_SOURCE, APP_SOURCE):
            korean = self.source(path)['locales']['ko']
            text = '\n'.join(strings(korean))
            with self.subTest(path=path):
                self.assertEqual([term for term in RETIRED_KOREAN if term in text], [])
                self.assertEqual((korean['name'], korean['perk']), ('AI 기록 도우미', '우선 문의 답변'))
        perk = self.source(APP_SOURCE)['locales']['ko']['copy']['pro.support.priority']
        self.assertTrue('1영업일' in perk and '의료 질문에는 답하지 않아요' in perk)

    def test_german_uses_sie_and_dutch_uses_u(self):
        for path in (WEB_SOURCE, APP_SOURCE):
            document = self.source(path)
            for locale, pattern in (('de', GERMAN_DU), ('nl', DUTCH_JE)):
                for text in strings(document['locales'][locale]):
                    with self.subTest(path=path, locale=locale, text=text[:40]):
                        self.assertIsNone(pattern.search(text))

    # -- app-consumed copy ------------------------------------------------------------------------

    def test_consent_and_settings_copy_exists_for_every_key_in_17_locales(self):
        document = self.source(APP_SOURCE)
        self.assertEqual(tuple(document['keys']), APP_KEYS)
        self.assertRegex(document['consentVersion'], r'^\d{4}-\d{2}-\d{2}\.\d+$')
        reference = document['locales']['ko']['copy']
        for locale in LOCALES:
            copy = document['locales'][locale]['copy']
            with self.subTest(locale=locale):
                self.assertEqual(tuple(copy), APP_KEYS)
                for key, text in copy.items():
                    self.assertTrue(text.strip(), key)
                    self.assertEqual(sorted(PLACEHOLDER.findall(text)),
                                     sorted(PLACEHOLDER.findall(reference[key])), key)
                    if key.endswith('.ios'):
                        self.assertEqual([t for t in ('Android', 'Google Play', 'Health Connect') if t in text], [], key)
                    elif key.endswith('.android'):
                        self.assertEqual([t for t in ('Apple', 'iOS', 'App Store') if t in text], [], key)
                    else:
                        self.assertEqual([t for t in ('Android', 'iOS', 'Google Play', 'App Store', 'Apple',
                                                      'Health Connect') if t in text], [], key)
                for token in ('Amazon Bedrock', 'Anthropic', 'Claude', 'DoseWeek'):
                    self.assertIn(token, copy['ai.consent.a.where.body'])
                self.assertIn('Amazon Bedrock', copy['ai.consent.a.e2ee.body'])
                self.assertTrue(number(2, copy['ai.consent.a.retention.body'])
                                and number(30, copy['ai.consent.a.retention.body']))
                self.assertTrue(number(18, copy['ai.consent.a.check.age']))
                self.assertIn('PIPA', copy['ai.consent.a.region.jp'])

    def test_korean_screen_a_is_the_reconciled_spec_text(self):
        copy = self.source(APP_SOURCE)['locales']['ko']['copy']
        expected = {
            'ai.consent.a.title': 'AI 기록 도우미를 켤까요?',
            'ai.consent.a.sent.title': '무엇을 보내나요',
            'ai.consent.a.where.title': '어디서 처리하나요',
            'ai.consent.a.retention.title': '얼마나 보관하나요',
            'ai.consent.a.e2ee.title': '종단간 암호화와 달라요',
            'ai.consent.a.optional.title': '동의하지 않아도 괜찮아요',
            'ai.consent.a.check.health': '[선택] 건강정보(민감정보) 처리에 동의해요',
            'ai.consent.a.check.age': '만 18세 이상이에요',
            'ai.consent.a.later': '나중에 할게요',
            'ai.consent.a.agree': '동의하고 켜기',
            'ai.consent.b.title': '이 기록을 AI에 보낼까요?',
            'ai.consent.b.cancel': '취소',
            'ai.consent.b.send': '보내기',
        }
        for key, text in expected.items():
            with self.subTest(key=key):
                self.assertEqual(copy[key], text)
        self.assertIn('이용 횟수(내용 제외)는 최대 2개월, 동의 기록은 계정이 있는 동안 보관해요',
                      copy['ai.consent.a.retention.body'])
        self.assertIn('AWS가 운영하고, Anthropic은 내용을 볼 수 없어요', copy['ai.consent.a.where.body'])
        self.assertNotIn('메모도', copy['ai.consent.a.sent.body'])

    def test_helplines_match_the_spec_and_are_marked_not_refetched(self):
        helplines = self.source(APP_SOURCE)['helplines']
        self.assertEqual({code: (item['emergency'], item['crisis']) for code, item in helplines['regions'].items()},
                         {'KR': ('119', '109'), 'JP': ('119', '0120-279-338'), 'US': ('911', '988')})
        self.assertEqual(helplines['regions']['JP']['alternatives'], [{'number': '0570-783-556'}])
        self.assertEqual(helplines['default']['link'], 'https://findahelpline.com')
        self.assertEqual(helplines['verification']['refetchFromOfficialSources'], 'NOT_RUN')

    def test_whats_new_is_one_neutral_ai_line_without_commercial_terms(self):
        document = self.source(APP_SOURCE)
        for locale in LOCALES:
            line = document['locales'][locale]['whatsNew']
            with self.subTest(locale=locale):
                self.assert_names_feature(locale, line, "What's New")
                self.assertNotIn('\n', line)
                folded = line.casefold()
                self.assertEqual([term for term in RELEASE_NOTE_TERMS[locale] if term in folded], [])
                self.assertIsNone(TIER_WORDS.search(line), 'no tier name in release notes')
                self.assertEqual([t for t in ('Android', 'Google', 'iOS', 'Apple', 'Bedrock') if t in line], [])
                self.assertIsNone(re.search(r'\d', line), 'no number, price or cap in release notes')
        self.assertEqual(
            document['locales']['ko']['whatsNew'],
            '새 기능: AI 기록 도우미가 주간 요약, 일반 식사 아이디어, 앱 사용 도움말을 만들어요. '
            '기록은 보낼 때마다 먼저 확인해요. 이용 조건은 앱의 AI 기록 도우미 화면에서 볼 수 있어요.')

    # -- review receipts and store declarations ------------------------------------------------

    def test_locale_review_receipts_are_recorded_honestly(self):
        document = self.source(APP_SOURCE)
        expected_status = {locale: 'codex-changed-scope-self-review'
                           for locale in ('ko', 'en', 'ja')}
        for locale in LOCALES:
            path = f'{RECEIPTS}/{locale}.json'
            with self.subTest(locale=locale):
                receipt = self.source(path)
                self.assertEqual(receipt['locale'], locale)
                self.assertEqual(receipt['consentVersion'], document['consentVersion'])
                self.assertEqual(receipt['date'], document['consentVersion'].rsplit('.', 1)[0])
                self.assertIn('Codex', receipt['reviewer'])
                self.assertEqual(receipt['status'], expected_status.get(locale, 'back-translation-only'))
                self.assertIs(receipt['nativeSpeakerReview'], False)
                self.assertIs(receipt['counselReview'], False)
                copy = document['locales'][locale]['copy']
                recorded = receipt.get('backTranslation', {})
                if locale not in expected_status:
                    missing = [key for key in (*BACK_TRANSLATED_APP_KEYS, *CON_PRO_KEYS) if key not in recorded]
                    self.assertEqual(missing, [],
                                     f'{len(missing)} of {len(BACK_TRANSLATED_APP_KEYS) + len(CON_PRO_KEYS)} keys '
                                     'have no recorded back-translation (PRO-SPEC section 8, critic C23)')
                for group, keys in RECEIPT_SCOPE.items():
                    self.assertEqual(tuple(receipt['scope'].get(group, ())), keys, f'receipt scope {group}')
                reviewed = {key: copy[key] for key in APP_KEYS}
                self.assertEqual(receipt['sources']['appCopy']['sha256'], canonical_sha256(reviewed),
                                 'the app copy changed after this receipt: review it again')
                self.assertRegex(receipt['sources']['conProSharedCopy']['sha256'], r'^[0-9a-f]{64}$')
                self.assertEqual(tuple(receipt['sources']['conProSharedCopy']['keys']), CON_PRO_KEYS)
                flag = receipt['flag']
                self.assertEqual(flag['key'], f'locales.{locale}')
                if locale in ('ko', 'ja'):
                    self.assertIs(flag['recommended'], False)
                if locale not in expected_status:
                    self.assertIn('same-model', receipt['method'])
                    in_scope = [key for keys in receipt['scope'].values() for key in keys]
                    self.assertEqual([key for key in in_scope if key not in recorded], [],
                                     'a key in the declared scope has no recorded back-translation')
                    self.assertEqual(tuple(recorded), (*BACK_TRANSLATED_APP_KEYS, *CON_PRO_KEYS))
                    self.assertTrue(all(isinstance(text, str) and len(text) > 3 for text in recorded.values()))
                    for key in BACK_TRANSLATED_APP_KEYS:
                        self.assertEqual(sorted(PLACEHOLDER.findall(recorded[key])),
                                         sorted(PLACEHOLDER.findall(copy[key])), f'{key}: placeholders')
                    self.assertIs(flag['recommended'], True)
        summary = self.source('evidence/pro-legal-ai-20261002/locale-review/summary.json')
        self.assertEqual(summary['backTranslationOnly'],
                         [locale for locale in LOCALES if locale not in expected_status])
        self.assertEqual(summary['nativeSpeakerReviewed'], [])
        self.assertEqual(summary['flagsOff'], ['ko', 'ja'])
        self.assertIn('backTranslationKeyCoverage', summary,
                      'the summary must state how many keys have a recorded back-translation')
        coverage = summary['backTranslationKeyCoverage']
        self.assertEqual(coverage['locales'], summary['backTranslationOnly'])
        self.assertEqual(coverage['perLocale'], {
            'screenA': {'recorded': 22, 'total': 22}, 'screenB': {'recorded': 16, 'total': 16},
            'settingsAndPerk': {'recorded': 12, 'total': 12}, 'labels': {'recorded': 3, 'total': 3},
            'refusalTemplates': {'recorded': 12, 'total': 12}})
        self.assertEqual(coverage['appKeys'], {'recorded': 50, 'total': 50})
        self.assertEqual(coverage['missing'], {})

    def test_store_declarations_follow_the_critic_corrections(self):
        self.assertTrue((ROOT / STORE_DOC).is_file(), f'{STORE_DOC} is missing')
        text = (ROOT / STORE_DOC).read_text(encoding='utf-8')
        for required in ('HPKE', 'Not linked', 'Product Interaction', 'App interactions', '5.1.1(ix)',
                         '{REVIEWER_SIGN_IN}', 'ap-northeast-2', 'not a medical', 'Health Connect',
                         'AI-Generated Content', '2.3.12'):
            self.assertIn(required, text)
        self.assertNotIn('encrypted end-to-end between the app and our server', text,
                         'critic C22: end-to-end stays reserved for sync and backup')
        self.assertIsNone(re.search(r'[\w.+-]+@(?!wonyoungchoi\.dev)[\w-]+\.[\w.]+', text),
                          'no sandbox account or other address is written into the draft')
        self.assertIsNone(re.search(r'password\s*[:=]\s*\S', text, re.IGNORECASE))


if __name__ == '__main__':
    unittest.main()
