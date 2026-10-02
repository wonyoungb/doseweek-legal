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
        for item in ('식사 선호', '알레르기', '싫어하는 음식', '종단간 암호화 대상이 아니'):
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
        expected_status = {'ko': 'pending-owner-gate-6', 'ja': 'pending-counsel-or-native-review',
                           'en': 'reviewed-by-lane-agent'}
        for locale in LOCALES:
            path = f'{RECEIPTS}/{locale}.json'
            with self.subTest(locale=locale):
                receipt = self.source(path)
                self.assertEqual(receipt['locale'], locale)
                self.assertEqual(receipt['consentVersion'], document['consentVersion'])
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
