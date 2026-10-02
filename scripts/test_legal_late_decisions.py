"""Late owner decisions: source-only RED proof, all locales, offline."""
import copy
import json
import unittest
from pathlib import Path

import render_account_sync
import render_terms
from test_legal_revision1 import MARKETS, REGIONAL_ANCHORS, strings

ROOT = Path(__file__).resolve().parents[1]
PRICES = ('USD 1.99', 'USD 13.99', 'KRW 3,300', 'KRW 19,900', 'JPY 300', 'JPY 1,980')
VARIABLE_DURATION = {
    'de': ('Die im Store angezeigte tatsächliche Dauer ist maßgeblich', 'Die tatsächliche Dauer wird vor der Bestätigung angezeigt'),
    'fr': ('La durée réelle affichée par la boutique fait foi', 'La durée réelle est affichée avant la confirmation'),
    'es': ('Rige la duración real que muestra la tienda', 'La duración real se muestra antes de la confirmación'),
    'it': ('Fa fede la durata effettiva indicata dallo store', 'La durata effettiva è mostrata prima della conferma'),
    'nl': ('De werkelijke duur die de store toont, is bepalend', 'De werkelijke duur wordt vóór bevestiging getoond'),
    'pt-PT': ('vale a duração efetivamente apresentada pela loja', 'vale a duração apresentada na loja'),
    'pl': ('obowiązuje rzeczywista długość podana w sklepie', 'obowiązuje długość podana w sklepie'),
    'sv': ('den faktiska längd som butiken visar gäller', 'den längd som butiken visar gäller'),
    'hi': ('स्टोर में दिखाई गई वास्तविक अवधि लागू होती है', 'स्टोर में दिखाई गई अवधि लागू होती है'),
    'pt-BR': ('vale a duração efetivamente mostrada pela loja', 'vale a duração mostrada pela loja'),
    'tr': ('mağazanın gösterdiği gerçek süre geçerlidir', 'mağazada gösterilen süre geçerlidir'),
}


def load(name):
    return json.loads((ROOT / 'docs' / name).read_text())


class LegalLateDecisionsTest(unittest.TestCase):
    def test_all_locales_preserve_trial_renewal_cancel_and_local_price_meanings(self):
        anchors = json.loads((ROOT / 'scripts/fixtures/legal_late_trial_anchors.json').read_text())
        canonical = load('terms-content.json')
        staged = render_account_sync.integrated_sources()['terms-content.json']
        self.assertEqual(set(anchors), set(canonical['localeOrder']))
        for stage, source in (('canonical', canonical), ('staged', staged)):
            for locale, entry in source['locales'].items():
                sections = {s['id']: s for s in entry['sections']}
                with self.subTest(stage=stage, locale=locale, field='offer'):
                    for meaning in anchors[locale]:
                        self.assertIn(meaning, sections['free-plus']['paragraphs'][2])
                for sub in sections['billing']['subsections']:
                    with self.subTest(stage=stage, locale=locale, field=sub['id']):
                        for meaning in anchors[locale][:2]:
                            self.assertIn(meaning, sub['paragraphs'][0])

    def test_fixed_month_trial_has_no_variable_duration_override(self):
        for locale, entry in load('terms-content.json')['locales'].items():
            sections = {s['id']: s for s in entry['sections']}
            fields = [('offer', sections['free-plus']['paragraphs'][2])]
            fields += [(sub['id'], sub['paragraphs'][0]) for sub in sections['billing']['subsections']]
            for field, text in fields:
                with self.subTest(locale=locale, field=field):
                    for stale in VARIABLE_DURATION.get(locale, ()):
                        self.assertNotIn(stale, text)

    def test_final_reference_prices_in_canonical_and_staged_terms(self):
        canonical = load('terms-content.json')
        staged = render_account_sync.integrated_sources()['terms-content.json']
        self.assertEqual(len(canonical['localeOrder']), 17)
        for stage, source in (('canonical', canonical), ('staged', staged)):
            for locale, entry in source['locales'].items():
                offer = next(s for s in entry['sections'] if s['id'] == 'free-plus')['paragraphs'][2]
                with self.subTest(stage=stage, locale=locale):
                    for price in PRICES:
                        self.assertIn(price, offer)
                    self.assertNotRegex(offer, r'22[,\s]?000|2[,\s]?900')

    def test_renderer_accepts_final_price_and_rejects_each_retired_price(self):
        terms, ios = render_terms.load()
        final = copy.deepcopy(terms)
        for entry in final['locales'].values():
            offer = next(s for s in entry['sections'] if s['id'] == 'free-plus')
            offer['paragraphs'][2] = offer['paragraphs'][2].replace('KRW 22,000', 'KRW 19,900')
        render_terms.validate(final, ios)
        for locale in final['localeOrder']:
            for correct, retired in (('KRW 19,900', 'KRW 22,000'), ('KRW 3,300', 'KRW 2,900')):
                invalid = copy.deepcopy(final)
                offer = next(s for s in invalid['locales'][locale]['sections'] if s['id'] == 'free-plus')
                offer['paragraphs'][2] = offer['paragraphs'][2].replace(correct, retired)
                with self.subTest(locale=locale, retired=retired):
                    with self.assertRaises(AssertionError):
                        render_terms.validate(invalid, ios)

    def test_active_sources_have_no_retired_prices_or_representative_placeholder(self):
        for path in sorted((ROOT / 'docs').glob('*content*.json')):
            for field, text in strings(json.loads(path.read_text())):
                with self.subTest(source=path.name, field=field):
                    self.assertNotRegex(text, r'KRW\s*(?:22[,\s]?000|2[,\s]?900)|₩\s*(?:22[,\s]?000|2[,\s]?900)')
                    self.assertNotIn('TO BE APPOINTED', text)

    def test_excluded_regions_and_no_rep_contact_in_every_policy_locale(self):
        # Raw source works on the pre-exclusion ancestor too, without new implementation symbols.
        for name in ('ios-content.json', 'android-content.candidate.json'):
            source = load(name)
            with self.subTest(source=name):
                self.assertEqual(source.get('marketAvailability'), MARKETS)
                self.assertEqual(source.get('representatives'), {
                    region: {'status': 'not-designated-excluded-markets', 'contact': None}
                    for region in ('EU', 'UK')})
            for locale, entry in source['locales'].items():
                text = json.dumps(entry['privacy'], ensure_ascii=False)
                with self.subTest(source=name, locale=locale):
                    for meaning in REGIONAL_ANCHORS[locale].values():
                        self.assertIn(meaning, text)
                    self.assertNotIn('TO BE APPOINTED', text)


if __name__ == '__main__':
    unittest.main()
