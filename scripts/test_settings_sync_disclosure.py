"""Settings sync disclosure (owner decisions 2026-10-02 19:22 "settings sync and restore" and
20:29 "settings sync works across iPhone and Android").

The cross-platform settings contract
(release/evidence/1.0.6/CODEX-LANES-20261002/settings-xplat-contract-20261002.md, sections 2-3)
syncs a named set of SHARED settings. Device grants and device-local state stay on each device:
the OS notification permission, the app lock, the health, calendar and cloud-storage connections
and the widget appearance. Sync never turns an AI feature on. A restore started from Settings
applies the saved settings and says which ones changed.

The account/sync candidate lists what the end-to-end encrypted server copy holds in `sync`
("all your records ... together with supported settings"). That text must name the settings
that sync, say what stays on each device, and must not claim that every app setting syncs or
is the same on every device: the same staged pages say that Plus tool data and the reference
medication for the estimate stay on the device (review round 3, major). The staged privacy
policies, Terms and rendered pages must carry it in all 17 locales.

Run from the repository root: python3 -m unittest discover -s scripts -p 'test_*.py'
"""
import html
import json
import re
import unittest
from pathlib import Path

import render_account_sync

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'docs/account-sync-content.candidate.json'
LOCALES = ('ko', 'en', 'ja', 'de', 'fr', 'es', 'it', 'nl', 'pt-PT', 'pl', 'sv', 'hi',
           'pt-BR', 'ar', 'zh-Hans', 'zh-Hant', 'tr')
