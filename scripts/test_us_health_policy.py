"""Failing-first US consumer health-data notice requirements (all 17 locales).

These checks load files directly and tolerate an absent new policy source. They can run on the
approved parent without new renderer imports; unmet requirements fail assertions, not imports.
"""
from __future__ import annotations

import json
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LOCALES = ('ko', 'en', 'ja', 'de', 'fr', 'es', 'it', 'nl', 'pt-PT', 'pl', 'sv', 'hi',
           'pt-BR', 'ar', 'zh-Hans', 'zh-Hant', 'tr')
POLICY = ROOT / 'docs/us-health-content.json'
SECTIONS = ('categories', 'purposes-sources', 'disclosures', 'consent', 'rights', 'deadlines', 'contact')


def source():
    return json.loads(POLICY.read_text(encoding='utf-8')) if POLICY.is_file() else {}


def section_text(entry, section_id):
    section = next((s for s in entry.get('sections', []) if s.get('id') == section_id), {})
    return '\n'.join(section.get('paragraphs', []))


class PrivacyLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.locale = None
        self.current = None
        self.links = {}

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == 'article':
            self.locale = attrs.get('data-language')
        if tag == 'a' and self.locale:
            self.current = [attrs.get('href', ''), '']

    def handle_data(self, text):
        if self.current is not None:
            self.current[1] += text

    def handle_endtag(self, tag):
        if tag == 'a' and self.current is not None:
            self.links.setdefault(self.locale, []).append(tuple(self.current))
            self.current = None
        if tag == 'article':
            self.locale = None


