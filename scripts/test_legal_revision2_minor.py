"""Review-2 regressions for store-neutral iOS copy and PIPA number formatting.

Only existing renderer APIs are used so these checks load on the reviewed parent;
missing copy corrections fail assertions rather than imports or test setup.
"""
import json
import copy
import re
import unittest
from pathlib import Path

import render_account_sync
import render_ios

ROOT = Path(__file__).resolve().parents[1]
PRIVACY_SOURCES = ('ios-content.json', 'android-content.candidate.json')
# ASCII letter boundaries also catch Play購入, Play-Kauftoken and Play'den.
# Unicode word boundaries would miss the shortened name next to CJK letters.
OTHER_PLATFORM = re.compile(r'(?<![A-Za-z])(?:Android|Google\s+Play|Play)(?![A-Za-z])',
                            re.IGNORECASE)
PIPA_THRESHOLD = {
    'de': r'mindestens (?:1\.000|eintausend|tausend) Personen',
    'fr': r'au moins (?:1[ \u00a0\u202f]000|mille) personnes',
    'es': r'al menos (?:1\.000|mil) personas',
    'pl': r'co najmniej (?:1[ \u00a0\u202f]000|tysiąc) osób',
    'sv': r'minst (?:1[ \u00a0\u202f]000|ett tusen|tusen) personer',
    'tr': r'En az (?:1\.000|bin) kişi',
}
PIPA_INDEPENDENT_TRIGGERS = {
    'de': ('sensible Daten oder eindeutige Identifikationsdaten betroffen sind',
           'oder ein einschlägiger unbefugter Zugriff von außen',
           'Diese Auslöser gelten unabhängig voneinander',
           'auch ein kleiner Vorfall mit Gesundheitsdaten kann meldepflichtig sein'),
    'fr': ('données sensibles ou d’identification unique',
           'ou lorsqu’un accès externe non autorisé répondant aux critères',
           'Ces critères sont indépendants',
           'un incident limité portant sur des données de santé peut donc exiger un signalement'),
    'es': ('datos sensibles o de identificación única',
           'o la filtración se debe a un acceso externo no autorizado',
           'Estos supuestos son independientes',
           'un incidente pequeño con datos de salud puede requerir notificación'),
    'pl': ('danych wrażliwych lub unikalnych danych identyfikacyjnych',
           'albo został spowodowany kwalifikującym się nieuprawnionym dostępem z zewnątrz',
           'Przesłanki te są niezależne',
           'także mały incydent dotyczący danych zdrowotnych może wymagać zgłoszenia'),
    'sv': ('känsliga uppgifter eller unika identifieringsuppgifter',
           'eller om en läcka orsakas av extern obehörig åtkomst',
           'Dessa grunder gäller oberoende av varandra',
           'Även en liten incident med hälsouppgifter kan kräva rapportering'),
    'tr': ('hassas veriler veya benzersiz kimlik verileri',
           'ya da gerekli koşulları karşılayan dış kaynaklı yetkisiz erişim',
           'Bu koşullar birbirinden bağımsızdır',
           'az sayıda kişiyi etkileyen bir sağlık verisi olayı da bildirim gerektirebilir'),
}


def load(name):
    return json.loads((ROOT / 'docs' / name).read_text(encoding='utf-8'))


def strings(value, path=''):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from strings(item, path + '.' + key)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from strings(item, path + f'[{index}]')


class LegalRevision2MinorTest(unittest.TestCase):
    def assert_store_neutral(self, source):
        for locale, entry in source['locales'].items():
            for path, value in strings(entry):
                with self.subTest(locale=locale, field=path):
                    self.assertIsNone(OTHER_PLATFORM.search(value),
                                      f'competing platform/store name in {locale}{path}')

    def test_canonical_ios_copy_rejects_shortened_competing_store_names(self):
        self.assert_store_neutral(load('ios-content.json'))

    def test_staged_ios_copy_rejects_shortened_competing_store_names(self):
        self.assert_store_neutral(render_account_sync.integrated_sources()['ios-content.json'])

    def test_brand_guard_covers_localized_shortened_forms_and_allows_google_sign_in(self):
        # These are the shortened store references observed in the reviewed staged copy.
        for text in ('Play 구매 토큰', 'Play purchase token', 'Play購入トークン',
                     'Play-Kauftoken', 'jeton d’achat Play', 'compra de Play',
                     'acquisto Play', 'Play-aankooptoken', 'compra Play', 'zakupu Play',
                     'Play-köptoken', 'Play खरीद टोकन', 'رمز شراء Play',
                     'Play 购买令牌', 'Play 購買權杖', 'Play satın alma belirteci',
                     'Play requests', 'Play-Anträge', 'Play-aanvragen', "Play'den",
                     'Android', 'Google Play'):
            with self.subTest(text=text):
                self.assertIsNotNone(OTHER_PLATFORM.search(text))
        for text in ('Sign in with Google', 'Google로 로그인', 'Googleでサインイン',
                     'Google sign-in', 'accounts.google.com', 'display', 'playback'):
            with self.subTest(allowed=text):
                self.assertIsNone(OTHER_PLATFORM.search(text))

    def test_renderer_rejects_short_store_name_next_to_localized_text(self):
        for locale, suffix in (('en', 'Play purchase token'), ('ja', 'Play購入トークン'),
                               ('de', 'Play-Kauftoken'), ('ko', 'Play 구매 토큰')):
            with self.subTest(locale=locale):
                source = copy.deepcopy(load('ios-content.json'))
                source['locales'][locale]['privacy']['intro'] += ' ' + suffix
                with self.assertRaisesRegex(AssertionError, 'neutral references'):
                    render_ios.validate(source)

    def incidents(self):
        for name in PRIVACY_SOURCES:
            source = load(name)
            for locale in PIPA_THRESHOLD:
                sections = source['locales'][locale]['privacy']['legalSupplement']['sections']
                incident = next(section for section in sections if section['id'] == 'incident')
                yield name, locale, incident

    def test_pipa_thousand_threshold_uses_locale_correct_grouping_both_sources(self):
        for name, locale, incident in self.incidents():
            with self.subTest(source=name, locale=locale):
                text = incident['paragraphs'][1]
                self.assertNotIn('1,000', text, 'comma reads as a decimal separator here')
                self.assertRegex(text, PIPA_THRESHOLD[locale],
                                 'PIPA threshold must clearly mean at least one thousand people')

    def test_pipa_sensitive_and_external_access_triggers_remain_independent(self):
        for name, locale, incident in self.incidents():
            with self.subTest(source=name, locale=locale):
                self.assertEqual(incident['pipaReportTriggers'],
                                 ['1000-or-more', 'sensitive-or-unique-ID',
                                  'qualifying-external-unauthorized-access'])
                self.assertEqual(incident['deadlines']['pipaHours'], 72)
                text = incident['paragraphs'][1]
                for token in ('PIPA', 'PIPC', 'KISA', '72',
                              *PIPA_INDEPENDENT_TRIGGERS[locale]):
                    self.assertIn(token, text)


if __name__ == '__main__':
    unittest.main()