CJK = ('ja', 'zh-Hans', 'zh-Hant')
SENTENCE = re.compile(r'(?<=[。।])|(?<=\.)\s+')
# The sentence that says what does not sync names the calendar connection and the notification
# permission. Neither word is in the 1.0.5-era sync text of any locale.
DEVICE_GRANT_STEMS = {
    'ko': ('캘린더', '알림 권한'),
    'en': ('calendar', 'notification permission'),
    'ja': ('カレンダー', '通知の許可'),
    'de': ('Kalender', 'Berechtigung für Benachrichtigungen'),
    'fr': ('calendrier', 'autorisation des notifications'),
    'es': ('calendario', 'permiso de notificaciones'),
    'it': ('calendario', 'autorizzazione per le notifiche'),
    'nl': ('agenda', 'toestemming voor meldingen'),
    'pt-PT': ('calendário', 'permissão de notificações'),
    'pl': ('kalendarz', 'zgoda na powiadomienia'),
    'sv': ('kalender', 'aviseringsbehörighet'),
    'hi': ('कैलेंडर', 'नोटिफ़िकेशन की अनुमति'),
    'pt-BR': ('calendário', 'permissão de notificações'),
    'ar': ('التقويم', 'إذن الإشعارات'),
    'zh-Hans': ('日历', '通知权限'),
    'zh-Hant': ('行事曆', '通知權限'),
    'tr': ('takvim', 'bildirim izni'),
}
# The device-grant sentence also names the widget appearance (DEVICE-LOCAL in the contract).
WIDGET_STEMS = {
    'ko': '위젯 모양', 'en': 'widget appearance', 'ja': 'ウィジェットの外観',
    'de': 'Aussehen der Widgets', 'fr': 'apparence des widgets', 'es': 'apariencia de los widgets',
    'it': 'aspetto dei widget', 'nl': 'uiterlijk van widgets', 'pt-PT': 'aspeto dos widgets',
    'pl': 'wygląd widżetów', 'sv': 'widgetarnas utseende', 'hi': 'विजेट का रूप',
    'pt-BR': 'aparência dos widgets', 'ar': 'مظهر الأدوات المصغّرة', 'zh-Hans': '小组件外观',
    'zh-Hant': '小工具外觀', 'tr': 'widget görünümü',
}
# Sync never turns an AI feature on (contract 1.3: "on" is never applied by a sync).
AI_STEMS = {
    'ko': 'AI 기능은 동기화로 켜지지 않고', 'en': 'Sync never turns on an AI feature',
    'ja': '同期によってAI機能がオンになることはなく', 'de': 'schaltet nie eine KI-Funktion ein',
    'fr': 'n’active jamais une fonction d’IA', 'es': 'nunca activa una función de IA',
    'it': 'non attiva mai una funzione di IA', 'nl': 'zet nooit een AI-functie aan',
    'pt-PT': 'nunca ativa uma funcionalidade de IA', 'pl': 'nigdy nie włącza funkcji AI',
    'sv': 'slår aldrig på en AI-funktion', 'hi': 'कोई AI सुविधा कभी चालू नहीं होती',
    'pt-BR': 'nunca ativa um recurso de IA', 'ar': 'لا تشغّل المزامنة أي ميزة ذكاء اصطناعي',
    'zh-Hans': '同步绝不会开启 AI 功能', 'zh-Hant': '同步絕不會開啟 AI 功能',
    'tr': 'hiçbir zaman bir yapay zeka özelliğini açmaz',
}
# A restore started from Settings applies the saved settings and says what changed (19:22).
RESTORE_STEMS = {
    'ko': '설정에서 복원하면', 'en': 'When you restore from Settings', 'ja': '設定から復元すると',
    'de': 'in den Einstellungen wiederherstellen', 'fr': 'restaurez depuis les Réglages',
    'es': 'restaura desde Ajustes', 'it': 'ripristini dalle Impostazioni', 'nl': 'herstelt via Instellingen',
    'pt-PT': 'restaura a partir das Definições', 'pl': 'przywracasz dane w Ustawieniach',
    'sv': 'återställer från Inställningar', 'hi': 'सेटिंग से रीस्टोर करने पर',
    'pt-BR': 'restaura pelas Configurações', 'ar': 'عند الاستعادة من الإعدادات', 'zh-Hans': '从设置中恢复时',
    'zh-Hant': '從設定中復原時', 'tr': "Ayarlar'dan geri yüklediğinizde",
}
# Review round 3 (major): "all your app settings" and "the same on every device" contradict the
# staged sentences that keep Plus tool data and the estimate's reference medication on the device.
TOTALITY_STEMS = {
    'ko': ('앱 설정 전체', '똑같이 맞춰져요'),
    'en': ('all your app settings', 'same on every device'),
    'ja': ('アプリの設定すべて', '同じ内容にそろいます'),
    'de': ('alle Ihre App-Einstellungen', 'gleich gehalten'),
    'fr': ('tous les réglages de l’app', 'restent identiques sur tous les appareils'),
    'es': ('todos los ajustes de la app', 'Se mantienen iguales'),
    'it': ('tutte le impostazioni dell’app', 'Restano uguali'),
    'nl': ('al uw app-instellingen', 'blijven gelijk op elk apparaat'),
    'pt-PT': ('todas as definições da aplicação', 'Mantêm-se iguais'),
    'pl': ('wszystkie ustawienia aplikacji', 'Pozostają takie same'),
    'sv': ('alla dina appinställningar', 'hålls likadana'),
    'hi': ('सभी ऐप सेटिंग', 'एक जैसी रहती हैं'),
    'pt-BR': ('todas as configurações do app', 'ficam iguais em todos'),
    'ar': ('جميع إعدادات التطبيق', 'متطابقة على كل جهاز'),
    'zh-Hans': ('全部应用设置', '这些设置保持一致'),
    'zh-Hant': ('所有 App 設定', '這些設定會保持一致'),
    'tr': ('tüm uygulama ayarlarınız', 'aynı kalırlar'),
}
# Settings that the staged pages keep on the device; the list of synced settings never names them.
NOT_LISTED = ('Plus', 'reference medication', '기준 약', '기준 약물')
ENGLISH = (
    'The settings that sync are appearance (colour and light or dark mode), the weight-change unit, '
    'the body map view, whether injection reminders are on, whether reminders show details or the '
    'medication name, recording without a plan, supply tracking, and your food search market and '
    'search-language choices. When one of these is changed on another device, this device applies '
    'it and tells you once about an important change, such as reminders or supply tracking. Sync '
    'never turns on an AI feature: you turn it on yourself on each device. Permissions, connections '
    'and display choices that belong to a single device are not synced: notification permission, '
    'the app lock, health-data, calendar and cloud-storage connections, and widget appearance. When '
    'you restore from Settings, the saved settings are applied and the app tells you which settings '
    'changed.'
)
KOREAN = (
    '동기화하는 설정은 화면 모양(색상과 라이트·다크 모드), 체중 변화 단위, 신체 지도 보기 방식, 주사 알림을 '
    '켰는지, 알림에 자세한 내용이나 약물 이름을 보여 줄지, 계획 없이 기록만 하는지, 약품 재고를 추적하는지, '
    '음식 검색의 시장·검색 언어 선택이에요. 다른 기기에서 이 설정을 바꾸면 이 기기에도 적용하고, 알림이나 재고 '
    '추적처럼 중요한 변경은 한 번 알려 드려요. AI 기능은 동기화로 켜지지 않고, 기기마다 직접 켜야 해요. 알림 '
    '권한, 앱 잠금, 건강 데이터·캘린더·클라우드 저장소 연결, 위젯 모양은 기기마다 따로 정하고 동기화하지 '
    '않아요. 설정에서 복원하면 저장된 설정을 적용하고, 어떤 설정이 바뀌었는지 알려 드려요.'
)

