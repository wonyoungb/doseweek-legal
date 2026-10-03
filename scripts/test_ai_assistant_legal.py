"""Legal copy contract for the Pro "AI 기록 도우미" (lane LEGAL-AI, 2026-10-02).

PRO-SPEC section 8 (critic C18, C20, C23), sections 4.4 and 5.1-5.5, compliance sections 4.5
and 8, and the owner's second round: 150 requests a month, a 7-day trial with 50, the names
"AI 기록 도우미" and "우선 문의 답변" (never "상담").

ai-consent-v3 (2026-10-03): the processor is Google (Gemini on Google Cloud Vertex AI), the
cross-border transfer notice is shown on every storefront, and the two open owner decisions
(location us | global; AWS output Guardrail off | on) are switches whose four combinations are
all validated. Staged pages are rendered with the staging preview pair (us, off).

The staged 1.0.6 pages must carry the privacy section "AI 기록 도우미(Pro)", the Google Vertex AI
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

import ai_assistant_candidate
import ai_legal_guard
import render_account_sync

ROOT = Path(__file__).resolve().parents[1]
WEB_SOURCE = 'docs/ai-assistant-content.candidate.json'
APP_SOURCE = 'docs/ai-app-copy.candidate.json'
STORE_DOC = 'docs/AI_STORE_DECLARATIONS_1_0_6.md'
RECEIPTS = 'evidence/pro-legal-ai-v3-20261003/locale-review'
LOCALES = ('ko', 'en', 'ja', 'de', 'fr', 'es', 'it', 'nl', 'pt-PT', 'pl', 'sv', 'hi',
           'pt-BR', 'ar', 'zh-Hans', 'zh-Hant', 'tr')
CJK = ('ja', 'zh-Hans', 'zh-Hant')
SECTION = 'ai-assistant'
PROCESSOR_ROW = 'google-vertex-ai'
PREVIEW = ai_assistant_candidate.STAGING_PREVIEW_SWITCHES
COMBINATIONS = tuple((location, guardrail) for location in ('us', 'global') for guardrail in ('off', 'on'))
QUOTE = '“may be processed in any Google Cloud location around the world”'
GOOGLE_ENTITIES = ('Google Cloud Korea LLC', 'Google Asia Pacific Pte. Ltd.', 'Google LLC')
RETIRED_PROVIDER = ('Bedrock', 'Anthropic', 'Claude', 'AWS', 'Amazon', 'ap-northeast-2')
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
    'e2ee.title', 'e2ee.body', 'optional.title', 'optional.body', 'transfer.title', 'transfer.body',
    'check.health', 'check.health.detail', 'check.transfer', 'check.age', 'later', 'agree', 'region.us',
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
        # The candidate files carry switch tokens; staged pages use the staging preview pair.
        cls.web = ai_assistant_candidate.resolve(load(WEB_SOURCE), *PREVIEW)
        cls.app = ai_assistant_candidate.resolve(load(APP_SOURCE), *PREVIEW)

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
                    for token in ('Google', 'Gemini', 'Vertex AI', *GOOGLE_ENTITIES):
                        self.assertIn(token, clauses[4], f'processor clause lacks {token}')
                    self.assertEqual([t for t in RETIRED_PROVIDER if t in ''.join(clauses)], [])
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
        # every backup (R-8); counts up to 2 months, report excerpts 30 days (R-9). ai-consent-v3:
        # 90 days is Google's abuse-review log for a flagged prompt and 24 hours its memory cache
        # (FACTS.md section 2), stated in the Google sentence only.
        for locale in LOCALES:
            with self.subTest(locale=locale):
                clauses = self.ai_section(self.ios, locale)['paragraphs']
                self.assertTrue(number(2, clauses[3]) and number(30, clauses[3]), clauses[3])
                google = [part for part in sentences(clauses[3]) if number(90, part) or number(24, part)]
                self.assertTrue(google and all('Google' in part for part in google),
                                '24 hours and 90 days are stated for Google only')
        korean = self.ai_section(self.ios, 'ko')['paragraphs']
        self.assertNotIn('내가 고른 경우의 메모', korean[1])
        for item in ('증상 종류별 기록 횟수', '단백질 평균·목표', '연속 기록 주 수', '알레르기', '싫어하는 음식',
                     '언어·지역', '앱 버전'):
            self.assertIn(item, korean[1], f'clause 2 names {item} as Screen A does')
        for fact in ('DoseWeek는 대화 내용을 저장하지 않아요', '최대 2개', '최대 2개월', '계정이 있는 동안', '30일'):
            self.assertIn(fact, korean[3])

    def test_processor_table_lists_google_vertex_with_recipient_country_and_retention(self):
        for platform, document in (('ios', self.ios), ('android', self.android)):
            live = load('docs/ios-content.json' if platform == 'ios' else 'docs/android-content.candidate.json')
            for locale in LOCALES:
                with self.subTest(platform=platform, locale=locale):
                    table = sections(self.supplement(document, locale)['sections'])['processors']['table']
                    ids = [row['id'] for row in table['rows']]
                    self.assertIn(PROCESSOR_ROW, ids, 'processor table has no Google Vertex AI row')
                    self.assertNotIn('aws-bedrock', ids)
                    self.assertEqual(ids.index(PROCESSOR_ROW), ids.index('aws') + 1)
                    row = sections(table['rows'])[PROCESSOR_ROW]
                    self.assertEqual(row['role'], 'processor')
                    cells = row['cells']
                    self.assertTrue(cells['legalBasis'].startswith('Google Cloud Vertex AI (Google) — '))
                    self.assertIn(ai_assistant_candidate.US_STEMS[locale], cells['country'])
                    for token in (*GOOGLE_ENTITIES, 'https://support.google.com/cloud/contact/dpo'):
                        self.assertIn(token, cells['recipientContact'])
                    self.assertTrue('Google' in cells['retention'] and number(24, cells['retention'])
                                    and number(90, cells['retention']))
                    self.assertIn('Gemini', cells['purpose'])
                    self.assertEqual([t for t in RETIRED_PROVIDER if t in ''.join(cells.values())], [])
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
                            if 'Google' not in first_block or 'Bedrock' in first_block:
                                unqualified.append(claim[:60])
                            start = text.find(claim, start + len(claim))
                with self.subTest(source=name, locale=locale):
                    self.assertGreaterEqual(found, minimum, 'the staged text lost its sync claims')
                    self.assertEqual(unqualified, [],
                                     f'{len(unqualified)} of {found} "server cannot read" claims lack the '
                                     'AI record assistant exception (end-to-end encryption covers sync '
                                     'and backup only)')

    def test_the_exception_is_the_candidate_sentence_and_names_the_feature(self):
        candidate = self.web
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
                self.assertIn('Google Cloud Vertex AI', staged)
                self.assertNotIn('Bedrock', staged)
                self.assert_names_feature(locale, staged, 'the Android AI answer')

    def test_android_badge_and_not_used_list_no_longer_deny_generative_ai(self):
        # The 1.0.5 badge "No generative AI" and the item "Generative AI" in the list of things
        # DoseWeek does not use are false once the assistant ships in 1.0.6. The same page
        # carries the "AI 기록 도우미(Pro)" section and the Google Vertex AI row.
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
        # Google (Gemini on Google Cloud Vertex AI). PRO-SPEC 4.4 `ai.paused` links to this answer.
        live = load('docs/ios-content.json')
        candidate = self.web
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
                for token in ('Google Cloud Vertex AI', 'Gemini', 'DoseWeek', 'Private Cloud Compute'):
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
            '확인하고 보낸 내용이 DoseWeek 서버를 거쳐 Google Cloud Vertex AI(미국)로 가고, '
            'Google의 Gemini 모델이 답을 만들어요. 인터넷에 연결되어 있어야 하고, 잠시 쉬어 갈 때는 '
            '앱에서 알려 드려요. 자세한 내용은 개인정보 처리방침의 ‘AI 기록 도우미(Pro)’ 항목에 있어요.'), korean)
        english = self.ios['locales']['en']['support']['released']['ai']['answers'][0]
        self.assertTrue(english.endswith(
            'These two on-device features use no Private Cloud Compute, server model, or third-party '
            'model. The AI record assistant (Pro) is a different feature: it is processed on a server, '
            'with a third-party model. Only after your separate consent, what you confirm and send '
            'goes through the DoseWeek server to Google Cloud Vertex AI (United States), '
            'where the Gemini model by Google creates the answer. It needs an internet connection '
            'and can be paused for a while; the app tells you when that happens. The Privacy Policy '
            'describes it under “AI record assistant (Pro)”.'), english)

    def test_on_device_ai_section_scopes_its_denial_to_the_on_device_features(self):
        live = load('docs/ios-content.json')
        candidate = self.web
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
        candidate = self.web
        app = self.app
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
        candidate = self.web
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
                for token in ('Google', 'Vertex AI'):
                    self.assertIn(token, found['disclosures']['paragraphs'][0])
                self.assertNotIn('Bedrock', found['disclosures']['paragraphs'][0])
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
                    self.assertIn('Google Cloud Vertex AI (Google)', self.pages[f'{locale}/{route}index.html'])
                    self.assertNotIn('Bedrock', self.pages[f'{locale}/{route}index.html'])
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
                self.assertNotIn('Vertex AI', text)
                self.assertNotIn(SECTION, text)

    # -- candidate sources ----------------------------------------------------------------------

    def test_candidate_states_the_decided_facts_and_stays_unpublished(self):
        candidate = self.source(WEB_SOURCE)
        self.assertEqual(candidate['status'], 'pre-release-candidate-not-published')
        facts = candidate['facts']
        self.assertEqual((facts['monthlyRequests'], facts['trialDays'], facts['trialRequests'],
                          facts['minimumAge'], facts['provider'], facts['model'], facts['googleRole'],
                          facts['crossBorderTransfer'], facts['locationOptions'], facts['googleTrainsOnContent'],
                          facts['googleInMemoryCacheHours'], facts['googleAbusePromptLogDays']),
                         (150, 7, 50, 18, 'Google Cloud Vertex AI', 'gemini-3.8-flash', 'processor', True,
                          ['us', 'global'], False, 24, 90))
        self.assertEqual([key for key in facts if 'bedrock' in key.casefold() or key == 'region'], [])
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

    def test_release_gate_refuses_an_undecided_switch_even_when_every_flag_is_true(self):
        # ai-consent-v3 has two open owner decisions. Flipping every flag without choosing the
        # location and the guardrail must not publish: no combination is a silent default.
        import copy
        import tempfile
        module = importlib.import_module('ai_assistant_candidate')
        candidate = copy.deepcopy(module.load())
        self.assertIsNone(module.selection(candidate), 'the committed candidate must leave both switches open')
        candidate['status'] = 'integrated-and-verified'
        candidate['unresolvedBeforePublication'] = []
        candidate['readiness'] = {key: True for key in candidate['readiness']}
        with tempfile.TemporaryDirectory(prefix='doseweek-legal-gate-') as directory:
            candidate['legalSelfReviewEvidence'] = self._synthetic_legal_self_review_evidence(
                candidate, directory)
            with self.assertRaises(AssertionError,
                                   msg='the release gate opens while the owner switches are undecided') as failure:
                module.require_release_ready(candidate, allow_synthetic_fixture=True)
            self.assertIn('owner switches are not decided', str(failure.exception))
        for only in ('location', 'guardrail'):
            partial = copy.deepcopy(candidate)
            partial['switches'][only]['selected'] = partial['switches'][only]['options'][0]
            with self.subTest(only=only):
                self.assertIsNone(module.selection(partial), 'one decision alone is not a selection')
        self.assertEqual(candidate.get('preReleaseWording'), {locale: [] for locale in LOCALES},
                         'ai-consent-v3 carries no "not yet verified" draft sentence')
        candidate['switches']['location']['selected'] = 'us'
        candidate['switches']['guardrail']['selected'] = 'off'
        with tempfile.TemporaryDirectory(prefix='doseweek-legal-gate-') as directory:
            candidate['legalSelfReviewEvidence'] = self._synthetic_legal_self_review_evidence(
                candidate, directory)
            module.require_release_ready(candidate, allow_synthetic_fixture=True)

    def _synthetic_legal_self_review_evidence(self, candidate, directory):
        # A test receipt is never evidence of counsel/native review or product readiness.
        scope = ('schemaVersion', 'plannedVersion', 'facts', 'switches', 'localeOrder',
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
            self.test_release_gate_refuses_an_undecided_switch_even_when_every_flag_is_true()
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
            # Every factual flag and both switch selections are valid in this fixture, so
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

    def test_open_owner_decisions_and_unverified_google_facts_are_recorded_as_blockers(self):
        unresolved = self.source(WEB_SOURCE)['unresolvedBeforePublication']
        self.assertEqual([item for item in unresolved if 'Bedrock' in item], [])
        for tokens in (('SWITCH_LOCATION', 'us or global'),
                       ('SWITCH_AWS_GUARDRAIL', 'off or on'),
                       ('googleContractingEntityVerified', 'Google Cloud Korea LLC', 'billing'),
                       ('vertexCacheSettingReadback', '24 hours', '90 days', 'zero data retention'),
                       ('28-8(2)2', 'global', 'pipaCountryItemForGlobalAccepted'),
                       ('28-8(2)2', 'location us', 'NOT_RETRIEVED'),
                       ('APPI Rule 17(2)', 'Singapore', 'Q12-11', 'Rule 17(2)3'),
                       ('DoseWeek server location', 'not read back'),
                       ('serverRegistry.guardrailLocales', 'awsGuardrailEntityAndProcessorRowVerified'),
                       ('no native-speaker review', '17 locales'),
                       ('ai.consent.a.check.transfer', 'server registry'),
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
        self.assertEqual((document['consentVersion'], document['wireConsentVersion']),
                         ('2026-10-03.3', 'ai-consent-v3'))
        self.assertNotIn('ai.consent.a.region.jp', document['keys'],
                         'v3 shows the transfer notice on every storefront, not as a Japan-only paragraph')
        self.assertIn('EVERY storefront', document['screens']['A'])
        document = self.app
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
                for token in ('Google', 'Gemini', 'Vertex AI', 'DoseWeek'):
                    self.assertIn(token, copy['ai.consent.a.where.body'])
                self.assertIn('Google', copy['ai.consent.a.e2ee.body'])
                self.assertEqual([t for t in RETIRED_PROVIDER if t in '\n'.join(copy.values())], [])
                self.assertTrue(number(2, copy['ai.consent.a.retention.body'])
                                and number(30, copy['ai.consent.a.retention.body']))
                self.assertTrue(number(18, copy['ai.consent.a.check.age']))
                transfer = copy['ai.consent.a.transfer.body']
                for token in ('PIPA', *GOOGLE_ENTITIES, 'https://support.google.com/cloud/contact/dpo',
                              ai_assistant_candidate.US_STEMS[locale], 'APEC'):
                    self.assertIn(token, transfer, f'transfer notice lacks {token}')
                self.assertIn('Google', copy['ai.consent.a.check.transfer'])

    def test_korean_screen_a_is_the_reconciled_spec_text(self):
        copy = self.app['locales']['ko']['copy']
        expected = {
            'ai.consent.a.title': 'AI 기록 도우미를 켤까요?',
            'ai.consent.a.sent.title': '무엇을 보내나요',
            'ai.consent.a.where.title': '어디서 처리하나요',
            'ai.consent.a.retention.title': '얼마나 보관하나요',
            'ai.consent.a.e2ee.title': '종단간 암호화와 달라요',
            'ai.consent.a.optional.title': '동의하지 않아도 괜찮아요',
            'ai.consent.a.check.health': '[선택] 건강정보(민감정보) 처리에 동의해요',
            'ai.consent.a.transfer.title': '개인정보 국외 이전',
            'ai.consent.a.check.transfer': '[선택] 위 내용대로 개인정보를 Google에 국외 이전하는 데 동의해요',
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
        self.assertEqual(
            copy['ai.consent.a.where.body'],
            '앱에서 한 번 더 암호화해 DoseWeek 서버(대한민국 서울)로 보내요. 서버는 이 내용을 Google Cloud의 Vertex AI로 '
            '전달하고, Google의 AI 모델인 Gemini가 답을 만들어요. Google은 이 내용의 AI 처리와 저장을 미국에서 해요.')
        self.assertIn('Google은 응답 속도를 높이려고 이 내용을 메모리에 최대 24시간 둘 수 있고, Google의 자동 악용 탐지에서 '
                      '의심되는 요청은 최대 90일 보관할 수 있어요. 이런 요청은 권한이 있는 Google 직원이 검토할 수 있어요. '
                      'DoseWeek는 대화 내용을 저장하지 않아요.', copy['ai.consent.a.retention.body'])
        self.assertNotIn('바로 삭제', copy['ai.consent.a.check.health.detail'],
                         'Google does not delete at once: 24-hour memory cache, 90-day abuse log')
        for item in ('이전받는 자:', '이전되는 국가: 미국', '이전 항목:', '이전 시기와 방법:', '이용 목적과 보유 기간:',
                     '거부 방법과 효과:'):
            self.assertIn(item, copy['ai.consent.a.transfer.body'], 'PIPA 28-8(2) notice item')
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
        # ai-consent-v3: one AI model wrote the changed strings; nobody reviewed them. The receipts
        # must say exactly that, pin the text, and recommend no locale.
        document = self.source(APP_SOURCE)
        apply = self.source('docs/ai-consent-v3-apply.json')
        changed = ['ai.consent.a.where.body', 'ai.consent.a.retention.body', 'ai.consent.a.e2ee.body',
                   'ai.consent.a.transfer.title', 'ai.consent.a.transfer.body',
                   'ai.consent.a.check.health.detail', 'ai.consent.a.check.transfer',
                   'ai.consent.b.processing', 'ai.help.inputNote']
        for locale in LOCALES:
            with self.subTest(locale=locale):
                receipt = self.source(f'{RECEIPTS}/{locale}.json')
                self.assertEqual(receipt['locale'], locale)
                self.assertEqual((receipt['consentVersion'], receipt['wireConsentVersion']),
                                 (document['consentVersion'], document['wireConsentVersion']))
                self.assertEqual(receipt['date'], document['consentVersion'].rsplit('.', 1)[0])
                self.assertEqual(receipt['status'], 'same-model-authoring-no-review')
                self.assertIn('not a human', receipt['reviewer'])
                self.assertIn('No back-translation', receipt['method'])
                self.assertIs(receipt['nativeSpeakerReview'], False)
                self.assertIs(receipt['counselReview'], False)
                self.assertEqual(receipt['backTranslation'], 'NOT_RUN for the changed and new keys')
                entry = document['locales'][locale]
                self.assertEqual(receipt['sources']['appCopyTemplate']['sha256'],
                                 canonical_sha256({'copy': {key: entry['copy'][key] for key in APP_KEYS},
                                                   'switchText': entry['switchText']}),
                                 'the app copy changed after this receipt: write the receipts again')
                self.assertEqual(receipt['changedOrNewKeys'], changed)
                self.assertEqual(receipt['unchangedFromV2']['count'], len(APP_KEYS) - len(changed))
                self.assertEqual(receipt['unchangedFromV2']['retiredV2Keys'], ['ai.consent.a.region.jp'])
                self.assertEqual(list(receipt['sources']['combinations']), ['us-off', 'us-on', 'global-off', 'global-on'])
                for name, block in receipt['sources']['combinations'].items():
                    self.assertEqual(block, apply['combinations'][name]['locales'][locale])
                self.assertEqual(receipt['flag'], {'key': f'locales.{locale}', 'recommended': False,
                                                   'condition': receipt['flag']['condition']})
        summary = self.source(f'{RECEIPTS}/summary.json')
        self.assertEqual(summary['flagsOff'], list(LOCALES))
        self.assertEqual((summary['backTranslated'], summary['nativeSpeakerReviewed'], summary['counselReviewed']),
                         ([], [], []))
        self.assertEqual(summary['changedOrNewKeys'], changed)

    def test_store_declarations_follow_the_critic_corrections(self):
        self.assertTrue((ROOT / STORE_DOC).is_file(), f'{STORE_DOC} is missing')
        text = (ROOT / STORE_DOC).read_text(encoding='utf-8')
        for required in ('HPKE', 'Not linked', 'Product Interaction', 'App interactions', '5.1.1(ix)',
                         '{REVIEWER_SIGN_IN}', 'Google Cloud Vertex AI', 'Gemini', 'Google Cloud Korea LLC',
                         'SWITCH_LOCATION', 'SWITCH_AWS_GUARDRAIL', '24 hours', '90 days',
                         'not a medical', 'Health Connect', 'AI-Generated Content', '2.3.12'):
            self.assertIn(required, text)
        for retired in ('Bedrock', 'Anthropic', 'Claude', 'ap-northeast-2', 'retention mode "none"',
                        'no storage, no training'):
            self.assertNotIn(retired, text, 'the store drafts still describe the v2 provider')
        self.assertNotIn('encrypted end-to-end between the app and our server', text,
                         'critic C22: end-to-end stays reserved for sync and backup')
        self.assertIsNone(re.search(r'[\w.+-]+@(?!wonyoungchoi\.dev)[\w-]+\.[\w.]+', text),
                          'no sandbox account or other address is written into the draft')
        self.assertIsNone(re.search(r'password\s*[:=]\s*\S', text, re.IGNORECASE))

    # -- ai-consent-v3: Google, every storefront, two owner switches ----------------------------

    def test_all_four_switch_combinations_resolve_to_complete_text_in_17_locales(self):
        module = ai_assistant_candidate
        web, app = module.load(), module.load_app_copy()
        seen = {}
        for location, guardrail in COMBINATIONS:
            resolved_web = module.resolve(web, location, guardrail)
            resolved_app = module.resolve(app, location, guardrail)
            self.assertEqual(resolved_app['resolvedSwitches'], {'location': location, 'guardrail': guardrail})
            for locale in LOCALES:
                with self.subTest(location=location, guardrail=guardrail, locale=locale):
                    entry, copy = resolved_web['locales'][locale], resolved_app['locales'][locale]['copy']
                    self.assertNotIn('switchText', entry)
                    texts = [*strings(entry), *copy.values()]
                    joined = '\n'.join(texts)
                    self.assertEqual(re.findall(r'\{ai[A-Za-z]+\}', joined), [], 'a switch token is left')
                    sentence = web['locales'][locale]['switchText']['aiGuardrail']['on']
                    self.assertIn('Amazon Web Services', sentence)
                    self.assertEqual(joined.count(sentence), 3 if guardrail == 'on' else 0,
                                     'guardrail on adds one sentence to Screen A, the processor clause and '
                                     'the processor row; off adds none')
                    without = joined.replace(sentence, '')
                    self.assertEqual([t for t in RETIRED_PROVIDER if t in without], [],
                                     'AWS, Bedrock, Claude or the Seoul Region is still named as the AI processor')
                    country = module.US_STEMS[locale]
                    for text in (copy['ai.consent.a.where.body'], copy['ai.consent.a.transfer.body'],
                                 entry['clauses'][4], entry['clauses'][5], entry['processorRow']['country']):
                        if location == 'us':
                            self.assertIn(country, text)
                            self.assertNotIn(QUOTE, text)
                        else:
                            self.assertIn(QUOTE, text, 'location global quotes Google\'s own statement')
                    self.assertEqual(QUOTE in joined, location == 'global')
                    self.assertEqual('https://cloud.google.com/about/locations' in joined, location == 'global')
                    for token in (*GOOGLE_ENTITIES, 'https://support.google.com/cloud/contact/dpo'):
                        self.assertIn(token, copy['ai.consent.a.transfer.body'])
                        self.assertIn(token, entry['clauses'][4])
                    seen.setdefault(locale, set()).add(canonical_sha256(copy))
        self.assertEqual({locale: len(hashes) for locale, hashes in seen.items()},
                         {locale: 4 for locale in LOCALES}, 'the four combinations are four different texts')

    def test_retention_and_training_statements_match_the_google_facts(self):
        # FACTS.md section 2: no training; in-memory cache up to 24 hours; a prompt flagged by abuse
        # monitoring up to 90 days. "Deleted as soon as the answer is made" is not true for Google.
        self.assertEqual(sentences(self.web['locales']['en']['clauses'][3])[:3], [
            'Retention: The DoseWeek server does not keep what you send or the answers.',
            'Google does not use what you send or the answers to train AI models.',
            'To speed up responses, Google may hold this content in memory for up to 24 hours, and if '
            'Google’s automated abuse checks flag a request, Google may store that request for up to 90 days, '
            'and authorized Google staff may review it.'])
        english = '\n'.join([*strings(self.web['locales']['en']), *self.app['locales']['en']['copy'].values()])
        for stale in ('deleted as soon as the answer is made', 'set not to store', 'no-storage setting',
                      'not sent to a Region in another country', 'not sent to another country',
                      'Seoul Region'):
            self.assertNotIn(stale, english)
        korean = '\n'.join([*strings(self.web['locales']['ko']), *self.app['locales']['ko']['copy'].values()])
        for stale in ('답을 만든 뒤 바로 지워요', '바로 삭제', '서울 리전', '다른 나라의 리전으로 보내지 않아요'):
            self.assertNotIn(stale, korean)
        for locale in LOCALES:
            with self.subTest(locale=locale):
                copy = self.app['locales'][locale]['copy']
                for key in ('ai.consent.a.retention.body', 'ai.consent.a.check.health.detail'):
                    self.assertTrue('Google' in copy[key] and number(24, copy[key]) and number(90, copy[key]), key)
                self.assertTrue(number(24, self.web['locales'][locale]['deletion'])
                                and number(90, self.web['locales'][locale]['deletion']))

    def test_validators_reject_leftover_v2_claims_and_wrong_switch_text(self):
        import copy as copying
        module = ai_assistant_candidate
        web, app = module.load(), module.load_app_copy()
        pins = ai_legal_guard.read_pins()

        def web_fails(location, guardrail, change, message):
            resolved = module.resolve(web, location, guardrail)
            change(resolved['locales']['en'])
            with self.assertRaises(AssertionError, msg=message):
                module._check_web(resolved, web, location, guardrail, pins)

        def app_fails(location, guardrail, change, message):
            resolved = module.resolve(app, location, guardrail)
            change(resolved['locales']['en']['copy'])
            with self.assertRaises(AssertionError, msg=message):
                module._check_app(resolved, app, location, guardrail, pins)

        guard = web['locales']['en']['switchText']['aiGuardrail']['on']
        for location, guardrail in COMBINATIONS:
            module._check_web(module.resolve(web, location, guardrail), web, location, guardrail, pins)
            module._check_app(module.resolve(app, location, guardrail), app, location, guardrail, pins)
        for token in ('Amazon Bedrock', 'Anthropic', 'Claude', 'AWS', 'ap-northeast-2'):
            for guardrail in ('off', 'on'):
                with self.subTest(token=token, guardrail=guardrail):
                    web_fails('us', guardrail, lambda e: e['clauses'].__setitem__(6, e['clauses'][6] + ' ' + token),
                              f'the website copy accepts {token}')
                    app_fails('us', guardrail,
                              lambda c: c.__setitem__('ai.consent.b.processing', c['ai.consent.b.processing'] + ' ' + token),
                              f'the app copy accepts {token}')
        with self.subTest(case='guardrail sentence while the switch is off'):
            app_fails('us', 'off', lambda c: c.__setitem__('ai.consent.a.where.body',
                                                           c['ai.consent.a.where.body'] + ' ' + guard),
                      'Amazon Web Services is named although the guardrail switch is off')
            web_fails('global', 'off', lambda e: e['clauses'].__setitem__(4, e['clauses'][4] + ' ' + guard),
                      'Amazon Web Services is named although the guardrail switch is off')
        with self.subTest(case='guardrail sentence missing while the switch is on'):
            app_fails('us', 'on', lambda c: c.__setitem__('ai.consent.a.where.body',
                                                          c['ai.consent.a.where.body'].replace(guard, '').strip()),
                      'the guardrail switch is on but Screen A does not say so')
        with self.subTest(case='global quote under location us'):
            app_fails('us', 'off', lambda c: c.__setitem__('ai.consent.a.transfer.body',
                                                           c['ai.consent.a.transfer.body'] + ' ' + QUOTE),
                      'location us must not carry the global statement')
        with self.subTest(case='no quote under location global'):
            app_fails('global', 'off', lambda c: c.__setitem__('ai.consent.a.where.body',
                                                               c['ai.consent.a.where.body'].replace(QUOTE, 'x')),
                      'location global must quote Google')
        for token in (*GOOGLE_ENTITIES, 'https://support.google.com/cloud/contact/dpo', 'PIPA'):
            with self.subTest(case='transfer notice without', token=token):
                app_fails('us', 'off', lambda c: c.__setitem__('ai.consent.a.transfer.body',
                                                               c['ai.consent.a.transfer.body'].replace(token, 'x')),
                          f'the transfer notice may omit {token}')
        with self.subTest(case='Google retention figures'):
            app_fails('us', 'off', lambda c: c.__setitem__('ai.consent.a.retention.body',
                                                           c['ai.consent.a.retention.body'].replace('90', '9')),
                      'Screen A may drop the 90-day abuse log')
            web_fails('us', 'off', lambda e: e['processorRow'].__setitem__('retention', 'Not retained.'),
                      'the processor row may claim that Google retains nothing')
        with self.subTest(case='unresolved token'):
            broken = copying.deepcopy(module.resolve(app, 'us', 'off'))
            broken['locales']['en']['copy']['ai.help.inputNote'] += ' {aiLocation}'
            with self.assertRaises(AssertionError):
                module._check_app(broken, app, 'us', 'off', pins)

    def test_transfer_notice_and_its_consent_box_are_on_screen_a_for_every_storefront(self):
        module = ai_assistant_candidate
        for locale in LOCALES:
            copy = self.app['locales'][locale]['copy']
            for platform in ('ios', 'android'):
                default = module.screen_a_strings(copy, platform, 'default')
                us = module.screen_a_strings(copy, platform, 'US')
                with self.subTest(locale=locale, platform=platform):
                    for key in ('ai.consent.a.transfer.title', 'ai.consent.a.transfer.body',
                                'ai.consent.a.check.transfer'):
                        self.assertIn(copy[key], default, f'{key} is not shown on a non-US, non-JP storefront')
                    self.assertEqual(len(us), len(default) + 1)
                    self.assertLess(default.index(copy['ai.consent.a.transfer.body']),
                                    default.index(copy['ai.consent.a.check.transfer']),
                                    'the notice is read before the box')
                    self.assertEqual(default.index(copy['ai.consent.a.check.transfer']),
                                     default.index(copy['ai.consent.a.check.health.detail']) + 1,
                                     'the transfer consent is its own box, separate from the health box')
                    self.assertEqual(module.screen_a_hash(copy, platform, 'default'),
                                     hashlib.sha256('\n'.join(default).encode('utf-8')).hexdigest())

    def test_apply_list_and_hashes_are_current_for_the_four_combinations(self):
        import ai_consent_apply
        committed = self.source('docs/ai-consent-v3-apply.json')
        self.assertEqual(committed, json.loads(json.dumps(ai_consent_apply.build())),
                         'docs/ai-consent-v3-apply.json is stale: run python3 scripts/ai_consent_apply.py')
        self.assertEqual(list(committed['combinations']), ['us-off', 'us-on', 'global-off', 'global-on'])
        self.assertEqual(committed['ownerSwitches']['selected'], None)
        self.assertEqual((committed['consentVersion'], committed['wireConsentVersion']),
                         ('2026-10-03.3', 'ai-consent-v3'))
        every = []
        for name, block in committed['combinations'].items():
            registry = block['serverRegistry']
            self.assertEqual(registry['current'], {locale: 'ai-consent-v3' for locale in LOCALES})
            self.assertEqual(registry['recipients'],
                             {'ai-consent-v3': 'google-vertex-us' if block['location'] == 'us' else 'google-vertex-global'})
            for locale in LOCALES:
                hashes = registry['texts']['ai-consent-v3'][locale]
                with self.subTest(combination=name, locale=locale):
                    self.assertEqual(hashes, list(block['locales'][locale]['screenA'].values()))
                    self.assertEqual(len(set(hashes)), 4)
                    self.assertTrue(all(re.fullmatch(r'[0-9a-f]{64}', value) for value in hashes))
                    self.assertLessEqual(len(hashes), 6, 'server MAX_DISPLAY_VARIANTS')
                every += hashes
        self.assertEqual(len(set(every)), 4 * 17 * 4, 'no display hash is shared between combinations or locales')
        for platform, files in (('ios', ('Localizable.xcstrings', 'AIAssistWire.swift', 'AIConsentSheet.swift')),
                                ('android', ('ai_assistant_screens.xml', 'AiConsentPolicy.kt', 'AiAssistScreens.kt'))):
            steps = '\n'.join(committed['apply'][platform])
            for name in files:
                self.assertIn(name, steps)
        self.assertEqual(committed['keys']['androidNames']['ai.consent.a.check.health.detail'],
                         'ai_consent_a_check_health_detail')
        self.assertEqual(committed['keys']['androidNames']['ai.help.inputNote'], 'ai_help_input_note')

    # -- review round 2: semantic guards, purpose, subjects, scope, gates -------------------------

    def _reviewer_mutations(self):
        """The eight copy changes the round-1 reviewer got past the token validators (finding F1)."""
        labels = ai_legal_guard.read_pins()['pipaItemLabels']

        def append(locale, key, text):
            return lambda app: app['locales'][locale]['copy'].__setitem__(
                key, app['locales'][locale]['copy'][key] + text)

        def replace(locale, key, old, new):
            def change(app):
                copy = app['locales'][locale]['copy']
                assert old in copy[key], (locale, key, old)
                copy[key] = copy[key].replace(old, new, 1)
            return change

        def cut(locale, start, stop):
            def change(app):
                copy = app['locales'][locale]['copy']
                text = copy['ai.consent.a.transfer.body']
                begin, end = text.index(start), text.index(stop)
                assert 0 <= begin < end
                copy['ai.consent.a.transfer.body'] = text[:begin] + text[end:]
            return change

        retention, where = 'ai.consent.a.retention.body', 'ai.consent.a.where.body'
        return {
            'a: en adds "deleted as soon as the answer is made, never stored"': append(
                'en', retention, ' Google deletes your content as soon as the answer is made and never stores it.'),
            'b: ko adds "only in the Seoul Region, not sent to another country"': append(
                'ko', where, ' 서울 리전에서만 하고 다른 나라로 보내지 않아요.'),
            'c: en "does not use" becomes "uses" for training': replace(
                'en', retention, 'Google does not use what you send', 'Google uses what you send'),
            'd: de drops the first "nicht"': replace('de', retention, ' nicht zum Training', ' zum Training'),
            'e: fr retention reduced to bare figures': lambda app: app['locales']['fr']['copy'].__setitem__(
                retention, 'Google 24 90 2 30.'),
            'f: ja deletes the refusal item': cut('ja', labels['ja'][5], 'DoseWeekは大韓民国で'),
            'g: ko deletes the purpose and retention item': cut('ko', labels['ko'][4], labels['ko'][5]),
            'h: ko names the retired provider in Hangul': append(
                'ko', where, ' 아마존 베드록의 클로드가 서울에서 처리해요.'),
        }

    def test_reviewer_mutations_fail_the_validator_even_after_a_re_pin(self):
        # F1: before round 2 every one of these passed load_app_copy(). A hash pin alone would only
        # detect a change, and regenerating it would accept the wrong text. So each mutation is
        # replayed twice: against the committed pins, and against pins whose hashes were computed
        # from the mutated copy. The second run can fail only on the hand-written guards (exact
        # sentences, notice items, forbidden claims).
        import copy as copying
        module = ai_assistant_candidate
        web, app = self.source(WEB_SOURCE), self.source(APP_SOURCE)
        pins = ai_legal_guard.read_pins()
        module.validate_app(copying.deepcopy(app), web, pins)
        module.validate_app(copying.deepcopy(app), web, ai_legal_guard.with_hashes(pins, web, app))
        mutations = self._reviewer_mutations()
        self.assertEqual(len(mutations), 8)
        for name, change in mutations.items():
            with self.subTest(mutation=name):
                mutated = copying.deepcopy(app)
                change(mutated)
                self.assertNotEqual(mutated, app)
                with self.assertRaises(AssertionError, msg=f'committed pins accept {name}'):
                    module.validate_app(mutated, web, pins)
                repinned = ai_legal_guard.with_hashes(pins, web, mutated)
                with self.assertRaises(AssertionError, msg=f'a re-pin accepts {name}') as failure:
                    module.validate_app(mutated, web, repinned)
                self.assertNotIn('--repin', str(failure.exception),
                                 'the mutation must fail on a semantic guard, not on the hash')

    def test_website_copy_has_the_same_semantic_guards(self):
        import copy as copying
        module = ai_assistant_candidate
        web, app = self.source(WEB_SOURCE), self.source(APP_SOURCE)
        pins = ai_legal_guard.read_pins()
        module.validate_web(copying.deepcopy(web), pins)

        def english(change):
            return lambda document: change(document['locales']['en'])

        def korean(change):
            return lambda document: change(document['locales']['ko'])

        cases = {
            'clause 4 adds a never-stored claim': english(lambda e: e['clauses'].__setitem__(
                3, e['clauses'][3] + ' Google never stores your content.')),
            'retention cell drops the negation': english(lambda e: e['processorRow'].__setitem__(
                'retention', e['processorRow']['retention'].replace('does not use', 'uses'))),
            'deletion paragraph loses the Google sentences': english(lambda e: e.__setitem__(
                'deletion', e['deletion'].split(' Google does not use')[0] + ' Google 24 90.')),
            'purpose cell says only': english(lambda e: e['processorRow'].__setitem__(
                'purpose', 'Processor that only creates the AI answers you request.{0}'.format(''))),
            'exception sentence loses the holding period': english(lambda e: e.__setitem__(
                'e2eeException', e['e2eeException'].split(' Google can also read')[0])),
            'Korean clause names the retired provider in Hangul': korean(lambda e: e['clauses'].__setitem__(
                4, e['clauses'][4] + ' 아마존 베드록에서 처리해요.')),
            'Korean clause claims the Seoul Region': korean(lambda e: e['clauses'].__setitem__(
                5, e['clauses'][5] + ' 서울 리전에서만 처리해요.')),
        }
        for name, change in cases.items():
            with self.subTest(case=name):
                mutated = copying.deepcopy(web)
                change(mutated)
                with self.assertRaises(AssertionError):
                    module.validate_web(mutated, pins)
                with self.assertRaises(AssertionError) as failure:
                    module.validate_web(mutated, ai_legal_guard.with_hashes(pins, mutated, app))
                self.assertNotIn('--repin', str(failure.exception))

    def test_every_locale_guards_negation_notice_items_and_native_script_names(self):
        import copy as copying
        module = ai_assistant_candidate
        web, app = self.source(WEB_SOURCE), self.source(APP_SOURCE)
        pins = ai_legal_guard.read_pins()
        retention, transfer = 'ai.consent.a.retention.body', 'ai.consent.a.transfer.body'
        names = pins['forbiddenClaims']['everyLocale']
        for word in ('아마존', '베드록', '클로드', 'アマゾン', '亚马逊', '亞馬遜', 'अमेज़न', 'أمازون'):
            self.assertIn(word, names)
        for index, locale in enumerate(LOCALES):
            sentences_ = pins['requiredSentences'][locale]
            labels = pins['pipaItemLabels'][locale]
            copy = app['locales'][locale]['copy']
            self.assertEqual(copy[retention].count(sentences_['googleNoTraining']), 1)

            def without_training(document, locale=locale, sentences_=sentences_):
                text = document['locales'][locale]['copy'][retention]
                document['locales'][locale]['copy'][retention] = ' '.join(
                    text.replace(sentences_['googleNoTraining'], '').split())

            def without_item(document, locale=locale, labels=labels, item=index % 4 + 2):
                text = document['locales'][locale]['copy'][transfer]
                begin, end = text.index(labels[item]), text.index(labels[item + 1]) if item < 5 else len(text)
                document['locales'][locale]['copy'][transfer] = text[:begin] + text[end:]

            def native_name(document, locale=locale, word=names[index % 22]):
                document['locales'][locale]['copy'][retention] += ' ' + word

            for case, change in (('no-training sentence removed', without_training),
                                 ('a notice item removed', without_item),
                                 ('a retired provider in a non-Latin script', native_name)):
                with self.subTest(locale=locale, case=case):
                    mutated = copying.deepcopy(app)
                    change(mutated)
                    with self.assertRaises(AssertionError) as failure:
                        module.validate_app(mutated, web, ai_legal_guard.with_hashes(pins, web, mutated))
                    self.assertNotIn('--repin', str(failure.exception))

    def test_forbidden_claims_are_searched_in_every_app_key_not_only_the_pinned_ones(self):
        import copy as copying
        module = ai_assistant_candidate
        web, app = self.source(WEB_SOURCE), self.source(APP_SOURCE)
        pins = ai_legal_guard.read_pins()
        unpinned = [key for key in APP_KEYS if key not in ai_legal_guard.app_fields(app['locales']['ko']['copy'])]
        self.assertIn('ai.settings.withdraw.note', unpinned)
        for locale, key, text in (('ko', 'ai.settings.withdraw.note', ' 아마존 베드록에서 처리해요.'),
                                  ('ja', 'ai.consent.b.preview', ' アマゾンのクロードが処理します。'),
                                  ('en', 'pro.support.priority', ' Google never stores your content.'),
                                  ('zh-Hans', 'ai.settings.usage', ' 亚马逊会立即删除。')):
            with self.subTest(locale=locale, key=key):
                self.assertIn(key, unpinned)
                mutated = copying.deepcopy(app)
                mutated['locales'][locale]['copy'][key] += text
                # An unpinned key does not change the hashes, so only the forbidden list can fail.
                self.assertEqual(ai_legal_guard.with_hashes(pins, web, mutated)['combinationSha256'],
                                 pins['combinationSha256'])
                with self.assertRaises(AssertionError) as failure:
                    module.validate_app(mutated, web, pins)
                self.assertIn('forbidden claim or retired name', str(failure.exception))

    def test_hash_pins_catch_any_other_change_to_a_pinned_field_until_it_is_re_pinned(self):
        # What the hashes are for, and their limit: a change no hand-written guard knows about is
        # detected, and it is accepted again after a re-pin. That is why --repin is a review step.
        import copy as copying
        module = ai_assistant_candidate
        web, app = self.source(WEB_SOURCE), self.source(APP_SOURCE)
        pins = ai_legal_guard.read_pins()
        self.assertEqual(ai_legal_guard.changed_fields(pins, web, app), [],
                         'pinned legal text changed: read it against the sources, then ai_legal_guard.py --repin')
        self.assertEqual(pins['consentVersion'], app['consentVersion'])
        mutated = copying.deepcopy(app)
        mutated['locales']['sv']['copy']['ai.consent.a.optional.body'] += ' Tack.'
        with self.assertRaises(AssertionError) as failure:
            module.validate_app(mutated, web, pins)
        self.assertIn('--repin', str(failure.exception))
        self.assertEqual(ai_legal_guard.changed_fields(pins, web, mutated), ['sv:app:ai.consent.a.optional.body'])
        module.validate_app(mutated, web, ai_legal_guard.with_hashes(pins, web, mutated))
        self.assertEqual(list(pins['combinationSha256']), ['us-off', 'us-on', 'global-off', 'global-on'])
        for name, block in pins['combinationSha256'].items():
            self.assertEqual(list(block), list(LOCALES))
        self.assertEqual(len({value for block in pins['combinationSha256'].values()
                              for entry in block.values() for value in entry.values()}), 4 * 17 * 2)

    def test_purpose_item_states_the_two_further_google_uses_and_never_says_only(self):
        # F2: Google also caches for speed (24 hours, in memory) and logs flagged prompts for abuse
        # review (90 days, authorized staff). "Only to create the answer" overstated the purpose.
        pins = ai_legal_guard.read_pins()
        for locale in LOCALES:
            copy = self.app['locales'][locale]['copy']
            entry = self.web['locales'][locale]
            sentences_ = pins['requiredSentences'][locale]
            with self.subTest(locale=locale):
                items = ai_legal_guard.pipa_items(locale, copy['ai.consent.a.transfer.body'], pins, locale)
                purpose = items['purposeAndRetention']
                self.assertTrue(purpose.startswith(sentences_['googleUse']))
                self.assertTrue(purpose.endswith(sentences_['googleCacheAndAbuse']))
                self.assertTrue(number(24, purpose) and number(90, purpose) and purpose.count('Google') >= 3)
                self.assertIn(sentences_['googleCacheAndAbuse'], entry['processorRow']['purpose'])
        stale = {'en': ('only to create', 'Not used for AI training or advertising'),
                 'ko': ('만드는 데에만', '광고에는 쓰지 않아요'), 'ja': ('ためだけに', '目的でのみ'),
                 'de': ('nur zur Erstellung', 'ausschließlich zur Erstellung'), 'fr': ('uniquement pour créer',),
                 'es': ('solo para crear',), 'it': ('solo per creare',), 'nl': ('alleen om de AI-antwoorden',
                                                                              'alleen om het antwoord'),
                 'pt-PT': ('apenas para criar',), 'pt-BR': ('apenas para criar',), 'pl': ('wyłącznie tworzenie',
                                                                                      'wyłącznie w celu'),
                 'sv': ('bara för att skapa', 'enbart för att skapa'), 'hi': ('सिर्फ़ आपके माँगे हुए', 'सिर्फ़ जवाब बनाने'),
                 'ar': ('التي تطلبها فقط', 'لإنشاء الإجابة فقط'), 'zh-Hans': ('仅用于生成',), 'zh-Hant': ('僅用於產生',),
                 'tr': ('yalnızca istediğiniz', 'yalnızca yanıtı')}
        self.assertEqual(sorted(stale), sorted(LOCALES))
        for locale, phrases in stale.items():
            text = '\n'.join([*strings(self.web['locales'][locale]), *self.app['locales'][locale]['copy'].values()])
            with self.subTest(locale=locale, check='no only'):
                self.assertEqual([phrase for phrase in phrases if phrase in text], [])

    def test_conversations_sentence_names_doseweek_and_google_reading_covers_the_holding_period(self):
        # F3: "Conversations are not saved" right after two Google sentences read as a Google
        # claim. F4: Google can read the content for as long as it holds it, and authorized staff
        # may review a flagged request; "while the answer is being made" alone understated that.
        pins = ai_legal_guard.read_pins()
        for locale in LOCALES:
            sentences_ = pins['requiredSentences'][locale]
            copy, entry = self.app['locales'][locale]['copy'], self.web['locales'][locale]
            with self.subTest(locale=locale):
                self.assertIn('DoseWeek', sentences_['doseweekNoConversations'])
                self.assertNotIn('Google', sentences_['doseweekNoConversations'])
                for text in (copy['ai.consent.a.retention.body'], entry['clauses'][3]):
                    self.assertIn(sentences_['googleCacheAndAbuse'] + ai_legal_guard.separator(locale)
                                  + sentences_['doseweekNoConversations'], text)
                held = sentences_['googleReadsWhileHeld']
                self.assertTrue(number(24, held) and number(90, held) and held.count('Google') >= 2, held)
                for text in (copy['ai.consent.a.e2ee.body'], entry['clauses'][7], entry['e2eeException'],
                             entry['usHealth']['categories']):
                    self.assertEqual(text.count(held), 1)
        english = pins['requiredSentences']['en']
        self.assertIn('authorized Google staff may review it', english['googleCacheAndAbuse'])
        self.assertIn('authorized Google staff may then review', english['googleReadsWhileHeld'])
        self.assertEqual(english['doseweekNoConversations'], 'DoseWeek does not save your conversations.')
        self.assertIn('권한이 있는 Google 직원이 검토할 수 있어요', pins['requiredSentences']['ko']['googleCacheAndAbuse'])
        self.assertIn('権限のあるGoogleの担当者が確認することがあります', pins['requiredSentences']['ja']['googleCacheAndAbuse'])
        japanese = self.app['locales']['ja']['copy']['ai.consent.a.check.health.detail']
        self.assertIn('保持されることがあり', japanese, 'F6: ja states the Google retention as a possibility, like ko and en')
        self.assertNotIn('最大90日間保存します', japanese)

    def test_us_text_states_the_scope_of_the_commitment_and_both_texts_describe_singapore(self):
        # F5: Google's commitment for the us multi-region covers storage at rest and ML processing;
        # other processing may happen wherever Google or its subprocessors have facilities.
        # APPI Rule 17(2) with PPC Q12-11: the country is where the recipient is located.
        module = ai_assistant_candidate
        pins = ai_legal_guard.read_pins()
        app = self.source(APP_SOURCE)
        for locale in LOCALES:
            switch = app['locales'][locale]['switchText']
            sentences_ = pins['requiredSentences'][locale]
            with self.subTest(locale=locale):
                self.assertEqual(switch['aiLocation']['us'], sentences_['usProcessing'])
                us, world = switch['aiTransferCountry']['us'], switch['aiTransferCountry']['global']
                self.assertIn(sentences_['usCommitment'], us)
                self.assertNotIn(sentences_['usCommitment'], world)
                self.assertIn(module.US_STEMS[locale], sentences_['usCommitment'])
                for text in (us, world):
                    self.assertTrue(text.endswith(sentences_['usSystem'] + ai_legal_guard.separator(locale)
                                                  + sentences_['singapore']))
                self.assertIn('Personal Data Protection Act 2012', sentences_['singapore'])
                self.assertIn('Google Asia Pacific Pte. Ltd.', sentences_['singapore'])
        english = pins['requiredSentences']['en']
        self.assertEqual(english['usProcessing'],
                         'Google runs the AI processing and stores this content in the United States.')
        self.assertIn('other processing may take place in any country where Google or its subprocessors have '
                      'facilities', english['usCommitment'])

    def test_release_gate_ties_each_open_legal_point_to_its_switch_value(self):
        # F8: location global (PIPA country item) and guardrail on (AWS entity and processor row)
        # were blocked only by the free-text unresolved list. Each now needs its own flag.
        import copy
        import tempfile
        module = importlib.import_module('ai_assistant_candidate')
        self.assertEqual(module.CONDITIONAL_READINESS, {
            ('location', 'global'): 'pipaCountryItemForGlobalAccepted',
            ('guardrail', 'on'): 'awsGuardrailEntityAndProcessorRowVerified'})
        base = copy.deepcopy(module.load())
        base['status'] = 'integrated-and-verified'
        base['unresolvedBeforePublication'] = []
        for location, guardrail, flag in (('global', 'off', 'pipaCountryItemForGlobalAccepted'),
                                          ('us', 'on', 'awsGuardrailEntityAndProcessorRowVerified')):
            with self.subTest(location=location, guardrail=guardrail), \
                    tempfile.TemporaryDirectory(prefix='doseweek-legal-gate-') as directory:
                candidate = copy.deepcopy(base)
                candidate['readiness'] = {key: key not in module.CONDITIONAL_READINESS.values()
                                          for key in candidate['readiness']}
                candidate['switches']['location']['selected'] = location
                candidate['switches']['guardrail']['selected'] = guardrail
                candidate['legalSelfReviewEvidence'] = self._synthetic_legal_self_review_evidence(
                    candidate, directory)
                with self.assertRaises(AssertionError) as failure:
                    module.require_release_ready(candidate, allow_synthetic_fixture=True)
                self.assertIn(flag, str(failure.exception))
                candidate['readiness'][flag] = True
                module.require_release_ready(candidate, allow_synthetic_fixture=True)
        with tempfile.TemporaryDirectory(prefix='doseweek-legal-gate-') as directory:
            candidate = copy.deepcopy(base)
            candidate['readiness'] = {key: key not in module.CONDITIONAL_READINESS.values()
                                      for key in candidate['readiness']}
            candidate['switches']['location']['selected'] = 'us'
            candidate['switches']['guardrail']['selected'] = 'off'
            candidate['legalSelfReviewEvidence'] = self._synthetic_legal_self_review_evidence(candidate, directory)
            module.require_release_ready(candidate, allow_synthetic_fixture=True)

    def test_apply_data_binds_the_guardrail_switch_for_the_server(self):
        committed = self.source('docs/ai-consent-v3-apply.json')
        pins = ai_legal_guard.read_pins()
        for name, block in committed['combinations'].items():
            registry = block['serverRegistry']
            with self.subTest(combination=name):
                self.assertEqual(registry['guardrailLocales'],
                                 {'ai-consent-v3': ['en', 'es', 'fr'] if block['guardrail'] == 'on' else []})
                self.assertEqual(registry['guardrail'],
                                 {'ai-consent-v3': 'aws-guardrail-seoul' if block['guardrail'] == 'on' else None})
                for locale in LOCALES:
                    self.assertEqual(block['locales'][locale]['legalPinSha256'],
                                     pins['combinationSha256'][name][locale]['app'])
        steps = '\n'.join(committed['apply']['server'])
        self.assertIn('serverRegistry.guardrailLocales', steps)
        self.assertIn('refuses to start', steps)


if __name__ == '__main__':
    unittest.main()
