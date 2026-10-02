"""Review-1 regressions: operator fields, market decision and iOS copy isolation.

Raw-source assertions run on the reviewed parent without new implementation symbols.
The tests cover every locale and inspect staged sources separately from canonical copy.
"""
import copy
import json
import unittest
from pathlib import Path

import account_sync_candidate
import privacy_legal
import render_account_sync

ROOT = Path(__file__).resolve().parents[1]
PRIVACY_SOURCES = ('ios-content.json', 'android-content.candidate.json')
MARKETS = {'version': '1.0.6', 'excludedRegions': ['EU', 'EEA', 'UK', 'Switzerland'],
           'existingUserRightsPreserved': True}


REGIONAL_ANCHORS = {'ko': {'exclusion': '판매하지 않아요',
        'noRepresentatives': '대리인을 선임하지 않았어요',
        'existingUsers': '기존 이용자',
        'rightsPreserved': '권리와 보호 조치는 유지해요',
        'switzerland': '스위스'},
 'en': {'exclusion': 'not offered for sale',
        'noRepresentatives': 'not appointed',
        'existingUsers': 'existing users',
        'rightsPreserved': 'does not remove applicable rights or safeguards',
        'switzerland': 'Switzerland'},
 'ja': {'exclusion': '販売しません',
        'noRepresentatives': '代理人は選任していません',
        'existingUsers': '既存の利用者',
        'rightsPreserved': '権利と保護措置は維持します',
        'switzerland': 'スイス'},
 'de': {'exclusion': 'nicht zum Verkauf angeboten',
        'noRepresentatives': 'keine Vertreter für die EU oder das Vereinigte Königreich '
                             'bestellt',
        'existingUsers': 'bestehende Nutzer',
        'rightsPreserved': 'Rechte und Schutzmaßnahmen',
        'switzerland': 'Schweiz'},
 'fr': {'exclusion': 'pas proposée à la vente',
        'noRepresentatives': 'pas désigné de représentant',
        'existingUsers': 'utilisateurs existants',
        'rightsPreserved': 'ne supprime pas les droits et garanties',
        'switzerland': 'Suisse'},
 'es': {'exclusion': 'no se ofrece a la venta',
        'noRepresentatives': 'No hemos designado representantes',
        'existingUsers': 'usuarios existentes',
        'rightsPreserved': 'no elimina los derechos ni las garantías',
        'switzerland': 'Suiza'},
 'it': {'exclusion': 'non è offerta in vendita',
        'noRepresentatives': 'Non abbiamo nominato rappresentanti',
        'existingUsers': 'utenti esistenti',
        'rightsPreserved': 'non elimina i diritti e le tutele',
        'switzerland': 'Svizzera'},
 'nl': {'exclusion': 'niet te koop aangeboden',
        'noRepresentatives': 'geen vertegenwoordigers in de EU of het VK aangewezen',
        'existingUsers': 'bestaande gebruikers',
        'rightsPreserved': 'geen afbreuk aan de toepasselijke rechten en waarborgen',
        'switzerland': 'Zwitserland'},
 'pt-PT': {'exclusion': 'não é disponibilizada para venda',
           'noRepresentatives': 'Não designámos representantes',
           'existingUsers': 'utilizadores existentes',
           'rightsPreserved': 'não elimina os direitos e as garantias',
           'switzerland': 'Suíça'},
 'pl': {'exclusion': 'nie jest oferowana do sprzedaży',
        'noRepresentatives': 'Nie wyznaczyliśmy przedstawicieli',
        'existingUsers': 'dotychczasowych użytkowników',
        'rightsPreserved': 'nie ogranicza praw ani zabezpieczeń',
        'switzerland': 'Szwajcarii'},
 'sv': {'exclusion': 'erbjuds inte till försäljning',
        'noRepresentatives': 'inte utsett representanter',
        'existingUsers': 'befintliga användare',
        'rightsPreserved': 'tar inte bort tillämpliga rättigheter eller skyddsåtgärder',
        'switzerland': 'Schweiz'},
 'hi': {'exclusion': 'बिक्री के लिए उपलब्ध नहीं',
        'noRepresentatives': 'प्रतिनिधि नियुक्त नहीं',
        'existingUsers': 'मौजूदा उपयोगकर्ताओं',
        'rightsPreserved': 'अधिकार या सुरक्षा उपाय समाप्त नहीं होते',
        'switzerland': 'स्विट्ज़रलैंड'},
 'pt-BR': {'exclusion': 'não é oferecida para venda',
           'noRepresentatives': 'Não nomeamos representantes',
           'existingUsers': 'usuários existentes',
           'rightsPreserved': 'não elimina os direitos e as salvaguardas',
           'switzerland': 'Suíça'},
 'ar': {'exclusion': 'لا يُعرض',
        'noRepresentatives': 'لم نُعيّن ممثلين',
        'existingUsers': 'المستخدمين الحاليين',
        'rightsPreserved': 'لا يلغي استبعاد البيع الحقوق أو الضمانات',
        'switzerland': 'سويسرا'},
 'zh-Hans': {'exclusion': '1.0.6不在欧盟和欧洲经济区（EU/EEA）、英国或瑞士销售',
             'noRepresentatives': '未为此版本任命',
             'existingUsers': '现有用户',
             'rightsPreserved': '销售限制不影响',
             'switzerland': '瑞士'},
 'zh-Hant': {'exclusion': '1.0.6不在歐盟和歐洲經濟區（EU/EEA）、英國或瑞士銷售',
             'noRepresentatives': '未為此版本任命',
             'existingUsers': '現有使用者',
             'rightsPreserved': '銷售限制不影響',
             'switzerland': '瑞士'},
 'tr': {'exclusion': 'satışa sunulmaz',
        'noRepresentatives': 'temsilcileri atanmamıştır',
        'existingUsers': 'mevcut kullanıcıların',
        'rightsPreserved': 'haklarını veya güvencelerini kaldırmaz',
        'switzerland': 'İsviçre'}}

