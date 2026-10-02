"""Failing-first 1.0.6 privacy duties; source and accessible-render acceptance.

These checks deliberately inspect the website-owned sources without requiring a new
implementation symbol, so the RED compiles and fails on missing disclosure assertions.
"""
import json
import unittest
from pathlib import Path
import render_ios
import render_android

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ('ios-content.json', 'android-content.candidate.json')
COLUMNS = ('legalBasis', 'data', 'country', 'timingMethod', 'recipientContact',
           'purpose', 'retention', 'refusalEffect')
PROVIDERS = ('cloudflare', 'aws', 'firebase', 'admob', 'apple-sign-in', 'google-sign-in')


def catalogs():
    return [json.loads((ROOT / 'docs' / name).read_text()) for name in SOURCES]


def supplement(entry):
    return entry['privacy'].get('legalSupplement', {})


class PrivacyLegalUpdateTest(unittest.TestCase):
    def each(self):
        for name, source in zip(SOURCES, catalogs()):
            for locale, entry in source['locales'].items():
                yield name, locale, entry

    def section(self, entry, ident):
        found = [s for s in supplement(entry).get('sections', []) if s['id'] == ident]
        self.assertEqual(len(found), 1, f'missing legal disclosure {ident}')
        return found[0]

    def test_art30_processing_basis_security_destruction_and_no_health_sale(self):
        for name, locale, entry in self.each():
            with self.subTest(source=name, locale=locale):
                s = self.section(entry, 'processing')
                self.assertEqual(set(s['duties']), {'purpose', 'categories', 'ordinaryBasis',
                    'healthBasis', 'retention', 'security', 'destruction', 'noPublicDisclosureSaleAdUse'})
                self.assertTrue(all(s['duties'].values()))
                self.assertGreaterEqual(len(s['paragraphs']), 3)
                text = '\n'.join(s['paragraphs'])
                self.assertGreater(len(text), 500)
                for token in ('DoseWeek', 'OS'):
                    self.assertIn(token, text)
                # Required disclosures must be prose, not only truth flags.
                self.assertIn('7', text, 'backup destruction must be stated in the policy')

    def test_responsible_operator_and_public_business_contacts(self):
        for name, locale, entry in self.each():
            with self.subTest(source=name, locale=locale):
                text = '\n'.join(p for s in entry['privacy']['sections'] for p in s['paragraphs'])
                for token in ('Wonyoung Labs', 'Wonyoung Choi', '863-25-02023',
                              '201, 6 Surim-ro 81beon-gil', '46281'):
                    self.assertIn(token, text)
                self.assertIn('wonyoung@wonyoungchoi.dev', text)

    def test_korean_rights_ten_days_withdrawal_refusal_and_appeal(self):
        for name, locale, entry in self.each():
            with self.subTest(source=name, locale=locale):
                s = self.section(entry, 'rights')
                self.assertEqual(s['deadlines']['koreaAccessDays'], 10)
                text = '\n'.join(s['paragraphs'])
                self.assertIn('10', text, 'actual Korean access deadline absent')
                self.assertIn('wonyoung@wonyoungchoi.dev', text)
                self.assertIn('118', text, 'Korean complaint channel absent')
                self.assertEqual(set(s['rights']), {'access', 'correction', 'erasure',
                    'restriction', 'withdrawal', 'objection', 'portability', 'appeal', 'complaint'})
                self.assertTrue(all(s['rights'].values()))

    def test_international_health_basis_rights_and_transfer_mechanisms(self):
        for name, locale, entry in self.each():
            with self.subTest(source=name, locale=locale):
                s = self.section(entry, 'rights')
                self.assertEqual(s['deadlines']['euUkMonths'], 1)
                self.assertEqual(s['regions'], ['EU', 'UK', 'Japan', 'Brazil'])
                text = '\n'.join(s['paragraphs'])
                for token in ('GDPR', 'Art. 6', 'Art. 9', 'APPI', 'Art. 28', 'LGPD',
                              'ANPD', 'SCC', 'IDTA'):
                    self.assertIn(token, text)

    def test_health_permissions_optional_read_only_no_ad_use(self):
        for name, locale, entry in self.each():
            with self.subTest(source=name, locale=locale):
                s = self.section(entry, 'processing')
                self.assertEqual(s['healthPermissions'], {'optional': True, 'readOnly': True,
                    'manualEntryAvailable': True, 'healthAdvertising': False})

    def test_mg_estimate_reference_not_measurement_effect_or_dose_advice(self):
        for name, locale, entry in self.each():
            with self.subTest(source=name, locale=locale):
                s = supplement(entry)
                self.assertEqual(s.get('estimate'), {'unit': 'mg', 'referenceOnly': True,
                    'measuredBloodConcentration': False, 'predictsEffectOrSafety': False,
                    'medicalAdvice': False, 'doseChangeBasis': False})
                self.assertIn('mg', entry['privacy']['medicalDisclaimer']['body'])

    def test_pipa_sensitive_breach_notice_and_report_seventy_two_hours(self):
        for name, locale, entry in self.each():
            with self.subTest(source=name, locale=locale):
                s = self.section(entry, 'incident')
                self.assertEqual(s['deadlines']['pipaHours'], 72)
                self.assertEqual(s['pipaReportTriggers'], ['1000-or-more', 'sensitive-or-unique-ID',
                                                         'qualifying-external-unauthorized-access'])

    def test_ftc_health_breach_sdk_disclosures_and_exact_deadlines(self):
        for name, locale, entry in self.each():
            with self.subTest(source=name, locale=locale):
                s = self.section(entry, 'incident')
                d = s['deadlines']
                self.assertEqual(d['ftcIndividualCalendarDays'], 60)
                self.assertEqual(d['ftcLargeBreachThreshold'], 500)
                self.assertEqual(d['ftcSmallYearEndCalendarDays'], 60)
                self.assertEqual(d['ftcMediaStateResidents'], 500)
                self.assertTrue(s['unauthorizedSdkDisclosureCovered'])
                self.assertTrue(s['encryptedDataRequiresKeyAndMetadataAssessment'])
                text = '\n'.join(s['paragraphs'])
                for token in ('FTC', 'SDK', '72', '60', '500', 'GDPR'):
                    self.assertIn(token, text, 'rendered breach duty absent')
                self.assertRegex(text, r'1[,. \u00a0]?000', 'Korean reporting threshold absent')

    def test_gdpr_breach_risk_and_high_risk_notice(self):
        for name, locale, entry in self.each():
            with self.subTest(source=name, locale=locale):
                s = self.section(entry, 'incident')
                self.assertEqual(s['deadlines']['gdprAuthorityHours'], 72)
                self.assertTrue(s['gdprHighRiskIndividualNotice'])

    def test_processor_transfer_table_art28_8_columns_and_roles(self):
        for name, locale, entry in self.each():
            with self.subTest(source=name, locale=locale):
                table = self.section(entry, 'processors').get('table', {})
                self.assertEqual([c['id'] for c in table.get('columns', [])], list(COLUMNS))
                self.assertEqual([r['id'] for r in table.get('rows', [])], list(PROVIDERS))
                for row in table['rows']:
                    self.assertEqual(set(row['cells']), set(COLUMNS))
                    self.assertTrue(all(isinstance(v, str) and v.strip() for v in row['cells'].values()))
                    self.assertIn(row['role'], ('processor', 'independent-controller'))

    def test_unverified_provider_and_sales_configuration_block_release_without_rep_appointment(self):
        for name, source in zip(SOURCES, catalogs()):
            with self.subTest(source=name):
                flags = source.get('legalReadiness', {})
                self.assertEqual(set(flags), {'providerInventoryVerified', 'overseasTransferBasisVerified',
                    'processorContractsVerified', 'regionalSafeguardsVerified', 'salesRegionExclusionsVerified'})
                self.assertFalse(any(flags.values()))
                self.assertEqual(set(source.get('representatives', {})), {'EU', 'UK'})
                self.assertTrue(all(r['status'] == 'not-designated-excluded-markets' and
                                    r['contact'] is None
                                    for r in source['representatives'].values()))

    def test_rendered_transfer_table_accessible_in_every_locale(self):
        for name, source in zip(SOURCES, catalogs()):
            for locale, entry in source['locales'].items():
                with self.subTest(source=name, locale=locale):
                    if name.startswith('ios'):
                        result = render_ios.panel(locale, entry, source['bundleVersion'], source['effectiveDate'])
                    else:
                        result = render_android.privacy_panel(source, locale)
                    self.assertIn('<table class="processor-table">', result)
                    self.assertIn('<caption>', result)
                    self.assertEqual(result.count('<th scope="col"'), 8)
                    self.assertEqual(result.count('<th scope="row"'), 6)


if __name__ == '__main__':
    unittest.main()