def sections(entries):
    return {section['id']: section for section in entries}


def sentences(text):
    return [part.strip() for part in SENTENCE.split(text) if part.strip()]


def plain(markup):
    return html.unescape(re.sub(r'<[^>]+>', '', markup))


def device_grant_sentences(locale, text):
    """The sentences of text that name both device grants (calendar, notification permission)."""
    stems = [stem.casefold() for stem in DEVICE_GRANT_STEMS[locale]]
    return [part for part in sentences(text) if all(stem in part.casefold() for stem in stems)]


class SettingsSyncDisclosureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate = json.loads((ROOT / SOURCE).read_text(encoding='utf-8'))
        cls.staged = render_account_sync.integrated_sources()
        cls.pages = {path.relative_to(ROOT).as_posix(): markup
                     for path, markup in render_account_sync.rendered_pages(cls.staged).items()}

    def sync(self, locale):
        return self.candidate['locales'][locale]['sync']

    def test_sync_text_says_what_settings_sync_and_what_stays_on_one_device_in_17_locales(self):
        for locale in LOCALES:
            text = self.sync(locale)
            with self.subTest(locale=locale):
                found = device_grant_sentences(locale, text)
                self.assertEqual(len(found), 1,
                                 'the sync text does not say that the notification permission and the '
                                 'calendar connection stay on one device (settings sync, owner decision '
                                 '2026-10-02 19:22)')
                # It follows the list of what the encrypted copy holds, before the key sentences.
                parts = sentences(text)
                self.assertIn(parts.index(found[0]), (2, 3, 4, 5))
                self.assertNotIn(found[0], parts[0])
                self.assertIn(WIDGET_STEMS[locale], found[0],
                              'the device-only sentence does not name the widget appearance (contract 1.3)')

    def test_korean_and_english_state_the_owner_decision(self):
        english, korean = self.sync('en'), self.sync('ko')
        first = sentences(english)[0]
        self.assertTrue(first.endswith('together with supported settings, for automatic backup and sync '
                                       'across both platforms.'))
        self.assertTrue(english.startswith(first + ' ' + ENGLISH + ' This is end-to-end encryption:'),
                        english[:900])
        first = sentences(korean)[0]
        self.assertTrue(first.endswith('지원하는 설정을 기기에서 암호화해 두 플랫폼 사이에서 자동 백업하고 동기화해요.'))
        self.assertTrue(korean.startswith(first + ' ' + KOREAN + ' 이 방식은 종단간 암호화예요.'), korean[:600])

    def test_the_settings_sentences_name_no_platform_store_or_provider(self):
        # The sync text reaches the iOS and the Android pages, so the new sentences stay neutral.
        for text in (ENGLISH, KOREAN):
            self.assertEqual([token for token in ('iOS', 'Android', 'Apple', 'Google', 'iCloud', 'HealthKit',
                                                  'Health Connect', 'Face ID', 'Drive') if token in text], [])
        for locale in LOCALES:
            with self.subTest(locale=locale):
                for sentence in device_grant_sentences(locale, self.sync(locale)):
                    self.assertEqual([token for token in ('iOS', 'Android', 'Apple', 'Google', 'iCloud',
                                                          'HealthKit', 'Health Connect', 'Face ID', 'Drive')
                                      if token in sentence], [])

    def test_no_page_claims_that_every_app_setting_syncs_or_is_the_same_on_every_device(self):
        for locale in LOCALES:
            places = {
                'candidate sync text': self.sync(locale),
                'iOS privacy page': plain(self.pages[f'{locale}/privacy/index.html']),
                'Android privacy page': plain(self.pages[f'{locale}/android/privacy/index.html']),
                'Terms page': plain(self.pages[f'{locale}/terms/index.html']),
            }
            for name, text in places.items():
                for stem in TOTALITY_STEMS[locale]:
                    with self.subTest(locale=locale, place=name, stem=stem):
                        self.assertNotIn(stem, text,
                                         'the settings text claims every app setting syncs or is the same '
                                         'on every device; the same page keeps named settings on the device')

    def test_sync_text_says_ai_stays_off_and_restore_names_what_changed_in_17_locales(self):
        for locale in LOCALES:
            text = self.sync(locale)
            parts = sentences(text)
            for name, stem in (('AI', AI_STEMS[locale]), ('restore', RESTORE_STEMS[locale])):
                with self.subTest(locale=locale, sentence=name):
                    found = [part for part in parts if stem in part]
                    self.assertEqual(len(found), 1, f'the sync text lacks the {name} sentence')
                    self.assertLess(parts.index(found[0]), 8)
                    for page in (f'{locale}/privacy/index.html', f'{locale}/android/privacy/index.html'):
                        self.assertIn(found[0], plain(self.pages[page]))

    def test_the_list_of_synced_settings_names_no_setting_the_pages_keep_on_the_device(self):
        for locale in LOCALES:
            listed = sentences(self.sync(locale))[1]
            with self.subTest(locale=locale):
                self.assertEqual([token for token in NOT_LISTED if token in listed], [], listed)
                self.assertNotIn(WIDGET_STEMS[locale], listed)

    def test_staged_policies_terms_and_pages_carry_the_settings_sentences(self):
        ios = self.staged['ios-content.json']['locales']
        android = self.staged['android-content.candidate.json']['locales']
        terms = self.staged['terms-content.json']['locales']
        for locale in LOCALES:
            found = device_grant_sentences(locale, self.sync(locale))
            with self.subTest(locale=locale):
                self.assertEqual(len(found), 1, 'the candidate has no device-grant sentence')
                sentence = found[0]
                ios_privacy = sections(ios[locale]['privacy']['sections'])
                android_privacy = sections(android[locale]['privacy']['sections'])
                places = {
                    'iOS storage section': ios_privacy['storage']['paragraphs'][0],
                    'iOS backup section': ios_privacy['backups']['paragraphs'][0],
                    'Android backup section': '\n\n'.join(android_privacy['backup']['paragraphs']),
                    'Android optional-services list': android_privacy['no-collection']['items'][0],
                    'Terms records section': sections(terms[locale]['sections'])['records']['paragraphs'][0],
                    'iOS privacy page': plain(self.pages[f'{locale}/privacy/index.html']),
                    'Android privacy page': plain(self.pages[f'{locale}/android/privacy/index.html']),
                    'Terms page': plain(self.pages[f'{locale}/terms/index.html']),
                }
                for name, text in places.items():
                    self.assertIn(sentence, text, f'{name} lacks the settings sync sentences')


if __name__ == '__main__':
    unittest.main()