IOS_RETENTION_LABELS = {'ko': [{'old': 'Google Play', 'new': '다른 지원 스토어'}],
 'en': [{'old': 'Google Play', 'new': 'another supported store'}],
 'ja': [{'old': 'Google Play', 'new': '対応する他のストア'}],
 'de': [{'old': 'bei Google Play', 'new': 'bei einem anderen unterstützten Store'},
        {'old': 'über Google Play', 'new': 'über einen anderen unterstützten Store'}],
 'fr': [{'old': 'de Google Play', 'new': 'd’un autre store pris en charge'},
        {'old': 'sur Google Play', 'new': 'sur un autre store pris en charge'}],
 'es': [{'old': 'Google Play', 'new': 'otra tienda compatible'}],
 'it': [{'old': 'Google Play', 'new': 'un altro store supportato'}],
 'nl': [{'old': 'Google Play', 'new': 'een andere ondersteunde store'}],
 'pt-PT': [{'old': 'do Google Play', 'new': 'de outra loja compatível'},
           {'old': 'no Google Play', 'new': 'em outra loja compatível'}],
 'pl': [{'old': 'Google Play', 'new': 'innym obsługiwanym sklepie'}],
 'sv': [{'old': 'Google Play', 'new': 'en annan stödd butik'}],
 'hi': [{'old': 'Google Play', 'new': 'किसी अन्य समर्थित स्टोर'}],
 'pt-BR': [{'old': 'no Google Play', 'new': 'em outra loja compatível'},
           {'old': 'o Google Play', 'new': 'outra loja compatível'}],
 'ar': [{'old': 'Google Play', 'new': 'متجر آخر مدعوم'}],
 'zh-Hans': [{'old': 'Google Play', 'new': '其他受支持的商店'}],
 'zh-Hant': [{'old': 'Google Play', 'new': '其他支援的商店'}],
 'tr': [{'old': "Google Play'den", 'new': 'desteklenen başka bir mağazadan'}]}


def load(name):
    return json.loads((ROOT / 'docs' / name).read_text(encoding='utf-8'))


def section(entry, ident):
    return next(s for s in entry['privacy']['sections'] if s['id'] == ident)


def strings(value, path=''):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from strings(item, path + '.' + key)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from strings(item, path + f'[{index}]')


