"""Settings sync disclosure (owner decision 2026-10-02 19:22, "설정도 함께 동기화 시켜야함").

Account sync carries every app setting across the devices of one account, including the
injection-reminder switches, record-only mode and supply tracking. A change made on another
device is applied on this device, and an important one is announced once. Grants that belong
to one device cannot sync: the OS notification permission, the app lock, and the health,
calendar and cloud-storage connections.

The account/sync candidate lists what the end-to-end encrypted server copy holds in `sync`
("all your records ... together with supported settings"). That list must say what the
settings are, that they sync across the account's devices and what stays on one device, in
all 17 locales, and the staged privacy policies, Terms and rendered pages must carry it.

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
ENGLISH = (
    'Supported settings are all your app settings, including whether injection reminders are on, '
    'recording without a plan and supply tracking. They are kept the same on every device signed '
    'in to your account. When an important setting is changed on another device, this device '
    'applies it and tells you once. Permissions and connections that belong to a single device '
    'are not synced: notification permission, the app lock, and health-data, calendar and '
    'cloud-storage connections.'
)
KOREAN = (
    '지원하는 설정은 앱 설정 전체예요. 주사 알림을 켰는지, 계획 없이 기록만 하는지, 약품 재고를 추적하는지도 '
    '포함해요. 같은 계정으로 로그인한 기기마다 설정이 똑같이 맞춰져요. 다른 기기에서 중요한 설정을 바꾸면 '
    '이 기기에도 적용하고 한 번 알려 드려요. 알림 권한, 앱 잠금, 건강 데이터·캘린더·클라우드 저장소 연결처럼 '
    '기기마다 따로 정하는 항목은 동기화하지 않아요.'
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