class USConsumerHealthPolicyTests(unittest.TestCase):
    def entries(self):
        data = source()
        self.assertEqual(data.get('localeOrder'), list(LOCALES), 'US_POLICY_17_LOCALES: separate source missing or incomplete')
        self.assertEqual(list(data.get('locales', {})), list(LOCALES), 'US_POLICY_17_LOCALES: exact locale coverage')
        return data['locales']

    def test_separate_prominent_localized_us_health_policy(self):
        for locale, entry in self.entries().items():
            self.assertTrue(entry.get('title', '').strip(), f'{locale}: US_POLICY_TITLE')
            self.assertTrue(entry.get('intro', '').strip(), f'{locale}: US_POLICY_SCOPE')
            self.assertEqual([s.get('id') for s in entry.get('sections', [])], list(SECTIONS), f'{locale}: US_POLICY_REQUIRED_SECTIONS')
            self.assertTrue(all(p.strip() for s in entry['sections'] for p in s['paragraphs']), f'{locale}: US_POLICY_LOCALIZED_CONTENT')

    def test_health_categories_purposes_and_sources_are_disclosed(self):
        for locale, entry in self.entries().items():
            self.assertTrue(section_text(entry, 'categories').strip(), f'{locale}: US_HEALTH_CATEGORIES')
            self.assertTrue(section_text(entry, 'purposes-sources').strip(), f'{locale}: US_HEALTH_PURPOSES_SOURCES')
            self.assertIn('HealthKit', section_text(entry, 'purposes-sources'), f'{locale}: US_HEALTH_API_SOURCE')
            self.assertIn('Health Connect', section_text(entry, 'purposes-sources'), f'{locale}: US_HEALTH_API_SOURCE')
        en = self.entries()['en']
        for phrase in ('medication', 'weight', 'meals', 'health inferences', 'encrypted', 'account'):
            self.assertIn(phrase, section_text(en, 'categories'), f'US_HEALTH_CATEGORY_{phrase}')
        for phrase in ('you enter', 'you choose', 'sync', 'security'):
            self.assertIn(phrase, section_text(en, 'purposes-sources'), f'US_HEALTH_PURPOSE_SOURCE_{phrase}')

    def test_recipients_affiliates_no_sale_no_health_geofencing(self):
        for locale, entry in self.entries().items():
            disclosures = section_text(entry, 'disclosures')
            for token in ('Cloudflare', 'AWS'):
                self.assertIn(token, disclosures, f'{locale}: US_HEALTH_RECIPIENT_{token}')
            self.assertGreaterEqual(len(entry['sections'][2]['paragraphs']), 3, f'{locale}: US_HEALTH_RECIPIENT_AND_RESTRICTIONS')
        text = section_text(self.entries()['en'], 'disclosures')
        for phrase in ('corporate affiliates', 'do not sell', 'geofencing', 'advertising', 'processors'):
            self.assertIn(phrase, text, f'US_HEALTH_DISCLOSURE_{phrase}')

    def test_separate_collection_and_sharing_consent_requested_service_limit(self):
        for locale, entry in self.entries().items():
            consent = section_text(entry, 'consent')
            self.assertGreaterEqual(len(entry['sections'][3]['paragraphs']), 2, f'{locale}: US_HEALTH_SEPARATE_CONSENT')
            self.assertTrue(consent.strip(), f'{locale}: US_HEALTH_REQUESTED_SERVICE_LIMIT')
        text = section_text(self.entries()['en'], 'consent')
        for phrase in ('requested service', 'separate consent', 'optional ads or analytics', 'withdraw'):
            self.assertIn(phrase, text, f'US_HEALTH_CONSENT_{phrase}')

    def test_health_rights_and_downstream_backup_deletion(self):
        for locale, entry in self.entries().items():
            rights = section_text(entry, 'rights')
            self.assertIn('7', rights, f'{locale}: US_HEALTH_BACKUP_DELETION_7_DAYS')
            self.assertIn('wonyoung@wonyoungchoi.dev', rights, f'{locale}: US_HEALTH_RIGHTS_ROUTE')
            self.assertGreaterEqual(len(entry['sections'][4]['paragraphs']), 3, f'{locale}: US_HEALTH_RIGHTS_AND_DOWNSTREAM_DELETION')
        text = section_text(self.entries()['en'], 'rights')
        for phrase in ('confirm', 'access', 'withdraw', 'delete', 'recipients', 'immediately', 'processors', '7 days'):
            self.assertIn(phrase, text, f'US_HEALTH_RIGHT_{phrase}')

    def test_state_response_deletion_and_appeal_deadlines(self):
        for locale, entry in self.entries().items():
            text = section_text(entry, 'deadlines')
            for token in ('Washington', 'Nevada', 'Connecticut', '45', '30', '60', '15'):
                self.assertIn(token, text, f'{locale}: US_HEALTH_STATE_DEADLINE_{token}')
            self.assertGreaterEqual(text.count('45'), 5, f'{locale}: US_HEALTH_45_DAY_RESPONSE_EXTENSION_APPEAL')
        text = section_text(self.entries()['en'], 'deadlines')
        for phrase in ('from receipt', 'extension', 'authentication', 'appeal', 'Attorney General'):
            self.assertIn(phrase, text, f'US_HEALTH_DEADLINE_{phrase}')

    def test_both_privacy_pages_have_actual_policy_links_all_locales(self):
        entries = source().get('locales', {})
        for relative in ('privacy/index.html', 'android/privacy/index.html'):
            path = ROOT / relative
            parser = PrivacyLinks()
            parser.feed(path.read_text(encoding='utf-8') if path.is_file() else '')
            for locale in LOCALES:
                wanted = urlsplit(urljoin(path.as_uri(), '../' * relative.count('/') + 'us-health/#' + locale))
                matching = [label for href, label in parser.links.get(locale, [])
                            if urlsplit(urljoin(path.as_uri(), href)) == wanted]
                self.assertTrue(matching, f'{relative}:{locale}: US_POLICY_ACTUAL_PRIVACY_LINK missing')
                title = entries.get(locale, {}).get('title', '')
                self.assertTrue(title and any(title in label for label in matching), f'{relative}:{locale}: US_POLICY_LOCALIZED_LINK_LABEL')


if __name__ == '__main__':
    unittest.main()
