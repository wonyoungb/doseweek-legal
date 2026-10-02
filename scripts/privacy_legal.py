"""Validate and render the localized 1.0.6 privacy supplement.

Readiness receipts are source metadata. They are not evidence that providers,
contracts, deletion operations or excluded-market Store settings have been verified.
"""
from __future__ import annotations
import html
import re

LINKED_URLS = (
    'https://www.cloudflare.com/privacypolicy/',
    'https://aws.amazon.com/privacy/',
    'https://www.apple.com/legal/privacy/',
    'https://privacy.google.com/businesses/processorsupport',
    'https://policies.google.com/privacy',
)
SECTION_IDS = ('processing', 'rights', 'processors', 'incident')
COLUMN_IDS = ('legalBasis', 'data', 'country', 'timingMethod', 'recipientContact',
              'purpose', 'retention', 'refusalEffect')
PROVIDER_IDS = ('cloudflare', 'aws', 'firebase', 'admob', 'apple-sign-in', 'google-sign-in')
# Staged Pro AI record assistant (scripts/ai_assistant_candidate.py): the 1.0.6 staging render
# appends one more supplement section and puts an Amazon Bedrock processor row right after the
# AWS hosting row. Sources without them stay valid; nothing else may be added.
STAGED_AI_SECTION_ID = 'ai-assistant'
STAGED_AI_PROVIDER_ID = 'aws-bedrock'
STAGED_AI_PARAGRAPHS = 12
PROCESSOR_IDS = ('cloudflare', 'aws', STAGED_AI_PROVIDER_ID, 'firebase')
READINESS_KEYS = ('providerInventoryVerified', 'overseasTransferBasisVerified',
                  'processorContractsVerified', 'regionalSafeguardsVerified',
                  'salesRegionExclusionsVerified')


def validate_market_availability(source: dict) -> None:
    assert source.get('marketAvailability') == {
        'version': '1.0.6',
        'excludedRegions': ['EU', 'EEA', 'UK', 'Switzerland'],
        'existingUserRightsPreserved': True,
    }, '1.0.6 excludes EU/EEA, UK and Switzerland sales; existing-user rights remain'


def validate_readiness(source: dict) -> None:
    validate_market_availability(source)
    assert set(source['legalReadiness']) == set(READINESS_KEYS)
    assert all(type(value) is bool for value in source['legalReadiness'].values())
    assert set(source['representatives']) == {'EU', 'UK'}
    for representative in source['representatives'].values():
        assert representative == {'status': 'not-designated-excluded-markets', 'contact': None}, (
            'No EU/UK representative is designated for the 1.0.6 excluded-market scope'
        )


def validate_supplement(supplement: dict, locale: str) -> None:
    assert set(supplement) == {'sections', 'estimate'}, locale
    assert supplement['estimate'] == {'unit': 'mg', 'referenceOnly': True,
        'measuredBloodConcentration': False, 'predictsEffectOrSafety': False,
        'medicalAdvice': False, 'doseChangeBasis': False}, locale
    sections = supplement['sections']
    assert [section['id'] for section in sections] in (
        list(SECTION_IDS), [*SECTION_IDS, STAGED_AI_SECTION_ID]), locale
    for section in sections:
        assert isinstance(section['title'], str) and section['title'].strip(), locale
        assert isinstance(section['paragraphs'], list) and section['paragraphs'], locale
        assert all(isinstance(p, str) and p.strip() for p in section['paragraphs']), locale
    for section in sections[len(SECTION_IDS):]:
        assert set(section) == {'id', 'title', 'paragraphs'}, locale
        assert len(section['paragraphs']) == STAGED_AI_PARAGRAPHS, locale
    table = sections[2]['table']
    assert set(table) == {'caption', 'columns', 'rows'}, locale
    assert isinstance(table['caption'], str) and table['caption'].strip(), locale
    assert [column['id'] for column in table['columns']] == list(COLUMN_IDS), locale
    assert all(set(column) == {'id', 'label'} and isinstance(column['label'], str)
               and column['label'].strip() for column in table['columns']), locale
    staged = list(PROVIDER_IDS)
    staged.insert(staged.index('aws') + 1, STAGED_AI_PROVIDER_ID)
    assert [row['id'] for row in table['rows']] in (list(PROVIDER_IDS), staged), locale
    for row in table['rows']:
        assert set(row) == {'id', 'role', 'cells'}, locale
        assert row['role'] == ('processor' if row['id'] in PROCESSOR_IDS
                               else 'independent-controller'), locale
        assert set(row['cells']) == set(COLUMN_IDS), locale
        assert all(isinstance(value, str) and value.strip() for value in row['cells'].values()), locale


def breakable_url(safe_url: str) -> str:
    scheme, separator, rest = safe_url.partition("://")
    return scheme + separator + re.sub(r"/(?=.)", "/<wbr>", rest)


def linked_text(value: str) -> str:
    result = html.escape(value, quote=True)
    for url in LINKED_URLS:
        safe = html.escape(url, quote=True)
        result = result.replace(safe, f'<a href="{safe}"><bdi dir="ltr">{breakable_url(safe)}</bdi></a>')
    return result.replace('\n', '<br>')


def table_html(table: dict) -> str:
    columns = table['columns']
    header = ''.join(f'<th scope="col">{linked_text(column["label"])}</th>' for column in columns)
    rows = []
    for row in table['rows']:
        cells = []
        for index, column in enumerate(columns):
            tag = 'th scope="row"' if index == 0 else 'td'
            closing = 'th' if index == 0 else 'td'
            value = row['cells'][column['id']]
            if index == 0:
                name, separator, basis = value.partition(' — ')
                assert separator, 'row header must identify its service'
                rendered = f'<strong><bdi dir="ltr">{html.escape(name)}</bdi></strong><br>{linked_text(basis)}'
            else:
                rendered = linked_text(value)
            cells.append(f'<{tag}>{rendered}</{closing}>')
        rows.append('<tr>' + ''.join(cells) + '</tr>')
    caption = linked_text(table['caption'])
    return (f'<div class="processor-table-scroll" tabindex="0" role="region" '
            f'aria-label="{html.escape(table["caption"], quote=True)}">'
            f'<table class="processor-table"><caption>{caption}</caption>'
            f'<thead><tr>{header}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')


def toc(locale: str, supplement: dict) -> str:
    return ''.join(f'<li><a href="#{html.escape(locale)}-{section["id"]}">'
                   f'{html.escape(section["title"])}</a></li>' for section in supplement['sections'])


def sections_html(locale: str, supplement: dict) -> str:
    result = []
    for section in supplement['sections']:
        body = ''.join(f'<p>{linked_text(block)}</p>' for paragraph in section['paragraphs']
                       for block in paragraph.split('\n\n'))
        if 'table' in section:
            body += table_html(section['table'])
        result.append(f'<section id="{html.escape(locale)}-{section["id"]}" '
                      f'class="policy-section"><h2>{html.escape(section["title"])}</h2>'
                      f'<div>{body}</div></section>')
    return '\n'.join(result)