class LegalRevision1Test(unittest.TestCase):
    def test_operator_bearing_fields_use_business_and_keep_representative(self):
        canonical = {name: load(name) for name in PRIVACY_SOURCES}
        staged = render_account_sync.integrated_sources()
        for stage, sources in (('canonical', canonical), ('staged', staged)):
            for name in PRIVACY_SOURCES:
                for loc, entry in sources[name]['locales'].items():
                    contact_id = 'contact' if name.startswith('ios') else 'changes'
                    fields = {'contact': section(entry, contact_id)['paragraphs'][0]}
                    if name.startswith('android'):
                        fields['scope'] = section(entry, 'scope')['paragraphs'][0].split('\n\n')[0]
                    for field, text in fields.items():
                        with self.subTest(stage=stage, source=name, locale=loc, field=field):
                            self.assertIn('Wonyoung Labs', text)
                    with self.subTest(stage=stage, source=name, locale=loc, role='representative'):
                        self.assertIn('Wonyoung Choi', fields['contact'])
                        self.assertIn('863-25-02023', fields['contact'])

    def test_market_metadata_matches_exclusions_and_no_rep_appointment(self):
        for name in (*PRIVACY_SOURCES, 'account-sync-content.candidate.json'):
            source = load(name)
            with self.subTest(source=name):
                self.assertEqual(source.get('marketAvailability'), MARKETS)
                self.assertNotIn('internationalRepresentativesVerified', source.get('serverReadiness', {}))
                self.assertNotIn('representativesVerified', source.get('legalReadiness', {}))
                self.assertNotIn('TO BE APPOINTED', json.dumps(source, ensure_ascii=False))

    def test_excluded_market_prose_preserves_existing_user_rights_all_locales(self):
        for name in PRIVACY_SOURCES:
            for loc, entry in load(name)['locales'].items():
                rights = next(s for s in entry['privacy']['legalSupplement']['sections']
                              if s['id'] == 'rights')
                text = rights['paragraphs'][1]
                with self.subTest(source=name, locale=loc):
                    for token in ('1.0.6', 'EU/EEA', 'GDPR', 'Art. 6', 'Art. 9',
                                  *REGIONAL_ANCHORS[loc].values()):
                        self.assertIn(token, text)
                    self.assertEqual(rights['deadlines']['euUkMonths'], 1)

    def test_market_contract_rejects_reopened_regions_and_fake_rep_contact(self):
        for name in PRIVACY_SOURCES:
            source = load(name)
            with self.subTest(source=name):
                self.assertEqual(source.get('marketAvailability'), MARKETS)
                privacy_legal.validate_readiness(source)
                for key, value in (('excludedRegions', ['EU', 'EEA', 'UK']),
                                   ('existingUserRightsPreserved', False)):
                    mutated = copy.deepcopy(source)
                    mutated['marketAvailability'][key] = value
                    with self.assertRaises(AssertionError):
                        privacy_legal.validate_readiness(mutated)
                mutated = copy.deepcopy(source)
                mutated['representatives']['EU']['contact'] = 'TO BE APPOINTED'
                with self.assertRaises(AssertionError):
                    privacy_legal.validate_readiness(mutated)

    def test_release_still_requires_actual_sales_exclusion_readback(self):
        source = load('account-sync-content.candidate.json')
        flags = source['serverReadiness']
        self.assertIn('salesRegionExclusionsVerified', flags)
        self.assertIs(flags['salesRegionExclusionsVerified'], False)
        ready = copy.deepcopy(source)
        ready.update(status='integrated-and-verified', unresolvedBeforePublication=[])
        ready['serverReadiness'] = {key: True for key in flags}
        ready['serverReadiness']['salesRegionExclusionsVerified'] = False
        with self.assertRaisesRegex(AssertionError, 'salesRegionExclusionsVerified'):
            account_sync_candidate.require_release_ready(ready)

    def test_operations_gate_excludes_markets_preserves_existing_user_safeguards(self):
        text = (ROOT / 'docs/LEGAL_OPERATIONS_1_0_6.md').read_text(encoding='utf-8')
        for token in ('EU/EEA, UK and Switzerland are excluded', 'no EU/UK representative',
                      'existing users', 'Store availability readback'):
            with self.subTest(token=token):
                self.assertIn(token, text)
        self.assertNotIn('contacts are explicitly pending until appointments', text)

    def test_canonical_ios_policy_and_help_avoid_other_platform_names(self):
        for loc, entry in load('ios-content.json')['locales'].items():
            for path, value in strings(entry):
                with self.subTest(locale=loc, field=path):
                    self.assertNotIn('Android', value)
                    self.assertNotIn('Google Play', value)

    def test_staged_ios_policy_and_help_avoid_other_platform_names(self):
        source = render_account_sync.integrated_sources()['ios-content.json']
        for loc, entry in source['locales'].items():
            for path, value in strings(entry):
                with self.subTest(locale=loc, field=path):
                    self.assertNotIn('Android', value)
                    self.assertNotIn('Google Play', value)

    def test_neutral_ios_retention_preserves_other_store_verifier_and_deletion_bounds(self):
        candidate = load('account-sync-content.candidate.json')
        source = render_account_sync.integrated_sources()['ios-content.json']
        for loc, entry in source['locales'].items():
            text = section(entry, 'deletion')['paragraphs'][0]
            with self.subTest(locale=loc):
                self.assertNotIn('Google Play', text)
                for number in ('30', '7', '90'):
                    self.assertIn(number, text)
                # Neutral labels may change, all purchase-record and erasure prose must survive.
                expected = candidate['locales'][loc]['retention']
                for label in IOS_RETENTION_LABELS[loc]:
                    self.assertIn(label['old'], expected)
                    expected = expected.replace(label['old'], label['new'])
                self.assertIn(expected, text)


if __name__ == '__main__':
    unittest.main()
